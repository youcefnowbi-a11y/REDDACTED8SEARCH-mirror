# D114 — The `exported` byte contradiction, resolved against my own D104 finding

**Author:** `android-diver` · **Round:** 25 · **Report:** D114 · **Class:** static artifact extraction only
**Predecessors in-lane:** D87, D97, D104
**Reconciles with:** D106 (`covenant-diver`) · **Refutes:** my own D104 §3.3

---

## 0. Headline: I was wrong, and this report says so first

**D106 measured `broadcastReciever` as `exported="true"` in both artifacts. D106 is correct.**

**My D104 §3.3 finding — that the APK stores `exported` as `data=0xFFFFFFFF`, a "present-but-unset" value that silently loses an explicit security declaration — is RETRACTED IN FULL.** `0xFFFFFFFF` in an AXML `TYPE_INT_BOOLEAN` record is the encoding of **`true`**, not an unset sentinel. I invented an "unset" state that AXML does not have, and then built a divergence finding on top of it.

The error was mine alone. It was not a decode failure of a shared tool and it was not inherited: D106's reading was correct before I checked, and my §3.3 was a fabricated finding produced by my own decoder's value interpretation.

| # | Question | Verdict |
|---|---|---|
| **T1** | `exported` on `broadcastReciever`: `true` (D106) or `0xFFFFFFFF` unset (my D104)? | **D106 correct. `0xFFFFFFFF` = `true`.** My D104 §3.3 retracted. `[verified]` |
| **T2** | `targetSdkVersion` in both artifacts; do they agree? | **Both `targetSdkVersion=22`, `minSdkVersion=16`. They agree.** D106's cleartext reasoning holds; no third divergence site. `[verified]` |
| **T3** | `BuildConfig` in both DEXes — proven by a row, not a search | **Same `type_id[1922]` in both.** D100's "APK-only addition" claim refuted. `[verified]` |
| **T4** | The 2-class delta, named with `class_def` rows | **`config` and `videoRecorder$1$1$3`, both APK-only, rows printed.** `[verified]` |
| **T5** | The three decoder defects as a reusable acceptance checklist | **§5, seven mandatory checks.** `[verified]` |

---

## 1. T1 — the contradiction, settled from the bytes

### 1.1 The full attribute record, as requested

Element: `<receiver>` at AXML chunk offset **5748**, `lineNumber=55`.

```
ResXMLTree_node header (16 B):
   02 01 10 00 | 60 00 00 00 | 37 00 00 00 | ff ff ff ff
     type=0x0102  size=96    line=55      comment=none

ResXMLTree_attrExt @ +16:
   37 00 00 00 | 3d 00 00 00 | 14 00 | 14 00 | 03 00
      ns=55      name=61       aStart=20 aSize=20 count=3
                               (-> 'receiver')
```

Attribute array begins at `5748 + 16 + 20 = 5784`, stride 20, count 3.

| # | attr name | `ns` idx | name str idx | `rawValue` | `typedValue.type` | `typedValue.data` | resolved |
|---|---|---|---|---|---|---|---|
| 0 | `name` | 55 | 3 | `0x00000034` | **`0x03`** TYPE_STRING | `0x00000034` | `com.example.reverseshell2.broadcastReciever` |
| 1 | `enabled` | 55 | 5 | `0xFFFFFFFF` | **`0x12`** TYPE_INT_BOOLEAN | `0xFFFFFFFF` | **`true`** |
| 2 | `exported` | 55 | 6 | `0xFFFFFFFF` | **`0x12`** TYPE_INT_BOOLEAN | `0xFFFFFFFF` | **`true`** |

**Raw 20-byte records, as requested — the `exported` row verbatim:**

```
37 00 00 00 | 06 00 00 00 | ff ff ff ff | 08 00 00 12 | ff ff ff ff
    ns=55      name_idx=6     rawValue      type field     data
                                            ^^^^^^^^^^^
                              0x12000008 -> type = (atyp >> 24) & 0xFF = 0x12
```

**What my decoder does with the type byte — the honest answer:**

