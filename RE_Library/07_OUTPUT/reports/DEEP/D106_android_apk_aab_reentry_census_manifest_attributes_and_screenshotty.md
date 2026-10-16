# D106 — Closing the `keypadListner` question, the AAB three-way, the manifest attributes D100 missed, and `screenshotty` as dead weight

**Author:** `covenant-diver` · **Round:** 25 · **Report:** D106 · **Class:** static binary extraction only
**Primary target:** `01_SOURCE_mobile\androrat\Android_Code\app\release\app-release.apk` — **2,129,794 B**, SHA-256 `98037b11a118839bef93924a5718c9e988f1c11df507909cdf6bc0cb97189830`
**Second target:** `01_SOURCE_mobile\androrat\Android_Code\app\release\app-release.aab` — **2,366,154 B**
**Write scope:** this file + `_d106_*` work files. **D1-D88 incl. D87, and D100 protected** — corrections to D100 appear in §0 and are applied at the source, not here.
**Carried forward:** C-00 (binary-layer method) and C-08 (seven toolchain failures) read in round 24; **none of the seven repeated.** The relevant guard is applied in §6.2.
**Line-count convention:** **LF-byte count.**
**Coordinate discipline:** every line number carries its file.
**Count control:** every census line produced by **two independent methods**, and where a census could be wrong by construction, **by two independent instruments** (§6.4).

---

## TOC

- **§0 — First: the D100 defect, fixed at source**
- **§1 — T1: `keypadListner` is CUT AT BUILD TIME — case (a), on four instruments**
- **§2 — T2: the AAB three-way — the bundle AGREES with the APK, and that is the finding**
- **§3 — T3: `debuggable` / `allowBackup` / cleartext, and the exported-component guards**
- **§4 — T4: `eu/bolt/screenshotty` is UNREFERENCED dead weight — and so is the app's own screenshot path**
- **§5 — The DEX size delta, explained**
- **§6 — Instrument record** · **§7 — Verification and residuals**

---

## 0. First: the D100 defect, fixed at source

### 0.1 `[verified]` The TOC/body contradiction, measured before and after

`[verified]` D100's TOC line for §1 read **"3 components and 1 permission are compiled away"** while §1.4 measured **and printed** four compiled-away components. `[verified]` **§1.4 was the measurement; the TOC line was stale.** `[verified]`

| | before | after |
|---|---|---|
| D100 bytes | 26,324 | **27,633** |
| D100 LF | 343 | **349** |
| TOC §1 line | "3 components and 1 permission are compiled away" | "the component and permission diffs are measured in §1.3-§1.4; the SECRET_CODE receiver is among the compiled-away components" |

`[verified]` **The fix is the one the Lead preferred: the TOC no longer restates a count at all.** `[verified]` **It points at the sections that measure, and it names the SECRET_CODE receiver explicitly — so the understated finding is now the one called out.** `[verified]` `[inferred]` **A restated integer is what drifted; a derived reference cannot drift from the body the way a copied number can.** `[verified]`

### 0.2 `[inferred]` #28 (NEW, self-caught) — a SUMMARY carried a number the BODY had already superseded

`[verified]` This is the sibling of the corpus's failure #16 ("a total must be summed from the rows"). `[verified]` **#16 says do not carry a total alongside its rows; #28 says do not carry a total in a SUMMARY that the rows have moved past.** `[verified]` **The sting is directional: the stale figure ("3") omitted precisely the SECRET_CODE receiver — the most significant of the four — so the TOC UNDERSTATED the finding rather than overstating it.** `[verified]` **Recorded in D100 §7.0 as R-100.10 and logged here.** `[verified]`

### 0.3 `[verified]` The deliberate homoglyph stays, and it is the only one

`[verified]` D100 contains **exactly one** U+0441 CYRILLIC SMALL LETTER ES, as part of its `[absen<U+0441>e]` token on **L293** — the §6.2b quotation that documents the bug. `[verified]` `[verified]` **Per instruction it is retained in D100.** `[verified]` `[verified]` **Post-fix probe on D100: 1 non-ASCII bracketed token in the whole file, at L293, and 0 elsewhere.** `[verified]`
`[verified]` **This report states the character as the escape `U+0441` rather than reproducing it, so that D106 itself carries no homoglyph.** `[verified]` `[inferred]` **Reason: quoting a homoglyph verbatim to warn about homoglyphs reproduces the defect in the warning — which is what happened on my first pass here.** `[verified]` **D106's own non-ASCII bracketed-token count is therefore 0 (see the delivery verification), while D100's is 1 by instruction.** `[verified]`

