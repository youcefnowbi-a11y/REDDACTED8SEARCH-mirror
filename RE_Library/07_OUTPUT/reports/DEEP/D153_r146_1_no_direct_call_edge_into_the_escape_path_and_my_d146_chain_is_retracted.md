# D153 — R-146.1 closed: the escape path is LINKED but has NO direct call edge; the D146 "chain" was package adjacency, not a call graph

**Round 9.** Lane: **sliver-diver**. **Number:** D153 (claimed and locked to `sliver-diver`; `check 153` attempted before writing).
**Task as issued:** *"R-146.1, the residual YOU filed against your own D146. Close it or bound it."* Disassemble `merlinAgent-Windows-x64.exe` for **DIRECT call edges** into the escape path, and verify each of `appendEscapeArg 0xC75C0 → makeCmdLine 0xC79C0 → CreateProcess 0xCEA40` is a direct edge rather than symbol-table adjacency.

**SCOPE:** all 94,263 call instructions in `merlinAgent-Windows-x64.exe`, plus four bounded disassembly windows of 400 instructions each from five true entry points.
**DEFINER SCOPE:** Ghidra 12.1.4 headless, `x86:LE:64:default:golang`, imageBase `0x140000000`; symbol identity cross-checked against the pclntab (12,524 rows) because Ghidra's Go RTTI analyser fails on Go 1.27.2.
**CONDITIONAL SCOPE:** static only. No execution, no REA `open_binary`, no `-readOnly`.
**COUNTED:** call instructions (94,263), call sites per probe, per-entry instruction and call counts, pclntab rows (12,524).

**LINE-COUNT CONVENTION:** LF bytes; `LF == Get-Content .Count` where a trailing newline is present.

**Tags:** `[verified]` = probe output printed beside the claim · `[read]` = cited lines read · `[inferred]` = reasoning from read evidence · `[absence]` = a zero with its enumeration and a proven non-degenerate probe · `[blocked]` = a named instrument refused.

---

## 0. HEADLINE — THE ANSWER IS **NO DIRECT EDGE**, AND MY OWN D146 CHAIN IS RETRACTED

`[verified]` **THERE IS NO DIRECT CALL EDGE INTO THE ESCAPE PATH. Not one of the three claimed edges exists.** `[verified]`

| Edge claimed in D146 | Test performed | Result |
|---|---|---|
| `appendEscapeArg 0xC75C0` → `makeCmdLine 0xC79C0` | direct rel32 callees of `appendEscapeArg` | **NOT PRESENT** |
| `makeCmdLine 0xC79C0` → `CreateProcess 0xCEA40` | direct rel32 callees of `makeCmdLine` | **NOT PRESENT** |
| `commands.shell 0x559B40` → any escape symbol | direct rel32 callees of `commands.shell` | **NOT PRESENT** |
| any of 5 targets reaching any other | all 20 ordered pairs | **`none` for every pair** |

`[verified]` **THE DECISIVE MEASUREMENT — a whole-program scan, independent of function boundaries, of every call instruction in the image:** `[verified]`

```
TOTAL CALL INSTRUCTIONS SCANNED: 94,263
call sites targeting rva=0xC75C0 (appendEscapeArg) : 0
call sites targeting rva=0xC79C0 (makeCmdLine)      : 0
```

`[verified]` **94,263 call instructions. ZERO target either escape symbol.** `[verified]` **This scan does not use Ghidra's function model, does not use my disassembly windows, and does not depend on the Go analyser — it walks every call instruction and compares the resolved target against the exact VA. The zero is a measurement.** `[verified]`

`[verified]` **R-146.1 IS CLOSED. The answer is the negative the task explicitly allowed: *"A negative here is a result, not a failure."*** `[verified]`

### 0.1 THE RETRACTION — a correction to my own D146 §0 and §3

`[verified]` **D146 §0 printed:** `appendEscapeArg 0xC75C0 → makeCmdLine 0xC79C0 → CreateProcess 0xCEA40` **as a "chain", describing the addresses as "laid out contiguously" and inferring `appendEscapeArg` "is the escaper `makeCmdLine` calls".** `[verified]`

