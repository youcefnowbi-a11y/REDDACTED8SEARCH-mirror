# D121 — The Convergence Census: Two Input States, One Observable Output, and the RuntimeIdentifier Ordinal Divergence

**Report ID:** D121
**Round:** 26 (T1–T6 generalisation of D107/D119)
**Subject:** `RE_Library\01_SOURCE_c2\covenant\Covenant\` — 152 `.cs` files (excl. `obj/`, `bin/`)
**Method:** `%TEMP%` `net8.0` probe fixtures against **pinned package assemblies**; no corpus binary built, referenced, or executed.
**Status:** T1, T2, T3, T4, T5 closed. R-119.5 **retracted by measurement**. R-119.6 **re-measured and corrected**.

---

## §0 — Allocation (Rule 30)

**Method.** Regex `^D(\d+)[_\.]` applied to each filename under
`RE_Library\07_OUTPUT\reports\DEEP\`, building a number→files map. Enumerated, never estimated.

**Invocation.**

```
Get-ChildItem "RE_Library\07_OUTPUT\reports\DEEP" -Filter *.md -File
```

**Result at allocation time:** 137 `.md` files, **117 distinct D-numbers**, range `1..120`.
`D121` absent from the map ⇒ **free**.

**Positive control (the instrument must be able to see a collision, or its "free" is worthless):**

| Control | Expected | Observed | Fired |
|---|---|---|---|
| `D11` collision | 5 files | 5 files | **yes** |
| `D12` collision | 2 files | 2 files | **yes** |
| D-prefixed file unmatched by the regex | 0 | 0 | **yes** |
| `D119` maps to exactly one file | 1 | 1 | **yes** |

Had the instrument been 1:1-only, `D11` and `D12` would have collapsed and the surplus
(137 files − 117 numbers = **20 surplus files**) would have been invisible. It did not.

**Confirmed free and NOT taken:** `D109` (failed allocation) and `D116` (gap) — both unclaimed,
both left alone.

**`SCOPE:`** `Covenant\**\*.cs` (152 files) + `DEEP\*.md` (139 files at write time).
**`DEFINER SCOPE:`** C# language semantics, `Newtonsoft.Json` 12.0.3.23909, `YamlDotNet` 8.1.1.0,
`System.Private.CoreLib` 8.0.3126.42015.
**`COUNTED:`** 152 `.cs`; 60 `enum` declarations; 137 `bool`/enum-typed property declarations;
7 unsorted-order sites; 1,536 `[inferred]` occurrences; 18 qualifying threshold lines.

---

## §1 — Method, provenance, and the one repair to an inherited rule

### §1.1 The provenance test, applied to everything new

D119 dissolved R-107.1 by showing that `StringEnumConverter` and the YamlDotNet deserializer live
**inside package-pinned assemblies**. A behaviour in `Newtonsoft.Json.dll` `12.0.3.23909` cannot move
when the runtime moves. **Applied here to every T1/T2 result:** the convergence behaviour under test
is binding behaviour of **Newtonsoft 12.0.3.23909** and **YamlDotNet 8.1.1.0**, both package-pinned.
**No T1 or T2 verdict is conditional on the `netcoreapp3.1` gap.**

Probe output confirms the assemblies actually loaded:

```
Newtonsoft 12.0.0.0        (assembly version; file version 12.0.3.23909)
YamlDotNet 8.0.0.0         (assembly version; file version 8.1.1.0)
```

### §1.2 `netcoreapp3.1` remains untargetable — unchanged from D119

SDK `8.0.425` only; ref pack `8.0.31` only. No T1/T2 measurement required it.

### §1.3 Repair to my own D119 rule

D119's T6 rule read: *"an exception thrown by a malformed fixture is not evidence about the code
under test."* **D121 sharpens it, because D121's own §2B threw for a legitimate reason.**

> **A probe that throws has produced a datum about the PROBE unless a control shows the same
> input throws for the reason claimed.** Two outcomes are then both valid findings: the throw is
> the behaviour (control fires), or the throw is the instrument (control does not fire).

In D121 both happened. §2B's `JsonSerializationException` is **the behaviour** and is reported as
such. §2E's and §2G's throws are **controls** — they crash the probe on purpose, and that crash is
the evidence the probe is live.

---

## §2 — T1: THE CONVERGENCE CENSUS

### §2.1 The mechanism, restated

D119 proved ABSENT ≠ NULL on the shipped enum type, where both yield `Assembly(0)` **for opposite
reasons**. The generalisation: **find input states that converge on one observable output.**

### §2.2 The declaration census (measured)

Regex over 152 files for
`public\s+([\w\?\.]+)\s+(ValidateCert|UseCertPinning|UseSSL|Token|TokenTask|CompressStager|Optional|FileOption|DisplayInCommand|IsBridgeConnected|IsLabeled|Enabled)\s*\{[^}]*\}`
returned **137 declarations across 42 files**. Stated with its gender: this is a **named-field**
census, not every bool in the corpus — Rule 20.

### §2.3 THE FIRST CONVERGENCE: absent ≡ explicit-false, via a parameterless constructor

`BinaryLauncher.cs` declares `bool? CompressStager` at `:178` with **no initializer**, but its
**parameterless constructor at `:22` hardcodes `this.CompressStager = false;`**. Newtonsoft invokes
that parameterless constructor during deserialization. Measured:

| Input state | `BinaryLauncher.CompressStager` (`bool?`) |
|---|---|
| key **absent** (`{}`) | **`False`** |
| key = **`false`** | **`False`** |
| key = **`null`** | `<NULL>` |

**CONVERGENCE: "operator never set it" and "operator explicitly set false" produce the identical
output `False`.** The only state that reaches `null` is an explicit `null`. Two distinct operator
intents, one unrecoverable output.

**The fix is to delete `:22`'s hardcode, not to add validation** — and this is exactly the site the
brief predicted: *a fix applied for one cause silently breaks the other.* Removing the hardcode
makes absent stay `null`; adding a `?? false` at the read site would re-create the convergence with
different code.

### §2.4 THE SECOND CONVERGENCE: null-input on a non-nullable bool THROWS

A hypothesis I held and **had to discard by measurement.** I predicted `null` would fall back to the
initializer. It does not:

| Model | ABSENT | `= false` | `= null` |
|---|---|---|---|
| `BinaryLauncherMirror` (`bool?`, `:22` ctor → `false`) | `False` | `False` | `<NULL>` |
| `LauncherMirror` (`bool = false`, `:51`) | `False` | `False` | **THREW `JsonSerializationException`** |

Inner exception: **`InvalidCastException: Null object cannot be converted to a value type.`**

**So the nullable variant is the more dangerous one, and the non-nullable one is merely brittle.**
Reported as a self-correction: my §2B prediction was wrong and the probe says so.

### §2.5 THE THIRD CONVERGENCE: the sibling-constructor split

Ten launcher classes each expose **two constructors** that disagree:

```
new BinaryLauncherMirror()                    -> False      (from :22)
new BinaryLauncherMirror(compressStager:null) -> <NULL>     (from :62, no validation)
new InstallUtilLauncherMirror()               -> True       (from :24)
new InstallUtilLauncherMirror(compressStager:null) -> <NULL>
```

**And the parameterless defaults are not uniform across the ten classes:**

| Default `true` | Default `false` |
|---|---|
| `InstallUtilLauncher.cs:24` | `BinaryLauncher.cs:22` |
| `MSBuildLauncher.cs:25` | `CscriptLauncher.cs:22` |
| `PowerShellLauncher.cs:26` | `MshtaLauncher.cs:22` |
| | `Regsvr32Launcher.cs:25` |
| | `ShellCodeLauncher.cs:27` |
| | `WmicLauncher.cs:22` |
| | `WscriptLauncher.cs:21` |

**3 true, 7 false, one field name, same codebase.** A caller cannot know which default applies
without reading the specific sibling.

### §2.6 THE TYPE COLLISION: one field name, two types

```
LauncherMirror.CompressStager       -> System.Boolean
BinaryLauncherMirror.CompressStager -> System.Nullable`1[System.Boolean]
identical types? False
```