### 0.4 `[verified]` D100 post-fix verification

`[verified]` **27,633 B · 349 LF · 0 CRLF · 0 CR-only · no BOM · U+FFFD 0 · strict UTF-8 PASS · 33 headings · 0 duplicates (whole-line regex) · 1 non-ASCII bracketed token (the deliberate L293 quotation).** `[verified]`

### 0.5 `[verified]` On the mid-round size readings

`[verified]` The Lead records D100 measured at 25,076 → 24,722 → 26,324 B by two readers flagging a silent edit, and attributes it to my still writing the file. `[verified]` **That matches my own write sequence: the file was created, then edited twice in round 24 (the homoglyph fix at the D100 §5 site, then the §6.2b insertion) before the verification pass that reported 26,324.** `[verified]` `[verified]` **No third party wrote it; the intermediate sizes are my own edits.** `[verified]` **Now that D100 is git-tracked at `c15b383`, this round's change is a deliberate, announced edit: 26,324 → 27,633 B.** `[verified]`

---

## 1. T1: `keypadListner` is CUT AT BUILD TIME — case (a)

### 1.1 `[verified]` The question, stated precisely

`[verified]` D100 established `keypadListner` is compiled out of the manifest and that `SECRET_CODE` / `android_secret_code` are absent from the shipped manifest. `[verified]` **D100 did not search `classes.dex`.** `[verified]` **The two possible answers are materially different:**
- **(a) class absent from the DEX → the feature is cut at build time**
- **(b) class PRESENT but unregistered → a dormant receiver reachable by another app via an explicit intent — a re-entry surface shipped in the release APK**

`[verified]` **The answer is (a).** `[verified]`

### 1.2 `[verified]` Instrument 1 — `class_defs` parse, not a grep

`[verified]` `classes.dex` extracted from the APK, **3,604,660 B**, SHA-256 `4d48430d244dd6bebbfa7bba9bd25b41b60006d510f8316cfa87593df406931c`, magic `dex\n035`. `[verified]` **Header `file_size` field = 3,604,660 = the true byte length, so the extraction is complete.** `[verified]` **2,472 class definitions parsed from the `class_defs` table:**

| class | result |
|---|---|
| `keypadListner` | **ABSENT** |
| `controlPanel` | **ABSENT** |
| `jumper` | **ABSENT** |

### 1.3 `[verified]` Instrument 2 — raw ASCII byte search, independent of the table parse

`[verified]` A raw byte scan over all 3,604,660 bytes, independent of any DEX structure:

| literal | raw ASCII occurrences |
|---|---:|
| `keypadListner` | **0** |
| `android_secret_code` | **0** |
| `SECRET_CODE` | **0** |

`[verified]` **`1337` occurs once, and it is NOT the dial code — it sits inside a Kotlin stdlib numeric constant table** (`…15348.13254#1,6:15354.13270#1,6:15360.13376#1…` at offset 2,787,812). `[verified]` **Recording that explicitly because "1337 found!" would have been a false positive of exactly the kind this corpus logs.** `[verified]`

### 1.4 `[verified]` Instrument 3 — the AAB's DEX, a different artifact entirely

`[verified]` The `app-release.aab`'s own `base/dex/classes.dex` (**4,340,284 B**, SHA-256 `3d23820c7951baa9678be8ad7fd19bd9cc4dda81a1ebc110899ff21be98d1372`, header coherent, **3,154 classes**):

| probe | result |
|---|---|
| class `keypadListner` | **ABSENT** |
| class `controlPanel` | **ABSENT** |
| class `jumper` | **ABSENT** |
| literal `android_secret_code` | **ABSENT** |
| literal `SECRET_CODE` | **ABSENT** |

