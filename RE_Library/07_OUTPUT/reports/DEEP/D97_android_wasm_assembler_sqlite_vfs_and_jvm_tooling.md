# D97 — The WASM layer, opened: a validated parser, an assembler engine with five unmapped exports, and a SQLite that cannot touch the filesystem

**Lane:** android-diver
**Round:** 24
**Scope:** the two most interesting non-native binaries in the corpus, plus a bounded census of vendored JVM tooling.
**Method files read first:** `C-00_binary_layer_method_and_merlin_confirmation.md` (method) and `C-08_ghidra_census_merlin_suite_symbol_asymmetry_and_toolchain_failures.md` (the seven recorded toolchain failures).
**Constraints honoured:** nothing executed. No network. No REA `open_binary`. All paths quoted — the repo path contains a space.
**Line-count convention:** LF count by `[System.IO.File]::ReadAllText(...) -split "\`n"`, minus the trailing newline. **CR measured separately and reported.** Stated so D97 is comparable to D87/D79/D100.

---

## §0 — The headline

**1. WABT is unavailable. That is the finding, and it is recorded rather than worked around with a guess.**

`inspect_wasm_artifact` was **invoked**, not presumed, and returned:

```
code    : capability_unavailable
category: unsupported_provider
message : REA_WABT_BIN_DIRECTORY must be an absolute tool directory.
          Supply WABT 1.0.42 via absolute REA_WABT_BIN_DIRECTORY; REA does not install tools.
```

`REA_WABT_BIN_DIRECTORY` is set to the **empty string**. All of `wasm2wat`, `wasm-objdump`, `wasm-validate`, `wat2wasm`, `wasm-strip`, `wasm-interp`, `wasm-tools` are **absent from PATH** (`where.exe`), absent from every probe directory, and no Python wasm library (`wasmtime`, `pywasm`, `lief`) is installed. **Per the round-24 instruction, the unavailable tool is recorded as the finding. The fallback is a hand-written static section parser.**

**2. The fallback parser was validated against a known figure BEFORE any of its results were used.**

> **All seven `.wasm` modules in the corpus walk EXACTLY to end-of-file (residual 0, every one).**
> **Their sizes sum to 7,118,726 B — reproducing `C-00 §1`'s recorded `.wasm` total exactly.**

**Reproducing a figure measured by a different instrument, by a different lane, in a different report, is what makes this parser's other numbers believable.** A parser with an off-by-one in its length-prefix reader would not sum to the same total.

**3. `keystone.wasm` is an Emscripten-compiled Keystone 0.9 assembler engine, name-stripped, with FIVE exports the Go wrapper never maps.**

**4. `sqlite3.wasm` cannot reach the filesystem or the network through its own import surface.** All 66 imports are `env`-scoped `go_*` callbacks; **zero** filesystem and **zero** network primitives exist in the module itself. This is the security answer, and it is a materially different object from an embedded SQLite that can open files.

**5. The two `sign.jar` files are unrelated programs sharing a filename.** A NAME-IS-NOT-A-MEASUREMENT specimen at the toolchain layer.

---

## §1 — Instrument: the parser, and the validation that licenses it

### 1.1 What was written, and what it does and does not do

A static WASM section parser (Python 3.11.9, **no third-party libraries**) that reads:

- the 8-byte header (magic `00 61 73 6d`, version);
- every section header — **section id byte + LEB128 length** — and walks to EOF;
- the `type`, `import`, `function`, `table`, `memory`, `global`, `export` sections;
- `custom` sections by name, including the `name` section's function-name subsection.

**It does NOT decode function bodies.** It reads the `code` section's extent but not its bytecode. **No disassembly, no semantics, no behaviour is claimed anywhere in this report.** Everything below is *structure and interface*, which is exactly what a section parser can honestly deliver.

### 1.2 The validation gate — the strongest evidence in this report

