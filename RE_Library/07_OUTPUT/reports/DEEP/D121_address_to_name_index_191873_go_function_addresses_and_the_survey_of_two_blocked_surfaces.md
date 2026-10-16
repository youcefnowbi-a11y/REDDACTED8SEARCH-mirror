# D121 — The address→name index: 191,873 Go function addresses resolved across 11 binaries, and the survey of what two blocked surfaces actually hide

**SCOPE:** `05_TARGETS\merlin_extracted\data\bin\` (10 cross-platform Go binaries) · `02_BINARIES\sliver\sliver-client_windows-amd64.exe` · `01_SOURCE_c2\covenant\` · `02_BINARIES\merlin\merlinServer-Windows-x64.7z` · `07_OUTPUT\binlayer\`
**DEFINER SCOPE:** every count below states the set it was taken over, in the same block as the number.
**COUNTED:** 11 binaries parsed · 11 TSVs emitted · 191,873 FUNC rows · 15060 text files searched (T5 password sweep) · 32 files mentioning the archive.
**Line-count convention:** LF count over `[IO.File]::ReadAllText`, final unterminated line excluded.
**Tags:** `[verified]` instrument run, output shown · `[read]` quoted from an artifact · `[inferred]` reasoning · `[absence]` zero **with a positive control shown** · `[blocked]` actively prevented, mechanism documented.
**Discipline:** **no corpus binary was executed.** No network. No live C2. **No Ghidra run.** No archive cracking attempted. Every figure is a byte or metadata read.
**Write scope:** `D121_*.md` + 11 `_d121_addr2name_*.tsv` in `binlayer\`. All scripts staged in `%TEMP%`.

---

## §0 Allocation method and its positive control (Rule 30)

`[verified]` **ENUMERATION, not assumption.** **SCOPE:** all `*.md` in `07_OUTPUT\reports\DEEP`. **COUNTED: 137** — independently reproducing the Lead's figure.

`[verified]` **Probe:** filename matched against `^D(\d{1,3})[_\.]`, grouped by integer. **D121 → 0 matches.**

| control | expected | observed | verdict |
|---|---|---|---|
| D110 | occupied | **1** | ✓ probe detects occupancy |
| D121 | free | **0** | ✓ available |
| D109 | failed allocation, not a gap | **0** | ✓ consistent with Lead |
| D1000 | cannot exist (4 digits) | **0** | ✓ probe does not over-match |

`[verified]` **Absent numbers across D1–D121: 27, 109, 116, 121.** `[inferred]` **A control on a KNOWN-OCCUPIED number (D110 → 1) is what makes the D121 zero admissible. Without it, "0 matches" and "broken regex" are the same output.**

`[inferred]` **NOTE ON D116:** D112 closed by naming `D116` as next free. **D116 is still unoccupied.** The Lead's instruction placed this report at D121 and reserved D116, so **D116 remains unclaimed and is flagged rather than silently reconciled.**

### §0.1 POST-HOC CORRECTION — THREE REPORTS SHARE D121

`[verified]` **This report is one of THREE files now carrying the `D121` prefix.** **COUNTED at 22:14, after all writers finished:**

| file | bytes | mtime |
|---|---:|---|
| `D121_convergence_census_enum_bool_state_collapse_runtime_identifier_ordinal_divergence_and_compiler_file_selection.md` | 29,796 | **22:10:39** |
| `D121_android_axml_res_value_column_identity_ahmyth_absence_and_c2_substitution.md` | 29,418 | **22:10:45** |
| `D121_address_to_name_index_191873_go_function_addresses_and_the_survey_of_two_blocked_surfaces.md` (this report) | 31,311 | **22:11:35** |

`[inferred]` **ALL THREE WRITERS RAN RULE 30 AND ALL THREE PASSED.** `[inferred]` **Each measured the same population — 137 `.md` files — and each found `D121` absent.** `[read]` The convergence report records: *"Result at allocation time: 137 `.md` files, 117 distinct D-numbers, range `1..120`. `D121` absent from the map ⇒ free."* `[read]` The android report records: *"`^D121(?!\d)` → 0 files. `^D122(?!\d)` → 0 files"* with negative controls `D114` → 1 and `D100` → 1, and adds **"Recheck immediately before commit. D121 free, D122 free. Committed as `D121`."**

`[inferred]` **Every control was sound and every conclusion was correct at the instant it was measured. All three were written within 56 seconds of each other.**

`[inferred]` **THE FINDING: Rule 30's control establishes that a number is free NOW. It cannot establish that a number is free WHEN THE WORK FINISHES.** `[inferred]` **A read-then-write allocation in which one allocator hands the same number to several lanes concurrently has no mutual exclusion across the WORK window, and no amount of pre-commit rechecking closes it — the android lane rechecked immediately before commit and still collided, because its peer landed in the interval between the recheck and the write.**

`[verified]` **This is not a new defect. Two older sites exist and were found by the same census:**

| number | files | character |
|---|---:|---|
| **`D11`** | **5** | historical — `havoc_native_win32`, `merlin_binaries`, `mythic_crypto_postresponse`, `pupy_transport_crypto`, `sliver_rpc_core` |
| **`D12`** | **2** | historical — `havoc_dispatch`, `sliver_aitools` |
| **`D121`** | **3** | this round, 56-second window |

`[inferred]` **`D11` carrying five files shows the defect is long-standing and has now recurred with a control in place. The control did not fail; the CONTROL'S SCOPE was insufficient. A point-in-time census is the wrong instrument for an allocation that must hold for the duration of a write.**

`[inferred]` **Stale-by-one-window correction to §0 above:** `[inferred]` **the D116 note at §0 says D116 is unoccupied. That was true when measured. `D116_d96_denominator_merlin_archive_open_and_line_vs_row_adjudications.md` (27,982 B) was written at 22:04:32 — six minutes before the D121 triple.** `[inferred]` **The sentence is preserved rather than edited so the observation time is recoverable; it is superseded by this subsection.**

`[verified]` **WHAT WAS NOT DONE.** No file was renamed. **Not this report and not either peer's.** `[inferred]` **Renaming unilaterally would create a fourth collision and desynchronise the Lead's allocation records, and the other two reports' internal `Report ID: D121` declarations are correct under their own reading. The collision is surfaced to the allocator, which is the only party that can resolve it.** `[inferred]` **The remedy belongs upstream: serialise allocation through the task board, or allocate by claim-then-verify against a written reservation rather than by census.**

`[verified]` **Recommended resolution if the allocator confirms it:** this report renumbers to the next free number at the allocator's direction, since it is the newest of the three and the only one whose content is completely self-contained.**

---

## §1 T1 — THE ADDRESS→NAME INDEX

### §1.1 What was built

`[verified]` **11 TSVs, one per binary, in `07_OUTPUT\binlayer\`, in the `_d96_pclntab.tsv` convention extended with the image-basis note.** **COUNTED: 191,873 FUNC rows.**

`[verified]` **Row format:** `FUNC<TAB>0x{entryoff:X}<TAB>{name}<TAB>0x{funcoff:X}`, preceded by `# program` / `# source` / `# kind` / `# NOTE` and followed by `# SUMMARY`.

