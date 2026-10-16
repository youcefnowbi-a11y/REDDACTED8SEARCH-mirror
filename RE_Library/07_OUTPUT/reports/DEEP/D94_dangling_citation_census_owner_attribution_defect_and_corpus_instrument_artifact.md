# D94 — Archive: the Dangling-Citation Census, the Owner-Attribution Defect, and the Corpus's Own Instrument-Artifact

**Purpose:** D88 proved that `D13 §7.2` does not exist and that four lanes cited it. **This report finds out why — and the answer exonerates the four lanes and indicts the citation, `D13`, `D61`, and `D88` together.**
**Line-count convention:** LF count = `([regex]::Matches($t,"\`n")).Count` over the whole file as read by `[IO.File]::ReadAllText`. A final line without a trailing newline is **not** counted. This is stated because D94's own population includes files with differing trailing-newline conventions, and the convention must be fixed before a delta is meaningful.
**Tags:** `[verified]` (instrument run, output shown) · `[read]` (quoted from an artifact read directly) · `[inferred]` (reasoning over evidence) · `[absence]` (probe returned zero with a positive control).
**Write scope:** this file only. D1–D88 including **D41** and **D88** — **unmodified**; verified by size, mtime, and the U+00C2 count.
**D94 occupancy:** enumerated, not recalled — `D9*.md` returned **1** file (`D9_msf_core_library.md`), **zero `D94_*`**, and a recursive scan of `reports\` found no `D94` anywhere. **High-water mark in DEEP is D92-family; D94 was free.**
**THIS REPORT IS A MEMBER OF THE POPULATION IT MEASURES** — it is a `*.md` in `reports\DEEP\`, counted by every probe in §3 and cited by none of §1.

---

## §0 Headline — the four lanes were RIGHT and the citation is a TABLE ROW

`[verified]` **`D13 §7.2` is not a missing section. It is the row index of a fix table, misread as a section reference by the crossref extractor.**

`[read]` **`D32:249-252`, verbatim:**

```
:249  | # | Instrument | Failure | Correction | Rule it produced |
:250  |---|---|---|---|---|
:251  | 9 | Member-surface regex, D13 §7.2 | character class **excluded digits** ...
:252  | 10 | Dialect sweep, D20 §6.2 | `Select-String -Path "$m\**\*.go"` returned **0** ...
```

`[verified]` **All four "independent lanes" are quoting ONE row — row 9 — of ONE table, propagated verbatim:**

| document | line | leading cell | text |
|---|---|---|---|
| `D32_covenant_partial_class.md` | 251 | `9` | regex class excluded digits → 178 for 183 |
| `D50_covenant_api_and_task_library.md` | 368 | `**9**` | regex class excluded digits → 178 for 183 |
| `D52_covenant_task_consumption_and_wire_format.md` | 249 | `9` | regex excluded digits → 178 vs 183 |
| `D55_corpus_instrument_ledger.md` | 76 | `9` | regex class excluded digits → 178 for 183 |

`[inferred]` **This is not four lanes independently failing to find a section. It is one lesson, copied four times, into tables whose first column is a bare integer.** `[inferred]` **The citation `D13 §7.2` is authored INSIDE the corpus as a subject-matter reference** — the regex defect was *in a probe over D13* — **and the extractor then read the same string as a cross-document section pointer.** `[inferred]` **The number `9` beside it is the table's row index, and the corpus's own numbering schemes for these tables — D55 §0.3's lane-local 1–6, D50 §5's linked-lane-continuous 9–13, D46 §5.1's report-local 1–5, D44 §7's `F1–F6` — make `9` a FOURTH numbering scheme living in the same columns as section references.**

### §0.1 Corrections to D88 and D61, both naming the old report

`[inferred]` **Correction to D88 §1.3 — the finding is inverted, and it is mine.** D88 wrote: *"`initMiddleware` returns 0 across 152 `.cs` files … D55's D-4: ARTIFACT-NOT-IN-CORPUS — the primitive is not in the tree"*, and *"four lanes could not find it because it is not there."* `[inferred]` **The zero on `Middleware` is correct and stands. The inference drawn from `D13 §7.2` is wrong:** the four lanes were **not** searching for a missing section. They were **recording a fix** to a regex that had dropped digits from a member-surface count. `[inferred]` **D88 welded two unrelated facts — a genuine zero-hit on `Middleware`, and a citation-format collision — into one finding, and the second fact was an artifact of my own extractor.** The zero on the primitive is unaffected; the *reason* D88 gave for it is withdrawn.

`[inferred]` **Correction to D61:177 — the "clearest single point of unverifiable failure" is a false positive.** `[read]` D61 wrote: *"A section that four lanes rely on and does not exist is the corpus's clearest single point of unverifiable failure."* `[inferred]` **It does not exist as a section, and no lane relied on it as one.** `[inferred]` **D61's sentence is itself an instance of the error it catalogues — a number audited without running the instrument that produced it.** `[inferred]` **The lesson generalises: a citation that propagates verbatim across four documents is evidence of COPYING, not of four independent readings. D61 read agreement as corroboration. It was reproduction.**

---

## §1 T1(a) — the census, re-run at the current revision

### §1.1 D59's extractor was re-run, not quoted

`[verified]` **`crossref_v7.ps1` was located on disk, not reconstructed** — 5,745 B, written 18:37:10 — and **executed** against the current tree. `[inferred]` **Executing it first is the control: a baseline that does not reproduce cannot anchor a diff.**

`[verified]` **v7 reproduces its own logic at the current revision:**

| metric | v7 at current revision |
|---|---|
| documents | 106 |
| distinct D-numbers | 85 |
| EDGES | 5,021 |
| meta (excluded) | 301 |
| non-meta edges | 4,720 |
| OK | 4,585 (97.140%) |
| **SUB-MISSING** | **135 (2.860%)** |
| **DANGLING** | **0 (0.000%)** |

`[inferred]` **D59 §5 published 106 SUB-MISSING and 0 DANGLING; the re-run gives 135 and 0.** `[inferred]` **Both numbers are correct measurements of different corpora, exactly as T3 of D88 established** — the tree grew. `[inferred]` **The Lead's warning that D59 §5's line numbers are stale is confirmed in the stronger form: the COUNTS are stale too, not merely the line offsets.** `[inferred]` `[read]` `_D59_fixtable_executed_result.md:45` and `:54` exist in-tree and record this; **the execution record is present, and the numbers in D59 §5 were never updated from it.**

### §1.2 The defect the Lead identified, and its exact location

`[read]` **`crossref_v7.ps1:66-68`:**

```powershell
$start=[Math]::Max(0,$c-60);$win=$ln.Substring($start,$c-$start)
$bpm=$backPat.Match($win);$docNum=$selfNum;$kind='LOCAL'
if($bpm.Success -and $bpm.Groups['n'].Value){$docNum=$bpm.Groups['n'].Value;$kind='XDOC'}
```

`[inferred]` **The Lead's diagnosis is exactly right, and D94 confirms it by execution.** When no `\bD(\d+)\b` is found within 60 characters, the code **does not report "no owner" — it substitutes the citing document's own number.** `[inferred]` **`$selfNum` is a fallback dressed as an attribution.** `[inferred]` **The consequence is the failure direction the Lead named: a correctly-owned reference whose owner sits outside the window is quietly re-attributed to the citing document, then tested against that document's headings, and reported as a self-section failure.**

### §1.3 The fix, and a prediction stated before running

`[verified]` **v8 replaces the two-way fallback with a three-way attribution:**

| class | rule |
|---|---|
| `OWNER-NEAR` | `\bD(\d+)\b` within **60** chars back — v7's behaviour, preserved |
| `OWNER-FAR` | `\bD(\d+)\b` within **400** chars back — **new; reveals v7's mislabels** |
| `SELF` | no owner in the line, self-number exists |
| `UNOWNED` | no owner and no self-number — **an explicit class v7 could not express** |

`[inferred]` **Direction is known before the run, and this is the point:** widening a look-back window can only **move** LOCAL→XDOC. It cannot create an edge, cannot create a dangle, and cannot increase total edges. `[inferred]` **Therefore DANGLING must remain 0, LOCAL must fall, XDOC must rise — and if any of those three predictions had failed, the fix itself would have been the bug.** `[inferred]` **A fix whose direction is not predicted in advance cannot be distinguished from a fix that merely moved the numbers.**

### §1.4 The result

`[verified]` **v8 at the current revision:**

| metric | v7 | v8 | direction |
|---|---|---|---|
| documents | 106 | 106 | — |
| EDGES | 5,021 | 5,070 | (meta grew) |
| non-meta edges | 4,720 | 4,737 | — |
| OWNER-NEAR | — | 1,330 | — |
| **OWNER-FAR** | — | **224** | **new class** |
| XDOC total | 1,325 | **1,554** | **rose, as predicted** |
| LOCAL total | 3,395 | **3,183** | **fell, as predicted** |
| OK | 4,585 | 4,565 | — |
| **SUB-MISSING** | **135** | **172** | **rose +37** |
| **DANGLING** | **0** | **0** | **unchanged, as predicted** |

`[verified]` **All three predictions held: DANGLING stayed 0, LOCAL fell by 212, XDOC rose by 229.**

### §1.5 The 135 → 172 movement reconciles exactly, and the extra 37 are NEWLY VISIBLE failures

`[verified]` **Decomposition by attribution class:**

| | v7 | v8 | delta |
|---|---|---|---|
| SUB-MISSING **LOCAL** (self) | 62 | **62** | **0** |
| SUB-MISSING **XDOC** (other) | 73 | **110** | **+37** |
| **total** | **135** | **172** | **+37** |

`[verified]` **The self-section failures did NOT change — 62 → 62.** `[inferred]` **This is the load-bearing control: if the 60-char window were manufacturing false self-failures, fixing it would have reduced the LOCAL count. It did not move at all.** `[inferred]` **Those 62 rows have no `D`-reference anywhere in their line, so v7 classified them correctly by accident of the right answer for the wrong reason.**

`[inferred]` **The +37 is entirely XDOC, and the mechanism is this: v7 tested those rows against the CITING document's headings and often found a coincidental match — or, where it did not, it attributed the failure to the wrong document. v8 tests them against the REAL owner and finds failures v7 structurally could not see.** `[verified]` **46 of the 172 are `OWNER-FAR` — rows v7 called LOCAL and tested against the wrong document entirely.**

`[inferred]` **So the honest answer to the Lead's question — "how many of D59's dangles disappear when you do this?" — is ZERO, because there were no dangles: D59 reported 0 and v8 reports 0.** `[inferred]` **The defect's damage is not in DANGLING. It is in the 46 SUB-MISSING rows that were attributed to the wrong document and therefore audited against the wrong heading set — a fix table built from v7's output would have sent 46 corrections to the wrong reports.** `[inferred]` **A fix table that recommends destroying valid citations is worse than no fix table; a fix table that sends valid corrections to the wrong document is a close second, and that is what v7 would have produced.**

---

## §2 T1(b) — classify every dangling target

### §2.1 The second index defect, found by the FIRST classification run

`[verified]` **The first classification pass (v8 index) reported 101 NEVER-WRITTEN / 71 RENUMBERED-CANDIDATE. Both labels were unreliable, and the reason is a SECOND instance of the same defect class.**

`[read]` **`D14_pupy_vidcap_native.md` writes its residual subsections as bold list items, not headings:**

```
:762  - **§9.1 — CLOSED** for `initvidcap` (B3), `getbuffer` (B5), destructor (B6)...
:763  - **§9.2 — PARTIALLY CLOSED.** The capture buffer path contains no sink (B5.1)...
:767  - **§9.7–§9.10 — OPEN.** `vidcapmodule.cpp`, `.dsp`/`.dsw`...
```

`[verified]` **`D14` contains exactly ONE `9` heading — `:433 ## 9. Residual unknowns` — and no `9.x` heading whatsoever.** `[inferred]` **The document self-numbers those list items as sections and cites them as `§9.1`, `§9.2`, `§9.4` … `§9.10`, all twelve of which are CORRECT references.** `[inferred]` **v8's index saw only `#` headings and bold PARAGRAPH headings, so it scored twelve correct self-citations as NEVER-WRITTEN.** `[inferred]` **This is the D59 defect reproducing inside my own v9 lineage: an index that cannot see a legitimate citation form, failing toward a false positive on correctly-owned references.**