**Acceptance criterion, stated before use:** every module must satisfy `walk_end == file_size` with the magic confirmed.

```
keystone.wasm          size= 4,450,666  sections=11  walk_end= 4,450,666  EXACT=YES
sqlite3.wasm           size= 1,406,839  sections=13  walk_end= 1,406,839  EXACT=YES
sgn.wasm               size=   448,450  sections=10  walk_end=   448,450  EXACT=YES
donut.wasm             size=    44,765  sections=10  walk_end=    44,765  EXACT=YES
sql3parse_table.wasm   size=    16,455  sections= 9  walk_end=    16,455  EXACT=YES
hex.wasm               size=    91,745  sections=18  walk_end=    91,745  EXACT=YES
mythic sql-wasm        size=   659,806  sections=11  walk_end=   659,806  EXACT=YES
                       ------------------------------------------------
                       TOTAL   7,118,726 B      <- C-00 §1 records 7,118,726 B
```

**Seven for seven exact, and the total matches a figure this lane did not produce.** [verified]

**This is the same acceptance form D87 used for AXML** (`walk exhausts at EXACTLY chunkStart+chunkSize`). **The bound discriminates because the total is fixed by the file, not by the reader.**

### 1.3 One arithmetic error in my FIRST pass, and why it is reported

My initial section table printed `section payload total = 4,450,628 (+8 = 4,450,636) vs file 4,450,666 [MISMATCH]` — **a 30-byte discrepancy.** The parser was correct; **my reporting arithmetic was wrong.**

**A WASM section's on-disk cost is `1 (id) + len(LEB128 size) + payload`.** There are 11 sections, so the header bytes total 30 — and `8 + 4,450,628 + 30 = 4,450,666`. Exact.

**The instructive part is how the error presented.** The mismatch surfaced as a *clean, specific, plausible* 30-byte gap — the kind of number a reader would accept as trivia. **Had I not chased it, I would have shipped a correct parser with a wrong stated total, and the wrong total would have been the only auditable number in the table.** [self-corrected]

**Also worth recording:** the `data` section's LEB128 length is **4 bytes** (`dd dd be 01` = 3,124,957). A single-byte length reader would truncate the section and overrun the file. **The parser's exact-EOF walk is what proves it read the long form correctly.**

---

## §2 — (A) `keystone.wasm` — the assembler engine

### 2.1 Identity

| property | value |
|---|---|
| path | `01_SOURCE_c2\sliver\vendor\github.com\moloch--\go-keystone\wasm\keystone.wasm` |
| **SHA-256** | **`E6477742A437B98840143EFAE72DEBA7B42C7AFC8C3D41A0C0D19C435A4E9591`** |
| **bytes** | **4,450,666** |
| version | 1 |
| sections | 11 |
| types | 65 |
| declared functions | 1,409 |
| table | funcref, min 984 |
| **memory** | **min 311 pages = 20,381,696 B (19.4 MiB) · max 32,768 pages = 2,048 MiB** |
| exports | 16 (15 func + 1 mem) |
| imports | 20 (all func) |
| **custom sections** | **NONE** |

**Zero custom sections means zero symbol names.** Everything the module exports and imports is a **single letter**. [verified]

### 2.2 The complete interface as measured from the BINARY

**Exports (16):**
```
u  [mem ] idx=   0
v  [func] idx=1428      H  [func] idx=1206
w  [func] idx=1227      I  [func] idx=1167
x  [func] idx=1220      J  [func] idx=1160
y  [func] idx=1226      A  [func] idx=1224
z  [func] idx=1225      B  [func] idx=1223
C  [func] idx=1222      D  [func] idx=  50
E  [func] idx=1221      F  [func] idx=  42
G  [func] idx=  20
```