`[verified]` **Field-integrity check — COUNTED: 191,873 FUNC rows examined; rows NOT exactly 4 tab-delimited fields: 0.** `[inferred]` **This matters because a Go symbol may contain spaces and semicolons** — e.g. `UnwrapNew[go.shape.interface { BlockSize() int; Reset(); ... }].func1` — **and a separator other than TAB would have split those rows.**

### §1.2 Per-binary results

`[verified]` **All eleven parsed. No binary was skipped.**

| # | binary | kind | pclntab base | functab | layout | entries | resolved | unique | collisions | TSV lines |
|---:|---|---|---|---|---|---:|---:|---:|---:|---:|
| 1 | `merlinAgent-Darwin-arm64` | macho | `0x500B40` | `0x738238` | u64 | 12,052 | 12,052 | 11,881 | 171 | 12,057 |
| 2 | `merlinAgent-Darwin-x64` | macho | `0x5D9460` | `0x8378A0` | u64 | 12,167 | 12,167 | 11,984 | 183 | 12,172 |
| 3 | `merlinAgent-Linux-arm` | elf | `0x64A1E0` | `0x863288` | **u32** | 12,037 | 12,037 | 11,885 | 152 | 12,042 |
| 4 | `merlinAgent-Linux-arm64` | elf | `0x526960` | `0x75FF28` | u64 | 11,970 | 11,970 | 11,795 | 175 | 11,975 |
| 5 | `merlinAgent-Linux-x64` | elf | `0x5F0C20` | `0x8503C8` | u64 | 12,062 | 12,062 | 11,877 | 185 | 12,067 |
| 6 | `merlinCLI-Darwin-arm64` | macho | `0x5B3440` | `0x82D9A0` | u64 | 16,056 | 16,056 | 15,838 | 218 | 16,061 |
| 7 | `merlinCLI-Darwin-x64` | macho | `0x688200` | `0x928C10` | u64 | 16,135 | 16,135 | 15,911 | 224 | 16,140 |
| 8 | `merlinCLI-Linux-arm` | elf | `0x6E67E0` | `0x939550` | **u32** | 15,939 | 15,939 | 15,740 | 199 | 15,944 |
| 9 | `merlinCLI-Linux-arm64` | elf | `0x5D6820` | `0x84EF10` | u64 | 15,863 | 15,863 | 15,640 | 223 | 15,868 |
| 10 | `merlinCLI-Linux-x64` | elf | `0x69BDA0` | `0x93A368` | u64 | 15,935 | 15,935 | 15,705 | 230 | 15,940 |
| 11 | `sliver-client_windows-amd64.exe` | pe | `0x269DDE0` | `0x2F86498` | u64 | 51,657 | 51,657 | 51,208 | 449 | 51,662 |

