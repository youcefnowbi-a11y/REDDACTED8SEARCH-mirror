# D130 — THE FIVE ENUMERATED LAYER-PAIRS, THE TWO-TIER SYMBOL COVERAGE, AND THE RELEASE/DEBUG CONTROL THAT HAD NEVER RUN

**Author:** lead (Lead-authored)
**Lane:** binary-layer — **LANE DIED**
**Scope owner:** lead
**Written:** 2026-10-16, round 4/80
**Layer:** binary-layer (source cross-referenced)

## Rule 33 census header

```
SCOPE:            RE_Library/07_OUTPUT/binlayer/*.tsv (15 pclntab name tables, 7 Ghidra symbol dumps)
                  RE_Library/05_TARGETS/merlin_extracted/data/bin/merlinAgent-Windows-x64{,-Debug}.exe
                  RE_Library/01_SOURCE_c2/sliver (17,124 files, source cross-reference only)
DEFINER SCOPE:    names defined in each binary's pclntab (Go funcnametab); Ghidra symbol table
CONDITIONAL SCOPE: none — no preprocessor arm is involved in this report
COUNTED:          data rows per TSV, distinct names, matching names, differing bytes
```

---

## §0 — Corrections to the brief, LEAD-OWNED, and two of them are mine

**C-130.1 — I destroyed my own first probe and the damage is instructive.**
My first read of D127's decisive byte indexed `68,779,968` into a **64-byte array**. PowerShell returned `$null`, the format string printed nothing, and my own comparison then printed `0x17 = kEncodedHeader? False`. **A verdict manufactured from a null operand.** I caught it one step later and re-seeked — the byte at that offset is `0xE6`, not `0x17`. This is recorded here because it is the same defect class as the brief's own warning, and I committed it two steps after praising a lane for avoiding it.

**C-130.2 — D127's decisive byte is UNVERIFIED by the Lead, not disproven.**
After the correct seek, `0xE6` is still not `0x17`. But my big-endian control returned `0` rather than the 17-orders-of-magnitude figure, which means **my check measures a different field base than the claim does.** A check that measures a different thing cannot refute its subject. D127's byte `0x17` therefore stands as **lane-verified, Lead-unverified**, and I am not calling it wrong. Independently confirmed on my side: archive is unique (143 archives scanned corpus-wide, exactly one `merlinServer-Windows-x64.7z`), `68,780,065 B` exact, `32 + 68,779,968 + 65 = 68,780,065` exact, signature `37 7A BC AF 27 1C` exact.

**C-130.3 — my binary paths were guessed, and both guesses were wrong.**
My first P5 byte-diff script constructed `RE_Library\02_BINARIES\merlin\merlinAgent-Windows-x64.exe`. **Both operands MISSING.** The real location is `RE_Library\05_TARGETS\merlin_extracted\data\bin\`. The report below uses enumerated paths. This is the standing rule violated by me: **never build a path from a remembered filename — enumerate.**

**C-130.4 — the brief's P2 warning was correct and its own named helper does not exist.**
The brief warned that `shellEscapeByte` is a collision. That warning held, and the outcome is stronger: **no `ShellEscape`/`ShellQuote`/`escapeShell`/`QuoteArg`/`SingleQuote` symbol exists in ANY probed binary.** D85's helper is not present — and it was not dead-code-eliminated. It does not exist under that name. See P2.

**C-130.5 — `binary-layer` is no longer on the roster.**
`send_message` to that target returned `active teammate "binary-layer" not found`. This report is Lead-authored under the standing rule *"Lead writes any report whose lane dies."* The D130 number was free at authoring time (registry max key `129`, DEEP glob max D129) and is claimed here.

---

## §1 — THE TOOLING SURFACE: Ghidra name coverage is TWO-TIER and BINARY-SPECIFIC

This is the measurement that had to exist before any pair could be honestly probed. Read from the `# SUMMARY` line of each Ghidra symbols TSV:

| TSV | total | **named** | thunks | bodybytes |
|---|---|---|---|---|
| `C-01_merlin.x86.dll` | 7,440 | **7,118** | 51 | 4,798,169 |
| `C-02_merlinServer-Windows-x64.exe` | 17,265 | **16,971** | 5 | 7,832,526 |
| `C-03_merlinCLI-Windows-x64.exe` | 13,318 | **13,059** | 5 | 6,093,195 |
| `C-04_merlin.x64.dll` | 11,311 | **11,081** | 20 | 5,896,791 |
| `C-05_merlinAgent-Windows-x64.exe` | 11,246 | **1** | 4 | 5,909,930 |
| `C-06_merlinAgent-Windows-x64-Debug.exe` | 11,246 | **1** | 4 | 5,909,930 |
| `C-07_sliver-client_windows-amd64.exe` | 41,528 | **1** | 5 | 23,600,441 |

**`named=1` is a non-loaded name table, not an absence.** Proven with a control on `C-07`: `main.` → 0, `runtime.` → 0, `fmt.` → 0, `Split` → 0, `strings.` → 0. **A Go binary cannot lack `runtime.`** Every row in those three files is Ghidra's synthetic `FUN_140001080`.

**Consequence, and it is the reason three pairs could have died silently:** a lane told to "search the sliver binary for the ownership filter" would have got `0` from `C-07` and filed an **absence** for a symbol that may be perfectly present. `[verified]` The objective's own warning is confirmed with a number — *symbols come from DWARF, so symbol coverage must be measured PER BINARY.*

**The working instrument is the pclntab name table.** Control-confirmed on `_lead_pclntab_merlinAgent-Windows-x64.exe.tsv` (12,529 rows): `runtime.` **1,420** · `net/http` **962** · `strings.` **56** · `os.Executable` **1**. Every probe in §2–§5 uses these, and every probe below prints a control pair (`always-present` must be >0, `never-present` must be 0) before any verdict.

---

## §2 — P5: THE RELEASE/DEBUG CONTROL THAT HAD NEVER RUN

`[verified]` **The rows are identical. The bytes are not.**

**Row identity, on both operands, operand-checked first:**
```
release exists True   debug exists True
release lines 12,529  debug lines 12,529
DATA ROWS release 12,525  debug 12,525
FULL-FILE case-sensitive identical        : False
ROW-FOR-ROW case-sensitive identical      : True
NAMES-ONLY, order preserved identical     : True
NAMES-ONLY, sorted set identical          : True
OFFSETS-ONLY, order identical             : True
FIRST DIVERGING DATA ROW (0-based)        : -1
header lines release 4  debug 4  -> hdr[0] DIFFERS, hdr[1..3] SAME
```
**The only difference in either TSV is `hdr[0]`, which carries the filename string itself.** Every one of the 12,525 data rows — name and offset, case-sensitive, in order — is identical.

**Byte identity of the real artifacts (enumerated paths):**
```
A: ...\05_TARGETS\merlin_extracted\data\bin\merlinAgent-Windows-x64.exe        13,939,200 B
B: ...\05_TARGETS\merlin_extracted\data\bin\merlinAgent-Windows-x64-Debug.exe  13,939,200 B
release sha256 E9501A7F325950591B585DFC83E0BAE8B519FFF153806E9EA91351B6742C3FA5
debug   sha256 F12C1B24C4A700F08EC3E5EF282CED877AA7660C5E5FA4A589DE63E0E768A654
SAME SHA : False      SAME SIZE: True
bytes compared 13,939,200   FIRST DIFFERING OFFSET 220
TOTAL DIFFERING BYTES 64,565   (0.46319%)
```

**`[verified]` The differing bytes are LOCALIZED, not spread — and the histogram is the finding:**

| 1 MB band | offset | differing bytes |
|---|---|---|
| 0 | 0 | 4 |
| 2 | 2,097,152 | 18 |
| 4 | 4,194,304 | 1 |
| 5 | 5,242,880 | 60 |
| **6** | **6,291,456** | **1,375** |
| 11 | 11,534,336 | 210 |
| 12 | 12,582,912 | 1 |
| **13** | **13,631,488** | **62,896** |

`[inferred]` **Band 13 holds 62,896 of 64,565 differing bytes (97.4%)** — the file tail, where Go places DWARF/debug sections. The Debug build carries that material and the release build does not. **Both files are byte-identical in size**, so the space is *reused*, not appended — the sections are not truncated away, they are written differently.

