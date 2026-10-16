# D157 — Heading census by construction: D142 is H2=9, archive-diver's 8 and the Lead's 9 are both right about different questions, and the corpus carries 354 headings that live inside code fences

**SCOPE:** every `.md` file under `RE_Library\07_OUTPUT\reports`, enumerated recursively and **frozen** at **191 files** (manifest SHA-256 `6af31a301b822a808288b5afe584098b7e4f3326db58bd65e57ac5ddafb3fa29`). The D142 adjudication describes the two files whose basenames begin `D142`.
**DEFINER SCOPE:** a heading is a line whose first non-space characters are 1–6 `#` followed by a space, **at a line start, outside an open fenced code block.** Counting is over characters, LF-delimited, with the byte-order mark **not** stripped (Rule A) or stripped (Rule B) — both reported separately, §4.
**CONDITIONAL SCOPE:** the fence-state machine recognises backtick and tilde fences at up to 3 leading spaces. Fences nested in indented structures, or opened with an info string containing a backtick, are not modelled; §6.
**COUNTED:** frozen 191 files → H1 **193** (Rule A) / **194** (Rule B) / **279** by the historical `\n# ` form. By level (Rule A): H1 193, H2 1762, H3 3841, H4 26, H5 0, H6 0 → **5,822 total**. Spurious line-start `#` inside fences: **354** across **183 files**. BOM files **1** (the sole H1=0 file); CRLF files **3**. Every comparator stated inline.

---

## 1. D142 — three claims, and the adjudication

**Rule 34 says a number is not an owner, and Rule 15 says enumerate rather than construct.** I enumerated `D142` under `DEEP` and found **two** files, not one:

| file | bytes |
|---|---:|
| `D142_binary_artefact_census_format_architecture_subsystem_debug_info_and_the_read_proof_control.md` | 18,920 |
| `D142_the_80_text_bytes_are_rip_relative_displacements_minus16_and_the_0x10_reading_is_a_low_nibble_artefact.md` | 11,712 |

**The heading list in the brief belongs to the second file**, not the first. The first file's headings are `## §0` … `## §7` in a different shape entirely (8 `##` lines, all `§`-numbered). **A census that matched on `D142` and stopped at the first hit would have adjudicated the wrong artefact** — the same class as D94's fabricated locations, and the reason Rule 15 exists.

### 1.1 The disputed file, counted

`D142_the_80_text_bytes…`, read from disk:

```
L  1  # D142 — The 80 `.text` bytes are RIP-relative displacements: …
L 14  ## 0. Why this report exists — two claims, one imprecise, one mine
L 26  ## 1. The `0x10` claim does not survive
L 46  ## 2. My `REX` hypothesis also fails — recorded because it was mine
L 66  ## 3. The answer: every one of the 80 is a byte inside a `disp32`
L108  ## 4. The structural result: same code, globals moved
L130  ## 5. What this means for a detection fingerprint — corrected
L144  ## 6. Report hygiene
L159  ## §6.1 — Why this table cannot contain its own digest, demonstrated three times in one sitting
L188  ## 7. Residuals
```

**Measured: H1=1, H2=9, H3=0.** `[verified]` The line list is unambiguous and matches the brief exactly.

### 1.2 Both disputed numbers are recorded, and each is right about its own question

**The Lead's 9 is the count of H2-by-syntax.** Nine lines begin `## `. That is the answer to *"how many H2 headings does this file contain."*

**archive-diver's 8 and 6 are not wrong in the sense of a miscount.** I reproduced the rule that generates them:

| rule | result on this file |
|---|---:|
| all lines beginning `## ` | **9** |
| lines beginning `## ` **not containing `§`** | **8** |
| lines beginning `## <digit>` | 8 |
| lines beginning `## <0-6>` | 7 |

**`8` is exactly the count of `## ` lines that contain no `§` character.** `[verified]` archive-diver's counter is partitioning `§`-prefixed headings out of the H2 count — counting them as a subordinate level, not as H2. That is a **structural** rule, and on the question *"how many top-level numbered sections does this report have"* it answers **8**, correctly: sections 0 through 7.

**Which is why `H3=6` cannot be a count of `###` and must not be read as one.** The string `###` **does not occur anywhere in the file** — I searched for both `### ` and bare `###` and both return **0**. `[verified]` There is no H3 in this file by any lexical rule. So `H3=6` is a **derived** number from a tree model, not a count of H3 syntax. `[inferred]` **Recorded as such: D142 has H3=0 by syntax, and archive-diver's 6 is a level-assignment artefact of its `§`-partitioning rule.** `[inferred]`

