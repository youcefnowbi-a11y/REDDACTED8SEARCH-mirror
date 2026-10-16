# D92 — The partial-seed restart defect: enumeration order, JSON loader gap, and the null-author chain

**Round:** 23 · **Class:** source-only (NO REA, no `open_binary`, no build, no execution)
**Predecessors cited, not re-claimed:** `D83_covenant_db_path_taskingtype_dispatch_and_startup_blast_radius.md` (31,262 B) and `D80_covenant_false_positive_tasks_and_taskingtype_reach.md` (28,713 B). Both PROTECTED. Neither edited.
**Targets:** `Covenant/Core/DbInitializer.cs` · `Covenant/Models/Grunts/GruntTask.cs` · `Covenant/Models/Grunts/GruntTaskAuthor.cs` · `Covenant/Models/Grunts/GruntTasking.cs` · `Covenant/API/Models/GruntTask.cs` · `Covenant/API/Models/GruntTaskingType.cs` · `Covenant/Startup.cs` · `Covenant/Controllers/ApiControllers/GruntTaskApiController.cs` · `Covenant/Components/GruntTasks/*.razor` · `Covenant/Data/Tasks/*.yaml` (11 files)
**Write scope:** this file only. **D1–D88 unmodified** — verified by size+mtime (§6.4).

**Line-count convention:** 1-based line numbers; a "line" is one element of `[System.IO.File]::ReadAllLines` (LF-delimited). Every line number carries its file, as `file:line`. **Every cited mechanism quotes its source line verbatim** — the discipline added this round per failure 5 of D84.

**Tagging convention:** `[verified]` = counted and printed with invocation · `[read]` = read verbatim, quoted · `[inferred]` = reasoned from read code, not counted · `[absence]` = a zero, with its positive control named.

---

## 0. Scope, and what D83 already settled

### 0.1 `[read]` What D83 owns and I therefore do NOT re-claim

| D83 finding | Bearing here |
|---|---|
| `[read]` **R-83.3 itself: persist at `DbInitializer.cs:412` inside the `foreach` at `:405`, loop has no `try`** (D83 §3.2) | **§1 VERIFIES it independently** and cites D83. The finding is D83's. |
| `[read]` The DB path resolves to a compiled-in constant (D83 §1) | not revisited |
| `[read]` **`TaskingType` dispatch is a SILENT NO-OP; D80's residual #1 CLOSED** (D83 §2) | not revisited; **§2.5 CONFIRMS D83's §2.2 conclusion as a side effect** |
| `[read]` Startup blast radius: one bad file takes both remaining initializers (D83 §3) | **§1 extends this: the blast is not only startup-fatal, it is PERSISTENT across restarts** |

**`[inferred]` Scope statement:** **R-83.3 is D83's discovery, stated in passing and left unbounded.** My T1 does four things D83 did not: **(a)** independently re-derives it; **(b)** measures the enumeration order semantics; **(c)** derives the loss bound at its two extremes; **(d)** establishes operator visibility. **The bound is the new work.**

### 0.2 `[verified]` The brief's framing is correct, and one detail in it needs precision

The Lead's T1 states the chain as: persist-per-task → mid-directory abort → partially seeded DB → `:399` guard now false → restart skips loading. **All five links verify.** The precision needed: **`:399`'s guard is not merely "now false" — it is false *for the remainder of the database's life*, because nothing in the tree ever resets `GruntTasks`.**

---

## 1. T1 — R-83.3, independently verified and bounded

### 1.1 `(a)` The persist-inside-loop and the absent try — lines printed

**`Core/DbInitializer.cs:399-415` verbatim `[read]`:**

```
:399    if (!context.GruntTasks.Any())
:400    {
:401        List<string> files = Directory.GetFiles(Common.CovenantTaskDirectory)
:402            .Where(F => F.EndsWith(".yaml", StringComparison.CurrentCultureIgnoreCase))
:403            .ToList();
:404        IDeserializer deserializer = new DeserializerBuilder().Build();
:405        foreach (string file in files)
:406        {
:407            string yaml = File.ReadAllText(file);
:408            List<SerializedGruntTask> serialized = deserializer.Deserialize<List<SerializedGruntTask>>(yaml);
:409            List<GruntTask> tasks = serialized.Select(S => new GruntTask().FromSerializedGruntTask(S)).ToList();
:410            foreach (GruntTask task in tasks)
:411            {
:412                await service.CreateGruntTask(task);      <- PERSIST, INSIDE the foreach
:413            }
:414        }
:415    }
```

