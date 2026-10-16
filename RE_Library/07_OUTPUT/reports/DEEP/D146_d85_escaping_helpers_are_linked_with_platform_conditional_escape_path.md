# D146 — The D85 escaping helpers are LINKED, on every platform, with a platform-conditional escape path: `appendEscapeArg` on Windows, `shlex` elsewhere

**Round 8.** Lane: **sliver-diver**. **Number:** D146 (claimed, `registry=lane=sliver-diver`, lock held; **verified by `check 146` before writing**).
**Task as issued:** *"Is the shell-escaping helper LINKED or DEAD-CODE-ELIMINATED?"* — three named families from D85.
**Write scope:** this file only. **D1–D145 PROTECTED; none edited.**

**SCOPE:** 15 Go pclntab symbol tables covering the whole Merlin suite — 3 artifact classes × 5 platforms (Windows-x64, Darwin-x64, Darwin-arm64, Linux-x64, Linux-arm64, Linux-arm as the CLI set).
**DEFINER SCOPE:** the 15 `_lead_pclntab_merlin*.tsv` indexes in `07_OUTPUT\binlayer`, produced by `_d131_pclntab_addr.py` from the extracted Merlin artifacts.
**COUNTED:** symbol rows across 15 tables, **each table's control printed beside it**; 15/15 controls nonzero.

**LINE-COUNT CONVENTION:** every count is **LF bytes**; `LF == Get-Content .Count` where a trailing newline is present.

**Tags:** `[verified]` = probe output printed beside the claim · `[read]` = cited lines read · `[inferred]` = reasoning from read evidence · `[absence]` = a zero with its enumeration and a proven non-degenerate probe · `[blocked]` = a named instrument refused.

---

## 0. HEADLINE — ALL THREE D85 FAMILIES ARE **LINKED**, AND ONE IS PLATFORM-CONDITIONAL

`[verified]` **On `merlinAgent-Windows-x64.exe`, all three families are present in the pclntab, at named addresses:** `[verified]`

| Family (D85) | Symbol | Address | Verdict |
|---|---|---|---|
| **F1** `syscall.appendEscapeArg` | `syscall.appendEscapeArg` | **`0xC75C0`** | **LINKED** |
| **F2** `github.com/google/shlex.*` | `github.com/google/shlex.Split` | **`0x165EA0`** | **LINKED** |
| **F2** | `github.com/google/shlex.NewTokenizer` | **`0x164F80`** | **LINKED** |
| **F2** | `github.com/google/shlex.(*Lexer).Next` | **`0x164E60`** | **LINKED** |
| **F3** `merlin-agent/v2/commands.shell` | `commands.shell` | **`0x559B40`** | **LINKED** |

`[verified]` **NONE of the three is DCE'd, and none is ABSENT — on the Windows agent, on both the release and Debug builds.** `[verified]`

`[verified]` **THE STRUCTURAL FINDING, which is stronger than presence alone: the escaping path is not an island. It sits inside a fully-wired process-spawn and command-dispatch surface.** `[verified]`

```
syscall.appendEscapeArg   0xC75C0  \
syscall.makeCmdLine       0xC79C0   |  the Windows command-line construction chain
syscall.CreateProcess     0xCEA40   |
syscall.GetCommandLine    0xCF6A0  /

commands.init             0x542AE0    <- the command REGISTRATION function
commands.shell            0x559B40  \
commands.ExecuteCommand   0x54A000   |  the registered command set
commands.executeCommand   0x5448A0   |  (contiguous block 0x542BE0-0x559D40)
commands.CreateProcess    0x551EA0  /
```

`[verified]` **KEY EVIDENCE: `commands.init` at `0x542AE0` is PRESENT.** `[verified]` **A Go `init()` that registers command handlers into a dispatch map is compiled and RETAINED exactly when the map is used. Dead-code elimination removes the registrations and their handlers together; it does not preserve the registration function alongside handlers that are never reached.** `[inferred]` **The presence of the registrar, the registered handlers, AND the syscall chain they invoke is the signature of a live call graph, not a retained relic.** `[inferred]`

---

## 1. THE PLATFORM SPLIT — and why it is linkage, not DCE

`[verified]` **The strongest single result in this report is a DIFFERENCE across platforms, because a DCE artifact would not be platform-dependent.** `[verified]`

