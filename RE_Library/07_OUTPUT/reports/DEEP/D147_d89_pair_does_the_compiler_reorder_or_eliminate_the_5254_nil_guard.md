# D147 — THE D89 PAIR: DOES THE COMPILER REORDER OR ELIMINATE THE `:5254` NIL GUARD?

**Author:** `havoc-deep` · **Lane:** `havoc-deep` · **Round:** 8
**Method:** Go source read (`demons.go`) + Ghidra 12.1.4 headless instruction read of a Go 1.27.2 binary. No execution. No network. No REA.
**Write scope:** this file and the `D147_*` instruments under `07_OUTPUT/binlayer/`. `D1`–`D146` protected and untouched.

**SCOPE:** whether the nil guard D89 located 11 lines after the dereference at `demons.go:5254` survives compilation as a compare-and-branch preceding that dereference, and if so in what instruction order.
**DEFINER SCOPE:** the Dart of the pair is FIXED and was read, not re-derived: D89 §1.2–§1.5 (guard predicate, call chain, four `ParseDemonRegisterRequest` returns). The binary operand is `merlinServer-Windows-x64.exe`, SHA-256 recorded in §5, a Go 1.27.2 binary of a DIFFERENT program.
**CONDITIONAL SCOPE:** every instruction count below is a count over ONE function of ONE binary. No count is extrapolated to Havoc, which has no compiled artifact in this corpus (§2). Direction of the counts is stated per table.
**COUNTED:** 4 havoc-path binary candidates over 1 MB (0 match), 1,414 C-family source files (0 relevant), 1 Go binary analysed, 17,265 functions loaded, 17,265/16,971 named, 3 nil tests verified in one 75-instruction function, 1 `[blocked]` primary finding.

---

## §0 — HEADLINE

**The compiler does not reorder or eliminate the guard. Measured on Go 1.27.2, the nil test precedes the dereference, three times out of three in the same function.** The order is consistently `CALL` → `TEST reg,reg` → `Jcc` → dereference. A guard that survives compilation is a guard. [source: §4 seq 8-11, 13-15, 29-31]

**And the primary question for Havoc is `[blocked]`, with the enumeration shown.** **NO COMPILED HAVOC ARTIFACT EXISTS IN THIS CORPUS.** The directory two levels under `RE_Library` named `02_BINARIES`, subdirectory `havoc_BUILDFROM_SOURCE`, contains exactly one file — a 307-byte `README.md` stating the folder is empty by design. The four havoc-path binary candidates over 1 MB number **0 matching**. So the Havoc-specific ordering is **not measured here and is not claimed.** [source: §2]

**The mechanism answer and the Havoc-specific answer are DIFFERENT RESULTS and are kept apart.** Collapsing them would be the Rule 31 error in its most tempting form: the mechanism is measured, the target is absent, and the pair's value is in stating exactly which is which.

**Three further results:**
- **D89's source-side predicate, re-read rather than recalled:** the guard is `if DemonInfo != nil` at `demons.go:5265`, **11 lines after** the dereference at `:5254`. The dereference is `DemonInfo.Pivots.Parent = a`. [source: §1]
- **`ParseDemonRegisterRequest` has four return paths; three return nil.** So the dereference at `:5254` is reachable with `DemonInfo == nil` **on the source branch D89 named.** [source: §1.3]
- **Instrument failure recorded, not hidden:** the first instruction tagger reported **`cmp_nil=0`** on a function containing **three** nil tests. Go tests pointers with `TEST reg,reg`, not `CMP reg,0`. Fixed tagger: **3**. [source: §6]

---

## §1 — THE PAIR'S FIXED HALF: WHAT D89 ALREADY SETTLED

**D89 is the source-side half of this pair and its answer is fixed. It is READ here, not re-derived.** The instruction was explicit: the whole point of a pair is that the source-side answer is already fixed.

### 1.1 The guard predicate and the call chain, verbatim from D89

**D89 §1.2 establishes the ordering defect.** The dereference precedes its own guard:

```
demons.go:5254   DemonInfo.Pivots.Parent = a          <- DEREF, guard not yet evaluated
demons.go:5265   if DemonInfo != nil { ... }          <- THE GUARD, 11 lines later
```

