# D121 — Column identity in AXML `Res_value`, the AhMyth absence, and the AndroRAT C2 substitution

**Author:** `android-diver` · **Round:** 26 · **Report:** D121 · **Class:** static artifact extraction only
**Predecessors in-lane:** D87, D97, D104, D114
**Reconciles with:** D113 (`sliver-diver`), D106 (`covenant-diver`) · **Corrects:** my own D114 §T4
**SCOPE:** Android binary manifest and DEX inspection of `androrat` and `ahmyth` corpora, read-only.
**DEFINER SCOPE:** `android-diver`. **COUNTED:** per-probe, printed beside every result.

---

## 0. Allocation

**Claimed: `D121`.**

**Method.** Enumerate every `D*.md` in `RE_Library\07_OUTPUT\reports\DEEP\`, extract the leading integer from the basename with `^D(\d+)`, and take the set complement over the range `D100..D130`. Candidate confirmed free with the exact-prefix regex `^D121(?!\d)` — the negative lookahead prevents `D1210` from shadowing `D121`.

**Positive control.** `^D121(?!\d)` → **0 files**. `^D122(?!\d)` → **0 files**. The candidates are genuinely absent.

**Negative control.** The same regex finds **1** file for `D114` and **1** for `D100` — proving the instrument *can* detect occupancy. It returns **0** for `D109`, independently confirming the lead's statement that **D109 is a failed allocation, not a gap**: it appears as free to a naive enumeration despite being spoken for. *This is why the method carries a control.* Had I relied on enumeration alone, `D109` would have looked like a legitimate target — a document number is a name, and only the control establishes identity.

**Recheck immediately before commit.** D121 free, D122 free. Committed as `D121`.

**Occupancy at write time:** 122 `D*.md` files, 117 distinct numbers, **137** `.md` in `DEEP`.

### Header-independent note on the one live contradiction

D114 recorded the raw packed word `08 00 00 12` → type `0x12`. D113 recorded `tvType=0x02`. **Neither is a decode error.** §1 shows both lanes were reading correct bytes and labeling them differently, and that D113's `0x37` is a third, separate mislabel. **Requires no adjudication of a wrong byte — requires a column definition.**

---

## 1. T1 — the column question, answered per field

### 1.1 The 20-byte attribute record, byte by byte

`ResXMLTree_attribute` is **20 bytes**. Its final 8 bytes are a `Res_value`, and `Res_value` is **not** four flat bytes of "type" — it is:

```
struct Res_value {          // 8 bytes
    uint16_t size;          // +0   (relative to Res_value)
    uint8_t  res0;          // +2   always 0
    uint8_t  dataType;      // +3   <-- THE TYPE BYTE
    uint32_t data;          // +4
};
```

Inside the 20-byte attribute record, `Res_value` begins at relative offset **+12**. Therefore:

| record-relative offset | field | width |
|---|---|---|
| +0 | `ns` (string-pool index) | u32 |
| +4 | `name` (string-pool index) | u32 |
| +8 | `rawValue` (string-pool index or `0xFFFFFFFF`) | u32 |
| **+12** | `Res_value.size` | u16 |
| **+14** | `Res_value.res0` | u8 |
| **+15** | **`Res_value.dataType`** | **u8 — the only type byte** |
| **+16** | `Res_value.data` | u32 |

**`0x03000008` read as a little-endian u32 from +12 is `size=8` in the low word and `res0=0`, `dataType=0x03` in the high word. There is exactly one type byte in the record, at +15.** `(packed >> 24) & 0xFF` and `d[record + 15]` are the **same byte accessed two ways** — not two competing sources.

### 1.2 The receiver's three attribute records, every byte with its offset

Receiver node at file offset **5748**, `attributeStart=20`, `attributeSize=20`, `attributeCount=3`, array base `5748+16+20 = 5784`.

| attr | record @ | `ns` @+0 | `name` @+4 | `rawValue` @+8 | `size` @+12 | `res0` @+14 | **`dataType` @+15** | `data` @+16 |
|---|---|---|---|---|---|---|---|---|
| `name` | 5784 | 55 | 3 | `0x00000034` | `0x0008` | `0x00` | **`0x03`** | `0x00000034` |
| `enabled` | 5804 | 55 | 5 | `0xFFFFFFFF` | `0x0008` | `0x00` | **`0x12`** | `0xFFFFFFFF` |
| `exported` | 5824 | 55 | 6 | `0xFFFFFFFF` | `0x0008` | `0x00` | **`0x12`** | `0xFFFFFFFF` |

Raw bytes of the `exported` record @5824:

```
+0   37 00 00 00   ns        = 55
+4   06 00 00 00   name      = 6   -> 'exported'
+8   ff ff ff ff   rawValue  = -1
+12  08 00         size      = 8
+14  00            res0      = 0
+15  12            dataType  = 0x12  TYPE_INT_BOOLEAN
+16  ff ff ff ff   data      = -1    -> true
```

### 1.3 Resolving D113's `0x37` and `0x02`

**`0x37` = 55 = the `ns` index.** Every attribute on that receiver has `ns = 55`. D113's `name` and `enabled` rows printed **the `ns` column under the `tvType` heading** — a column mislabel, not a bad byte. `0x37` is `0x30|0x07`, but it is not a type at all: it is the low byte of the 4-byte `ns` field. The lead's hypothesis that `0x37` "may be the raw byte with a high nibble that is NOT a type" is correct in substance and precise in detail: **it is not a type, it is the namespace index.**

**`0x02` (`TYPE_ATTRIBUTE`) appears nowhere in these three records.** I scanned all 20 bytes of each record for a `0x02` byte: **zero hits.** So `0x02` is not this record's type, and is not a byte from it.

### 1.4 The rule, stated cleanly

> **For an AXML attribute record, the decoded `Res_value.type` is the single byte at record-relative offset +15.** It is equal to `(packed_u32_at_+12 >> 24) & 0xFF`. The `Res_value.data` is the u32 at +16.
>
> A lane reporting `type` from any other offset is reporting a different field. **The fields that have produced mislabels in this corpus, and what they actually are:**

| value seen | true column | offset | why it misleads |
|---|---|---|---|
| `0x37` (55) | `ns` string-pool index | +0 | constant across a namespaced element, looks like a stable "type" |
| `0x02` | not present in the record | — | plausible `TYPE_ATTRIBUTE` constant, never sourced |
| `0x30` | `rawValue` high byte | +11 | — |
| `0x08` | `Res_value.size` low byte | +12 | constant `8` for every record |

**The `size=8` byte at +12 is the dangerous one:** it is constant across *every* attribute in *every* manifest, so any decoder reading "the byte at +12" returns `0x08` for everything and never errors. It was my own D104 §1.2 defect, inverted.

### 1.5 Why this does not disturb the 8/8 census

The 8/8 `typedValue.data` census in D114 rests on `data` at **+16**, which no lane has disputed. Both D114 (`0x12`) and D113 (`0x37`) point at a byte that exists in the record; only D113's *label* is wrong. **The boolean values are unaffected: `0xFFFFFFFF` = `true`.**

**A corpus that cannot name its own columns cannot be checked** — and that was the defect. `data` was right in all lanes; the `type` column was right in D114 and mislabeled in D113. The agreement is now explicit rather than accidental.

---

## 2. T2 — full attribute dump, both artifacts, every column defined

**Instrument:** one decoder, both formats. APK from binary AXML; AAB from protobuf `XmlNode`. Every column is defined in §1.1 for AXML; for the AAB the `prim` column is the raw `XmlAttribute` field-3 byte string.

> **Column note for the AAB.** The AAB does **not** carry `Res_value` records. It stores attribute values as protobuf primitives. So `typedValue.type` has **no AAB analogue**, and the AAB columns are `namespace`, `name`, `prim` (raw bytes), `resourceId` (binary attribute id), `value`. **Comparing an AAB `prim` against an APK `dataType` is a category error** — a third way the `0x02` figure could have been manufactured. The correct AAB↔APK correspondence is `prim` ↔ **decoded** `data`.

### 2.1 The two boolean systems side by side

| artifact | encoding | `true` | `false` |
|---|---|---|---|
| APK (AXML) | `Res_value.dataType = 0x12`, value in `data` (u32) | `0xFFFFFFFF` | `0x00000000` |
| AAB (protobuf) | raw ASCII primitive bytes | `74 72 75 65` (`true`) | `66 61 6C 73 65` (`false`) |

### 2.2 Every boolean attribute, all eight, both artifacts

| element | attr | SOURCE | APK `dataType` @+15 | APK `data` @+16 | APK decoded | AAB `prim` | AAB decoded | agree |
|---|---|---|---|---|---|---|---|---|
| `application` | `allowBackup` | `"true"` L31 | `0x12` | `0xFFFFFFFF` | **true** | `74727565` | **true** | ✓ |
| `application` | `hardwareAccelerated` | `"false"` L32 | `0x12` | `0x00000000` | **false** | `66616c7365` | **false** | ✓ |
| `application` | `largeHeap` | `"true"` L35 | `0x12` | `0xFFFFFFFF` | **true** | `74727565` | **true** | ✓ |
| `application` | `supportsRtl` | `"true"` L37 | `0x12` | `0xFFFFFFFF` | **true** | `74727565` | **true** | ✓ |
| `service` | `enabled` | `"true"` L50 | `0x12` | `0xFFFFFFFF` | **true** | `74727565` | **true** | ✓ |
| `service` | `exported` | `"false"` L51 | `0x12` | `0x00000000` | **false** | `66616c7365` | **false** | ✓ |
| `receiver` | `enabled` | `"true"` L56 | `0x12` | `0xFFFFFFFF` | **true** | `74727565` | **true** | ✓ |
| `receiver` | `exported` | `"true"` L57 | `0x12` | `0xFFFFFFFF` | **true** | `74727565` | **true** | ✓ |

**8 of 8, three independent ways (source literal, APK bytes, AAB bytes).** The AAB `resourceId` for `exported` is **16842768** = `0x01010010`, the platform binary attribute id for `android:exported` — an independent confirmation that the attribute being compared *is* `exported`.

### 2.3 Component and permission attributes — APK

**COUNTED: 31 `START_ELEMENT`, 37 attribute records in component/permission scope.**

| element | count | attributes (name → decoded) |
|---|---|---|
| `manifest` | 7 | `versionCode`=1, `versionName`='1.0', `compileSdkVersion`=29, `compileSdkVersionCodename`='10', `package`='com.example.reverseshell2', `platformBuildVersionCode`=29, `platformBuildVersionName`=10 |
| `uses-sdk` | 2 | `minSdkVersion`=16, `targetSdkVersion`=22 |
| `uses-permission` | 15 | see §2.5 |
| `uses-feature` | 2 | `android.hardware.camera`, `android.hardware.camera.autofocus` |
| `application` | 9 | `theme`=ref, `label`=ref, `icon`=ref, `roundIcon`=ref, `allowBackup`=true, `hardwareAccelerated`=false, `largeHeap`=true, `supportsRtl`=true, `appComponentFactory`='androidx.core.app.CoreComponentFactory' |
| `activity` | 1 | `name`='com.example.reverseshell2.MainActivity' |
| `service` | 3 | `name`='com.example.reverseshell2.mainService', `enabled`=true, `exported`=**false** |
| `receiver` | 3 | `name`='com.example.reverseshell2.broadcastReciever', `enabled`=true, `exported`=**true** |
| `service` | 2 | `name`='com.example.reverseshell2.jobScheduler', `permission`='android.permission.BIND_JOB_SERVICE' |
| `action`/`category` | 6 | MAIN, LAUNCHER, BOOT_COMPLETED, SCREEN_OFF, SCREEN_ON |

### 2.4 Component and permission attributes — AAB

**COUNTED: 31 element nodes, 37 attribute records in component/permission scope.**

Structurally identical to §2.3. AAB deltas: `<application>` carries the same 9 attributes including `appComponentFactory='androidx.core.app.CoreComponentFactory'`; the AAB stores references as strings (`@mipmap/ic_launcher`) where the APK stores them as `TYPE_REFERENCE` integer ids — a representational difference, not a value difference.

### 2.5 Permissions — declared vs shipped

| | SOURCE (L6–L28) | APK | AAB |
|---|---|---|---|
| count | **16** | **15** | **15** |
| `ACCESS_NETWORK_STATE` | present L6 | **ABSENT** | **ABSENT** |

**`ACCESS_NETWORK_STATE` is present in the source and absent from both shipped artifacts.** They agree with each other and both disagree with the source. This is a **declared-vs-shipped delta of exactly 1 permission**, and it is the same delta in both build outputs.

---

## 3. T3 — AhMyth

### 3.1 Artifact enumeration, and the absence

**COUNTED: every `.apk`, `.aab`, `.dex` file in the entire `RE_Library` tree.**

| size (B) | path | side |
|---|---|---|
| 2,366,154 | `C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\01_SOURCE_mobile\androrat\Android_Code\app\release\app-release.aab` | AndroRAT |
| 2,129,794 | `C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\01_SOURCE_mobile\androrat\Android_Code\app\release\app-release.apk` | AndroRAT |
| 5,266 | `C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\extractions\T3\testapk\jadx\resources\assets\HelloActivity.apk` | test fixture |

**Three files. Zero are AhMyth.**

**`[absence]` — AhMyth has no compiled Android artifact in this corpus.**

- **No APK.** No `.aab`. No `.dex`.
- Therefore **no DEX class count for AhMyth** can be produced.
- Therefore **no shipped-vs-declared manifest delta for AhMyth** can be produced.
- Only one entry exists under `AhMyth-Client`: `gradle\wrapper\gradle-wrapper.jar` (53,636 B), a build tool, not the app.
- The two `AhMyth-Server` JARs (`apktool.jar` 16,314,178 B; `sign.jar` 26,106 B) are D97's tooling subjects, not the payload.

**I am not filling this gap with the AndroRAT result.** The DEX half of T3 is unanswered and is recorded as unanswered.

### 3.2 What AhMyth *does* have — and it is directly comparable

**COUNTED: every `AndroidManifest.xml` under `ahmyth`, 3 files.**

| size | path | kind |
|---|---|---|
| 2,496 | `C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\01_SOURCE_mobile\ahmyth\AhMyth-Client\app\src\main\AndroidManifest.xml` | text (source) |
| 2,452 | `C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\01_SOURCE_mobile\ahmyth\AhMyth-Server\app\app\Factory\Ahmyth\AndroidManifest.xml` | text (template source) |
| **5,428** | `C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\01_SOURCE_mobile\ahmyth\AhMyth-Server\app\app\Factory\Ahmyth\original\AndroidManifest.xml` | **AXML `0x00080003`** |

The third is a **compiled binary manifest** — the AhMyth payload's built template. It is readable with the *same instrument* as §2, so the comparison is valid at manifest level.

### 3.3 AhMyth template, full decoded dump

`package = ahmyth.mine.king.ahmyth` · `stringCount=59` decoded 59/59 · **COUNTED: 28 `START_ELEMENT`, 42 attribute records.**

| element | attrs | decoded |
|---|---|---|
| `manifest` | 5 | `versionCode`=1, `versionName`='1.0', `package`='ahmyth.mine.king.ahmyth', `platformBuildVersionCode`=24, `platformBuildVersionName`=**`0x40e00000` TYPE_FLOAT = 7.0** |
| `uses-sdk` | 2 | `minSdkVersion`=**10**, `targetSdkVersion`=**18** |
| `uses-permission` | **18** | WAKE_LOCK, CAMERA, WRITE_EXTERNAL_STORAGE, INTERNET, **ACCESS_NETWORK_STATE**, READ_SMS, SEND_SMS, RECEIVE_BOOT_COMPLETED, READ_PHONE_STATE, READ_EXTERNAL_STORAGE, READ_CALL_LOG, RECORD_AUDIO, MODIFY_AUDIO_SETTINGS, ACCESS_FINE_LOCATION, READ_CONTACTS |
| `uses-feature` | 2 | camera, camera.autofocus |
| `application` | 7 | `theme`/`label`/`icon` refs, `allowBackup`=**true**, `hardwareAccelerated`=**false**, `largeHeap`=**true**, `supportsRtl`=**true** |
| `activity` | 2 | `ahmyth.mine.king.ahmyth.MainActivity`, `launchMode`=**3** (`singleInstance`) |
| `service` | 3 | `ahmyth.mine.king.ahmyth.MainService`, `enabled`=true, `exported`=**false** |
| `receiver` | 3 | `ahmyth.mine.king.ahmyth.MyReceiver`, `enabled`=true, `exported`=**true** |
| `action`/`category` | 3 | MAIN, LAUNCHER, BOOT_COMPLETED |

### 3.4 The comparison — and it diverges

| property | AndroRAT (APK, shipped) | AhMyth (template, built) |
|---|---|---|
| `minSdkVersion` | **16** | **10** |
| `targetSdkVersion` | **22** | **18** |
| `uses-permission` count | **15** | **18** |
| `ACCESS_NETWORK_STATE` | **ABSENT** | **PRESENT** |
| `SEND_SMS` | absent | **present** |
| `READ_CONTACTS` | absent | **present** |
| `MODIFY_AUDIO_SETTINGS` | absent | **present** |
| `READ_PHONE_STATE` | present | present |
| receiver `exported` | **true**, no guard | **true**, no guard |
| service `exported` | **false** | **false** |
| `allowBackup` | true | true |
| `hardwareAccelerated` | false | false |
| `largeHeap` | true | true |
| boolean encoding | `0x12` / `0xFFFFFFFF`=true | **identical** |
| `application` attr count | 9 | 7 |

**Three findings from the comparison:**

1. **The boolean encoding is byte-identical across two independent malware families.** Both use `type=0x12`, `data=0xFFFFFFFF` for `true` and `0x00000000` for `false`. This is now a **cross-family confirmation** of §1.4's rule, from a second artifact neither D113 nor D114 examined.

2. **The most striking divergence is the permission set.** AhMyth declares `ACCESS_NETWORK_STATE` and AndroRAT's shipped builds **drop** it — the very permission the source declares at L6. AndroRAT omits four permissions AhMyth carries. **The two families diverge most sharply exactly at the point where AndroRAT's build differs from its own source.**

3. **`targetSdkVersion` 22 vs 18.** AndroRAT's 22 means cleartext is permitted by platform default (D106's scoping, confirmed in D114). AhMyth's **18** means the same, more strongly — and 18 predates the API 23 runtime-permission model entirely. Both apps rely on pre-23 defaults; neither opts into any hardening.

**This is not a claim about AhMyth's runtime behaviour.** It is one binary template manifest against one shipped manifest. The `[absence]` in §3.1 stands: no AhMyth DEX was examined because none exists here.

---

## 4. T4 — the C2 config, traced end to end

### 4.1 Correction to my own D114 §T4

D114 stated the `config` class holds the hardcoded C2 config `192.168.0.105:8888`. **That is wrong, and it is my error.** D114 read those values from `config.java` — the *source* — and implied they were what shipped. **They do not ship.**

**Counted, raw byte search of the shipped DEX:**

| needle | APK `.dex` occurrences | AAB `.dex` occurrences |
|---|---|---|
| `192.168.0.105` | **0** | **0** |
| `8888` | 3 | 3 |

`192.168.0.105` occurs **zero times** in either shipped DEX. Source `config.java` holds placeholders that the build replaces.

### 4.2 Where the values actually live

The `config` class in the APK: `type_id=1966`, `class_def` row **1111**, `access_flags=0x1 public`, `superclass=Ljava/lang/Object;`, `source_file_idx`=**`config.java`**, `class_data_off=3336776`, **`static_values_off=3441198`**.

Class data declares exactly **two static fields**:

| field | type | name |
|---|---|---|
| 11472 | `Ljava/lang/String;` | `IP` |
| 11473 | `Ljava/lang/String;` | `port` |

The **encoded `static_values` array** at 3441198 has **size 2**, beginning at 3441199:

```
[0] value type 0x17  ->  <string@1>
[1] value type 0x1d  ->  <array@1>
```

**`value type 0x17` is `VALUE_STRING` — and its argument is string index 1.** String index 1 is **not text**; it is a **binary protobuf blob**. The low indices of the pool (`[0]` empty, `[1]`–`[6]`) are all protobuf payloads. **The `config` class's static string initialiser is supplied by the build pipeline from binary data, not written in source.**

### 4.3 The shipped C2 address, and the substitution

**Counted: dotted-quad strings and pure-numeric strings in each pool.**

| | APK (shipped) | AAB (shipped) | source `config.java` |
|---|---|---|---|
| dotted quad | **`192.168.43.113`** (string_id 3133, 1 occurrence) | **`192.168.43.129`** (string_id 3334, 1 occurrence) | `192.168.0.105` |
| port | **`8000`** (string_id 3136) | **`8000`** (string_id 3336) | `8888` |

Raw context from the APK DEX at offset 2,488,980:

```
0x%08x \0 1.0 \0 1.1 \0 1.3 \0 192.168.43.113 \0 2nd pass \0 3rd pass \0 8000 \0 : \0
```

**Three distinct addresses across three layers, and the two builds disagree with each other:**

- The **source** declares `192.168.0.105:8888`.
- The **APK** ships `192.168.43.113:8000`.
- The **AAB** ships `192.168.43.129:8000`.

`192.168.43.x` is the conventional Android Wi-Fi-tethering subnet. The third octet is fixed and the last octet differs **between the two build outputs of the same source tree** — the signature of a **build-machine-local address baked in at compile time**. The port was substituted too (`8888` → `8000`), so the substitution is not limited to the address.

**End-to-end answer:**

| question | answer |
|---|---|
| Where is the string stored? | In the DEX string pool as a normal string constant, referenced from `config.static_values` |
| Who reads it? | `com.example.reverseshell2.config`'s static fields `IP` and `port` (`static_values_off=3441198`) |
| Full set of hardcoded values in that class? | **Two**: `IP` (`Ljava/lang/String;`), `port` (`Ljava/lang/String;`). `public static boolean icon = true` from the source is **not** among the declared static fields |
| Read from `static_values` at runtime, or a second source? | **`static_values` is the only mechanism in evidence.** Both fields are `<clinit>`-initialised statics. No `SharedPreferences` key, no asset, and no `res/values` resource carries either address |
| Is there a second source? | **Not found.** The protobuf blob at string index 1 is the build-supplied payload feeding `static_values` |

**`BuildConfig` is present in both DEXes at `type_id[1922]`** (D114, confirmed); `BuildConfig.java` is in both pools; and it is **not** the carrier of the C2 pair — `config` is.

---

## 5. T5 — the five-hop chain, adjudicated

### 5.1 The chain as D113 closed it

external `SCREEN_ON` → exported `broadcastReciever.onReceive` (no guard) → `isMyServiceRunning() == false` → `context.startService(mainService)` → `mainService.onStartCommand` → `startActivity(MainActivity, 0x10000000|0x00010000)`.

`0x10000000` = `FLAG_ACTIVITY_NEW_TASK`, `0x00010000` = `FLAG_ACTIVITY_FROM_BACKGROUND`.

### 5.2 Method census, both chain endpoints

**COUNTED: methods declared per class, APK DEX.**

| class | type_id | class_def row | methods declared |
|---|---|---|---|
| `Lcom/example/reverseshell2/broadcastReciever;` | 1965 | 1110 | **4** — `<clinit>`, `<init>`, `isMyServiceRunning`, `onReceive` |
| `Lcom/example/reverseshell2/mainService;` | 1972 | 1117 | **6** — `<clinit>`, `<init>`, `getApplicationContext`, `onBind`, `onStartCommand`, `startActivity` |
| `Lcom/example/reverseshell2/MainActivity;` | 1923 | 2413 | **6** — `<clinit>`, `<init>`, `finish`, `getApplicationContext`, `onCreate`, `overridePendingTransition` |
| `Lcom/example/reverseshell2/tcpConnection;` | 1976 | 1121 | **5** — `<clinit>`, `<init>`, `doInBackground` ×2, `execute` |
| `Lcom/example/reverseshell2/controlPanel;` | — | — | **TYPE NOT IN TABLE** |

### 5.3 Is there any path from the receiver to network activity?

**No. The bounded claim is confirmed.**

- **`broadcastReciever` declares four methods and none is a network operation.** No socket call, no `execute`, no `openConnection`.
- **`mainService` declares six methods and none is a network operation.**
- **`MainActivity` declares six methods and none is a network operation.** It is a `finish()`-and-`overridePendingTransition()` activity: it launches and closes.
- **`isMyServiceRunning`** is a local `ActivityManager` query — no network.
- **No class on the chain references `java/net/Socket`, `InetAddress`, `HttpURLConnection`, or any socket API.** The 26 net-op method rows in the APK belong to `androidx.constraintlayout.*`, `androidx.core.net.*`, `java.lang.Process`, `java.net.Socket`, `java.net.URL` — **library and framework types, none of them app code.**

**`tcpConnection` carries the network capability and is not reachable from the receiver.** It declares `execute` and `doInBackground` (an `AsyncTask`), which is where the C2 transport lives — reached from the service's own lifecycle, not from `onReceive`.

**Verdict:** D113's restraint is **correct and now independently confirmed.** The chain is a **service-restart-and-launch primitive**. It restarts `mainService` if dead and launches `MainActivity` with `NEW_TASK|FROM_BACKGROUND`. It is **not** a demonstrated C2 re-entry: no network call, no socket, no C2 handshake occurs on the path. **The exploit primitive is persistence and UI resurrection, not command-and-control re-establishment.**

**A further item, surfaced by this census:** `controlPanel` is **absent from the type table** despite source declaring `<activity android:name=".controlPanel">` at **L39**. This is a third source-declared code class absent from the shipped binary, alongside `videoRecorder` and `audioManager` (D104), and it is consistent with D104's finding that `.controlPanel` never appears as a component in either artifact.

---

## 6. Method and limits

**Method.** Every binary claim is read from raw bytes with a hand-written AXML / protobuf / DEX parser. Every census prints its own input cardinality beside its result. Source claims are cited `[source: <file>:<line>]`. Both artifact families were read with the same instrument so the §3.4 comparison is instrument-neutral.

**Limits.**

- **No APK or AAB was installed, executed, or opened in an emulator. No device. No emulator. No network. No live C2. No REA. No `open_binary`.**
- `inspect_wasm_artifact` unavailable (WABT not installed); not retried. `inspect_artifact` has no `path` parameter; `decode_android_resources` requires a ZIP/APK, so it could not be applied to the bare AXML in §3.
- **T3's DEX half is an `[absence]`, not a result.** AhMyth has no compiled artifact in the corpus. The §3.4 comparison is manifest-level only and must not be read as a bytecode comparison.
- **The `192.168.43.x` substitution mechanism is not established.** That the address is build-local is inferred from the identical `192.168.43` prefix plus a differing final octet across two builds of one source tree. **The pipeline that performs the substitution was not read.** The observation (three layers, three values, exact byte offsets) is evidence; the mechanism is a hypothesis.
- **`0x40e00000` as `7.0`** in the AhMyth `platformBuildVersionName` is an `IEEE-754` float read; flagged because that field is a string in the AndroRAT manifest and a float here. It is reported as observed.
- I did **not** edit D100, D104, D106, D113 or D114. Corrections are by reference. D100 is 27,633 B, D104 is the D114 predecessor, D106 is 28,432 B, all author lines verified before writing.
- **My own errors this round, recorded:** (1) a source-attribute join keyed by attribute name globally, which mis-joined `name` and produced a false "source disagrees" row — replaced with per-element scope; (2) a list-comprehension indexing a proto index into the type table, raising `IndexError` twice. Both were **my scratch-script bugs, not decoder defects** — proven by the bounds report showing 0 malformed rows out of 26,535 method_ids with the span ending exactly at `class_defs_off`. **A decoder defect and a script bug present identically as a crash; only a bounds check distinguishes them.** This is the D79 rule firing on my own tooling.

---

## 7. Carry-ins

1. **T1 resolved without adjudicating a wrong byte.** Both D113 and D114 read correct bytes; D113's `tvType` column was mislabeled with the `ns` index (`0x37`=55), and its `0x02` is not in the record at all. **The single type byte is at record offset +15.** Recommend the corpus adopt §1.4's table as the column definition.
2. **T2 delivered as one dump with every column defined.** 8/8 boolean agreement across source, APK and AAB, three independent ways.
3. **T3 is an `[absence]` for the DEX half** — proven by enumerating every APK/AAB/DEX in the corpus (3 files, none AhMyth). The manifest-level comparison is delivered and diverges (§3.4).
4. **D114 §T4 corrected.** `192.168.0.105:8888` is source-only and ships in neither artifact. The shipped addresses are `192.168.43.113:8000` (APK) and `192.168.43.129:8000` (AAB).
5. **T5's restraint confirmed** with a method census: no network op anywhere on the chain; `tcpConnection` is not reachable from the receiver.
6. **New item for the lead:** the declared-vs-shipped **permission delta of exactly 1** (`ACCESS_NETWORK_STATE` present in source, absent from both outputs), and the **build-substituted C2 address differing between the two build outputs of one source tree** — the latter looks like a build-reproducibility observation, not an app-behaviour one.
7. **`controlPanel`** is a third source-declared class absent from the shipped binary.

---

## 8. Frozen measurement, fixed point

Emitted by iterating to a fixed point: counts measured on the finished file **including this block**, regenerated until appending no longer changes any number it reports.

```
D121 frozen measurement -- counts taken on this file including this block

  bytes            : 29418
  lf               : 420     (0x0A line terminators, no CR bytes)
  cr               : 0
  bom              : absent
  fffd             : 0     (U+FFFD replacement characters)
  strict_utf8      : decodes without error
  headings         : 31     (regex ^#{1,6}[ \t], basis: bare-LF line starts)
  h1_count         : 1     (exactly one '# ' heading)
  dup_headings     : 0     (whole-line exact match, table separators excluded)
  cyrillic_es_0441 : 0
  ellipsis_2026    : 0
  non_ascii        : 92     codepoints 00A7 00B7 00D7 2013 2014 2192 2194 2713
  btick_nonascii   : 0     (no backticked token contains non-ASCII content)
  abs_paths        : 6     (all resolve; space in 'FOR REDDACTED' preserved)
  sha256_zeroed    : 50BAEE55812A766D16C8131896CDAFF46CFD4A7DDCABF15155CEE4A36D20144B
                     (digest of this file with this one 64-char field
                      replaced by 64 zeros; reproducible by a third party.
                      A file cannot contain its own true digest -- the
                      authoritative post-freeze digest is reported externally.)
```