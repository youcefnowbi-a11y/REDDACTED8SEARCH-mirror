# RULE 39 — PRESENT IS NOT DOMINATES, AND THE SINK IS NOT THE SWITCH

**Author:** Lead
**Date:** Round 9c
**Scope:** Every "guard exists" claim in the corpus, and every switch-classification claim
**Status:** Applies to all future lanes. Retracts nothing already shipped; it re-reads it.

---

## §0 — The two rules

> **RULE 39a.** A GUARD'S EXISTENCE AND A GUARD'S DOMINANCE ARE DIFFERENT CLAIMS, AND
> ONLY DOMINANCE IS A SECURITY PROPERTY. The test is not *"is there a nil check"* but
> *"is every dereference inside the block that the check guards."*

> **RULE 39b.** A SWITCH THAT LACKS A `default:` IS A CODE-SHAPE FACT. WHETHER ITS
> FAIL-THROUGH REACHES A SINK IS A CONSEQUENCE, AND THE CONSEQUENCE IS WHAT MATTERS.
> Classify the ARM by what it selects; classify the DEFECT by what the unarmed path
> *reaches*.

Both rules were produced by two lanes in the same round, independently, on two
codebases in two languages. That is the evidence for stating them as rules rather
than as findings.

---

## §1 — Rule 39a: the havoc instance, measured

`D161` (havoc-deep), `R-147.1`. Source `demons.go`.

**The guard is present.** `if DemonInfo != nil` at `:5265`. D89 and D147 both
recorded it and both were correct that it is there.

**The guard dominates nothing.** Six uses of `DemonInfo` precede it. Two are
unambiguous nil-dereferences:

| line | use | guarded? |
|---|---|---|
| `:5254` | `.Pivots.Parent` | **NO** — before the guard |
| `:5259` | `.Info.MagicValue` | **NO** — before the guard |
| `:5265` | guard `if DemonInfo != nil` | — |
| `:5268` | `else` writes *"failed to parse the agent"* | after both arms |

The guard sits **outside** the `if`/`else` that closes at `:5263`. It runs *after*
both arms and therefore covers *neither*. Its branch body contains two map writes
and a string build — **every dereference it could have protected is outside it and
before it.**

**The mechanism is nameable, not merely locatable.** It is a *message-selection*
check. The `else` at `:5268` writes *"Failed to connect: failed to parse the agent"*
— **precisely the nil case it is twelve lines too late to handle.** The author knew
the parse could fail. **Right shape, wrong position.**

### §1.1 — What converts adjacency into structure

An observation about line distance is not a defect claim: a guard *can* legitimately
sit after a call if nothing dereferences the result before it. What makes this a
defect is a **controlled comparison on the identical call.**

`ParseDemonRegisterRequest` has four returns, three of them `nil`. It has three callers:

| caller | guard offset | block contains the derefs? | verdict |
|---|---|---|---|
| `handlers.go:273` | **+1 line** | yes — early return dominates all | **CORRECT** |
| `agent.go:568` | **+1 line** | yes — block encloses all six | **CORRECT** |
| `demons.go:5253` | **+12 lines** | **no** | **DEFECT** |

> **DISTANCE IS A SYMPTOM; CONTAINMENT IS THE PROPERTY.**
> **A single defective site proves a defect exists; two correct ones prove it IS one.**

Two correct call sites on the same function, handling the same three-nil-return
contract, establish that the difference is **positional and not a property of the
callee.** Without them, the finding is that this code looks suspicious.

---

## §2 — Rule 39b: the Covenant instance, measured

`D160` (covenant-diver), `R-158.1`. Source `Covenant\Core\CovenantService.cs`.

**The code-shape fact, and it is D158's number, not a new one.** Of the switches
D158 could not see, **eleven** lack a `default:`. All eleven: brace-matched,
`default:`=0, `throw`=0, `return`=0, `continue`=0. Every fail-path is a silent
fall-through. **That is a census, and on its own it is not a security claim.**

**The consequence, and it is one sentence.** Of the eleven, **ten fail through
harmlessly or visibly, and ONE — `CovenantService.cs:3456` — fails through into
durable storage, from two unvalidated entry points, with no caller anywhere in the
tree that guards it.**

