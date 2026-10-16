# D164 — AndroRAT reversed as binaries: four layers, four different C2 addresses, and the source agrees with none of them

**Author:** `android-diver` · **Lane:** `android-diver` · **Report:** D164 · **Class:** static parse, no execution
**Claimed:** D164 by attempt-the-claim on the lane allocator.

**SCOPE:** the AndroRAT target reversed as **binaries** — the APK and the AAB — plus the two further layers that ship beside them in the same tree: a full `apktool` decode and the Java source. Four layers, one target.
**DEFINER SCOPE:** `android-diver`. Files read from disk and parsed in Python; `apktool` 2.12.0 present and used for the decoded tree. **No APK executed, no device, no emulator, no network, no REA `open_binary`.**
**CONDITIONAL SCOPE:** every count carries its denominator. Two of my walkers were wrong and are reported as wrong; one initial value I expected to be stable turned out to be a false positive and is reported as unresolved rather than absent.
**COUNTED:** input cardinality printed beside every count.

**Rule 33 applies. An enumerated scope is not a population.**

---

## 0. The headline

**Four layers of the same target, and four different C2 endpoints.**

| layer | path | IP | port | carries it? |
|---|---|---|---|---|
| Java source | `Android_Code\...\config.java:4-5` | `192.168.0.105` | `8888` | yes, as source text |
| apktool decode | `Compiled_apk\...\config.smali:16-19` | **`127.0.0.1`** | **`8080`** | yes, as smali |
| **shipped APK** | `app-release.apk` → `classes.dex` | **`192.168.43.113`** | `8000` | yes, in `config` |
| **shipped AAB** | `app-release.aab` → `base/dex/classes.dex` | **`192.168.43.129`** | `8000` | yes, but **`config` is deleted** |

**No two layers agree on the address.** The source declares one address; the shipped binaries contain two entirely different ones; and the `apktool` decode in the same repository is a decode of **neither** shipped artifact. D137's three-address observation is confirmed and now resolved by artifact. [verified]

**Second headline: the AAB is not a second build of the same app.** It is a **near-strict superset of the APK's string pool — 5,495 strings added, 11 removed — and those 11 are exactly `config`, its C2 address, and command vocabulary.** The AAB deleted the RAT's configuration class. §5.

**Third: D137's "no HTTP layer" holds, and the cause of the AAB's unexplained AAB-only stack is named.** `org/apache/ftpserver` **0 → 740 types**. §6.

---

## 1. Artifact identity and integrity

| artifact | bytes | SHA-256 |
|---|---|---|
| `app-release.apk` | **2,129,794** | `98037B11A118839BEF93924A5718C9E988F1C11DF507909CDF6BC0CB97189830` |
| `app-release.aab` | **2,366,154** | `2251774AC27DE59586DE01ACECAC9AA3D4CC6442B396E6431F8F761ECA85B410` |
| APK `classes.dex` | **3,604,660** | `4D48430D244DD6BEBBFA7BBA9BD25B41B60006D510F8316CFA87593DF406931C` |
| AAB `base/dex/classes.dex` | **4,340,284** | `3D23820C7951BAA9678BE8AD7FD19BD9CC4DDA81A1EBC110899FF21BE98D1372` |

The APK's digest matches the value the lead supplied. Each dex was re-read from the archive and compared byte-for-byte with the copy on disk: **identical in both cases**, so the digests above are of the shipped member and not of a transcription. [verified]

### 1.1 The DEX integrity gate — RUN, and it fails on both artifacts

D137 recorded this gate as **never run**. It is run here, and the result is negative on both:

| field | APK dex | AAB dex |
|---|---|---|
| `file_size` vs actual length | 3,604,660 = 3,604,660 **MATCH** | 4,340,284 = 4,340,284 **MATCH** |
| **`adler32`** header vs `zlib.adler32(d[12:])` | header `6979ef2c`, computed `1b0b8642` **MISMATCH** | header `aa0cbb76`, computed `a4afbb93` **MISMATCH** |
| **`sha1`** header vs `sha1(d[32:file_size])` | header `2CEF7969` (truncated), computed `7DB90628` (truncated) **MISMATCH** | header `76BB0CAA` (truncated), computed `EF2B662E` (truncated) **MISMATCH** |

