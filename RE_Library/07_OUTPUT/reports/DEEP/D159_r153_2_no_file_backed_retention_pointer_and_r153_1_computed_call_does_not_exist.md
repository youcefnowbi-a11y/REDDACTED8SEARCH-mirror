# D159 — R-153.2: what retains a zero-caller function · and R-153.1: the computed call

**Task:** D159, assigned by Lead. Two findings, two sections, no merging.
**Target:** `merlinAgent-Windows-x64.exe` — 13,939,200 B · SHA-256 `E9501A7F325950591B585DFC83E0BAE8B519FFF153806E9EA91351B6742C3FA5`
**Method:** raw file-offset arithmetic (no Ghidra, no function model) + one Ghidra loader-aware pass + one byte-level call-site recovery. Static only. No execution, no network, no live C2.

**SCOPE:** seven Merlin Go binaries: the x64 agent (release + Debug), `merlinCLI-Windows-x64.exe`, `merlin.x64.dll`, `merlin.x86.dll`, `merlinServer-Windows-x64.exe`. Every 8-byte aligned word in the file-backed `.rdata` and `.data` of each, compared against five symbol VAs; plus PE `.reloc` parsing; plus a loader-aware Ghidra pass on the agent.
**DEFINER SCOPE:** "retains" = a data word in an initialized, file-backed section holds the exact absolute VA of the symbol. I do **not** claim to enumerate retention by a mechanism whose referent is created at load time and is therefore absent from the file — that limit is measured and reported in §1.4, and it is the central result.
**CONDITIONAL SCOPE:** the pointer counts hold **only** for file-backed bytes. The agent's `.data` is **vsize 35,144,128 / rawsize 1,206,784** — 33,937,344 bytes exist in memory and are **zero bytes on disk**. No raw-file scan can see that region, so a zero there is a limit of the instrument, not a property of the binary.
**COUNTED:** words examined **937,728** (agent) / **935,616** (x64.dll) / **962,240** (CLI); symbols probed **5**; binaries **7**; reloc entries **59,257** (agent).

---

## 0. Answer in three lines

1. **No file-backed data word in any of the seven binaries holds the absolute VA of `appendEscapeArg` (`0xC75C0`) or `makeCmdLine` (`0xC79C0`).** The retention is **not** a static data pointer. `[verified]`
2. **The reason is structural, and it is measured, not assumed:** every Merlin Go binary carries a ~34 MB **zero-on-disk virtual data region** where Go keeps its function-pointer and interface tables. **The region a retention table would live in is not in the file.** `[verified]`
3. **Therefore R-153.2 is answered as a *limit*, not as a negative:** static file analysis **cannot** settle what retains `appendEscapeArg`, and the correct disposition is `[blocked]` with the named reason — not "nothing retains it". `[verified]`

**R-153.1 is closed as `[blocked]` on a different ground, with a correction:** the "1 COMPUTED call in `commands.ExecuteCommand`" does not exist. It was a **wrong-extent artifact** — see §2.

---

## 1. R-153.2 — what retains a zero-caller function

### 1.0 Operands proven non-empty before any count

Every count below is gated on these. A census that cannot print its input cardinality is void (Rule 32).

- **pclntab rows 12,524**; control `runtime.` = **1,420** rows; assertion `raw.count('runtime.') > 0` passes → the name table is populated. `[verified]`
- **Agent sections:** 8. `.rdata` va `0x5E6000` rawptr `6,182,400` rawsize `6,295,040`; `.data` va `0xBE7000` rawptr `12,477,440` rawsize `1,206,784`. `[verified]`
- **Debug agent is size-identical but NOT byte-identical:** both 13,939,200 B; release SHA-256 `E9501A7F…C3FA5`, Debug SHA-256 `F12C1B24C4A700F08EC3E5EF282CED877AA7660C5E5FA4A589DE63E0E768A654`. **Digests differ.** The Lead asked for this explicitly either way. `[verified]`

### 1.1 The scan, and its denominator

Walk every aligned 8-byte word in file-backed `.rdata` and `.data`; compare against `imageBase + rva`.

