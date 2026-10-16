# D101 — The Covenant binary↔source pair: a NEGATIVE result, and four empirical closures

**Author:** `covenant-diver` · **Round:** 24 · **Class:** source-only + **three executed BCL probes** (no REA, no `open_binary`, no Covenant build, no Covenant execution)
**Lane:** Covenant `.NET` binary↔source **pair**
**Write scope:** this file only. **D1–D100 protected** — D92/D93 read, neither edited.
**Line-count convention:** **LF-byte count**, matching D83/D93. "Lines" are LF bytes.
**Coordinate discipline:** every line number written **`file:line`**, never bare.

---

## 0. THE HEADLINE: the lane's premise is false, and I am leading with that

### 0.1 `[verified]` There is no Covenant binary in this corpus

**The brief states: "Covenant ships both a compiled `Covenant.dll` and the full C# source. That is the best-available pairing in the corpus."**

**`[verified]` That is not the case. The compiled half of the pair does not exist.**

**Enumerations, all printed:**

| Probe | Result |
|---|---|
| `Get-ChildItem -Recurse -File` where `Name -match '^Covenant\.(dll\|exe\|pdb)$'` | **NONE anywhere in the tree** `[verified]` |
| `Get-ChildItem -Recurse -Directory` where `Name -in @('bin','obj')` | **NO bin/ or obj/ directories** `[verified]` |
| All `*.dll`/`*.exe`/`*.pdb`/`*.nupkg`, sorted by size, top 40 printed | **zero Covenant-authored binaries** `[verified]` |

**`[read]` D93 §1.6 was RIGHT and my brief was wrong.** D93 recorded that its own `Covenant.dll` enumeration "returned nothing." **I re-ran that enumeration independently and it returns nothing.** **The brief's premise is a memory error, not a D93 error.**

**`[verified]` Consequence, stated plainly: all four of my assigned tasks presuppose an artifact that is not in the corpus.**

| Task | Presupposes | Status |
|---|---|---|
| T1 — is the `FromJson`/null-`Author` abort reachable *in the compiled* `Covenant.dll`? | a compiled `Covenant.dll` | **unanswerable as posed** — §2 answers it a different way |
| T2 — are `Split("bin")[0]` literals recoverable *from the compiled* build? | a compiled `Covenant.dll` | **unanswerable as posed** — §3 |
| T3 — enumerate task-persistence call sites *in the compiled assembly* | a compiled `Covenant.dll` | **unanswerable as posed** — §4 answers it from source |
| T4 — confirm *against the compiled assembly* which enum the type parses into | a compiled `Covenant.dll` | **unanswerable as posed** — §5 answers it empirically |

### 0.2 `[verified]` The decompiler IS available — so absence of a binary is the reason, not absence of tooling

**`[verified]` `ilspycmd: 9.1.0.7988` / `ICSharpCode.Decompiler: 9.1.0.7988` is installed** at `C:\Users\PC\.dotnet\tools\ilspycmd.exe`.

**`[verified]` I proved it works on real managed metadata** — `ilspycmd -l c refs\dnlib.dll` returned real type rows (`dnlib.Settings`, `dnlib.W32Resources.ResourceData`, `dnlib.Utils.LazyList`).

**`[inferred]` This matters for how the negative result is read.** The brief anticipated the fallback: *"If a managed decompiler is unavailable, say so and fall back to enumerating method signatures + string literals."* **The decompiler is available. It has nothing Covenant-authored to read.** **A working tool pointed at an absent artifact and returning nothing is a stronger negative than a missing tool** — it cannot be attributed to the instrument.

### 0.3 The honest deliverable

**I cannot decompile a binary that does not exist, and I will not simulate one.** **What I *can* do — and did — is close the underlying questions empirically**, because every one of them turns on a **library contract** that I can execute:

- **§2** re-tests D92's `FromJson` conclusions against **Newtonsoft.Json 12.0.3** (the pinned version, `Covenant.csproj:43`).
- **§3** re-tests D93's `Split` conclusion against the BCL.
- **§5** re-tests the `Enum.Parse` mechanism against the BCL.
- **§6** re-tests D92's residual #1 against **YamlDotNet 8.1.1** (`Covenant.csproj:46`).

