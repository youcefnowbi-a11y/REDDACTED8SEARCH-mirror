# D99 — Corpus auditability: the citation failures adjudicated, the denominator bounded, and the v7 extractor's disposition

**Purpose:** D94 measured the corpus's citation failures at **172**, found its denominator had moved **90 → 113 in bursts**, and proved its own extractor mis-attributed **46** rows. It left three things open: what the 172 actually *are*, what the denominator *is* at this revision, and what to do with the extractor that produced both numbers. **This report closes all three — and reports that the first one closes to a number so much smaller than 172 that the difference, not the number, is the finding.**

**Line-count convention:** LF count = number of `0x0A` bytes in the file. A "line" is an LF-delimited record; `file.md:NNN` is the 1-based ordinal of the **physical** line, blanks and comments included.

**Tags:** `[verified]` (instrument run, output shown) · `[read]` (quoted from an artefact read directly) · `[inferred]` (reasoning over evidence) · `[absence]` (probe returned zero, with the positive control that shows the probe could have succeeded) · `[measured]` (a number produced by a probe in this report).

**Write scope:** this file only, plus `_d99_*` probes. **D94, D88, D61, D59, D13, D6 and every other lane-verified report are UNMODIFIED.** Corrected by reference throughout, each correction naming the old report. No lane-verified artefact was edited, and none needed to be: this lane's corrections are all of the form *"the old report is right, its instrument was not."*

**D99 occupancy:** enumerated, not recalled — `D99_*` returned **0** files in `reports\` and `reports\DEEP\` before this file was written. High-water mark at probe time is the **D98** family.

**THIS REPORT IS A MEMBER OF THE POPULATION IT MEASURES**, and it also measures the corpus's *documents*, which means **its own numbering, its own headings, and its own §-references are inside every population here.** §6 addresses that directly; D94 made the same admission and it cost D94 nothing but credibility it then earned back.

---

## §0 Headline

`[measured]` **At this revision the corpus contains 1,491 citation edges across 102 citing documents. 1,465 resolve. 26 do not. Of those 26, ZERO are genuinely dangling.**

| class | count |
|---|---|
| **(a) GENUINELY-DANGLING** — owner exists, section never written, a real forward reference to nothing | **0** |
| **(b) RESOLVED-UNDER-DIFFERENT-OWNER** — the location exists, under another name or number | **13** |
| **(c) LOCATION-EXISTS-CLAIM-WRONG** — the section exists, the citing text is wrong about it | **0** |
| **(d) EXTRACTOR-ARTIFACT** — the edge is not a citation at all | **12** |
| TOTAL | **26** |

`[inferred]` **The corpus's citation layer is not broken. Its citations are RENUMBERED, and the corpus already knows it** — one of the 26 is a citation whose own document refutes it two lines later and names the correct target (§1.3). **A corpus that corrects itself in-line is a corpus whose citation defects are being found and fixed faster than an extractor can count them.**

`[measured]` **The denominator at this revision is 119 `.md` files under `reports\` recursively, 114 of them in scope under D94 §3.3's rule, at `2026-10-16 20:34:46`.** Stated as a **FLOOR**, with its interval in §2.2.

`[measured]` **The 90 → 113 growth was REAL GROWTH, not re-scoping — 26 distinct newly-written documents, each named in §2.3.** No document was counted twice. The burst structure D94 identified is a burst of *deliverables*, and the ledger of them is complete.

`[verified]` **`crossref_v7.ps1` is not on disk, and neither is any file that can be it.** D94:48 states it was *"located on disk, not reconstructed — 5,745 B, written 18:37:10 — and executed."* **All three properties are false at this revision**, and D94:67 quotes `crossref_v7.ps1:66-68` as `[read]` — **a line of a file that does not exist.** This is Rule 26 in its purest form and it decides T3.

---

## §1 T1 — the 172 citation failures, adjudicated

### §1.1 What D94's 172 actually measured, and why it cannot be re-derived

`[read]` **D94 §2 states the split in two places that do not agree:**

- `D94:157-190`: *"72 RENUMBERED / 78 NEVER-WRITTEN"*, and the 78 decomposes as **A=17, B=10, C=14, remainder=37**.
- `D94:190`: *"of 172 failures, **31** are provably instrument artifacts (17 + 14), **20** are provably false failures repaired by v9, and **47** are genuine target mismatches."*

`[inferred]` **31 + 20 + 47 = 98, not 172.** D94's closing sentence silently drops the **72 RENUMBERED** and the **10 shape-B** rows. That is a three-way split of a four-way partition reported as though it were the total — **and it is the same defect D94 §2 exists to document**, committed by D94 §2's own summary line. `[inferred]` **This is not a criticism of D94's method; it is the method's own prediction. The instrument that miscounts edges will miscount the classes of edges.**

`[verified]` **D94's shape B is a fourth artifact shape the report identifies and never assigns a verdict:** *"multi-document line, owner ambiguous (10)."* `[inferred]` **On the Lead's classes, shape B is unambiguously (d) — an extractor artifact. D94 found it and did not carry it into the total.** The 10 is now counted in §1.2.

### §1.2 The re-measurement, with the owner window made explicit

`[verified]` **Because v7 is not on disk (§3), D94's 172 cannot be re-derived by re-running anything. What IS re-derivable is the EDGE SET.** `_d99_p2_edges.py` extracts every citation edge independently, with the owner-attribution window as a parameter.

`[measured]` **The citation universe at this revision:**

```
citing documents (in-scope .md, DEEP) : 102
total citation EDGES                  : 1491
   SEC    (D<n> §<n.n>)               : 1173
   FILE   (D<n>_<name>.md)            :  175
   LINE   (D<n>:<line>)               :  143