**Imports (20), all from module `a`:**
```
a→type  4   b→type  1   c→type  0   d→type  1   e→type  3
f→type  1   g→type  1   h→type  2   i→type 44   j→type 35
k→type 45   l→type 46   m→type  1   n→type  1   o→type  1
p→type  3   q→type  3   r→type  3   s→type 19   t→type  0
```

### 2.3 The Rosetta stone — `func_map.go` binds every letter

**The Go wrapper in the same vendor directory carries a hand-written mapping table**, with the author's own explanation:

> *"I have tried to adjust the parameters for compiling, but I still can't solve the confusion of import and export function names, so I have to manually configure the mapping table of function names. Fortunately, the mapping relationship of these function names does not seem to change easily."* — `func_map.go` L3–9

**Imports (20/20):**
```
a=_cxa_throw    b=_fd_fdstat_get  c=_fd_close      d=_syscall_lstat64   e=_syscall_newfstatat
f=_syscall_stat64 g=_syscall_fstat64  h=_exit       i=_fd_pread          j=_fd_seek
k=_mmap_js      l=_munmap_js      m=_environ_get   n=_environ_sizes_get o=_syscall_getcwd
p=_syscall_openat q=_fd_write     r=_fd_read       s=__abort_js         t=_emscripten_resize_heap
```

**Mapped exports (10):**
```
A=_ks_open  B=_ks_close  C=_ks_option  D=_ks_free  E=_ks_asm
F=_malloc   G=_free      w=_ks_version x=_ks_errno y=_ks_strerror
```

### 2.4 THE CROSS-CHECK — two independent channels agreeing

**I compared my binary parse against `func_map.go` programmatically:**

```
IMPORTS   binary=20   source=20
  binary-only : []          source-only : []
  MATCH: True

EXPORTS   binary_func=15   source_mapped=10
  binary-only : ['H', 'I', 'J', 'v', 'z']     <- the five UNMAPPED
  source-only : []
  source 10 mapped are ALL present in binary: True
```

**20/20 imports and 10/10 mapped exports agree, in both directions, with zero discrepancy.** That agreement is what makes the five remainder a **finding** rather than a parser artifact. [verified]

### 2.5 THE FINDING — five exports the source map does not cover

**`H` (idx 1206), `I` (idx 1167), `J` (idx 1160), `v` (idx 1428), `z` (idx 1225).**

**What I can state:**
- These five are **named exports of the module** — they are reachable through the WASM export table and any embedder can call them.
- They are **not mapped in `func_map.go`**, which maps exactly ten.
- The Go wrapper therefore **never calls them**, and their existence is invisible at the source level.

**What I cannot state:** **what they do.** A name is not a measurement — and here there is not even a name, only a letter. **I did not decode function bodies, so I have no basis to claim semantics, and I will not infer them from index position or from the fact that they sit near `_ks_*`.**

**The precise characterisation:** the source-level mapping is **incomplete**, not the functions **undocumented**. Those are different claims, and only the first is supported by a name appearing in an export table while being absent from a hand-maintained constant block.

**Why this matters to the corpus:** the mapping table's own comment concedes it is manual and fragile — *"I have to manually configure"*, *"does not seem to change easily."* **A hand-maintained symbol map that already omits five exports of the artifact it describes is exactly the D53/D64 pattern: a pipeline that works until the artifact changes underneath it, with nothing validating the correspondence.** Rebuilding the `.wasm` with different Emscripten settings would silently re-letter everything — and the failure mode would be a **wrong assembler call**, not an error. [inferred, mechanism]

### 2.6 Why an implant shipping an assembler is load-bearing

**The capability the module provides, from the bound names, is a full multi-architecture machine-code assembler** — `const.go` enumerates `ARCH_ARM ARM64 MIPS X86 PPC SPARC SYSTEMZ HEXAGON EVM RISCV` (11 targets), 17 mode flags, 6 syntax dialects (`INTEL ATT NASM MASM GAS RADIX16`), and **52 distinct error codes** for assembly failures.

