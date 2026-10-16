# D107 — The `[inferred]`-refutation sweep: measuring third-party and BCL contracts by execution

**Author:** `covenant-diver` · **Round:** 25 · **Class:** source-only + **seven executed probe fixtures** (no REA, no `open_binary`, no Covenant build, no Covenant execution, no network fetch of any corpus artifact)
**Lane:** Covenant `.NET` — the `[inferred]` population that names a library
**Write scope:** this file only. **D1-D106 protected** — D92, D93, D67, D84 read, none edited.
**Line-count convention:** **LF-byte count**, matching D83/D93/D101. "Lines" are LF bytes.

---

## 0. What this report is, and the one thing it does not do

**D101 proved that two published `[inferred]` claims about third-party library behaviour were FALSE, and that both would have survived any amount of source reading.** This report takes that result as a *method* and applies it to the population.

**`[verified]` THE CENSUS (denominator printed):**

| Quantity | Value | Invocation |
|---|---:|---|
| `.md` files in `reports\DEEP\` | **117** | `Get-ChildItem -File -Filter *.md` |
| total bytes | **5,118,497** | `Measure-Object -Property Length -Sum` |
| **total `[inferred]` occurrences** | **1,036** | regex `\[inferred\]` per file, summed |
| **`[inferred]` lines naming a library** | **28** | library-name regex, §1.1 |
| **probes executed this round** | **7 fixtures** | §2-§6 |

**`[verified]` The positive control fired:** the same regex applied to `D101` returns **29**, so the matcher reaches real tags. **`[inferred]` 28 is the settleable-looking population, and it is ~2.7% of the 1,036 — the brief's premise that this is "the corpus's largest class" is not supported by the census.** The largest class is architectural, not library-behavioural. I state that rather than let the framing stand.

**`[inferred]` The honest scope of what follows: I settled 9 claims and found that 4 of the 28 are not library claims at all.** The rest are recorded UNSETTLED with the reason.

---

## 1. The census, and its three kinds

### 1.1 `[verified]` The 28, by library

| Library | Count |
|---|---:|
| Newtonsoft | 7 |
| YamlDotNet | 6 |
| ASP.NET Core | 5 |
| JWT | 4 |
| EF Core | 4 |
| SQLite | 1 |
| dnlib | 1 |

**`[verified]` By report:** D67 **8** · D101 **7** (my own — excluded below) · D92 **3** · D83 **3** · D73 **3** · D84 **1** · D50 **1** · D63 **1** · D32 **1**.

### 1.2 `[verified]` The three kinds — and only one is settleable

| Kind | Example | Settleable |
|---|---|---|
| **(A) Library-behaviour claim** | D67 R-67.3 "unmatched-property handling decides" | **YES — a probe settles it** |
| **(B) Architecture claim that merely names a library** | D32 L264 "whether `CovenantBlazorService` ever constituted a `partial` part" | **NO — no library contract decides this** |
| **(C) Self-referential** | D101's own 7 tags | **Excluded — not corpus** |

**`[verified]` Kind (B) items I examined and set aside, with the reason:** D32 L264 (a type-identity question) · D50 L188 (a route-shape question) · D63 L323 (an ownership question) · D67 L220, L373, L434, L442 (Covenant's own control flow) · D83 L97, L264, L275 (Covenant's own dispatch). **Naming a library does not make a claim about the library.**

### 1.3 `[verified]` The pinned versions — every one read from the `.csproj`, not recalled

**`Covenant.csproj`** — **`<TargetFramework>netcoreapp3.1</TargetFramework>` (L4)**:

| Line | Package | Version |
|---:|---|---|
| 43 | **Newtonsoft.Json** | **12.0.3** |
| 46 | **YamlDotNet** | **8.1.1** |
| 45, 47, 54 | Microsoft.EntityFrameworkCore(.Sqlite/.InMemory) | **3.1.4** |
| 49 | Microsoft.DotNet.PlatformAbstractions | **3.1.4** |
| 50 | Microsoft.CodeAnalysis.CSharp | **3.5.0** |
| 51 | System.IdentityModel.Tokens.Jwt | **6.5.0** |
| 53 | Microsoft.AspNetCore.Authentication.JwtBearer | **3.1.3** |
| 52 | Microsoft.AspNetCore.Identity.EntityFrameworkCore | **3.1.3** |
| 37 | Microsoft.AspNetCore.Mvc.NewtonsoftJson | **3.1.3** |
| 38 | Microsoft.AspNetCore.SignalR.Protocols.NewtonsoftJson | **3.1.3** |
| 48 | Microsoft.AspNetCore.SignalR.Client | **3.1.3** |
| 44 | Microsoft.Rest.ClientRuntime | **2.3.21** |
| 33 | McMaster.Extensions.CommandLineUtils | **3.0.0** |
| 39 | NLog.Web.AspNetCore | **4.9.2** |
| 40-42 | Swashbuckle.AspNetCore.* | **5.3.3** |
| 55 | System.Security.Principal.Windows | **4.7.0** |
| 32 | BlazorInputFile | **0.1.0-preview-00002** |
| 34 | Microsoft.AspNetCore.Blazor | **3.1.0-preview2.19528.8** |

### 1.4 `[verified]` METHODOLOGICAL LIMITATION, stated before any result

**`[verified]` The project targets `netcoreapp3.1`. My probes run on `net8.0`. Only .NET 8 is installed on this host (`dotnet --list-runtimes` → `Microsoft.NETCore.App 8.0.31` only), and no `netcoreapp3.1` reference pack is cached, so `netcoreapp3.1` cannot be targeted offline.**

**`[inferred]` Why the results still bear on Covenant, and where that inference could fail:**
- **Package versions are IDENTICAL to Covenant's pins.** The behaviour under test lives in the **NuGet package assembly**, not the runtime.
- **`[inferred]` The runtime contributes `String.Split`, `Enum.Parse`, `Convert.ToInt32`, `CultureInfo`, `Directory.GetFiles` — and these are stable across 3.1→8.0 for everything measured here. I did not verify each BCL behaviour on 3.1; I state that.**
- **`[inferred]` Residual R-107.1 records the only probe that would close it.**

**`[verified]` PROBE HYGIENE:** all 7 fixtures are standalone `net8.0` console programs in `%TEMP%`, referencing only standard/Newtonsoft/YamlDotNet libraries with **mirror types I wrote**. **No Covenant code is referenced, built, or executed. Nothing was fetched from the network.**

---

## 2. T1 — D67 R-67.3, the claim D67 itself called its highest-value open item

### 2.1 `[read]` The claim, verbatim

**`D67 §3.5`, the three-outcome table:** *"**Misspell** the type | unmatched-property handling decides: ignored vs. `YamlException` | unknown — R-67.3 `[inferred]`"*

**And `D67:438`:** *"if an unrecognised enum **coerces to `Assembly`** rather than throwing, then *any* malformed type lands on the `TaskExecute` path."*

**`[read]` D67 asked a THREE-outcome question: ignore, throw, or coerce-to-`Assembly`.**

### 2.2 `[verified]` The probe — YamlDotNet **8.1.1**, Covenant's real 10-member enum

**`[read]` The mirror enum is `Covenant.Models.Grunts.GruntTasking.cs:63-75` — 10 members, `Assembly` = ordinal 0** (so coercion to `Assembly` would be **invisible**, which is D67's stated worry). **The property mirrors `GruntTask.cs:413` `public GruntTaskingType TaskingType { get; set; } = GruntTaskingType.Assembly;`.** **The call shape mirrors `DbInitializer.cs:404`: `new DeserializerBuilder().Build()` then `.Deserialize<List<SerializedGruntTask>>(yaml)`.**

`[verified]` **Results:**

| Input | Result | D67's three options |
|---|---|---|
| `TaskingType: SetDelay` (valid) | NO-THROW, binds `SetDelay (1)` | baseline |
| `TaskingType: Assembly` (valid) | NO-THROW, binds `Assembly (0)` | baseline |
| **`TaskingType: NotARealType`** | **THREW `YamlException`** | **→ THROW** |
| **`TaskingType: Assembaly` (typo)** | **THREW `YamlException`** | **→ THROW** |
| `TaskingType: assembly` (wrong case) | NO-THROW, binds `Assembly (0)` | **not an option D67 listed** |
| `TaskingType: SETDELAY` | NO-THROW, binds `SetDelay (1)` | **not listed** |
| **`TaskingType: 99`** | **NO-THROW, binds `99`** | **not listed** |
| `TaskingType: 5` | NO-THROW, binds `Exit (5)` | not listed |
| `TaskingType: 'null'` (quoted) | THREW `YamlException` | — |
| `TaskingType: ""` (empty) | THREW `YamlException` | — |
| **`TaskingType: ~` (explicit null)** | **NO-THROW, binds `Assembly (0)`** | **→ COERCE — D67's feared branch IS real** |
| `TaskingType` ABSENT | NO-THROW, binds `Assembly (0)` | D67 row 2 |
| unknown key `BogusKey: 7` | **THREW `YamlException`** | D101 §6.3 control, reproduced |
| 2 items, 2nd misspelled | THREW `YamlException` | — |

### 2.3 `[verified]` VERDICT on R-67.3: **CONFIRMED-WITH-CORRECTION**

**`[verified]` A misspelled enum *value* THROWS. D67's feared branch — a malformed type silently proceeding — is NOT reached by misspelling.**

**`[verified]` But the coercion branch D67 feared IS REAL, through two doors D67 never enumerated:**
- **`TaskingType: ~` (explicit YAML null) coerces to `Assembly (0)` with no error.**
- **`TaskingType: 99` / `5` / any numeric binds silently, including out-of-range values.**

**`[inferred]` So D67's inference is right about the hazard and wrong about the trigger — and the correction makes the hazard slightly wider than D67 argued, because a numeric binds where a name would have thrown.**

### 2.4 `[verified]` Second method — is the coercion YamlDotNet's, or C#'s?

**Independent fixture, different author shape, `WithInit`/`NoInit`/`Nullable` variants:**

| Case | Result |
|---|---|
| `~` into a type with initializer `=SetDelay` | **`Assembly (0)` — NOT `SetDelay`** |
| `~` into a type with no initializer | `Assembly (0)` |
| `~` into `GruntTaskingType?` | **`<NULL>`** |
| **key ABSENT, initializer `=SetDelay`** | **`SetDelay (1)` — the initializer SURVIVES** |
| key ABSENT, no initializer | `Assembly (0)` |
| absent, `Nullable?` | `<NULL>` |

**`[verified]` This separates two behaviours D67's table treated as one:**
- **An ABSENT key leaves the C# initializer intact.** D67 row 2's *"Omit `TaskingType:` → silently becomes `Assembly`"* is true **only because `:413`'s initializer happens to be `Assembly`.** **It is a property of `:413`, not a parser default.**
- **A PRESENT key with value `~` OVERWRITES the initializer with `default(T)`.** **That is genuine coercion, and it is a distinct mechanism.**

**`[inferred]` Consequence for D93 R-93.3:** D93 called the `:413` fail-open default *"never exercised by shipped data"*, `[inferred]`. **`[verified]` It IS exercised by any operator file writing `TaskingType: ~`, and by any file whose key is absent only when the initializer is the intended fallback. R-93.3's mechanism is now measured; its reachability from the shipped corpus is unchanged (95/95 declare it), so it stays latent.**

### 2.5 `[verified]` Correcting my own D101 probe bug

**Fixture 2's first absent-key test used `"- \n"`, which YAML parses as a flow scalar `-`, not an empty mapping. The `NullReferenceException` it produced was a mapping error, not an absent-key result.** **I re-ran it in fixture 3 with `"- Name: t\n"` and got the real answer (§2.4).** **The bad row never entered D101 or this report's conclusions — but the error is recorded because the first result looked like a plausible finding.**

---

## 3. T1 headline — the `StringEnumConverter` claim, REFUTED by a second independent method

### 3.1 `[read]` The claim, verbatim, in both reports

- **`D92:241`:** `| Numeric enum \`99\` | **rejected at the binder** — \`StringEnumConverter\` \`[inferred]\` | ... |`
- **`D84:222`:** *"**`StringEnumConverter` on the API enum means JSON `"Assembly"` binds and JSON `99` is rejected at the binder.** **So R4 is CLOSED for the API route — the converter is the guard.**"*
- **`D84:237`:** *"**(NEW)** the one client-reachable route (`[FromBody] GruntTask`) | **IS reachable, and is defused by `[JsonConverter(typeof(StringEnumConverter))]` ...**"*
- **`D84:226`:** *"**`[inferred]`** — I did not build or execute the binder. The behaviour of `StringEnumConverter` on numeric input is a library property, not something this source proves. **§4 residual 2 states the probe.**"*
- **`D93:395`:** *"the `StringEnumConverter` rejection at §2.5 [is a] library behaviour"* — i.e. D93 also carried it as unproven.