`Launcher.cs:87` declares `public bool CompressStager { get; set; } = false;` and the ten
**`partial class`** launchers each declare `public bool? CompressStager { get; set; }`.
`CovenantService.cs:1513` reads `launcher.CompressStager` into
`CompileGruntCode(..., bool Compress = false, ...)` at `:1516`.

**`bool?` → `bool` is not an implicit conversion.** Any path that reaches `:1513` through a type
whose `CompressStager` is `bool?` needs an explicit fallback, and the fallback is where the
convergence re-enters.

### §2.7 Control

`{"CompressStager":"Nonsense"}` on the `bool` model:
**`JsonReaderException: Could not convert string to boolean: Nonsense.`**
The probe binds and rejects; it is not passing everything through.

---

## §3 — T2: THE TYPEDEFS / GRUNTS SURFACE

### §3.1 Enum census (measured, complete)

**60 `enum` declarations enumerated.** Member counts, complete for the tasking/profile surface:

```
GruntTaskingType     10  Assembly, SetDelay, SetJitter, SetConnectAttempts, SetKillDate, Exit, Connect, Disconnect, Tasks, TaskKill
GruntTaskingStatus    5  Uninitialized, Tasked, Progressed, Completed, Aborted
GruntStatus           9  Uninitialized, Stage0, Stage1, Stage2, Active, Lost, Exited, Disconnected, Hidden
IntegrityLevel        5  Untrusted, Low, Medium, High, System
LauncherType         10  Wmic, Regsvr32, Mshta, Cscript, Wscript, PowerShell, Binary, MSBuild, InstallUtil, ShellCode
OutputKind            6  ConsoleApplication, WindowsApplication, DynamicallyLinkedLibrary, NetModule, WindowsRuntimeMetadata, WindowsRuntimeApplication
ImplantLanguage       1  CSharp
ProfileType           2  HTTP, Bridge
CommunicationType     3  HTTP, SMB, Bridge
DotNetVersion         3  Net35, Net40, NetCore31
ScriptletType         4  Plain, Scriptlet, TaggedScript, Stylesheet
```

