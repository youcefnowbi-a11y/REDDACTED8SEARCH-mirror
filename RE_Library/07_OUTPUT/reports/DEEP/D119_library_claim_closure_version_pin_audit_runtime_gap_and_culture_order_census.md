# D119 — The library-claim closure: every `[inferred]` library claim resolved, the version pin audited, and the runtime gap quantified

**Author:** `covenant-diver` · **Round:** 26 · **Class:** source-only + **four executed fixtures** (no REA, no `open_binary`, no Covenant build or execution, no network, no live C2)
**Lane:** Covenant `.NET`
**Write scope:** this file and `D107` (one-character-class repair, §7). **D84, D67, D93, D101, D92 corrected by reference and NOT edited.**
**Allocation:** `D119` verified free by enumeration before writing — §0.1.
**Line-count convention:** **LF-byte count**, matching D83/D93/D101/D107.

---

## 0. Allocation, and what the Lead's list got wrong

### 0.1 `[verified]` `D119` confirmed free — and the list I was given was incomplete

**The Lead said: *"On disk I read D100–D108, D110, D111, D113, D114, D115; D112, D116, D117, D118 are in flight. So D119 should be free — verify, don't trust my list."***

**`[verified]` Enumeration result:**

| Lead's claim | Measured |
|---|---|
| D100–D108 on disk | **D103, D106, D108 also on disk** — the Lead's read stopped at D108 but named only D100–D108 *and* D110/D111, implying D112 onward |
| **D112 in flight** | **`D112_pclntab_lane_open_…` IS ON DISK** (493 B-titled, present) |
| D116 in flight | **not present** — genuinely in flight |
| **D117 in flight** | **`D117_havoc_client_agent_discriminant_…` IS ON DISK** |
| D118 in flight | **not present** — genuinely in flight |
| **D119 free** | **CONFIRMED FREE** — no file anywhere under `RE_Library` matches `^D119` |

**`[verified]` `D119` is free and is claimed.**

### 0.2 `[verified]` The numbering collision class is worse than reported, and it is not a collision — it is a namespace split

**`[verified]` `D11` maps to FIVE files:**
`D11_havoc_native_win32.md` · `D11_merlin_binaries.md` · `D11_mythic_crypto_postresponse.md` · `D11_pupy_transport_crypto.md` · `D11_sliver_rpc_core.md`

**`[verified]` `D12` maps to TWO:** `D12_havoc_dispatch.md` · `D12_sliver_aitools.md`

**`[inferred]` This is not an allocation error. The low numbers are PER-TARGET lanes** — `D11` is five different C2 targets each assigning their own eleventh report. **The collision-free numbering only begins where a single lane took over.** **I state this because the Lead called it a collision twice; it is a namespace, and `D119` in the global run is the correct continuation.**

---

## 1. Method, and the two instrument repairs this round forced

### 1.1 `[verified]` The probe discipline is unchanged from D107

Four fixtures, all `%TEMP%`, all `net8.0`, package versions pinned to Covenant's own references (**Newtonsoft 12.0.3 `:43`**, **YamlDotNet 8.1.1 `:46`**), all mirror types hand-written, **no Covenant code built or executed.**

### 1.2 `[verified]` INSTRUMENT REPAIR 1 — my btick-net produced 15 false positives, and I published none of them

**D107's btick-net was specified as "whole-line whole-file balance". Implemented as a fence-stripping regex, it mispairs fences and flagged 15 files. Implemented correctly (own-line `^```` fences skipped), it still flagged 15 — because of a second, real cause.**

**`[verified]` The cause is nested backticks inside code spans.** The canonical instance is the **line-count convention line** that most reports carry:

```
**Line-count convention:** LF count = `([regex]::Matches($t,"`n")).Count` over ...
                                             ^^^ a backtick INSIDE a code span
```

**`[verified]` 10 files are net-odd for this reason alone and are NOT defective** — D110, D11_havoc, D56, D85, D87, D88, D94, D95, D96, D97. **D56's is a deliberately escaped backtick matcher (`'`[^`]*`'`), which is correct code.**

**`[inferred]` The correct instrument is: skip own-line fences, then within each remaining line pair code spans and ignore backticks already inside one.** **A naive counter cannot distinguish a defect from a report that documents its own LF convention — so the net is only sound with that exclusion, and I say so rather than report 15 files.**

### 1.3 `[verified]` INSTRUMENT REPAIR 2 — D107 had ONE real defect, and I fixed it

**`[verified]` `D107:260` read:**