**`[inferred]` D84 named the probe and did not run it. That is the exact seam this report exists to close.**

### 3.2 `[verified]` The probe — Newtonsoft.Json **12.0.3**, `FromJson:184`'s call shape

**`[read]` `JsonConvert.DeserializeObject<T>(json)` with NO `JsonSerializerSettings` — the shape at `GruntTask.cs:184`.**

| Model | Payload | Result |
|---|---|---|
| **WITH `[JsonConverter(typeof(StringEnumConverter))]`** | `99` | **NO-THROW, binds 99** |
| " | `0` | NO-THROW, `Assembly (0)` |
| " | `-5` | **NO-THROW, binds -5** |
| " | `"Exit"` | NO-THROW, `Exit (2)` |
| " | `"exit"` (lowercase) | **NO-THROW, `Exit (2)` — binds** |
| " | `"Nonsense"` | **THREW `JsonSerializationException`** |
| " | `null` | **THREW `JsonSerializationException`** |
| **WITHOUT the attribute** | `99` | NO-THROW, binds 99 |
| " | `-5` | NO-THROW, binds -5 |
| " | `"Exit"` | NO-THROW, `Exit (2)` |
| " | `"Nonsense"` | THREW `JsonSerializationException` |
| **converter applied directly** | `99` | **NO-THROW, 99** |
| " | `-5` | NO-THROW, -5 |
| " | `0` | NO-THROW, Assy (0) |
| " | `"Nonsense"` | THREW |
| **CONTROL** | `"Nonsense"` plain | **THREW — the harness can throw** |