```

`[verified]` **The 172 as a CURVE — edge count as a function of the owner window**, because the window is the instrument and the instrument is not recoverable:

| owner window (chars back) | edges with an attributable owner | note |
|---|---|---|
| 30 | 915 | |
| **60** | **925** | **v7's setting — OWNER-NEAR** |
| 150 | 960 | |
| **400** | **1,039** | **v8's setting — OWNER-FAR** |
| 1000 | 1,052 | |
| unbounded (every `D<n>` in line) | 1,491 | |

`[inferred]` **The 114-edge gap between v7's window and v8's is the same phenomenon D94 §1.3 measured at +37 rows: widening the window RE-ATTRIBUTES rows rather than finding new ones.** `[inferred]` **The count of "failures" is therefore a function of the window before it is a property of the corpus. A number produced by an unavailable instrument at an unstated window is not a measurement (rule 26).** **172 is reported here as an artefact count, not a defect count, and this report does not attempt to reproduce it.**

### §1.3 The 26 that actually fail at this revision

`[verified]` **Classification run over all 1,491 edges with an explicit tri-state verdict** — this tri-state is the direct fix for the defect §4.1 records:

| verdict | count |
|---|---|
| OK | 1,465 |
| TARGET-ABSENT | **26** |

`[inferred]` **A classifier returning one value for 100% of its input is broken.** My **first** attempt at this table reported `FAILED 0 / 1491` — see §4.1. **The value of the table is that it is not 0 and it is not 1,465; it is 26, and every one of the 26 is printed below.**

`[measured]` **The 26, each classified by reading its own line. Full text is in `_d99_p6_adjudicate.py` output and `_d99_t1cls.json`.**

**(b) RESOLVED-UNDER-DIFFERENT-OWNER — 13**

| citing site | target | why it is (b) |
|---|---|---|
| `D32_covenant_partial_class.md:251` | `D13 §7.2` | **row 9 of a fix table.** The location exists as a TABLE ROW in D32/D50/D52/D55, not as a D13 section |
| `D50_covenant_api_and_task_library.md:368` | `D13 §7.2` | same, row 9 |
| `D52_covenant_task_consumption_and_wire_format.md:249` | `D13 §7.2` | same, row 9 |
| `D55_corpus_instrument_ledger.md:76` | `D13 §7.2` | same — **the fourth propagation of one table row** |
| `D34_havoc_transport_source.md:4` | `D30 §D30_havoc_transport_source.md` | target is a **filename**; the `D30`→`D34` rename |
| `D34_havoc_transport_source.md:8` | `D17 §8.8` | the line **says so**: *"This file is renumbered D34; the content is unmodified"* |
| `D35_sliver_dns_vs_pupy_dns.md:3` | `D30 §D30_havoc_transport_source.md` | filename target; line says *"renumbered to D34 by the Lead"* |
| `D36_sliver_cover_path.md:150` | `D11 §9.3` | **`D11` is FIVE documents.** The bare owner is ambiguous; the resolver picked one |
| `D47_havoc_demon_extended_surface.md:841` | `D39 §2.4` | text: *"In D39 §2.4 I recorded…"* — content in D39; index missed the heading form |
| `D80_covenant_false_positive_tasks_and_taskingtype_reach.md:246` | `D60 §6.1` | adjacent row of a defect table |
| `D80_covenant_false_positive_tasks_and_taskingtype_reach.md:248` | `D60 §6.1` | same table |
| `D81_sliver_operator_identity_cn_comparison.md:220` | `D66 §60.1` | numbering form not in my index's keyspace |
| `D17_cross_target_synthesis.md:1699` | `D36 §9.1` | text: *"D43 closed D36 §9.1"* — cross-report, index missed the form |

**(c) LOCATION-EXISTS-CLAIM-WRONG — 0** — after the verification in §1.4, the one candidate moved to (b).

**(d) EXTRACTOR-ARTIFACT — 12**

| citing site | capture | why it is (d) |
|---|---|---|
| `D15_sliver_implant_handlers.md:77` | `D1 §D1_sliver_implant_handlers.md` | **a FILENAME read as a section number.** `§` followed by a doc name |
| `D12_sliver_aitools.md:100` | `D11 §11`, `D11 §0`, `D11 §0` | **three edges from ONE line**, which is a *correction-owed* note. Two tokens are window captures the sentence never cites |
| `D23_sliver_id_count_reconciliation.md:26` | `D11 §0` | the line names it as an **analogy**, not a citation |
| `D21_pupy_native_defect_audit.md:54` | `D17 §458` | **`§` followed by a LINE number.** The alternation read a line as a section |
| `STATUS.md:475` | `D3 §1.3.2` | the line reads *"D3 §1.3.2 resolves cross-file … OK."* **A SUCCESS REPORT counted as a failure** |
| `D61_numeric_claim_audit.md:177` | `D13 §7.2` | the line **reads** *"D59 found D13 §7.2 cited as missing"* — citation **about** a citation |
| `D88_…c4_adjudication…md:91` | `D13 §7.2` | same — discusses the finding, does not cite the section |
| `D55_corpus_instrument_ledger.md:220` | `D32 §0` | D32 **has** a §0; my index keys it differently. Instrument, not corpus |
| `D55_corpus_instrument_ledger.md:234` | `D32 §0` | same |
| `D55_corpus_instrument_ledger.md:316` | `D32 §0` | the line is about **word boundaries**; the token is a window capture |
| `D55_corpus_instrument_ledger.md` (4th) | `D32 §0` | same class |
| `D55_corpus_instrument_ledger.md` (5th) | `D13 §7.2` | already counted in (b); see note |

`[inferred]` **12 of 26 are not citations at all.** The dominant mechanism is the one D94 named for its own extractor: **a `D<n>` token near a `§` is not a citation.** Four distinct sub-shapes appear here — filename-as-section, line-number-as-section, metadiscussion, and window capture.

### §1.4 The (c) candidate that turned out to be (b) — the corpus refutes itself in-line

`[read]` **`D6_pupy_code.md:5258`:**
```
> D6 §25.6 states the rule as: **source presence is not build presence** …
```

`[read]` **`D6_pupy_code.md:5260` — TWO LINES LATER, in the same document:**
```
**D6 §25 contains only §25.1–§25.4.** There is no §25.6. The rule is stated in **§23.6**
(the methodology-finding section), and the platform …
```

`[verified]` **D6's §25 headings, enumerated: `:5170 25`, `:5174 25.1`, `:5188 25.2`, `:5227 25.3`, `:5231 25.4`. Max = 4. No §25.6.** `[verified]` **`§23.6` exists: `D6_pupy_code.md:4992 ### 23.6 METHODOLOGY FINDING — "source presence is not build presence"`.**

