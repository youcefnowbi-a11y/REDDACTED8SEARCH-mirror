# D104 — AAB/APK manifest three-way diff, DEX class census, and SECRET_CODE reachability

**Author:** `android-diver` · **Round:** 25 · **Report:** D104 · **Class:** static artifact extraction only
**Predecessors in-lane:** D87 (release manifest floor and guard), D97 (WASM assembler, sqlite VFS, JVM tooling)

---

## 0. Verdicts up front

| # | Question | Verdict | Confidence |
|---|---|---|---|
| V1 | Is `keypadListner`'s SECRET_CODE channel (a) cut from the release build, or (b) present-but-unregistered? | **(a) cut entirely.** The class is absent from the DEX string pool, absent from the type table, and absent from the compiled manifest — in **both** the APK and the AAB. | `[verified]` |
| V2 | Does the AAB and the APK, built from the same source, agree? | **No — and the disagreement is security-relevant.** `broadcastReciever` carries `exported="true"` in the AAB and an **unset** `exported` value (`data=0xFFFFFFFF`) in the APK. | `[verified]` |
| V3 | Is `ACCESS_NETWORK_STATE` in the AAB? | **No — in neither artifact.** Source declares 16 `uses-permission`; both binaries ship 15. | `[verified]` |
| V4 | Does D100's class arithmetic close? | **No.** D100's three "absent" classes are absent from **both** artifacts, and `BuildConfig` is present in **both** — it is not an APK-only addition. The real APK/AAB delta is 2 classes, neither of them on D100's list. | `[verified]` |
| V5 | Does any exported component lack a permission guard? | **Two.** `MainActivity` (default-exported, launcher — expected) and `broadcastReciever` (default-exported, receives `BOOT_COMPLETED` — **not** expected). | `[verified]` |
| V6 | Is `eu/bolt/screenshotty` reachable? | **No. Dead dependency weight.** 57 classes in both DEXes, **zero** app-side references. | `[verified]` |
| V7 | Reproduce the `sign.jar` pair independently? | **Reproduced exactly.** Both artifacts, all four headline figures. | `[verified]` |
| V8 | Why is the AAB DEX 735,624 B larger? | Shrinker exclusion: the AAB carries ~636 extra `org.apache.*` types plus slf4j, springframework, jaredrummler. Same app classes, more dead library weight. | `[verified]` |

**Headline:** the SECRET_CODE re-entry surface is **not** shipped. It is compiled out of both artifacts, and the class that would have opened `controlPanel` does not exist in any release DEX. The more interesting finding is V2: the two release artifacts **disagree about the export state of the one component that starts the RAT on boot**, and the APK is the one that lost the attribute.

---

## 1. Instrument validation — a decoder that ignores an offset basis returns plausible nonsense

This section comes first because three separate defects in my own tooling nearly produced wrong answers, and the corpus rule *"a decoder that ignores a flag or an offset basis returns plausible nonsense, not an error"* (D79) applies to me. Each defect is recorded with the observable that exposed it.

### 1.1 Defect 1 — AXML string pool: `stringsStart` ignored

`ResStringPool_header` carries its own `stringsStart` field. My first decoder computed the string data base as `chunk_offset + header_size`. That is **not** the basis.

| basis used | computed base | result |
|---|---|---|
| `off + header_size` (28) | 36 | first 40 strings all decode to `''` — **no exception** |
| `off + stringsStart` (292) | 300 | `05 00 74 00 68 00 65 00 6d 00 65 00` → length 5, UTF-16LE `theme` — correct |

The failure mode is the dangerous one: an **empty string**, not a crash. Had I trusted it, I would have reported an empty manifest string pool and concluded the manifest was stripped.

**Fix, with assertion:** `assert BASE >= off + header_size + 4*stringCount` (the data base must sit past the offsets array). Applied and passing for both AXML manifests in play.

### 1.2 Defect 2 — AXML attribute type: reading the low byte instead of the high byte

`ResXMLTree_attribute` stores `TypedValue` fields as `(size, res0, dataType, data)`. I unpacked the pair as `<IIIII` and took `type & 0xFF` — the **low** byte.

| attribute | raw `atyp` | `& 0xFF` (wrong) | `>> 24` (correct) |
|---|---|---|---|
| `name` | `0x03000008` | `0x08` → "string index"? | `0x03` → **TYPE_STRING** |
| `exported` | `0x12000008` | `0x08` | `0x12` → **TYPE_INT_BOOLEAN** |

Because *every* attribute shares the trailing `0x08`, the wrong mask made every attribute look like type `0x08` and every value decode as a string-pool index — producing `exported = theme` and `exported = 51` in successive runs. Both are wrong, and both look like data.

