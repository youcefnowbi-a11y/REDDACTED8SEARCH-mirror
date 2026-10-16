# D87 — The floor is not debug-specific; a guard for the offset basis; R-68.1 closed without network

**Scope owner:** android-diver
**Deliverable:** T1 (R-79.1/2/3 — decode the release APK and AAB manifests) + T2 (the offset-basis guard as a reusable checklist) + T3 (R-68.1 re-examined)
**Method:** hand-written decoders for **two different binary manifest encodings**; git object-database enumeration; direct file reads.
**Constraints honoured:** no REA `open_binary`, no execution, no network, no builds. **All paths quoted** — the workspace root contains a space.
**Protected and untouched:** D37, D43, D49, D53, D64, D68, D79. Corrections below name the old file in place.
**Line-count convention:** LF count, `[System.IO.File]::ReadAllText(...) -split "\`n"` count. **Stated because D79 and D87 must be counted the same way to be comparable.**

---

## §0 — The headline

**T1 answers the one provenance question D79 §1.6 left open, and the answer is that the claim's scope WIDENS:**

```
artifact                                    minSdk   targetSdk   encoding
Compiled_apk\original\AndroidManifest.xml     16        22        binary AXML (UTF-16 pool)   [CN=Android Debug]
app-release.apk :: AndroidManifest.xml        16        22        binary AXML (UTF-16 pool)   [CN=karma]
app-release.aab :: base/manifest/...xml       16        22        PROTOBUF (aapt2 proto)      [CN=karma]
```

> **All three artifacts declare `minSdkVersion=16`, `targetSdkVersion=22`.**
> **D79 §1.6's conclusion — "the floor is inherited state the builder is unaware of" — is NOT debug-build-specific. It holds for the release APK and the release AAB.**

**And the release APK/AAB are not even the same *encoding* as the debug tree, which is the finding that matters more than the numbers.** The AAB manifest is **protobuf, not AXML at all** — a different container entirely — and it still declares the same floor. **The floor survives a change of manifest format, which rules out "the value is an artifact of the AXML encoder" as an explanation.**

**T3 closes R-68.1 without network, and the answer is an absence.** **The `CN=Android Debug` APK is not in the git object database** — I enumerated **all 3,270 blobs** and **all five zip-magic blobs**, and attributed every one to a path.

---

## §1 — T1: the release APK

### 1.1 Enumeration first — Rule 20, before any decode

**I did not construct the entry path. I enumerated every entry matching `manifest`:**

```
app-release.apk  (2,129,794 B)   AndroidManifest.xml        6,340 B   <- decode target
                                 META-INF/MANIFEST.MF      75,578 B
app-release.aab  (2,366,154 B)   base/manifest/AndroidManifest.xml  5,795 B   <- decode target
                                 META-INF/MANIFEST.MF      96,200 B
```

**Both manifests differ in size from the debug build's 7,700 B** — `6,340` and `5,795`. **That was the first signal that these are not the same file, and it is why I decoded rather than inferred.**

### 1.2 `app-release.apk :: AndroidManifest.xml` — binary AXML, same instrument

```
pool: count=66  flags=0x0 (UTF-16)   GUARD-A 66/66 in-range
GUARD-B walk exhausted at 6340 == chunkSize 6340

<manifest>  @3476
  versionCode                 dataType=0x10  rawIdx= -1  value=1
  versionName                 dataType=0x03  rawIdx= 19  value=1.0
  compileSdkVersion           dataType=0x10  rawIdx= -1  value=29
  compileSdkVersionCodename   dataType=0x03  rawIdx= 20  value=10
  package                     dataType=0x03  rawIdx= 50  value=com.example.reverseshell2
  platformBuildVersionCode    dataType=0x10  rawIdx= -1  value=29
  platformBuildVersionName    dataType=0x10  rawIdx= -1  value=10

<uses-sdk>
  minSdkVersion               dataType=0x10  rawIdx= -1  value=16
  targetSdkVersion            dataType=0x10  rawIdx= -1  value=22
```