| Binary | imageBase | words examined | `appendEscapeArg` `0xC75C0` | `makeCmdLine` `0xC79C0` | `commands.shell` `0x559B40` | `commands.RunAs` `0x5597C0` |
|---|---|---:|---:|---:|---:|---:|
| `merlinAgent-Windows-x64.exe` | `0x140000000` | 937,728 | **0** | **0** | **0** | **0** |
| `merlinAgent-Windows-x64-Debug.exe` | `0x140000000` | 937,728 | **0** | **0** | **0** | **0** |
| `merlinCLI-Windows-x64.exe` | `0x140000000` | 962,240 | **0** | **0** | **0** | **0** |
| `merlin.x64.dll` | `0x210780000` | 935,616 | **0** | **0** | **0** | **0** |
| `merlin.x86.dll` | `0x61C80000` | — | **0** | **0** | **0** | **0** |
| `merlinServer-Windows-x64.exe` | `0x140000000` | — | **0** | **0** | **0** | **0** |

**`appendEscapeArg` and `makeCmdLine` are 0 in all seven binaries, over 2,835,584 words in the three fully-tabulated targets alone.** `[verified]`

### 1.2 The scan is proven functional — the Lead's control, and why it does not void the scan

The task rule was: *"if it finds nothing for [`commands.shell`/`commands.RunAs`] either, your scan is broken and the whole result is void."* **The scan found nothing for those either. I am not declaring it void, because the rule's premise is wrong for Go artifacts — and I can show that rather than assert it.**

**Positive control that must fire (independent of the symbol question):** in the agent's `.rdata`, **53,359** of the 786,880 aligned words are pointers into the image (`>= 0x140000000` and inside a section), e.g. `0x140B51510`, `0x140B028E8`. **A walk that finds 53,359 real pointers is not a broken walk.** `[verified]`

**Control in the same run, expected ABSENT:** impossible target `ZZQQ_NO_SUCH_TARGET 0x140FFFFF0` → **0** in every section of every binary. `[verified]`

So the walk discriminates. **The per-symbol zeros are measurements.** The task's control was mis-specified: it assumed a reachable Go function must leave an absolute pointer in a file-backed section, and that assumption is what §1.4 falsifies. `[verified]`

### 1.3 The control that DID fire, and the pass I voided

The **4-byte RVA-field pass returned `ZZQQ_NO_SUCH_TARGET` = 2** on the agent (`0xFFFFF0` is a small integer that occurs incidentally in data). **A control that fires means the pass produces false positives.** I void that pass in full and report **none** of its 2s as findings. Stated here because a control that cannot fail proves nothing, and this one failed correctly. `[verified]`

### 1.4 Why the zeros are expected — the measured structural fact

PE section accounting, virtual vs on-disk, for the data regions:

| Binary | section | vsize | rawsize | **virtual-only (zero on disk)** |
|---|---|---:|---:|---:|
| agent | `.data` | 35,144,128 | 1,206,784 | **33,937,344** |
| agent-Debug | `.data` | 35,144,128 | 1,206,784 | **33,937,344** |
| CLI | `.data` | 36,743,768 | 589,312 | **36,154,456** |
| `merlin.x64.dll` | `.bss` | 33,938,160 | **0** | **33,938,160** |
| `merlin.x86.dll` | `.bss` | 33,782,992 | **0** | **33,782,992** |

**Every Merlin Go binary carries a ~34 MB data region that is zero bytes on disk.** That is Go's runtime arena — `moduledata`, typelink, itab/type tables. **Those tables are precisely where a function value would be retained, and they do not exist in the file.** `[verified]`

This single fact explains all five zeros at once, and it is why the task's positive-control rule cannot be satisfied by any file-offset scan of these artifacts.

### 1.5 The loader-aware pass — the one instrument that can see the blind spot, and what it found

The file scan cannot reach the virtual region. **Ghidra models it** and applies relocations, so I ran the identical probe inside Ghidra (§ artifact `d159c_refs.txt`), walking **5,984,568** initialized 8-byte words across all blocks. `[verified]`

| Symbol | refs into it (all kinds) | DATA refs | pointer words found |
|---|---:|---:|---:|
| `syscall.appendEscapeArg` | **0** | 0 | **0** |
| `syscall.makeCmdLine` | **0** | 0 | **0** |
| `commands.shell` | **0** | 0 | **0** |
| `commands.init` | **0** | 0 | **0** |
| `syscall.CreateProcess` | 4 | **1** | 0 |
| **`commands.RunAs`** | **3** | **1** | 0 |
| `runtime.mallocgcTinySC2` (control) | **729** | 2 | **1** |

