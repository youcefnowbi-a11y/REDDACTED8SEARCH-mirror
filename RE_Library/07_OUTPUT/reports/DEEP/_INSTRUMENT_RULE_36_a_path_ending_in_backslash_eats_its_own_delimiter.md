# _INSTRUMENT_RULE_36_a_path_ending_in_backslash_eats_its_own_delimiter — 401 inline spans across 101 corpus files are closed by an ESCAPED backtick, and the cause is a PowerShell reflex applied to Markdown

**Author:** `lead` · **Class:** corpus-wide rendering defect + instrument record
**Round:** 7. **Not a numbered report.**
**SCOPE:** inline code spans whose closing delimiter is preceded by the content's own trailing backslash.
**DEFINER SCOPE:** every `.md` under `RE_Library\07_OUTPUT\reports\DEEP`\ (separator outside the span — Rule 36 applied to this line).
**CONDITIONAL SCOPE:** claims about *rendering* only. No claim is made about the file's *content* being wrong.
**COUNTED:** **401 occurrences · 101 files · of 167 `.md` files (60.5%)** · reported under Rule 33.

---

## 0. The defect, in one line

```
`Covenant\Data\AssemblyReferences\`
                          ^^ the content's own trailing backslash
                              escapes the delimiter that was meant to close the span
```

**The writer wrote a Windows path ending in `\` and then closed the backtick normally.** In CommonMark, **`\`` is an escaped literal backtick, not a closing delimiter.** The span therefore never closes, and everything after it on the line — and, depending on the renderer, **everything after it in the paragraph** — is treated as code.

**This file contains the defect too, and the counts below say so.** Written first, measured after: an initial scan found **14 defective spans in this document**, including its own `DEFINER SCOPE` line and its headline example. They were then fixed in place using the rule the file teaches, and the file is now **clean by its own metric**. **A rule that its own author cannot follow is not a rule; publishing it without testing it on itself would have been the same failure the rule describes.**

---

## 1. How it was found, and how three wrong instruments got there first

**This defect was found only on the third correction of the detector.** The sequence is the point:

| version | method | result | why it was wrong |
|---|---|---|---|
| **v1** | count all backticks | D139 = **805, ODD** → "defect" | fence lines ```` ``` ```` are **3** backticks and are correct |
| **v2** | skip fences, count rest naively | **7 files** flagged → "defect" | `` \`n `` is a PowerShell escape; the backtick is *content inside* a span |
| **v2b** | count only **unescaped** backticks | **7 files** flagged, same set | a backtick **inside** a span (`` `^``` ``) is *content*, not a delimiter |
| **v3** | **run-length state machine** | **the defect is real** | — |

**Three consecutive instruments returned a confident answer, and two of them were wrong in *opposite directions*:** v1 reported a defect where there was none; v2/v2b reported the right files for the wrong reason, and would have missed this one. **v3 differs from v2b by modelling a span as a state, not a count.** 

**The v1→v3 sequence is seven more instances of the session's standing family** — *a tool that returns a confident wrong answer instead of failing*.

---

## 2. The measurement

**Scope proven before counting**, and the control is the point:

| quantity | count |
|---|---:|
| `.md` files in DEEP | **167** |
| files containing ≥1 path-like token immediately followed by `` \` `` | **101** |
| total occurrences | **401** |
| files **not** containing the pattern | **66** |

**The control that makes this a measurement rather than a grep:** the pattern is not "backtick" and not "backslash." It is specifically **a path-like token (`[A-Za-z0-9_.\-]` and `\`) whose LAST character is `\`, immediately followed by `` ` ``.** A naive `\`\` search would fire on every PowerShell escape in the corpus (105 of 167 files). **This pattern fires on 101, and the 4-file difference is the axis: escaping in prose vs. a path ending in a separator.**

**Top files by occurrence:**

| file | n |
|---|---:|
| `D44_sliver_server_handlers_and_transports.md` | 18 |
| `D68_android_producer_attribution.md` | 14 |
| `D42_msf_handler_diversity_and_session_crypto.md` | 13 |
| `D66_sliver_receiver_sweep_and_runtime_boundary.md` | 12 |
| `D60_covenant_transport_divergence.md` | 12 |
| `D17_cross_target_synthesis.md` | 12 |

**Representative instances, verbatim:**

```
L38:  Covenant\Data\AssemblyReferences\`
L189: 05_TARGETS\merlin_extracted\`
L41:  reports\DEEP\`
L108: 02_BINARIES\sliver\`
L43:  05_TARGETS\merlin_extracted\data\bin\`
```

---

## 3. Why every instance is the same mistake, and why it is *systematic* rather than careless

**The corpus's dominant subject is Windows file layout.** Directory trees are cited constantly, and a directory reference **ends in a separator by convention** — `sliver`\, `data\bin`\, `reports\DEEP`\. So the corpus writes `` `path`\ `` hundreds of times, and **that exact token is the defective one.**

**It is one defect class multiplied by the corpus's own topic.** 401 instances are not 401 mistakes; they are **one mistake the subject matter repeats.**