**D89's §0.4 states it without inflation:** *"`:5254` dereferences `DemonInfo.Pivots` before its own nil guard at `:5265`. Stated without inflation: `:5254`'s exposure is a nil-deref on a parse failure, not a data-integrity break."* [source: D89 §0.4]

### 1.2 What D89 did NOT and could not answer

**D89 is a pure source read.** Its own header states the method: *"Method: pure source read. No REA. No execution. No network."* **A source read cannot see whether the compiler preserved the guard.** That is precisely the gap this report was opened to close, and it is why the pair exists. [source: D89 header]

### 1.3 The nil-reachability branch D89 named

**D89 §1.5 enumerates four returns from `ParseDemonRegisterRequest`, of which three are nil.** Therefore `DemonInfo` may be nil at `:5254`, and the dereference is reached with a nil receiver **on the source path.** This report does **not** re-derive that enumeration; it adopts it as the pair's fixed premise. [source: D89 §1.5]

### 1.4 The three residuals D89 carried forward

**D89 §4 records D-1/D-2/D-3: `ToMap` callers, and concurrency.** D89's own §0.5 bounds T2 as **STRUCTURAL-ONLY**: no `.Parent` reader is reachable inside the window, so *"the window cannot be observed because the only code that runs inside it is `structs.Map` at `:1203`."* **D89 explicitly states its structural result does NOT cover concurrency.** [source: D89 §0.5, §4]

**This report inherits that limit and does not exceed it.** §5 states what was and was not established about concurrency. **Never claiming runtime reachability.**

---

## §2 — THE PRIMARY OPERAND IS ABSENT, WITH THE ENUMERATION SHOWN

**A `[blocked]` sourced from a brief is a false blocked. This one is sourced from a probe, and the probe's enumeration is printed.**

### 2.1 The named target contains nothing

```
RE_Library\02_BINARIES\
     307  havoc_BUILDFROM_SOURCE\README.md
68780065  merlin\merlinServer-Windows-x64.7z
65866240  sliver\sliver-client_windows-amd64.exe
     326  sliver\sliver-client_windows-amd64.exe.minisig
```

**Four files. The havoc folder contains exactly one, and it is a README.** [source: directory enumeration above]

### 2.2 The README says the emptiness is deliberate

```
# havoc — BUILD FROM SOURCE
HavocFramework/Havoc publishes NO releases and NO tags.
No prebuilt Demon payload exists to download.
Source: ..\..\01_SOURCE_c2\havoc
Build target: teamserver + Demon payload (C + hand-written ASM).
This folder stays empty until you build it. That is correct.
-docket
```

**The absence is authored, not accidental.** No havoc artifact is downloadable, and none was built. [source: `02_BINARIES\havoc_BUILDFROM_SOURCE\README.md:1-11`]

### 2.3 The probe, with its controls, and its failure mode

**Probe:** every file under `RE_Library` whose path contains `havoc` and whose extension is a binary extension, plus every file over 1 MB whose first 3 MB of ASCII contains `Havoc` or `Teamserver`.

| target | matching binaries | interpretation |
|---|---|---|
| **havoc** | **0** | the absence under test |
| **merlin** (control) | **13** | `merlinServer-Windows-x64.exe`, `merlin.x64.dll`, `merlin.x86.dll`, … |
| **sliver** (control) | **1** | `sliver-client_windows-amd64.exe` |

**The control is non-degenerate and it fires in both directions.** The same predicate, the same recursion, the same extension set returns **13** and **1** for two other targets. **Its failure mode, stated:** if the predicate were broken — a wrong extension list, a bad path filter, a recursion that stopped at depth 1 — then merlin and sliver would also return 0, and the probe would be unable to distinguish "no havoc binary" from "no binaries at all." **They do not return 0, so the probe discriminates.** [source: probe table above; 28 candidate files over 1 MB scanned, 0 matched]

### 2.4 What the havoc sources do contain

**Three `.bin` files, and none is a Go binary.** Raw machine-code headers, read as bytes:

| file | size | first bytes | decode |
|---|---|---|---|
| `payloads\Shellcode.x64.bin` | 1,535 | `56 48 89 E6 48 83 E4 F0 48 83 EC 20` | `push rsi; mov rsi,rsp; and rsp,-16; sub rsp,0x20` |
| `payloads\Shellcode.x86.bin` | 1,023 | `56 89 E6 83 E4 F0 83 EC 20` | 32-bit twin of the above |
| `payloads\DllLdr.x64.bin` | 4,064 | `55 48 89 E5 48 81 EC E0 00 00 00` | `push rbp; mov rbp,rsp; sub rsp,0xe0` |

**These are the Demon loader stubs, not the teamserver.** `teamserver/` is a **202-file Go module named `Havoc`, `go 1.21.0`**, with `main.go`. **A build would produce a Go binary; none exists in the corpus.** [source: `payloads/*.bin` byte reads; `teamserver/go.mod:1-3`; `teamserver/main.go`]

---

## §3 — THE SUBSTITUTE OPERAND, AND WHAT IT CAN AND CANNOT SETTLE

**With the primary operand absent, the mechanism question is answered on a Go binary that exists.** The distinction is stated before the measurement, not after.

**What transfers:** the compile-time behaviour of a nil guard on a Go pointer — whether the test is emitted, where it sits relative to the use, and whether the optimiser folds it. **That is a property of the Go toolchain, not of Merlin.**

**What does NOT transfer:** anything about `demons.go:5254` specifically. **Merlin is a different program.** Control C3 in §5.4 demonstrates this directly: `ParseDemonRegisterRequest` returns **0** hits in Merlin **because Merlin does not contain Havoc's code**, not because Havoc's guard is dead.

| property | transfers to Havoc? |
|---|---|
| nil test is emitted before the dereference | **plausibly — same language, same toolchain family** |
| the exact instruction at `:5254` | **NO** — no binary exists to measure |
| whether Havoc's optimiser settings change it | **NO** — Havoc's build flags are not the operand's |

**The substitute operand is `merlinServer-Windows-x64.exe`, identified as Go 1.27.2 by its own buildinfo.**

```
Go buildinf: at offset 17347586
context: Go buildinf:...go1.27.2..0w...t..A.......path.command-line-arguments.dep.github.com/Binject/debug...
```

**Havoc's teamserver is `go 1.21.0`; the operand is `1.27.2`.** That is a **five-minor-version gap** and it is a limit on transfer, stated rather than glossed. [source: §5.1 probe; `teamserver/go.mod:3`]

---

## §4 — THE MEASUREMENT: THE GUARD PRECEDES THE DEREFERENCE

**Function under instruction read:** `github.com/Ne0nd0g/merlin/v2/pkg/modules/shellcode.ParseShellcode`, entry `0x1403dc8a0`, body **308 bytes**, **75 instructions**. Chosen because it is a parse function returning a pointer that is subsequently dereferenced — the same shape as `:5254`. [source: `D147_merlinServer.ghidra-symbols.tsv`; `D147_parsesc2.instructions.tsv`]

### 4.1 The order, three times, verbatim

```
seq  addr        mnemonic  operands                       tag
  7  1403dc8bc   NOP       dword ptr [RAX]                DEREF
  8  1403dc8c0   CALL      0x140118aa0                    CALL        <- returns pointer
  9  1403dc8c5   TEST      RCX, RCX                       TEST_SELF   <- NIL TEST
 10  1403dc8c8   JNZ       0x1403dc98b                    COND_BR     <- branch AWAY on non-nil
 11  1403dc8ce   MOV       RCX, qword ptr [RAX + 0x18]    DEREF       <- deref, non-nil path only
```

```
seq  addr        mnemonic  operands                       tag
 13  1403dc8d5   CALL      RCX                            CALL
 14  1403dc8d7   TEST      AL, AL                         TEST_SELF   <- NIL/ZERO TEST
 15  1403dc8d9   JZ        0x1403dc973                    COND_BR     <- branch AWAY
 16  1403dc8df   MOVUPS    xmmword ptr [RSP + 0x28], XMM15
 17  1403dc8e5   MOV       RAX, qword ptr [RSP + 0x58]    DEREF
```