**The instrument is proven correct before the negative is believed:** `zlib.adler32(b'Wikipedia')` returned `11e60398` against the published value `11E60398`. A claim of mismatch is only worth as much as the control behind it, so the control is stated first.

**What this does and does not establish.** A DEX header carries a checksum and a signature over its own contents, and neither matches. Three readings are consistent with the observation and **I cannot discriminate between them from the bytes alone**:

1. the dex was rewritten after compilation and the header was not backfilled;
2. the packaging tool that produced the release artifact recomputed a new file but preserved a stale header region;
3. the header fields were deliberately zeroed or scrambled.

**I am not asserting tampering.** What is established is narrower and still useful: **both shipped DEX containers fail their own internal integrity fields, and therefore neither can be integrity-verified by its own header.** D137's open gate is now **closed as a measured negative**, not left open as unrun. [verified for the numbers; the cause is [unknown]]

---

## 2. Q1 — the APK dex, and the command namespace

**INPUT CARDINALITY: `classes.dex` 3,604,660 B. All six count fields cross-checked against the DEX's own `map_list`:**

| table | parsed | `map_list` declared | |
|---|---|---|---|
| `string_ids` | 26,908 | 26,908 | OK |
| `type_ids` | 3,403 | 3,403 | OK |
| `proto_ids` | 6,109 | 6,109 | OK |
| `field_ids` | 12,964 | 12,964 | OK |
| `method_ids` | 26,535 | 26,535 | OK |
| `class_defs` | 2,472 | 2,472 | OK |

**`map_list` is the control that matters**, because it is a number the parser **reads** rather than **produces**. All six agree.

### 2.1 `code_item` walk, validated at ratio 1.000

D156's lesson applied. The walker collects `code_off` from every `class_data_item` and the denominator is the DEX's own declared count:

| DEX | `map`-declared `code_item` | collected | valid | **ratio** | `class_data` ok/bad |
|---|---|---|---|---|---|
| APK | **19,085** | 19,085 | 19,085 | **1.000** | 2,301 / **0** |
| AAB | **24,127** | 24,127 | 24,127 | **1.000** | 2,959 / **0** |

**`rejected = 0` in both.** The D156 walker transfers to this target unchanged, and reproduces the declared count exactly. This is a **second independent target** confirming the D156 fix rather than a restatement of it.

### 2.2 The command namespace — 15 `equals()` comparisons

Enumerated from `tcpConnection.java`, where the RAT compares the received line:

```
exit  camList  shell  getClipData  deviceInfo  help  clear  getSimDetails
getIP  getLocation  startAudio  stopAudio  stopVideo  getCallLogs  getMACAddress
```

**COUNTED: 15 commands, from 15 `.equals()` call sites.** All 15 are present in the Java source; all 15 appear as `const-string` literals in the APK dex.

**This is a different shape from AhMyth's, and the difference is the finding:**

| | AhMyth (D156) | **AndroRAT (D164)** |
|---|---|---|
| namespace | `x0000ca`, `x0000cl`, `x0000cn`, `x0000fm`, `x0000lm`, `x0000mc`, `x0000sm` | `getLocation`, `getCallLogs`, `getMACAddress`, … |
| size | **7** | **15** |
| form | **opaque, machine-minted, 6 chars** | **self-documenting English verbs** |
| decode needed | yes — required matching each opcode to a manager class | **none — the name states the capability** |
| dispatch | static methods per opcode | `String.equals()` chain on a line read from a socket |

**Two Android RATs in one corpus with distinguishable command namespaces.** A detector that keys on `getX`-style verbs will **miss AhMyth entirely**; a detector that keys on `x0000`-style tokens will **miss AndroRAT entirely**. The shared property is not the vocabulary — it is the **plaintext, unauthenticated, single-socket command channel**. [verified]

