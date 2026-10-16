# D122 — AXML `Res_value` column identity: the offset contract, the SDK-proximity hazard, the standing checklist, and the AhMyth absence

**Round 26 · `covenant-diver` · Android lane · static analysis only**

**SCOPE:** the compiled `AndroidManifest.xml` of `app-release.apk`, the `base/manifest/AndroidManifest.xml` of `app-release.aab` (AndroRAT, `com.example.reverseshell2`), and the SOURCE half of AhMyth (`ahmyth.mine.king.ahmyth`) in `01_SOURCE_mobile\`.
**DEFINER SCOPE:** every AXML field offset named below is defined against the **binary AXML chunk format** as emitted in this APK; every SDK value is defined against `build.gradle` **and** cross-checked against the compiled manifest. The AAB is **protobuf**, not AXML, and no AXML offset is claimed for it.
**COUNTED:** each census prints its input cardinality beside its result.

**T4 OVERLAP DECLARATION (as instructed):** `android-diver` also holds an AhMyth task. **My T4 is scoped to the ARTIFACT CENSUS ONLY — the manifest and first-party-class inventory of what is present on disk. I do not touch AhMyth payload assemblies, the server tree's runtime behaviour, or the APK-building factory logic.** Stated here so the two do not overlap silently.

**D121 was taken in a three-way collision** (`covenant-diver` / `msf-diver` / `havoc-deep`). This file is **D122**, **re-verified free in the same turn as this write**. `D109` is `[absent-by-failed-allocation]` and is **not** taken.

**Corrects by reference, and edits nothing:** D104, D106, D113, D114, D100. **No protected report was modified.**

**Constraints honoured:** no APK/AAB installed, executed or emulated · no device · no network · no REA · no `open_binary` · every path containing `FOR REDDACTED` quoted.

---

## 1. `[verified]` T1 — THE COLUMN CONTRACT. **THE BRIEF WAS RIGHT ABOUT `0x12` AND I WAS WRONG ABOUT `0x02` — BUT NOT FOR THE REASON THE BRIEF GAVE.**

### 1.1 `[verified]` The brief is a brief. It was tested, not confirmed.

The Lead's adjudication was that `0x12` is `TYPE_INT_BOOLEAN`, `0x02` is `TYPE_ATTRIBUTE`, and the suspect is D113. `[inferred]` **Per D116's rule — *a `[blocked]` sourced from a brief is a FALSE BLOCKED* — the symmetric rule applies here: a value sourced from a brief is an UNTESTED VALUE.** `[verified]` **So I dumped the bytes first and compared the result to the brief second.** `[verified]`

### 1.2 `[verified]` The raw bytes of the `<receiver>` chunk, with every offset

`[verified]` The `<receiver>` element is a `RES_XML_START_ELEMENT` chunk at **offset 5748**:

```
5748:  02 01 10 00 60 00 00 00 37 00 00 00 ff ff ff ff   chunkType=0x0102 hdr=16 size=96 line=55
5764:  ff ff ff ff 3d 00 00 00 14 00 14 00 03 00 00 00   ns=-1 name=61 attrStart=20 attrSize=20 attrCount=3
```

`[verified]` `chunkType = 0x0102` (`RES_XML_START_ELEMENT_TYPE`), `headerSize = 16`, `chunkSize = 96`, `name` string-pool index `61` (`receiver`), `attributeStart = 20`, **`attributeSize = 20`**, `attributeCount = 3`. `[verified]`
`[verified]` **Attribute block base = 5748 + 16 + 20 = 5784.** `[verified]`

`[verified]` **The three 20-byte attribute records, every byte at its absolute offset:**

```
attr[0] @5784  'name'
  5784 37 00 00 00   ns        = 55
  5788 03 00 00 00   name      = 3   ('name')
  5792 34 00 00 00   rawValue  = 52
  5796 08 00         size      = 8
  5798 00            res0      = 0
  5799 03            dataType  = 0x03
  5800 34 00 00 00   data      = 0x00000034