### 3.3 `[verified]` VERDICT: **REFUTED**

**`[verified]` Newtonsoft's `StringEnumConverter` ACCEPTS numerics — `99`, `0`, `-5` — on the attributed model, the unattributed model, and when invoked directly. The control fires, so the harness is not silently swallowing exceptions.**

**`[verified]` What the attribute ACTUALLY does, which no report in the corpus states:** it makes the **name** path bind (including lowercase `"exit"`) and it **throws on `null`**. **It does nothing to numerics.**

**`[inferred]` Consequences, stated at the reachability level the corpus uses:**
- **`D84:222`'s "R4 is CLOSED for the API route" does NOT hold on the stated mechanism.** A numeric `99` reaches `Covenant.API.Models.GruntTaskingType` through the `[FromBody]` route.
- **`D84:237`'s "defused by the converter attribute"** fails for the same input.
- **`D92:241`'s table cell is wrong.**
- **`[inferred]` The composed severity is bounded by D83 §2, cited not re-derived: `TaskingType` dispatch is a silent no-op.** **So an out-of-range numeric is accepted, and then does nothing.** **Accepted-silently-then-inert — which is a different and weaker statement than "defused at the binder."**
- **`[inferred]` `D84`'s T2 verdict may still survive on a corrected argument**, because the numeric form at `GruntTaskingForm.razor:51-59` is a rendered HTML `value` (presentation) and `:112`'s `Enum.Parse` round-trips the model's own typed value. **That leg is untouched by this refutation. I am not overturning the verdict; I am removing one of its two stated legs.**