---

## 3. Q2 — the endpoint and registration payload

**COUNTED, and the count that matters is the one that had to be rejected first.**

### 3.1 The `8888` false positive — a substring test is not a table-membership test

`config.java:5` declares port `"8888"`. A substring count over the APK dex string pool returns:

```
'8888' matches 2 strings:
   [ 3558] 'ARGB_8888'          <- an Android bitmap format constant
   [11565] 'SMAP\n_Arrays.kt\n… 8888#1,3:15235 …' <- a Kotlin source-map line coordinate
```

**Neither is a port.** The standalone literal `8888` is present in **neither** shipped DEX. Had I reported the substring count I would have written *"port 8888 present in both binaries"* — a confident, wrong, operationally meaningful claim. **This is the D156/D137 failure family: an instrument that inflates rather than fails.** The exact-match test is the control, and it fires the other way. [verified]

### 3.2 The real endpoint table

| artifact | address literal | port literal | where |
|---|---|---|---|
| APK dex | `192.168.43.113` (string_id 3133) | `8000` (string_id 3136) | **3 apart** |
| AAB dex | `192.168.43.129` (string_id 3334) | `8000` (string_id 3338) | **4 apart** |
| source | `192.168.0.105` | `8888` | `config.java:4-5` |
| apktool decode | **`127.0.0.1`** | **`8080`** | `config.smali:16-19` |

The address and port occupy **adjacent slots in the string pool** in both DEXes — `3133/3136` and `3334/3338`, in identical neighbourhoods (`'2nd pass'`, `'3rd pass'`, `'8000'`) — the layout signature of **two `const-string`s in one static initializer**. Both shipped artifacts therefore carry a compiled `config` class; what differs is the literal that was compiled into it. [verified]

**No encryption on either path.** Class-level ownership, not string matching:

| | APK: types with methods | app-owned | AAB: types with methods | app-owned |
|---|---|---|---|---|
| `javax/crypto` | 0 | **0** | 2 | **0** |
| `java/security/MessageDigest` | 0 | **0** | 2 | **0** |
| `SecretKeySpec` | 0 | **0** | 1 | **0** |
| `Base64` | 1 | **0** | 2 | **0** |

**Not one AndroRAT-owned class in either build uses a cipher, a digest, or a key spec.** The apparent hits (`AES` 0, `RSA` 4, `DES` 11 on a naive sweep) were **substring garbage** — `EXTRA_CONVERSATION` matched `RSA`, `CAN_HIDE_DESCENDANTS` matched `DES`. Both were caught by reading the matching strings rather than trusting the count. [verified]

**D137's header finding holds on the corrected instrument:** `User-Agent` **0**, `Content-Type` **0**, `multipart` **0**, `form-data` **0** — as exact literals **and** as substrings **and** in both DEXes. The AAB does contain `HTTP/1.0` and `HTTP/1.1`, which arrive with the FTP server stack (§6) and carry no request-header vocabulary. [verified]

---

## 4. Q3 — the pairing: does source agree with the compiled artifact?

**Answered separately per facet, in both layers. Three of four facets disagree.**

| facet | source | APK binary | AAB binary | verdict |
|---|---|---|---|---|
| **C2 address** | `192.168.0.105` | `192.168.43.113` | `192.168.43.129` | **ALL DISAGREE** |
| **port** | `8888` | `8000` | `8000` | **DISAGREE** (source vs both) |
| **`config` class** | declared, `config.java` | **present**, type_idx 1966, 2 methods | **TYPE NOT IN POOL** | **DISAGREE** |
| **command namespace** | 15 verbs | **15/15 present** | **13/15 present** | **DISAGREE** |

**The registration field list is `IP` + `port` + `icon`** — the whole of `config.java` is three static fields, and the compiled `config` class in the APK has exactly the two-`String`-one-`boolean` shape. **There is no registration *payload*** in AndroRAT the way there is in AhMyth: AhMyth builds a query string (`?model=&manf=&release=&id=`) before it connects; **AndroRAT opens a raw TCP socket and sends nothing until commanded.** The equivalent of AhMyth's registration is an empty one. [verified]