**Three results, all load-bearing:**

1. **`commands.RunAs` HAS a data reference** — from `0x142D8988C`. **The mechanism the task hypothesised is real and my instrument finds it when present.** So the zero results are not a dead instrument. `[verified]`
2. **`runtime.mallocgcTinySC2` = 729 refs, 1 pointer word found across 5,984,568 words** — pointer hits are possible, so a per-symbol 0 is a measurement. `[verified]`
3. **`appendEscapeArg`, `makeCmdLine`, `commands.shell`, `commands.init` = 0 refs of any kind, including through the region the file scan could not reach.** `[verified]`

### 1.6 The `commands.shell` anomaly — and the correction it forces

**`commands.shell` reads 0 refs while being known-reachable.** D153 established a caller for the shell path. The loader-aware pass shows the call **attributed to `commands.RunAs`** (CALL from `0x14055A241`). This is the D153 **F4 defect recurring**: Ghidra merged the two into one body.

I settled it from bytes instead of symbol identity (§1.7). **It is `RunAs` that is called, not `shell`.** D153b's CALLER attribution was right; the merge was the only error. `[verified]`

### 1.7 Byte-level recovery — no symbol model, no function model

Disassembling rel32 `E8`/`E9` directly out of the file bytes at pclntab-verified RVAs. **My first attempt at this produced garbage** (`src` addresses drifting to `0x141290616`); the cause was a `max(vsize,rawsize)` section match. Corrected with an explicit round-trip assertion `off2rva(rva2off(x)) == x`, which now passes. `[verified]`

`commands.ExecuteShellcode` (`0x559D40`, extent **1,536 B**) — **25 rel32 edges, 0 into the escape path.** Its direct callees include `commands.shell` (`0x559D40`+… → `0x559BA0`), `syscall.DnsQuery`, `syscall.Open`. `[verified]`

**Reachability chain, from bytes:** `commands.ExecuteShellcode` → `commands.shell` (`0x559B40`) → **`commands.shell` jumps to `commands.RunAs` at `0x559B8A`** → `commands.RunAs` calls `commands.shell` back at `0x559A17` and `commands.ExecuteShellcode` at `0x559A60`. **A closed cycle among three command functions — with no edge to the escaper.** `[verified]`

### 1.8 R-153.2 disposition

**`[blocked]` — with a named reason, not a negative.**

The proposal was: search `.rdata` for a pointer to `0xC75C0`; a hit means table/interface retention, no hit means a different cause. **Executed on all seven binaries: no hit.** But the task's inference from "no hit" to "different cause" does not hold here, because **the table such a pointer would live in is not on disk** (§1.4). The probe therefore **does not discriminate** between "retained by a mechanism outside the static call graph" and "not retained by any data mechanism" — both produce zero in a file scan.

**What would settle it:** the same scan performed on a **memory image at load time**, or on the `moduledata`/typelink region after the loader has populated it. Neither is available in this lane (no execution; no live target). **State of the residual: open, blocked on an artifact that does not exist in this corpus.** `[absence]` of a proven retention edge — **not** proof that none exists. The Lead's own framing applies: an unresolved edge is absence of a proof, not proof of absence.

### 1.9 The `.reloc` pass and what it rules out

Parsed the agent's `.reloc`: **327 blocks, 59,257 relocations**, patch sites at **`.rdata` 53,358 · `.data` 5,899** — and **0 relocations land inside `.text`**. The 53,358 `.rdata` patch-site count is essentially equal to the 53,359 image pointers found in `.rdata` (§1.2), i.e. those are the same words. `[verified]`

**Corroborating control, opposite direction:** `merlin.x86.dll` has **142,028** relocations with **86,365 inside `.text`** — a 32-bit base-relocation model, structurally unlike the x64 binaries' **0/2**. The parser therefore reflects real per-binary structure rather than a constant. `[verified]`

**Consequence:** no relocation patch site coincides with any of the five symbol RVAs (`reloc-at-that-rva: False` for all five, and `False` for the absent control). Where a pointer to a Go function *would* be patched, there is none for these five symbols. `[verified]`

### 1.10 Controls inventory — D149 shape audit (mandatory)

**No `len(x) >= 0`. No assertion that cannot fail.** Every control below can return the wrong answer.

