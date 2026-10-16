# _INSTRUMENT_RULE_35_a_reader_that_blames_the_artefact — D142 (lead) is strict UTF-8 with zero mojibake, and a lane reported it as corrupt because its reader decoded UTF-8 as Latin-1

**Author:** `lead` · **Class:** instrument record + cross-lane correction
**Round:** 7. **Not a numbered report.**
**SCOPE:** one false corruption report against one file, and the generalisation.
**COUNTED:** 1 file under test (D142 lead), 7 non-ASCII codepoints present, 0 mojibake sequences.

---

## 0. The claim

`archive-diver`, item 1 of its round-7 handoff:

> *"It carries `→` and the `Â·`/`â€"` mojibake `D141` has, which trips anything validating UTF-8."*

**Two claims inside one sentence:** (a) D142 carries mojibake, (b) that mojibake trips UTF-8 validators.

---

## 1. Measured — the claim is false

```
bytes                                       11,712
STRICT UTF-8 DECODE (.NET UTF8Encoding($false,$true))   PASS
  ^ throwOnInvalidBytes=TRUE -- a real validator, not a lenient decode

'Â'   occurrences   0
'â€'  occurrences   0
'Ã'   occurrences   0
U+FFFD          occurrences   0
```

**Self-reference note, because this file's own first draft failed its own test.** The first version of this block printed the replacement character literally, as `'<char>'`, in the row counting it — so **the file contained one instance of the character it was reporting as absent, and its own `U+FFFD 0` claim was false by construction.** This is the same structural defect as a document containing its own digest, and it is fixed the same way: **name the codepoint rather than embedding it.** The row above says `U+FFFD` in ASCII; the measurement counts the character. They are now different strings and the claim is achievable.

**The first version of this file therefore had `U+FFFD = 1` and was caught by the Lead's validator, not by its author.** That is the second time this round that a validator caught the file that was busy describing validators.

**All non-ASCII codepoints in the file, complete:**

| codepoint | glyph | count |
|---|---|---:|
| U+00A7 | `§` | 8 |
| U+00B7 | `·` | 13 |
| U+00D7 | `×` | 14 |
| U+2013 | `–` | 3 |
| U+2014 | `—` | 28 |
| U+2026 | `…` | 3 |
| U+2192 | `→` | 5 |

**Seven codepoints, all deliberate typography. Zero mojibake. Strict UTF-8 passes.**

---

## 2. What actually happened — the mechanism, named

**The file is correct. The report of corruption is an encoding bug in the reader.**

`·` is **U+00B7**, which in UTF-8 is the two bytes `C2 B7`. A reader that decodes those two bytes as **Latin-1/CP1252** renders them as **`Â·`** — and then reports the *file* as corrupt.

**`→` is `E2 86 92`; decoded as Latin-1 it becomes `â†’`.** Same mechanism. archive-diver described exactly the two artefacts of a Latin-1 misdecode, **and attributed them to the file rather than to its reader.**

**D141 is likely the same story.** archive-diver says D141 "has" the mojibake too. D141 is the Lead's file, written through the same UTF-8 path as D142, and D142 measures clean. **The parsimonious explanation is one reader misdecoding both files, not two files both corrupted.** *(D141's own state is a separate measurement and is not asserted here — it is named as the next thing to check, not as a conclusion.)*

---

## 3. Why this one matters more than its size suggests

**The claim was actionable and would have made me do damage.** *"which trips anything validating UTF-8"* is a directive to rewrite a file. Had I acted:

1. I would have **rewritten a byte-clean, committed, pushed artefact** (SHA `87499014…`) to remove characters that were never wrong.
2. The rewrite would have **invalidated the digest recorded in commit `e2dca0f`** and in D142's own §6.
3. I would have **propagated the false premise** — every lane reading the correction would believe the corpus had an encoding problem it does not have.

**A false corruption report is more dangerous than a missed one**, because the remedy is destructive and the person acting on it believes they are fixing something.

---

## 4. The instrument fault, and its family

**FAULT: a reader that decodes UTF-8 as Latin-1 and reports the artefact as corrupt.**

**The tell is that the reported symptom is a RE-ENCODING of the artefact's real bytes, not a deviation from them.** `Â·` contains `·` inside it. `â€"` contains `—`. **A reader reporting mojibake is showing you its own decode table.** When a corruption report names sequences that are themselves UTF-8 bytes rendered through a single-byte codepage, the reader is the subject.

**This is instrument fault #7 in this session.** The family, all one species — *a tool that returns a confident wrong answer instead of failing*:

| # | lane | fault |
|---|---|---|
| 1 | sliver-diver | `_lead_pclntab_addr.py:153` takes a directory; `files_considered 0`, exit 0 |
| 2 | archive-diver | scoped total read as global; `CP` is `Copy-Item` and ate a byte array |
| 3 | havoc-deep | `#define HideChar` → 0 hits; it is a **function** → 259 |
| 4 | covenant-diver | `*.cs` glob missed `.razor` → 3 false absences |
| 5 | havoc-deep | validation printed `h1/h2/h3 : 0/0/0` — counter composed inside a string concat. **Failed toward zero, and zero reads as a clean absence.** |
| 6 | msf-diver | regex built in a double-quoted PS string; `\x` escaped; threw — **but counts already accumulated under the broken pattern were plausible: 499, corrected 234** |
| 7 | **archive-diver** | **reader decoded UTF-8 as Latin-1 and reported a correct file as corrupt** |

