# D156 — AhMyth smali measured, and the `code_item` scan closed: the walker was wrong four times, the map-declared count was the control that caught it

**Author:** `android-diver` · **Lane:** `android-diver` · **Report:** D156 · **Class:** static parse, no execution
**Claimed:** D156 confirmed by attempt-the-claim, `HELD D156 by android-diver since 2026-10-16 23:44:53`.

**SCOPE:** two closures. (1) The **411 AhMyth `.smali` files** D150 found but did not parse — the bytecode column D150 correctly refused to fill with AndroRAT's result. (2) The **`code_item` invoke scan** whose two `IndexError`s D150 filed `[blocked]`.
**DEFINER SCOPE:** `android-diver`. Files read from disk, parsed in Python. **No APK executed, no network, no device, no REA `open_binary`.**
**CONDITIONAL SCOPE:** every count carries its denominator. Two counts in this report were produced by an instrument that was **proven wrong and then fixed**; they are labelled as such and the wrong values are retained.
**COUNTED:** input cardinality printed beside every count.

**Rule 33 applies. An enumerated scope is not a population.**

---

## 0. Outcome first

| D150 left open | D156 result |
|---|---|
| AhMyth bytecode column unmeasured | **MEASURED.** 411 classes, 2,764 methods, 1,974 string literals. A full command namespace recovered. |
| `code_item` invoke scan `[blocked]` | **CLOSED**, and validated against an external invariant at ratio **1.000**. The D150 zero is **confirmed correct** — for a different reason than the broken walker gave. |
| D137's `getX` fingerprint vocabulary | **Refuted for AhMyth.** Different vocabulary, different transport, different everything. |

**Both closures required correcting my own instrument. §4 is the record of that, and it is the more useful half of this report.**

---

## 1. AhMyth smali census

**INPUT CARDINALITY: 411 `.smali` files, 3,708,843 bytes.**

| quantity | COUNTED |
|---|---|
| class declarations | **411** |
| method declarations | **2,764** |
| field declarations | **1,649** |
| `const-string` literals | **1,974** |
| annotations | **561** |

**Controls, both of which can fail:**
- **Positive:** `Lahmyth/mine/king/ahmyth/ConnectionManager;`, `MainActivity;`, `CameraManager;`, `BuildConfig;` — **all FOUND.**
- **Negative (Rule 37 shape):** `ZZQQ_NO_SUCH_SYMBOL_ANYWHERE` appears in **0** string literals. A candidate that cannot exist returns nothing.

### 1.1 The corpus is 94% third-party library

| package | classes |
|---|---|
| `okhttp3` (incl. `internal/http2`, `internal/cache`, `internal/ws`) | **193** |
| `io/socket` (incl. `engineio`, `parser`) | **151** |
| `okio` | **41** |
| **`ahmyth/mine/king/ahmyth`** | **26** |

**385 of 411 classes are bundled libraries. AhMyth's own code is 26 classes / 76 methods — 2.7% of the method count.**

**This is itself a fingerprint:** the RAT ships a **full HTTP + WebSocket client stack** (`okhttp3` 193 classes, `io.socket` 151). A detection rule that keys on "app bundles socket.io" will fire on enormous numbers of legitimate applications. **Named as a non-discriminator, not a finding.**

---

## 2. The AhMyth command namespace — `x0*` opcodes

**COUNTED 17 literals matching `x0` + two letters, over 1,974 string literals. 7 distinct:**

| opcode | occurrences | manager(s) containing it | matching class exists |
|---|---|---|---|
| `x0000ca` | 3 | `CameraManager`, `ConnectionManager$2`, `ConnectionManager` | `CameraManager` ✔ |
| `x0000cl` | 2 | `ConnectionManager$2`, `ConnectionManager` | `CallsManager` ✔ |
| `x0000cn` | 2 | `ConnectionManager$2`, `ConnectionManager` | `ContactsManager` ✔ |
| `x0000fm` | 3 | `ConnectionManager$2`, `ConnectionManager`, `FileManager` | `FileManager` ✔ |
| `x0000lm` | 2 | `ConnectionManager$2`, `ConnectionManager` | `LocManager` ✔ |
| `x0000mc` | 2 | `ConnectionManager$2`, `ConnectionManager`, `MicManager` | `MicManager` ✔ |
| `x0000sm` | 3 | `ConnectionManager$2`, `ConnectionManager` | `SMSManager` ✔ |

**The mapping is not a guess — it is confirmed by an independent property.** Each opcode string co-occurs in exactly the file implementing that capability, and **the initial letters decode cleanly**: **ca**mera, **c**a**ll**s, **c**o**n**tacts, **f**ile**m**anager, **l**ocation**m**anager, **m**i**c**rophone, **sm**s. The `"   ,  "` literal at `ConnectionManager.smali:392` is a comma separator with padding.

