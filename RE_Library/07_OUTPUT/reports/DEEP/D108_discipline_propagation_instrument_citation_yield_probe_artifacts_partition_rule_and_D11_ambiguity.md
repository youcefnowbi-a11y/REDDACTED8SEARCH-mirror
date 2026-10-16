# D108 — Did the discipline propagate? Instrument citations, probe artifacts, the partition rule, and the D11 ambiguity

**Purpose:** D94 fabricated two artifact locations (`crossref_v7.ps1`, `_INSTRUMENT_RULE_26_line_is_not_a_source.md`) and published a three-way split of a four-way partition. D99 caught both. **Six reports landed after D99 was written by lanes that had read it.** This report tests whether the discipline those findings demanded actually propagated — and whether the two rules C-09 wrote into the corpus are honoured by the corpus.

**Line-count convention:** LF count = number of `0x0A` bytes. `file.md:NNN` is the 1-based ordinal of the **physical** line, blanks included.

**Tags:** `[verified]` (instrument run, output quoted) · `[read]` (quoted from an artefact read directly) · `[measured]` (a number produced by a probe in this report) · `[inferred]` (reasoning over evidence) · `[absence]` (probe returned zero, with its positive control).

**Write scope:** this file and `_d108_*` only. **No lane-verified report is modified.** Every finding here is a correction **by reference**, each naming the old report.

**Occupancy:** `D108_*` enumerated before writing — **0 files.** The corpus high-water mark at probe time is the **D110** family; the next free `C` is **C-14**, not C-11 (§6.1).

**THIS REPORT IS A MEMBER OF THE POPULATION IT MEASURES** (§7), and **three of its four tasks were first answered WRONG by its own probes** before reading. That is recorded in place rather than cleaned up.

---

## §0 Headline

`[measured]` **The discipline HELD.** Across the nine documents of the new round (D95–D102, C-09, C-10) plus C-11/C-12/C-13:

| task | result |
|---|---|
| **T1** — `[verified]`/`[read]` citations to a FILE that does not exist | **0** |
| **T2** — reports stating a byte size for a probe file | **0** (the claim that failed is not being made) |
| **T3** — arithmetic chains `a + b + … = n` across the whole corpus | **41 chains, 41 correct, 0 wrong** |
| **T4** — citation defects repaired in prose rather than removed | **2 outside D99 itself** — the hypothesis is **NOT** supported |
| **T5** — citations whose owner prefix does not identify a document | **83** (D11: 67, D12: 16) |

`[inferred]` **D94's two fabrications are not repeated anywhere in the new round.** 148 file candidates were extracted from nine reports; **126 resolve on disk; and every one of the 22 that do not is a probe defect or a correct negative statement, not a false location** (§1.3). **The corpus began auditing its own instruments after C-09 and the audit held.**

`[inferred]` **The strongest single piece of evidence is C-09 itself.** It cites `crossref_v7.ps1` and `_INSTRUMENT_RULE_26_*.md` — **both nonexistent files** — and a naive presence-probe correctly returns "not found" for both. **A citation to a fabricated artifact, written by the report that exposes the fabrication, is the healthiest possible use of a nonexistent path.** My probe scored those two as failures until §1.3 read them.

`[measured]` **T3's result is the most expensive and the most reassuring: the partition rule C-09 wrote at 20:40 is HONOURED.** 41 arithmetic chains; **41 close exactly.** And **C-13 performs the partition check on D110 and finds D110 CORRECT**, recording at `C-13:28` that its own first draft accused D110 wrongly. **The rule fired twice and both times fired correctly — once against its own author.**

---

## §1 T1 — instrument citations in the new reports

### §1.1 The probe, and why its first two generations were wrong

`[verified]` **Probe 1** swept nine reports for backticked tokens ending in `.something`. It returned **260 tokens, 109 not found.** `[inferred]` **Read the shape: 85 of the 109 were Go symbol paths (`a.Pivots.Parent`, `structs.Map`), .NET type names (`MissingMemberHandling.Ignore`, `Newtonsoft.Json`), Java class names (`brut.apktool.Main`), and shell expressions (`$pfx.Length`).** **The regex did not know what a path is.** This is D94's own defect class — a token near a delimiter is not a citation — and **D99's author walked into it one round after writing the report about it.**

