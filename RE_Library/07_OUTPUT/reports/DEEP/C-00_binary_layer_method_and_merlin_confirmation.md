# C-00 — The binary layer, opened: method, toolchain, and a source-to-binary confirmation

**Lead, round 23.** The objective has been pursued entirely at the **source level** for 94 reports.
The user's directive in round 23 is explicit: *"we want power not just blindly reverse, an
intelligent reverse so binary is very important."* This report opens the binary layer, records what
it can and cannot do, and delivers the first source-to-binary confirmation in the corpus.

**This is a capability report, not a finding report.** Its job is to establish that the layer works
and to bound it honestly before any lane spends effort in it.

---

## 1. What binaries the corpus actually contains

Census over all of `RE_Library` for binary extensions (`exe dll so dylib sys elf apk wasm class
jar lib o a pyc node`)**, by enumeration, not by name:

| ext | files | bytes |
|---|---|---|
| `.dll` | 159 | 119,646,593 |
| `.class` | 85 | 252,319 |
| `.bin` | 80 | 2,243,908 |
| `.exe` | 52 | 221,387,834 |
| `.jar` | 21 | 36,164,634 |
| `.so` | 13 | 240,616 |
| `.wasm` | 7 | 7,118,726 |
| `.elf` | 6 | 2,446,292 |
| `.lib` | 6 | 1,083,566 |
| `.apk` | 2 | 2,135,060 |
| `.dylib` | 1 | 8,660 |
| **total** | **432** | **392,728,208 (374.5 MB)** |

### The denominator defect in that table, stated before anyone uses it

**432 files / 374.5 MB is NOT the analysable population.** It is dominated by three categories that
must be excluded, and I am excluding them before any lane counts them:

1. **Microsoft reference assemblies, vendored.** `Covenant\Data\AssemblyReferences\` carries
   `System.Windows.Forms.dll` (5.9 MB + 5.0 MB), `mscorlib.dll`, `System.Data.dll`,
   `System.XML.dll`, `System.Management.Automation.dll` at **two framework generations (net35 and
   net40)**. These are **Microsoft's** binaries, shipped so Covenant can compile payloads against
   them. Under the objective's own rule they are `vendored-dependency`, and reversing them is
   reversing .NET itself.
2. **Tooling jars.** `apktool.jar` appears **twice** at 17.7 MB and 16.3 MB; `sign.jar` 1.9 MB.
   Third-party packaging tools.
3. **The `.class` population (85 files / 252 KB)** is ~0.06% of the byte mass and is compiled Java
   from a source tree already in scope.

**After exclusion, the genuinely first-party binary population is small and specific.** That is the
finding, and it is the opposite of what the 374.5 MB figure suggests.

---

## 2. The first-party binary targets, named

| target | bytes | what it is |
|---|---|---|
| `02_BINARIES\sliver\sliver-client_windows-amd64.exe` | **65,866,240** | Sliver operator client, Go, compiled |
| `merlinServer-Windows-x64.exe` | 26,329,600 | Merlin teamserver |
| `merlinCLI-Windows-x64.exe` | 20,754,432 | Merlin CLI |
| `merlin.x64.dll` | 15,145,760 | Merlin agent, reflective DLL |
| `merlin.x86.dll` | 14,687,006 | Merlin agent, reflective DLL |
| `merlinAgent-Windows-x64(-Debug).exe` | 13,939,200 ea. | Merlin agent, standalone |
| `merlinAgent-Linux-{x64,arm,arm64}` | ~12 MB ea. | Merlin agent, Linux |
| `merlinAgent-Darwin-arm64` | 11,808,210 | Merlin agent, macOS |
| `androrat\...\app-release.apk` | 2,129,794 | AndroRAT release APK |
| `keystone.wasm` | 4,450,666 | **embedded assembler engine** in Sliver's vendor tree |
| `sqlite3.wasm` | 1,406,839 | embedded SQLite in Sliver's vendor tree |

**Note the pairing opportunity this creates.** For **Sliver** and for **Metasploit's handlers** we
hold source *and*, for Sliver, a compiled client. For **Merlin** we hold binaries and `merlin.c` /
`merlin.def` but not the full source tree. Merlin is therefore the target where the binary layer
carries information the source layer cannot.

---

## 3. The toolchain, verified by execution

**Ghidra 12.1.4 PUBLIC at `C:\tools\ghidra_12.1.4_PUBLIC`**, `GHIDRA_INSTALL_DIR` set, JDK 21.0.12
resolvable. Verified by a real analysis run, not by checking that the directory exists.

### The invocation, corrected twice — both failures recorded

**Failure 1 — positional arguments.** `analyzeHeadless <projLocation> <projName> -import <file>`
takes the project location and name **positionally**. My first attempt used
`name=probe location=...`, which Ghidra rejected:

```
ghidra.util.exception.InvalidInputException: Bad argument: probe
```

**Failure 2 — `-readOnly` discards the import.** My second attempt used `-readOnly` to suppress an
interactive *"Press any key to continue . . ."* prompt. It ran and reported
`Analysis succeeded` — and then reported:

```
REPORT: Discarded file import due to readOnly option: /merlin.x86.dll
```

**The analysis was real and the program was thrown away.** The third attempt dropped `-readOnly`,
used `-deleteProject` never, and succeeded. A subsequent `-process`-mode call then failed with
`Could not find project: ... -- should already exist in -process mode`, which is the *consequence*
of failure 2, not a new defect.

**Rule extracted: `-readOnly` is not a headless/no-prompt flag. It is a "do not persist" flag, and
it is incompatible with any two-phase workflow.** The keypress prompt is avoided instead by running
through a batch wrapper with stdin closed.

### The working invocation

```bat
cd /d "C:\tools\ghidra_12.1.4_PUBLIC\support"
call analyzeHeadless.bat "<projDir>" <projName> ^
     -import "<target>" -analysisTimeoutPerFile 900 ^
     -scriptPath "<scriptDir>" -postScript DumpSyms.java