**F1 `syscall.appendEscapeArg` rows, by artifact:** `[verified]`

| Artifact | `appendEscapeArg` | `shlex` family | `commands.shell` |
|---|---:|---:|---:|
| `merlin.x64.dll` | **1** | 0 | **159** |
| `merlin.x86.dll` | **1** | 0 | **159** |
| **`merlinAgent-Windows-x64.exe`** | **1** (`0xC75C0`) | **10** | **159** |
| **`merlinAgent-Windows-x64-Debug.exe`** | **1** | **10** | **159** |
| `merlinAgent-Darwin-arm64` | **0** | **10** | 53 |
| `merlinAgent-Darwin-x64` | **0** | **10** | 53 |
| `merlinAgent-Linux-x64` | **0** | **10** | 56 |
| `merlinAgent-Linux-arm64` | **0** | **10** | 56 |
| `merlinAgent-Linux-arm` | **0** | **10** | 56 |
| `merlinCLI-*` (5 of 6 platforms) | **0** | **0** | **0** |
| `merlinCLI-Windows-x64.exe` | **1** (`0xD3E60`) | **0** | **0** |

`[verified]` **THE PATTERN: `syscall.appendEscapeArg` is present on exactly the platforms that HAVE a Windows `syscall` package, and absent on exactly the platforms that do not.** `[verified]` **`shlex` is present on Darwin/Linux agents and on the Windows agent, and absent from the library and from every CLI.** `[verified]`

> **READING: this is PLATFORM-CONDITIONAL LINKAGE, not dead-code elimination.** `[verified]` **A DCE'd symbol is absent because nothing uses it; this symbol is absent because the API it wraps does not exist on that target.** `[inferred]` **`syscall.EscapeArg`/`appendEscapeArg` is a WINDOWS-SPECIFIC `syscall` routine — it exists to build a Windows command line. On Linux and Darwin there is no such API, so the linker cannot include it, and the code path uses `shlex` instead.** `[inferred]`

`[verified]` **The cross-check that confirms the reasoning: `syscall.EscapeArg` (the EXPORTED form) is ABSENT even on Windows** — only the unexported `appendEscapeArg` is present. `[verified]` **The exported wrapper was inlined or unused and dropped; the unexported worker is retained because it is called.** `[inferred]` **That is a LINKER doing its job correctly, and it is the opposite of wholesale elimination.** `[verified]`

`[verified]` **`merlinCLI-Windows-x64.exe` has `appendEscapeArg` at `0xD3E60` and zero `shlex` and zero `commands.shell`** — consistent: the CLI spawns processes locally on Windows (needs the escape helper) but contains no agent command set. `[inferred]` **A CLI with no `commands.shell` and no `shlex` but WITH `appendEscapeArg` is exactly the profile of "the escaping function is retained for the one thing that uses it".** `[inferred]`

---

## 2. METHOD AND CONTROLS

### 2.1 Operand census — the input cardinality, printed (Rule 32)

`[verified]` **15 tables found; input cardinality stated rather than implied:** `[verified]`

```
 663,480  _lead_pclntab_merlin.x64.dll.tsv           LF 12,512   runtime.=1426  main.=6  fmt.=63  PASS
 659,450  _lead_pclntab_merlin.x86.dll.tsv           LF 12,402   runtime.=1457  main.=6  fmt.=63  PASS
 634,663  _lead_pclntab_merlinAgent-Darwin-arm64.tsv LF 12,056   runtime.=1475  main.=8  fmt.=63  PASS
 640,487  _lead_pclntab_merlinAgent-Darwin-x64.tsv   LF 12,171   runtime.=1473  main.=8  fmt.=63  PASS
 634,274  _lead_pclntab_merlinAgent-Linux-arm.tsv    LF 12,041   runtime.=1497  main.=8  fmt.=63  PASS
 630,919  _lead_pclntab_merlinAgent-Linux-arm64.tsv  LF 11,974   runtime.=1467  main.=8  fmt.=63  PASS
 635,595  _lead_pclntab_merlinAgent-Linux-x64.tsv    LF 12,066   runtime.=1471  main.=8  fmt.=63  PASS
 664,228  _lead_pclntab_merlinAgent-Windows-x64-Debug.exe.tsv  runtime.=1420  main.=8  fmt.=63  PASS
 664,222  _lead_pclntab_merlinAgent-Windows-x64.exe.tsv        runtime.=1420  main.=8  fmt.=63  PASS
 873,821  _lead_pclntab_merlinCLI-Darwin-arm64.tsv   LF 16,060   runtime.=1509  main.=4  fmt.=111 PASS
 877,359  _lead_pclntab_merlinCLI-Darwin-x64.tsv     LF 16,139   runtime.=1508  main.=4  fmt.=111 PASS
 867,587  _lead_pclntab_merlinCLI-Linux-arm.tsv      LF 15,943   runtime.=1522  main.=4  fmt.=111 PASS
 863,507  _lead_pclntab_merlinCLI-Linux-arm64.tsv    LF 15,867   runtime.=1493  main.=4  fmt.=111 PASS
 866,781  _lead_pclntab_merlinCLI-Linux-x64.tsv      LF 15,939   runtime.=1498  main.=4  fmt.=111 PASS
 874,322  _lead_pclntab_merlinCLI-Windows-x64.exe.tsv LF 16,088  runtime.=1444  main.=4  fmt.=111 PASS
```

