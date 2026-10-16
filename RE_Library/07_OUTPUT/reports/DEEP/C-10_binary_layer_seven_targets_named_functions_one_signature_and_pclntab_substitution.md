# C-10 — The binary layer at seven targets: the `NAMED_FUNCTIONS=1` signature, and the pclntab instrument that recovers what Ghidra cannot

**Purpose:** C-00 opened the binary layer and C-08 measured the Merlin suite. This report closes the first wave: it files the **seventh** target, records the **cross-target pattern** that seven measurements now support, and states the **instrument substitution** that made the Sliver client measurable at all.

**Tags:** `[verified]` (instrument run, output shown) · `[read]` (quoted from an artifact read directly) · `[absence]` (zero with a positive control) · `[inferred]` (reasoning over evidence).

**Write scope:** this file only plus `binlayer\C-07_*.tsv`. Every prior report unmodified.

---

## §0 Headline

`[verified]` **Across seven targets, Ghidra's name resolution does not fail proportionally — it fails BIMODALLY.** Four Merlin targets resolve **95.7%–98.3%** of their functions. Three targets resolve **one function each**:

| target | bytes | functions | named | coverage | thunks |
|---|---:|---:|---:|---:|---:|
| `merlin.x86.dll` | 14,687,006 | 7,440 | 7,118 | **95.7%** | 51 |
| `merlin.x64.dll` | 15,145,760 | 11,311 | 11,081 | **98.0%** | 20 |
| `merlinServer-Windows-x64.exe` | 26,329,600 | 17,265 | 16,971 | **98.3%** | 5 |
| `merlinCLI-Windows-x64.exe` | 20,754,432 | 13,318 | 13,059 | **98.1%** | 5 |
| `merlinAgent-Windows-x64.exe` | 13,939,200 | 11,246 | **1** | **0.009%** | 4 |
| `merlinAgent-Windows-x64-Debug.exe` | 13,939,200 | 11,246 | **1** | **0.009%** | 4 |
| **`sliver-client_windows-amd64.exe`** | **65,866,240** | **41,528** | **1** | **0.002%** | 5 |

`[verified]` **`NAMED_FUNCTIONS=1` is not a partial failure. It is a distinct signature**, and the Sliver client reproduces it on a binary **4.7× larger** than either Merlin agent, from a **different project**, with a **different Go version** (1.27.1 vs 1.27.2).

`[inferred]` **The mechanism is the same in both cases and it is not "stripping."** It is that Go's function names live in **`pclntab`**, not in the PE symbol table, and Ghidra's Go analyzer requires `GoRttiMapper`, which refuses an untested Go version:

```
ERROR Untested Go version [1.27.1] (GoRttiMapper)
WARN  Missing Go bootstrap type info, unable to extract Go RTTI info.
ERROR Go symbol analyzer error: unable to get GoRttiMapper (GolangSymbolAnalyzer)
ERROR Go string analyzer error: unable to get GoRttiMapper (GolangStringAnalyzer)
```

`[inferred]` **Both versions in this corpus are untested by Ghidra 12.1.4.** No target in this corpus has been named by `pclntab`. **Every named count in C-08 and C-07 is therefore a count of DWARF-derived names, not of Go names** — and the two populations are different.

---

## §1 The Sliver client run — what it cost and what it produced

`[verified]` **Target:** `RE_Library\02_BINARIES\sliver\sliver-client_windows-amd64.exe`, **65,866,240 B**, SHA-256 `7C500D4AE84D792E4BB3F4BC89A0F325688F6E7B7F0574A6718BB99D30B305CB`.

`[read]` **Run output, verbatim:**

```
INFO  REPORT: Analysis succeeded for file: ...sliver-client_windows-amd64.exe
INFO  DumpSyms.java> EXPORTED_FUNCTIONS=41528
INFO  DumpSyms.java> NAMED_FUNCTIONS=1
INFO  DumpSyms.java> THUNKS=5
INFO  DumpSyms.java> TOTAL_BODY_BYTES=23600441
INFO  REPORT: Post-analysis succeeded
INFO  REPORT: Save succeeded
GATE_STAGE_OK
```

`[verified]` **Artefact filed:** `binlayer\C-07_sliver-client_windows-amd64.ghidra-symbols.tsv`, **1,945,710 B / 41,534 rows.** Header records `language x86:LE:64:default`, `compiler golang`, `imageBase 140000000`.

`[inferred]` **The harness worked exactly as C-08 specified it** — space-free `%TEMP%` stage, hardcoded wrapper `.bat`, `GATE_STAGE_OK`, then copy back. **No new toolchain failure, which is NOT evidence that C-08's seven are fixed.** 12 minutes wall clock, 769 s CPU, 1.9 GB working set.

`[verified]` **Incidental observation, recorded because it is unusual:** Ghidra reported `Invalid PNG data` at 5 addresses and `Invalid GIF data` at 4, i.e. **the client carries embedded image resources that Ghidra's PNG/GIF analyzers walked into and rejected.** Not followed up here.

---

## §2 The instrument substitution — and why its number is not comparable

`[verified]` **sliver-diver built an independent `pclntab` parser** (`binlayer\_d96_pclntab.ps1` → `_d96_pclntab.tsv`, 51,661 rows on disk) and recovered:

**51,657 functions / 51,657 named / 100%**, split 22,273 third-party · 7,472 Sliver-internal across 90 packages · 1,445 `runtime.*` · 855 `type:*`.