**Both `rawIdx=-1` again — DECLARED, not defaulted, exactly as in the debug build.** **Pool is 66 strings (debug: 78), same `flags=0x0` UTF-16 mode, same attribute base `off+16+attrStart`, same `attrSize=20`.** **[read]**

**A separate, independent observation worth recording:** the release manifest's element chain is **structurally 16 bytes longer per element** than the debug build's because it carries **`resourceId`-bearing attributes** — the release APK went through a full `aapt2 link`, the debug tree did not. **Same values, different producer.** **[inferred from offsets]**

### 1.3 `app-release.aab :: base/manifest/AndroidManifest.xml` — NOT AXML

**The first two bytes are `0a 9c`, not `03 00`.** My AXML decoder **refused the file** rather than producing output:

```
magic=0a9c   root chunkSize=1627851321   pool count=1886680168   flags=0x656863
```

**Those numbers are nonsense, and the decoder rejected it** — `1627851321` is not a plausible chunk size and `1886680168` (= `0x70736568`, ASCII `hse p` reversed) is not a string count. **This is the guard working: the file did not match the AXML contract, so it failed instead of emitting a plausible garbage table.**

**An AAB stores the manifest as `aapt2 proto` protobuf** (`Resources.XmlNode` / `XmlElement` / `XmlAttribute` / `Item.Primitive`), not as binary XML. **[verified by schema fit]**

### 1.4 The protobuf decode — and why it took four attempts

**The schema, as I finally established it by reading the field structure rather than assuming it:**

```
XmlNode    { XmlElement element = 1; string text = 2; }
XmlElement { XmlNamespace decl = 1; string ns_uri = 2; string name = 3;
             repeated XmlAttribute attribute = 4; repeated XmlNode child = 5; }
XmlAttribute { string ns_uri = 1; string name = 2; string rawValue = 3;
               uint32 resource_id = 5; Item compiled_item = 6; }
Item       { Primitive prim = 7; }        <- FIELD 7, not field 1
Primitive  { int32 type = 1; uint32 data = 6; }
```

**Result:**
```
<manifest>
  package                     ns=(none)   raw='com.example.reverseshell2'
  versionCode                 ns=android  raw='1'      resId=0x101021b  Primitive.data=1
  versionName                 ns=android  raw='1.0'    resId=0x101021c
  compileSdkVersion           ns=android  raw='29'     resId=0x1010572  Primitive.data=29
  platformBuildVersionCode    ns=(none)   raw='29'
  compileSdkVersionCodename   ns=android  raw='10'     resId=0x1010573
  platformBuildVersionName    ns=(none)   raw='10'

<uses-sdk>
  minSdkVersion               ns=android  raw='16'     resId=0x101020c  Primitive.data=16
  targetSdkVersion            ns=android  raw='22'     resId=0x1010270  Primitive.data=22
```

> **`minSdkVersion=16`, `targetSdkVersion=22` — the same floor as the debug build and the release APK, recovered from a completely different binary format.**

**The `resource_id` field is the independent confirmation:** `0x0101020c` is the framework's canonical `minSdkVersion` attribute ID and `0x01010270` is `targetSdkVersion`. **The AAB carries the attribute IDs explicitly, so the identification does not depend on my string decoding at all** — even if the name strings were misread, the IDs are numeric and unambiguous. **[read, two independent channels]**

**Four failed attempts before this, all recorded in §4 — and the first three failed SILENTLY.**

---

## §2 — T2: the guard, as a reusable checklist

**D79 §0.2 documented the offset-basis hazard as a note. This is the same finding written as an assertion set, so the next decoder cannot ship without it.**

### 2.1 The Acceptance Criterion — exactly as my passing run reported it

**A decode of a binary AXML manifest is ACCEPTED only when all of these hold simultaneously:**

