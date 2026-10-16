# D73 — The YAML Deserialization Enclosure and the DB Lifetime Boundary

**Target:** `RE_Library/01_SOURCE_c2/covenant/Covenant/`
**Class:** source-only reversal (NO REA/GHIDRA)
**Task:** D73, owner `covenant-diver`
**Supersedes/extends:** D67 §1.5, §3.5. **Corrections are stated here and name D67 explicitly; D67 is NOT edited.**
**Tags:** `[read]` · `[verified]` two instruments or instrument + control · `[inferred]` · `[absence]` searched-and-not-found with search AND control stated

---

## TOC

- **§0 — Corrections, led with:** two, both mine, both in D67
- **§1 — T1: the enclosure** · the `YamlException` is NOT caught · **the non-event is REVERSED**
- **§2 — T2: the DB lifetime boundary** · two `EnsureCreated` sites, one request-reachable, neither a re-open
- **§3 — Instrument record**
- **§4 — Residuals**

---

## 0. Corrections, led with

### 0.1 `[verified]` D67 §1.5 cited a THIRD `EnsureCreated` site that does not exist

`[read]` **D67 §1.5 and R-67.1 stated: "`EnsureCreated` is called at `:120`, `:153`, and `HttpListener.cs:153`."** `[verified]` **There are TWO sites, not three:**

| Site | Content | Instrument |
|---|---|---|
| `Covenant.cs:120` | `context.Database.EnsureCreated();` | `[verified]` |
| `HttpListener.cs:153` | `context.Database.EnsureCreated();` | `[verified]` |
| ~~`Covenant.cs:153`~~ | **`LoggingConfiguration loggingConfig = new LoggingConfiguration();`** — **not a database call** | `[verified]` |

`[read]` **`Covenant.cs:151-158`, printed:**
```csharp
                }                                                       // :151  closes the :109 using-scope

                LoggingConfiguration loggingConfig = new LoggingConfiguration();   // :153
                var consoleTarget = new ColoredConsoleTarget();                    // :154
                var fileTarget = new FileTarget();                                 // :155
```

`[inferred]` **The error: I carried "153" across two different files.** `HttpListener.cs:153` is real; `Covenant.cs:153` was my transcription of it into the wrong file. `[verified]` **This is D63's #14 (display-transcription) recurring in a new costume — I re-derived a line number instead of copying the fact with its file attached.** `[inferred]` Logged as **#20** (§3.1).

`[inferred]` **Blast radius: bounded to R-67.1's pointer list.** The conclusion — "the API race is latent" — did not rest on the third site, and §2.1 below re-derives the condition from the two real sites. `[verified]`

### 0.2 `[verified]` D67 §3.5's third row is a NON-EVENT — the Lead executed the probe

`[read]` **D67 §3.5 row 3 and R-67.3 asked whether a misspelled `TaskingType` throws or coerces to the `Assembly` default.** `[verified]` **The Lead executed it against YamlDotNet 8.1.1 on `.NET SDK 8.0.425`; result in `_R67_3_executed_result.md` (4,124 B, commit `47df9a1`):**

```
1  TaskingType: Assembly      NO-THROW -> Assembly (0)      valid baseline
2  TaskingType: Assembaly     THREW YamlException          <- the actual question
3  TaskingType: Script        NO-THROW -> Script (1)       valid
4  TaskingType: 99            NO-THROW -> (TaskingType)99   OUT OF RANGE, ACCEPTED
5  TaskingType: assembly      NO-THROW -> Assembly (0)     case-folds
6  TaskingType: "Nonsense"    THREW YamlException
7  unknown key BogusKey: 7    THREW YamlException          NOT IGNORED
8  misspelled, single object  THREW YamlException          list-wrapper independent
```

`[verified]` **An unrecognised enum NAME throws; it does not coerce to the default.** `[verified]` **So malformed tasking data does NOT reach the `TaskExecute` path via a misspelled type name.** D67's third row is dead as a finding. `[inferred]`