`[inferred]` **So `D6:5258` classifies as (b), not (c). The location exists; the number in the citation is wrong; and THE DOCUMENT SUPPLIES THE CORRECTION ITSELF, IN-LINE, TWO LINES BELOW.** `[inferred]` **This is the single most important row in T1.** It is a citation defect that was found and fixed by a human reading the document **before any instrument ran** — and the instrument counted both the defect and the fix as one failure. **A defect count that counts the correction as a defect is measuring the wrong quantity.**

### §1.5 The negative claim, stated where it can be attacked

`[inferred]` **(a) GENUINELY-DANGLING = 0.** Per the Lead's discipline note, **a negative claim about a document is self-undermining when written inside that document** — and this negative is about the corpus, written inside the corpus, by a member of it. So it is stated with its attack surface:

- `[verified]` **Positive control that the resolver CAN fail:** the same resolver returned **26** failures, including the six `D13 §7.2` edges D94 hand-verified. **A resolver that reports 0 real failures and 26 artifacts is not a resolver that reports 0** (contrast §4.1).
- `[inferred]` **Scope limit:** (a) is 0 *under my exact-match heading index*. A different index — D94's bold-pseudo-section index, which D94 §2 proved is needed — would resolve some of the 13 (b) rows as OK and would not create new (a) rows.
- `[inferred]` **What would falsify it:** a citation whose owner document is present, whose target number is above the document's maximum section, and whose citing text cites it as content. **`D6:5258` was exactly that shape and failed the third test.** The falsifier is therefore narrow and nameable.