`[inferred]` **Band 6's 1,375 bytes are the interesting ones.** That region is neither the PE header (band 0, 4 bytes — timestamp/checksum fields) nor the debug tail. A mid-image difference of that size is a **code or data difference**, not build metadata. **This is the one P5 result I am flagging as unresolved:** the two builds are structurally identical in the function table but differ in 1,375 bytes of image body, and determining what those bytes *are* requires disassembly that this report did not perform. Named as a residual, not smoothed over.

`[verified]` **The prior "row-for-row identical: True" printed off the Debug file alone** is now superseded: the verdict is real because the operand-acquisition check ran first and confirmed both operands present and non-empty.

---

## §3 — P1: the D91 ownership filter is not in the compiled sliver agent

**The sliver client's Ghidra TSV (`C-07`) is `named=1` and is USELESS for this question.** Recorded as an instrument limit, not an absence.

`[verified]` Against `_lead_pclntab_merlinAgent-Windows-x64.exe.tsv`, control `always-present 'a' = 23,247 / never-present = 0`:
```
'Ownership'      -> 0
'ownership'      -> 0
'Filter'         -> 2
'GetSessions'    -> 0
'IsSessionOwned' -> 0
```
`[verified]` The only `Filter` names present corpus-wide in that binary are runtime/stdlib: **`internal/runtime/gc/scan.FilterNilAVX512`** and **`net.filterAddrList`**.

**`[blocked]` P1 is NOT answerable from the available binary layer, and the named missing ingredient is precise: the sliver client's pclntab was never parsed.** The agent/dll/CLI have `_lead_pclntab_*.tsv` tables; **`sliver-client_windows-amd64.exe` does not.** Its only symbol artifact is the `named=1` Ghidra dump. Therefore the question *"is the filtered or the unfiltered query string in the compiled build?"* cannot be reached by name lookup on that binary.

`[read]` Source-side cardinality for cross-reference: `OwnershipFilter` occurs at `portfwd.go:110`, `socks.go:912`, `socks.go:1008`, `socks_test.go:454/459/462` — **six occurrences, three of them in a test file.** That is **3 production sites**, and the D91 "9 sites" figure is not reproduced by this probe. **D91 is not edited; the discrepancy is carried here by reference** and is assigned to D131 for reconciliation.

**REQUIRED NEXT PROBE (named so it is not lost):** parse the sliver client's pclntab. The technique exists and is proven — `_lead_pclntab_addr.py` already produced 15 tables. The missing act is running it against that binary, not inventing a method.

---

## §4 — P2: D85's escaping helper DOES NOT EXIST — and it was not eliminated

`[verified]` Exact-name census (not substring), against the agent's 12,333 distinct names, control `'a' = 23,247 / absent = 0`:
```
'ShellQuote' -> 0     'shellEscape' -> 0     'escapeShell' -> 0
'QuoteArg'   -> 0     'SingleQuote' -> 0
```
`[verified]` **Zero in the agent. Zero in the CLI.** The escaping helper as named by D85 is absent from the compiled artifacts.

**`[verified]` But escaping-shaped code IS present, and the actual names answer the question:**
```
syscall.appendEscapeArg                    <- the Go runtime's own Windows argument-escaping primitive
github.com/google/shlex.Split
github.com/google/shlex.NewTokenizer
github.com/google/shlex.(*Lexer).Next
github.com/google/shlex.(*Tokenizer).scanStream
github.com/google/shlex.newDefaultClassifier
github.com/Ne0nd0g/merlin-agent/v2/commands.shell
encoding/json/internal/jsonwire.appendEscapedASCII
encoding/json/internal/jsonwire.QuoteRune
net/url.escape / net/url.unescape
```

**`[inferred]` The correct reading is that D85 named a symbol that never existed.** The binary escapes with `syscall.appendEscapeArg` (runtime, Windows-specific) and *parses* with `github.com/google/shlex`. There is no Merlin-authored `ShellEscape` to link in or eliminate.