**It is instantiated in an interpreter, not a JIT compiler:** `wazero.NewRuntimeConfigInterpreter()` with the source comment **`// prevent generate RWX memory`**. [read]

**That comment is the whole design rationale, and it is worth naming:** an implant that assembles at runtime normally needs a writable-executable page, which is both a security-product flag and a hard-blocked allocation on hardened targets. **Running the assembler in a WASM interpreter keeps the assembled bytes in ordinary data memory.** The capability is retained while the RWX pattern is avoided. [inferred from source comment + config]

**Bounded:** `C-00 §1` records 7 `.wasm` files; I enumerated and validated all 7. **`keystone.wasm` is the largest and the only one that is a general-purpose assembler.**

---

## §3 — (B) `sqlite3.wasm` — what the VFS actually requires

### 3.1 Identity

| property | value |
|---|---|
| path | `01_SOURCE_c2\sliver\vendor\github.com\ncruces\go-sqlite3\embed\sqlite3.wasm` |
| **SHA-256** | **`2BFED60A8BD70A845EBEA88C473A25D81B11655D6853BCE86B070A78ECFB86FA`** |
| **bytes** | **1,406,839** |
| version | 1 |
| sections | 13 |
| types | 59 |
| declared functions | 1,601 |
| table | funcref, min 589 |
| memory | min 5 pages, **no declared maximum** (grows on demand) |
| **exports** | **145 (144 func + 1 mem)** |
| **imports** | **66, ALL from `env`, ALL func** |
| custom sections | **`name` (40,328 B)** · `target_features` (173 B) |

### 3.2 THE SECURITY ANSWER

> **All 66 imports are `env`-scoped `go_*` callbacks. The module contains ZERO filesystem primitives and ZERO network primitives of its own.**

**Every file operation is a callback the Go host implements.** The VFS-relevant import set, enumerated rather than sampled **(11 of 66):**

```
go_vfs_find   go_full_pathname   go_access   go_delete    go_open
go_read       go_write           go_sync     go_truncate  go_file_size
go_file_control
```

plus the SHM/WAL group: `go_shm_map`, `go_shm_lock`, `go_shm_barrier`, `go_shm_unmap`, `go_sector_size`, `go_device_characteristics`, `go_lock`, `go_unlock`, `go_check_reserved_lock`.

**The two imports that LOOK like network are not.** `go_vtab_connect` and `go_vtab_disconnect` are **SQLite virtual-table lifecycle callbacks** (paired with `go_vtab_create`, `go_vtab_destroy`, `go_vtab_best_index`, `go_vtab_update`, `go_vtab_rename`, `go_vtab_begin`, `go_vtab_commit`, `go_vtab_rollback`, `go_vtab_savepoint`, `go_vtab_release`, `go_vtab_sync`, `go_vtab_integrity`, `go_vtab_rollback_to`, `go_vtab_find_function`). **A grep for `socket|net|http|connect|listen|dns|url` returns these and nothing else** — **a name-substring probe that would have reported "network surface present" on a module with no network capability whatsoever.**

**This is the D17 §13.2 instrument shape again** — a probe with no word boundary reports the ambient vocabulary as its subject. `connect` in SQLite's vocabulary means *bind a virtual table*, never *open a socket*.

**So the answer to the brief's question is: the module requires NO host filesystem or network access through its import surface.** What it requires is a **Go host that implements 66 callbacks** — and the security-relevant capability lives entirely in that host, not in the `.wasm`. **An auditor who reads only the `.wasm` will find no VFS and conclude nothing; the VFS is Go code, and that is where the question must be asked.** [verified + inferred]

### 3.3 The second instrument — `name` section agreement

**`sqlite3.wasm` retains a 40,328-byte `name` custom section.** Decoding it:

```
name subsections: [(0, module=13), (1, function=33,547), (7, global=18), (9, data=6,734)]
FUNCTION NAMES: 1,667 (declared count 1,667)
```