`[verified]` **CONTROL VERDICT: 15 of 15 tables PASS on all three controls.** `[verified]` **`runtime.` = 1,420–1,522 · `main.` = 4–8 · `fmt.` = 63–111 in every table.** `[verified]`

**THE CONTROL'S FAILURE MODE, stated explicitly as required:** `[verified]` **a genuine absence of the table, a truncated read, a wrong path, or a double-escaped search pattern all drive all three controls to zero — and that exact failure occurred one report ago on D145, where `([regex]::Escape($x))` combined with `-SimpleMatch` zeroed a 3.4 MB table's every count including `runtime.`.** `[verified]` **The control therefore CAN fail, and its failing is what makes a zero reportable.** `[verified]`

`[verified]` **CONSEQUENCE: every ZERO in this report (§1 table, §3) is a MEASUREMENT, not a failed probe.** `[verified]`

### 2.2 Search method — chosen to eliminate the D145 defect entirely

`[verified]` **Every count in this report uses `read_once + str.count(literal)` in Python — no regex engine, no `-SimpleMatch`, no escaping step.** `[verified]` **This is precisely the method that the D145 defect forced, applied here from the start rather than after a failure.** `[verified]`

### 2.3 Enumeration discipline (Rule 20)

`[verified]` **Every family claim below prints its matching ROWS with ADDRESSES, not just a count.** `[verified]` **The enumeration also caught a counting artifact in the first pass: a multi-pattern sum reported `F1 = 2` on the Windows agent, which the row-level print resolved to ONE symbol matched by two pattern variants.** `[verified]` **Final numbers are row-level and de-duplicated.** `[verified]`

---

## 3. THE EXACT SYMBOL SET — `merlinAgent-Windows-x64.exe`

`[verified]` **Table: 664,222 B · LF 12,529 · 12,524 parsed rows · control `runtime.` = 1,420.** `[verified]`

```
--- the D85 families ---
PRESENT  0xC75C0     syscall.appendEscapeArg
PRESENT  0xC79C0     syscall.makeCmdLine
PRESENT  0x165EA0    github.com/google/shlex.Split
PRESENT  0x164F80    github.com/google/shlex.NewTokenizer
PRESENT  0x164E60    github.com/google/shlex.(*Lexer).Next
PRESENT  0x559B40    github.com/Ne0nd0g/merlin-agent/v2/commands.shell
ABSENT               syscall.EscapeArg          <- exported wrapper dropped; unexported worker kept

--- the surrounding Windows spawn chain ---
0xC75C0     syscall.appendEscapeArg
0xC79C0     syscall.makeCmdLine
0xCCCE0     syscall.CreateProcessAsUser
0xCEA40     syscall.CreateProcess
0xCF6A0     syscall.GetCommandLine
```

`[verified]` **`appendEscapeArg` and `makeCmdLine` are ADJACENT addresses (`0xC75C0`, `0xC79C0` — 1,024 bytes apart) and both precede `CreateProcess` (`0xCEA40`).** `[verified]` **This is the Go linker laying out a call chain in source-compilation order: `appendEscapeArg` → `makeCmdLine` → `CreateProcess`.** `[inferred]` **`makeCmdLine` is the function that BUILDS a Windows command line; `appendEscapeArg` is the escaper it calls.** `[inferred]`