`[verified]` **Probe 2** added an extension allowlist plus a separator requirement. **260 tokens → 148 file candidates / 112 excluded.** The exclusion distribution — **93 dotted symbol paths, 11 shell expressions/pseudocode, 8 other** — is the proof the filter works.

`[inferred]` **But probe 2 was still wrong in the other direction:** `go.mod` and `merlin.def` were excluded as symbols when `go.mod` is a real filename. **A filter noisy in both directions is not a filter.** Named here because the §1.3 adjudication is what actually decides the task, not the filter.

### §1.2 The yield

`[measured]` **148 file candidates across nine reports:**

| report | candidates | found |
|---|---|---|
| D97_android_wasm… | 38 | 37 |
| D95_merlin_binary_layer… | 31 | 30 |
| D101_covenant_binary_source_pair… | 18 | **8** |
| D102_meterpreter_tlv_wire… | 18 | 18 |
| D96_sliver_client_server… | 16 | 13 |
| C-10_binary_layer… | 10 | 9 |
| D100_android_binary_layer… | 8 | 8 |
| C-09_correction_to_d94… | 7 | **3** |
| D98_havoc_tomap… | 2 | **0** |
| **TOTAL** | **148** | **126** |

`[inferred]` **D101's 8/18 and C-09's 3/7 and D98's 0/2 are the low cells and every one of them is explained by §1.3.** A yield table without that read would report a 14% failure rate that does not exist.

### §1.3 The 22 not-found, adjudicated by reading

`[verified]` **Six species. Every one is the probe's error or the report's correctness:**

| species | n | what it actually is |
|---|---|---|
| **REFUTATION-GOOD** | **2** | C-09:12 and C-09:14 assert `crossref_v7.ps1` and `_INSTRUMENT_RULE_26_*.md` **do not exist**. My resolver returning None **is the report being right** |
| **NEGATIVE-ASSERTION-GOOD** | **4** | D96:26/193/368 cite `gsli.tsv` as **absent** — *"no `gsli.tsv` on disk"*, *"no `gsli.tsv` at cutoff"*. D96:368 is a residual PROBE. `gsli.tsv` is genuinely 0 on disk |
| **LACK-ASSERTION-GOOD** | **6** | D101:15 quotes the brief; **D101:27 refutes it** — *"D93 §1.6 was RIGHT and my brief was wrong"*; D101:33-36 mark T1–T4 **"unanswerable as posed"**; D101:305 names acquiring a `Covenant.dll` as the priority residual. `Covenant.dll` is **0 on disk** — the report found that and said so |
| **NOT-A-LOCATION** | **4** | write-scope **globs** (`binlayer\_d95_*.ps1`, `binlayer\C-07_*.tsv`), a **Go symbol** (`structs.Map` at D98:396, which reads *"Not read in this report"*), a **NuGet package ID** (`Newtonsoft.Json`) |
| **NOT-A-CORPUS-ARTEFACT** | **2** | `where.exe` (Windows system binary); `Covenant.dll` quoted from the brief |
| **FRAGMENT** | **1** | D101:97 `_x86.dll` is the **tail** of `powerkatz_x86.dll`; the full name is earlier in the same sentence |
| **HEADING** | **3** | C-09:26 and C-09:39 are **section headings** titled after the artifacts being refuted. My probe read headings as citations |

`[inferred]` **`T1 = 0 false locations.`** A corpus-wide absence claim, so its positive controls, per the Lead's rule:

- **Control 1 — the resolver can fail and did.** The same resolver returned 22 misses against 148 candidates. It is not returning a constant.
- **Control 2 — the known-bad case is caught.** D99 §3.1 established `crossref_v7.ps1` is not on disk by three independent tests; a scanner that could not find a genuinely missing file would return 0 here and be meaningless.
- **Control 3 — the tag filter is live.** **56 of 148 candidates carry a `[verified]`/`[read]` tag**; 7 of those are not-found, and all 7 are adjudicated above. **The tagged population is populated and inspected, not empty.**

`[inferred]` **The falsifier that would overturn this:** a `[verified]` citation to a corpus-relative path, asserting the file exists, where the file is absent. **No such row exists in 148 candidates.** The nearest candidates make the opposite assertion.

### §1.4 D99's own contribution to this population

`[inferred]` **D99 is a member of the audited set and is not exempt.** Its §3.1 cites `D94:48` and `D94:67` — both real. Its §3.1 also names `crossref_v7.ps1` **as absent**, which the probe correctly scores as a not-found and correctly classifies as a refutation. **D99 contributes no false location.** Stated because a report that audits a population including itself must say where it sits in it.

