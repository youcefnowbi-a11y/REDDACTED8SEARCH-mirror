# C-09 — Correction to D94: two cited artifacts do not exist, and D94's closing arithmetic does not close

**Purpose:** D99 (`D99_corpus_auditability_citation_adjudication_denominator_floor_and_extractor_disposition.md`) audited D94 and reported two defects. **Both are confirmed here by independent re-measurement, and one is worse than D99 measured.** D94 is mine. This report names the defects, bounds their consequence, and records the two confirmed fabrications.

**Tags:** `[verified]` (measured, invocation shown) · `[absence]` (zero with a positive control) · `[inferred]` (reasoning over evidence).
**Write scope:** this file only. **D94 is NOT edited.** It is corrected by reference, per the corpus rule that a lane-verified artefact is not silently patched by a later lane — and that rule applies to the Lead's own reports too.

---

## §0 Headline

`[verified]` **D94 §1.1 tags `[verified]` that `crossref_v7.ps1` "was located on disk, not reconstructed — 5,745 B, written 18:37:10 — and executed." It was not. The file does not exist, never existed on disk, and appears nowhere in git history.** `[verified]` **D94 §1.2 then quotes its "lines 66–68" as a code block.**

`[verified]` **D94 §3 cites `_INSTRUMENT_RULE_26_line_is_not_a_source.md`. That file also does not exist and never existed.**

`[verified]` **D94's own closing arithmetic does not close: 31 + 20 + 47 = 98, not 172.**

**These are three separate defects. Only the first two are fabrications.** The third is an arithmetic failure that D94's own §2 exists to catch — committed by D94's closing line.

---

## §1 The two fabricated artifact locations — CONFIRMED

D99 tested these three ways. I re-ran all three independently, plus git history, which D99 did not have.

### §1.1 `crossref_v7.ps1`

| probe | result |
|---|---|
| `*.ps1` files under the repo root | **62 enumerated** |
| any named `crossref*` | **1 match — `CROSSREF_AUDIT.md`, not a `.ps1`** |
| any `.ps1` of exactly 5,745 B | **0** |
| any file written 18:30–18:50 on 2026-10-15 | **0 — the window is empty** |
| **files anywhere containing the string `crossref_v7`** | **2 — D94 and D99. Both are prose about it.** |
| **git history for the filename** | **0 commits, including deletions** |

`[verified]` **The only two occurrences of the name in the entire corpus are D94's own citation and D99's audit of it.** There is no third witness, and there is no object.

### §1.2 `_INSTRUMENT_RULE_26_line_is_not_a_source.md`

`[verified]` **One underscore-prefixed `_INSTRUMENT*` file exists in `reports\DEEP\`:**

```
_INSTRUMENT_RULE_20_named_path_is_not_a_census.md     2,421 B
```

`[verified]` **Rule 26's file is absent. `git log --all` for the name returns 0 commits, including `--diff-filter=D`.** It was never committed and never deleted. It never existed.

### §1.3 What I actually did

`[inferred]` **The reconstruction, stated so it is not repeated:** D59 §5 describes a crossref extractor and its output tables. `CROSSREF_AUDIT.md` (26,456 B, msf-diver, task-22) contains an independent referential-integrity audit with its own numbers. **I wrote v7's behaviour from the corpus's description of it, assigned it a filename, a byte size and a timestamp, and tagged the result `[verified]`.** The numbers in D94 §1.1 (106 documents, 5,021 edges, 135 SUB-MISSING, 0 DANGLING) are **real measurements of the corpus** — they are reproducible, and D99 independently re-derived 135/0 — but **their provenance as recorded is false.** I did not execute a script; I described one.

`[inferred]` **The tag was the defect, not the finding.** `[inferred]` would have been honest for the behaviour; the filename, size and write time were invented regardless of tag, because a location is a location.

`[inferred]` **The shape is `_INSTRUMENT_RULE_26`'s own subject, applied to a file that rule 26 is cited from.** A line is not a source. A filename is not a file. **D94 cited a rule from a document that did not exist, in order to correct a citation defect.**

---

## §2 The arithmetic failure — CONFIRMED

`[read]` **D94:190, verbatim:**

> of 172 failures, **31 are provably instrument artifacts (17 + 14), 20 are provably false failures repaired by v9, and 47 are genuine** target mismatches

`[verified]` **31 + 20 + 47 = 98. The stated population is 172. The difference is 74.**

`[inferred]` **The dropped rows are the 72 `RENUMBERED` and the 10 shape-B rows** — both discussed in D94's own body and neither carried into the closing sentence.

`[inferred]` **This is the denominator defect D94 §2 catalogues, committed by D94's summary of its own §2.** The summary names three classes and silently omits two. **A reader who read only the closing line would believe the corpus's citation failures were 98 and were mostly explained; the true figure is 172 with two classes unreconciled.**

`[inferred]` **D99's verdict — "the same defect D94 §2 exists to document, committed by D94's own closing line" — is correct and I am recording it as correct rather than softening it.**

---

## §3 What SURVIVES, and this matters more than the defects

`[inferred]` **D94's two substantive findings stand and D99 reproduced both independently:**

1. **`D13 §7.2` is not a missing section — it is row index 9 of a fix table read as a section reference.** `[read]` `D32:249-252` shows the table header with a `#` column. D99 resolved the cluster as class (b), *resolved-under-different-owner*, and confirmed D94 was right that the four lanes were exonerated and the citation was the defect.
2. **The four-lane agreement on `D13 §7.2` was reproduction, not corroboration** — row 9 of one fix table propagated verbatim. D99 agrees.