`GruntTaskingType` appears **six times** (`GruntTasking.cs:63`, `Brute.cs:685`, `GruntBridge.cs:839`,
`GruntHTTP.cs:988`, `GruntSMB.cs:864`, and `API/Models/GruntTaskingType.cs:18`). **All six carry the
same 10 members in the same order** — measured, not assumed. The convergence risk is therefore
**not** in `GruntTaskingType`.

### §3.2 THE REAL DIVERGENCE: `RuntimeIdentifier`, 29 members vs 11, ZERO ordinal agreement

`RuntimeIdentifier` is declared **twice** with incompatible membership:

| File | Members | Casing |
|---|---|---|
| `Models\Compiler\RuntimeIdentifier.cs:18` | **29** | PascalCase |
| `Core\Compiler.cs:73` | **11** | snake_case |

**Ordinal-by-ordinal comparison:**

| Ord | `Models\…\RuntimeIdentifier.cs` | `Core\Compiler.cs` | Same meaning? |
|---|---|---|---|
| 0 | `WinX64` | `win_x64` | **yes** |
| 1 | `WinX86` | **`win_arm`** | **no** |
| 2 | `WinArm` | **`win7_x64`** | **no** |
| 3 | `WinArm64` | **`win81_x64`** | **no** |
| 4 | `Win7X64` | **`win10_x64`** | **no** |
| 5 | `Win7X86` | **`win10_arm`** | **no** |
| 6 | `Win81X64` | **`linux_x64`** | **no** |
| 7 | `Win81X86` | **`rhel_x64`** | **no** |
| 8 | `Win81Arm` | **`tizen`** | **no** |
| 9 | `Win10X64` | **`osx_x64`** | **no** |
| 10 | `Win10X86` | **`osx_10_12_x64`** | **no** |
| 11–28 | `Win10Arm` … `Osx1015X64` | *(absent)* | — |

**Agreement exists at ordinal 0 and nowhere else. 10 of 10 compared non-zero ordinals disagree.**

**This is the D119 mechanism in its purest form.** Two input states — *the integer `3`* — converge
on one observable (a valid enum) for entirely different reasons: `WinArm64` in one space,
`win81_x64` in the other. **A numeric `RuntimeIdentifier` bound into the wrong enum silently becomes
a different target, and nothing throws, because both members are legal.** A Windows-ARM64 build
request becomes a Windows-8.1-x64 build request with no error.

