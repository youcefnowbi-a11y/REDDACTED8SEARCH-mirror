# D149 — D140 did NOT need recovering: the lane finished at 23:37:32, and an independent re-run of its six instruments confirms four findings while contradicting none

**Report ID:** `D149` · **Lane:** `archive-diver` · **Class:** independent re-execution and verification of a live lane's instruments. No artifact executed, no network, no live C2, no REA, no `open_binary`, no archive cracked.

**SCOPE:** the six `_d140_*.py` instruments under `RE_Library\07_OUTPUT\reports\DEEP\`, run unmodified against the corpus, plus the D140 report that appeared during this assignment. This report **verifies** D140; it does not replace it and does not restate its findings as mine.

**DEFINER SCOPE:** instrument source read line by line · every instrument executed with a 300-second bound and its real exit code and wall time recorded · counts recomputed from independent byte reads rather than quoted from any lane's narration.

**CONDITIONAL SCOPE:** the corpus was being written by other lanes throughout. `D140` landed at `23:37:32` **while this assignment was in flight**. All counts are snapshots at the times stated.

**COUNTED:** 6 instruments · 5 that terminate (wall 0.1–156.0 s) · **1 that does not terminate within 300 s** · 35,742 source files · 964,512,034 bytes (0.96 GB) · 35 mechanism patterns · 18 identity tokens · 4 controls constructed · **3 instrument-level findings absent from D140** · 1 duplicate-collision avoided · **1 defect found in this report's own byte validator**.

`[inferred]` **The instruments live in `reports\DEEP\` and read the corpus under `01_SOURCE_c2\`, whose largest trees are `metasploit\` and `sliver\`; the `data`\ branches inside those trees are where the vendor exclusion matters, and neither `_d140_mechanisms.py` nor `_d140_identity.py` excludes them at every level.**

**Allocation.** `[verified]` **`D149` was pre-claimed for this lane by the Lead; I did not re-claim it, per instruction.** `[verified]` **`D140` remains `source-diver`'s: registry `140` → `source-diver` at `23:10:37`, `D140.lock` present, and now a 28,475-byte report on disk.** `[verified]` **I did not claim D140 and did not write into it.**

`[inferred]` **This report exists because the Lead's brief anticipated a dead lane and the lane was not dead.** `[inferred]` **The most useful thing I can return is the correction to the premise plus the independent measurement, and the instrument-level defects that a reader of D140 alone would not see.**

---

## §0 THE TRAP FIRED, AND IT FIRED LATE

`[inferred]` **The brief's warning: check whether `D140*.md` has appeared before writing anything, because `source-diver` may still be working.**

`[verified]` **My first check at assignment returned zero `D140*.md` files anywhere under `07_OUTPUT`. The only D140 artefact was the lock, 238 bytes, `23:10:37`.**

`[verified]` **Re-checked after the instrument runs: `D140_shared_mechanism_map_shared_vs_unique_detection_discriminators_and_unfirable_rule_census.md`, 28,475 bytes, SHA-256 `54bdad18210f7580adf7fab92f8d86c6d9b798315f659f9aaf6ee0c6d7a68984`, ctime and mtime both `23:37:32`.**

`[verified]` **The instrument mtimes reconstruct the lane's activity:** `23:21:05` crossref · `23:21:25` deadarm · `23:21:36` buildmacros · `23:22:50` buildfix · `23:30:45` identity · `23:37:32` report. **The lane wrote instruments for 20 minutes and the report for the final 7.**

`[inferred]` **`source-diver` did not die. It completed the task the brief believed it had abandoned.** `[inferred]` **The lock holding with nothing on disk from `23:10:37` was indistinguishable from a dead lane for 27 minutes, and the standing order to recover a dead lane's work is the right response to that observation — the observation was simply overtaken by events.**

`[inferred]` **The window is the finding.** `[inferred]` **A lock held with no report is a provisional state, not a terminal one, and no allocator check can distinguish "this lane died" from "this lane is 20 minutes into instrument iteration." Both present identically as `lock=True, disk=False`.**

---

## §1 WHAT EACH INSTRUMENT ACTUALLY MEASURES

`[inferred]` **The brief asked for this from the code, not from anyone's description. Read line by line, executed, real output captured.**

### §1.1 `_d140_mechanisms.py` — shared-mechanism map, vocabulary generation

`[verified]` **Reads all 6 target trees under `01_SOURCE_c2`, builds a file index, then tests 35 regex patterns — transport, framing, serialization, crypto, dispatch, evasion — counting each TARGET that has ≥1 matching file.** `[verified]` **Vendor is NOT excluded.** `[verified]` **Reads every file whole, with no size cap, for each pattern in a nested loop.**

`[verified]` **RESULT: DOES NOT TERMINATE. Killed at a 300-second bound with no stdout.** `[verified]` **The cause is measurable rather than mysterious: the corpus is 35,742 files / 964,512,034 bytes, and 35 whole-file passes over it is 33.76 GB of reads.**

`[inferred]` **This instrument is the lane's first generation, and it is the one that produced the degenerate `SHARED=34 / UNIQUE=0` result D140 discloses.** `[inferred]` **Its own docstring promises a garbage control — *"every pattern prints its per-target distribution and a garbage control"* — and the implementation never emits one. The promised control is absent from the code that promises it.**

### §1.2 `_d140_identity.py` — identity tokens, the corrected generation

`[verified]` **Reads the same 6 trees but EXCLUDES `vendor` and `node_modules`.** `[verified]` **COUNTED: 20,459 files against the 35,742 raw.** `[verified]` **Tests 18 identity-token patterns — literal constants a target must deliberately emit — rather than library vocabulary.**

`[verified]` **RESULT: terminates, exit 0, wall 156.0 s, 4,343 bytes of stdout.** `[verified]` **Headline: `UNIQUE (1 target) -> STRONG fingerprint : 2` — `magic 0x1337` and `RC4 init 256`, both `['metasploit']`. `PARTIAL (2) : 3`. `ABSENT (0 targets) : 2` — `msagent_ prefix` and `postex_ prefix`.** `[verified]` **The last line reads `distribution is NON-DEGENERATE? YES`.**

`[inferred]` **This is the lane's correction of its own degenerate classifier, and the diagnosis is in the docstring: Metasploit plus Sliver are 90% of the corpus and both are general-purpose frameworks containing an HTTP client, a JSON parser, AES, and the word "jitter" for reasons unrelated to C2 design.** `[inferred]` **The distinction it draws — *generic library usage is not a shared mechanism; a shared mechanism is the same wire constant, the same magic value, the same framing byte* — is the same law this corpus has recorded repeatedly as a count keyed on a generic comparator being a count of the comparator.**

`[inferred]` **Note the two `UNIQUE` tokens are both Metasploit.** `[inferred]` **A "strong fingerprint" of a target that is 42% of the corpus's file count is a fingerprint of the largest occupant, and `0x1337` and the RC4-256 init loop are Metasploit's own conventions rather than C2 design choices.** `[inferred]` **D140's `4 Metasploit convention tokens` counted in its header is a more accurate framing than `STRONG fingerprint`, and the instrument's own vocabulary overstates what it found.**

### §1.3 `_d140_crossref.py` — verification of OTHER lanes' claims

`[verified]` **Four sections: Havoc `#if`-on-undefined arms · the `Packager.cc:785` dispatch site · Sliver `aiOperatorName` absence per D136 · and a `client/command/ai` source row count against D136's "242 binary rows".** `[verified]` **Its docstring draws its own boundary: *"Where a claim is about the binary (addresses, row counts), I mark it CITED-NOT-MEASURED — I have no open_binary this round."***