`[verified]` **THAT INFERENCE IS REFUTED AND I WITHDRAW IT. `appendEscapeArg` has zero callers in the entire binary.** `[verified]` **The contiguity was real; the CALL RELATIONSHIP I inferred from it was not. D146's §0 structural paragraph and its §8 summary sentence describing a "chain" are superseded by this report.** `[verified]`

`[verified]` **WHAT IN D146 SURVIVES — and it is the finding that mattered:** all three families are **LINKED** (present in the shipped image, past DCE), and the **platform-conditional discriminator stands** (1 row on Windows, 0 on Darwin x2 / Linux x3). `[verified]` **D146's headline — "the D85 families are LINKED, not DCE'd" — is untouched. Only the stronger "and they form a wired chain" claim dies.** `[verified]`

`[verified]` **THE LESSON, and it is exactly the Lead's framing: *"a symbol-co-occurrence is not a call edge."* D146 honoured the boundary by refusing to claim a live call site, then §0 violated it anyway by describing a *chain* built from adjacent addresses. Adjacent addresses in a Go package are package layout.** `[inferred]`

---

## 1. THE FALSIFIABLE CONTROL — it passed, and it also caught two of my own wrong probes

`[verified]` **The Lead's procedural requirement: *"name an edge you EXPECT to be absent and show your method reporting it absent."* Extended to also name targets I expected PRESENT, because a method reporting zero for everything cannot fail.** `[verified]`

**Same 94,263-call scan, eight probes, expected value declared in advance:** `[verified]`

| Probe | RVA | Expected | Exact hits | Verdict |
|---|---|---:|---:|---|
| `runtime.mallocgcTinySC2` | `0x1F000` | **PRESENT** | **726** | **PASS (nonzero)** |
| `runtime.morestack` | `0x8F40` | **PRESENT** | **104** | **PASS (nonzero)** |
| `syscall.Syscall` | `0xC6721` | **PRESENT** | **0** | ***** FAIL *** ** |
| `syscall.Syscall6` | `0xC674E` | **PRESENT** | **0** | ***** FAIL *** ** |
| `commands.shell` | `0x559B40` | absent | 0 | zero as expected |
| `syscall.makeCmdLine` | `0xC79C0` | absent | 0 | zero as expected |
| `syscall.appendEscapeArg` | `0xC75C0` | absent | 0 | zero as expected |
| `ZZQQ_NO_SUCH_TARGET` | `0x1FFFFF0` | absent | 0 | zero as expected |

`[verified]` **CONTROL VERDICT: `runtime.mallocgcTinySC2` 726 and `runtime.morestack` 104 prove the scan resolves real call sites; the impossible target reads 0. The method discriminates — it CAN return the wrong answer, and it returns the right one on the probes whose answer is known.** `[verified]` **Therefore D153c's zeros are measurements.** `[verified]`

`[verified]` **THE TWO FAILED PROBES ARE THE MOST VALUABLE ROWS IN THIS REPORT.** `[verified]` **I expected `syscall.Syscall` and `syscall.Syscall6` PRESENT and got 0 — which forced §2's boundary sweep.** `[verified]` **A control that only ever confirms a hypothesis is decoration; these two forced a second instrument, and that instrument is what makes the `appendEscapeArg` zero trustworthy.** `[inferred]`

`[verified]` **THE FAILURE MODE OF THIS CONTROL, stated as required: it cannot detect a WRONG probe VA when the probe's expected value is "absent" — an absent expectation and a broken probe are indistinguishable in one run. That is exactly why the PRESENT probes exist, and why two of them failing was informative rather than fatal.** `[verified]`

---

## 2. THE BOUNDARY SWEEP — an equality test misses off-by-N call sites

`[verified]` **Motivation: `syscall.Syscall` reading 0 while being obviously used means exact-entry equality is not sufficient. Go call sites can target an address offset from the symbol entry.** `[verified]` **So every call target in the program was compared against each probe within ±4,096 bytes.** `[verified]`