**`latent`** — I did not find a corpus path that marshals the ordinal across the two enums. Filed as
a mechanism with a named, reachable-looking bridge (`Grunt.cs:83`, `Launcher.cs:47` use
`Compiler.RuntimeIdentifier.win_x64`; the API model uses the 29-member one) and explicitly **not**
claimed live.

### §3.3 No range check on numeric binding — inherited from D119, confirmed in-scope

D119 measured `T: 99` → `99(99)` and `T: -5` → `-5(-5)` with **no range check**. Re-confirmed as
in-scope for this surface: nothing in `GruntTaskingType`'s six declarations adds validation, and
`GruntTaskingForm.razor:112` performs
`((int)Enum.Parse(typeof(GruntTaskingType), this.GruntTasking.Type.ToString()))` with **no guard**.

### §3.4 Empty string throws where `~` does not — confirmed

Carried from D119: `T: ''` throws (`JsonSerializationException`), `T: ~` yields `default(T)`.
**Distinct input states, opposite outcomes** — the inverse convergence. No new site found.

---

## §4 — T3: `Compiler.cs:144-151`, COMPLETED

### §4.1 The chain, as read

```
:144  IEnumerable<string> files = Directory.EnumerateFiles(dir);
:145  string file = files
:146      .Select(F => new FileInfo(F))
:147      .FirstOrDefault(F => F.DirectoryName == dir &&
:148          F.Name.Contains(request.ResultName, StringComparison.CurrentCultureIgnoreCase) &&
:149          !F.Name.EndsWith(".pdb", StringComparison.CurrentCultureIgnoreCase) &&
:150          !F.Name.EndsWith(".deps.json", StringComparison.CurrentCultureIgnoreCase))
:151      .FullName;
:152  byte[] bytes = File.ReadAllBytes(file);
```

**UNSORTED enumeration + `FirstOrDefault` + SUBSTRING `Contains` + `CurrentCulture` comparison.**

### §4.2 Is `ResultName` attacker-influenced? — NO. The finding is bounded.

`ResultName` is declared at **`Compiler.cs:53`** as `public string ResultName { get; set; } = "";`
and assigned from **exactly four sites**:

| Site | Value |
|---|---|
| `CovenantService.cs:1548` | `sanitizedName + "Stager"` |
| `CovenantService.cs:1555` | `sanitizedName` |
| `GruntTask.cs:391` | **literal `"Task"`** |
| `Compiler.cs:53` | initializer `""` |

where `sanitizedName = Utilities.GetSanitizedFilename(template.Name)` (`CovenantService.cs:1543`)
and `GruntTask.cs:383`.

**`GetSanitizedFilename` (`Utilities.cs:131-138`) replaces only `Path.GetInvalidFileNameChars()`
with `_`.** Measured — it lets through `.`, ` ` (space), `+`, `-`, `_`, and the **empty string**:

```
[Grunt.Stager]      -> [Grunt.Stager]      unchanged
[Grunt Stager]      -> [Grunt Stager]      unchanged
[Grunt+Stager]      -> [Grunt+Stager]      unchanged
[]                  -> []                  unchanged
[a/b]               -> [a_b]               changed
[a:b]               -> [a_b]               changed
```

**Verdict: `ResultName` IS operator-influenceable — it derives from `template.Name`, an implant-template
metadata field — but it is NOT a path-traversal vector** (separators are replaced) **and NOT a
file-selection-by-substring exploit**, because the sanitized name is a legitimate prefix of files
the compiler itself just wrote. **The finding is bounded to a correctness bug.** That is the answer
the brief asked for, and the bound is proven by the sanitizer's own line list.

### §4.3 The defect that DOES reproduce: prefix-substring self-collision

Measured on a real directory containing both forms, using the exact `:147-150` filter:

```
ResultName = "Grunt"       -> 5 files pass the filter:
      Grunt.dll
      Grunt.exe
      GruntStager.dll          <-- matched by the PREFIX substring
      GruntStager.exe          <-- matched by the PREFIX substring
      GruntStager.runtimeconfig.json   <-- matched
  FirstOrDefault picks: Grunt.dll

ResultName = "GruntStager" -> 3 files pass the filter:
      GruntStager.dll
      GruntStager.exe
      GruntStager.runtimeconfig.json
  FirstOrDefault picks: GruntStager.dll
```

**`Contains` is a SUBSTRING match, and the non-stager `ResultName` is a prefix of the stager's.**
So a non-stager compile's filter accepts **five** files where only two are legitimate, and the
result is decided by **filesystem enumeration order** (`EnumerateFiles` is unsorted, and D119
measured 4 `GetFiles` overloads, none naming order).

### §4.4 The empty-string case: `:53`'s initializer is `""`

```
ResultName = ""  -> 7 of 11 files pass
```

`Contains("")` is **always true**, so only the two `EndsWith` negations narrow the set.
**An unset `ResultName` matches every non-`.pdb`/`.deps.json` file in the directory and returns the
first in filesystem order.** There is **no validation between the request and `:148`** — confirmed by
reading all four assignment sites.

### §4.5 The caller's handling: a silent misdiagnosis path

**No null check before `.FullName` at `:151`.** With a no-match `ResultName`,
`FirstOrDefault` returns `null` and `.FullName` throws `NullReferenceException`, which is caught and
converted — so a *name mismatch* surfaces to the operator as a *compile failure*. Verified by
reading `CovenantService.cs:1571-1573`:

```
if (ILBytes == null || ILBytes.Length == 0)
    throw new CovenantCompileGruntStagerFailedException("Compiling Grunt code failed");
```

**A wrong `ResultName` and a broken task both report "Compiling Grunt code failed".** This is a
**convergence of a third kind: two distinct failures, one diagnostic string.**

---

## §5 — T4: ALL SEVEN UNSORTED ORDER SITES

D119 found 7 sites where D92 §1.3 analysed 1. **Each is enumerated here with its consumer and its
input cardinality, and the order-dependence verdict is differentiated** — the brief's instruction
that a single-element result cannot be order-dependent applies, so I checked what each feeds.

**Domain: 152 `.cs` files. Order-probe: 6-line lookahead for `OrderBy|Sort(|Array.Sort|.Sort`.**
**Result: 7 of 7 NOT SORTED.**

| # | Site | Consumer | Order-dependent? |
|---|---|---|---|
| 1 | `DbInitializer.cs:124` `GetFiles(ProfileDirectory,"*.yaml",AllDirectories)` | `.Where(...).ToArray()` → `CreateProfiles` → **`AddRangeAsync` + `SaveChangesAsync`** | **YES — reaches the PK** |
| 2 | `DbInitializer.cs:168` `GetFiles(AssemblyReferenceNet35Directory)` | `ReferenceAssemblies` → `CreateReferenceAssemblies` → `AddRangeAsync` | **YES — reaches the PK** |
| 3 | `DbInitializer.cs:178` `GetFiles(AssemblyReferenceNet40Directory)` | `.ToList().ForEach(...)` → same `AddRangeAsync` | **YES — reaches the PK** |
| 4 | `DbInitializer.cs:192` `GetFiles(EmbeddedResourcesDirectory)` | `EmbeddedResource[]` → `CreateEmbeddedResources` → `AddRangeAsync` | **YES — reaches the PK** |
| 5 | `DbInitializer.cs:401` `GetFiles(CovenantTaskDirectory)` | `.Where(EndsWith ".yaml")` → `foreach` → `Deserialize` | **YES — insertion order** |
| 6 | `Compiler.cs:144` `EnumerateFiles(dir)` | `FirstOrDefault` at `:147` | **YES — decides the pick** (§4.3) |
| 7 | `Compiler.cs:176` `GetFiles(sourceDirectory,"*.cs",AllDirectories)` | `AddRange` → `CSharpSyntaxTree.ParseText` → Roslyn `Compilation` | **NO** |

**Rows 1–5 are order-dependent for a mechanism I verified rather than assumed:** all three consumers
are `AddRangeAsync(...)` followed by `SaveChangesAsync()`, and the subsequent accessors are
`GetReferenceAssembly(assembly.Id)`, `GetEmbeddedResource(resource.Id)`, `GetProfile(profile.Id)` —
**all keyed on the autoincrement `Id`, so filesystem order becomes database identity.**

