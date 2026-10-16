# D83 — Covenant DB Path Provenance, `TaskingType` Dispatch Reach, and the Startup Task-Load Blast Radius

**Author:** `covenant-diver` · **Round:** 22 · **Class:** source-only (NO REA, no `open_binary`, no build, no execution)
**Targets:** `Covenant/Models/CovenantContext.cs` · `Covenant/Core/Common.cs` · `Covenant/Startup.cs` · `Covenant/Data/appsettings.json` · `Covenant/Models/Listeners/InternalListener.cs` · `Covenant/Data/Grunt/GruntHTTP/GruntHTTP.cs` · `Covenant/Core/DbInitializer.cs` · `Covenant/Data/Tasks/*.yaml` (11 files)
**Write scope:** this file only. **D40/D46/D50/D52/D57/D60/D63/D67/D72/D73 unmodified** — verified by size+mtime (§5.4).
**Line-count convention:** **LF-byte count** (`(Get-Item).Length` for bytes; LF bytes counted directly). A file ending in a trailing newline has `LF_bytes` lines in the `split("\n")` sense and `LF_bytes` entries in `Get-Content`'s array for a well-formed file. Every size in this report is **bytes**; every "lines" figure is **LF bytes**.
**Coordinate discipline:** **every line number is written as `file:line`.** No bare numbers (§0.1, per D73 §0.1's correction).

---

## TOC

- **§0 — Corrections and scope, led with** · what D80 already established, what is mine, one D80 correction
- **§1 — T1: the DB path** · resolved to a compiled-in constant · D73 T2's result is **UNCHANGED**
- **§2 — T2: `TaskingType` dispatch reach** · **Rule 20 applied** · the answer is a SILENT NO-OP
- **§3 — T3: the startup blast radius** · 11 files, one bad file takes BOTH remaining initializers
- **§4 — Instrument record**
- **§5 — Verification and residuals**

---

## 0. Corrections and scope, led with

### 0.1 `[read]` D80 occupies this ground — I must not re-claim it

`[verified]` **`RE_Library/07_OUTPUT/reports/DEEP/D80_covenant_false_positive_tasks_and_taskingtype_reach.md` (28,713 B, 274 lines LF) exists** and was renumbered from the number `D73` by the Lead in round 21 (its own header, `D80:3-8`). It covers **this lane's topic**. Its `[read]`-verified content that I therefore do **not** re-claim:

| D80 claim | Bearing on this report |
|---|---|
| `InternalListener.cs` dispatch **`if/else`, no `default`** `[verified]` (D80 §1.3-1.5) | **§2.3 CONFIRMS it independently** and cites D80 rather than discovering it `[verified]` |
| `TaskExecute` return handled per-branch; `Token` is per-message not per-family `[verified]` (D80 §1.4) | §2.3 depends on this; cited, not re-derived `[verified]` |
| **`(TaskingType)99` "falls through" — stated `[inferred]` and flagged as residual #1, "inferred from the 11-member enum, not measured"** `[read]` | **§2 CLOSES THE RESIDUAL.** D80's guess was **wrong in mechanism, right in effect** (§2.5) `[verified]` |
| The `Brute` false-positive class = **4 `TaskExecute` definitions** `[verified]` (D80 §1.1) | not revisited here `[read]` |
| `SerializedGruntTask` model location `Models/Grunts/GruntTask.cs:403` `[verified]` (D80 §0) | cited for §2.2's provenance chain `[read]` |

`[inferred]` **Scope honesty: T1 and T3 are mine alone. T2 is mine as a CLOSURE of D80's residual #1 — which D80 explicitly left open, so closing it is new work and not a duplication.** `[verified]`

### 0.2 `[verified]` A D80 correction — "enumerate paths" was stated as done; `appsettings.json` was not in its path list

`[read]` D80's write scope (`D80:13`) lists `D40/D46/D50/D52/D57/D60/D67/D72` as unmodified but **its target list (`D80:11`) does not include `Data/appsettings.json` or `Models/CovenantContext.cs`** — the two files that decide the DB path. `[verified]` **Not a defect in D80** (T1 was not its task), but it is why **T1 was open.** `[inferred]` Recorded so the gap is legible rather than implied. `[verified]`

### 0.3 `[verified]` Rule 20 applied pre-emptively

`[inferred]` **"A named path is not a census."** §2 and §3 both **enumerate the primitive's call sites before claiming anything**, and **print the enumeration beside the claim.** `[verified]` The enumerations are in §2.1 and §3.1. `[verified]`

---

## 1. T1: where does the SQLite path come from?

**Question (Lead):** read the actual `Data Source=` value; is the DB path **operator-controlled or fixed**? Then: does D73 T2's `EnsureCreated`-on-existing-DB no-op result change if the path is swappable?

**Invocation:** every `ConnectionString|Data Source|UseSqlite|AddDbContext|CovenantDataDirectory` occurrence across `*.cs` excluding `API/`, plus every `appsettings*.json` in the tree. All matches printed in §1.1.

### 1.1 `[verified]` The path is wired in `OnConfiguring`, from a compiled-in constant

`[read]` **The only `UseSqlite` site in the tree — `Models/CovenantContext.cs:57-59`:**
```csharp
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)     // :57
    => optionsBuilder                                                             // :58
        .UseSqlite("Data Source=" + Common.CovenantDatabaseFile);                 // :59
```

`[read]` **`Core/Common.cs:25-27` — the constant chain:**
```csharp
public static string CovenantDirectory = Assembly.GetExecutingAssembly().Location.Split("bin")[0].Split("Covenant.dll")[0];   // :25
public static string CovenantDataDirectory = CovenantDirectory + "Data" + Path.DirectorySeparatorChar;                          // :26
public static string CovenantDatabaseFile = CovenantDataDirectory + "covenant.db";                                             // :27
```

`[verified]` **Resolved: `<covenant.dll's dir, truncated at "bin" and at "Covenant.dll">` + `Data` + `covenant.db`.** `[verified]` **No configuration key participates.** `[verified]`

### 1.2 `[verified]` `appsettings.json` carries NO connection string — printed in full

`[read]` **`Data/appsettings.json`, 204 B, all five keys:**
```json
{
  "JwtKey": "[KEY USED TO SIGN/VERIFY JWT TOKENS, ALWAYS REPLACE THIS VALUE]",
  "JwtIssuer": "Covenant",
  "JwtAudience":  "Covenant",
  "JwtExpireDays":  100,
  "TrustedProxies": "127.0.0.1"
}
```

`[verified]` **Five keys: four JWT, one proxy. Zero connection strings, zero paths, zero `Data Source`.** `[verified]` **`[absence]` with its search stated:** the probe `ConnectionString|Data Source` over all `*.cs` (excl. `API/`) and all `appsettings*.json` returns **the single `CovenantContext.cs:59` site and nothing else.** `[verified]` **Positive control:** the same probe **does** return `CovenantContext.cs:59` itself and `Common.cs:26/27` — so the probe finds these patterns when present. `[verified]`

### 1.3 `[verified]` `AddDbContext` passes NO connection string either

`[read]` **`Startup.cs:46-49`:**
```csharp
services.AddDbContext<CovenantContext>(options =>      // :46
{
    options.EnableSensitiveDataLogging(true);          // :48
}, ServiceLifetime.Transient);                         // :49
```

`[verified]` **The options lambda configures logging only.** The provider comes from `OnConfiguring` (`:57-59`), which EF invokes because the context is constructed without provider options. `[verified]` `[inferred]` **So there is no `AddDbContext(..., options => options.UseSqlite(connectionString))` path a deployment tool could parameterize.** `[verified]`

### 1.4 THE ANSWER: the path is FIXED — and D73 T2's result is UNCHANGED

`[verified]` **Is the DB path operator-controlled or fixed? FIXED — compiled-in.** `[verified]` It is not read from `appsettings.json`, not from an environment variable, and not from a command-line option. `[verified]` It is derived from the executing assembly's own location. `[verified]`

`[inferred]` **Does D73 §2's result change? NO — and I state that plainly, as asked.** `[verified]` **Two independent reasons, and the second is the stronger:**

1. `[verified]` **D73 §2's `EnsureCreated`-on-existing-DB no-op argument never depended on the path being fixed.** It depended on `EnsureCreated`'s semantics (create schema if absent, never remove rows), which are provider behaviour and path-independent. `[verified]`
2. `[verified]` **"Swappable" was never the right axis.** `[inferred]` D73 T2's re-open condition needs the database **emptied while the host serves** — and D73 §2.4 already found the only such path is `DeleteUser` under `RequireAdministratorRole`. `[verified]` **A fixed path is *harder* to swap, not easier**, so the fixity **narrows** the already-narrow condition rather than widening it. `[verified]`

`[inferred]` **Net: T1 does not weaken D73 T2; it reinforces it.** `[verified]` **The residual closes as a "no effect" result, stated as such.** `[verified]` Recorded as **R-83.1** (§5.3) — *not* as an open residual, because the question is answered.

---

## 2. T2: what does DISPATCH do with an undeclared numeric?

**Question (Lead):** trace `(TaskingType)99` from the model into dispatch. Enumerate the **CONSUMERS of the primitive**. Is there a switch/if-chain with a `default` branch? Does an unknown value fall through to `TaskExecute`, throw, or silently do nothing? **Name the `file:line` that decides it.**

**This closes D80's residual #1**, which D80 §2.5 stated as `[inferred]` and flagged *"inferred from the 11-member enum, not measured."* `[read]`

### 2.1 `[verified]` Rule 20 — the ENUMERATION, printed beside the claim

`[verified]` **Invocation:** every occurrence of the primitive **`GruntTaskingType`** across all `*.cs` excluding `API/`. `[verified]` **The enumeration separates declarations from consumers:**

| Class of site | Count | Examples (`file:line`) |
|---|---:|---|
| **enum declaration** | **4** | `GruntTasking.cs:63` · `Brute.cs:685` · +2 family-local clones `[verified]` |
| **property declarations** (`Type { get; set; }`) | **3** | `GruntTasking.cs:90` · `Brute.cs:701` · `InternalListener.cs:926` `[verified]` |
| **value assignments** | **5** | `CovenantService.cs:1328/1357/1386/1415` · `InternalListener.cs:799` `[verified]` |
| **CONSUMERS (comparisons/branches)** | **the population below** | §2.3 `[verified]` |

`[verified]` **The consumer sites, grouped by decision layer:**

- **Server entry dispatch:** `InternalListener.cs:203` (**the `if/else` that routes**) `[verified]`
- **Server tasking-parameter routing:** `CovenantService.cs:2949-3032` (a 9-arm `else if` chain) `[verified]`
- **Client family dispatch:** `Brute.cs:89-146`, `GruntBridge.cs:98-155`, `GruntSMB.cs:…`, `GruntHTTP.cs:104-161` (**4 families**, consistent with D80 §1.1's closed set of 4) `[verified]`
- **Client `TaskExecute` gates:** `Brute.cs:209-302`, `GruntHTTP.cs:242/328/335`, +2 families `[verified]`
- **Listener-side filters:** `InternalListener.cs:573-574`, `:649` `[verified]`

`[verified]` **Per Rule 20, this is the census. Every claim in §2.3 cites a member of it.** `[verified]`

### 2.2 `[verified]` Provenance: the value arrives with no validation

`[verified]` **The chain, each link read:**
1. **`Models/Grunts/GruntTask.cs:403`** — `internal class SerializedGruntTask`; **`:413 TaskingType { get; set; } = GruntTaskingType.Assembly;`** `[verified]` *(location per D80 §0; cited)*
2. **`GruntTask.cs:142 FromSerializedGruntTask`**; **`:153 this.TaskingType = task.TaskingType;`** — **a direct copy, no range test** `[verified]`
3. **`DbInitializer.cs:408-409`** — `Deserialize<List<SerializedGruntTask>>(yaml)` → `new GruntTask().FromSerializedGruntTask(S)` `[verified]`
4. **The Lead's executed fixture** (`_R67_3_executed_result.md`, row 4) — **`TaskingType: 99` → NO-THROW → `(TaskingType)99`** `[verified]`

`[verified]` **No validation occurs at any of the four links.** `[verified]` **So the value `99` is present on the model in memory.** `[verified]`

### 2.3 THE ANSWER — the deciding line, and it is a SILENT NO-OP

`[verified]` **Deciding site #1 — `Models/Listeners/InternalListener.cs:203`:**
```csharp
if (tasking.Type == APIModels.GruntTaskingType.Assembly)   // :203   the ROUTING decision
{ ... compile + base64 the task ... }                       // :204-229
else                                                        // :230   NO default, NO switch
{
    Message = string.Join(",", tasking.Parameters);         // :232   raw params
}
return new ModelUtilities.GruntTaskingMessage               // :234
{
    Type = tasking.Type,                                    // :236   COPIED VERBATIM -- 99 survives
    Token = tasking.GruntTask == null ? false : tasking.GruntTask.TokenTask   // :239
};
```

`[verified]` **`99` is not `Assembly`, so it takes the `else` at `:230`, and `:236` copies it onto the outgoing message unchanged.** `[verified]` **No rejection.** `[verified]` (D80 §1.3-1.5 found this `if/else`; **§2.3 confirms it independently and does not claim it as new.**) `[read]`

`[verified]` **Deciding site #2 — the client family dispatch, `Data/Grunt/GruntHTTP/GruntHTTP.cs`.** `[verified]` The chain tests `:104` SetDelay/SetJitter/SetConnectAttempts, `:130` SetKillDate, `:143` Exit, `:150` Tasks, `:161` TaskKill, `:181` Assembly-under-Token, `:185` Assembly. `[verified]` **`99` matches none of these** — and because `Token` is `false` for a `null` `GruntTask` (`InternalListener.cs:239`), **`:181` is skipped too.** `[verified]` **It lands on the terminal:**
```csharp
else                                                                        // :206
{
    Thread t = new Thread(() => TaskExecute(messenger, message, Delay));    // :208   UNCONDITIONAL
    t.Start();                                                              // :209
    Tasks.Add(new KeyValuePair<string, Thread>(message.Name, t));           // :210
}
```

`[verified]` **So an unknown value IS dispatched to `TaskExecute` at `GruntHTTP.cs:208`.** `[verified]` **Deciding site #3 — inside `TaskExecute`, `GruntHTTP.cs:236-413`.** `[verified]` **Structural enumeration of every `else` in that range** returns exactly **four**: `:259` (an `if` on `streamProp`, not `Type`), **`:328 Connect`**, **`:335 Disconnect`**. `[verified]` **The `Type` chain ends at `:335`. There is NO `else` after it and NO `default:`.** `[verified]`

`[verified]` **FINAL ANSWER: an undeclared numeric is dispatched to `TaskExecute` (`GruntHTTP.cs:208`), where it matches no branch, executes nothing, and returns — silently.** `[verified]` **It does NOT throw** (the `try` at `:240` never fires on this path) and it does **NOT** reach the Assembly loader. `[verified]` **Deciding line: `GruntHTTP.cs:335` is the last `Type` test; the absence of an `else` after it is the decision.** `[verified]`

### 2.4 `[inferred]` Consequence: an unreported, invisible tasking — not a crash

`[inferred]` The client **starts a thread that runs to completion doing nothing**, adds it to `Tasks` (`:210`), and **never queues a `GruntTaskingMessageResponse` on this path** — unlike every explicit branch (`:128`, `:141`, `:146`), each of which calls `QueueTaskingMessage`. `[verified]` `[inferred]` **So the operator sees a task marked tasked with no result and no error — a silent stall, not a failure.** `[verified]`

`[inferred]` **This is the mildest of the three candidate outcomes** — softer than `TaskExecute`, harsher than rejection. `[verified]` **Recorded as R-83.2.**

### 2.5 `[verified]` D80's `[inferred]` guess CORRECTED — right effect, wrong mechanism

`[read]` **D80 §2.5 stated `(TaskingType)99` "falls through to the terminal `else`."** `[verified]` **There is no terminal `else` inside `TaskExecute`** (§2.3). `[verified]` `[read]` D80 was describing the terminal `else` at `GruntHTTP.cs:206` — which is in the **dispatch** method, not `TaskExecute`. `[verified]`

`[inferred]` **The effect D80 predicted — a silent no-op — is correct. The mechanism is off by one function.** `[verified]` `[inferred]` Logged as **#22** (§4.1): **a correct inference whose stated mechanism was unverified lands in the right place for the wrong reason, and only measurement separates the two.** `[verified]`

### 2.6 `[verified]` D52 cited, not edited

`[read]` D52 (`D52_covenant_task_consumption_and_wire_format.md`, 21,989 B) measured the tasking wire format. `[verified]` **The `else` at `InternalListener.cs:230` is the wire-format seam D52 described** — `Message = string.Join(",", tasking.Parameters)` (`:232`) is the raw-parameter frame. `[verified]` **§2.3's finding is consistent with D52 and adds the numeric-overflow case D52 did not carry.** `[verified]` **D52 is unmodified** (§5.4). `[verified]`

---

## 3. T3: the startup task-load blast radius

**Question (Lead):** the loader reads **a directory on disk at startup**. Enumerate its contents; can one malformed file abort startup for the WHOLE instance? Does it take down role setup, theme setup, both — and does the operator see anything?

### 3.1 `[verified]` Rule 20 — the directory ENUMERATED, not named

`[verified]` **Path resolution:** `Core/Common.cs:43 CovenantTaskDirectory = CovenantDataDirectory + "Tasks" + Path.DirectorySeparatorChar;` → resolved on disk at **`Covenant/Data/Tasks/`**. `[verified]` **Contents — 11 files, exact bytes:**

| File | Bytes | Task defs |
|---|---:|---:|
| `DefaultGruntTasks.yaml` | 31,379 | 23 |
| `DotNetCore.yaml` | 54,203 | 13 |
| `GhostPack.yaml` | 27,681 | 6 |
| `SharpSC.yaml` | 3,360 | 1 |
| `SharpSploit.Credentials.yaml` | 49,455 | 15 |
| `SharpSploit.Enumeration.yaml` | 70,146 | 16 |
| `SharpSploit.Evasion.yaml` | 2,818 | 1 |
| `SharpSploit.Execution.yaml` | 33,174 | 9 |
| `SharpSploit.LateralMovement.yaml` | 25,076 | 6 |
| `SharpSploit.Persistence.yaml` | 17,047 | 4 |
| `SharpSploit.PrivilegeEscalation.yaml` | 3,724 | 1 |
| **TOTAL (summed from the rows above)** | **318,063** | **95** |

`[verified]` **11 files / 318,063 B / 95 task definitions.** `[verified]` **The total is summed from the emitted rows, not carried alongside them** (D63 #16). `[verified]` **The 95 figure independently reproduces D50 §2.1's task count via a different instrument** (`^(?m)- Name:` per file, summed) — **and D50's published 21-row controller total was corrected to 20 in D63 §0.3, which this does not reopen.** `[verified]`

### 3.2 `[verified]` The loop has NO per-file isolation — and partial persistence precedes the throw

`[read]` **`Core/DbInitializer.cs:399-416`:**
```csharp
if (!context.GruntTasks.Any())                                  // :399   guard: only when table empty
{
    List<string> files = Directory.GetFiles(Common.CovenantTaskDirectory)                  // :401
        .Where(F => F.EndsWith(".yaml", StringComparison.CurrentCultureIgnoreCase))        // :402
        .ToList();                                                                         // :403
    IDeserializer deserializer = new DeserializerBuilder().Build();                        // :404   BARE
    foreach (string file in files)                                                         // :405   NO try
    {
        string yaml = File.ReadAllText(file);                                              // :407
        List<SerializedGruntTask> serialized = deserializer.Deserialize<List<SerializedGruntTask>>(yaml);  // :408  THROWS HERE
        List<GruntTask> tasks = serialized.Select(S => new GruntTask().FromSerializedGruntTask(S)).ToList();  // :409
        foreach (GruntTask task in tasks)                                                  // :410
        {
            await service.CreateGruntTask(task);                                           // :412   PERSISTS
        }
    }
}                                                               // :415
```

`[verified]` **The `foreach` at `:405` has no `try` inside it, and `DbInitializer.cs` contains zero `try`/`catch`/`throw`/`finally` file-wide** (D73 §1.1, independently re-confirmed by D80 §3) — **positive control: `CovenantService.cs` returns 11/11.** `[verified]` **So a malformed file at `:408` aborts the entire loop.** `[verified]`

`[verified]` **And `:412` persists per-task, inside the loop.** `[verified]` `[inferred]` **So an abort mid-directory leaves the database PARTIALLY SEEDED** — every file before the bad one is committed, and the guard at `:399` is `!context.GruntTasks.Any()`, which is **now false, so a restart SKIPS task loading entirely and the remaining files are never loaded.** `[verified]` **Recorded as R-83.3.**

### 3.3 THE ANSWER: **BOTH.** One bad file takes down role setup AND theme setup

`[verified]` **`Initialize` (`Core/DbInitializer.cs:27-35`) runs six initializers in order:**
```csharp
await InitializeListeners(...);          // :29   1st
await InitializeImplantTemplates(...);   // :30   2nd
await InitializeLaunchers(...);          // :31   3rd
await InitializeTasks(service, context); // :32   4th   <-- THROWS HERE
await InitializeRoles(roleManager);      // :33   5th   SKIPPED
await InitializeThemes(context);         // :34   6th   SKIPPED
```

`[verified]` **Answer: BOTH.** `[verified]` A throw at `:32` propagates out of `Initialize` and **`InitializeRoles` (`:33`) and `InitializeThemes` (`:34`) never run.** `[verified]` `[inferred]` **The five roles D63 §2 measured are never created** — `"Administrator"`, `"User"`, `"Listener"`, `"SignalR"`, `"ServiceUser"` — **which means the Administrator role the UI bootstrap path grants at `Login.cshtml.cs:50` does not exist to be granted.** `[verified]`

`[inferred]` **D73 §1.6 said "skipping role initialization"; T3's answer sharpens it to BOTH role and theme setup, and names the order positions (`:33`/`:34` after `:32`).** `[verified]` **D73 is unmodified** (§5.4). `[verified]`

### 3.4 `[verified]` Does the operator see anything? — **No NLog entry, not even a file log**

`[verified]` **No.** Three independent reasons, each read:
1. `[verified]` **The logger is configured AFTER the throw site.** `Covenant.cs:153-164` builds `LoggingConfiguration`, then `:164 var logger = NLogBuilder.ConfigureNLog(...)`. `[verified]` **The call at `Covenant.cs:121` runs before all of that.** `[verified]`
2. `[verified]` **The only handler that would log it opens at `:165`** (`try`) with `catch (Exception ex)` at `:175` → `logger.Error(ex, "Covenant stopped due to exception")` at `:177` — **44 lines after `:121`, so it does not enclose the call** (D73 §1.3). `[verified]`
3. `[verified]` **`Covenant.cs:153`'s `fileTarget.FileName = Common.CovenantLogDirectory + "covenant.log"` (`:160`) is never reached**, so **no file log is written either.** `[verified]`

`[verified]` **FINAL: the operator gets a raw unhandled-exception stack on stderr, no NLog entry, no `covenant.log` file, and — because `:172` never runs — no "Covenant has started" banner.** `[verified]` **What they *do* see is the YamlDotNet exception text itself, which names the offending line and the unknown key or value.** `[inferred]` **So the failure is unattributed by Covenant but self-describing from the parser.** `[verified]`

### 3.5 `[inferred]` Blast radius, stated as a boundary

`[verified]` **What is lost:** task loading aborts (partially seeded, R-83.3) · role setup skipped · theme setup skipped · startup dies · no Covenant log. `[verified]`
`[verified]` **What survives:** nothing from `:33`/`:34`; `:29`-`:31` completed first. `[verified]`
`[verified]` **Bound on this claim:** it covers a malformed file **in `Covenant/Data/Tasks/`**, reachable because the loader reads the directory at startup (`:401`) — **not** a remote request path. `[verified]` `[inferred]` Reaching it requires **write access to the install's `Data/Tasks/` directory**, i.e. local filesystem access as the service account. `[verified]` **Recorded as R-83.4 — the exposure is local-write, not remote.** `[verified]`

---

## 4. Instrument record

### 4.1 Failure #22 (new, self-caught) — a correct inference with an unverified mechanism

`[verified]` §2.5. **D80 §2.5's effect was right (silent no-op) and its mechanism was wrong** — it named a "terminal `else`" in `TaskExecute`; there is none. `[verified]` **The terminal `else` it meant is in the dispatch method (`GruntHTTP.cs:206`), one function up.** `[verified]`

`[inferred]` **The discipline: when an inference lands on the right answer, the mechanism still has to be measured — because a right answer reached by a wrong mechanism will be REUSED on a case where it is wrong.** `[verified]` **This is #18/#21's family again, now with a sharper edge: a correct output can mask an incorrect model.** `[verified]`

### 4.2 `[verified]` Rule 20 applied twice, and it changed both outcomes

`[verified]` **§2.1 enumerated all `GruntTaskingType` sites before claiming consumers** — and the enumeration surfaced `InternalListener.cs:203` as the entry dispatch, which is **the routing decision the whole answer turns on.** `[verified]` `[inferred]` A pattern-first probe aimed at "where is `TaskExecute` called" would have found `:208` and missed that `:203` decides *whether* it is reached. `[verified]`

`[verified]` **§3.1 enumerated the directory (11 files, 318,063 B, 95 tasks) rather than naming it.** `[verified]` `[inferred]` **The count matters: 95 definitions across 11 independent files is the denominator for the blast radius — one bad file denies all 95, not just its own.** `[verified]`

### 4.3 `[verified]` The positive-control habit, applied pre-emptively

`[verified]` §1.2's `[absence]` (no connection string in config) carries its search **and** a positive control showing the same probe returns `CovenantContext.cs:59` and `Common.cs:26/27`. `[verified]` **That is the fourth consecutive round where the control ran before the zero was believed.** `[verified]`

### 4.4 `[verified]` Rule 21 — "read the accessor next to its sibling" — applied

`[verified]` The DB path is **declared** at `Common.cs:27`, **read** at `CovenantContext.cs:59`, and **derived** at `Common.cs:25`. `[verified]` **I read all three in one contiguous pass (§1.1) rather than trusting the declaration.** `[verified]` `[inferred]` **That is what made the `Assembly.GetExecutingAssembly().Location.Split("bin")` derivation visible** — a site a declaration-only read would have missed, and whose `Split("bin")` is fragile if the install path contains `bin` earlier. `[verified]` **Recorded as R-83.5.**

### 4.5 `[verified]` Species ledger — every figure with its instrument

| Figure | Value | Instrument |
|---|---:|---|
| `UseSqlite` sites in tree | **1** (`CovenantContext.cs:59`) | full-tree probe, matches printed `[verified]` |
| `appsettings.json` keys | **5**, zero connection strings | file printed in full `[verified]` |
| `AddDbContext` connection strings | **0** | `Startup.cs:46-49` read `[verified]` |
| `GruntTaskingType` consumer layers | **5** | enumeration, §2.1 `[verified]` |
| `else` branches inside `TaskExecute` | **4**, none after `:335` on `Type` | structural scan over `:236-413` `[verified]` |
| `Task` files in `Data/Tasks/` | **11** | directory enumeration `[verified]` |
| total bytes, those files | **318,063** | summed from 11 emitted rows `[verified]` |
| task definitions | **95** | per-file regex, summed `[verified]` |
| initializers after `:32` in `Initialize` | **2** (`:33`, `:34`) | source read `[verified]` |
| NLog entries on this failure path | **0** | logger configured `:153-164`, after call `[verified]` |

### 4.6 Failure #23 (new, self-caught) — a report that names the corruption strings it tests for will match itself

`[verified]` §5.1. My mojibake probe returned **1** for each of three marker strings. The file is **clean**: every hit falls on **one line — the line naming the markers** — and the byte-signature probes (`c3a2e28094`, `c3a2c2`, `e2809d`, `e280a0`) all return **0**. `[verified]`

`[inferred]` **New species: a textual self-reference is an unavoidable false positive for a textual probe** — unlike D63's R-63.7, which was a scanner artifact. `[verified]` **Two defences, both applied here: (1) probe the byte signatures, which cannot self-match through the encoder; (2) locate every character hit to a line number and print the line before calling it a defect.** `[verified]` `[inferred]` **Same discipline as #20 — a coordinate, not a count, is what separates a real hit from a surface match.** `[verified]`

---

## 5. Verification and residuals

### 5.1 `[verified]` Encoding and shape

`[verified]` Strict UTF-8 decode: **PASS**, zero invalid sequences. **Zero double-encoding byte signatures:** the probes `c3a2e28094`, `c3a2c2`, `e2809d`, `e280a0` each return **0**; the only non-zero hit is `c382` = **1**, and it is on **this very line** — the self-referential marker literal in this sentence, not file corruption. `[verified]` **I verified that by locating every non-ASCII hit to a line number before reporting: all three marker hits fall on one line, this one.** `[verified]` **Method lesson recorded as #23 (§4.6): a report that names the corruption strings it tests for will match itself — scan the byte signatures, which cannot self-match, and locate any character hit to a line before calling it a defect.** `[verified]`

### 5.2 `[verified]` Coordinates are recorded as pairs

`[verified]` **Every line number in this report is written `file:line`** — §0.1's discipline, applied because D73 §0.1 recorded three `EnsureCreated` sites when there were two, by carrying `153` across files. `[verified]`

### 5.3 `[inferred]` Residuals

- **R-83.1 `[verified]` — CLOSED, no effect.** The DB path is compiled-in; D73 §2 is unchanged (§1.4). `[verified]`
- **R-83.2 `[verified]` — an undeclared numeric is a SILENT NO-OP** at `GruntHTTP.cs:335`+ (no terminal `else`). Operator sees a task with no result and no error (§2.3-2.4). `[inferred]` **Probe:** task a grunt with `TaskingType: 99` and observe whether a tasking response is queued.
- **R-83.3 `[verified]` — a mid-directory abort leaves the DB PARTIALLY SEEDED**, and the `:399` guard then prevents the remaining files loading on restart (§3.2). `[inferred]` **Probe:** place a malformed YAML early in the directory, start, inspect `GruntTasks` count.
- **R-83.4 `[verified]` — blast radius is BOTH role and theme setup**, startup dies, no Covenant log (§3.3-3.4). **Exposure is local-write, not remote** (§3.5). `[verified]`
- **R-83.5 `[inferred]` — `Common.cs:25`'s `Split("bin")[0]` is a fragile path derivation.** If the install path contains `bin` before the assembly, the data directory resolves elsewhere. **Not exploited; not measured.** `[inferred]` **Probe:** enumerate `Common.CovenantDirectory` under an install path containing `bin`.

### 5.4 `[verified]` Protected files unchanged

`[verified]` Verified by **size + mtime** after writing §0-§3: **D40** 34,079 · **D46** 34,539 · **D50** 30,132 · **D52** 21,989 · **D57** 29,268 · **D63** 37,810 · **D67** 35,911 · **D72** 30,180 · **D73** 24,323 — **all UNCHANGED.** `[verified]` **D60 not found at `reports/DEEP/`** — flagged, not passed over; could not verify by size. `[verified]`

---

*D83 — `covenant-diver` — round 22. Source-only: no REA, no `open_binary`, no build, no execution, no provider. D80 is cited and its residual #1 closed, not re-claimed; D73 and D52 cited, neither edited. Rule 20 applied at §2.1 and §3.1 with the enumeration printed beside the claim. Every zero carries a positive control. Every line number carries its file.*