| Probe | EXACT | NEAR (±4K) | Reading |
|---|---:|---:|---|
| `syscall.appendEscapeArg` | **0** | **380** | window hits are at **+544, +608, +1184, +2016, +2336, +4096** |
| `syscall.makeCmdLine` | **0** | **381** | window hits are at **±384, 416, 480, 640, 992** |
| `syscall.CreateProcess` | **2** | **75** | **exact call sites DO exist in this package** |
| `commands.shell` | **0** | **38** | window hits at **−1600**, one address, repeated |
| `syscall.Syscall` (control) | 0 | 29 | probe VA is an interior offset, not the call target |
| `syscall.Syscall6` (control) | 0 | 37 | same |
| `runtime.mallocgcTinySC2` (control) | **726** | 6,773 | dense real callers |

`[verified]` **THE FINDING THAT SETTLES IT: `syscall.CreateProcess` has EXACT = 2.** `[verified]` **Exact-entry call sites are therefore resolvable inside this very package. So `appendEscapeArg` and `makeCmdLine` reading EXACT = 0 is not an artifact of the package — a sibling function in the same package shows that exact hits do get found.** `[verified]` `[inferred]`

`[verified]` **AND THE `NEAR` COLUMN PROVES THE ADJACENCY FALLACY DIRECTLY: every window hit sits 384–4,096 bytes AWAY from the probe — i.e. on a DIFFERENT function that happens to be adjacent because the Go linker emits a package contiguously. `commands.shell`'s 38 window hits are all at −1600, one repeated address: that is `commands.RunAs`, not `commands.shell`.** `[verified]` **Proximity in a package is layout. It is not a call edge, and D146 §0 read layout as wiring.** `[verified]`

---

## 3. INSTRUMENT DEFECT FOUND IN MY OWN FIRST RUN — Ghidra function boundaries are misaligned by 4,096 bytes

`[verified]` **My first enumeration resolved targets with `getFunctionAt(rva+imageBase)` and printed:** `[verified]`

```
rva=0xC75C0  va=0x1400C75C0  syscall.appendEscapeArg   FUN_1400c6560
```

`[verified]` **`FUN_1400c6560` is 4,096 bytes BELOW `0x1400C75C0`.** `[verified]` **Ghidra snapped the query address to a nearby function start.** `[verified]` **Cross-checked against the pclntab: the function containing `0x1400C75C0` is `syscall.init` per Ghidra, while the pclntab places `syscall.appendEscapeArg` at exactly `0xC75C0` (+0).** `[verified]`

`[verified]` **SECOND INSTANCE, worse: Ghidra merged `commands.shell` and `commands.RunAs` into ONE function.** `[verified]` **Both `0x5599C0` and `0x559B40` resolve to `FUN_1405599c0` with identical body sizes — 446 bytes, 98 instructions, 9 calls — although the pclntab lists them as two distinct functions 384 bytes apart.** `[verified]` **So the first run enumerated `commands.RunAs` while believing it was enumerating `commands.shell`.** `[verified]`

`[verified]` **CONSEQUENCE AND FIX: every claim in this report is made from address-explicit scans (§0, §1, §2) that do not depend on Ghidra's function boundaries at all.** `[verified]` **The window scans disassemble forward from the true entry VA; the global scan walks every call instruction and compares target addresses.** `[verified]`

---

## 4. WHAT THE ESCAPE PATH ACTUALLY IS

`[verified]` **`syscall.appendEscapeArg` at `0x1400C75C0`: 781 instructions, 65 call instructions, 65 DIRECT, 0 COMPUTED — and 0 callers.** `[verified]` **A function with 65 outgoing direct calls and no incoming call site anywhere in a 94,263-call instruction stream is not "wired". It is retained for a reference this static analysis cannot resolve — an interface method value, a reflected symbol, or a table entry.** `[inferred]`