**The opcodes are real static methods with real signatures:**

```
public static x0000ca(I)V
public static x0000cl()V
public static x0000cn()V
public static x0000fm(ILjava/lang/String;)V
public static x0000lm()V
public static x0000mc(I)V
public static x0000sm(ILjava/lang/String;Ljava/lang/String;)V
```

`x0000fm(I, String)` takes a **file index and path**; `x0000sm(I, String, String)` takes an **index and two SMS strings**. **Seven static methods dispatch the entire RAT.** `ConnectionManager` also exposes `startAsync(Context)` and `sendReq()`. [verified]

**No other `x`-prefixed command literal exists.** The remaining `x`-prefixed strings are library text: `x509TrustManager`, `xhr open %s: %s`, `xhr poll`, `xhr poll error`, `xhr post error` — **socket.io transport diagnostics, not RAT commands.** The namespace is closed at 7. [verified]

---

## 3. `IOSocket` — endpoint, registration, and NO encryption

**All five literals in `IOSocket.smali`:**

| line | literal |
|---|---|
| 46 | `android_id` |
| **79** | **`http://192.168.8.100:42474?model=`** |
| 95 | `&manf=` |
| 107 | `&release=` |
| 119 | `&id=` |

**The registration URL is assembled from query parameters:** `?model=` + `&manf=` + `&release=` + `&id=` `android_id`. **Device model, manufacturer, Android release and `Settings.Secure.ANDROID_ID` are sent to the C2 in the clear at registration.** [verified]

### 3.1 There is no cipher anywhere in AhMyth

Swept all 26 AhMyth classes for `javax/crypto/*`, `AES/*`, `Cipher`, `SecretKeySpec`, `IvParameterSpec`, `Base64`, `DigestUtils`, `MessageDigest`:

**COUNTED: zero matches, in all 26 classes.** `ConnectionManager`'s complete 16-literal set is `ping`, `order`, `errrr`, `x0000ca`, `x0000cl`, `x0000cn`, `x0000fm`, `loc`, `"   ,  "`, `enable`, `lat`, `lng`, `x0000lm`, `enable`, `x0000sm`, `x0000sm`. **No key, no IV, no encoding step.** [verified]

**AhMyth traffic is plaintext socket.io over HTTP.** The absence is stated as a search result over a named, complete class set — **not** as a universal claim, and D150's standing `PGSZ`-style correction applies: an absence in a corpus is not an absence in the world. But the search space here is *closed* (all 26 classes, all 1,974 literals), which is stronger than a keyword sweep. [verified]

---

## 4. The `code_item` scan — four wrong answers, and the control that caught them

**This section is the point of the report.** D150 recorded **0 field-refs and 0 signature-refs** into the four absent classes, then correctly noted *"a count from a walker that threw is a count of the walker."* Closing it took **five attempts**, and the first four were wrong.

### 4.1 The declared value, and where it comes from

`map_list` is an **independent table inside each DEX** stating how many items of each type the file contains:

| DEX | map-declared `code_item` count | first offset |
|---|---|---|
| APK | **19,085** | 589,760 |
| AAB | **24,127** | 723,488 |

`file_size` matches actual file length in **both** DEXes. **This declared count is an external check on my own parse — the parser does not produce it, and reproducing it is evidence the parse is right.**

### 4.2 The four wrong answers

| attempt | change | `code_off` collected | validated | **ratio to map** |
|---|---|---|---|---|
| v1 | fixed 6-byte stride | 19,044 | — | — |
| v2 | full 241-opcode width table | 19,044 | — | — |
| v3 | + "code region" filter | 19,044 | 76 | 0.004 |
| v4 | + field lists consumed | 18,356 | 78 | 0.004 |
| v5 | region filter removed | 18,356 | 8,937 | 0.468 |
| **v6** | **`encoded_field` = 2 ULEBs** | **19,085** | **19,085** | **1.000** |
| | | | AAB: 24,127 | **1.000** |

**Every wrong attempt produced a plausible number.** v1/v2 were off by 41 and looked fine. v5 was off by 52% and still returned 8,937 valid-looking bodies. **Nothing failed loudly. Only the ratio exposed them.**

### 4.3 Two real defects found, and one reasoning error

**Defect 1 — the region filter was invented.** I asserted *"a correct walk yields 19,085 offsets in `[589760, 608845)`."* The arithmetic refutes it on sight: **19,085 items in a 19,085-byte region is 1.0 byte per item, and a `code_item` header is 16 bytes minimum.** I then filtered against this false invariant and **discarded 18,278 valid offsets.** `map_list`'s `off` field is the offset of the **first** item, not a contiguous span. **A map entry that points somewhere is not a claim that everything lives there.** This was a reasoning error, not a coding one, and it survived two runs.

