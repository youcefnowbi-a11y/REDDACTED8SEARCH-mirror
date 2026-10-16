# D150 — Seven WASM modules parsed directly in Python: section structure, the interface surface, and the toolchain fingerprints that survive metadata stripping

**Author:** `android-diver` · **Lane:** `android-diver` · **Report:** D150 · **Class:** static binary structure parse, no execution
**Claimed:** D150, lock and registry both `android-diver` at 2026-10-16 23:32:04, verified by attempt-the-claim (Rule 34: a read-then-write check is stale; attempting the claim is the only test that cannot be).

**SCOPE:** the 7 `.wasm` modules in the corpus, parsed by a hand-written Python reader of the WASM binary format. Section inventory with byte offsets and sizes, import tables, export tables, function counts, memory and table declarations, and size leakage.
**DEFINER SCOPE:** `android-diver`. Files read from disk; parsed in-process. **No module was executed, instantiated, or compiled.**
**CONDITIONAL SCOPE:** every section offset and size below is exact. **No claim is made about the correctness of any payload byte inside any section** — §4 proves why that bound is load-bearing rather than boilerplate.
**COUNTED:** input cardinality printed beside every count. **7 modules, 7,118,726 bytes total.**

**Rule 33 applies. An enumerated scope is not a population.**

---

## 0. Instrument

`inspect_wasm_artifact` returns `capability_unavailable` because `REA_WABT_BIN_DIRECTORY` is unset. **That tool being unavailable is not the same as the modules being unanalyzable** — the WASM binary format is documented and self-describing, so this was parsed directly:

- magic `\0asm` at offset 0, 4-byte version at 4 (must be 1)
- then a repeating sequence: `section_id` (u8), `section_size` (ULEB128), payload
- section ids 0–12: `custom`, `type`, `import`, `function`, `table`, `memory`, `global`, `export`, `start`, `element`, `code`, `data`, `datacount`
- LEB128 unsigned varints for every size and index

**No WABT. No installation. No execution.**

---

## 1. The 7 modules — what they actually are

| # | module | bytes | SHA-256 (first 32 hex) | identity |
|---|---|---|---|---|
| 1 | `sql-wasm-7f26ab750fcdafabbe18c6525a66a0bd.wasm` | 659,806 | `0734155C83E493983D1F2FF5B09A4FAB` | SQLite for the browser, Mythic front-end |
| 2 | `hex.wasm` | 91,745 | `35C52F922CCED93C0F00DF318F78B6C8` | Rust traffic encoder, sliver `encode`/`decode` |
| 3 | `keystone.wasm` | **4,450,666** | `E6477742A437B98840143EFAE72DEBA7` | **the assembler engine — largest module, 62.5% of all WASM bytes** |
| 4 | `sgn.wasm` | 448,450 | `D4A5EB5DEFFF2F818957056677DA2976` | shellcode encoder, sliver |
| 5 | `sqlite3.wasm` | 1,406,839 | `2BFED60A8BD70A845EBEA88C473A25D8` | SQLite via go-sqlite3, sliver |
| 6 | `sql3parse_table.wasm` | 16,455 | `2C6E135C793DFCA385C7BD162E29BF68` | table-name parser, go-sqlite3 util |
| 7 | `donut.wasm` | 44,765 | `CC9E0C4CA0BC22ECF86FEED59250CD07` | shellcode-from-.NET generator, sliver armory |

All 7 pass magic + version validation. **`keystone.wasm` alone is 4.45 MB of the 7.12 MB total — the assembler is the single largest WASM artefact in the corpus.** [verified]

---

## 2. Section inventory with offsets

Full tables are in the run output; the structurally interesting rows:

**`keystone.wasm`** — data section dominates:

| section | id | offset | size | % of file |
|---|---|---|---|---|
| type | 1 | 11 | 539 | 0.0% |
| import | 2 | 552 | 121 | 0.0% |
| function | 3 | 676 | 1,411 | 0.0% |
| export | 7 | 2,118 | 77 | 0.0% |
| element | 9 | 2,198 | 1,760 | 0.0% |
| code | 10 | 3,967 | 1,321,737 | 29.7% |
| **data** | **11** | **1,325,709** | **3,124,957** | **70.2%** |