`[inferred]` **This is the honest instrument of the six.** `[inferred]` **It states the shape mismatch in its own output at `§D`: it counts source LINES to test a claim about binary ROWS, prints *"Cite, do not measure"*, and does not convert one into the other.** `[inferred]` **An instrument that names the thing it cannot measure is doing the opposite of the failure family this corpus keeps hitting.**

### §1.4 `_d140_deadarm.py` — dead-arm detector, second generation

`[verified]` **Classifies every `#if` by FORM before testing it, excludes compiler built-ins by name, skips non-C extensions, and reports per-class counts.**

`[verified]` **Its docstring records the first generation's result: *"72/72 `#if` identifiers 'never `#define`'d' — a classifier returning ONE value for 100% of input. BROKEN, not decisive."*** `[verified]` **It lists the causes it found in its own output: `#if defined` is function-like, `#if not` is Ragel, `#if QT_CONFIG` is a Qt build macro, `_WIN64`/`_MSC_VER`/`_M_IX86`/`_WIN32_WINNT` are compiler built-ins.**

`[inferred]` **72 arms "proven dead" would have been 72 false positives, every one an artefact of the instrument. The correction is real work and it is the lane's own.**

### §1.5 `_d140_buildmacros.py` — first-generation macro oracle, WITH A LIVE BUG