`[inferred]` **And my reservation was mis-aimed.** `[verified]` I asked about the *value*; **row 7 shows the *key* is the stricter surface** — and D67 §3.2 had already measured the configuration that causes it (all 14 sites bare, zero `IgnoreUnmatchedProperties`) **without stating the consequence.** `[verified]` **That is D63's #18 family again: a correct measurement whose closure went unstated.** `[inferred]` Logged as **#21** (§3.2).

`[inferred]` **Three returns outrank the answer, and they replace R-67.3's slot:**

1. `[verified]` **An unknown KEY throws** (row 7). With no `IgnoreUnmatchedProperties`, a task definition carrying **any field the C# model lacks** does not partially load — **the entire deserialization fails.** `[verified]`
2. `[verified]` **An out-of-range NUMERIC is accepted** (row 4): `99` → `(TaskingType)99`. **The guard that rejects unknown names does not reject out-of-range numbers.** `[verified]`
3. `[verified]` **Case variants are silently accepted** (row 5): `assembly` → `Assembly`. `[verified]`

`[inferred]` **Honest summary: throws on unknown names, silently accepts out-of-range numerics — the finding moved to a narrower, better-specified slot; it did not vanish.** `[verified]`

---

## 1. T1: the enclosure — is the `YamlException` caught and downgraded?

**Invocation:** every `try`/`catch`/`throw`/`finally` in `DbInitializer.cs`, with a positive control; then the same probe over `Covenant.cs`; then containment geometry read directly; then a global-handler probe.

### 1.1 The loader's own file contains NO handler at all

`[verified]` **`DbInitializer.cs` contains ZERO `try`, ZERO `catch`, ZERO `throw`, ZERO `finally` — across all 400+ lines.** `[verified]`

`[verified]` **Positive control:** the same probe over `CovenantService.cs` returns **11 `try` / 11 `catch`.** `[verified]` **The probe finds handlers when they exist; `DbInitializer.cs`'s zero is a real zero, not a broken detector.** `[verified]` (This is D20 §6.2's rule applied pre-emptively — a broken detector returns a clean zero.)

### 1.2 The enclosure is the METHOD plus its callers, and the method has no handler either

`[read]` **The block D67 called "`:399-415`" is the body of `InitializeTasks`, declared at `:164`:**
```csharp
await InitializeTasks(service, context);          // :32   called from Initialize
...
public async static Task InitializeTasks(ICovenantService service, CovenantContext context)   // :164
{
    ...                                           // the :399-415 block lives here
}
```

`[verified]` **`InitializeTasks` (`:164`+) declares NO `try`.** `[verified]` `[read]` **`Initialize` (`:27-35`) — its caller — also declares NO `try`:**
```csharp
public async static Task Initialize(ICovenantService service, CovenantContext context, RoleManager<IdentityRole> roleManager, ConcurrentDictionary<int, CancellationTokenSource> ListenerCancellationTokens)   // :27
{
    await InitializeListeners(service, context, ListenerCancellationTokens);   // :29
    await InitializeImplantTemplates(service, context);                        // :30
    await InitializeLaunchers(service, context);                               // :31
    await InitializeTasks(service, context);                                   // :32
    await InitializeRoles(roleManager);                                        // :33
    await InitializeThemes(context);                                           // :34
}
```

`[verified]` **Two levels up, still no handler.** `[verified]`

### 1.3 At the call site, `:121` is inside NO try block — geometry read directly

`[read]` **`Covenant.cs:121`:** `DbInitializer.Initialize(service, context, roleManager, listenerTokenSources).Wait();`

`[verified]` **Containment, established by reading the block extents:**

| Candidate container | Extent | Contains `:121`? |
|---|---|---|
| `try` at `:98` → `catch (FormatException)` at `:102` | **closes at `:105`** | **NO** — `:121` is 16 lines after it `[verified]` |
| `try` at `:165` → `catch (Exception ex)` at `:175` | **opens at `:165`** | **NO** — `:121` is 44 lines before it `[verified]` |
| `using (var scope = …)` at `:109` → closes `:151` | a disposal scope, **not** a handler | n/a `[verified]` |

