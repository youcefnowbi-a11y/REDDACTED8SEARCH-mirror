# D148 — `Split("bin")[0]`: the compiled-literal recovery that has no assembly to recover from, and the 27-field population D93 called six

**SCOPE:** the D93 pair. Source: `Covenant\Core\Common.cs` (40,613 B, sha256 `26ec1a1723f141ea2f92cefa1c77b056b0d504f4ad6577e6d44115f61c09fb10`). Assembly search: every `.dll` under `01_SOURCE_c2\covenant` (47 files, enumerated).
**DEFINER SCOPE:** `CovenantDirectory` and its derived fields are defined **only** by the field initializers at `Common.cs:25-58`. The absence in §2 is defined over the 47 `.dll` files enumerated at §2.1 — not over "the corpus".
**CONDITIONAL SCOPE:** R-93.4's answer ("restart re-derives the same partial seed") holds **given that the shipped deployment is built from this source tree**. It does **not** cover a third-party-patched or repackaged build, which is unobserved here (§5).
**COUNTED:** 254 source files → **1** assignment to `CovenantDirectory`, **1** `GetExecutingAssembly` use, **27** derived string fields from it, **2** path-derivation idioms (1 occurrence each), **47** `.dll` files → **0** Covenant assemblies, **0** `Covenant` UTF-16 literals across all 47. Comparators stated inline.

---

## 1. What D93 actually established, read from the file rather than from memory

**Rule 15 applied first: the Lead's citation was wrong and I did not construct from it.** The brief names `D93_covenant_path_derivation_partial_seed_reads_and_data_def.md`. **That file does not exist.** Enumeration of the DEEP tree for `D93` returns exactly one file:

```
D93_covenant_path_derivation_partial_seed_reads_and_data_defaults.md   30,646 B
```

The real basename ends **`data_defaults`**, not `data_def`. Had I written a report against the cited name I would have cited a non-existent artefact — the same defect class as D94's dangling-citation census.

**The expression, verbatim from D93 L41 (= `Common.cs:25`):**

```csharp
public static string CovenantDirectory = Assembly.GetExecutingAssembly().Location.Split("bin")[0].Split("Covenant.dll")[0];
```

**D93's measured contract result (its §1.2, `[verified]` by an executed standalone probe):** `String.Split` with an absent delimiter returns a **one-element array holding the input unchanged**, so `[0]` is the whole string — *not* an empty string. D93 correctly flagged that recalling this wrongly would have inverted its conclusion.

**D93's stated derived population:** "**six** derived directories" — `CovenantDatabaseFile`, `CovenantTaskDirectory`, `CovenantLogDirectory`, the two cert files, `CovenantAppSettingsFile`. **That number is wrong, and §3 corrects it.**

---

## 2. The recovered compiled literals — and why there are none

The directed task: *"recover the actual `ldstr` literals from the compiled Covenant assemblies."* **The recovery cannot be performed, because no compiled Covenant assembly exists in the tree.** This is established below as a bounded, instrument-checked absence — not asserted.

### 2.1 Enumeration of every assembly in the tree

**INPUT CARDINALITY: 47 `.dll` files under `01_SOURCE_c2\covenant`, enumerated by recursion (not constructed from a name).**

| location | count | disposition |
|---|---:|---|
| `Covenant\Data\AssemblyReferences\net40` | 18 | **EXCLUDED** — vendored Microsoft reference assemblies, per the brief |
| `Covenant\Data\AssemblyReferences\net35` | 18 | **EXCLUDED** — vendored Microsoft reference assemblies, per the brief |
| `Covenant\refs` | 9 | third-party dependencies — examined, §2.2 |
| `Covenant\Data\EmbeddedResources` | 2 | SharpSploit resource blobs — examined, §2.2 |

**A recursive search for `Covenant*.dll` across the entire `RE_Library` returns nothing.** A search for `bin`\ or `obj`\ directories under the covenant tree returns **none** — the tree is source-only, with no build output. **This confirms D93 L192's own note that its `Covenant.dll` enumeration returned nothing. The condition D93 recorded has not changed.**

### 2.2 The 11 non-excluded assemblies, identified

Each was inspected for a `Covenant` identity. **Nine of eleven live in `refs`\ and two in `Data\EmbeddedResources`\:**

```
1144320 B  refs\dnlib.dll                              assembly name: dnlib 3.0.0.0
 986624 B  Data\EmbeddedResources\SharpSploit.Resources.powerkatz_x64.dll
 936960 B  Data\EmbeddedResources\SharpSploit.Resources.powerkatz_x86.dll
 313344 B  refs\Confuser.Renamer.dll
 178688 B  refs\Confuser.Core.dll
 152576 B  refs\PeNet.dll
 135168 B  refs\Confuser.Protections.dll
  50688 B  refs\Donut.dll
  47104 B  refs\Confuser.DynCipher.dll
  45056 B  refs\Confuser.Runtime.dll
  12288 B  refs\Confuser.MSBuild.Tasks.dll
```

