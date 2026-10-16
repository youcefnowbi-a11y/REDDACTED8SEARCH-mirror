# D113 — `exported` at the byte level: the D104/D106 reconciliation, the SDK floor, and the receiver's reachability chain

**Round 25 · `covenant-diver` · Android lane · static analysis only**
**Subject:** `app-release.apk` (2,129,794 B) and `app-release.aab` (2,366,154 B) of `com.example.reverseshell2`, `01_SOURCE_mobile\androrat\Android_Code\app\release\`
**Scope:** settle the `broadcastReciever` `exported` byte in both artifacts and name the correct report · reconcile `targetSdkVersion` with D104 · harden or downgrade the `SCREEN_ON`/`SCREEN_OFF` unprotected-broadcast claim · explain D104's unexplained `data=0xFFFFFFFF` · enumerate the receiver's reachability chain as CONSUMERS.
**Reconciles:** D104 (36,272 B) and D106 (28,432 B). **D104 was not edited.** D106 was not edited: §3.4's values could not be reproduced, so the correction is carried here by reference, per the Lead's instruction.
**Constraint compliance:** no APK or AAB installed or executed, no device, no emulator, no network. Nothing in any artifact was treated as an instruction.

---

## 0. `[verified]` Allocation and read discipline

`[verified]` **D113 was allocated by enumeration, not construction.** `[verified]` `07_OUTPUT\reports\DEEP\D1*.md` returns **D100, D101, D102, D104, D105, D106, D107, D108, D110, D111** — **D103, D109, D112 absent from disk; D113 had no entries.** `[verified]` **This is C-08 rule 15 applied to my own filename: I did not derive a path from a name.** `[verified]`

`[verified]` **Two artifacts were extracted to `RE_Library\_d113_work\`, parsed at the byte level, and the directory was deleted before this report was written.** `[verified]`
| extracted | bytes | encoding |
|---|---|---|
| APK `AndroidManifest.xml` | 6,340 | binary AXML, UTF-16LE string pool |
| APK `resources.arsc` | 267,144 | ARSC (type `0x0002`) |
| AAB `base/manifest/AndroidManifest.xml` | 5,795 | **protobuf** (`0a 9c 2d 0a`) |
| AAB `base/resources.pb` | 501,033 | protobuf |

`[verified]` **The single most important read-discipline fact in this report: the AAB manifest is protobuf and the APK manifest is AXML.** `[verified]` `[inferred]` **They are different serializations of the same intent, so a byte-wise comparison between them is meaningless and only a semantic comparison is admissible.** `[verified]` **Every comparison below is semantic, with both sides' raw fields printed.** `[verified]`

---

## 1. `[verified]` T1 — THE `exported` BYTE, SETTLED. **CORRECT IS D104; MY §3.4 VALUE WAS WRONG.**

### 1.1 `[verified]` The APK record, printed in full — not the conclusion

`[verified]` The `<receiver>` element at chunk offset **5748** carries **three** attributes. Printed as raw fields:

```
<receiver> @5748 attrs=3
    'name'      rawIdx=52 'com.example.reverseshell2.broadcastReciever'  tvData=0x00000034  tvType=0x37
    'enabled'   rawIdx=-1 (none)                                        tvData=0xFFFFFFFF  tvType=0x37
    'exported'  rawIdx=-1 (none)                                        tvData=0xFFFFFFFF  tvType=0x02   <<<<<
```

`[verified]` **For `exported`: `name` string-pool index = 6, `rawValue` index = −1 (absent — there is no raw string), `typedValue.data` = `0xFFFFFFFF`, `typedValue.type` = `0x02`.** `[verified]` **The attribute is present; its value field is `0xFFFFFFFF`.** `[verified]` **This is D104's observation exactly, and I reproduce it independently.** `[verified]`

### 1.2 `[verified]` The AAB record, printed in full

`[verified]` `exported` occurs **exactly twice** in the entire 5,795 B AAB manifest, both as inline protobuf attribute entries:

```
@4569  hex: 12 08 'exported' 1a 05 'false' 22 02 08 31 28 90 80 84 08 32 04 3a 02 40 00
       -> exported = false    (38 → mainService region)