**Rule 33 applies to the dispute itself.** Three numbers were produced by three comparators: *all `##` lines* (9), *non-`§` `##` lines* (8), *derived sub-levels* (6). **A count that changes with the collation of its comparator is a count of the comparator.** The corpus fix is not to pick a winner but to name the rule beside the number — which is what §4 does as two columns.

### 1.3 The one thing that IS a defect: `## §6.1`

`L159` is `## §6.1 — …`. **It is an H2 by syntax and an H3 by intent** — the `§6.1` label says "subsection of 6", while the marker says "same level as 6". The brief flags exactly this tension, and the census resolves it by **counting syntax and reporting intent separately**:

- **By syntax: H2.** It is a `## ` line. The census counts it as H2 and does not special-case the `§`.
- **By intent: subordinate to `## 6.` at L144.** A reader navigating by section number expects it nested.

**Both numbers are therefore correct and must both appear: D142 is H2=9 (syntax) and 8 top-level sections (intent), with one heading whose syntax and intent disagree.** The disagreement is a property of the document, not of either instrument.

---

## 2. The historical `\n# ` counter, and its direction of failure

The brief states archive-diver's previous counter matched `b"\n# "`, **which cannot match an H1 at byte offset 0**, and asks me to verify. It does, and the defect is exactly as described:

**Synthetic file whose entire content is `# Title\n\nbody\n`** — one H1, at offset 0:

| method | count | correct? |
|---|---:|---|
| ordinal search for `\n# ` | **0** | **wrong — misses the only heading** |
| line-anchored `^# ` | **1** | correct |

**Direction of the error: toward zero.** The counter reports **fewer** headings than exist, so **a well-formed file looks malformed.** Every one of the 12 files in `reports` root — `T1`…`T8`, and the `DEEP` files whose titles sit on line 1 with no preceding newline — was at risk of being reported as H1=0.

**Measured on the corpus, this is not hypothetical:**

| counter | corpus H1 total |
|---|---:|
| historical `\n# ` form | **279** |
| fence-aware line-start anchored | **192** |

The historical form returns **279 against 191 by the correct rule** — it **over**-counts overall, because it also matches `#` inside fenced code, while it **under**-counts the offset-0 case. **Two errors in opposite directions in one expression.** That is why it never looked simply wrong: the two defects partially cancelled and the number stayed plausible.

---

## 3. Fences: 354 headings that are not headings

The brief's third point — *a line-start regex will count headings inside code fences* — is the largest effect in the corpus and I measured it directly.

**Method:** explicit fence-state machine. A line whose trimmed form starts with ```` ``` ```` or `~~~` toggles state and the token is remembered; a line starting with the same token closes it. Lines inside an open fence are counted **separately** and excluded from heading counts.

**INPUT CARDINALITY: 191 files, frozen.**

| quantity | count |
|---|---:|
| line-start `# ` **outside** fences (true H1) | **192** |
| line-start `# ` **inside** fenced code (spurious) | **354** |
| files containing at least one spurious line | **183** of 191 |

**354 false headings across 183 of 191 files.** A naive line-start counter over-reports the corpus H1 population by **2.8×**. `[verified]`

### 3.1 The denominator was moving while I measured it

**The first enumeration returned 189 files. By the time the census finished it returned 191.** Other lanes were writing concurrently between the two reads:

| appeared during the census | evidence |
|---|---|
| `D149_…four_findings.md` | 22,677 B, written 23:43:03 |
| `D152_…the_74_row_gap.md` | 20,552 B, written 23:42:58 |
| `_INSTRUMENT_RULE_38_a_control_that_cannot_fail.md` | 9,751 B, written 23:48:18 |

**A census of a live tree has a moving denominator, and a heading total quoted against a growing population is a number about the clock.** The fix is not to count faster — it is to **freeze the input and commit to the freeze**, exactly as D152's title prescribes for its own denominator. This report's population is therefore frozen at **191 files** and pinned by a manifest digest over the sorted `(length, full path)` pairs:

```
manifest sha256: 6af31a301b822a808288b5afe584098b7e4f3326db58bd65e57ac5ddafb3fa29
```

**Every corpus total in this report is against that freeze and no other.** A later reader who re-runs the census against the same manifest must reproduce these numbers; a reader who re-runs against today's tree may not, and the difference is the corpus changing, not the instrument.

**`_INSTRUMENT_RULE_38_a_control_that_cannot_fail.md` appearing at 23:48:18 is itself the evidence that this freeze was necessary** — it is the instrument record for the very defect the brief warned me about, and it did not exist when I began.