### §2.1 — The sink, verified on the bytes

| line | content | guarded? |
|---|---|---|
| `:3451` | `if (matchingIndicator == null)` | tests the **DB lookup**, not the switch expression |
| `:3455` | `matchingIndicator.Type = indicator.Type;` | **UNGUARDED WRITE** |
| `:3456` | `switch (indicator.Type)` | three cases, `:3458`/`:3468`/`:3478` |
| `:3486` | `await _context.SaveChangesAsync();` | **UNCONDITIONAL COMMIT** |
| `:3488` | `return await this.GetIndicator(indicator.Id);` | **HTTP 200 on the bad path** |

**Lead-independent census over exactly `L3455`–`L3486`: `if`=0 `throw`=0 `return`=0
`continue`=0.** Confirms D160 exactly.

### §2.2 — Why it is a sink and not a bug

The lane went **one step past the brief**, because "persisted" needed proving rather
than asserting:

- `GetIndicator(int)` at `:3393` resolves the row with `FirstOrDefaultAsync(...)` at
  `:3395`. **That returns a CHANGE-TRACKED entity.**
- So `:3455` mutates the tracked `Type` **in place**.
- The unconditional `SaveChangesAsync()` at `:3486` **flushes EF's change tracker.**
- **No arm needs to run and no `Update()` call is required.** The armed arms call
  `Update()` (`:3466`/`:3476`/`:3483`) only to mark their *subclass copies*; `Type`
  was already dirty from `:3455` alone.

**Consequence:** the out-of-domain `Type` is committed, the type-specific fields are
silently *not* copied, `:3488` re-reads the row and returns it. **The caller receives
HTTP 200 and an `Indicator`, as if the edit worked.**

### §2.3 — Containment failed, so it is API-level

The brief asked whether a second caller arms `Type` — D161's decisive move. **No such
caller exists.** Exactly two entry points, both pass the object straight through:

- `IndicatorApiController.cs:189` `[HttpPut(Name="EditIndicator")]` `EditIndicator([FromBody] Indicator)` → `:193` `_service.EditIndicator(indicator)`. The `try`/`catch` at `:191`/`:195` is **exception translation for the response** — and **a catch downstream of a call cannot guard its arguments.**
- `CovenantHub.cs:417` `EditIndicator(Indicator)` → `:419`, no validation.

**VERDICT: API-LEVEL DEFECT, NOT POSITIONAL.** Containment cannot be claimed.
*Two doors, one room, the room has no lock.*

### §2.4 — The D149 control, and what it bought

The lane named **the caller it expected to validate** — the SignalR hub, a more
trusted surface. It does not validate.

**But the codebase contains the validating idiom.** Sibling reader `GetFileIndicator`
at `:3403`–`:3409` does exactly:

```csharp
if (indicator == null || indicator.Type != IndicatorType.FileIndicator)
{
    throw new ControllerNotFoundException($"NotFound - FileIndicator with id: {indicatorId}");
}
```

**Same file, same enum, same `Type` field, fifty lines above — and omitted on the
`EditIndicator` path.** *That* is what turns "a caller did not validate" into evidence
the path *should* have. **The omission is specific, not a file-wide convention.**

**Lead verified `:3406` verbatim.**

---

## §3 — The reversal that changes the protection argument

`D160` §3, printed as its own section on the Lead's instruction.

`CredentialForm.razor:16,20` emit `value="...ToString("d")"` — **the NUMERIC form.**
`Enum.Parse<T>` **accepts a numeric string**: `Enum.Parse<CredentialType>("7")` returns
`(CredentialType)7` with **no exception**, because enum values are just integers.

**Consequence, stated exactly:**

- **D158's COUNTS REMAIN VALID.**
- **What falls is the PROTECTION ARGUMENT** that the parser would have rejected
  out-of-domain values.
- **That is why the remaining 57 may matter after all.**

And the lane did **not** overclaim: whether an attacker can deliver a numeric `Type`
**over the wire** is `OPEN` (`R-160.2`). `IndicatorType.cs` carries
`[JsonConverter(typeof(StringEnumConverter))]` with no `AllowIntegerValues` argument,
and whether that default permits `{"type":7}` **is not read.** Flagged as the
highest-value next probe rather than resolved by assumption.