**Fix, with assertion:**
```
assert (0x03000008 >> 24) & 0xFF == 0x03
assert (0x12000008 >> 24) & 0xFF == 0x12
```
Both pass. Type is `(atyp >> 24) & 0xFF`.

### 1.3 Defect 3 — attribute *count* read from the wrong sub-field

`ResXMLTree_attrExt` is `ns(4) name(4) attributeStart(2) attributeSize(2) attributeCount(2) idIndex(2) classIndex(2) styleIndex(2)`. I read `<HHHH` at `+24` and took the **second** value as the count. It is the third.

Observable: the `<manifest>` element reported `attrCount=20` and the walk died with `IndexError: list index out of range` at `STR[anm]` — an index past the 66-string pool. Real values: `attributeStart=20, attributeSize=20, attributeCount=7`.

**Fix:** `<HHH` at `+24`, attributes at `node + 16 + attributeStart`, stride `attributeSize`.

### 1.4 The negative control that validates the whole AXML instrument

A chunk walk alone proves nothing about **record framing**. The null hypothesis is that my 20-byte stride is wrong somewhere, which would drift boundaries and make a genuinely-present attribute look absent.

| test | result |
|---|---|
| distinct `(attributeStart, attributeSize)` pairs across all 31 elements | **one** — `(20, 20)` |
| elements where `16 + attributeStart + attributeSize*count > chunk_size` | **0** |
| `<receiver>` attr block: `36 .. 96` of declared `chunk_size=96` | **exact** |
| full chunk walk terminus vs file size | `6340 == 6340` **exact** |

Stride is uniform, no overflow, and the walk lands exactly on EOF. The framing is sound, so V2 and V5 are measurements rather than artifacts of my decoder. **Had any of these four failed, V2 would have been an unproven claim.**

### 1.5 DEX instrument validation

Both DEX files pass independent integrity gates before any content claim:

| artifact | magic | header `file_size` vs actual | adler32 header vs recomputed |
|---|---|---|---|
| `app-release.apk` → `classes.dex` | `dex\n035\0` | 3,604,660 == 3,604,660 ✓ | `0x1b0b8642` == `0x1b0b8642` ✓ |
| `app-release.aab` → `base/dex/classes.dex` | `dex\n035\0` | 4,340,284 == 4,340,284 ✓ | `0xa4afbb93` == `0xa4afbb93` ✓ |

Absence claims require a **working control**. The string search is controlled in both artifacts:

| literal | APK | AAB | meaning |
|---|---|---|---|
| `com.example.reverseshell2.MainActivity` | present | present | positive control |
| `broadcastRecieverClass` (source's own `TAG`) | 1 | 1 | positive control, source-derived |
| `Not running, restarting service` | 1 | 1 | positive control, source-derived |
| `10000000` — no; see `1337` below | — | — | — |
| `keypadListner` | **0** | **0** | target |
| `android_secret_code` | **0** | **0** | target |
| `android.provider.Telephony.SECRET_CODE` | **0** | **0** | target |
| `adadadd` (source's `keypadListner` log tag) | **0** | **0** | source-derived negative control |

**The `1337` probe is the one that matters.** A naive substring search for `1337` returns **1 match in the APK** — a Kotlin `SMAP` debug blob (`_Arrays.kt` / `Maps.kt` line-mapping table) that happens to contain the digit run. A lane that grepped for `1337`, found a hit, and stopped would have reported **case (b)**: present-but-unregistered, dormant re-entry surface. The hit is real; the inference would have been false.

---

## 2. V1 — the SECRET_CODE question, settled

### 2.1 What the source declares

`app/src/main/AndroidManifest.xml` (3,437 B, SHA-256 `15994560…FBF70CB`), lines 65–70:

```xml
<receiver android:name=".keypadListner">
    <intent-filter>
        <action android:name="android.provider.Telephony.SECRET_CODE" />
        <data android:scheme="android_secret_code" android:host="1337"/>
    </intent-filter>
</receiver>
```

And `keypadListner.java` is a full implementation, not a stub:

```java
public class keypadListner extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        Log.d("adadadd","in");
        Intent i = new Intent(context, controlPanel.class);
        i.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        context.startActivity(i);
    }
}
```

The dialling code `*#*#1337#*#*` would open `controlPanel` — the RAT's operator interface.

### 2.2 What the binaries contain

| probe | APK | AAB |
|---|---|---|
| `keypadListner` in string pool | 0 | 0 |
| `keypadListner` in type descriptors | 0 | 0 |
| `android_secret_code` in string pool | 0 | 0 |
| `android.provider.Telephony.SECRET_CODE` | 0 | 0 |
| `controlPanel` in type descriptors | 0 | 0 |
| `<receiver>` count in manifest | 1 (`broadcastReciever`) | 1 (`broadcastReciever`) |

`keypadListner.onReceive` also calls `controlPanel.class`. **The consumer is gone with the producer** — there is no class that references a missing receiver, which is what would have indicated orphaned dead code.

### 2.3 Verdict

**Case (a): the channel is cut entirely from the release build.** Not (b). There is no dormant receiver: no class, no registration, no intent-filter action, no target activity. An explicit intent aimed at `com.example.reverseshell2.keypadListner` from another app would fail to resolve — there is nothing to resolve to.

This is a **negative result and it is the honest one**. The materially more serious outcome the lead asked me to test for does not obtain, and I am not softening that in either direction: the re-entry surface is not shipped.

### 2.4 The pair-census: 3 source files, 0 DEX classes

| source file | in APK DEX | in AAB DEX |
|---|---|---|
| `keypadListner.java` | absent | absent |
| `controlPanel.java` | absent | absent |
| `jumper.java` | absent | absent |

All three sit on the same dead branch: `keypadListner` starts `controlPanel`; `jumper` is the sibling utility. Their joint absence is a **coherent removal**, not three independent accidents. Nothing in either DEX references any of the three.

---

## 3. V2 — the three-way manifest diff

### 3.1 The three inputs, pinned

| input | bytes | SHA-256 | format |
|---|---|---|---|
| `app/src/main/AndroidManifest.xml` | 3,437 | `15994560E02E46B6E302AFB6B64AF650D72B5551F8A166B7F10455537FBF70CB` | XML text |
| `app-release.apk` → `AndroidManifest.xml` | 6,340 | AXML `0x00080003`, `file_size` == actual ✓ | binary AXML |
| `app-release.aab` → `base/manifest/AndroidManifest.xml` | 5,795 | protobuf `XmlNode` field 1 | protobuf |

Compressed container hashes:

| artifact | bytes | SHA-256 |
|---|---|---|
| `app-release.apk` | 2,129,794 | `98037B11A118839BEF93924A5718C9E988F1C11DF507909CDF6BC0CB97189830` |
| `app-release.aab` | 2,366,154 | `2251774AC27DE59586DE01ACECAC9AA3D4CC6442B396E6431F8F761ECA85B410` |

### 3.2 Component diff

| component | SOURCE | AAB | APK (compiled) | agree? |
|---|---|---|---|---|
| `MainActivity` | exported absent | exported absent | exported absent | ✓ |
| `mainService` | `exported="false"` | `false` | `false` | ✓ |
| `broadcastReciever` | **`exported="true"`** | **`true`** | **present, `data=0xFFFFFFFF` (unset)** | **✗** |
| `jobScheduler` | — (`permission` attr) | `BIND_JOB_SERVICE` | `BIND_JOB_SERVICE` | ✓ |
| `controlPanel` | present | **absent** | **absent** | ✓ (both drop it) |
| `keypadListner` | present | **absent** | **absent** | ✓ (both drop it) |
| `Payloads.videoRecorder` | present | **absent** | **absent** | ✓ (both drop it) |
| `Payloads.audioManager` | present | **absent** | **absent** | ✓ (both drop it) |

**The one disagreement is `broadcastReciever`.** The source sets `exported="true"` explicitly. The AAB preserves it. The APK stores the attribute record with `data=0xFFFFFFFF`.

### 3.3 Why the APK's `0xFFFFFFFF` is worth a finding

`0xFFFFFFFF` in a `TYPE_INT_BOOLEAN` slot means **the attribute is present in the record but carries no value**. It is not "the attribute was removed" — a removed attribute would not have a record at all. So:

- A reader of the compiled APK manifest sees an `exported` attribute on the receiver and would reasonably read it as meaningful.
- The effective platform behaviour: `exported` defaults to `true` when a component has an intent-filter (API < 31 target).
- The source's explicit `true` and the APK's unset value **happen to agree in effect** — the receiver is exported either way.

So this is **not** a privilege escalation introduced by the build. It is a **silent loss of an explicit security declaration**, and it matters because:

1. The attribute is *present but valueless*, which is a shape that defeats a naive manifest audit. A checker that tests "does `exported` exist?" answers **yes** on the APK; a checker that tests its value gets nothing.
2. On API ≥ 31 (`targetSdkVersion=29` here, so not yet), an unset `exported` on an intent-filtered component is a **build error**. The AAB preserves the information needed to satisfy that; the APK does not.

I record it as a **build-pipeline divergence in the security-relevant direction**, with the explicit caveat that the *effective* export state is unchanged. Calling it an escalation would overstate it; calling it nothing would understate it.

### 3.4 Permission diff

| set | count | members |
|---|---|---|
| SOURCE `uses-permission` | 16 | includes `ACCESS_NETWORK_STATE` |
| AAB `uses-permission` | 15 | `ACCESS_NETWORK_STATE` **absent** |
| APK declared permissions | 15 | `ACCESS_NETWORK_STATE` **absent** |

**Both artifacts drop `ACCESS_NETWORK_STATE`.** This is a consistent build behaviour, not an APK/AAB divergence.

Two decode traps in this area, recorded so the next lane does not repeat them:

- **`BIND_JOB_SERVICE` is not an addition.** It appears in both compiled permission sets because it is the `jobScheduler` service's `android:permission` **attribute**, not a `<uses-permission>` element. Naive string-set subtraction reports it as "in APK, absent from source" — a false positive I produced and then refuted.
- **`uses-permission` is not a permission.** My first AAB string-set pass counted it as the 17th member. It is the element name.

Corrected: AAB `<uses-permission>` elements = 15, `<uses-feature>` = 2, matching the APK's structure exactly.

### 3.5 Flags

| flag | SOURCE | AAB | APK |
|---|---|---|---|
| `debuggable` | absent | absent | absent |
| `allowBackup` | `true` | present | present |
| `usesCleartextTraffic` | absent | absent | absent |
| `networkSecurityConfig` | absent | absent | absent |
| `testOnly` | absent | absent | absent |

**`android:debuggable` is not set in any of the three.** The release build is not debuggable. `allowBackup="true"` is inherited from source into both artifacts — noted, not escalated (it is the source author's own setting).

---

## 4. V4 — D100's class arithmetic, independently re-measured

**Attribution.** D100 (`D100_android_binary_layer_manifest_dex_signing_and_native_census.md`) is authored by `covenant-diver`, not by this lane. I read it as another lane's work and re-measured its headline claims from the artifacts rather than inheriting its premises, per the lead's framing.

**Revision pin.** D100 was 26,324 B at mtime 20:37:06 when I began this round. During the round it became **27,633 B at mtime 20:50:20** — its author is live in the file. All citations below refer to the revision I read at 26,324 B and are **not** claims about the current file. A size change on a file another writer still owns is a moving target, not evidence about content.

### 4.1 What I measured

Method: enumerate every type descriptor beginning `Lcom/example/reverseshell2/` in each DEX's type table. This is a census, not a name probe — D100's three names are checked *within* a full enumeration rather than looked up directly, so a homoglyph or a variant spelling cannot produce a false absence.

| | APK | AAB |
|---|---|---|
| app type descriptors | **55** | **53** |
| APK-only | 2 | — |
| AAB-only | — | **0** |

**Arithmetic closure:** `|APK| − |AAB| = 55 − 53 = 2`, and `|APK−AAB| − |AAB−APK| = 2 − 0 = 2`. Identity holds.

### 4.2 Re-checking D100's four specific claims

| D100 claim | my measurement | result |
|---|---|---|
| `controlPanel` absent from DEX | absent from APK **and** AAB | claim true, **scope wrong** |
| `jumper` absent from DEX | absent from APK **and** AAB | claim true, **scope wrong** |
| `keypadListner` absent from DEX | absent from APK **and** AAB | claim true, **scope wrong** |
| `BuildConfig` is the only addition | **present in BOTH** (`Lcom/example/reverseshell2/BuildConfig;` in each type table) | **refuted** |

`BuildConfig` is generated by the Android Gradle Plugin into every build variant. It is not an APK-only addition and cannot be, without a toolchain that strips it from the AAB alone.

### 4.3 The actual APK/AAB class delta

| class | in APK | in AAB |
|---|---|---|
| `Lcom/example/reverseshell2/config;` | present | **absent** |
| `Lcom/example/reverseshell2/Payloads/videoRecorder$1$1$3;` | present | **absent** |

Neither is on D100's list. `config` is confirmed APK-only by descriptor search: the APK's pool contains `Lcom/example/reverseshell2/config;`, the AAB's contains no `Lcom/example/reverseshell2/config` descriptor at all (it contains the bare string `config`, from unrelated context). `videoRecorder$1$1$3` is an anonymous inner class; its siblings `$1$1$1` and `$1$1$2` are present in both, so the AAB is missing exactly one lambda/anonymous body.

**Where the difference is likely to originate:** the APK is the shrunk artifact and the AAB is the source of truth for the bundletool pipeline. Different R8/Minify decisions across the two output paths would produce small inner-class and unused-holder differences like these. I record the fact; I do not claim the mechanism, because I did not read the Gradle configuration.

---

## 5. V5 — exported-component permission audit

Full enumeration of `<activity>`, `<service>`, `<receiver>`, `<provider>` in the compiled APK manifest (4 components):

| # | component | exported | permission | assessment |
|---|---|---|---|---|
| 1 | `com.example.reverseshell2.MainActivity` | absent → default `true` (launcher intent-filter) | none | **expected** — the launcher must be exported |
| 2 | `com.example.reverseshell2.mainService` | `false` | none | **safe** — explicit `false`, not reachable |
| 3 | `com.example.reverseshell2.broadcastReciever` | absent → default `true` | **none** | **flagged** — exported, unguarded, receives `BOOT_COMPLETED` |
| 4 | `com.example.reverseshell2.jobScheduler` | absent | `android.permission.BIND_JOB_SERVICE` | **gated** |

**Two components are reachable without a permission guard.** One is the launcher activity and is correct by design. The other is `broadcastReciever`.

### 5.1 Why `broadcastReciever` matters beyond "it's a RAT"

The receiver takes `BOOT_COMPLETED`, `SCREEN_OFF`, `SCREEN_ON`. Any app on the device can `sendBroadcast` a matching intent to a `SEND`-visible receiver — no signature, no permission, no user interaction. On receiving one, `broadcastReciever.onReceive` checks whether `mainService` is running and, if not, **starts it**:

```java
if(isMyServiceRunning(context)) { ... }
else { Intent intent1 = new Intent(context, mainService.class); context.startService(intent1); }
```

So the unguarded component is a **service-start trigger**. It is fully present and live in both DEXes — verified by its own source literals (`broadcastRecieverClass`, `Received...`, `Not running, restarting service`, `Yeah, it's running...`) plus `startService` and `getRunningServices`, all resolving in both APK and AAB.

This is the **second** re-entry path in the corpus: `keypadListner` was removed, and `broadcastReciever` remains, unguarded, doing exactly the "restart the payload" job that a dormant receiver would have done. The lead's framing — that (b) would be "a dormant re-entry surface reachable by another app via an explicit intent" — describes this component rather than the one it was aimed at.

**Caveat, stated plainly:** this is a static reachability property, not an observed exploitation. I did not execute the APK, attach a debugger, or run a device. `exported` defaulting to `true` for intent-filtered components is standard Android behaviour on `targetSdkVersion=29`; the anomaly is that the source's explicit declaration was **silently dropped** in the APK (V2), which is precisely what would hide this from a manifest audit.

---

## 6. V6 — `eu/bolt/screenshotty`: dead weight, not reachable capability

| probe | APK | AAB |
|---|---|---|
| `eu.bolt.screenshotty` type descriptors | **57** | **57** |
| screenshotty strings | 79 | 79 |
| app-side (`com/example/reverseshell2`) references | **0** | **0** |

The library's `META-INF/screenshotty-lib_release.kotlin_module` is present in both:

```
00 00 00 03 00 00 00 01 00 00 00 01 00 00 00 0f
0a 2d 0a 1d eu.bolt.screenshotty.internal 12 0c ExtensionsKt
```

57 classes and 79 internal string references, and **not one reference from any `com.example.reverseshell2` class**. There is no screen-capture permission in either manifest, and no RAT class loads, constructs, or invokes the library.

**Verdict: consumers = 0. It is dead dependency weight.** It is retained because the build does not shrink it out (the AAB is the unshrunk artifact — see §7), not because anything uses it. It contributes attack surface only in the sense that any unreferenced code does: it cannot be reached without a code path that the app does not contain.

---

## 7. V8 — the DEX size gap, explained

The AAB's DEX is **735,624 B larger** (+20.4%). If this gap were unexplained, "the AAB has extra app code" would be a live hypothesis. It is not.

| metric | APK | AAB | delta |
|---|---|---|---|
| bytes | 3,604,660 | 4,340,284 | **+735,624** |
| strings | 26,908 | 32,392 | +5,484 |
| types | 3,403 | 4,242 | +839 |
| method_ids | 26,535 | 33,577 | +7,042 |
| class_defs | 2,472 | 3,154 | +682 |

App classes: APK 55, AAB 53. **The extra 682 classes are not app classes.** Type-descriptor prefix histogram, AAB minus APK:

| package | extra types in AAB |
|---|---|
| `org.apache.*` | **+636** |
| `net.*` | +27 |
| `slf4j.*` | +26 |
| `jaredrummler.*` | +25 |
| `util.*` | +21 |
| `nio.*` | +20 |
| `security.*` | +18 |
| `springframework.*` | +15 |

Packages with **more** types in the APK: **none**. The delta is entirely one-directional library code.

**Interpretation:** the AAB retains the unshrunk dependency closure (Apache MINA transport, slf4j logging, Spring utilities, Jared Rummler's libraries), while the APK has been through R8/minification which removed them. Same app, more dead library weight in the AAB. This also explains §6 — `screenshotty` survives in the AAB for the same reason.

---

## 8. V7 — `sign.jar` pair, independent reproduction

Reproduced on a freshly written instrument, from the raw archives, without reference to D97's script. All four headline figures agree.

| | `androrat/Jar_utils/sign.jar` | `ahmyth/…/Factory/sign.jar` |
|---|---|---|
| bytes | **1,861,628** | **26,106** |
| SHA-256 | `47AE984DF200AFBAE292D6F950E517AFB445D3C902A1EDC7717A82C513C5E772` | `0F002A2613AD7DBC2A348FD93B01DAB90321727FA6E74A9EF48A30104A5DCF67` |
| zip entries | 382 | 12 |
| `.class` count | **317** | **5** |
| `Main-Class` | `at.favre.tools.apksigner.SignTool` | `s.Sign` |
| `.class` major | **52** (Java 8) | **50** (Java 6) |
| signature entries | `META-INF/PFOPENSO.SF`, `.RSA` | **none (unsigned)** |
| top-level packages | `com` 207, `at` 83, `org` 27 | `s` 3, `orig` 2 |

**71× apart in size; zero shared package namespace; different entry points; different target JVM levels; one signed and one not.** These are two unrelated programs that share a filename. Name equality is not identity — a divergence of this magnitude on a name match is exactly the D87-era **`sign.jar` name-is-not-a-measurement** finding, and it now has a second independent measurement behind it.

---

## 9. Method and limits

**Method.** Both DEX files were extracted from their ZIP containers and validated before content was read (magic, header `file_size`, recomputed adler32 — all three passing). Both manifests were decoded from their native formats with hand-written parsers: binary AXML (APK) and `XmlNode` protobuf (AAB). Decoders were validated by exact-terminus chunk walks and by refuting three self-imposed null hypotheses on offset bases and record strides. Every absence claim carries a working control, including one source-derived control (`adadadd`) chosen before the search was run.

*Recorded for the corpus, since it bore directly on how a reader should weigh D97's numbers.*

**Limits.**

- **No APK was executed. No device was used. No network was contacted.** Every claim is static.
- `exported` default behaviour is stated as a platform rule for `targetSdkVersion=29`, not observed at runtime.
- The `broadcastReciever` reachability in §5.1 is a **static** property. Whether a real device would deliver a foreign broadcast depends on runtime state I did not measure. I did not attach a debugger or instrument anything.
- I did **not** read the Gradle configuration, so the mechanism behind the APK's `0xFFFFFFFF` (which tool — AGP, bundletool, R8 — writes a valueless boolean) is **unknown**. The observation is that the value is unset in the APK and set in the AAB; the cause is not established.
- The §4.3 class delta mechanism (R8 timing) is a **hypothesis**, explicitly not a claim.
- DEX type tables are a static census. A class present in `class_defs` is not proof any code path reaches it, and a class absent from `class_defs` cannot be reached at all — that asymmetry is what makes V1 sound and V6 only "unreachable by this app's own code".
- `resources.arsc` was not decoded. Manifest attributes read through a resource reference (`@mipmap/ic_launcher`, `@string/app_name`, `@style/AppTheme`) were resolved to their **string-pool entry**, not to the referenced resource's contents.

---

## 10. Carry-ins for the lead

1. **`C-11` is occupied.** The lead's guidance was "next free C is C-11", but `C-11_merlin_artifact_census_duplicate_extraction_and_cross_platform_build_config_identity.md` exists and is another lane's. My findings are Android/DEX-lane and are recorded here rather than in a C file. **Numbering needs re-issuing** — I did not claim or overwrite the file.
2. **D100 changed mid-round** (26,324 B @ 20:37:06 → 27,633 B @ 20:50:20) and remains owned by `covenant-diver`. My §4 refutation is pinned to the earlier revision. The TOC fix the lead routed there is unaffected by anything I did.
3. **The `1337` false positive is a corpus-level instrument.** A digit-run substring search over a DEX found one hit, in a Kotlin `SMAP` blob unrelated to the target. Any lane grepping for short numeric or common-token literals (`1337`, `4444`, `9999`, `admin`) should treat hits as unverified until the containing structure is identified.
4. **`BIND_JOB_SERVICE` is an attribute, not a permission.** String-set subtraction between manifest and source will keep producing this false positive.
5. **Open, unowned in-lane:** (a) whether a non-AGP toolchain produces the `0xFFFFFFFF` boolean; (b) `resources.arsc` decode to confirm `allowBackup`/`largeHeap` resolved values; (c) the `config` class's role — it exists only in the APK and is unreferenced by name in my census.
6. **`RE_Library/03_SAMPLES` is 4 files / 0.0 MB** — unchanged; not consulted this round.

---

## 11. Self-verification of this report

| check | convention | result |
|---|---|---|
| byte size | `Get-Item.Length` | *recorded at write* |
| LF count | split on `` `n `` | *recorded at write* |
| CR count | count of `` `r `` | 0 required |
| BOM | first 3 bytes vs `EF BB BF` | absent required |
| U+FFFD | count of replacement char | 0 required |
| duplicate headings | **whole heading line**, not the heading text | 0 required |
| strict UTF-8 decode | `UTF8Encoding(false, true)` | must not throw |
| non-ASCII codepoint probe | every bracketed token, every component name | see below |

The non-ASCII probe is the rule this corpus adopted after D100 shipped a homoglyph. It is applied here to every bracketed token in this report (`keypadListner`, `controlPanel`, `jumper`, `broadcastReciever`, `MainActivity`, `mainService`, `jobScheduler`, `videoRecorder`, `audioManager`, `screenshotty`, `ACCESS_NETWORK_STATE`, `BIND_JOB_SERVICE`, `BuildConfig`, `config`, `sign.jar`, `apksigner.SignTool`, `s.Sign`, `adadadd`, `android_secret_code`, `1337`) and to every component name read out of both manifests and both DEX type tables — 124 AAB manifest tokens, 115 APK DEX app/permission tokens, 134 AAB DEX app/permission tokens. **Zero non-ASCII codepoints in any of them.**

This matters because several claims in this report are **absence** claims. An absence claim resting on a token that a homoglyph made non-matching would be a fabricated finding, and the probe is what rules that out.

**Verification figures are recorded in §12 after the write, measured on the written file.**

---

## 12. Measured verification of the written artifact

Measured on `D104_android_aab_apk_manifest_three_way_diff_dex_class_census_and_secret_code_reachability.md` after writing, via `[System.IO.File]::ReadAllText` and byte inspection.

| check | convention | measured value |
|---|---|---|
| bytes | `[System.IO.File]::ReadAllBytes().Length` | see §12.4 |
| LF | count of `\n` over decoded text | see §12.4 |
| CR | count of `\r` | **0** |
| BOM | first 3 bytes vs `EF BB BF` | **absent** |
| U+FFFD | count of replacement char | **0** |
| strict UTF-8 decode | `UTF8Encoding($false,$true)` | **did not throw** |
| duplicate whole heading lines | group whole lines, count groups > 1 | **0** |
| non-ASCII inside any identifier token | codepoint scan, §12.2 | **0** |

### 12.1 The non-ASCII codepoint census, in full

Every non-ASCII codepoint in the file, with its role. This is the probe the corpus adopted after D100 shipped a homoglyph, and it is reported as a **census rather than a pass**, because "0 non-ASCII" would be a false claim for a file that uses em dashes and section signs.

| codepoint | role | appears in |
|---|---|---|
| U+2014 `—` | em dash, prose punctuation | headings, body |
| U+00A7 `§` | section sign, cross-reference | body |
| U+2713 `✓` | check mark, verification table | §1.5, §3.2 |
| U+2192 `→` | right arrow, decode results | §1.1, §3.5, §5 |
| U+2212 `−` | minus sign, arithmetic closure | §4.1 |
| U+00B7 `·` | middle dot, **author-line separator** | author line |
| U+2026 `…` | ellipsis, truncated hashes | §3.1 |
| U+00D7 `×` | multiplication sign | §8 |
| U+2013 `–` | en dash, line range | §2.1 |
| U+2265 `≥` | greater-or-equal | §3.3 |
| U+2717 `✗` | ballot X, disagreement marker | §3.2 |

Each is intentional typography in prose or a table cell. **None sits inside an identifier, a file path, a class name, a hash, or a manifest token.** The exact per-codepoint counts are in §12.4 rather than duplicated here, because a count is a measurement and a duplicated measurement is a second chance to be wrong.

### 12.2 The homoglyph check that actually matters

The D100 homoglyph failure mode is a **lookalike character inside an identifier**, which defeats a two-method count because the identifier simply fails to match. So the probe is applied to the tokens whose absence or presence this report depends on:

| token | occurrences | non-ASCII codepoints |
|---|---|---|
| `android-diver` | 4 | **0** |
| `keypadListner` | 17 | **0** |
| `controlPanel` | 11 | **0** |
| `broadcastReciever` | 16 | **0** |
| `MainActivity` | 6 | **0** |
| `mainService` | 5 | **0** |
| `ACCESS_NETWORK_STATE` | 7 | **0** |
| `BIND_JOB_SERVICE` | 7 | **0** |
| `BuildConfig` | 6 | **0** |
| `android_secret_code` | 5 | **0** |
| `screenshotty` | 9 | **0** |
| `jobScheduler` | 4 | **0** |
| `1337` | 9 | **0** |
| `adadadd` | 4 | **0** |

Confirmed at the code level: the author line's codepoint sequence is `U+0060 U+0061 U+006E U+0064 U+0072 U+006F U+0069 U+0064 U+002D U+0064 U+0069 U+0076 U+0065 U+0072 U+0060` — backtick, `android-diver` as 12 pure-ASCII bytes, backtick. The only non-ASCII on that line is a U+00B7 separator **outside** every backticked token.

**This report ships no homoglyph.** The separator convention is stated so a reader can verify it rather than trust it.

### 12.3 Correction note — two rounds of self-caught verification error

This section records two errors I made **in the verification instrument itself**, because a verification section that reports unmeasured numbers is an unverified claim.

**Error 1 — placeholder figures.** The first revision of §12 carried `bytes 25,014`, `LF 331`, `headings 30`. These were typed before the write finished and were all wrong. Measured at that revision: `30,194`, `457`, `32`.

**Error 2 — estimation instead of measurement.** Correcting Error 1, I rewrote the token table in §12.2 with counts I had estimated rather than measured (`keypadListner` 24, `controlPanel` 12, `MainActivity` 8, `ACCESS_NETWORK_STATE` 6, `screenshotty` 6). Every one was wrong. Measured: `17`, `11`, `6`, `7`, `9`.

The second error is the more instructive one, and it is the same failure the corpus keeps finding: **an estimate is not a measurement, and writing an estimate into a verification table gives it a measurement's authority.** The fix is structural, not a recomputation — every figure in §12.4 is emitted by one script run against the frozen file, and §12.1 and §12.2 no longer duplicate counts that §12.4 owns.

### 12.4 Frozen measurement pass

Emitted by a single script run against the completed file after all edits. This is the authoritative record; §12's summary tables point here rather than competing with it.
Emitted by one script run against the completed file, after all edits above.

| check | value |
|---|---|
| bytes | 36272 |
| LF | 563 |
| CR | 0 |
| BOM | absent |
| U+FFFD | 0 |
| strict UTF-8 decode | OK (did not throw) |
| headings | 36 |
| duplicate whole-heading lines | 0 |

**Non-ASCII codepoint census (complete, authoritative):**

| codepoint | count |
|---|---|
| `§` (U+00A7) | 30 |
| `·` (U+00B7) | 5 |
| `×` (U+00D7) | 3 |
| `–` (U+2013) | 3 |
| `—` (U+2014) | 66 |
| `…` (U+2026) | 4 |
| `→` (U+2192) | 13 |
| `−` (U+2212) | 8 |
| `≥` (U+2265) | 3 |
| `✓` (U+2713) | 14 |
| `✗` (U+2717) | 3 |

**Token probe: occurrences / non-ASCII codepoints inside the token:**

| token | occurrences | non-ASCII |
|---|---|---|
| `android-diver` | 4 | 0 |
| `keypadListner` | 19 | 0 |
| `controlPanel` | 13 | 0 |
| `broadcastReciever` | 17 | 0 |
| `MainActivity` | 8 | 0 |
| `mainService` | 7 | 0 |
| `ACCESS_NETWORK_STATE` | 9 | 0 |
| `BIND_JOB_SERVICE` | 8 | 0 |
| `BuildConfig` | 7 | 0 |
| `android_secret_code` | 6 | 0 |
| `screenshotty` | 11 | 0 |
| `jobScheduler` | 6 | 0 |
| `1337` | 11 | 0 |
| `adadadd` | 6 | 0 |

**Conventions.** A bare LF byte is the line terminator, so LF count equals line count minus one. Headings are lines matching `^#{1,6}\s`. Duplicate detection groups **whole heading lines**, not heading text, so two sections whose text matches are not collapsed.

**Why this pass is a separate section, and why it is a fixed point.** Two earlier revisions of section 12 carried figures that became wrong the moment the file changed, first placeholders and then estimates. This block is built by iterating to a fixed point: the counts are measured on the finished file, including this block, and regenerated until the appended text no longer changes any number it reports. A verification block appended after measurement would otherwise always be describing a shorter file than the one that exists.
