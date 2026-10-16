# D59 §5.1 — the fix table, executed

**Lead, round 22.** Four of five rows applied. One refused, and the refusal is the finding.

`D59` §5.1's table was written as `[inference]` and deliberately left unexecuted — *"If the fix
table is correct the Lead executes it; if you edit 60 reports directly, no one can verify what
changed."* That reasoning holds, and this is the execution.

## What was applied

Every old string was **re-verified against the live file** before any edit, and each was required
to occur **exactly once** — an ambiguous match was to be skipped, not guessed.

| # | file:line (D59) | old | new | status |
|---|---|---|---|---|
| 2 | `D11_mythic_crypto_postresponse.md:371` | `D6 §22.6, §25.3` | `D6 §22.6, D6 §25.3` | **APPLIED** |
| 3 | `D3_android_code.md:374` | `mutual exclusion (§23.3)` | `mutual exclusion (D6 §23.3)` | **APPLIED** |
| 4 | `D3_android_code.md:574` | `Pupy §23.3` | `Pupy D6 §23.3` | **APPLIED** |
| 6 | `D8_msf_exploit_side.md:562` | `§11.3-§11.4` | `D7 §11.3-§11.4` | **APPLIED** |
| 1 | `D1_sliver_implant_code.md:3195` | `§25` | *delete the reference* | **REFUSED** |

**Diff: 3 files, 1 line each, 3 insertions, 3 deletions.** Nothing else moved.

### Every repaired referent was checked to exist

An edit that repoints a reference at a section that does not exist is worse than the ambiguity it
replaced. Each target was verified by enumerating the destination document's headings:

- `D6 §25.3` exists — `### 25.3 Verdict`
- `D6 §23.3` exists — `### 23.3 The mutual exclusion — and it answers the task's pointer directly`
- `D7 §11.3` exists — `### 11.3 bind_aws_ssm.rb — C2 inside AWS Systems Manager API calls`
- `D7 §11.4` exists — `### 11.4 bind_aws_instance_connect.rb — C2 inside EC2 Instance Connect`

**Row 4's destination matters:** the sentence at `D8:562` already opened with `D7 §11.2`, so the
bare `§11.3-§11.4` beside it was a mode-`LOCAL`/mode-`XDOC` ambiguity, not a missing target. It now
reads `D7 §11.2 … ; D7 §11.3-§11.4 …` and both halves resolve to D7.

## Row 1 — REFUSED, and the reason is that the row is wrong

**The line number had moved.** D59 placed the defect at `D1_sliver_implant_code.md:3195`. That line
now reads *"corrupted envelope fails closed at the signature check and never reaches the AEAD"* —
nothing to do with `§25`. D59's own §6 warned that the corpus moved during its audit; it moved here.

**Enumerating rather than assuming found `§25` at four other lines** — `3274`, `3284`, `3285`,
`3289` — every one of them a reference to **D6 §25**, not D1 §25.

**And D6 §25 exists.** `## 25. Is the severance pattern Windows-only? — Linux Makefile and
pupy_load.c`, with `### 25.1` through `### 25.4`. So `D1 L3274`'s table column header
`| Property | Sliver | Pupy (D6 §17–§25) |` is **correct as written** — it names D6's section range,
and D6 has a §25. `D1 L3284` even labels itself *"REFINEMENT (added after D6 §25 landed — see
§24.4)"*, and `L3289` cites *"D6 §25.3 is the authoritative scope statement"* — which resolves to
`### 25.3 Verdict`.

**D59's row 1 would have deleted a valid citation.** It inferred that a bare `§25` implied *D1* was
believed to have a §25, and asked for the reference to be deleted with a note that *"§25 does not
exist; D1 ends at §24."* **D1's real last section is indeed §24.3** — D59 was right about that — but
the reference was never to D1. **A reference's owner cannot be inferred from its bare number.**

### The corpus had already caught this class, and D59 did not use it

**`D6` §26.2 is titled *"BROKEN CROSS-REFERENCE in D1 — flagged, not silently patched."*** The
corpus had already identified a cross-reference defect in D1 and made the correct call: **flag it,
do not silently patch it.** D59's §5.1 row 1 proposed exactly the silent patch that D6 §26.2
declines.

**Bound on this refusal, stated:** I have shown that `D6 §25` exists and that the four surviving
`§25` references in D1 resolve to it. I have **not** exhaustively enumerated every bare `§`-number
in D1 to confirm no genuinely-dangling sibling exists elsewhere. **Row 1 is refused on the evidence
that its stated instance is a false positive; that is not a claim that D1 has no dangling
references at all.**

## Instrument failure, logged

**Shape 8 — a declaration is not necessarily written in the form in which it is referenced.**
D59's extractor classified a reference by scanning for a nearby `\bD(\d+)\b`; when none was found
within its window it fell back to `LOCAL`, attributing the reference to the citing document. **That
fallback cannot distinguish "no owner stated" from "owner stated outside the window."** The header
`Pupy (D6 §17–§25)` carries its owner *earlier in the same line*, outside a 60-character
look-back — so a correctly-owned reference was classified as local and then reported as dangling.

**This is the same family as Rule 20.** A census of the paths the extractor knew about returned a
population that excluded the one it was looking for. **And it failed toward a false positive** —
toward recommending a destructive edit — which is the more dangerous direction for a fix table.

## What remains from D59 §5

- **§5.2, the self-section cluster** — three edits claimed to close 39 references (37% of all
  failures) by promoting existing bold text into `### n.m` headings. **Not executed here.** The
  claim that the sub-headings already exist as bold text is `[read]` by D59 but I have not verified
  it, and a heading promotion is a structural edit to a lane-verified artefact — it needs the same
  verification this table did not get.
- **§5.3/§5.4, the Mode A prefix-drops** — D59 states *"the invocation is the table"* and gives
  `§0.2` as the reproducible generator. Not executed; the generator needs a re-run at the **current**
  corpus revision, since §5.1's line numbers are already stale.

*End of D59 execution result.*