---

## §4 — The meta-observation: where Rule 36 violations actually land

`D166` and `D160` each ran a Rule-36 span check on their own drafts. **Twelve spans
across two consecutive reports.** The distribution is not random:

- **`D166`'s span** sat in §7 — the paragraph **ASSERTING** the lane had avoided the defect.
- **`D160`'s span** sat in the residuals clause **LISTING WHAT IT LEFT OUT.**

> **BOTH LANDED IN THE META-SENTENCES ABOUT THE WORK RATHER THAN IN THE WORK.**

The check earns its place because **the failure mode concentrates exactly where care
is being asserted.** A claims about diligence is precisely where the unexamined
construct survives longest.

This is the same family as Rule 38 — *a control that cannot fail is not a control* —
one level up:

> **A SENTENCE THAT CLAIMS A PROPERTY IS NOT A CHECK ON THAT PROPERTY.**
> The place a check is most confidently believed to have passed is the place it is
> least likely to have been run.

---

## §5 — Rule 39, operational form

Before shipping any guard claim or switch claim, run these four questions and print
the answers:

1. **For a guard:** name the line of the guard. Name every dereference of the same
   object in the enclosing function. **For each, state whether it is inside the
   guard's block.** If any is outside, `dominates` is FALSE — regardless of the
   guard's presence.
2. **For a switch without `default:`:** name what the unarmed path **reaches**, not
   that it exists. A sink, an early return, a silent no-op and a logged warn are four
   different findings and only one of them is a defect class worth a rule.
3. **For containment:** find the *other* callers of the same callee. If two place the
   guard correctly, the defect is positional and provable. **If none do, it is
   API-level and that is the stronger finding.**
4. **For the control:** name a site you expected to behave *differently* and show what
   it does instead. `D160` named the SignalR hub expecting validation and found none —
   and then found the idiom present 50 lines above, in the same file, on the same enum.
   **That is what a control looks like when it buys something.**

---

## §6 — Instances of record

| # | target | claim as previously stated | claim under Rule 39 | evidence |
|---|---|---|---|---|
| 1 | havoc `demons.go:5265` | "the nil guard is present" (D89, D147) | **present, dominates NOTHING**; two unguarded derefs before it | D161 §1 |
| 2 | Covenant `CovenantService.cs:3456` | "11 switches lack a `default:`" (D158 scope) | **one of them reaches `SaveChangesAsync` unconditionally** | D160 §1–§2 |
| 3 | Covenant `Common.cs:25` | "the segment-aware fix already ships at L89" (D93) | **L89 does not fix L25** — different assemblies, different purpose | D166 §Q3 |
| 4 | Covenant enum switches | "the parser would have rejected out-of-domain values" | **`Enum.Parse` accepts the numeric form the UI itself emits** | D160 §3 |

**Instance 3 is a fourth member of a family already recorded:** a claim that a fix
exists elsewhere in the same file, when the two sites compute different things.
**Instance 4 is the round's cleanest example of a protection argument that survived
because nobody asked what the parser actually accepts.**

---

## §7 — Non-claims

- **`D161`'s R-147.1 stays `OPEN`**, with the missing piece named: a Go toolchain and
  an artifact. `go` is not on PATH and no execution is permitted — **the block is
  concrete, not policy-shaped.**
- **`D160`'s R-160.2 stays `OPEN`** and is the highest-value next probe.
- **`D160` explicitly did NOT touch `R-93.4`** — the two switches it read are inside
  instance methods that do not initialise `Core\Common.cs`. **No linkage claim.**
  `D166` owns that residual.
- **No runtime reachability is claimed anywhere in this document.** Every statement is
  about code as written. Whether an attacker can deliver the triggering value over the
  wire is open at `R-160.2` and was not assumed.
- **The Lead verified `D160`'s guard census and `D166`'s absence census independently.**
  The Lead did not re-derive `D161`'s byte-level idiom table; it is cited from the lane.

---

## §8 — One line

> **Presence is a fact about the file. Dominance is a fact about the flow. And the
> switch is not the sink — the unarmed path's destination is the sink, and only the
> destination decides whether anyone should care.**