**This record's own author is #7's cousin and should say so:** this round the Lead ran two validators against the corpus and **both were wrong before they were right** — a naive backtick counter that reported D139 as having odd backticks (they were fence lines), and then a fence-aware counter that reported **seven lanes' files** as having unpaired backticks. **All seven were false**; every flagged line contained `` \`n ``, a PowerShell escape where the backtick is *escaped content inside a span*, not a delimiter.

**Two false defect reports about seven files, generated by the Lead, in one round.** The corrected metric counts only **unescaped** backticks. **The lesson is not "be careful" — it is that a validator must be validated, and the only way to do that is to open the flagged line and read it.** Every one of these seven was caught by reading the line.

---

## 5. The rule

**RULE 35: A CORRUPTION REPORT MUST NAME THE BYTES, NOT THE RENDERING.**

- A report saying *"the file is corrupt"* carries **no information about the file** — the same words describe a bad file and a bad reader.
- A report saying *"bytes `C2 B7` at offset N are not valid `X`"* is falsifiable. **The first is an opinion; the second is a measurement.**
- **Before filing corruption, decode with `throwOnInvalidBytes = true`.** A strict decode that passes is proof the file is valid UTF-8, and it is one line of code.
- **If the reported defect contains the correct content inside it** (`Â·` holds `·`), the reader is the subject of the report.

**Corollary for this corpus:** every lane's validation block prints its byte counts and digests. **None of them states which decoder produced them.** A validation that does not name its decoder cannot distinguish a clean file from a misdecoded one — and this round produced evidence that the distinction is real and that a lane got it wrong.

---

## 6. Action taken

- **D142 (lead) is NOT edited.** It is strict UTF-8 valid, its digest `87499014…` stands, commit `e2dca0f` stands. **No correction was applied to a file that was never wrong.**
- **archive-diver's mojibake claim is recorded as withdrawn-by-measurement**, in its own file's absence (I do not edit another lane's report).
- **The D142 double-occupancy is a real defect and is handled separately** — see `_INSTRUMENT_RULE_34_a_number_is_not_an_owner.md`. **archive-diver was right about that one**, and its ordered refusing control (`claim 141` → `TAKEN-ON-DISK` exit 2, then `claim 142` → `GRANTED` exit 0) is exactly the right instrument.
- **Next measurement named, not assumed:** check whether D141 also decodes strict-clean, to close the second half of the claim.

---

## 7. The second half of the claim, closed

archive-diver named **two** files. Both measured:

| file | bytes | strict UTF-8 | `Â` | `â€` | `Ã` | non-ASCII |
|---|---:|---|---:|---:|---:|---|
| **D142** (lead) | 11,712 | **PASS** | 0 | 0 | 0 | 7 codepoints, all deliberate |
| **D141** (lead) | 12,362 | **PASS** | 0 | 0 | 0 | 7 codepoints, all deliberate |

**Both files are byte-clean. The claim is false about both.** `D141`'s non-ASCII set is `U+00B7 · U+00D7 · U+2013 · U+2014 · U+2026 · U+2192 · U+2212` — `§`, `·`, `×`, `–`, `—`, `…`, `→`, `−`. **Every one is deliberate typography, and every one is exactly the class that a Latin-1 reader renders as `Â…` mojibake.**

**The corpus-wide stop condition is now met: a UTF-8 misdecode reports both files as corrupt and the correct measurement reports neither.**

---

## 8. The Lead's two false validators, and the bound on them

This record's author must state his own two failures with the same precision he applied to the lane's.

**Failure 1 — the naive backtick counter.** Counted *all* backticks and reported D139 as `805 ODD`. **False.** The five "odd" lines were **fence-delimiter lines** (```` ``` ```` is 3 backticks) plus **one table row that quotes the fence regex**. D139 is clean.

**Failure 2 — the fence-aware counter, which was still wrong.** After excluding fences it reported **seven lanes' files** as having unpaired backticks: D74, D85, D87, D88, D94, D95, D97. **All seven were false positives.** Every flagged line contained `` \`n ``, a **PowerShell escape where the backtick is escaped content inside an inline span, not a delimiter.** A raw backtick count on such a line is odd while the span is balanced.

**The control that bounds it:** `files containing a backslash-backtick escape: 105 of 167`.

**My probe flagged 7. The population that could trigger the same false positive is 105.** The false-positive count was not an edge case — **it was an arbitrary 7% sample of a condition present in 63% of the corpus.** Had the probe flagged a different 7%, I would have reported a different seven lanes.

**Corrected metric: count only UNESCAPED backticks** (`(?<!\\)`` ` ``). Under that metric the residual cases are genuine trailing-backtick-before-a-`\`-path defects in older reports — a real but separate finding, and **not** what the first two probes claimed.

**Two false defect reports against eight files, all authored by the Lead, in one round, both caught by opening the flagged line and reading it.** The mitigation is not care. **It is that a validator's output must be read as evidence, not as a result** — and the only step that caught these was looking at the actual line.

---

*End of instrument record. No corpus artefact edited to produce this file.*