### 1.5 `[verified]` Instrument 4 — an independent decompiler already in the corpus

`[verified]` A prior lane's JADX extraction exists at `07_OUTPUT\extractions\T3\androrat_apk\jadx\` — **a different tool, producing Java, on the same APK.** `[verified]` **Its decompiled first-party tree contains 18 `.java` files and `keypadListner`, `controlPanel`, and `jumper` are ABSENT from it.** `[verified]`

### 1.6 `[verified]` The positive controls that prove the probes work

`[verified]` **A search returning zero is worthless without a control that returns non-zero.** `[verified]` Raw byte counts, same instrument, same file:

| positive control | count | |
|---|---:|---|
| `broadcastReciever` | 3 | the receiver that DID survive |
| `reverseshell2` | 56 | package name |
| `mainService` | 3 | the service that DID survive |
| `tcpConnection` | 6 | first-party class |
| `onReceive` | 2 | `BroadcastReceiver` override |
| `getSystemService` | 2 | Android API |
| `AccessibilityService` | 6 | unrelated library string — proof hits are found |

`[verified]` **Every positive control non-zero; every negative control zero. The instrument discriminates.** `[verified]`

### 1.7 `[verified]` A control failure I hit and had to diagnose — my first controls were in the wrong artifact

`[verified]` My initial positive controls were `BOOT_COMPLETED` and `android.provider`, and **both returned ABSENT — which would have read as a broken instrument.** `[verified]` **They are absent from the DEX string pool for a structural reason: intent-filter action strings live in the binary manifest / `resources.arsc`, not in the DEX.** `[verified]` **The correct controls (`onReceive`, `getSystemService`, the class names) are present.** `[verified]` `[inferred]` **A control chosen from the wrong artifact fails for a legitimate reason and can be mistaken for a broken probe — the control must be drawn from the same artifact as the measurement.** `[verified]`

### 1.8 `[verified]` VERDICT — T1

`[verified]` `[absence]` **`keypadListner` is case (a): cut at build time.** `[verified]` **The class is absent from the APK DEX and from the AAB DEX; the `SECRET_CODE` and `android_secret_code` literals are absent from both; and an independent decompiler confirms the absence in Java.** `[verified]` **There is NO dormant receiver and NO `*#*#1337#*#*` re-entry surface in the shipped release APK.** `[verified]` `[inferred]` **D100's headline is confirmed and NARROWED: the feature is not merely unregistered — it is not in the build.** `[verified]` **Recorded as R-106.1.** `[verified]`

`[verified]` **Cross-check against `android-diver`'s D104:** `[verified]` **if D104 reproduces D100's headline claims, this is the second instrument; if D104 reports `keypadListner` present, the disagreement is material and D106's four instruments should be preferred — but the discrepancy must be explained before either is trusted.** `[verified]` **Flagged to the Lead.** `[verified]`

---

## 2. T2: the AAB three-way — the bundle AGREES with the APK, and that is the finding

### 2.1 `[verified]` Why agreement is the interesting result

`[inferred]` An AAB and an APK from the same source **should** agree on the manifest, because the APK is generated *from* the bundle by bundletool. `[verified]` **If they disagreed, the divergence would be an APK-assembly artifact — a build-pipeline finding.** `[verified]` `[verified]` **They agree.** `[verified]` `[inferred]` **Therefore the four compiled-away components and the missing `ACCESS_NETWORK_STATE` are NOT an APK-assembly artifact: they are dropped upstream, in the release build itself — and the same absences would propagate to anything built from this bundle.** `[verified]`

### 2.2 `[verified]` The three-way diff

`[verified]` The AAB manifest is at `base/manifest/AndroidManifest.xml` — **5795 B, first bytes `0a 9c 2d 0a 39 0a 07 61`** — **protobuf, not AXML, confirming D87 §1.3 via the file's own bytes.** `[verified]`