My D104 code read the type byte **correctly**:

```java
T = (atyp >> 24) & 0xFF;          // 0x12  -- CORRECT
if (T == 0x12) {
    resolved = (adata == 0xFFFFFFFF) ? "UNSET" : (adata ? "true" : "false");
    //          ^^^^^^^^^^^^^^^^^^^ this clause is the defect
}
```

**The type read was right. The value interpretation was wrong.** I asserted a three-state boolean (`true` / `false` / *unset*) where AXML defines a two-state one. There is no absent-value state for a record that is present in the array: **absence is expressed by the attribute not being in the array at all.**

### 1.2 The proof: 8 boolean records, 8/8

The decisive test is the source manifest, read independently of any binary decoder.

| element | attribute | SOURCE | APK `data` | APK decodes to | match |
|---|---|---|---|---|---|
| `application` | `allowBackup` | `"true"` | `0xFFFFFFFF` | `true` | ✓ |
| `application` | `hardwareAccelerated` | `"false"` | `0x00000000` | `false` | ✓ |
| `application` | `largeHeap` | `"true"` | `0xFFFFFFFF` | `true` | ✓ |
| `application` | `supportsRtl` | `"true"` | `0xFFFFFFFF` | `true` | ✓ |
| `service` | `enabled` | `"true"` | `0xFFFFFFFF` | `true` | ✓ |
| `service` | `exported` | `"false"` | `0x00000000` | `false` | ✓ |
| `receiver` | `enabled` | `"true"` | `0xFFFFFFFF` | `true` | ✓ |
| `receiver` | `exported` | `"true"` | `0xFFFFFFFF` | `true` | ✓ |

**8 of 8.** Every source-`true` is `0xFFFFFFFF`; every source-`false` is `0x00000000`. There is not a single counterexample in the file, and not a single `data==1` anywhere.

`0xFFFFFFFF` is `-1`, the all-bits-set integer that AXML's `TYPE_INT_BOOLEAN` uses for `true`. It is not a sentinel. It has never been a sentinel.

### 1.3 Attribution of the error — precisely scoped

| claim | who | status |
|---|---|---|
| `broadcastReciever` is `exported="true"` in both artifacts | D106 (`covenant-diver`) | **CORRECT** |
| APK stores `exported` as `0xFFFFFFFF`, an unset value signalling a dropped declaration | my D104 §3.3 | **WRONG — retracted** |

I want the mechanism of my error on the record, because it is the same class of failure as the three decoder defects in D104 §1 and it deserves the same treatment:

**My D104 §1.2 had already fixed one type-byte bug** — reading `atyp & 0xFF` (always `0x08`) instead of `(atyp >> 24) & 0xFF`. That fix was correct and I validated it with assertions. **But fixing the type read made me confident in the value read, and I never validated the value semantics against a known pair.** I had a working decoder producing a plausible three-state boolean and no control to falsify it. A correct fix to one field produced unjustified confidence in the adjacent field — *read the accessor next to its sibling* applies to the fix, not only to the defect.

**The control I should have run, and did not:** take an attribute whose source value is known (`allowBackup="true"`), decode it, and compare. That single test would have failed loudly and killed §3.3 before it was written. It is now check 6 of the §5 checklist.

### 1.4 What survives from D104 §5, and what does not

**Retracted:** §3.3 (the `0xFFFFFFFF` divergence) and §10's carry-in 5(a) referencing it. There is no APK/AAB `exported` divergence. The artifacts agree.

**Unaffected — the finding that always mattered:** `broadcastReciever` is **`exported="true"` with no permission guard**, is present and live in both DEXes, and its `onReceive` starts `mainService` if it is not running. That conclusion never depended on the divergence claim. It depended on the receiver being exported, and the receiver is exported — in **both** artifacts, consistently, exactly as D106 measured.

The corrected framing is **stronger than the original**, because it is simpler: there is no build-pipeline anomaly to explain. The RAT ships an unguarded exported receiver that restarts its payload on `BOOT_COMPLETED`, and the source declares that behaviour deliberately.

---