**`[verified]` The brief's collision warning was correct and the collision is confirmed:** the only `ShellEscape*` in the Go source is `shellEscapeByte = byte(0x1d) // Ctrl-]` (`ioloop.go:18`, used `ioloop.go:149`) — an interactive-terminal escape character. Different mechanism, colliding name. **`[verified]` `github.com/Ne0nd0g/merlin-agent/v2/commands.shell` is present in the agent**, so the command-execution surface itself is linked.

---

## §5 — P4: D93's path derivation — `path.Dir` is a NAME-FORM artifact, not an absence

**I got this wrong first and I am recording the wrong version.** My initial probe read `'path\.Dir' -> 0` and `'path\.Base' -> 0` and I nearly filed "path derivation absent." That was **false**: the exact-name census shows the Go runtime's filepath implementation under a different package path:
```
internal/filepathlite.Base
internal/filepathlite.Clean
internal/filepathlite.Dir          <- filepath.Dir's real implementation
internal/filepathlite.IsAbs
internal/filepathlite.VolumeName
internal/filepathlite.volumeNameLen
internal/filepathlite.pathHasPrefixFold
internal/filepathlite.postClean
internal/filepathlite.replaceStringByte
os.Executable                      <- present, exactly 1
main.getArgsFromStdIn
main.getArgsFromStdIn.deferwrap1
```
`[verified]` `os.Executable` occurs **exactly once**; `internal/filepathlite.Dir` is present. **`Split` has 8 hits but `Split("bin")` was not found as a source literal in the sliver checkout (0 hits, with the control `Split` → 5,453 corpus-wide).** Two readings remain live and are NOT resolved here: the literal is absent from this checkout, or the source and binary are at different commits.

`[blocked]` **D93's six derived directories and R-93.4 are not answered.** Named missing ingredient: the **compiled literal strings** from `sliver-client_windows-amd64.exe` were never extracted — extracting them requires the string surface of that binary, which was never dumped. Source side offers 33 `os.Executable()` sites but the derivation expression itself remains unidentified.

**`[verified]` `main.*` is FIVE names, not eight.** My substring probe returned `8`; the exact census returns:
```
main.getArgsFromStdIn
main.getArgsFromStdIn.deferwrap1
main.main
main.main.gowrap1
main.usage
```
**`main.Magic` DOES NOT EXIST in the agent, the CLI, or the DLL.** This answers the standing `_lead_magic_probe.py` question: the `Magic` export is a **PE export-table** surface (`merlin.def`), not a Go `main` package symbol. The only `Magics` in the agent is `golang.org/x/crypto/ssh.(*handshakeMagics).write` — an SSH handshake type, unrelated.

---

## §6 — P3: the concurrency surface, and what D89 D-2 can and cannot be answered from

`[verified]` The agent's own locking surface, exact names — **eight `(*T).Lock`/`(*T).Unlock` pairs authored by Merlin**, plus the repository:
```
agent/memory.(*Repository).Lock            / .Unlock
clients/http.(*Client).Lock                / .Unlock
clients/memory.(*Repository).Lock          / .Unlock
clients/smb.(*Client).Lock                 / .Unlock
clients/tcp.(*Client).Lock                 / .Unlock
clients/udp.(*Client).Lock                 / .Unlock
p2p.(*Link).Lock                           / .Unlock
p2p/memory.(*Repository).Lock              / .Unlock
crypto/tls.(*halfConn).Lock                / .Unlock      <- stdlib
```
`[verified]` `ToMap` occurs **0 times** in the agent and the DLL, and `GetToMap`, `addCommandsFromFile` also 0. **`[blocked]` D89's `ToMap` callers cannot be enumerated from this binary layer**, because the identifier is not present under that name in either artifact. Named missing ingredient: the source-lane spelling of the method (D89's own text) is required before the binary can be searched — searching a binary for a name the source may spell differently is the substring-probe defect in its purest form.

`[inferred]` **What the binary layer DOES contribute to D89 D-2:** ten lock/unlock pairs are linked and named, and `agent/memory.(*Repository)` exposes `Lock`/`Unlock` as **separate exported methods** rather than internal critical sections — so callers are responsible for pairing them. That is a structural fact about the concurrency design and is recorded as an observation, not as an answer to D-2.