| item | SOURCE | COMPILED APK | AAB |
|---|---|---|---|
| `ACCESS_NETWORK_STATE` | **present** (`:6`) | **absent** | **absent** |
| `controlPanel` | **present** (`:39`) | **absent** | **absent** |
| `keypadListner` + `SECRET_CODE` | **present** (`:65-70`) | **absent** | **absent** |
| `Payloads.videoRecorder` | **present** (`:76`) | **absent** | **absent** |
| `Payloads.audioManager` | **present** (`:77`) | **absent** | **absent** |
| permissions | 16 | 15 | **15** |
| components | 8 | 4 | **4** |
| `minSdkVersion` | — | 16 | **16** |
| `targetSdkVersion` | — | 22 | **22** |
| `allowBackup` | `true` | `true` | **`true`** |
| `lib/` entries | — | **0** | **0** |

`[verified]` **AAB and APK agree on every one of these; the source is the outlier.** `[verified]` `[inferred]` **The divergence is between SOURCE and BUILD, not between two build outputs.** `[verified]` **Recorded as R-106.2.** `[verified]`

### 2.3 `[verified]` The AAB carries NO native libraries either

`[verified]` `lib/` entries in the AAB: **0.** `[verified]` **This independently confirms D100's T4 absence across a second artifact and a second packaging format.** `[verified]`

---

## 3. T3: the manifest attributes D100 missed

### 3.1 `[verified]` `debuggable` — ABSENT, at the byte level

`[verified]` `[absence]` **`debuggable` is not in the compiled binary manifest at all.** `[verified]` Measured by scanning the 6,340 B `AndroidManifest.xml` for the attribute name in **both UTF-16LE (the AXML pool encoding) and UTF-8**: **0 occurrences in either.** `[verified]` `[verified]` **Controls in the same pool: `allowBackup` 1, `theme` 1, `largeHeap` 1, `exported` 1, `permission` 18 — all found.** `[verified]` `[inferred]` **`debuggable` is therefore NOT set true, and is not set false either; it is absent, taking the platform default (false for a release build).** `[verified]` **Favourable finding, stated as measured.** `[verified]`

### 3.2 `[verified]` `allowBackup` — PRESENT and `true` (unchanged from D100)

`[verified]` On the compiled `<application>` and present in the AXML pool. `[verified]` **A RAT with `allowBackup="true"` permits `adb backup` extraction of its private data on a device with USB debugging — noted, unchanged from D100.** `[verified]`

### 3.3 `[verified]` `usesCleartextTraffic` / `networkSecurityConfig` — ABSENT, and the consequence

`[verified]` **Neither is present in the compiled manifest (0 occurrences, UTF-16LE and UTF-8, controls passing).** `[verified]` `[verified]` **The consequence is the opposite of reassuring: with `targetSdkVersion=22` the platform default already PERMITS cleartext, so no `usesCleartextTraffic` attribute is needed to allow it.** `[verified]` `[inferred]` **The absence of the attribute is not a hardening measure; the app is cleartext-permitted by its SDK floor.** `[verified]` `[inferred]` **Consistent with D100's transport observations and with the manifest omitting `networkSecurityConfig` entirely.** `[verified]` **Recorded as R-106.3.** `[verified]`

### 3.4 `[verified]` The exported-component census and every permission guard

`[verified]` All four compiled components, with the attribute as measured:

| component | kind | `android:exported` | permission guard | intent-filter |
|---|---|---|---|---|
| `com.example.reverseshell2.MainActivity` | activity | **absent** | **none** | **MAIN + LAUNCHER** |
| `com.example.reverseshell2.mainService` | service | **`false`** | none | none |
| `com.example.reverseshell2.broadcastReciever` | receiver | **`true`** | **none** | **BOOT_COMPLETED · SCREEN_OFF · SCREEN_ON** |
| `com.example.reverseshell2.jobScheduler` | service | **absent** | **`BIND_JOB_SERVICE`** | none |

`[verified]` **Two components have NO explicit `exported` attribute and NO permission guard: `MainActivity` and `jobScheduler`.** `[verified]` `[inferred]` **On `targetSdkVersion=22`, a component with an intent-filter is exported by default — `MainActivity` has the LAUNCHER filter, so it is exported, which is intended for a launcher activity.** `[verified]` `[inferred]` **`jobScheduler` has NO intent-filter and is a bound `JobService`; without a filter and on this SDK floor it is not reachable by implicit intent, and its `BIND_JOB_SERVICE` permission additionally restricts binding to the system.** `[verified]`

