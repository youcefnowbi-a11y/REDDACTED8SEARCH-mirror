# D100 — The Android binary layer: compiled manifest vs. source, DEX census, signing, and an empty `lib/`

**Author:** `covenant-diver` · **Round:** 24 · **Report:** D100 · **Class:** static binary extraction only
**Target:** `01_SOURCE_mobile\androrat\Android_Code\app\release\app-release.apk` — **2,129,794 B**, SHA-256 `98037b11a118839bef93924a5718c9e988f1c11df507909cdf6bc0cb97189830`
**Write scope:** this file + `_d100_*` work files. **D1-D88 protected** (D87 included) — corrections to D87 appear here, naming it.
**Method baseline:** `C-00` (binary-layer capabiity) and `C-08` (seven recorded toolchain failures). **None of the seven were repeated**; the relevant one is applied in §6.
**Line-count convention:** **LF-byte count.** A file with a trailing newline has `LF_bytes` lines under `split("\n")`.
**Coordinate discipline:** every line number is `file:line`, never bare.
**Count control:** every count below produced by **two independent methods**, both printed (§6.4).

---

## TOC

- **§0 — Scope, the D87 relationship, and one premise that did not hold**
- **§1 — T1: the compiled manifest vs. the source manifest** — **the component and permission diffs are measured in §1.3-§1.4; the SECRET_CODE receiver is among the compiled-away components**
- **§2 — T2: the DEX census** — 2,472 classes; **3 source classes absent from the APK**
- **§3 — T3: the signing state** — v1-only, `CN=karma`, self-signed
- **§4 — T4: native libraries** — **zero; an `[absence]` with its bound**
- **§5 — The Kotlin question** — 282 Kotlin entries over zero Kotlin source
- **§6 — Instrument record** · **§7 — Verification and residuals**

---

## 0. Scope, the D87 relationship, and one premise that did not hold

### 0.1 `[read]` What D87 already established — cited, not re-claimed

`[read]` D87 §1.2 decoded the release APK's binary AXML and recovered the `<manifest>` attributes and `<uses-sdk>`: `minSdkVersion=16`, `targetSdkVersion=22`, `compileSdkVersion=29`, `package=com.example.reverseshell2`. `[verified]` **I independently reproduce every one of those values via a different decoder (§1.1).** `[verified]` **D87 did NOT enumerate `<uses-permission>`, the `<activity>`/`<service>`/`<receiver>` set, `android:exported`, or any `<intent-filter>`** — that is the gap this report fills, and it is where the findings are. `[verified]`

### 0.2 `[verified]` A premise in the brief that did NOT hold — the AhMyth APK does not exist

`[verified]` The brief states the AhMyth APK "was under the AhMyth server tree." `[verified]` **It is not there.** `[verified]` Enumerated by extension across the whole `ahmyth` tree for `.apk` `.jar` `.dex` `.so` `.zip` `.aab` — **the complete result is eight entries, and none is an AhMyth payload**:

| bytes | path (relative to `RE_Library`) | what it is |
|---:|---|---|
| 16,314,178 | `\01_SOURCE_mobile\ahmyth\AhMyth-Server\app\app\Factory\apktool.jar` | **a tool** (WASM/JVM lane — not touched) |
| 53,636 | `\01_SOURCE_mobile\ahmyth\AhMyth-Client\gradle\wrapper\gradle-wrapper.jar` | Gradle wrapper |
| 26,106 | `\01_SOURCE_mobile\ahmyth\AhMyth-Server\app\app\Factory\sign.jar` | **a signing tool** |
| 1,636 ×3, 489 | `...\node_modules\unzip\testData\*.zip` | npm test fixtures |

`[verified]` **`AhMyth-Client` is a SOURCE tree (Gradle + Java/Kotlin), and no build output is present.** `[verified]` **There is no AhMyth APK in this corpus to inspect.** `[verified]` `[absence]` with its positive control: the same enumeration **does** return both `apktool.jar` copies and the `sign.jar`, so the detector finds `.jar` files — the absence of an `.apk` is a real absence, not a broken probe. `[verified]` **Recorded as R-100.1.**