`[inferred]` **The 100% is instrument-specific and MUST NOT be compared to the DWARF percentages in §0.** Both are percentages of a function count; the **denominators are different populations.** `[inferred]` **Ghidra's 41,528 is a count of things Ghidra decided were functions in a stripped-of-DWARF binary; the pclntab 51,657 is a count of entries in Go's own function table.** Same-looking number, different objects — **this is the D88/D90 shape: a name that is not the thing it denotes.**

`[inferred]` **The correct reading: pclntab is authoritative for Go function identity, and Ghidra is authoritative for control-flow recovery.** They answer different questions and neither supersedes the other.

### §2.1 Three instrument failures, each caught before it became a finding

`[read]` **F1 — a false-positive magic match.** The first `pclntab` candidate yielded `nfunc=1.4e19`, `pad1=102`. **Requiring `pad1==0 pad2==0 minLC==1 ptrSize==8` found exactly one valid candidate.** A magic-number match is not a table.

`[read]` **F2 — a greedy regex manufactured a 25-name "build/source mismatch," and the tell was the bijection.** Every "extra" was a source name plus a gRPC runtime suffix. **A lazy quantifier did not fix it** — the instrument had to be rebuilt around the 201 known names. **`[inferred]` The generalisable form: when a diff reports 25 additions and 0 removals against a list you expect to match exactly, check for a 25/25 bijection before believing a mismatch.**

`[read]` **F3 — a path filter `-like "*$p/*"` returned 0 for `client/console` while the string control said 163.** Go symbols continue with `.`, not `/`, after the package name. **The probe's shape did not match the evidence's shape** (instrument rule 5).

---

## §3 The Sliver result that matters most: the client does not link the server

`[verified]` **`[absence]`, with positive controls firing:**

| searched | result |
|---|---|
| `server/db` | **0** |
| `server/rpc` | **0** |
| `server/certs` | **0** |
| `gorm.io/gorm` | **0** |
| `modernc.org/sqlite` | **0** |
| `operator_name` | **0** |
| `aiOperatorName` | **0** |
| **`client/console`** (control) | **163 strings / 145 functions** |
| **`protobuf/rpcpb`** (control) | **604** |
| `client/command/ai` (control) | `ai.AICmd`, `ai.buildAIContext`, `ai.isAITTY` present |

`[inferred]` **D91's inert-ownership-filter finding stands in the SOURCE and has NO compiled counterpart in this artifact, because the file containing it — `server/db` — is not linked into the client at all.** The filtered-vs-unfiltered SQL literal question **cannot be answered against the client binary**, and answering "filtered" or "unfiltered" from it would be a fabrication.

`[verified]` **`DeleteAIConversation` occurs 7× in the client, all gRPC stubs** — and `[inferred]` **the compiler cannot eliminate an argument to a function that was never compiled in.** The lane answered **"not applicable"** rather than **"UNKNOWN"**, and `[inferred]` **that distinction is correct: UNKNOWN implies inconclusive evidence; this is conclusive absence on two independent instruments.**

`[verified]` **`SaveAIConversation` occurs 14× in a binary that does not contain the function.** `[inferred]` **Counting those as "server code present" would have reported the exact inversion of the truth.** The lone `implant/sliver/handlers` symbol is `matcher.Match` — the client's **local** regex filter, not implant code.

`[inferred]` **R1, the corpus gap this opens: there is no `sliver-server` binary in `02_BINARIES\sliver\`.** D91's finding has no compiled artefact to test against. **That is a corpus gap, not an analysis gap** — and it is the single highest-value acquisition for the binary layer.

---

## §4 What seven measurements support, that four could not

`[inferred]` **C-08 §8 offered "symbol richness is not transferable across binaries or architectures" on the strength of six Merlin targets.** Seven targets, now spanning **two projects and two Go versions**, support a stricter form:

**Every Go binary in this corpus that Ghidra cannot map RTTI for will report `NAMED_FUNCTIONS=1` or near it, regardless of size, project, or whether DWARF is present.** The four Merlin targets that scored 95.7%–98.3% did so because they carry **DWARF** (the `/NNN` sections), which is a Ghidra-readable name source independent of Go RTTI. `[verified]` **The agents and the Sliver client carry no DWARF names, and their PE symbol tables are not a substitute** — C-08 §4 recorded both Merlin DLLs declaring a COFF symbol table past their own EOF.

`[inferred]` **Operationally: `NAMED_FUNCTIONS=1` on a Go binary is a signal to switch to `pclntab`, not a signal that the target is stripped.** Three targets now demonstrate it, and the substitution recovered 100% of Go function identity on the largest.

`[inferred]` **The bound, stated: `pclntab` gives identity, not behaviour.** It does not recover control flow, types, or call edges. The Sliver client's 51,657 functions are **named and unreversed** — which is the honest state.

---

## §5 Status

`[verified]` Seven targets analysed; `C-01`–`C-07` on disk, 6.9 MB of symbol tables total.

`[verified]` The Sliver client yields **41,528 functions / 1 named** under Ghidra and **51,657 / 51,657** under an independently built `pclntab` parser.

`[verified]` The Sliver client does **not** contain `server/db`, so D91's finding is unverifiable against it. Positive controls fired.

`[inferred]` **Open:** no `sliver-server` binary; the five non-PE Merlin agents (Mach-O and ELF — Ghidra P0 is PE-only on this host) remain unanalysed; the two APKs are D100's; the seven `.wasm` modules are D97's.

`[inferred]` **C-08's seven toolchain failures were not re-tested**, so their fix status is unknown and this run is not evidence either way.

**End of C-10.**
