# D137 — Android detection surface: C2 fingerprints, the permission-as-fingerprint control, and the DEX-vs-source gap as a bounded rate

**Author:** `android-diver` · **Lane:** `android-diver` · **Report:** D137 · **Class:** static artifact extraction only
**Reserved:** D137 (renumbered by the lead from D132; lock and registry both read `android-diver` at 23:08:07).
**SCOPE:** the Android half of the corpus detection surface — C2/network fingerprints, permission-set discrimination, and the source-vs-shipped-class gap, for the two AndroRAT build outputs and the AhMyth payload template.
**DEFINER SCOPE:** `android-diver`. Static read of artifacts on disk. No execution of any kind.
**CONDITIONAL SCOPE:** every fingerprint row is marked **SHIPPED** (byte-confirmed in a compiled artifact) or **SOURCE-ONLY** (a claim about intent, confirmed only in source text). A row with neither mark is not a fingerprint.
**COUNTED:** input cardinality printed beside every count. Counts stated without a cardinality are not measurements.

**Cites, does not repeat:** D125 (method reachability, missing-class count), D124 (`covenant-diver`, independent read), D122 (AXML column typology), D114 (my own, frozen), D104 (retracted §3.3 only).

---

## 0. The brief that this report answers

The corpus has **151 reports, 5.8 MB, 128 distinct D-numbers, max D130** and **no capstone**. `D17_cross_target_synthesis` is number 17 of 130 and predates nearly everything it would need to synthesize.

This is the **Android section** of the objective's final leg — *detection engine / C2 fingerprint DB / threat model*. It does not attempt the capstone. It delivers one section of it, with the discarding done in the open.

**An enumerated scope is not a population.** What follows is a **census of what the two Android families in this corpus ship**, not a claim about Android malware generally. Every generalisation is marked as one.

---

## 1. C2 / network fingerprint surface

### 1.1 Instrument and cardinality

The string pool of each DEX, read directly from `string_ids`, decoded as ULEB128-length + MUTF-8. No disassembler, no third-party tool.

| artifact | bytes | pool strings | types |
|---|---|---|---|
| APK `classes.dex` | 3,604,660 | **26,908** | 3,403 |
| AAB `base/dex/classes.dex` | 4,340,284 | **32,392** | 4,242 |

**Control (a check that can fail, placed before the readings that depend on it):** method_ids span `26,535 * 8 = 212,280` B from offset 298,376, ending exactly at `class_defs_off` = **510,656**; **COUNTED: 0 malformed method_id rows of 26,535.** proto `return_type_idx` max = 3,400 against 3,403 types; **COUNTED: 0 malformed proto rows of 6,109.**

### 1.2 The endpoint — SHIPPED, and the two builds disagree

| artifact | IPv4 literal | pool id | port | pool id | status |
|---|---|---|---|---|---|
| APK `app-release.apk` | `192.168.43.113` | 3133 | `8000` | 3136 | **SHIPPED** |
| AAB `app-release.aab` | `192.168.43.129` | 3334 | `8000` | 3338 | **SHIPPED** |
| source `config.java` | `192.168.0.105` | — | `8888` | — | **SOURCE-ONLY** |

All three appear in the **config-class literal cluster**, adjacent to the same neighbours in both artifacts (`2nd pass`, `3rd pass`).

**This is the headline result, and it is not the addresses — it is that there are three of them.** One source tree produces two shipped artifacts whose hardcoded C2 endpoint differs. The source literal is a third value that **appears in neither shipped artifact** — `192.168.0.105` occurs **0 times** in both DEX files.

**Confidence: [verified] for the bytes; [inferred] for the mechanism.** The substitution clearly happens at build time and clearly varies by build — that is the observation, and it is byte-level. **The pipeline that performs it was not read**, so "why the two builds differ" is a hypothesis (a build-machine-local IP baked in at compile time) and is labelled as one. §6 records this as an open residual.

### 1.3 The extra network stack in the AAB — the asymmetry is the fingerprint