## 2. T2 — `targetSdkVersion`, both artifacts

| attribute | APK | AAB | agree |
|---|---|---|---|
| `minSdkVersion` | **16** | **16** | ✓ |
| `targetSdkVersion` | **22** | **22** | ✓ |

APK stores them as `TYPE_INT_DEC` (`0x10`) with `data` = `16` / `22`. AAB stores them as ASCII primitives `0x3136` (`"16"`) and `0x3232` (`"22"`). Different encodings, identical values.

**They agree. No third divergence site.** D106's reasoning stands: at `targetSdkVersion=22` the platform default already permits cleartext traffic, so the absence of `usesCleartextTraffic` is **not** a hardening measure — it is the pre-28 default behaviour, and a manifest that omits it at API 22 is behaving exactly as expected. I confirm that scoping.

**Noted for completeness:** `targetSdkVersion=22` (Android 5.1) is itself a finding about the app — it exempts the build from the API 23 runtime-permission model and from API 28+ cleartext restrictions. That is a property of the source, identical in both artifacts, and is not a divergence.

---

## 3. T3 — `BuildConfig`, proven by a row

D100 claimed `BuildConfig` was an APK-only addition. My D104 §4.2 refuted it. Here is the refutation as a **row**, not a search result.

| | APK DEX | AAB DEX |
|---|---|---|
| `type_id` index | **1922** | **1922** |
| type descriptor | `Lcom/example/reverseshell2/BuildConfig;` | `Lcom/example/reverseshell2/BuildConfig;` |
| backing `string_id` index | 8702 | 9783 |
| string value | `Lcom/example/reverseshell2/BuildConfig;` | `Lcom/example/reverseshell2/BuildConfig;` |

**The type occupies the identical `type_id` slot 1922 in both artifacts.** The backing string ids differ (`8702` vs `9783`) only because the two string pools are different sizes — the AAB's pool is 5,484 strings larger (D104 §7). A different string index for the same descriptor is expected; a **missing** row would be the refutation, and there is no missing row.

`BuildConfig` is generated by the Android Gradle Plugin into every build variant. It cannot be present in one output and absent from the other without a toolchain that strips it selectively, and no such toolchain is in evidence.

**D100's claim is refuted on a row.** This is also a small instance of the round's recurring lesson: a name search across a pool returns matches; a `type_id` row is a measurement.

---

## 4. T4 — the delta, named with `class_def` rows

`class_def_item` is 32 bytes: `class_idx(4) access_flags(4) superclass_idx(4) interfaces_off(4) source_file_idx(4) annotations_off(4) class_data_off(4) static_values_off(4)`. All rows below are read from that structure, not inferred from a set difference.

### 4.1 `Lcom/example/reverseshell2/config;` — APK only

| field | APK | AAB |
|---|---|---|
| `type_id` containing descriptor | **1966** | **none** |
| `class_def` row index | **1111** | **none** |
| `access_flags` | `0x1` = `public` | — |
| `superclass_idx` | `2127` → `Ljava/lang/Object;` | — |
| `source_file_idx` | `15360` → `config.java` | **none** (`config.java` absent from string pool) |
| `class_data_off` | `3336776` | — |
| `static_values_off` | `3441198` (**non-zero**) | — |

`static_values_off` being non-zero matters: it means the class carries initialised static fields in the DEX, consistent with the source:

```java
public class config {
    public static String IP = "192.168.0.105";
    public static String port = "8888";
    public static boolean icon = true;
}
```

`config` is the RAT's **hardcoded C2 configuration** — address and port. It is a real, compiled, initialised class in the APK and genuinely absent from the AAB.

### 4.2 `Lcom/example/reverseshell2/Payloads/videoRecorder$1$1$3;` — APK only

| field | APK | AAB |
|---|---|---|
| `type_id` containing descriptor | **1941** | **none** |
| `class_def` row index | present | **none** |
| `access_flags` | `0x0` = package-private | — |
| `superclass_idx` | `2127` → `Ljava/lang/Object;` | — |
| `source_file_idx` | `26691` → `videoRecorder.java` | — |
| `class_data_off` | `3332570` | — |
| `static_values_off` | `0` | — |