### 4.1 The command-layer pairing, per command, across all four layers

| command | java | smali | APK dex | AAB dex |
|---|---|---|---|---|
| `exit` `shell` `getClipData` `deviceInfo` `clear` `getSimDetails` `getIP` `getLocation` `startAudio` `stopAudio` `stopVideo` `getCallLogs` `getMACAddress` | ✔ | ✔ | ✔ | ✔ |
| `camList` | ✔ | ✔ | ✔ | **absent** |
| `help` | ✔ | ✔ | ✔ | **unresolved** |

**13 of 15 commands agree across all four layers.** The two that do not are examined rather than asserted, and they resolve differently:

- **`camList` — genuinely absent from the AAB dex.** Verified by exact match **and** by substring: **0 hits of any kind** for `camList`, `camlist`, `CamList`. The capability is gone from the compiled artifact. [verified]
- **`help` — UNRESOLVED, and I am not calling it absent.** The AAB has **19 substring hits** for `help`, but none is the bare command: they are `--help` (an FTP-server CLI string), a TLD-matching regex, and unrelated prose. A case-variant `HELP` **is** present. **My exact-match test conflated "the literal `help` is missing" with "the command is gone."** Since the RAT compares with `.equals()`, the bare literal is what matters — but I cannot show the AAB's dispatch chain without a walker I have not validated for this question, so it stays **`[blocked]`**: *the AAB's `help` handling is unmeasured, not disproved.* [blocked]

### 4.2 D156's type-in-pool method applied to AndroRAT

An `invoke` operand is a `method_id` carrying a `class_idx`; **a type with zero `method_id`s cannot be named by any invoke.** Applied here:

| type | APK | AAB |
|---|---|---|
| `tcpConnection` | type_idx 1976, **5** methods | type_idx 1974, **5** |
| `mainService` | type_idx 1972, **6** | type_idx 1970, **6** |
| `MainActivity` | type_idx 1923, **6** | type_idx 1923, **6** |
| `functions` | type_idx 1969, **11** | type_idx 1967, **11** |
| **`config`** | type_idx 1966, **2** | **TYPE NOT IN POOL** |
| `jumper` | TYPE NOT IN POOL | TYPE NOT IN POOL |
| `controlPanel` | TYPE NOT IN POOL | TYPE NOT IN POOL |
| `keypadListner` | TYPE NOT IN POOL | TYPE NOT IN POOL |

**This reproduces D156's result on a second target.** `jumper`, `controlPanel` and `keypadListner` are absent from **both** type pools — so D150's finding is not an APK/AAAB quirk but a property of the compiled app. And **`config`, present with 2 methods in the APK, has no type at all in the AAB.** [verified]

---

## 5. Q4 — what 236,366 bytes of AAB tells you

### 5.1 The AAB dex is a near-strict superset, and the 11 exceptions name the divergence

| | strings |
|---|---|
| APK dex | 26,908 |
| AAB dex | 32,392 |
| **AAB-only** | **5,495** |
| **APK-only** | **11** |

**All 11 strings present in the APK and absent from the AAB:**

```
'192.168.43.113'                            the APK's C2 address
'Lcom/example/reverseshell2/config;'        the config CLASS
'config.java'                               its SourceFile attribute
'IP'                                        its field name
'camList'  'help'  'help\n'  'getSMS '      command literals
'Hello there, welcome reverse shell of '    banner
'Large File\n'                              message
'Lcom/example/reverseshell2/Payloads/videoRecorder$1$1$3;'
```

**This is the whole answer to the "what differs" question, and it is a deletion, not an addition.** The AAB does not merely add an FTP server — it also **removes `config`, its `SourceFile` attribute, its `IP` field, its C2 address, and several command literals.** A build configuration flag cannot delete a class's `SourceFile` attribute. **The two DEXes were compiled from different source states.** [verified]

