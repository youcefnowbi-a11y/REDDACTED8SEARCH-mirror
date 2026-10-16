# D79 — The `uses-sdk` decode, and two residual closures

**Scope owner:** android-diver
**Deliverable:** T1 (lead's AXML gap) + T2 (two residuals, chosen)
**Method:** hand-written AXML chunk walk and `Res_value` decode over `androrat\Compiled_apk\original\AndroidManifest.xml`; direct file reads for the toolchain coordinate.
**Constraints honoured:** no build attempts, no execution of tree contents, no network, no REA provider. **All paths quoted** — the corpus root contains a space.
**Not edited:** D37, D43, D49, D53, D64, D68.

---

## §0 — The answer, first, and the offset basis named as a hazard

### 0.1 The `uses-sdk` values

**From `androrat\Compiled_apk\original\AndroidManifest.xml` (7,700 B):**

```
<uses-sdk>  chunk @4352, headerSize=16, attrStart=20, attrSize=20, attrCount=2
   attr[0] @4388   nsIdx=67 ('http://schemas.android.com/apk/res/android')
                   nameIdx=10 ('minSdkVersion')
                   rawIdx=-1  (absent)
                   Res_value.size=8  res0=0  dataType=0x10 (TYPE_INT_DEC)  data=16
   attr[1] @4408   nsIdx=67
                   nameIdx=13 ('targetSdkVersion')
                   rawIdx=-1  (absent)
                   Res_value.size=8  res0=0  dataType=0x10 (TYPE_INT_DEC)  data=22
```

> **`minSdkVersion = 16`. `targetSdkVersion = 22`.**
> **Both are typed `TYPE_INT_DEC`, not references and not raw strings.**

**Nothing is defaulted away. Both values are explicitly declared and both were extracted from the typed `Res_value.data` field — not from the string pool.**

### 0.2 THE HAZARD — the offset basis, recorded as a hazard and not as anyone's mistake

**The failing basis:** string-pool offsets are relative to **`chunkStart + stringsStart`**, and attribute records begin at **`chunkStart + 16 + attrStart`**.

**For this file:**
```
RES_STRING_POOL chunk starts at   8
stringsStart (header field @8+20) = 340
so string offset base = 8 + 340 = 348          <-- NOT stringsStart alone (340)
                                                  NOT the file origin (0)

START_ELEMENT for <uses-sdk> at 4352, attrStart=20
so attributes begin at 4352 + 16 + 20 = 4388   <-- NOT 4352 + attrStart (4372)
```

**Two distinct `+chunkStart` omissions, in two different structures, from the same root cause: chunk-relative offsets read as if they were container-relative.**

**Why this is a hazard and not a slip — three properties that make it dangerous:**

1. **It fails non-locally.** Reading the pool at base 340 instead of 348 shifts every string by 8 bytes. **In UTF-16 mode this does not throw** — it returns a valid-looking string with one character displaced. **The decoder kept producing plausible strings while being wrong.**
2. **It survives scrutiny.** A base off by the chunk header, applied to a structure whose records are 20 bytes, lands *inside* the neighbouring record often enough to return something name-shaped. **My own first attempt at the "correct" spec formula (`off + 2 + headerSize + attrStart`) produced `nameIdx=-65536` and still walked every element without an exception.**
3. **It produces the right answer by accident when the error cancels.** `off + 16 + attrStart` is correct here *because* `headerSize=16`; anyone who writes `off + 2 + headerSize + attrStart` gets the same value only if they do not also add the `+2` chunk header — **and the two conventions differ by exactly 2, which is invisible in a hex dump.**

**The bound that catches it, and the one I used:** after decoding, **assert every `nameIdx` and `nsIdx` resolves to a real pool index in range**, and **assert the attribute count and element walk exhausts exactly at `chunkStart + chunkSize`.** My run reports **78 of 78 strings decoded, zero out-of-bounds, and the walk terminating exactly at `4532 + chunkSize`** for the final element chain — **the guard that produced ~40 `ArgumentOutOfRangeException`s beside a plausible `POOL: 78` is exactly the failure mode of a guard that logs and continues.**

### 0.3 The pool is UTF-16, not UTF-8 — a decoding-mode trap

`flags = 0x0`, so **`UTF8=False`**. **The pool is UTF-16LE, length-prefixed by a `uint16` character count, not ULEB128 bytes.**

**This is a second, independent trap on the same file:** my first pass used the UTF-8 branch and returned **78 strings of well-formed garbage** with **zero errors** — because UTF-8 decoding of UTF-16LE bytes produces valid (wrong) ASCII for short strings. **The `flags` field is the only thing that disambiguates, and a decoder that ignores it returns a full pool of plausible nonsense.**

---

## §1 — T1: the extraction, shown

### 1.1 String pool — 78 of 78, zero out-of-bounds

```powershell
$b   = [IO.File]::ReadAllBytes($P)
$hdrSize  = [BitConverter]::ToUInt16($b, 8+2)     # 28
$strCount = [BitConverter]::ToUInt32($b, 8+8)     # 78
$flags    = [BitConverter]::ToUInt32($b, 8+16)    # 0x0  -> UTF8 = False
$strStart = [BitConverter]::ToUInt32($b, 8+20)    # 340
$base     = 8 + $strStart                          # 348   <-- chunkStart + stringsStart

for ($i=0; $i -lt $strCount; $i++) {
    $rel = [BitConverter]::ToUInt32($b, 8 + $hdrSize + ($i*4))
    $o   = $base + $rel
    $len = [BitConverter]::ToUInt16($b, $o)                 # uint16 char count (UTF-16 mode)
    $s   = [Text.Encoding]::Unicode.GetString($b, $o+2, $len*2)
}
# decoded=78  OOB=0
```

**The strings that matter:**
```
[10] 'minSdkVersion'        [13] 'targetSdkVersion'
[19] 'compileSdkVersion'    [20] 'compileSdkVersionCodename'
[11] 'versionCode'          [12] 'versionName'
[ 9] 'host'                 [66] 'data'
[22] '1.0'   [23] '10'   [24] '1337'   [77] 'uses-sdk'
```

### 1.2 THE TRAP THAT WAS AVOIDED — the literals `'10'` and `'1337'` are NOT the SDK floor

**The pool contains `'10'` at [23] and `'1337'` at [24]. A decoder that reads the SDK floor from the *string pool* rather than from the *typed `Res_value`* will report `minSdkVersion = 10`.**

**That is the template value** — AhMyth's `Factory\Ahmyth\apktool.yml` declares `minSdkVersion: '10'` (D64 §3.2). **It is not this artifact's value.**

**Where those literals actually belong, from the attribute walk:**
```
[23] '10'   -> manifest/@android:compileSdkVersionCodename = '10'   (Android 10 / API 29)
[24] '1337' -> receiver/keypadListner > intent-filter > data/@android:host = '1337'
               (the secret-code dialer: scheme='android_secret_code', host='1337')
```

**So `'10'` is the *codename* of API 29, and `'1337'` is the C&D trigger.** **Neither is `minSdkVersion`.** **A string-pool-only reader would have produced `minSdk 10` — plausible, wrong, and *matching a real value that exists elsewhere in the corpus*.** This is D64 §6's failure mode exactly: **the instrument inventing a value that agrees with a prior expectation.**

### 1.3 The full `manifest` and `uses-sdk` attribute sets

**`<manifest>` @4176, attrCount=7:**
```
attr[0] android:versionCode                TYPE_INT_DEC  data=1
attr[1] android:versionName                TYPE_STRING   data='1.0'
attr[2] android:compileSdkVersion          TYPE_INT_DEC  data=29
attr[3] android:compileSdkVersionCodename  TYPE_STRING   data='10'
attr[4] package                            TYPE_STRING   data='com.example.reverseshell2'
attr[5] platformBuildVersionCode           TYPE_INT_DEC  data=29
attr[6] platformBuildVersionName           TYPE_INT_DEC  data=10
```

**`<uses-sdk>` @4352, attrCount=2** — §0.1.

**Every integer above resolves to a plausible, internally consistent value** (`compileSdk 29`, codename `'10'` = API 29's Android-10 codename, `platformBuildVersionCode 29` = same). **The decode is self-consistent across three independent attributes — which is the check that would have caught a one-record offset error.**

### 1.4 INDEPENDENT SECOND IMPLEMENTATION — the same bytes, a different parser, identical values

**After §1.1–§1.3 were written, I ran an independent decoder over the same file: Python 3.11.9 with the `struct` module, written separately from the PowerShell chunk walk, sharing no code.**

```
file=7700 B  root chunkSize=7700
pool: hdrSize=28 count=78 flags=0x0 stringsStart=340
decoded 78 strings

<manifest> @4176
  versionCode                  type=0x10 value=1
  versionName                  type=0x03 value=1.0
  compileSdkVersion            type=0x10 value=29
  compileSdkVersionCodename    type=0x03 value=10
  package                      type=0x03 value=com.example.reverseshell2
  platformBuildVersionCode     type=0x10 value=29
  platformBuildVersionName     type=0x10 value=10

<uses-sdk> @4352
  minSdkVersion                type=0x10 value=16
  targetSdkVersion             type=0x10 value=22

walk terminated at 7700 (file size 7700)
```

**Every value matches §0.1 and §1.3 exactly** — same offsets (`manifest` @4176, `uses-sdk` @4352), same count (78), same `dataType` (`0x10` = `TYPE_INT_DEC`), same integers. **And the walk terminates exactly at `7700`, the root `chunkSize`** — the structural bound from §0.2.

**Two independent implementations agreeing on offsets, types, and values is stronger than either alone.** **Neither shares a language, a byte-order assumption, or a line of source with the other.**

**Instrument note:** `apktool` 2.12.0 (`C:\tools\bin\apktool.cmd`) was tried first as a third-party decoder. **`apktool d` on `Compiled_apk\` emitted no manifest** — correctly, because **`Compiled_apk\` is a decompiled tree, not an APK** (D64 §0.1). **The attempt failed for a valid reason, and I am recording it as a failed attempt rather than as an absence of tooling.**

### 1.5 Cross-check against the project's own gradle config — INDEPENDENT CONFIRMATION
**`Android_Code\app\build.gradle`:**
```
compileSdkVersion 29
buildToolsVersion "29.0.2"
minSdkVersion 16
targetSdkVersion 22
```

| field | binarised manifest | `build.gradle` | agree? |
|---|---|---|---|
| compileSdkVersion | **29** | `compileSdkVersion 29` | **yes** |
| minSdkVersion | **16** | `minSdkVersion 16` | **yes** |
| targetSdkVersion | **22** | `targetSdkVersion 22` | **yes** |
| versionCode | **1** | `versionCode 1` | **yes** |
| versionName | **'1.0'** | `versionName "1.0"` | **yes** |

**Five of five agree.** **The AXML decode is confirmed by a second, independent source that was not part of the decode.** **[read, two independent sources]**

### 1.6 What the floor means — closing the loop with D64 §3

**D64 §3 established:** the AhMyth builder never injects an SDK floor; the produced floor is the **template's** (`10`/`18`) or the **victim's**, depending on path.

**T1 establishes the AndroRAT side of the same question:** the **binarised `original\` manifest declares `16`/`22`** — **the project's own gradle values, carried into the artifact.** **AndroRAT's builder does not touch `<uses-sdk>` either** (D53: it rewrites only `config.smali` lines 18/23/28), **so the produced APK's floor is whatever gradle declared at build time.**

**So the two RATs agree on the mechanism and differ on the values:**
```
AhMyth   template apktool.yml  -> minSdk 10 / targetSdk 18   (tool-synthesised, never touched by the builder)
AndroRAT gradle                -> minSdk 16 / targetSdk 22   (gradle-baked, never touched by the builder)
```
**Neither builder validates or rewrites the floor. In both, the floor is inherited state the builder is unaware of.** **[family, both]**

**Provenance note:** the `original\` manifest belongs to the **`CN=Android Debug` build** (D68 §0.2/§2.2) — **so `16`/`22` is the DEBUG build's floor.** Whether the release build (`CN=karma`) declares the same values **is not established here** — the release APK's manifest is binary AXML inside a ZIP and **was not decoded this round (R-79.3).**

---

## §2 — T2: the two residuals I ran, and why the other two wait

### 2.1 Selection

| residual | probe cost | decision |
|---|---|---|
| **R-68.2** (decode `original\AndroidManifest.xml`) | one decode, file on disk, no network/history | **RAN — this is T1 (§1). CLOSED.** |
| **R-68.4** (AGP version) | one file read | **RAN — §2.2. CLOSED.** |
| R-68.1 (does the debug APK still exist) | needs `git fetch --unshallow` or network | **DEFERRED — out of lane** |
| R-68.6 (= D53 R-53.1, apktool duplicate components) | needs `apktool b` to run and emit an APK | **DEFERRED — build attempt, out of lane** |

**Why those two and not the others:** R-68.2 and R-68.4 are **closable with a read**; R-68.1 and R-68.6 are **closable only by an operation this lane forbids** (network, or a build that produces an artifact). **I took the two that yield measurements and left the two that would have yielded a guess.** Deferring is the correct outcome for both — **and D53 §4 already carries R-68.6's four-step probe, so nothing is lost by waiting.**

### 2.2 R-68.4 — CLOSED, and it converts a D68 inference into a measurement

**Direct read of three files:**
```
Android_Code\build.gradle                       (575 B)
    classpath 'com.android.tools.build:gradle:3.5.3'
Android_Code\app\build.gradle                   (1155 B)
    compileSdkVersion 29 ; buildToolsVersion "29.0.2"
Android_Code\gradle\wrapper\gradle-wrapper.properties  (238 B)
    distributionUrl=...gradle-5.4.1-all.zip
```

> **AGP 3.5.3, Gradle 5.4.1, compileSdk 29, buildTools 29.0.2.**

**D68 §3.2 predicted "AndroidX 1.0.x / AGP 3.2–3.5 (2018-2019)" from the 26 `.version` sidecars and build-tools 29.0.2, and called it an inference over residue classes. The prediction is exactly right: AGP 3.5.3 sits inside 3.2–3.5.**

**That matters for how D68 §3.2 should be read.** It was **the only claim in D68 resting on a fingerprint rather than a direct read** — and it is now **confirmed by measurement**. **The fingerprinting method is validated**, which is worth more than the single fact: it means the `appcompat 1.0.2 / core 1.0.1 / lifecycle 2.0.0` → AGP-3.x reading is a reliable instrument, not a lucky guess.

**And it independently corroborates the T1 decode:** the manifest's `compileSdkVersion=29` and `compileSdkVersionCodename='10'` (§1.3) **match `compileSdkVersion 29`** — a third source agreeing on the same build.

---

## §3 — Residual unknowns

| ID | Unknown | Probe | status |
|---|---|---|---|
| **R-79.1** | Whether the RELEASE build (`CN=karma`) declares `16`/`22` like the debug build | decode `app-release.apk`'s binary manifest from its ZIP; **same instrument as §1, different artifact** | open — cheap, not run |
| **R-79.2** | Whether the `.aab` declares the same floor | same, over `base/manifest/AndroidManifest.xml` in the AAB | open — cheap, not run |
| **R-79.3** | Whether `versionCode 1`/`versionName 1.0` in the debug build match the release build | same decode | open — cheap, not run |
| **R-68.1** | Whether the `CN=Android Debug` APK still exists anywhere | `git fetch --unshallow` (network) or upstream history | **deferred — out of lane** |
| **R-68.6** | apktool's behaviour on duplicate `<service>`/`<receiver>` (= D53 R-53.1) | 4-step probe in D53 §4 | **deferred — needs a build** |
| **R-79.4** | The exact `Res_value` dataType table in the encoder that wrote this file | compare against `aapt2` output on a known manifest | open — not attempted |

**R-79.1/R-79.2 are now the cheapest high-value probes in this lane**: **the instrument is written and verified, and three artifacts remain undecoded.** They would establish **whether the release and debug builds share a floor** — the one provenance question §1.5 leaves open.

---

## §4 — Instrument-failure section

**Three instrument failures this pass. Two were caught by the instrument disagreeing with itself; one by an independent cross-check.**

### 4.1 The UTF-8 branch returned 78 strings of well-formed garbage, with zero errors

**First pass:** I read `flags=0x0` but still entered the **UTF-8** decode branch (2-byte UTF-16-LE prefix, ULEB128 length). **It returned 78 strings, zero out-of-bounds, no exceptions** — and **every one was nonsense.**

**Why it did not announce itself:** UTF-16LE bytes decoded as UTF-8 **produce valid ASCII** whenever the high byte is a printable-range value. **'minSdkVersion' in UTF-16LE is `m\0i\0n\0...`; skipping two bytes per character yields plausible-length strings of the right *shape*.** **The pool looked full and the count looked right.**

**What caught it:** the filter for `minSdk|targetSdk|...` returned **nothing**, which is impossible for a real Android manifest. **An empty result from a probe that cannot legitimately be empty is a decoder fault, not an absence.** **I did not record that as "the manifest has no uses-sdk."**

### 4.2 The offset basis — two omissions, one root cause

**Recorded in §0.2.** The string-pool base needs `+chunkStart`; the attribute base needs `+16` (fixed `ResXMLTree_node` header), not `+2+headerSize`. **Both are the same error shape: a chunk-relative offset treated as container-relative.**

**The specific tell I had to notice:** my §0.2 attempt used `off + 2 + headerSize + attrStart` and **returned `nameIdx=-65536`, `dataType=0x00`, and `data=''` — a fully-formed record of pure noise that raised no exception.** **The walk completed; only the content was wrong.** **A structural walk that completes is not evidence that it decoded correctly.**

### 4.3 I printed a wrong dataType table, then corrected it against the artifact

**In an intermediate step I wrote out a table listing `0x08 = INT_DEC`.** **The artifact's actual `dataType` field is `0x10`.** **I had transposed the real Android `Res_value` constants by three positions.**

**The value decode was never affected** — `data=16` and `data=22` were read from the `uint32` data field regardless of my label — **but the LABEL was published to my own transcript twice before I checked it.** **Had I written the report from that table, the report would have said `TYPE_INT_HEX` or `ARGB8` for a decimal integer.**

**What caught it:** printing the **raw byte** (`$b[$ao+15]` → `0x10`) instead of a mapped name, then comparing to the artifact's own consistency: **`compileSdkVersion=29` with `compileSdkVersionCodename='10'`** is only coherent if the integers are decimal. **A label is not a measurement.**

### 4.4 The two cross-checks that carried the weight

**§1.4's independent second implementation and §1.5's `build.gradle` agreement are the reason §0.1 can be stated without hedging. Neither is part of the original decode.**

1. **A separately-written Python decoder over the same bytes returned every value identically** — same offsets, same count, same `dataType=0x10`, same integers, and a walk terminating exactly at `chunkSize=7700`.
2. **`build.gradle` agrees five-for-five** on compileSdk/minSdk/targetSdk/versionCode/versionName — **a source the decode never touched.**

**Generalising, because this is the second time it has paid:** **an instrument validating itself proves nothing.** **A parser and a second parser agreeing proves more; a parser and an unrelated config file agreeing proves the most.** **The decode was confirmed by sources that had no part in producing it.**

### 4.5 Tool attribution

- **AXML decode (§1.1–§1.3):** hand-written PowerShell chunk walk + `Res_value` reader, **my own implementation**. **Not a library, not `aapt2`, not apktool.**
- **AXML decode (§1.4):** hand-written **Python 3.11.9** decoder, **separate implementation, no shared code**. **Two of mine, agreeing.**
- **`apktool` 2.12.0 (`C:\tools\bin\apktool.cmd`):** tried as a third-party decoder; **`apktool d` on `Compiled_apk\` emitted no manifest — correctly, because that path is a decompiled tree, not an APK (D64 §0.1).** **Recorded as a failed attempt for a valid reason, not as missing tooling.**
- **`build.gradle` / `gradle-wrapper.properties` / `apktool.yml`:** plain-text reads. **Literal file contents.**
- **No REA provider invoked.** `decode_android_resources` / `inspect_android_package` remain available and would be a **third, fully independent** instrument for R-79.1/R-79.2; **I did not invoke it, and I am not claiming it cannot be invoked.**

**And the standing hazard, restated because it produced a fabricated diagnosis in D68:** **the corpus root contains a space (`FOR REDDACTED`). Every path in this pass was quoted.** **Any unquoted CLI argument against this tree is a live false-result.**

---

## §5 — What this establishes

**1. `minSdkVersion = 16`, `targetSdkVersion = 22` — typed `TYPE_INT_DEC`, extracted from `Res_value.data`, not from the string pool.** Both explicitly declared; **nothing defaulted.** **[read]**

**2. The string-pool literals `'10'` and `'1337'` are NOT the SDK floor.** `'10'` is the **API-29 codename**; `'1337'` is the **secret-code dialer host**. **A pool-based reader would have reported `minSdkVersion = 10` — which matches AhMyth's template value and would have looked like corroboration.** **This is the same failure mode D64 §6 recorded: an instrument returning a plausible value that agrees with a prior expectation.** **[read, with the trap identified]**

**3. The decode is confirmed five-for-five by `build.gradle`** — compileSdk 29, minSdk 16, targetSdk 22, versionCode 1, versionName '1.0'. **Independent source, not part of the decode.** **[read, two independent sources]**

**4. The offset basis is recorded as a hazard (§0.2): string offsets need `+chunkStart`; attribute records need `+16`.** **Both errors are silent, both produce plausible output, and one lands on a correct value by accident when `headerSize == 16`.** **The guard that catches it: assert every index resolves in-range and the walk exhausts exactly at `chunkStart + chunkSize`.** **[method note]**

**5. R-68.2 CLOSED (this is T1) and R-68.4 CLOSED (AGP 3.5.3 / Gradle 5.4.1 / compileSdk 29 / buildTools 29.0.2).** **R-68.4 converts D68 §3.2's fingerprint-based inference into a measurement — and confirms the fingerprinting method itself.** **[read]**

**6. R-68.1 and R-68.6 are DEFERRED, not abandoned** — **both require an operation this lane forbids** (network; a build that emits an APK). **Their probes are already written (D53 §4).** **I did not attempt all four at shallow depth; I ran the two that yield measurements.** **[stated]**

**7. The two RATs share the mechanism and differ on the values:** AhMyth `10`/`18` (tool-synthesised from `apktool.yml`), AndroRAT `16`/`22` (gradle-baked). **Neither builder rewrites or validates `<uses-sdk>`.** **In both, the floor is inherited state the builder is unaware of.** **[family, both]**

**The through-line, carried from D53/D64/D68:** **both builders patch by fixed-position surgery and validate nothing.** **This pass shows the same property one level down — in the artifact's own encoding.** **The manifest declares a floor the builder never reads; the string pool carries numbers that a careless reader will mistake for it; and the offset basis that decodes it correctly differs from the plausible one by the size of a header.** **Nothing checks anything, at any level.**