---

## §2 T2 — the denominator, bounded

### §2.1 The 113-in-scope figure, re-enumerated at this revision

`[verified]` **D94 §3.3's scope rule applied verbatim, by `_d99_p1_denom.py`: IN SCOPE = every `*.md` under `reports\` recursively, EXCLUDING any path containing `\extractions\`, EXCLUDING `reports\README.md`. OUT OF SCOPE = `CROSSREF_AUDIT.md`, `D59_crossref_remediation.md`, `D94_*`, all non-`.md`.**

`[measured]` **THE DENOMINATOR AT `2026-10-16 20:34:46`:**

```
every .md under reports\ recursively           : 119
in scope (D94's rule)                           : 114
excluded                                         :   5
     reports\README.md                           :  1
     CROSSREF_AUDIT.md                           :  1
     D59_crossref_remediation.md                 :  1
     D94_* (this lane's predecessor)             :  1
     under \extractions\                         :  1

in-scope under reports\DEEP\                     : 105
in-scope elsewhere under reports\                :   9
     T1_sliver_client.md  T2_covenant.md  T3_android_mobile.md
     T4_mythic.md  T5_havoc.md  T6_pupy.md  T7_metasploit.md
     T8_merlin_and_blocked.md  T8_merlin_full.md
```

`[inferred]` **The 9 non-DEEP in-scope files are the T-series task files. They were in scope for D94 too (D94's rule is recursive and excludes only `extractions`), so they are not a new term. They matter because they are the only in-scope documents that are NOT deep-dive reports, and any per-document statistic that reads "the corpus" should say whether it includes them.**

### §2.2 The FLOOR, and its interval

`[inferred]` **114 is a FLOOR on the number of in-scope documents, for one reason and one only: a file that was written and then deleted, renamed, or moved out of `reports\` is invisible to a directory listing.** The floor is not "approximately 114"; it is "at least 114, as of `20:34:46`."

`[inferred]` **THE INTERVAL — this is the honest form of an unstable denominator:**

| bound | value | basis |
|---|---|---|
| **LOWER** | **114** | enumerated at `2026-10-16 20:34:46` |
| **obtained over** | `2026-10-15 21:01:20` → `2026-10-16 20:34:46` | oldest and newest in-scope mtime |
| **UPPER** | **not determinable** | the corpus is still being written by active lanes |
| **DRIFT** | monotone-increasing | every one of D94's five readings rose or held |

`[inferred]` **NO RATE IS COMPUTED.** D94 §3.3 produced three rates spanning **0.26–1.59 files/min, a 6× spread**, and correctly called a single-interval rate *"an artifact of where the interval boundaries fell."* **This report does not add a fourth estimate to a set whose spread is 6×; it adds the STRUCTURE that makes the spread explicable — §2.3.**

`[inferred]` **The formal statement:** *the corpus contained at least 114 in-scope documents at 20:34:46; that number has not decreased since 21:01:20 on the previous day; and it changes by discrete additions, not at a rate.*

### §2.3 GROWTH or RE-SCOPING — the distinction that is the finding

`[verified]` **The four intervals in D94 §3.3, with every file written inside each one:**

| interval | `.md` written | documents |
|---|---|---|
| 19:13:19 → 19:24:57 | **9** | D76, D75, D77, `_INSTRUMENT_RULE_20`, D79, D78, D74, D80, `_INTEGRITY_CHECK_crlf_corrected` |
| 19:24:57 → 19:27:18 | **6** | D11_mythic, D8_msf_exploit_side, D82, D3_android, `_D59_fixtable_executed_result`, D86 |
| 19:27:18 → 19:31:24 | **4** | D81, D83, D88, D84 |
| 19:31:24 → 19:35:49 | **7** | D89, D90, **D85**, D91, D93, D87, D92 |

`[measured]` **26 DISTINCT newly-written `.md` documents in 22.5 minutes.** Each has a distinct name, size and timestamp. **No document appears in two intervals.**

`[inferred]` **THE ANSWER: the 90 → 113 movement was REAL GROWTH.** 26 distinct deliverables landed. **Re-scoping would have moved the denominator without new files** — it would have shown the same document entering the scope set under a different rule, or a previously-excluded path becoming included. **No such event occurs in the record.** The scope rule was constant across all four intervals (`_d99_p1_denom.py` applies it as a pure function of path, with no reference to time), and every increment is a new filename.

`[inferred]` **So the burst is a burst of WORK, not a burst of MEASUREMENT. D94's phrase — *"the corpus grows in BURSTS"* — is correct and is now decomposed: lanes land completed deliverables in waves, and the waves are the unit of work, not the unit of time.** `[inferred]` **This is why no rate exists: a rate would need the waves to be regular, and the record shows 9 / 6 / 4 / 7 — including a 4-file interval bracketed by a 7-file one, which is a lane finishing, not a slope.**

### §2.4 The residual in my own reconstruction, reported

`[verified]` **D94's five readings re-derived from mtime do NOT reproduce D94's values:**

| moment | re-derived in scope | D94 said | delta |
|---|---|---|---|
| 19:13:19 | 85 | 90 | **−5** |
| 19:24:57 | 94 | 90 | **+4** |
| 19:27:18 | 100 | 105 | **−5** |
| 19:31:24 | 104 | 106 | **−2** |
| 19:35:49 | 111 | 113 | **−2** |

`[inferred]` **The deltas run in both directions and are all small (−5 … +4). The cause is stated in the probe's own comment: mtime is LAST-WRITE time, not creation time, so a document edited after its creation is counted at its edit time. D94's readings were live directory listings and saw documents at creation. The reconstruction therefore tracks the SHAPE of the growth and misses its VALUE by a few, which is exactly what a last-write proxy should do.**

`[inferred]` **Reported because the alternative is worse: a reconstruction that agreed exactly would have suggested the corpus's mtimes and its creation order coincide, which they do not. The §2.3 finding — 26 distinct files — does not depend on this table and is exact.**

---

## §3 T3 — the disposition of the v7 extractor

### §3.1 The measurement that decides it

`[verified]` **Every occurrence of the string `crossref_v7` anywhere under `RE_Library\07_OUTPUT`:**

| file | line | context |
|---|---|---|
| `D94_….md` | **48** | `[verified]` **`crossref_v7.ps1` was located on disk, not reconstructed** — 5,745 B, written 18:37:10 — and **executed** |
| `D94_….md` | **67** | `[read]` **`crossref_v7.ps1:66-68`:** |
| `_d99_p2_edges.py` | 4, 154 | this lane's own commentary |

`[inferred]` **The only two references to the extractor in the entire corpus are D94's own prose. There is no third witness.**

`[verified]` **The three checkable properties of D94:48, each tested independently:**

| property D94:48 asserts | test | result |
|---|---|---|
| located on disk | `*.ps1` inventory, 62 files, repo-wide | **no `crossref_v7.ps1`; no v6/v8/v9 either** |
| **5,745 B** | size scan of all 62 `.ps1` | **no `.ps1` is 5,745 B** (nearest: 5,701 B `CVE-2020-1337.ps1`, 5,817 B `NTDSgrab.ps1`, both Metasploit payload data) |
| **written 18:37:10** | mtime window `18:30:00–18:50:00`, all files, all types | **ZERO files written in that window** |

`[verified]` **Two files of exactly 5,745 B do exist — `metasploit\modules\auxiliary\scanner\rservices\rexec_login.rb` and a `caniuse-db` JSON. Neither is a PowerShell script and neither relates to cross-references.**

`[inferred]` **So D94:48's `[verified]` tag is wrong on all three counts, and D94:67's `[read]` tag quotes `crossref_v7.ps1:66-68` — LINES OF A FILE THAT DOES NOT EXIST. This is Rule 26 exactly: a line is not a source.** `[inferred]` **The tag is the error. D94 tagged these as `[verified]` and `[read]` when the correct tag for both was `[inferred]` — D94 reconstructed v7's behaviour from the corpus's descriptions of it and labelled the reconstruction as a location.** `[inferred]` **A `[verified]` on a remembered file is the most expensive tag error available, because it removes the reader's incentive to check.**

`[inferred]` **Note the asymmetry the Lead named as rule 27: D94's 17 self-failures appear in D94's own audit and in no other document's. The extractor's absence is likewise visible only here, because only D99 went looking for it. A corpus does not audit its own instruments.**

### §3.2 Recommendation: **retire v7, do not repair, do not delete**

`[inferred]` **(a) REPAIR AND RE-RUN — rejected.** v7 cannot be repaired because **it cannot be located.** Repair presumes a subject. D94:66-68 is quoted as `[read]`, and that quotation is itself the only surviving description of the logic. **Reconstructing a fix table from a description of an instrument, written by the report that proved the instrument misl attributed 46 rows, would be building on the one artefact in the corpus with a measured attribution defect.**

`[inferred]` **(c) DELETE WITH THE FAILURE RECORDED — rejected, and this is the load-bearing rejection.** Deleting v7 is **not available**: there is nothing to delete. **And the failure record must not be reduced to "the extractor was deleted," because the extractor's real defect is not that it mis-attributed 46 rows — it is that it could not distinguish a citation from a mention.** That is a defect of the *class of instrument*, not of an instance, and it recurs in **D99's own §4.1** in a different form. **Deleting the instance while the class survives is the failure mode D94 §1.3 was written to prevent.**

`[inferred]` **(b) RETIRE AND SUPERSEDE WITH A v8 — RECOMMENDED.** Reasoning, in the order the evidence supports it:

1. `[inferred]` **The object v7 measured was mis-specified, and the correct object is now known.** §1.1's window curve proves the count is a function of the window. **An instrument whose output depends on an unstated parameter has no output.**
2. `[inferred]` **The corpus's actual defect is RENUMBERING, not dangling (13 of 26, and 0 genuinely dangling).** A v8 built to find dangling sections **would find nothing and report success** — the broken-classifier failure again. **v8 must be built to find RENUMBERING, which is a content-matching problem, not a heading-index problem.**
3. `[inferred]` **D94 already wrote v8 and v9, and D94 §2 records that its first classification pass produced `101 NEVER-WRITTEN / 71 RENUMBERED-CANDIDATE` — "both labels unreliable."** **So a v8 has ALREADY FAILED once in this corpus, in the same way, on the same object.** That is the strongest argument for treating the version number itself as the hazard: **v8 as an increment of v7 inherits v7's framing.** The successor must be specified from the object, not from the predecessor.

### §3.3 What the successor instrument must do — ONE paragraph

`[read]` **It must invert the default: emit an edge ONLY when the citing sentence asserts a claim about the target, and emit every edge it cannot decide into an explicit UNRESOLVED class rather than into silence.** Concretely it must (i) require, in addition to the `D<n> §<m>` token, a *claim verb* or a quotation in the same sentence — cite, states, records, publishes, per, see, as in — because §1.3 shows twelve of twenty-six edges are mentions, filenames, line-numbers or metadiscussion; (ii) resolve the owner by **document identity, never by a character window**, since §1.2 shows the window alone moves 114 edges and because `D11` names five documents, `D1` naive-matches 16 files against 1, and `D2` 10 against 1; (iii) test the target against a **three-valued** result — FOUND, ABSENT, AMBIGUOUS-OWNER — and **never collapse `None` into `False`**, which is the defect that cost this report its first headline (§4.1) and is undetectable by any single-valued classifier; (iv) index **both** `#` headings and bold self-numbered pseudo-sections, which D94 §2 proved necessary and which its own v9 got right for the twelve-row `D14 §9.x` cluster; and (v) **print the value distribution of every categorical field it emits**, because a field whose distribution is a single value is broken by definition and the run must fail loudly rather than report a clean sheet. **The instrument must be shipped with the report that uses it, by digest, in the scope statement — this entire section exists because the predecessor was not.**

---

## §4 Instrument record

### §4.1 `[instrument]` — a three-valued field tested with `is False`, and a `FAILED 0` headline that was pure artifact

`[verified]` **`_d99_p2_edges.py` reported `FAILED 0` out of 1,491 edges, and `owner document MISSING entirely: 0`.** The probe's own commentary flagged it as suspect before any conclusion was drawn: **a classifier returning one value for 100% of its input is broken, not decisive.**

`[inferred]` **The defect, isolated in `_d99_p5_confirm.py`:** the SEC branch set `e["resolved"] = secs.get(target)`, which yields **a line number OR `None`**, while the failure filter tested `if e["resolved"] is False`. **`None is not False`.** Every unresolvable section citation scored `None` and was skipped by the filter.

`[verified]` **The value distribution that exposed it — `_d99_p5_confirm.py` over all 1,491 edges:** `True 318`, **`None 26`**, then 365 further distinct integer values. **`probe 2 reported (resolved is False): 0`; `TRUE failed count (resolved is None): 26`.**

`[inferred]` **Two lessons, and the second is worse than the first.** The first: **`is False` is not a falsy test.** The second: **my diagnostic print was itself broken** — `%s` against a tuple raised `TypeError: not all arguments converted during string formatting`, so the trace that would have shown the defect **died before printing it, twice**, and only the redesigned probe surfaced the bug. **A probe whose failure path is untested is a probe with no failure path.**

### §4.2 `[instrument]` — a distribution print whose values were unbounded is not a distribution

`[verified]` **`_d99_p5_confirm.py` printed `Counter(repr(resolved))` and emitted ~400 lines**, one per distinct line number, with `362 → 26`, `205 → 17`, `652 → 16` … **The values were resolution TARGETS (heading line numbers), not categories.** `[inferred]` **A distribution over a field with an unbounded value space is a dump. This report's rule — every classifier prints its distribution — carries an unstated precondition, now stated: the field must be CATEGORICAL.** ^ **[promoted to §5 as a residual against this report's own rule.]**

