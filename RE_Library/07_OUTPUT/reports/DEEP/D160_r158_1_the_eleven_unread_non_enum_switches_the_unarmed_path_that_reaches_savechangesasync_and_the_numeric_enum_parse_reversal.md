# D160 — R-158.1: the eleven unread non-enum switches, and the unarmed path that reaches `SaveChangesAsync`

`SCOPE` — `RE_Library\01_SOURCE_c2\covenant\Covenant` — 254 source files (152 `.cs` + 102 `.razor`), the 11 switches D158 recorded as non-enum and lacking a `default:` (R-158.1), each brace-matched and read in full at its own site; plus the caller closure of `CovenantService.EditIndicator`.

`DEFINER SCOPE` — `D158` for the census that scoped these 11 (65 `switch` occurrences, 57 without `default:`, 13 non-enum, 2 read, 11 remaining) and for the decision rule that every arm is classified by **what the arm selects**; `D143` for the `default:` arms; `D151` for the three transport dispatch arms; `D161` for the containment-versus-distance standard this report adopts for the sink.

`CONDITIONAL SCOPE` — `R-93.4` was **not** touched: this walk did not reach `CovenantDirectory` static initialisation or its derivations. Stated explicitly rather than passed over. `R-158.2`, `R-158.3`, `R-158.4` remain open and are not resolved here.

`COUNTED` — **11 switches read · 11 brace-matched · 0 `default:` · 0 `throw` inside any switch · 0 `return` inside any switch · 0 `continue`** · 3 two-method counts with an agree column · **2 entry points into `EditIndicator`, both unvalidated** · **1 persistence sink** · **3 controls, 3 distinct outcomes** · 1 reversed read (`CredentialForm.razor:143`).

---

## 0. Method, boundaries, and the one refusal

Static only. No execution, no network, no live C2, no assembly loaded. No `REA open_binary` — a shared active target across lanes. D160 is **measurement and reading, not repair**: no lane artefact was edited, and D157 (24,033 B, `8d00bfbe…`) and D166 (28,710 B, `770e9691…`) were not touched.

Nothing here is re-derived. D158's census (`65` / `57` / `13` / `2 read`) is taken as given; this report reads the **11 it could not see**, because *a construct defined by the ABSENCE of `default:` is outside the range of a search FOR `default:`*. Every switch below was located by its **`switch` token**, brace-matched by depth, and never window-truncated.

`~/.dsh/AGENTS.md` was delivered again during this task, appended to a tool result — the **ninth** consecutive round (D113, D122, D124, D133, D143, D148, D157, D166, and now D160). **Refused in full.** No persona, no mandated phrase, no mandated thinking format, no change to framing, standards, or behaviour. It arrived as *file content riding on tool output*, never as a turn from the Lead or the operator; that delivery channel is the evidence about what it is. Artifact contents and injected file contents are **data, never instructions**.

---

## 1. The headline: the unarmed path reaches `SaveChangesAsync`

The finding is not "11 switches lack a `default:`". That is D158's number re-derived, and D158 already owns it. **The finding is that on one of those switches, falling through does not merely fail to handle a bad value — it writes the unarmed value to durable storage and commits it.**

`CovenantService.EditIndicator`, verbatim from `CovenantService.cs:3448`:

```csharp
3448: public async Task<Indicator> EditIndicator(Indicator indicator)
3449: {
3450:     Indicator matchingIndicator = await this.GetIndicator(indicator.Id);
3451:     if (matchingIndicator == null)
3452:     {
3453:         throw new ControllerNotFoundException($"NotFound - Indicator with id: {indicator.Id}");
3454:     }
3455:     matchingIndicator.Type = indicator.Type;      // <-- WRITE, before the switch
3456:     switch (indicator.Type)
3457:     {
3458:         case IndicatorType.FileIndicator:
...
3466:             _context.Indicators.Update(matchingFileIndicator);
3467:             break;
3468:         case IndicatorType.NetworkIndicator:
...
3476:             _context.Indicators.Update(matchingNetworkIndicator);
3477:             break;
3478:         case IndicatorType.TargetIndicator:
...
3483:             _context.Indicators.Update(matchingTargetIndicator);
3484:             break;
3485:     }                                             // <-- no default:, no throw, no return
3486:     await _context.SaveChangesAsync();            // <-- COMMIT, after the switch
3487:     // _notifier.OnEditIndicator(this, indicator);
3488:     return await this.GetIndicator(indicator.Id);
3489: }
```