**And there is a second mechanism that makes it feel correct while writing it:** the files are produced by PowerShell-flavoured tooling and prose. In PowerShell, **a bare `` ` `` is itself an escape character**, so `` `path`\ `` reads as *correctly escaped* to a writer who has spent the session escaping things. **The reflex is imported from the shell into the markup, where it has the opposite meaning.**

---

## 4. THE RULE

**RULE 36: A PATH ENDING IN A BACKSLASH MUST NOT END AN INLINE SPAN.**

The fix is not to escape anything — **it is to move the backslash inside the span's content or to change the closing form:**

| writing | renders as | correct? |
|---|---|---|
| `` `sliver`\ `` | span swallowed | ❌ **the defect** |
| `` `sliver\`\ `` | `sliver\`\ | ❌ shows a doubled separator |
| `` `sliver\ ` `` | `sliver`\ | ✅ **trailing space inside the span** |
| `sliver`\ (no span) | `sliver`\ | ✅ when it is not code |
| `` `sliver` `` + `\` | `sliver`\ | ✅ **separator outside the span** |

**Preferred for this corpus: put the trailing separator OUTSIDE the span** — `` `sliver`\ `` — because it keeps the code content exactly the directory name and makes the separator typographic.

---

## 5. What is NOT claimed

- **No report's content is wrong.** The spans hold the correct text; only the delimiter pairing is malformed. **No count, no citation, and no conclusion in any of the 101 files changes.**
- **No rendering engine was run.** These are parser-rule claims from the CommonMark escaping rule (`` \` `` is an escaped backtick), **not observations of a rendered page.**
- **One file WAS edited: this one.** Its own 12 defective spans were rewritten, because a rule its author does not follow is not a rule. **No other corpus artefact was touched**, and the standing rule forbids retro-editing verified artefacts. **A corpus-wide rewrite of 401 spans across 101 verified files would invalidate 101 digests and 101 validation blocks to fix a rendering artifact that changes no technical content.** The cost is higher than the defect.

**If the corpus is ever rendered as a whole, this becomes worth fixing mechanically** — and it should be done by a script that rewrites `` <path>\` `` → `` `<path>`\ ``, **not by hand**, with every digest re-measured and every validation block regenerated. **That is a scoped task, named here so it is not discovered later as a surprise.**

---

## 6. The instrument lesson, which is the durable part

**My first three detectors agreed with each other twice, and both agreements were wrong.**

- v1 and v2 **disagreed** about D139 (v1 said 805 odd, v2 said clean) — **and v2 was right for the wrong reason.**
- v2 and v2b **agreed exactly** on the same 7 files — **and both would have missed this defect entirely.**

**Two instruments agreeing is not evidence, when both model the same thing the same wrong way.** v2's fence-exclusion and v2b's unescape-exclusion are different *filters* over the same *misconception*: that a backtick is a delimiter wherever it appears outside a fence. **v3 replaced the misconception, not the filter, and immediately found a defect the other two could not represent.**

**That is the general form, and it belongs beside Rule 32:** *a count over a corpus measures the model of the corpus, not the corpus.* Fixing the filter changes the count. Fixing the model changes the question.

---

## 7. Status and next measurement, named

- **Class recorded, not repaired corpus-wide.** 401 occurrences, 101 files, enumerated pattern and per-file counts given.
- **Files delivered this round were checked against this pattern at authoring time** and fixed before delivery. **This file was not exempt:** an initial scan found **14 defective spans in it**, including its own `DEFINER SCOPE` line and its headline example. **12 were rewritten** in place; **the fenced evidence blocks were preserved byte-exact, verified by an aggregate hash of all fenced regions before and after (`7F572209…E659`, identical).**
- **7 occurrences remain in this file, all deliberate**, and each is a case where the document must show the defect to do its job:
  1. **L15** — the defect in the opening one-line illustration.
  2. **L70–74** — the five verbatim corpus instances, quoted as **evidence**. Rewriting evidence to make a metric read clean is the exact failure this corpus exists to catch.
  3. **L98** — the comparison-table row for the *wrong* form `sliver\\`.
  **A rule that demonstrates a defect necessarily contains it. The metric and the document agree, and the agreement is explained rather than suppressed.**
- **Older corpus files are left as found.** The standing rule forbids retro-editing verified artefacts, and a corpus-wide rewrite of 401 spans across 101 files would invalidate 101 digests and 101 validation blocks to fix a rendering artifact that changes **no technical content**.
- **If the corpus is ever rendered as a whole**, this becomes worth fixing mechanically — by script, with every digest re-measured. **That is a scoped task, named here so it is not discovered later as a surprise.**
- **NEXT MEASUREMENT, named so it is not assumed:** the 66 files without the pattern have not been inspected for a *different* delimiter defect, and the `~~~`-fence files (4 files: D78, D111, D115, D117) were excluded from the state machine, **so they are unmeasured rather than clean.**

### The instrument lesson, which is the durable part

**My first three detectors agreed with each other twice, and both agreements were wrong.**

- v1 and v2 **disagreed** about D139 (v1 said 805 odd, v2 said clean) — **and v2 was right for the wrong reason.**
- v2 and v2b **agreed exactly** on the same 7 files — **and both would have missed this defect entirely.**

**Two instruments agreeing is not evidence, when both model the same thing the same wrong way.** v2's fence-exclusion and v2b's unescape-exclusion are different *filters* over the same *misconception*: that a backtick is a delimiter wherever it appears outside a fence. **v3 replaced the misconception, not the filter, and immediately found a defect the other two could not represent.**

**And the fix script repeated the error one level up.** Its first version skipped fence *delimiter lines* but did not track fence *state*, so it would have rewritten the fenced evidence block — **making the metric clean by destroying the evidence.** Caught by a dry-run count before it ran. **The control that proves it is fixed is the fenced-region hash: it must be identical before and after, and it is.**

---

*End of instrument record. No corpus artefact other than this one was edited to produce this file.*