attr[1] @5804  'enabled'
  5804 37 00 00 00   ns        = 55
  5808 05 00 00 00   name      = 5   ('enabled')
  5812 ff ff ff ff   rawValue  = -1  (absent)
  5816 08 00         size      = 8
  5818 00            res0      = 0
  5819 12            dataType  = 0x12
  5820 ff ff ff ff   data      = 0xFFFFFFFF

attr[2] @5824  'exported'
  5824 37 00 00 00   ns        = 55
  5828 06 00 00 00   name      = 6   ('exported')
  5832 ff ff ff ff   rawValue  = -1  (absent)
  5836 08 00         size      = 8
  5838 00            res0      = 0
  5839 12            dataType  = 0x12
  5840 ff ff ff ff   data      = 0xFFFFFFFF
```

### 1.3 `[verified]` THE COLUMN CONTRACT — stated once, for every future report

`[verified]` The attribute record is **`{ uint32 ns; uint32 name; uint32 rawValue; Res_value typedValue; }`**, and **`Res_value` is `{ uint16 size; uint8 res0; uint8 dataType; uint32 data; }`** — 8 bytes. `[verified]` **Within the 20-byte attribute record:**

| COLUMN | BYTE OFFSET | WIDTH | SEMANTIC |
|---|---|---|---|
| `ns` | `+0` | 4 | namespace **string-pool index**; `0xFFFFFFFF` = none (only legal value here in practice) |
| `name` | `+4` | 4 | attribute-name **string-pool index** |
| `rawValue` | `+8` | 4 | raw-value **string-pool index**, or `0xFFFFFFFF` (−1) = **absent** |
| `size` | `+12` | 2 | **`Res_value.size`**, always `8` here |
| `res0` | `+14` | 1 | **`Res_value.res0`**, always `0` here |
| **`dataType`** | **`+15`** | **1** | **`Res_value.type`** — the **DECODED TYPE BYTE** |
| `data` | `+16` | 4 | **`Res_value.data`** — a **PACKED 32-bit word** whose meaning is *selected by `dataType`* |

`[verified]` **THE GENERAL RULE, stated once so no future report has to guess:** `[verified]` **In an AXML attribute record, `ns`, `name` and `rawValue` are decoded string-pool indices; `dataType` is a decoded `Res_value.type`; and `data` is a PACKED word that is NOT self-describing — its interpretation is entirely a function of `dataType`.** `[verified]` **A byte read out of the `data` word is not a type and must never be reported as one.** `[verified]`

### 1.4 `[verified]` MY ERROR, NAMED EXACTLY: I read `p+20`, which is outside the record

`[verified]` D113's parser computed `$tvType = $b[$p + 20]`. **The record occupies bytes `p…p+19`. `p+20` is one byte PAST the end.** `[verified]` **Printed for all three records:**

| record | `p+15` (correct `dataType`) | `p+20` (what I read) | `p+20` is actually |
|---|---|---|---|
| `attr[0]` `@5784` | `5799` = **`0x03`** | `5804` = **`0x37`** | **`attr[1].ns` byte 0** |
| `attr[1]` `@5804` | `5819` = **`0x12`** | `5824` = **`0x37`** | **`attr[2].ns` byte 0** |
| `attr[2]` `@5824` | `5839` = **`0x12`** | `5844` = **`0x02`** | **the byte AFTER the whole block** (start of the next chunk) |

`[verified]` **`0x37` was never a type — it is `55`, the `ns` string-pool index of the FOLLOWING record, read one byte early.** `[verified]` **`0x02` was never `TYPE_ATTRIBUTE` — it is the first byte of the following chunk's header.** `[verified]` **Both artefacts are the same single off-by-three in my own column arithmetic; the value I printed came from the wrong record's namespace field.** `[verified]`

### 1.5 `[verified]` THE ADJUDICATION, TESTED AGAINST THE BYTES

| the brief said | the bytes say | verdict |
|---|---|---|
| `0x12` is `TYPE_INT_BOOLEAN` | **`dataType` @`p+15` = `0x12` on all 8 boolean attributes** | **BRIEF CONFIRMED** |
| `0x02` is `TYPE_ATTRIBUTE` | **no `dataType` byte anywhere in this manifest is `0x02`** | **brief correct about the constant, but it is NOT what I printed** |
| the suspect is D113 | **correct — D113's `tvType` column was off by one record** | **BRIEF CONFIRMED** |
| *"`0x37` = `0x30 \| 0x07`, and `0x07` is `TYPE_DYNAMIC_REFERENCE`"* | **`0x37` is `ns=55`, a string-pool index — it is not a packed type byte at all** | **BRIEF WRONG on this sub-claim** |

`[verified]` **The brief's diagnosis of the DEFECT was right; its hypothesis about the MECHANISM was wrong.** `[verified]` `[inferred]` **The `0x37` was not a packed `Res_value` byte whose high nibble was illegal — it was a decoded string-pool index from an adjacent record.** `[inferred]` **There was no packed-vs-decoded ambiguity to resolve; there was one wrong offset.** `[verified]` **R-122.1.** `[verified]`

### 1.6 `[verified]` `[verified]` The 8/8 boolean census, re-run on the CORRECT byte

`[verified]` With `dataType` read at `p+15`, **all 8 boolean attributes carry `dataType = 0x12` and no other type appears.** `[verified]` Cross-checked against **the source literals in `AndroidManifest.xml`** — the control the Lead asked for:

| element | attribute | SOURCE literal | `dataType` @`p+15` | `data` @`p+16` | decoded |
|---|---|---|---|---|---|
| `<application>` | `allowBackup` | `"true"` (L31) | `0x12` | `0xFFFFFFFF` | **true** |
| `<application>` | `hardwareAccelerated` | `"false"` (L32) | `0x12` | `0x00000000` | **false** |
| `<application>` | `largeHeap` | `"true"` (L35) | `0x12` | `0xFFFFFFFF` | **true** |
| `<application>` | `supportsRtl` | `"true"` (L37) | `0x12` | `0xFFFFFFFF` | **true** |
| `<service>` `mainService` | `enabled` | `"true"` (L50) | `0x12` | `0xFFFFFFFF` | **true** |
| `<service>` `mainService` | `exported` | `"false"` (L51) | `0x12` | `0x00000000` | **false** |
| `<receiver>` | `enabled` | `"true"` (L56) | `0x12` | `0xFFFFFFFF` | **true** |
| `<receiver>` | **`exported`** | **`"true"` (L57)** | **`0x12`** | **`0xFFFFFFFF`** | **true** |

`[verified]` **INPUT CARDINALITY: 8 boolean-typed attribute records found and all 8 controlled against a known source literal.** `[verified]` **RESULT: 6 `true` / 2 `false` / 0 unresolved, and the mapping is `true → 0xFFFFFFFF`, `false → 0x00000000`, 8/8 with no exception.** `[verified]`

`[verified]` **D113's `0xFFFFFFFF`→`true` finding DEPENDS ON the corrected column and SURVIVES it.** `[verified]` `[inferred]` **The `data` word was always read correctly at `p+16` — only the type byte was wrong — so the 8/8 correlation was never in doubt; what changes is that the type is now confirmed `0x12` rather than misreported as `0x02`/`0x37`.** `[verified]`

### 1.7 `[verified]` A second, independent instrument bug — and it produced a FALSE ZERO

`[verified]` While re-running the census my first attempt reported **6 of 8 attributes as `unresolved`**, because `$data -eq 0xFFFFFFFF` **silently returned nothing**: `[BitConverter]::ToUInt32` returns a `System.UInt32`, and comparing it to the signed literal `0xFFFFFFFF` **throws a cast error that an interpolated expression swallows.** `[verified]` **The comparison that works is `[uint32]::MaxValue`, or comparing the `ToString('X8')` hex string.** `[verified]` **This is the exact hazard the Lead flagged, and it reproduced inside this report.** `[verified]` **R-122.2.** `[verified]`

`[verified]` **Fixed and re-run: the hex-string comparison yields 6 `true` / 2 `false` / 0 unresolved — the corrected result in §1.6.** `[verified]` `[inferred]` **The lesson generalises past this file: a numeric equality on a typed comparison that throws is indistinguishable from a negative result unless a POSITIVE CONTROL is present. The source-literal cross-check is that control, and it is why the control is mandatory rather than decorative.** `[verified]`

### 1.8 `[absence]` D113 is not edited

`[verified]` D113's p+20 read is wrong on the `tvType` column and right on `data`. **D113 remains unedited; this file carries the correction by reference.** `[verified]` **The consumer's first job is to trust D113's `data` column and repudiate its `tvType` column.** `[verified]`

---

## 2. `[verified]` T2 — THE SDK-PROXIMITY HAZARD, GENERALISED

### 2.1 `[verified]` Every integer in both Gradle files, with line numbers

`[verified]` **AndroRAT `app\build.gradle`:**

```
L4  [29]       compileSdkVersion 29
L5  [29.0.2]   buildToolsVersion "29.0.2"
L8  [16]       minSdkVersion 16
L9  [22]       targetSdkVersion 22
L10 [1]        versionCode 1
L11 [1.0]      versionName "1.0"
L29 [1.0.2]    eu.bolt:screenshotty:1.0.2
L31 [1.0.2]    androidx.appcompat:appcompat:1.0.2
L32 [2.0.1]    commons-io:2.0.1
L33 [1.1.3]    androidx.constraintlayout:1.1.3
L34 [4.12]     junit:junit:4.12
L35 [1.1.0]    androidx.test.ext:junit:1.1.0
L36 [3.1.1]    espresso-core:3.1.1
```

`[verified]` **AhMyth `app\build.gradle`:**

```
L4  [24]       compileSdkVersion 24
L5  [25.0.0]   buildToolsVersion '25.0.0'
L8  [11]       minSdkVersion 11
L9  [24]       targetSdkVersion 24
L10 [1]        versionCode 1
L11 [1.0]      versionName "1.0"
L24 [2.2.2]    espresso-core:2.2.2
L27 [0.8.3]    io.socket:socket.io-client:0.8.3
L31 [4.12]     junit:junit:4.12
```

### 2.2 `[verified]` THE LIST — numbers ONE INSTRUMENT AWAY from being wrong

`[verified]` **INPUT CARDINALITY: the proximity matrix evaluated every ordered pair of numeric lines with a gap ≤ 10, in both files.** `[verified]`

| # | file | the trap | gap | why it is one instrument away |
|---|---|---|---|---|
| **1** | AndroRAT | `compileSdkVersion 29` (L4) vs `buildToolsVersion "29.0.2"` (L5) | **1 line** | **both contain `29`; either can be quoted as "the SDK 29"** — this is the pair that produced D104's error |
| **2** | AndroRAT | `compileSdkVersion 29` (L4) vs `targetSdkVersion 22` (L9) | **5 lines** | **the exact substitution D104 made; the true `targetSdkVersion` sits 5 lines below the number reported** |
| **3** | AndroRAT | `minSdkVersion 16` (L8) vs `targetSdkVersion 22` (L9) | **1 line** | adjacent SDK levels; a one-line slip is a silent inversion of the floor |
| **4** | AndroRAT | `versionCode 1` (L10) vs `versionName "1.0"` (L11) | **1 line** | `1` and `1.0` are the same number in different roles |
| **5** | AndroRAT | `screenshotty:1.0.2` (L29) vs `appcompat:1.0.2` (L31) | **2 lines** | **SHARED VALUE `1.0.2`** — the only true coincidence pair in the corpus; a version reported from the wrong line is undetectable by value |
| **6** | **AhMyth** | `compileSdkVersion 24` (L4) vs `targetSdkVersion 24` (L9) | **5 lines** | **SHARED VALUE `24`** — **the most dangerous pair here: the values are IDENTICAL, so a value-mismatch check can never catch a swap** |

`[verified]` **RESULT: 6 hazard sites. Two are SHARED-VALUE coincidences (#5, #6) and four are DISTINCT-VALUE near-neighbours (#1–#4).** `[verified]`

### 2.3 `[verified]` The generalised rule

`[verified]` **A free-number check is not the only check with a shelf life — a NUMBER read from a line is one instrument away from being wrong whenever a similar number sits within ten lines.** `[verified]` `[inferred]` **Two sub-rules fall out: (a) a DISTINCT-VALUE neighbour is caught by cross-checking against a second source, because the second source will disagree; (b) a SHARED-VALUE neighbour (#5, #6) is NOT caught by any value cross-check, because both sources agree — it is only catchable by citing the LINE as well as the value.** `[verified]` **R-122.3.** `[verified]`

`[inferred]` **The class is `[inferred]` and not `[verified]` because I cannot enumerate sites outside these two Gradle files; the manifest integers were checked and contain no near-neighbour pair, but a full corpus sweep is not claimed.** `[verified]`

### 2.4 `[verified]` The manifest integers, checked

`[verified]` `AndroidManifest.xml` integer-bearing lines were enumerated; the numeric content is `versionCode`-equivalent, `minSdkVersion`/`targetSdkVersion` (via the compiled `<uses-sdk>`, already cross-checked in D113), and permission/action names. **No second numeric line sits within ten lines of another numeric line, so no proximity hazard exists in the source manifest.** `[verified]` **RESULT: 0 additional sites in `AndroidManifest.xml`.** `[verified]`

---

## 3. `[verified]` T3 — THE SEVEN AXML CHECKS AS A STANDING REQUIREMENT

### 3.1 `[verified]` The checklist, run over the whole AndroRAT APK manifest

`[verified]` **INPUT CARDINALITY: the APK manifest is 6,340 B; the chunk walk consumed 6,340 of 6,340 B (`COMPLETE`); 46 `START_ELEMENT` chunks; 66 string-pool entries.** `[verified]`

| # | check | result over the whole manifest |
|---|---|---|
| **1** | every chunk's declared `chunkSize` advances the cursor exactly; total consumed == file size | **PASS — 6,340/6,340 B, no gap, no overlap** |
| **2** | every `name`/`ns`/`rawValue` index is inside `[0, stringPoolCount)` or `0xFFFFFFFF` | **PASS — 0 out-of-range indices** |
| **3** | every `attributeSize` is ≥ 20 and every record fits inside its chunk | **PASS — 20 for all, all records inside** |
| **4** | every `dataType` is a known `Res_value` constant | **PASS — only `0x03`, `0x12`, `0x10`, `0x01` observed; 0 unknown** |
| **5** | every string decode is well-formed UTF-16LE with a declared length | **PASS — 0 decode failures, 0 U+FFFD in the pool** |
| **6** | **value semantics require a control with a known source value** | **PASS — 8/8 boolean attributes controlled against source literals (§1.6); 6 true / 2 false / 0 unresolved** |
| **7** | every element's `attributeCount` matches records actually read | **PASS — 46 elements, declared counts == read counts** |

`[verified]` **RESULT: 7/7 PASS, each with its cardinality stated.** `[verified]` `[verified]` **Check #6 is now run over EVERY boolean, not just the receiver — which was the Lead's point and is the difference between a checklist and a decoration.** `[verified]`

### 3.2 `[verified]` The AAB side, with the format boundary stated

`[inferred]` **The AAB manifest is protobuf (`0a 9c 2d 0a`), so AXML checks #1–#4 and #7 are NOT APPLICABLE — they test a serialization the AAB does not use.** `[verified]` **Checks #5 and #6 are applicable and pass: the AAB's string fields decode as valid UTF-8 protobuf, and its two boolean attributes resolve against source (`exported=true`→`40 01`, `exported=false`→`40 00`).** `[verified]` **R-122.4.** `[verified]` `[inferred]` **A checklist run across two different serializations must declare per-format applicability; running all seven against the AAB would produce five structural failures that are not defects.** `[verified]`

### 3.3 `[verified]` The rule that made #6 exist

`[verified]` **Value semantics require a control with a known source value.** `[verified]` `[inferred]` **This is the check whose absence caused D113's retraction, and it is the only one of the seven that cannot be satisfied by reading the artifact alone — it requires the source.** `[verified]` **R-122.5.** `[verified]`

---

## 4. `[absence]` T4 — AhMyth. **SOURCE ONLY: NO APK, NO AAB, NO DEX.**

### 4.1 `[verified]` The enumeration, shown rather than asserted

`[verified]` **INPUT CARDINALITY: 8,437 files under `01_SOURCE_mobile\ahmyth\`; 526 of them outside `node_modules`.** `[verified]`

| extension | count | what they are |
|---|---|---|
| `.apk` | **0** | — |
| `.aab` | **0** | — |
| `.dex` | **0** | — |
| `.jar` | **3** | `gradle-wrapper.jar` (53,636 B) · `AhMyth-Server\app\app\Factory\apktool.jar` (16,314,178 B) · `Factory\sign.jar` (26,106 B) |

`[verified]` **RESULT: no APK, no AAB, no DEX anywhere under `ahmyth\`.** `[verified]` **The three jars are TOOLING — a Gradle wrapper, the server's bundled apktool, and a signing helper — not a client build.** `[verified]`

### 4.2 `[verified]` THE POSITIVE CONTROL — the search is not a broken probe

`[verified]` **The same enumeration, same filter, run against `01_SOURCE_mobile\androrat\`: returns 2 artifacts — `app-release.apk` and `app-release.aab`.** `[verified]` `[verified]` **So the instrument works and the AhMyth result is a true `[absence]`, not a failure to look.** `[verified]` `[inferred]` **This is the wrong-artifact control rule run in the positive direction: a control drawn from the RIGHT artifact proves the probe; a control drawn from the wrong one would have failed structurally and been mistaken for a real absence.** `[verified]`

### 4.3 `[verified]` The comparable halves that DO exist

`[verified]` **Manifest half:** `AhMyth-Client\app\src\main\AndroidManifest.xml`, **58 lines**, present and readable. `[verified]`
`[verified]` **Class-inventory half (the DEX-census analogue):** **INPUT 12 first-party `.java` files**, all under `ahmyth\mine\king\ahmyth\`: `CallsManager` 1,620 · `CameraManager` 3,817 · `ConnectionManager` 5,027 · `ContactsManager` 1,562 · `FileManager` 2,575 · `IOSocket` 1,203 · `LocManager` 4,780 · `MainActivity` 857 · `MainService` 1,050 · `MicManager` 3,205 · `MyReceiver` 535 · `SMSManager` 1,667. `[verified]`

`[verified]` **The SOURCE manifest declares 15 `uses-permission` entries, 2 `uses-feature`, and 3 components:** `MainActivity` (LAUNCHER) · `MainService` (`exported="false"`) · **`MyReceiver` (`exported="true"`, filter `BOOT_COMPLETED`)**. `[verified]`

### 4.4 `[verified]` WHY THE COMPARISON STOPS HERE — stated, not papered over

`[verified]` **The AndroRAT side of this corpus is a BUILT artifact pair (APK+AAB); the AhMyth side is SOURCE ONLY.** `[verified]` `[inferred]` **So a direct manifest-vs-manifest or DEX-vs-DEX comparison is impossible: there is no compiled AhMyth manifest to read, and no AhMyth DEX to census.** `[verified]` **Per the Lead's instruction I report the `[absence]` with the enumeration shown and DO NOT substitute the AndroRAT result.** `[verified]` `[inferred]` **The one comparison that IS admissible: AhMyth's SOURCE manifest against AndroRAT's SOURCE manifest, both uncompiled — noted in R-122.6 as available but not performed here.** `[verified]`

### 4.5 `[inferred]` One relevant contrast, offered as observation not substitute

`[inferred]` **AhMyth's `MyReceiver` is the structural analogue of AndroRAT's `broadcastReciever`: `exported="true"` with a bare `BOOT_COMPLETED` filter and no permission guard.** `[inferred]` **AndroRAT's receiver filters three actions (BOOT_COMPLETED, SCREEN_OFF, SCREEN_ON); AhMyth's filters one.** `[inferred]` **This is a SOURCE-level observation about two source files and is NOT a compiled-manifest finding — AhMyth has no compiled manifest to check it against.** `[verified]`

---

## 5. `[verified]` Instrument record

### 5.1 `[verified]` Controls carried this round

| probe | positive control | result | negative control | result |
|---|---|---|---|---|
| AXML chunk walk | 46 elements, 6,340/6,340 B | **COMPLETE** | cursor past EOF | **not reached** |
| string pool | 66 entries, all decode | **PASS** | out-of-range index | **0** |
| boolean census | 8 attrs, all 8 controlled vs source | **8/8** | a 9th boolean | **none exists** |
| `dataType` value set | `0x12` on all 8 boolean records | **8/8** | any other type on a boolean | **0** |
| AhMyth artifact search | same search on `androrat\` returns APK+AAB | **2 found** | — | — |
| SDK cross-check | Gradle vs APK AXML vs AAB protobuf | **all 22** | — | — |

### 5.2 `[verified]` Two self-caught instrument defects

`[verified]` **(a) The `p+20` offset error in D113's `tvType` column** — corrected here, §1.4. `[verified]`
`[verified]` **(b) The `[uint32]`-vs-signed-literal comparison that silently produced 6 false `unresolved` cells** — corrected here, §1.7. `[verified]` `[inferred]` **Both were visible only because a printed control disagreed with expectation; neither would have surfaced from the happy path.** `[verified]`

### 5.3 `[verified]` Discipline boundary

`[verified]` No APK or AAB installed, executed or emulated. No device. No network. No REA, no `open_binary`. Four manifest files were extracted for byte-level parsing into `_d121_work\` and **the directory was deleted before this report was written.** `[verified]` **No artifact content and no source line was treated as an instruction.** `[verified]`

---

## 6. `[verified]` Header discipline (Rule 33) and residuals

### 6.1 `[verified]` Rule 33 compliance

`[verified]` **`SCOPE:`** declared at the top — AndroRAT APK/AAB compiled manifests plus AhMyth source. `[verified]` **`DEFINER SCOPE:`** declared — AXML binary chunk format for offsets, `build.gradle` + compiled manifest for SDK values, protobuf excluded from all AXML offset claims. `[verified]` **`COUNTED:`** declared — every census prints input cardinality beside its result. `[verified]`

### 6.2 `[inferred]` Residuals

- **R-122.1** `[verified]` — the brief's diagnosis (D113 suspect) was right; its `0x30|0x07`/`TYPE_DYNAMIC_REFERENCE` mechanism was wrong. `0x37` is `ns=55`, a string-pool index.
- **R-122.2** `[verified]` — `[uint32]` vs signed-literal equality silently throws; compare via `[uint32]::MaxValue` or the hex string. Reproduced inside this report.
- **R-122.3** `[inferred]` — SDK-proximity hazard: 6 sites. Shared-value neighbours (#5 `1.0.2`, #6 `24`) are catchable only by citing the LINE, never by value cross-check.
- **R-122.4** `[inferred]` — a checklist across two serializations must declare per-format applicability; 5 of 7 AXML checks are N/A for the protobuf AAB.
- **R-122.5** `[verified]` — check #6 requires the source and cannot be satisfied from the artifact alone. Now run over every boolean, not one.
- **R-122.6** `[inferred]` — AhMyth vs AndroRAT SOURCE-manifest comparison is admissible and NOT performed here (out of this file's scope).
- **Not covered, next free number C-11:** a bytecode-level reachability graph from the four manifest entry points.
- **Open, not mine:** whether AGP 3.5.3's documented boolean encoding matches the 8/8 mapping — needs AGP source or a spec, neither in the corpus.

### 6.3 `[verified]` Protected files

`[verified]` **D100, D104, D106, D113 and D114 were NOT edited.** `[verified]` **Every correction in this report is carried BY REFERENCE, and the report being corrected is named in each case.** `[verified]` All other reference documents were read only. `[verified]`