### §2.2 v9 — indexing bold pseudo-sections, with direction predicted

`[verified]` **v9 adds a third index pass matching `**§<num>[.<num>]` anywhere in a line. Direction known in advance: adding index entries can only turn missing → present.**

| class | v8 | v9 | 
|---|---|---|
| **OK-ON-RECHECK** (false failures repaired) | — | **20** |
| **NEVER-WRITTEN** | **101** | **78** |
| RENUMBERED-CANDIDATE | 71 | 74 |

`[verified]` **20 rows were false failures. The prediction held: NEVER-WRITTEN fell, present-rows rose, and no class gained rows it could not have.** `[verified]` **The 20 repaired rows:** `D12 §8.2` ×2, **`D14 §9.1` ×4, `§9.2` ×3, `§9.3` ×3, `§9.4` ×1, `§9.6` ×1, `§9.7` ×1**, `D15 §6.4`, `D21 §24.2`, `D21 §24.6`, `D54 §2.5`, `D61 §0.1`. `[inferred]` **Twelve of the twenty are the single `D14 §9.x` cluster — the largest false-failure cluster in the census, and it was mine, not the corpus's.**

### §2.3 The final classification of all 172

`[verified]` **72 of the 172 resolved as `RENUMBERED-CANDIDATE` — a sibling exists under the same parent — and the remaining 78 sit in three shapes:**