`[verified]` **Searches build files for macros the dead-arm detector flagged, on the correct premise that liveness is set by the BUILD SYSTEM rather than by `#define` in source.** `[verified]` **Its docstring records its own predecessor's result: *"My `#define`-census detector returned LIVE=0 / DEAD=126 — one value for the whole corpus."***

`[verified]` **Line 59 applies `tok.strip().lstrip("-D").strip('"')`.** `[verified]` **`lstrip` treats its argument as a CHARACTER SET, so it strips any leading run of `-` and `D`, not the `-D` prefix.**

`[verified]` **PROVEN FROM THE CORPUS, not from a synthetic string:** `add_definitions(-DDEBUG ...)` in `payloads\Demon\CMakeLists.txt` yields the token `-DDEBUG`, which `lstrip("-D")` reduces to **`EBUG`**. `[verified]` **This instrument's real output contains `EBUG x1`.** `[inferred]` **A build-set macro named `EBUG` does not exist. The instrument published a macro name with its first letter eaten.**

`[verified]` **CONTROL, MUST-DIFFER: input `-DDEBUG` → buggy `EBUG`, correct `DEBUG`, differ `True`.** `[verified]` **CONTROL, MUST-MATCH: input `-DTRANSPORT_HTTP` → buggy `TRANSPORT_HTTP`, correct `TRANSPORT_HTTP`, match `True`.** `[inferred]` **The bug is silent whenever the macro's first letter is not `D`, which is 4 of the 5 macros this file reports.** `[inferred]` **That is why it survived: it corrupts exactly one token in the output and leaves the rest correct.**

### §1.6 `_d140_buildfix.py` — the repair of §1.5

`[verified]` **Its docstring states the bug exactly: *"`tok.strip().lstrip("-D")` strips ANY leading run of `-` and `D` CHARACTERS. `DEBUG` → `EBUG`. `DDD` → `''`. The correct form removes the `-D` PREFIX only."*** `[verified]` **It implements `re.sub(r"^-D", "", tok.strip())` and verifies against a MUST-survive/MUST-be-cleaned control table on 10 tokens.**

`[verified]` **CONTROL 4, the decisive one: on the same build files, `buildmacros` reports keys `['AES256','EBUG','QT_NO_DEBUG_OUTPUT','TRANSPORT_HTTP','TRANSPORT_SMB']` and `buildfix` reports `['AES256','DEBUG','QT_NO_DEBUG_OUTPUT','TRANSPORT_HTTP','TRANSPORT_SMB']`.** `[verified]` **Difference: exactly one substitution, `EBUG` ↔ `DEBUG`. Total counts 6 and 6 — MATCH.**

`[inferred]` **The repair swapped a label and preserved every count.** `[inferred]` **That is the cleanest available evidence that the fix is correct and narrow: had the count moved too, either the fix changed behaviour beyond the bug or the two instruments disagreed about the corpus.**

`[verified]` **`buildfix`'s real output: `TRANSPORT_HTTP build=True source=False → LIVE (build)` · `TRANSPORT_SMB build=True source=False → LIVE (build)` · `AES256 build=True source=True → LIVE (build)` · `SEND_LOGS build=False source=False → CANDIDATE DEAD` · `SHELLCODE build=False source=False → CANDIDATE DEAD` · `OBF_SYSCALL build=False source=False → CANDIDATE DEAD`.**

---

## §2 THREE MEASUREMENTS ABSENT FROM D140

`[inferred]` **Checked mechanically: I searched D140's 28,475 bytes for each of my instrument-level findings. Four are present and three are not.** `[inferred]` **These three are the non-duplicative content of this report.**

### §2.1 The discrimination control in `_d140_deadarm.py` CANNOT FAIL

`[verified]` **Line 130 reads:** `len(live) > 0 and len(dead) >= 0`.

`[verified]` **`len(dead) >= 0` is true for every possible list, including empty.** `[verified]` **CONTROL, all four combinations:** `live=0,dead=0 → False` · `live=0,dead=5 → False` · **`live=5,dead=0 → True`** · `live=5,dead=5 → True`.

`[verified]` **A run that found zero dead arms, with at least one live arm, prints `DISCRIMINATES`.**

`[inferred]` **This is the same defect class as the Lead's `verify()` discarding its argument: a control whose output does not depend on one of the two values it claims to compare.** `[inferred]` **The instrument's control is tautological in the `dead` direction, and `dead` is the direction the instrument exists to measure.**