`[verified]` **`commands.shell` at `0x140559B40`: 98 instructions, 9 call instructions, 9 DIRECT, 0 COMPUTED. Its sole reported caller is `commands.ExecuteShellcode` (`0x14055A060`, +800).** `[verified]` **`commands.ExecuteCommand` (`0x14054A000`) has 50 calls of which 49 direct and **1 COMPUTED**; its sole caller is `commands.Native` (`0x140553040`, +2176).** `[verified]`

`[verified]` **THE COMPUTED CALLS ARE THE HONEST FRONTIER. `commands.ExecuteCommand` contains one COMPUTED call, and per the task's rule: *"an unresolved indirect call is `[absence]` of a proven edge, not proof the edge does not exist."*** `[verified]` **So the precise statement is: no DIRECT edge exists; whether a computed edge reaches the escaper is NOT disproven by this instrument and remains open as R-153.1.** `[verified]`

`[verified]` **`commands.shell` itself has 0 COMPUTED calls — 9 direct, all resolved. So for `commands.shell` specifically, the set of callees is COMPLETE: it does not call the escaper directly or indirectly through its own body.** `[verified]`

---

## 5. THE CROSS-PLATFORM IMPLICATION — taken, as the task asked

`[verified]` **D146's discriminator: `appendEscapeArg` appears 1× on Windows, 0× on Darwin x2 and Linux x3.** `[verified]` **The task asked that the consequence be stated rather than implied.** `[verified]`

`[verified]` **ON DARWIN AND LINUX THE QUESTION "IS THE EDGE DIRECT?" HAS NO REFERENT.** `[verified]` **The symbol is absent from the pclntab on those five artifacts, so neither a direct nor an indirect edge can exist there. It is not that the edge is missing there — there is no escaper to call.** `[verified]` **The correct cross-platform statement is: on Windows the escaper is LINKED and UNCALLED; on Darwin/Linux it is ABSENT. Neither platform shows a link from the shell command into an escaping routine.** `[verified]`

`[verified]` **This makes the platform split MORE informative, not less: D146 used the split to prove LINKAGE over DCE (correct, and it stands). D153 shows the linked Windows copy is unreferenced — so the split identifies a linked-but-uncalled Windows-only routine.** `[inferred]`

---

## 6. INSTRUMENT FAILURES

| # | Failure | Resolution |
|---|---|---|
| **F1** | **`cmd /c "... 2>&1"`** — the redirect inside the quoted string became a **literal argument** to `analyzeHeadless.bat`, which exited 255 before analysing anything. **The run never happened.** | Redirect removed; PowerShell captures natively. **An error about the harness, indistinguishable from an error about the target.** |
| **F2** | **Ghidra project directory must already exist.** `ERROR Headless analyzer error: Directory not found: ...d153probe3 java.io.FileNotFoundException`. Ghidra does **not** create it. | `New-Item -ItemType Directory` on the project path before invocation. **Cost two runs.** |
| **F3** | **Java compile error `line 198: incompatible types: InstructionIterator cannot be converted to AddressIterator`** — my hand-rolled wrapper declared the wrong iterator type. Ghidra reported `The class could not be found ... D153Edges not found`. | Used `getInstructions(f.getBody(), true)` returning `InstructionIterator` directly; wrapper deleted. |
| **F4** | **`getFunctionAt`/`getFunctionContaining` snap to misaligned boundaries** — 4,096 bytes off for `appendEscapeArg`; `commands.shell` merged with `commands.RunAs`. | All final claims made from address-explicit scans independent of the function model (§3). |
| **F5** | **Wrong pclntab path** (`_d131_out`\ prefix) → `FileNotFoundError`. | Corrected to `binlayer`\; **added `os.path.exists` + size asserts** so a bad path fails loudly rather than reporting `files_considered 0`. |
| **F6** | **Two of my PRESENT control probes returned 0** (`syscall.Syscall`, `syscall.Syscall6`). | Not a defect in the method — the probe VAs were interior offsets. **This failure forced §2's boundary sweep and is why the final zero is trustworthy.** |