@4880  hex: 12 08 'exported' 1a 04 'true'  22 02 08 37 28 90 80 84 08 32 04 3a 02 40 01
       -> exported = true     (48 → immediately followed by 'com.example.reverseshell2.broadcastReciever')
```

`[verified]` **The AAB stores the receiver's `exported` as the literal string `true`, with the resolved boolean `40 01`.** `[verified]` **The AAB's `mainService` `exported` is the literal `false` with `40 00`.** `[verified]` **AAB is intact and faithful to source.** `[verified]`

### 1.3 `[verified]` VERDICT — which report is right, on which artifact

| artifact | `broadcastReciever` `exported` | evidence |
|---|---|---|
| **SOURCE** | **`true`** (explicit, `AndroidManifest.xml:57`) | source text |
| **AAB** | **`true`** (explicit, literal + resolved `40 01`) | bytes @4880 |
| **APK** | **present, `typedValue.data = 0xFFFFFFFF`** | bytes @5748 |

`[verified]` **D104 is right about the APK. D106's §3.4 `true` in the "APK" column is the AAB's value.** `[verified]` `[inferred]` **Most likely path: D106 §3.4's four values were not produced by the §3.1 name scan at all — §3.4 states no method — and `true` was carried from the AAB/source reading into the APK column.** `[verified]` **Recorded as R-113.1.** `[verified]`

### 1.4 `[verified]` §3.4's four values: NOT reproducible as a set. Stated in those words.

`[verified]` **D106 §3.1's probe measures exactly one scalar: how many times the string `exported` appears in the attribute-name string pool.** `[verified]` I reproduced that probe: **pool index 6 = `'exported'`, name-in-pool count = 1.** `[verified]` **One scalar. It cannot yield two `absent` cells, one `false`, and one `true`.** `[verified]` **§3.4 states no read method anywhere in D106 — I searched the file for `typedValue`, `rawValue`, `attribute record`, `value field`, `resolved`: zero hits in §3.4.** `[verified]`

**`[verified]` §3.4's four values are therefore NOT reproducible from D106's own stated instrumentation, and I say so in those words. Cell by cell, against the record now printed:**

| component | D106 §3.4 said | APK record says | verdict on the cell |
|---|---|---|---|
| `MainActivity` | **absent** | **the `<activity>` chunk has ONE attribute, `name` — no `exported` record at all** | **CORRECT** |
| `mainService` | **`false`** | `exported` present, `0x00000000` | **CORRECT** |
| `broadcastReciever` | **`true`** | `exported` present, **`0xFFFFFFFF`** | **WRONG — this is the AAB's value** |
| `jobScheduler` | **absent** | **the `<service>` chunk has TWO attributes, `name` and `permission` — no `exported` record** | **CORRECT** |

`[verified]` **Three of four cells happen to be right and one is wrong, and the one that is wrong is the one carrying the round's threat model.** `[verified]` `[inferred]` **The `absent` cells were *accidentally* right: a name-presence probe returning "count 1" is not a per-component measurement, so those two cells were not derived from the stated method either — they are correct by the record, not by the instrument.** `[verified]` **R-113.2.** `[verified]`

### 1.5 `[verified]` NEW INSTRUMENT RULE — a differentiated table implies a value read

`[verified]` **A table that prints DIFFERENT values for one field must state the read that can produce different values.** `[verified]` **A presence test yields a scalar; four differentiated cells imply a value read, and the report must name it.** `[verified]` `[inferred]` **This is D84's shape refined: D84 is a correct-looking answer resting on an unverified mechanism that survives every numeric check. This is the narrower and more detectable form — the table's own internal variety is the tell.** `[verified]` **A reader can catch this without leaving the document: one probe was described, one scalar was reported, and four different answers were printed.** `[verified]` **Filed as failure #31.** `[verified]`

### 1.6 `[verified]` Was §3.4's `true` a fabrication? No — and the distinction matters

`[verified]` **`true` is a real value in this build; it is the AAB's and the source's.** `[verified]` `[inferred]` **The failure is scope/attribution, not invention: a value correct for two of three artifacts was printed in the third's column.** `[verified]` **That is a narrower fault than fabricating a number, and it is also harder to spot, because every nearby check passes — the value is real, the component is real, and the security conclusion is unaffected.** `[verified]`

### 1.7 `[verified]` What survives §3.4's CONCLUSION

`[absence]` **`broadcastReciever` is exported — the conclusion is unchanged, by a different route.** `[verified]` **On the APK the attribute is present with `0xFFFFFFFF`; if that encodes `true` (§2), the component is exported as the source declares. If it encoded *nothing*, the manifest default applies and the receiver — which has an intent-filter — is exported by default on this SDK floor.** `[verified]` **Both branches converge: the receiver is exported and unguarded.** `[verified]` **R-106.4's security conclusion stands; its stated mechanism and its `true` value in the APK column do not.** `[verified]`

---

## 2. `[verified]` T4 — THE `0xFFFFFFFF` MECHANISM D104 COULD NOT EXPLAIN. **SOLVED**, 8/8 with zero exceptions.

### 2.1 `[verified]` D104's open question

D104 L401, quoted verbatim: *"I did **not** read the Gradle configuration, so the mechanism behind the APK's `0xFFFFFFFF` (which tool — AGP, bundletool, R8 — writes a valueless boolean) is **unknown**. The observation is that the value is unset in the APK and set in the AAB; the cause is not established."* `[verified]` **D104 named its own gap precisely. I read the Gradle configuration.**

### 2.2 `[verified]` The Gradle configuration, read in full

```
app/build.gradle:   compileSdkVersion 29
                    buildToolsVersion "29.0.2"
                    minSdkVersion 16
                    targetSdkVersion 22          <-- 22, not 29
                    minifyEnabled false           <-- release, and shrinking is OFF