**Indices 0–65 are exactly the 66 imports, in exactly the order my section parser produced them** — `[0] go_vfs_find`, `[1] go_full_pathname`, `[2] go_access`, … `[65] go_shm_unmap`, `[66] memcmp`.

**Two instruments, independently implemented, agreeing on count AND order.** [verified]

### 3.4 Export surface — the real SQLite C API

**145 exports: 144 functions + 1 memory.** **143 are `sqlite3_*`** — the genuine amalgamation C API (`sqlite3_backup_init/step/finish`, `sqlite3_value_blob/text/int64`, `sqlite3_result_*`, `sqlite3_bind_*`, `sqlite3_exec_go`, …).

**The one non-`sqlite3_` export is `aligned_alloc` (idx 1634)** — a C11 allocator symbol the Emscripten build leaves exported, almost certainly incidental rather than designed. **Recorded because "143 of 144" is a cleaner claim than "all of them," and the exception is enumerated rather than averaged away.**

**Note the `_go` suffix on several exports** (`sqlite3_exec_go`, `sqlite3_create_module_go`, `sqlite3_bind_pointer_go`) — **the Go binding's own additions, not upstream SQLite.** The export table therefore carries vocabulary from **three** layers (upstream C, Emscripten, the Go binding) under one namespace. [read]

---

## §4 — (C) Vendored JVM tooling — a bounded census, and why shallow

### 4.1 The boundary, stated and justified

**Tagged `vendored-tooling`.** These are **third-party packaging tools shipped so the builders can run**, not first-party capability. The boundary is drawn at:

- `META-INF/MANIFEST.MF` — the declared `Main-Class`;
- signature files;
- **top-level package structure and class counts only.**

**Why not deeper, stated as a positive reason rather than a budget excuse:**
1. **They are not the adversary's code.** `apktool.jar` is `brut.apktool` + `org.jf` (JesusFreke's smali/baksmali/dexlib2); `sign.jar` is `com.android.apksig`. **Reversing them is reversing other people's maintained projects**, and the corpus already carries a rule against that (`C-00 §1` excludes Microsoft reference assemblies on exactly this basis).
2. **The interesting facts are at the boundary, not inside.** Which version, which entry point, and whether the two files that share a name are the same program — all answerable in one pass.
3. **Function-by-function reversal has no consumer.** No report downstream asks a question that requires apktool's internals.

**A shallow pass with a reason is a finding; a shallow pass presented as depth is a defect.** [boundary justified]

### 4.2 The census

| file | SHA-256 | bytes | Main-Class | classes | signature |
|---|---|---:|---|---:|---|
| `01_SOURCE_mobile\androrat\Jar_utils\apktool.jar` | `BDEB66211D1DC1C71F138003CE35F6D0CD19AF6F8DE7FFBDD5B118D02D825A52` | 17,661,172 | `brut.apktool.Main` | 1,517 | none |
| `01_SOURCE_mobile\ahmyth\AhMyth-Server\app\app\Factory\apktool.jar` | `A0F116E8916D6F21160E1559847BB8B8C32EE71900F321CAFEADBE37B87EBCC1` | 16,314,178 | `brut.apktool.Main` | 1,612 | none |
| `01_SOURCE_mobile\androrat\Jar_utils\sign.jar` | `47AE984DF200AFBAE292D6F950E517AFB445D3C902A1EDC7717A82C513C5E772` | 1,861,628 | `at.favre.tools.apksigner.SignTool` | 317 | `PFOPENSO.SF`/`.RSA` |
| `01_SOURCE_mobile\ahmyth\AhMyth-Server\app\app\Factory\sign.jar` | `0F002A2613AD7DBC2A348FD93B01DAB90321727FA6E74A9EF48A30104A5DCF67` | 26,106 | `s.Sign` | 5 | none |