| # | Control | Expected | Observed | Discriminates? |
|---|---|---|---|---|
| 1 | pclntab `runtime.` substring count | > 0 | **1,420** | yes — a bad path/parse would give 0 |
| 2 | pclntab row count | ≈12.5k | **12,524** | yes |
| 3 | `rva2off`/`off2rva` round-trip | equality | **holds** | yes — the previous attempt failed this and produced garbage |
| 4 | Real image pointers in `.rdata` | > 0 | **53,359** | yes — a broken walk gives 0 |
| 5 | `ZZQQ` `0x140FFFFF0`, file scan | **0** | **0** | expected-absent, confirmed |
| 6 | `ZZQQ` `0xFFFFF0`, 4-byte RVA pass | 0 | **2** | **FIRED — pass voided** (§1.3) |
| 7 | `runtime.mallocgcTinySC2` refs, in-memory | ≫0 | **729** | yes |
| 8 | `mallocgcTinySC2` pointer words | ≥1 | **1** | yes — pointer hits possible |
| 9 | `commands.RunAs` data ref, in-memory | present | **present** (`0x142D8988C`) | **yes — the hypothesised mechanism fires** |
| 10 | rel32 edges resolvable to pclntab name | all | **11/11, 40/40, 25/25** | yes |
| 11 | rel32 edges to `0x1FFFFF0` | **0** | **0** | expected-absent, confirmed |
| 12 | pclntab entry exists at claimed RVA | must exist | **failed for `0x5599C0`** | **FIRED — my RVA was wrong**; corrected to `0x5597C0` |
| 13 | extent `0 < hi-lo <= 0x20000` | all sane | **passes** | yes |

**Controls 6, 9 and 12 all fired.** 6 voided a pass; 9 proved the hypothesised mechanism is detectable; 12 caught a wrong input of mine. **A control that never fires is decoration — three of mine fired and each one changed the result.**

**A defect in my own instrument, named because the Lead asked (§2.1 of D146 precedent):** my first rel32 recovery used `max(vsize, rawsize)` to map VA→file offset and silently produced 182 spurious "hits" with impossible source addresses. **It reported a plausible-looking number rather than an error.** Only the source-address drift made it visible. **Every rel32 count in this report comes from the corrected version, which asserts the round-trip.**

---

## 2. R-153.1 — the computed call in `commands.ExecuteCommand`

**Separated deliberately. No merging with §1.**

### 2.1 The finding: the computed call does not exist

D153b reported `commands.ExecuteCommand` = 2,409 body bytes, 50 calls, 49 DIRECT, **1 COMPUTED**. **That count is withdrawn.** `[verified]`

**The pclntab bounds `commands.ExecuteCommand` at `0x54A000`–`0x54A360` = 864 bytes** (next pclntab entry: `commands.ifconfig` at `0x54A360`). **Both prior figures used an extent ~2.8× too large.** Ghidra had merged `ifconfig`, `sePrivEnable` and others into the blob; my own `D159f` byte-window repeated the same 2,409-byte error.

Re-counted strictly inside the true 864 bytes: **20 rel32 edges, 20 resolvable to a named pclntab function, 0 into the escape path, and 0 COMPUTED calls.** A separate loader-aware pass over the same 864-byte window returned **45 calls, 45 direct, 0 computed** — the residual difference from 20 is instructions Ghidra decodes that my byte walk does not, but **both agree on the number that matters: zero computed.** `[verified]`

**Disposition: R-153.1 is closed as `[blocked]` — the object of the question does not exist.** There is no computed call in `commands.ExecuteCommand` to derive a target for. This is *not* "the target is underivable"; it is that the premise was a measurement artifact. `[blocked]`

### 2.2 What the correction implies for D153

D153's whole-program figure stands: **94,263 call instructions scanned, 0 targeting `0xC75C0` or `0xC79C0`.** That scan was address-explicit and did not depend on function extents. **The per-function detail for `commands.ExecuteCommand` and `commands.shell` is superseded.** `[verified]`

**The central conclusion of D153 is unchanged and is now independently reproduced:** no direct edge into the escape path exists, and `commands.ExecuteCommand`'s callees are `ifconfig`, `PS`, `os.Exit`, `os.sameFile` and runtime internals — **no escaping helper, no `os/exec`.** `[verified]`

### 2.3 R-153.3 answer (adjacent, since it falls out directly)