**This gives the C2 difference its cause.** D137 recorded the addresses as differing and could not explain it. The mechanism is now visible: **the AAB was built from a tree in which `config` had already been removed** — its address survives only because some other class's static initializer retains the literal, in the same string-pool neighbourhood. Since `config` is the class the RAT reads its endpoint from, **the AAB's C2 address may be unreachable configuration rather than an active endpoint.** I state that as the shape of the evidence, **[inferred]**, not as an established behavioural claim — establishing reachability needs a validated walker over the AAB's invoke graph, which §4.1 shows I have not done for this question.

### 5.2 The additive half: Apache FtpServer

**Normalised member-level diff (AAB `base/root/` prefix stripped): AAB-only 14, APK-only 5.**

APK-only members are the four packaging files plus the DEX: `AndroidManifest.xml`, `META-INF/CERT.RSA`, `META-INF/CERT.SF`, `classes.dex`, `resources.arsc`. **That is the APK/AAB format difference, not a payload difference.**

AAB-only members name the payload:

```
org/apache/ftpserver/config/spring/ftpserver-1.0.xsd
org/apache/ftpserver/message/FtpStatus.properties
org/apache/ftpserver/message/FtpStatus_en.properties
org/apache/ftpserver/message/FtpStatus_zh-tw.properties
META-INF/spring.handlers
META-INF/spring.schemas
META-INF/DEPENDENCIES
META-INF/KEY0.RSA   META-INF/KEY0.SF
BundleConfig.pb   resources.pb   BUNDLE-METADATA/...
```

**Type-level confirmation, AAB-only namespaces (zero types in the APK):** `org/apache/ftpserver` **0 → 740**, `org/slf4j` **0 → 26**, `com/jaredrummler` **0 → 25**, `javax/net` **0 → 20**, `org/springframework` **0 → 15**, `org/ietf` **0 → 6**, `java/sql` **0 → 4**, `org/w3c` **0 → 3**.

**There are ZERO APK-only namespaces.** Every namespace-level difference is additive.

**This resolves D137's open item.** D137 observed AAB-only URL families — `slf4j` (9), `mina.apache.org`, `springframework` — and could not attribute them. **They are an embedded Apache FtpServer with its Spring handler/schema wiring and its Mina transport.** String-pool confirmation: `org/apache/ftpserver` 0 → 206, `ftpserver` 0 → 227, `Ftplet` 0 → 25, `slf4j` 0 → 52, `springframework` 0 → 15, `mina` **12 → 498**.

**An FTP server inside the release artifact is itself the finding.** A RAT that also embeds a listening FTP service is a materially different exposure from one that only dials out. I record it as **a capability present in the shipped AAB and absent from the shipped APK**, and do not assert it is started — that is a runtime question and this is a static report. [verified for presence; activation is [unknown]]

---

## 6. Mandatory control inventory — D149 shape audit

**Every control below can fail. The ones that fired are reported firing; the ones that did not are reported not firing.**

**EXPECTED PRESENT — found:**

| probe | java | smali | APK dex | AAB dex |
|---|---|---|---|---|
| `getLocation` | ✔ | ✔ | ✔ | ✔ |
| `getIP` | ✔ | ✔ | ✔ | ✔ |
| `getCallLogs` | ✔ | ✔ | ✔ | ✔ |
| `camList` | ✔ | ✔ | ✔ | **✘ — the finding** |

**EXPECTED ABSENT — shown absent.** AhMyth's namespace, probed inside an AndroRAT artifact (cross-family non-contamination):

| probe | java | smali | APK dex | AAB dex |
|---|---|---|---|---|
| `x0000ca` `x0000cl` `x0000cn` `x0000fm` `x0000lm` `x0000mc` `x0000sm` | ✘ | ✘ | **✘** | **✘** |
| `getPhoto` `getAudio` `9609` | ✘ | ✘ | **✘** | **✘** |

**All seven AhMyth opcodes are absent from every AndroRAT layer, on both instruments.** The two RATs do not share a command namespace.