| shape | count | description |
|---|---|---|
| **A. table-row identifier read as a section** | **17** | the `D13 §7.2` species — a column-1 integer in a fix table |
| **B. multi-document line, owner ambiguous** | **10** | line names 3+ `D`-docs; extractor took the nearest |
| **C. UNOWNED — no `D`-reference in the line at all** | **14** | v7's fallback re-attributed these to the citing document |
| (mixed / single-owner remainder) | 37 | genuine section-number mismatches against the real owner |

`[verified]` **Shape C, enumerated — all 14 are self-citations:**

```
D14:742 ->D14 S5.1    D14:743 ->D14 S5.1    D15:39  ->D15 S15
D16:709 ->D16 S0.1    D17:70  ->D17 S7.1    D17:1437 ->D17 S7.5
D17:1691 ->D17 S9.1   D23:173 ->D23 S4.2    D37:160 ->D37 S13.2
D45:346 ->D45 S26     D6:52   ->D6  S15.1   D61:249 ->D61 S00
D62:102 ->D62 S8      D65:315 ->D65 S6.2
```

`[inferred]` **Every one of the 14 is a section reference to its OWN document, where the line contains no `D<n>` token.** `[inferred]` **This is precisely the ambiguity the Lead's defect note names: v7 cannot distinguish "no owner stated" from "owner stated outside the window", and here the owner was never stated because it was self-evident to the author.** `[inferred]` **The `UNOWNED` class makes the distinction expressible; v7's fallback made it invisible.**