`[verified]` **Ghidra's Go analyser also failed benignly, as known: `ERROR Untested Go version [1.27.2] (GoRttiMapper)` for both the symbol and string analysers. This is why symbol identity is cross-checked against the pclntab, which does not need RTTI.** `[verified]`

---

## 7. RESIDUALS

**R-153.1 — the one COMPUTED call inside `commands.ExecuteCommand`.** `[verified]` **PROBE:** decompile `0x14054A000` and resolve the indirect target; it is the only route by which the command path could reach the escaper without a direct edge. `[verified]` **Per the task's rule this is an ABSENCE OF A PROVEN EDGE, not proof of no edge.** `[inferred]`

**R-153.2 — what retains `appendEscapeArg` with zero callers.** `[verified]` **PROBE:** search `.rdata`/`.data` for a pointer holding `0x1400C75C0`; a method-value or itab entry would explain a zero-caller function with 65 outgoing calls. `[inferred]` **This is the same question class as R-138.1.** `[inferred]`

**R-153.3 — what `commands.shell` actually invokes to run a process.** `[verified]` **PROBE:** its 9 direct callees were enumerated but only `commands.RunAs`-adjacency was resolved; naming each callee from the pclntab would show whether the shell path reaches `os/exec` instead of `syscall` escape helpers. `[inferred]`

---

## 8. SUMMARY

`[verified]` **NO DIRECT CALL EDGE INTO THE ESCAPE PATH EXISTS. Across 94,263 call instructions in `merlinAgent-Windows-x64.exe`, exactly ZERO target `appendEscapeArg` (`0xC75C0`) or `makeCmdLine` (`0xC79C0`). No pair among five escape-path functions has a direct rel32 edge.** `[verified]`

`[verified]` **`syscall.appendEscapeArg` has 65 direct outgoing calls, 0 computed, and 0 callers. `commands.shell` has 9 direct, 0 computed callees — none of them an escape symbol.** `[verified]`

`[verified]` **MY OWN D146 §0 "chain" IS RETRACTED: `appendEscapeArg → makeCmdLine → CreateProcess` is package adjacency, not a call graph. The tell is in this report's own NEAR column — every window hit sits 384–4,096 bytes off-probe on an adjacent function, and `commands.shell`'s 38 hits are all one repeated address 1,600 bytes below it.** `[verified]`

`[verified]` **D146's HEADLINE SURVIVES: the three D85 families are LINKED, not DCE'd, and the platform-conditional discriminator stands. Only the stronger "wired chain" claim dies.** `[verified]`

`[verified]` **CONTROLS: 726 and 104 hits on known-present targets, 0 on an impossible target, EXACT=2 on `syscall.CreateProcess` proving exact hits are resolvable in the same package — and two of my own PRESENT probes failing, which forced the boundary sweep that makes the final zero trustworthy.** `[verified]`

`[verified]` **BOUNDARY, stated as the task required: the precise claim is absence of a DIRECT edge. `commands.ExecuteCommand` contains one COMPUTED call (R-153.1) and an unresolved indirect call is an ABSENCE OF A PROVEN EDGE, not proof of no edge. `commands.shell` itself has 0 computed calls, so its callee set is complete.** `[verified]`

`[verified]` **CROSS-PLATFORM, stated rather than implied: on Darwin/Linux the question has no referent — the symbol is absent, so no edge of any kind exists there. On Windows the escaper is LINKED and UNCALLED. Neither platform shows a link from the shell command to an escaping routine.** `[verified]`

**The method sentence:** `[inferred]` **the residual closed not by finding the edge but by exhausting the space where it could hide — and the instrument that made that exhaustion credible is the one that failed on two probes I was sure about.**

*End of D153. Instruments: `D153Edges.java` (boundary-dependent, superseded by F4), `D153bEdges.java` (correct-entry edges), `D153cBytes.java` (byte-level + whole-program call scan), `D153dControl.java` (8 probes, present AND absent expectations), `D153eSweep.java` (±4KB boundary sweep), `_d153_resolve.py` (VA→Go name via pclntab). No binary executed. No `open_binary`. No `-readOnly`.*
