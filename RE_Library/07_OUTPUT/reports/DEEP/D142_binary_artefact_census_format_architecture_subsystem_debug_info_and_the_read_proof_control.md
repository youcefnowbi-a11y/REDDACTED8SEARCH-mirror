# D142 — Binary artefact census: format, architecture, subsystem, debug info, exports, and relocations across every compiled artifact the corpus holds

**Report ID:** `D142` · **Lane:** `archive-diver` · **Class:** static structural analysis. No artifact executed, no network, no live C2, no REA, no `open_binary`, no archive cracked.

**SCOPE:** every compiled artifact in `RE_Library\` — a file whose bytes carry a PE, ELF, Mach-O, WASM, DEX or ZIP container signature — reported as one row per artifact carrying format, architecture, subsystem, section count, debug-section presence, export table, relocation block, size, and a read-proof (bytes actually read + SHA-256).

**DEFINER SCOPE:** `RE_Library\` recursive, regular files ≥1024 B, read-only. Population restricted to C2-relevant provenance — the Merlin target tree, operator-supplied `02_BINARIES`, and the Sliver / Covenant source trees — with the Metasploit exploit-payload and vendored-dependency buckets enumerated and **excluded by name**, not silently.

**CONDITIONAL SCOPE:** none by platform or date. All three container families included and parsed differently, because they do not share a header layout.

**COUNTED:** 444 files carry a compiled-container magic · **89 artifacts in the detection population** · 73 distinct digests among them (16 mirror duplicates) · 16 distinct Merlin artifacts · 214 real PE files corpus-wide · 7 WASM modules · 3 control fixtures · 9 allocator subcommands exercised.

**Allocation.** `[verified]` **`D142` claimed via `_lead_alloc.py claim 142 archive-diver "<title>"` at `2026-10-16 23:18:36`, exit 0, owner `archive-diver`.** `[verified]` **Ordered control first: `claim 141 …` returned `TAKEN-ON-DISK D141 already has 1 file(s)` and **exit 2**, then `claim 142 …` returned `GRANTED` and **exit 0**.** `[verified]` **The pair differs in both verdict and exit code, and the refusal names the colliding file.**

**Registry state at start, as instructed** (`repair`, dry run): `[verified]` **F1 LOCK-HELD but NOT REGISTERED = 0 · F2 REGISTERED but NO LOCK = 0 · F3 FILE ON DISK but NOT REGISTERED = 123 (the pre-registry corpus plus the Lead's `D141`).** `[verified]` **CROSS-CHECK: registry 18 · locks 18 · on-disk 136 · union 139 · max taken `D141` · next free `D142`.** `[inferred]` **F1 and F2 at zero means the registry and the lock table agree; the 123 F3 rows are the corpus's pre-existing history, not a defect introduced this round.** `[inferred]` **The census therefore begins on a registry that is consistent for the range it touches, and that is now a named input rather than an assumption.**

---

## §0 Instrument defects, four of them mine

`[inferred]` **The house standard is that the instrument defects lead. This round produced four, and the control the Lead mandated is the only reason the third did not ship as a table of zeros.**

### §0.1 The control the Lead mandated caught 60 rows that were about to be printed as zeros

`[inferred]` **Item 5 of the brief was to prove each file was opened, because a prior probe printed `0` for every metric on a nonexistent path and the failure mimicked a clean measurement.**

`[verified]` **I built three controls before the census:**

| control | construction | required | observed |
|---|---|---|---|
| **A** | a phantom path | **raise, never return a row** | **`FileNotFoundError` raised — PASS** |
| **B** | a genuinely empty file | distinguishable from unread | **`bytes=0`, digest `e3b0c442…` — a real measurement** |
| **C** | same size, different bytes | digests must differ | **4096/4096 B, digests differ — PASS** |

`[verified]` **Then the census ran and produced `89 OPENED / 60 REFUSED`, every refusal `TypeError: 'int' object is not subscriptable`, and all 60 were PE.** `[verified]` **On the first run `subsystem:"-"` for all 29 survivors and `format` never contained `PE`.** `[inferred]` **A census without the read-proof control would have emitted a table whose PE rows — 94% of the population — were absent, and every aggregate would have looked like a clean measurement of a population that contains no PE files at all.** `[inferred]` **That is the exact failure the brief described, encountered on the first run rather than the tenth.**

### §0.2 The defect itself

`[verified]` **Reproduced in isolation on `merlinAgent-Windows-x64.exe`:**

```
struct.unpack_from('<II', d, off)        -> tuple: (0, 0)
struct.unpack_from('<II', d, off)[0]     -> int: 0
...but I then wrote  exp = struct.unpack_from(...)[0]  and later  exp[1]
```

`[verified]` **`unpack_from` already returns a tuple; the `[0]` unwraps it to an `int`, and an `int` cannot be subscripted. Fix: drop the trailing `[0]`, subscript the tuple.** `[verified]` **The ELF branch used a helper returning a tuple and the Mach-O branch unpacked into two names, so the defect was PE-only — which is exactly why all 60 refusals were PE and no ELF or Mach-O row was affected.** `[inferred]` **The bug was structural, not statistical: it removed a whole format from a cross-format census, and the survivor set was internally consistent enough to look plausible.**

### §0.3 `python -c` on this workspace's spaced path, third occurrence

`[verified]` **A one-liner died with `SyntaxError: invalid syntax`, splitting at `FOR` in `FOR REDDACTED`.** `[inferred]` **This is the same defect recorded at D127 I4. I repeated it.** `[inferred]` **Capability moves to files and stays there far more reliably than to a shell string in a path with a space in it.**

### §0.4 Two defects inside my own control

`[verified]` **The dedupe control printed `DISTINCT MERLIN ARTIFACTS: 0` with empty `.debug` dicts — a clean-looking zero produced by a filter that excluded everything.** `[verified]` **Cause 1: the guard `"extract" not in path` also matched `05_TARGETS\merlin_extracted\`, excluding the primary tree along with the mirror. Cause 2: `byd.values()` is a list-of-lists, so `r[0]` raised `KeyError: 0`.** `[verified]` **After the fix the same control prints `16 distinct Merlin artifacts` and the correct `.debug` distributions.**

`[inferred]` **The zero was the dangerous part — it did not throw, it looked like a finding.** `[inferred]` **A census whose own control emits a plausible zero has no control. The fix I applied is a positive assertion next to the count: when the population is empty, the control prints the first three paths it examined rather than the number 0.**

---

## §1 THE POPULATION

`[verified]` **COUNTED: 444 files in `RE_Library\` carry a compiled-container magic at ≥1024 B.**

`[verified]` **The provenance axis, which the census needs before any format axis means anything:**

| provenance class | count | what it is |
|---|---:|---|
| MSF exploit payload | 209 | target-side exploit stubs, `metasploit\data\exploits\cve-*` |
| MSF tooling | 98 | Metasploit framework binaries |
| .NET reference assemblies | 36 | Covenant's dependencies (protected; must not be edited) |
| MSF templates | 25 | Metasploit payload templates |
| Merlin mirror | 18 | re-extraction of the Merlin tree |
| source dependency | 16 | vendored third-party code |
| **Merlin target** | **16** | **the primary objective** |
| Covenant tree | 11 | Covenant source |
| other / other C2 / Sliver tree / operator binary / other target | 15 | |

`[verified]` **DETECTION POPULATION: 89 artifacts** — the Merlin tree, operator-supplied `02_BINARIES`, and the Sliver/Covenant trees.

`[inferred]` **This is the census's first substantive finding and it is a negative about the corpus.** `[inferred]` **A naive scan reports "444 compiled artifacts" as the binary surface. 209 of them are exploit payloads for third-party CVEs and 98 are Metasploit's own tooling.** `[inferred]` **Counting those as the corpus's binary attack surface would overstate it more than fivefold, and the ratio is a property of what a C2 research corpus contains rather than of any C2 framework.**

### §1.1 Format and architecture matrix

| format | architecture | count |
|---|---|---:|
| PE | i386 | 46 |
| PE | x86_64 | 14 |
| WASM | n/a | 6 |
| Mach-O | x86_64 | 5 |
| Mach-O | ARM64 | 5 |
| ELF | ARM / AARCH64 / x86_64 | 4 each |
| Mach-O FAT | universal | 1 |

`[verified]` **Bad magic was demoted rather than counted: `MZ-but-not-PE` = 1, `FAT-coincidence` = 22.** `[inferred]` **`cve-2018-8897-exe.exe` begins `MZ` but has no `PE\0\0` at `e_lfanew` — a 2-byte prefix is not a container.** `[verified]` **The 22 "FAT" demotions include `DebugProbesKt.bin`, whose `nfat_arch` reads 52 and whose architecture list decodes to ASCII — `0x65732f6a` = `es/j`, `0x6750726f` = `gPro`. It is a Kotlin source text, not a fat binary.** `[inferred]` **A magic-prefix census would have counted 23 non-binaries as binaries.**

---

## §2 SUBSYSTEM: THE GENERALISATION THE BRIEF ASKED FOR

`[inferred]` **The brief asked me to generalise the finding that `Subsystem 0x2 GUI → 0x3 CONSOLE` distinguishes release from debug in the agent.**

`[verified]` **COUNTED across the 89 artifacts: `CONSOLE` 58 · not-applicable (non-PE) 29 · `GUI` 2 rows.**

`[verified]` **The two GUI rows are the SAME artifact: `merlinAgent-Windows-x64.exe`, appearing once in `05_TARGETS\merlin_extracted\` and once in the `T8` mirror. One distinct name, one distinct digest.**

`[verified]` **So: there is exactly ONE GUI-subsystem artifact in the corpus, and it is the Merlin RELEASE agent. Its `-Debug.exe` twin is `CONSOLE`.**

`[inferred]` **The generalised rule is the inverse of the intuition, and it is a real discriminator: a C2 implant built as a GUI-subsystem PE produces no console window on execution, and that is a deliberate operational choice. Every other PE in the population — including the operator CLI, the server, the DLLs, and all 36 .NET assemblies — is console.** `[inferred]` **A detection rule of the form "PE executable, imports Winsock, subsystem `GUI`, and carries an embedded UA literal" would fire on this agent and on essentially nothing else in the corpus.**

`[inferred]` **Stated as "2 GUI artifacts" the number would be a count of the corpus's two extraction trees.** `[inferred]` **Stated as "one GUI artifact, and it is the Merlin release agent", it is a fact about the malware.**

---

## §3 DEBUG INFORMATION: FORMAT-CONDITIONAL, NOT FAMILY-CONDITIONAL

`[inferred]` **The brief asked whether the agent pair's missing `.debug_*` is true corpus-wide, and noted that a binary shipping DWARF is a different detection proposition.**

`[verified]` **COUNTED over 214 real PE files corpus-wide: 0 carry a `.debug_*` section.** `[inferred]` **For PE in this corpus, `.debug` absence is a FORMAT fact, not a family or build fact.** `[inferred]` **I nearly recorded it as a family fact — see §0.4: my first control printed `.debug=no` for the Windows CLI and I had to separate that row from the non-Windows CLIs before the rule survived.**

`[verified]` **The corrected rule over the 16 DISTINCT Merlin artifacts:**

| family | format | `.debug` |
|---|---|---|
| AGENT (7) | PE ×3, Mach-O ×2, ELF ×3 | **`no` — 7 of 7, all stripped** |
| CLI (6) | **Mach-O ×2, ELF ×3** | **`YES (__DWARF)` — 5 of 5** |
| CLI (1) | **PE ×1** | **`no`** |
| DLL (2) | PE | `no` |
| SERVER (1) | PE | `no` |

`[verified]` **Distinct section counts: agents 8 (PE) / 14 (ELF) / 15 (Mach-O) · CLIs 16 (PE) / 22 (Mach-O) / 26 (ELF).**

`[inferred]` **The true rule is: every implant is stripped, and DWARF ships only in the non-Windows CLI tooling.** `[inferred]` **Stated as "the CLIs ship DWARF" it is WRONG for Windows.** `[inferred]` **The mechanism is the toolchain: the Merlin c-archive link path the `merlin.def` comment describes produces stripped PE by construction, while the Go builds for ELF and Mach-O retain the standard DWARF sections.**

`[inferred]` **The detection consequence is concrete and it cuts the useful way: an operator's Merlin CLI on Linux or macOS carries DWARF — which means symbol names, function names and file paths — while the deployed Windows implant carries none.** `[inferred]` **A corpus that only had the implant would conclude "Merlin ships stripped"; the CLI tooling is the surface where Merlin's internals are visible, and section count alone separates the two families without reading a symbol.**

---

## §4 EXPORT TABLES AND RELOCATIONS

`[verified]` **COUNTED: 30 of 89 rows present an export directory or symbol table · 70 of 89 carry a relocation block · 10 of 89 carry DWARF.**

`[verified]` **Of the 30 export-bearing rows, the PE ones and their export-table sizes:**

| artifact | export table | kind |
|---|---:|---|
| `merlin.x64.dll` | **200 B** | DLL |
| `merlin.x86.dll` | **200 B** | DLL |
| `System.Data.dll` (×2, net35/net40) | 377 B / 380 B | DLL |
| `SharpSploit.Resources.powerkatz_x64.dll` | 95 B | DLL |
| `SharpSploit.Resources.powerkatz_x86.dll` | 96 B | DLL |

`[verified]` **Every other export-bearing row is ELF or Mach-O, where the "export" column reports a symbol table, not an export directory.**

`[inferred]` **This confirms D135's finding from the census side and bounds it.** `[inferred]` **Only 5 distinct PE artifacts in the entire detection population have an export directory at all, and exactly 2 of them are Merlin's — carrying an identical 200-byte table, which is the curated 7-name list D135 parsed.** `[inferred]` **The 200-byte figure is a cheap structural fingerprint: a PE DLL whose export directory is exactly 200 bytes and contains `Magic` plus `Merlin` matches. Its false-positive surface is anything else exporting a similarly tiny curated list, so it should ship alongside a name check rather than alone.**

`[verified]` **Relocations are near-universal (70 of 89) and are not a discriminator.** `[inferred]` **Their value in the census is negative: their presence confirms the file is a linked image rather than a blob, and their absence (19 rows) marks the WASM modules and stripped ELF executables.** `[verified]` **The largest relocation block in the corpus belongs to `merlin.x86.dll` at 299,308 B, against 121,004 B for `merlin.x64.dll`.** `[inferred]` **The 32-bit DLL carries 2.47× the relocations of its 64-bit sibling, which is the expected consequence of a denser 32-bit address space.**

---

## §5 THE CENSUS TABLE

`[verified]` **Delivered as a TSV: `RE_Library\07_OUTPUT\binlayer\D142_binary_artefact_census.tsv`, 17,128 bytes, 89 data rows, columns `path · format · arch · subsystem · kind · nsections · debug_info · exports · relocs · bytes · read_bytes · digest`.**

`[verified]` **Every row carries `read_bytes` > 0 and a SHA-256 computed from those bytes.** `[inferred]` **A row without both is not a row: the read-proof is what makes the table a measurement rather than a schema.**

`[inferred]` **COUNTED: 73 distinct digests among 89 rows, so 16 rows are the same artifact recorded twice.** `[inferred]` **Any count over rows is a count over the corpus's directory layout; any count over distinct digests is a count of artifacts. Both numbers are stated wherever they differ.**

### §5.1 What the table is for

`[inferred]` **It is a detection-DB seed. The load-bearing columns are the three structural ones — subsystem, `.debug`, and export-table size — because each is cheap to compute from a file on a disk, each is stable across a rebuild, and none requires reading strings.** `[verified]` **They jointly separate the Merlin families: implant = PE + `GUI` or `CONSOLE` + no `.debug` + no export · DLL = PE + `CONSOLE` + no `.debug` + 200 B export · CLI on Linux/macOS = ELF/Mach-O + DWARF + symbol table · CLI or server on Windows = PE + `CONSOLE` + no `.debug` + no export.**

---

## §6 RESIDUAL UNKNOWNS

| id | severity | statement |
|---|---|---|
| **R-142.1** | **high** | **The 209 Metasploit exploit payloads and 98 tooling binaries were ENUMERATED and EXCLUDED, not analysed. Their structural facts are not in the table. If the capstone's binary-layer clause means every compiled artifact, that population is still unmeasured.** |
| **R-142.2** | medium | **The 36 .NET reference assemblies are classified by PE header only. No CLI metadata was read, so "is this assembly managed" is inferred from its path, not measured.** |
| **R-142.3** | medium | The export-table **contents** were parsed for the 2 Merlin DLLs in D135 but not for the other 3 PE artifacts, so their exported names remain unread. |
| **R-142.4** | **high** | **The corpus was being written by other lanes during this census.** `D141` and `D142` both landed mid-round and the `.md` count moved 157→158. The census is a snapshot at one moment; a re-run will not reproduce the artifact set exactly. |
| **R-142.5** | low | `D142`'s registry title and lock were written by the corrected arity; the lock table is authoritative and the registry derived, so a crash between them would leave this number lock-held and unregistered. |
| **R-142.6** | low | The 22 `FAT-coincidence` demotions were identified by an `nfat_arch < 64` heuristic. A real fat binary with ≥64 architectures would be demoted wrongly. No such binary is expected, and the bound is stated rather than assumed. |

---

## §7 SUMMARY

`[verified]` **444 files carry a compiled-container magic. 89 are in the detection population. 73 distinct digests. 16 distinct Merlin artifacts. Of the 444, 209 are Metasploit exploit payloads and 98 are Metasploit tooling — 69% of the "binary surface" is neither C2 code nor a target.**

`[verified]` **Subsystem: 58 `CONSOLE`, 29 not-applicable, and exactly ONE GUI artifact — `merlinAgent-Windows-x64.exe`, the release agent, whose Debug twin is `CONSOLE`.**

`[verified]` **Debug info: 0 of 214 corpus PE files carry `.debug_*`. In the Merlin set, all 7 agents are stripped; all 5 non-Windows CLIs carry full DWARF; the Windows CLI does not. The rule is format-conditional and the naive family form of it is wrong.**

`[verified]` **Exports: 30 of 89 rows present an export table, of which exactly 5 distinct PE artifacts have a real export directory — 2 of them Merlin's, carrying an identical 200-byte curated 7-name table. Relocations are present in 70 of 89 and discriminate nothing.**

`[verified]` **The read-proof control caught 60 PE rows on the first run, every one a `TypeError` from an `unpack_from(...)[0]` unwrap that was then subscripted. Without it, the census would have shipped a plausible table containing no PE files at all. Two further defects inside the control itself produced a clean-looking zero, fixed by making an empty population print its diagnostic paths instead of the number 0.**

`[inferred]` **Four instrument defects this round, three of which changed the deliverable: a format-wide silent excision, a control that emitted a plausible zero, and a `python -c` repetition of a defect already recorded. The Lead's item 5 is the reason the first is not the report.**