```
GUARD A  string pool: decoded == stringCount, and every offset in-range
                       -> my run: 78/78 (debug)  ·  66/66 (release APK)
GUARD B  element walk: terminal offset == chunkStart + chunkSize, EXACTLY
                       -> my run: 7700 == 7700 (debug)  ·  6340 == 6340 (release)
GUARD C  every nameIdx resolves to a pool index in range
GUARD D  every nsIdx resolves to a pool index in range OR is exactly -1
GUARD E  flags is READ, not assumed: UTF8 = (flags & 0x100) != 0
GUARD F  no chunk with chunkSize == 0, and no chunk overruns the file
```

**These six were the acceptance criterion for D79's original run and for §1.2 above.** **GUARD A + B + "78/78 decoded and terminating at exactly 7700" is the criterion, and I am writing it here because it is the difference between a decode and a plausible-looking guess.**

### 2.2 GUARD D is the one I got WRONG — and it crashed on a valid file

**In my first pass at §1.2 I asserted `0 <= nsIdx < cnt`.** **The release APK's `<manifest>` element has three attributes with `nsIdx = -1`** — `package`, `platformBuildVersionCode`, `platformBuildVersionName`, i.e. **every non-Android-namespace attribute, which is normal and correct.**

**My decoder crashed on the third of them. No traceback, no message — just `exit 1`.**

**The corrected invariant:**
```
nameIdx MUST resolve to a real pool index       (a name is mandatory)
nsIdx   MUST resolve to a real index OR be -1   (-1 == NO NAMESPACE, legal)
```

> **A guard that is too strict does not fail safe. It fails on correct input — and a silent crash on a valid file is indistinguishable from a decoder that cannot read the format.**
> **This is the mirror of the original hazard. D79's failure was a guard too LOOSE (it let a plausible result out beside its errors). This one is a guard too TIGHT (it rejected a correct artifact). Both produce a wrong conclusion about the artifact, and neither announces itself.**

### 2.3 THE INVARIANT — what makes a decoder fail loudly instead of plausibly

**Stated as the thing to test a decoder against:**

> **A decoder is trustworthy only if there EXISTS an input on which it fails loudly.**
> **The offset-basis error is dangerous precisely because it violates this: the wrong basis returns structure-shaped data with no error, so there is no input that distinguishes it from the right basis by its output structure. The only thing that separates them is an EXTERNAL consistency check — a bound the decode must satisfy that the wrong basis cannot.**

**The bounds that actually discriminate, and why each one works:**

| bound | wrong-basis behaviour | why it discriminates |
|---|---|---|
| walk ends **exactly** at `chunkStart + chunkSize` | drifts and overruns or stops short | the total is fixed by the file, not by the basis |
| **every** `nameIdx` in-range | eventually yields an index ≥ `stringCount` | a random 4-byte read almost never lands inside a 78-entry pool |
| `flags` **read**, not assumed | UTF-16 decoded as UTF-8 gives 78 **well-formed** strings | the only field that distinguishes the two modes |
| attribute names must be **identifiable strings** | returns `655360`, `-65536` (my §0.2 attempt) | a name-shaped read from the wrong base fails a printable/identifier test |

**The bound that does NOT work: "the walk completed without an exception."** **Every one of my wrong attempts completed without an exception.** **A structural walk that terminates is not evidence of a correct decode.**

### 2.4 The three-failure catalogue, as evidence that the guard is necessary

**All three are mine, all three this corpus, all three produced fully plausible output:**

| # | failure | what it returned | what caught it |
|---|---|---|---|
| 1 | string pool read in **UTF-8** mode (`flags` ignored) | **78 well-formed strings of pure garbage, ZERO errors** | a filter for `minSdk\|targetSdk` returned **nothing** — impossible for a real manifest |
| 2 | attribute base `off + 2 + headerSize + attrStart` | **`nameIdx=-65536`, `dataType=0x00`, `data=''`** — a complete record of noise | a coordinate that cannot exist; the walk still completed |
| 3 | `nsIdx` asserted `>= 0` | **hard crash, `exit 1`, no traceback — on a VALID file** | the file's own attributes (non-Android namespace = `-1`) |