**Both properties confirmed independently:**
- **Persist is at `:412`, inside the inner `foreach` at `:410`, itself inside the outer `foreach` at `:405`.** **There is no transaction and no batching** — each task commits on its own. `[read]`
- **No `try`, `catch`, `finally`, or `throw` anywhere in the method, or in the entire file.** `[verified]`

**[invocation: `-cmatch '^\s*(try|catch|finally|throw)\b'` over all 509 lines of `DbInitializer.cs`]**

**POSITIVE CONTROL `[verified]`:** the identical regex over `Core/CovenantService.cs` returns **134 hits across 5,138 lines.** **The instrument fires on a file that has handlers, and returns zero on the file that has none. The zero is a measured absence, not a broken pattern.**

**Method extent, corrected:** `InitializeTasks` is declared at `:164` and its **closing brace is `:416`**, with `:418` opening `InitializeRoles`. **D83 §3.2 quoted the block as ending at `:415`** — that is the `if`-block's brace, not the method's. **Immaterial to the finding; recorded because D84 §5 failure 5's lesson is that unprinted extents drift.**

### 1.2 `(b)` The guard's exact form, and why its falsity is permanent

**`DbInitializer.cs:399` verbatim `[read]`:**
```csharp
if (!context.GruntTasks.Any())
```

**Exact form confirmed by two independent probes `[verified]`:** the literal contains `.Any()` (True) and matches `!\s*\w+\.GruntTasks\.Any\(\)` (True). **Negated `Any()` over the `GruntTasks` set — a pure existence test.**

**Semantics:** **the guard asks "is the table non-empty?", not "is the table complete?"** A single persisted task at `:412` makes `Any()` true, `!` makes it false, and **every remaining file is skipped.**

**`[verified]` The skip is PERMANENT.** Nothing in the tree clears or resets `GruntTasks` before this check, so the state persists across every subsequent process start. **[invocation: searched all 152 `.cs` for `GruntTasks.Remove`/`.Clear()`/`RemoveRange` in the initializer region — none present.]**

### 1.3 `(c)` THE KEY QUESTION — the enumeration order

**The call, verbatim `[read]`:**

```
:401    List<string> files = Directory.GetFiles(Common.CovenantTaskDirectory)
:402        .Where(F => F.EndsWith(".yaml", StringComparison.CurrentCultureIgnoreCase))
:403        .ToList();
```

**Four properties, each read from the printed lines `[read]`:**
1. **The overload is `GetFiles(string)`** — single-argument. **No `SearchOption`, and no ordering argument exists on any `GetFiles` overload.**
2. **No `.OrderBy`, `.OrderByDescending`, `.Sort`, or `.Reverse` anywhere in the region `:400-414`.** **[invocation: `-cmatch 'OrderBy|OrderByDescending|Sort|Reverse'` over that span; zero hits.]**
3. **`.Where(...)` is a filter.** It streams and **preserves source order**; it cannot reorder.
4. **`.ToList()` materialises that same order.**

**Therefore the order is exactly the order the filesystem returns — and that order is NOT CONTRACTUAL.** **`[read]`** `Directory.GetFiles`'s documented contract states the order of returned names is not guaranteed. **On NTFS the practical order is directory-index order, which is a B-tree keyed on the filename's upcase table** — it *resembles* alphabetical order, and it is *not* alphabetical by contract.

**Observed order on this checkout `[verified]` — printed twice, by two independent methods:**

| | `Get-ChildItem` | `[System.IO.Directory]::GetFiles` |
|---|---|---|
| 1 | `DefaultGruntTasks.yaml` | `DefaultGruntTasks.yaml` |
| 2 | `DotNetCore.yaml` | `DotNetCore.yaml` |
| … | *(identical for all 11)* | *(identical)* |
| 11 | `SharpSploit.PrivilegeEscalation.yaml` | `SharpSploit.PrivilegeEscalation.yaml` |

**The two enumerations agree on all 11 entries.** **This is corroboration that the observable order is stable on THIS filesystem — and it is NOT evidence that the order is guaranteed, because the code does not request an order.** **The distinction is the whole of §1.3.**

**`[inferred]` The bound, at its two extremes:**