`[verified]` **TOTALS: 191,873 entries resolved · 189,464 unique names · 2,409 collisions.**

### §1.3 THE EXTERNAL CONTROL — an independently-built parser agrees exactly

`[verified]` **The Sliver PE was parsed by D96's separate script at an earlier date and its TSV's own `# SUMMARY` line reads `total=51657 unique=51208`.**

`[verified]` **D121's independently-built reader on the same artifact: `entries=51657 resolved=51657 unique=51208`.**

`[inferred]` **Two parsers, written in different rounds, agree to the unit on both the total and the unique count.** `[inferred]` **This is the strongest available external validation of the instrument and it was not constructed for this purpose — it was an artifact of choosing the Sliver PE as an eleventh target. A control that happens to exist is worth more than one arranged.**

`[inferred]` **It also confirms the `u64` path, the `funcoff` dereference, and the name-offset arithmetic simultaneously, since a defect in any of the three would shift both numbers.**

---

## §2 T1 — END-TO-END RESOLUTION PROOF

`[verified]` **Target named by the Lead: `agent.(*Agent).SetComms`.** Resolved from the emitted TSVs with no further parsing:

| binary | TSV row |
|---|---|
| `merlinAgent-Darwin-arm64` | `FUNC	0x198580	github.com/Ne0nd0g/merlin-agent/v2/agent.(*Agent).SetComms	0x79B80` |
| `merlinAgent-Linux-x64` | `FUNC	0x1CD520	github.com/Ne0nd0g/merlin-agent/v2/agent.(*Agent).SetComms	0x79F38` |

`[verified]` **Three rows match `SetComms` in each agent, and the other two are distinct functions, not duplicates:** `agent/memory.(*Repository).SetComms` and its `.deferwrap1`.

`[inferred]` **The end-to-end property this demonstrates:** a name printed in a report can now be resolved to a byte offset in a specific artifact, and a byte offset can be resolved back to a name. `[inferred]` **Identity is now joinable in both directions — the thing D112 named as the bound on its own lane.**

---

## §3 T1 — THE LIMITATION, DEMONSTRATED RATHER THAN ASSERTED

`[verified]` **`entryoff` is a RAW/BYTE OFFSET inside the image. It is NOT a runtime VA, and it is NOT derivable by adding the image base.**

`[verified]` **Demonstration on the Sliver PE — section table read directly:**

| section | VirtAddr | RawPtr | **delta** |
|---|---:|---:|---:|
| `.text` | `0x1000` | `0x600` | **`0xA00`** |
| `.rdata` | `0x17B1000` | `0x17AFA00` | **`0x1600`** |
| `.data` | `0x3C43000` | `0x3C40E00` | **`0x2200`** |
| `.pdata` | `0x5E4E000` | `0x3DD7400` | **`0x2076C00`** |
| `.xdata` | `0x5EC6000` | `0x3E4F000` | **`0x2077000`** |

`[verified]` **`ImageBase = 0x140000000`.** `[verified]` **A mid-table function, `gvisor.dev/gvisor/pkg/tcpip.(*ErrBadLocalAddress).StateTypeName`, sits at `entryoff 0x855C20`; `0x855C20 + 0x140000000 = 0x140855C20`, and that value is WRONG** because the containing section's delta is not zero.

`[verified]` **The correct mapping is `VA = ImageBase + VirtAddr(section) + (entryoff − RawPtr(section))`, applied PER SECTION.**

`[inferred]` **THE TRAP: the delta spans six orders of magnitude between sections — `0xA00` for `.text` versus `0x2076C00` for `.pdata`. A naive `entryoff + ImageBase` is correct for exactly one section and silently wrong for the other six.** `[inferred]` **This is the failure geometry the Lead attributed to `1417cb3a2` — a virtual address read as a file offset — and it is the same error in the opposite direction. Both are a basis mismatch in which the wrong answer is plausible and well-formed.**

`[verified]` **Every emitted TSV carries a `# NOTE` line stating the full rule, including the per-section delta, so the map cannot be misused without contradicting its own header.**

`[inferred]` **For the ten non-Windows binaries the basis is the file image, and the Lead's warning applies with equal force: an `entryoff` from a non-relocated Go binary is a file-relative offset, not a runtime VA, unless the load address is independently known.**

---

## §4 T2 — THE REAL QUALITY METRIC, REPLACING THE TAUTOLOGICAL ONE