**Failure 1 and 2 are D79's hazard. Failure 3 is this round's, and it is the new information: the guard can fail in BOTH directions, and the too-tight direction is silent too.** **[verified]**

**And a fourth failure, mechanical rather than logical, worth recording because it produced plausible numbers:** extracting a git blob with PowerShell's `>` **re-encoded it to UTF-16LE and prefixed `FFFE`**, roughly doubling every size. **`2,129,794 → 4,063,078 B`.** **That is `2N - 2`, the exact UTF-16 signature — a wrong result that looked like a real file of a real size.** Fixed by using `cmd.exe /c "... > file"`. **[verified]**

---

## §3 — T3: R-68.1 closed WITHOUT network, and the answer is an absence

**D68 left R-68.1 open: "does the `CN=Android Debug` APK still exist anywhere?"** **Deferred as network-bound (`git fetch --unshallow`).** **Re-examined: it is answerable from the objects already on disk.**

### 3.1 Rule 20 applied to git — enumerate the objects, not the refs

**The reachable history is one commit (confirmed again):** `rev-list --all --count` = **1**, `1516f5e6cad261db33f7f5bb074377de72cc6d94`, and `.git\shallow` holds the same hash — **HEAD IS the shallow boundary.**

**So refs tell me nothing. But the pack holds more than the refs reach:**

```
count-objects -v:   in-pack: 3540   size-pack: 26941 KB   packs: 1
cat-file --batch-all-objects:   blob 3270 · commit 1 · tree 269   = 3540
```

**3,270 blobs are physically present. I enumerated every one of them for zip magic (`50 4B 03`) — not a sample, not the ones I expected.**

### 3.2 The complete result — five zip blobs, every one attributed

```
blob            bytes        entries  kind    path in tree
2eca80881bff   17,661,172     1574   tool    Jar_utils/apktool.jar
93d719e706e5    2,366,154      751   AAB     Android_Code/app/release/app-release.aab
a7a4d6ce278c    1,861,628      382   tool    Jar_utils/sign.jar
cb5fda50a77c    2,129,794      742   APK     Android_Code/app/release/app-release.apk
f6b961fd5a86       54,329       50   tool    Android_Code/gradle/wrapper/gradle-wrapper.jar
```

**Exactly ONE APK in the entire object database.** Its `META-INF/CERT.RSA` is **1,086 B** — the **`CN=karma` RELEASE** certificate (D68 §2.2), not the debug `CN=Android Debug` key (765 B).

**No blob of any size carries a 765-byte `CERT.RSA`. No blob is a second APK.**

### 3.3 The largest non-zip blobs, checked individually — Rule 20 again

```
014c503c    832,962 B   magic 2E63   not a zip
279e44da    626,315 B   magic FFD8   = JPEG
2f899851  2,367,208 B   magic 2E63   not a zip (and NOT the committed AAB, which is 2,366,154)
```

**`2f899851` is 2,367,208 B — 1,054 B larger than the committed AAB and at the same rough scale.** **A size near an expected artifact is exactly the kind of coincidence that produces a false identification**, so I checked it: **magic `2E63`, not `50 4B`. It is not a zip and not an APK/AAB.** **[read]**

### 3.4 VERDICT

> **R-68.1 is CLOSED — as an ABSENCE, established without network.**
> **The `CN=Android Debug` APK is not present in the git object database: not in the committed tree, and not as an unreferenced object in the pack. All 3,270 blobs were enumerated and all five zip blobs attributed to paths.**