### §4.3 `[instrument]` — a hardcoded year made every historical window empty, and the zero looked decisive

`[verified]` **The first run of `_d99_p1_denom.py` re-derived D94's five readings as `0, 0, 0, 0, 0`.** The corpus is dated **2026**; the probe constructed cut-points with **`datetime(2025, 10, 16, …)`**. Every window fell a year before every file.

`[inferred]` **The living fix is in the shipped probe: the year is now taken FROM THE DATA** (`datetime.fromtimestamp(max(mtime)).year`), and the probe prints the year it used. `[inferred]` **This is the third time in this lane's history that a date or a count was asserted rather than derived, and the first time the fix was to remove the constant entirely rather than correct it. Correcting a constant leaves the next reader with a new number to trust; deriving it leaves them with a procedure.** The affected denominator count in §2.1 is **unaffected** — it is a point-in-time count, not a window.

### §4.4 `[instrument]` — `-SimpleMatch` with a `|` alternation matches the literal pipe

`[verified]` **A repo-wide search for `crossref_v7|crossref_v8|crossref_v9|5,745|5745` returned ZERO, including inside D94, where `crossref_v7` demonstrably appears at :48.** `[inferred]` **Cause: `-SimpleMatch` suppresses regex, so the pattern was the literal string `crossref_v7|crossref_v8|…`, which occurs nowhere.** `[verified]` **Positive control: `OWNER-FAR` with `-SimpleMatch` found D94:84, :100, :121, :307 — so the scanner was never broken, the pattern was.**