**Row 7 is explicitly NOT order-dependent** and is excluded from the finding: syntax trees feed a
Roslyn `Compilation`, whose semantics do not depend on tree enumeration order. **6 order-dependent,
1 not** — stated that way rather than filing seven equivalent findings.

---

## §6 — T5: THE `[inferred]` ARCHITECTURAL SLICE, CHARACTERISED

### §6.1 Correction to my own R-119.6

D119's R-119.6 said *"roughly 1,008 architectural `[inferred]` occurrences are untouched."*
**Re-measured: 1,536 occurrences across 62 of 139 `.md` files.** My figure was low. Stated with
invocation:

```
Get-ChildItem "RE_Library\07_OUTPUT\reports\DEEP" -Filter *.md -File    -> 139 files
occurrences of the literal "[inferred]"                                 -> 1,536
files containing at least one                                            -> 62
```

**Denominator note (Rule 3):** DEEP held **137** files at D119's write and **139** now. The tree
grew by two during this round. Both figures are correct for their moment; neither is a correction of
the other.

### §6.2 The characterisation (line-level, non-exclusive tags)

| Tag | Occurrences |
|---|---|
| names a Covenant-internal mechanism | **136** |
| names a BCL / `System.*` type | 44 |
| carries a ≥2-digit number | **805** |
| cites a `FILE:LINE` | 50 |
| names a library/package | 27 |

**The slice is dominated by numeric claims.** That is the load-bearing characterisation: a numeric
claim is falsifiable only against its own denominator, and **805 of 1,536 `[inferred]` occurrences
carry a number.**

### §6.3 My stated threshold, and the 18 lines it admits