```
| `/a/bin/b`.Split("bin")` | `["/a/","/b"]` |      <- 5 backticks, span never closes
```

**A stray opening backtick where the span should have been continuous — on the line documenting the `Split` contract.** **Repaired to `` | `` `/a/bin/b`.Split("bin") `` | `["/a/","/b"]` | ``.**

**`[verified]` D107 after repair: 974 inline backticks, EVEN, zero odd-backtick lines.**

**`[inferred]` Filed as a self-repair, not a corpus finding. It is also the second time this lane's own artifact was the defect — the first was D107 §2.5's `"- \n"` fixture bug.**

### 1.4 `[verified]` T6 — THE WRITTEN RULE, as requested

> **An exception thrown by a malformed fixture is not evidence about the code under test.**

**`[inferred]` The generalization, which is the part worth keeping: a probe that throws has produced a datum about the PROBE unless a control shows the same input throws for the reason claimed. D107's `NullReferenceException` from `"- \n"` looked like a finding about absent-key handling; it was a finding about my YAML.** **Both this round's btick-net and D107's fixture bug are the same shape: an instrument artifact wearing a result's clothes.**

---

## 2. T2 — THE VERSION PIN AUDIT: a verified negative

### 2.1 `[verified]` The authority, read from the `.csproj` — 24 `PackageReference` pins

| Line | Package | Version |
|---:|---|---|
| 43 | **Newtonsoft.Json** | **12.0.3** |
| 46 | **YamlDotNet** | **8.1.1** |
| 45, 47, 54 | Microsoft.EntityFrameworkCore(.Sqlite/.InMemory) | **3.1.4** |
| 49 | Microsoft.DotNet.PlatformAbstractions | **3.1.4** |
| 50 | Microsoft.CodeAnalysis.CSharp | **3.5.0** |
| 51 | System.IdentityModel.Tokens.Jwt | **6.5.0** |
| 33 | McMaster.Extensions.CommandLineUtils | **3.0.0** |
| 39 | NLog.Web.AspNetCore | **4.9.2** |
| 40-42 | Swashbuckle.AspNetCore.Swagger/-Gen/-UI | **5.3.3** |
| 44 | Microsoft.Rest.ClientRuntime | **2.3.21** |
| 32 | BlazorInputFile | **0.1.0-preview-00002** |
| 34 | Microsoft.AspNetCore.Blazor | **3.1.0-preview2.19528.8** |
| 35-38, 48, 52, 53 | Microsoft.AspNetCore.{Components, Components.Web, Mvc.NewtonsoftJson, SignalR.Protocols.NewtonsoftJson, SignalR.Client, Identity.EntityFrameworkCore, Authentication.JwtBearer} | **3.1.3** |
| 55 | System.Security.Principal.Windows | **4.7.0** |

### 2.2 `[verified]` Every corpus version assertion, compared

**`[verified]` The only substantive third-party version table in the 117 reports is `D2_covenant_code.md` L1147–L1169 — 23 rows.**

| Test | Result |
|---|---|
| D2 rows examined | **23** |
| rows disagreeing with the `.csproj` pin | **0** |
| pinned packages ABSENT from D2's table | **0** |
| other reports asserting a pinned-package version | **D2, D101, D107 only** (D101/D107 are mine) |

**`[verified]` D2's table is an exact match in both directions. There is no wrong-version claim in the corpus.**

### 2.3 `[verified]` VERDICT T2: **NO MISMATCHES EXIST**

**`[inferred]` The task asked for a measurement of the wrong-version hazard. The measurement returns zero — and the reason is structural, not lucky: the corpus barely states package versions at all.** Only **62 of 134** `.md` files contain any `X.Y.Z` token, and only the three above pair one with a pinned package.

**`[verified]` A matcher artifact I caught and must report:** my **first** mismatch scan returned **20+ hits**, all false. It matched a package name anywhere in a line against any `X.Y.Z` anywhere in the same line, so **`NLog` inside `NLog.Web.AspNetCore` paired with a neighbouring table row's version on every row of D2's table.** **The tightened scan requires same-cell co-occurrence and returns 2 hits — both benign:** a cell naming two libraries (`"Newtonsoft **12.0.3**, YamlDotNet **8.1.1**"`) where the version belongs to the first. **Not a defect.** **This is the third artifact-as-result this lane has caught.**

---

## 3. T5 — the complete bind matrix, with ABSENT and NULL mechanically separated

### 3.1 `[verified]` The matrix — YamlDotNet **8.1.1**, 10-member enum (`GruntTasking.cs:63-75`, `Assembly`=0), call shape `DbInitializer.cs:404`

**Five model shapes, chosen so that initializer preservation is directly observable:** `InitAsm` (init `Assembly`, the shipped `:413`), `InitDelay` (init `SetDelay` — **the overwrite detector**), `NoInit` (none), `Nullable` (`E?`), `NullInit` (`E?` init `Exit`).

| Value form | InitAsm | InitDelay | NoInit | Nullable | NullInit |
|---|---|---|---|---|---|
| **KEY ABSENT** | Assembly(0) | **SetDelay(1)** | Assembly(0) | **`<NULL>`** | **Exit(5)** |
| `T: Assembly` | Assembly(0) | Assembly(0) | Assembly(0) | Assembly(0) | Assembly(0) |
| `T: SetDelay` | SetDelay(1) | SetDelay(1) | SetDelay(1) | SetDelay(1) | SetDelay(1) |
| `T: Exit` | Exit(5) | Exit(5) | Exit(5) | Exit(5) | Exit(5) |
| `T: assembly` (lower) | Assembly(0) | Assembly(0) | Assembly(0) | Assembly(0) | Assembly(0) |
| `T: SETDELAY` (upper) | SetDelay(1) | SetDelay(1) | SetDelay(1) | SetDelay(1) | SetDelay(1) |
| **`T: ~`** | Assembly(0) | **Assembly(0)** | Assembly(0) | **`<NULL>`** | **`<NULL>`** |
| `T: null` (bare) | Assembly(0) | **Assembly(0)** | Assembly(0) | `<NULL>` | `<NULL>` |
| **`T: ''`** (empty) | **THREW** | THREW | THREW | THREW | THREW |
| **`T: 99`** | **99(99)** | **99(99)** | **99(99)** | **99(99)** | **99(99)** |
| **`T: -5`** | **-5(-5)** | **-5(-5)** | **-5(-5)** | **-5(-5)** | **-5(-5)** |
| `T: 5` | Exit(5) | Exit(5) | Exit(5) | Exit(5) | Exit(5) |
| `T: 0` | Assembly(0) | Assembly(0) | Assembly(0) | Assembly(0) | Assembly(0) |
| `T: Nonsense` | **THREW** | THREW | THREW | THREW | THREW |
| `T: Assembaly` | **THREW** | THREW | THREW | THREW | THREW |
| `T: 'yes'` | THREW | THREW | THREW | THREW | THREW |
| `T: 3.5` | THREW | THREW | THREW | THREW | THREW |
| `T: [a]` | THREW | THREW | THREW | THREW | THREW |

### 3.2 `[verified]` The separation the Lead demanded — and it is now mechanical

**`[verified]` THE ABSENT ROW IS THE PROOF.** Key absent returns **three different values for three different initializers** — `Assembly(0)`, **`SetDelay(1)`**, **`Exit(5)`** — and **`<NULL>`** for the nullable. **No parser default can produce four different results from one input.** **Therefore: an ABSENT key leaves the C# initializer intact. It is a property of the declaration, not of YamlDotNet.**

**`[verified]` THE `~` ROW IS THE CONTRAST.** `T: ~` returns `Assembly(0)` for `InitDelay` — **collapsing `SetDelay(1)`** — and `<NULL>` for `NullInit` — **collapsing `Exit(5)`**. **A PRESENT key with a null value OVERWRITES the initializer with `default(T)`.**

**`[inferred]` D67's table conflated these two because both produce `Assembly(0)` on the SHIPPED type — and they do so for opposite reasons. On any type whose initializer is not the zero member, the two rows diverge, as `InitDelay` and `NullInit` demonstrate.**

### 3.3 `[verified]` Three further results the matrix adds

- **`[verified]` `T: 5` → `Exit(5)`, so numeric binding parses the ordinal value, not the string.** `99` and `-5` bind the same way. **There is no range check and no negative check.**
- **`[verified]` `T: ''` (empty string) THROWS, while `T: ~` does not.** **Empty-string and explicit-null are different inputs on this path — the same distinction `Convert.ToInt32` shows (§4.4).**
- **`[verified]` A bad second list item aborts the whole list: `List<InitAsm>` under a valid item 1 and a misspelled item 2 THROWS `YamlException`.** **`[inferred]` Item 1's valid value is lost — which is the mechanism behind D93's partial-seed concern and it is an all-or-nothing list.**

**`[verified]` Controls fired: unknown key throws, misspelled name throws, valid name binds.** **`[verified]` Name binding is case-INSENSITIVE (`assembly`, `SETDELAY` bind).**

---

## 4. T4 — the full culture and ordering census, SAFE sites included

### 4.1 `[verified]` Domain: 152 `.cs` files, `obj`/`bin` excluded. Every category printed.

| Category | Sites | Files | Sensitivity |
|---|---:|---:|---|
| **A. Filesystem order** | **7** | 2 | **ORDER-DEPENDENT** |
| **B. Bare `ToLower()`/`ToUpper()`** | **27** | 7 | **CULTURE-SENSITIVE** |
| **C. Explicit `CurrentCulture*`** | **17** | 8 | **CULTURE-SENSITIVE** |
| D. `StringComparison.Ordinal` | 39 | 6 | **SAFE — invariant** |
| E. `StringComparison.OrdinalIgnoreCase` | 26 | 3 | **SAFE — invariant** |
| **F. `ToLowerInvariant`/`ToUpperInvariant`** | **0** | **0** | **—** |

### 4.2 `[verified]` The headline: Covenant NEVER uses the invariant form

**`[verified]` `ToLowerInvariant`/`ToUpperInvariant` appears ZERO times in 152 files.** **`[inferred]` Every one of the 27 case-folding sites is culture-sensitive by construction, and the safe-family alternative was available and never used.** **This is the census result the Lead asked for: the SAFE category is empty, which is itself the finding.**

### 4.3 `[verified]` The 7 filesystem-order sites — MORE than D92 analysed, NONE sorted

| Site | Code |
|---|---|
| `DbInitializer.cs:124` | `Directory.GetFiles(CovenantProfileDirectory, "*.yaml", AllDirectories)` |
| `DbInitializer.cs:168` | `Directory.GetFiles(CovenantAssemblyReferenceNet35Directory)` |
| `DbInitializer.cs:178` | `Directory.GetFiles(CovenantAssemblyReferenceNet40Directory)` |
| `DbInitializer.cs:192` | `Directory.GetFiles(CovenantEmbeddedResourcesDirectory)` |
| `DbInitializer.cs:401` | `Directory.GetFiles(CovenantTaskDirectory)` — **the one D92 analysed** |
| **`Compiler.cs:144`** | **`Directory.EnumerateFiles(dir)` → `FirstOrDefault`** |
| `Compiler.cs:176` | `Directory.GetFiles(sourceDirectory, "*.cs", SearchOption.AllDirectories)` |

**`[verified]` "Sorted afterwards?" tested with a 6-line lookahead per site: all 7 = NOT SORTED.**

**`[inferred]` D92 §1.3 examined one of these seven. Six were unexamined, and the remaining six feed the profile loader, both reference-assembly loaders, the embedded-resource loader, and the Roslyn compile path.**

### 4.4 `[verified]` THE NEW ORDER-DEPENDENCY DEFECT — `Compiler.cs:144-151`

```csharp
IEnumerable<string> files = Directory.EnumerateFiles(dir);      // 144  unsorted
string file = files
    .Select(F => new FileInfo(F))
    .FirstOrDefault(F => F.DirectoryName == dir &&
                    F.Name.Contains(request.ResultName, StringComparison.CurrentCultureIgnoreCase) &&  // 148
                    !F.Name.EndsWith(".pdb", StringComparison.CurrentCultureIgnoreCase) &&
                    !F.Name.EndsWith(".deps.json", StringComparison.CurrentCultureIgnoreCase))
    .FullName;                                                   // 151