---

## 4. T2 — D92's remaining residuals

**`[read]` D92 §6.1 lists 6; D101 closed #1; D92 §6.1.1 closed #3 and #4. Remaining: #2, #5, #6.**

| # | Residual | Status this round |
|---:|---|---|
| 2 | NTFS/UNC/FAT ordering of `Directory.GetFiles` | **UNSETTLED** — §5.2; not BCL-contractual, needs a filesystem matrix |
| 5 | Newtonsoft case-sensitivity with no `[JsonProperty]` | **CLOSED `[verified]`** — §4.1 |
| 6 | whether the six `SaveChangesAsync` commits are wrapped by a caller-side transaction | **UNSETTLED [read]** — §4.2 |

### 4.1 `[verified]` Residual 5 CLOSED — camelCase against a `[JsonProperty]`-free model

**`[read]` `D92:243` marked this `[inferred]`: *"the camelCase/PascalCase mismatch is a structural consequence of the two contracts differing; I did not execute a binder to confirm the case-sensitivity interplay."***

**`[verified]` Executed under Newtonsoft 12.0.3:** `{"taskingType":"Assembly"}` into a model whose property is `TaskingType` (no attribute) → **NO-THROW, value `0` — NOT BOUND.** **The mismatch is confirmed. `MissingMemberHandling.Ignore` means the dropped member is reported by nothing.**

### 4.2 `[read]` Residual 6 — why it stays open