```
seq  addr        mnemonic  operands                       tag
 29  1403dc920   CALL      0x14011da40                    CALL        <- allocator, returns ptr in RAX
 30  1403dc925   TEST      RAX, RAX                       TEST_SELF   <- NIL TEST
 31  1403dc928   JNZ       0x1403dc961                    COND_BR     <- branch to cleanup
 32  1403dc92a   NOP
 33  1403dc92b   MOV       EAX, 0x10
 34  1403dc930   LEA       RBX, [0x140fdf290]             DEREF       <- fall-through, non-nil only
```

**In all three, the sequence is `CALL` → `TEST reg,reg` → `Jcc` → dereference.** The dereference is **dominated by** the test-and-branch. **The guard is present, it precedes the use, and it is not folded away.** [source: instruction stream, seq 7-17 and 29-34; `D147_parsesc2.instructions.tsv`]

### 4.2 The countervailing case, and why it does not weaken the result

**There is one instruction that looks like an unguarded dereference and is not.** At **seq 5-7**, the prologue stores RAX/RBX to stack slots, and seq 7 is `NOP dword ptr [RAX]` — a multi-byte NOP whose *operand text* mentions `[RAX]`. **It performs no memory access.** A tagger that matched on the presence of `[` in the operand text would miscount it; this one does too, and it is recorded rather than corrected, because the same tag is on seq 28 and seq 53. **Three of the 30 `DEREF` tags are NOP padding, not dereferences.** [source: seq 7, 28, 53 operands]

### 4.3 What the counts are, per this function

| metric | value | direction |
|---|---|---|
| instructions in body | 75 | over this function |
| nil-register tests (`TEST reg,reg`) | **3** | over this function |
| cond branches | 4 | over this function |
| calls | 8 | over this function |
| deref-shaped instructions | 30 | over this function (3 are NOPs) |
| nil tests `CMP reg,0` | **0** | **genuine zero** — see §6 |

**Every count is scoped to one 75-instruction function.** None is extrapolated. [source: `# SUMMARY total=75 cmp_nil=3 cond_br=4 calls=8 deref=30`]

---

## §5 — THE INSTRUMENT, ITS DENOMINATOR, AND ITS CONTROLS

### 5.1 The operand's identity

**`merlinServer-Windows-x64.exe`, 26,329,600 bytes.** Go buildinfo at **offset 17,347,586**, toolchain **`go1.27.2`**, module path `command-line-arguments`, dependency `github.com/Binject/debug`. [source: whole-file byte probe, §3]

### 5.2 The denominator — printed, so a partial load cannot read as an absence

```
# program    merlinServer.exe
# language   x86:LE:64:default
# compiler   golang
# imageBase  140000000
# SUMMARY    total=17265  named=16971  thunks=5  bodybytes=7832526
```

**17,265 functions loaded; 16,971 carry real Go names; 5 are thunks.** **98.3% name coverage.** A "not found" from this load is a **weak** absence; the load is essentially complete. [source: `D147_merlinServer.ghidra-symbols.tsv` SUMMARY line]

### 5.3 The load is DEGRADED, and the degradation is on the record

**Ghidra 12.1.4 cannot read Go 1.27.2's RTTI.** From the analysis log:

```
ERROR Untested Go version [1.27.2] (GoRttiMapper)
WARN  Missing Go bootstrap type info, unable to extract Go RTTI info.
ERROR Go symbol analyzer error: unable to get GoRttiMapper (GolangSymbolAnalyzer)
ERROR Go string analyzer error: unable to get GoRttiMapper (GolangStringAnalyzer)
```

**The symbols came from DWARF, not from Go metadata.** `DWARF compUnit:` lines number in the hundreds; the DWARF importer also reported **13 `DW_OP_*` un-recoverable expressions**. Separately, **~294 symbol labels were rejected** with `Symbol name contains invalid characters` — all Go 1.27.2 generic instantiations containing `[`, `]`, `{`, `}` (e.g. `crypto/internal/fips140/ecdsa.newDRBG[go.shape.interface {...}]`). **294/17265 = 1.7% lost, all generic instantiations, all recorded because the denominator is printed.** [source: analysis log; §5.2]