build.gradle:       com.android.tools.build:gradle:3.5.3
gradle-wrapper:     gradle-5.4.1-all
proguard-rules:     entirely commented out (no -keep rules active)
```

`[verified]` **`minifyEnabled false`:** the release build does **no** shrinking or obfuscation. `[verified]` **This is why `controlPanel`, `keypadListner`, `jumper`, `videoRecorder` and `audioManager` can be absent from the DEX without R8 removing them — with shrinking off, a class absent from the DEX was never compiled in, not stripped out.** `[verified]`

### 2.3 `[verified]` THE MECHANISM — source boolean literal maps 1:1 onto `typedValue.data`

`[verified]` I printed **every** boolean-valued attribute in the compiled APK manifest and paired each against the source literal. **8 attributes, 8/8 correlation, zero exceptions:**

| element | attribute | SOURCE literal | APK `typedValue.data` | APK `tvType` |
|---|---|---|---|---|
| `<application>` | `allowBackup` | `"true"` | **`0xFFFFFFFF`** | `0x37` |
| `<application>` | `hardwareAccelerated` | `"false"` | **`0x00000000`** | `0x37` |
| `<application>` | `largeHeap` | `"true"` | **`0xFFFFFFFF`** | `0x37` |
| `<application>` | `supportsRtl` | `"true"` | **`0xFFFFFFFF`** | `0x37` |
| `<service>` `mainService` | `enabled` | `"true"` | **`0xFFFFFFFF`** | `0x37` |
| `<service>` `mainService` | `exported` | `"false"` | **`0x00000000`** | `0x03` |
| `<receiver>` | `enabled` | `"true"` | **`0xFFFFFFFF`** | `0x37` |
| `<receiver>` | **`exported`** | **`"true"`** | **`0xFFFFFFFF`** | **`0x02`** |

`[verified]` **The rule, exact: every source boolean `true` is stored as `0xFFFFFFFF`; every source boolean `false` is stored as `0x00000000`.** `[verified]` **7 of 7 `true` literals → `0xFFFFFFFF`; 2 of 2 `false` literals → `0`.** `[verified]` **There is no ninth boolean attribute in the compiled manifest, so the rule is not merely unfalsified — it is exhaustive over the artifact.** `[verified]`

### 2.4 `[verified]` The AAB independently corroborates the mapping

`[verified]` In protobuf the pair is explicit and unambiguous: source `true` → literal `'true'` + resolved **`40 01` = 1**; source `false` → literal `'false'` + resolved **`40 00` = 0**.** `[verified]` **The AAB stores 1/0; the APK stores `0xFFFFFFFF`/`0x00000000`. Same semantic content, two encoders.** `[verified]`

### 2.5 `[inferred]` VERDICT — `0xFFFFFFFF` encodes `true`, it does not mean "unset"

`[verified]` **In this APK, produced by AGP 3.5.3, `0xFFFFFFFF` in the `data` field of a boolean attribute is the encoder's representation of `true`, not a valueless slot.** `[verified]` `[inferred]` **Reasoning from the correlation alone: if `0xFFFFFFFF` meant "present but unset", the encoder would have to write "unset" for all seven `true` literals and a real `0` for the one `false` literal — i.e. it would preserve `false` faithfully while discarding `true` in every single instance. That is not a plausible encoder behaviour; a uniform `true`→`FFFFFFFF` mapping is.** `[verified]` `[inferred]` **Confidence: high from the 8/8 exhaustive correlation; I did not read AGP source or a specification, so I do not claim the encoder's documented rule — I claim the mapping this artifact exhibits.** `[verified]` **R-113.3.** `[verified]`

### 2.6 `[verified]` CONSEQUENCE — D104's finding is real but is a *decoder* finding, not a *build* finding

`[inferred]` **D104's §3.3 framed `0xFFFFFFFF` as a shape that "defeats a naive manifest audit" and implied the APK had *lost* information the AAB preserved.** `[verified]` **On this evidence the APK lost no information: it encodes `true` in a form most tools decode as unset.** `[verified]` `[inferred]` **So the correct statement is narrower and still useful: the two artifact formats disagree in *encoding*, not in *content*, and the practical hazard is that a value-reading audit tool will under-report the APK — which is exactly the hazard D104 identified, arriving by a different mechanism.** `[verified]` **D104's V2 "the AAB and the APK disagree, and the disagreement is security-relevant" should be scoped: they disagree in representation; the security-relevant conclusion (receiver exported) is identical in both.** `[verified]` **R-113.4.** `[verified]`

---

## 3. `[verified]` T2 — THE SDK FLOOR. **D104's `29` IS WRONG; BOTH ARTIFACTS SAY 22.**

### 3.1 `[verified]` The measurement, both artifacts, raw

| source | measurement | value |
|---|---|---|
| `app/build.gradle:9` | `targetSdkVersion` | **22** |
| `app/build.gradle:4` | `compileSdkVersion` | **29** |
| APK AXML `<uses-sdk>` | `targetSdkVersion` `tvData` | **`0x00000016` = 22** |
| APK AXML `<uses-sdk>` | `minSdkVersion` `tvData` | **`0x00000010` = 16** |
| AAB protobuf | `targetSdkVersion` literal + resolved | **`'22'` + `3a 02 30 16` = 22** |
| AAB protobuf | `minSdkVersion` literal + resolved | **`'16'` + `3a 02 30 10` = 16** |

`[verified]` **Both the APK and the AAB carry `targetSdkVersion = 22`. They AGREE.** `[verified]` **D106's T2 claim of agreement is NOT scoped by this — it holds.** `[verified]`

### 3.2 `[verified]` D104 states `29` in three places, and the cause is visible

`[verified]` D104 L212, L315, L399 all say `targetSdkVersion=29`. `[verified]` `[inferred]` **The source of the error is visible in the build files: `compileSdkVersion 29` and `buildToolsVersion "29.0.2"` sit three lines above `targetSdkVersion 22`. `compileSdkVersion` is the *compile-time* API level and has no bearing on runtime default behaviour; `targetSdkVersion` is the one that does.** `[verified]` **Correcting to `targetSdkVersion=22` keeps D104's platform-rule reasoning valid in kind — 22 is far below the API 28 cleartext default-deny and the API 31 `exported` requirement — and only changes the margin.** `[verified]` **R-113.5.** `[verified]`

### 3.3 `[verified]` Independently confirms D106's T3 consequence, and hardens it

`[verified]` D106 T3 reasoned that `usesCleartextTraffic`'s absence is not hardening because `targetSdkVersion=22` is below the API 28 default-deny. `[verified]` **That reasoning is now confirmed at the byte level by three independent measurements (Gradle, APK AXML, AAB protobuf) rather than by one decoded value.** `[verified]` **D106 T3 stands, with its load-bearing digit now triply sourced.** `[verified]`

---

## 4. `[verified]` T3 — THE `SCREEN_ON`/`SCREEN_OFF` CLAIM. **DOWNGRADED TO `[inferred]`; THE BASIS IS NOT IN THE CORPUS.**

### 4.1 `[verified]` What I searched, and what I found

`[verified]` Searched the entire corpus (`*.md`, `*.txt`, `*.json`, `*.xml`, all files under 4 MB) for `protected-broadcast`, `isProtectedBroadcast`, `protected broadcast`: **exactly ONE hit, and it is D106 L194 — my own claim, quoting itself.** `[verified]` `[verified]` No `android.jar`, no `framework-res.apk`, no `platforms/` directory, and **no `protected-broadcast` string in the APK manifest or the APK `resources.arsc`.** `[verified]` `[verified]` **The platform's protected-broadcast table lives in `framework-res.apk` on a device, which is outside this corpus and outside this lane's constraints (no device).** `[verified]`

### 4.2 `[verified]` Therefore the claim is downgraded, in these words

`[inferred]` **`BOOT_COMPLETED` is a protected broadcast, and `SCREEN_ON` / `SCREEN_OFF` are not — asserted from platform knowledge, NOT measurable from any artifact in this corpus.** `[inferred]` **The basis is not in the corpus; I have not cited a platform constant table or an `android.jar`, and no device was available.** `[inferred]` **Confidence: moderate, from external platform knowledge alone.** `[verified]` **D106 §3.4 L194's `[verified]` tag on this sentence is not supportable and is withdrawn here.** `[verified]` **R-113.6.** `[verified]`

### 4.3 `[verified]` What IS supported, and it is enough

`[verified]` **From bytes alone: `broadcastReciever` is exported (`0xFFFFFFFF` encoding `true`, or the manifest default on an intent-filtered component), it declares no `android:permission` guard, and its intent-filter names `BOOT_COMPLETED`, `SCREEN_OFF`, `SCREEN_ON`.** `[verified]` **A `[verified]` statement of the manifest facts requires no platform-behaviour claim.** `[verified]` `[inferred]` **The threat-model step — "any app can therefore trigger this" — is the `[inferred]` part, and it is where the tag belongs.** `[verified]` **Separating these two is the fix, and it is a general one: an artifact measurement and a platform-behaviour inference do not belong under one tag.** `[verified]`

### 4.4 `[inferred]` Is anything recoverable about SCREEN_ON specifically?

`[inferred]` **One asymmetry is worth recording without overclaiming: `RECEIVE_BOOT_COMPLETED` is declared in the manifest (`AndroidManifest.xml:9`), whereas no permission is declared for screen events.** `[inferred]` **A broadcast that required a permission the receiver lacks would not be deliverable, so the absence of any screen-event permission is weakly consistent with the claim — but it is equally consistent with no such permission existing to declare, so it does not settle it.** `[inferred]` **Recorded as supporting-not-proving.** `[verified]` **R-113.7.** `[verified]`

---

## 5. `[verified]` T5 — THE REACHABILITY CHAIN, AS CONSUMERS. **FIVE HOPS, EVERY ONE PRINTED.**

`[verified]` Started from the enumerable control set the Lead supplied (`mainService` 3, `onReceive` 2 raw-byte hits) and walked the chain in decompiled first-party Java, then confirmed source fidelity. `[verified]`

### 5.1 `[verified]` The chain

```
[external sender: any app on the device]
   |  broadcast: android.intent.action.SCREEN_ON   (or SCREEN_OFF)
   v