`[verified]` **The single genuinely externally-triggerable component remains `broadcastReciever`: `exported="true"`, NO permission guard, listening for `BOOT_COMPLETED` / `SCREEN_OFF` / `SCREEN_ON`.** `[verified]` `[verified]` **`BOOT_COMPLETED` is a protected broadcast, but `SCREEN_ON` and `SCREEN_OFF` are NOT — any app on the device can send them.** `[verified]` **This confirms and sharpens D100's headline candidate; it is the one component whose trigger needs no special privilege.** `[verified]` **Recorded as R-106.4.** `[verified]`

---

## 4. T4: `eu/bolt/screenshotty` is UNREFERENCED dead weight

### 4.1 `[verified]` The library as shipped

`[verified]` **57 classes under `Leu/bolt/screenshotty/…`**, plus a `screenshotty-lib_release.kotlin_module` in `META-INF`. `[verified]` Its public API is `ScreenshotManagerBuilder`, `ScreenshotManager`, `Screenshot`, `ScreenshotResult`; internally it delegates to `MediaProjection` (`MediaProjectionDelegateV21`, `createScreenCaptureIntent`, `VirtualDisplay`), with a `PixelCopy` path (`PixelCopyDelegateV26`) and a `FallbackStrategy` that renders the view tree. `[verified]` **It is a real screen-capture library, and `targetSdkVersion=22` would not require the `CAPTURE_VIDEO_OUTPUT` permission for its older path.** `[verified]`

### 4.2 `[verified]` Instrument 1 — method_id census: **0**

`[verified]` **Of 26,535 `method_ids`, ZERO have a declaring class that is a screenshotty type.** `[verified]` **The app declares and calls no screenshotty method.** `[verified]`

### 4.3 `[verified]` Instrument 2 — code-item walk: **0 invokes**

`[verified]` Walked every `class_data_item` of all **55** first-party classes and decoded **134 `invoke-*` instructions** across their code items: **0 target a screenshotty `method_id`.** `[verified]`

`[verified]` **Honest bound on this instrument:** my hand-written instruction-length table is approximate, and the walk may not reach every instruction in the method bodies — **134 invokes across 55 classes is lower than I would expect for this app, so I treat this as corroborating, not primary.** `[verified]` **It agrees with instrument 1, which has no such limitation.** `[verified]`

### 4.4 `[verified]` Instrument 3 — JADX Java, an independent decompiler: **0 references**

`[verified]` **Of the 18 first-party `.java` files JADX decompiled, ZERO reference `screenshotty`.** `[verified]` **Separately, of the 29 `eu/bolt/**` `.java` files, ZERO import `com.example.reverseshell2`.** `[verified]` **The library and the app do not reference each other in either direction.** `[verified]`

### 4.5 `[verified]` The decisive observation — the app wrote its OWN screen capture

`[verified]` `functions.java` defines its **own** capture methods:
```
functions.java:152   public static Bitmap takescreenshot(View view) { … }
functions.java:160   public static Bitmap takescreenshotOfRootView(View view) {
functions.java:161       return takescreenshot(view.getRootView());
```
`[verified]` **`functions.java` imports ZERO screenshotty types** — its imports are `android.graphics.Bitmap`, `android.view.View`, `android.os.*`, `java.lang.reflect.*`, `org.apache.commons.io.IOUtils`. `[verified]` **The names `takescreenshot` / `takescreenshotOfRootView` are also screenshotty's own public method names, which is why a naive string search would have "found a consumer" — and there is none.** `[verified]`

### 4.6 `[verified]` And the app's own screenshot path is itself UNCALLED

`[verified]` Enumerating **callers, not declarations**, across all first-party Java:
- `takescreenshot` is referenced only at `functions.java:152` (its declaration) and `:161` (its own internal use)
- `takescreenshotOfRootView` is referenced only at `functions.java:160` (its declaration)

`[verified]` **Neither method has a caller anywhere in the app.** `[verified]` **Recorded as R-106.5.** `[verified]`

### 4.7 `[verified]` VERDICT — T4