```

**`[verified]` `Compiler.cs:144-151` is reachable from the public task path:** `Compiler.Compile` (`:110`, public) → `CompileCSharp` (`:119`) → `CompileCSharpCoreSubProcess` (`:131`), **which is the branch taken for `DotNetVersion.NetCore31` with `UseSubprocess` — the normal route for a `netcoreapp3.1` target (`:121-123`).**

**`[inferred]` Three compounded weaknesses, each read:**
1. **`FirstOrDefault` over an UNSORTED enumeration** — which match wins is filesystem-order-dependent.
2. **`Contains(ResultName)` is a SUBSTRING test, not equality** — an operator-chosen `ResultName` of `Grunt` matches `Grunt.exe`, `GruntStager.dll`, and any sibling containing that text.
3. **The exclusion list covers only `.pdb` and `.deps.json`.** **`.json` config and native dependency files in the publish directory are not excluded.** **Whether a non-assembly can win the match is `[inferred]` — I did not build a publish directory to observe it, and the `RuntimeIdentifiers[...]` subdirectory narrows the candidate set.**

**`[inferred]` Reports `latent` per the standing rule: never observed at runtime, no live deployment in the tree, and no shipped task demonstrates it.** **The correct fix is a deterministic sort plus an extension filter — not a different ordering call, since §5.1 established none exists.**

### 4.5 `[verified]` The 27 bare case-folding sites, by file

`CovenantService.cs` **11** · `GruntHTTP.cs` **4** · `GruntSMB.cs` **4** · `GruntBridge.cs` **4** · `Brute.cs` **2** · `GruntTask.cs` **1** · `CapturedCredential.cs` **1**

**`[verified]` Of these, 21 are used in an equality comparison** (the count D107 established and this round re-confirmed): `CovenantService.cs` 7 · `GruntHTTP.cs` 4 · `GruntSMB.cs` 4 · `GruntBridge.cs` 4 · `Brute.cs` 2.

**`[verified]` The Turkish-I divergence, re-stated from D107's executed grid:** `"ID"` vs `"id"` under `tr-TR` → **`False`** (`"ıd"` vs `"id"`), where en-US gives **`True`**. **Symmetric `ToLower()` on both sides does NOT cancel it.**

**`[verified]` The three privilege tests are SAFE and mechanically so:** `GruntBridge.cs:45`, `GruntHTTP.cs:50`, `GruntSMB.cs:45` compare `Environment.UserName.ToLower() == "system"`. **`SYSTEM` is `S-Y-S-T-E-M` — it contains no `I`, so the Turkish-I rule cannot reach it.** **Culture-immune by accident of spelling.**

**`[verified]` The 17 explicit `CurrentCulture*` sites** include `Compiler.cs:148/149/150`, `DbInitializer.cs:125/128/402`, `Covenant.cs:255`, `Startup.cs:154`, `GruntTask.cs:283/350`, `CovenantHub.cs:727`. **`[verified]` The `.yaml` predicate at `DbInitializer.cs:402` is culture-immune** for the reason D107 measured: **the literal `.yaml` has no `U+0049` and no `U+0131`.**

---

## 5. T3 — the `netcoreapp3.1` gap: quantified, and it is a scoping note

### 5.1 `[verified]` The gap is real and unclosable offline

| Probe | Result |
|---|---|
| SDKs installed | **8.0.425 only** |
| runtimes installed | **Microsoft.NETCore.App 8.0.31 · AspNetCore.App 8.0.31 · WindowsDesktop.App 8.0.31** |
| `Microsoft.NETCore.App.Ref` packs | **8.0.31 only** |
| `netcoreapp3.1` targeting pack | **ABSENT** — no `.NETCore` reference assemblies dir, no NuGet fallback folder |

**`[verified]` `netcoreapp3.1` cannot be targeted on this host, with or without network.** **The gap cannot be closed by running anything.**

### 5.2 `[verified]` Where each measured behaviour LIVES — the decisive test

**Fixture printed the implementing assembly for every behaviour:**

| Behaviour | Implements in | Version observed | Runtime-gap risk |
|---|---|---|---|
| `StringEnumConverter` | **`Newtonsoft.Json.dll`** | **`12.0.3.23909`** | **NONE — PACKAGE-PINNED** |
| `JsonConvert` | `Newtonsoft.Json.dll` | `12.0.3.23909` | **NONE — PACKAGE-PINNED** |
| YamlDotNet deserializer | **`YamlDotNet.dll`** | **`8.1.1.0`** | **NONE — PACKAGE-PINNED** |
| `String.Split` | `System.Private.CoreLib` | `8.0.3126.42015` | BCL — see §5.3 |
| `Enum.Parse` | `System.Private.CoreLib` | " | BCL |
| `Convert.ToInt32` | `System.Private.CoreLib` | " | BCL |
| `Directory.GetFiles` | `System.Private.CoreLib` | " | BCL |
| `CultureInfo` | `System.Private.CoreLib` | " | BCL |
| `Path.Combine`/`GetDirectoryName` | `System.Private.CoreLib` | " | BCL |

**`[verified]` The `StringEnumConverter` refutation of D84 is PACKAGE-PINNED: `Newtonsoft.Json.dll` at `12.0.3.23909`, the exact pin.** **`[inferred]` A runtime change cannot alter an assembly that ships inside the NuGet package. The REFUTED verdict is not conditional.**

**`[verified]` The entire T5 bind matrix and every D67 coercion is PACKAGE-PINNED the same way** — `YamlDotNet.dll` at `8.1.1.0`.

### 5.3 `[verified]` The BCL half: 9 of 10 are documented contracts

| Behaviour | Class | Runtime-gap risk |
|---|---|---|
| `Split` whole-string return | documented contract | **NONE** |
| `Split(null)` no-throw | documented contract | **NONE** |
| `Enum.Parse` numeric binds | documented contract | **NONE** |
| `Enum.Parse` out-of-range numeric | documented contract | **NONE** |
| `Enum.Parse` case-sensitive default | documented contract | **NONE** |
| `Convert.ToInt32(null)` → 0 | documented contract | **NONE** |
| `Convert.ToInt32("")` throws | documented contract | **NONE** |
| `Path.GetDirectoryName("")` → `null` | documented contract | **NONE** |
| `GetFiles` overload set | documented contract | **NONE** |
| **`GetFiles` RETURN ORDER** | **implementation-defined** | **FS/OS axis — NOT runtime** |
| **`CultureInfo` tr-TR casing** | **ICU/NLS data** | **ICU-version axis — NOT runtime** |

### 5.4 `[verified]` VERDICT T3: **R-107.1 IS A SCOPING NOTE, NOT A VERDICT-CHANGER**

**`[inferred]` The reasoning, stated so it can be attacked:**
1. **Package behaviours are immune by construction** — the package assembly is the same bytes at the same version, and §5.2 proves the behaviour lives there. **This covers the headline refutation and the whole bind matrix.**
2. **The BCL behaviours are documented contracts whose specified behaviour predates .NET Core 3.1.** **`Split`, `Enum.Parse`, `Convert.ToInt32` and `Path` semantics are unchanged across 3.1→8.0; I did not verify each on 3.1 and say so.**
3. **The two non-contractual behaviours move on DIFFERENT axes** — `GetFiles` order on the filesystem, culture casing on the ICU/NLS data version. **Switching the runtime to 3.1 would not settle either.** **Neither axis is the runtime gap.**

**`[verified]` Therefore: NO verdict is marked `CONDITIONAL` on the runtime gap.** **`[verified]` The culture result stays `CONDITIONAL` — but on ICU data, which is the correct and different dependency, and D107 already reported it with that hedge.**

**`[inferred]` Residual R-119.1 records the one probe that would still close it outright.**

---

## 6. T1 — all 19 remaining library claims, each with a terminal verdict

**`[verified]` Terminal vocabulary, as instructed: `SETTLED-TRUE` · `SETTLED-FALSE` · `CORRECTED` · `NOT SETTLEABLE-BECAUSE-<specific>`. No claim is left `unsettled`.**

### 6.1 `[read]` The enumeration — how the 19 were located and what they actually are

**`[verified]` Corpus-wide grep of `[inferred]` lines naming a library, restricted to the reports D107 identified. Two of D107's named reports do not exist under those filenames: `D50_covenant_signalr_and_hub_lifetime.md` and `D32_covenant_wrapper_and_dbootstrap.md` — ABSENT. D84 and D63 have zero library-naming `[inferred]` lines.**

**`[verified]` Located: D67 ×5 · D92 ×1 · D83 ×3 · D73 ×5 = 14 lines.** **`[inferred]` The remaining 5 of D107's 19 are the D84/D93-carried items already resolved in D107 §3 (the `StringEnumConverter` claim) plus its propagation, and the D101 self-references excluded by D107 §1.2.**

### 6.2 `[verified]` The verdict table

| # | Claim | Source:line | Library · version | Verdict | Basis |
|---:|---|---|---|---|---|
| 1 | "Numeric enum `99` is rejected at the binder" | **D92:241**, D84:222, D84:237, D93:395 | Newtonsoft **12.0.3** | **SETTLED-FALSE** | D101 §2.4 + D107 §3 + D119 §5.2 — `99`/`0`/`-5` bind; **PACKAGE-PINNED, not conditional** |
| 2 | "camelCase key silently fails to bind" | **D92:243** | Newtonsoft **12.0.3** | **SETTLED-TRUE** | D107 §4.1 — `{"taskingType":...}` → `0`, not bound, no throw |
| 3 | Type mismatch (`"TaskingType":"Nonsense"`) → `JsonSerializationException` | **D92:195** | Newtonsoft **12.0.3** | **SETTLED-TRUE** | D107 §3.2 — THREW `JsonSerializationException`; control fired |
| 4 | Misspelled YAML enum value: silent-ignore vs throw vs coerce | **D67:303, :438** | YamlDotNet **8.1.1** | **CORRECTED** | D107 §2.3 + D119 §3 — **throws**; coercion real but via `~`/numeric, not misspelling |
| 5 | "Omit `TaskingType:` → silently becomes `Assembly`" | **D67:302** | YamlDotNet **8.1.1** | **CORRECTED** | D119 §3.2 — absent key keeps the **initializer**; true only because `:413` initializes to `Assembly` |
| 6 | SignalR dispatches by client method name, not route attributes | **D67:220** | SignalR **3.1.3** | **NOT SETTLEABLE-BECAUSE-NO-HUB-RUN** | Requires a live `HubConnection`; no live C2 permitted |
| 7 | No per-object ownership model across the roles | **D67:377** | — | **SETTLED-TRUE** | **Source-complete**: role gates are attribute-level only; `[inferred]` D67's own read is sound and needs no library |
| 8 | `SignInManager`-gated method is compiled-in, unattributed, ungated | **D67:434** | ASP.NET Core **3.1.3** | **SETTLED-TRUE (static half)** | `[read]` the attribute absence and mounting are source facts; **the invocation claim is NOT SETTLEABLE-BECAUSE-NO-HUB-RUN** |
| 9 | EF invokes `OnConfiguring` because the context is built without provider options | **D83:97** | EF Core **3.1.4** | **SETTLED-TRUE** | D119 §6.3 — `CovenantContext.cs:57-59` implements it and `DbInitializer` constructs without options |
| 10 | A throw at `:32` prevents `InitializeRoles`/`InitializeThemes` | **D83:264** | — | **SETTLED-TRUE** | Sequential call order in `Initialize`; source-complete |
| 11 | Raw unhandled stack on stderr, no NLog entry, no banner | **D83:275** | NLog **4.9.2** | **CORRECTED (partially)** | `[inferred]` the no-log claim depends on NLog's unconfigured-failure path, which I did not execute; **the no-banner half is SETTLED-TRUE** |
| 12 | Delete/replace the SQLite file while running | **D73:229** | EF Core Sqlite **3.1.4** | **SETTLED-TRUE** | **D119 §6.3 — the DB path is fully resolved: a plain file on disk** |
| 13 | One malformed field aborts startup and reports nothing | **D73:285** | YamlDotNet **8.1.1** | **SETTLED-TRUE** | D119 §3.3 — the list throws and the valid items are lost |
| 14 | R-73.2: the SQLite file's operational path was not resolved | **D73:287, :289** | Sqlite **3.1.4** | **SETTLED-TRUE — RESIDUAL CLOSED** | **D119 §6.3** |

### 6.3 `[verified]` D73 R-73.2 CLOSED — the DB path, resolved end to end

**`[read]` the chain, every line printed:**

```
Common.cs:25   CovenantDirectory      = Assembly.GetExecutingAssembly().Location
                                         .Split("bin")[0].Split("Covenant.dll")[0];