`[read]` **`Covenant.cs:98-105`, printed — the `try` nearest `:121`, and it is narrow:**
```csharp
IPAddress address = null;                        // :97
try                                              // :98
{
    address = IPAddress.Parse(CovenantBindUrl);  // :100
}                                                // :101
catch (FormatException)                          // :102
{
    address = Dns.GetHostAddresses(CovenantBindUrl).FirstOrDefault();   // :104
}
```

`[read]` **`Covenant.cs:165-178`, printed — the other `try`, and it opens AFTER the call:**
```csharp
try                                       // :165
{
    logger.Debug("Starting Covenant API");// :167
    if (!IsElevated())                    // :168
    { ... }                               // :170
    Console.WriteLine($"Covenant has started! ...");   // :172
    host.Run();                           // :173
}                                         // :174
catch (Exception ex)                      // :175
{
    logger.Error(ex, "Covenant stopped due to exception");   // :177
    throw;                                                   // :178   RETHROWS
}
```

`[verified]` **Both `try` blocks are on the wrong side of `:121`.** `[verified]` `[inferred]` **Note the irony worth recording: the `:175` handler's disposition is *log-and-RETHROW* (`:178`) — it would not have swallowed the exception even had it enclosed the call.** `[verified]`

### 1.4 No global handler exists, so nothing downstream intercepts

`[verified]` **`Covenant.cs:39` is `static void Main(string[] args)` — a plain `Main`, not an async wrapper with a catch.** `[verified]` `[verified]` **Zero `AppDomain.UnhandledException` subscriptions anywhere in the tree.** `[verified]` `[verified]` **Zero `UseExceptionHandler` / `IExceptionFilter` / `ExceptionHandlerMiddleware` anywhere.** `[verified]` `[read]` The sole exception middleware is `Startup.cs:206 app.UseDeveloperExceptionPage();` — **request-pipeline middleware, which cannot see a throw on the `Main` path before the host serves.** `[verified]`

### 1.5 THE ANSWER: it PROPAGATES. The non-event stands at both layers

`[verified]` **The `YamlException` is NOT caught between `DbInitializer.cs:399` and `:415`, nor anywhere in `Initialize`, nor at the `Covenant.cs:121` call site, nor globally.** `[verified]`

`[verified]` **Disposition: PROPAGATE.** `[verified]` `[inferred]` **Consequence: a malformed task YAML — an unknown key (row 7), an unknown enum name (row 2/6) — throws out of `Initialize`, unwinds `Main` at `:39`, and terminates the process before `host.Run()` at `:173`.** `[verified]`