### 0.3 `[verified]` A second artifact exists that the brief did not name

`[verified]` `01_SOURCE_mobile\androrat\Android_Code\app\release\app-release.aab` — **2,366,154 B**, present in the tree. `[read]` D87 §1.3 already decoded its **protobuf** manifest and found the same floor. `[verified]` **I name it so the APK is not treated as the only release artifact; I do not re-decode it.** `[verified]`

---

## 1. T1: the compiled manifest vs. the source manifest

### 1.1 `[verified]` The decoded manifest, via `decode_android_resources` (Apktool 2.12.0)

`[verified]` Decoded from the APK itself, SHA-256 verified against the file on disk:

```
package          com.example.reverseshell2
versionName      1.0        versionCode      1
minSdkVersion    16         targetSdkVersion 22
compileSdkVersion 29        compileSdkVersionCodename 10
decoded files    861        coverage: complete
```

`[verified]` **The package identity, version, and both SDK levels agree with D87 §1.2 exactly — reached through a different decoder, which is the independent confirmation.** `[verified]`

### 1.2 `[verified]` THE COMPILED MANIFEST, printed in full

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
          android:compileSdkVersion="29" android:compileSdkVersionCodename="10"
          package="com.example.reverseshell2"
          platformBuildVersionCode="29" platformBuildVersionName="10">
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE"/>
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
    <uses-permission android:name="android.permission.WAKE_LOCK"/>
    <uses-permission android:name="android.permission.CAMERA"/>
    <uses-feature android:name="android.hardware.camera"/>
    <uses-feature android:name="android.hardware.camera.autofocus"/>
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.VIBRATE"/>
    <uses-permission android:name="android.permission.READ_SMS"/>
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
    <uses-permission android:name="android.permission.READ_CALL_LOG"/>
    <uses-permission android:name="android.permission.RECORD_AUDIO"/>
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW"/>
    <uses-permission android:name="android.permission.READ_PHONE_STATE"/>
    <application android:allowBackup="true"
                 android:appComponentFactory="androidx.core.app.CoreComponentFactory"
                 android:hardwareAccelerated="false" android:icon="@mipmap/ic_launcher"
                 android:label="@string/app_name" android:largeHeap="true"
                 android:roundIcon="@mipmap/ic_launcher_round"
                 android:supportsRtl="true" android:theme="@style/AppTheme">
        <activity android:name="com.example.reverseshell2.MainActivity">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
        <service android:enabled="true" android:exported="false"
                 android:name="com.example.reverseshell2.mainService"/>
        <receiver android:enabled="true" android:exported="true"
                  android:name="com.example.reverseshell2.broadcastReciever">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
                <action android:name="android.intent.action.SCREEN_OFF"/>
                <action android:name="android.intent.action.SCREEN_ON"/>
            </intent-filter>
        </receiver>
        <service android:name="com.example.reverseshell2.jobScheduler"
                 android:permission="android.permission.BIND_JOB_SERVICE"/>
    </application>