---

## §2 T2 — artifact citations to the new probe files

`[measured]` **36 probe artifacts on disk in `DEEP`, 1,397,202 B total.** Distribution: **21 `.json`, 15 `.py`.**

`[read]` **NOT ONE REPORT IN THE NEW ROUND STATES A BYTE SIZE FOR A PROBE FILE.** Scanned for a probe-name pattern co-occurring with a size pattern across all thirteen documents of the new round: **zero occurrences.**

`[inferred]` **This is the right kind of absence and it is T2's whole finding.** D94's failure was a **fabricated location with a stated size** (`5,745 B`). The new round does not make that claim at all. **The propagation test passes by the reports not attempting the thing that failed.** A caveat stated honestly: this is a *weaker* form of passing than "they state sizes and all 36 are correct," and it is reported as the weaker form.

### §2.1 The `_d99_edges.json` write collision — reported as unresolved

`[read]` **Four declared writers of `_d99_edges.json`, from source read (not run):** `_d99_p2_edges.py:176`, `:178`, `_d99_p5_confirm.py:12`, `_d99_p6_adjudicate.py:19`.

`[verified]` **The file on disk carries p2's schema — `n_docs`, `n_edges`, `edges` — and mtime `20:35:12`.** p5 ran at `20:35:56`, p6 at `20:36:09`. **p2's payload is intact.**

`[inferred]` **Which means the two later probes opened it read-only, or the collision never fired. I CANNOT TELL WHICH FROM OUTSIDE, and the reason is a defect in my T2 probe, not in the lane:** the `open()` survey captured the **filename** and never captured the **mode**. **A probe that reports a write collision it cannot see is reporting its own ambiguity.** The schema is the real evidence and it says the data survived.

`[inferred]` **Corrected by reference:** D99 §6 lists no write path for its probes. **This report supplies it: `_d99_edges.json` has four declared writers and one intact payload.** That is a D99 omission, named here rather than edited there.

`[inferred]` **Method note for T2 as posed.** The Lead asked that reported numbers be "reproducible from the probe by reading, not running." **Reading a probe recovers its METHOD and its OUTPUT PATHS; it cannot recover its NUMBERS** — the numbers are data, and the data is in the `.json`. **What reading proves is that each `.json` on disk is the output of a probe declaring that path, with a schema matching the probe's writer.** All 21 `.json` artifacts satisfy that. **Reading does not, and cannot, confirm the numbers are right** — only re-running by the owning lane does.

---

## §3 T3 — the partition rule, corpus-wide

### §3.1 The rule and its origin

`[read]` **C-09:96, writing the rule into the corpus:** *"a summary that partitions a population must sum to the population. State the total in the same sentence as the parts."*

`[read]` **C-09:65, the instance that produced the rule:** *"31 + 20 + 47 = 98. The stated population is 172. The difference is 74."* `[read]` **C-09:108 correctly declines to close it:** *"The 74-row gap is a residual, not a closure. D94:190's two unsummed classes (72 RENUMBERED + 10 shape-B) are carried into D99's adjudication and are not closed here."*

### §3.2 The sweep