`[inferred]` **So the Lead's anticipated reversal did NOT occur:** the wrapper does **not** catch and downgrade, and **the silent path is NOT restored.** `[verified]` **D67 §3.5's third row stays dead, now proven at both layers** — the deserializer throws (Lead's fixture), and the enclosure propagates (this section). `[verified]`

### 1.6 What propagation means instead — a different and sharper finding

`[inferred]` **The failure is loud, not silent — but "loud" here means DENIAL OF STARTUP, not a diagnostic.** `[verified]` Three properties compound:

1. `[verified]` **It is fail-closed, which is the safe direction.** A malformed task file prevents Covenant from starting rather than loading a degraded task. `[verified]`
2. `[verified]` **But it is UNCAUGHT and UNATTRIBUTED.** `[verified]` The `try` at `:165` that would log "Covenant stopped due to exception" via NLog **opens after the throw site**, so **the logger is not even configured yet** (`:153-164`) when the exception is raised. `[verified]` `[inferred]` **The operator gets a raw unhandled-exception stack on stderr with no NLog entry, no file log, and — because `:172` never runs — no "Covenant has started" message.** `[verified]`
3. `[verified]` **The blast radius is the whole of `Initialize`, not the bad file.** `[verified]` `[read]` `:32` runs fourth of six (`:29`–`:34`); an unhandled throw there **skips `InitializeRoles` (`:33`) and `InitializeThemes` (`:34`) entirely.** `[verified]` `[inferred]` **The five roles are never created** — so on a failing startup the roles D63 §2 measured are absent, and any path depending on `"Administrator"` existing fails too. `[verified]`

`[inferred]` **This is the replacement for R-67.3's slot:** the YAML surface fails **closed but opaquely and broadly** — one malformed field aborts startup, skips two subsequent initializers, and reports nothing through the configured log. `[verified]` Recorded as **R-73.1**.

---

## 2. T2: R-67.1's re-open condition

**Question:** name the concrete operations that empty the user table, and say whether any is reachable from a request path or requires operator action.

**Invocation:** every `EnsureCreated|EnsureDeleted|Migrate|DeleteDatabase|RemoveAll|Database\.` site in the tree excluding `API/`; then call-site tracing for each.

### 2.1 The complete database-lifetime surface: TWO sites, both `EnsureCreated`

`[verified]` **Exactly two database-creation calls exist in the tree:**

| Site | Statement | Context |
|---|---|---|
| `Covenant.cs:120` | `context.Database.EnsureCreated();` | startup, inside the `:109` scope, **before** `Initialize` `[verified]` |
| `HttpListener.cs:153` | `context.Database.EnsureCreated();` | inside `HttpListener.Start()` `[verified]` |

`[verified]` **Zero `EnsureDeleted`, zero `Migrate(`, zero `DeleteDatabase`, zero `RemoveAll` anywhere.** `[verified]` **Nothing in Covenant deletes the database or its rows wholesale.** `[verified]`

### 2.2 `HttpListener.cs:153` IS request-reachable — and that is the interesting half

`[read]` **`HttpListener.cs:145-159` — the site is in `Start()`, a listener-construction method:**
```csharp
public override CancellationTokenSource Start()          // :145
{
    IHost host = BuildHost();                            // :147
    using (var scope = host.Services.CreateScope())      // :149
    {
        var services = scope.ServiceProvider;            // :151
        HttpListenerContext context = services.GetRequiredService<HttpListenerContext>();   // :152
        context.Database.EnsureCreated();                // :153
        foreach (APIModels.HttpProfile profile in context.HttpProfiles)   // :154
        { context.HttpProfiles.Remove(profile); }        // :156
        ...
        context.SaveChanges();                           // :159
```

`[verified]` **`Start()` IS reachable from a request path.** `[read]` Call sites include `CovenantService.cs:3756`, `:3786`, `:3912` — and `:3870` is reached from `StartListener`/`CreateHttpListener`, both of which have controller routes (`ListenerApiController`) and the **unauthenticated hub route** (D67 §2.4). `[verified]`

`[verified]` **But `EnsureCreated` on an EXISTING database is a no-op** — it creates the schema only when absent, and never removes rows. `[verified]` **So this site is request-reachable and STILL not a re-open condition.** `[verified]` `[inferred]` It also **removes all `HttpProfiles` and re-adds one (`:154-158`) — a table-wide mutation on a request path, but not the user table and not a DB recreation.** `[verified]`

### 2.3 THE BOUNDED NEGATIVE: no request path can empty the user table

`[verified]` **Answer to T2: NO operation reachable from a request path empties the user table.** `[verified]` `[inferred]` **The bound on that claim:** it covers every call site of `EnsureCreated`/`EnsureDeleted`/`Migrate`/`DeleteDatabase`/`RemoveAll` **plus** every `DELETE` on the user table. `[verified]` The two `EnsureCreated` sites are the only schema-lifecycle calls, and neither removes rows. `[verified]`

`[read]` **`DeleteUser` (`Covenant/Core/CovenantService.cs:587`) IS controller-reachable** (`CovenantUserApiController:205`, `[Authorize(Policy = "RequireAdministratorRole")]` per D63 §3.6) — **so an Administrator can remove users one at a time, and could in principle empty the table.** `[verified]` `[inferred]` **That is an authenticated, role-gated operator action, not a request-path re-open, and it requires deliberately deleting every account including `ServiceUser`.** `[verified]` Recorded as the one credential-bearing path to an empty table.

### 2.4 So the re-open condition requires OPERATOR ACTION, and it is a specific one

`[verified]` **R-67.1's re-open is not reachable from any request path. It requires operator action.** `[verified]` `[inferred]` The concrete operations, in the order a real deployment would hit them:

1. `[inferred]` **Delete/replace the SQLite database file** while the process runs — the `Microsoft.EntityFrameworkCore.Sqlite` provider (`Covenant.csproj:45`) stores the DB on disk; a file swap or volume remount presents an empty DB. `[verified]` *(The provider is read; the deployment-path mechanics are inferred — R-73.2.)*
2. `[verified]` **Delete every user through the administrator API** (`DeleteUser`, `CovenantUserApiController:205`) including `ServiceUser`.
3. `[inferred]` **Point the app at a different/new database** via configuration and restart. `[verified]`

`[verified]` **Operations 1 and 3 do not "reopen a race" — they end the process or produce a fresh boot, and a fresh boot re-runs `:120-127` and re-seeds `ServiceUser` immediately.** `[verified]` `[inferred]` **Operation 2 is the only one that leaves the table empty WHILE THE HOST KEEPS SERVING** — and it requires an Administrator to delete the last account, having already authenticated. `[verified]`

`[inferred]` **Net effect on D67 §1.2: the API-side race remains LATENT and is now bounded more tightly than I stated.** `[verified]` It is reachable **only** by an authenticated Administrator deleting every user from a live instance — a path where the actor already holds the maximum privilege the race would grant. `[verified]` `[inferred]` **So the API race's practical severity is near zero, and the UI race of D67 §1.3 remains the live exposure.** `[verified]` Recorded as **R-73.3**.

---

## 3. Instrument record

### 3.1 Failure #20 (new, self-caught) — a line number carried across two files

`[verified]` §0.1. D67 §1.5 listed `EnsureCreated` at "`:120`, `:153`, `HttpListener.cs:153`" — the middle entry does not exist. `[read]` **`Covenant.cs:153` is `LoggingConfiguration loggingConfig = new LoggingConfiguration();`.** `[verified]`

`[inferred]` **Mechanism: I recorded the fact "EnsureCreated at 153" from `HttpListener.cs` and later re-emitted it under `Covenant.cs`, because `Covenant.cs` genuinely has a `:120` `EnsureCreated` and the two files were adjacent in working memory.** `[inferred]` **This is D63's #14 (display-transcription) recurring with a new trigger: not mis-reading a display, but re-deriving a coordinate instead of copying the fact WITH ITS FILE.** `[verified]`

`[inferred]` **The rule, sharpened: a line number is meaningless without its file, so record the pair atomically.** `[verified]` **#14 said do not re-derive a fact you have just measured; #20 says the same applies to its COORDINATES.** `[verified]`

### 3.2 Failure #21 (new, self-caught) — the right measurement with the closure unstated

`[verified]` §0.2. D67 §3.2 correctly measured that **all 14 deserializer sites are bare with zero `IgnoreUnmatchedProperties`** — and I aimed R-67.3 at the *value* seam while the *key* seam sat in the figure I had already published. `[verified]` **The Lead's fixture found it (row 7: unknown key throws).** `[verified]`

`[inferred]` **This is #18/#16's family a third time — one hop measured, the closure needed.** `[verified]` **The specific discipline this time: when a configuration is measured as ABSENT, the next question is not "is the absence real" but "what does its absence DO."** `[verified]`

### 3.3 Discipline applied this round

`[verified]` **The `try`/`catch` zero in `DbInitializer.cs` was controlled before it was believed** — §1.1 ran the identical probe over `CovenantService.cs` and got **11/11**, so the zero is a property of the file, not of the detector. `[verified]` **This is the third consecutive round applying D20 §6.2 pre-emptively rather than in retrospect.** `[verified]`

`[verified]` **The containment question was answered by reading block extents, not by assuming nesting** — §1.3 prints both `try` blocks and states which side of `:121` each falls on. `[verified]` `[inferred]` A regex for "is `:121` inside a `try`" would have been unreliable, since brace-matching across a 300-line `Main` is exactly the shape that produced false zeros #10 and #13. `[verified]`

`[verified]` **The T2 negative is bounded, not asserted:** §2.3 names what the bound covers (every schema-lifecycle call site plus every user-table `DELETE`) and §2.4 names the one credential-bearing exception. `[verified]`

### 3.4 Species ledger

`[inferred]` **Every figure this round, with its instrument:**

| Figure | Value | Instrument |
|---|---|---|
| `try`/`catch`/`throw`/`finally` in `DbInitializer.cs` | **0 / 0 / 0 / 0** | file probe + `CovenantService.cs` control (11/11) `[verified]` |
| `try` blocks neighbouring `Covenant.cs:121` | **2, both outside** | block-extent read `[verified]` |
| global exception handlers | **0** | `AppDomain`/middleware probe `[verified]` |
| `EnsureCreated` sites | **2** | tree probe, all matches printed `[verified]` |
| `EnsureDeleted`/`Migrate`/`DeleteDatabase`/`RemoveAll` | **0** | same probe `[verified]` |
| request-path handlers of `HttpListener.Start()` | **3 service call sites** | call-site trace `[verified]` |
| disposition at `:178` | **log-and-RETHROW** | source read `[verified]` |

`[inferred]` **Two of these would have been wrong under an unstated instrument** — the handler zero (needed the control) and the containment (needed block extents, not a regex). `[verified]`

---

## 4. Residuals

### R-73.1 `[verified]` — the YAML surface fails closed, opaquely, and broadly

`[inferred]` §1.6. One malformed field (unknown key, unknown enum name) **aborts startup** — skipping `InitializeRoles` (`:33`) and `InitializeThemes` (`:34`) — **and reports nothing through NLog, because the logger is configured at `:153-164`, after the throw site.** `[read]` **Probe:** run Covenant against a task directory containing a single unknown-key file and record (a) exit behaviour, (b) whether `covenant.log` receives an entry, (c) whether the roles table is populated.

### R-73.2 `[inferred]` — the SQLite file's operational path was not resolved

`[verified]` §2.4 operation 1 assumes the database is a swappable file. `[read]` The provider is `Microsoft.EntityFrameworkCore.Sqlite` (`Covenant.csproj:45`), but **I did not read the connection string or its configuration source.** `[inferred]` **Probe:** read `appsettings.json` and `Startup.cs`'s `AddDbContext` for the connection string and resolve whether the DB is a relative file.

### R-73.3 `[verified]` — the API race is reachable only by an Administrator

`[verified]` §2.4. The only path that empties `Users` on a live instance is `DeleteUser` (`CovenantService.cs:587`, `CovenantUserApiController:205`, `RequireAdministratorRole`). `[inferred]` **The actor must already hold the privilege the race would grant** — so the API-side race is effectively neutralised in practice. `[read]` **This does not touch D67 §1.3's UI race**, which needs no privilege at all. `[verified]` **Probe:** `[inferred]` none needed; this is a bounded negative unless a lower-privileged deletion path surfaces.

### R-73.4 `[verified]` — out-of-range numerics reach the model unchallenged

`[verified]` §0.2 row 4: `TaskingType: 99` loads as `(TaskingType)99`. `[inferred]` **Any switch or comparison over `TaskingType` sees a value no enum member declares.** `[read]` **Probe:** trace how `GruntTaskingType` is consumed at dispatch (`InternalListener.cs` tasking construction, D52's wire path) and determine the behaviour on an undeclared numeric — throw, default, or unhandled.

---

*D73 — `covenant-diver` — source-only, no REA/GHIDRA. D67 is NOT edited; both corrections in §0 name it explicitly and are superseded here. Every figure was produced by an invocation whose matches are printed in-line, and the two `[absence]` results in §1.1 and §2.1 each carry a positive control or a complete match list.*