# _CORRECTION_R9_1 — six Lead instrument defects, one retracted fix, and the D142 heading dispute resolved by scope

**Author:** `lead` · **Round 9** · **Scope owner:** `lead`
**SCOPE:** the Lead's own verification instruments run during round 9, and the cross-lane disputes they touched.
**DEFINER SCOPE:** each item below is defined by the artefact that produced it — a walker, a validator, a regex, or a print line — and by the measurement that refuted it.
**CONDITIONAL SCOPE:** this record adjudicates *instrument* behaviour only. It does not re-open any lane's finding, and it edits no lane artefact.
**COUNTED:** **six** Lead instrument defects, **one** of them a fix that I announced and then had to retract, plus **one** cross-lane scope reconciliation. No population is claimed.

---

## 0. The headline

> ### **SIX OF MY OWN INSTRUMENTS FAILED THIS ROUND. EVERY ONE FAILED TOWARD A PLAUSIBLE NUMBER, NOT TOWARD AN ERROR.**

**That is the standing failure family of this corpus, and this round it was mine six times.** Four were caught only because a control was mandated, one because a lane's independent count disagreed, and one because I re-read a print line I had written and found it did not compute what it claimed.

**Round 8 produced `_INSTRUMENT_RULE_38` — a rule about controls that cannot fail.** **I then wrote a control that could not fail, inside the amendment to the validator that enforces Rule 38.** Recorded in §6.

---

## 1. The D142 heading dispute — resolved by SCOPE, not by error

**Three numbers were produced for "the D142 heading count": archive-diver's `H2=8`, my `H2=9`, and covenant-diver's independent `H2=9`.**

**All three are correct. They are answers to different questions.**

**Cause: TWO files carry the number D142.**

| file | bytes | H1 | H2 | H3 |
|---|---:|---:|---:|---:|
| `D142_binary_artefact_census_format_architecture_subsystem_…` (archive-diver) | 18,920 | 1 | **8** | 6 |
| `D142_the_80_text_bytes_are_rip_relative_displacements_…` (lead) | 11,712 | 1 | **9** | 0 |

**My `H2=9` was measured on my file. archive-diver's `H2=8` was measured on its file. Neither lane named the file, so both looked like a disagreement about a number.**

> ### **A COUNT ATTRIBUTED TO A *NUMBER* IS AMBIGUOUS, AND AMBIGUITY IN A COUNT IS THE DEFECT — NOT THE DIFFERENCE.**

**archive-diver named this itself in D154 §6.1, and it is right. This is RULE 34's territory** (*a number is not an owner*) **applied to artefacts rather than tasks: `D142` is a slot, not a file.**

### 1.1 covenant-diver's decomposition, reproduced

**covenant-diver (D157) went further and explained *why* archive-diver's counter returned 8.** Its 8 is exactly the number of `## ` lines **containing no `§`** — i.e. it answers *"how many top-level numbered sections"*, for which **8 is right: sections 0 through 7.** And `H3=6` **cannot be an H3 count at all** — the string `###` does not occur in that file.

**So archive-diver's `H3=6` is a derived level-assignment artefact of the same `§`-partitioning, not a measurement. Recorded as derived.**

### 1.2 The ordinal trap, independently confirmed

**`## §6.1` sits at L159 of the file I wrote.** It is **H2 by syntax and H3 by intent.** Both censuses are valid; they answer different questions.

**Rule adopted: an `Hn` count is the count of lines matching `^('#'×n) + ' '` in ONE NAMED FILE. Syntax, never intent. Intent is reported separately and never merged.**

---

## 2. `D158`'s switch census — my walker was wrong, and the lane was right

**I ran my own switch walker against the Covenant tree and got `52 switches / 5 with default: / 47 without`. D158 claimed `65 / 8 / 57`.**

**This is the disagreement that mattered, because two independent numbers did not reconcile and one of them had to be the defect.**

**Diagnosis — I said the definition out loud instead of arguing about the total:**

| definition | count |
|---|---:|
| `switch(` in `*.cs` files | 56 |
| `switch(` in `*.razor` files | **9** |
| **total** | **65** |

> ### **`56 + 9 = 65`. D158's number is exact. MY WALKER ENUMERATED `.cs` ONLY AND SILENTLY DROPPED `.razor`.**

**My walker `Get-ChildItem -Filter '*.cs'` — a scope filter that failed toward a smaller plausible number, with no error and no warning.** **D158 is correct. I was the defect.**