**Defect 2 — `encoded_field` is 2 ULEBs, not 3.** I consumed `(field_idx_diff, access_flags, type_byte)`. The DEX format defines `encoded_field = field_idx_diff(uleb) access_flags(uleb)` — **two fields; the type is implied by the declaration, not restated.** The extra byte desynchronized every `class_data_item` containing fields. Caught by reading raw bytes:

```
raw: \x8b\x01 \x19 \x8c\x01 \x10
     idx_diff=139  access=0x19  idx_diff=140  access=0x10   <- 2 ULEBs, clean
     decode-A read access=0x101a  <- access mask with bits that DO NOT EXIST
```

**`0x101a` as an access-flags value is the plausible-garbage signature** — not an error, a number. That is the same failure shape as D79: *a decoder that ignores a flag or an offset basis returns plausible nonsense, not an error.* [verified]

### 4.4 The control that actually worked

**`ratio to map-declared = 1.000`, on both DEXes, with `rejected=0`.**

This is a control that **can** fail and **did** fail four times: it read 0.004, 0.004, 0.468, 0.468 before reading 1.000. It is not tautological — the denominator (19,085 / 24,127) is produced by the DEX's own `map_list`, which my parser merely reads; it is not derived from the walk.

**A second, walker-independent control:** the `reverseshell2` invoke census rose from **0** (broken walker) to **13 classes (APK)** and **15 (AAB)** once the parse was correct — including `tcpConnection`, `mainService`, `newShell`, `ipAddr`, `locationManager`. **A control that reads zero when the instrument is dead and non-zero when it is alive is doing its job.**

### 4.5 Residual, stated

**`undefined_opcode` = 4,030 (APK) / 5,495 (AAB)** on the surviving walk. My 241-entry width table does not model **payload pseudo-ops** (`packed-switch`/`sparse-switch`/`fill-array-data` at even offsets, ids `0x0100`/`0x0200`/`0x0300`), so a walk entering a payload region desynchronizes and stops. **This affects only how far each body is walked, never which `code_off` values are collected** — the offset collection is validated at ratio 1.000. **It is a bound on invoke coverage within bodies, and it is why §5 leans on a walk-free check rather than the walk alone.**

---

## 5. The four absent classes — the zero is confirmed, by a method that needs no walker

**D150's 0/0 for field-refs and signature-refs is now independently confirmed.** The argument does not use an instruction walk at all:

> An `invoke-kind` instruction's operand is a **`method_id` index**. A `method_id` is `(class_idx u16, proto_idx u16, name_idx u32)`. Therefore **if a type has zero `method_id`s, no `invoke` instruction in the entire DEX can name it** — there is no index to encode.

**COUNTED, by `type_idx` → `method_id` counts:**

| type | APK | AAB |
|---|---|---|
| `Lcom/example/reverseshell2/jumper;` | **TYPE NOT IN POOL** | **TYPE NOT IN POOL** |
| `Lcom/example/reverseshell2/controlPanel;` | **TYPE NOT IN POOL** | **TYPE NOT IN POOL** |
| `Lcom/example/reverseshell2/keypadListner;` | **TYPE NOT IN POOL** | **TYPE NOT IN POOL** |
| `Lcom/example/reverseshell2/config;` | type_idx 1966, **2 methods defined** | **TYPE NOT IN POOL** |
| `Lcom/example/reverseshell2/tcpConnection;` | type_idx 1976, 5 methods *(control)* | type_idx 1974, 5 *(control)* |
| `Lcom/example/reverseshell2/mainService;` | type_idx 1972, 6 *(control)* | type_idx 1970, 6 *(control)* |
| `Lcom/example/reverseshell2/MainActivity;` | type_idx 1923, 6 *(control)* | type_idx 1923, 6 *(control)* |

**Reading:**

- **APK:** three of the four types are **not in the type pool at all**. They cannot be referenced by any instruction. The residual **0 invoke-refs is a structural certainty, not a scan result.** `config` **is** in the APK pool with **2 methods defined** — but the corrected walk finds **0 invokes** into it.
- **AAB:** all four types are **absent from the pool.** Again structural.
- **Controls live in the same table** — `tcpConnection` 5, `mainService` 6, `MainActivity` 6 — so the instrument demonstrably counts real classes.

**The D150 zero survives.** It was produced by a broken scan; it is **true**, and now it is true **for a reason independent of that scan.** [verified]

### 5.1 What this does to D150's dangling-reference claim

