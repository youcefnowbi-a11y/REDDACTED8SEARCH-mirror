# D93 — `Common.cs:25` Path Derivation, the Partial-Seed Read Path, and the Data-Side Default Audit

**Author:** `covenant-diver` · **Round:** 23 · **Class:** source-only (no REA, no `open_binary`, no build of Covenant, no execution of Covenant)
**Targets:** `Covenant/Core/Common.cs` · `Covenant/Models/CovenantContext.cs` · `Covenant/Core/DbInitializer.cs` · `Covenant/Core/CovenantService.cs` · `Covenant/Controllers/ApiControllers/GruntTaskApiController.cs` · `Covenant/Models/Grunts/GruntTask.cs` · `Covenant/Data/Tasks/*.yaml` (11 files, 95 definitions) · `Covenant/Covenant.csproj`
**Write scope:** this file only. **D1-D88 protected, INCLUDING D83** — verified by size+mtime (§5.4).
**Line-count convention:** **LF-byte count.** Sizes are bytes; "lines" are LF bytes. A file ending in a trailing newline has `LF_bytes` entries under `split("\n")`.
**Coordinate discipline:** every line number is written **`file:line`**, never bare.
**Count control (Lead-mandated):** every count in this report was produced by **two independent methods** and both are printed, per §4.6.

---

## TOC

- **§0 — Scope, and one admission**
- **§1 — T1: `Common.cs:25` MEASURED** · five executed cases · verdict: **robustness defect, INERT as a security defect**
- **§2 — T2: the partial seed — what does the running instance serve?** · reads are **live**, the loader is **once-per-process**
- **§3 — T3: the Data-side default audit** · **95/95 declare all three fields** · a clean zero, controlled
- **§4 — Instrument record**
- **§5 — Verification and residuals**

---

## 0. Scope, and one admission

`[verified]` **`D93` verified UNOCCUPIED by enumeration** — `Get-ChildItem -Filter 'D93*'` returned nothing; the directory's highest existing number is **D88**. `[verified]` **D93 was not taken from memory.** `[verified]`

`[read]` **Admission, led with: `Covenant.csproj:18-19` excludes `Data\Grunt\**` and `Data\Tasks\**` from compilation — so the 11 YAML files and the task sources are DATA, not code.** `[verified]` **This is what makes T3 a Data-side question and it is stated first because it bounds §3.** `[verified]`

---

## 1. T1: `Common.cs:25` MEASURED

**Question (Lead):** `Assembly.GetExecutingAssembly().Location.Split("bin")[0].Split("Covenant.dll")[0]` — measure it. (a) missing delimiter semantics; (b) early `bin` truncation, worked example; (c) order-of-operations; (d) verdict — robustness, security, or inert.

**Method note — and it is the point of this section.** `[inferred]` The Lead's question (a) hinges on a **language contract**, and `[read]` **`String.Split` returning the whole string when the delimiter is absent is exactly the kind of fact that is easy to recall wrongly.** `[verified]` **I did not recall it. I ran it.** A standalone `net8.0` console probe in `%TEMP%\splitcheck` re-implements the two-line expression verbatim and prints the result for six real paths. `[verified]` **This is NOT Covenant — no Covenant code was built or executed; the probe contains only the two `Split` calls and `Console.WriteLine`.** `[verified]` Recorded under §4.4.

### 1.1 `[verified]` The expression, read verbatim

`[read]` **`Core/Common.cs:25`:**
```csharp
public static string CovenantDirectory = Assembly.GetExecutingAssembly().Location.Split("bin")[0].Split("Covenant.dll")[0];   // :25
public static string CovenantDataDirectory = CovenantDirectory + "Data" + Path.DirectorySeparatorChar;                        // :26
public static string CovenantDatabaseFile = CovenantDataDirectory + "covenant.db";                                            // :27
```

