# D141 — Lead verification of the release-vs-debug byte diff: band 13 is `.reloc` not DWARF, band 6 is a fixed-width `.rdata` table, and the 80 `.text` bytes are single operand bytes inside otherwise identical instructions

**Author:** `lead` · **Lane:** `lead` · **Report:** D141 · **Class:** independent re-measurement of a lane claim at byte level
**Reserved:** D141, allocated by `_lead_alloc.py` after `controls` returned `D132*` → True and `D141*` → False (the pair differs, so it is not degenerate).
**SCOPE:** the release-vs-debug byte diff between `merlinAgent-Windows-x64.exe` and `merlinAgent-Windows-x64-Debug.exe`, both 13,939,200 B. This report verifies sliver-diver's D138 section attribution, corrects D130's band framing, and settles the `.text` question that a detection DB depends on.
**DEFINER SCOPE:** PE section table parsed directly from the file headers by `_lead_verify_sections.py`; attribution by FILE OFFSET, not RVA. Disassembly-free — no instruction decoder was used, and every structural inference below is marked at the claim.
**CONDITIONAL SCOPE:** the `.text` conclusion holds for **this pair of builds only**. The `.rdata` table conclusion holds for this pair only. Generalising either to other Merlin binaries is explicitly NOT claimed.
**COUNTED:** all 13,939,200 bytes of each file; 64,565 differing bytes; 8 sections; 80 `.text` differing bytes.
**STATUS:** [verified] by independent re-measurement unless tagged at the claim.

---

## 0. Why the Lead re-measured this

D130 reported the release/debug diff as a 1 MB **band histogram** with band 13 holding 62,896 bytes and characterised it as *"97.4% DWARF tail"*. sliver-diver (D138) then attributed the same diff to **PE sections** and reported `.text 80`.

**The `.text` number is the one a detection DB lives or dies on.** If executable text differs between release and debug, any fingerprint keyed on those bytes is build-configuration-specific and the DB is unsound. If it does not, the fingerprint is stable across both builds.

I therefore re-measured the attribution from the headers rather than accept either instrument's summary.

---

## 1. Operand control — the instrument must have opened both files

```
release : merlinAgent-Windows-x64.exe        13939200 B  MZ=True
debug   : merlinAgent-Windows-x64-Debug.exe  13939200 B  MZ=True
equal length : True
distinct bytes: True
```

Both operands non-empty, both valid PE, same length. **Offset-wise attribution is therefore meaningful** — the guard that would abort the whole measurement if the lengths differed was present and did not fire.

**Coverage control:** the 8 raw section ranges cover **13,937,664 of 13,939,200 bytes = 99.99%**; the **1,536** uncovered bytes are the DOS/NT headers before the first raw section at 1,536. **Attribution closes.**

---

## 2. The section table, measured

```
name         vsize     vaddr     rawsize     rawptr   chars
.text       0x5e4f91   0x1000     6180864       1536  0x60000020
.rdata      0x600cb0   0x5e6000   6295040    6182400  0x40000040
.data      0x21841c0   0xbe7000   1206784   12477440  0xc0000040
.pdata      0x1fcd4  0x2d6c000    130560   13684224  0x40000040
.xdata         0xb4  0x2d8c000       512   13814784  0x40000040
.idata        0x57c  0x2d8d000      1536   13815296  0xc0000040
.reloc      0x1da5c  0x2d8e000    121856   13816832  0x42000040
.symtab         0x4  0x2dac000       512   13938688  0x42000000
```

**Optional header magic `0x20B` = PE32+. Eight sections. There are NO `.debug_*` or `.zdebug_*` sections in this image.** That single absence falsifies D130's "DWARF tail" characterisation by inspection — a PE cannot have a DWARF tail in a section that does not exist.

The `.text` window is **file 1,536 – 6,182,400**, matching sliver-diver's quoted table exactly.

---

## 3. Attribution — reproduces the lane claim exactly

Verified independently, whole-file, every differing byte assigned by file offset:

| section | claimed (D138) | measured (lead) | match |
|---|---:|---:|---|
| `.reloc` | 62,896 | **62,896** | True |
| `.rdata` | 1,375 | **1,375** | True |
| `.data` | 211 | **211** | True |
| `.text` | 80 | **80** | True |
| outside | 3 | **3** | True |
| **SUM** | **64,565** | **64,565** | **True** |

**Closure: sum == total differing bytes == 64,565 = 0.46319% of 13,939,200.** Every section matches; the lane's attribution is confirmed at byte level by a second instrument.

First differing offset **220 (0xDC)**, last **13,938,267 (0xD4AE5B)**.

---

## 4. Correction to D130 — band 13 is `.reloc`, and that is the EXPECTED difference

D130 called band 13 (the final 1 MB, holding 62,896 differing bytes = 97.42% of the whole diff) the *"DWARF tail"*.

**Measured: `.reloc` occupies file 13,816,832 – 13,938,688. The final 1 MB of the file is the relocation table.** With no `.debug_*` section present at all, the 97.42% is not debug metadata.

This is a **stronger** explanation than D130 could give: a release build and a debug build of the same Go program legitimately differ in their relocation tables. Band 13 is fully explained, and the explanation is the structural one.

**D130's band histogram is not wrong** — I reproduced all eight of its band counts exactly. Its *interpretation* of band 13 is what this report corrects.

---

## 5. The `.text` question — 80 bytes, and what they are

### 5.1 First: the header bytes, three of them

Before any code, **exactly 3 bytes differ, all in the PE headers** (offset 0–1,535):

| offset | optional-header field | release | debug |
|---|---|---:|---:|
| 220 | **`Subsystem`** (opt+68) | `0x2` | `0x3` |
| 308 | `.reloc` virtual size low byte (opt+156) | `0x5C` | `0x58` |
| 640 | same value, second copy (opt+488) | `0x5C` | `0x58` |

**`Subsystem 0x2` = `IMAGE_SUBSYSTEM_WINDOWS_GUI`; `0x3` = `IMAGE_SUBSYSTEM_WINDOWS_CONSOLE`.** The debug build is a console program. That is a **linker flag**, and it explains the offset-220 first-difference exactly: the earliest byte at which two builds with different linker flags can diverge.

The two `0x5C`→`0x58` bytes are the same value recorded twice: `.reloc` virtual size `0x1DA5C` (release) vs `0x1DA58` (debug), a **4-byte difference**. The section table is otherwise byte-identical — field-by-field comparison of all 8 headers found **this one field** as the only difference.

**`ImageBase` is IDENTICAL in both builds: `0x140000000`.** This matters below.

### 5.2 The `.text` diff is 80 bytes in 77 runs, 74 singletons

```
xor histogram:  x10 n=39   x70 n=16   x30 n=14   xF0 n=8
                x03 n=1    x07 n=1    x01 n=1
bit positions:  bit4 77   bit5 38   bit6 24   bit7 8   bit0-2 6
runs: 77   singletons: 74   16-aligned starts: 5 of 77
```

**My first hypothesis — that every diff clears bit 4 — was WRONG, and the control killed it.** Only 40 of 80 are clearings; the other 40 have bits set in debug that are absent in release. `a & b == b` holds for 40 of 80. I record the falsified hypothesis because the corrected version is what the data supports.

**Bit 4 differs in 77 of 80** — it is near-universal and bimodal, not directional. Bits 5 and 6 differ in 38 and 24. That is a **register-number / `REX` / ModRM-encoding pattern**, not a low-bit-value pattern.

### 5.3 The decisive test — these are SINGLE OPERAND BYTES, not shifted code

| test | result | reading |
|---|---:|---|
| both immediate neighbours (i−1, i+1) byte-identical | **74 of 80** | each diff is one byte inside one instruction |
| all 8 bytes either side byte-identical | **70 of 80** | the instruction is otherwise the same |
| inside a wider differing region | 10 of 80 | residual |

**If the two builds had different code or shifted layout, neighbouring bytes would differ too.** They do not, for 74 of 80. The instruction stream is identical and a single operand byte within an instruction changes.

RVA distribution of the 80 bytes over 64 KB windows:

```
0x0D0000 : 1     0x210000 : 18     0x430000 : 1
0x580000 : 17    0x5A0000 : 43
```

Five tight clusters, not a uniform scatter and not a monotonic tail.

**Interpretation, tagged [inferred]:** these are displacement/immediate operand bytes in `mov`-family encodings where the two builds made different local encoding choices. `ImageBase` is identical and `.reloc` block count is identical (15,179 both), so this is **not** address-base propagation — which was my second falsified hypothesis.

### 5.4 What this means, and it is the point of the report

**The `.text` bytes that differ are operand bytes at 80 positions, 74 of them surrounded by identical bytes, in 5 localised clusters.** The surrounding executable stream is the same.

**Therefore a detection fingerprint must NOT key on raw `.text` bytes at those 80 offsets** — they are build-configuration-sensitive. It may key on:

- the **instruction stream** (identical at 74 of 80 positions, per the neighbour test);
- the `.rdata`/`.pclntab` **name and string tables**, which D130 already measured as 12,525/12,525 rows identical case-sensitively across these same two builds;
- the **section structure**, which is byte-identical apart from one 4-byte size field.

This is the concrete, bounded statement a detection DB needs, and it was **not available from D130's band histogram**.

---

## 6. Band 6 — a fixed-width record table in `.rdata`, not code

D130 left band 6 unexplained: **1,375 differing bytes at file offset 6,291,456**.

Measured: **file offset 6,291,456 falls in `.rdata` (6,182,400 – 12,477,440), not `.text`.** All 1,375 band-6 bytes are `.rdata`.

sliver-diver reported 784 runs with 500 singletons at 16-byte-aligned offsets, consistent with **fixed-width records with a handful of differing fields** — a build-configuration-dependent read-only data table.

**Lead verification status: the SECTION ATTRIBUTION of band 6 (`.rdata`) is [verified] here**, because it follows from the section table and reproduces in my attribution. **The internal record structure (784 runs / 16-byte stride / 500 singletons) is [read] from D138 and NOT independently re-measured by me** — I verified where the bytes live, not how they are organised within `.rdata`.

**Band 6 does not threaten a detection DB**, because it is read-only data and not executable text, and because the `.rdata` region D130 measured there is not the pclntab (12,525/12,525 identical).

---

## 7. Residuals this report leaves open

- **R-141.1** — the internal structure of the 1,375 band-6 bytes (record width, field identity). Attribution verified, organisation not. **[open]**
- **R-141.2** — what the 10 of 80 `.text` diffs that sit inside wider differing regions are. The other 74 are settled. **[open]**
- **R-141.3** — whether the `.text` pattern generalises to the other Merlin agent binaries. **Not claimed, not tested.** **[open]**
- **R-141.4** — the three file-header-differing bytes are fully explained (Subsystem, `.reloc` size ×2). **No residual.** **[closed]**

---

## 8. Corpus-integrity findings recorded in passing

While resolving a number collision for this report, three **multi-file D-numbers** were found in the corpus: **D11 (5 files), D12 (2 files), D121 (4 files)**. Header inspection confirms these are **distinct reports by different lanes sharing a number** — pre-registry work, not corruption. They are a live citation hazard and are **NOT retro-renamed**, because the standing correction rule forbids editing a lane-verified artefact to absorb a later finding.

Separately: **`D132` was found to hold two files** — `D132_havoc_…` (23:08:10, havoc-deep, lock holder) and `D132_covenant_…` (23:11:35, covenant-diver). covenant-diver already held the **D133** lock and registry entry with no file there. The covenant report was therefore moved **D132 → D133**, where its own lock already was. **SHA-256 verified unchanged by the move: `CC0D5BFE…`.** No byte of any artefact was altered.

**Denominator note, applying the corpus's own law:** the DEEP directory holds **157 `.md`**, of which **142** match `^D\d+_` and **15** are `C-*` binary-layer reports and `_*` instrument records. Two earlier figures in this session (155, 156) and this 142 counted **different scopes**. All are correct; none is the corpus size. **A denominator over a growing corpus is a count of its own timestamp.**

---

*End of D141.*
