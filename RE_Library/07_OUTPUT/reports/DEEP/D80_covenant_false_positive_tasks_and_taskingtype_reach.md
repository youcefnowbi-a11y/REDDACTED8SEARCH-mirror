# D80 — Covenant false-positive task class, and `TaskingType` reach from the UI

> **RENUMBERED D73 -> D80 by the Lead, round 21.** This report was authored under the number
> `D73` while `D73_covenant_yaml_enclosure_and_db_lifetime.md` (covenant-diver) was being
> written against the same number. **Two files, one number — a Lead allocation error, not a lane
> error.** covenant-diver's D73 was already committed at `1e7c4c2` and is the surviving D73; this
> report is the one renumbered. §0's probe-script names (`d73_enum.ps1` etc.) are REAL FILENAMES
> of artefacts produced under the old number and are intentionally NOT rewritten.

**Scope:** T1 (is the `Brute` false-positive an instance or a class?) · T2 (does any load path feed UI-controlled input to `FromSerializedGruntTask` such that an out-of-range numeric `TaskingType` can arrive?)
**Targets:** `Covenant/Data/Grunt/{Brute,GruntBridge,GruntHTTP,GruntSMB}/*.cs` · `Covenant/Models/Grunts/GruntTask.cs` · `Covenant/Core/DbInitializer.cs` · `Covenant/Covenant.cs` · `Covenant/Components/GruntTasks/GruntTaskForm.razor` · `Covenant/Components/GruntTaskings/GruntTaskingForm.razor` · `_R67_3_executed_result.md` (Lead's executed R-67.3)
**Method:** pure source; no provider, no build, no execution. Scripts to files, never inline. Comments stripped before classification. **Every path list ENUMERATED before being touched (§0).** Every number carries its invocation and denominator.
**Write scope:** this file only. D40/D46/D50/D52/D57/D60/D67/D72 unmodified.

---

## 0. Method note — the mechanical fix the Lead asked for

**The Lead's instruction: "enumerate every path list before touching it, this round, and say in the method note that you did."** Done, and it did not merely satisfy a rule — **it changed both answers.**

**Every write script for this report opens with an enumeration stage, not a construction stage:**

| Probe | Enumeration performed FIRST | What it settled |
|---|---|---|
| `d73_enum.ps1` | all files under `Data\Grunt` (**17**, incl. `.gitignore`/`.csproj`/`.sln`) · all `*Grunt*`/`*Stager*`/`*Listener*`/`*.cs` in Covenant · **all 152 `.cs` for `TaskExecute`** | **the family set is CLOSED at 4.** T1's "enumerate the rest" resolves to a finite population, not a sample |
| `d73_t2b.ps1` | all `DbInitializer.cs` (**1**) · all `FromSerializedGruntTask` sites (**11**) · all `*.razor` for `TokenTask`/`TaskingType` | the load path and the form set |
| `d73_model.ps1` | **all 152 `.cs` for `class SerializedGruntTask`** | **the model is at `Models\Grunts\GruntTask.cs:403`** — *not* `GruntTaskComponents.cs`, which my first probe guessed and which cost me a false negative (§6 failure 1) |

**The enumeration directly produced the T2 answer.** I had assumed `SerializedGruntTask` lived in `GruntTaskComponents.cs` (a name that *sounds* like a container for serialized task components). It does not. **Enumerating found it at `Models\Grunts\GruntTask.cs:403` — the same file whose API-side twin carries `TokenTask` — and reading it produced the `:413` default that is the load-bearing fact of T2.**

---

## 1. T1 — is the `Brute` false positive an instance or a class?

### 1.1 **The population is CLOSED at four, and `TaskExecute` definitions number exactly four**

**`TaskExecute` DEFINITIONS — enumerated across all 152 `.cs`:**

| Family | Line | Signature |
|---|---:|---|
| **`Brute`** | **`:203`** | **`private static void TaskExecute(...)`** |
| `GruntBridge` | `:230` | `private static IntPtr TaskExecute(...)` |
| `GruntHTTP` | `:236` | `private static IntPtr TaskExecute(...)` |
| `GruntSMB` | `:230` | `private static IntPtr TaskExecute(...)` |

**Four definitions total. No other file in the tree defines one.** `[invocation: `Select-String 'static\s+\w+\s+TaskExecute'` over 152 enumerated `.cs`; matches printed]`

### 1.2 **`TaskExecute` CALL SITES — enumerated: 8 total, TWO per family**

| Family | `message.Token` branch | `else` branch | Return consumed? |
|---|---|---|---|
| **`Brute`** | **`:168`** — `Thread t = new Thread(() => TaskExecute(...))` | `:175` — same | **NO — discarded in BOTH** |
| `GruntBridge` | `:182` — `() => impersonatedToken = TaskExecute(...)` | `:202` — `() => TaskExecute(...)` | **YES** in token branch |
| `GruntHTTP` | `:188` — `() => impersonatedToken = TaskExecute(...)` | `:208` — `() => TaskExecute(...)` | **YES** in token branch |
| `GruntSMB` | `:182` — `() => impersonatedToken = TaskExecute(...)` | `:202` — `() => TaskExecute(...)` | **YES** in token branch |

### 1.3 **The correction to the brief's framing — and it matters**

**The brief asks me to "enumerate the task families whose `TaskExecute` return is discarded by the caller, versus consumed."** **The enumeration shows that framing is one level off, in a way that would have produced a wrong answer:**

**Every family discards the return in its `else` branch.** `GruntHTTP:208` discards. `GruntSMB:202` discards. `GruntBridge:202` discards. **`Brute:175` also discards.** So "families that discard" = **4 of 4**, which is true and useless.

**The discriminator is not the family — it is the BRANCH.** `message.Token` is a **per-message boolean**, not a family property:

- **`message.Token == true` → the token branch.** Return consumed in 3 families; **discarded in `Brute` only.**
- **`message.Token == false` → the else branch.** Return discarded in **all four**, and *correctly* — there is no token to return, so nothing to consume.

**So the correct enumeration is: which families discard the return INSIDE the `message.Token` branch. Answer: exactly one, `Brute`.**

### 1.4 **THE FALSE-POSITIVE DISCRIMINATOR, measured**

**The brief's discriminator — "whether the return value is consumed" — is necessary but not sufficient.** A discarded return is harmless if nothing depended on it. **The sufficient discriminator is: is the success message composed independently of the discarded effect?** Measured on the two-sided comparison:

**`GruntHTTP:181-203` / `GruntSMB:175-197` / `GruntBridge:175-197` — the consumer, verbatim:** **`if (completed && impersonatedToken != IntPtr.Zero)` → `identity.Impersonate()`.** **The return value GATES the impersonation.**

**`Brute:166-172` — the whole branch, verbatim:**
```csharp
else if (message.Token)
{
    Thread t = new Thread(() => TaskExecute(messenger, message, Delay));
    t.Start();
    Tasks.Add(new KeyValuePair<string, Thread>(message.Name, t));
    bool completed = t.Join(5000);          // :171  captured...
}                                           // :172  ...and the block ENDS. Never read.
```

**`Brute` captures `bool completed` at `:171` and never reads it.** No `if`, no gate, no consumer. **The branch ends at `:172`.**

**And the success message is emitted from inside `TaskExecute` itself, not from the caller.** `Brute.cs` constructs `new GruntTaskingMessageResponse(GruntTaskingStatus.Completed, output)` at `:113, :126, :131, :144, :164` — **all inside `TaskExecute`, all from the local `output` string, none from any return value.** **`output` on the token path is the assembly's own success string ("Successfully made and impersonated token for user: ...").**

**So the false-positive shape is:**
> **A success message composed from a LOCAL STRING that the effect never validates, emitted unconditionally as `GruntTaskingStatus.Completed`, while the value that would have gated the effect (`bool completed`) and the value that carries it (`impersonatedToken`) are both captured-then-discarded.**

**Measured once. Count: 1.**

### 1.5 **THE T1 ANSWER: it is an INSTANCE, not a class — and it NARROWS D60 while confirming it**

**Count of families with a consumed `TaskExecute` return in the token branch: 3 (`GruntHTTP`, `GruntSMB`, `GruntBridge`).**
**Count of families with a discarded return in the token branch: 1 (`Brute`).**
**Count of families where a success message is composed independently of the gating value: 1 (`Brute`).**

**`Brute` is the only one. There is no false-positive class in the `TaskExecute` return surface.**

**Why this narrows rather than weakens D60:** D60 §1.3's finding was "`Brute`'s token branch is dead." **T1 shows the token branch is dead in exactly one place, and that the `else`-branch symmetry across all four families is CORRECT design, not a defect.** **A class would have meant the whole token mechanism is unsound; an instance means one family was mis-forked.** **The blast radius is `Brute` alone.**

**The one thing this does NOT clear:** the `else` branch discards the return in all four families, and I measured that it is *correct* to do so — **there is no `impersonatedToken` to gate on when `message.Token` is false.** **That is not a defect and I am not reporting it as one.** `[invocation: 8 call sites enumerated + 5 `GruntTaskingMessageResponse` sites in `Brute.cs` + 3 consumer blocks read verbatim]`

---

## 2. T2 — does the UI reach `FromSerializedGruntTask` with an out-of-range numeric `TaskingType`?

### 2.1 **The load path, enumerated — one caller, no handler anywhere**

**`FromSerializedGruntTask` sites: 11, across 3 files** (`DbInitializer.cs:409`, `GruntTask.cs:142/174/185/145/156`, `GruntTaskAuthor.cs:37/55/66`, `GruntTaskOption.cs:42/65/76`).

**The only path that feeds OPERATOR-CONTROLLED input is `DbInitializer.cs:401-409`, verbatim:**
```csharp
List<string> files = Directory.GetFiles(Common.CovenantTaskDirectory)
    .Where(F => F.EndsWith(".yaml", StringComparison.CurrentCultureIgnoreCase)).ToList();   // :401-403
IDeserializer deserializer = new DeserializerBuilder().Build();                              // :404  BARE
foreach (string file in files)                                                               // :405
{
    string yaml = File.ReadAllText(file);                                                    // :407
    List<SerializedGruntTask> serialized = deserializer.Deserialize<List<SerializedGruntTask>>(yaml);  // :408
    List<GruntTask> tasks = serialized.Select(S => new GruntTask().FromSerializedGruntTask(S)).ToList();  // :409
```

**Its input is `Common.CovenantTaskDirectory` — a DIRECTORY OF YAML FILES ON DISK, read at startup.** **Not an HTTP parameter, not a form post.**

### 2.2 **The exception is NOT caught. This closes R-67.3's own named next probe.**

**R-67.3's `Bounds` section states the open question plainly:** *"the real `:399-415` path wraps this call in its own error handling, which was not exercised. Whether the thrown `YamlException` is caught and downgraded there is not measured — and that is the natural next probe, since a caught exception would restore the silent path."*

**Measured. `InitializeTasks` spans `L164-416` — 253 lines. `try` = 0, `catch` = 0, `finally` = 0.** **[Verified two ways: a segment count over `L164-416`, and a whole-file `try` count — `DbInitializer.cs` contains ZERO `try` statements in its entire 509 lines.]** **`ILogger`/`_logger`/`Log.` references: 0.**

**And the caller, `Covenant.cs:121`, verbatim:**
```csharp
DbInitializer.Initialize(service, context, roleManager, listenerTokenSources).Wait();
```

**The exact scope, measured — there IS a `try` in `Covenant.cs` before `:121`, and it does not cover the call.** `Covenant.cs:98-105`:
```csharp
try     { address = IPAddress.Parse(CovenantBindUrl); }        // :98-101
catch (FormatException) { address = Dns.GetHostAddresses(...).FirstOrDefault(); }   // :102-105
```
**That handler closes at `:105`. `:121` sits in the `using` block at `:109-151`, outside it.** **The next `try` opens at `:165` and guards `host.Run()` (`:173`), not the initializer.** **So `:121` is unhandled — and I am stating the two `try` statements and their exact spans rather than the loose "zero `try` there" I first wrote.**

**`.Wait()` on a faulted `Task` wraps the exception in an `AggregateException` and rethrows it SYNCHRONOUSLY at the call site. The call site has no handler.**

**So: a `YamlException` from `:408` propagates out of `InitializeTasks`, out of `Initialize`, out of `.Wait()` at `:121`, and terminates startup — the process exits before `host.Run()` at `:173` is ever reached. NOT downgraded, NOT logged** (the NLog logger is not even configured until `:164`), **NOT partial.** **R-67.3's three unexpected results are therefore all HARD failures of a startup-killing magnitude** — including case 7's unknown KEY. **That upgrades the Lead's §3 note ("a hard failure, not partial data") to: a hard failure that takes the server down.**

### 2.3 **`GruntTaskForm.razor` binds `TaskingType` ZERO times — the form CANNOT submit one**

**Enumerated every `@bind=` and `ValidationMessage For=` in `GruntTaskForm.razor` (478 lines, 31 sites). The form binds:** `Name` · `Description` · `Author.Name/Handle/Link` · `Aliases` · `Language` · `CompatibleDotNetVersions` · **`TokenTask` (`:113`, `type="checkbox"`)** · `UnsafeCompile` · `Compiled` · `ReferenceSourceLibraries` · `EmbeddedResources` · `ReferenceAssemblies` · `Options[].Name/Description/DefaultValue/SuggestedValues/Optional/DisplayInCommand` · `Help` · `Code`.

**`TaskingType` hits in `GruntTaskForm.razor`: 0.** `[invocation: `Select-String 'TaskingType'` over that file; count printed]`

**The brief's premise — "`GruntTaskForm.razor:113` binds `TokenTask` as a plain checkbox with no companion `TaskingType` validation" — is confirmed and then exceeded: there is no companion `TaskingType` *control* at all.** **The form has no `TaskingType` field, so no submission can carry one — numeric, absent, or otherwise.**

### 2.4 **The model tolerates absence — silently — and this is independent of YamlDotNet**

**`SerializedGruntTask`, `Models\Grunts\GruntTask.cs:403-420`, fields verbatim:**

```csharp
public GruntTaskingType TaskingType { get; set; } = GruntTaskingType.Assembly;   // :413  DEFAULT
public bool UnsafeCompile { get; set; } = false;                                  // :414
public bool TokenTask { get; set; } = false;                                      // :415  DEFAULT
```

**`TaskingType` carries an initializer defaulting to `GruntTaskingType.Assembly` (0).** **So a task YAML that OMITS `TaskingType` entirely does not throw and does not reach the unknown-name guard at all — it silently becomes `Assembly`.**

**This is a fourth case R-67.3 did not test, and it is a different mechanism from all three of its findings:** cases 2/6/7 throw on unknown *content*; **case 4 accepts out-of-range *numerics*. Neither covers ABSENCE — and absence is the one an author actually produces by typo-ing a key name.** **YamlDotNet's behaviour is not even consulted: the default lives in the C# model.**

**Measured against the shipped corpus: the absence case is REAL but UNEXERCISED.** Indent-aware enumeration of all **11 `Data\Tasks\*.yaml` files / 95 top-level task entries** gives **`named=95 · numeric=0 · ABSENT=0`**. **Every shipped task declares a named `TaskingType`, so neither the absence nor the numeric path is expressed by the corpus — both are latent capabilities.** **That is the correct framing: a real hole in the loader's validation, reachable only by an author who writes a new YAML, not by the UI and not by anything shipped.**

**`TokenTask: false` defaulting (`:415`) is the SAFE direction** — an omitted `TokenTask` means the grunt takes the `else` branch and reports honestly under the D72 finding. **The dangerous default is `TaskingType`, because `Assembly` is precisely the value that routes to `TaskExecute` and thus to the `Brute` defect.**

### 2.5 **THE T2 ANSWER: the UI is a NON-VECTOR, by a stronger route than "no validation"**

**Three independent reasons, any one of which is sufficient:**

1. **No UI control exists.** `GruntTaskForm.razor` binds `TaskingType` 0 times (§2.3). **The task-definition form cannot submit a `TaskingType` at all.**
2. **The only UI surface that DOES emit a numeric enum feeds a different consumer.** `GruntTaskingForm.razor:51-59` emits `<option value="...ToString("d")">` — **numeric.** R-67.3 case 4 proved numerics do not throw. **But `GruntTaskingForm` binds `GruntTasking.Type` (`GruntInteract.razor:195` `Type = task.TaskingType`) — the TASKING dispatch model, not the TASK DEFINITION loader.** **It never reaches `FromSerializedGruntTask`.**
3. **The loader's input is a directory of YAML on the server's disk** (`Common.CovenantTaskDirectory`, `DbInitializer.cs:401`), **read once at startup.** **Reaching it requires writing a `.yaml` file to the server's task directory — filesystem access, not UI access.**

**So: an out-of-range numeric `TaskingType` cannot arrive from the UI. It can only arrive from a hand-authored or corrupted YAML file in `Data\Tasks\` — which is a supply-chain / file-write precondition, not a UI vector.**

**And if it DOES arrive, the consequence is bounded:** `(TaskingType)99` reaches `TaskExecute`, matches **no** `if (message.Type == GruntTaskingType.X)` arm, and falls through to the terminal `else`. **That is downstream of the loader and was not exercised here.**

---

## 3. What T2 changes in D72 §3 — stated as a correction

**D72 §3.3 said the `TokenTask` contradiction is "silent by construction" and rested partly on malformed input being rejected. The Lead's R-67.3 execution shows that premise is false in general. My §3 VERDICT SURVIVES; my §3 REASONING was too broad. Corrected:**

| D72 §3.3 claim as written | Status after R-67.3 + T2 |
|---|---|
| The contradiction is structurally **latent** — observable only at the `TokenTask` branch | **HOLDS.** Nothing in the substitution logic consults `TaskExecute`'s shape. |
| Malformed input **is rejected** | **FALSE IN GENERAL — RETRACTED.** Names throw; numerics (`99` → `(TaskType)99`) and case variants (`assembly` → `Assembly`) are accepted; **and per §2.4 an ABSENT key is silently defaulted in the C# model, a case YamlDotNet never sees.** |
| The `else`-branch path is the silent one | **HOLDS, and is now better specified:** `Brute`'s token branch is dead; the `else` branch discards the return in all four families **correctly** (§1.5). |

**The corrected statement of D72 §3.3:** **the mis-grouping is latent not because malformed input is rejected, but because the template-selection path and the dispatch path are never cross-checked against each other at all.** **Input validation is orthogonal to the contradiction — which is a cleaner claim than the one I wrote, and it does not depend on any YamlDotNet behaviour.**

---

## 4. Residual unknowns, each with a concrete probe

| # | Unknown | Probe |
|---:|---|---|
| 1 | **The consequence of `(TaskingType)99` reaching `TaskExecute`.** §2.5 says "no arm matches, falls to terminal `else`" — **inferred from the 11-member enum, not measured.** | Read the terminal `else` of `TaskExecute` in all four families and confirm it reports rather than faults. |
| 2 | **Whether the `Data\Tasks\*.yaml` corpus contains any absent-`TaskingType` or numeric-`TaskingType` instance.** | **CLOSED — measured, negative.** Indent-aware enumeration of all **11 `.yaml` files / 95 top-level task entries**: `named=95  numeric=0  ABSENT=0`. **Every shipped task declares a named `TaskingType`. Neither the numeric nor the absence case occurs in the corpus — the capability of §2.4 is REAL but UNEXERCISED (latent, not expressed).** **[My first probe of this returned "1113 absent", which was a bad regex counting nested `Author: Name:` / `Options: Name:` lines — see §6 failure 6.]** |
| 3 | **Whether `.Wait()` is really unhandled at `Covenant.cs:121`** — §2.2 rests on it, and my first probe of the enclosing scope faulted (§6 failure 3). | Read `Covenant.cs:105-135` verbatim and confirm no enclosing `try`. |
| 4 | **Whether `GruntTaskingForm.razor`'s numeric `Type` can be tampered to out-of-range over HTTP**, bypassing the `<option>` list. §2.5 reasons from the rendered control, not from server-side binding. | Trace the tasking POST handler to `GruntTasking.Type` and check for a range guard. |
| 5 | **`Brute`'s missing usings** (§4.1) — whether `System.Security.Principal` absence alone would fail the build, or whether the `void` signature is the compiled truth. | Build `Brute.cs`; expect the missing-using errors D72's §1.5 note implies. |

### 4.1 A corroboration D72 did not have — the usings diff

**`Brute.cs` L1-12 vs `GruntHTTP.cs` L1-14, enumerated:**

```
Brute.cs:      L11 System.Security.Cryptography      L12 System.Text.RegularExpressions
GruntHTTP.cs:  L11 System.Security.Principal         L12 System.Security.AccessControl
               L13 System.Security.Cryptography      L14 System.Text.RegularExpressions
```

**`Brute` is missing EXACTLY two usings, and they are exactly the two its defect requires: `System.Security.Principal` (for `WindowsIdentity`/`WindowsImpersonationContext`) and `System.Security.AccessControl` (for pipe security).** **`Brute` can therefore not even NAME the types its siblings use to consume the token — which is a second, independent confirmation of D72 §1.4's verdict that the assemblies are not self-contained and the host must apply the token.** **And `Brute.cs` references `WindowsIdentity` 0 times (§6, verified).**

---

## 5. Consolidated answers

| Task | Answer |
|---|---|
| **T1 — instance or class?** | **INSTANCE.** The `TaskExecute` population is **closed at 4 definitions / 8 call sites**. The token branch consumes the return in **3** families (`GruntHTTP:188`, `GruntSMB:182`, `GruntBridge:182`) and **discards it in exactly 1 (`Brute:168`)**. The false-positive shape — **a success message composed from a local `output` string, emitted unconditionally as `Completed`, while the gating value is dropped** — occurs **once**. **Clean answer: `Brute` only. This NARROWS D60's blast radius to one family and CONFIRMS §1.3 rather than generalising it.** |
| **T2 — does the UI reach the loader?** | **NO — NON-VECTOR, three independent reasons.** (1) **`GruntTaskForm.razor` binds `TaskingType` ZERO times** — no such control exists. (2) The one numeric-emitting form (`GruntTaskingForm.razor:51-59`, `.ToString("d")`) feeds **tasking dispatch**, not the definition loader. (3) The loader reads **a directory of YAML on disk** at startup. **An out-of-range numeric `TaskingType` requires filesystem write, not UI access.** |
| **T2 — is the exception caught?** | **NO. `InitializeTasks` (`L164-416`, 253 lines) contains ZERO `try`/`catch`/`finally`, and `DbInitializer.cs` contains zero `try` in all 509 lines.** `Covenant.cs:121` calls `.Wait()`. **R-67.3's `YamlException` terminates startup.** **This closes R-67.3's own named next probe.** |
| **T2 — the case R-67.3 missed** | **ABSENCE.** `SerializedGruntTask.TaskingType` (`Models\Grunts\GruntTask.cs:413`) has an initializer `= GruntTaskingType.Assembly`. **An omitted key silently becomes `Assembly` — the exact value that routes to `TaskExecute`. YamlDotNet is never consulted; the default is in the C# model.** |

---

## 6. Instrument failures, this report

| # | Failure | Caught by | Effect |
|---:|---|---|---|
| 1 | **Assumed `SerializedGruntTask` was declared in `GruntTaskComponents.cs`** (a name that sounds like a container for it) and probed that file, which matched nothing | a probe returning **zero** for a class I had just asserted exists | **none — enumerated all 152 `.cs` and found it at `Models\Grunts\GruntTask.cs:403`, whose `:413` default is the load-bearing fact of T2 §2.4.** **This is shape 15 again, and this time the enumeration was what produced the answer — not just what caught the error.** |
| 2 | **A brace-walk anchored on the CALL `InitializeTasks(service, context)` at `L32` instead of the DEFINITION at `L164`**, so the span swept to EOF (509 lines) | the span length being obviously absurd for the method | **none — but the `try/catch` enumeration inside that bogus span returned EMPTY, which I nearly read as evidence.** Re-anchored on `(private\|public)\s+(async\s+)?(static\s+)?Task\s+InitializeTasks\(` and re-verified with a segment count. **An instrument that answers the wrong question confidently is the D60 §6.1 class.** |
| 3 | **Walked backwards from the deserialize to the nearest `try` and matched a comment in the license header at `L1`**, reporting "nearest preceding try at L0" | the reported line number being `0` | **none — the true answer is zero `try` in the whole file, so the bogus anchor did not change the conclusion.** Verified by whole-file count. |
| 4 | **`ForEach-Object` with `$_.Name` interpolated inside a quoted string in an outer loop** — `Unexpected token`, `Missing closing )`, `string is missing the terminator`, **exit 1** | PowerShell's own parser, loudly | **none — rewrote with explicit variables (`$nm = $f.Name`).** **Kept because this is D60 §6.1's exact species: a quoting defect in command construction. This time it CRASHED rather than emitting plausible output, which is the failure mode worth having.** |
| 5 | **A `write` call missing its `content` property** | schema rejection | **none — resubmitted.** |
| 6 | **The absence probe reported "1113 entries WITHOUT `TaskingType`" out of 1,208 — a figure I recognised as impossible from having read the YAMLs in D72** | **pattern-matching the number against prior first-hand reading; a YAML file whose 5 tasks all declare `TaskingType` cannot have 1,113 tasks lacking it** | **none — but this is the worst near-miss of the round.** My regex `^\s*-\s*Name:` matched **nested** entries (`Author:`'s `Name:`, `Options[].Name:`) and counted each as a task. **Indent-aware re-measure: 95 entries, `named=95 · numeric=0 · ABSENT=0`.** **Had I written the 1,113, it would have claimed the shipped corpus is full of malformed tasks — the opposite of the truth.** |
| 7 | **D80's own first draft said `Covenant.cs:121` had "no `try` there either"** | **verifying my own written claim as a second pass** | **A `try` DOES exist at `:98-105` — but it scopes to `IPAddress.Parse` / `catch (FormatException)` and closes at `:105`.** `:121` sits in the `using` at `:109-151`, outside it; the next `try` opens at `:165` around `host.Run()`. **Conclusion unchanged, phrasing corrected to name both `try` statements and their exact spans (§2.2).** |

### 6.1 The new species the Lead asked to be named

**Failure 6 from D72, restated here for the record because the Lead asked that it be preserved as a named instrument species:**

> **A line-oriented regex silently undercounts calls that wrap across lines, and the number it produces looks entirely reasonable.**

**The D72 instance: `Select-String -Pattern '\.Replace\(".*REPLACE_'` over `CovenantService.cs` returned 17 for the HTTP block and I transposed it to 18/10/10.** **The true counts are 18/10/12.** The regex required the placeholder and the `.Replace(` on one line; where a call wrapped, the match was silently lost and the count came back **one lower than truth** — a number with no smell on it.

**Why it belongs in the taxonomy: it is not a crash and not an implausible value. It is an UNDERCOUNT that is off by a small integer, which is indistinguishable from a correct count by inspection.** **The only defence that worked was recomputing as a second method and treating the mismatch as a defect in either direction.** **Failure 1 of this report is the same family one level up — a probe that returns zero, where zero is also a legitimate answer.**

---

## 7. Corrections to file with the Lead

1. **D72 §3.3's "malformed input is rejected" is RETRACTED** (§3). The verdict holds; the reasoning was too broad. **The corrected claim does not depend on YamlDotNet at all.**
2. **The brief's T1 framing — "task families whose `TaskExecute` return is discarded" — cannot produce the right answer as stated**, because **all four families discard in the `else` branch.** The discriminator is the **`message.Token` branch**, which is per-message, not per-family (§1.3).
3. **R-67.3's named next probe is CLOSED: the exception is NOT caught.** Zero `try` in `DbInitializer.cs`; `.Wait()` at `Covenant.cs:121`. **Its three unexpected results are startup-terminating hard failures.**
4. **R-67.3 has a missing fourth case: ABSENCE** (§2.4). It is the case a human actually produces by typo-ing a key name, and it is silent.

---

*End of D80. Pure source; no provider, no build, no execution. Every path list enumerated before being touched (§0). Two instrument-failure species named, including the undercount class the Lead asked to be recorded. One D72 retraction, one brief-framing correction, one residual closed, one missing test case added.*