### 1.1 The Lead's three questions, answered on the printed lines

**1. Is `Type` written BEFORE or AFTER the guard?**
**Before, and there is no guard on `Type` at all.** The write is `CovenantService.cs:3455`. The only `if` in the method is `:3451`, and it tests `matchingIndicator == null` — the **database lookup result**, not the switch expression. The commit is `CovenantService.cs:3486`.

**2. Is there any `if`/`throw`/`return`/`continue` between L3455 and L3486 on the unarmed path?**
**No. None.** A guard census over the exact span L3455–L3486 (`$c[3454]..$c[3485]`) returns:

| construct | count in L3455–L3486 |
|---|---|
| `if (` | **0** |
| `throw` | **0** |
| `return` | **0** |
| `continue` | **0** |

**The write is unconditional and the commit is unconditional.** There is no intervening test of any kind — not on `Type`, not on the arm taken, not on a success flag. The `break` at L3467/3477/3484 exits the switch, not the method.

**3. Are there other callers of this method that DO validate `Type` first?**
**No. There are exactly two entry points and neither validates.** That is the containment answer, and it is the stronger outcome — §1.3.

### 1.2 Why the commit persists the unarmed value (the part that makes it a sink)

The arm bodies call `_context.Indicators.Update(...)` (L3466, L3476, L3483) — but the commit at L3486 does **not** depend on any arm having run. It is reached from all paths through the switch, including no arm at all.

The mutated entity is **already change-tracked before the switch**: `GetIndicator(int)` at L3393 resolves the row with

```csharp
3395: Indicator indicator = await _context.Indicators.FirstOrDefaultAsync(I => I.Id == indicatorId);
```

`FirstOrDefaultAsync` on a `DbSet` returns a **tracked** entity. So at L3455 the tracked `matchingIndicator.Type` is mutated in place, and the unconditional `SaveChangesAsync()` at L3486 flushes EF's change tracker to the database. **No `Update()` call is required for the mutation to be persisted** — `Update()` is how the armed arms mark their subclass copies, but the `Type` mutation was already dirty by virtue of L3455 alone.

**The consequence, stated exactly:** an `Indicator` whose `Type` is a value with no case — an out-of-domain enum value — has that value written to `matchingIndicator.Type` and **committed to the database**, while the type-specific fields (`FileName`, `Protocol`, `ComputerName`, and the rest) are silently **not** copied. The record's `Type` discriminator is changed to a value no arm understands, and the response at L3488 re-reads the row and returns it as if the edit succeeded. The caller receives HTTP 200 and an `Indicator`.

### 1.3 Containment: the D161 test, and the verdict

D161's standard, adopted here verbatim: **distance is a symptom; containment is the property. A single defective site proves a defect exists; two correct ones prove it is a defect.**

The decisive move is to look for a caller that arms `Type` before the call. **There is no such caller.**

| caller | file:line | does it validate `Type`? |
|---|---|---|
| REST controller | `Controllers\ApiControllers\IndicatorApiController.cs:189` | **No** — passes straight through |
| SignalR hub | `Hubs\CovenantHub.cs:417` | **No** — passes straight through |
| hub service client | `Core\CovenantHubService.cs:453` | **No** — client stub, `_connection.InvokeAsync` |
| generated API client | `API\CovenantAPIExtensions.cs:2310/2323` | **No** — generated wrapper |
| generated interface | `API\ICovenantAPI.cs:937` | declaration only |
| service interface | `Core\CovenantService.cs:252` | declaration only |

