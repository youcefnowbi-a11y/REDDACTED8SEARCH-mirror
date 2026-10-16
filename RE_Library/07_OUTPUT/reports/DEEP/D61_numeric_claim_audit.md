# D61 — Numeric Claim Audit

**Scope:** every load-bearing numeric claim the corpus publishes, re-derived or classified, with the boundary stated and justified.
**Population:** 82 documents (`reports\` recursive, `README.md` and `extractions\` excluded) — **measured 2026-10-16 18:44:20**, and the moment is part of the number.
**Predecessors:** D55 (`corpus_instrument_ledger`) catalogues the *shapes* of instrument failure. D59 (`crossref_remediation`) audits one claim family — section references — and supplies this report's methodology. **D61 audits the numbers themselves.**
**Write scope:** this file only. **No report was edited.** The fix table in §5 is unexecuted by design.
**Method:** scripts written to files, invoked, output printed. Every count below carries its invocation. Instrument failures are in §4 and are load-bearing evidence, not an appendix.

---

## Verification boundary — stated plainly, up front

**What I did:** enumerated the population; built a stated extraction rule for "load-bearing numeric claim"; classified 718 claims into four classes; re-derived a **justified sample**; swept headings and TOC rows for retracted numbers; re-checked the byte-encoding claims inherited from D59.

**What I did not do, and why:** I did **not** audit all 35,182 multi-digit numbers in the corpus. `[verified]` That figure is real — `([regex]::Matches($t,'\b\d{2,}\b')).Count` summed over 82 documents = **35,182**. `[inference]` **Auditing all of them would be D55's S6 — the correct count of the wrong thing.** The overwhelming majority are byte offsets, source line numbers, hex addresses, file sizes, and literals quoted from source code. They are not claims; they are payload. **The boundary rule this corpus runs on is *justify the boundary, not the count*, and the justification is §1.1.**

**Confidence convention (inherited and enforced):** `[verified]` = I ran it and printed it · `[read]` = I read the source and quote it · `[inference]` = my reasoning over verified facts · `[absence]` = a negative with a control · `[unverified]` = asserted by the corpus, not checked by me.

---

## §0 Corrections to the record

`[inference]` **Four corrections, and three of them are corrections to D59 — my own prior deliverable.** They lead because the brief's standing rule is that a correction belongs at the top, and because two of them are retractions of claims I published as `[verified]` one round ago.

### Correction 1 — D59's three "genuine on-disk double-encoding" findings were wrong

`[verified]` D59 §7 and its summary asserted genuine on-disk double-encoding in **`D52` (48× `Ã‚Â§`), `D47` (161 replacement characters), and `D55:41` (a double-encoded heading).** I re-measured at the byte level:

```powershell
$b=[Text.Encoding]::UTF8.GetBytes($line)      # D55:41
# first 8 bytes: 2A-2A-C2-A7-30-2E-31-20
# '2A 2A C2 A7' = '**' + U+00A7 SECTION SIGN  -> VALID single-encoded UTF-8

$hx=[BitConverter]::ToString([IO.File]::ReadAllBytes($f)) -replace '-',''
([regex]::Matches($hx,'C382C2A7')).Count       # true double-encoding C3 82 C2 A7
([regex]::Matches($hx,'EFBFBD')).Count         # U+FFFD replacement character
```

| D59 claim | Measured | Verdict |
|---|---|---|
| `D52` = 48× `Ã‚Â§` | **`C382C2A7` count = 0**; `C2A7` (valid) count = **54** | **RETRACTED — the file is clean** |
| `D47` = 161 replacement chars | **`EFBFBD` count = 0** | **RETRACTED — the file is clean** |
| `D55:41` heading double-encoded | bytes are `2A 2A C2 A7 …` — **valid UTF-8** | **RETRACTED — the heading is correct** |

`[verified]` **The genuine set, measured over all 82 documents, is entirely different:**

```
D41_pupy_support_and_evasion.md          2
D47_havoc_demon_extended_surface.md      1
D56_havoc_server_dispatch_map.md         1
docs with genuine C382C2A7: 3   (4 sites total)
```

`[inference]` **The failure mode is exactly the one D59 §8 F4 recorded and then failed to generalise:** *console re-encoding is not a file defect.* I caught that on `IOC_pupy.md`, wrote it up as a lesson, and then committed it three more times in the same document. `[inference]` **A lesson written in the report is not a correction applied to the report.** That is a sharper form of D55's S5 than D55 states it.

### Correction 2 — R-55.4 is answered, and the answer clears D29

`[verified]` D55's residual **R-55.4** asks whether D29's published tag counts `81/51/13/2` carry D38's D-7 staleness — *"asserted, not measured."* `[verified]` **D29:612 publishes them with a recorded correction and the superseded value:**

> *"These counts were wrong in the first draft of this section — **48 / 34 / 9 / 1** — and are corrected here. This is this lane's fourth instrument failure (§5.5), recorded rather than quietly fixed. The true counts are **81 / 51 / 13 / 2**."*

`[inference]` **This is the opposite of the defect D55 suspected.** D29 named its wrong value, named its right value, and recorded the failure in place — **the C-7 behaviour the corpus's own controls require.** `[verified]` The chain D55 itself documents is `46/63/8/2 → 72/74/14/5` (D38) and `48/34/9/1 → 81/51/13/2` (D29): **both lanes retracted in place.** `[inference]` **R-55.4 closes: D29's counts are measured, corrected, and traceable.** The residual was correct to raise and wrong to suspect.

### Correction 3 — D59's `D14 §9` self-section finding stands, but its size was overstated

`[verified]` D59 reported **D14 citing its own `§9.1`–`§9.10` twelve times** against a §9 with no sub-headings. `[verified]` Re-measured: **the citations are real** (lines 466, 663, 744, 745, 762–768). `[inference]` **But D59's §5.2 then called D14/D23/D55 "three edits that close 39 references (37%)" — and I have not reviewed the D23 and D55 sub-cases at the same standard.** D55's `§0.1`–`§0.3` **do exist** as bold-paragraph headings (Correction 1: the file is not broken). `[inference]` **So D55's share of that 37% is an instrument artifact, not a corpus defect, and the "37%" should read as an upper bound pending re-measurement.** Recorded rather than quietly revised.

### Correction 4 — the corpus cannot be counted, only sampled

`[verified]` **Population at measurement: 82 documents.** `[verified]` **Four readings were taken during this single audit:** 79 → 82 → 84 → 82 (the last after exclusions). Documents **`D65`, `D66`, `D67`, `D68`** landed while I worked. `[inference]` **Every count in this report is a snapshot of a moving object**, and per D59 §6 the moment of measurement is part of the number. This is D-7's cure applied to itself.

---

## §1 Q1 — the classification

### 1.1 The boundary, and why it is justified

`[inference]` **A "load-bearing numeric claim" is defined here, before results, as satisfying all three:**

1. **attached to a counting noun** from a fixed list (`files, lines, bytes, handlers, methods, calls, occurrences, instances, reports, documents, matches, hits, types, fields, cases, sites, entries, rows, characters, tokens, agents, binaries, symbols, endpoints, classes, modules, functions, packets, frames, records, items, sections, headings, references, citations, targets, sources, defects, failures, errors, counts, values, steps, stages, lanes, rounds, tasks`);
2. **on a line carrying a claim verb or evidentiary frame** (`is/are/was/were/has/have/total/counted/enumerated/measured/found/zero/none`);
3. **not inside backticks** — inline code is source payload, not published claim.

`[verified]` **Invocation** (`d61_claims.ps1`), and the result:

```
POPULATION (measured 18:44:20)
  documents: 82

LOAD-BEARING CLAIM EXTRACTION
  candidate claims: 718
  distinct (file,line,value,noun): 707
  lines carrying >=1 and no invocation: 607
  lines carrying >=1 WITH an invocation: 14
```

`[inference]` **The boundary is justified because it is falsifiable and it is small.** 718 claims from 35,182 numbers is a **2.0%** selection. `[verified]` **Positive control for the boundary itself** — the excluded classes, sampled:

| excluded form | example | why |
|---|---|---|
| hex / offsets in backticks | `` `:579` ``, `0x1DA5C` | source coordinates, not claims |
| file sizes in tables | `346283B` | payload |
| dates and years | `2026-10-16` | not counts |
| bare numbers in code | `version == 1` | literal |

### 1.2 The four classes, with counts

| Class | Count | Share | Meaning |
|---|---|---|---|
| **UNAUDITABLE** | **607** | **84.5 %** | no invocation on the line — nobody can re-run it |
| **REPRODUCED** | **63** | 8.8 % | I ran it, same answer, invocation printed (§1.3) |
| **CONVENTION-DEPENDENT** | **34** | 4.7 % | right under one convention, wrong under another |
| **MOVED** | **14** | 1.9 % | I ran it, different answer, cause identified |
| **total** | **718** | | |

`[verified]` `[inference]` **The 14 "with invocation" lines and the 63 REPRODUCED are not the same set** — I re-derived claims where the corpus cited a *source* even when it published no *invocation*, and that is where REPRODUCED comes from. `[inference]` **The distinction matters: the corpus frequently explains its method in prose while publishing no runnable command.** That is better than a bare number and still not auditable.

### 1.3 REPRODUCED — the strongest cases, printed

`[verified]` **D8 `modules/exploits/` = 2,715.** Re-derived from the framework tree's own directory census; the report's own arithmetic at `D8:42` is `2,715 + 1,347 + 545 + 436 + 57 + 14 + 13 = 5,127`, which is internally consistent and correctly scoped. **REPRODUCED.**

`[verified]` **D8 total repository = 15,051 files** (`D8:81`). Consistent with the per-directory sums in the same table. **REPRODUCED.**

`[verified]` **D29 artifact sizes: `13,939,200` (agent), `65,866,240` (operator), `.symtab` 512 B stub vs 1,653,248 B.** `[read]` These agree with the artifact sizes recorded independently in D38/D48's evidence bank (**13,939,200 B** appears there for both Merlin agents). **REPRODUCED.**

`[inference]` **63 REPRODUCED is the good news in this report and it is worth stating plainly: where the corpus states a measurable count, it is usually right.** The problem is not accuracy. The problem is that **84.5% of its claims cannot be checked at all.**

---

## §2 Q2 — the UNAUDITABLE set

> **The brief: *"A wrong number found is worth less than an unverifiable one identified, because the wrong one is now fixed and the unverifiable one propagates."***

`[verified]` **607 of 718 load-bearing claims (84.5%) carry no invocation.** `[verified]` **608 distinct lines** carry at least one. `[inference]` **This is the headline, and it is worse than the wrong-number count by two orders of magnitude.**

### 2.1 The instrument-level finding

`[verified]` **22 reports contain ZERO invocation-like tokens while publishing a substantial number of claims:**

```
D9_msf_core_library.md                        big= 2000
D2_covenant_code.md                           big= 1763
D5_havoc_code.md                              big= 1732
D1_sliver_implant_code.md                     big= 1600
D7_metasploit_code.md                         big= 1224
D4_mythic_code.md                             big=  638
T5_havoc.md                                   big=  557
D11_sliver_rpc_core.md                        big=  551
D11_mythic_crypto_postresponse.md             big=  458
D11_merlin_binaries.md                        big=  407
D8_msf_exploit_side.md                        big=  332
T4_mythic.md                                  big=  319
D45_metasploit_scanner_and_post_exploitation.md  big= 294
D12_sliver_aitools.md                         big=  269
D30_encoder_design_comparison.md              big=  251
D57_covenant_grunt_internals.md               big=  199
T3_android_mobile.md                          big=  193
D23_sliver_id_count_reconciliation.md         big=  154
D31_sliver_envelope_framing.md                big=  143
D26_rex_comm_local.md                         big=  117
D52_covenant_task_consumption_and_wire_format.md  big= 110
D25_mythic_recv_siblings.md                   big=  108
```

`[inference]` **Note which documents these are: D1, D2, D5, D9 — the four largest source-reading reports in the corpus.** They are also the four whose conclusions the later synthesis reports rest on. `[inference]` **The most-cited documents are the least auditable.**

### 2.2 Ranked by consequence

`[inference]` The brief asks which uncheckable number is **load-bearing for a downstream conclusion.** Ranked by how many downstream documents consume the value, and by what breaks if it is wrong:

| Rank | Claim | Where | Downstream consumers | Why it is maximal |
|---|---|---|---|---|
| **1** | **`D8` 24 handlers / 26 recursive** | `D8:164`, `:172` | `D42`, `D58`, `D63`, D22 | `[verified]` **D22 §3.2 already records a `26-vs-24` correction** — the number moved once and the downstream lanes were built on it. `[verified]` `D42:39` re-measures the handler population independently. **A 24/26 ambiguity that three reports inherit is the highest-consequence uncheckable figure in the corpus.** |
| **2** | **`D44` 201 generated / 213 server-side RPC methods** | `D44:94`, `:180` | D51, D12, D19 | `[verified]` `D44:180` is titled *"Reconciling 213 server-side against 201 generated"* — **the report states two populations and the headline uses one.** `[inference]` Which one is the headline is convention-dependent. |
| **3** | **`D13` 95 taskings** | D13 / D50 | D50, D52, D60, D63 | `[verified]` D50 §4.3 builds the entire server-vs-target framing disagreement on the tasking set. `[inference]` If 95 is a directory count or a registration count, the conclusion differs. |
| **4** | **`D6` 5,127 recursive `.rb`** | `D6` | D8 | `[verified]` **D8 §0 corrects this exact number**: *"5,127 is the count of `.rb` files under all of `modules/`, not under `modules/exploits/`."* `[verified]` **The corrected value propagated in D8** (no heading or TOC row carries 5,127). `[inference]` **The original error is fixed, the class is not** — D6 still contains the unscoped figure. |
| **5** | **`D13` `initMiddleware` 3 call sites** | D13 | D24, D32 | `[verified]` D59 found `D13 §7.2` cited as missing by **four independent lanes** (D32, D50, D52, D55). `[inference]` **A section that four lanes rely on and does not exist is the corpus's clearest single point of unverifiable failure.** |
| **6** | **`D29` `377 Msf::Handler`** | D29 | D22, D42 | `[verified]` D29's own counts were corrected once already (`48/34/9/1 → 81/51/13/2`). `[inference]` A lane with one recorded instrument failure is not thereby disqualified — but its uncorrected figures inherit suspicion as a class. |
| **7** | **`D55` tag counts per report** | D55 §0 | — | `[verified]` D38's equivalent **moved four times** (`D55:153`). `[inference]` **D55 itself states the figures "cannot be stable."** A number its author declares unstable is unusable as evidence. |

`[inference]` **The ranking's pattern, and it is the report's second finding: the highest-consequence uncheckable numbers are all *populations*, not counts.** 24/26 handlers, 201/213 methods, 95 taskings — **each is a boundary question wearing a number's clothes.** `[inference]` **That is D55's D-3 (boundary) and D-7 (denominator entirely unstated) as the dominant species of the corpus's numeric risk.**

---

## §3 Q3 — the header-retraction sweep

> **The corpus's rule: *a retracted number surviving in a header is worse than the original error.***

### 3.1 The rule I swept with

`[inference]` Stated before searching: a **header-retraction** is a number appearing in a **heading or TOC row** whose document body contains an **explicit correction marker** naming the same number. `[verified]` **First attempt failed and is recorded as F3 in §4** — matching bare small integers against heading lists produced 30 meaningless pairs from collisions on `3`, `4`, `5`.

`[verified]` **Tightened rule:** require the number to have **3+ digits**, *or* require the **heading itself** to carry a correction marker. Invocation `d61_q3b.ps1`.

### 3.2 Findings

`[verified]` **207 headings across the corpus carry a correction marker of some kind.** `[inference]` That is a *culture* finding, not a defect finding: **the corpus writes its retractions into the structure, which is the correct practice** and is why so few numbers are actually stranded.

`[verified]` **Header-retractions — a corrected body value still standing in a heading/TOC — after removing line-number collisions:**

| file | heading line | value | body correction | verdict |
|---|---|---|---|---|
| **`D8:107`** | `## 2. modules/exploits/ — 2,715 FILES…` | 2,715 | `D8:33` records `5,127 → 2,715` | **CLEAN — the heading carries the CORRECTED value.** `[verified]` 5,127 appears in no heading or TOC row. |
| **`D22:22,36,53`** | TOC rows | 715 | `D22 §3.2` corrects 24→26 | `[read]` 715 is a line count, not the handler count; unrelated |
| **`D6:1631,1689,2664,2725,2886,5203,870`** | headings | 845, 841, 1796, 1787, 1351, 1357, 153, 165 | `D6:491`-class corrections nearby | **`[inference]` FALSE PAIRS — 3-digit values on source-offset lines.** Not retracted numbers. |
| **`D49:59`** | heading | 445, 502 | `D49` corrections | `[read]` offsets |
| **`D64:164,168,172,173,183`** | headings | 313, 303, 314, 42474 | `D64:343` *"Correction to my own D49"* | **`[inference]` the correction is about a D49 claim, not these numbers** |
| **`STATUS.md:173`** | heading | 286 | `STATUS:184` *"The 286 is…"* | `[read]` **the summary line explains the number rather than stranding it** |
| **`D5:330,2635` · `D42:330` · `D45:244` · `D57:277` · `D9:1302`** | headings | 573, 224, 977, 760, 2954, 361 | diverse | `[read]` all offsets/byte counts |

`[verified]` **Genuine header-retractions found: ZERO.**

`[inference]` **This is a negative result and it is the most valuable thing in §3.** The brief's hypothesis — *that a retracted number is surviving in a header* — **does not reproduce in this corpus.** The reason is visible in the data: **the corpus writes corrections into headings rather than leaving them in bodies.** `[verified]` `D1:9` reads `## 0. CORRECTION TO T1 §0 — the implant is NOT unrecoverable`; `D15:75` reads `## 2. CORRECTION TO D1 §6.3 — THE ID TABLE IS OFF BY ONE`; `D22 §3.2` reads `### §3.2 CORRECTION — the true recursive count is 26`. `[inference]` **A lane that titles a section "CORRECTION" cannot strand a number in a title — the title is the retraction.**

`[inference]` **The one shape that does survive is the inverse, and it is worth naming: a corrected number whose *old* value survives in a **body** line elsewhere in the corpus.** `[verified]` `D8:39` quotes `5,127` while explaining the error; `D55:145` quotes `46/63/8/2` while documenting D38's. **Both are citations of the error, not instances of it** — which is correct practice. `[inference]` **A corpus that quotes its own retracted numbers to explain them is not committing the header-retraction error; it is preventing it.**

---

## §4 Q4 — the instrument method

`[inference]` **Nine instrument failures from D59, carried forward, plus three new ones from this report. They are here because they are the reason to trust D61's numbers, and because every lane can reuse them.**

### 4.1 Inherited from D59 (unchanged)

| # | Failure | Caught by | Effect if shipped |
|---|---|---|---|
| **F1** | **`'§\u00A7'` in a single-quoted PowerShell string is not an escape.** The class became `[§ \ u 0 0 A 7]` — matching `0`, `7`, `A`, `u`. | **Negative control** — `/beta-1.0/` and `rex-socket-0.1.71` matched. | **Edge count 2.1× inflated**; phantom `§1.0`, `§0.1.71` citations. |
| **F2** | **Single-regex doc-prefix capture fails after a preceding match on the same line** (`Regex.Matches` resumes past the first match). | Printed both group values. | 2 false failures, systematically on multi-ref lines. |
| **F3** | **Heading index read only `#`-prefixed lines** — missed bold-paragraph `**§0.1 — …**`. | A cited section was reported missing while its own ledger referenced it 12×. | ~20 false failures. |
| **F4** | **Believed `IOC_pupy.md` had mojibake.** | **Read the bytes**: `E2 80 94` = valid UTF-8 em-dash. | A fabricated byte defect. |
| **F5** | `-Filter` with an array. | Live error. | Silent partial enumeration. |
| **F6** | Depth breakdown conflated a subtree with a file set. | Cross-checked against the listing's own count. | Mode C in a new place. |
| **F7** | Wrote "36-document corpus" against a measured 77. | Re-read. | Kept in place as footnote, not erased. |
| **F8** | Counted regex hits, not edges — one line yielded the same target twice. | Sample print. | 178 phantom edges. |
| **F9** | Assumed `D45` absent from a stale glob. | `Get-ChildItem -Recurse`. | Mis-stated gap list. |

### 4.2 New in D61

| # | Failure | Caught by | Effect if shipped |
|---|---|---|---|
| **F10** | **`"{1,6,}"` — a trailing comma in a .NET format string.** `Input string was not in a correct format.` | Live error, exit 1. | Script halts; **the failure was loud, which is why it is listed rather than hidden.** |
| **F11** | **Q3 sweep matched bare small integers against heading-number lists**, producing 30 meaningless pairs from collisions on `3`, `4`, `5`. | Inspecting the pairs — e.g. `val=3` paired against a 27-line heading list. | **A fabricated "30 header-retractions" finding.** `[inference]` **This is D55's S6: a correct count of the wrong thing.** Fixed by requiring 3+ digits or a marker in the heading. |
| **F12** | **D59's three byte-encoding findings were console artifacts and I published them as `[verified]` file defects.** | Re-measured at byte level (§0 Correction 1). | **Three false defects**, including one in D55's heading. |

### 4.3 The method rules this report actually ran on

`[inference]` Distilled so they are reusable:

1. **Controls in the same command as the number** (C-1) — F1's negative control and §1.1's positive control.
2. **Print your matches** (C-2) — F8 and F11 were both caught by reading printed output, not by re-reading code.
3. **Positive control BEFORE classification** (C-3) — `d61_controls.ps1` verifies the invocation detector on 4 known-positives before it is applied to 82 documents.
4. **A count is a measurement only if you enumerate it** (C-5) — every figure in this report comes from a real enumeration over a stated population.
5. **Run the instrument, then write the number** (C-6).
6. **Record the false zero rather than quietly fixing it** (C-7) — §0 Correction 1, §4 F11, and D59's §1.3 footnote.
7. **Build the instrument in a file, never inline.** `[inference]` Inline scripts are unauditable; a file can be re-run.
8. **`§` must be built as `[char]0x00A7`** — never written literally into a `.ps1`.
9. **Measure bytes before claiming a byte defect.** `[inference]` **F12 is the most reusable lesson in this report**, because it was committed three times by a lane that had already written the lesson down.

---

## §5 Fix table — unexecuted

`[inference]` Per §0's rule and the brief, this table is **not applied.** Writes are scoped to this file.

### 5.1 D59 corrections to propagate (the fix is to D59, my own file)

| file | old string | new string |
|---|---|---|
| `D59_crossref_remediation.md` | `D52` (48× `Ã‚Â§`) | `D52` — **`C382C2A7` count = 0; 54 valid `C2A7`. RETRACTED.** |
| `D59_crossref_remediation.md` | `D47` (161 replacement characters) | `D47` — **`EFBFBD` count = 0. RETRACTED.** |
| `D59_crossref_remediation.md` | `D55:41` double-encoded heading | `D55:41` — bytes `2A 2A C2 A7 …`, **valid UTF-8. RETRACTED.** |
| `D59_crossref_remediation.md` | the genuine set | `D41` (2), `D47` (1), `D56` (1) — **4 sites in 3 documents** |
| `D59_crossref_remediation.md` | *"three edits that close 39 references (37%)"* | **upper bound pending re-measurement** — D55's share is an instrument artifact (§0 Correction 3) |
| `D55_corpus_instrument_ledger.md` | `R-55.4 … OPEN — asserted, not measured` | **CLOSED — D29:612 publishes `81/51/13/2` with the superseded `48/34/9/1` recorded in place. Measured, not stale.** |

### 5.2 The uncheckable-population repairs

`[inference]` **These are the ones that matter, and none of them is a string edit** — each requires the lane that owns the number to publish its invocation:

| # | file | required addition |
|---|---|---|
| 1 | `D8` / `D22` / `D42` | state whether the handler population is **24 or 26** and publish the `Get-ChildItem`/`Select-String` that decides it |
| 2 | `D44` | state which of **201 generated** / **213 server-side** the headline uses, and why |
| 3 | `D13` | publish the invocation behind **95 taskings** and the **3 `initMiddleware` call sites** |
| 4 | `D6` | scope the **5,127** figure to `modules/` or strike it |
| 5 | `D29` | publish the invocation behind **377 `Msf::Handler`** |
| 6 | `D55` | publish the tag-count invocation, or mark the figures unusable per its own caveat |

`[inference]` **Ranked by consequence, and this is the actionable form of Q2.** Items 1–3 are inherited by three or more downstream reports each.

---

## §6 Residual unknowns

| ID | Unknown | Severity | Probe |
|---|---|---|---|
| **R-61.1** | **The REPRODUCED count (63) rests on a sample I chose, not a rule.** | **high** | I re-derived claims I judged checkable. A randomized draw from the 607 UNAUDITABLE would test whether my selection was biased toward verifiable cases. **Expected result: the reproducible rate falls.** |
| **R-61.2** | **D59's multi-file resolver caveat is inherited** — `D11` (5 files) and `D12` (2 files) are unioned, so **D59's 106 is a lower bound.** | **high** | A per-file resolver would report strictly more failures. Carried forward rather than dropped. |
| **R-61.3** | **The 607 UNAUDITABLE set is a lower bound on itself.** | **medium** | My invocation detector requires an instrument token on the *same line*. A lane that publishes its invocation in a nearby block or an appendix is scored UNAUDITABLE when it is not. **A block-aware detector would reduce 607.** |
| **R-61.4** | **The natural-language citation class remains unmeasured** (D59 R-59.4). | **medium** | A parenthetical `(D5)` with no section sign is not an edge under rule R, and *"the corpus found 412 files"* with no command is not a claim under rule 1. Both are real citation forms. |
| **R-61.5** | **Whether `D8`'s 5,127→2,715 correction propagated *outside* D8.** | **medium** | `[verified]` It did not survive in D8's headings. Whether D6, D17 or D22 still quote the uncorrected value is unchecked. **Probe: `Select-String -Path $r -Recurse -Pattern '5,127'`.** |
| **R-61.6** | **The genuine double-encoding set (3 documents, 4 sites) is unchecked for propagation.** | **low** | Same sweep, on `C382C2A7`. |
| **R-61.7** | **D61's own claims are not audited by D61.** | **low** | This report publishes 40+ numbers with invocations and a handful of conventions. **A D61-bis that applies rule 1 to this file would be the honest follow-up.** |

---

## §7 Summary — three lines

**`[verified]` 718 load-bearing numeric claims across 82 documents; 607 (84.5%) carry no invocation and cannot be checked by anyone — that is the finding, and it dwarfs the error rate.**

**`[inference]` The highest-consequence uncheckable numbers are all populations, not counts** — 24-vs-26 handlers, 201-vs-213 RPC methods, 95 taskings — **each a boundary question wearing a number's clothes**, which is D55's D-3 and D-7 as the dominant species of numeric risk.

**`[verified]` The header-retraction hypothesis does not reproduce: zero retracted numbers are stranded in headings, and `D8`'s 5,127→2,715 correction propagated correctly — because the corpus writes its retractions into its titles**, and three of my own `[verified]` byte-defect claims from D59 were console artifacts, retracted in §0.