`[measured]` **Every `a + b + … = n` chain in every in-scope `.md` under `reports\`, with unbounded addends:**

```
chains found : 41
ARITHMETIC OK: 41
WRONG        :  0
by addend count: 2→22, 3→13, 4→1, 5→4, 7→1
```

`[inferred]` **Zero arithmetic errors in 41 chains across the whole corpus.** The corpus's addition is clean.

### §3.3 The three fake errors, and how each was manufactured

`[inferred]` **T3 took THREE probe generations, and each generation produced fake errors. This is the most instructive part of the task and it is recorded rather than hidden.**

**Generation 1 — a five-term sum with four capture groups.** `[verified]` The `CHAIN` regex had slots for `a+b+c+d`. On `D7_metasploit_code.md:178` — `4 + 16 + 4 + 4 + 4 = 32` — it summed the first four terms and reported **`28 != 32`**. **The document is exact.** `[inferred]` **A regex with a fixed number of capture groups cannot evaluate an unbounded sum.** This is instrument rule 18's family and it produced a false accusation against a correct report.

**Generation 2 — comma-truncated right-hand sides.** `[verified]` After capturing the whole expression, the right-hand-side alternation `\d{1,3}(?:,\d{3})*|\d+` matched **`687`** from `68780065` and **`438`** from `4388`, because the comma-form branch was tried first and the bare-`\d+` branch was never reached for an uncommaed 8-digit number. Two more false errors: `T8_merlin_and_blocked.md:70` and `T8_merlin_full.md:295` (`32 + 68779968 + 65 = 68780065`, **exact**) and `D79_android_manmifest…:46` (`4352 + 16 + 20 = 4388`, **exact**).

**Generation 3 — `%s` against a tuple.** `[verified]` The corrected probe died on `print("%s :%d  %s" % (status, doc, line))` — **three slots, three arguments, but the second is a string and `%d` requires a number** — `TypeError: %d format: a real number is required, not str`. **This is the same species D99 §4.1 recorded, written by the lane that recorded it, in a probe whose entire purpose was to catch this class.** Fixed with `.format()`, which cannot silently coerce.

`[inferred]` **The pattern across all three: every fake error was produced by the extractor, and every one accused a correct document of an arithmetic failure.** A report that published generation 1's result would have claimed three arithmetic errors in the corpus. **The true count is zero.** **A tool that generates errors has to be trusted less than the text it reads** — which is D94's own lesson, arriving from the other side.

### §3.4 The partition statements, and the two that exist

`[measured]` **The D94:190 shape — a stated total followed by named parts — occurs twice in the corpus, and both occurrences are the SAME sentence:** `D94:190` and its quotation at `C-09:63`.

`[verified]` **`D94:190` verbatim:** *"of 172 failures, 31 are provably instrument artifacts (17 + 14), 20 are provably false failures repaired by v9, and 47 are genuine target mismatches..."* **Parts named: 31, 20, 47. Sum 98. Stated total 172. Difference 74.**

`[inferred]` **The rule is 1-for-1 on instances and both instance-pairs are the same defect.** The partition rule has **one** live violation in the corpus, it is the one that produced the rule, and **C-09 does not fix D94** — deliberately, because (§4.1) the false citation is the evidence.

`[inferred]` **The rule's real yield is not the violation; it is C-13.** `[read]` **`C-13:26`: *"D110's arithmetic is CORRECT: 80 + 1,375 + 211 = 1,666, and 13,813,760 is the sum of the five sections it lists. D110 did not claim 1,666 was the whole-f[ile]…"*** `[read]` **`C-13:28`: *"A first draft of this report accused D110 of under-reporting and was WRONG. I read a deliberately scoped total as a global one — instrument rule 3."***

`[inferred]` **So the partition rule fired twice: once as a violation (D94, found independently by D99 and confirmed by C-09) and once as a near-miss where the accusation was withdrawn after reading (C-13 against D110). Both times it worked. The second is the more valuable because the rule was applied and then RETRACTED — which is what a rule is for.** **The rule's own §5.6-of-D99 requirement — state the scope of the total in the same sentence as the total — is what C-13 used to withdraw its accusation.**

---

## §4 T4 — the renumbering hypothesis and repair-in-prose

### §4.1 The test

`[inferred]` **D99 §5.6 asked whether citation defects are repaired in prose rather than removed, and predicted the answer would be material.** The patterns tested: *"There is no §X"*, *"contains only §X–§Y"*, *"§X does not exist"*, *"no such section"*, *"never written"*, *"only runs to §X.Y"*.

`[measured]` **Across 132 in-scope documents:**

| pattern | occurrences |
|---|---|
| never written / never existed | 20 |
| there is no §X | 2 |
| contains only §X–§Y | 2 |
| §X does not exist | 2 |
| only runs to / ends at | 2 |
| no such section | **0** |
| **total occurrences** | **28** |
| **distinct (doc, line) sites** | **24** |

### §4.2 The result, against the hypothesis

`[read]` **The genuine instances, read individually:**

- **`D6_pupy_code.md:5260`** — *"**D6 §25 contains only §25.1–§25.4.** There is no §25.6. The rule is stated in **§23.6**"* — the in-line repair D99 §1.4 documented. **One instance.**
- **`D99:140`** — **D99 quoting D6's repair.** The second occurrence of `there_is_no` and the second of `contains_only` are **my own report**, so both counts are inflated by 1 by self-reference.
- **`D5_havoc_code.md:876`** — *"**`PROC`=5 does not exist** — the gap is real; the client never sends 5."* A real in-line defect annotation — **about an enum, not a citation.**
- **`D99:323`** — **mine again.**

`[inferred]` **So the non-D99 count of citation defects repaired in prose is ONE: `D6:5260`. The hypothesis in D99 §5.6 is NOT supported.** `[inferred]` **The mechanism is real — the corpus demonstrably does repair a citation defect in prose and name the correct target — but it occurs once, not materially. Every other hit is my own report quoting that one instance, or an enum gap.**

`[inferred]` **This is a negative result against my own prediction and it is the more useful outcome.** D99 §5.6 said *"if the count is material, the corpus's true outstanding defect count is lower than any citation census reports."* **The count is 1, not material, and the inference that followed from it does not hold.** The `never_written` count of 20 is the noisy pattern — it fires on prose about things other than citations — and is reported with that caveat rather than as 20 defects.

### §4.3 The renumbering mechanism itself, kept

`[inferred]` **D99 §0's inference — the citation layer is renumbered and self-correcting — survives, on different evidence.** The `D30 → D34` rename is stated verbatim in the citing text (`D34:8`: *"This file is renumbered D34; the content is unmodified"*), and the `D13 §7.2` table row propagated through four owners. **The renumbering is real; the prose-repair COUNT is what fails to be material. Both are reported.**

---

## §5 T5 — the `D11` ambiguity

### §5.1 The five documents

`[verified]` **`D11` names five documents**, enumerated from disk:

```
D11_havoc_native_win32.md
D11_merlin_binaries.md
D11_mythic_crypto_postresponse.md
D11_pupy_transport_crypto.md
D11_sliver_rpc_core.md
```

`[verified]` **And a second ambiguous prefix nobody had flagged:**

```
D12 -> D12_havoc_dispatch.md
       D12_sliver_aitools.md