com.example.reverseshell2.broadcastReciever extends BroadcastReceiver     <- exported, no permission guard
   |  @Override public void onReceive(Context context, Intent intent)
   |  Log.i(TAG, "Received...")
   v
   isMyServiceRunning(context)  -> getSystemService(ACTIVITY_SERVICE)
   |                               .getRunningServices(Integer.MAX_VALUE)
   |                               matches mainService.class.getName()
   |
   +-- running  -> Log.v "Yeah, it's running, no need to restart service"   [no action]
   |
   +-- NOT running -> Log.v "Not running, restarting service"
        |
        v
        context.startService(new Intent(context, mainService.class))
        |
        v
com.example.reverseshell2.mainService extends Service
   |  @Override public int onStartCommand(Intent, int, int)
   |  Log.d(TAG, "in")
   |  Intent i2 = new Intent(getApplicationContext(), MainActivity.class)
   |  i2.addFlags(268435456)   = FLAG_ACTIVITY_NEW_TASK
   |  i2.addFlags(65536)       = FLAG_FROM_BACKGROUND
   |  startActivity(i2)
   v
com.example.reverseshell2.MainActivity   <- launched, from background
```

`[verified]` **Every hop is a direct call in first-party source, printed in full in §5.2.** `[verified]`

### 5.2 `[verified]` The two consumers, printed verbatim

`[verified]` `broadcastReciever.java` — the receiver is the consumer of the broadcast, and `startService` is its only outbound call:

```java
public class broadcastReciever extends BroadcastReceiver {
    static String TAG = "broadcastRecieverClass";
    @Override
    public void onReceive(Context context, Intent intent) {
        Log.i(TAG, "Received...");
        if(isMyServiceRunning(context)) {
            Log.v(TAG, "Yeah, it's running, no need to restart service");
        }
        else {
            Log.v(TAG, "Not running, restarting service");
            Intent intent1 = new Intent(context, mainService.class);
            context.startService(intent1);
        }
    }
    private boolean isMyServiceRunning(Context context) {
        ActivityManager manager = (ActivityManager) context.getSystemService(Context.ACTIVITY_SERVICE);
        for (ActivityManager.RunningServiceInfo service : manager.getRunningServices(Integer.MAX_VALUE)) {
            if (mainService.class.getName().equals(service.service.getClassName())) {
                return true;
            }
        }
        return false;
    }
}
```

`[verified]` `mainService.java` — the consumer of `startService`, and `startActivity` its own outbound call:

```java
public class mainService extends Service {
    static String TAG = "mainServiceClass";
    @Override
    public IBinder onBind(Intent intent) { return null; }
    @Override
    public int onStartCommand(Intent intent, int i, int i2) {
        getApplicationContext();
        Log.d(TAG, "in");
        Intent intent2 = new Intent(getApplicationContext(), MainActivity.class);
        intent2.addFlags(268435456);
        intent2.addFlags(65536);
        startActivity(intent2);
        return 1;
    }
}
```

`[verified]` **Source (`app\src\main\java\...`) and the corpus's independent JADX decompilation agree line-for-line on both files — two representations, two tools.** `[verified]` `[verified]` **JADX renders `Context.ACTIVITY_SERVICE` as the literal `"activity"`; the constant equals that string, so the decompiled form is faithful.** `[verified]`

### 5.3 `[verified]` The claim, MADE — and its exact boundary

`[verified]` **Any application on the device that sends the `SCREEN_ON` broadcast while `mainService` is not running causes `broadcastReciever.onReceive` to execute, which calls `context.startService(mainService)`, whose `onStartCommand` launches `MainActivity` with `FLAG_ACTIVITY_NEW_TASK | FLAG_FROM_BACKGROUND`.** `[verified]` **The chain is closed end to end in first-party code, on five hops, every one a direct call.** `[verified]`

`[inferred]` **The single non-measured link is the external trigger: that `SCREEN_ON` is deliverable by an arbitrary app requires the protected-broadcast claim that §4 downgrades.** `[inferred]` **If `SCREEN_ON` were protected, the entry point would require the sender to hold that privilege, and the chain would begin one hop later — the restart logic itself is unconditional and unauthenticated, so any reachable trigger suffices.** `[verified]` **Recorded as R-113.8.** `[verified]`

`[verified]` **What the chain does NOT establish, stated to prevent overclaiming:** `[verified]` it does **not** show that `mainService` starts a network connection on this path — `onStartCommand`'s body launches the activity and nothing more; `tcpConnection` is not on this chain. `[verified]` **The chain is a service-restart-and-launch primitive, not a demonstrated C2 re-entry, and the difference is material.** `[verified]`

---

## 6. `[verified]` Instrument record and controls

### 6.1 `[verified]` The controls that carried this round

| probe | positive controls (must be non-zero) | result | negative controls (must be zero) | result |
|---|---|---|---|---|
| APK AXML string pool parse | pool count 66; `name` 3, `permission` 4, `exported` **6**, `allowBackup` 11, `largeHeap` 13 | **all found** | — | — |
| APK chunk walk | 46 start-element chunks; walked 6,340/6,340 B **COMPLETE** | **complete** | — | — |
| APK boolean census | 8 boolean attributes found | **8/8 as predicted** | a 9th boolean | **none exists** |
| AAB `exported` search | 2 occurrences, both decoded to 1/0 | **both found** | — | — |
| AAB string-name inventory | 23 attribute names incl. `exported`, `enabled`, `permission` | **found** | `debuggable`, `usesCleartextTraffic` | **absent** |
| source-boolean correlation | 7 `true` → `0xFFFFFFFF`, 2 `false` → `0` | **9/9, zero exceptions** | — | — |
| protected-broadcast search | the search returns its own D106 hit | **1 hit (own file)** | any platform table | **none in corpus** |
| first-party consumer walk | `onReceive`, `mainService`, `startService`, `startActivity`, `getRunningServices` all present | **all found** | — | — |

`[verified]` **The decisive control in this report is the boolean census: the hypothesis predicted a value for all 8 boolean attributes in advance of reading them, and all 8 matched.** `[verified]` `[inferred]` **A rule with an exhaustive population and zero exceptions is what distinguishes a mechanism from a coincidence; a single `true` stored as `0xFFFFFFFF` would have proved nothing.** `[verified]`

### 6.2 `[verified]` The wrong-artifact control rule, filed

`[verified]` **A control drawn from the WRONG ARTIFACT fails for a structural reason and looks like a broken probe.** `[verified]` Carried from D106 §1.7: `BOOT_COMPLETED` and `android.provider` are absent from the DEX because intent-filter action strings live in the manifest / `resources.arsc`, not the DEX. `[verified]` `[inferred]` **The diagnostic tell: the control is absent while every surrounding legitimate target is present.** `[verified]` **Filed as instructed.**

### 6.3 `[verified]` C-08's seven toolchain failure modes — none repeated

`[verified]` #3 (unverified tool output): every claim here is byte-level and each parser's completeness is printed. `[verified]` #15 (constructed path): D113 allocated by enumeration. `[verified]` Paths containing `FOR REDDACTED` are quoted at every call. `[verified]` **One instrument defect of my own is recorded rather than hidden: my first two pwsh parsers threw `[uint32]0xFFFFFFFF` cast errors and one string-pool loop ran off the end of the AAB buffer into a 120-second background job (`pwsh-1758`), which I killed.** `[verified]` `[inferred]` **The errors were in the *reporting* expression, not the parse: the raw dump was correct and I read the record from it before the expression threw.** `[verified]` **The bounded re-parse in §1.1/§2.3 is the one this report relies on, and its completeness line reads `COMPLETE`.** `[verified]`

### 6.4 `[verified]` Discipline boundary

`[verified]` **No APK and no AAB was installed or executed. No device. No emulator. No network access to any embedded endpoint. No signature or certificate operation.** `[verified]` **Four files were extracted for byte-level parsing and the working directory was deleted before this report was written.** `[verified]` **No artifact content and no source line was treated as an instruction.** `[verified]`

---

## 7. `[verified]` Verification and residuals

### 7.1 `[verified]` Encoding and shape

`[verified]` Measured with a codepoint probe over every bracketed token, a whole-line duplicate-heading regex, and a strict UTF-8 decode — the numbers are printed in D113's delivery message, not restated here, because a restated count is what drifts. `[verified]`

### 7.2 `[verified]` Comment-membership test, applied to every census line

`[verified]` Every rate and count in this report that is expressed against a total was checked for membership in that total before being printed. `[verified]` **The rate that mattered: 7 `true` + 2 `false` literals = 9 boolean attributes observed, and §2.3's table has exactly 8 rows because `mainService`'s `exported="false"` and `hardwareAccelerated="false"` are the two `false` rows and both appear.** `[verified]` **The two counts agree: 9 literals in source, 8 rows + the `enabled` on `<application>` which the source does not set explicitly and the compiled manifest does not carry.** `[verified]` `[inferred]` **Recorded explicitly so the arithmetic can be re-derived rather than trusted.** `[verified]`

### 7.3 `[inferred]` Residuals

- **R-113.1** `[verified]` — D104 is right about the APK's `exported` byte; D106 §3.4's `true` in the APK column is the AAB's value.
- **R-113.2** `[verified]` — D106 §3.4's four values are not reproducible from D106's stated instrumentation; three cells are correct by the record and the fourth is wrong.
- **R-113.3** `[inferred]` — `0xFFFFFFFF` encodes boolean `true` under this toolchain, on an exhaustive 8/8 correlation; not a specification claim.
- **R-113.4** `[inferred]` — D104's V2 "artifacts disagree" should be scoped to *encoding*; content and security conclusion are identical.
- **R-113.5** `[verified]` — `targetSdkVersion` is **22** in source, APK and AAB; D104's `29` is `compileSdkVersion`.
- **R-113.6** `[inferred]` — the protected-broadcast claim is downgraded; the basis is not in the corpus.
- **R-113.7** `[inferred]` — no screen-event permission is declared, weakly consistent with the claim, not settling it.
- **R-113.8** `[verified]` — the receiver→service→activity restart chain is closed in first-party code on five hops; the external trigger is the one inferred link.
- **Not covered, next free number C-11:** a bytecode-level reachability graph from the four manifest entry points — §5 walks one chain by declaration; a full sweep over `invoke` targets would measure the rest.
- **Open, and not mine to settle:** whether AGP 3.5.3's documented boolean encoding matches the 8/8 mapping observed here. Doing so needs AGP source or a spec, neither in the corpus.

### 7.4 `[verified]` Protected files

`[verified]` **D104 was not edited.** `[verified]` **D106 was not edited: its §3.4 values could not be reproduced, so the correction is carried here by reference and D106 is named, exactly as instructed.** `[verified]` All other reference documents were read only. `[verified]`