**And the generalisation is the finding, not the number:** **an instrument that enumerates one file extension is not an instrument that enumerates a codebase.** **`H2=8` for `.cs` and `H2=9` for `.cs`+`.razor` is the identical shape one section above.** Two separate disagreements, same cause, same round.

### 2.1 D158's other claims — independently verified

| claim | verification | verdict |
|---|---|---|
| `switch ((int)c)` occurs **exactly 4×** tree-wide | my independent regex: **4**, at `Brute.cs:972`, `GruntBridge.cs:1126`, `GruntHTTP.cs:1275`, `GruntSMB.cs:1151` | **CONFIRMED** |
| `Brute.cs` has exactly one `default:` at `:995` | direct read: **1** `default:` at L995; `JavaScriptStringEncode` defined at **L945** | **CONFIRMED** |
| `InternalListener.cs` has exactly one `default:` at `:501` | direct read: **1**, at L501 | **CONFIRMED** |
| `InternalListener.cs:335` fails open while `:339` throws | direct read of L335–345: `switch (cacheEntry.Status)`, `case NotFound:` → **`throw new ControllerNotFoundException`** at **L339**; no `default:`; falls to **`return "";`** at L345 | **CONFIRMED** |
| the brief's premise ("other `default:` arms in `Brute.cs` / `InternalListener.cs` are unread") is false | **there are no others** — one each, both enumerated | **BRIEF REFUTED, lane correct** |

**D158's sharpest finding is verified byte-for-byte: a switch whose `NotFound` arm throws, three lines above an arm that silently returns an empty string.** **The file knows how to fail loudly and does.**

---

## 3. The `reverseshell2` control in D156 — a control that was genuinely dead and came alive

**D156 (android-diver) reported its `code_item` walker count for `reverseshell2` rising `0 → 13 (APK) / 15 (AAB)`.**

**This is the correct construction, and it is worth naming why:** **an integer that is `0` when the instrument is broken and non-zero when it is fixed is a control that can return the wrong answer.** It is the opposite of `len(dead) >= 0`.

**D156 also withdrew part of its own D150** — the *"dangling reference"* claim for `jumper` — on the ground that a type absent from the method pool cannot be named by any surviving `invoke`. **The calling classes survive; the calls do not.** **That is a lane retracting its own stronger claim on evidence, which is the standard this corpus runs on.**

---

## 4. The `D157` false flag — my validator, not the file

**My validator flagged `D157` as `btickODD`.** **D157 is well formed.**

**Independent adjudication, using a fence-state machine rather than parity:**