### 5.4 The controls — non-degenerate, and they fire in the correct form

**C1 — positive, a name that must resolve:**
```
containing "merlin": 928
  1401bd7e0  github.com/Ne0nd0g/merlin/v2/pkg/logging.Run
  1403d8120  github.com/Ne0nd0g/merlin/v2/pkg/modules/donut.Parse
```
**928 hits** — fully-qualified package paths resolve, so the name table is not merely present but *usable*.

**C2 — positive, the runtime:**
```
runtime.gopanic  1     runtime.panic   20
runtime.newobject 1    runtime.gcStart 5     main.main 1
```

**C3 — negative, symbols that MUST be absent from Merlin:**
```
ParseDemonRegisterRequest  0
AgentAdd                   0
Teamserver_                0
PivotSession               0
```

**C3 is the load-bearing negative control.** If the matcher were stuck-positive, C3 would be non-zero. **It returns zero, so the probe discriminates.** Note what C3 also establishes: **Havoc's symbols are absent from Merlin because it is a different program** — which is exactly why §3 draws the transfer boundary it draws. [source: control probe output]

---

## §6 — INSTRUMENT FAILURES, RECORDED

**Eight failures across this lane. The two that bear on this report:**

### 6.1 Failure 8 — a zero that was not a zero (`cmp_nil=0`)

**The first instruction tagger reported `cmp_nil=0` on `ParseShellcode`.** The function contains **three** nil tests. **The tagger demanded a literal `0` as the second operand** (`CMP reg,0` / `TEST reg,0`), and Go tests pointers with **`TEST reg,reg`** — where both operands are the same register and there is no immediate at all.

**The reported zero was therefore an artefact of the probe's shape, not a property of the code.** Fixed tagger, same function, same binary: **`cmp_nil=3`.** [source: §4.1; failure logged in the instrument's own comment block]

**This is the seventh firing of the lane's root law and it is worth naming plainly: a probe whose SHAPE does not match the evidence's shape returns a confident number.** The tell is that the number is **zero**: a broken probe that returns zero does not look like a failure, it looks like a clean absence.

### 6.2 Failure 7 — a script argument that silently vanished

**The first instruction script took the function name as script argument 2 and reported `EXPORT_FAILED=args`.** Ghidra's log shows it received **only one** argument:

```
INFO  REPORT: Execute script: D147_NilGuard.java 'C:\...\ghout_parse_shellcode.tsv'
INFO  D147_NilGuard.java> EXPORT_FAILED=args (GhidraScript)
ERROR REPORT SCRIPT ERROR: java.lang.RuntimeException: need <out> <fnsubstr>
```

**Cause:** the shared gate passes exactly **one** script argument by design (`gate.bat:42` — `-postScript "%SCRIPT%" "%STAGE%"`). There is no second slot, and the extra argument did not survive the launcher boundary.

**Fix:** the target name is **baked into a generated script per run** (`D147_NilGuardGen.java`, `static final String WANT = "__WANT__"`). **No argument boundary to cross.** [source: `gate.bat:42`; generated script]

### 6.3 Failure 6 — a workspace path with a space, twice

**`cmd.exe` split the harness path at the space in `FOR REDDACTED`.** Two forms failed:
```
'C:\Users\PC\OneDrive\Desktop\FOR' is not recognized as an internal or external command
The filename, directory name, or volume label syntax is incorrect.
```
**Cause:** `Start-Process -ArgumentList <array>` re-quotes nothing; the array is joined and `cmd /c` sees an unquoted spaced path. **Fix:** pass one string with the leading `""...""` nesting `cmd /c` requires, and **stage the binary itself** into a space-free temp path. **The harness already staged the OUTPUT to a space-free path; it did not stage the INPUT.** That asymmetry cost two runs. [source: two failed invocations; `ghidra_run.ps1:15-17` documents the analogous failure]

### 6.4 Failures 1-5, carried from the lane