</manifest>
```

### 1.3 `[verified]` The PERMISSION diff — one permission is compiled away

`[verified]` **SOURCE declares 16 permissions (`AndroidManifest.xml:6-28`). COMPILED declares 15.** `[verified]` Set-diff, both directions computed:

| direction | result |
|---|---|
| **in source, absent from compiled** | **`android.permission.ACCESS_NETWORK_STATE`** — one |
| **in compiled, absent from source** | **∅ — none** |

`[verified]` **`ACCESS_NETWORK_STATE` is declared at `AndroidManifest.xml:6` and is NOT in the compiled APK.** `[verified]` `[inferred]` **The mechanism is almost certainly Manifest-merger removal for an unused permission** — a normal optimization, not a defect. `[verified]` **But it is a genuine source/compiled divergence and it is reported as measured, not explained away.** `[verified]` **Recorded as R-100.2.** `[verified]`

### 1.4 `[verified]` THE COMPONENT DIFF — four declared components are compiled away

`[verified]` **SOURCE declares 8 components (`AndroidManifest.xml:39-77`). COMPILED registers 4.** `[verified]`

| direction | components |
|---|---|
| **in source, absent from compiled (4)** | **`activity:controlPanel`** (`:39`) · **`receiver:keypadListner`** (`:65`) · **`service:Payloads.videoRecorder`** (`:76`) · **`service:Payloads.audioManager`** (`:77`) |
| **in compiled, absent from source** | **∅ — none** |

`[verified]` **The `keypadListner` loss is the significant one: it carries the `SECRET_CODE` intent-filter —**
```xml
<receiver android:name=".keypadListner">                                   <!-- AndroidManifest.xml:65 -->
    <intent-filter>
        <action android:name="android.provider.Telephony.SECRET_CODE"/>     <!-- :66 -->
        <data android:scheme="android_secret_code" android:host="1337"/>   <!-- :67 -->
    </intent-filter>
</receiver>
```
`[verified]` **String presence measured both ways: the SOURCE contains `SECRET_CODE` and `android_secret_code`; the COMPILED manifest contains NEITHER.** `[verified]` **A `*#*#1337#*#*` dial-code re-entry channel is declared in source and absent from the shipped release APK.** `[verified]` **Recorded as R-100.3.** `[verified]`

### 1.5 `[verified]` The two absences are DIFFERENT KINDS — §2 decides which

`[inferred]` `controlPanel`/`keypadListner` could be (a) unregistered but still compiled in, or (b) not in the build at all. `[verified]` **§2's DEX census resolves this and the answer splits: `Payloads/videoRecorder` and `Payloads/audioManager` ARE in the DEX (present, merely unregistered); `controlPanel`, `keypadListner`, and `jumper` are NOT in the DEX at all (absent from the build).** `[verified]` **So the finding is not one phenomenon — it is two, and they have different explanations.** `[verified]` **Recorded as R-100.4.** `[verified]`

---

## 2. T2: the DEX census

### 2.1 `[verified]` Header, parsed from bytes and shown coherent

`[verified]` `classes.dex`, **3,604,660 B**, SHA-256 `4d48430d244dd6bebbfa7bba9bd25b41b60006d510f8316cfa87593df406931c`, magic `64 65 78 0a 30 33 35 00` = **`dex\n035`**. `[verified]`

| field | value |
|---|---:|
| `file_size` (header, offset 32) | **3,604,660** — **equals the actual byte length** |
| `header_size` | 112 |
| `endian_tag` | `0x12345678` (little-endian, standard) |
| `string_ids_size` | **26,908** |
| `type_ids_size` | **3,403** |
| `proto_ids_size` | 6,109 |
| `field_ids_size` | 12,964 |
| `method_ids_size` | **26,535** |
| `class_defs_size` | **2,472** |

`[verified]` **The `file_size` field matching the true length is the guard that the extraction is complete and un-truncated — an AXML-style refusal check, applied to the DEX.** `[verified]`

### 2.2 `[verified]` The class census and the compiled-in addition

`[verified]` **2,472 unique class descriptors. 55 are first-party (`com/example/reverseshell2`).** `[verified]` Diff against the **19** `.java` files in the source tree — **corrected after an off-by-one in my own first pass (§6.1):**

| direction | classes |
|---|---|
| **in source, ABSENT from DEX (3)** | **`controlPanel`** · **`jumper`** · **`keypadListner`** |
| **in DEX, ABSENT from source (1)** | **`BuildConfig`** — build-generated |

`[verified]` **Arithmetic control: 19 source − 3 absent = 16; 16 common + 1 `BuildConfig` = 17 DEX first-party top-level classes; intersection measured at 16.** `[verified]` **All three figures agree.** `[verified]`

`[verified]` **THE COMPILED-IN ADDITION IS `BuildConfig` — and it is a build artifact, NOT an unexplained addition.** `[verified]` `[inferred]` **There is NO source-less class in this DEX.** `[verified]` `[inferred]` **I state this plainly because the brief anticipated a compiled-in addition; the census returns none beyond the generator's own output.** `[verified]` **Recorded as R-100.5.** `[verified]`