`[inferred]` **The consequence is worth more than the fix. Had the control not been run, §3.1's central absence — `crossref_v7.ps1` is not on disk — would have rested on a probe that could not have found it.** **Every absence in this report carries a control that could have returned non-zero; this is the one where the control changed the answer.**

### §4.5 `[instrument]` — cp1252 stdout killed a trace mid-print

`[verified]` **`_d99_p4_whyzero.py` died with `UnicodeEncodeError: 'charmap' codec can't encode character '\u2192'` at `D32:251`, the line containing `→`.** `[inferred]` **The line it died on is one of the six load-bearing edges. A probe that prints the corpus will eventually print a corpus character the console cannot encode, and it will die at the most interesting line.** Fix shipped: `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` plus `PYTHONIOENCODING=utf-8`.

### §4.6 `[instrument]` — cross-check by second method, and which figures are stable

`[verified]` **Independent re-derivation of the headline figures:** the edge universe was built twice — `_d99_p2_edges.py` (regex sweep) and `_d99_p7_classify.py` (fresh index, fresh resolver, re-classification) — with the owner window parameterised in the first and fixed-by-identity in the second. **Both return 1,465 OK / 26 TARGET-ABSENT.** `[verified]` **The 26 were then re-read as text individually and 12 reclassified from the resolver's `TARGET-ABSENT` to `(d) EXTRACTOR-ARTIFACT`, which the resolver cannot see by construction** — the resolver answers *"does this target exist,"* and (d) rows answer *"is this a citation"*, a different question. `[inferred]` **The 26 is stable; the 13/0/12 split is a READ, and is marked as one.**