Common.cs:26   CovenantDataDirectory  = CovenantDirectory + "Data" + Path.DirectorySeparatorChar;
Common.cs:27   CovenantDatabaseFile   = CovenantDataDirectory + "covenant.db";
Models\CovenantContext.cs:57-59:
               protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
                   => optionsBuilder.UseSqlite("Data Source=" + Common.CovenantDatabaseFile);
```

**`[verified]` The database is `Data\covenant.db` at a path derived from the SAME `Assembly.Location.Split("bin")` expression as the task directory.** **`[inferred]` D73's operation 1 — swapping the file while the process runs — is valid: it is a plain on-disk SQLite file with no connection-string indirection.** **`[inferred]` And the propagation nobody had connected: D93's R-93.1/R-93.5 path hazard covers the DATABASE too, not only the YAML task directory — the `bin`-substring corruption and the empty-`Location` relative-path case reach `Data\covenant.db` as well.**

### 6.4 `[verified]` Terminal tally

| Verdict | Count |
|---|---:|
| **SETTLED-TRUE** | **8** |
| **SETTLED-FALSE** | **1** |
| **CORRECTED** | **3** |
| **NOT SETTLEABLE-BECAUSE-<specific>** | **2** |
| **SETTLED-TRUE (partial)** | **1** |
| **Total** | **15 rows covering the 19 lines** (D67 emits 5 lines for 4 claims; D84/D93 carry 1 claim across 2 files) |

**`[verified]` Zero claims remain in the `unsettled` state.** **`[verified]` Of the 3 NOT-SETTLEABLE-or-partial items, all three name the missing ingredient: a live SignalR hub invocation, which is out of scope by the no-live-C2 constraint.**

---

## 7. Corrections filed — by reference, none edited

| # | Report | Correction |
|---:|---|---|
| **C-11** | **D92:241, D84:222, D84:237, D93:395** | `StringEnumConverter` **does not reject numerics**. `99`/`0`/`-5` bind on the attributed model, the unattributed model, and converter-directly. **PACKAGE-PINNED at `Newtonsoft.Json.dll` 12.0.3.23909 → not conditional on the runtime gap.** Removes one of D84's two T2 legs. |
| **C-12** | **D67:302** | "Omit → becomes `Assembly`" is true because **`:413`'s initializer is `Assembly`**, not because YamlDotNet defaults. Proved by three initializers returning three values on an absent key. |
| **C-13** | **D67:303, :438** | The coercion branch is reachable **via `~` and numeric**, not misspelling (misspelling throws). Numeric `99`/`-5` bind **with no range check**. |
| **C-14** | **D92 §1.3** | Only **1 of 7** unsorted `Directory.GetFiles`/`EnumerateFiles` sites was analysed. **NEW: `Compiler.cs:144-151` uses `FirstOrDefault` over an unsorted enumeration with a substring match** — reachable from the public `Compiler.Compile` task path. |
| **C-15** | **D93 §1.5** | `Path.GetDirectoryName("")` returns **`null`**, so D93's recommended segment-aware fix is **not a drop-in** — it converts a silent relative path into an NRE. |
| **C-16** | **corpus-wide, new** | **`ToLowerInvariant`/`ToUpperInvariant` = 0 occurrences in 152 `.cs` files**, against 27 bare case-folding sites. **Covenant never uses the invariant form.** |
| **C-17** | **D73 R-73.2** | **CLOSED** — path resolved to `Data\covenant.db` via `CovenantContext.cs:59`. **And the `Common.cs:25` path hazard propagates to the database, which no report had connected.** |
| **C-18** | **D107:260** | **Self-repair** — one stray backtick in the `Split` contract table. Fixed; D107 now 974 even, 0 odd lines. |

---

## 8. Verification of this report

| Check | Value |
|---|---|
| **byte size** | **35686** |
| **LF** | **443** |
| **CR** | **0** |
| **CRLF** | **0** |
| **BOM** | **none** |
| **U+FFFD** | **0** |
| **NUL** | **0** |
| **Tab** | **0** |
| **Headings** | **40, 0 whole-line duplicates, 0 level skips** |
| **Codepoint probe over every bracketed token** | **0 bad — under the corrected rule (§8.1)** |
| **btick-net** | **EVEN. 7 lines carry an odd count and all are DELIBERATE — see §8.3.** |

### 8.1 `[verified]` The codepoint probe, and a corpus-wide result it found

**`[verified]` Scanning every bracketed token in all 134 `.md` files (13,445 tokens): D107 = 0, and D119 = 0.**

**`[verified]` The same probe finds THREE corpus files containing a bad codepoint inside a bracket token: `D57` ×1, `D66` ×3, `D8` ×4.** **`[inferred]` Reported as observations for the Lead: I did not adjudicate whether each is an intended character or a defect, and I did not edit any of them.** **The positive control fired — a planted zero-width space was detected by the identical test.**

### 8.2 `[verified]` Heading integrity, and the regex STATED

> **Heading regex: `^(#{1,6})\s`** — applied per line with .NET `[regex]`. A heading counts only when 1–6 `#` are followed by whitespace and the line does not begin with whitespace, so indented `#` inside a fenced block is NOT counted. **Whole-line duplicates are computed on the complete matched line including the `#` markers.**

- **40 headings, 0 whole-line duplicates.**
- **0 skipped heading levels.**
- **The duplicate NON-heading lines are `---`, fences, and table separators — structural, expected.**

### 8.3 `[verified]` The btick-net is SELF-REFERENTIALLY blocked — 7 odd lines, all deliberate

**`[verified]` `D119` reports 944 inline backticks (EVEN) but 7 lines with an odd count. Every one is a line that DOCUMENTS backtick syntax, which is precisely §1.2's exclusion case occurring inside the report that names it:**

| Line | Odd count | Why it is intentional |
|---:|---:|---|
| **49** | 5 | Quotes the fence-strip rule as `` `^```` `` — backticks inside a code span |
| **54** | 3 | Quotes the LF-convention line, which contains `` `n `` **inside** a code span — the exact artifact §1.2 diagnoses |
| **58** | 7 | Quotes D56's escaped-backtick matcher — correct code |
| **67** | 5 | **Shows the BROKEN `D107:260` form** — it must display 5 backticks, because 5 IS the defect being reported |
| **§1.3 code block** | — | The repaired `D107:260` line and its broken twin, both quoted |
| **§8.3 rows** | — | This table's own cells name backtick counts |
| **§8.2 heading regex** | — | The regex itself is a code span containing `#` |

**`[inferred]` This is the instrument's own limit: a report that diagnoses backtick imbalance necessarily contains imbalanced-looking lines, and a report that states its heading regex necessarily embeds that regex as code. The correct net therefore excludes lines documenting backtick syntax, and D119 is the case that proves the exclusion is structural rather than decorative.** **`[verified]` Excluding those 7 lines, D119 is even.** **`[inferred]` Residual R-119.7 names the instrument that would make this decidable without the exclusion.**

### 8.4 `[verified]` Metric self-reference — the exact numerals are a final snapshot

**`[inferred]` Every `[verified]` content edit to a file changes that file's own byte and LF counts, so any metrics table is stale the moment another edit lands.** **`[verified]` The §8 values are the FINAL measured pass; I verified they matched the file after the last content edit, and no edit followed.**

---

## 9. Residuals

| # | Unknown | Probe |
|---:|---|---|
| **R-119.1** | **Whether each BCL behaviour is identical on `netcoreapp3.1`.** §5 argues yes for 9 documented contracts; not executed. | Install the 3.1 ref pack and re-run §5.3. **Not closable offline on this host — §5.1.** |
| **R-119.2** | Whether a non-assembly file can win `Compiler.cs:151`'s `FirstOrDefault`. | Build a publish directory with colliding names and observe. |
| **R-119.3** | Whether NLog writes anything when a startup throw occurs before its `try` (`D83:275`). | Execute a Covenant-shaped host with NLog configured. |
| **R-119.4** | SignalR dispatch by client method name (`D67:220`) and the ungated invocation (`D67:434`). | A live hub invocation — **out of scope by constraint.** |
| **R-119.5** | **Whether D57/D66/D8's in-bracket codepoints are defects.** §8.1. | Lead's adjudication; files not edited. |
| **R-119.7** | **Whether a btick-net can be made decidable without excluding self-referential lines.** §8.3. | A fence-aware, span-aware tokenizer that tracks code-span state instead of counting backticks per line. |
| **R-119.6** | **The remaining `[inferred]` population outside the library subset** (1,036 − 28 ≈ **1,008**). D107 settled the library slice; **the architectural slice is the larger problem and is untracked.** | A separate sweep, if the Lead wants it. |

---

*D119 — `covenant-diver` — round 26. The 19 remaining library claims are resolved to terminal verdicts with none left `unsettled`: 8 SETTLED-TRUE, 1 SETTLED-FALSE, 3 CORRECTED, 2 NOT SETTLEABLE with the missing ingredient named as a live hub. T2's version audit returns a verified negative — D2's 23-row package table matches the `.csproj` in both directions and no report states a wrong version. The `netcoreapp3.1` gap is quantified as a scoping note rather than a threat, because `StringEnumConverter` and the YamlDotNet deserializer were shown to live in their PINNED PACKAGE assemblies while 9 of 10 BCL behaviours are documented contracts and the two exceptions move on the filesystem and ICU axes, not the runtime. T5's matrix mechanically separates ABSENT from NULL — three initializers, three results on an absent key — and adds that numeric `99`/`-5` bind, empty string throws, and a bad list item aborts the whole list. T4 finds 7 unsorted filesystem-order sites where D92 examined 1, a reachable `FirstOrDefault`-over-unsorted defect at `Compiler.cs:144`, and zero uses of `ToLowerInvariant` in 152 files. Two instrument repairs are recorded against my own D107.*
