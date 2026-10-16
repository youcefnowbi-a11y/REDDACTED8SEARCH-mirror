# C-12 — INSTRUMENT RECORD: THE ALLOCATION COLLISION, THE LINE-COMMENT BLINDNESS, AND RULE 30

**Scope: instrument defects only.** No target findings. Four entries — one allocator defect with two halves, one blind spot in a census test, one correction with no prior home, and one inherited measurement hazard.

**Provenance of this file:** this is the document D105 §7.5 should have been. D105 claimed `C-11` for its correction entry **and created no file of that number.** `C-11` was already taken. **The claim had no referent.** That defect, and the resulting split, are entry 1 below.

**Tags:** `[verified]` read verbatim here; `[read]` read here without full quotation; `[inferred]` derived, NOT measured; `[absence]` a negative with its enumeration printed beside it.

---

## §1 — ENTRY 1: THE ALLOCATION COLLISION (RULE 30)

### 1.1 What happened

**A number was claimed twice, from two directions, and neither party knew.**

**Disk state, by enumeration with mtimes:**

```
C-00_binary_layer_method_and_merlin_confirmation.md                        11,050 B  19:41:25
C-08_ghidra_census_merlin_suite_symbol_asymmetry_and_toolchain_failures.md  9,426 B  20:30:50
C-09_correction_to_d94_two_fabricated_artifact_locations_and_unclosed_arithmetic.md  9,182 B  20:40:47
C-10_binary_layer_seven_targets_named_functions_one_signature_and_pclntab_substitution.md  10,399 B  20:47:23
C-11_merlin_artifact_census_duplicate_extraction_and_cross_platform_build_config_identity.md  10,999 B  20:54:06
```
[source: directory enumeration, mtimes as printed]

**The two halves, stated symmetrically and without softening either:**