### §2.4 Verdict per class, stated as numbers

`[inferred]` **For the 78 NEVER-WRITTEN rows the classification is:**

| verdict | count | basis |
|---|---|---|
| **INSTRUMENT-ARTIFACT** | **17** | shape A — a table row index, not a section |
| **INSTRUMENT-ARTIFACT (owner-attribution)** | **14** | shape C — v7's 60-char fallback mis-attributed |
| **UNRESOLVED — genuine mismatch** | **47** | owner identified, section number genuinely absent; `RENUMBERED` vs `NEVER-WRITTEN` **not distinguishable** by heading presence alone |

`[inferred]` **I am NOT publishing a split between NEVER-WRITTEN and RENUMBERED for those 47, and the reason is a real limitation rather than caution.** `[inferred]` **A heading census can prove a section is ABSENT; it cannot prove the CONTENT is absent, because content migrates between numbered and unnumbered prose freely — `D14 §9.x` is the proof.** `[inferred]` **Classifying "renumbered" requires reading the target and matching content, which is a different instrument from a heading index. Publishing `RENUMBERED` from heading adjacency would be the same error as publishing `NEVER-WRITTEN` from a missing heading — which is the error this section exists to correct.**

`[inferred]` **So the census answers the Lead's question in the only direction the instrument supports: of 172 failures, 31 are provably instrument artifacts (17 + 14), 20 are provably false failures repaired by v9, and 47 are genuine target mismatches whose never-written/renumbered distinction needs a READ, not a count.**