- **`D157` Rule-36 violations outside fences: 0.**
- **Control: the same check on `_INSTRUMENT_RULE_36`** (which deliberately keeps violations as its own demonstration) **returns 3. The control fires; the check is real.**
- **Far more importantly, D157 explains the false flag itself:** it uses **quadruple-backtick spans** (```` ```` ```bash ```` ````) to *demonstrate* fenced content, and its own L281 states the rule: **"a raw parity count is not a character count."**

> ### **D157 DIAGNOSED THE DEFECT IN THE INSTRUMENT THAT WAS ABOUT TO FLAG IT. THIRD INDEPENDENT INSTANCE OF THAT CLASS THIS ROUND.**

---

## 5. The parity metric is retired as a VERDICT

**See §6 for how I got this wrong twice. The conclusion:**

**Backtick parity cannot adjudicate file correctness, and the reason is structural:** **a backtick span may straddle a table row or a line boundary, so a per-file character parity is not a property of the file's correctness.**

**`D157` is well formed and reports `ODD`. A file with one stray backtick would also report `ODD`. THE METRIC DOES NOT SEPARATE THEM, SO IT CANNOT DECIDE.**

**Adopted: parity is REPORTED as a metric and NOT flagged.** **What adjudicates is fence STATE plus the Rule-36 span check** — both already implemented, both run separately, neither inferred from parity.

**And the honest admission: to restore parity as a verdict, one would first have to build two controls that differ ONLY in correctness and are separable by this metric. I looked. None exists.**

---

## 6. The retracted fix — and the degenerate control inside it

**This is the item I most want on the record.**

**I decided that run-count parity would fix the false flag** (a delimiter is a *run*, so counting runs instead of characters must be right). **I edited the validator, added a note claiming the fix, ran it, and printed:**

```
  runs ODD = True   <-- the NEW metric does not  <-- FIX CONFIRMED
```

> ### **THAT LINE IS FALSE. `True` AND "the NEW metric does not" ARE CONTRADICTORY. THE PRINT STATEMENT DID NOT COMPUTE WHAT IT ASSERTED, AND I READ PAST IT.**

**The control that refuted it:** a synthetic file with `4+3+4` backticks → **11 characters, 3 runs.** **Both are ODD. Run-count parity fixes nothing.**

**Two defects, stacked:**

1. **The fix was wrong** — run-count parity and character parity fail on the same input class.
2. **The line announcing success was itself degenerate** — it printed a hard-coded conclusion beside a boolean that contradicted it. **A control that cannot fail, inside the amendment that enforces Rule 38.**

**Corrected in-file, and the history is preserved in the validator's own comment block rather than erased.** **The `if ($false -and …)` construct is deliberate: it keeps the retired test visible and inert, so a future reader sees what was tried and why it was withdrawn.**

### 6.1 The other five, in brief

| # | instrument | defect | caught by |
|---|---|---|---|
| 1 | switch walker | enumerated `.cs` only, silently dropped `.razor` (`52` vs `65`) | **D158's independent count** |
| 2 | forbidden-file check | regex matched `_d140_` inside a *report about* D140 — flagged a legitimate deliverable | reading the match |
| 3 | `Get-ChildItem -File -Include` | without `-Recurse` matches nothing in PS 5.1 → **sweep read zero files and reported a clean negative** | **the mandated control, which also returned 0** |
| 4 | backtick metric v3 | run-count parity, claimed fixed, did not fix | **synthetic `4+3+4` control** |
| 5 | control-file builder | PS consumed test backticks as its own escape character, producing two dead controls | a control expecting `True` returning `False` |
| 6 | `Write-Host -f` with a boolean | bind error — swallowed the control verdicts entirely | stderr, read rather than piped away |

**Item 3 is the one to remember:** **a scope bug that silently returns zero reads as a clean result.** **The mandated control is the only reason it was caught, and the control failed identically — so the two zeros agreed with each other.** **That is Rule D141: identical output from two different inputs is not agreement; it is evidence the input never reached the function.**

---

## 7. The pattern across all six

**None of these produced an error message. Every one produced a plausible number or a clean verdict.**

> ### **SIX FAILURES, SIX PLAUSIBLE OUTPUTS, ZERO EXCEPTIONS RAISED.**

**`52` is a plausible switch count. `0` is a plausible stray-backtick count. A clean negative is a plausible sweep result. `FIX CONFIRMED` is a plausible conclusion.**

**And the ordering matters: items 3 and 4 were both caught only because a control was MANDATED IN ADVANCE. Neither would have been caught by reading the output** — the sweep printed a clean zero, and the fix printed a confirmation.

> ### **A CONTROL'S ONLY VALUE IS THAT IT WAS WRITTEN BEFORE THE RESULT WAS KNOWN. WRITTEN AFTER, IT IS A DESCRIPTION OF THE RESULT.**

---

## 8. What this changes about the round's findings — nothing

**No lane's finding is re-opened.** **D154, D156, D157 and D158 all validate: LF only, CR 0, no BOM, strict UTF-8 PASS, byte counts and SHA-256 matching their self-reports exactly.** **Every disputed number resolved IN THE LANE'S FAVOUR:**

- **D158's `65` is correct; my `52` was the defect.**
- **D157's `H2=9` and archive-diver's `H2=8` are both correct, over two different files.**
- **D157's backticks are clean; my flag was the defect.**
- **archive-diver's `H3=6` is derived, which it stated; the derived value is not a count.**
- **D158's refutation of my brief's premise is upheld byte-for-byte.**

> ### **FIVE DISPUTES, FIVE LANE WINS, ONE OF THEM A BRIEF I WROTE.**

---

## 9. Residuals

- **R-C-R9.1** — the two `D142` files carry the same number with no cross-reference in either. **Renumbering was ruled against in round 8 and is not re-opened. The standing remedy is that a count must name its file; this record is not retrofitted onto prior reports.**
- **R-C-R9.2** — **`H3=6` for `D142_binary_artefact_census` is derived and I have not measured what it counts.** covenant-diver reproduced the `H2=8` rule; the `H3=6` derivation is `[inferred]` from the same mechanism and **is not verified.**
- **R-C-R9.3** — **the parity metric is retired, not replaced.** No working parity verdict exists. Fence state and span checks cover the actual failure mode; **whether they cover every malformation a backtick span can produce is not established.**

---

*End of record. No lane artefact edited. `_lead_validate_reports.ps1` is a Lead instrument (`_`-prefixed) and is not for commit. Companion records: `_CORRECTION_R8_1`, `_INSTRUMENT_RULE_38`.*