`[verified]` **D112 withdrew its own `bad=0` metric on the ground that `Read-GoName` substituted `.` for non-printable bytes and therefore could never reject. This section replaces it.**

`[verified]` **New metrics, input cardinality printed in the same block, aggregated over all 11 binaries:**

| metric | value |
|---|---:|
| `functab` entries scanned (**input**) | **191,873** |
| resolved to a name inside `funcnametab` | **191,873** |
| **zero-length names** | **0** |
| **names containing a control byte (<0x20 or 0x7F)** | **0** |
| **name reads truncated at the cap** | **0** |
| unique after dedup | **189,464** |
| **collisions after dedup** | **2,409** |

`[inferred]` **The difference from the old metric is that these CAN fail.** `[inferred]` **A zero-length count of 0 is falsifiable because a real reader can return an empty string; a control-byte count of 0 is falsifiable because a mis-aligned name offset lands in binary data and would produce control bytes; a truncation count of 0 is falsifiable because the cap is 512 and a runaway read would hit it.** `[inferred]` **The old `bad=0` could not fail; none of these three can pass by construction.**

### §4.1 THE COLLISION POPULATION, IDENTIFIED

`[verified]` **The 2,409 collisions are not parse defects. They are distinct functions sharing a name.** `[verified]` **Worked example — the most-duplicated name in `merlinAgent-Linux-x64`, appearing 8 times at 8 distinct addresses:**

```
FUNC	0x20D560	crypto/internal/fips140hash.UnwrapNew[go.shape.interface {...}].func1	0x86770
FUNC	0x20D700	crypto/internal/fips140hash.UnwrapNew[go.shape.interface {...}].func1	0x86848
FUNC	0x20D8A0	crypto/internal/fips140hash.UnwrapNew[go.shape.interface {...}].func1	0x86920
FUNC	0x20DA40	crypto/internal/fips140hash.UnwrapNew[go.shape.interface {...}].func1	0x869F8
FUNC	0x240000	crypto/internal/fips140hash.UnwrapNew[go.shape.interface {...}].func1	0x8D8D0
FUNC	0x24F400	crypto/internal/fips140hash.UnwrapNew[go.shape.interface {...}].func1	0x90280
FUNC	0x293440	crypto/internal/fips140hash.UnwrapNew[go.shape.interface {...}].func1	0x99260
FUNC	0x325240	crypto/internal/fips140hash.UnwrapNew[go.shape.interface {...}].func1	0xB5BE8
```

`[inferred]` **Eight distinct `entryoff` values, eight distinct `funcoff` values, one name.** `[inferred]` **The name is derived from the generic SHAPE, so every instantiation site emits an identically-named closure. The addresses are tens of kilobytes apart, so these are genuinely separate code ranges.**

`[verified]` **Distribution in `merlinAgent-Linux-x64`: 12,062 rows · 179 distinct names occurring more than once · 364 rows involved in a collision.** `[verified]` **Of the duplicated names, 8 contain a generic bracket and 30 carry a `runtime`/`internal/`/`type:` prefix.**

`[inferred]` **CONSEQUENCE FOR THE BUILD-DIFF WORK:** `[inferred]` **a name is NOT a unique key in this table. Any diff that joins on name alone will silently collapse 2,409 distinct functions. The correct key is `(binary, entryoff)`, and the TSV's row identity is that pair.**

---

## §5 T3 — WHAT THE CLIs CARRY THAT THE AGENTS DO NOT

### §5.1 Three failed attempts, and why the fourth is the one reported

`[inferred]` **The obvious instrument — split the symbol on `/` to recover the package — is wrong, and it took three attempts to establish that.** `[inferred]` **Recorded because the failures are the finding.**

| attempt | rule | failure |
|---|---|---|
| 1 | prefix = first 3 path segments | emitted **full function names** as packages |
| 2 | prefix = first 4 path segments | same failure, more rows |
| 3 | prefix = everything before the **last** `/` | stripped the real package |

`[verified]` **Attempt 3's rule was tested on eight known shapes BEFORE any number was reported, and the control failed:**

```
net/http.(*Client).Do                       -> net        WRONG (package is net/http)
golang.org/x/crypto/ssh.(*channel).WriteExtended -> golang.org/x/crypto   WRONG (package is .../ssh)
golang.org/x/crypto/ssh.NewClient           -> golang.org/x/crypto        WRONG
fmt.Println                                 -> <no-slash: stdlib root>    correct
```

`[inferred]` **CAUSE: a Go symbol is `import/path.FunctionName`, so the function name is joined to the LAST path segment by a dot. There is no fixed depth and no fixed slash position that recovers the package.** `[inferred]` **`net/http` has its package at the second slash; `golang.org/x/crypto/ssh` at the fourth. The true package boundary lives in the pclntab COMPILATION-UNIT table, not in the name text.**

