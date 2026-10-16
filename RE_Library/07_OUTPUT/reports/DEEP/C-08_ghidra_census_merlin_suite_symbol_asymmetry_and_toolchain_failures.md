# Ghidra headless symbol census — Merlin suite + toolchain failures

Run: round 24, goal `goal-7a9014c9`. Tool: Ghidra 12.1.4 PUBLIC,
`analyzeHeadless.bat`, script `DumpSyms.java`, driver `gate.bat`.

All rows below are **measured by executing Ghidra**, not inferred.

---

## 1. Results

| Target | Bytes | Machine | Sections | Functions | Named | Coverage |
|---|---:|---|---:|---:|---:|---:|
| `merlin.x86.dll` | 14,687,006 | `0x14C` i386 | 18 | 7,440 | 7,118 | **95.7%** |
| `merlin.x64.dll` | 15,145,760 | `0x8664` x64 | — | 11,311 | 11,081 | **98.0%** |
| `merlinServer-Windows-x64.exe` | 26,329,600 | `0x8664` x64 | 16 | 17,265 | 16,971 | **98.3%** |
| `merlinCLI-Windows-x64.exe` | 20,754,432 | `0x8664` x64 | — | 13,318 | 13,059 | **98.1%** |
| `merlinAgent-Windows-x64.exe` | 13,939,200 | `0x8664` x64 | 8 | 11,246 | **1** | **0.009%** |
| `merlinAgent-Windows-x64-Debug.exe` | 13,939,200 | `0x8664` x64 | — | 11,246 | **1** | **0.009%** |

Thunk counts: x86.dll 51 · x64.dll 20 · server 5 · CLI 5 · both agents 4.

---

## 2. THE FINDING: the "Debug" agent is not debug-symbol-carrying

`merlinAgent-Windows-x64-Debug.exe` and `merlinAgent-Windows-x64.exe` are
**byte-identical in size** (13,939,200) and **identical in every census figure**:
11,246 functions, **1 named**, 4 thunks.

**The filename says `Debug`. The symbol table says stripped.** A build named for
its debug variant that carries no symbols is a **name-is-not-a-measurement**
instance of exactly the species D90 named (`Bool` ≠ `Bare`).

Consequence for the binary layer: **there is no debug-instrumented agent build in
this corpus to fall back on.** The rich-symbol targets are the *server-side*
binaries (server, CLI, both DLLs). The *implant-side* binaries are dark.

This inverts the natural assumption. The obvious reverse target — the thing that
lands on a victim — is the least analysable artifact here.

---

## 3. THE MECHANISM: the `/NNN` sections ARE the DWARF

Measured by parsing the PE section tables directly:

```
merlin.x86.dll               18 sections
  .text .data .rdata /4 .bss .edata .idata .CRT .tls .reloc
  /14 /29 /41 /55 /67 /78 /94 /110

merlinAgent-Windows-x64.exe   8 sections
  .text .rdata .data .pdata .xdata .idata .reloc .symtab      <-- NO /NNN

merlinServer-Windows-x64.exe 16 sections
  .text .rdata .data .pdata .xdata /4 /19 /32 /46 /65 /78 /95 /112 .idata .reloc .symtab
```

The `/NNN` names are **COFF long-name offsets into the string table**, and they
are the Go linker's DWARF debug sections. Their absolute absence from the agent
builds is the mechanism behind the 1-named-function result.

Note the machine-type asymmetry: `merlin.x86.dll` is **i386 (`0x14C`)** and takes
the 18-section path, while the agents are **x64 (`0x8664`)** with 8 sections.
The x86 and x64 builds are produced by materially different linker
configurations, so **symbol richness must be measured per binary and never
generalised across architectures in the same suite.**

---

## 4. A MEASUREMENT PROBLEM IN THE PE ITSELF

Reading the COFF symbol table offset from the file header:

```
merlin.x86.dll       size=14,687,006  symtab=0x02037E00  nSyms=  5040  strtab=0x0204E060  PAST_EOF=True
merlin.x64.dll       size=15,145,760  symtab=0x0205DC00  nSyms=  4928  strtab=0x02073680  PAST_EOF=True
merlinAgent-Win.exe  size=13,939,200  symtab=0x00000000  nSyms=568480  strtab=0x009C2340  PAST_EOF=False
merlinServer-Win.exe size=26,329,600  symtab=0x00000000  nSyms=585632  strtab=0x00A0D940  PAST_EOF=False
```

**Both DLLs declare a symbol table starting past their own end of file.** The Go
linker emits a COFF header whose symbol-table pointer is not backed by file
bytes. Recorded as an observation; **the cause is not asserted.** It is a
plausible reason Ghidra fell back to DWARF for the DLLs and found no symbol path
at all for the agents, but that linkage is not proven here.

The agents instead report `symtab=0x0` with an implausibly large `nSyms`
(568,480 and 585,632). Those figures are **not** a symbol count; they are a
header field that does not mean what its name says in these images.

---

## 5. TOOLCHAIN FAILURES — SEVEN, EACH COST A RUN

These are recorded because six of the seven were silent or misleading. The
harness that works is `gate.bat` + `ghidra_run.ps1`; the `.bat` variants are
retained only as a record of what fails.