| probe | APK | AAB |
|---|---|---|
| IPv4 literals | 1 | 1 |
| bare-number ports | **2** (`0`, `8000`) | **5** (`0`, `300`, `8000`, `95`, `98`) |
| `http://` / `https://` URLs | 3 | **13** |
| TLS-matching strings | 42 | **193** |
| `java/net` type descriptors | 14 | **21** |

AAB-only URL families: **`slf4j` (9 entries), `mina.apache.org`, `springframework`**. AAB-only network types: `ConnectException`, `Inet4Address`, `Inet6Address`.

**Reading:** the AAB contains an FTP server, an SSL engine and a logging framework that the APK does not. **A detector matching on "this APK contains a C2 endpoint" would fire identically on both; a detector matching on the network stack's size and composition would separate them.** The asymmetry, not the address, is the discriminative signal.

**Confidence: [verified].** Counts are pool enumeration with the cardinality printed above.

### 1.4 The wire protocol — SHIPPED constants, SOURCE-ONLY structure

**A discarded false lead, recorded because it is the reason this section is trustworthy.** A keyword sweep of the pool for known RAT commands returned **34 "hits"** across 26,908 strings. Every one was a generic library or framework word: `get`, `set`, `read`, `write`, `list`, `start`, `stop`, `info`, `id`, `token`, `stream`, `dir`, `exec`, `cmd`. **A fingerprint DB built on that sweep would have shipped 34 false positives and called it a detection surface.** The sweep was discarded.

The real protocol is a **plain-text, newline-delimited `equals()` dispatch chain** in `tcpConnection.java`, lines **105–288**:

| verb | source line | capability |
|---|---|---|
| `getIP` | L182 | device IP via `ipAddr.getIPAddress(true)` |
| `getLocation` | L211 | GPS |
| `startAudio` / `stopAudio` | L219 / L226 | microphone |
| `stopVideo` | L242 | camera |
| `getCallLogs` | L248 | call log |
| `getMACAddress` | L261 | MAC |
| `getSMS <box>` | L189–L201 | SMS; `box[1]` selects `inbox` / `sent` |

**The `getX` camelCase command vocabulary is the fingerprint** — string constants that survive compilation because they are compared against, and cannot be optimised away. A parameterised verb is dispatched by splitting on a single space (`line.split(" ")` at L189, L196, L235).

**Status: SHIPPED for the verb constants** (they are pool entries — `getIP`, `getLocation`, `startAudio`, `stopAudio`, `stopVideo`, `getCallLogs`, `getMACAddress` are all present in the compiled pool). **SOURCE-ONLY for the dispatch structure** — the `if/else if` ladder at L105–288 is source text; the compiled control flow was not disassembled. **Confidence: [verified] for constants, [read] for structure.**

### 1.5 Protocol-absent fields — a negative worth recording

| probe | APK | AAB |
|---|---|---|
| `User-Agent` string | **0** | **0** |
| `Content-Type` string | **0** | **0** |
| `multipart` / `form-data` | **0** | **0** |

**Instrument check before filing these zeros, per the D130 correction:** the instrument was proven to have a name table in the same run by finding 26,908 and 32,392 pool strings respectively, and by the positive TCP hits in the same sweep. **A zero from this instrument is a real zero, not a null instrument.** The transport is a raw `java.net.Socket` with `getInputStream`/`getOutputStream` — **there is no HTTP anywhere in either app.** No header fingerprint can exist because no header is emitted.

---

## 2. The permission-as-fingerprint problem

### 2.1 The control, built before the claim

**This is the section where the honest answer is a negative result.**

Android permission sets are a **dangerous** fingerprint family: widely shared, weakly discriminative, and trivially matched by legitimate software. **A permission every legitimate app requests cannot discriminate.** So the control is applied first — for every permission, name the legitimate software that also requests it, and discard any row that a legitimate app matches.

