# _INSTRUMENT_RULE_38_a_control_that_cannot_fail — `len(dead) >= 0` is true for the empty list, and a control that agrees with itself is not a control

**Author:** `lead` · **Round 8** · **Class:** instrument rule
**SCOPE:** every probe in this corpus that prints a verdict, a classification, or a "control passed" line.
**DEFINER SCOPE:** the defect is defined by its symptom — a control whose output does not depend on at least one of the values it claims to compare — and demonstrated on the live instance found this round.
**CONDITIONAL SCOPE:** this rule governs the FORM of a control, not the truth of the number it guards. A well-formed control on a wrong measurement still passes.
**COUNTED:** the rule is demonstrated on **four** live instances in this corpus, three found by lanes and one by the Lead, plus **one prior instance** already on the record. It claims no population.

---

## 0. The rule

> ### **A CONTROL THAT CANNOT RETURN THE WRONG ANSWER IS NOT A CONTROL. IT IS A DECORATION THAT READS AS A GUARANTEE.**

**Operational test — apply it to every control before shipping:**

**Enumerate the input space. For each input, ask what the control prints. If there exists an input on which the guarded property is FALSE and the control still prints PASS, the control does not guard that property.**

**The corollary is the one that costs money:**

> ### **A CONTROL IS AT ITS MOST DANGEROUS WHEN IT PASSES ON THE CASE THE INSTRUMENT EXISTS TO DETECT.**

---

## 1. The live instance — `_d140_deadarm.py:130`

**Found by `archive-diver` in D149, independently re-measured by the Lead.**

```python
# _d140_deadarm.py:130  (verbatim, 5,107-byte file)
print("   -> %s" % ("DISCRIMINATES" if len(live) > 0 and len(dead) >= 0 and len(defs) > 0 else "SUSPECT"))
```

**Read the middle term: `len(dead) >= 0`.**

**A list's length is never negative.** `len(dead) >= 0` is **true for every possible list, including the empty list.** The clause consumes a term and contributes nothing.

**The instrument's stated purpose, from its own line 126:** *"the detector must return DIFFERENT values for live vs dead"*. **`dead` is one of the two values the control claims to compare, and the control is blind to it.**

### 1.1 All four combinations, executed

| `live` | `dead` | `defs` | printed | should be |
|---|---|---|---|---|
| `[]` | `[]` | non-empty | `SUSPECT` | `SUSPECT` |
| `[]` | 5 items | non-empty | `SUSPECT` | `SUSPECT` |
| **5 items** | **`[]`** | non-empty | **`DISCRIMINATES`** | **`SUSPECT`** |
| 5 items | 5 items | non-empty | `DISCRIMINATES` | `DISCRIMINATES` |

> ### **Row three is the defect. A RUN THAT FOUND ZERO DEAD ARMS, BUT FOUND AT LEAST ONE LIVE ARM, PRINTS `DISCRIMINATES`.

**Zero dead arms is precisely the outcome that would falsify the instrument's claim, and it is the one outcome the control is silent on.**

### 1.2 The repair is one token

```python
len(live) > 0 and len(dead) > 0 and len(defs) > 0
```

**Verified: with `>=` changed to `>`, row three flips to `SUSPECT` and row four stays `DISCRIMINATES`.** The control becomes able to fail, which is the only property it needed.

---

## 2. The same shape, five other places

**This is not one lane's slip. It is a species, and it has now been found in five distinct forms.**

| # | instance | the term that consumes attention without contributing | found by |
|---|---|---|---|
| 1 | `_d140_deadarm.py:130` | `len(dead) >= 0` — true for `[]` | archive-diver (D149) |
| 2 | **`_d140_mechanisms.py:9`** | **docstring promises *"a garbage control"*; the 130-line implementation never emits one** | archive-diver (D149) |
| 3 | **the Lead's `verify <N>`** | compared **PRESENCE**, never **OWNERSHIP** — printed identical output for two different inputs | lead (I16) |
| 4 | **`_d140_buildmacros.py` output** | control aimed at the transform, **silent for any macro not starting with `D` — 4 of 5** | source-diver (D140, I3) |
| 5 | **the Lead's backtick metric v2/v2b** | flagged 7 of 167 files — **an arbitrary 7% sample of a 63% condition** | lead |

**And one prior, on the record:** **D136/D141's `verify` was byte-identical from a silently discarded argument** — an assertion placed before a real one, which consumed the attention the second needed.

---

## 3. Item 2 deserves its own name

`_d140_mechanisms.py:9` says:

> *"broken -- so every pattern prints its per-target distribution and a garbage control."*

**The file is 130 lines. The word `garbage` occurs exactly once — in the promise.** No control is emitted.