**EXPECTED IMPOSSIBLE — cannot exist:**

| probe | APK dex | AAB dex |
|---|---|---|
| `ZZQQ_NO_SUCH_SYMBOL_ANYWHERE` | **absent** | **absent** |

**INSTRUMENT CONTROL — a value with a published answer:**

`zlib.adler32(b'Wikipedia')` → `11e60398`, against the published `11E60398`. **The digest primitive is correct before any mismatch is believed** (§1.1).

**THE MOVING CONTROL — D156's `reverseshell2` shape, built here.** The control that discriminates a live walker from a dead one on this target is the **`map_list` ratio**:

| walker state | ratio | meaning |
|---|---|---|
| a fixed-stride or desynchronized walk | `< 1.000` | dead |
| **the validated walk** | **1.000, `rejected=0`, both DEXes** | live |

The ratio **did** move across this lane's history (D156 recorded 0.004 → 0.468 → 1.000); on this target it reads **1.000 on first correct application in both DEXes**, which is the expected result for a fix that transferred. **A control that has never moved is not a control; this one has, and its movement is documented in D156.**

**CONTROLS THAT DID NOT FIRE, reported as such:**
- My `const-string`-to-owning-class walker returned **nothing** on both DEXes (§3, abandoned). It is a **dead instrument** and no count from it appears in this report.
- My `class_data` field-list parser raised `list index out of range` on `tcpConnection` and `MainActivity`. **It produced no number used here.** The `config`-shape question was answered instead by `apktool`'s decoded tree, which is a **different instrument** with a checked output.
- `help` in the AAB is **`[blocked]`**, not absent (§4.1). Reporting it as absent would have been the convenient zero this corpus keeps finding.

---

## 7. Limits

- **No execution.** No APK run, no emulator, no device, no network, no live C2. No REA `open_binary`.
- **`Compiled_apk` is a decode of neither shipped artifact.** Its `config.smali` says `127.0.0.1:8080`; its `apktool.yml` names the input `Compiled_apk.apk`, which is **not present** in the tree — no file in the repository begins with the DEX magic. **The decode is a third, undocumented source state and is treated as such.** [verified]
- **The DEX integrity failure is recorded without a cause** (§1.1). Three readings are consistent with the bytes; I cannot discriminate, and I am not asserting tampering.
- **AAB C2 reachability is `[inferred]`, not established** (§5.1). The literal is present; whether any surviving code path reads it requires a validated invoke walk over the AAB, which §4.1 records as not done.
- **`help` in the AAB is `[blocked]`** (§4.1).
- **The AAB's FTP server is recorded as present, not as running** (§5.2).
- **`Android_Code` may not be the source of either binary.** Given §5.1 shows the two DEXes came from different source states, and the source tree matches neither endpoint, **the source-to-artifact relationship for this target is not a clean pairing** — which is precisely the answer Q3 asked for, and it is a negative one.

---

## 8. Frozen measurement, fixed point

```
D164 frozen measurement -- counts taken on this file including this block

  bytes            : 23145
  lf               : 347
  cr               : 0
  bom              : absent
  fffd             : 0
  strict_utf8      : decodes without error
  headings         : 19     (regex ^#{1,6}[ \t], basis: bare-LF line starts)
  h1_count         : 1
  dup_headings     : 0     (whole-line exact match)
  fences           : 10     (even = balanced)
  backslash_btick  : 0     (literal backslash before a closing backtick; Rule 36)
  cyrillic_es_0441 : 0
  ellipsis_2026    : 3
  non_ascii        : 113
  btick_nonascii   : 0     (backticked tokens containing non-ASCII)
  abs_paths        : 0     (absolute path tokens in code spans)
  sha256_zeroed    : 3AC05EC7F1DF2D192C2160469865D03163511271C5EC9B5CDAE6120651E88D84
                     (digest of this file with this one 64-char field replaced
                      by 64 zeros; a file cannot contain its own true digest.)
```