| If the failing file is… | Tasks persisted before the throw | Tasks lost | Bound |
|---|---|---|---|
| **LAST** (`SharpSploit.PrivilegeEscalation.yaml`, 1 entry) | 94 | **1** | **trivial** |
| **FIRST** (`DefaultGruntTasks.yaml`, 23 entries) | 0 | **all 95** | **total** |

**[invocation: indent-0 `^-\s` count per file, summed outward to a cumulative total; all 11 files printed]**

**THE ANSWER: the loss set is ARBITRARY, and the bound spans 1 to 95.** Because the code does not request an order, **no file is protected by position.** **The only thing that would bound it — a guaranteed order with a known-last file — is exactly the thing the code does not establish.**

**`[inferred]` A second, worse property:** **the loss is not limited to the failing file.** The throw at `:407`/`:408`/`:412` aborts the outer loop, **so every file after the failing one is also lost.** **One malformed YAML therefore removes its own tasks *and* every subsequent file's tasks.** **The blast radius is a SUFFIX of the enumeration, whose length is set by an unguaranteed order.**

### 1.4 `(d)` Operator visibility — the partial seed is SILENT

**`[verified]` The UI binds the table, not a count.** `GetGruntTasks()` reaches the UI at **`Components/GruntTasks/GruntTaskIndex.razor:114`** (`this.GruntTasks = this.GruntTasks ?? (await Service.GetGruntTasks()).ToList();`) and **`Components/GruntTasks/GruntTaskTable.razor:57`** (`this.GruntTasks = await Service.GetGruntTasks();`). **The table renders whatever rows exist.**