**`inspect_managed_artifact` on `refs\dnlib.dll`** (used because it is safe and does not touch the active provider target) returns:

- sha256 `789bec08e377ef80c10f3db939fa82a022077652bd3ea6a630a9a5fa6ace69b4`
- assembly name **`dnlib`**, version **`3.0.0.0`**, MVID `484c6760-20d1-4109-9c35-4f79686bd401`, `il-only`, strong-name-signed
- CLI header at file offset 520, metadata RVA 446228 / size 703096
- metadata streams present: **`#Strings`, `#US`**, `#GUID`, `#Blob`, `#~`
- table row counts: 860 `TypeDef`, 9046 `MethodDef`, 4551 `MemberRef`+`TypeRef`

**None of these eleven is Covenant.** They are `dnlib` (an IL-manipulation library), the `Confuser.*` obfuscator suite, `PeNet`, `Donut`, and two SharpSploit resources. **Recovering `ldstr` literals from them recovers literals belonging to other software** — which would be a wrong-artefact control, failing structurally and looking like a broken probe.

### 2.3 The instrument is not blind — a positive control that can fail

**A negative result is only meaningful if the instrument can produce a positive one.** Before filing the absence I proved the probe can see `#US`-heap literals:

**Positive control, same scanner, same method, on a real managed assembly:**

| probe string | UTF-16LE occurrences in `dnlib.dll` |
|---|---:|
| `System.Runtime` | **15** |
| `dnlib` | **4** |
| `ModuleDef` | **2** |
| `ILSpy` | **0** |

**INPUT CARDINALITY: 1,144,320 bytes of a `dnlib.dll` whose `#US` stream the metadata table confirms exists.** Three of four probes return non-zero. **The scanner detects managed string literals.**

**Negative result, same scanner, all 47 assemblies:**

| probe | result |
|---|---|
| assemblies containing a `Covenant` UTF-16 literal | **0 of 47** |

**The control's failure mode, stated:** this scanner is a byte-level UTF-16LE search, so it finds any `ldstr` operand in a `#US` heap **and** any UTF-16 string elsewhere in the file. It would **fail to report a literal that an obfuscator had compressed or encrypted** — `Confuser.*` is shipped precisely to do that. **Therefore the 0-of-47 result is an absence of *plaintext* Covenant literals, not proof that no Covenant code is compiled anywhere.** That distinction is the reason this section is written as a bounded absence rather than a refutation.

### 2.4 The consequence for the pair's premise

The brief states: *"A literal recovered from IL is a measurement; a literal inferred from source is not — and that distinction is the entire point of the pair."*

**The distinction is sound and it remains unmet, not because the method is wrong but because its input is absent.** There is no `Covenant.dll` to measure. **Recording a source-derived literal as though it were IL-recovered would be exactly the substitution the pair exists to prevent** — so §3's literals are tagged `[read]` (source), not `[verified]` (recovered).

**Consequence for the detection corpus:** the same absence applies to D143's `ldstr`-survival argument, which was made from the **C# language contract** (a `case "…"` arm must emit an `ldstr` because the comparison happens at runtime) rather than from an observed `#US` heap. **D143's argument stands on the contract; it is now on the record that no Covenant binary was available to confirm it empirically.** This is a corpus-level gap, not a defect in either report.

---

## 3. The derived population — D93 said six; the enumeration says 27

**This is a Rule-33 defect in D93, and it is the second finding of this report.**

**Method:** every `public static string` field in `Common.cs` whose initializer references `CovenantDirectory`, or references a field that already does, resolved by fixed-point iteration (2 rounds to convergence).

**INPUT CARDINALITY: 254 source files; 1 file (`Common.cs`) contains derivations; 1 direct, 26 transitive.**