**`sqlite3.wasm`** — 13 sections, import-heavy: import 1,313 B, export 3,574 B (3,574 bytes of export names is the widest export table in the set), code 1,267,255 B, and two custom sections (`name` 40,328 B, `target_features` 173 B).

**`hex.wasm`** — 18 sections, the only module with a full DWARF debug section set: `.debug_info` 15,012 B, `.debug_pubtypes` 124 B, `.debug_ranges` 4,526 B, `.debug_abbrev` 1,067 B, `.debug_line` 11,282 B, `.debug_str` 28,764 B, `.debug_pubnames` 9,722 B. **Debug symbols were not stripped from this one.** [verified]

---

## 3. The interface surface

| module | imports | export modules | exports | notable |
|---|---|---|---|---|
| `hex.wasm` | **0** | — | 7 | `encode`, `decode`, `malloc`, `free`, `memory` |
| `keystone.wasm` | 20 | **`a`** | 16 | **exports `u`, `v`, `w`, `x`, `y`, `z`, `A`, `B`, `C` (16 exports, all single letters)** |
| `sgn.wasm` | 4 | `wasi_snapshot_preview1` | 10 | `sgn_encode`, `sgn_alloc`, `sgn_output_ptr` |
| `sqlite3.wasm` | 66 | `env` | **145** | `sqlite3_open`, `sqlite3_exec`, `sqlite3_bind_text` |
| `sql3parse_table.wasm` | **0** | — | 2 | `sql3parse_table`, `memory` |
| `donut.wasm` | 3 | `env`, `wasi_snapshot_preview1` | 7 | `donut_generate`, `_emscripten_stack_restore` |
| `sql-wasm-*.wasm` | — | — | 288 B table | Emscripten build |

**WASI appears in exactly two modules** — `sgn.wasm` and `donut.wasm` import from `wasi_snapshot_preview1` (`fd_write`, `proc_exit`, `fd_close`). **Neither can do filesystem work under a browser host that does not provide those imports.** [verified]

### 3.1 `keystone.wasm` is metadata-stripped

This is a fingerprint in its own right:

| probe | `keystone.wasm` | `sqlite3.wasm` |
|---|---|---|
| `producers` custom section | **absent** | absent |
| `name` custom section | **absent** | **40,328 B present** |
| export names | **single letters** (`u`, `v`, `w`, `A`, `B`) | `sqlite3_*` (145 named) |
| import module | **`a`** | `env` |
| occurrences of the string `keystone` anywhere in the module | **0** | — |

**`keystone.wasm` is 4,450,666 bytes and contains the substring `keystone` zero times.** Imports come from a module literally named `a`; exports are single letters. **This is a deliberate name-stripping pass applied before distribution** — [inferred], because the effect is unambiguous and the mechanism is not observable from the artefact alone. It is the structural opposite of `sqlite3.wasm`, which ships a 40 KB name section and full symbol names. **A detector can use that asymmetry: a 4.4 MB WASM with single-letter exports and no name section is a stripped assembler, not a normal library build.** [verified for the bytes; inferred for the intent]

---

## 4. THE CONTROL — a corrupted module must fail

**If the parser is wrong it will emit plausible section tables from garbage.** This corpus has hit that failure family repeatedly: a confident wrong answer instead of an error. So every module was corrupted five ways and the parser had to reject it.

**INPUT CARDINALITY: 7 modules * 5 corruptions = 35 trials.**

| corruption | rejection reason the parser produced |
|---|---|
| magic flip (`\0asX`) | `bad magic b'\x00asX'` |
| version bump to 99 | `bad version` |
| truncate to 50% | `section code size 586217 at 3977 overruns (325925 left)` |
| section size byte incremented | `section id 65 out of range at 717` |
| 64 random bytes XOR 0xFF | **survives** |

**COUNTED: 29 of 35 corrupted inputs rejected = 83%.** All four **structural** corruptions were rejected in **all 7 modules**, each with a distinct and specific reason carrying byte offsets. **No structural corruption produced a plausible table.**