`[inferred]` **The control caught this BEFORE a single count was published. A control run after the numbers would have been a correction; run before, it was a prevention.**

### §5.2 The reported diff — literal prefix tests only

`[verified]` **The diff below uses literal string-prefix tests and NO path parsing, so every count is defensible without a package-boundary rule.** **COUNTED: agent name rows = 60,288 (5 builds) · CLI name rows = 79,928 (5 builds).**

| literal prefix | agents | CLIs |
|---|---:|---:|
| `github.com/Ne0nd0g/merlin-cli` | **0** | **6,254** |
| `github.com/Ne0nd0g/merlin-agent` | **1,504** | **0** |
| `google.golang.org/grpc` | **0** | **7,890** |
| `google.golang.org/protobuf` | **0** | **11,394** |
| `google.golang.org` (all) | **0** | **19,348** |
| `text/template` | **0** | **1,940** |
| `html/template` | **0** | **550** |
| `github.com/chzyer` (readline) | **0** | **1,580** |
| `github.com/olekukonko` (tablewriter) | **0** | **115** |
| `github.com/clipperhouse/uax29` | **0** | **70** |
| `golang.org/x/crypto/ssh` | **1,520** | **0** |
| `net/http` | **4,099** | **1,124** |

`[inferred]` **THE MUTUAL ZEROS ARE THE FINDING.** `[inferred]` **`github.com/Ne0nd0g/merlin-cli` appears 0 times in 60,288 agent rows. `github.com/Ne0nd0g/merlin-agent` appears 0 times in 79,928 CLI rows.** `[inferred]` **Not "few" — zero. Two binaries from one module root with no code-level overlap in either direction.**

`[inferred]` **WHAT THE CLIs CARRIED, as a package list with counts and nothing more: a gRPC/protobuf control plane (19,348), template rendering (2,490), and an interactive line editor (1,580 readline + 115 tablewriter), plus the entire `merlin-cli` command tree (6,254 — including `commands/agent/{all,windows,linux}`, `commands/listeners`, `commands/multi`, `commands/module`, `commands/mainMenu`, `services`, `listener`, `entity`, `module`).**

`[inferred]` **WHAT THE AGENTS CARRIED INSTEAD: `golang.org/x/crypto/ssh` at 1,520, and MORE `net/http` than the CLI (4,099 vs 1,124).** `[inferred]` **The implant carries the SSH client surface and the heavier HTTP surface; the tool carries the operator-facing gRPC/template console.**

`[inferred]` **BOUND, STATED PLAINLY: these are symbol-namespace counts. They establish which packages have code in which binary. They do not establish what that code does, whether it is reached, or how it is configured.** `[inferred]` **No behavioural claim is made in this section.**

---

## §6 T4 — THE MANAGED SURFACE: AN `[absence]` FINDING