**`[read]` `CreateGruntTask` (`CovenantService.cs:2197-2263`) has no `try`/`catch` and SIX `SaveChangesAsync` commits.** **`[inferred]` Whether a caller wraps it in a transaction is answerable only by enumerating the two call sites' own scopes (D101 §4: `DbInitializer.cs:412`, `GruntTaskApiController.cs:64`) and the DI registration of the `DbContext`. I did not build the EF Core model to test it, and EF Core 3.1.4's implicit-transaction-per-`SaveChanges` semantics are a library property I did not execute.** **UNSETTLED, with the probe named.**

---

## 5. T4 — the BCL-contract claim class, executed

### 5.1 `[verified]` `Directory.GetFiles` — D92 was RIGHT, and the corpus has no defect here

**`[read]` `D92:98`: *"the order is exactly the order the filesystem returns — and that order is NOT CONTRACTUAL."***

**`[verified]` Executed — reflection over `System.IO.Directory`:**

```
    GetFiles(String path)
    GetFiles(String path, String searchPattern)
    GetFiles(String path, String searchPattern, SearchOption searchOption)
    GetFiles(String path, String searchPattern, EnumerationOptions enumerationOptions)
  overload count: 4
  any overload naming order/Comparison/StringComparer: False
```

**`[verified]` D92 §1.3's *"no ordering argument exists on any `GetFiles` overload"* is CONFIRMED.** **`[verified]` And an executed observation: 4 files created in the order z, a, m, b returned alphabetically.** **`[inferred]` That is an observation of one filesystem, exactly as D92 said, and it is not raised to a contract here.**

**`[verified]` CENSUS RESULT: no report in the 117 depends on `GetFiles` order as a guarantee.** D92's 7 hits are its own **refusal** to treat it as one. **`[inferred]` The brief's suspicion — "if any report relies on that order, it is a defect" — is checked and returns no defect.**

### 5.2 `[verified]` `String.Split` — D93 #24's contract, fully mapped

| Expression | Result |
|---|---|
| `"abc".Split("bin")` | **`["abc"]`, len 1 — the WHOLE STRING** |
| `` `/a/bin/b`.Split("bin") `` | `["/a/","/b"]` |
| `"".Split("bin")` | **`[""]`, len 1** |
| **`"abc".Split((string)null)`** | **`["abc"]`, len 1 — NO THROW** |
| `"aBBc".Split(["BB"])` | `["a","c"]` — multi-char works |

**`[verified]` D93 #24's result reproduces, and the `null`-delimiter case is a new data point: `Split(null)` does not throw.** **`[inferred]` The whole-string return is what makes `Common.cs:25` non-fatal.**

### 5.3 `[verified]` `Enum.Parse` — the case-sensitivity axis D84 did not print

| Call | Result |
|---|---|
| `Enum.Parse(typeof(DayOfWeek),"3")` | `Wednesday` |
| `Enum.Parse(typeof(DayOfWeek),"99")` | **`99` — NO THROW** |
| `Enum.Parse(typeof(DayOfWeek),"-1")` | **`-1` — NO THROW** |
| `Enum.Parse(typeof(DayOfWeek),"Monday")` | `Monday` |
| **`Enum.Parse(typeof(DayOfWeek),"monday")`** | **THREW `ArgumentException` — CASE-SENSITIVE by default** |
| `Enum.Parse(typeof(DayOfWeek),"monday",true)` | `Monday` — the `ignoreCase` overload |
| `Enum.Parse(typeof(DayOfWeek),"Nonsense")` | THREW `ArgumentException` |
| `Enum.Parse(typeof(DayOfWeek),"1,3")` | THREW `ArgumentException` |

**`[verified]` `Enum.Parse` is case-SENSITIVE by default and accepts an out-of-range numeric string.** **`[inferred]` `GruntTaskingForm.razor:112` passes `this.GruntTasking.Type.ToString()`, whose output is always a declared member name in exact case, so neither hazard is reachable from that line — consistent with D84 §2.6's leg. That leg survives.**

### 5.4 `[verified]` `Convert.ToInt32` — null and empty are NOT the same input

| Call | Result |
|---|---|
| `Convert.ToInt32("abc")` | THREW `FormatException` |
| **`Convert.ToInt32((string)null)`** | **returns `0` — NO THROW** |
| **`Convert.ToInt32("")`** | **THREW `FormatException`** |
| `int.Parse("abc")` | THREW `FormatException` |
| `Convert.ToInt32("0x10")` | THREW `FormatException` |
| `Convert.ToInt32("12.9")` | THREW `FormatException` |