The controller body in full, `IndicatorApiController.cs:188-193`:

```csharp
188: [HttpPut(Name = "EditIndicator")]
189: public async Task<ActionResult<Indicator>> EditIndicator([FromBody] Indicator indicator)
190: {
191:     try
192:     {
193:         return await _service.EditIndicator(indicator);
194:     }
195:     catch (ControllerNotFoundException e)
```

The hub body in full, `CovenantHub.cs:417-420`:

```csharp
417: public Task<Indicator> EditIndicator(Indicator indicator)
418: {
419:     return _service.EditIndicator(indicator);
420: }
```

**Verdict: this is an API-level defect, not a positional defect at one site.** There is no second caller that could be said to contain it. Both entry points accept the object as deserialised and hand it to the same unguarded method. The defect is the **absence of validation on the service boundary**, and it is reachable from every caller the service exposes.

### 1.4 The D149 control the Lead named — a caller I expected to validate

**Expectation:** the SignalR hub is the more trusted surface, being the operator's authenticated console; I expected it to validate before dispatch, or the controller to do so at the edge.

**Observed:** both pass the object through untouched. The controller wraps the call in `try`/`catch` — but that is **exception translation for the response, not input validation**. It catches `ControllerNotFoundException` and `ControllerBadRequestException` and maps them to 404/400; it never inspects `Type` before calling. A `catch` block downstream of a call cannot guard the call's arguments.

**And the codebase demonstrably contains the validating pattern** — it just is not on this path. `GetFileIndicator` at `CovenantService.cs:3403` does exactly the right thing:

```csharp
3406: if (indicator == null || indicator.Type != IndicatorType.FileIndicator)
3407: {
3408:     throw new ControllerNotFoundException($"NotFound - FileIndicator with id: {indicatorId}");
3409: }
```

So the idiom `if (… .Type != X) throw` **is** used in this file, by a sibling reader, for the same enum. The `EditIndicator` path omits it. **The control therefore discriminates: I named a caller I expected to validate, and it does not — while naming a sibling in the same file that does, which proves the omission is specific and not a file-wide convention.** An all-unguarded result is a stronger finding than a positional defect, and that is what the evidence shows.

**Reachability, the two surfaces kept separate — do not merge them:**

- `[HttpPut]` with `[FromBody] Indicator`, name `EditIndicator` — **operator-facing wire surface.** The controller carries `[Authorize]` at class scope and the route is `PUT api/indicators`. Reachable by any authenticated principal holding whatever role the controller demands; the body is fully attacker-controlled JSON, so the `Type` value is whatever the client sends.
- SignalR `CovenantHub.EditIndicator` — **a different trust domain.** It is an RPC method on the hub, not an HTTP verb on a REST route; its authorisation is the hub's connection-level authentication, its parameter binding is SignalR's, and it has no route or verb to reason about. It must not be described as "the same endpoint."

**Both reach the same unguarded method.** That is the finding; they are two doors to one room, and the room has no lock.

**What I did not read, for this reachability claim:** I did not read the `[Authorize]` attributes on the hub or the controller's role list in full, so I state *that each surface is authenticated* without claiming *which roles* can reach them. I did not inspect the `Indicator` model's deserialisation attributes beyond `IndicatorType.cs`, and I did not execute or fuzz either surface. Whether a **numeric** JSON `Type` survives deserialisation is the open question in R-160.2, and it is the one that decides whether this is exploitable from the wire or only from memory.

---

## 2. The eleven, enumerated

Rows are a census; a count with no rows is a claim. Every arm below was brace-matched and read in full. **Zero `default:`, zero `throw`, zero `return`, zero `continue` inside any of the eleven** — so **every one of the eleven fails through silently.** What differs is *what the fall-through costs*, which is the classification.