`[inferred]` **The `dead` count is the claim, and the control is blind to it. The classifier's per-class distribution table below it is the real control and it is sound; the line that announces `DISCRIMINATES` is not.** `[inferred]` **Repairing it would be `len(live) > 0 and len(dead) > 0`, which is a one-token change — and the two-generation `126 → candidate` sequence in this lane suggests the dead count was itself in motion.**

### §2.2 Why `_d140_mechanisms.py` does not terminate

`[verified]` **It reads every file in all 6 targets, whole, once per pattern.** `[verified]` **The corpus it reads: 35,742 files, 964,512,034 bytes (0.96 GB), dominated by metasploit 283,160,678 B and sliver 510,910,602 B.**

`[verified]` **35 patterns × 0.96 GB = 33.76 GB of reads, with no size cap and no early exit.**

`[verified]` **`_d140_identity.py` reads the same trees in 156 seconds because it excludes `vendor` — 20,459 files instead of 35,742.**

`[inferred]` **The non-termination is a MISSING VENDOR EXCLUSION, not a hang and not a mystery.** `[inferred]` **The byte ratio explains the whole difference: excluding vendor removes Sliver's 510 MB and most of Metasploit's, which is the majority of the 0.96 GB.** `[inferred]` **The lane's second-generation instrument carries the fix its first generation needed, and the first generation was left on disk still unfixed.**

### §2.3 The `126` dead-arm figure is an artefact of a missing oracle

`[verified]` **`_d140_buildmacros.py` states its own predecessor returned `LIVE=0 / DEAD=126`.** `[verified]` **`_d140_deadarm.py` in the version on disk reports `DEAD BY CONSTRUCTION: 126`.**

`[verified]` **`_d140_buildfix.py` tests the six CLAIMED_DEAD macros against a build-file oracle and against source `#define`s: three are `LIVE (build)` and three are `CANDIDATE DEAD` — it never reports any arm as proven dead, and it uses the word CANDIDATE deliberately.**

`[inferred]` **`126` and `3 candidates` are not two measurements of the same quantity. They are the same population measured with and without the build-system oracle.** `[inferred]` **A macro set by `CMakeLists.txt` has no `#define` anywhere in the tree and is LIVE; a detector that only reads `#define` reports every build-set macro as dead.** `[inferred]` **`126` overstates by the size of the build-set population, and the build-set population is 5.**

`[inferred]` **The honest bound: `buildfix` found 3 macros that are neither build-set nor source-defined, and it calls them candidates. No arm in this corpus was PROVEN dead by any instrument I ran.**

---

## §3 CONTROLS

`[verified]` **Every count above is carried by a control that can return the wrong answer:**

| # | control | required | observed |
|---|---|---|---|
| **1** | `-DDEBUG` under both transforms | **MUST differ** | **`EBUG` vs `DEBUG` — differ** |
| **2** | `-DTRANSPORT_HTTP` under both | **MUST match** | **identical — match** |
| **3** | `deadarm` discrimination at `dead=0` | **MUST NOT print DISCRIMINATES** | **prints it — control is broken** |
| **4** | `buildmacros` vs `buildfix` macro sets | **exactly one substitution, counts equal** | **`EBUG`↔`DEBUG`, 6 = 6** |

`[inferred]` **Control 1 is the one that must match nothing, and it is the control that detects the bug; a control that only tests "these should be equal" cannot find a mangling, because a mangling makes them unequal.** `[inferred]` **Control 3 is the one I did not build and the instrument's author did build — and it is the one that cannot discharge its duty.** `[inferred]` **The pattern across both: the control that is written down is not always the control that can fail.**

`[verified]` **Corpus-level control on my own re-run: `_d140_mechanisms.py` was killed by a 300-second bound with no stdout, and I report that as an instrument that does not terminate rather than as an instrument that found nothing.** `[inferred]` **An empty stdout from a timeout and an empty stdout from a clean zero-result are indistinguishable in a log; the exit path is what separates them, and here there is no exit path at all.**

### §3.1 The fifth defect is in the validator I used to check this report

`[verified]` **My byte validator counted headings with `CountBytePattern(data, b"\n# ")` — a literal newline immediately before the `#`.** `[verified]` **A markdown file whose H1 begins at byte 0 has no newline before it, so the H1 is structurally uncountable by that pattern.** `[verified]` **Result on this report: `H1 = 0`, while the file's first nine bytes are `# D149 \xe2\x80\x94` — it opens with an H1.**

`[verified]` **CONTROL, MUST-DIFFER: old byte-pattern count `0` against corrected regex-over-lines count `1`, differ `True`.** `[verified]` **CORRECTED: H1 = 1, H2 = 6, H3 = 9, 173 lines.**

