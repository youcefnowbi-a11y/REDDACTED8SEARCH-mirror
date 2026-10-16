# D112 — The pclntab lane is open: 140,216 Go symbols recovered from the 10 unanalysed cross-platform binaries without Ghidra

**Scope:** target T8 `merlin_extracted\data\bin\` + `RE_Library\binlayer\` + the D95/D61/D41 report set. Round 25 follow-on to D110.
**Line-count convention:** LF count = the count of regex matches for the LF character over the full text returned by `[IO.File]::ReadAllText`. A final line without a trailing newline is **not** counted. **This line is stated in prose deliberately** — an earlier draft embedded the query as inline code and leaked PowerShell string-concatenation syntax into the report body.
**Tags:** `[verified]` instrument run with output shown · `[read]` quoted from an artifact read directly · `[inferred]` reasoning over evidence · `[absence]` probe returned zero **with a positive control shown**.
**Discipline:** **no corpus binary was executed.** No network. No live C2. **No Ghidra run** — none was needed and none was permitted. Every figure below is a byte read.
**Write scope:** `D112_*.md` only. **All working artifacts were staged in `%TEMP%`, never the repo** (`d112_pclntab.ps1`, `d112_pclntab32.ps1`, `d112_modules.ps1`, `d112_t5.ps1`, 5 name files). Verified: `_d112_*` in `binlayer\` = **0**.
**Allocation:** `D112` enumerated → **0 matches**, so `D112` is free and is taken. `D113`/`D114`/`D115` **already exist**; the next free after this report is **`D116`**. The numbering is not monotonic.

---

## §0 Headlines

`[verified]` **1. THE LANE IS OPEN. All 10 formerly-unanalysed binaries carry a parseable Go pclntab, and 140,216 function names were recovered WITHOUT Ghidra.** 5 agents → **60,288** names; 5 CLIs → **79,928** names. **Zero absent magic. Ten of ten.** The `merlinCLI*` set — never previously analysed at any layer — is now fully nameable.

`[verified]` **2. The instrument generalises by RELAXING VALIDATION, not by bypassing the magic.** The anchor is the magic `0xFFFFFFF1` **plus** `pad1==0 && pad2==0` in every one of the ten. `[inferred]` **A name-table-tail anchor was NOT used, and claiming otherwise would overstate the instrument.** `[inferred]` **The header LAYOUT is what differs per target (`u64` vs `u32` offsets), not the presence of the anchor.**

`[verified]` **3. A validation rule derived from the MAJORITY case silently deleted the MINORITY case — and the deletion looked like absence.** The strict rule `minLC==1 && ptrSize==8` (D96's, and the Lead's) **rejects Darwin-arm64, Linux-arm, and Linux-arm64** — exactly the three targets that appeared to have "no table." `[inferred]` **`minLC` is instruction-length alignment: 1 on x86, 4 on ARM. It is a legitimate per-architecture value treated as a constant.** This is now the same defect class as D110's `ptrSize==8` bug, recorded once.

`[verified]` **4. T3 is airtight and better than a byte count.** `.reloc` is **121,856 bytes in BOTH** builds; **block count identical (327 both)**; **`DIR64` (type 10) fixup count IDENTICAL: 59,257 both.** Only `ABSOLUTE` block padding differs, 153 vs 151. **The relocation set is the same size and the same type; only the VALUES move.** The 62,896 differing bytes are shifted fixup targets, not created fixups. The 2-entry `ABSOLUTE` delta is **block alignment padding, not a fixup.**

`[verified]` **5. `github.com/awgh/rawreader` is the ONLY build-conditional module: 2 of 7 builds, `W-x64` and `W-x64-Dbg`.** All **19** others are **7/7**. `[inferred]` **Its presence in the DEBUG build as well as release is the informative part — the condition is OS, not build mode.**

`[verified]` **6. R-110.9 closes as: THE D95 CLAIM STANDS, THE EVIDENCE WAS INVALID.** D95 is genuinely clean (33,431 B, mojibake 0, U+FFFD 0, valid UTF-8) — **but its §5 probe could not match anything, so its "0 hazards" was a claim the instrument was physically incapable of falsifying.** `[inferred]` **D95 reached a true conclusion by careful prose editing and then certified it with a broken detector. D95 needs no textual correction; its §5 must be marked unverified-by-measurement.**

`[verified]` **7. PCLNTAB GIVES IDENTITY, NOT BEHAVIOUR.** Recovering 140,216 names does **not** deobfuscate a single string, does **not** give a single address, and does **not** tell anyone what any function does. C-10's rule, restated in §6 so the number cannot be over-read.

---

## §1 T1 — R-110.9 CLOSED: D95'S CLEANLINESS CLAIM STANDS, ITS EVIDENCE DOES NOT

### §1.1 The detector, rebuilt from BYTES

`[verified]` D110's hazard probe was **broken**: it concatenated four *characters* (`0xC3, 0x82, 0xC2, 0xA7`) and UTF-8-encoded the result, producing the eight-byte sequence `C3 83 C2 82 C3 82 C2 A7` — which can never match a four-byte sequence in any file. **It scanned both files and matched nothing, silently.**

`[verified]` **The corrected detector operates on raw bytes with no character-concatenation step:**

| probe | pattern | meaning |
|---|---|---|
| mojibake | `C3 82` | start of the double-encoded `Â` |
| replacement | `EF BF BD` | U+FFFD |
| correct section sign | `C2 A7` | a properly encoded `§` |
| validity | strict `UTF8Encoding($false,$true)` | **throws** on invalid input |

### §1.2 The positive controls — the detector is proven live

`[verified]` **No cleanliness claim is admissible without a control that returns non-zero.**

| control | bytes | mojibake `C3 82` | U+FFFD | correct `§` (`C2 A7`) | strict UTF-8 |
|---|---:|---:|---:|---:|---|
| **D41** (two documented instances at L747/L757) | 75,359 | **2** ✓ | 0 | 179 | valid |
| **D61** (numeric claim audit) | 30,130 | **3** | 0 | 55 | valid |

`[inferred]` **D41 returning exactly 2 matches the two intentional instances the corpus already documents** — so the detector is not merely non-zero, it is **accurate to a known ground truth**. `[inferred]` **D61's true value is 3, not the 4 recorded last round; the prior figure was wrong and this supersedes it.**

### §1.3 The scan of D95

`[verified]` **D95 §5's four named artifacts** — `D95` names them by spelling, so they were resolved by **enumeration against the report text plus a direct byte scan of D95 itself**:

| target | bytes | mojibake `C3 82` | U+FFFD | correct `§` | strict UTF-8 |
|---|---:|---:|---:|---:|---|
| **`D95_merlin_binary_layer_…census.md`** | **33,431** | **0** | **0** | **38** | **valid** |
| `D110_merlin_artifact_census_…divergence.md` | 41,800 | 0 | 0 | 53 | valid |

`[verified]` **D95's own text was additionally probed for the two literals it claimed to have removed** — the string `C382C2A7` and the string `EFBFBD` — and for the raw byte sequences:

```
C382C2A7 literal in D95 text : 0
EFBFBD   literal in D95 text : 0
raw C3 82 bytes in D95       : 0
raw EF BF BD bytes in D95    : 0
```

`[verified]` **D95's byte size independently reproduces at 33,431 — the figure D95 itself records.**

### §1.4 THE RESOLUTION

`[verified]` **R-110.9 CLOSES AS: THE CLAIM STANDS; THE EVIDENCE WAS INVALID.**

`[inferred]` **D95 is clean. It is clean by measurement now, and by three independent methods (byte scan, character-level count, strict UTF-8 decode).** `[inferred]` **But D95's own §5 probe was a detector that could not match any input, so the "0 hazards" D95 published was a number its instrument could not have contradicted.** `[inferred]` **The correct disposition is not "D95 was wrong" — D95 was RIGHT. It is "D95 was right without having measured it."**

`[inferred]` **WHY THIS IS WORTH RECORDING RATHER THAN QUIETLY FIXING:** `[inferred]` **A false-clean claim from a working detector is a defect in the FILE. A right-answer claim from a broken detector is a defect in the METHOD — and it is more dangerous, because every OTHER claim that detector produced carries the same unquantified risk.** `[inferred]` **D95's §5 remediation is substantively correct and its prose fix was real. What D95 cannot support is that it was CHECKED.**

`[inferred]` **Action recorded:** D95 needs **no textual correction**. Its §5 should be annotated as **unverified-by-measurement**, with D112 §1.2 cited as the control series that proves the original probe was inert.

### §1.5 THE REPORT'S OWN DETECTOR TRIPS ON THIS REPORT

`[verified]` **Running the corrected byte-level probe over D112 itself returns `mojibake = 1`.** `[inferred]` **This is a TRUE POSITIVE with an innocent cause, and it is recorded rather than suppressed.**

`[verified]` **The hit is inside §1.1's own detector table, at the row that NAMES the pattern. To name the byte pair in prose is to contain the byte pair.** `[inferred]` **A report that documents a hazard pattern in raw hex will necessarily fail its own scan for that pattern.**

`[inferred]` **WHY THIS IS WORTH A SECTION AND NOT A SILENT EXEMPTION:** `[inferred]` **the correct disposition is neither to suppress the hit nor to rewrite the documentation to dodge the detector. It is to state the cause, state the count (1), and state that the count is explained.** `[inferred]` **A scanner hit that is explained is evidence the scanner works. A scanner hit that is quietly filtered out is the beginnings of a detector that reports what you expect.**

`[verified]` **D112's OTHER byte-level probes remain clean and are unaffected: U+FFFD = 0, strict UTF-8 valid over all 37,335 bytes, and 55 correctly-encoded section signs.** `[inferred]` **The single C3 82 occurrence is the documented pattern inside the documentation, not corruption in the file.**

---

## §2 T2 — THE PCLNTAB LANE, AND WHAT ACTUALLY ANCHORS IT

### §2.1 The mechanism, stated exactly

`[verified]` **The anchor is the 4-byte magic `0xFFFFFFF1` followed by `pad1==0` and `pad2==0`.** `[verified]` **This holds for all ten binaries — no exceptions.**

`[verified]` **Raw magic-hit counts inside each file, before any validation:**

| agent | `0xFFFFFFF1` byte-pattern hits | validated base |
|---|---:|---|
| Darwin-arm64 | 3 | `0x500B40` |
| Darwin-x64 | 29 | `0x5D9460` |
| Linux-arm | 3 | `0x64A1E0` |
| Linux-arm64 | 3 | `0x526960` |
| Linux-x64 | 30 | `0x5F0C20` |

`[inferred]` **The magic alone is not sufficient — it occurs 3 to 30 times per file.** `[inferred]` **The discriminator is the field validation AFTER the magic**, in this order: `pad1==0`, `pad2==0`, plausible `nfunc` (1,000–200,000), plausible `nfiles` (100–20,000), and every header offset resolving inside the file.

`[inferred]` **CORRECTION TO A GENEROUS READING OF THIS RESULT.** `[inferred]` **The instrument is NOT name-table-tail anchored and does NOT bypass the magic.** `[inferred]` **Claiming it generalises past the header would overstate it.** `[inferred]` **What genuinely generalises is the VALIDATION RELAXATION — see §3.**

### §2.2 The two header layouts

`[verified]` **Two distinct pcHeader layouts are required, and which one applies is determined by `ptrSize`, not by the container format:**

| layout | when | fields read |
|---|---|---|
| `u64 offsets` | `ptrSize == 8` | `nfunc`@+8, `nfiles`@+16, `textStart`@+24, `funcnameOffset`@+32, `cuOffset`@+40, `filetabOffset`@+48, `pctabOffset`@+56, `pclnOffset`@+64 |
| `u32 offsets` | `ptrSize == 4` | `nfunc`@+8, `nfiles`@+12, `textStart`@+16, `funcnameOffset`@+20, `cuOffset`@+24, `filetabOffset`@+28, `pctabOffset`@+32, `pclnOffset`@+36 |

`[verified]` **`merlinAgent-Linux-arm` is the only 32-bit target** and resolves under the `u32` layout. Its header, decoded positionally from the literal bytes at `0x64A1E0`:

```
+0  magic 0xFFFFFFF1   +4 pad1 0   +5 pad2 0   +6 minLC 4   +7 ptrSize 4
+8  nfunc 12037   +12 nfiles 1327   +16 textStart 0x0
+20 funcnameOffset 0x28   +24 cuOffset 0xB0798
+28 filetabOffset 0xBA758  +32 pctabOffset 0xD13C8  +36 pclnOffset 0x2190A8
```

`[inferred]` **NOTE `textStart == 0x0`.** `[inferred]` **This is a known-good header whose `textStart` is zero.** `[inferred]` **Any probe shaped as an eight-field struct expecting a NON-ZERO `textStart` at a fixed offset will mis-anchor on this file — the layout searched for is not the layout the file has.**

### §2.3 The per-target results (agents)

`[verified]` All five non-Windows agents parsed with **zero empty reads**:

| agent | kind | pclntab base | nfunc | parsed | unique | pkgs | layout | minLC | ptrSize |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| Darwin-arm64 | Mach-O | `0x500B40` | 12,052 | 12,052 | 11,881 | 322 | u64 | **4** | 8 |
| Darwin-x64 | Mach-O | `0x5D9460` | 12,167 | 12,167 | 11,984 | 324 | u64 | 1 | 8 |
| Linux-arm | ELF | `0x64A1E0` | 12,037 | 12,037 | 11,885 | — | **u32** | **4** | **4** |
| Linux-arm64 | ELF | `0x526960` | 11,970 | 11,970 | 11,795 | 328 | u64 | **4** | 8 |
| Linux-x64 | ELF | `0x5F0C20` | 12,062 | 12,062 | 11,877 | 330 | u64 | 1 | 8 |
| **TOTAL** | | | **60,288** | **60,288** | **59,422** | | | | |

`[verified]` **Real recovered symbols, identical across all five builds:**

```
github.com/Ne0nd0g/merlin-agent/v2/core.init
github.com/Ne0nd0g/merlin-agent/v2/core.RandStringBytesMaskImprSrc
github.com/Ne0nd0g/merlin-agent/v2/cli.Message
github.com/Ne0nd0g/merlin-agent/v2/os.GetIntegrityLevel
github.com/Ne0nd0g/merlin-agent/v2/agent.New
github.com/Ne0nd0g/merlin-agent/v2/agent.(*Agent).SetAuthenticated
github.com/Ne0nd0g/merlin-agent/v2/agent.(*Agent).SetComms
github.com/Ne0nd0g/merlin-agent/v2/agent.(*Agent).SetFailedCheckIn
github.com/Ne0nd0g/merlin-agent/v2/agent.(*Agent).SetInitialCheckIn
github.com/Ne0nd0g/merlin-agent/v2/agent.(*Agent).SetKillDate
```

### §2.4 THE CORROBORATION — and the caveat that must travel with it

`[verified]` **`bad==0` in the parse loop is NOT evidence of a clean parse, and is not offered as such.** `[inferred]` **`Read-GoName` substitutes `.` for every non-printable byte, so it can always return a non-empty string and CANNOT REJECT. The `bad` counter only ever caught empty reads.** `[inferred]` **Reporting `bad=0` as a clean-parse metric would be exactly the broken-detector pattern this round exists to correct.**

`[verified]` **The real corroboration is a SECOND INDEPENDENT METHOD** — an ASCII scan of the raw file counting occurrences of the import path, compared against the parsed name list:

| agent | parsed names | parsed `merlin-agent/v2` names | raw-byte `merlin-agent/v2` hits | ratio |
|---|---:|---:|---:|---|
| Darwin-arm64 | 12,052 | 299 | 399 | 1.33 |
| Darwin-x64 | 12,167 | 299 | 400 | 1.34 |
| Linux-arm | 12,037 | 302 | 402 | 1.33 |
| Linux-arm64 | 11,970 | 302 | 401 | 1.33 |
| Linux-x64 | 12,062 | 302 | 402 | 1.33 |

`[inferred]` **The two methods agree in structure: parsed names are consistently ~1/3 of raw byte hits, because each import path also appears in the module-path and build-info tables, not only in the function-name table.** `[inferred]` **The 299–302 consistency across five independently-parsed builds is the load-bearing evidence — a parser that fabricated names would not produce a stable, platform-consistent `merlin-agent` subset.** `[inferred]` **Stated as corroboration, not as proof.**

### §2.5 Beyond the brief: the CLIs also carry pclntab

`[verified]` **All five non-Windows CLIs have exactly one validated pclntab each.** `[inferred]` **This extended the lane from the 5 agents the task named to all 10 unanalysed binaries.**

`[inferred]` **It also means R-110.1 — D110's critical residual, "10 of 16 artifacts have no symbol-layer analysis" — is no longer a critical gap.** `[inferred]` **It is now a parser run.**

---

## §3 THE DEFECT CLASS: A RULE FROM THE MAJORITY CASE DELETES THE MINORITY CASE

`[verified]` **Three independent probes in this round failed the same way, and one is mine.**

`[verified]` **The strict header rule `minLC==1 && ptrSize==8` — used by the D96 script and independently by the Lead — was tested against every confirmed base:**

| agent | `minLC` | `ptrSize` | strict rule `minLC==1 && ptrSize==8` | D112 rule `pad1==0 && pad2==0` |
|---|---:|---:|---|---|
| Darwin-arm64 | **4** | 8 | **REJECTS** | accepts |
| Darwin-x64 | 1 | 8 | accepts | accepts |
| Linux-arm | **4** | **4** | **REJECTS** | accepts |
| Linux-arm64 | **4** | 8 | **REJECTS** | accepts |
| Linux-x64 | 1 | 8 | accepts | accepts |

`[verified]` **The strict rule rejects exactly the three targets that appeared to have no pclntab.**

`[inferred]` **THE MECHANISM: `minLC` is INSTRUCTION-LENGTH ALIGNMENT — the minimum instruction length for the target ISA. It is `1` on x86/x86-64 and `4` on ARM.** `[inferred]` **It is a legitimate per-architecture value. Treating `1` as a constant deletes every ARM target, and the deletion surfaces as "the table is not there."**

`[inferred]` **THE SAME CLASS, SECOND INSTANCE — mine:** `[inferred]` **D110/D112's first parser hardcoded `ptrSize==8` and thus rejected `merlinAgent-Linux-arm`, a genuine 32-bit table.**

`[inferred]` **THE RULE, STATED ONCE FOR THE CORPUS:** `[inferred]` **A validation rule derived from the majority case rejects the minority case SILENTLY, and the rejection is indistinguishable from absence.** `[inferred]` **The remedy is a positive control on the minority case — a known-good artifact of the under-represented class must be run through the same predicate before any absence is reported.**

### §3.1 The shape-filter trap, reproduced and explained

`[verified]` **A shape-based hunt — "find `nfunc` in 8,000–20,000 with a sane `nfiles`/`textStart`" — anchored identically in three unrelated binaries.** The value **`nfunc=12411`** was located:

| binary | offset of `u64 12411` | occurrences | following 32 bytes (ASCII) |
|---|---:|---:|---|
| Darwin-arm64 | `0x4FB9A8` | **1** | `{0......6.......'H........ .....` |
| Linux-arm64 | `0x50EDC0` | **1** | `{0......6.......'H........ .....` |
| Linux-x64 | `0x5D5090` | **1** | `{0......6.......'H........ .....` |

`[verified]` **A single `u64` of value `12411` occurs once in each file, and the 64 bytes following it are byte-identical across a Mach-O arm64, an ELF arm64 and an ELF x86-64 binary.**

`[inferred]` **A per-binary function count cannot be identical and byte-identical in its surroundings across three different architectures. This is shared read-only data — a Go runtime table emitted identically into every build — that merely FALLS INSIDE a plausible range.** `[inferred]` **A shape filter tuned to "find something in range" found something in range; it was not tuned to find the RIGHT thing.** `[inferred]` **The comparison that would have caught it immediately: three architectures cannot share a table.** `[inferred]` **Recorded because it is the cheap falsification test — if a probe returns the same value for targets that must differ, the probe is reading a shared constant.**

---

## §4 T3 — THE `.reloc` MECHANISM, CONFIRMED BY ENTRY COUNT

`[verified]` **Method: parse the `.reloc` section table in each Windows agent and walk every `IMAGE_BASE_RELOCATION` block.** No execution.

`[verified]` **Byte-level summary:**

| measure | release | Debug | delta |
|---|---:|---:|---:|
| `.reloc` section size | 121,856 | 121,856 | **0** |
| differing bytes in common prefix | — | — | **62,896** |

`[verified]` **Entry-level summary, which is the measurement the Lead asked for:**

| measure | release | Debug | delta |
|---|---:|---:|---:|
| relocation BLOCKS | 327 | 327 | **0** |
| **`DIR64` (type 10) fixups** | **59,257** | **59,257** | **0** |
| `ABSOLUTE` (type 0) entries | 153 | 151 | **2** |
| total entries | 59,410 | 59,408 | 2 |
| terminator block present | yes | yes | — |

`[verified]` **THE VERDICT: the layout-shift explanation is CONFIRMED, in a stronger form than "counts are equal."** `[inferred]` **The GENUINE relocation set — the `DIR64` fixups — is identical in count (59,257) and identical in type distribution in both builds. The 62,896 differing bytes are the fixup TARGET VALUES shifting, which is exactly what a layout shift produces.** `[inferred]` **No relocation was created by removing a 14-byte string; existing relocations were re-pointed.**

`[verified]` **The only count difference is 2 `ABSOLUTE` entries, and `ABSOLUTE` (type 0) is a no-op padding entry used to align blocks to 4-byte boundaries.** `[inferred]` **A 2-entry `ABSOLUTE` delta is block padding, NOT a fixup.** `[inferred]` **It follows that T3's mechanism is confirmed by entry count rather than byte count — the confirmation the Lead requested.**

---

## §5 T4 — THE FULL 20-MODULE PRESENCE MATRIX

`[verified]` **7 builds × 20 modules, presence by direct substring search of each build's recovered string set.** Legend: `W` = Windows-x64 · `Wd` = Windows-x64-Debug · `Da` = Darwin-arm64 · `Dx` = Darwin-x64 · `La` = Linux-arm · `Lb` = Linux-arm64 · `Lx` = Linux-x64.

| module | W | Wd | Da | Dx | La | Lb | Lx | count |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|---:|
| `github.com/andybalholm/brotli` | ● | ● | ● | ● | ● | ● | ● | 7 |
| `github.com/armon/go-socks5` | ● | ● | ● | ● | ● | ● | ● | 7 |
| **`github.com/awgh/rawreader`** | **●** | **●** | · | · | · | · | · | **2** |
| `github.com/cretz/gopaque` | ● | ● | ● | ● | ● | ● | ● | 7 |
| `github.com/fatih/color` | ● | ● | ● | ● | ● | ● | ● | 7 |
| `github.com/go-jose/go-jose/v3` | ● | ● | ● | ● | ● | ● | ● | 7 |
| `github.com/google/shlex` | ● | ● | ● | ● | ● | ● | ● | 7 |
| `github.com/google/uuid` | ● | ● | ● | ● | ● | ● | ● | 7 |
| `github.com/klauspost/compress` | ● | ● | ● | ● | ● | ● | ● | 7 |
| `github.com/mattn/go-colorable` | ● | ● | ● | ● | ● | ● | ● | 7 |
| `github.com/mattn/go-isatty` | ● | ● | ● | ● | ● | ● | ● | 7 |
| `github.com/quic-go/qpack` | ● | ● | ● | ● | ● | ● | ● | 7 |
| `github.com/quic-go/quic-go` | ● | ● | ● | ● | ● | ● | ● | 7 |
| `github.com/refraction-networking/utls` | ● | ● | ● | ● | ● | ● | ● | 7 |
| `go.dedis.ch/fixbuf` | ● | ● | ● | ● | ● | ● | ● | 7 |
| `go.dedis.ch/kyber/v3` | ● | ● | ● | ● | ● | ● | ● | 7 |
| `golang.org/x/crypto` | ● | ● | ● | ● | ● | ● | ● | 7 |
| `golang.org/x/net` | ● | ● | ● | ● | ● | ● | ● | 7 |
| `golang.org/x/sys` | ● | ● | ● | ● | ● | ● | ● | 7 |
| `golang.org/x/text` | ● | ● | ● | ● | ● | ● | ● | 7 |

`[verified]` **THE TWO EXCEPTIONS, NAMED RATHER THAN COUNTED:**

1. **`github.com/awgh/rawreader` — present in exactly 2 of 7: `W-x64` and `W-x64-Dbg`, the Windows pair.**
2. **There is no second exception.**

`[verified]` **19 of 20 modules are universal (7/7). Exactly ONE is build-conditional, and it is Windows-only.** `[inferred]` **PREDICTION CORRECTED: an earlier count of "18/20" was wrong, and so was the "one exception" phrasing that implied two conditional modules. The measured figures are 19 universal, 1 conditional.**

`[inferred]` **`awgh/rawreader` present in the DEBUG build too is the informative detail: the conditional is the OPERATING SYSTEM, not the build mode.** `[inferred]` **`rawreader` is Windows process-memory reading, so its presence tracks the Windows target exactly — a clean, single-axis condition.**

`[inferred]` **`mattn/go-colorable` is 7/7 and was already corrected from a drafting-pass "2" to 7 last round. The total was not re-counted at that time, which is how "18/20" survived.** `[inferred]` **A correction applied to a row but not to the denominator is a correction half-applied — the same class as a fixup table rewritten without re-counting its entries.**

---

## §6 T5 — THE 10 BINARIES, ONE ROW EACH

`[verified]` **All ten formerly-unanalysed binaries, with anchor, yield, packages visible, and magic presence.** `pkgs` = distinct package prefixes observed in the name table.

| # | binary | kind | bytes | pclntab anchor | nfunc | parsed | unique | pkgs | layout |
|---:|---|---|---:|---|---:|---:|---:|---:|---|
| 1 | `merlinAgent-Darwin-arm64` | Mach-O | 11,808,210 | `0x500B40` | 12,052 | 12,052 | 11,881 | 825 | u64 |
| 2 | `merlinAgent-Darwin-x64` | Mach-O | 12,761,408 | `0x5D9460` | 12,167 | 12,167 | 11,984 | 827 | u64 |
| 3 | `merlinAgent-Linux-arm` | ELF | 12,124,284 | `0x64A1E0` | 12,037 | 12,037 | 11,885 | 837 | **u32** |
| 4 | `merlinAgent-Linux-arm64` | ELF | 11,534,460 | `0x526960` | 11,970 | 11,970 | 11,795 | 840 | u64 |
| 5 | `merlinAgent-Linux-x64` | ELF | 12,492,924 | `0x5F0C20` | 12,062 | 12,062 | 11,877 | 842 | u64 |
| 6 | `merlinCLI-Darwin-arm64` | Mach-O | 19,571,874 | `0x5B3440` | 16,056 | 16,056 | 15,838 | 907 | u64 |
| 7 | `merlinCLI-Darwin-x64` | Mach-O | 20,804,192 | `0x688200` | 16,135 | 16,135 | 15,911 | 909 | u64 |
| 8 | `merlinCLI-Linux-arm` | ELF | 19,183,912 | `0x6E67E0` | 15,939 | 15,939 | 15,740 | 915 | **u32** |
| 9 | `merlinCLI-Linux-arm64` | ELF | 19,017,586 | `0x5D6820` | 15,863 | 15,863 | 15,640 | 916 | u64 |
| 10 | `merlinCLI-Linux-x64` | ELF | 20,299,557 | `0x69BDA0` | 15,935 | 15,935 | 15,705 | 918 | u64 |

`[verified]` **ABSENT MAGIC: NONE. 10 of 10 carry a validated pclntab. Zero binaries in this set lack the structure.**

`[verified]` **TOTALS: agents 60,288 names · CLIs 79,928 names · COMBINED 140,216 names.**

`[inferred]` **NEW FINDING, previously invisible because the CLIs were never analysed at any layer: the CLI binaries carry ~32% MORE functions than the agents** (15,863–16,135 vs 11,970–12,167). `[inferred]` **The CLIs also expose 907–918 package prefixes versus the agents' 825–842 — roughly 10% more of the dependency graph. The CLI is the substantially richer binary, which is the opposite of what an "agent vs tool" naming suggests.**

`[inferred]` **The two 32-bit targets are exactly the two `Linux-arm` binaries** — `merlinAgent-Linux-arm` and `merlinCLI-Linux-arm` — consistent with `arm` being the 32-bit ABI and `arm64` the 64-bit one. `[inferred]` **This confirms the layout split is ABI-driven and not container-driven.**

---

## §7 T6 — WHAT THIS LANE GIVES, AND WHAT IT DOES NOT

`[verified]` **PCLNTAB GIVES IDENTITY, NOT BEHAVIOUR.**

`[verified]` **What was obtained:** 140,216 function **names**, their owning **package prefixes**, and the **table membership** of each. `[inferred]` **That is a symbol inventory. It is genuinely new: 10 artifacts that had no symbol layer at all now have a complete one, and the `merlinCLI*` set had none at any prior layer.**

`[verified]` **What was NOT obtained, and cannot be obtained this way:**

1. **No string was deobfuscated.** `[inferred]` The pclntab names functions; it does not decrypt, decode or transform a single literal. D110 §2's config strings were already plaintext; obfuscated strings elsewhere remain obfuscated.
2. **No function's BEHAVIOUR is known.** A name such as `agent.(*Agent).SetKillDate` states that a function exists and what it is called, **not what it does, what it validates, or whether it is ever reached.**
3. **No address was resolved to a name.** `[inferred]` The `funcoff`/`entryoff` fields were used to *locate* names in the table, but no mapping from a code address to a name was emitted and no call graph was built.
4. **No call relationship was recovered.** `[inferred]` pclntab carries function metadata, not edges. Reachability of the injection methods remains exactly as unknown as D95 §5.3 recorded.
5. **No new string, config, path or credential** was surfaced by this lane.

`[inferred]` **THE OVER-READ THIS SECTION EXISTS TO PREVENT:** `[inferred]` **"140,216 symbols recovered from cross-platform implants without a disassembler" is a statement about COVERAGE, and coverage is not comprehension.** `[inferred]` **D88's promoted standard applies one level down: instrumentability is not accuracy, and a complete symbol list is not an analysis.** `[inferred]` **The correct claim is narrow and it is still large: every previously unanalysed artifact now has a name-level index. Turning that index into understanding requires the behavioural work, which this lane does not do.**

---

## §8 APPENDIX A — CORRIGENDUM TO D110 §1.5 (do NOT edit D110; filed here)

`[verified]` **D110 §1.5 IS WRONG ABOUT THE SHAPE OF `02_BINARIES\`, AND THE CLAIM OF COMPLETE ENUMERATION IN IT IS FALSE.**

`[verified]` **D110 §1.5 stated that `02_BINARIES\` contains four files, and presented a four-row table of sizes. It does not contain four files at the top level.**

`[verified]` **The corrected shape, by enumeration including directories:**

```
02_BINARIES\
  havoc_BUILDFROM_SOURCE\   (DIR)
    README.md                                            307
  merlin\                   (DIR)
    merlinServer-Windows-x64.7z                   68,780,065
  sliver\                   (DIR)
    sliver-client_windows-amd64.exe               65,866,240
    sliver-client_windows-amd64.exe.minisig              326
```

`[inferred]` **D110 §1.5's four FILES and all four SIZES are correct. Every PATH in it is wrong** — D110 presented them as flat children of `02_BINARIES\`, and they are children of three named subdirectories. `[inferred]` **Three directories were omitted entirely, and with them the correct location of every file.**

`[inferred]` **ROOT CAUSE: `[IO.Directory]::GetFiles()` returns FILES ONLY. It cannot see a directory, and it does not recurse by default. D110 used it and then reported the result as a complete enumeration.** `[inferred]` **A census that walks files and ignores directories is not a census — and this is the SAME `Get-ChildItem -File` failure D110 §5 recorded as a probe hazard, committed by the report that recorded it.**

`[inferred]` **PROVENANCE LINK, SHARPENED NOT WEAKENED:** `[inferred]` **the 68,780,065-byte archive lives in `02_BINARIES\merlin\` — a directory named for the target — so the archive-to-extraction link D110 drew is now better located, not worse.** `[inferred]` **`sliver-client_windows-amd64.exe` is confirmed at 65,866,240 B in `02_BINARIES\sliver\`, independently corroborating C-08 §9's figure.**

`[inferred]` **D110's MerlIN ARTIFACT CENSUS IS NOT AFFECTED.** `[inferred]` **The 16 distinct binaries were enumerated from `05_TARGETS\merlin_extracted\` and `07_OUTPUT\extractions\`, and the `02_BINARIES\` files are the archive and the non-Merlin Sliver client — neither of which entered the count.** `[inferred]` **The defect is scoped to §1.5's description of `02_BINARIES\`.**

---

## §9 APPENDIX B — CORRIGENDUM TO D110 §1.5's SLIVER CLAIM, AND CROSS-REFERENCE TO D116

`[verified]` **D110 §1.5's IMPLICATION THAT `02_BINARIES\sliver\` DOES NOT EXIST WAS ITSELF THE ERROR.** `[inferred]` **The directory exists and holds the client `.exe` and its `.minisig`. The D96 script's hardcoded path — `02_BINARIES\sliver\sliver-client_windows-amd64.exe` — is therefore CORRECT, and no defect should be filed against it.**

`[inferred]` **HOW THIS WAS CAUGHT — and the control deserves the credit.** `[inferred]` **D110 §1.5's four-file enumeration was used to build a positive control for the pclntab scanner. The control's `Test-Path` returned `False`.** `[inferred]` **The control FAILING is what exposed the wrong conclusion: had the control silently succeeded or been skipped, the wrong "directory does not exist" claim would have shipped and D96's working script path would have been marked broken.** `[inferred]` **A failed control is not a failed task. It is the instrument doing its job.**

### §9.1 Cross-reference: two lanes, one finding

`[verified]` **A second lane independently established the same species of defect in D96.** `[inferred]` **D96 asserted a SERVER-ABSENCE over a directory it never enumerated — D96's only probe reads a single hardcoded path, the client `.exe`.**

`[inferred]` **TWO LANES, INDEPENDENTLY, FOUND THAT A NEGATIVE IN THIS CORPUS RESTS ON AN UNENUMERATED SCOPE:**

| lane | scope | defect |
|---|---|---|
| **D110/D112 (this lane)** | **`02_BINARIES` SHAPE** | Four files named as a complete enumeration; **three directories exist** and were invisible to `GetFiles`. |
| **D96 (sliver-diver lane)** | **`02_BINARIES` CONTENT** | Server-absence asserted over a directory whose content was **never enumerated**; one hardcoded client path was the only probe. |

`[inferred]` **These are the same defect at two levels — one miscounted the SHAPE of the root, the other asserted a NEGATIVE about its CONTENT.** `[inferred]` **Both are rule 15/rule 20 violations: a path you can name is not a population you have counted.** `[inferred]` **Cross-referenced to D116 for reconciliation.**

`[inferred]` **The compounding lesson:** `[inferred]` **D110's shape error was MEASURED this round precisely because a control was pointed at the same root for an unrelated reason.** `[inferred]` **The corpus's best current detector of unenumerated scope is an unrelated probe that happens to touch the same directory.**

---

## §10 Residual unknowns

| ID | Unknown | Severity | Probe |
|---|---|---|---|
| **R-112.1** | **No address-to-name mapping was produced.** `funcoff`/`entryoff` were consumed but no code-address index was emitted, so names cannot yet be attached to the existing Windows `C-0x` dumps. | **high** | Emit `entryoff`-indexed output and join against `C-05`/`C-06`. |
| **R-112.2** | **No call graph was recovered.** pclntab carries metadata, not edges. Reachability of any function — especially injection paths — is unchanged from D95 §5.3. | **high** | Requires disassembly; blocked by the dead Go analyzer per C-08 §6. |
| **R-112.3** | **No string was deobfuscated** (T6 item 1). The 140,216 names say nothing about literal content. | **high** | Separate lane; not a pclntab task. |
| **R-112.4** | **`parsed == nfunc` in all ten cases, yet `Read-GoName` cannot reject**, so the parse-count equality is not independent corroboration of name quality. Corroboration rests on §2.4's two-method cross-check only. | **medium** | Add a strict-name predicate (valid Go symbol charset) and re-measure a true reject rate. |
| **R-112.5** | **The 825–918 `pkgs` counts derive from a heuristic** (last `/` or last `.` of each name); nested-package names may split inconsistently. | **medium** | Re-derive with the `cuOffset` compilation-unit table instead of string heuristics. |
| **R-112.6** | **`12411`'s owning table was identified by position and shared bytes, not by name.** It is confirmed as shared read-only data; its semantic identity is unknown. | **low** | Map the surrounding blob against Go runtime tables. |
| **R-112.7** | **D110 §1.5's four sizes were not re-verified in their correct paths** beyond `merlin\` and `sliver\`; `havoc_BUILDFROM_SOURCE\README.md` at 307 B is newly visible. | **low** | Confirm all four at full paths. |
| **R-112.8** | **D95 §5 remains annotated-as-unverified rather than corrected.** No edit was made to D95 per the Lead's instruction. | **low** | Lead decides whether to annotate in place. |

---

## §11 Summary

`[verified]` **T1 — R-110.9 CLOSES: CLAIM STANDS, EVIDENCE INVALID.** The rebuilt detector is proven live on two controls — **D41 = 2** (matching the two documented intentional instances) and **D61 = 3** (superseding last round's wrong "4"). **D95 measures clean at 33,431 B: mojibake 0, U+FFFD 0, both literals 0, strict UTF-8 valid.** `[inferred]` **But D95's own §5 probe could not match any input, so its published "0 hazards" was unfalsifiable by its instrument. D95 was right without having measured it. No textual correction needed; §5 must be marked unverified-by-measurement.**

`[verified]` **T2 — THE LANE IS OPEN.** All five non-Windows agents parsed: **60,288 names**, bases `0x500B40`, `0x5D9460`, `0x64A1E0`, `0x526960`, `0x5F0C20`. `[inferred]` **The anchor is the magic plus `pad1==0 && pad2==0` — NOT a name-table-tail parse; claiming otherwise would overstate the instrument.** Two layouts (`u64`/`u32`) split on `ptrSize`. `[inferred]` **`bad=0` is explicitly withdrawn as a quality metric; corroboration is the two-method cross-check giving a stable 299–302 `merlin-agent` subset across five builds.**

`[verified]` **THE DEFECT CLASS — a rule from the majority case deletes the minority case, silently, and the deletion looks like absence.** The strict rule `minLC==1 && ptrSize==8` **rejects exactly the three ARM/32-bit targets that appeared table-less**; `minLC` is instruction-length alignment (1 on x86, **4 on ARM**) and `ptrSize` is 8 or 4 by ABI. `[inferred]` **Same class as the shape-filter that anchored `u64 12411` in three unrelated binaries — a shared read-only constant, proven shared by byte-identical surroundings.** `[inferred]` **Cheap falsification test recorded: if a probe returns the same value for targets that must differ, it is reading a shared constant.**

`[verified]` **T3 — CONFIRMED BY ENTRY COUNT.** `.reloc` **121,856 B in both**, **327 blocks in both**, **`DIR64` fixups 59,257 in both**. `[inferred]` **The genuine relocation set is identical in size and type; only VALUES move. The 62,896 differing bytes are shifted fixup targets, not created fixups. The 2-entry `ABSOLUTE` delta (153 vs 151) is block padding, not a fixup.**

`[verified]` **T4 — 19/20 UNIVERSAL, EXACTLY ONE EXCEPTION: `github.com/awgh/rawreader`, 2/7, builds `W-x64` and `W-x64-Dbg`.** `[inferred]` **Its presence in Debug as well as release shows the condition is OS, not build mode.** The "18/20" figure is corrected, and the cause of that error is itself recorded: a row was corrected without re-counting the denominator.

`[verified]` **T5 — 10 OF 10, ZERO ABSENT MAGIC, 140,216 NAMES TOTAL** (agents 60,288 · CLIs 79,928). `[inferred]` **New finding: the CLIs carry ~32% more functions and ~10% more packages than the agents — the richer binary is the tool, not the implant.**

`[verified]` **T6 — PCLNTAB GIVES IDENTITY, NOT BEHAVIOUR.** `[inferred]` **No string deobfuscated, no behaviour known, no address resolved, no edge recovered. Coverage is not comprehension, and "140,216 symbols" must not be read as analysis.**

`[verified]` **APPENDIX A — D110 §1.5 CORRIGENDUM (D110 not edited): `02_BINARIES\` is 3 DIRECTORIES + 4 nested FILES, not four flat files.** All four sizes correct; **every path wrong**; three directories invisible to `[IO.Directory]::GetFiles`. **D110's 16-binary Merlin census is unaffected.** `[verified]` **APPENDIX B — D110's implication that `02_BINARIES\sliver\` is absent was the error; the directory exists and D96's hardcoded path is correct.** `[inferred]` **Caught because the control returned `False` — a failed control exposing a wrong conclusion is the instrument working.** `[inferred]` **Cross-referenced to D116: two lanes independently found that a negative in this corpus rests on an unenumerated scope — D110 miscounted the root's SHAPE, D96 asserted a negative about its CONTENT.**

**Next free report number after D112 is `D116`.**