| permission | source line | legitimate software that also requests it | discriminates? |
|---|---|---|---|
| `INTERNET` | L7 | every networked app on Play; browsers, email, weather, banking | **NO** |
| `ACCESS_NETWORK_STATE` | L6 | nearly universal among networked apps; required for connectivity checks | **NO** |
| `ACCESS_WIFI_STATE` | L8 | WiFi analysers, speed tests, streaming, VoIP, captive-portal apps | **NO** |
| `RECEIVE_BOOT_COMPLETED` | L9 | alarm clocks, launchers, sync clients, antivirus, MDM agents | **NO** |
| `WAKE_LOCK` | L10 | video players, music, navigation, sync, download managers | **NO** |
| `CAMERA` | L11 | camera apps, QR scanners, video chat, document scanners, flashlights | **NO** |
| `READ_EXTERNAL_STORAGE` | L19 | photo editors, file managers, media apps, social, backup | **NO** |
| `WRITE_EXTERNAL_STORAGE` | L20 | download managers, editors, scanners, backup tools | **NO** |
| `VIBRATE` | L21 | keyboards, games, alarm clocks, camera shutter (haptics are generic) | **NO** |
| `READ_SMS` | L22 | SMS backup, launchers, smartwatches, banking 2FA/OTP readers, antivirus | **NO** |
| `ACCESS_FINE_LOCATION` | L23 | maps, rideshare, weather, fitness, food delivery, cameras | **NO** |
| `ACCESS_COARSE_LOCATION` | L24 | virtually every location-aware app, as a fallback | **NO** |
| `READ_CALL_LOG` | L25 | call-blockers, dialers, call recorders, carriers, CRM | **NO** |
| `RECORD_AUDIO` | L26 | voice memos, video chat, assistants, tuners, transcription | **NO** |
| `SYSTEM_ALERT_WINDOW` | L27 | screen recorders, overlays, assistive tools, floating notes | **NO** |
| `READ_PHONE_STATE` | L28 | call recorders, dual-SIM managers, games (device ID), carriers | **NO** |

**COUNTED: 16 permissions; 16 rows tested; 0 discriminate. Input cardinality: source manifest 3,437 B; 16 `uses-permission` entries.**

`VIBRATE` is filed as **NON-DISCRIMINATING** with its reason (haptics are generic) — not as a placeholder. **An honest "this row carries no signal" is a result.**

### 2.2 What survives, and it is not the list

**No individual permission in either family is a fingerprint.** The discriminative facts are relational, not membership:

1. **The declared-vs-shipped drop.** Source declares **16**; the **APK ships 15** and the **AAB ships 15**. `ACCESS_NETWORK_STATE` is present at source L6 and in the APK, and **absent from the AAB**. **A detector comparing declared to shipped catches this; a detector reading either alone does not.**
2. **The request set is broad and unrelated to function.** A single app requesting `READ_SMS` + `READ_CALL_LOG` + `RECORD_AUDIO` + `CAMERA` + `SYSTEM_ALERT_WINDOW` + `ACCESS_FINE_LOCATION` describes an app that is a dialer, an SMS client, a camera, a voice recorder, a screen recorder **and** a map — simultaneously. **The signal is the union, not the members.** Named legitimate comparators for that union were not found in this pass and are not claimed.
3. **Cross-family divergence.** AndroRAT 16, AhMyth 18 (D122). The sets overlap heavily. **The divergence is in the tail, not the body.**

**Confidence: [read] for the table above (source text and manifest bytes); [inferred] for the union argument, which is a hypothesis this census supports but does not prove.** Proving it needs a legitimate-app corpus, which this corpus does not contain. **That is stated rather than worked around.**

---

## 3. The DEX-vs-source gap — a bounded rate, not a rule

### 3.1 The test

Enumerate every `.java` under `app/src/main`, extract `package` plus every top-level `class` declaration, convert to a DEX type descriptor, and test membership against the DEX type table. **INPUT CARDINALITY: 19 files, 19 declarations.**

| artifact | types | declared classes absent | rate |
|---|---|---|---|
| APK | 3,403 | **3** — `controlPanel`, `jumper`, `keypadListner` | **3/19 = 16%** |
| AAB | 4,242 | **4** — the three above **plus `config`** | **4/19 = 21%** |

**Control:** the 16 present classes include all 12 `R$*` classes and `R`, and `BuildConfig` — independently confirmed in both DEXes at `type_id[1922]` by D114. **The instrument finds classes that are built, so the 3 and 4 are real absences rather than a broken descriptor conversion.**