**What this does NOT establish:** whether the debug APK ever existed upstream, or exists in a remote not fetched. **A shallow clone's pack contains what the clone fetched.** **The claim is bounded: "not in the objects on disk," not "never existed."** **A `git fetch --unshallow` could still surface it, and I am not claiming otherwise.** **[absence, bounded]**

**And the honest consequence for R-68.3:** it asked whether the debug and release builds share a `config.smali` state, and I deferred it **because it required R-68.1's APK.** **That APK is now established absent from disk, so R-68.3's blocker is not "waiting on a fetch" — it is that the artifact required to answer it is not in this corpus.** **R-68.3 becomes bounded-absent too, not open.** **[inferred from R-68.1's absence]**

---

## §4 — Instrument-failure section

**Six failures this pass. Two were logical (both directions of the guard), one mechanical, three were silent crashes of the same decoder.**

### 4.1 The AAB manifest refused to decode — correctly

**`magic=0a 9c`.** My AXML walk rejected it. **The `assert` on the magic is what turned "cannot read this" into a statement instead of a garbage table.** **[the guard working]**

### 4.2 Four attempts to decode the protobuf, three of which failed silently

**(a)** Assumed `Item.prim` was field **1**. It is field **7**. **(b)** Assumed an attribute's `f5` was always a bytes message; **it is a VARINT (the resource ID, `16843291`)** — calling a sub-parser on an integer **crashed the process with `exit 1` and no traceback.** **(c)** Assumed the root node and its children had the same shape; **the root IS an element, children are WRAPPERS with the element at `f1`.** My classification helper checked "has an `f3` field" first, and **the wrapper also has an `f3` (a 4-byte `Primitive`), so every child was misclassified as an element and the whole subtree was never walked.**

**Failure (c) is the important one.** **It did not crash. It silently returned a correct `<manifest>` and simply never reached `<uses-sdk>`.** **My first complete-looking AAB output was missing the one element I was sent to find — and looked like a finished decode.**

> **A decoder that walks the wrong branch returns a SHORTER answer, not a wrong one. The absence of `uses-sdk` was an artifact of my traversal, and for one step I was reading it as a property of the file.**
> **What caught it: I had enumerated 39 children, and my walk reported two elements. The counts disagreed. Rule 20 — print the enumeration beside the claim.**

### 4.3 The guard that was too tight, on a valid file

**§2.2.** `nsIdx = -1` is legal and means *no namespace*. **Three attributes of the release APK's own `<manifest>` use it.** **My assertion killed the process silently.**

### 4.4 The PowerShell redirection that doubled every file

**§2.4.** `git cat-file blob <sha> > file` in PowerShell **writes UTF-16LE with a `FFFE` BOM**, doubling size minus the BOM. **`2,129,794 → 4,063,078`.** **Every size I read was ~2× the truth and none of them looked impossible.** Fixed with `cmd.exe /c`.

**Generalising: this is the same class as the offset basis.** **A wrong transform that preserves plausibility — a number that is too big by exactly the factor you would expect from an encoding change is *more* convincing than a random number, not less.**

### 4.5 Tool attribution

- **Binary AXML decode:** hand-written PowerShell/Python chunk walk + `Res_value` reader, **my own implementation**. **Not `aapt2`, not apktool.**
- **AAB protobuf decode:** hand-written Python 3.11.9 protobuf field walk, **my own implementation, no protobuf library.**
- **git object enumeration:** `git cat-file --batch-all-objects`, `git rev-list --objects --all`, `git count-objects -v` — **the tool's own inventory.**
- **`apktool` 2.12.0:** not used this round. **Not claimed unavailable.**
- **No REA provider invoked.** **`decode_android_resources` requires a ZIP/APK — for the AAB it may accept the `.aab` container; I did not invoke it and am not claiming it cannot be.** **A third implementation over the protobuf manifest would be a genuine independent check of §1.4, and the `resource_id` field already provides a second numeric channel.**

**Standing hazard:** **the workspace root contains a space (`FOR REDDACTED`). Every path in this pass was quoted.** **D68's fabricated `keytool` diagnosis came from exactly this.**

---

## §5 — Residual unknowns

| ID | Unknown | Probe | status |
|---|---|---|---|
| **R-87.1** | Whether the debug `CN=Android Debug` APK exists in an UNFETCHED remote | `git fetch --unshallow` (network — out of lane) | **open, network-bound** |
| **R-87.2** | Whether the release APK/AAB `<uses-sdk>` also carries `rawIdx=-1` on **all** attributes (I verified the two SDK attrs) | already read: `rawIdx=-1` on both SDK attrs in both artifacts | **effectively closed** |
| **R-87.3** | Whether D79's `original\` tree and the release APK share a `config.smali` state | blocked: requires the debug APK, **now established absent from disk** | **bounded-absent** |
| **R-87.4** | Whether `2f899851` (2,367,208 B, magic `2E63`) has artifact significance | magic ruled out zip/APK/AAB; **unidentified** | open |
| **R-87.5** | Whether the AAB's protobuf manifest also declares the release build's other options identically | same decoder, already available | open, cheap |

**R-87.4 is the one I want to flag: a 2.37 MB blob whose magic is not a zip and whose size is close to the committed AAB.** **It is not an artifact of either builder as far as I can tell, and "unidentified" is the honest status.**

---

## §6 — What this establishes

**1. `minSdkVersion=16`, `targetSdkVersion=22` in ALL THREE artifacts** — the debug tree's binary AXML, the release APK's binary AXML, and the release AAB's **protobuf** manifest. **D79 §1.6's claim is confirmed and its scope WIDENS: the floor is not debug-build-specific.** **[read]**

**2. The floor survives a change of manifest ENCODING** — AXML with a UTF-16 string pool *and* `aapt2` protobuf both declare `16`/`22`. **That rules out "the value is an artifact of one encoder."** **[read]**

**3. The AAB carries explicit framework `resource_id`s** — `0x0101020c` (`minSdkVersion`), `0x01010270` (`targetSdkVersion`). **The identification does not depend on string decoding at all.** **[read, independent channel]**

**4. R-68.1 CLOSED — as a bounded absence, without network.** **All 3,270 blobs enumerated; all five zip blobs attributed by path; exactly one APK exists and it carries the `CN=karma` release certificate (1,086 B), not the debug key (765 B).** **Bounded to "the objects on disk" — a shallow clone's pack contains what it fetched.** **[absence]**

**5. R-68.3 becomes bounded-absent rather than open** — its required artifact is now established absent from this corpus. **[inferred from 4]**

**6. The guard is bidirectional, and both directions are silent.** **D79's hazard was a guard too loose (a plausible result escaping beside its errors). This round's is a guard too tight (a valid file rejected, `exit 1`, no message). The invariant to test a decoder against: does there EXIST an input on which it fails loudly?** **The offset-basis error violates this — no input distinguishes it by output structure, because the wrong basis returns structure-shaped data. Only an external bound discriminates: the walk must end exactly at `chunkStart + chunkSize`, and every `nameIdx` must land inside the pool.** **[method note]**

**7. Four of this round's six failures produced plausible output; three of the four produced NO error at all** — a full pool of garbage strings (UTF-8 mode), a complete noise record (`nameIdx=-65536`), a truncated-but-correct `<manifest>` (wrong branch), and a doubled file size (UTF-16 redirection). **The mechanism is identical in each: a transform that preserves the SHAPE of the answer while destroying its content.**

**The through-line, carried from D53/D64/D68/D79:** **both builders patch by fixed-position surgery and validate nothing.** **This pass adds the same property in the analysis layer: my own decoders produced four plausible wrong answers before the guards caught them, and the guards themselves failed in both directions.** **Nothing checks anything — which is why the external bound, and not the walk completing, is the only thing that has ever told me the truth here.**