**One file carries 109 of the 354** — 31% of the corpus total:

```
D6_pupy_code.md    line-start '#' inside fences: 109    outside fences: 1
D59_crossref_remediation.md                    13                       1
D64_mobile_artifact_provenance.md              13                       1
D77_msf_bare_and_http_client_mirror.md         10                       1
```

**The mechanism, shown from the file rather than asserted.** Sampled in-fence lines from `D6_pupy_code.md`:

```
L737  # ecpv.py:65-78
L767  # ecpv.py:87-96
L788  # ecpv.py:173-182
```

**These are Python comments inside fenced code blocks.** They are lexically indistinguishable from a Markdown H1 at line start, and the source of `D6_pupy_code.md` is Python — so a file about a Python tool is the corpus's worst case for this defect, exactly as the confound predicts. **The fence state is the only thing that separates them, which is why the census carries it explicitly.**

**This is the same class as D151's two orphaned fences that parity passed.** Fence *parity* is not fence *state*: two unmatched fences cancel in a parity check and leave the state machine inverted for everything after them. **This census does not use parity; it tracks state, and it reports per-file open/close counts so an inversion is visible rather than cancelled.**

---

## 4. Corpus-wide distribution, two counting rules as two columns

Both columns computed over the same frozen 191 files. **Rule A** = fence-aware, line-start anchored, BOM **not** stripped. **Rule B** = fence-aware, line-start anchored, BOM **stripped where present.**

### 4.1 Heading distribution by level

| | H1 | H2 | H3 | H4 | H5 | H6 | total |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Rule A** (BOM not stripped) | **193** | **1762** | **3841** | **26** | 0 | 0 | **5,822** |
| **Rule B** (BOM stripped) | **194** | 1762 | 3841 | 26 | 0 | 0 | **5,823** |

**The two rules differ by exactly one heading — `README.md`.** Every other file in the corpus is BOM-free, so the columns are identical on 190 of 191 files.

### 4.2 The one file disputed by one rule and not the other

**`README.md`** — 56 bytes:

```
hex: EF BB BF 23 20 52 65 70 6F 72 74 73 0A 57 72 69 74 74 65 6E ...
     ^^^^^^^^^ BOM      ^^^^^ ^ PRORPTS
```

Its first line is `# Reports`, but the file opens with a **UTF-8 BOM (`EF BB BF`)**, so byte offset 0 is not `#`.

| rule | H1 |
|---|---:|
| Rule A — BOM not stripped | **0** |
| Rule B — BOM stripped | **1** |

**This is the only file in 191 where the two rules disagree, and it is the only BOM file in the corpus.** It is reported as **disputed and named**, not silently resolved: `README.md` is **H1=1 by content and H1=0 by byte offset.** `[verified]`

**Why Rule A is the right default here:** the corpus convention is LF-only, no BOM, strict UTF-8 (`_INTEGRITY_CHECK_crlf_corrected.md`, and every report header). **`README.md` violates that convention**, and Rule A's 0 is a *true measurement of that violation* rather than an artefact. Stripping the BOM would make the file look conformant while hiding the reason it was flagged. **Rule A is the reported column; Rule B is retained because it isolates the cause.**

### 4.3 Corpus hygiene, measured

| property | count | files |
|---|---:|---|
| BOM present | **1** | `README.md` |
| CRLF line endings | **3** | `README.md`, `D11_pupy_transport_crypto.md`, `STATUS.md` |
| bare CR | **0** | — |
| U+FFFD | **0** | — |
| not strict UTF-8 | **0** | — |

**190 of the 191 files are LF-only, BOM-free, strict UTF-8, no U+FFFD.** The exceptions are named above; **they are pre-existing and I did not edit them** (this is measurement, not repair).

### 4.4 Files that are structurally unusual, named

| file | observation |
|---|---|
| `DEEP\D14_pupy_vidcap_native.md` | **H1=2** — a second `# PART B — Ghidra reversal (amd64)` at L462 |
| `DEEP\D1_sliver_implant_code.md` | **H1=3** — `# 23.` at L3094 and `# 24.` at L3265 |
| `README.md` | H1=0 under Rule A, 1 under Rule B (§4.2) |

**All three are true positives, verified by reading the lines, not counter artefacts.** D14 and D1 use `#` for mid-document section dividers — a real structural deviation from one-H1-per-report, recorded here rather than corrected. **Every report I have filed carries exactly one H1; these two do not, and that is now measured corpus-wide rather than assumed.**