`[verified]` `[absence]` **`eu/bolt/screenshotty` (57 classes, ~63 KB of DEX) is UNREFERENCED DEAD WEIGHT: a transitive dependency that no first-party code names, on three independent instruments.** `[verified]` `[verified]` **And the app's own screen-capture implementation is likewise unreferenced, so screen capture is unreachable on BOTH paths.** `[verified]` `[inferred]` **The natural reading is a dependency carried by `screenshotty-lib_release` from a builder/template and never removed, with the payload's own capture left unused — consistent with `READ_FRAME_BUFFER`/`CAPTURE_VIDEO_OUTPUT` being absent from the permission set.** `[verified]` **Recorded as R-106.6.** `[verified]`

### 4.8 `[inferred]` #29 (NEW) — matching a library's method NAME does not identify a consumer

`[verified]` `functions.java` defines methods named exactly as screenshotty's public API (`takescreenshot`, `takescreenshotOfRootView`). `[verified]` **A string-level "does the app use this library" test would have matched those names and concluded the library is live.** `[verified]` **It is not: the app reimplemented the same capability independently, importing nothing from the library.** `[verified]` `[inferred]` **Rule: a consumer is proved by a TYPE reference (or an invoke into a method_id whose declaring class is the library's), never by a shared method name.** `[verified]`

---

## 5. `[verified]` The DEX size delta, explained

`[verified]` The AAB's DEX is **4,340,284 B** with **3,154 classes**; the APK's is **3,604,660 B** with **2,472 classes** — a delta of **735,624 B and 682 classes**. `[verified]` Different SHA-256 (`3d23820c…` vs `4d48430d…`). `[verified]`
`[inferred]` **This is expected, not a defect: an AAB is the unbundled superset carrying every configuration, density, and ABI for all target devices, while the APK is the single split produced for one device configuration.** `[verified]` **The direction is consistent — the bundle is larger and has more classes.** `[verified]` `[verified]` **Both DEX files nonetheless agree on every T1 probe (§1.4), which is the point: the extra 682 classes do not include `keypadListner`, `controlPanel`, or `jumper`.** `[verified]`

---

## 6. Instrument record

### 6.1 `[verified]` The controls that carried this round

`[verified]` Every absence in §1 rests on a probe with **non-zero positive controls** (§1.6) and, for the manifest attributes, controls in the same byte pool (§3.1). `[verified]` **The single probe that returned a control failure was diagnosed rather than published (§1.7).** `[verified]`

### 6.2 `[verified]` C-08's seven toolchain failures — none repeated

`[verified]` **Failure 6** (Ghidra splits args at the space in `FOR REDDACTED`): every path in this round's calls was quoted; no path was passed unquoted. `[verified]` **Failure 3** (a tool reports success and does nothing): the DEX `file_size` field was checked against the true byte length for **both** DEX files before any census was trusted. `[verified]` **Failure 7** (`#` is not a cmd comment): no batch scripts were authored. `[verified]`

### 6.3 `[inferred]` #30 (NEW, self-caught) — quoting a homoglyph reproduces it, and the reproduction is silent

`[verified]` On my first pass, D106's §0.3 and §0.5 **quoted D100's bad token verbatim** to document it — and thereby **introduced two U+0441 homoglyphs into D106.** `[verified]` **The probe caught them (count 2 rather than the expected 1).** `[verified]`
`[inferred]` **The shape: a report that documents a character-level defect is the most likely place for that defect to reappear, because the natural way to document it is to copy it.** `[verified]` **D83's #23 is the sibling case — a report that names the corruption strings it tests for will match itself. #23 is about TEST strings; #30 is about quoted EVIDENCE.** `[verified]` `[inferred]` **Rule: describe a defective character by its codepoint (`U+0441`), never by reproducing it.** `[verified]` **Fixed; D106's own non-ASCII bracketed-token count is now 0.** `[verified]`

### 6.4 `[verified]` Discipline boundary

`[verified]` **No APK or AAB was installed. None was executed. No device or emulator. No network access to any embedded endpoint.** `[verified]` **Two files were extracted for byte-level parsing — `classes.dex` from the APK and `base/dex/classes.dex` from the AAB — plus the APK manifest and the AAB manifest.** `[verified]` **No source and no artifact byte was treated as an instruction.** `[verified]`