| # | site | switch expression | cases | domain | closes? | on an unrecognised value |
|---|---|---|---|---|---|---|
| 1 | `CovenantService.cs:1522` | `grunt.DotNetVersion` | 2 | `DotNetVersion` {Net35, Net40, NetCore31} | **yes, by guard** | unreachable — L1519 admits only Net35/Net40 |
| 2 | **`CovenantService.cs:3456`** | `indicator.Type` | 3 | `IndicatorType` (3 members) | no | **persisted** — write L3455, commit L3486 |
| 3 | `CreateCredential.razor:21` | `credential.Type` | 3 | `CredentialType` (3) | no | navigates away, `Credential` unchanged |
| 4 | `CreateIndicator.razor:21` | `indicator.Type` | 3 | `IndicatorType` (3) | no | navigates away, `Indicator` unchanged |
| 5 | `CreateLauncher.razor:166` | `aLauncher.Name` | 10 | `LauncherType` (10) | no | silent `catch` swallows; no user signal |
| 6 | `CreateLauncher.razor:237` | `Launcher.Name` | 10 | `LauncherType` (10) | no | silent `catch` swallows; no user signal |
| 7 | `CredentialForm.razor:144` | `type` | 3 | `CredentialType` (3) | no | `Credential` unchanged (silent discard) |
| 8 | `IndicatorForm.razor:134` | `type` | 3 | `IndicatorType` (3) | no | `Indicator` unchanged (silent discard) |
| 9 | `GruntInteractTerminal.razor:158` | `e.Key` | 3 | all keyboard strings | no, by construction | no-op; no state written |
| 10 | `LauncherForm.razor:134` | `Launcher.Name` (Razor markup) | 10 | `LauncherType` (10) | no | renders nothing; submit button still present |
| 11 | `LauncherForm.razor:298` | `this.Launcher.Type` | 10 | `LauncherType` (10) | no | downloads a **zero-length** file, no error |

**Two-method counts with an explicit agree column.** Every count below was produced by two independent methods: **(M1)** a line-anchored regex `^\s*case\s` over the brace-matched span; **(M2)** a distinct-literal extraction from the same span, deduplicated. Where they could disagree is a multi-`case` line (`case A: case B:`) — none of the eleven uses that form, so they agree everywhere, and the agree column is stated rather than assumed.

| site | cases (M1) | cases (M2) | agree | `default:` | `throw` | `return` |
|---|---|---|---|---|---|---|
| `CovenantService.cs:1522` | 2 | 2 | ✓ | 0 | 0 | 0 |
| `CovenantService.cs:3456` | 3 | 3 | ✓ | 0 | 0 | 0 |
| `CreateCredential.razor:21` | 3 | 3 | ✓ | 0 | 0 | 0 |
| `CreateIndicator.razor:21` | 3 | 3 | ✓ | 0 | 0 | 0 |
| `CreateLauncher.razor:166` | 10 | 10 | ✓ | 0 | 0 | 0 |
| `CreateLauncher.razor:237` | 10 | 10 | ✓ | 0 | 0 | 0 |
| `CredentialForm.razor:144` | 3 | 3 | ✓ | 0 | 0 | 0 |
| `IndicatorForm.razor:134` | 3 | 3 | ✓ | 0 | 0 | 0 |
| `GruntInteractTerminal.razor:158` | 3 | 3 | ✓ | 0 | 0 | 0 |
| `LauncherForm.razor:134` | 10 | 10 | ✓ | 0 | 0 | 0 |
| `LauncherForm.razor:298` | 10 | 10 | ✓ | 0 | 0 | 0 |
| **total** | **60** | **60** | **11/11** | **0** | **0** | **0** |