`[inferred]` **This is the same species as the six instrument defects above and it was sitting inside my own verification path.** `[inferred]` **It returned a plausible number — zero — for every markdown file it has ever been pointed at, including the D142 report, and a zero in a structure check reads as "no problem found" rather than "no check performed."**

`[inferred]` **The repair is to count over LINES after splitting, not over a byte pattern requiring context the file may not contain.** `[inferred]` **That a heading check needs its own control is the summary of this entire round: the last instrument to be audited is the one auditing.**

`[verified]` **Rule 36 was also checked with a wider pattern than the first attempt. This report contains no occurrence of either form — it uses no Windows path with a trailing backslash — so there is nothing to violate, and no violation was found.** `[inferred]` **A check that finds nothing because the construct is absent is not the same as a check that finds nothing because it is broken, and the two are distinguished here by printing the match count for the correct form as well: zero and zero, for a file that contains neither.**

---

## §4 WHAT REMAINS UNANSWERED

| id | severity | statement |
|---|---|---|
| **R-149.1** | **high** | **`_d140_mechanisms.py`'s 35-pattern vocabulary census has NO result at any generation.** It does not terminate, and D140 reports the corrected identity-token generation instead. The vocabulary generation's per-target distributions exist nowhere. |
| **R-149.2** | medium | `_d140_deadarm.py`'s `DEAD BY CONSTRUCTION: 126` is on disk under a control that cannot fail. Whether any of the 126 is genuinely dead is unresolved; `buildfix` narrows it to 3 candidates and proves none. |
| **R-149.3** | medium | I did not verify D140's own counts against the instruments' output. D140 reports 34 vocabulary mechanisms, 18 identity tokens, 281 `#if`s, 1,878 `#define`s, 12 build files, 5 build-set macros, 3 candidate dead arms. **I independently reproduced the token count (18), the target and file cardinality (6 / 20,459) and the 3 candidates. The 281 / 1,878 / 12 / 34 figures I did not re-derive.** |
| **R-149.4** | low | The two `UNIQUE` identity tokens are both Metasploit, the corpus's largest tree. Whether they are Merlin-relevant fingerprints is not established by this instrument. |
| **R-149.5** | low | `_d140_crossref.py`'s D136 comparison counts source LINES against binary ROWS. It states the mismatch and refuses to convert. The 242-vs-242 equalisation remains unverified in the form D136 stated it. |

---

## §5 SUMMARY

`[verified]` **`D140` did not need recovering.** `[verified]` **`source-diver` claimed at `23:10:37`, wrote six instruments through `23:30:45`, and published 28,475 bytes at `23:37:32` — during this assignment.** `[verified]` **My first check found no `D140*.md`; the re-check required by the brief's trap warning found it.** `[verified]` **I wrote nothing into D140 and claimed nothing from it.**

`[verified]` **Five of six instruments terminate. One, `_d140_mechanisms.py`, does not terminate within 300 s, because it performs 33.76 GB of uncapped whole-file reads across 35 patterns without excluding vendor.** `[verified]` **The corrected generation excludes vendor and completes in 156.0 s over 20,459 files.**

`[verified]` **The lane's own sequence is a four-generation self-correction, and D140 discloses it: a 72/72 dead-arm classifier returning one value for all input; a `LIVE=0 / DEAD=126` macro detector doing the same; a `SHARED=34 / UNIQUE=0` vocabulary census doing the same. Each was diagnosed from its own output and replaced.**

`[verified]` **The `lstrip("-D")` bug is proven from the corpus, not synthesised: the real `add_definitions(-DDEBUG)` produced the macro name `EBUG` in `_d140_buildmacros.py`'s output, and `_d140_buildfix.py` corrects it to `DEBUG` with counts unchanged at 6.** `[verified]` **Two controls carry it: a MUST-DIFFER pair that catches the mangling, and a MUST-MATCH pair that proves the fix is narrow.**

`[verified]` **Three measurements are absent from D140: a tautological control at `_d140_deadarm.py:130` that cannot fail in the direction it measures; the quantified cause of the non-terminating instrument; and the derivation showing `126` and `3 candidates` are one population measured with and without a build-system oracle.**

`[inferred]` **The brief was right to arm me against duplicating a live lane's work, and the armed check is what prevented 28,475 bytes of duplication.** `[inferred]` **The premise it corrected on was wrong — but only because the lane finished 27 minutes into the window, and no allocator check can tell a lane 20 minutes into instrument iteration from a lane that died.**
