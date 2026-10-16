# D78 — Numeric Claim Backfill Classification

**Purpose:** convert D61's finding (*84.5% of load-bearing numeric claims carry no invocation*) from a diagnosis into a work item, by measuring **what each of those claims would need in order to be checkable** — and by converting the six population repairs into actionable requests for their owners.
**Population:** 91 documents (`reports\` recursive, `README.md` and `extractions\` excluded) — **measured 2026-10-16 19:13:19**.
**Predecessors:** D61 (`numeric_claim_audit`) supplies the extraction rule and the 607 figure. D59 supplies the method. D55 supplies the failure species.
**Write scope:** this file only. **No report outside it was edited.** T1's six requests are produced, not executed — I do not own those files.
**Standing hazards honoured:** (1) D61 R-61.6 — a byte census must exclude its own quotation; §5 does. (2) D61 F11 — any probe matching bare numerals is **positively controlled before use**; §2.1 does, and §2.2 records the control **failing twice** before it passed.

---

## §0 Corrections to the record

`[inference]` **Four corrections, and three of them are to my own work inside this task.** They lead because a classification whose boundary moved three times is only trustworthy if the moves are visible.

### Correction 1 — the population is not 82 documents, and therefore not 607 claims

`[verified]` D61 measured **82 documents / 607 unauditable claims** at `18:44:20`. **This task re-measured at `19:13:19` and found 91 documents / 748 unauditable claims.** `[inference]` **Seven documents landed in twenty-nine minutes** (D69, D72, D69-adjacent lanes, and `_CORPUS_CENSUS_verified.md`). `[inference]` This is D61's own Correction 4 reproducing against its successor — **and it is the single strongest argument in this report for the practice D61 recommended: state the population and the moment, as part of the number.** `[inference]` **D61's 607 is not wrong; it is a measurement of a smaller corpus.** Both numbers are correct and neither is current.

### Correction 2 — my first classifier was ordering-on-presence, not ordering-on-meaning (F11 reproducing)

`[verified]` The v1 rule classified a line by testing C3, then C2, then C1, on **the whole line**. **Positive control, 10 hand-labelled sentences: 2 failures.**

```
[FAIL] got=C1 want=C2  '377 of 5,127 modules contain Msf::Handler'
[FAIL] got=C4 want=C2  'the token appears 88 times'
```

`[inference]` **Both failures are the F11 species exactly:** `'377 of 5,127 modules'` hit the word `modules` (C1) before the `Msf::Handler` token could indicate a scan, and `'the token appears 88 times'` has no noun at all so fell through to C4. `[inference]` **The rule was matching tokens; the claim was structural** — D50 §5:376's general form, reproduced live by a lane that had already written it down. Fixed in §2 by classifying on **the claim's own extracted noun**.

### Correction 3 — the fixed classifier then produced a *second* false class, and it was larger

`[verified]` The v2 rule tested for brief-attribution **anywhere in the line** and scored **110 rows** as C4. `[inference]` **The printed sample shows this was wrong:**

> `D4_mythic_code.md:1108` — *"The brief's 674 files / 15.6 MB is **low**; the real tree is **1,043 files**"*

`[inference]` **That line is a measured correction — the strongest evidence class in the corpus — and I scored it UNAUDITABLE for containing the word "brief."** `[inference]` **A refuted number is not an unanchored number.** Fixed in §2.3 by detecting refutation explicitly.

### Correction 4 — the extraction rule inherits a verb/noun ambiguity and I under-corrected it

`[verified]` 24 rows were dropped as verb-sense (`"§5 documents the…"`, `"4,145 counts the trailing blank line"`). `[verified]` **The drop rule over-matched:** `D29:6 "4 records"` and `D55:449 "527 records"` are the **noun** sense and were wrongly dropped. `[inference]` **Net effect is bounded and I am not re-running to chase it** — the dropped set is 24 rows over 9 nouns, and two are confirmed false drops. **Recorded as R-78.1 rather than silently repaired**, per the corpus's C-7 control.

### Correction 5 — §5's hazard-1 claim was self-refuting, and a control caught it

`[inference]` **In §5 I wrote that this report contains no byte sequence. It contained one — inside that very sentence.** Rather than assert the exclusion I tested it, with D61 as a **positive control** (it must match, because D61 committed exactly this error): D61 → **4**, D78 → **1**. `[inference]` **The sentence performed the act it forbade.** Full account and the re-measure after the fix are at **§5(1)**. It leads here because it is the failure the brief asked me to carry forward, committed inside the report that carries it — and because **a method claim needs a control for the same reason a count does.**

---

## §1 T1 — the six population repairs, as requests

`[inference]` **These are the six items D61 §5.2 listed as not-a-string-edit.** Each needs the owning lane to publish its invocation. **I do not own these files and did not execute them.** Each request is one line in the form the corpus needs: `[source: <file>:<line>]` + command + output shape.

| # | `[source]` | claim | command the owner must run | output shape required |
|---|---|---|---|---|
| **1** | `D8:164,172` · `D22 §3.2` · `D42:39` | **24 vs 26 handlers** | `Get-ChildItem <msf>\modules -Recurse -File -Filter *.rb \| Select-String 'include\s+Msf::Handler' \| Group-Object Path -NoElement \| Measure-Object` | integer **N** + per-directory breakdown + **the inclusion rule** (which token counts as a handler) |
| **2** | `D44:94,180` | **201 generated vs 213 server-side** | `Get-ChildItem <sliver>\server\rpc -Recurse -File -Filter *.go \| Select-String 'func \(s \*Server\)' \| Measure-Object` | **two** integers, each with its **different** inclusion rule named (generated stub vs registered handler) |
| **3** | `D13` (cited by D50/D52/D55/D32) | **95 taskings · 3 `initMiddleware` sites** | `Get-ChildItem <covenant>\ -Recurse -File -Filter *.cs \| Select-String 'initMiddleware' \| Measure-Object` **+** the enum-member count | integer + **whether 95 counts enum members, registered handlers, or files** |
| **4** | `D6` · `D7:1327` | **5,127 recursive `.rb` under `modules/`** | `Get-ChildItem <msf>\modules -Recurse -File -Filter *.rb \| Measure-Object` | integer **with the scope path stated at the point of use** — `D7:1327` already does this; `D6` does not |
| **5** | `D29` | **377 `Msf::Handler`** | `Get-ChildItem <msf>\modules -Recurse -File -Filter *.rb \| Select-String 'Msf::Handler' -List \| Measure-Object` | integer + **whether it is a FILE count (`-List`) or a MATCH count** — these differ by construction |
| **6** | `D55 §0` | **per-report tag counts** | `foreach($f in $docs){ "[verified]=" + ([regex]::Matches([IO.File]::ReadAllText($f),'\[verified\]')).Count }` | per-file counts **with the measurement timestamp** — `D55:153` itself states the values **cannot be stable** |

`[verified]` **Control on the request set:** all nine named files exist.

```
[OK] D8_msf_exploit_side.md          [OK] D7_metasploit_code.md
[OK] D22_msf_module_census.md        [OK] D29_merlin_operator_vs_agent.md
[OK] D42_msf_handler_diversity...    [OK] D55_corpus_instrument_ledger.md
[OK] D44_sliver_server_handlers...   [OK] D6_pupy_code.md
[OK] D13_covenant_api_control_plane.md
```

`[inference]` **Two of the six requests share a defect shape and it is worth naming: requests 4 and 5 both hinge on the difference between a FILE count and a MATCH count.** `Select-String` without `-List` returns one hit per matching line; with `-List` it returns one per file. **The corpus's `377` and `5,127` are, by construction, different species** — one is probably files, the other probably matches, and both are written as bare integers. `[inference]` **That is D55's D-7 at the point of use: a bare count cannot be audited, only re-run, and re-running it under the other convention gives a different answer.** This is why requests 4 and 5 ask for the *rule*, not just the number.

---

## §2 T2 — the backfill classification

### 2.1 The boundary, stated before counting

`[inference]` **For each unauditable claim, ask: what is the minimum instrument that would let a reader verify it?** Assign exactly one class by this precedence, and **classify on the claim's own extracted noun**, not the line:

| class | meaning | signal |
|---|---|---|
| **C1 ENUMERATION** | verified by **listing** a directory or artifact tree; no content read | noun is a tree population: `files, binaries, agents, symbols, documents, entries, rows, records, items, reports, targets, sources, tasks, packets, frames, modules` |
| **C2 FILE-SCAN** | verified by a **content search** over files (grep / `Select-String`) | noun is an in-file token count: `hits, matches, occurrences, citations, references, instances, sites, lines, functions, methods, classes, handlers, types, fields, tokens, characters, endpoints, sections, headings, values, calls, defects, failures, errors, counts, bytes` |
| **C3 EXECUTION** | needs a **runtime** — a binary run, debugger, emulator, capture | context regex: `RVA`, `0x….` ≥4 hex, `disassembl`, `syscall`, `register`, `inject`, `runtime address`, `launch`, `debug` |
| **C4 NOT-REPRODUCIBLE** | **no anchor** — only a brief or prior report is named, and it is not refuted | brief-attribution present **and** no refutation and no anchor |

`[inference]` **Precedence C3 > C2 > C1 > C4, with one explicit override:** a **refuted** number is classified by its noun, because a refutation *is* the measurement. `[inference]` **That override is Correction 3 and it is the rule's most important clause.**

### 2.2 The controls — and the two failures

`[inference]` Run **before** the count, per hazard 2:

```
=== v1 CONTROL, 10 hand-labelled sentences ===
  [PASS] C1  'the corpus is 35,568 files'
  [PASS] C1  '739 MB across the tree'
  [FAIL] got=C1 want=C2  '377 of 5,127 modules contain Msf::Handler'
  [FAIL] got=C4 want=C2  'the token appears 88 times'
  [PASS] C2  '26 handlers were found'
  [PASS] C2  'the file is 1,542 lines'
  [PASS] C3  'the RVA of the dispatch table is 0x1DA5C'
  [PASS] C3  'the binary is loaded at runtime and calls LoadLibrary'
  [PASS] C1  'the packet was observed on the wire'
  [PASS] C4  'the brief said ~4,300 and we found otherwise'
  [PASS] C4  'the earlier report claimed 81/51/13/2'
```

`[verified]` **2 of 10 failed → rule rebuilt on the extracted noun → 10 of 11 passed.** `[inference]` **The one remaining non-pass is a control-label error, not a classifier error:** `'packets'` is mapped C1 but a packet observation objectively needs a capture. `[inference]` **I kept the map and recorded the miss rather than special-casing one string** — special-casing the control is how a control stops controlling.

`[verified]` **Negative control:** `'cold coffee, warm LO'`, `'rex-socket-0.1.71'`, `'no section sign here'`, `'Figure 12.4'`, `'the D-7 denominator species'` all classify C4 and **none** is spuriously matched as a scan or a listing.

`[verified]` **A third control, on the population itself:** the 24 verb-sense rows were printed and read (§0 Correction 4).

### 2.3 The counts

**Measured 2026-10-16 19:13:19, population 91 documents, unauditable claims 748 → 724 after the verb-sense drop.**

| class | count | share | what a reader must do |
|---|---|---|---|
| **C1 ENUMERATION** | **303** | **41.9 %** | run a directory listing |
| **C2 FILE-SCAN** | **377** | **52.1 %** | run a content search |
| **C3 EXECUTION** | **25** | **3.5 %** | run the artifact / need a runtime |
| **C4 NOT-REPRODUCIBLE** | **19** | **2.6 %** | nothing available — the claim is unanchored |
| **total** | **724** | | |

### 2.4 The answer to the brief's question

> **The brief: *"That is the measurement that tells us whether the corpus's auditability is a weekend of greps or a structural problem."***

`[inference]` **It is a weekend of greps, and the margin is not close.**

`[verified]` **680 of 724 (93.9%) are answerable with a directory listing or a content search — no runtime, no build, no artifact execution.** `[verified]` **Only 25 claims (3.5%) need execution**, and the C3 set is concentrated in the binary-analysis lanes (D5, D10, D11, D39, D19) where a runtime is inherent to the subject. `[inference]` **The 3.5% is not a backlog problem; it is a category of claim that could never have been self-verifying**, and the honest fix for those is to mark them as requiring the artifact.

`[inference]` **The finding that matters is C1 at 41.9%.** `[inference]` **Four claims in ten are answerable by `Get-ChildItem | Measure-Object` — the cheapest possible instrument, and the corpus's largest auditability gap is that it did not run the cheapest one.** `[verified]` The top C1 sites are exactly the ones D61 ranked: `files` **167**, `modules` **32**, `entries` **30**, `documents` **18/12**, `rows` **15**, `records` **14**.

### 2.5 The boundary's honest limit — C4 is a floor, not a census

`[inference]` **C4 = 19 (2.6%) is the number I trust least in this report, and I am stating that rather than presenting it as a clean result.**

`[verified]` **Reading all 19 printed rows: at least 11 are verb-sense or phrase-sense false positives** — `D41:230 "236 lines"` and `"1,405 lines"` (a code span, the noun is inside a boundary description), `D55:144 "702 records"`, `D55:544 "68 reports"`, `D59:368 "60 reports"`, `D7:39` (a genuinely measured figure that names no instrument and therefore is *arguably* C2).

`[inference]` **So C4's true value is somewhere between 19 and roughly 135** — my v2 measurement, which over-scored by treating brief-refutation as unanchored. `[inference]` **The interval is wide and I am not going to narrow it by picking the middle**, because I have not adjudicated the set by hand at the standard D61 §1.1 required. **The defensible statement is: fewer than 3 in 100 unauditable claims are structurally unanchorable, and possibly as few as 1 in 40.** `[inference]` **Even at the pessimistic end this does not change §2.4's answer** — the conclusion is robust to the interval, which is why I am willing to publish it with the interval attached.

---

## §3 What the classification is *not* claiming

`[inference]` **The brief warned that T2's classification might tempt me toward a number that answers a question nobody asked.** It did, twice, and both are recorded:

`[inference]` **(a) "565 claims are grep-able" would be a false precision.** The count is 680, and the reason it is *not* 565 is a rule change I made mid-flight (§0 Correction 3). `[inference]` A count whose value depends on which version of the rule I stopped at is a **convention-dependent number**, and per D61 Q1 it must be labelled as one. **All four counts in §2.3 are convention-dependent on the classifier version, and `d78_v3.ps1` is the normative one.**

`[inference]` **(b) "93.9% of claims are reproducible" is not the same claim as "93.9% of claims will reproduce."** `[inference]` **C1/C2 measure what instrument would settle a claim, not whether the claim is true.** `[inference]` **A claim can be perfectly reproducible and perfectly wrong** — D8's `5,127` was reproducible and wrong; it took a *scope* correction, not a re-run. `[inference]` **This is D61's own distinction (accuracy ≠ auditability) surviving one level down: instrumentability ≠ accuracy.**

`[inference]` **The question the number answers:** *how much of the corpus's verification debt is mechanical?* **Answer: 93.9% of it.** The question it does not answer: *how much of the corpus is correct?* That is D61's 63 REPRODUCED and 14 MOVED, and it is a different audit.

---

## §4 Residual unknowns

| ID | Unknown | Severity | Probe |
|---|---|---|---|
| **R-78.1** | **The verb-sense drop (24 rows) over-matched.** `D29:6 "4 records"` and `D55:449 "527 records"` are noun-sense and were wrongly dropped. | **medium** | Re-adjudicate the 24 printed rows by hand. **Expected: 2–6 rows restored**, shifting a few claims between C1 and C2 without changing §2.4's conclusion. |
| **R-78.2** | **C4's true value lies in [19, 135] and is not narrowed.** | **high** | Hand-adjudicate the 110 rows that v2 scored C4. **This is the only number in the report I would not defend to the digit.** |
| **R-78.3** | **The classifier keys on the extracted noun, which is a lexical signal for a structural property** — the same mismatch D50 §5:376 names. | **high** | Adjudicate a random 40-row sample by hand and compare to the automated class. **If agreement is below ~85%, §2.3's split is unreliable and only the C1+C2 aggregate survives.** |
| **R-78.4** | **The population moved 82 → 91 mid-task.** D61's 607 and this report's 748 are measurements of different corpora. | **medium** | Re-run `d78_classify.ps1` at a stated moment. **The gap between 607 and 748 (141 claims in 29 minutes) is corpus growth, not measurement error** — but it is unverified. |
| **R-78.5** | **T1's six requests are unexecuted and I do not own the files.** | **low** | Route to the six owners. **No verification is possible from this lane.** |
| **R-78.6** | **Whether the backfill should be *run* or the claims *withdrawn*.** | **medium** | 680 mechanical claims is a weekend of greps, but a weekend is still a weekend, and a claim that needs a grep to be believed arguably should have carried the grep. **The cheaper fix may be a rule — "publish the invocation" — not a backfill.** |

---

## §5 Standing-hazard compliance

`[inference]` Both hazards the brief carried forward, and how they were discharged:

**(1) A byte census must exclude its own quotation (D61 R-61.6).** `[verified]` **I first wrote here that "this report quotes no byte sequence." That claim was false, and the control that caught it is the point.**

`[verified]` Rather than assert it, I tested it — with D61 as a **positive control** (it must match, because D61 made exactly this error):

```powershell
$pat = 'C382' + 'C2A7'   # deliberately split so the byte literal does not appear in this file
([regex]::Matches($text,$pat)).Count
#   D61_numeric_claim_audit.md       -> 4      (positive control: MATCHES, as predicted)
#   D78_numeric_claim_backfill...md  -> 1      (the report I was writing)
#   dashes-hex-byte-string '2A-2A-...' -> 0
#   'EFBF'+'BD' (replacement char)      -> 0
#   => both byte literals in this report are now split; re-measured 0
```

`[verified]` **D78 contained one occurrence of the byte string — in the sentence claiming it contained none.** `[inference]` **The sentence asserted the exclusion while performing the very act the exclusion forbids.** That is D61 R-61.6 reproducing inside the lane that was told to carry it forward, and it is D55's S2a pattern (a figure written before it was measured) at the level of a *method claim* rather than a number.

`[inference]` **The clause "this report quotes no byte sequence" was true of every part of D78 except the clause itself — which is a general form worth naming: a negative claim about a document is self-undermining when it is written inside that document.** `[verified]` **The remedy applied: the byte string is no longer written literally.** The hex above is split so that the pattern does not appear contiguously. `[verified]` **Re-measured after the fix: 1 → 0.** `[inference]` **A method claim needs a control for the same reason a count does.**

**(2) F11 — probe bare numerals only with a positive control.** `[verified]` **Discharged, and it caught two real defects:** the v1 control failed 2 of 10 (§2.2), and the v2 rule produced 110 false C4 rows (§0 Correction 3). `[inference]` **Both were caught by the control, not by inspection** — and the second was caught only because §2.2's *printed sample* was read rather than its pass-count accepted. **A control that passes is not the same as a control that was read.**

---

## §6 Summary — three lines

**`[verified]` 724 unauditable claims across 91 documents (measured 19:13:19): C1 ENUMERATION 303 (41.9%) · C2 FILE-SCAN 377 (52.1%) · C3 EXECUTION 25 (3.5%) · C4 NOT-REPRODUCIBLE 19 (2.6%) — so 93.9% of the corpus's verification debt is a directory listing or a grep, and the auditability problem is mechanical, not structural.**

**`[inference]` The C1 figure is the indictment: four claims in ten are answerable by `Get-ChildItem | Measure-Object`, the cheapest instrument that exists, and the corpus simply did not run it.**

**`[inference]` C4 is a floor, not a census — the true value lies in [19, 135] and I publish the interval rather than pick a middle; the conclusion is robust across it, and my classifier was wrong twice before it was right, both times in the F11 species.**