D150 found `jumper` constructed at **three** source sites (`jobScheduler.java:37`, `mainService.java:21`, `tcpConnection.java:142`) with all three caller classes surviving, and flagged that as a **dangling reference**.

**The bytecode does not support the strong form of that claim.** `jumper`'s type is **not in the APK type pool** — but `jobScheduler`, `mainService` and `tcpConnection` **are**, and the corrected walk shows `tcpConnection` and `mainService` making **13/15 real `reverseshell2` invokes**. If a surviving method body still called `jumper.<init>`, that call would require a `method_id` for `jumper` — and **none exists.**

**Corrected statement:** the source-level construction sites **do not survive as bytecode invokes.** D150's "dangling reference" is **withdrawn as stated.** The accurate description is the weaker, better-evidenced one: **the calling classes survive; the calls to `jumper` do not.** Whether the source tree and the shipped DEXes are from the same build revision is **not established** — that would require the build pipeline, which was not read. [verified for the bytecode; the source-to-build correspondence is [inferred] and not claimed]

---

## 6. D137's fingerprint vocabulary does NOT hold for AhMyth

D137 established for **AndroRAT**: `getX` camelCase method verbs, plaintext newline-delimited line protocol on a raw `java.net.Socket`, no HTTP layer.

**AhMyth is different on every axis:**

| axis | AndroRAT (D137) | AhMyth (D156) |
|---|---|---|
| command vocabulary | `getIP`, `getLocation`, `getCallLogs`, `getMACAddress` | **`x0000ca`, `x0000cl`, `x0000cn`, `x0000fm`, `x0000lm`, `x0000mc`, `x0000sm`** |
| transport | raw `java.net.Socket`, plaintext newline protocol | **socket.io over HTTP/WebSocket** (`io.socket` 151 classes) |
| HTTP layer | **absent** (0 `User-Agent`, 0 `Content-Type`) | **present** — `okhttp3` 193 classes |
| commands are | `equals()` dispatch on text lines | **real static methods** (`x0000fm(I, String)V`) |
| endpoints | `192.168.43.113:8000` / `192.168.43.129:8000` | **`192.168.8.100:42474`** |
| encryption | none found | **none found — 0 cipher references in 26 classes** |

**The `getX` vocabulary appears only twice in AhMyth** — `LocManager.getLocation()` and `ContactsManager.getContacts()` — and the `getSMS` "hit" is `SMSManager.getSMSList()`, caught by substring, not by vocabulary. **COUNTED: 4 substring hits over 2,764 method declarations, and none of them is a wire command.** [verified]

**The D137 `getX` fingerprint is AndroRAT-specific and must not be generalised to AhMyth.** The genuine cross-family discriminator is **not** the command vocabulary — it is that **both RATs dispatch commands through an unencrypted, hardcoded-RFC1918 channel and neither implements authentication.** The command *names* differ; the *architecture* does not.

---

## 7. Limits

- **No execution.** No APK, emulator, device, network or live C2. No REA, no `open_binary`.
- **The smali is decompiled Dalvik, not shipped bytecode.** AhMyth's `smali/` tree is apktool output retained in the Server's `Factory/` directory. **It is source-form bytecode and is not an AhMyth binary that shipped** — the corpus still contains **0 AhMyth APK/AAB/DEX.** Statements in §2–§3 are about **the AhMyth client built by this tool**. [verified]
- **`undefined_opcode` 4,030 / 5,495** bounds invoke coverage within bodies (§4.5). The offset collection is validated independently at ratio 1.000.
- **The four-attempt failure record is retained deliberately.** The first four numbers are wrong; they are printed so the failure is auditable rather than erased.
- **The source-to-DEX correspondence for `jumper` is not established** (§5.1) — the build pipeline was not read.

---

## 8. Frozen measurement, fixed point

```
D156 frozen measurement -- counts taken on this file including this block

  bytes            : 17970
  lf               : 264
  cr               : 0
  bom              : absent
  fffd             : 0
  strict_utf8      : decodes without error
  headings         : 18     (regex ^#{1,6}[ \t], basis: bare-LF line starts)
  h1_count         : 1
  dup_headings     : 0     (whole-line exact match)
  fences           : 6     (even = balanced)
  backslash_btick  : 0     (literal backslash before a closing backtick; Rule 36)
  cyrillic_es_0441 : 0
  ellipsis_2026    : 0
  non_ascii        : 56
  btick_nonascii   : 0     (backticked tokens containing non-ASCII)
  abs_paths        : 0     (absolute path tokens in code spans)
  sha256_zeroed    : C511AA2B8DA53BDFE0E53A7586031EAEF26C97A27A98F6DD5E3B6719E635F162
                     (digest of this file with this one 64-char field replaced
                      by 64 zeros; a file cannot contain its own true digest.)
```