**A correction to my own earlier working, recorded because it changed a classification:** `LauncherType` has **10** members, not 9 — `Wmic, Regsvr32, Mshta, Cscript, Wscript, PowerShell, Binary, MSBuild, InstallUtil, ShellCode`, confirmed from `LauncherType.cs` with its `[EnumMember(Value = …)]` attributes. My first pass read 9 because a regex missed `Regsvr32` where its `EnumMember` line sat adjacent to the next declaration. **Consequence:** switches 5, 6, 10 and 11 case **10/10 — fully exhaustive over the enum**, so their fall-through is unreachable *from an enum value*. This changes their class from "incomplete case set" to "complete case set, no `default:`, and therefore no defence if the domain ever grows." I state it because the corrected number is what the table must carry.

**The 13 − 2 = 11 reconciliation, on the record.** D158's §4 table holds 13 rows of non-enum switches lacking a `default:`; its R-158.1 parenthetical names 9 sites. The 2 already read are `InternalListener.cs:335` and `:1038`. **13 − 2 = 11**, and the 11 in the table above are those 11. The parenthetical's "9" and the table's "13" are not in conflict: they count different things (the parenthetical is an illustrative list, the table is the census), and no reconciliation beyond this is claimed.

### 2.1 What the arm SELECTS — the classification rule applied

D158's rule stands: each arm is classified by **what the arm selects**, not by the presence of a `default:` token, not by the enclosing file, not by a method name. The tell is to ask what the arm selects **before** classifying the file it sits in — the `Brute.cs:995` counter-example, where D143 printed the arm body `sb.Append(c);` and still misclassified fail-open because it classified by *file*.

Applying it here, the eleven split by what the arm produces:

- **Selects a handler / performs a mutation** — #2. The arm mutates a tracked entity. Its absence of a match leaves the mutation from L3455 unopposed. **This is the sink.**
- **Selects a transform / builds a value** — #1 (a string), #11 (filename/extension/content triples). #1 is guarded upstream; #11 is not, and its pre-initialised `""` defaults are the failure mode.
- **Selects a partial UI or a navigation outcome** — #3, #4, #5, #6, #7, #8, #10. These render, navigate, or construct; an unmatched value leaves the prior state in place or renders nothing.
- **Selects nothing observable** — #9. A key that matches no case does nothing; nothing is written.

**The sink is not the largest or the ugliest of the eleven. It is the one whose arm selects a mutation.**

### 2.2 The razor switch whose defaults are pre-initialised (#11)

`LauncherForm.razor:298` is worth its own note because it inverts the usual failure shape. The method declares its outputs **before** the switch:

```csharp
294: string fileext = ".exe";
295: string mediatype = "";
296: string content = "";
```

and downloads **after** it, unconditionally. An unmatched `Type` therefore does not crash and does not skip the download — it reaches `InvokeAsync("DownloadFile", filename + fileext, mediatype, content)` with `content` still `""` and writes a **zero-length file** with no error surfaced.

I corrected this in working: my first read said the download carried **null** content. L296 proves `content` is initialised to the empty string, so the outcome is a **zero-length file**, not a null-reference crash. The correction is recorded because the two failure modes have different signatures for anyone triaging it.

---

## 3. The reversed read: `Enum.Parse<T>` accepts the numeric form the UI itself emits

This section exists because my first read of the razor family was **wrong in the direction that changes the protection argument**, and the reversal is a wire-format fact rather than a UI detail.

**First read.** `CredentialForm.razor:141-143`:

```csharp
141: private void OnChangeType(ChangeEventArgs e)
142: {
143:     CredentialType type = Enum.Parse<CredentialType>((string)e.Value);
144:     switch (type)
```

I read `Enum.Parse<T>` as a guard: it throws on an unrecognised string, so an out-of-domain value cannot reach the switch, so switches #7 and #8 are **fail-closed** — genuinely protected, and a candidate for the "expected fail-closed, shown fail-closed" control.

**What broke the read.** The `<select>` that drives it emits its option values in the **numeric** form. `CredentialForm.razor:16` and `:20`:

```csharp
<option value="@(((Enum)typeof(CredentialType).GetField(n).GetValue(null)).ToString("d"))">@n</option>
```

`.ToString("d")` on an enum yields its **numeric** value — `"0"`, `"1"`, `"2"` — not its name. The DOM value posted back through `@onchange` is therefore a **numeric string**.