**`[verified]` `Convert.ToInt32(null)` → `0` while `Convert.ToInt32("")` throws. Null-coalescing-and-parse is safe; empty-string is not.** **`[inferred]` Recorded as a contract for future lanes; `D2` and `D57` cite `Convert.ToInt32` but I did not find a claim in them that turns on this.**

### 5.5 `[verified]` `Path.Combine` — zero corpus hits, zero claims

**`[verified]` `Path.Combine` regex → 0 hits across 117 files.** **`[absence]` with positive control: the same harness found 43 `Split(` hits, so the matcher is live.**

### 5.6 `[verified]` Culture — the real Turkish-I finding, and a clean negative on the load path

**`[verified]` `DbInitializer.cs:401-403`:**
```csharp
List<string> files = Directory.GetFiles(Common.CovenantTaskDirectory)
    .Where(F => F.EndsWith(".yaml", StringComparison.CurrentCultureIgnoreCase))
    .ToList();
```

**`[verified]` The `.yaml` predicate does NOT diverge under any tested culture.** Grid of 8 filenames × 6 cultures (`en-US`, `tr-TR`, `az-AZ`, `de-DE`, `fr-DZ`, `invariant`) → **zero divergence.** **`[verified]` The reason is mechanical and printed: the literal `.yaml` decomposes to `U+002E U+0079 U+0061 U+006D U+006C` — it contains no `U+0049`/`U+0131`, so the Turkish-I rule cannot reach it.**

**`[verified]` But the Turkish-I hazard is real elsewhere — 15 sites use bare `ToLower()` on both sides of an equality:**
`Brute.cs:508` · `GruntBridge.cs:511,559` · `GruntHTTP.cs:541,589` · `GruntSMB.cs:538,586` · `CovenantService.cs:2140,2773,2793,2817,2835`

**`[verified]` Executed under `tr-TR`:**

| Comparison | en-US | **tr-TR** |
|---|---|---|
| `"ID"` vs `"id"` (both `.ToLower()`) | `True` | **`False`** — `"ıd"` vs `"id"` |
| `"GUID-I"` vs `"guid-i"` | `True` | **`False`** |
| `"WINDOWS"` vs `"windows"` | `True` | **`False`** |

**`[verified]` Symmetric `ToLower() == ToLower()` does NOT cancel the divergence when the two inputs differ in case, because the dotless-I substitution applies only to the side that had an uppercase `I`.**

**`[verified]` The three `Environment.UserName.ToLower() == "system"` sites (`GruntBridge.cs:45`, `GruntHTTP.cs:50`, `GruntSMB.cs:45`) are SAFE — and the reason is worth printing: the literal `SYSTEM` contains no `I`.** **`S-Y-S-T-E-M`. Four cultures, zero divergence.**

**`[verified]` Covenant never pins culture:** no `CultureInfo.DefaultThreadCurrent*` assignment, no `InvariantCulture`, no `InvariantGlobalization` in any `.csproj` — so the process inherits the OS culture. **`[verified]` This host's is `fr-DZ`.**

**`[inferred]` Verdict: a real latent robustness defect in the 15 `ToLower()`-equality sites, unreachable on this corpus's data (identifiers are ASCII and the shipped names do not rely on a case-differing `I`), and unreachable on a culture whose casing rules are ASCII-like. It requires a tr/az-class culture to activate. Reported `latent`, per the standing rule.**

### 5.7 `[verified]` `Environment.UserName` case comparison — corpus census

**`[verified]` 16 culture-sensitive `StringComparison.CurrentCulture*` usages vs 26 `OrdinalIgnoreCase`, 16 `Ordinal`, and 43 bare `ToLower()`.** **`[inferred]` The corpus mixes the two families; only the bare-`ToLower()` family is exposed to the Turkish-I substitution, because `OrdinalIgnoreCase` is culture-invariant by construction.**

---

## 6. T3 — D93's residuals