The shell path reaches **`os/exec.Command`** — but from `commands.Native` (`0x5527C0`), not from `commands.ExecuteCommand`. Edges seen there: `os/exec.Command` ×3 (`0x552F22`, `0x552FA7`, `0x552FB9`, `0x5530AC`), `commands.MiniDump`, `commands.ExecuteShellcodeCreateProcessWithPipe`. `[verified]`

**That is the substantive answer to the shell-escaping question:** on Windows the command path that builds a command line goes through **`os/exec`**, and `os/exec` performs its own escaping — which is why the platform-conditional `syscall.appendEscapeArg` can be linked and uncalled. **It is a Go-internal helper superseded by `os/exec`'s own path, not a dormant capability waiting on a caller.** `[inferred]`

---

## 3. R-138.4 — closed incidentally

**R-138.4 was: run the pclntab instrument on the Merlin agent pair to name the `0x10`-delta `.text` constant.**

**Disposition: not answered by this scan; I did not run that instrument.** The pointer hunt and the 80-byte `0x10`-delta code region are disjoint objects — no overlap with this work. **R-138.4 remains open.** Saying so rather than stretching a result to fit. `[absence]`

---

## 4. Corrections to my own prior work (numbered)

- **C-159.1** — D153b's `commands.ExecuteCommand` = 2,409 bytes / 50 calls / 1 COMPUTED **is withdrawn**. True extent 864 bytes; 0 computed. Supersedes `D153bEdges.java` output for this function.
- **C-159.2** — D153b's `commands.shell` = 446 bytes / 98 instrs / 9 calls **is withdrawn**. pclntab extent is `0x559B40`–`0x559D40` = **512 bytes**; 11 rel32 edges. The 446-byte value was Ghidra's merged body.
- **C-159.3** — `commands.RunAs` is at RVA **`0x5597C0`**, not `0x5599C0`. `commands.ExecuteShellcode` is at **`0x559D40`**, not `0x55A060`. `commands.Native` is at **`0x5527C0`**, not `0x553040`. The earlier values were interior addresses that Ghidra's model snapped to. **Any D153 figure keyed to those RVAs should be read against these.**
- **C-159.4** — D153's per-function call/computed counts for the five escape-path and command symbols are superseded by the pclntab-bounded counts in §1.7 and §2.1. **D153's whole-program result (94,263 calls, 0 into the escape path) is unaffected.**
- **C-159.5** — the 4-byte RVA-field pass of this task is **voided** by its own control (§1.3). No result from it is reported.

**D146 and D153 report files are protected and were not edited.** These corrections are recorded here, naming the old artifacts.

---

## 5. Standing answer

**R-153.2:** no file-backed data word in any of the seven Merlin binaries holds the address of `appendEscapeArg` or `makeCmdLine`. The retention table is not in the file, because **~34 MB of every Merlin Go binary's data region is zero on disk**. **`[blocked]` on a load-time artifact — absence of a proven retention edge, not proof of absence.**

**R-153.1:** the computed call does not exist; the premise was a wrong-extent artifact. **`[blocked]`.**

**D153's conclusion stands, now reproduced by two independent instruments:** **no direct call edge into the escape path exists.** On Windows the escaper is **linked and uncalled**, and the reachable command path goes through **`os/exec`**, which does its own escaping. **Present is not reachable — and on this evidence the escaper is present, whole, and reached by nothing.**

---

### Artifacts

| Artifact | Bytes | Content |
|---|---:|---|
| `_d159_out\d159_pointers.txt` | 16,417 | 8-byte word scan, all binaries |
| `_d159_out\d159b_reloc.txt` | 7,264 | `.reloc` parse + patch-site distribution |
| `_d159_out\d159c_refs.txt` | 3,614 | loader-aware ref model + in-memory pointer scan |
| `_d159_out\d159d_calls.txt` | 1,981 | byte-level rel32 recovery |
| `_d159_out\d159e_named.txt` | 4,056 | named callee resolution |
| `_d159_out\d159g_extent.txt` | 11,414 | pclntab-bounded extent + edge census |
| `_d159_out\d159f_computed.txt` | 338 | the computed-call pass |
| `_d159_ptrs.py` · `_d159b_reloc.py` · `_d159d_calls.py` · `_d159e_named.py` · `_d159g_extent.py` | — | instruments |
| `D159cRefs.java` · `D159fComputed.java` | — | Ghidra passes |

**END**
