# D84 — Covenant false-positive primitive census, `TaskingType` refutation condition, and model-default sweep

**Predecessor:** `D80_covenant_false_positive_tasks_and_taskingtype_reach.md` (formerly numbered D73; renumbered by the Lead). D80's findings are the input here, and **§1 of this report formally narrows one of them and §2 refutes one leg of another.**
**Scope:** T1 — is the false-positive *primitive* unique, enumerated as a primitive rather than as known paths? · T2 — what would REFUTE the `TaskingType` non-reachability claim, enumerated rather than hedged? · T3 — do other model properties carry non-nullable defaults a YAML loader would silently supply?
**Targets:** `Covenant/Data/Grunt/*` · `Covenant/Models/Grunts/*` · `Covenant/API/Models/GruntTask.cs` · `Covenant/Core/{DbInitializer,CovenantService,Compiler}.cs` · `Covenant/Covenant.cs` · `Covenant/Controllers/ApiControllers/GruntTaskApiController.cs`
**Method:** pure source. No REA, no `open_binary`, no build, no execution. Scripts to files, never inline. **Comments stripped before classification.** Every path list ENUMERATED. Every number carries its invocation and denominator.
**Tagging convention:** **[verified]** = counted and printed with invocation · **[read]** = read verbatim, quoted · **[inferred]** = reasoned from read code, not counted · **[absence]** = a zero, with its positive control named in §5
**Line-count convention:** 1-based line numbers throughout; a "line" is one element of `[System.IO.File]::ReadAllLines`, i.e. LF-delimited. Block spans are computed by brace-depth walk from the *definition* line.
**Write scope:** this file only. D40/D46/D50/D52/D57/D60/D63/D67/D72/D73/D80 unmodified.

---

## 0. Method note — the two new rules, applied

**Instrument Rule 20 — "A NAMED PATH IS NOT A CENSUS":** every claim below is preceded by an enumeration of the *primitive* and printed beside the claim. **This rule fired against my own D80 headline.** §1 shows D80's "the only return-gate in the corpus" was true only for the `IntPtr`-typed handle, and §1.3 states the narrowing.

**Rule 21 — "READ THE ACCESSOR NEXT TO ITS SIBLING":** for the three-site pattern (`SerializedGruntTask.TaskingType` declared / written / read) I read all three in one contiguous pass. **§3 is the result: the declaration site and one read site were adjacent all along, and the third site is where the D80 §2.4 finding actually escalates.**

**Self-corrections in this report: five** (§5), including one instrument defect caught mid-probe that would have produced a false "4 reads" count on the `Brute` local (§5 failure 2).

---

## 1. T1 — enumerate the primitive: is the false-positive shape exactly once?

### 1.1 **(a) The capture-and-discard primitive — enumerated [verified]**

**Primitive definition used:** *a `bool` LOCAL assigned from a blocking completion call (`Join`/`Wait`), where the local is then read by nothing.*

**Enumeration of the first half — every `bool <name> = <x>.Join(` in the tree:**

| Site | Text | Denominator |
|---|---|---|
| `Brute.cs:171` | `bool completed = t.Join(5000);` | |
| `GruntBridge.cs:185` | `bool completed = t.Join(5000);` | |
| `GruntHTTP.cs:191` | `bool completed = t.Join(5000);` | |
| `GruntSMB.cs:185` | `bool completed = t.Join(5000);` | |
| **total** | **4** | **152 `.cs` enumerated, excl `obj/`/`bin/`** |

**[invocation: `Select-String 'bool\s+\w+\s*=\s*\w+\.Join\('` over all enumerated `.cs`; 4 hits printed]**

**Second half — is each local ever read? Run CASE-SENSITIVELY:**

| Site | Case-sensitive reads of the local below its declaration |
|---|---|
| **`Brute.cs:171`** | **ZERO** |
| `GruntBridge.cs:185` | **1** — `:186` `if (completed && impersonatedToken != IntPtr.Zero)` |
| `GruntHTTP.cs:191` | **1** — `:192` same |
| `GruntSMB.cs:185` | **1** — `:186` same |