### 3.2 The AAB drops `config` itself

**New in D137, and it explains an asymmetry D114 recorded but could not account for:** the APK has the class `config` but not the bare string `config`; the AAB has the bare string `config` (pool 18539) but **no class**. The AAB does not merely lose the initialiser — **it loses the class that owns the endpoint.** That is consistent with the AAB's C2 address surviving as an unowned pool string.

### 3.3 Is it generalisable? **No.**

**One-off, n=3 (APK) / n=4 (AAB), not a detection rule.** Three of nineteen is a **rate**, and a rate of roughly one in six is close to what ordinary build-time dead-code elimination, manifest pruning and ProGuard-style reachability analysis produce from any non-trivial source tree. **A signal with n=3 does not carry a detection rule**, and D130's two-tier correction is the standing warning about exactly this error shape: a zero or a small count from an unverified instrument is not a finding.

The **co-occurrence** is the more interesting fact — three of the four absences are classes whose manifest components were also pruned (`keypadListner` receiver L65–70, `controlPanel` activity L39, `jumper` has no component), and three DEX-present callers invoke `new jumper(...)`. **Live callers referencing an absent class is a symptom worth a probe, not a rule.** Filed as a hypothesis with its n stated.

**Confidence: [verified] for the counts; [inferred] for the dead-code explanation; [absence] for any general rule.**

---

## 4. UNIQUE vs SHARED — the discriminator

| observation | AndroRAT APK | AndroRAT AAB | AhMyth | discriminator? |
|---|---|---|---|---|
| raw `java.net.Socket` transport | yes | yes | unknown | **shared between AndroRAT builds** |
| HTTP header emission | **none** | **none** | unknown | **absence is distinctive** |
| `getX` plaintext command verbs | yes | yes | unknown | **strong, family-specific** |
| hardcoded RFC1918 C2 endpoint | yes | yes | unknown | **moderate — common in RATs** |
| C2 endpoint **differs between builds** | `192.168.43.113` | `192.168.43.129` | — | **strong, build-specific** |
| extra FTP/SSL/logging stack | no | **yes** | unknown | **strong, artifact-specific** |
| exported receiver, no permission guard | yes | yes | yes (D122) | **strong, cross-family** |
| `INTERNET` permission | yes | yes | yes | **none** |
| `targetSdkVersion` 22 | yes | yes | 18 (D122) | **weak** |
| source classes absent from DEX | 3/19 | 4/19 | unknown | **not generalisable (§3.3)** |

**The discriminator is the conjunction of: a plaintext line-protocol command vocabulary, no HTTP layer at all, and an exported unguarded receiver.** Each element alone is weak. `INTERNET` is not a signal; `EXPORTED_RECEIVER + NO_HTTP + PLAINTEXT_VERBS` is a shape.