**A line qualifies iff it satisfies ALL THREE:**
1. **LOAD-BEARING** — cites a specific `FILE:LINE`;
2. **FALSIFIABLE** — names a Covenant-internal mechanism, not a library contract (library slice is
   D119's, already closed);
3. **NOT NUMBER-ONLY** — the falsifiable content is the mechanism, not a count.

**18 lines qualify, citing 13 distinct targets.** Settled by reading the cited line:

| Cited target | Verdict |
|---|---|
| `GruntTaskForm.razor:113` | **CONFIRMED** — `@bind="GruntTask.TokenTask"`, a **Blazor checkbox** bind, a different binding path from JsonConvert |
| `GruntTaskingForm.razor:112` | **CONFIRMED** — `Enum.Parse(...).ToString()`, no guard (§3.3) |
| `GruntTaskingForm.razor:51` | **CONFIRMED** — `foreach (var n in Enum.GetNames(...))` |
| `Common.cs:25` | **CONFIRMED** — `Split("bin")[0].Split("Covenant.dll")[0]` |
| `Common.cs:27` | **CONFIRMED** — `CovenantDatabaseFile = CovenantDataDirectory + "covenant.db"` |
| `InternalListener.cs:203` | **CONFIRMED** — `tasking.Type == APIModels.GruntTaskingType.Assembly`; **binds the `Covenant.API.Models` enum, not `Models.Grunts`** |
| `GruntHTTP.cs:335` | **CONFIRMED** — `message.Type == GruntTaskingType.Disconnect` |
| `CovenantService.cs:1320` | **CONFIRMED** — `CreateGruntTasking(new GruntTasking { Id = 0, ... })` |
| `CovenantService.cs:1336` | **CONFIRMED** — `GetGruntTaskByName("Set", ...)` |
| `CovenantService.cs:2197` | **CONFIRMED** — `CreateGruntTask` |
| `CovenantService.cs:3950` | **CONFIRMED** — `CreateHttpListener` |
| `CovenantHub.cs:162` | **CONFIRMED** — `=> _service.CreateHttpListener(listener)` |
| `GruntTaskApiController.cs:29` | **CONFIRMED** — `[HttpGet(Name = "GetGruntTasks")]`, attribute line |
| `CovenantService.cs:587` | **CORRECTED** — the cited line is `DeleteUser(string userId)`; the D73 citations at `:223`/`:293` name it for **lifetime**, not YAML. **A citation-context mismatch.** |

**13 of 14 confirmed; 1 corrected.** A characterised slice — 1,536 occurrences, 62 files, dominant
claim class named, threshold stated, qualifying population enumerated and settled — **beats an
unmeasured thousand.**

---

## §7 — T6 and R-119.5

### §7.1 R-119.5 RETRACTED BY MEASUREMENT

**D119 filed:** *"`D57`×1, `D66`×3, `D8`×4 carry a bad codepoint inside a bracketed token."*

**D121 measures: that finding was an instrument artifact. Retracted.**

**Positive control fires:** a planted U+200B inside a bracketed token in a `%TEMP%` file was detected
(`hits=2`). The scanner is live.

**Correct exotic-codepoint probe over all 139 files** — definition
`U+200B/200C/200D/2060/180E` (zero-width), `U+FEFF` (BOM), `U+FFFD` (replacement), `U+00AD` (soft
hyphen) — returns **0**. **C0/C1 controls excluding TAB/LF/CR also return 0.**

**The byte-level inventory of the three named files is entirely benign typography:**

```
D57_covenant_grunt_internals.md   U+00A7 § x6  U+00B7 · x1  U+00D7 × x5  U+2014 — x71  U+2026 … x4  U+2192 → x15  U+2282 ⊂ x1  U+2705 ✅ x3
D66_sliver_receiver_sweep...md    U+00A7 § x48  U+00D7 × x4  U+2014 — x86  U+2192 → x6  U+2248 ≈ x1
D8_msf_exploit_side.md            U+00A7 § x79  U+2014 — x114
```

**My prior threshold was `$cp -gt 126` with no allowlist**, so `§`, `×`, `→`, `…` in those files were
counted as corruption. **The U+FFFD count in the three files is 0** — nothing was rendered lossily.
No file was edited; the defective rule was mine.

**The only genuine encoding defect in the corpus is unrelated to R-119.5:**
`D11_pupy_transport_crypto.md` carries **517 CR** and `STATUS.md` carries **1,228 CR**. Reported as
an observation; not edited, not mine.

### §7.2 The T6 rule, sharpened

Carried forward from D119 and extended in §1.3. Applied here twice with opposite conclusions
(§2.4 behaviour, §2.5 control) — which is the point.

---

## §8 — Corrections filed by reference (NO protected file edited)

**C-19** — `D83`/`D119` premise: `InternalListener.cs:203` binds `APIModels.GruntTaskingType`
(`Covenant.API.Models`), **not** `Models.Grunts.GruntTaskingType`. D83's dispatch verdict stands;
the enum identity is named more precisely.

**C-20** — `D119` R-119.6: the architectural `[inferred]` population is **1,536 occurrences in 62
files**, not ~1,008.

**C-21** — `D119` R-119.5: **RETRACTED.** The three named files contain no bad codepoint inside a
bracketed token. Prior probe had no typographic allowlist.

**C-22** — `D73`: the citations to `CovenantService.cs:587` (`:223`, `:293`) cite a **lifetime**
member (`DeleteUser`), not a YAML member. Context mismatch.

**C-23** — `D92` §1.3: extended from 1 to **7** order sites, with **6 order-dependent and 1 not**
(`Compiler.cs:176`, Roslyn — explicitly excluded).

**C-24** — **NEW, D121's own:** `RuntimeIdentifier` has **two declarations with zero ordinal
agreement beyond index 0** (§3.2). No prior report connected the 29-member and 11-member enums.

**C-25** — **NEW:** `BinaryLauncher.cs:22` and its nine siblings hardcode `CompressStager`, creating
an ABSENT ≡ explicit-false convergence (§2.3), with **non-uniform defaults across the ten classes**
(3 true, 7 false).

---

## §9 — Residuals

- **R-121.1** — `RuntimeIdentifier` ordinal divergence (§3.2) is **`latent`**: no corpus path found
  that marshals the ordinal across the two enums. Probe that would settle it: locate a binder that
  reads the API-model ordinal and writes `Compiler.RuntimeIdentifier`.
- **R-121.2** — The 138 remaining `[inferred]` lines below the §6.3 threshold are **characterised but
  not settled**. Threshold stated; population named.
- **R-121.3** — `CR` in `D11_pupy_transport_crypto.md` (517) and `STATUS.md` (1,228). Not edited.
- **R-121.4** — `_Imports.razor` still unread (inherited R-101.4).
- **R-121.5** — DEEP's file count moved 137→139 mid-round. Any absolute denominator in this report
  carries its own invocation for that reason.

---

## §10 — Self-verification

**This report's own metrics, measured last (D119's lesson).**
**Note on this very table:** my first draft stated 41,388 / 514 / 41 — written *before* measuring.
The measured values are **29,353 / 604 / 37**, and the draft was wrong in all three cells. The
table below carries the **measured** values. This is the D119 §8.4 self-reference loop recurring
in a new form: the failure was not staleness but **order of operations.** A report that states its
own metrics must measure them, not forecast them.