```

---

## 4. First real result: 7,440 functions, and a source-to-binary confirmation

Run against `merlin.x86.dll` (14,687,006 B,
SHA-256 `5242B9D5A2777DF5A0CB011F92FF620B3D6D5CB2C97DA2CA71052F82CE28768F`):

```
EXPORTED_FUNCTIONS=7440
NAMED_FUNCTIONS=7118
```

**7,118 of 7,440 functions carry real names — 95.7% symbol coverage.** This is not a stripped
binary. Full table exported to `07_OUTPUT\binlayer\C-01_merlin.x86.dll.ghidra-symbols.tsv`
(392,165 B).

### The exports match `merlin.def` exactly — seven for seven

`merlin.def` declares seven exported symbols. The binary contains all seven, at their real sizes:

| export | address | body bytes | declared in `.def` |
|---|---|---|---|
| `_Magic` | `61c81507` | 24 | yes |
| `Run` | `61c81520` | 67 | yes |
| `VoidFunc` | `61c81570` | 67 | yes |
| `DllInstall` | `61c815c0` | 67 | yes |
| `DllRegisterServer` | `61c81610` | 67 | yes |
| `DllUnregisterServer` | `61c81660` | 67 | yes |
| `Merlin` | `61c816b0` | 64 | yes |

**This is the corpus's first source-to-binary confirmation.** `merlin.def` is a source artefact
claiming an interface; the compiled binary is the measurement; they agree. The five sibling
exports (`Run`, `VoidFunc`, `DllInstall`, `DllRegisterServer`, `DllUnregisterServer`) all being
**exactly 67 bytes** is consistent with thin forwarders to a shared implementation — worth a
follow-up, flagged not asserted.

### And the `Merlin`→`Magic` chain is visible in the binary

`merlin.c` declares `Magic(char *url)` → `Merlin(url)`. Both symbols are present, adjacent
(`_Magic` at `61c81507`, `Merlin` at `61c816b0`), consistent with the source. **The reflective-DLL
entry point is real and present, not merely documented.**

---

## 5. What Ghidra does NOT do on these targets, stated as a bound

**The Go analyzers fail.** Every run emits:

```
ERROR Untested Go version [1.27.2] (GoRttiMapper)
WARN  Missing Go bootstrap type info, unable to extract Go RTTI info.
ERROR Go symbol analyzer error: unable to get GoRttiMapper (GolangSymbolAnalyzer)
ERROR Go string analyzer error: unable to get GoRttiMapper (GolangStringAnalyzer)
```

**Consequences, and this matters for planning:**

- Go **RTTI** is unavailable → **no Go type reconstruction** from the binary.
- Go **string** analysis is unavailable → the string de-obfuscation pass does not run.
- Go **symbol** analysis is unavailable → the 7,118 names come from **DWARF**, not from Go's own
  pclntab symbol table.

**A critical distinction I am recording before anyone builds on this:** DWARF is present here
because this build carries debug info. **A release or stripped Merlin build would lose most of the
7,118 names.** The `merlinAgent-Windows-x64-Debug.exe` in the same directory is explicitly a debug
build. **Symbol coverage must be measured per binary, never assumed from this one.**

**DWARF import is partial but real:** 277 types imported, with a bounded set of unrecoverable
expressions (`DW_OP_reg1`, `DW_OP_lit4; DW_OP_stack_value`, and a four-piece
`DW_OP_reg0; DW_OP_piece; ...` composite). These are un-recoverable *locations*, not missing types.

---

## 6. Method rules for the binary layer, derived from the three failures above

1. **A tool that reports success may have done nothing with the result.** `-readOnly` printed
   `Analysis succeeded` and discarded the program. **Read the REPORT lines, not the exit code** —
   the exit code was 0 on the run that threw the analysis away.
2. **Measure symbol coverage per binary before trusting any symbol-based claim.** 95.7% here is a
   property of *this* build with *this* debug info.
3. **The analyzer's own error output is evidence.** `Untested Go version [1.27.2]` is a fact about
   the target's toolchain and is itself a finding — it constrains what Ghidra can recover.
4. **Source agreement is confirmatory only when the source claims an interface and the binary shows
   it.** The seven `.def` exports are a genuine confirmation because the direction is
   source-claims → binary-measures. Comparing two source files proves nothing.

---

## 7. What the binary layer is FOR, given the source layer's findings

The source layer has produced defects whose *exploitability* is a binary-layer question:

| source finding | the binary question it raises |
|---|---|
| D91 — `AIConversationByID`'s ownership filter passed `""` at 8 of 9 sites | does the compiled build contain the filtered or the unfiltered query string? |
| D85 — 49 of 49 operator-data interpolations reach a shell unescaped | is the escaping helper **linked in at all**? A source call can be dead-code-eliminated. |
| D90 — `SSLClientCert`/`SSLClientKey` guards both accept any file | unchanged by compilation; a source-level defect. **Binary adds nothing.** |
| D89 — `:5254` nil-deref with the guard 11 lines later | does the compiler reorder or eliminate the guard? |
| D93 — `Split("bin")[0]` path derivation | the compiled path strings are literal and recoverable |
| D82/D77 — `bare?` structurally unable to return true | is the call site present in the compiled gem? **(No Ruby toolchain — remains blocked.)** |

**And the honest scope statement:** the binary layer **does not** make the remaining ~35,000 source
files tractable, and it **does not** substitute for the source pass. It is a **verification and
exploitability layer** — a small number of specific questions, each answerable against a specific
binary. Treating it as a second exhaustive sweep would repeat the denominator error this corpus has
already made four times.

*End of C-00. Evidence: `07_OUTPUT\binlayer\C-01_merlin.x86.dll.ghidra-symbols.tsv`, 392,165 B.*