**[invocation: per-file `-cmatch '\bcompleted\b'` from the declaration line forward; results printed in full]**

**And the enclosing-block check settles it — `Brute.cs:171-172` is the entire block:**

```
Brute.cs:171    bool completed = t.Join(5000);
Brute.cs:172  }
```
```
GruntBridge.cs:185    bool completed = t.Join(5000);
GruntBridge.cs:186    if (completed && impersonatedToken != IntPtr.Zero)
```
**[read] — brace-walk from the declaration line; `Brute`'s block closes on the line immediately after the capture; the siblings' block does not close until the gate has consumed the value.**

### 1.2 **(b) The null-handle gate — enumerated [verified]**

**Is the return-gate unique, or unique only among the four families I enumerated in D80? Measured:**

| File | `IntPtr.Zero` hits |
|---|---|
| `Data\Grunt\GruntBridge\GruntBridge.cs` | 2 — `:181` declaration, `:186` gate |
| `Data\Grunt\GruntHTTP\GruntHTTP.cs` | 2 — `:187` declaration, `:192` gate |
| `Data\Grunt\GruntSMB\GruntSMB.cs` | 2 — `:181` declaration, `:186` gate |
| **tree-wide total** | **6 hits, 3 files, 152 `.cs`** |

**`Brute.cs`: 0 hits. No file outside `Data\Grunt\` has any.** **[invocation: `Select-String 'IntPtr\.Zero'` over all 152 `.cs`; all 6 hits printed]**

### 1.3 **THE NARROWING D80's CLAIM NEEDS — and it is real**

**D80 said: "`if (completed && impersonatedToken != IntPtr.Zero)` — the only return-gate in the corpus."** **That is true for the `IntPtr`-typed handle. It is NOT true for null-handle tests generally**, and the difference is measured:

| Null-handle test shape | hits | files |
|---|---:|---:|
| `!= IntPtr.Zero` / `== IntPtr.Zero` | **6** | **3** |
| `!= null` | **1,161** | 33 |
| `== null` | **224** | 45 |
| `.HasValue` | 4 | 1 |
| `.IsAlive` | 17 | 4 |
| `IsNullOrEmpty` | 41 | 11 |
| `IsNullOrWhiteSpace` | 8 | 4 |

**[invocation: per-pattern `Select-String` over 152 enumerated `.cs`; counts and file counts printed]**

**So "the only return-gate in the corpus" must be read as: the only gate on an `IntPtr`-typed impersonation handle.** **The `IntPtr.Zero` census is complete and the three files that hold it are exactly the three families that can impersonate.** **The claim survives at that scope, and D80's phrasing was broader than its evidence.**

### 1.4 **THE T1 ANSWER: EXACTLY ONCE, and it is a census rather than a path count**

**The primitive — capture a completion gate into a local, then never read it — occurs exactly once in this corpus, at `Brute.cs:171`. `[verified]`**

**This is now a census, not a path count,** because **both halves of the primitive were enumerated across the full 152-file denominator rather than sampled from the four families D80 already knew:**
- **Capture sites: 4 total**, all in `Data\Grunt\`.
- **Null-handle gates: 6 total**, all in `Data\Grunt\`.
- **Case-sensitive read classification: 1 of 4 gates is never read.**

**The claim "exactly once" now rests on a complete enumeration of the primitive, not on the coincidence that D80 had examined four families.** **The boundary of the census is the 152-file denominator; `obj/`/`bin/` are excluded, and no `.razor` or `.cshtml` file was searched** (§4 residual 1).

---

## 2. T2 — the refutation condition, enumerated

### 2.1 **What would refute it, stated as falsifiable conditions**

**D80's T2 claim was: `TaskingType` is not client-reachable, proven three ways (0 binds in the task form · the numeric form feeds dispatch not definition · the loader reads YAML on disk at startup).**

**Stated as refutation conditions, ANY ONE of these would overturn it:**

| # | Condition | Status |
|---:|---|---|
| R1 | **A second `FromSerializedGruntTask` loader path reachable from a controller or hub** | **EXISTS BUT UNREACHABLE — see §2.2** |
| R2 | **A `Deserialize<SerializedGruntTask>` site outside `DbInitializer.cs`** | **EXISTS — `GruntTask.cs:173`. Unreachable — see §2.3** |
| R3 | **A `YamlDotNet` deserializer that is NOT bare** (e.g. `IgnoreUnmatchedProperties`) | **NO — all 9 sites are bare. Reinforced, see §2.4** |
| R4 | **A client-reachable route to `TaskingType` that bypasses the YAML loader entirely** | **EXISTS IN PRINCIPLE — `GruntTaskApiController.cs:62` binds `[FromBody] GruntTask`. See §2.5 — this is the one live refutation candidate** |

### 2.2 **R1 — the second loader path exists. Enumerated.**

**`FromSerializedGruntTask` call sites re-censused: 12, across 3 files** (`[verified]`, **up from the 11** D80 reported):

```
DbInitializer.cs:409    new GruntTask().FromSerializedGruntTask(S)
GruntTask.cs:142        internal GruntTask FromSerializedGruntTask(SerializedGruntTask task)   <- definition
GruntTask.cs:145        new GruntTaskAuthor().FromSerializedGruntTaskAuthor(task.Author)
GruntTask.cs:156        new GruntTaskOption().FromSerializedGruntTaskOption(O)
GruntTask.cs:174        return this.FromSerializedGruntTask(task);    <- FromYaml
GruntTask.cs:185        return this.FromSerializedGruntTask(task);    <- FromJson
GruntTaskAuthor.cs:37   definition
GruntTaskAuthor.cs:55   FromYaml
GruntTaskAuthor.cs:66   FromJson
GruntTaskOption.cs:42   definition
GruntTaskOption.cs:65   FromYaml
GruntTaskOption.cs:76   FromJson
```

**[invocation: `Select-String 'FromSerializedGruntTask'` over 152 `.cs`; all 12 printed]**

**`GruntTask.cs:170-186` is a second and third entry point into the same loader `[read]`:**
```csharp
public GruntTask FromYaml(string yaml)                                    // :170
{
    IDeserializer deserializer = new DeserializerBuilder().Build();        // :172  BARE
    SerializedGruntTask task = deserializer.Deserialize<SerializedGruntTask>(yaml);  // :173
    return this.FromSerializedGruntTask(task);                             // :174
}
public GruntTask FromJson(string json)                                     // :182
{
    SerializedGruntTask task = JsonConvert.DeserializeObject<SerializedGruntTask>(json);  // :184  NOT YamlDotNet
    return this.FromSerializedGruntTask(task);                             // :185
}
```

**`FromJson` does not use YamlDotNet at all.** **R-67.3's entire `YamlException` analysis therefore does not constrain this path** — a JSON body with `"TaskingType": 99` never meets the unknown-name guard that R-67.3 measured. **This is a genuine gap in R-67.3's coverage that its own fixture could not have found.**

### 2.3 **R1/R2 reachability — enumerated, and BOTH are unreachable [verified]**

**Reachability of `FromYaml`, every occurrence of the string:**

```
Models\Common.cs:13                    public T FromYaml(string yaml);          <- interface declaration
Models\Grunts\GruntTask.cs:170         public GruntTask FromYaml(string yaml)   <- implementation
Models\Grunts\GruntTaskAuthor.cs:51    implementation
Models\Grunts\GruntTaskComponents.cs:53  implementation
Models\Grunts\GruntTaskComponents.cs:108 implementation
Models\Grunts\GruntTaskComponents.cs:213 implementation
Models\Grunts\GruntTaskOption.cs:61    implementation
total = 7 — ALL declarations/implementations
```

**Call sites of `.FromYaml(`: ZERO.** **[invocation: `Select-String '\.FromYaml\('` with the leading dot, over 152 `.cs`; no output]**

**`FromYaml` is an interface method (`Models\Common.cs:13`) with six implementations and no caller anywhere in the corpus.** **[absence]**

**Reachability of `GruntTask.FromJson`: `.FromJson(` has 12 hits, and every one is a DIFFERENT type** — `GruntEncryptedMessage.FromJson` (`Brute:391`, `GruntBridge:400`, `GruntHTTP:430`, `GruntSMB:427`) and `GruntTaskingMessage.FromJson` (`Brute:452/457`, `GruntBridge:461/466`, `GruntHTTP:491/496`, `GruntSMB:488/493`). **A `GruntTask`-receiver `.FromJson(` call site: ZERO.** **[invocation: `Select-String 'new GruntTask\(\)\.FromJson|GruntTask\(\)\.FromJson|task\.FromJson'`; no output]**

**So R1 and R2 are REAL PATHS THAT EXIST and are `unreachable-from-corpus`. [read + verified]**

### 2.4 **R3 — all 9 deserializer builders are bare, and the census is now complete [verified]**

```
DbInitializer.cs:404             new DeserializerBuilder().Build()
GruntTask.cs:172                 new DeserializerBuilder().Build()
GruntTaskAuthor.cs:53            new DeserializerBuilder().Build()
GruntTaskComponents.cs:55        new DeserializerBuilder().Build()
GruntTaskComponents.cs:110       new DeserializerBuilder().Build()
GruntTaskComponents.cs:215       new DeserializerBuilder().Build()
GruntTaskOption.cs:63            new DeserializerBuilder().Build()
Models\Listeners\Profile.cs:92   new DeserializerBuilder().Build()
Models\Listeners\Profile.cs:146  new DeserializerBuilder().Build()
total = 9
```

**Nine sites, nine bare builders, zero options.** **R-67.3's case 7 (unknown KEY throws) therefore applies to NINE load paths, not one** — and per D80 §2.2 none of them is wrapped in a handler that downgrades the throw. **This reinforces D80's §2.2/§2.4 conclusion and widens its blast radius from one loader to nine.** [verified]

**Denominator note:** D67 recorded 14 bare sites; **I find 9 `DeserializerBuilder` sites.** **That is a discrepancy I am reporting rather than reconciling** — D67 may have counted serializer builders, or sites across additional file classes. **§4 residual 3.**

### 2.5 **R4 — the one live refutation candidate, and it needs its own probe**

**`GruntTaskApiController.cs:60-66` `[read]`:**
```csharp
[HttpPost(Name = "CreateGruntTask")]
[ProducesResponseType(typeof(GruntTask), 201)]
public async Task<ActionResult<GruntTask>> CreateGruntTask([FromBody] GruntTask task)   // :62
{
    GruntTask savedTask = await _service.CreateGruntTask(task);                          // :64
```

**`[FromBody] GruntTask` binds the API-side model via ASP.NET model binding (Newtonsoft.Json).** **It does NOT call `FromSerializedGruntTask`** — but **it does write `TaskingType`**, because `CovenantService.cs:2293` is `updatingTask.TaskingType = task.TaskingType;` and the create path stores the bound object.

**And the API-side enum IS converter-guarded — `[read]`:**
```csharp
// API\Models\GruntTaskingType.cs:17
[JsonConverter(typeof(StringEnumConverter))]
public enum GruntTaskingType { ... }
```
**`StringEnumConverter` on the API enum means JSON `"Assembly"` binds and JSON `99` is rejected at the binder.** **So R4 is CLOSED for the API route — the converter is the guard.**

**But it is closed by a DIFFERENT mechanism than D80 claimed.** D80 argued non-reachability from form bindings and YAML-on-disk. **The API route IS client-reachable; it is the `StringEnumConverter` that stops a numeric value, not the absence of a route.** **That is the honest correction, and it is the answer the Lead asked for: the refutation condition was reachable, and what defuses it is a converter attribute, not the reach argument.**

**`[inferred]`** — I did not build or execute the binder. The behaviour of `StringEnumConverter` on numeric input is a library property, not something this source proves. **§4 residual 2 states the probe.**

### 2.6 **THE T2 ANSWER**

**The `TaskingType` non-reachability claim SURVIVES, on a corrected argument:**

| Leg of D80's proof | Status |
|---|---|
| 0 `TaskingType` binds in `GruntTaskForm.razor` | **HOLDS** [verified] |
| the numeric form feeds dispatch, not the definition loader | **HOLDS — and the mechanism is now READ, not asserted.** `GruntTaskingForm.razor:51-59` emits `<option value="@(((Enum)typeof(GruntTaskingType).GetField(n).GetValue(null)).ToString("d"))">`. **The numeric string is a rendered `value` attribute — JavaScript-side presentation only.** The one place a numeric form is PARSED back is `:112`: `((int)Enum.Parse(typeof(GruntTaskingType), this.GruntTasking.Type.ToString())).ToString()` — **`Enum.Parse` over the model's OWN typed enum round-tripped through `ToString()`, i.e. `GruntTasking.Type` is already a `GruntTaskingType` before this line executes.** **No string-originated numeric value enters through this form.** [read; line printed, not cited from memory] |
| the loader reads YAML on disk at startup | **HOLDS but is INCOMPLETE — there are 9 deserializer sites and 2 extra `FromSerializedGruntTask` entry points, both `unreachable-from-corpus`** | [verified] |
| **(NEW)** the one client-reachable route (`[FromBody] GruntTask`) | **IS reachable, and is defused by `[JsonConverter(typeof(StringEnumConverter))]` at `API\Models\GruntTaskingType.cs:17`, not by unreachability** | [read] |

---

## 3. T3 — model-default sweep: which non-nullable defaults are security-relevant?

### 3.1 **The full initializer census [verified]**

**`SerializedGruntTask` (`Models\Grunts\GruntTask.cs:403-420`) — the type YAML actually binds to — 16 properties, 13 with initializers:**
```csharp
public string Name              { get; set; } = "";                                        // :405
public List<string> Aliases     { get; set; } = new List<string>();                        // :406
public SerializedGruntTaskAuthor Author { get; set; }                                      // :407  NO INITIALIZER
public string Description       { get; set; } = "";                                        // :408
public string Help              { get; set; } = "";                                        // :409
public ImplantLanguage Language { get; set; }                                              // :410  NO INITIALIZER
public IList<Common.DotNetVersion> CompatibleDotNetVersions { get; set; } = new List<...>(); // :411
public string Code              { get; set; } = "";                                        // :412
public GruntTaskingType TaskingType { get; set; } = GruntTaskingType.Assembly;              // :413  <- D80's finding
public bool UnsafeCompile       { get; set; } = false;                                     // :414
public bool TokenTask           { get; set; } = false;                                     // :415
public List<SerializedGruntTaskOption> Options { get; set; } = new List<...>();             // :416
public List<SerializedReferenceSourceLibrary> ReferenceSourceLibraries ... = new List<...>(); // :417
public List<SerializedReferenceAssembly> ReferenceAssemblies ... = new List<...>();         // :418
public List<SerializedEmbeddedResource> EmbeddedResources ... = new List<...>();            // :419
```

**`GruntTask` (`:21-401`) — 12 initializers:** `Author = new GruntTaskAuthor()` (`:27`) · `Name = "GenericTask"` (`:30`) · `Aliases = new List<string>()` (`:31`) · `Description = "A generic GruntTask."` (`:32`) · `Language = CSharp` (`:34`) · `CompatibleDotNetVersions = {Net35, Net40}` (`:35`) · `Code = ""` (`:37`) · **`Compiled = false` (`:38`)** · **`TaskingType = Assembly` (`:39`)** · **`UnsafeCompile = false` (`:51`)** · **`TokenTask = false` (`:52`)** · `Options = new List<...>()` (`:54`)

**[invocation: regex `^\s*(public|internal)\s+.*\{[^}]*\}\s*=\s*.+;` over the brace-walked class span; every hit printed]**

### 3.2 **THE SECURITY-RELEVANT ONES — four, and only one is genuinely fail-open**

| Property | Default | Direction | Trace |
|---|---|---|---|
| **`TaskingType`** | **`Assembly` (0)** | **FAIL-OPEN — routes to the `TaskExecute` path** | `:413` and `:39`, **both default to `Assembly`**. Consumed at `CovenantService.cs:2584` `Type = task.TaskingType` and `:2293`. |
| **`UnsafeCompile`** | **`false`** | **FAIL-SAFE** | `Compiler.cs:37` `= false`; the sink is `Compiler.cs:192` `CSharpCompilationOptions`, gated by the request field. An omitted key cannot turn unsafe compilation on. |
| **`TokenTask`** | **`false`** | **FAIL-SAFE (for the D80 defect)** | `InternalListener.cs:239` `Token = tasking.GruntTask == null ? false : tasking.GruntTask.TokenTask`. An omitted key means the grunt takes the `else` branch — honest reporting under D80 §1. |
| **`Compiled`** | **`false`** | **FAIL-SAFE, and note `:2282-2290`** | `CovenantService.cs:2285` forces `Compiled = false` when `Code` changes. |

### 3.3 **THE T3 ANSWER — `TaskingType` is the only fail-open default, and the pattern does NOT generalise**

**Enumerated 25 initializers across the two models (§3.1). Exactly one is security-relevant in the fail-open direction: `TaskingType = GruntTaskingType.Assembly`, and it defaults the same way in BOTH the serialized type (`:413`) and the domain type (`:39`).**

**The other three security-tinged defaults (`UnsafeCompile`, `TokenTask`, `Compiled`) all default `false` — the conservative direction. Two properties carry NO initializer at all: `Author` (`:407`) and `Language` (`:410`) in the serialized type.**

**`Author` with no initializer is the one worth naming:** `SerializedGruntTask.Author` (`:407`) is a reference type with no initializer, so an omitted `Author:` key yields `null` — **and `FromSerializedGruntTask` passes it straight into `new GruntTaskAuthor().FromSerializedGruntTaskAuthor(task.Author)` (`:145`).** **Whether that null-guards internally is not measured here (§4 residual 4).** **It is a null-dereference candidate, not a privilege candidate.**

**So the honest T3 conclusion: the default-in-the-model pattern is real and worth having swept, and the sweep found exactly one fail-open instance — the one D80 already had.** **The pattern does not generalise into a class of privilege bugs in this model.** [verified for the census; inferred for the direction classification]

---

## 4. Residual unknowns, each with a concrete probe

| # | Unknown | Probe |
|---:|---|---|
| 1 | **The T1 census denominator excludes `.razor` and `.cshtml`.** Blade/Razor components can hold `@code` blocks with C#. | Enumerate all `*.razor`/`*.cshtml` for `Join(`/`IntPtr.Zero`/`bool <x> =`. |
| 2 | **`StringEnumConverter`'s behaviour on numeric JSON input is a library property, not proven here.** §2.5's R4 closure rests on it. | Unit-probe `JsonConvert.DeserializeObject<API.Models.GruntTask>("{\"taskingType\":99}")` and confirm a `JsonSerializationException`. |
| 3 | **D67 counted 14 bare deserializer sites; I find 9.** §2.4. | Re-run D67's own invocation string and diff the two site lists line by line. |
| 4 | **Whether `FromSerializedGruntTaskAuthor(null)` null-guards** — §3.3. | Read `GruntTaskAuthor.cs:37-50` for a null check on the argument. |
| 5 | **Whether `GruntTask.FromJson` (`:182`) is genuinely dead or invoked via reflection/serialization.** §2.3 counts static call sites only. | Enumerate reflection use of these method names across 152 `.cs`. |

---

## 5. Instrument failures, this report

| # | Failure | Caught by | Effect |
|---:|---|---|---|
| 1 | **D80's "the only return-gate in the corpus" was stated wider than its evidence.** It is the only `IntPtr`-typed gate; `!= null` alone has 1,161 hits in 33 files. | The Lead's Rule 20, applied to my own headline | **none — §1.3 states the narrowing and preserves the claim at its true scope.** |
| 2 | **My first read-check of the `completed` local used case-INsensitive `-match`, and reported 4 "reads" of `Brute:171`'s local** — every one of them the ENUM MEMBER `GruntTaskingStatus.Completed`. | **the reported reads landing at `:185`, `:312`, `:737` — hundreds of lines from the local, in different methods** | **none — re-ran with `-cmatch`: `Brute` = ZERO reads. Every case-insensitive "read" was the enum member. `Select-String` is case-insensitive by default; this is the second time this exact defect has appeared in my lanes (D60 §6).** |
| 3 | **D80 reported 11 `FromSerializedGruntTask` call sites; the re-census finds 12.** | the Lead's instruction to re-count and print | **none — §2.2 prints all 12. The extra is `GruntTask.cs:174`/`:185` (the `FromYaml`/`FromJson` returns), which is exactly the second loader path T2 was meant to find.** |
| 4 | **D80 §2.1 presented `DbInitializer.cs:404` as the load path.** There are **9** deserializer sites and **3** entry points into the loader. | Rule 20 enumeration | **Yes — D80 §2.1 is INCOMPLETE. §2.2-2.4 correct it. The verdict survives; the route inventory did not.** |

**The species worth naming (per the Lead's request):** **failures 2 and 3 are the same shape in two directions.** Failure 2 is an **overcount produced by case-folding** — the instrument merged `completed` with `Completed` and returned a plausible small integer. Failure 3 is an **undercount produced by my own earlier probe** being narrower than the primitive. **Both were caught by reading the *reported line numbers* against the local's location, not by re-reading the regex.** **The defence that worked was positional: a read 141 lines away, in another method, is not a read of this local.**

| # | Failure | Caught by | Effect |
|---:|---|---|---|
| 5 | **This report's own draft asserted the numeric form's conversion "happens in `OnInitializedAsync`" — a mechanism I had not printed.** | **the final verification pass printing `GruntTaskingForm.razor:112` verbatim, which reads `Enum.Parse(typeof(GruntTaskingType), this.GruntTasking.Type.ToString())`** | **Conclusion unchanged; the cited mechanism was different from the real one. §2.6 now quotes the line.** **This is a distinct species from failures 1-4: not a miscount, but a CORRECT CONCLUSION resting on an UNVERIFIED MECHANISM — the kind of error that survives every numeric check because its numbers are ASCII characters rather than measurements.** |


---

## 6. Corrections to file with the Lead

1. **D80 §1.2's "only return-gate in the corpus" → "only `IntPtr`-typed return-gate," with the null-test census in §1.3.** [verified]
2. **D80 §2.1's load-path description is INCOMPLETE: 9 deserializer sites, 3 loader entry points (`DbInitializer.cs:409`, `GruntTask.cs:174`, `GruntTask.cs:185`). All three accounted for; two are `unreachable-from-corpus`.** [verified]
3. **R-67.3's coverage has a gap: `GruntTask.FromJson` uses `JsonConvert`, not YamlDotNet. Any residue of that analysis does not transfer to the JSON path.** [read]
4. **The T2 verdict survives on a CORRECTED argument** — the client-reachable API route (`GruntTaskApiController.cs:62`) is defused by `[JsonConverter(typeof(StringEnumConverter))]` at `API\Models\GruntTaskingType.cs:17`, not by unreachability. [read; library behaviour = residual 2]
5. **T3: exactly one fail-open default (`TaskingType`), 25 initializers enumerated, pattern does NOT generalise.** [verified]
6. **Discrepancy flagged, not reconciled: D67's 14 bare deserializer sites vs my 9.** §4 residual 3.

---

*End of D84. Pure source; no REA, no build, no execution. Primitive enumerated in both T1 halves; refutation condition enumerated rather than hedged in T2; 25 model initializers censused in T3. Four instrument failures, five self-corrections, six corrections filed.*
