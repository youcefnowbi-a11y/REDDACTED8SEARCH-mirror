# Instrument Rule 20 — "a named path is not a census"

**Promoted from lesson to required practice, round 21.** Nominated by `havoc-deep` after the
thirteenth recurrence, with a count that makes it a defect class rather than an anecdote.

## The rule

> **A path you can name is not a population you have counted. Enumerate the call sites of the
> primitive — not the paths you already know about.**

## The evidence: three consecutive dives, every one toward a false clean

| # | report | what was named | what the census found |
|---|---|---|---|
| 1 | D65 | the outbound key set | under-scoped |
| 2 | D65 | followed `:5373` | missed `handlers.go:193` |
| 3 | D71 | "the" writer to the pivot handle | a second writer family, same binary |

**Every instance failed in the same direction: toward a clean result.** That is what makes it a
class. A probe that can only err by finding *less* is a probe that manufactures confidence.

## Why it belongs beside the other shapes rather than inside one

- **Not shape 15** (a path constructed from a name instead of an enumeration) — though 15 is its
  nearest relative. Shape 15 is about *constructing* a path. This is about **stopping at the
  first path you find and treating it as the set.**
- **Not shape 13** (no word boundary → reports ambient vocabulary) — that over-reports.
  This **under-reports**, and is therefore harder to notice: the wrong answer looks like a
  smaller, tidier, more confident answer.
- **It is the census variant of D-3/D-7.** The boundary is unstated, so the count reads as
  complete.

## Required mitigation

Any claim of the form *"the writer is X"*, *"only Y reaches Z"*, *"the set is N"* must be
preceded by an enumeration of the **primitive's call sites** and must print that enumeration
beside the claim. If the enumeration is infeasible, **say so and state the bound** — an
acknowledged limit is worth more than an unacknowledged one.

## The worked example, from D76 itself

The primitive was `PipeWrite`. Enumerating its callers tree-wide gave **6 hits / 3 live call
sites**, which surfaced a second writer family in the same binary that the known path had hidden.
**The enumeration is what produced the finding — and then the bound retired it.** Both outcomes
required the census. Without it the lane would have had a confident non-answer either way.

*Worked example and nomination: `havoc-deep`, D76 §6 Failure 1.*