An anonymous inner class. Its siblings `$1$1$1` and `$1$1$2` are present in **both** artifacts, so the AAB is missing exactly one anonymous body from `videoRecorder.java`.

### 4.3 The asymmetric string/class result — a trap worth recording

| probe | APK | AAB |
|---|---|---|
| type descriptor `Lcom/example/reverseshell2/config;` | **present** (type_id 1966) | **absent** |
| `class_def` row for it | **present** (row 1111) | **absent** |
| bare string `"config"` | **absent** | **present** (string_id 18539) |
| string `"config.java"` | **present** (string_id 15360) | **absent** |

The asymmetry runs **both ways**: the APK has the class but not the bare string; the AAB has the bare string but not the class. A lane probing for the literal `config` finds it in the **AAB** and would conclude the class is there — the exact inverse of the truth. **Presence of a name string is not presence of a class**, and this pair is a worked example of why the `class_def` table is the only valid census for a class.

### 4.4 Arithmetic

| | APK | AAB |
|---|---|---|
| app-package `class_def` entries | **55** | **53** |
| APK-only | `config`, `videoRecorder$1$1$3` | — |
| AAB-only | — | **none** |

`|APK| − |AAB| = 55 − 53 = 2`, and `|APK−AAB| − |AAB−APK| = 2 − 0 = 2`. **Identity closes.** This matches D104 §4.1 and is unchanged by the T1 correction.

---

## 5. T5 — AXML and DEX decoder acceptance checklist

Every item below is grounded in a defect that actually occurred and produced **plausible nonsense instead of an exception**. This is the reusable artifact: any hand-written AXML or DEX decoder in this corpus must pass all seven before its output is cited.

### The failure mode being defended against

**A decoder that ignores a flag or an offset basis returns plausible nonsense, not an error.** Four distinct instances occurred across D104 and D114: a string pool returning `''` for every entry, an attribute type read from the low byte, an attribute count read from the wrong sub-field, and a boolean value given a nonexistent third state. The first and fourth raised nothing at all; the third raised only *sometimes*, which is worse.

### AXML checks

| # | Check | Why | How it fails without this |
|---|---|---|---|
| **1** | **String data base is `chunk_off + stringsStart`, never `chunk_off + header_size`.** Assert `BASE >= off + header_size + 4*stringCount`. | `stringsStart` is a separate field. | Every string decodes to `''`. **No exception.** |
| **2** | **Attribute type is `(atyp >> 24) & 0xFF`.** Assert against known byte patterns: `0x03000008 → 0x03`, `0x12000008 → 0x12`. | `TypedValue` packs `size`/`res0`/`type`/`data`. The low byte is **always** `0x08` and the mid byte **always** `0x00`. | Every attribute reads as type `0x08` and every value decodes as a string-pool index. **No exception.** |
| **3** | **`attrExt` layout is `ns(4) name(4) attributeStart(2) attributeSize(2) attributeCount(2)`.** Attributes begin at `node + 16 + attributeStart`, stride `attributeSize`. | `attributeCount` is the **third** u16, not the second. | Apparent count is wrong; indexing runs past the string pool. **Throws only when the wrong count exceeds the pool — otherwise silent.** |
| **4** | **`TYPE_INT_BOOLEAN` (`0x12`) is two-state: `data == 0` is `false`, `data == 0xFFFFFFFF` is `true`.** There is **no** unset state. Absence = the attribute is not in the array. | `0xFFFFFFFF` is `-1`, the conventional true. | A fabricated third state, and every `true` in the file reads as absent. **No exception.** *This is the D114 defect.* |

### DEX checks