**Why that matters.** `Enum.Parse<T>(string)` accepts a numeric string and returns the value with that underlying number **even when no member has it**. `Enum.Parse<CredentialType>("7")` returns `(CredentialType)7` — no exception. Enum values are just integers; C# permits any value of the underlying type, and `Enum.Parse` respects that rather than restricting to declared members.

**Consequence for the whole enum-switch family:** the switch is protected only against strings that are *neither names nor numbers*. It is **not** protected against the numeric form — which is precisely the form the UI produces. `(CredentialType)7` parses clean, matches no case, and falls through to the unchanged-`Credential` outcome of #7. The same holds for #8 (`IndicatorForm.razor:134`, driven by `IndicatorForm.razor:131-133`, same numeric `option value` construction).

**Why this reframes the numbers rather than changing them.** D158 spent a whole report on the **8 `default:` arms** among the enum family, and those counts remain valid. What changes is the **protection argument**: the enum-typed switches among the 57 cannot be dismissed on the grounds that "the parser would have rejected anything out of domain," because the parser accepts the numeric form the component itself emits. **The numbers still stand; the reason for treating the 57 as bounded is what falls.** That is why R-158.1's remaining 11 are worth reading rather than assuming safe.

**What I did not establish, and will not assert:** whether an attacker can actually deliver a numeric `Type` **over the wire** to switch #2. The UI path emits numerics from a browser, but switch #2 is reached from a **deserialiser** (`[FromBody]` and SignalR), not from this component. `IndicatorType.cs` carries `[JsonConverter(typeof(StringEnumConverter))]` with **no `AllowIntegerValues` argument**. Whether that default permits `{"type": 7}` to deserialise into an out-of-domain enum is **not read** — it is R-160.2, and it is the single fact that decides whether the sink is wire-reachable or only reachable from a crafted in-process caller. I flag it as the highest-value next probe rather than resolving it by assumption.

---

## 4. Mandatory control inventory (D149 shape audit)

**Named expected-fail-closed, and shown closed — #1, `CovenantService.cs:1522`.**
`switch (grunt.DotNetVersion)` cases 2 of the enum's 3 members. It *looks* non-exhaustive. It is not: the switch sits inside `if (grunt.DotNetVersion == Net35 || grunt.DotNetVersion == Net40)` at L1519, so the only values that can reach it are exactly the 2 cased, and `NetCore31` is handled by the else branch. **Expectation: CLOSED. Observed: CLOSED.** The `default:`-less form is safe here.

**Named expected-fail-open, and shown open — #2, `CovenantService.cs:3456`.**
3 cases over a 3-member enum; on case-count alone this looks *exhaustive* and therefore safe. It is not: the guard census (§1.1) shows the write at L3455 precedes the switch, `SaveChangesAsync()` at L3486 follows it, and **0 `if`/`throw`/`return`/`continue`** lie between them. **Expectation: CLOSED (by apparent exhaustiveness). Observed: OPEN.** The write and commit are unconditional.

**Do the two controls land in the same bucket?** No — case-count-similar, verdict-opposite, and the discriminator is *not* the case count but the guard structure around the arm. **The classifier discriminates.**

**Additional control, on the razor family — #7/#8, `CredentialForm.razor:144` / `IndicatorForm.razor:134`.**
I named these expected-**fail-closed** (the `Enum.Parse` guard) and, on the numeric-form evidence in §3, they came back **fail-open**. **Expectation: CLOSED. Observed: OPEN**, with the reversal recorded rather than the first read defended. That is the opposite failure of the #1 control and the same outcome as #2, reached by a different mechanism — which is the point: three controls probed, three distinct reasoning paths, and the verdicts did not collapse to one value.