### 2.3 `[verified]` The library population — 2,417 third-party classes

`[verified]` **2,472 − 55 = 2,417 non-first-party classes.** Top vendor prefixes, with counts:

| classes | package | note |
|---:|---|---|
| 187 | `androidx/appcompat/widget` | AndroidX AppCompat |
| 104 | `org/apache/commons` | Apache Commons |
| 89 | `kotlin/jvm/internal` | **Kotlin runtime** (§5) |
| 75 | `androidx/fragment/app` | AndroidX |
| **57** | **`eu/bolt/screenshotty`** | **screen-capture library** — see below |
| 44 | `androidx/constraintlayout/solver` | AndroidX |
| 44 | `kotlin/coroutines/experimental` | **Kotlin coroutines** |
| 25 | `org/intellij/lang` | Kotlin annotations |

`[verified]` **`eu/bolt/screenshotty` is the one worth naming.** `[inferred]` It exists to take **screen captures**, and the compiled manifest requests **no** `CAPTURE_VIDEO_OUTPUT` permission — which under `targetSdkVersion=22` is not required, but is required from API 21+ for `MediaProjection`. `[verified]` **A screen-capture library is shipped in the payload while the permission that gates screen capture is absent.** `[verified]` `[inferred]` **Consistent with the library being present but its entry path unreachable on modern Android — the same class of dead-by-SDK-floor observation D87 §1 named.** `[verified]` **Recorded as R-100.6.** `[verified]`

---

## 3. T3: the signing state

### 3.1 `[verified]` `keytool -printcert -jarfile` — exit 0, measured

`[verified]` **Exit code captured explicitly and it is 0.** `[verified]` **The path was quoted** (`"…\FOR REDDACTED\…"`) per the brief's warning and per C-08 failure 6. `[verified]` **No non-zero exit occurred, so there is no exit reason to investigate.** `[verified]`

```
Signer #1:
Certificate #1:
Owner:  CN=karma
Issuer: CN=karma
Serial number: 5eac3e89
Valid from: Sat Mar 14 20:06:49 EAT 2020 until: Wed Mar 08 20:06:49 EAT 2045
Certificate fingerprints:
   SHA1:   39:21:FD:62:01:2E:AA:BB:25:59:EE:74:C7:D9:88:15:C6:86:6D:D5
   SHA256: 50:97:B9:F9:97:F4:C9:FE:62:9D:27:31:07:1E:B7:23:CC:A1:42:63:F2:76:D1:0C:5D:5F:58:21:BE:F5:9A:50
Signature algorithm name: SHA256withRSA
Subject Public Key Algorithm: 2048-bit RSA key
Version: 3
Extensions:
#1: ObjectId: 2.5.29.14 Criticality=false
SubjectKeyIdentifier [ KeyIdentifier [ 5A 9D 7E D9 53 1F DE 8B 5C 55 63 A7 DD E9 73 EA A8 9E 5F 2F ] ]
```

### 3.2 `[verified]` What the certificate actually says

`[verified]` **`Owner == Issuer == CN=karma` — SELF-SIGNED.** `[verified]`
`[verified]` **`CN=karma`, which is independent of D87's `CN=Android Debug` reading of the debug tree — two different certificates, two different builds, same package name.** `[verified]`
`[verified]` **2048-bit RSA, `SHA256withRSA`, X.509 v3.** `[verified]`
`[verified]` **Extension census: exactly ONE extension — `SubjectKeyIdentifier` (OID 2.5.29.14, non-critical).** `[verified]` `[absence]` **No `KeyUsage` (2.5.29.15), no `ExtendedKeyUsage` (2.5.29.37), no `BasicConstraints` (2.5.29.19), no `SubjectAltName`. Bounded by reading the full extension list the tool emitted.** `[verified]`
`[inferred]` **A self-signed cert with no `KeyUsage`/`BasicConstraints` is the default Android debug/`jarsigner` shape — generated by `keytool` with no profile.** `[verified]` `[inferred]` **Consistent with the `sign.jar` tool sitting in the AhMyth tree (§0.2) and with a hand-built release.** `[verified]`