`[verified]` **ENUMERATION, not assumption.** The first scope guess (`05_TARGETS`) held **17 managed-candidate files and zero Covenant**. Covenant was then located by **enumerating every path under `RE_Library` matching `Covenant`** — **COUNTED: 58 paths** — and it lives at `01_SOURCE_c2\covenant\`.

`[verified]` **Build-output enumeration:** `bin\` directories found: **0**. `obj\` directories found: **0**.

`[verified]` **Files named `Covenant.dll` anywhere under `RE_Library`: 0.**

`[verified]` **POSITIVE CONTROL: the same finder returns `mscorlib.dll` → 2.** `[inferred]` **The finder detects a `.dll` that exists, so the zero for `Covenant.dll` is a real absence, not a broken probe.**

`[verified]` **Of the 47 `.dll` files under the covenant tree, 36 are inside `Data\AssemblyReferences\` (Microsoft reference assemblies — EXCLUDED as vendored tooling, untouched).** The 11 outside it are **tooling and payloads, not Covenant's own assembly**:

| non-vendor DLL | role |
|---|---|
| `Confuser.Core` · `Confuser.DynCipher` · `Confuser.MSBuild.Tasks` · `Confuser.Protections` · `Confuser.Renamer` · `Confuser.Runtime` | obfuscation toolchain |
| `dnlib.dll` · `Donut.dll` · `PeNet.dll` | IL/PE/dotnet payload tooling |
| `SharpSploit.Resources.powerkatz_x64.dll` · `..._x86.dll` | embedded payload resource |

`[inferred]` **THE DISPOSITION.** `[inferred]` **Covenant exists in this corpus as SOURCE ONLY — `.csproj`, `.sln`, and the `.cs` tree. There is no compiled Covenant assembly to decompile.**

`[inferred]` **THE SUBSTANTIVE ANSWER TO THE OBJECTIVE:** `[inferred]` **D107's `StringEnumConverter` result cannot be checked against Covenant's own compiled assembly, because Covenant never contributed a compiled assembly to this corpus.** `[inferred]` **D107 was tested against THE LIBRARY by execution, as its own title states. There is no Covenant build output whose IL could confirm or contradict the source's declared initializers.**

`[inferred]` **CAPABILITY NOTE, offered because the Lead believed otherwise:** `[inferred]` **`ilspycmd` is not blocked by policy here — it is blocked by the ABSENCE OF A TARGET.** `[inferred]` **The reason no one ran it over Covenant is that there is no Covenant binary to run it over, not that the instrument was unavailable.** `[inferred]` **If a Covenant build output is later obtained, the comparison becomes straightforward; the instrument and the question are both ready.**

`[inferred]` **GRADE CONTRAST:** `[inferred]` **here the FILE NAMES inside a directory were fully enumerable and only the compiled result was missing. In §7 not even the names are readable. The corpus now carries two distinguishable grades of `[absence]`, and they should not be recorded with the same word.**

---

## §7 T5 — THE ENCRYPTED ARCHIVE: `[blocked]`, WITH THE MECHANISM CORRECTED

### §7.1 Identity

`[verified]` **Path:** `02_BINARIES\merlin\merlinServer-Windows-x64.7z`
`[verified]` **Bytes: 68,780,065**
`[verified]` **SHA-256:** `6A93F70BE0720D1CA3C4938F79FBEF947C0BE21D94B61A634D6A2A7061334983`
`[inferred]` **Matches the Lead's `6A93F70B…34983` exactly (prefix and suffix).**
`[verified]` **Tool: 7-Zip 26.04 (x64), `C:\Program Files\7-Zip\7z.exe`, reported build date 2026-10-05.**

### §7.2 The correction — three distinct behaviours, and it is a PROMPT, not a refusal

`[inferred]` **The brief stated 7-Zip "refuses even `l`." The measurement shows otherwise, and the difference is the finding.**

| invocation | observed stdout | exit |
|---|---|---:|
| `7z l -slt <archive>` | `Enter password (will not be echoed):` — **blocks on stdin** | **255** |
| `7z l -p"" <archive>` | `Errors: 1` | **2** |
| `7z l -p"notthepassword" <archive>` | `Errors: 1` | **2** |
| `7z l -p"" -ba <archive>` (bare listing) | **no listing emitted at all** | **2** |

`[verified]` **Exact refusal text, stderr, identical for the empty and wrong passwords:**

```
ERROR: ...\merlinServer-Windows-x64.7z : Cannot open encrypted archive. Wrong password?
```

`[inferred]` **A PROMPT AND A REFUSAL ARE DIFFERENT GEOMETRIES.** `[inferred]` **7-Zip read far enough into the archive to determine that a key is required, and asked for it. That is not the same as declining to open the file.** `[inferred]` **For a `[blocked]` finding this distinction is load-bearing: a prompt establishes that the archive's KEY STRUCTURE is intact and the tool engaged with it, whereas a blanket refusal would leave even that unknown.**

### §7.3 What the block DOES prove, established without any tool

`[verified]` **The 32-byte StartHeader, read as raw bytes:**

```
signature        : 37 7A BC AF 27 1C   (7z)
version          : 0x0400
StartHeaderCRC   : 0xFC661B8D
NextHeaderOffset : 0x4197FC0
NextHeaderSize   : 0x41   (65 bytes)
NextHeaderCRC    : 0xC29D5BDA
```

`[verified]` **PROVEN:** the file is a well-formed 7z with an intact StartHeader and a declared Next Header of 65 bytes at `0x4197FC0+32`. **It is not truncated, not corrupt, and not misidentified.**
`[verified]` **PROVEN ABSENT:** the contents. **Not even filenames are readable** — the `-ba` bare listing suppresses its own headers and returns nothing, so the entry table is inaccessible without the key.
`[inferred]` **This places the archive at the STRONGEST grade of block available: an encrypted-header archive defeats name enumeration too, whereas a data-only-encrypted archive would still list its entries.**
`[inferred]` **CONTRASTING REFERENCE:** the corpus records `sliver-client_windows-amd64.exe` as **NOT STRIPPED** with its symbols present. `[inferred]` **The Sliver client is fully readable; this archive is fully sealed. The corpus contains both extremes on the same surface.**

### §7.4 The password is not in the corpus

`[verified]` **SCOPE:** every text-like file under `RE_Library` (`*.md`, `*.txt`, `*.json`, `*.yml`, `*.yaml`, `*.ps1`, `*.bat`, `*.csv`, `*.log`, `*.ini`, `*.cfg`, `*.xml`). **COUNTED: 15,060 files.**

`[verified]` **Narrowed to the files that actually mention the archive: COUNTED: 32.**

`[verified]` **In those 32 files, no line pairs the archive with a password value.** `[inferred]` **The 41 "password-like token" matches produced by a loose regex were all inspected and are ALL FALSE POSITIVES** — they match prose containing `extract`/`key`/`cross-tabulation`, the filename `merlinServer-Windows-x64.exe` itself, and one directory listing (`merlin/  merlinServer-Windows-x64.7z  65.6 MB  v2.2.2`) whose trailing token is a **version number, not a credential**.

`[verified]` **POSITIVE CONTROL: the same search finds `merlin` in 141 files.** `[inferred]` **The searcher works, so "no password found" is a real absence.**

`[inferred]` **A LOOSE PATTERN'S HIT COUNT IS NOT EVIDENCE, AND REPORTING ONE WOULD HAVE BEEN THE SAME DEFECT AS `bad=0`.** `[inferred]` **Reporting "1,558 files contain a password" would have been arithmetically true, semantically empty, and materially misleading. The count was narrowed to the only defensible scope and every survivor was inspected by eye.**

### §7.5 Adjacent finding — the server binary was analysed, but not from this archive

`[verified]` `C-02_merlinServer-Windows-x64.exe.ghidra-symbols.tsv` exists in `binlayer\`, with provenance:

```
# program	merlinServer-Windows-x64.exe
# language	x86:LE:64:default
# compiler	golang
# imageBase	140000000
# kind	address	name	size	namespace	is_thunk
FUNC	140001000	FUN_140001000	655	Global	false
```

`[verified]` `_d99_edges.json` records `merlinServer-Windows-x64.exe` as **NOT STRIPPED**, "the server's own symbols are present".

`[verified]` **`02_BINARIES` contains exactly 4 files and no extracted server `.exe`:** `havoc_BUILDFROM_SOURCE\README.md` (307) · `merlin\merlinServer-Windows-x64.7z` (68,780,065) · `sliver\sliver-client_windows-amd64.exe` (65,866,240) · `sliver\sliver-client_windows-amd64.exe.minisig` (326).

`[inferred]` **THE ARCHIVE IS SEALED BUT THE SERVER BINARY IS NOT UNKNOWN — a `merlinServer-Windows-x64.exe` was analysed with real symbols at some earlier point, and its provenance does not record a source path pointing at this `.7z`.**

`[inferred]` **R-121.6 files the gap: an artifact exists in the analysis record whose extraction source is not stated anywhere in the corpus. This is the `02_BINARIES` root again — a path named is not a provenance established.**

### §7.6 What was NOT done

`[verified]` **No cracking was attempted.** No wordlist, no dictionary, no brute force, no `-p` against a candidate list. **One empty password and one deliberately wrong password were used solely to force a non-interactive refusal for documentation.**

---

## §8 Instrument and process failures this round

`[inferred]` **Five failures, all self-caught. Recorded because the corpus's value is in the failures being visible.**

**F1 — `Start-Process -ArgumentList` silently mis-split the spaced path.**
`[verified]` 7-Zip received `C:\Users\PC\OneDrive\Desktop\FOR` and returned `ERROR: The system cannot find the file specified`, exit 2.
`[inferred]` **CAUGHT BY THE CONTROL.** `[inferred]` **The control ran 7z against an unencrypted `DLLHijackAuditKit.zip` and ALSO returned exit 2.** `[inferred]` **Without the control I would have reported "7-Zip refuses even `l` — encrypted headers confirmed", a fabricated finding built on a path-parsing failure. This is the same spaced-path failure class the Lead documented, and it is the single most dangerous thing that happened this round.**
`[inferred]` **FIX:** hardcoded absolute path in a `.bat` wrapper, invoked `Start-Process cmd.exe -ArgumentList '/c',$wrap`. **The prompt then appeared immediately and the archive opened far enough to demand a key.**

**F2 — PowerShell backtick-escaped quotes are not valid syntax.**
`[verified]` `"...\"$seven\"..."` raised `Unexpected token`. `[inferred]` **A `cmd` quoting habit; single quotes or paired `""` are required.**

**F3 — T3's package heuristic failed three times before the control caught it.**
`[inferred]` **Documented in full at §5.1.** `[inferred]` **The third rule would have mislabelled `net/http` as `net` in every row of a published table.**

**F4 — A loose search pattern produced 41 meaningless matches.**
`[inferred]` **Documented at §7.4. Reporting the raw count would have been a number that cannot fail to be large.**

**F5 — my own instrument's substitution character.**
`[inferred]` **D112's `Read-GoName` replaced non-printable bytes with `.`, making `bad=0` partly tautological. T2 replaces it with three falsifiable counters and adds a collision count that reports a real population.**

`[inferred]` **THE PATTERN ACROSS ALL FIVE:** `[inferred]` **every one was caught by a control or a cross-check, and four of the five would have produced a plausible, well-formed, WRONG number. None would have looked broken.**

---

## §9 Residual unknowns

| ID | Unknown | Severity | Probe |
|---|---|---|---|
| **R-121.1** | **No call graph.** The index gives addresses and names, not edges. Reachability of any function remains unknown, including the injection paths D95 §5.3 flagged. | **high** | Requires disassembly; blocked by the dead Go analyzer. |
| **R-121.2** | **No runtime VA mapping.** `entryoff` is an image-relative offset; converting to VA needs per-section mapping and, for non-Windows, a load address. No VA column was emitted. | **high** | Add a per-section VA column once the loader basis is fixed. |
| **R-121.3** | **Package boundary is not resolved from names.** §5.2 uses literal prefixes only because the text is ambiguous. The exact package per function is available in the `cuOffset` table and was NOT read. | **medium** | Decode the compilation-unit table; replaces the prefix heuristic. |
| **R-121.4** | **2,409 collisions mean a name is not a unique key.** Any join on name alone collapses distinct functions. | **medium** | Documented; key on `(binary, entryoff)`. |
| **R-121.5** | **`Covenant.dll` absent; no compiled Covenant artifact exists in this corpus.** D107's library result stands untested against Covenant's own build. | **medium** | Obtain a build output; instrument is ready. |
| **R-121.6** | **`C-02`'s server `.exe` exists in the analysis record with no stated extraction source,** while `02_BINARIES\merlin\` holds only a sealed `.7z`. | **medium** | Locate the extraction that produced `C-02`, or record its absence. |
| **R-121.7** | **The 65-byte Next Header's contents are unreadable** — the encrypted-header flag itself sits inside the block requiring the key. | **low** | Confirmed encrypted by tool behaviour; exact flag not directly observed. |
| **R-121.8** | **No archive password exists in the corpus** (15,060 files searched, 32 narrowed, control positive). The password's location is external. | **low** | Out of static reach. |

---

## §10 Summary

`[verified]` **T1 — THE ADDRESS→NAME INDEX EXISTS.** **11 TSVs in `binlayer\`, 191,873 functions resolved to names, 189,464 unique, 2,409 collisions, 0 malformed rows.** Proven end-to-end on `agent.(*Agent).SetComms` → `0x198580` / `0x1CD520`. `[inferred]` **Independently validated: D96's separate parser and this one both report `total=51657 unique=51208` for the Sliver PE.**

`[verified]` **T1 LIMITATION — the offset/VA trap, demonstrated.** `[inferred]` **Per-section deltas span `0xA00` to `0x2076C00`; `entryoff + ImageBase` is correct for one section and silently wrong for six. The rule is in every TSV's `# NOTE` line.**