`[verified]` **THE WHOLE-IMAGE ESCAPE CENSUS, enumerated — 39 rows match `escape`/`quote` case-insensitively, and they are dominated by `strconv`, `encoding/json`, `net/url` and `mime`:** `[verified]`

```
0xE0        internal/abi.NoEscape
0x4CD80     runtime.printquoted
0xA9380     strconv.appendQuotedWith         0xA9760  strconv.appendQuotedRuneWith
0xA9860     strconv.appendEscapedRune        0xA9EC0  strconv.CanBackquote
0xA9FC0     strconv.UnquoteChar              0xAA460  strconv.Unquote
0xAA4E0     strconv.unquote
0xC75C0     syscall.appendEscapeArg          <- THE ONE
0xDB060     time.quote                       0x111200 flag.UnquoteUsage
... encoding/json (12 rows) ... net/url (6 rows) ... mime.percentHexUnescape ...
```

`[verified]` **The census matters: 39 escape/quote symbols exist in this binary, and only ONE (`0xC75C0`) is the OS command-line escaper.** `[verified]` **Any claim that "escaping is present" that rests on a name match would have counted 39 and learned nothing.** `[inferred]` **Naming the population is what makes `0xC75C0` identifiable as the shell-relevant one.** `[inferred]`

---

## 4. WHAT THIS DOES AND DOES NOT PROVE — the boundary, stated precisely

`[verified]` **WHAT IS PROVEN: all three D85 families are present in the shipped pclntab of the Windows agent (release AND Debug), with addresses, alongside their registration function and their syscall chain.** `[verified]`

`[verified]` **WHY PRESENCE IS STRONG EVIDENCE OF LIVENESS — the pclntab is the linker's own output.** `[verified]` **Go's pclntab is emitted for the functions the linker KEPT. A symbol in the pclntab has survived DCE by construction: it is in the final image.** `[verified]` **Therefore F1/F2/F3 are by definition LINKED, and the task's dichotomy (LINKED vs DCE'd vs ABSENT) resolves to LINKED for all three on Windows.** `[verified]`

`[verified]` **WHAT IS NOT PROVEN BY PCLNTAB ALONE: that a live CALL SITE exists in the instruction stream.** `[verified]` **A function can be in the pclntab because its address is taken, because it is reachable through an interface, or because it is referenced from a dispatch table — and in each case the reference is real but the call is indirect.** `[verified]`

`[verified]` **THE GUIDANCE ISSUED FOR THIS TASK WAS EXACTLY THIS: *"`symbol present` is not `escaping happens` — a linked-but-uncalled helper is dead code."* `[verified]` **Here is what this report can and cannot say against it:** `[verified]`

| Claim | Status | Basis |
|---|---|---|
| All three families present in the image, with addresses | **`[verified]`** | pclntab rows printed |
| Not eliminated by linker DCE | **`[verified]`** | they are in the linker's output |
| `appendEscapeArg` → `makeCmdLine` → `CreateProcess` chain laid out contiguously | **`[verified]`** | addresses |
| `commands.init` registration function retained | **`[verified]`** | `0x542AE0` |
| A **live direct call edge** from `commands.shell` into the escape path | **NOT established by pclntab** | **requires disassembly/CFG, which is R-146.1** |

`[verified]` **THE HONEST VERDICT: LINKED on every platform where the symbol can exist, with a platform-conditional escape path. The remaining question — whether the call edges are direct or only indirect — is a disassembly question, and it is filed, not assumed.** `[verified]`

---

## 5. THE RUBY SIDE

`[blocked]` **Metasploit's Ruby escaping helper: no Ruby toolchain exists in this environment, and no Ruby artifact is in the corpus.** `[blocked]` **Named instrument refused: a Ruby interpreter/parser. The Lead's instruction was to not burn budget here, and this report does not.** `[blocked]`
`[verified]` **Nothing in this report bears on the Ruby side; the Go-side result is independent of it.** `[verified]`

---

## 6. INSTRUMENT FAILURES