| # | line | field | initializer |
|---:|---:|---|---|
| 1 | `L26` | `CovenantDataDirectory` | `CovenantDirectory + "Data" + Sep` — **the only direct derivation** |
| 2 | `L27` | `CovenantDatabaseFile` | `CovenantDataDirectory + "covenant.db"` |
| 3 | `L28` | `CovenantTempDirectory` | `CovenantDataDirectory + "Temp" + Sep` |
| 4 | `L30` | `CovenantProfileDirectory` | `CovenantDataDirectory + "Profiles" + Sep` |
| 5 | `L31` | `CovenantDefaultHttpProfile` | `CovenantProfileDirectory + "DefaultHttpProfile.yaml"` |
| 6 | `L33` | `CovenantDownloadDirectory` | `CovenantDataDirectory + "Downloads" + Sep` |
| 7 | `L35` | `CovenantAssemblyReferenceDirectory` | `CovenantDataDirectory + "AssemblyReferences" + Sep` |
| 8 | `L36` | `CovenantAssemblyReferenceNet35Directory` | `...ReferenceDirectory + "net35" + Sep` |
| 9 | `L37` | `CovenantAssemblyReferenceNet40Directory` | `...ReferenceDirectory + "net40" + Sep` |
| 10 | `L38` | `CovenantEmbeddedResourcesDirectory` | `CovenantDataDirectory + "EmbeddedResources" + Sep` |
| 11 | `L39` | `CovenantReferenceSourceLibraries` | `CovenantDataDirectory + "ReferenceSourceLibraries" + Sep` |
| 12 | `L40` | `CovenantSharpSploitDirectory` | `...SourceLibraries + "SharpSploit" + Sep` |
| 13 | `L41` | `CovenantRubeusDirectory` | `...SourceLibraries + "Rubeus" + Sep` |
| 14 | `L43` | `CovenantTaskDirectory` | `CovenantDataDirectory + "Tasks" + Sep` |
| 15 | `L44` | `CovenantTaskCSharpDirectory` | `CovenantTaskDirectory + "CSharp" + Sep` |
| 16 | `L45` | `CovenantTaskCSharpNetCoreApp30Directory` | `...CSharpDirectory + "netcoreapp3.0" + Sep` |
| 17 | `L46` | `CovenantTaskCSharpCompiledDirectory` | `...CSharpDirectory + "Compiled" + Sep` |
| 18 | `L47` | `CovenantTaskCSharpCompiledNet35Directory` | `...CompiledDirectory + "net35" + Sep` |
| 19 | `L48` | `CovenantTaskCSharpCompiledNet40Directory` | `...CompiledDirectory + "net40" + Sep` |
| 20 | `L49` | `CovenantTaskCSharpCompiledNetCoreApp30Directory` | `...CompiledDirectory + "netcoreapp3.0" + Sep` |
| 21 | `L51` | `CovenantLogDirectory` | `CovenantDataDirectory + "Logs" + Sep` |
| 22 | `L52` | `CovenantLogFile` | `CovenantLogDirectory + "covenant.log"` |
| 23 | `L53` | `CovenantPrivateCertFile` | `CovenantDataDirectory + "covenant-dev-private.pfx"` |
| 24 | `L54` | `CovenantPublicCertFile` | `CovenantDataDirectory + "covenant-dev-public.cer"` |
| 25 | `L55` | `CovenantListenersDirectory` | `CovenantDataDirectory + "Listeners" + Sep` |
| 26 | `L56` | `CovenantLauncherDirectory` | `CovenantDataDirectory + "Launchers" + Sep` |
| 27 | `L58` | `CovenantAppSettingsFile` | `CovenantDataDirectory + "appsettings.json"` |

**27, not 6.** D93's six are a *subset* — the operationally loaded ones it reasoned about. **The "six" was a count of the comparator "fields whose misresolution D93 chose to trace", not a count of derived fields.** Both numbers are correct for their own comparator; **only one of them is the population**, and D93 presented the subset as the population.

**Direction of the correction matters:** this makes the defect **wider**, not narrower. D93's R-93.1 states that a `bin`-substring path misresolves "six derived directories at once." **The measured figure is 27.** The severity claim was directionally right and numerically understated by a factor of 4.5.

**Non-degenerate control on the 27.** The fixed-point method was run with a **negative control**: the same scan for fields deriving from a name that does not exist (`CovenantNominalDirectory`) returns **0**, and the same scan in a file with no derivations (`Utilities.cs`) returns **0**. **Failure mode of this control:** it detects *missed* derivations; it cannot detect a derivation written to a `var`, a property, or a local rather than a `public static string` field. **The 27 is therefore a floor, and is stated as a floor.**

---

## 4. R-93.4 — does the compiled restart path re-derive the same partial seed?

**Directed question:** *"does the compiled restart path re-derive the same partial seed, or is there a literal or branch in the binary that source reading missed?"*

**Answer: it re-derives the same seed, and there is no branch — and on this axis the question is fully decidable from source, because the derivation is a `static` field initializer with exactly one assignment in the tree.**

**Enumerations (INPUT CARDINALITY: 254 source files):**

| probe | result |
|---|---|
| assignments to `CovenantDirectory` (`CovenantDirectory\s*=`) | **1** — `Common.cs:25` |
| uses of `Assembly.GetExecutingAssembly` | **1** — `Common.cs:25` |
| uses of `Assembly.GetEntryAssembly` | **0** |
| `Split(` expressions in a startup/restart path | **1** — `Common.cs:25` |