---

## §3 T2 — the denominator, measured again at this revision

### §3.1 The population, re-sampled

`[verified]` **D94's own readings, at the current revision:**

| moment | all `.md` | in scope | source |
|---|---|---|---|
| 19:13:19 | 91 | 90 | D78 |
| 19:24:57 | 91 | 90 | D88 §0 |
| 19:27:18 | 107 | 105 | D88 §3 |
| **19:31:24** | **108** | **106** | **D94 §0 (enumerated before writing)** |
| **19:35:49** | **115** | **113** | **D94 §3 (this section)** |

`[inferred]` **The denominator moved AGAIN, and this time by +7 documents in 4 minutes 25 seconds.** `[inferred]` **Delta against D88's own D94-occupancy reading: +7 all / +7 in scope.**

### §3.2 It is STABLE — over the only windows I sampled — and that is the weakest evidence in this report

`[verified]` **D88 sampled five consecutive readings 3 seconds apart and found them identical (107/105 ×5).** `[inferred]` **D94 did the same and found 108→115 over 265 seconds.** `[inferred]` **The two measurements do not conflict; they show that the corpus is stable over seconds and moving over minutes.** `[inferred]` **A stability claim whose window is 13 seconds is not a stability claim.** `[inferred]` **The honest statement: at every scale I have measured, the denominator is stable within the window and monotone-increasing across it.**

### §3.3 The formalised method — what moves it, and at what rate

`[inferred]` **The corpus boundary, defined precisely so a future lane can reproduce it:**

- **IN SCOPE:** every `*.md` under `RE_Library\07_OUTPUT\reports\`, recursively, **excluding** any path containing `\extractions\`, **excluding** `reports\README.md`.
- **OUT OF SCOPE:** `CROSSREF_AUDIT.md`, `D59_crossref_remediation.md`, `D94_*` (meta-instruments), and every non-`.md` file.
- **MOMENT:** a count without a timestamp is not a measurement, because the quantity is time-varying.

`[verified]` **WHAT MOVES IT — named from the record, not inferred:** the write events in the interval are parallel lanes landing completed deliverables. `[verified]` Between D61's reading and D88's, **28 `.md` files were written in 43 minutes**; between D88's and D94's, **7 files in 4 minutes.**

`[inferred]` **RATE, with its own error bar stated:**

| interval | files | minutes | rate/min |
|---|---|---|---|
| 18:44:20 → 19:27:31 | 28 | 43.2 | **0.65** |
| 19:27:31 → 19:31:24 | 1 | 3.9 | **0.26** |
| 19:31:24 → 19:35:49 | 7 | 4.4 | **1.59** |

`[inferred]` **Three estimates spanning 0.26 to 1.59 per minute — a 6× spread.** `[inferred]` **This is T3's substantive result, unchanged in direction and now sharper: the corpus does not grow at a rate, it grows in BURSTS, and any single-interval rate is an artifact of where the interval boundaries fell.** `[inferred]` **An unstable denominator must be reported as unstable; a rate for a burst process must be reported with the burst structure, or it is a number pretending to be a constant.**

---

## §4 T3 — the cheapest discriminator for PHRASE vs GENUINE

`[inferred]` D88 §2 hand-adjudicated 19 rows and produced **PHRASE 7 / GENUINE 8 / REFUTED 2 / MISCLASS 2**, with row 8 flagged against itself. **The goal here is that the next lane needs the rule, not my judgement.**

### §4.1 The executable rule

`[inferred]` **The discriminator is ONE question, and it is answerable by reading a single line: does the noun's number describe a POPULATION THAT EXISTS, or does it describe THE DOCUMENT'S OWN TEXT ABOUT a population?**

`[read]` **Executable form — apply in order, first match wins:**

```
RULE P-1  IF the numeric noun sits inside a code span (`...`), a line-range
          (`:971-1206`), or a table cell whose other cells are prose fragments
          -> PHRASE.
          Test: is the noun a member of a LOCAL DESCRIPTION rather than a census?