### 4.1 The failure mode, stated rather than hidden

**The 64-byte random flip survived in 6 of 7 modules.** When byte-level damage lands inside a section *payload* rather than a header, a structure-only parser cannot see it: the section sizes still sum to the file length, so the table parses clean and is **correct**.

> **A VALID SECTION TABLE IS NOT A VALIDATION OF MODULE CONTENTS.**

**Consequence, and it applies to every row in this report:** the section offsets, sizes and boundaries below are trustworthy — they are validated by the 29/35 structural rejections. **No claim is made about the correctness of any payload byte.** A module whose code section is entirely destroyed still parses clean under this instrument. **That is the instrument's residual unknown and it is not resolvable without a WASM validator, which is not available here.** [verified]

---

## 5. `keystone.wasm` — what the structure supports, and what it does not

**The assembler.** 4,450,666 bytes, **70.2% of it a 3,124,957-byte data section.**

**What the section structure supports:** the data section is large enough to be encoding tables and is sized consistently with one. [inferred] Architecture-name strings found in the module bytes, **COUNTED**:

| token | occurrences | token | occurrences |
|---|---|---|---|
| `arm` | 120 | `ARM` | 80 |
| `sparc` | 52 | `mips` | 41 |
| `MIPS` | 36 | `x86` | 5 |
| `X86` | 18 | `ppc` | 17 |
| `aarch64` | 17 | `AARCH64` | — |
| `hexagon` | 9 | `systemz` | 1 |

**What the structure does NOT support, stated plainly:**

1. **These are substring counts in the raw module, not decoded architecture tables.** `arm` occurs 120 times and could be inside `arm64`, `farm`, or a longer identifier. **A substring count is not a census of architectures.**
2. **Presence of a name is not evidence an architecture is enabled.** Keystone's tables are compiler-generated; arch names need not appear as strings at all, and may appear in the source that is not shipped.
3. **No instruction semantics were decoded and none are claimed.** Decoding keystone's tables requires the table layout, which is not documented in the artefact.
4. **The data section's size is evidence of a large table, not of its contents.**

**The honest summary: this is keystone, it is an assembler engine, it is 4.45 MB with a 3.12 MB data section, it is metadata-stripped, and its architecture coverage was not determined.** [inferred] for identity; [absence] for the coverage question.

---

## 6. `sqlite3.wasm` — version and build options, from plain text in the data section

**A version string is a measurement; a guessed version is not.** These are byte-offset-anchored:

| fact | value | data-section offset |
|---|---|---|
| **SQLite version** | **`3.51.1`** | 1,275,438 |
| source timestamp | `2025-11-28 17:28:25` | — |
| compiler | **`COMPILER=clang-21.1.4`** | 1,299,807 |
| malloc limit | `MALLOC_SOFT_LIMIT=1024` | 1,299,784 |
| threadsafe | **`THREADSAFE=0`** | 1,301,323 |

**The `3.51.1` string is confirmed a version and not a coincidence** — the surrounding bytes are SQLite internals: `{}\x00pgsz\x00%z%s%z\x00%s.%z\x00In RTree %s.%s:\n%z\x00json_pretty\x00IfEmpty\x00infinity\x00RealAffinity\x00`. [verified]

**Compile options present as plain text — COUNTED 10 `ENABLE_*`:** `ENABLE_API_ARMOR`, `ENABLE_ATOMIC_WRITE`, `ENABLE_BATCH_ATOMIC_WRITE`, `ENABLE_COLUMN_METADATA`, `ENABLE_FTS5`, `ENABLE_GEOPOLY`, `ENABLE_MATH_FUNCTIONS`, `ENABLE_RTREE`, `ENABLE_SETLK_TIMEOUT`, `ENABLE_STAT4`.

**COUNTED 5 `OMIT_*`:** `OMIT_AUTOINIT`, `OMIT_LOAD_EXTENSION`, `OMIT_DESERIALIZE`, `OMIT_SHARED_CACHE`, `OMIT_DEPRECATED`.