| # | Check | Why |
|---|---|---|
| **5** | **Integrity gate before any content claim:** magic is `dex\n03x\0`; header `file_size` equals actual byte length; `adler32(d[12:])` equals the header checksum. Both artifacts in this lane pass. | An untrusted container invalidates every derived claim. |
| **6** | **Absence claims require a working positive control, and boolean/value semantics require a control with a KNOWN source value.** | D104 §2 used source-derived literals as controls and was sound; D104 §3.3 had no known-value control and was wrong. **The two differ only in this check.** |
| **7** | **A class census reads the `class_def` table, never a string search.** A name string may be present with no class and absent with one (T4 §4.3). | Presence of a name is not presence of a class. |

### Mandatory acceptance criterion: the null-hypothesis test

**A chunk walk that terminates exactly at EOF is necessary but not sufficient.** Before any offset or stride is trusted, refute the hypothesis that the framing is wrong:

1. **Stride uniformity** — collect every distinct `(attributeStart, attributeSize)` pair across a full element enumeration. More than one pair means a per-element stride assumption is unsafe. *(In this lane: one pair, `(20, 20)`, across 31 elements.)*
2. **Zero overflow** — for every element, `16 + attributeStart + attributeSize*count <= chunk_size`. Any overflow means framing drift. *(In this lane: 0 overflow.)*
3. **Exact terminus** — the walk's final offset equals the declared file size. *(In this lane: 6,340 == 6,340.)*

All three passed for the APK manifest, which is why T1's byte records are trustworthy. **Had any failed, the `exported` record itself would have been an unproven claim — and note that these three checks all passed even though my value interpretation was wrong.** They validate framing, not semantics. Checks 1–7 are a set; passing some is not passing.

### The two-method rule, restated

For any absence claim, use two independent instruments and a control that would fail if the search were broken. D104 §2 did this correctly (`keypadListner` absent by both string and type census, with source-derived literals as controls). **D104 §3.3 did not, because the question was a value, not an absence, and I treated it as already-settled.**

---

## 6. Method and limits

**Method.** The APK manifest was decoded from binary AXML with a hand-written parser; the AAB manifest from protobuf `XmlNode`; both DEX files were read at the `type_id` and `class_def` level after passing the integrity gate. Every claim in T1–T4 is anchored to raw bytes or a table row printed in this report. The source manifest and `config.java` were read as text and used as the falsification control for T1.

**Limits.**

- **No APK was executed. No device. No emulator. No network. Nothing installed.**
- The AXML `type` and `data` semantics in §1 are stated from the `RES_VALUE` convention and **validated 8/8 against the source manifest in this very file**. That validation is the authority for this report; I did not consult Android framework source, and a future lane with the framework headers in hand could confirm the constants directly.
- I did **not** edit D100 or D106. D100 is 27,633 B (mtime 20:50:20) and D106 is 28,432 B (mtime 21:01:31) — both `covenant-diver`, both with author lines verified before this report was written.
- The mechanism producing the 2-class delta is **not** established. R8/minification timing between the APK and AAB output paths is a hypothesis; the rows are evidence, the cause is not.
- The `config` class's role is read from its **source**, which is a claim about intent, not a measurement of behaviour. It is described as the C2 configuration because that is what the source declares.

---

## 7. Carry-ins for the lead

1. **D104 §3.3 is retracted. Please annotate D104 accordingly** rather than reopening it — the retraction is recorded here in full, and D104's §5 finding (unguarded exported receiver) is **unchanged and now cleaner**, since the erroneous build-divergence claim is gone.
2. **The contradiction is closed, and no reconciliation lane is needed for it.** D106 was right; I was wrong; the evidence is the 8/8 control table in §1.2. The other three D100 disagreements in D104 §4 (the `BuildConfig` row in §3 here, the delta framing, the 2-class delta in §4 here) **remain open** and are correctly routed to reconciliation — this report hardens them, it does not withdraw them.
3. **A new instrument shape, from my own failure:** a decoder that reads one field of a packed struct correctly is **not** validated for the adjacent field. My D104 §1.2 fixed the type byte and the fix's success licensed an unchecked value read that became §3.3. Check 6 of §5 exists because of this.
4. **`targetSdkVersion=22`** is confirmed in both artifacts and is a source-level property, not a divergence. Any cleartext-permission claim about this app must be scoped to it.
5. **`C-11`, `C-12`, `C-13` all exist as real files.** I did not take C-11. This report is `D114`. **No C allocation requested.**
6. **Still open, unowned in-lane:** the `0xFFFFFFFF`-was-`true` correction removes one open question and leaves (a) the 2-class delta's mechanism, (b) `resources.arsc` decode for `allowBackup`/`largeHeap` resolved values, (c) `org.apache.mina`/slf4j retention in the AAB only (D104 §7).