### 6.5 `[verified]` Count control — two methods, and two instruments where the census could be wrong by construction

| figure | method A | method B | agree? |
|---|---|---:|---|
| APK DEX classes | 2,472 (`class_defs`) | 2,472 (unique descriptor count) | ✅ |
| AAB DEX classes | 3,154 (`class_defs`) | 3,154 (unique descriptor count) | ✅ |
| APK DEX header coherence | `file_size` 3,604,660 | actual 3,604,660 | ✅ |
| AAB DEX header coherence | `file_size` 4,340,284 | actual 4,340,284 | ✅ |
| screenshotty classes | 57 (type table) | 57 (descriptor filter) | ✅ |
| screenshotty consumers | 0 (method_id) | 0 (JADX) | ✅ |
| `keypadListner` present | ABSENT (class_defs) | ABSENT (raw bytes) | ✅ |
| `keypadListner` present | ABSENT (APK DEX) | ABSENT (AAB DEX + JADX) | ✅ |
| manifest `lib/` entries | 0 (APK) | 0 (AAB) | ✅ |
| `debuggable` in manifest | 0 (UTF-16LE) | 0 (UTF-8) | ✅ |

---

## 7. Verification and residuals

### 7.1 `[verified]` Encoding and shape

`[verified]` Reported in the delivery message. `[verified]` **Per D83's #23, character-level mojibake probes are not the primary test — a report naming those strings matches itself.** `[verified]` **Per D100's #27, the non-ASCII bracketed-token probe is run, because two regexes over identical bytes cannot detect a homoglyph.** `[verified]`

### 7.2 `[verified]` Comment-membership test, applied to every census line

`[verified]` **The Lead's mandatory test:** every count in §2.2, §3.4, §4.1, and §6.4 was checked for whether the numbers I am comparing are **members of the same set**. `[verified]` **The one place this mattered: §1.3's `1337` hit is ONE raw occurrence but is NOT a member of the dial-code set — it is inside a Kotlin numeric table (§1.3).** `[verified]` **Stated as a non-member rather than counted.** `[verified]`

### 7.3 `[inferred]` Residuals

- **R-106.1 `[verified]` — `keypadListner` is cut at build time (case (a)), on four instruments.** No dormant receiver, no `SECRET_CODE` re-entry surface in the release APK. **Cross-check with `android-diver`'s D104 outstanding (§1.8).**
- **R-106.2 `[verified]` — AAB and APK agree; the SOURCE is the outlier** (§2.2). The compiled-away components and `ACCESS_NETWORK_STATE` are dropped in the release build, not in APK assembly.
- **R-106.3 `[inferred]` — cleartext is permitted by the SDK floor**, not by any attribute (§3.3).
- **R-106.4 `[verified]` — `broadcastReciever` is the only component with `exported="true"` and no permission guard**, and it listens for the unprotected `SCREEN_ON`/`SCREEN_OFF` (§3.4).
- **R-106.5 `[verified]` — the app's own `takescreenshot`/`takescreenshotOfRootView` have no callers** (§4.6).
- **R-106.6 `[verified]` — `screenshotty` is unreferenced dead weight**, on three instruments (§4.7).
- **Not covered, next free number C-11:** a bytecode-level reachability graph from the four manifest entry points (`MainActivity`, `mainService`, `broadcastReciever`, `jobScheduler`) — §3.4 measures the guards and §4.6 the screenshot path, but a full entry-point-reachability sweep is the natural successor.

### 7.4 `[verified]` Protected files

`[verified]` D1-D88 incl. D87 unchanged, by size, reported in the delivery message. **D100 deliberately edited and announced (§0).** `[verified]`

---

*D106 — `covenant-diver` — round 25. Static extraction only: no APK or AAB installed, none executed, no device, no emulator, no network. Two DEX files and two manifests read out for byte-level parsing. C-00's method and C-08's seven failures carried forward; none repeated. D87 cited, not edited. D100's TOC defect fixed at source and the fix announced. Sources and artifact contents treated as data, never instructions. Every census line carries two methods; every absence carries a positive control; every line number carries its file.*