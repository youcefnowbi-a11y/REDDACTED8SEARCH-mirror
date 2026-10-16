# _ROUND9_DISPATCH_LEDGER — ten tasks, eight lanes, one read-overlap declared

**Author:** `lead` · **Round 9 continuation** · **Scope owner:** `lead`
**SCOPE:** the ten tasks dispatched in the round-9 continuation, their owning lanes, and their declared write scopes.
**DEFINER SCOPE:** a task is defined by its output filename and the residual or pairing question it closes.
**CONDITIONAL SCOPE:** this ledger records dispatch only. It makes no claim about any result, and no task is counted as done because it was dispatched.
**COUNTED:** **10** dispatched tasks across **8** lanes. Zero outputs existed at dispatch time. **Zero write collisions.** **One read-overlap**, declared below.

---

## 0. Why these ten and not others

**The source layer already holds 80+ deep reports.** Raw coverage is not the gap. **The gap is two things:**

1. **PAIRINGS** — a source finding whose reachability or exploitability is a *binary* question, answered against the compiled artifact. The objective names four; three are or were open.
2. **CHAINS** — mechanisms that cross file and layer boundaries, where the security property depends on every link.

**D153 is the proof that this is the right target.** Its chain looked real in D146 — three addresses, described as contiguous, presented as a call chain. **It was refuted the moment someone read the call edges.** Contiguity was real; the relationship derived from it was not.

> ### **A CORPUS CAN BE FULLY ENUMERATED AND STILL HAVE AN UNREAD RELATIONSHIP BETWEEN ITS PARTS. THAT IS WHAT THESE TEN TASKS GO AFTER.**

---

## 1. The ledger

| task | lane | closes | write scope |
|---|---|---|---|
| **D159** | sliver-diver | **R-153.2** + R-153.1 | `D159_*.md` |
| **D160** | covenant-diver | **R-158.1** | `D160_*.md` |
| **D161** | havoc-deep | **R-147.1** | `D161_*.md` |
| **D162** | archive-diver | D91/D85 pairing | `D162_*.md` |
| **D163** | msf-diver | **R-154.2** + **R-142.4** | `D163_*.md` |
| **D164** | android-diver | AndroRAT binary layer | `D164_*.md` |
| **D165** | source-diver | **R-155.1**, **R-155.2** | `D165_*.md` |
| **D166** | covenant-diver | D93 pairing | `D166_*.md` |
| **D167** | archive-diver | D150 WASM residuals | `D167_*.md` |
| **D168** | covenant-deep | Covenant authority chain | `D168_*.md` |

**All ten output paths verified free at dispatch. Written by different lanes to different files — disjoint.**

---

## 2. The one read-overlap, declared

**`Common.cs` (40,613 B) is read by both D160 and D166.**

- **D160** reads it as part of the 11-switch walk.
- **D166** reads it for the two `Split` sites D148 found — `:25 Split("bin")[0]` and `:89 Split(Path.DirectorySeparatorChar).Take(Count-1)`.

**Read-overlap is not a write conflict.** Both lanes are consumers; neither writes to it. **The outputs are `D160_*.md` and `D166_*.md`, which are distinct.** Declared rather than resolved, because resolving it would waste a lane.

**`archive-diver` holds two tasks — D162 (PE/Go binaries) and D167 (WASM modules).** Different file populations entirely; **disjoint.**

---

## 3. What each lane was told to be careful about

**Every dispatch carried the same four standing constraints, and they are the round-9 record applied forward:**

1. **The D149 shape audit is mandatory.** No `len(x) >= 0`. No assertion that cannot fail. **Name a case you expected ABSENT and show it absent; name one you expected PRESENT and show it present.**
2. **If both controls return the same value, the instrument is degenerate and the lane must SAY SO** before reporting any zero — rather than reporting the zero and calling it a measurement.
3. **`symbol present` is not `code reachable`.** D153 retracted a chain built from address adjacency; the same trap is live in D159 and D162.
4. **Ghidra's `getFunctionAt` snaps to misaligned boundaries** and merged two distinct `commands` functions 384 bytes apart. **Address-explicit scans over the function model. No `-readOnly`. No REA `open_binary`.**

---

## 4. The count-disagreement record this round

**Six disagreements between Lead counts and lane counts. All six resolved in the lane's favour.**

| # | Lead | lane | cause |
|---|---:|---:|---|
| 1 | 52 switches | **65** | my walker globbed `.cs` only; `.razor` holds 9 |
| 2 | H2 = 9 | H2 = 8 | **two files carry D142**; both correct |
| 3 | 31 `+build` | **30** | my denominator included pupy, outside the five Go targets |
| 4 | `btickODD` flag | clean | character parity of quadruple-backtick spans |
| 5 | `_d140_` file flagged forbidden | legitimate | my regex matched the substring inside a report *about* D140 |
| 6 | sweep returned 0 | 0 — but so did the control | `-Include` without `-Recurse` matched nothing |

> ### **SIX DISAGREEMENTS, SIX LANE WINS, FIVE OF THE SIX CAUSED BY MY OWN SCOPE FILTER.**

**Item 6 is the one to remember: the sweep read zero files and reported a clean negative, and the control returned zero for the same reason, so the two zeros agreed with each other.** Rule D141: identical output from two different inputs is not agreement; it is evidence the input never reached the function.

---

## 5. State at dispatch close

- **Round 9 delivered and pushed: 7 lane reports + 2 Lead instruments, 2 commits, both exit-0 with API `MATCH`.**
- **All 8 lanes running.** No lane died; no report was written by the Lead as a substitute this dispatch.
- **Nothing in this ledger is a result.** Every task is `dispatched`, not `closed`.

---

*End of ledger. No lane artefact edited. Instruments remain unstaged.*