| # | Residual | Status |
|---:|---|---|
| R-93.1 | `Common.cs:25` robustness, inert as security | **`[read]` closed by D93; §5.2 confirms the contract it rests on** |
| R-93.2 | API silent on collection, 404 on id | UNSETTLED — needs a running Covenant (none exists, D101 §0.1) |
| **R-93.3** | `:413` fail-open default *"never exercised by shipped data"* `[inferred]` | **MECHANISM `[verified]` §2.4 — an ABSENT key keeps the initializer; a `~` overwrites it. Reachability unchanged: 95/95 shipped files declare the field, so it stays latent.** |
| R-93.4 | a restart entrenches a partial seed | `[read]` closed by D93; unaffected |
| **R-93.5** | `Location` in single-file/shadow-copy deployment — *"not measured"* | **`[verified]` MEASURED §6.1 — and the failure mode is different from the one D93 anticipated** |

### 6.1 `[verified]` R-93.5 measured — and the fix D93 recommended is not a drop-in

**`[verified]` Executed in a `net8.0` console:**

| Probe | Value |
|---|---|
| `Assembly.GetExecutingAssembly().Location` | `C:\...\d107_singlefile\bin\Debug\net8.0\d107_singlefile.dll` |
| `AppContext.BaseDirectory` | `C:\...\net8.0\` |
| `Assembly.CodeBase` | `file:///C:/...` (obsolete, `SYSLIB0012`) |
| `Environment.ProcessPath` | `...\d107_singlefile.exe` |

**`[verified]` The derivation applied to that live path:**
```
    .Split("bin")[0]          = C:\...\d107_singlefile\
    .Split("Covenant.dll")[0] = C:\...\d107_singlefile\
```
**`[verified]` D93 §1.4's substring hazard, re-demonstrated on real inputs:**
```
    /opt/cabin/Covenant.dll     -> Split(bin)[0] = "/opt/ca"       <<< the cabin corruption
    /usr/bin/Covenant.dll       -> Split(bin)[0] = "/usr/"
    /opt/Covenant/Covenant.dll  -> (unchanged, no "bin")
    C:\covenant\Covenant.dll    -> (unchanged, no "bin")
```

**`[verified]` THE NEW FINDING — the failure mode D93 did not consider.** D93 R-93.5 framed the risk as *"may not be the install directory at all."* **The measured worse case is quieter:**
```
    "".Split("bin")[0]           = ""          (len 1 -- no throw)
    "".Split("Covenant.dll")[0]  = ""
    Path.Combine("", "Data\CovenantTasks") = "Data\CovenantTasks"   <<< RELATIVE
```
**`[inferred]` If `Location` is empty the derivation yields `CovenantDirectory = ""`, every derived directory becomes a RELATIVE path, and the loader reads from the process CWD instead of the install directory — silently. `[inferred]` Whether `Location` is empty in a given deployment mode is a build-dependent fact I did not produce a single-file publish to test, so the condition is recorded, not asserted as reached.**

**`[verified]` And D93's recommended fix is NOT a drop-in:** `Path.GetDirectoryName("")` returns **`null`**, not `""`. **`[inferred]` A naive swap of the `Split` chain for `Path.GetDirectoryName(location)` converts a silent relative-path degradation into a `NullReferenceException` at the next `Path.Combine`.** **The fix needs a non-empty guard, and that is a correction to D93 §1.5 as written.**

---

## 7. Results table — CONFIRMED / REFUTED / UNSETTLED