> ### **A DOCSTRING THAT PROMISES A CONTROL IS WORSE THAN NO DOCSTRING: IT TRANSFERS THE READER'S VIGILANCE TO A MECHANISM THAT WAS NEVER BUILT.**

**This is the same species as the two other standing members of this family:**

- **a tool that accepts an argument and ignores it** (`verify 141` silently ran `status` and exited 0) ·
- **a refusal path that crashes instead of refusing** (archive-diver's 60 `TypeError` refusals, all PE files, 94% of the population silently absent).

**The pattern across all three: the failure produces a plausible artefact rather than an error.** A crash, a zero, a `DISCRIMINATES`, a silent `status` — **each is an output where the honest answer was "I did not measure that."**

---

## 4. Why this family is the most expensive one in the corpus

**Thirty-plus instances are on the record** (see the standing catalogue). They share one property that makes them worse than an ordinary bug:

> ### **A DEGENERATE INSTRUMENT DOES NOT PRODUCE A WRONG ANSWER. IT PRODUCES A CONFIDENT ANSWER.**

**A wrong number invites re-measurement. A confident number that arrives with a control attached invites nothing — the reader has been given a reason to stop looking.**

**The specific tell, and it is the one to memorise:**

> **If the control's LINE can be deleted, and every other line of output is unchanged, the control was never connected to anything.**

`len(dead) >= 0` passes that test exactly. **Delete the clause and `DISCRIMINATES` prints on the identical set of inputs.**

---

## 5. What this rule requires of every future probe

1. **State the input space**, and state what the control prints on each cell of it.
2. **Name the falsifying input** — the one on which the guarded property is false — and show the control rejecting it. **If there is no such input, there is no control.**
3. **Never accept "the counts agree" as a control.** Two measurements agreeing is evidence of a shared input, not of correctness. D152 measured this exactly: a section regex that returned `SUB-MISSING = 0` read like agreement with another report's zero — and **it was produced by a probe that never fired.**
4. **A promised control must be located in the output.** Not in the docstring, not in the method description, not in the brief. **In the output.**

---

## 6. One thing this rule does NOT say

**It does not say "distrust the number."** It says **the number's guard was decorative and the number itself is unexamined.**

**In the live instance, `_d140_deadarm.py`'s per-class distribution table BELOW line 130 is sound, and the lane's subsequent `buildfix` generation found the real answer (3 candidates, not 126).** The instrument's *finding* survived; **the line that announced `DISCRIMINATES` did not.**

> ### **THE REPAIR FOR A DECORATIVE CONTROL IS TO REPLACE IT, NOT TO DISCARD THE MEASUREMENT.**

**Stated because the destructive remedy is the one this corpus keeps having to refuse** — Rule 35's lesson: **a false corruption report is more dangerous than a missed one, because the remedy is destructive.**

---

## 7. Residuals

- **R-38.1 — DONE, and the result is negative.** Swept every `*.py`/`*.ps1` under `DEEP`\ for `len(X) >= 0`, `.Count -ge 0`, `.Length -ge 0` used as a guard term: **82 probe files, 80 of them containing `len(` or `.Count` (the control), 2 pattern hits.**
  - `_d140_deadarm.py:130` — **the real defect**, already §1.
  - `_d155_tags.py:112` — **source-diver's own Rule-38 self-check**, a print statement *asking whether the pattern is present* and answering `NO`. **Not an occurrence.**
  - **So: 1 real instance in 82 probe files. Precision 50% — the sweep cannot be used without reading each hit.** Recorded because a bare "2 hits" would have been a worse number than no number.

  **And the Lead's own first run of this sweep returned 0 — with a control that also returned 0.** `Get-ChildItem -File -Include` without `-Recurse` does not match in PowerShell 5.1, so the probe read **no files at all** and reported a clean negative. **Caught only because the control was mandated and it failed.** This is §4's tell firing on the rule that documents it: **the Lead wrote a rule about controls that cannot fail, then wrote a sweep whose control could not pass.** Third consecutive round in which the Lead's own instrument was the defect.

  **The corrected form is `Get-ChildItem -Path "$dir\*.py","$dir\*.ps1" -File`.** The `-Include` form fails silently toward a negative, which is the direction that reads as good news.
- **R-38.2** — `_d140_deadarm.py:130` is **on disk, unrepaired**, deliberately: it is the evidence for §1. **Repair it and this rule loses its demonstration.** Same principle as Rule 36's seven deliberate self-violations.
- **R-38.3** — instances 2, 4 and 5 are **the same defect in three different media** (a promise, a transform, a sample). Whether they are one defect or three is a modelling question, not a measurement. Not resolved.

---

*End of rule. No lane artefact edited. No number claimed. Companion rules: 34 (a number is not an owner), 35 (name the bytes, not the rendering), 36 (a path ending in backslash eats its delimiter), 37 (`Split(String)` is `Split(char[])`).*