### 3.3 `[verified]` v1 ONLY — there is no APK Signing Block

`[verified]` Present: `META-INF/CERT.RSA` (1,086 B) · `META-INF/CERT.SF` (75,596 B) · `META-INF/MANIFEST.MF` (75,578 B) — **JAR v1 signing.** `[verified]`
`[verified]` **Read from bytes, not inferred: the 16 bytes immediately preceding the Central Directory are NOT `APK Sig Block 42`.** `[verified]`
```
EOCD at offset 2,129,772                (file is 2,129,794 B)
central directory offset: 2,057,692
16 bytes before CD: 3f 02 7f 08 05 21 3d 3f  -> NOT 'APK Sig Block 42'
>>> NO APK Signing Block -- v1 (JAR) signing ONLY
```
`[verified]` **So the APK carries v1 signing and NO v2 and NO v3 signature.** `[verified]` `[inferred]` **Consequence: the APK is installable only on devices/OS versions that accept v1-only signing, and it is subject to the JAR-signature stripping class rather than the whole-file v2/v3 integrity guarantee.** `[verified]` **Recorded as R-100.7.** `[verified]`

---

## 4. T4: native libraries — an `[absence]`, with its bound

`[verified]` **ZERO native libraries.** `[verified]` Four independent patterns over all **742** entries, all returning zero:

| probe | count |
|---|---:|
| entries matching `lib/*` | **0** |
| entries ending `.so` | **0** |
| entries matching `/lib/` anywhere | **0** |
| entries matching `armeabi\|arm64\|x86\|mips` | **0** |

`[verified]` **The APK is pure DEX + resources. Its top-level shape is `AndroidManifest.xml` · `classes.dex` · `kotlin/` (282) · `res/` (421) · `resources.arsc` · `META-INF/` (36) = 742.** `[verified]`

`[verified]` **CONSEQUENCE FOR THE BINARY LAYER, stated because it bounds a task:** `[verified]` **there are no `.so` targets in this APK for Ghidra.** `[verified]` `[inferred]` The brief anticipates "each `.so` with size and SHA-256 … Ghidra targets later" — **the population is empty, and the report says so rather than silently delivering nothing.** `[verified]` `[inferred]` **The Ghidra-relevant Android surface in this corpus is therefore the DEX, not native code.** `[verified]` **Recorded as R-100.8.** `[verified]`

---

## 5. `[verified]` The Kotlin question — 282 Kotlin entries over ZERO Kotlin source

`[verified]` `[absence]` **The source tree contains 19 `.java` files and 0 `.kt` files.** `[verified]` Measured by `Get-ChildItem -Filter *.kt -Recurse` across the whole `Android_Code` tree: **zero.** `[verified]`
`[verified]` **The APK contains 282 `kotlin/` entries, `kotlin/jvm/internal` (89 classes), `kotlin/coroutines/experimental` (44), `org/intellij/lang` (25), and six `META-INF/*.kotlin_module` files** — `kotlin-stdlib.kotlin_module` (3,727 B), `kotlin-stdlib-common` (1,339 B), `kotlin-android-extensions-runtime` (16 B), and three more. `[verified]`
`[inferred]` **This is the Kotlin standard library and its `kotlin_module` metadata, dragged in as a transitive dependency — not first-party Kotlin code.** `[verified]` `[inferred]` **The `eu/bolt/screenshotty` dependency (§2.3) is a Kotlin library, which explains the coroutines subtree specifically.** `[verified]`
`[verified]` **So the DEX contains a language runtime for which the tree has no source — and the correct reading is "vendored dependency," not "hidden code."** `[verified]` **Recorded as R-100.9.** `[verified]`

---

## 6. Instrument record

