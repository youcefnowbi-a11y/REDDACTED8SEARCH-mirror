# _CORRECTION_R9_2_the_naive_h1_counter_and_the_fenced_comment_class

**Author:** `lead` · **Round 9 continuation** · **Scope owner:** `lead`
**SCOPE:** one Lead instrument defect — a naive `^# ` line counter used for H1 counts in ad-hoc verification, and the class of false positive it produces.
**DEFINER SCOPE:** the counter is defined by the regex `^# ` applied to every line of a file with **no fence-state tracking**. The validator's counter is defined by the same regex **applied only outside fenced blocks**.
**CONDITIONAL SCOPE:** this record covers the counter. It does **not** claim any report is defective — measured on eight of nine round-9 reports the naive counter and the fence-aware counter agree exactly, and the ninth is a false positive of the naive counter, not a defect of the report.
**COUNTED:** **9** round-9 reports re-counted. **1** disagreement (D163). **0** real defects found. **2** independent H1 counters in use by the Lead. **1** of them wrong.

---

## 1. What happened

**Verifying D163's self-reported `H1=1`, my ad-hoc counter printed `H1 3`.** I nearly filed that as a defect against the lane.

**It was my counter.** The two extra "H1" lines are:

```
L  50: # Needed for Meterpreter
L  52: # Needed for the next-generation POSIX Meterpreter
```

**Both are Ruby comments inside a fenced code excerpt** — a gemspec fragment the report quotes verbatim. In Ruby, `#` starts a comment. In Markdown, `^# ` at column 0 starts an H1. **The same two characters, two languages, one line.**

**Fence-aware recount: `H1 = 1`.** D163 is correct.

> ### **A LINE OF TEXT DOES NOT KNOW WHAT LANGUAGE IT IS IN. ONLY ITS CONTEXT DOES.**

---

## 2. The class, not the instance

**This is not a bug in a counter. It is a whole class of false positive:** **any line-oriented Markdown counter that does not track fence state will misclassify quoted code as document structure.**

**Measured across all nine round-9 reports:**

| report | naive `^# ` | fence-aware | fences | verdict |
|---|---:|---:|---:|---|
| D147 | **7** | **1** | 28 | naive over-counts by 6 |
| D153 | 1 | 1 | 4 | agree |
| D154 | 1 | 1 | 2 | agree |
| D155 | 1 | 1 | 0 | agree |
| D156 | 1 | 1 | 6 | agree |
| D157 | 1 | 1 | 10 | agree |
| D158 | 1 | 1 | 6 | agree |
| D162 | 1 | 1 | 0 | agree |
| D163 | **3** | **1** | 12 | naive over-counts by 2 |

**D147 is the worse case: naive 7 against a true 1.** Had I run the naive counter on D147 first, I would have reported six spurious H1s in a report that is clean. **The error direction is toward MORE apparent defects, and the reports with the most code excerpts — the good ones — suffer most.**

> ### **THE DEFECT PENALISES EXACTLY THE REPORTS THAT QUOTE THE MOST EVIDENCE.**

---

## 3. Why the validator never caught this

**The validator is fence-aware.** On D163 it reports `H 25` and the verdict `OK`; on D147, `H 32` and `OK`. **It walks fences and counts headings outside them.**

**So the Lead has had two H1 counters running:**

| counter | location | fence-aware | status |
|---|---|---|---|
| validator | `_lead_validate_reports.ps1` | **yes** | correct — this is the one that gates reports |
| ad-hoc | typed inline during verification | **no** | **WRONG — retired by this record** |

**The gate was never compromised. Only my spot-checks were.** That distinction matters: **a wrong instrument that is not the gate produces wrong *narrative*, not wrong *acceptance*.** I nearly wrote a defect against a clean report on the strength of it.

---

## 4. Why it was not caught sooner, and the honest reason

**D163 itself warned me.** Its §"MY OWN INSTRUMENT WAS THE DEFECT THIS TIME" describes a validator reporting **3 H1s** where two were fenced Ruby comments — **the identical bug, in the identical file, on the identical lines.**

**I read that warning, quoted it back, and then reproduced the bug in my own tool within the same verification pass.**

> ### **READING A WARNING IS NOT INSTALLING A CONTROL. A WARNING CHANGES NOTHING UNLESS IT CHANGES A TOOL.**

**This is Rule 38 in its purest form, one level up.** Rule 38 says a control that cannot fail is not a control. **This is the adjacent failure: a control that was correctly specified, correctly described, and then not used — while a worse control was used in its place.**

---

## 5. The tell, stated so it is usable

**A naive heading count and a fence-aware heading count agree on files with no fences and diverge on files with fences.** Therefore:

> ### **IF TWO COUNTERS AGREE, CHECK THAT THE INPUT COULD HAVE MADE THEM DISAGREE. TWO COUNTERS AGREEING ON AN INPUT THAT CANNOT SEPARATE THEM IS NOT CORROBORATION — IT IS THE D141 CONDITION: IDENTICAL OUTPUT FROM INPUTS THAT NEVER REACHED THE DIFFERENCE.**

**D155, D162 and D163's siblings with `fences 0` prove nothing about either counter.** D147 and D163 are the only two rows in the table that test anything.

---

## 6. Disposition

- **No report is retracted. No report is defective.** Nine of nine round-9 reports have `H1 = 1` under the correct counter.
- **The ad-hoc counter is retired.** Any inline heading count must walk fence state. **The validator already does; there is no reason to hand-roll a second one, and doing so produced this record.**
- **`_ROUND9_DISPATCH_LEDGER_...md`** carries a `H 7` reading from the validator and is unaffected.
- **Recorded rather than quietly fixed**, because the pattern — *a specified control not used while an inferior one was* — has now occurred twice in this session and the second occurrence is the one that nearly produced a false report against a lane.

---

*End of record. No lane artefact edited. No report's content changed by this correction.*