**AhMyth columns are `unknown`, and that is deliberate.** D122 established that the corpus contains **0 AhMyth APK / 0 AAB / 0 DEX** (8,437 files walked, positive control on `androrat\` returning both). AhMyth is present only as a **compiled AXML manifest template** (5,428 B), which supports manifest-level rows and **nothing** at bytecode level. **Those cells are not filled with the AndroRAT result.**

---

## 5. Probe zeroes and instrument validation

Per the standing correction: **a zero is only a finding if the instrument demonstrably had a name table.**

| probe | result | instrument validated in the same run by |
|---|---|---|
| `User-Agent` in APK/AAB pool | 0 | 26,908 / 32,392 strings enumerated; positive TCP verb hits |
| `Content-Type` in APK/AAB pool | 0 | as above |
| app methods returning `java/net` type | 0 | 3,403 types, 26,535 methods; 0 malformed rows; proto bounds checked |
| `AhMyth` APK/AAB/DEX in corpus | 0 | D122: 8,437 files, positive control on `andorat` returning 2 |
| source classes absent from APK | 3 | 16 present incl. 12 `R$*` + `BuildConfig` |

**Every zero above is accompanied by the positive control that proves the instrument was live.** No probe in this report files a zero from an unverified reader.

---

## 6. Method, limits, and open residuals

**Method.** Hand-written DEX and AXML parsers; no disassembler, no third-party tool, no execution. Bounds controls run before dependent readings. Both artifacts read with the same instrument, so APK/AAB comparisons are instrument-neutral. Source claims cited as `[source: file:line]`.

**Limits.**

- **No execution. No device. No emulator. No network. No live C2. No REA. No `open_binary`.** No artifact installed, run, or opened.
- **The C2 substitution mechanism is not established.** Three addresses across three layers is a byte-level observation. The build-time substitution is a hypothesis; **the build pipeline was not read.**
- **The dispatch ladder is source text.** The compiled control flow of `tcpConnection.java` was not disassembled, so verb ordering, unreachable branches and obfuscated dispatch are unverified. The verb **constants** are shipped and confirmed in the pool.
- **AhMyth bytecode is entirely unknown** — no compiled AhMyth artifact exists in this corpus. All AhMyth cells are manifest-level only.
- **The permission union argument is a hypothesis**, untestable without a legitimate-app corpus, which this corpus lacks.
- **§3 is a rate, not a rule.** n=3 / n=4 out of 19. Not generalisable, stated as such.
- **Endpoints are RFC1918 private addresses.** They are build-time artefacts of a lab environment, not operational C2 infrastructure. This does not weaken the fingerprint — the *fingerprint* is the literal-in-pool pattern — but the addresses have no external meaning.

**Open residuals for the lead:**

1. **The build-substitution mechanism.** Two builds of one source tree produced different C2 literals and different network-stack contents. Reading the build pipeline would convert a strong observation into a mechanism. `videoRecorder`, `audioManager` and `controlPanel` are absent from both artifacts while `tcpConnection` — which the source also constructs — is present. **What selects a class for inclusion was not determined.**
2. **Why the AAB carries an FTP server, an SSL engine and `slf4j` that the APK does not.** Consistent with an unfiltered dependency set, but the dependency resolution was not read.
3. **A legitimate-app comparator corpus** is what §2 needs to convert its union hypothesis into a control. Not available here.

**Own errors, recorded:**

- **D121 §1.3 is superseded by D122** and I have withdrawn it. I tested D122's `p+20` claim against raw bytes: `rec[0]+20 = 55` = ns of rec[1], `rec[1]+20 = 55` = ns of rec[2], `rec[2]+20 = 2` = the following chunk's header low byte (`u16 = 0x0102`). **D122 is correct on every point.**
- **I nearly shipped a 34-entry false-positive command list.** The keyword sweep in §1.4 returned only generic library words. Discarding it is the substance of that section.
- **I re-committed an `IndexError`** from indexing a proto index into the type table — the identical bug recorded in D121 §6. It surfaced in one step because the bounds control printed `return_type_idx max = 3400` against 3,403 types, which did not match the failure.
- **My first D125 freeze failed its own verification** (`btick_nonascii` claim 0, actual 1 — a `*` used as arithmetic inside a code span). Caught by my own check.

---

## 7. Frozen measurement, fixed point

```
D137 frozen measurement -- counts taken on this file including this block

  bytes            : 20613
  lf               : 259
  cr               : 0
  bom              : absent
  fffd             : 0
  strict_utf8      : decodes without error
  headings         : 19     (regex ^#{1,6}[ \t], basis: bare-LF line starts)
  h1_count         : 1     (exactly one '# ' heading)
  dup_headings     : 0     (whole-line exact match, table separators excluded)
  cyrillic_es_0441 : 0
  ellipsis_2026    : 0
  non_ascii        : 50
  btick_nonascii   : 0     (backticked tokens containing non-ASCII content)
  abs_paths        : 0     (absolute path tokens in code spans)
  sha256_zeroed    : 222F0EE743C27CC4C6AEB9C7DFF3AAC6678D319147B9CC7E0E06B3DDB7A5A892
                     (digest of this file with this one 64-char field replaced
                      by 64 zeros; reproducible by a third party from the artifact
                      alone. A file cannot contain its own true digest -- the
                      authoritative post-freeze digest is reported externally.)
```