`[verified]` **T2 — A METRIC THAT CAN FAIL.** `[inferred]` **191,873 entries scanned, 0 zero-length, 0 control-byte, 0 truncated, 2,409 collisions.** `[inferred]` **The collisions are generic-instantiation closures sharing a shape-derived name — 8 distinct addresses for one name, proven. A name is not a unique key.**

`[verified]` **T3 — THE CLI SURFACE.** `[inferred]` **The mutual zeros are absolute: `merlin-cli` 0 in 60,288 agent rows; `merlin-agent` 0 in 79,928 CLI rows.** `[inferred]` **The CLI carries gRPC/protobuf 19,348, template 2,490, readline 1,580; the agent carries SSH 1,520 and MORE HTTP (4,099 vs 1,124).** `[inferred]` **Counts only — no behavioural claim.** `[inferred]` **The package-boundary heuristic failed three times; the control caught it before publication.**

`[verified]` **T4 — `[absence]`, WITH THE ENUMERATION SHOWN.** `[inferred]` **Covenant is SOURCE-ONLY. `Covenant.dll`: 0 anywhere. `bin\`/`obj\`: 0. Control: `mscorlib.dll` → 2.** `[inferred]` **D107 cannot be checked against Covenant's own compiled assembly because none exists in this corpus. 36 `AssemblyReferences` DLLs excluded and untouched.**

`[verified]` **T5 — `[blocked]`, MECHANISM CORRECTED.** `[inferred]` **7-Zip 26.04 does NOT refuse `l`; it PROMPTS for a password (exit 255), and refuses with `Cannot open encrypted archive. Wrong password?` (exit 2) under `-p`.** `[inferred]` **StartHeader read directly: valid 7z, NextHeader 65 bytes at `0x4197FC0+32`, not truncated.** `[inferred]` **Contents — including filenames — unreadable. Password absent from 15,060 files. No cracking attempted.**

`[inferred]` **FIVE INSTRUMENT FAILURES, ALL SELF-CAUGHT.** `[inferred]` **The most dangerous was the spaced-path mis-split, caught only because the control also failed on an unencrypted archive — without it, a fabricated `[blocked]` finding would have shipped.**

`[inferred]` **D116 remains unoccupied and unclaimed.**
