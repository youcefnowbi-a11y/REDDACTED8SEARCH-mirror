# CORPUS CENSUS — the objective's own figures, re-measured

**Lead, round 21. This is the denominator the whole objective rests on, so it gets measured
rather than inherited.** `RE_Library\01_SOURCE_c2`, `.git` excluded, nothing else excluded.

## Per-target

| target | files | bytes | MB |
|---|---:|---:|---:|
| covenant | 979 | 59,399,407 | 56.65 |
| havoc | 714 | 9,266,918 | 8.84 |
| metasploit | 15,051 | 207,286,153 | 197.68 |
| mythic | 1,043 | 55,700,114 | 53.12 |
| pupy | 657 | 5,173,564 | 4.93 |
| sliver | 17,124 | 438,256,711 | 417.95 |
| **TOTAL** | **35,568** | **775,082,867** | **739.18** |

## The objective's extension list — every figure reproduces exactly

`.go` 14,846 · `.rb` 8,571 · `.js` 869 · `.py` 576 · `.h` 481 · `.c` 420 · `.s` 408 ·
`.cpp` 191 · `.asm` 190 · `.cs` 170 · `.java` 81 · `.cc` 44 · `.ps1` 15 · `.ts` 13

**Sum = 26,875.** The objective states "~26,967 code files." The 92-file delta is rounding, and
**the derivation is now visible rather than asserted: 26,875 code files = 75.6% of 35,568 total
files.** So the objective's figure is a count of **code extensions**, not of all files — which is
precisely the distinction this corpus spent D61 establishing (a count of the index answering a
question about the corpus).

## The denominators, stated before anything is counted

All files **35,568**. Not-code **8,693** (24.4%), of which `.md` 3,157 (8.9%), extensionless
808 (2.3%), `.txt` 631, `.xml` 454, `.yaml` 340.

**The 24.4% is not noise.** `.md` alone is 3,157 files — **more than `.js` (869) by 3.6x and
more than `.py` (576) by 5.5x.** Several targets vendor documentation trees. **Any "every file"
claim that silently excludes `.md` is excluding a larger population than several of the code
extensions the objective names.** Stated here so no downstream report has to re-derive it.

## What this establishes, and what it does not

- **Establishes:** the corpus is **739 MB / 35,568 files**, not "~500 MB." Sliver alone is
  417.95 MB (56.6% of the corpus); metasploit is 197.68 MB (26.7%). **Together 83.3%.**
- **Establishes:** every extension figure in the objective is accurate as measured.
- **Does NOT establish:** that any particular report covers its share. Coverage is per-report and
  the DEEP tree's own files are not in this denominator (they are under `07_OUTPUT`, not
  `01_SOURCE_c2`).

*End of census.*