`[verified]` **The package delta the objective's D128 asked for, settled exactly:**
```
merlinAgent-Windows-x64.exe   distinct names 12,333   merlin-agent/v2 names 443
merlin.x64.dll                distinct names 12,313   merlin-agent/v2 names 443
merlinCLI-Windows-x64.exe     distinct names 15,855   merlin-agent/v2 names   0
agent set vs DLL set IDENTICAL : True
```
**`[verified]` The CLI carries ZERO `merlin-agent/v2` symbols; the agent and the DLL carry an identical set of 443.** The CLI is larger by distinct name count (15,855 vs 12,333) while containing none of the agent package — a client/server split, not a scale difference.

---

## §7 — P6: D82/D77 `bare?` — blocked, by reference only

`[blocked]` **MISSING TOOLCHAIN.** No Ruby/`gem`/`bundle` on this host; every Rex/MSF runtime claim is `[inferred]` at the claim. **Not re-derived here.** Cross-referenced to **D127 §B-2**, which re-derived the absence with a **positive control in the same pass** (`cmd`/`python`/`dotnet`/`node`/`java`/`7z` all PRESENT). D127's taxonomy is the correct frame: **missing TOOLCHAIN is fixable by acquiring the tool; missing INVOCATION is not.**

---

## §8 — The instrument-failure register for this report

Every one of these printed a plausible number, and none of them threw.

| # | defect | how it was caught |
|---|---|---|
| I1 | **null-operand byte read** — indexed 68,779,968 into a 64-byte array, printed `0x17 = kEncodedHeader? False` | I re-seeked and checked bytes-read before the verdict |
| I2 | **guessed binary paths** — both P5 operands MISSING at `02_BINARIES\merlin\` | operand check printed `MISSING` twice, aborting before any diff |
| I3 | **`path.Dir` read as 0** and nearly filed as absence | exact-name census found `internal/filepathlite.Dir` |
| I4 | `%` operator on a format string — `Cannot convert "--- {0} ---" to Int32`, 7 times | failed loudly; no probe result was taken from it |
| I5 | **substring count vs name count** — `main.*` read 8, actual named surface is 5 | exact-name census |
| I6 | **control measuring the wrong thing** — my BE read of D127's field returned 0, not 17 orders of magnitude | recognised as a different field base, so it cannot refute the claim |
| I7 | `_lead_magic_probe.py` question answered indirectly — `Magic` is not a Go symbol | exact-name census of `main.*` |

**The through-line: five of seven were caught by an operand-acquisition or control check running BEFORE the verdict.** That is the only reason this report contains no fabricated absence.

---

## §9 — Residuals

**R-130.1 — the sliver client's pclntab was never parsed.** `[blocked]` Named ingredient: run `_lead_pclntab_addr.py` against `sliver-client_windows-amd64.exe`. This unblocks P1 (D91 ownership filter) AND D93's literal recovery in one act. **Highest-value residual in this report.**
**R-130.2 — D127's decisive byte `0x17` is Lead-unverified.** My control measures a different field base than the claim; the three arithmetic/identity checks ARE confirmed. Resolution requires reading the 7z StartHeader field layout the lane actually used.
**R-130.3 — band 6 (offset 6,291,456, 1,375 differing bytes) is unexplained.** Neither PE header nor debug tail. Requires disassembly; not performed.
**R-130.4 — `ToMap` (D89) is unfindable under that spelling in either agent artifact.** Requires the source-lane method name.
**R-130.5 — D91 9-vs-3 site discrepancy** is carried here and assigned to D131.
**R-130.6 — the sliver source/binary commit relationship is unestablished.** `Split("bin")` 0 hits in source may mean a different commit rather than absence.

---

## §10 — Instruments

**I1** `_d130_p5_reldbg.ps1` — row identity, both operands, operand-checked first.
**I2** `_d130_p5_bytes.ps1` — SHA-256, chunked byte diff, 1 MB band histogram, enumerated paths.
**I3** `_d130_p1234.ps1` — P1–P4 substring probes with a control pair (`'a'` must be >0, sentinel must be 0) per file.
**I4** `_d130_names.ps1` — exact-name census over pclntab TSVs.
**I5** `_lead_pclntab_addr.py` (existing) — the pclntab parser that produced the 15 tables; its absence against the sliver binary is R-130.1.

**End of D130.**