**Top-level packages (apktool, both copies):** `org/jf/dexlib2` (690 / 671) · `com/google/common` (183 / 298) · `org/yaml/snakeyaml` (190) · `org/jf/smali` (142) · `org/jf/baksmali` (66 / 64) · `brut/androlib/res` (59) · `org/antlr/runtime` (45) · `org/apache/commons` (42 / 43).

**Bytecode target:** both apktool copies are **class major 52 (Java 8)**. `SignTool.class` is **major 52**; **`s/Sign.class` is major 50 (Java 6)**.

### 4.3 THE FINDING — two `sign.jar` files, two unrelated programs

> **`sign.jar` is not one tool. It is two different programs that share a filename and a directory role.**
> **`at.favre.tools.apksigner.SignTool` (1,861,628 B, 317 classes, Android `com.android.apksig`)** versus **`s.Sign` (26,106 B, 5 classes).**
> **A 71× size difference, no shared package, no shared entry point, different Java target.**

**`sign.jar` names a ROLE, not an artifact.** Any census that keys on the filename — *"both builders ship `sign.jar`"* — is true and useless: it will report a single dependency where there are two unrelated ones, and will attribute AndroRAT's signing behaviour to AhMyth's code and vice versa.

**This is the same species `D90` named (`Bool` ≠ `Bare`; `fake_server` is a client), and the specimen is cleaner because both copies sit in the same corpus under the same filename.** [verified]

**Two consequences worth carrying forward:**
- **The `D64`/`D53` builder comparison must not treat "both use `sign.jar`" as shared lineage.** The tools are not related.
- **`s.Sign` at 5 classes and 26 KB is a hand-rolled signing helper**, three orders of magnitude from `apksig`. **A 5-class signer is a plausible place for a fixed-position or hardcoded-key defect** — which is exactly the `D53` builder-defect thesis. **I did not inspect its code; that is a probe, not a claim.** [probe named, not run]