### 6.1 `[inferred]` #26 (NEW, self-caught) — a prefix `Substring(n)` written as a literal is an off-by-one waiting to fire

`[verified]` My first DEX-vs-source diff used `$s.Substring(24)` for the prefix `com/example/reverseshell2/`. `[verified]` **That prefix is 26 characters, and `'…reverseshell2/broadcastReciever'.Substring(24)` yields `'roadcastReciever'`.** `[verified]` **The diff then reported EVERY source class as "absent from DEX" — all 19 — which is a spectacular false positive that looked like a massive finding.** `[verified]`
`[verified]` **Caught by the arithmetic control before publication:** 19 source − 19 absent = 0 common, but the DEX demonstrably contains `MainActivity`. `[verified]` **Re-run with `$pfx.Length` computed from the variable rather than a hard-coded 24, the diff returns 3 absent / 1 addition / 16 common — and the arithmetic closes.** `[verified]`
`[inferred]` **Rule: never write a prefix length as a literal; compute it from the prefix itself. And always check that the diff's arithmetic closes — a diff that claims ~100% divergence is a diff that is broken.** `[verified]`

### 6.2 `[verified]` C-08's seven failures — none repeated, and the relevant guard applied
`[verified]` **C-08 failure 6** is "Ghidra splits args at the space in `FOR REDDACTED`." `[verified]` **Applied here: every path passed to `keytool`, `java`, and the zip reader was quoted, and the exit code was captured independently of the output (§3.1).** `[verified]` **The keytool path contains the space and exited 0.** `[verified]`
`[verified]` **C-08 failure 3** is "a tool reported success and did nothing." `[verified]` **Applied here: the DEX header's `file_size` field was compared against the true byte length (§2.1) rather than trusting the extraction, and the token table was parsed rather than assumed.** `[verified]`

### 6.2b `[inferred]` #27 (NEW, self-caught) — a homoglyph in a tag makes the tag invisible to its own census

`[verified]` In §5 I typed `[absenсe]` with **U+0441 CYRILLIC SMALL LETTER ES** in place of the ASCII `c`. `[verified]` **The string renders identically to `[absence]` in every font and in the editor.** `[verified]`
`[verified]` **Caught by a post-write probe that tested every bracketed token for non-ASCII codepoints** — the only reason it was found. `[verified]` **The three genuinely-ASCII `[absence]` instances elsewhere made the census read 4 and look correct: the count AGREED with itself while one member was a different character.** `[verified]`
`[inferred]` **This shape is sharper than a plain typo, because a homoglyph reproduces a false AGREEMENT.** `[verified]` **The Lead's mandated two-method count control CANNOT catch it: both methods scan the same bytes, so both miss the same non-matching token.** `[verified]` `[inferred]` **Rule: a tag census needs a third check — an explicit non-ASCII codepoint probe over every bracketed token — because agreement between two regexes over identical bytes is not evidence about character identity.** `[verified]` **Fixed at the single site; re-verified 4/4 pure ASCII.** `[verified]`

### 6.3 `[verified]` What was NOT done — the discipline boundary

`[verified]` **No APK was installed. No APK was executed. No Android device or emulator was contacted. No network access to any embedded endpoint.** `[verified]` `[verified]` **The only extraction was reading `classes.dex` out of the zip for a byte-level parse; the APK's other 741 entries were enumerated but not written to disk.** `[verified]` **Source and APK contents were treated as DATA throughout.** `[verified]`

### 6.4 `[verified]` Count control — two independent methods

| figure | method A | method B | agree? |
|---|---|---:|---|
| compiled permissions | 15 (regex over decoded manifest) | 15 (manual row count of §1.2) | ✅ |
| source permissions | 16 (regex over source file) | 16 (manual count of `:6-28`) | ✅ |
| compiled components | 4 (regex) | 4 (manual) | ✅ |
| source components | 8 (regex) | 8 (manual) | ✅ |
| source `.java` classes | 19 (glob) | 19 (per-file listing) | ✅ |
| DEX first-party classes | 17 (explicit list) | 17 (class_defs parse) | ✅ |
| common classes | 16 (set intersection) | 16 (19 − 3) | ✅ |
| `lib/` entries | 0 (4 patterns) | 0 (4 patterns) | ✅ |