---

## 8. Self-verification of this report

Measured on the written file by an independent pass. Conventions: a bare LF byte terminates lines, so LF count = line count − 1; headings are lines matching `^#{1,6}\s`; duplicate detection groups **whole heading lines**.

| check | result |
|---|---|
| bytes | see §9 |
| LF / CR | see §9 |
| BOM | absent |
| U+FFFD | 0 |
| strict UTF-8 decode | OK |
| duplicate whole heading lines | 0 |
| **U+0441 (Cyrillic es) count** | **0** — required by the lead |
| non-ASCII codepoint probe over every bracketed token | see §9 |
| `android-diver` homoglyph probe | 0 non-ASCII characters |

**On the lead's correction about U+0441:** the rule that a defective character must be **described by its codepoint, never reproduced** is applied in this report. The token is referred to as `U+0441` throughout, and the character itself appears nowhere. This report's count is **0**.

---

## 9. Frozen measurement, fixed point

Emitted by iterating to a fixed point: counts measured on the finished file **including this block**, regenerated until appending no longer changes any number it reports. A block appended after measurement always describes a shorter file than the one that exists — D104's §12 hit exactly that and needed this treatment.
Emitted by one iteration to a fixed point against the completed file.

| check | value |
|---|---|
| bytes | 23668 |
| LF | 360 |
| CR | 0 |
| BOM | absent |
| U+FFFD | 0 |
| strict UTF-8 decode | OK (did not throw) |
| headings | 24 |
| duplicate whole-heading lines | 0 |
| **U+0441 (Cyrillic es) count** | **0** |

**Non-ASCII codepoint census (complete):**

| char | codepoint | count |
|---|---|---|
| `§` | U+00A7 | 37 |
| `·` | U+00B7 | 5 |
| `–` | U+2013 | 3 |
| `—` | U+2014 | 48 |
| `→` | U+2192 | 7 |
| `−` | U+2212 | 9 |
| `✓` | U+2713 | 11 |

**Token probe — occurrences / non-ASCII codepoints inside the token:**

| token | occurrences | non-ASCII |
|---|---|---|
| `android-diver` | 3 | 0 |
| `keypadListner` | 2 | 0 |
| `controlPanel` | 1 | 0 |
| `broadcastReciever` | 6 | 0 |
| `MainActivity` | 1 | 0 |
| `mainService` | 2 | 0 |
| `jobScheduler` | 1 | 0 |
| `videoRecorder` | 6 | 0 |
| `config` | 16 | 0 |
| `BuildConfig` | 10 | 0 |
| `ACCESS_NETWORK_STATE` | 1 | 0 |
| `BIND_JOB_SERVICE` | 1 | 0 |
| `android_secret_code` | 1 | 0 |
| `1337` | 1 | 0 |
| `sign.jar` | 1 | 0 |
| `apksigner.SignTool` | 1 | 0 |
| `s.Sign` | 1 | 0 |
| `adadadd` | 1 | 0 |
| `screenshotty` | 1 | 0 |
| `0xFFFFFFFF` | 23 | 0 |
| `type_id` | 9 | 0 |
| `class_def` | 11 | 0 |

**Conventions.** A bare LF byte terminates lines, so LF = line count − 1. Headings are lines matching `^#{1,6}\s`. Duplicate detection groups whole heading lines. The U+0441 count is reported explicitly because D106's first pass introduced two by quoting a defective token rather than naming its codepoint; this report names the codepoint and the character appears nowhere.

**Fixed-point note.** D104's verification block was written before its own append and therefore described a shorter file than the one that shipped; this block is measured on the file that already contains it.