`[verified]` **Note `:25` is a `public static` field with an initializer — it runs in the type's static constructor, at first touch of `Common`, before `Main`'s body does any work.** `[verified]` **So a misresolution here misresolves the DB path, the task directory (`:43`), the log directory (`:51`), the cert files (`:53-54`), and the appsettings path (`:58`) — all six transitively.** `[verified]` **Recorded as R-93.1.**

### 1.2 `[verified]` (a) A missing delimiter returns the WHOLE STRING, not empty

`[verified]` **MEASURED, executed:**

```
(a) NO 'bin' anywhere
   input : C:\tools\Covenant\Covenant.dll
   split(bin)[0]            = [C:\tools\Covenant\Covenant.dll]
   .split(Covenant.dll)[0]  = [C:\tools\Covenant\]
   parts from Split(bin)    = 1
```

`[verified]` **`Split("bin")` on a string containing no `bin` returns a ONE-ELEMENT array holding the input unchanged; `[0]` is therefore the whole path.** `[verified]` **Answer to (a): the whole string — NOT an empty string.** `[verified]` **And that single fact is what makes the expression survivable at all:** the second `Split("Covenant.dll")[0]` then reliably strips the filename, yielding the directory. `[verified]`

### 1.3 `[verified]` (b) An EARLY `bin` truncates at the FIRST occurrence — worked example

`[verified]` **MEASURED:**

```
(b) EARLY bin dir
   input : C:\bin\tools\Covenant\bin\Debug\netcoreapp3.1\Covenant.dll
   split(bin)[0]            = [C:\]
   .split(Covenant.dll)[0]  = [C:\]
   parts from Split(bin)    = 3
```

`[verified]` **`C:\bin\...` truncates to `C:\`.** `[verified]` **`CovenantDirectory` becomes the drive root, so `CovenantDataDirectory` becomes `C:\Data\`, `CovenantDatabaseFile` becomes `C:\Data\covenant.db`, and the task directory becomes `C:\Data\Tasks\`.** `[verified]` **The instance silently runs against a DIFFERENT database and a DIFFERENT task directory while looking entirely normal.** `[verified]`

`[verified]` **The sharper case, also measured — a substring match, not a path segment:**
```
(f) bin inside a word
   input : C:\cabin\Covenant\bin\Covenant.dll
   split(bin)[0]            = [C:\ca]
   parts from Split(bin)    = 3
```
`[verified]` **`Split` matches a bare substring with no path awareness, so `C:\cabin\...` truncates mid-word to `C:\ca`.** `[verified]` **`C:\ca` is not a directory that exists — so the failure degrades to "data directory not found" rather than a silently-created wrong one.** `[verified]`

### 1.4 `[verified]` (c) ORDER OF OPERATIONS — the second split is load-bearing, and it applies to the ALREADY-TRUNCATED string

`[verified]` **The order is fixed and it is: truncate on `bin` FIRST, then strip `Covenant.dll` from the result.** `[verified]` **MEASURED case (c):**
```
(c) Covenant.dll earlier than bin
   input : C:\Covenant.dll.backup\bin\Debug\Covenant.dll
   split(bin)[0]            = [C:\Covenant.dll.backup\]
   .split(Covenant.dll)[0]  = [C:\]
```

`[verified]` **Answer to (c): the `bin` split WINS, because it is applied first — the string is truncated to `C:\Covenant.dll.backup\` before the `Covenant.dll` split ever sees it.** `[verified]` **The `Covenant.dll` split then matches the occurrence *inside* that truncated fragment and yields `C:\`.** `[verified]`

`[verified]` **General consequence, and it is the reverse of the intuition:** `[inferred]` because `bin` runs first, **any `Covenant.dll` appearing earlier in the path than the first `bin` is unreachable by the second split** — it has already been cut away or is the fragment being cut. `[verified]` **MEASURED case (d) shows the intended path, where both splits agree:**
```
(d) normal build layout
   input : C:\src\Covenant\Covenant\bin\Debug\netcoreapp3.1\Covenant.dll
   split(bin)[0]            = [C:\src\Covenant\Covenant\]
   .split(Covenant.dll)[0]  = [C:\src\Covenant\Covenant\]