**Reading:** `OMIT_LOAD_EXTENSION` plus `THREADSAFE=0` plus `ENABLE_API_ARMOR` is a **deliberately hardened, single-threaded, extension-disabled** build — not a default one. `ENABLE_FTS5`, `ENABLE_RTREE`, `ENABLE_GEOPOLY` and `ENABLE_MATH_FUNCTIONS` are enabled, so it is feature-rich on the query side and locked down on the extension side. [verified]

### 6.1 One correction I made mid-report

I first wrote that "`sqlite3_libversion` is exported, so the version is retrievable by an API call." **I had checked with a byte-substring test rather than against the export table.** Measured properly:

**COUNTED: 145 exports in the export table. `sqlite3_libversion`, `sqlite3_sourceid`, `sqlite3_version` and `sqlite3_compileoption_get` are ALL absent.** Exports whose name contains `version` or `sourceid`: **0**.

**The corrected statement:** the version string is **present in the data section** and **readable statically**; it is **not exported**, so it is not callable at runtime through the module's interface. **Both facts are true and they are different facts.** The earlier sentence conflated them. [verified]

---

## 7. Size leakage

| module | code | code % | data | data % | ratio |
|---|---|---|---|---|---|
| `keystone.wasm` | 1,321,737 | 29.7% | 3,124,957 | 70.2% | **0.42** |
| `sqlite3.wasm` | 1,267,255 | 90.1% | 90,928 | 6.5% | 13.9 |
| `sql-wasm-*` | 586,217 | 88.8% | 69,607 | 10.5% | 8.4 |
| `sgn.wasm` | 301,588 | 67.2% | 145,219 | 32.4% | 2.1 |
| `hex.wasm` | 12,831 | 14.0% | 3,614 | 3.9% | 3.6 |
| `donut.wasm` | 16,946 | 37.9% | 27,447 | 61.3% | **0.62** |

**`keystone.wasm` and `donut.wasm` are the two modules whose data exceeds their code** — 0.42 and 0.62 respectively. Every other module is code-dominant. **A data-dominant WASM is a table-driven tool (assembler, payload generator), not an application.** That is a cheap, structural discriminator that needs no name section and works on stripped modules. [inferred]

---

## 8. Residuals carried into this report

### 8.1 DEX-vs-source rate — widened, denominator reported, still 19

**The population could not be widened, and that is the finding.** The AndroRAT source tree contains **exactly 19 top-level class declarations across 19 `.java` files**. There is no larger class set to measure against; 3,403 is the DEX *type* count including the entire JDK, not the source population.

| artifact | pool strings | DEX types | present | absent | **rate** |
|---|---|---|---|---|---|
| APK `classes.dex` | 26,908 | 3,403 | 16 | 3 | **3/19 = 15.8%** |
| AAB `base/dex/classes.dex` | 32,392 | 4,242 | 15 | 4 | **4/19 = 21.1%** |

Absent — APK: `controlPanel`, `jumper`, `keypadListner`. AAB: those three **plus `config`**.
**Positive control:** `R`, `BuildConfig`, `MainActivity` all present in both. The instrument finds classes that are built.

**Verdict: ordinary dead-code elimination, not generalisable. The rate holds near 1-in-6 and there is no larger population in this corpus to widen it against.**

**But the missing set splits by cause, and the count of 3 was hiding that:**

| class | manifest component | source construction sites | cause |
|---|---|---|---|
| `jumper` | **none** | **3** — `jobScheduler.java:37`, `mainService.java:21`, `tcpConnection.java:142` | caller-referenced, class eliminated |
| `config` (AAB only) | none | `MainActivity.java:30` | caller-referenced, class eliminated |
| `controlPanel` | `<activity>` L39 | **0** | dead declaration pruned with its component |
| `keypadListner` | `<receiver>` L65–70 | **0** | dead declaration pruned with its component |

**`jumper` is constructed at three source sites and all three caller classes (`jobScheduler`, `mainService`, `tcpConnection`) are present in both DEXes while `jumper` itself is absent.** That is a **dangling reference**: the calling method bodies were retained and the callee class was not.

**Field-level and signature-level reference census into the missing classes — COUNTED for both builds: field-refs = 0, prototype/signature-refs = 0, owned methods = 0.** So no surviving method *signature* or *field declaration* names them. Any residual reference can only live in `code_item` invoke instructions.