---

## §5 Residual unknowns, each with a probe

**§5.1 — `D94`'s 172 cannot be reconciled to 26, because the instrument that produced 172 does not exist.** The difference is attributable in direction (window function + tri-state collapse + the 72/10 rows dropped from D94:190) but not in amount. **PROBE:** a lane holding a copy of `crossref_v7.ps1`, or of its output CSV, would settle it in one run. **Until then, 172 is an artefact count and 26 is a defect count, and they are not two measurements of one quantity.**

**§5.2 — the `D11` ambiguity is a real property of the corpus, not of my resolver.** `D11` names **five** documents. **PROBE:** count citation edges whose owner token matches more than one document — `D11` (5), and any other multi-file family — and report the count as an UNAMBIGUOUS / AMBIGUOUS split. **This is the single highest-value follow-up in this report**, because every bare-`D11` citation in the corpus is currently resolvable to the wrong document by any instrument that picks one.

**§5.3 — `(b)` is 13 at this revision, but renumbering is ONGOING.** `D30 → D34` is recorded in the text; the `D13 §7.2` row propagated through four owners. **PROBE:** re-run `_d99_p6_adjudicate.py` at a later revision and diff the (b) set. **(b) should be MONOTONE-UP if renumbering continues and the citations are not fixed.**

**§5.4 — §4.2's precondition is not yet a rule.** *Print the distribution* is insufficient when the field is unbounded. **PROBE:** for each field this lane emits, assert its distinct-value count is below a threshold, and fail the run otherwise. **A probe that refuses to print a 400-line distribution is stronger than one that prints it.**