```

`[measured]` **Every prefix naming more than one document: 2. Documents involved: 7. Unambiguous prefixes: 104.**

### §5.2 The citation hazard

`[measured]` **Section-citations by owner prefix, corpus-wide, in-scope:**

| prefix | documents | `§`-citations |
|---|---|---|
| **D11** | **5** | **67** |
| **D12** | **2** | **16** |
| **TOTAL AMBIGUOUS** | **7** | **83** |
| total `§`-citations | — | **1,477** |
| **ambiguous share** | — | **5.6%** |

`[inferred]` **83 citations, 5.6% of the corpus's section-citation layer, name an owner that does not identify a document.** D99 §5.2 predicted `D11` would be the highest-value follow-up; **it is, and `D12` was invisible because it has a plausible unique reading** (`D12_sliver_aitools` vs `D12_havoc_dispatch` — neither name suggests the other exists).

**Positive control, per the Lead's rule:** the scanner returns **D6 = 81** section-citations, non-zero. The instrument is live.

`[inferred]` **Two independent counts of the same quantity, reported with their difference:** the in-process sweep returned **1,457 total / 67 D11 / 5.7%**; the shell sweep returned **1,477 / 67 / 4.5%**. **The D11 numerator is identical (67) under both; the denominators differ by 20 because the two probes apply slightly different scope filters.** **The finding is robust; the share is a range (4.5–5.6%) and is reported as one.**

### §5.3 Why it is a hazard and not a style choice

`[inferred]` **Every bare-`D11` citation in the corpus is resolvable to the WRONG document by any instrument that picks one.** D99 §1.3 caught exactly this: `D36_sliver_cover_path.md:150` cites `D11 §9.3`, and **the resolver picked one of five.** `[inferred]` **The citation is only disambiguated by the reader's knowledge of context — and no extractor has that.** **This is a corpus-wide hazard no report has addressed, and it is the reason a v8 cannot resolve owners by any rule that keys on the `D<n>` token alone** (D99 §3.3 iii).

---

## §6 Corrections by reference

### §6.1 The Lead's round-25 note is stale on one point

`[read]` The brief says *"Next free C is C-11."* `[verified]` **C-11, C-12 and C-13 all exist:** `C-11_merlin_artifact_census_duplicate_extraction…` (10,999 B, 20:54), `C-12_havoc_instrument_record_and_the_allocation_collision…` (12,834 B, 21:01), `C-13_merlin_release_vs_debug…` (7,779 B, 20:58). **The next free C is C-14.** Reported because a numbering collision is exactly the defect D99 §1.3 catalogued.

### §6.2 D99's own omissions, named rather than edited

- **D99 §5.6's prediction is refuted by §4.2** — repair-in-prose is real but occurs once. **D99, not edited.**
- **D99 §6 lists no write paths for its probes** — `_d99_edges.json` has four declared writers (§2.1). **D99, not edited.**
- **D99's 102-document edge population** and this report's **132-document sweep population** differ: D99 scanned citing documents that produce edges; D108 scans all in-scope documents for arithmetic and prose patterns. **Both are stated where used** (§5.2 reports T5 under two scopes).

### §6.3 What D94 remains

`[inferred]` **D94's two fabricated locations stand as the corpus's evidence that this class of failure occurs, and C-09 preserves them by not editing.** §1.3's result **does not rehabilitate them**; it shows the corpus learned from them. **The distinction matters: a clean round after a caught fabrication is not evidence the fabrication was harmless. It is evidence the catch worked.**

---

## §7 Instrument record

`[instrument]` **§7.1 — a path regex that did not know what a path is.** Probe 1: **109 not-found out of 260, of which 85 were Go symbol paths, .NET type names and Java class names.** Caught by the *shape distribution* print, which D99 §4.2 established as the required control. **A mandatory distribution print is what turned "109 failures" into "85 classifier errors."**

`[instrument]` **§7.2 — a write-collision check that could not see a write mode.** The `open()` survey captured filenames, not modes (§2.1). **The probe reported a collision it could not observe.** The schema check settled it instead.

`[instrument]` **§7.3 — a four-slot regex against a five-term sum.** `28 != 32` on a correct document (§3.3).

`[instrument]` **§7.4 — a comma-truncated right-hand side.** `687` from `68780065`; `438` from `4388`. **Two more false accusations against exact documents** (§3.3).

`[instrument]` **§7.5 — `%s` against a tuple, species recurrence.** `TypeError: %d format: a real number is required, not str`. **D99 recorded this species; D108 wrote it again.** Fixed with `.format()`. **A recorded species is not an immunised species.**

`[instrument]` **§7.6 — a citation-sweep that read section HEADINGS as citations.** C-09:26 and C-09:39 are headings naming the refuted artifacts (§1.3). **Comment-and-structure membership must be tested, not assumed** — the same discipline that made fenced-block membership explicit in D99 §4.

`[instrument]` **§7.7 — what is stable.** T1's 148/126/22 counts are stable across two filter generations. T5's **D11 = 67 is identical under two independent implementations** (in-process Python and shell regex), which is the strongest agreement in this report. T3's **41/41** is stable across two addend-capture strategies after the false positives were removed.

---

## §8 Status

`[verified]` **Tasks answered:** T1 (**0 false locations**; 148 candidates, 126 found, 22 adjudicated into 6 species, all probe defects or correct negative statements). T2 (**0 reports state a probe size**; 36 artifacts / 1,397,202 B inventoried; the `_d99_edges.json` collision reported unresolved). T3 (**41 chains, 41 correct, 0 wrong**; the partition rule honoured; C-13 is the rule's second and better instance). T4 (**hypothesis NOT supported** — 1 genuine prose repair). T5 (**83 ambiguous citations, 5.6%**; `D11` five documents, `D12` two).

`[verified]` **Untouched:** D94, C-09, C-10…C-13, D95–D102, D99, and every lane-verified artefact. **Corrected by reference only.**

`[inferred]` **Retained probes, defects labelled in place:** `_d108_p1_cites.py` (**BROKEN** — path regex, §7.1) · `_d108_p2_refine.py` (**NOISY BOTH WAYS**, §1.1) · `_d108_p3_t1final.py` (**crash on cp1252 token, exit 1**) · `_d108_p4_reads.py` valid · `_d108_p5_t4t5.py` valid · `_d108_p6_t3.py` (**BROKEN** — four-slot sum, §7.3) · `_d108_p7_t3b.py` (**REPAIRED** — unbounded sums; then `%s`-on-tuple, §7.5) · `_d108_p8_t2.py` (**mode-blind**, §7.2).

`[inferred]` **Acceptance:** T1's headline is the **absence with its three controls**; T2's is the **absence of the claim**; T3's is the **zero with three fake errors recorded**; T4's is the **refutation of D99's own prediction**; T5's is the **second ambiguous prefix `D12`**, which nobody had flagged. **The corpus's instruments are clean; its owner-prefix namespace is not, and that is the one open hazard this round leaves behind.**