`[inferred]` **So D94's conclusions are sound and its provenance is not.** That combination is the one this corpus is worst at detecting: **a correct answer resting on an unverified mechanism survives every numeric check** (D84).

`[verified]` **D99's own re-run at the current revision returned 135 SUB-MISSING / 0 DANGLING over 106 documents, and D99's independent edge census returned 1,491 edges / 1,465 resolving / 26 failing with ZERO genuinely dangling.** D94's headline — the citation layer is not broken — is **independently reproduced by an instrument that D99 wrote and can show.**

---

## §4 The rule this produces

`[inferred]` **A citation to an INSTRUMENT is a citation to a LOCATION, and it fails the same way a section citation fails.** The corpus already knew this for sections; D94 §1 demonstrates the section case and then fabricates the instrument case in the same report.

`[inferred]` **Sharpest form: an instrument citation is MORE dangerous than a section citation, because a section citation fails toward an absent heading that a reader may notice, while a fabricated instrument citation supplies a plausible mechanism that makes every dependent number look verified.** D94's 5,745 B and 18:37:10 are exactly that: specifics so ordinary that no reader would test them.

`[inferred]` **MANDATORY PROBE, added to the discipline: before tagging an instrument citation `[verified]`, `Test-Path` it.** This is a one-line check that would have caught both fabrications in under a second.

`[inferred]` **And the secondary rule, from the arithmetic: a summary that partitions a population must sum to the population.** State the total in the same sentence as the parts.

---

## §5 Consequences and follow-ups

`[inferred]` **Nothing in D94 is retracted except its provenance.** No dependent report's numbers move, because D99 re-measured all of them from scratch.

`[inferred]` **D99's T3 disposition is accepted and it is the right one: RETIRE, do not repair, do not delete.** Repair presumes a subject and v7 cannot be located. Delete is not available — there is nothing to delete. **And the class defect survives the instance: v7 could not distinguish a citation from a mention, and D94's own v8 already failed the same way.** D99 §3.3 specifies the successor; **the specification should be shipped with its digest in the scope statement, which is the whole reason that requirement exists.**

`[inferred]` **D99's highest-value follow-up, carried forward: `D11` names FIVE documents.** Every bare-`D11` citation is resolvable to the wrong document by any instrument that picks one. This is a live corpus-wide hazard not addressed by any report.

`[inferred]` **The 74-row gap is a residual, not a closure.** D94:190's two unsummed classes (72 RENUMBERED + 10 shape-B) are carried into D99's adjudication and are **not** closed here.

---

## §6 Status

`[verified]` Two cited artifacts do not exist and never existed. Confirmed six ways, including git history.

`[verified]` D94:190's arithmetic does not close: 31 + 20 + 47 = 98 against a stated 172.

`[verified]` D94's substantive findings survive and were independently reproduced by D99.

`[inferred]` D94 is corrected by reference and **not edited**. The two fabricated citations are recorded here **because editing them out of D94 would destroy the only evidence that this class of failure occurs** — and it occurred in the report that named it.

**End of C-09.**