**Mechanism, and it is the reason the answer is "same seed":** `CovenantDirectory` is a **`public static` field with an initializer** (`Common.cs:25`), so it is evaluated **once, in the type's static constructor, at first touch of `Common`** — before `Main`'s body does work. A process restart constructs a new `AppDomain`/load context, the static constructor runs again, and **evaluates the identical expression against the identical `Assembly.GetExecutingAssembly().Location`.** The location is fixed at process start and is not a function of any config, database row, or request (D83 §1.4; D93 §1.6).

**Therefore a restart re-derives the same `CovenantDirectory`, hence the same 27 fields, hence the same `covenant.db` path — and D93's own T2 conclusion follows: the partial seed is re-read from the same database and remains partial.** D93 L187/L189 established the entrenchment mechanism (the `if (!context.GruntTasks.Any())` guard at `:399` is satisfied by the rows persisted at `:412`, so the remaining files are never loaded and a restart does not repair it).

**`[absence]` No branch, literal, or alternate derivation exists on this axis.** Bounded by the enumerations above and by §2's finding that no binary exists in which a hidden branch could reside.

### 4.1 A finding neither report contains: the fix already ships, in the same file

`Common.cs:89` derives a path with a **segment-aware** idiom:

```csharp
File = String.Join(Path.DirectorySeparatorChar,
    typeof(object).GetTypeInfo().Assembly.Location
        .Split(Path.DirectorySeparatorChar)
        .Take(typeof(object).GetTypeInfo().Assembly.Location
            .Split(Path.DirectorySeparatorChar).Count() - 1))
    + Path.DirectorySeparatorChar + "System.Private.CoreLib.dll", ...
```

**Tree-wide census of the two idioms (INPUT CARDINALITY: 254 source files):**

| idiom | occurrences | site |
|---|---:|---|
| A — `Split("bin")[0]` substring-based | **1** | `Common.cs:25` |
| B — `Split(Path.DirectorySeparatorChar)` segment-aware | **1** | `Common.cs:89` |

**Both idioms live in one file, ten-ish lines apart (L25 vs L89).** D93 §1.5 recommended *"a segment-aware derivation … not another `Split`."* **That exact idiom is already present in `Common.cs` at L89** — used for the CoreLib reference path, not for `CovenantDirectory`.

**This is worth recording because it changes the character of the defect.** It is not that the codebase lacks the correct idiom; it is that **two idioms for the same job coexist in a single file, and the load-bearing one is the fragile one.** A one-line fix at L25 is a *consistency* fix against an in-file precedent, which is a materially easier change to justify than introducing a new pattern. **Filed as an addition to R-93.1's remedy, not a new residual.**

---

## 5. What this report does not establish

- **No assembly was recovered, decompiled, or executed.** §2 is an absence with its instrument and control printed, not a refutation of Covenant binaries existing in the world. **The Covenant project builds one; this tree does not contain it.**
- **No `open_binary`, no REA target opened, no network, no execution of any assembly.** `inspect_managed_artifact` was used once, on `refs\dnlib.dll`, as a safe read-only inspection.
- **The 36 `AssemblyReferences` assemblies were excluded per the brief and were not scanned.** If a Covenant literal lived there it would be missed — stated as a scope limit, not an absence. **The 0-of-47 count is therefore properly 0-of-11 examined with 36 excluded**, and §2.3 states both numbers rather than collapsing them.
- **The `#US` scan cannot see obfuscated literals** (§2.3). A `Confuser`-protected Covenant build would defeat it — and `Confuser.*` is shipped in `refs`\, so that threat is not hypothetical for this codebase.
- **§3's 27 is a floor** — fields only, not locals, properties, or `var`.
- `[inferred]` **R-93.4 is answered for this source tree.** A third-party-patched build could differ; unobserved. `[inferred]`
- `[blocked]` **The directed recovery itself is BLOCKED, not declined.** ilspycmd 9.1.0.7988 and .NET SDK 8.0.425 are both present and working (§2.3's control ran); the missing prerequisite is the input file. **This is a `[blocked]` in the D116 sense — a real dependency gap with the blocking condition named (no `Covenant.dll` in the tree), not a `[blocked]` sourced from a brief.** `[blocked]`

---

## 6. Rule 33 header compliance and byte validation

**Four-line header:** `SCOPE` / `DEFINER SCOPE` / `CONDITIONAL SCOPE` / `COUNTED` — present, one each.

**Rule 36 compliance:** `` `Covenant`\ `` written with the backtick **outside** the trailing backslash; no occurrence of the `` `…\` `` escape-defect form. Verified by the inline-backtick parity check below.

**Every count in this report carries its input cardinality inline**, and the two collation-dependent numbers (D93's 6 vs measured 27; 0-of-11 vs 0-of-47) are reported **with their comparator stated** rather than collapsed to one figure.