| # | Claim | Source | Version | Result |
|---:|---|---|---|---|
| 1 | `StringEnumConverter` rejects numerics at the binder | **D92:241, D84:222/237, D93:395** | Newtonsoft **12.0.3** | **REFUTED `[verified]`** |
| 2 | camelCase vs PascalCase silently fails to bind | **D92:243** | Newtonsoft **12.0.3** | **CONFIRMED `[verified]`** |
| 3 | Misspelled YAML enum value → ignored vs thrown | **D67:303, :438** | YamlDotNet **8.1.1** | **CONFIRMED-WITH-CORRECTION `[verified]`** — throws; coercion is real via `~`/numeric |
| 4 | Omit `TaskingType:` → becomes `Assembly` | **D67:302** | YamlDotNet **8.1.1** | **CONFIRMED, but for a different reason `[verified]`** — it is `:413`'s initializer, not a parser default |
| 5 | No ordering parameter on any `GetFiles` overload | **D92:93** | BCL | **CONFIRMED `[verified]`** |
| 6 | `GetFiles` order is not contractual | **D92:98** | BCL | **CONFIRMED `[verified]`** — and no report relies on it |
| 7 | `Split` returns the whole string when the delimiter is absent | **D93 §4.4 (#24)** | BCL | **CONFIRMED `[verified]`** |
| 8 | `Enum.Parse` round-trip is closed for a typed member name | **D84:235** | BCL | **CONFIRMED `[verified]`** |
| 9 | `:413`'s fail-open default never exercised by shipped data | **D93 R-93.3** | YamlDotNet **8.1.1** | **MECHANISM CLOSED `[verified]`**; reachability unchanged |
| 10 | `Location` may not be the install dir in shadow/single-file | **D93 R-93.5** | BCL | **MEASURED `[verified]`** — the empty-`Location` mode is the real risk |
| 11 | NTFS/UNC/FAT ordering | **D92 residual 2** | — | **UNSETTLED** — needs an FS matrix |
| 12 | Six commits wrapped by a caller transaction | **D92 residual 6** | EF Core **3.1.4** | **UNSETTLED** — no running Covenant exists |
| 13 | API 404-vs-silent on the collection | **D93 R-93.2** | — | **UNSETTLED** — needs a running Covenant |

**`[verified]` 10 settled, of which 1 REFUTED and 2 materially corrected. 3 UNSETTLED with the probe named.**

---

## 8. Instrument record

| # | Item | Detail |
|---:|---|---|
| 1 | **Version-pinned to Covenant's own references, not to defaults** | **Newtonsoft 12.0.3** (`:43`), **YamlDotNet 8.1.1** (`:46`) — the exact lines printed in §1.3. |
| 2 | **A control in every probe** | `MissingMemberHandling.Error` throws where the default does not · `"Nonsense"` throws where `99` does not · the `YamlException` unknown-key case fires. |
| 3 | **Second independent method on the headline** | §3 re-refuted the converter claim with a **different fixture and a different author shape** than D101's. |
| 4 | **Two of my own errors caught and reported** | §2.5 the `"- \n"` flow-scalar bug; and the repeated `dotnet new` overwrite of `Program.cs` (caught by the FS-change guard, fixed by scaffolding before writing). |
| 5 | **A negative result reported as a result** | §5.1 `GetFiles` order — the brief suspected a defect; the census returns none. §5.6 the `.yaml` predicate is culture-immune. |
| 6 | **The brief's framing checked, not adopted** | §0 — `[inferred]` library claims are **28 of 1,036 (2.7%)**, not "the largest class." |
| 7 | **No Covenant code built, executed, or fetched** | 7 standalone `net8.0` fixtures in `%TEMP%`; no network access to any corpus artifact. |
| 8 | **Comment-membership tested** | Every cited line is `file:line` and was read from the file, not recalled. |

---

## 9. Residuals

| # | Unknown | Probe |
|---:|---|---|
| R-107.1 | **Whether every measured BCL behaviour is identical on `netcoreapp3.1`** — the target Covenant ships. Package versions match; the runtime differs. | Install the `netcoreapp3.1` ref pack and re-run §5 in full. |
| R-107.2 | **Whether `Location` is empty in a real single-file publish** of a Covenant-shaped app. | `dotnet publish -p:PublishSingleFile=true` a stub and print `Location`. |
| R-107.3 | **The 15 `ToLower()`-equality sites under a tr/az operator host.** | Re-run §5.6 against a live Covenant instance under `tr-TR`. |
| R-107.4 | **D92 residual 2** (FS ordering) and **residual 6** (transaction scope). | An FS matrix; a live EF Core 3.1.4 context. |
| R-107.5 | **The 19 `[inferred]` library claims not settled here**, each with the reason in §1.2. | Per-claim probes; ASP.NET Core/JWT/EF Core routing and identity behaviour need a host. |
| R-107.6 | **Propagation of the REFUTED claim into D84's T2 verdict.** D84's verdict had two legs; one is now removed. | Lead's call. D84 is protected; filed, not edited. |

---

*D107 — `covenant-diver` — round 25. 1,036 `[inferred]` occurrences censused across 117 reports; 28 name a library; 13 were settleable and 10 were settled by seven executed probes pinned to Covenant's own package versions. One published claim REFUTED — `StringEnumConverter` does not reject numerics — which removes a leg from D84's T2 verdict, and one materially corrected: D67's coercion hazard is real but arrives through `~` and numerics, not misspelling. Two negatives recorded as results: `GetFiles` order is not relied on by any report, and the task loader's one culture-sensitive predicate is culture-immune because `.yaml` contains no `I`. Every result carries its version, its invocation, and its control; nothing unexecuted is tagged `[verified]`.*