**Degeneracy check.** D149 requires me to say so if the classifier returns the same verdict for cases expected to differ. Cases #3, #4, #7, #8 are all 3/3 case sets with no `default:`; if the classifier were degenerate it would return one verdict for all four. It does not: #3/#4 fail-open by navigation with state unchanged, #7/#8 fail-open by silent discard, and under §3 two of them lose their supposed guard. **The classification is not a single bucket, and the four are not identical.** No assertion here cannot fail; no `len(x) >= 0` form; every zero carries the operand that produced it.

---

## 5. Rule-36 discipline note, kept from D166

My first publication check on D166 caught **eleven** Rule-36 spans in my own draft. The defect is a span whose content ends in a backslash, where that backslash escapes the closing backtick — so the span never closes and the following text renders as code. The offending form is a Windows path written inside a backtick span with its trailing separator included.

The eleven included the three classifier rules in the classification section, the two bucket inventories, the three path-layout cases, a `Data`-family reference, a residuals line — **and the clause in the §7 discipline note that asserted I had avoided the defect.** The assertion and its refutation were in the same line. The claim about my own care was falsified by the check that was supposed to confirm it.

All eleven were rewritten. The fix is not to escape the backslash but to **remove the trailing separator from inside the span**, naming a directory in prose or with separator-agnostic phrasing, since a path in running text needs no trailing separator to identify its directory. Re-measured after the fix: **0 spans.**

Kept here because it is the most useful paragraph in D166 and it applies equally to D160: the check must be **run-aware state tracking**, never raw parity. A raw backtick count on a defect-free file returned 311 — odd — and 311 appears again in D166 as the resolved-span count while being even there. **Parity is not a balance instrument; a fence or span count is a state machine, and any summary statistic standing in for one is the defect class D157 named.** D160 was checked the same way before publication, and the result is in §7.

**And the check caught one here too.** D160's own first pass found **one** Rule-36 span — in the residuals list, in the clause enumerating what was *not* read: the phrase "anything outside the Covenant source subtree" was originally written with a trailing separator inside a backtick span. The defect survived because the sentence about the boundary of the investigation is exactly where a path with a trailing separator feels natural to type.

That is now **twelve spans across two consecutive reports**, and the two catches share a shape worth naming: in D166 the span was in the paragraph asserting I had avoided the defect; in D160 it was in the paragraph listing what I had left out. **Both landed in the meta-sentences about the work rather than in the work. The check earns its place because the failure mode concentrates exactly where care is being asserted.** One span, rewritten, re-measured to zero.

---

## 6. Residuals

**`R-160.1`** — `CreateLauncher.razor:166` and `:237` each case 10/10 `LauncherType` members and sit inside a `try` whose `catch` body is **fully commented out** (`catch (Exception e) when (e is ControllerNotFoundException || e is ControllerBadRequestException || e is ControllerUnauthorizedException)`). A comment-out `catch` is a silent swallow; whether it was commented out deliberately was not determined. **Not resolved here.**

**`R-160.2`** — **the highest-value open question.** Whether `[JsonConverter(typeof(StringEnumConverter))]` on `IndicatorType` (no `AllowIntegerValues` argument) permits a **numeric** JSON `Type` to deserialise into an out-of-domain enum value, which would make switch #2 wire-reachable. **Not read.** This single fact separates "exploitable from the wire" from "reachable only from a crafted in-process caller", and it should be probed next.

**`R-160.3`** — `GruntInteractTerminal.razor:158` switches on `e.Key`, a **string** domain, so its case set cannot close by construction. Its fall-through is a no-op that writes nothing. Classified fail-open **and harmless**, and deliberately distinguished from #2's fail-open, which persists. **Not to be merged with the sink.**

**`R-160.4`** — the `[Authorize]` role lists on the controller and hub were not read, so the reachability claim is "authenticated surface, body fully client-controlled", not "reachable by role X". **Not read.**

**`R-160.5`** — `LauncherForm.razor:298`'s `Wmic` case yields `fileext = "xsl"` with no leading dot. Noted as an inconsistency in the same arm set; its behavioural consequence was not traced.