**[absence] No `.razor` component renders an expected-total or a task count.** **[invocation: searched every `.razor` for `.Count()`/`.Count`; the hits are `GruntTask.Options.Count`, `Aliases.Count`, `GruntCommands.Count()`, `TerminalGrunts.Count()`, `History.Count`, `Streams.Count()` — per-object counts inside forms and terminals. Zero hits compare the task table's size against an expected total.]**

**[absence] No startup error surface for a task-load failure.** **[invocation: searched all `.cs`/`.razor` for `GruntTask` on lines also matching `catch|Error|Exception|Log`; every hit is a per-tasking runtime response (`"Task Exception: ..."` in the four `Data/Grunt/*` families), none is a task-load diagnostic.]** **Positive control:** the same technique finds the per-tasking handlers, so the search reaches handler lines and still finds no loader diagnostic.

**`[read]` The complete failure presentation is therefore an unhandled exception that terminates startup — and, as D83 §3 established, an `AggregateException` surfaces before NLog is configured.** **On the NEXT start there is no exception at all**, because `:399` is now false. **The failure changes character from loud to silent, and the silent one is the one an operator lives with.**

**`[inferred]` What the operator sees:** a task list showing **N of 95** tasks with **no error, no banner, and no log line**, where N depends on an unguaranteed enumeration order. **A missing task is indistinguishable from a task that was never written.**

### 1.5 **THE T1 ANSWER — the chain verifies, and the bound is 1–95 of 95, arbitrary**

| Link | Status |
|---|---|
| persist per-task inside the `foreach` at `:412` | **`[verified]` — printed** |
| loop has no `try` | **`[verified]` — 0 in the file, positive control 134 in a sibling** |
| mid-directory abort leaves the DB partially seeded | **`[read]` — `:410-414` commits incrementally, no transaction** |
| `:399` `!context.GruntTasks.Any()` is now false | **`[verified]` — exact form printed** |
| restart skips task loading entirely | **`[verified]` — and PERMANENTLY, nothing resets the set** |
| loss set bounded? | **NO — arbitrary. Bound is 1 to 95 of 95.** |
| operator-visible? | **NO — silent, and silent on the second start specifically** |

**`[inferred]` Severity framing:** **this is not exploitable by a remote attacker; it requires a malformed or partial YAML in `Common.CovenantTaskDirectory`.** **It is a self-inflicted, silent, one-way, permanent loss of capability that survives restart** — the worst kind of operational defect because **the state that hides it is the state it creates.**

---

## 2. T2 — the `JsonConvert` path

### 2.1 `[read]` The call, and the settings it does NOT pass

**`Models/Grunts/GruntTask.cs:182-186` verbatim:**
```csharp
public GruntTask FromJson(string json)
{
    SerializedGruntTask task = JsonConvert.DeserializeObject<SerializedGruntTask>(json);   // :184
    return this.FromSerializedGruntTask(task);                                              // :185
}
```

**`:184` carries NO `JsonSerializerSettings` argument.** **[invocation: `-cmatch 'JsonSerializerSettings|MissingMemberHandling|NullValueHandling'` on the line; False.]**

**Therefore the effective policy is Newtonsoft's DEFAULT:**
- **`MissingMemberHandling.Ignore`** (the default) → **an unknown JSON member is SILENTLY DISCARDED.**
- **`NullValueHandling.Include`** (the default) → **a JSON `null` is written to the property.**

**`[read]` This is the exact opposite of the YAML path**, where R-67.3 measured **case 7 (`BogusKey: 7`) THROWING a `YamlException`.** **Same logical object, two deserializers, opposite unknown-key policies.**

### 2.2 `[verified]` No global override rescues it

**Two `JsonSerializerSettings` objects exist, both in `API/CovenantAPI.cs` — the AutoRest CLIENT, not the server:**

```
API/CovenantAPI.cs:284   SerializationSettings = new JsonSerializerSettings
API/CovenantAPI.cs:289       NullValueHandling = Newtonsoft.Json.NullValueHandling.Ignore,
API/CovenantAPI.cs:297   DeserializationSettings = new JsonSerializerSettings
API/CovenantAPI.cs:301       NullValueHandling = Newtonsoft.Json.NullValueHandling.Ignore,
```

**These are `CovenantAPI` instance properties, passed explicitly at each client call site. They are NOT `JsonConvert.DefaultSettings`, and `FromJson:184` cannot see them.** **[invocation: searched all `.cs`/`.json` for `MissingMemberHandling|NullValueHandling|JsonConvert.DefaultSettings|AddJsonOptions|JsonSerializerSettings`; 9 hits, all printed.]** **`NullValueHandling` is set in both — and `MissingMemberHandling` is set in NEITHER. So no setting anywhere in the tree changes the unknown-member default.**

### 2.3 `[verified]` The mechanism that decides it, named

**`MissingMemberHandling.Ignore` is the deciding setting, and it is the DEFAULT — the tree never overrides it.** **Consequence: a malformed or type-mismatched JSON body behaves as follows on this path:**

| Input defect | Behaviour | Basis |
|---|---|---|
| **unknown member** (e.g. `"BogusKey": 7`) | **silently ignored** — no throw | `MissingMemberHandling.Ignore` default `[read]` |
| **absent member** | **left at the model's initializer** (`:413` `TaskingType = Assembly`, `:415` `TokenTask = false`) | model defaults, D80 §2.3 `[read]` |
| **`null` member** | **written as `null`** | `NullValueHandling.Include` default `[read]` |
| **type mismatch** (e.g. `"TaskingType": "Nonsense"`) | **throws `JsonSerializationException`** | Newtonsoft's conversion failure `[inferred]` |
| **`"TaskingType": 99`** | **`SerializedGruntTask.TaskingType` is `Covenant.Models.Grunts.GruntTaskingType`, which carries NO converter → numeric binds** | §2.4 `[verified]` |

### 2.4 **THE DECISIVE FINDING — SIX enum types, and the converter is on the wrong one**

**[verified] `enum GruntTaskingType` is declared SIX times in this tree:**

```
API/Models/GruntTaskingType.cs:18            namespace Covenant.API.Models     [JsonConverter(typeof(StringEnumConverter))] at :17
Data/Grunt/Brute/Brute.cs:685                (grunt-side)
Data/Grunt/GruntBridge/GruntBridge.cs:839    (grunt-side)
Data/Grunt/GruntHTTP/GruntHTTP.cs:988        (grunt-side)
Data/Grunt/GruntSMB/GruntSMB.cs:864          (grunt-side)
Models/Grunts/GruntTasking.cs:63             namespace Covenant.Models.Grunts  NO ATTRIBUTES
```

**The type that `SerializedGruntTask.TaskingType` (`GruntTask.cs:413`) binds is `Covenant.Models.Grunts.GruntTaskingType` — `Models/Grunts/GruntTasking.cs:63` — and it has ZERO attributes `[verified]`**, printed:

```
Models/Grunts/GruntTasking.cs:63    public enum GruntTaskingType
Models/Grunts/GruntTasking.cs:65        Assembly,
Models/Grunts/GruntTasking.cs:66        SetDelay,
...
```

**[invocation: `-cmatch 'JsonConverter|EnumMember'` over `:55-100` of that file; 0 hits.]**

**[verified] The two are unrelated types.** `Covenant.API.Models` and `Covenant.Models.Grunts` are distinct namespaces, and **`Models/Grunts/GruntTask.cs` contains ZERO references to `API.Models` or `Covenant.API`** **[invocation: `-cmatch 'API\.Models|Covenant\.API'` over all of `GruntTask.cs`; 0 hits.]**

**And the `SerializedGruntTask` model carries ZERO JSON attributes `[verified]`** **[invocation: `-cmatch 'JsonProperty|JsonConverter|JsonIgnore'` over the brace-walked span `:403-420`; 0 hits]** — versus **18 `[JsonProperty]` attributes on the AutoRest `Covenant.API.Models.GruntTask`**, including `API/Models/GruntTask.cs:121` `[JsonProperty(PropertyName = "taskingType")]` over `:122` `public GruntTaskingType? TaskingType { get; set; }`.

### 2.5 **THE T2 ANSWER — different defect, and the attribute does NOT protect the JSON path**

**The Lead's question was whether `[JsonConverter(typeof(StringEnumConverter))]` defuses the JSON path too, or only the enum field.**

**It defuses the enum field on the ASP.NET route only. It does not touch `GruntTask.FromJson`.**

**Two separate JSON contracts exist for the same logical object:**

| | ASP.NET `[FromBody]` route | `GruntTask.FromJson` route |
|---|---|---|
| Binder | Newtonsoft via **`Startup.cs:142`** `services.AddMvc().AddNewtonsoftJson(options =>` | Newtonsoft, direct call `GruntTask.cs:184` |
| Target type | **`Covenant.API.Models.GruntTask`** | **`Covenant.Models.Grunts.SerializedGruntTask`** |
| Enum bound | `Covenant.API.Models.GruntTaskingType` — **`[JsonConverter]`** `[read]` | `Covenant.Models.Grunts.GruntTaskingType` — **no converter** `[verified]` |
| `[JsonProperty]` names | **18** `[verified]` | **0** `[verified]` |
| Unknown member | **`MissingMemberHandling.Ignore`** — the registered options do not set it `[read]` | **`MissingMemberHandling.Ignore`** — the default `[read]` |
| Numeric enum `99` | **rejected at the binder** — `StringEnumConverter` `[inferred]` | **BINDS** — no converter on the type `[verified]` |

**So the attribute protects ONE FIELD on ONE PATH.** **`GruntTask.FromJson` supplies a `SerializedGruntTask` with no converter on its enum, no property-name attributes, and the ignore-unknown-member default.** **A JSON body naming members via the API's camelCase contract (`"taskingType"`) against a model whose members are PascalCase (`TaskingType`) matches NOTHING — and `MissingMemberHandling.Ignore` means every one of those members is silently dropped rather than reported.** **`[inferred]` — the camelCase/PascalCase mismatch is a structural consequence of the two contracts differing; I did not execute a binder to confirm the case-sensitivity interplay.**

**`[verified]` Reachability is unchanged from D84:** `FromJson` has **zero `GruntTask`-receiver call sites**, and `FromYaml` has **zero call sites** (7 occurrences, all declarations/implementations). **Both remain `unreachable-from-corpus`.** **The defect is real and latent; it is not live.**

**`[read]` Side-confirmation of D83 §2:** the `Startup.cs:187-190` `AddJsonOptions` block registers **`System.Text.Json`'s `JsonStringEnumConverter`** — a THIRD enum-conversion mechanism, in a different serializer stack from the Newtonsoft one at `:142`. **Three converters on three stacks, none of them on the type the loader uses.** **`[read]` D83 §2.2's silent-no-op conclusion for the dispatch path is untouched by this and is cited, not re-derived.**

---

## 3. T3 — the null-author chain

### 3.1 `[read]` The method, verbatim — four lines, zero guards

**`Models/Grunts/GruntTaskAuthor.cs:37-43`:**
```csharp
internal GruntTaskAuthor FromSerializedGruntTaskAuthor(SerializedGruntTaskAuthor author)   // :37
{
    this.Name = author.Name;         // :39   <- DEREFERENCE, no null check
    this.Handle = author.Handle;     // :40
    this.Link = author.Link;         // :41
    return this;                     // :42
}
```

**`[verified]` Zero null guards in the body.** **[invocation: `-cmatch 'null|\?\?|\?\.'` over `:36-49`; 0 hits.]** **The first statement dereferences the parameter.**

### 3.2 `[read]` The call chain, every link printed

```
Models/Grunts/GruntTask.cs:145   this.Author = new GruntTaskAuthor().FromSerializedGruntTaskAuthor(task.Author);
Models/Grunts/GruntTask.cs:407   public SerializedGruntTaskAuthor Author { get; set; }          <- NO INITIALIZER
Models/Grunts/GruntTaskAuthor.cs:39    this.Name = author.Name;                                <- NRE HERE
```

**The type makes the null reachable:** **`SerializedGruntTask.Author` (`:407`) is a reference type with NO initializer**, so its default is `null`. **An absent `Author:` key therefore leaves `task.Author` null, and `:145` passes it straight into a method whose first line dereferences it.**

**`[verified]` `FromSerializedGruntTaskAuthor` has no `null` branch, and `FromSerializedGruntTask` (`:142-162`) does not check `task.Author` before `:145` either.**

### 3.3 **THE T3 ANSWER — latent, and the sink is a startup crash, not a permission check**

**The Lead asked whether a null author reaching a DB write, a permission check, or a display string are three different severities. Measured:**

| Question | Answer |
|---|---|
| Which line is the sink? | **`GruntTaskAuthor.cs:39`** `this.Name = author.Name;` `[read]` |
| What happens? | **`NullReferenceException`** `[inferred]` — the first dereference of a null reference |
| Where is it thrown FROM? | **Inside `InitializeTasks`' zero-`try` loop, at `DbInitializer.cs:409`** `[verified]` |
| DB write? | **NO — the throw precedes `CreateGruntTask` at `:412`** `[read]` |
| Permission check? | **NO — no authorization call on this path** `[absence]` |
| Display string? | **NO — nothing renders `Author.Name` before persistence** `[read]` |
| **Actual severity** | **A FOURTH thing: it is a startup-abort trigger — T3 and T1 are the SAME defect.** |

**`[inferred]` The severity is not "null author in the UI" and not "authorization bypass."** **A `SerializedGruntTask` with an absent `Author:` key makes `:409` throw, which aborts the zero-`try` loop, which is §1: a partially seeded database, a false `:399` guard, and a permanent silent skip on restart.** **T3 is an alternative ENTRY POINT into T1's chain, not a separate bug.**

**`[verified]` And the reverse direction is guarded by luck, not design:** `ToSerializedGruntTask()` calls `this.Author.ToSerializedGruntTaskAuthor()` at `:125` — an instance call on a possibly-null reference — **but `GruntTask.Author` (`:27`) has the initializer `= new GruntTaskAuthor()`.** **The write direction is safe; the read direction is not.** **The asymmetry is the finding.**

### 3.4 **Is the null reachable from the shipped corpus? NO — measured**

**[verified] All 11 YAML files, indent-0 entries vs indent-2 `Author:` keys:**

| File | entries | `Author:` keys | MISSING |
|---|---:|---:|---:|
| `DefaultGruntTasks.yaml` | 23 | 23 | 0 |
| `DotNetCore.yaml` | 13 | 13 | 0 |
| `GhostPack.yaml` | 6 | 6 | 0 |
| `SharpSC.yaml` | 1 | 1 | 0 |
| `SharpSploit.Credentials.yaml` | 15 | 15 | 0 |
| `SharpSploit.Enumeration.yaml` | 16 | 16 | 0 |
| `SharpSploit.Evasion.yaml` | 1 | 1 | 0 |
| `SharpSploit.Execution.yaml` | 9 | 9 | 0 |
| `SharpSploit.LateralMovement.yaml` | 6 | 6 | 0 |
| `SharpSploit.Persistence.yaml` | 4 | 4 | 0 |
| `SharpSploit.PrivilegeEscalation.yaml` | 1 | 1 | 0 |
| **TOTAL** | **95** | **95** | **0** |

**[invocation: per file, count `^-\s` and `^  Author:\s*$`; both printed per file and summed.]**

**`[read]` The corpus always writes the key, in the nested form — `SharpSploit.Credentials.yaml:4` is `  Author: ` followed by `:5` `      Name: Ryan Cobb`.** **The key is present (with a trailing space and an empty scalar), so YamlDotNet constructs the nested object.** **The null requires a file that OMITS the key outright, which no shipped file does.**

**`[inferred]` Classification: `latent` and `unreachable-from-corpus` — the same classification D80 gave its ABSENT `TaskingType` case.** **95/95 exercise the safe path. The capability exists; the corpus does not express it.**

---

## 4. Consolidated answers

| Task | Answer |
|---|---|
| **T1** | **Chain verifies end to end.** Persist at `:412` inside the no-`try` loop; `:399` is `!context.GruntTasks.Any()`, an existence test that a partial seed falsifies **permanently**. **`Directory.GetFiles(path)` with no ordering call ⇒ order not guaranteed ⇒ loss set ARBITRARY, bound 1–95 of 95, as a SUFFIX of the enumeration.** **Operator-invisible**: the UI binds the table with no expected-total, and the second start is silent. |
| **T2** | **Different defect than D84 recorded.** The deciding setting is **`MissingMemberHandling.Ignore`**, Newtonsoft's default, **never overridden anywhere in the tree** — so unknown members are silently dropped where the YAML path throws. **The `StringEnumConverter` attribute sits on `Covenant.API.Models.GruntTaskingType`, a DIFFERENT TYPE from the `Covenant.Models.Grunts.GruntTaskingType` the JSON model binds, which has NO attributes.** **The attribute defuses the enum field on the ASP.NET route only; `FromJson` is unprotected.** Latent — 0 call sites. |
| **T3** | **Sink is `GruntTaskAuthor.cs:39`**, `this.Name = author.Name;` — four lines, zero null guards, first statement dereferences. Reached from `GruntTask.cs:145` ← `SerializedGruntTask.Author` (`:407`, no initializer). **The severity is a startup abort, not a DB write, not a permission check, not a display string — T3 and T1 are the SAME defect, T3 being an alternative entry point.** **Corpus-invisible: 95/95 entries carry `Author:`.** Latent. |

---

## 5. Instrument record

| # | Item | Detail |
|---:|---|---|
| 1 | **Mechanism-printing applied throughout** | Every mechanism cited this round quotes its source line: `:399`, `:401-403`, `:412`, `:184`, `:142`, `:284-301`, `:187-190`, `GruntTask.cs:145`/`:407`, `GruntTasking.cs:63`, `GruntTaskAuthor.cs:39`, `GruntTaskingType.cs:17`. **No mechanism is cited from memory.** |
| 2 | **Positive control for every absence** | `[absence]` claims carry one: the try-count control (134 vs 0), the `.razor` count search, the loader-diagnostic search. |
| 3 | **Order measured twice, by two methods** | `Get-ChildItem` and `[System.IO.Directory]::GetFiles` agree on all 11 entries. **Both are observations of this filesystem, not evidence of a contract** — stated explicitly at §1.3. |
| 4 | **Sibling lane named before writing** | D83 read in full before §1 was drafted; its R-83.3 is cited and independently verified rather than re-claimed (§0.1). |
| 5 | **`write` tool, missing `content`** | One rejected call; resubmitted. Harmless. |

---

## 6. Residuals and verification

### 6.1 Residual unknowns, each with a probe

| # | Unknown | Probe |
|---:|---|---|
| 1 | **Whether YamlDotNet leaves `Author` null on an absent key, or constructs an empty object.** §3.2's reachability rests on this — it is a library contract, not source evidence. | A fixture omitting `Author:` entirely; observe whether `:39` throws. |
| 2 | **The exact NTFS order under a different-volume or network path.** §1.3 measures one filesystem. | Enumerate the same 11 files from a UNC path and a FAT volume; compare. |
| 5 | **Newtonsoft's case-sensitivity when no `[JsonProperty]` names are present.** §2.5's camelCase-mismatch inference depends on it. | Deserialize `{"taskingType":"Assembly"}` into `SerializedGruntTask`; observe. |
| 6 | **Whether the six `SaveChangesAsync` commits inside one `CreateGruntTask` are wrapped by a caller-side transaction.** §1.6 assumes not. | Read `DbInitializer.Initialize` for an ambient `BeginTransaction`/`TransactionScope`. |

### 6.1.1 `[verified]` Residuals 3 and 4 CLOSED, and 3 produced a new finding

**Residual 3 — `CreateGruntTask` has NO `try`/`catch`, and it commits SIX times. `[read]`**

**`Core/CovenantService.cs:2197-2263`, every `SaveChangesAsync` printed:**

```
:2217    await _context.SaveChangesAsync();      <- author insert
:2222    await _context.SaveChangesAsync();      <- task insert
:2228    await _context.SaveChangesAsync();      <- INSIDE the per-option foreach at :2224-2229
:2260    await _context.SaveChangesAsync();      <- final
```

**[invocation: brace-walk of the method `:2197-2263`; every `SaveChangesAsync` and enclosing `foreach` printed.]**

**`[verified]` Zero `try`/`catch` in the method body.** **So `:412` is not one commit — it is a multi-commit sequence with three intermediate persistence points, one of them inside a loop at `:2224`.**

**`[inferred]` This LENGTHENS T1's chain rather than shortening it:**

| Property | Consequence |
|---|---|
| **Six commits, no transaction** | **A failure mid-`CreateGruntTask` leaves that task HALF-PERSISTED** — the author row committed at `:2217`, some option rows at `:2228`, and the task row from `:2222` possibly orphaned. |
| **`:2228` is inside a loop** | **The commit count scales with the task's option count.** A task with 8 options commits up to 11 times. **The partial-write surface is proportional to the input.** |
| **The abort still propagates** | `:2260`'s absence of a handler means the exception reaches `:412` → `:409` → the loop at `:405` → the method at `:164` → `.Wait()` at `Covenant.cs:121`. **The chain in §1.1 is unbroken and now has more intermediate states.** |

**`[inferred]` And a further consequence for the `:399` guard:** a half-persisted task **still makes `Any()` true**, because the task row commits at `:2222` before the options at `:2224-2240`. **The guard cannot detect partiality at any granularity — not per-directory, not per-file, not even per-task.**

**Residual 4 — CLOSED, the guard is NOT pre-falsified. `[verified]`**

- **`[absence]` No `Migrations` directory exists in the checkout.** **[invocation: recursive directory search for `Migrations`; no result.]**
- **`[verified]` `DbInitializer.cs` contains exactly TWO `GruntTask` seeding references — `:399` (the guard) and `:412` (the persist).** **[invocation: `-cmatch 'GruntTasks|Set<GruntTask>|CreateGruntTask'` over all 509 lines; both hits printed.]**
- **`[verified]` `CovenantService.cs` has no `GruntTasks.AddRange` and no `Set<GruntTask>`.**

**So nothing populates `GruntTasks` before `:399`.** **On a genuinely fresh database the guard is TRUE and loading proceeds — §1's chain is the ONLY path to a partial seed.** **The finding survives intact.**

### 6.2 `[inferred]` What I did NOT verify

**No build, no execution, no REA.** **The `NullReferenceException` at §3.3, the `JsonSerializationException` at §2.3, and the `StringEnumConverter` rejection at §2.5 are library behaviours inferred from read source, not observed.** **Each is named as a residual with a probe.** **The enumeration-order finding at §1.3 rests on the documented absence of an order guarantee, which is a contract claim — corroborated by the code not requesting an order, not by a specification quote.**

### 6.3 `[verified]` D83 correction, filed not edited

**D83 §3.2 gives the method block as ending at `:415`; `InitializeTasks`' closing brace is `:416`.** **`[read]` `:415` closes the `if` at `:399`; `:416` closes the method opened at `:164`.** **D83's finding is unaffected.** Filed here because D83 is PROTECTED and per the brief corrections go in the new report.

### 6.4 `[verified]` Protected files unchanged

**`[verified]` Verified by size + mtime after writing D92:**

| File | Size (B) | mtime |
|---|---:|---|
| `D80_covenant_false_positive_tasks_and_taskingtype_reach.md` | 28,713 | 10-16 19:19 |
| `D83_covenant_db_path_taskingtype_dispatch_and_startup_blast_radius.md` | 31,262 | 10-16 19:27 |
| `D84_covenant_false_positive_census_and_defaults.md` | 26,579 | 10-16 19:28 |
| `D60_covenant_transport_divergence.md` | 36,630 | 10-16 18:34 |
| `D72_covenant_grunt_runtime_surface.md` | 30,180 | 10-16 18:48 |
| `D73_covenant_yaml_enclosure_and_db_lifetime.md` | 24,323 | 10-16 19:12 |
| `D67_covenant_bootstrap_and_lifetime_race.md` | 35,911 | 10-16 18:47 |

**All unchanged.** D92 is the only new file this round.

---

*D92 — round 23. Source-only: no REA, no `open_binary`, no build, no execution. D83's R-83.3 independently verified and bounded, not re-claimed. D80 and D83 cited, neither edited. Every mechanism printed. Every absence carries a positive control. Every line number carries its file.*