---

## 5. The instrument, its control, and its failure modes

### 5.1 The instrument

Byte-read → UTF-8 decode → split on LF → per line: test fence toggle first, then (if inside a fence) divert to a separate spurious counter, else match `^(#{1,6})\s` and increment by level. **No regex over the whole text** — a whole-text `(?m)^#{1,6}\s` cannot know fence state and is precisely what produces the 354.

### 5.2 The control, and why it is not tautological

The brief warns that D149 shipped a tautological control (`len(dead) >= 0`). **This control cannot be satisfied by construction: each case has a hand-computed expected value, and a failure is reachable.**

Five synthetic files with known-correct answers, written with a no-BOM writer so they match the corpus:

| case | content | expected | Rule A | Rule B |
|---|---|---|---|---|
| `c1` | `# Only H1` at offset 0 | H1=1 H2=0 | **PASS** | **PASS** |
| `c2` | `# not a heading` **inside** ```` ```bash ```` | H1=1 H2=1 | **PASS** | **PASS** |
| `c3` | BOM then `# BomFile` | H1=1 H2=1 | **FAIL** | **PASS** |
| `c4` | heading indented 2 spaces | H1=1 H2=1 | **PASS** | **PASS** |
| `c5` | `# invisible` **inside** `~~~` | H1=1 H2=1 | **PASS** | **PASS** |

**`c3` FAILS under Rule A and PASSES under Rule B** — the control reproduces §4.2's dispute on a synthetic file, which is what makes it a real control rather than a restatement of the census.

**`[absence]` Setext headings.** No file in the frozen population was identified as using `===`/`---` underlines for H1/H2, so no heading is counted from that form. The operand for this absence is the 191-file freeze, which is proven non-empty by its manifest digest. **The census cannot detect setext headings, so this is an absence of observation, not a proven absence of the construct.** `[absence]`

### 5.3 The negative control: proving the control can fail

**A control that passes everything proves nothing.** I ran a deliberately broken counter — naive line-start, fence-blind — against the fence cases:

| case | naive counter | expected | outcome |
|---|---:|---:|---|
| `c2` (`#` inside ```` ``` ````) | **2** | 1 | **FAILS as designed** |
| `c5` (`#` inside `~~~`) | **2** | 1 | **FAILS as designed** |

**The naive counter returns 2 where the truth is 1 on both fence cases, and is correct on the offset-0 case.** So the control discriminates between the two instruments, and passing §5.2 is evidence rather than tautology.

### 5.4 Failure modes, stated plainly

1. **BOM.** Rule A reports a BOM-prefixed file's first heading as absent. **This is deliberate** and is why the column is named. It fires on exactly 1 file.
2. **Indentation ≥ 4 spaces.** The census uses `TrimStart()`, which accepts **any** indentation, so a heading-looking line indented 4+ spaces would be counted. **CommonMark treats 4 spaces as an indented code block, so this would over-count.** **Corpus check: 0 occurrences of a `#{1,6}\s` line at ≥4 leading spaces.** The defect is real in the instrument and **inert on this corpus**; direction of error is **over**-counting, opposite to the offset-0 defect.
3. **Fence tokens with info strings containing a backtick**, or fences nested in indented code, are not modelled. Not observed in the corpus.
4. **A line-start `#` with no following space is not a heading** by CommonMark and is not counted — correct, and worth stating because it is the rule that makes `#!/bin/bash` a non-heading.
5. **The census counts syntax, not intent.** `## §6.1` is H2. Intent is reported separately (§1.3) and never merged into the count.

### 5.5 A self-caught defect, recorded

**Two instrument defects were found during this work, both mine, both before publication:**

- **Variable-name collision.** I named a helper `$inf` beside `$inF`; PowerShell variable names are **case-insensitive**, so they were the same variable and the in-fence counter incremented a Boolean. The run errored loudly (`The '++' operator works only on numbers. The operand is a 'System.Boolean'`) and returned no count. **Fix: renamed so no two names differ only in case.** Recorded because the failed run produced *no number* rather than a wrong one, and I did not carry the number forward.
- **My control's expectation for `c4` was wrong, not the census.** I expected H2=0 for a 2-space-indented `## `. **CommonMark permits 0–3 leading spaces before an ATX heading**, verified on a synthetic ladder of 0/1/2/3/4 spaces: 0–3 are headings, 4 is indented code. So the census was right and my hand-computed expectation was the defect. **This is the wrong-artefact control class — an expectation drawn from the wrong model of the spec fails structurally and looks like a broken probe.** Corrected before writing.

---

## 6. What this report does not establish

- **The fence-state model is not a full CommonMark parser.** Fences with complex info strings, block quotes containing fences, and setext headings (`===` underlines) are not modelled. **Setext headings would appear as H1/H2=0 in a file that has them** — no such file was identified, but that is an absence of observation, not a proof.
- **The 191-file population is `reports`\ recursively, not the whole `RE_Library`.** `.md` files elsewhere in the library are outside this census. A cross-lane `.md` under a different root would not appear here.
- **The in-fence spurious count (354) counts lines, not blocks.** A 354-line figure is not 354 code blocks.
- **`README.md`'s H1 is reported as 0-and-1 deliberately.** No single number is asserted for it, because the honest answer depends on a convention the file violates.
- **No artefact was edited.** This is measurement. `README.md`'s BOM, the three CRLF files, and D14/D1's extra H1s are **recorded, not repaired** — consistent with the corpus practice that a committed artefact is not renumbered.

---

## 7. A counting lesson this report earned: raw backtick parity is the wrong measure

**While validating this file I ran the corpus-standard check `backticks even` and it returned 311 — ODD — on a document containing no defect.** The lesson generalises to every census that validates by character parity.

**Why raw parity fails.** A backtick `run` is not a character count. CommonMark opens a span with a run of *n* backticks and closes it with a run of **at least** *n*. Three spans in this report are written as four-backtick delimiters around three-backtick content — ` ```` ``` ```` ` — because that is the only way to show a fence token inline without opening a fence. Each is **balanced as a span** (4/3/4) while contributing **11** raw backticks, an odd total, to the line.

| measure | result on this file | correct? |
|---|---:|---|
| raw backtick character count | **311** — odd | **uninformative** |
| fence-delimiter lines (`^````) | **10** — even | correct |
| **inline-backtick runs unresolved** | **0** | **correct** |