| Half | Actor | Defect |
|---|---|---|
| **A** | **Havoc lane (this report's author)** | **Enumerated `C-11` free at 20:53:46 — correctly — then wrote `"C-11 is taken by this report"` into D105 §7.5 and CREATED NO C-11 FILE.** |
| **B** | **Merlin lane (Lead)** | **Wrote `C-11_merlin_artifact_census_...md` at 20:54:06 and committed it at `2818b67` — and never claimed the number.** |

**Both halves are the same defect: an allocation that existed only in one party's head or in prose.** **A prose claim is not a file. A file is not a claim.** **Neither half is sufficient on its own; both are required.** [source: Lead message, allocation record; D105 §7.5]

### 1.2 Why the enumeration was not at fault

**The enumeration at 20:53:46 was correct at the moment it ran.** `C-11` did not exist on disk then. **A probe cannot report a file written 20 seconds later.** **The probe was sound; the protocol around it was not.** [source: D105 §0.1; mtimes above]

**This distinction matters and is recorded deliberately: the instrument worked, the allocator failed.** **Conflating the two would send the next fix at the probe, where nothing is broken.** [source: §1.1]

### 1.3 RULE 30

**RULE 30 — A RESERVATION THAT IS NOT WRITTEN DOWN DOES NOT EXIST.**

**Stated operationally:**
1. **Before writing a numbered artefact, allocate by enumeration** — list the namespace, print the mtimes, and confirm the number is free. **[done in both halves; this is not the failing step.]**
2. **Then TELL the other writers the number you are taking, before writing.** **A number announced only to oneself is not allocated.**
3. **Then create the file.** **A claim with no artefact is a phantom allocation and is indistinguishable from a mistake until someone enumerates.**
4. **All four steps are required. Any three are insufficient.**

**This is the allocator fix, and it is procedural rather than technical: no probe can see an intention, so the intention must be written down in a place the other party reads.**

### 1.4 Why this is NOT Rule 20

**Rule 20 is: *a named path is not a census.*** **Its defect is an incomplete enumeration presented as complete — the referent exists, the coverage is wrong.** [source: `_INSTRUMENT_RULE_20_named_path_is_not_a_census.md`]

**Entry 1's defect is different in kind: the referent does not exist at all.** **A claim — `"C-11 is taken"` — whose object was never created. It is unverifiable by reading the claim, because there is nothing to read.** **Filing this under Rule 20 would have buried the allocator defect inside a coverage defect, and the next writer would still not announce.** [source: §1.1; Rule 20 file above]

**It is closer to the `C-09` class: a citation to an instrument whose existence is asserted and not checked.** **C-09's own subject is fabricated artefact locations.** **Rule 30 carries it one step further back — the artefact was not fabricated, it was never made.** [source: `C-09_correction_to_d94_two_fabricated_artifact_locations_and_unclosed_arithmetic.md`]

### 1.5 Resolution applied

**D105 §7.5's correction entry is moved into this file as §3.** **D105 is not edited** — it is verified at 41,095 B / 717 LF and rewriting a verified artefact to fix an allocation is a second defect on top of the first. **The stale claim is left in place and corrected here, which is the pattern this corpus already uses.** [source: D105 §7.5; §3 below]

---

## §2 — ENTRY 2: THE BLOCK-COMMENT TEST IS BLIND TO C LINE COMMENTS

### 2.1 The blind spot, found in my own instrument

**D105 §7.2 recorded this.** **It is promoted here to a standing instrument rule, because it is a property of the test rather than of that report.**

**The comment-membership test as originally built:**
> for candidate line `n`, the line is inside a C block comment iff the last `/*` at-or-before `n` is later than the last `*/` at-or-before `n`.

**This test sees `/* … */`. It does not see `//`.** **A line commented with `//` is classified LIVE.** [source: D105 §7.2]

### 2.2 The measured instance

```
src/core/Command.c:72     // simply call SleepObf until we reach working hours or the kill date (if set)
```
**Classified LIVE by the block-only test.** **It is a line comment.** [source: `payloads/Demon/src/core/Command.c:72`; D105 §2.7]

### 2.3 Why it did not change D105's conclusions — and why that is not a defence

**No D105 §1 or §3 census hit depended on a line-commented line as a live hit.** **The `SleepObf` call-site census in §2.7 has two live sites (`Command.c:66`, `Demon.c:90`), neither of which is a `//` line.** **The block test's error was therefore non-load-bearing in that report.** [source: D105 §2.7]

**That is luck, not soundness.** **A test whose false-positive rate is unknown and was merely fortunate is not a validated test.** **The test is the instrument; its accuracy cannot be conditional on the population.** [source: §2.1-§2.2]

### 2.4 The fix, and it is now mandatory

**The comment test has TWO arms and both must be reported:**

1. **Block arm:** last `/*` at-or-before `n` later than last `*/` at-or-before `n` → inside a block comment.
2. **Line arm:** strip `//` and all following text **before** matching, on lines not inside a block.

**Required disclosure:** **the delta between the two arms must be printed.** **If the line arm removes zero additional lines, that is reported as a bounded zero WITH ITS ENUMERATION — not as silence.** **A zero from an unfired test is indistinguishable from a zero from a broken test unless the probe output is shown.** [source: C-08 Failure 3, "read the REPORT lines, not the exit code"; §2.1]

### 2.5 The compiler-adjacent limit, recorded so it is not mistaken for coverage

**Neither arm models: `#if 0` / `#ifdef` exclusion; `/*` inside a string literal; a `//` inside a string literal; or an unterminated block comment.**

**The `#if 0` case is the largest and is NOT detected by either arm.** **D105 §1.4 found the `Dotnet.c:226-306` region via the block arm; a `#if 0` region would have been invisible to it.** **No census in this lane has yet tested for `#if 0`.** **This is `[absence]` — a negative over a feature never probed.** [source: D105 §1.4; §2.4]

---

## §3 — ENTRY 3: THE D105 §7.5 CORRECTION ENTRY, MOVED HERE

**This is the text D105 §7.5 wrote, now in its own document and correctly numbered.**

**D89 §0.1's comment-region probe was written retrospectively — after the deadness at `agent.go:580` was noticed by eye.** **D89 §7 Failure 4 records that as the reason the mitigation became mandatory.** [source: D89 §0.1, §7 Failure 4]

**D105 was the first report in this lane to apply the test from the start (T5), and it found dead lines in two independent censuses:**

| Census | Matched | Removed by comment test | Rate |
|---|---|---|---|
| `Pivots` (Go, teamserver) | 51 | **10** | **19.6%** |
| `PackageCreate*` (C, Demon) | 42 | **2** | **4.8%** |

[source: D105 §1.4, §3.2]

**The correction is not to D89's finding, which stands.** **It is that a retrospective-only instrument under-reports, and the forward-applied instrument found dead lines at 19.6% and 4.8% in two fresh populations.** **Those rates are recorded because they bound how much a retrospective-only census can have missed.** [source: D105 §1.4, §3.2, §7.5]

**Restated as a rule: an instrument applied after a finding confirms the finding; an instrument applied before it measures the population.** **Both are legitimate; only the second yields a rate.** [source: §3]

---

## §4 — ENTRY 4: A RELOCATION-TABLE DIFF IS A LAYOUT ARTIFACT, NOT A BEHAVIOUR MEASURE

### 4.1 Provenance

**This entry records a measurement taken by the Merlin lane (Lead) by direct PE section-table parse, reported to this lane. It is recorded with its origin explicit — this lane did not take it and does not re-derive it.** [source: Lead message, independent verification of D110]

### 4.2 The measurement

```
.text     rawSize 6,180,864  DIFF     80
.rdata    rawSize 6,295,040  DIFF  1,375
.data     rawSize 1,206,784  DIFF    211
.pdata    rawSize   130,560  DIFF      0
.xdata    rawSize       512  DIFF      0
.idata    rawSize     1,536  DIFF      0
.reloc    rawSize   121,856  DIFF 62,896
.symtab   rawSize       512  DIFF      0
```
[source: Lead message, PE section-table parse of `merlinAgent-Windows-x64.exe` vs `-Debug.exe`]

**Total divergence 64,565 bytes (0.4632%).** **`.reloc` alone accounts for 62,896 — 97.4% of all divergent bytes.** **`.pdata` and `.xdata` are byte-identical.** **`.text` differs by 80 bytes.** [source: same]

### 4.3 The hazard this entry exists to prevent

**`[inferred]` — the Lead's reading, carried as inference and NOT as measurement:** **a 62,896-byte relocation divergence alongside byte-identical `.pdata`/`.xdata` is what results when the linker emits a different number of relocation entries because the section layout shifted.** **`-H=windowsgui` changes output section sizes, which shifts every subsequent RVA, which rewrites the relocation table.** **The divergence is large because it is DERIVED, not because 62,896 bytes of logic changed.** **`.text` at 80 bytes is the real code delta.** [source: Lead message; marked `[inferred]` at origin]

### 4.4 The rule

**A relocation-table diff is a layout artifact, not a behaviour measure.**

**Anyone reading "62,896 bytes differ" without the section breakdown will conclude the two builds are materially different.** **They are not: near-identical code, radically different layout bookkeeping.** **The correct primary measure of code divergence is `.text`, and the correct structural measure is `.pdata`/`.xdata`.** [source: §4.2-§4.3]

**This is the same class of hazard as D95 §3's 21-byte delta, which is `.rdata`-only and therefore undercounts total divergence by roughly three orders of magnitude.** **Undercount and overcount from the same cause: a single-section number presented without its section scope.** [source: Lead message; D95 §3]

---

## §5 — SUMMARY

| Entry | Defect class | Status |
|---|---|---|
| **1 — Allocation collision (Rule 30)** | **A reservation that is not written down does not exist. Two halves, one defect.** | **Rule 30 stated; resolution applied** |
| **2 — Line-comment blindness** | **The block-comment test cannot see `//`. Found in my own instrument.** | **Line arm now mandatory; delta must be printed** |
| **2.5 — `#if 0` blindness** | **Neither arm models preprocessor exclusion.** | **`[absence]` — never probed; recorded, not fixed** |
| **3 — D105 §7.5 correction** | **A correction with no home because its number was a phantom.** | **Moved here, correctly numbered** |
| **4 — `.reloc` layout artifact** | **A single-section diff read as a behaviour measure.** | **Rule stated; source attributed** |

**Two of these five were defects in this lane's own instruments.** **That ratio is recorded rather than summarised away: instrument defects are the highest-frequency finding class in this corpus, and the ones found in one's own tool are the ones that would otherwise have shipped.** [source: C-08 §5; D89 §7; D98 §7; D105 §7]

---

**End of C-12.**