| # | Invocation | Result |
|---|---|---|
| 1 | `name=probe location=...` | `InvalidInputException: Bad argument: probe` — project args are **positional** |
| 2 | project dir does not exist | `Abort ... Directory not found` — analyzeHeadless **does not create it** |
| 3 | `-readOnly` added | prints **`Analysis succeeded`**, then `Discarded file import due to readOnly option` — **exit 0, analysis gone** |
| 4 | `setlocal` in the `.bat` | scopes env vars away from the child; script sees nothing |
| 5 | env var `REA_EXPORT` | never reached the script process; **script args work, env vars did not** |
| 6 | spaced script arg under `FOR REDDACTED` | `Bad argument: REDDACTED\RE_Library\...` — Ghidra **splits args at the space**; output must stage through a space-free path |
| 7 | `#` used as a batch comment | `'#' is not recognized as an internal or external command` — cmd comments are `REM`; `%1`-substitution **silently corrupted the rest of the script** |

### The one that matters most

**Failure 3.** `-readOnly` was added to suppress the `Press any key to continue`
prompt. It printed `Analysis succeeded` **and then discarded the file import**,
exiting **0**. A tool reported success and did nothing with the result.

**Read the REPORT lines, not the exit code.** This is the same species as the
`git ls-remote` exit-0 trap already in `PUSH_PROCEDURE.md`: a tool's exit status
is a statement about the tool, not about the work.

### Failure 7 in context

Failure 7 is the one where I corrupted my own instrument and it *looked* like a
Ghidra fault. `#` at line start is not a batch comment, so cmd executed every
comment line as a command — and because `%1`/`%2` were already bound, the
comment text with substituted paths appeared in the error output, making it look
like a path-quoting bug in Ghidra. It was not. `gate.bat` now uses `REM`.

---

## 6. PERSISTENT ANALYZER BOUND

Every one of the six runs emitted, repeatedly:

```
ERROR Untested Go version [1.27.2] (GoRttiMapper)
ERROR Go symbol analyzer error: unable to get GoRttiMapper
ERROR Go string analyzer error: unable to get GoRttiMapper
WARN  Missing Go bootstrap type info, unable to extract Go RTTI info.
```

So, for the entire Merlin suite:

- **No Go RTTI** — interface tables and concrete type recovery unavailable.
- **No Go string de-obfuscation** — string analysis unavailable.
- The 95.7–98.3% names on the rich targets come from **DWARF**, not pclntab.

Also observed and worth recording, because it bounds the DWARF import itself:

```
ERROR Exception creating source file: path not valid: file://_/_/GOROOT/src/runtime/cgo/gcc_context.c
ERROR   DW_OP_reg1 -> 8
ERROR   DW_OP_reg2 -> 9
ERROR   DW_OP_lit4; DW_OP_stack_value -> 1
ERROR   DW_OP_reg0; DW_OP_piece; DW_OP_reg2; DW_OP_piece; ... -> 1
```

The `GOROOT` source paths mean **the build machine's Go source layout is recorded
in the binary** — an artifact-identity datapoint, and a reminder that DWARF type
recovery is **partial**: bounded location expressions are dropped.

---

## 7. Go generic symbols are rejected by the PE loader

Every run also emitted hundreds of:

```
ERROR Error creating label named
  crypto/internal/fips140/ecdsa.Sign[go.shape.*crypto/internal/fips140/nistec.P384Point,...]
at address 61f32260: Symbol name contains invalid characters (PeLoader)
```

**Bracketed Go generic instantiation names cannot be created as Ghidra labels.**
This is a real coverage bound, not noise: an unknown fraction of instantiated
generic functions are present as *functions* but **unnamed in the export**.

The 7,440 / 11,311 / 17,265 counts are therefore **function counts**, while the
7,118 / 11,081 / 16,971 are **labelled** counts — and the gap between
`EXPORTED` and `NAMED` mixes genuine `FUN_`-style unnamed code with
**nameable-but-rejected** generics. The true nameable population is unknown and
**strictly larger** than the named count.

---

## 8. Targets analysed

Path correction worth recording: **`merlinServer-Windows-x64.exe` is at the
extraction ROOT** (`05_TARGETS\merlin_extracted\`), **not** under `data\bin\`
where the other binaries live. The first batch run silently skipped it as
`MISSING` because the path was constructed from the pattern the other files
followed rather than from an enumeration. **Instrument rule 15 — a path
constructed from a NAME instead of an ENUMERATION.**

---

## 9. Still outstanding

- `merlinAgent-Darwin-arm64` (11,808,210) · `merlinAgent-Darwin-x64` (12,761,408)
  · `merlinAgent-Linux-arm` (12,124,284) · `merlinAgent-Linux-arm64` (11,534,460)
  · `merlinAgent-Linux-x64` (12,492,924) — **Mach-O and ELF, not PE.** Ghidra P0
  is PE-only on this host; these need a different provider or `-processor` hint.
- `sliver-client_windows-amd64.exe` (65,866,240, Go) — not yet run.
- The two APKs and the seven WASM modules.
- **Pairing work**: none of the source-to-binary questions in `C-00 §7` are
  answered yet. The symbol tables now exist; the query strings and call sites
  have not been extracted from them.