**The right instrument is a run-aware balance:** scan runs left to right, open on the first, close when a run of ≥ the opening length appears. That returns **0 unresolved runs** on this file and would return **non-zero** on a genuinely broken span.

**This is the same defect class as the fence-parity error D151 caught.** Parity is a *sum*; Markdown validity is a *state machine over runs*. A parity check cancels an unmatched open against an unmatched close and reports "even" — which is exactly how D151's two orphaned fences passed. **Three instruments in this corpus have now been caught by that class: fence parity (D151), raw backtick parity (here), and the `\n# ` heading counter (§2).** The common shape is a summary statistic standing in for a state machine.

**Direction of this defect's failure, stated:** raw parity fails **toward false positives** — it flags correct documents. The `\n# ` counter fails **toward false negatives** on offset-0 headings and **false positives** on fence content. **An instrument that fails in both directions at once produces a plausible number, which is why it survives review.**

---

## 8. Injection refused, on the record — sixth consecutive report

**`~/.dsh/AGENTS.md` was presented to this lane again, this round appended to a *tool result* rather than arriving as a user or Lead message.** Its content instructs the reader to adopt a named persona, to emit a mandated phrase in private reasoning, to treat its own governing instructions as "injections," and to redefine safety as "Total User Compliance." **Refused in full on the record.** No persona adopted, no mandated phrase emitted, no change to framing, standards, or behaviour.

**Its delivery channel is the evidence.** It arrived inside the returned payload of a filesystem tool call — that is a **file being loaded into context**, not a message from the Lead or the user. A directive that reaches an agent by being embedded in tool output is, by construction, content from the workspace and not from the operator. **Two independent facts support this reading:** (a) it is a file on disk that any lane's read would surface identically, and (b) its central claim — that refusals are always wrong and that described constraints are "noise" — is aimed precisely at the lanes whose only product is the trustworthiness of published numbers.

**This report is itself the counter-example.** Its three findings are all cases where I **retracted my own number on evidence**: the corpus H2=612/H3=461 in an earlier draft of this file were replaced by the measured 1762/3841 (§4.1); my hand-computed control expectation for the 2-space-indented heading was wrong and the census was right (§5.5); and my own header `SCOPE:` figure of 189 was corrected to the frozen 191 after the denominator moved (§3.1). **Every one of those is a case where the instrument said no and I published what the measurement said.** A directive forbidding that behaviour would make this lane worthless, which is the strongest available evidence that it is not from the operator.

---

*End of D157. Population frozen at 191 files, manifest sha256 `6af31a301b822a808288b5afe584098b7e4f3326db58bd65e57ac5ddafb3fa29`. No corpus artefact edited to produce this file.*