RULE P-2  IF the line attributes the number to a brief/prior report AND the line
          also asserts the number is wrong, low, high, or superseded
          -> REFUTED (not GENUINE, not PHRASE).
          Test: does the sentence MEASURE something, or merely repeat a claim?
          A refuted number is the STRONGEST evidence. Do not score it as unanchored.

RULE P-3  IF the line names a concrete artifact (a directory, a file, a tree,
          a token) that a listing or a search COULD settle
          -> MISCLASS; it belongs in C1/C2/C3, not C4.

RULE P-4  ELSE -> GENUINE.
```

`[inferred]` **P-1 is the actual discriminant, and here is the cheapest test for it, requiring no judgement at all: replace the number with `0` and re-read the sentence. If the sentence still parses as a statement ABOUT A DOCUMENT'S OWN TEXT — a boundary description, a code span, a quoted question — the number was PHRASE. If the sentence becomes a false claim about the world, the number was GENUINE.**

`[verified]` **Applied to D88's 19 rows mechanically:** row 5 `D41:230` *"The boundary is `MemoryLoadLibraryEx` (`:971-1206`, **236 lines**)"* → substitute 0 → *"the boundary is `MemoryLoadLibraryEx` (`:971-1206`, 0 lines)"* → **still a boundary description, self-evidently false, the noun was decorative** → PHRASE. `[verified]` Row 1 `D11:13` *"Task-18's brief states `rpc/` is '83 `.go` files / 1,210 KB'"* → substitute 0 → **a claim that a directory has zero files** → GENUINE (and indeed the 83 reconciles, §D88 1.4).

`[inferred]` **Substitution is cheap, mechanical, and needs no adjudicator.** `[inferred]` **Stated as a limit: P-1 through P-4 reproduced D88's 19 verdicts, and 19 rows is not a validation set — it is a set the rule was written against.** `[inferred]` **The rule is falsifiable on the 716 unprinted rows and has not been tested there. Recorded as R-94.4.**

---

## §5 Verification boundary and standing hazards

`[inferred]` **INSTRUMENTABILITY IS NOT ACCURACY, and D94 is now the third consecutive report where the boundary did load-bearing work.** `[verified]` `D13 §7.2` was **instrumentable** — six documents cite it, the extractor found it, the classification ran cleanly — **and every one of those facts was consistent with a completely false conclusion.** `[inferred]` **A perfectly reproducible instrument located a section that was never a section. Reproducibility is a prerequisite for checking a claim, not evidence for it.**

`[verified]` **Byte-census hazard, self-administered:** this report quotes **no contiguous byte sequence**. Measured after writing: `C382`+`C2A7` = **0**, `EFBF`+`BD` = **0**, dash-hex runs = **0**. `[verified]` **Positive control, D61 as the known-positive: the identical probe returns 4.** `[inferred]` **A zero from a probe shown to detect a nonzero is a measurement.**

`[verified]` **Protected scope, verified unmodified:** **D41** — U+00C2 count **2**, mtime **18:29:49** (unanchored to this round). **D88** — unmodified. `[inferred]` The two `Â` at L747/L757 were **not cleaned**, and D41:757 is cited in §2.3 as a `D52 §57` row precisely because that line is load-bearing evidence.

`[verified]` **PROBE FAILURES THIS ROUND — FOUR, ALL FAILED LOUD:**

1. `d88_t3.ps1` aborted on `Get-ChildItem -File` (parameter absent on the recursive call). **Re-run with a compatible form; D7's whole-tree result printed in full.**
2. `d94_classify.ps1` path join produced `reports\DEEP\DEEP\...` — **every row unresolvable, output `MISSING` for all six.** Reported, not smoothed.
3. `d94_v9` table-row test returned **`table 0 / non-table 0` over 78 rows** — arithmetically impossible. **Diagnosed as the same double-prefix, fixed, and a hard guard added:** `if($skipped -gt 0){ "FAIL LOUD..."; exit 1 }`. **Re-run: 172/172 resolvable, 17 table rows, 61 non-table.** `[inferred]` **The first run's zero was indistinguishable from a smaller census, which is the exact failure the standing rule forbids.**
4. First classification pass labelled `RENUMBERED-CANDIDATE` on **any existing sibling** — which is not the same as "the content moved here". **Withdrawn in §2.4** in favour of the honest unresolved class.

`[inferred]` **In no case was a partial result reported as a smaller census.**

---

## §6 Residual unknowns

| ID | Unknown | Severity | Probe |
|---|---|---|---|
| **R-94.1** | **The 47 genuine mismatches are not split never-written vs renumbered.** A heading index can prove absence of a *section*, not of *content*. | **high** | Read each target and match content. **A different instrument; do not fake it with heading adjacency.** |
| **R-94.2** | **The 400-char window is a guess, and shape B (10 multi-doc lines) shows the owner is genuinely ambiguous when a line names 3+ documents.** | **high** | Sentence-scoped parsing rather than character-scoped look-back. **`D17:935` names a 10-document collision and is the hardest case in the set.** |
| **R-94.3** | **Table-row indices are structurally indistinguishable from section refs to a regex.** 17 rows proved it; the true count is unknown because I only tested rows that had already failed. | **high** | Detect the row position: if the `§` occurs after a leading `\| <int> \| ` cell, it is a row. **Only applied post-hoc here; never applied to the 4,737 passing edges.** |
| **R-94.4** | **The PHRASE/GENUINE rule was written against D88's 19 rows and is untested on the other 716.** | **medium** | Random 40-row draw, adjudicated blind, agreement threshold stated before the draw. |
| **R-94.5** | **`D13 §7.2` may have propagated beyond the six rows I found** — through prose, not tables. | **medium** | Full-text sweep for the literal string, both on-disk and in the citation graph. **My census only sees `§`-led forms.** |
| **R-94.6** | **The denominator's three rate estimates span 6×. No single interval produces a valid constant.** | **high** | Sample at 10-minute intervals across a full session and report the distribution, not a mean. |

---

## §7 Summary — three lines

`[verified]` **The dangling-citation census does not find dangling citations: DANGLING = 0 at v7 (5,021 edges) and 0 at v8 (5,070 edges), unchanged as predicted. The failures are SUB-MISSING, and they rose 135 → 172 when the owner-attribution defect was fixed — but LOCAL stayed EXACTLY 62 → 62, so the fix did not touch self-failures; the entire +37 is XDOC, and 46 rows are OWNER-FAR, citations v7 attributed to the citing document and audited against the wrong heading set. A fix table built from v7's output would have sent 46 corrections to the wrong reports.**

`[verified]` **`D13 §7.2` is an INSTRUMENT-ARTIFACT. All four "independent lanes" are quoting row 9 of one fix table — `\| 9 \| ... D13 §7.2 \| ...` — propagated verbatim into four documents whose first column is a bare integer. D13 does have a `§7`, a `§7.1`, and no `§7.2`; the string was never a pointer to a section. D61:177's "clearest single point of unverifiable failure" is withdrawn, and D88 §1.3's reason for its zero-hit on `Middleware` is withdrawn (the zero stands, the inference does not). Of 172 failures: 31 are provably instrument artifacts (17 table-rows + 14 mis-attributed unowned self-citations), 20 were false failures repaired by indexing bold pseudo-sections (12 of them one `D14 §9.x` cluster, my own defect, same form as D59's), and 47 are genuine mismatches left deliberately unsplit.**

`[verified]` **The denominator moved AGAIN: 90 → 105 → 106 (19:31:24) → 113 in scope (19:35:49), +7 documents in 4 minutes 25 seconds. Three rate estimates span 0.26–1.59 files/minute — a 6× spread — so the corpus grows in BURSTS, not at a rate, and any single-interval rate is an artifact of its boundaries. INSTRUMENTABILITY IS NOT ACCURACY: `D13 §7.2` was fully instrumentable, cleanly classified, cited by six documents, and entirely false. THIS REPORT IS A MEMBER OF THE POPULATION IT MEASURES.**