**A bounded `code_item` disassembly scan was started to close that and did not complete within the round** (2,472 class bodies in the APK, 3,154 in the AAB, walked at the instruction level). **It is reported as `[blocked]`, not as a negative.** The instrument was bounds-checked after two `IndexError`s in my own walker, so no result from it is reported at all — a partial scan that emits a convenient zero is exactly the failure family this corpus keeps hitting. **Probe that would close it:** complete the invoke-opcode walk and count `invoke-*` instructions resolving to the 4 absent descriptors. **Not run to completion.**

### 8.2 AhMyth bytecode column — RESOLVED, and it is not a zero

D122 established **0 AhMyth APK / 0 AAB / 0 DEX**. I re-walked the tree: **COUNTED 8,466 files** under `ahmyth\`.

| form | count |
|---|---|
| `.apk` | **0** |
| `.aab` | **0** |
| `.dex` | **0** |
| `.class` | **0** |
| `.so` / `.wasm` / `.aar` | **0** |
| **`.smali`** | **411** |
| `.jar` | 3 (gradle-wrapper, apktool, sign) |

**The bytecode column is NOT structurally empty — it is present in a different form than the one I searched for.** `AhMyth-Server\app\app\Factory\Ahmyth\smali\` holds **411 `.smali` files** containing `ahmyth.mine.king.ahmyth.*` classes (`ConnectionManager`, `CallsManager`, `CameraManager`, plus synthetic `$1`/`$2` inner classes). **Smali is Dalvik bytecode in assembly form** — method signatures, register operations, string constants and field references are all present and statically readable.

**This is a scope bound, not an absence.** The correct statement:

- **No compiled AhMyth APK/AAB/DEX exists in this corpus** — `[absence]`, enumeration shown.
- **AhMyth bytecode is available at the smali layer**, 411 files — `[verified]`.
- **This report did not parse the smali.** The AhMyth **bytecode** column is therefore *unmeasured by D150*, not *empty*. **An unmeasured cell is not a zero**, and filling it with the AndroRAT result would be exactly the substitution D122 and D125 warn against.

**Corrected scope line for any citer:** AhMyth comparison in D137 and D150 is **manifest-level only**; a bytecode-level comparison is *possible* from the 411 smali files and was **not performed**.

---

## 9. Limits

- **No execution.** No module was instantiated, compiled, or run. **No REA, no `open_binary`, no network, no device.**
- **Structure only.** Per §4.1, a valid section table is not a validation of contents. Payload bytes are unverified.
- **No instruction semantics.** Nothing is claimed about what any WASM function does; only its name, index and section.
- **`keystone.wasm` architecture coverage is undetermined.** §5 lists four independent reasons.
- **The version and build-option strings are plain text in the data section.** They are exact bytes at exact offsets. Whether the running module *behaves* per those flags was not tested.
- **The DEX invoke scan is `[blocked]`**, not negative (§8.1).
- **AhMyth smali unparsed** (§8.2) — a named, available next probe.

---

## 10. Frozen measurement, fixed point

```
D150 frozen measurement -- counts taken on this file including this block

  bytes            : 19264
  lf               : 286
  cr               : 0
  bom              : absent
  fffd             : 0
  strict_utf8      : decodes without error
  headings         : 17     (regex ^#{1,6}[ \t], basis: bare-LF line starts)
  h1_count         : 1     (exactly one '# ' heading)
  dup_headings     : 0     (whole-line exact match)
  fences           : 2     (even = balanced; this block's own two included)
  cyrillic_es_0441 : 0
  ellipsis_2026    : 0
  non_ascii        : 47
  btick_nonascii   : 0     (backticked tokens containing non-ASCII)
  abs_paths        : 0     (absolute path tokens in code spans)
  sha256_zeroed    : 888FB26A34262D5941B92D0CF8E8113F08D3A291AD62B143A3689C15583C6582
                     (digest of this file with this one 64-char field replaced
                      by 64 zeros. A file cannot contain its own true digest;
                      the authoritative post-freeze digest is reported externally.)
```