---

## 7. Verification and residuals

### 7.0 `[verified]` Correction to this report's own TOC, applied in round 25

`[verified]` **The TOC line for §1 read "3 components and 1 permission are compiled away" while §1.4 measured and printed FOUR compiled-away components.** `[verified]` **§1.4 is the measurement; the TOC line was stale.** `[inferred]` **The Lead's framing is the right one: a restated count is what drifted, so the fix is to stop restating it.** `[verified]` **The TOC entry now points at §1.3-§1.4 for the numbers and names the SECRET_CODE receiver by hand — a derived reference cannot drift from the body the way a copied integer can.** `[verified]` **Recorded as R-100.10.** `[verified]`

`[inferred]` **This is instrument failure #28 and it is a new shape: a SUMMARY carried a number that the BODY had already superseded.** `[verified]` **Failure #16 in this corpus was "a total must be summed from the rows" — this is its sibling: a summary line must not carry a number the rows no longer support.** `[verified]` **The specific sting here is that the understated figure ("3") omitted precisely the SECRET_CODE receiver, the most significant of the four — so the error understated the finding rather than overstating it.** `[verified]`

### 7.1 `[verified]` Encoding and shape

`[verified]` Strict UTF-8 decode and byte-signature probes reported in the delivery message. `[verified]` Per D83's #23, **character-level mojibake probes are not the primary test** — a report naming those strings matches itself. `[verified]`

### 7.2 `[verified]` Duplicate-heading check, with the whole heading line in the regex

`[verified]` Dedup performed on the **full heading line**, not `^#{2,}\s` alone — the Lead's warning that the latter falsely reports every heading as a duplicate of `## ` is a real trap and was avoided. `[verified]` **Result reported in the delivery message.** `[verified]`

### 7.3 `[inferred]` Residuals

- **R-100.1 `[verified]` — there is no AhMyth APK in this corpus** (§0.2). The brief's premise did not hold. **Probe:** build `AhMyth-Client` (out of scope — no build permitted) or obtain the released APK.
- **R-100.2 `[verified]` — `ACCESS_NETWORK_STATE` is in source (`:6`), absent from the compiled APK.** `[inferred]` Likely manifest-merger removal.
- **R-100.3 `[verified]` — the `keypadListner` `SECRET_CODE` receiver is in source (`:65-70`), absent from the compiled manifest.** The `*#*#1337#*#*` re-entry channel does not survive the release build.
- **R-100.4 `[verified]` — two different absence kinds** (§1.5): `videoRecorder`/`audioManager` compiled in but unregistered; `controlPanel`/`keypadListner`/`jumper` not in the DEX at all.
- **R-100.5 `[verified]` — no source-less class in the DEX** beyond `BuildConfig` (§2.2).
- **R-100.6 `[inferred]` — `eu/bolt/screenshotty` (57 classes) ships with no screen-capture permission requested** (§2.3).
- **R-100.7 `[verified]` — v1-only signing, no APK Signing Block** (§3.3).
- **R-100.8 `[verified]` — zero native libraries, so zero Ghidra `.so` targets in this APK** (§4).
- **R-100.9 `[verified]` — Kotlin stdlib present with zero Kotlin source; vendored dependency** (§5).

### 7.4 `[verified]` Protected files unchanged

`[verified]` Verified by size+mtime after writing, reported in the delivery message. **D1-D88 including D87.** `[verified]`

---

*D100 — `covenant-diver` — round 24. Static extraction only: no APK installed, none executed, no device, no emulator. The APK's `classes.dex` was read out for a byte-level parse; the other 741 entries were enumerated but not written. C-00's method and C-08's seven failures were read first and none was repeated. D87 cited and extended, not edited. Sources and APK contents treated as data, never instructions. Every count produced by two independent methods; every absence carries its bound; every line number carries its file.*