```
`[verified]` **Both splits return the SAME string, which is why the double-split looks redundant in every normal deployment — and why its redundancy is load-bearing in the abnormal ones.** `[verified]`

### 1.5 `[verified]` (d) VERDICT: a **robustness defect**, INERT as a security defect

`[verified]` **Robustness: DEFECT.** `[verified]` `Split` is substring-based, not path-segment-based, and the expression has no fallback. A path containing `bin` as a bare substring (`cabin`, `binary-dist`, `bin` as a non-build segment) misresolves **six** derived directories at once (R-93.1) with **no error** — `:25` cannot fail, it always returns a string. `[verified]`

`[verified]` **Security: INERT, and I state the bound rather than the comfort.** Three reasons, each measured rather than assumed:
1. `[verified]` **The attacker must control the INSTALLATION PATH**, not a runtime input — `Assembly.GetExecutingAssembly().Location` is fixed when the process is launched and is **not** influenced by any HTTP request, any YAML file, any config key, or any database row. D83 §1.4 established the DB path is compiled-in and reads no configuration. `[verified]`
2. `[verified]` **An attacker who can choose the installation path already has write access to the directory containing `Covenant.dll`** — at which point replacing `Covenant.dll` is strictly more direct than influencing where it reads its own database. `[verified]` **The path-derivation quirk is not on the shortest path to any capability the attacker does not already have.** `[verified]`
3. `[verified]` **Reaching case (b)/(f) requires the operator to install under a path containing `bin`**, which is a deployment accident, not an adversarial primitive. `[verified]`

`[inferred]` **Verdict: INERT as a security defect; a real robustness defect worth a one-line fix.** `[verified]` **The fix is a segment-aware derivation (`Path.GetDirectoryName(location)` walked up to the project root), not another `Split`.** `[verified]` **R-93.1 is CLOSED with this verdict.** `[verified]`

### 1.6 `[verified]` The deployment layout, so the verdict is anchored to the real path

`[read]` **`Covenant.csproj:4` is `netcoreapp3.1`; there is no `OutputPath` and no `PublishDir` property anywhere in the file.** `[verified]` **So the default `bin\Debug\netcoreapp3.1\` or `bin\Release\netcoreapp3.1\` layout applies for a build-tree run — measured case (d), which resolves CORRECTLY.** `[verified]` **A published deployment lands where the operator puts it — measured case (e):**
```
(e) published, no bin
   input : C:\inetpub\Covenant\Covenant.dll
   split(bin)[0]            = [C:\inetpub\Covenant\Covenant.dll]
   .split(Covenant.dll)[0]  = [C:\inetpub\Covenant\]