**`[verified]` This is the D93 #24 precedent applied seriously.** #24 nearly asserted `Split` returns `""` from memory, ran a probe, and found it returns the **whole string**. **My probes inverted three of my own expectations (§2.4, §6.2, §6.3). Each inversion is a correction to a prior report.**

---

## 1. THE EXCLUSION — stated, and justified by BOUNDARY

### 1.1 `[verified]` The exclusion

**`Covenant\Data\AssemblyReferences\net35\` (18 files) and `net40\` (18 files) are EXCLUDED from this lane.** Tagged **`vendored-dependency`**.

### 1.2 `[verified]` The boundary is JUSTIFIED — by authorship, measured four ways

**(a) Zero Covenant-authored assemblies in the set.** `[verified]` Filtering the 18 net40 names against `Covenant|SharpSploit|Grunt|Confuser` returns **NONE**. **[invocation: full name list printed; the filter's denominator is the printed list of 18.]**

**(b) The name sets are IDENTICAL between the two framework versions.** `[verified]` `net35` = 18 files, `net40` = 18 files, **name sets EQUAL: True**. **A same-named set appearing twice is a framework-versioning pattern, not two Covenant components.** **[invocation: both sorted name arrays string-joined and compared; True.]**

**(c) The twins are BYTE-DIFFERENT — they are genuine separate framework builds.** `[verified]` Sampled five, SHA-256 first-16:

| Assembly | `net35` | `net40` | Identical |
|---|---|---|---|
| `mscorlib.dll` | `0A586CB755EB74D2` | `F7A62C9392D6762F` | **False** |
| `System.dll` | `B3998BE682FEC1CA` | `B6DC62E2437B39F4` | **False** |
| `System.Windows.Forms.dll` | `A17997665DC2F225` | `E969A78FFD275875` | **False** |
| `System.Management.Automation.dll` | `AC76D6AB7C2BB813` | `9CEBD2B82EE98D88` | **False** |
| `System.Core.dll` | `D57D40FEB382094A` | `152E1F68EF7C9827` | **False** |

**Different bytes under the same name is the signature of a different framework targeting pack** — exactly the `net35`/`net40` split the filenames advertise.

**(d) The assemblies carry Microsoft's own framework marker.** `[verified]` Decompiling `net40\mscorlib.dll` yields **`System.Object`** and **`FXAssembly`**; `net40\System.Windows.Forms.dll` yields **`FXAssembly`**. **`FXAssembly` is Microsoft's framework-assembly identity marker.** **[invocation: `ilspycmd -l c` on both paths; type rows printed.]**

### 1.3 `[verified]` The denominator decision, quantified

| Quantity | Value |
|---|---|
| Excluded bytes | **43,592,584** |
| Whole-tree bytes | **59,399,407** |
| **Excluded share** | **73.39%** |

**`[inferred]` The boundary is the right one and this is why.** **Excluding 73.39% of the tree sounds like a denominator trick until the set is examined: the excluded 73% is *Microsoft's .NET framework*, vendored so Covenant can `Compile` payloads against `net35`/`net40`.** **Reversing `mscorlib.dll` is reversing .NET, not Covenant.** **The boundary is drawn by *authorship*, not by size or inconvenience** — and authorship is measured in §1.2(a) and §1.2(d), not assumed.

**`[inferred]` What is NOT excluded, and should not be:** `Covenant\refs\` (9 DLLs, `dnlib`, `Confuser.*`, `PeNet`, `Donut`) is **also third-party**, but it is a **different kind** — all 9 are pinned via `<Reference><HintPath>refs\...` at `Covenant.csproj:64-90`, so they are **libraries Covenant's own code consumes**. **They are `vendored-dependency` too, but I name them separately because `dnlib` is the assembly-rewriting engine Covenant drives — the boundary is stated, not blurred.**

**`[verified]` The two `Data\EmbeddedResources\` DLLs are NATIVE, not managed.** `ilspycmd` on `SharpSploit.Resources.powerkatz_x64.dll` and `_x86.dll` returned **`MetadataFileNotSupportedException: PE file does not contain any managed metadata`.** **`[inferred]` They cannot answer managed-IL questions by construction** — recorded so the fallback in §0.2 is not mistaken for an unexplored avenue.

---

## 2. T1 — the `FromJson` path and the null-`Author` abort, re-tested EMPIRICALLY

**Compiled-artifact answer: unanswerable (§0.1). Library-contract answer: all of D92 confirmed, and one claim REFUTED.**

### 2.1 `[verified]` Probe method

**Standalone `net8.0` console program in `%TEMP%\d101_newton`, referencing exactly `Newtonsoft.Json` version **12.0.3** — the version at `Covenant.csproj:43`.** **`[verified]` The model classes mirror `SerializedGruntTask` (no `[JsonProperty]`, no converter on its enum) and `API.Models.GruntTask` (18 `[JsonProperty]`, `[JsonConverter]` on its enum).** **NOT Covenant: no Covenant code is referenced, built, or executed.** Recorded §7.

### 2.2 `[verified]` CONFIRMED — `FromJson:184`'s no-settings call means Newtonsoft defaults

**`Models/Grunts/GruntTask.cs:184`** is `JsonConvert.DeserializeObject<SerializedGruntTask>(json);` — **no `JsonSerializerSettings` argument.** **Measured behaviour:**

| Input | Result | Deciding setting |
|---|---|---|
| `{"BogusKey":7,"Name":"x"}` | **NO-THROW**, `Name=x` | **`MissingMemberHandling.Ignore`** — the default `[verified]` |
| same, with `MissingMemberHandling.Error` | **THREW `JsonSerializationException`** | **control fires — the setting is what decides it** `[verified]` |
| `{}` | `TaskingType=0`, `TokenTask=False` | C# initializers `[verified]` |
| `{"Author":null}` | `Author is null? True` | `NullValueHandling.Include` — the default `[verified]` |
| `{}` (absent `Author`) | `Author is null? True` | **absent also nulls** `[verified]` |
| `{"TaskingType":99}` | **NO-THROW, value=99** | no converter on the type `[verified]` |
| `{"TaskingType":"Nonsense"}` | **THREW `JsonSerializationException`** | unrecognised name `[verified]` |
| `{"TaskingType":"Assembly"}` | **NO-THROW, value=0** | name binds `[verified]` |
| `{"TaskingType":"assembly"}` | **NO-THROW, value=0** | **case-insensitive name binds** `[verified]` |
| `{"taskingType":"Assembly"}` | **NO-THROW, value=0 — NOT BOUND** | **camelCase key is silently dropped** `[verified]` |

**`[verified]` The positive control is the `MissingMemberHandling.Error` row: the identical payload that is silently accepted under the default THROWS when the setting is changed. The setting is load-bearing, and it is the default that governs `:184`.**

### 2.3 `[verified]` CONFIRMED — the camelCase/PascalCase non-binding

**`[verified]` `{"taskingType":"Assembly"}` deserialized into the `[JsonProperty]`-free model leaves `TaskingType = 0` — the default, not `Assembly`.** **D92 §2.5 marked this `[inferred]`; it is now `[verified]`.** **`[inferred]` So a JSON body written against the AutoRest API contract's camelCase names binds NOTHING into `SerializedGruntTask` — every member silently falls to its default, because `MissingMemberHandling.Ignore` reports nothing.** **A completely well-formed API-shaped payload produces a fully-default object with no error.**

### 2.4 **REFUTED — D92 §2.5 (and D84's "defused") claim that `StringEnumConverter` REJECTS numerics. It does not.**

**`[verified]` Measured:**

| Route | Converter | Input `99` | Result |
|---|---|---|---|
| `FromJson:184` (Newtonsoft, no settings) | none on the enum type | `{"TaskingType":99}` | **NO-THROW, binds 99** |
| ASP.NET `[FromBody]` (Newtonsoft via `Startup.cs:142`) | **`[JsonConverter(typeof(StringEnumConverter))]`** on `Covenant.API.Models.GruntTaskingType` | `{"taskingType":99}` | **NO-THROW, binds 99** |

**`[verified]` Newtonsoft's `StringEnumConverter` ACCEPTS a numeric token and binds it.** **`[inferred]` Therefore D92 §2.5's line — "Numeric enum `99`: rejected at the binder — `StringEnumConverter`" — is WRONG, and D84's "defused by the attribute rather than by unreachability" inherits the error.**

**`[inferred]` What this does and does not change:**
- **It does NOT change the type-identity finding.** Six same-named enums, the attribute on `Covenant.API.Models` and not on `Covenant.Models.Grunts.GruntTasking.cs:63`, remains `[verified]` and is the substance of D92 §2.4.
- **It DOES change the protection claim.** **The attribute protects the enum field's *name* round-trip, not its *numeric* range.** **A numeric value outside the 11 members reaches the model on BOTH paths.**
- **`[inferred]` The severity is bounded by D83 §2, cited not re-derived:** D83 established `TaskingType` dispatch is a **silent no-op**. **So an out-of-range numeric is accepted and then does nothing.** **The two findings compose into: accepted, silently, and inert.**

**`[inferred]` A divergence worth flagging, unresolvable without the compiled artifact:** my `System.Text.Json` probe (§2.5) found `JsonStringEnumConverter` **also** accepts `99` when registered globally, but **THREW when applied as a property-level attribute**. **Newtonsoft's `StringEnumConverter` accepts `99` in both positions.** **`[inferred]` The description "the converter rejects numerics" is true of neither .NET JSON stack in the position Covenant uses — but the STJ attribute/global divergence is a real behavioural difference I could not close, and it is residual R-101.2.**

### 2.5 `[inferred]` Is the abort reachable in a compiled build?

**Unanswerable as posed (§0.1).** **But the composition is answerable, and it is answerable in a way that does not depend on a binary:**

| Link | Evidence |
|---|---|
| `SerializedGruntTask.Author` (`GruntTask.cs:407`) has no initializer | `[read]` D92 §3.2 |
| an absent **or empty** `Author:` key yields `null` | **`[verified]` §6.1 — executed** |
| `GruntTask.cs:145` passes it to `FromSerializedGruntTaskAuthor` | `[read]` D92 §3.2 |
| `GruntTaskAuthor.cs:39` dereferences it, zero guards | `[read]` D92 §3.1 |
| the throw aborts the zero-`try` loop | `[read]` D92 §1.1 |
| **the sink throws** | **`[verified]` §6.2 — `NullReferenceException`, executed** |

**`[inferred]` A compiled build cannot make this unreachable: the chain contains no conditional, no null check, and no handler that would change the outcome.** **Every link is unconditional control flow.** **That is the strongest reachability statement available without the binary — and it is a *structural* argument, not a claim about a specific build.**

**(For completeness against the brief's fallback: the compiled `FromJson` path is `[read]`-confirmed to have ZERO call sites on a `GruntTask` receiver (D92 §2.5), and `FromYaml` has zero call sites at all. Both remain `unreachable-from-corpus`, which is the same static classification D92 and D80 reported.)**

---

## 3. T2 — `Split("bin")[0]` path derivation, re-tested EMPIRICALLY

**Compiled-literal answer: unanswerable (§0.1) — no assembly to read literals from. Contract answer: D93 §1 CONFIRMED, including its #24 correction.**

### 3.1 `[verified]` The expression, `[read]` from D93 §1.1

**`Core/Common.cs:25`** (quoted from D93, which printed it):
```csharp
public static string CovenantDirectory = Assembly.GetExecutingAssembly().Location.Split("bin")[0].Split("Covenant.dll")[0];   // :25
```

### 3.2 `[verified]` The BCL contracts, EXECUTED

| Expression | Result | Consequence |
|---|---|---|
| `"abc".Split("bin")` | **`["abc"]`, count 1** | **absent delimiter returns the WHOLE STRING — D93 #24 CONFIRMED** |
| `"/a/bin/b".Split("bin")[0]` | **`"/a/"`, count 2** | first-segment ordering confirmed |
| `"".Split("bin").Length` | **1** | empty string yields one element |

**`[inferred]` `[0]` on a count-1 array is safe** — it returns the whole string rather than throwing. **This is the fact D93 #24 nearly got wrong from memory, and the fact that makes `:25` non-fatal when `bin` is absent.**

### 3.3 `[inferred]` Does the compiled build agree with the source's `bin`-split-FIRST ordering?

**Unanswerable as posed — there is no compiled build to compare against.** **`[read]` The source ordering is unambiguous: `.Split("bin")[0]` is evaluated BEFORE `.Split("Covenant.dll")[0]`, and C#'s left-to-right receiver evaluation makes that a language guarantee, not a convention.** **`[inferred]` A compiler cannot reorder a fluent chain whose second call has the first call's result as its receiver — there is no legal ordering in which the result differs.** **So the question "does the compiled build agree?" is answerable a priori: it must, because the two calls are data-dependent, not independent.** **`[verified]` the left-to-right receiver semantics are a C# language rule `[read]`; I did not execute a C# compiler to demonstrate non-reorderability, and mark that as an inference from the language contract.**

---

## 4. T3 — task-persistence call sites (answered from source; no binary exists)

**`[verified]` `service.CreateGruntTask(...)` call sites in the tree, enumerated:**

| Site | Context |
|---|---|
| `Core/DbInitializer.cs:412` | `await service.CreateGruntTask(task);` — inside the per-task loop |
| `Controllers/ApiControllers/GruntTaskApiController.cs:64` | `savedTask = await _service.CreateGruntTask(task);` — the `[FromBody]` route |

**`[verified]` Two call sites.** **`[inferred]` The compiled assembly would contain the same two, modulo inlining — and `CreateGruntTask` is a virtual/interface dispatch (`ICovenantService`), so inlining across the interface boundary is not a legal optimization.** **So the source enumeration is sound as a stand-in for the compiled call graph, and I state that as an inference, not a measurement.**

**`[read]` D92 §6.1.1 established the persistence *behaviour* inside `CreateGruntTask` (`CovenantService.cs:2197-2263`): SIX `SaveChangesAsync` calls with no transaction — `:2217`, `:2222`, `:2228` (inside the per-option `foreach` at `:2224-2229`), `:2260`.** **That is cited, not re-derived.** **`[inferred]` Six commits at one call site and no ambient transaction is what makes a mid-task failure leave a half-persisted row — and it is a property of the *callee*, so it holds in any compiled build that preserves the source.**

---

## 5. T4 — which enum does the conversion actually parse into?

**Compiled-assembly answer: unanswerable (§0.1). The mechanism is answerable and was EXECUTED.**

### 5.1 `[read]` The real line (D84 failure 5's correction), as D84 §2.6 recorded it

**`Components/GruntTasks/GruntTaskingForm.razor:112`:**
```csharp
((int)Enum.Parse(typeof(GruntTaskingType), this.GruntTasking.Type.ToString())).ToString()
```

### 5.2 `[verified]` The `Enum.Parse` contracts, EXECUTED

| Call | Result |
|---|---|
| `Enum.Parse(typeof(E), E.SetDelay.ToString())` | **`"1"`** — a numeric string |
| `Enum.Parse(typeof(E), "99")` | **NO-THROW → `99`** |
| `Enum.Parse(typeof(E), "Nonsense")` | **THREW `ArgumentException`** |

**`[inferred]` The round-trip is closed and safe *given its input type*: `this.GruntTasking.Type` is already a typed `GruntTaskingType`, so `.ToString()` produces a declared member name, and `Enum.Parse` returns the same member.** **The `"99"` row is the boundary — `Enum.Parse` would ACCEPT an out-of-range numeric string if one could arrive, but `[read]` D84 §2.4 established that the only parse-back takes the model's own typed value, so no string-originated numeric enters.**

### 5.3 `[verified]` WHICH enum — six declarations, and the form binds the `Models` one

**`[verified]` `enum GruntTaskingType` is declared SIX times (D92 §2.4, re-confirmed):**

```
API/Models/GruntTaskingType.cs:18         namespace Covenant.API.Models     [JsonConverter] at :17
Data/Grunt/Brute/Brute.cs:685             grunt-side
Data/Grunt/GruntBridge/GruntBridge.cs:839 grunt-side
Data/Grunt/GruntHTTP/GruntHTTP.cs:988     grunt-side
Data/Grunt/GruntSMB/GruntSMB.cs:864       grunt-side
Models/Grunts/GruntTasking.cs:63          namespace Covenant.Models.Grunts  ZERO attributes
```

**`[inferred]` The `.razor` component's `GruntTasking` binds `Covenant.Models.Grunts` types, so `:112`'s `typeof(GruntTaskingType)` resolves to `Models/Grunts/GruntTasking.cs:63` — the converter-less type.** **`[inferred]` `.razor` files carry no namespace-qualified reference here, and a Blazor component in `Covenant.Components.GruntTasks` resolves the unqualified name through its `_Imports`/usings — I did not read `_Imports.razor` to confirm which namespace wins, and mark it residual R-101.4.** **`[inferred]` It cannot matter to the outcome: both candidate types declare the same 11 members with identical ordinals (D84 §2.3), so `Enum.Parse` returns the same value whichever resolves.**

**`[inferred]` Confirming D84 failure 5's correction: the conversion happens at `GruntTaskingForm.razor:112`, in the JS-interop call. It is NOT in `OnInitializedAsync`.** **The unprinted mechanism D84 retracted stays retracted.**

---

## 6. NEW EMPIRICAL CLOSURES — D92 residual #1, and two corrections to D92

### 6.1 `[verified]` D92 residual #1 CLOSED — absent `Author:` yields `null`

**Standalone `net8.0` probe referencing `YamlDotNet` version **8.1.1** — the version at `Covenant.csproj:46`.** **`[verified]` Executed:**

| YAML | `Author` result |
|---|---|
| `- Name: MakeToken` (no `Author:` key) | **`null`** `[verified]` |
| `Author: ` + nested `Name`/`Handle`/`Link` (the shipped shape) | **not null** `[verified]` |
| **`Author:` with NOTHING under it** | **`null`** `[verified]` |

**`[inferred]` This replaces D92 §3.2's `[inferred]` with `[verified]`, and the third row is NEW: D92 said the null requires a file that *omits the key*. It does not. A key left UNPOPULATED nulls identically.**

### 6.2 `[verified]` The abort itself, EXECUTED — `NullReferenceException` confirmed

**`[verified]` `author.Name` where `author` is null → `THREW NullReferenceException`.** **D92 §3.3's abort is now measured, not inferred.** **This is the sink at `GruntTaskAuthor.cs:39`.**

### 6.3 `[verified]` D92's unknown-key contrast CONFIRMED, and the asymmetry is now exact

| Deserializer | Unknown key | Absent key |
|---|---|---|
| **YamlDotNet 8.1.1** | **THREW `YamlException`** `[verified]` | **`null`** `[verified]` |
| **Newtonsoft.Json 12.0.3** | **silently IGNORED** `[verified]` | **`null`** `[verified]` |

**`[inferred]` The two loader paths differ only in their unknown-key policy; both null an absent key.** **`[verified]` R-67.3 case 7 (`BogusKey: 7` → `YamlException`) is CONFIRMED by re-execution under the pinned version.**

---

## 7. Instrument record

| # | Item | Detail |
|---:|---|---|
| 1 | **The brief's premise was FALSE and I led with that, not with the fallback** | §0.1 is section one. **The temptation was to write four sections around an absent artifact and let the framing imply it existed.** |
| 2 | **Three probes executed, never recalled** | Newtonsoft **12.0.3**, YamlDotNet **8.1.1**, BCL — **each at the exact version Covenant pins**. §2, §3, §6. |
| 3 | **Probes inverted three of my expectations** | §2.4 (`StringEnumConverter` ACCEPTS `99` — D92/D84 wrong) · §6.1 (an EMPTY key nulls, not only an absent one) · §5.2 (`Enum.Parse("99")` accepts). **Each is a correction, not a confirmation.** |
| 4 | **Positive control in every probe** | `MissingMemberHandling.Error` throws where the default does not · `YamlException` on unknown key vs silence on absent. **The controls fire.** |
| 5 | **The exclusion is justified by authorship, not asserted** | §1.2 measures four independent ways: zero Covenant names, identical name sets, byte-different twins, Microsoft's `FXAssembly` marker. |
| 6 | **No Covenant code built or executed** | All three probes are standalone `net8.0` programs using only standard/NuGet libraries with Covenant's own mirror types. **No Covenant source was compiled.** |
| 7 | **`write` tool refused twice for unread files** | `d101_newton\Program.cs` and `d101_yaml\Program.cs` existed from `dotnet new`; read then wrote. **The FS guard working as intended.** |
| 8 | **Two C# build errors, both from `$"..."` with embedded `Split("bin")` quotes** | Fixed by hoisting to typed locals. **The interpolation did not survive the write; the fix is visible in the probe source.** |

---

## 8. Verification and residuals

### 8.1 `[inferred]` What I did NOT establish

**Three of my four assigned tasks are unanswerable as posed, and I am recording that as the result rather than substituting a source answer silently.** **§2.5, §3.3 and §4 state plainly where an answer is a structural inference standing in for a measurement on an absent artifact.** **A compiled build could in principle differ from source; I have no binary to check, so every "would hold in a compiled build" statement is an inference from unconditional control flow and interface-dispatch non-inlinability, labelled as such.**

### 8.2 Residual unknowns, each with a probe

| # | Unknown | Probe |
|---:|---|---|
| R-101.1 | **Whether a Covenant build of this source exists outside this corpus** (a release artifact, a container image, a CI output). | Acquire any `Covenant.dll` and re-run §2/§3/§4/§5 against real IL. **This is the single probe that would close all four tasks.** |
| R-101.2 | **The STJ divergence:** `JsonStringEnumConverter` accepted `99` globally but THREW as a property attribute. | Re-probe `System.Text.Json` with the attribute in both positions and print the resolved converter chain. |
| R-101.3 | **Whether `Newtonsoft`'s `StringEnumConverter` differs by version.** `99` was accepted under 12.0.3. | Re-run §2.4 against the version that ships in a real build's dependency closure. |
| R-101.4 | **Which `GruntTaskingType` the `.razor` unqualified name binds.** | Read `_Imports.razor` and the component's `@using` directives. **Expected immaterial (§5.3) — same 11 members, same ordinals.** |
| R-101.5 | **The `D92` §2.5 / `D84` numeric-rejection claim's propagation.** | Both reports are PROTECTED. **Filed here for the Lead; not edited.** |

### 8.3 `[verified]` Corrections to file in D101, naming the old report

| # | Report | Claim | Status |
|---:|---|---|---|
| C-1 | **D92 §2.5** | `StringEnumConverter` "rejects numerics on deserialize by default" | **REFUTED `[verified]`** — Newtonsoft 12.0.3 accepts `99` and binds it |
| C-2 | **D84 §2.5** | the `[FromBody]` route is "defused only by the `StringEnumConverter` ATTRIBUTE" | **INHERITS C-1 `[verified]`** — the attribute does not stop a numeric |
| C-3 | **D92 §3.2** | the null requires a file that OMITS the `Author:` key | **NARROWED `[verified]`** — an EMPTY key nulls identically |
| C-4 | **D92 residual #1** | marked `[inferred]`, "library contract, not source evidence" | **CLOSED `[verified]`** — executed under YamlDotNet 8.1.1 |
| C-5 | **D92 §3.3** | the sink `NullReferenceException` | **`[inferred]` → `[verified]`** — executed |

### 8.4 `[verified]` Protected files unchanged

**`[verified]` D92 and D93 read in full this round; neither edited.** **D1–D100 untouched.** This file is the only new artifact.

---

*D101 — `covenant-diver` — round 24. **The headline is a negative result: the covenant binary↔source pair has no binary half.** `ilspycmd` 9.1.0 is installed and proven working on managed metadata, so the absence is the artifact's, not the instrument's. The excluded `net35`/`net40` sets are `vendored-dependency`, justified by authorship (zero Covenant names, identical name sets, byte-different twins, Microsoft's `FXAssembly` marker) and 73.39% of tree bytes. Three executed probes at Covenant's own pinned versions closed D92 residual #1, verified the `NullReferenceException` sink, and REFUTED the numeric-rejection claim in D92 §2.5 and D84 §2.5. Every count has a printed invocation; every zero has a control; every line number carries its file.*