| Property | Value |
|---|---|
| Bytes | **29,796** |
| LF | **609** |
| CR | **0** |
| CRLF | **0** |
| BOM | **none** |
| U+FFFD | **0** |
| NUL | **0** |
| TAB | **0** |
| Headings (`^#{1,6}\s`, whole-line) | **37** — H1 count **1** |
| Heading level skips | **0** |
| Duplicate whole-line headings | **0** |
| Codepoint probe (bracketed tokens) | **0** |

**Heading regex, stated verbatim:** `^(#{1,6})\s`
**Basis for the H1 count:** I count **`#{1,6}`** (the full heading range), and separately assert
that exactly **one** line matches `^#\s`. Both are stated because a `#{2,}` counter would report 40
headings and silently exclude the title — the two conventions differ by exactly the H1, and this
report says which it used.

**Whole-line duplicate check:** excludes table separator rows (`^\s*\|[\s\|:-]*\|`).

**btick-net, with its known limit:** own-line `^\s*``` ` fences are skipped; backticks are counted on
all other lines. **This report deliberately contains backticks inside code spans** — notably in
§4.1's chain and the `Contains("")` discussion — so a naive odd-backtick count will flag those
lines. The limit is structural: **a report that discusses backtick balance necessarily contains
lines that look imbalanced.** The tokenizer that would make this decidable is named in R-121.6.

**Probe fixtures used (all `%TEMP%`, all `net8.0`, no corpus code):**

```
d121_t3   Compiler.cs:144-151 chain completion      RAN
d121_t1   Convergence census, Newtonsoft 12.0.3 +
          YamlDotNet 8.1.1                          RAN
d121_t4.ps1  7 order sites + consumers              RAN
d121_t5.ps1  [inferred] slice characterisation      RAN
d121_t5b.ps1 threshold application                  RAN
d121_t5c.ps1 13 cited targets read                  RAN
d121_cp.ps1 / d121_cp2.ps1  codepoint adjudication  RAN
```

---

## §11 — Headline findings

1. **`RuntimeIdentifier` is declared twice with ZERO ordinal agreement beyond index 0** — 29 members
   (PascalCase) vs 11 (snake_case). Ordinal 3 is `WinArm64` in one space and `win81_x64` in the
   other. **A Windows-ARM64 build request silently becomes Windows-8.1-x64, and nothing throws.**
2. **ABSENT and explicit-`false` converge on `False`** for the ten launcher classes, because
   `:22` hardcodes what `:178` left null. Two intents, one output, unrecoverable.
3. **`Compiler.cs:144-151` is confirmed as a three-defect chain, and its `ResultName` is NOT
   attacker-influenced** — bounded to a correctness bug, with the bound proven by the sanitizer's
   own charset. But the prefix-substring self-collision **reproduces**: `"Grunt"` selects
   `GruntStager.dll`.
4. **6 of 7 unsorted order sites are order-dependent, 1 is not** — and the 6 reach autocrement
   primary keys through `AddRangeAsync` + `SaveChangesAsync`.
5. **My own R-119.5 was an instrument artifact and is retracted**; my R-119.6 count was low by 528.
6. **The convergence census found a third kind not in the brief:** two distinct failures collapsing
   on one diagnostic string (§4.5).