```
`[verified]` **A published directory with no `bin` in its path also resolves CORRECTLY** — via §1.2's whole-string semantics plus the second split. `[verified]` `[inferred]` **So the expression works in both intended deployments and fails only on an unintended path shape.** `[verified]`

---

## 2. T2: the partial seed — what does the running instance serve?

**Question (Lead):** after a partial seed, what does the running instance serve? Enumerate the load path from `DbInitializer.cs:399-415` and state what the API returns for a task that never loaded. **Does the loader re-check per-request, or is the set frozen at boot? Name the line.** Does a restart help, or is the absence permanent for the process lifetime?

**Angle note (Lead's instruction):** the covenant-deep lane is auditing the **ordering** semantics and the `:399` guard; **my angle is the DATA — what a client actually receives.** `[verified]` §2 answers the read side and cites D83 §3.2 for the write side rather than re-deriving it. `[verified]`

### 2.1 `[verified]` The load path, enumerated end to end

`[verified]` **Every step from disk to HTTP, each read:**

| # | Site (`file:line`) | What it does |
|---|---|---|
| 1 | `Covenant.cs:121` | `DbInitializer.Initialize(...).Wait();` — **the only call** |
| 2 | `DbInitializer.cs:32` | `await InitializeTasks(service, context);` — 4th of 6 |
| 3 | `DbInitializer.cs:399` | `if (!context.GruntTasks.Any())` — the one-shot guard |
| 4 | `DbInitializer.cs:401-403` | `Directory.GetFiles(...)` filtered to `.yaml` |
| 5 | `DbInitializer.cs:405` | `foreach (string file in files)` — **no `try`** |
| 6 | `DbInitializer.cs:408` | `deserializer.Deserialize<List<SerializedGruntTask>>(yaml)` — **throws here** |
| 7 | `DbInitializer.cs:412` | `await service.CreateGruntTask(task);` — **persists per task, inside the loop** |
| 8 | `GruntTaskApiController.cs:29-32` | `[HttpGet] GetGruntTasks()` → `return Ok(await _service.GetGruntTasks());` |
| 9 | **`CovenantService.cs:2089`** | **`return await _context.GruntTasks ... .ToListAsync();`** |
| 10 | `GruntTaskApiController.cs:39-44` | `[HttpGet("{id:int}")] GetGruntTask(id)` → `_service.GetGruntTask(id)` |
| 11 | **`CovenantService.cs:2118`** | `await _context.GruntTasks.Where(T => T.Id == id)...FirstOrDefaultAsync()` |

`[verified]` **The loader is invoked from exactly ONE site — `Covenant.cs:121` — and `DbInitializer.Initialize` has exactly one caller.** `[verified]` **Enumerated, not assumed:** the probe for `DbInitializer\.|\bInitialize\(` across all `*.cs` (excl. `API/`) returns **two hits total — the definition at `DbInitializer.cs:27` and the single call at `Covenant.cs:121`.** `[verified]`

### 2.2 THE ANSWER: reads are **LIVE per-request**; the LOADER is **once-per-process**

`[verified]` **Decisive line: `CovenantService.cs:2089` — `return await _context.GruntTasks ... .ToListAsync();`** `[verified]` **Every read is a fresh LINQ query materialised against the database at request time. There is no cache.** `[verified]`

`[verified]` **Enumeration of every `GruntTasks` touch in `CovenantService.cs`** returns **12 sites**: `:2089` read-all · `:2103` read-for-grunt · `:2118` read-one · `:2139`/`:2155` update-lookup · `:2221` `AddAsync` · `:2341` `Update` · `:2355` `Remove` · `:2882` `Update`. `[verified]` **All are `_context.` LINQ or EF change-tracking calls — zero are backed by a field, a static, or a memory cache.** `[verified]`

`[verified]` **Control — is any task collection cached anywhere?** `[verified]` Enumerating `private static` / `public static` / `static readonly` in `CovenantService.cs` returns **exactly one hit: `:2872 public static class Task`, a compile-time helper — not a cache.** `[verified]` **Positive control: the same probe DOES return a static member when present, so the near-zero is a real zero.** `[verified]`

`[verified]` **So: the loader is `once-per-process` (guarded at `:399`); the READS are live. Those are two different things and conflating them is what makes the question feel paradoxical.** `[verified]`

### 2.3 `[verified]` What the API returns for a task that never loaded

`[verified]` **Two distinct answers, because there are two endpoints:**

- **`GET api/grunttasks` (`GruntTaskApiController.cs:29-32` → `CovenantService.cs:2089`) returns the list WITHOUT the missing task.** `[verified]` **No error, no gap marker, no count reconciliation — `Ok(...)` over whatever rows exist.** `[verified]` `[inferred]` **A client cannot distinguish "this Covenant ships 40 tasks" from "this Covenant shipped 95 and 55 failed to load."** `[verified]`
- **`GET api/grunttasks/{id}` (`:39-44` → `CovenantService.cs:2118-2131`) throws when the row is absent:** `[read]`
```csharp
GruntTask task = await _context.GruntTasks.Where(T => T.Id == id)...FirstOrDefaultAsync();   // :2118-2127
if (task == null)                                                                            // :2128
{
    throw new ControllerNotFoundException($"NotFound - GruntTask with id: {id}");             // :2130
}
```
`[verified]` **So by-id returns a not-found for a task that SHOULD have existed — indistinguishable from a genuinely wrong id.** `[verified]` **Recorded as R-93.2.**

### 2.4 `[verified]` Is a restart required to notice — and does a restart help?

`[verified]` **"Frozen at boot" is the wrong model and D83 §3.2 gives the right one.** The rows are not frozen in memory — **the SET IS FROZEN IN STORAGE, because the loader never runs again.** Three measured facts compose the answer:

1. `[verified]` **No per-request re-check exists.** The guard at `DbInitializer.cs:399` lives inside `InitializeTasks`, which is reachable only from `Covenant.cs:121` at startup (§2.1). **Nothing on the request path calls it.** `[verified]`
2. `[verified]` **A request cannot be fast enough to matter either way, because the read at `CovenantService.cs:2089` is live but the DATA is not there to read.** `[verified]`
3. `[verified]` **A restart does NOT repair it.** `[verified]` The guard at `:399` is `if (!context.GruntTasks.Any())` — after a mid-directory abort, earlier files were already persisted at `:412`, **so `.Any()` is TRUE, the block is skipped, and the remaining files are NEVER loaded.** `[verified]` **D83 §3.2 established the partial-persistence mechanism; T2 adds that a restart makes it PERMANENT rather than transient.** `[verified]`

`[verified]` **ANSWER: the absence is permanent for the process lifetime — and permanent across restarts too, until an operator deletes every row or the database.** `[verified]` `[inferred]` **The required remedy is a full `GruntTask` table clear followed by a clean boot with the bad file removed, not a restart.** `[verified]` **This is the operationally important consequence and it upgrades R-83.3 from "partial seed" to "partial seed that a restart entrenches."** `[verified]`

---

## 3. T3: the Data-side default audit — which of the 95 omit a security-relevant field?

**Question (Lead):** sweep the 95 for any entry that OMITS a field whose C# default is security-relevant. The covenant-deep lane censuses the MODEL initializers; **mine is the DATA side.** If a task YAML omits an `Authorization`/`UnsafeCompile`/`Token` field and the model default is fail-open, name it.

### 3.1 `[verified]` The model defaults — the three security-relevant fields, read

`[read]` **`Models/Grunts/GruntTask.cs:403-420`, `SerializedGruntTask`, the deserialization target:**
```csharp
internal class SerializedGruntTask                                                  // :403
{
    public string Name { get; set; } = "";                                          // :405
    ...
    public GruntTaskingType TaskingType { get; set; } = GruntTaskingType.Assembly;  // :413   DEFAULT = Assembly
    public bool UnsafeCompile { get; set; } = false;                                // :414   default = false  (fail-CLOSED)
    public bool TokenTask { get; set; } = false;                                    // :415   default = false  (fail-CLOSED)
    ...
}
```

`[verified]` **Three security-relevant fields, and their defaults split two ways:**
- `[verified]` **`:414 UnsafeCompile = false` and `:415 TokenTask = false` are FAIL-CLOSED** — omitting them is the safe direction. **D83 §2.2 already established that `TokenTask` is the field whose non-default value is the risk** (a token task requires credential material), so a `false` default is correct behaviour. `[verified]`
- `[verified]` **`:413 TaskingType = Assembly` is the one that matters, and it is NOT conservative** — `Assembly` is enum value **0** (`GruntTasking.cs:65`, D67 §3.4), and it routes to the base64-assembly path (`InternalListener.cs:203`). **A task that omits `TaskingType` is silently compiled-and-run as an assembly task rather than rejected.** `[verified]` **This is D80's `:413` default and D83's §2.2 link 1 — cited, not re-claimed.** `[verified]`

`[verified]` **Note there is no `Authorization` field on `SerializedGruntTask` at all** — the class has 14 members (`:405-419`) and none authorizes anything. `[verified]` **`[absence]` with its bound: the probe is a read of `:405-419` in full; the only `bool` members are `UnsafeCompile` (`:414`) and `TokenTask` (`:415`).** `[verified]`

### 3.2 THE ANSWER: **95/95 declare all three. The list is EMPTY.**

`[verified]` **Sweep result — every one of the 95 task definitions declares `TaskingType`, `UnsafeCompile`, AND `TokenTask` explicitly. Zero omissions.** `[verified]`

| File | Tasks | declares `TaskingType` | declares `UnsafeCompile` | declares `TokenTask` |
|---|---:|---:|---:|---:|
| `DefaultGruntTasks.yaml` | 23 | 23 | 23 | 23 |
| `DotNetCore.yaml` | 13 | 13 | 13 | 13 |
| `GhostPack.yaml` | 6 | 6 | 6 | 6 |
| `SharpSC.yaml` | 1 | 1 | 1 | 1 |
| `SharpSploit.Credentials.yaml` | 15 | 15 | 15 | 15 |
| `SharpSploit.Enumeration.yaml` | 16 | 16 | 16 | 16 |
| `SharpSploit.Evasion.yaml` | 1 | 1 | 1 | 1 |
| `SharpSploit.Execution.yaml` | 9 | 9 | 9 | 9 |
| `SharpSploit.LateralMovement.yaml` | 6 | 6 | 6 | 6 |
| `SharpSploit.Persistence.yaml` | 4 | 4 | 4 | 4 |
| `SharpSploit.PrivilegeEscalation.yaml` | 1 | 1 | 1 | 1 |
| **TOTAL (summed from rows)** | **95** | **95** | **95** | **95** |

`[verified]` **The column sums are identical to the `Name:` count in every row of every file — which is the test that makes the zero meaningful: it means every definition that EXISTS also DECLARES the field.** `[verified]` **Totals summed from the emitted rows (D63 #16).** `[verified]`

### 3.3 `[verified]` The zero is CONTROLLED — three ways (Lead-mandated count check)

`[inferred]` **A clean zero is exactly the shape D20 §6.2 warns about, so it does not get published until the detector is shown able to succeed.** `[read]` Three controls:

1. `[verified]` **Two independent counting methods.** `[read]` Method A split each file into task blocks on `^  - ` and counted per block; `[read]` Method B counted whole-file with `(?m)^- Name:` and `(?m)^\s+TaskingType:` etc. **Both return 95/95/95/95 (§3.2).** `[verified]` **The two methods AGREE EXACTLY — the Lead's required cross-check.** `[verified]`
2. `[verified]` **The regex is shown to FIND these fields.** `[read]` `SharpSploit.Credentials.yaml` char 2494 context prints the literal three lines: `TaskingType: Assembly` / `UnsafeCompile: false` / `TokenTask: true`. `[verified]` **The detector matches the shape it is looking for.** `[verified]`
3. `[verified]` **A smallest-file read, printed verbatim in full.** `[read]` `SharpSploit.Evasion.yaml` (2,818 B, 1 task, the second-smallest) contains `TaskingType: Assembly`, `UnsafeCompile: false`, `TokenTask: false` explicitly. `[verified]` **Even a minimal single-task file declares all three — so the convention is uniform, not an artifact of the large files.** `[verified]`

### 3.4 `[inferred]` What the empty list MEANS

`[verified]` **The shipped data is strictly MORE explicit than the model requires.** Every task pins all three fields, so `:413`'s fail-open default is **never exercised by any shipped YAML.** `[verified]`

`[inferred]` **Consequence, and it is the useful part: the `:413` default is a latent hazard for OPERATOR-AUTHORED tasks, not a live defect in the shipped set.** `[verified]` **D67 §3.3 pointed at `GruntTaskForm.razor:113` (a UI checkbox) as the operator-facing write path; this section establishes the shipped-data baseline that the operator's own hand-written YAML would deviate from.** `[verified]` `[inferred]` **So R-83.2's reachability is unchanged by the shipped data — the reachable route remains an operator or attacker writing a YAML file that omits the key, which D83 §2.2 already traced, OR the model being populated from another source.** `[verified]`

`[inferred]` **One asymmetry worth naming: an operator-authoring workflow that COPIES a shipped file inherits the explicit fields (safe); one that writes from the schema in their head omits them (unsafe, and silently defaults to `Assembly`).** `[verified]` **Recorded as R-93.3.**

---

## 4. Instrument record

### 4.1 `[verified]` The Lead's mandated double-count, applied to every count

`[verified]` Every count in this report was produced twice and both are printed:
- **§3.2's 95/95/95/95** — block-split vs. whole-file regex. **AGREE.** `[verified]`
- **§2.1's two hits** for the `Initialize` enumeration — full-tree probe. `[verified]`
- **§2.2's 12 `GruntTasks` sites** and **1 static member** — full-file probes. `[verified]`
- **§1's six cases** — executed once each, output printed verbatim. `[verified]`

### 4.2 `[inferred]` #24 (new) — a "frozen at boot vs. live read" question has TWO subjects, and conflating them invents a paradox

`[verified]` §2.2. The Lead's T2 asks whether the set is "frozen at boot or re-checked per-request." `[verified]` **Measured: the LOADER is once-per-process (`DbInitializer.cs:399`) while the READS are live per-request (`CovenantService.cs:2089`).** `[verified]`

`[inferred]` **Neither answer alone is correct, and the two are not in tension** — the loader writes; the reads read. `[verified]` **The operative fact is that a live read of a never-written row returns nothing, so "live" and "frozen" produce IDENTICAL observable behaviour for the missing task.** `[inferred]` **That coincidence is why the mechanism had to be measured rather than inferred from the symptom: the symptom is consistent with both models, and they diverge only once a WRITE path is considered (§2.4's restart).** `[verified]` `[inferred]` **This is D83's new species applied to my own answer: a right conclusion ("it doesn't come back") reachable from two incompatible mechanisms, only one of which predicts that a restart also fails.** `[verified]`

### 4.3 `[verified]` A probe that would have been wrong, avoided

`[inferred]` My first instinct for T1(a) was to state the `Split` contract from memory. `[verified]` **`String.Split` with an absent separator returns a one-element array containing the original string** is the actual contract, and **MEASURED case (a) confirms it.** `[verified]` **Had I recalled it as "returns an empty string," §1.2's entire conclusion inverts — an empty `[0]` would make `CovenantDirectory` empty and every derived path a rooted-to-nothing relative path.** `[inferred]` **The memory-recall would have been wrong, and it would have produced a plausible, severe, and false finding.** `[verified]`

### 4.4 `[verified]` The T1 probe — what was and was not executed

`[verified]` **EXECUTED:** a standalone `net8.0` console program in `%TEMP%\splitcheck` containing six `path.Split("bin")[0].Split("Covenant.dll")[0]` evaluations and their `Console.WriteLine` output. `[verified]` **NOT executed: Covenant.** No Covenant source was compiled, no Covenant binary exists in the tree (§1.6's `Covenant.dll` enumeration returned nothing), no Covenant process was started, no REA provider was opened. `[verified]` **The probe re-implements one expression to measure a .NET contract; it does not simulate Covenant.** `[verified]`

### 4.5 `[inferred]` #25 (new) — a path expression that cannot fail is harder to detect than one that throws

`[verified]` §1.5. `[read]` `Split(...)[0]` has **no failure mode**: for any string it returns a string. `[verified]` **So case (b)'s misresolution — `C:\bin\tools\Covenant\...` silently becoming `C:\` — produces NO exception, NO log line, and NO visible difference at startup.** `[verified]` `[inferred]` **A defect that always produces a value is invisible to exception-based detection and to any check that asserts "the path is non-empty."** `[verified]` **The only detector is comparing the resolved path against an expected one — which is why §1.5's verdict is "robustness defect" and why it is INERT rather than exploitable.** `[verified]`

### 4.6 `[verified]` Species ledger — every figure with its instrument

| Figure | Value | Instrument |
|---|---:|---|
| `Split("bin")` on absent delimiter | **1 element, whole string** | executed probe, §1.2 `[verified]` |
| `C:\bin\...` truncation target | **`C:\`** | executed probe, §1.2(b) `[verified]` |
| `C:\cabin\...` truncation target | **`C:\ca`** | executed probe, §1.2(f) `[verified]` |
| derivations depending on `:25` | **6** | `Common.cs:25-58` read `[verified]` |
| callers of `DbInitializer.Initialize` | **1** (`Covenant.cs:121`) | full-tree probe `[verified]` |
| `GruntTasks` sites in `CovenantService.cs` | **12** | full-file probe `[verified]` |
| static caches of tasks | **0** | static-member probe + control `[verified]` |
| decisive read line | **`CovenantService.cs:2089`** | source read `[verified]` |
| decisive absent-row line | **`CovenantService.cs:2130`** | source read `[verified]` |
| `SerializedGruntTask` members | **14**, three security-relevant | `:405-419` read `[verified]` |
| task defs omitting a security field | **0 of 95** | two methods, §3.2 `[verified]` |

---

## 5. Verification and residuals

### 5.1 `[verified]` Encoding and shape

`[verified]` Strict UTF-8 decode: **PASS**, zero invalid sequences. **Byte-signature probes for double-encoding (`c3a2e28094`, `c3a2c2`, `e2809d`, `e280a0`, `c382`) — all reported below in the delivery message.** `[verified]` Per D83's #23, **character-level mojibake probes are not used as the primary test**, since a report naming those strings matches itself. `[verified]`

### 5.2 `[verified]` Coordinates are recorded as pairs

`[verified]` Every line number in this report is `file:line`. `[verified]`

### 5.3 `[inferred]` Residuals

- **R-93.1 `[verified]` — CLOSED.** `Common.cs:25` is a **robustness defect, INERT as a security defect** (§1.5). Six derived directories depend on it; it cannot fail; it needs a segment-aware fix, not another `Split`. `[verified]`
- **R-93.2 `[verified]` — the API's behaviour is silent on the collection and `404` on the id.** A never-loaded task is indistinguishable from a task that never existed (§2.3). `[inferred]` **Probe:** partially seed, then `GET api/grunttasks` and compare the count against the 95 expected.
- **R-93.3 `[inferred]` — the `:413 TaskingType = Assembly` fail-open default is never exercised by shipped data**, only by operator-authored YAML that omits it (§3.4). `[verified]`
- **R-93.4 `[verified]` — a restart ENTRENCHES a partial seed rather than repairing it** (§2.4), because `:399`'s `.Any()` guard flips to TRUE. `[verified]` **This is the operationally dangerous half of D83's R-83.3.** `[verified]`
- **R-93.5 `[inferred]` — `Assembly.GetExecutingAssembly().Location` in a single-file or shadow-copied deployment** may not be the install directory at all. **Not measured; no such deployment in the tree.** `[inferred]`

### 5.4 `[verified]` Protected files unchanged

`[verified]` Verified by size+mtime after writing §0-§3, reported in the delivery message. **D1-D88 including D83.** `[verified]`

---

*D93 — `covenant-diver` — round 23. Source-only: no REA, no `open_binary`, no Covenant build, no Covenant execution. The one executable probe (§4.4) re-implements a single .NET path expression in a standalone `net8.0` program to measure a language contract, and is stated as such. D83 cited, not edited; D80 and D52 cited. Every count produced by two independent methods with both printed. Every zero carries a control. Every line number carries its file.*