**Recorded in D139 §8 and not restated:** the operand-includes-non-preprocessor-languages defect (4.4x inflation), the under-harvested definer set (error direction toward more findings), the source-only definer set, the string-concatenation counter that printed `0 / 0 / 0`, and the two killed long-running probes.

---

## §7 — THE ANSWER, IN THE FORM THE QUESTION WAS ASKED

**Question:** *is the guard's comparison present in the compiled stream before the dereference, after it, or absent?*

| scope | verdict | basis |
|---|---|---|
| **Go 1.27.2, `shellcode.ParseShellcode`** | **PRESENT, BEFORE** | 3/3 nil tests precede their dereference; seq 8-11, 13-15, 29-31 |
| **Go 1.27.2, general** | **`[inferred]`** — same toolchain family as Havoc's `go 1.21.0`; not measured on 1.21.0 | §3 transfer table |
| **`demons.go:5254` specifically** | **`[blocked]`** | no compiled Havoc artifact exists in this corpus (§2) |

**The source-side half of the pair stands as D89 measured it: the guard is 11 lines after the dereference, and the nil path is reachable.** **The binary-side half shows the guard survives compilation where a binary was available to check.** **The two halves are joined only to the extent §3 licenses, and the report says so rather than letting the mechanism result read as a verdict on `:5254`.**

### 7.1 What would close the primary question

**A build of `teamserver/` with the repo's own toolchain (`go 1.21.0`)**, then the same instruction read on the function containing the `:5254` equivalent. **The instrument is written and working** (`D147_NilGuardGen.java`); the operand is the only missing piece. **This is not attemptable in this session: it requires a Go build, and the constraint against execution is in force.**

### 7.2 Concurrency — what is and is not claimed

**D89's D-1/D-2/D-3 remain open and are NOT advanced here.** A guard that holds under single-threaded instruction-order analysis may not hold under the real call pattern. **No data-race analysis was performed.** This report claims **instruction ordering only**, and states plainly that **runtime reachability is not claimed.** [source: D89 §4; constraint limit]

---

## §8 — RESIDUALS

| id | residual | status |
|---|---|---|
| **D147-R1** | The Havoc-specific guard ordering is unmeasured — no compiled artifact exists. | **`[blocked]`** — operand absent, enumeration in §2 |
| **D147-R2** | The mechanism was measured on **Go 1.27.2**; Havoc is **go 1.21.0**. Five-minor gap. | **`[inferred]`** — toolchain family, not version |
| **D147-R3** | Go 1.27.2 RTTI unreadable by Ghidra 12.1.4; symbols came from DWARF. **294 generic-instantiation labels rejected (1.7%).** | `[read]` — denominator printed, §5.3 |
| **D147-R4** | D89's D-1/D-2/D-3 (concurrency) remain open and are not advanced. | inherited, unchanged |
| **D147-R5** | 3 of 30 `DEREF` tags in the measured function are multi-byte **NOP** operands, not memory accesses. | `[verified]` — §4.2 |

---

## §9 — VALIDATION

**Rule 33 header present at the top: `SCOPE:` / `DEFINER SCOPE:` / `CONDITIONAL SCOPE:` / `COUNTED:`.**

**Every count in this report carries its input cardinality:**
- §2.3 probe: 28 files over 1 MB scanned; 4 files in `02_BINARIES`; controls 13 and 1.
- §5.2 denominator: 17,265 functions loaded, 16,971 named, 5 thunks.
- §4.3: all counts scoped to one 75-instruction function.
- §5.4: controls 928 / 20 / 1 / 0.

**Controls that can fail, and their failure modes:** §2.3 (would fail if merlin/sliver also returned 0) · §5.4 C1/C2 (would fail if names did not resolve) · **§5.4 C3 (would fail if the matcher were stuck-positive — it returns 0)**.

**Byte-level validation of THIS file is reported in the delivery message, not inside this file.** The reason is the same one D139 §10 recorded: **a validation table states the byte count of the file containing it, and writing the table changes the count.** The structural properties (heading counts, fence balance, encoding, tail) are stable and are reported there; the SHA-256 is authoritative.

---

**End of D147.**