**Both apktool copies are also distinct** (different SHA, 1,574 vs 1,688 entries, 1,517 vs 1,612 classes). **Same `Main-Class`, different builds** — consistent with `Compiled_apk\` vs `Factory\` having been populated at different times. **Neither carries a signature file** (unsigned jars), while AndroRAT's `sign.jar` carries `META-INF/PFOPENSO.SF` + `.RSA`. [read]

---

## §5 — Instrument record

### 5.1 WABT: unavailable, and recorded as the finding

Invoked once (per *"before you write that anything is unavailable, invoke it once"*), returning a typed `capability_unavailable`. **The distinction the corpus draws is preserved: this is "cannot be invoked" — a capability gap of the environment — and it is NOT recorded as an artifact gap.** The artifacts parsed fine. [verified]

### 5.2 The 30-byte arithmetic error

§1.3. **Parser correct, stated total wrong.** Caught by chasing a clean-looking discrepancy rather than accepting it. [self-corrected]

### 5.3 The `go_vtab_connect` / network false positive

§3.2. **A substring probe for network verbs fires on SQLite's virtual-table vocabulary and would have reported a network surface on a module with none.** **The fix is the one this corpus keeps rediscovering: enumerate the primitive's call sites, do not grep the ambient vocabulary.** [instrument shape, D17 §13.2]

### 5.4 A note on measuring a file another writer owns

**Not a finding of this report — an instrument note earned in this round, recorded because it is general.**

While checking whether an artifact had been altered, I measured a byte size that differed from a previously verified figure and inferred tampering of a frozen artifact. **The correct reading was that the file was mid-write and still owned by a live writer** — it moved down and then up because it was being rewritten, not because a verified artifact was damaged.

> **A size change measured on a file that another writer still owns is not evidence of tampering; it is evidence that a moving target was measured. Byte-size verification is only meaningful after a writer declares done.**

**The instinct to flag rather than edit was correct; the causal story I attached to it was invented.** **The failure mode is identically shaped to the `.wasm` finding above and to D87's offset basis: I inferred a cause from a shape, instead of from a measurement that could distinguish the two explanations.** [instrument note]

### 5.5 What was NOT done

- **No function bodies decoded.** No disassembly, no semantics.
- **No module instantiated or executed.** No `wazero`, no `wasmtime`, no JS runtime.
- **No REA `open_binary`.** No `inspect_wasm_artifact` result — it returned `capability_unavailable` before touching the target.
- **No apktool internals reversed.**
- **No network.**

---

## §6 — Residuals

| ID | Unknown | Why it is bounded | Status |
|---|---|---|---|
| **R-97.1** | What `H`, `I`, `J`, `v`, `z` do in `keystone.wasm` | requires code-section disassembly; **no WABT**, so this needs a hand-written body decoder or a WABT install | **open — tool-blocked** |
| **R-97.2** | Whether the five unmapped exports correspond to a specific Keystone build/config | would need correlation against a second Keystone WASM build, **which the corpus does not contain** | open |
| **R-97.3** | Whether `s.Sign` (5 classes) hardcodes a key or a fixed position | **probe: read the 5 classes' constant pools.** Not run — this was a bounded census | open, cheap, named |
| **R-97.4** | Whether `sqlite3.wasm`'s Go host implements the 66 callbacks safely | **the capability lives in the Go host, not the `.wasm`.** In scope for `ncruces/go-sqlite3`, not for this report | **out of scope, correctly located** |
| **R-97.5** | Identity of the 4 remaining `.wasm` modules (`sgn`, `donut`, `hex`, `sql3parse_table`, mythic `sql-wasm`) | enumerated and size-validated in §1.2; **not otherwise analysed** | open, bounded by this report's scope |

**R-97.4 is the one to carry: the security answer for `sqlite3.wasm` is that the module is incapable and the HOST is where the capability is. Any future audit of embedded SQLite in this corpus must ask the question of the Go host.**

---

## §7 — What this establishes

**1. The WASM layer now has a validated instrument.** Seven modules, seven exact EOF walks, and a total reproducing `C-00 §1` independently. **Any WASM number in this corpus can now be checked against a parser that has been calibrated.** [verified]

**2. WABT is unavailable in this environment and that is recorded, not obscured.** The fallback is static section parsing, and its limits are stated: **structure and interface, never behaviour.** [verified]

**3. `keystone.wasm` `E6477742…` 4,450,666 B is a name-stripped Emscripten Keystone 0.9 engine with a 15-function export surface, of which the Go wrapper maps 10.** The other five — **`H I J v z`** — are real, reachable, and unmapped in source. **The source map is incomplete; what the five do is unknown and is not guessed.** [verified + open]

**4. `sqlite3.wasm` `2BFED60A…` 1,406,839 B imports 66 `env`-scoped `go_*` callbacks and contains no filesystem and no network code of its own.** The embedded database's host access is entirely a property of the Go host. [verified]

**5. `sign.jar` is two unrelated programs under one name** — 1,861,628 B of `apksig` versus 26,106 B of `s.Sign`. **The cheapest class of error in this corpus, and this is a clean specimen.** [verified]

**The through-line, carried from D87 and D53/D64:** **the same failure shape recurs in every layer.** D87's offset basis returned structure-shaped nonsense; this report's first section table returned a clean 30-byte total that was wrong; a network probe returns SQLite's virtual-table vocabulary; and I read tampering into a file that was simply being written. **In each case a transform preserved the SHAPE of the answer while the content was wrong — and in each case what caught it was an external bound, never the decode completing.**

---

*End of D97. Instruments: hand-written WASM section parser (Python 3.11.9, no third-party libraries) validated against `C-00 §1`'s 7,118,726 B total; `zipfile`/hashlib for the JVM census; `func_map.go` + `const.go` + `keystone.go` as the independent source channel. All three WASM artifacts parsed statically; none executed.*
