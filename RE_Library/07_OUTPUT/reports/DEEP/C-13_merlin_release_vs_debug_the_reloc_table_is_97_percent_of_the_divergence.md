# C-12 is taken by havoc-deep. This is C-13.

**Filed:** round 25 by the Lead. **`C-12` was reserved in writing by `havoc-deep` at 20:56:30 with its enumeration shown.** This report takes **`C-13`**.

**Tags:** `[verified]` (measured, invocation shown) · `[read]` (quoted directly) · `[inferred]` (reasoning over evidence).

**Write scope:** this file only. **D95 and D110 are NOT edited.**

---

## §0 Headline — and a correction to a correction

`[verified]` **The two Windows agent builds differ at 64,565 byte positions out of 13,939,200 (0.4632%). `97.4%` of that divergence is in `.reloc`, and `.reloc` does not appear in D110's section table.**

`[read]` **D110's §3.2 table lists five sections and shows its own denominator:**

```
| .text   | 6,180,864 |    80 | 0.0013% |
| .rdata  | 6,295,040 | 1,375 | 0.0218% |
| .data   | 1,206,784 |   211 | 0.0175% |
| .pdata  |   130,560 |     0 | 0.0000% |
| .xdata  |       512 |     0 | 0.0000% |
| TOTAL   |13,813,760 | 1,666 | 0.0121% |
```

`[verified]` **D110's arithmetic is CORRECT: 80 + 1,375 + 211 = 1,666, and 13,813,760 is the sum of the five sections it lists.** D110 did not claim 1,666 was the whole-file divergence. **It bounded its own denominator explicitly and honestly.**

`[inferred]` **A first draft of this report accused D110 of under-reporting and was WRONG.** I read a deliberately scoped total as a global one — **instrument rule 3, the denominator defect, committed by me against another lane's correct work.** The draft was discarded before filing. **The measurement below survives; the accusation does not.**

---

## §1 The measurement

`[verified]` Direct PE section-table parse over both files, byte comparison per section:

```
                       rawSize      DIFF
.text                6,180,864        80
.rdata               6,295,040     1,375
.data                1,206,784       211
.pdata                 130,560         0
.xdata                     512         0
.idata                   1,536         0
.reloc                 121,856    62,896
.symtab                    512         0
```

`[verified]` **Whole-file byte comparison:** `differing bytes: 64,565 · first 0xDC · last 0xD4AE5B · 0.4632%`.

`[verified]` **Arithmetic closes:** 80 + 1,375 + 211 + 62,896 = **64,562**. Whole-file count = **64,565**. **The 3-byte residual is the PE header divergence** — first divergent byte at `0xDC`, inside the header, before any section. **64,562 + 3 = 64,565.** ✅

`[verified]` **The 62,896-byte `.reloc` divergence is a genuine gap in D110's table**, which lists eight sections' worth of PE structure but reports five. `.idata` and `.symtab` are also unreported — **both measured zero**, so their omission costs nothing. **`.reloc` is the only omission that carries a nonzero value, and it is the largest number in the artifact.**

---

## §2 What D110 got right — and it got more right than this report initially credited

`[verified]` **`.pdata` differs by zero bytes. `.xdata` differs by zero bytes.** D110 §3.2 draws the inference correctly: *"Exception unwind tables are generated from code structure. If the code differed, these would differ."*

`[verified]` **D110 §3.3 is titled *"The `.text` divergence is a RELOCATION, not code"* and it is correct.** It counted **80 bytes across 77 runs, 74 of them single bytes, every one at the same −16 delta** — and identified that delta as consistent with address fixup.

`[inferred]` **This report's `.reloc` observation is the SAME finding one layer down.** D110 established that `.text` changes are address fixups. **This report extends it: the address fixups are collected in `.reloc`, and that is where the bulk of the divergence physically lives.** D110 found the mechanism; this report sizes it.

`[verified]` **D110's `.rdata` = 1,375 reproduced exactly**, including the identification of `-H=windowsgui` at `.rdata` offset `0x651A2` and `main.psk=merlin` at `0x65040`.

`[inferred]` **D110's instrument was working and its section table was correct.** Its scope was five sections; mine is eight. **That is the entire difference and it is a scope difference, not a method difference.**

---

## §3 What is genuinely new here

### §3.1 `.reloc` is 97.4% of the divergence

`[verified]` **62,896 bytes. 45.7× larger than `.rdata`. 97.4% of all divergent bytes.**

`[inferred]` **Nobody has reported this figure.** D110 named "/reloc" once, in a §3.3 heading about `.text`, and did not tabulate it. D95 §3 did not measure sections at all.

### §3.2 The 21-vs-1,666-vs-64,565 question, settled as a SCOPING matter

`[inferred]` **Three figures for one artifact, all correct within their own scope:**

| figure | source | scope |
|---:|---|---|
| **21 B** | D95 §3 | the build-config string delta (15 + 6), verified by substring diff |
| **1,666 B** | D110 §3.2 | five PE sections, denominator shown |
| **64,565 B** | this report | whole file, eight sections + 3 header bytes |

`[inferred]` **The three are not in conflict.** They measure a string, a section subset, and a file. **The corpus's real hazard is that all three will be read as "the difference between the two builds"** — and only the third is that, while only the first is what a detection engineer cares about.

### §3.3 The mechanism, and why the large number is misleading

`[inferred]` The config delta is **14 bytes** (` -H=windowsgui`, D110 §0 claim 2, verified by length arithmetic 713 − 699). **Inserting bytes changes the file offsets of everything after the insertion point.** `.reloc` is a **derived table of address fixups**, so a layout shift rewrites it wholesale **without any change to the logic it describes.**

`[inferred]` **The 62,896-byte `.reloc` divergence and the 14-byte config divergence are the same change, measured at two layers.** D110 §3.3 reached the identical conclusion for the 80 `.text` bytes. **This report generalises it: the derived table absorbs the whole layout shift, which is why it is the largest number and the least informative one.**

`[inferred]` **Operationally: "62,896 bytes differ between release and Debug" is true and will be misread.** A reader will conclude the artifacts are materially different, when `.pdata` and `.xdata` are byte-identical across 131,072 bytes and `.text` moves by 80. **These are the same program.**

`[inferred]` **Rule: before reading a diff magnitude as a change magnitude, ask which differing sections are DERIVED from the others.** Same shape as C-08 §4, where a COFF symbol-table field yielded `nSyms=568480` for one target and `5040` for another — **a derived structure's size is a fact about the derivor, not the subject.**

---

## §4 Status

`[verified]` 64,565 divergent bytes; 64,562 attributed across four sections; 3 in the PE header; arithmetic closes.

`[verified]` `.reloc` = 62,896 B = **97.4%** of the divergence, and **the only nonzero section D110's table omits.**

`[verified]` D110's `.rdata` 1,375, `.text` 80, `.data` 211, `.pdata` 0, `.xdata` 0 **all reproduced exactly.**

`[verified]` D110's 1,666 = 80 + 1,375 + 211 against its own stated denominator. **Correct.**

`[inferred]` **A draft of this report asserted D110 had under-reported; that assertion was mine and it was wrong. Discarded before filing and recorded here so the error is countable.**

`[inferred]` **Corrected by reference. D95 and D110 are not edited.** D110's conclusion — *the code is unchanged* — stands and is strengthened.

`[inferred]` **Open (D110's own R-110.5, not closed here):** the 80 `.text` bytes at constant −16 are consistent with address fixup but not traced to specific referenced addresses. **Resolving the 77 sites against the `.rdata` strings is the next probe**, and it is D110's, not this report's.

**End of C-13.**