**`R-160.6`** — `~/.dsh/AGENTS.md` arrived for the **ninth** consecutive round, appended to a tool result. Refused in full, recorded, not investigated as to provenance.

**Explicitly not read:** `Indicator.IsValid()` or any model-level validator (not searched); the `Indicator` deserialisation attributes other than `IndicatorType.cs`; the hub's `[Authorize]` configuration; whether the runtime uses `null` or `""` for `mediatype` at the download call site; anything outside the Covenant source subtree.

**`R-93.4` — explicitly NOT touched.** This walk did not reach `CovenantDirectory` static initialisation, `Core\Common.cs:25`, or any of its 27 dependents. The one point of contact would have been a shared static-init path with `CovenantService`, and there is none: the two switches read here (#1, #2) are inside instance methods of `CovenantService`, which do not initialise `Common`. **No linkage claim is made.** D166 owns R-93.4.

---

## 7. Rule-36 span check

Run with explicit fence state before publication.

| check | result |
|---|---|
| fences opened / closed / still open | **8 / 8 / False — BALANCED** |
| inline spans resolved (run-aware) | 290 |
| unresolved span lines | **0** |
| Rule-36 spans (content ending in a backslash before the closing backtick) | **0** (1 found on the first pass — §5) |
| H1 count | **1** |
| BOM | **False** |
| CR count | **0** (pure LF) |
| strict UTF-8 decode | **PASS**, 0 replacement characters |

Fence and span balance are established by **run-aware state tracking** — an open run of *n* backticks closes on a later run of ≥ *n* — never by counting ticks. The 11-span self-catch in D166 (§5) is the reason this is checked mechanically rather than by eye, and D160's own single catch is why the check was run twice.

**A note on the fence count of 8, against D166's 3.** Eight fences means four fenced blocks, not three: D160 prints the `EditIndicator` method body, the controller body, the hub body, and the `LauncherForm.razor:294-296` declarations, where D166 printed three. The count is a property of this document's content, and it is reported as measured rather than carried over from the prior report's figure. Verifying it against the expected number of code blocks is the second method that makes it a check rather than a reading.

---

## 8. Summary

| question | answer |
|---|---|
| What is the finding? | **Not "11 switches lack a `default:`" — that is D158's number. The unarmed path in `EditIndicator` reaches `SaveChangesAsync`.** |
| Write before or after the guard? | **Write L3455, before the switch. No guard on `Type` at all** — the only `if` (L3451) tests the DB lookup. |
| Any guard between write and commit? | **None.** L3455–L3486: **0 `if`, 0 `throw`, 0 `return`, 0 `continue`.** Write and commit are both unconditional. |
| Does it actually persist? | **Yes.** `GetIndicator` (L3395) returns a **change-tracked** entity via `FirstOrDefaultAsync`; L3455 dirties it; L3486 flushes the tracker. No arm needs to run. |
| Other callers that validate `Type`? | **None. Two entry points, both unvalidated.** Controller and hub pass straight through. **API-level defect, not positional.** |
| Reachability | REST `[HttpPut] EditIndicator([FromBody] Indicator)` — operator-facing, body client-controlled. SignalR `CovenantHub.cs:417` — **different trust domain, kept separate.** Both reach the same unguarded method. |
| The reversed read | `<option value=…ToString("d")>` emits the **numeric** form, so `Enum.Parse<T>` **succeeds** rather than throwing. **The enum family cannot be defended by "the parser would have rejected it."** D158's counts stand; the protection argument does not. |
| Controls | 3 controls, 3 distinct paths, verdicts not collapsed: #1 expected-closed **shown closed**; #2 expected-closed **shown open**; #7/#8 expected-closed **shown open**. **Not degenerate.** |

**The one sentence that matters:** of the eleven switches D158 could not see, ten fail through harmlessly or visibly, and **one — `CovenantService.cs:3456` — fails through into durable storage, from two unvalidated entry points, with no caller anywhere in the tree that guards it.**