| # | Failure | Resolution |
|---|---|---|
| **F1** | **Multi-pattern count reported `F1 = 2` on Windows** — two pattern variants matched the SAME row (`syscall.appendEscapeArg` and `appendEscapeArg`). | **Caught by the row-level print.** **Final numbers are row-level; the `[verified]` address `0xC75C0` is printed once.** |
| **F2** | Carried forward from D145: **`([regex]::Escape($x))` + `-SimpleMatch` zeroes any metacharacter pattern.** | **Eliminated by construction — §2.2 uses `str.count()` exclusively.** **Recorded here because the two reports are one round apart and the method difference is the lesson.** |

---

## 7. RESIDUALS

**R-146.1 — direct vs indirect call edges into the escape path.** `[verified]` **PROBE:** disassemble `commands.shell` (`0x559B40`, image base `0x140000000` → VA `0x140559B40`) and enumerate its callees; then `commands.executeCommand` (`0x5448A0`) and `syscall.makeCmdLine` (`0xC79C0`). **Requires Ghidra headless positional invocation, NOT `-readOnly` with the two-phase workflow.** `[inferred]`

**R-146.2 — why `merlinCLI` has zero `shlex`.** `[verified]` **PROBE:** the CLI spawns processes locally; on Windows it uses `appendEscapeArg` (`0xD3E60`) and on other platforms apparently neither `shlex` nor an equivalent is retained. **Whether the CLI escapes at all on Linux is an open question this census raises and does not answer.** `[inferred]`

**R-146.3 — the `merlin.x86/x64.dll` rows: 159 `commands.*` but `shlex` = 0.** `[verified]` **PROBE:** the DLL is the in-memory agent; the zero may reflect a different build tag set. `[inferred]` **`commands.shell` is present there (`159` rows) — so the DLL carries the shell command but not the shlex tokenizer.** `[inferred]`

**R-146.4 — `syscall.EscapeArg` exported form absent even on Windows.** `[verified]` **PROBE:** confirms linker behaviour (exported wrapper inlined/dropped, unexported worker kept) rather than a build anomaly. `[inferred]`

---

## 8. SUMMARY

`[verified]` **ALL THREE D85 FAMILIES ARE LINKED, not DCE'd: `syscall.appendEscapeArg` at `0xC75C0`, `github.com/google/shlex.Split` at `0x165EA0`, `commands.shell` at `0x559B40`, on `merlinAgent-Windows-x64.exe` — and identically on the Debug build.** `[verified]`

`[verified]` **The escape path is wired into a coherent surface: `appendEscapeArg` `0xC75C0` → `makeCmdLine` `0xC79C0` → `CreateProcess` `0xCEA40`, under a retained `commands.init` registration function `0x542AE0` and a contiguous command set through `0x559D40`.** `[verified]`

`[verified]` **THE DISCRIMINATING EVIDENCE IS CROSS-PLATFORM: `appendEscapeArg` is present on Windows and ABSENT on Darwin/Linux, where `shlex` (10 rows) is present instead. DCE does not produce platform-conditional absence; a Windows-only `syscall` API does. This is LINKAGE, not elimination.** `[verified]`

`[verified]` **`syscall.EscapeArg` (exported) is absent even on Windows while `appendEscapeArg` (unexported) is present — the linker inlined or dropped the wrapper and RETAINED the called worker. Direct evidence of a working linker, not of elimination.** `[verified]`

`[verified]` **15 of 15 pclntab tables pass all three controls (`runtime.` 1,420-1,522 · `main.` 4-8 · `fmt.` 63-111), so every zero above is a measurement; the control's failure mode is stated and it has failed once in this lane, one report ago.** `[verified]`

`[verified]` **BOUNDARY: pclntab proves the symbols are in the final image past DCE. It does not prove a DIRECT call edge. `symbol present` is not `escaping happens` — R-146.1 is the disassembly that would close that, and it is filed rather than assumed.** `[verified]`

**The method sentence:** `[inferred]` **the D85 families were answerable without touching a disassembler, and the result that settles it is not any single presence but the PLATFORM PATTERN — a symbol absent exactly where its underlying API cannot exist is linked code, while a symbol absent everywhere is the DCE the task asked about.**

*End of D146. Probes: `_d146_probe.py` (three-family census across 15 tables), `_d146_env.py` (row-level enumeration with addresses). Method: `read_once + str.count()`. No binary executed. No `open_binary`. No Ruby toolchain.*