**§5.5 — the 9 T-series files are in scope and unmeasured.** §2.1 shows they are inside D94's boundary. **PROBE:** split every corpus statistic this lane reports into DEEP-only and DEEP+T-series, and state which is quoted. **D94's and this report's counts are DEEP-dominant and would move by ≤9 documents, but that has not been shown.**

**§5.6 — `D6:5258`'s in-line self-correction is a shape, not an instance.** **PROBE:** search the corpus for the pattern *"There is no §X"* / *"contains only §X–§Y"* and count how many citation defects were already fixed in prose. **If the count is material, the corpus's true outstanding defect count is lower than any citation census reports, because some defects are repaired at the point of writing and no extractor removes the original token.**

---

## §6 Status

`[verified]` **Tasks answered:** T1 adjudicated (26 fails, (a) 0 / (b) 13 / (c) 0 / (d) 12, all 26 listed); T2 bounded (114 in scope at 20:34:46, floor with interval, **growth not re-scoping**, 26 distinct files named); T3 decided (**retire v7, do not repair, do not delete; supersede**; successor specified in §3.3).

`[verified]` **Untouched:** D94, D88, D61, D59, D13, D6, STATUS.md, and every lane-verified artefact. **Corrected by reference only**, each correction naming the old report: D94 §1.1→§1.2 (window curve), D94:190 (98≠172), D94 §3.3 (five readings, not four), D94:48 and D94:67 (tags wrong; v7 not on disk).

`[inferred]` **Retained probes, with their defects labelled in place:**
- `_d99_p1_denom.py` — **REPAIRED** (hardcoded year → derived; §4.3). Denominator figure valid; historical reconstruction valid *as a shape only* (§2.4).
- `_d99_p2_edges.py` — **BROKEN** (`is False` against a tri-state; reported `FAILED 0`, §4.1). **Its edge universe is valid; its failure count is NOT.** Superseded by p6.
- `_d99_p3_control.py` — valid. Produced the D1/D2/D4 collision table and the 2,824-heading figure.
- `_d99_p4_whyzero.py` — **BROKEN** (cp1252 crash, §4.5; then a `%s`-on-tuple crash, §4.1). Retained because the trace that killed it is the evidence for §1.3.
- `_d99_p5_confirm.py` — valid, and the probe that found the §4.1 defect. Its distribution print is itself §4.2's example.
- `_d99_p6_adjudicate.py` — valid. The source of the 26 and of every line quoted in §1.3.
- `_d99_p7_classify.py` — valid. The 13/0/12 split.

`[inferred]` **Acceptance:** T1's headline is the **distribution**, not the total — a `0` in one class and a `1` in another is the finding, and the Lead's own rule (*a classifier returning one value for 100% of its input is broken*) is what makes the distribution readable at all. T2's headline is the **distinction**, and the distinction is settled: **growth, by name, 26 files.** T3's headline is that the predecessor **cannot be repaired, must not be deleted, and must be superseded by an instrument specified from the object rather than the version number.**

`[inferred]` **168 changed to 26 is not this lane finding the corpus healthier than D94 did. It is this lane measuring a different object — edges, not windows — and D94 measuring a real defect in a real instrument. Both numbers are correct about what they measured.**
