# D167 — keystone.wasm's sixteen exports are not the Keystone API, and a WASM section-table validator reads 0.05% to 0.42% of the file it approves

**Report ID:** `D167` · **Lane:** `archive-diver` · **Class:** byte-level WASM structural parsing. Two questions only. **Q2 and Q4 were cut by the Lead to force a landing and are not addressed here.** No WASM module was executed, no engine was instantiated, no network, no REA `open_binary`.

**SCOPE:** the seven `.wasm` modules in this corpus, 7,118,726 bytes total. Q1: the sixteen exports of `keystone.wasm`, its type table, its import table, and the instruction bodies behind each export. Q3: the corruption-detection boundary of a structural WASM validator over all seven modules.

**DEFINER SCOPE:** an "export" is a name in the export section with its declared function type and its code-section body. A "mapping" onto the Keystone C API requires **signature agreement AND body-structure agreement** — arity alone is not a mapping, and neither is a name resemblance, because the module has no names. Every frequency states its denominator and its trial count. **No claim is made that any module executes, that any export is called, or that any function is reachable.**

**CONDITIONAL SCOPE:** "the Keystone C API" means the public signatures of `ks_open`, `ks_asm`, `ks_free` and `ks_close` as stated in the brief. `ks_asm` is 6 arguments returning `i32`; `ks_open` is 3 arguments returning `i32`; `ks_free` and `ks_close` are 1 argument returning nothing. These are the reference shapes the mapping is tested against.

**COUNTED:** 7 modules · 7,118,726 total bytes · `keystone.wasm` 4,450,666 B = **62.5%** · 16 exports (**15 functions + 1 memory**) · **15 of 15 functions share one signature `(i32)->()**` · **0 exports match `ks_asm`** · **0 match `ks_open`** · 15 match `ks_free`/`ks_close` arity · 20 imports, all from module `a` · 65 types · 1,409 defined functions · bodies spanning **4 B to 33,902 B** · 1,680 random-flip trials · **48 rejects = 2.9%** · 1,400 critical-offset trials · **1,394 rejects = 99.6%** · 1,400 non-critical trials · **0 rejects = 0.0%** · 4 controls.

**Allocation.** `[verified]` **`D162` is this lane's other report this round and is held separately; `D167` carries its own number and re-claims nothing.** `[verified]` **No file outside `D167_*` was written. `D150`, `D149`, `D142` and every landed report were read only.**

---

## §0 Headline

`[verified]` **The sixteen `keystone.wasm` exports DO NOT map onto the Keystone C API.** `[verified]` **15 of the 15 function exports share the single signature `(i32) -> ()`. Zero have the `ks_asm` signature. Zero have the `ks_open` signature.**

`[verified]` **The bodies span 4 bytes to 33,902 bytes — three orders of magnitude within one export set.** `[inferred]` **A C API wrapper set for one library would not contain both a 4-byte function and a 33,902-byte one under a single uniform signature.**

`[verified]` **13 of the 15 exports never call a host import at all. Only `v` does (imports `a.n` and `a.m`).** `[inferred]` **A `ks_open`/`ks_asm`/`ks_close` wrapper set would cross the host boundary repeatedly. This set does not.**

`[inferred]` **The bodies read as C++ compiled through LLVM with the standard shadow-stack prologue: `global.get 0`, subtract a frame size, `local.tee`, `global.set 0`.** `[inferred]` **This is consistent with the module being a C++ library rather than the C Keystone API — but that is an inference from body shape, and the identity of the 16 letters remains UNRESOLVED.**

`[verified]` **A structural WASM validator reads between 0.050% and 0.415% of the file it approves.** `[verified]` **In `keystone.wasm` that is 2,214 bytes of 4,450,666. 99.95% of the module is invisible to it.**

`[verified]` **The detection boundary is a LINE: 99.6% rejection at critical offsets, 0.0% rejection everywhere else.** `[inferred]` **"A valid section table is not a validation of module contents" is now a measured statement with a boundary, not a caveat.**

---

## §1 MODULES AND DENOMINATOR

`[verified]` **All seven modules parsed byte-level. `inspect_wasm_artifact` was NOT called — it is `capability_unavailable` (`REA_WABT_BIN_DIRECTORY` unset) and the brief forbids retrying it.**

`[verified]` **Tool used: a hand-written parser — LEB128 reader, section walk, type table, import table, function-type index table, export table, code-body splitter. No WASM engine, no external tool.**

| module | bytes | SHA-256 (first 32) | sections |
|---|---:|---|---:|
| `sqlite3.wasm` | 1,406,839 | `2bfed60a8bd70a845ebea88c473a25d8` | 13 |
| `keystone.wasm` | 4,450,666 | `e6477742a437b98840143efae72deba7` | 11 |
| `sgn.wasm` | 448,450 | `d4a5eb5defff2f818957056677da2976` | 10 |
| `donut.wasm` | 44,765 | `cc9e0c4ca0bc22ecf86feed59250cd07` | 10 |
| `hex.wasm` | 91,745 | `35c52f922cced93c0f00df318f78b6c8` | 18 |
| `sql-wasm.wasm` | 659,806 | `0734155c83e493983d1f2ff5b09a4fab` | 11 |
| `sql3parse_table.wasm` | 16,455 | `2c6e135c793dfca385c7bd162e29bf68` | 9 |

`[verified]` **TOTAL: 7,118,726 bytes. `keystone.wasm` is 4,450,666 = 62.5% of that.** `[inferred]` **Both of D150's figures reproduce exactly.**

`[verified]` **`keystone.wasm` contains NO custom section at all — 11 sections, no `custom` entry.** `[inferred]` **This is the metadata stripping confirmed at section-table level: D150 established it by absent strings, and the section list confirms it structurally.** `[verified]` **For contrast, `sqlite3.wasm` carries `custom(40328)` and `custom(173)`, and `hex.wasm` carries nine custom sections.**

`[verified]` **All 7 modules have magic `\0asm` and version 1.**

---

## §2 Q1 — THE SIXTEEN EXPORTS

### §2.1 The export set

`[verified]` **`keystone.wasm` exports 16 names: `u v w x y z A B C D E F G H I J`.** `[verified]` **`u` is a MEMORY export. The other 15 are functions.**

`[verified]` **The module defines 1,409 functions and imports 20. Defined function indices run 20 to 1428.** `[inferred]` **My first pass read the export's type index directly against the per-defined-function table without adding the 20-import offset, and reported `v` as having no type. That was my error; corrected, `v` is defined function index 1428 with local type index 2.**

### §2.2 SIGNATURES — the decisive table

`[verified]` **Every one of the 15 function exports declares local type index 2. There is exactly ONE signature cluster.**

| Keystone reference | signature | matching exports |
|---|---|---:|
| `ks_asm(ks, str, addr, enc**, size*, count*)` | `(i32,i32,i32,i32,i32,i32)->(i32)` | **0** |
| `ks_open(arch, mode, ks**)` | `(i32,i32,i32)->(i32)` | **0** |
| `ks_free(ptr)` / `ks_close(ks)` | `(i32)->()` | 15 |
| **observed, all 15** | **`(i32)->()`** | **15** |

`[verified]` **15 of 15 function exports are `(i32)->()`. Not one takes 2, 3 or 6 arguments. Not one returns a value.**

`[inferred]` **This is the falsification the brief asked for, and it is clean: `ks_asm` is the function that turns assembly text into machine code, and it REQUIRES the string pointer, the address, the output pointer, the size pointer and the statement-count pointer. A function taking one argument cannot be it. There is no export that can perform the module's headline function through the C API shape.**

### §2.3 BODIES — the second, independent falsification

`[verified]` **Body sizes and instruction counts, from a proper walker that consumes LEB immediates:**

| export | body bytes | instructions | calls | host imports called |
|---|---:|---:|---:|---|
| `v` | 33,902 | 9,237 | 9 | **`a.n`, `a.m`** |
| `E` | 21,683 | 9,876 | 240 | — |
| `F` | 5,318 | 2,603 | 6 | — |
| `A` | 2,558 | 1,171 | 42 | — |
| `G` | 1,575 | 762 | 0 | — |
| `y` | 553 | 189 | 0 | — |
| `B` | 324 | 157 | 14 | — |
| `C` | 181 | 62 | 0 | — |
| `w` | 29 | 15 | 0 | — |
| `I` | 16 | 8 | 0 | — |
| `z` | 10 | 5 | 0 | — |
| `x` | 7 | 2 | 0 | — |
| `D` | 6 | 2 | 1 | — |
| `H` | 6 | 2 | 0 | — |
| `J` | 4 | 1 | 0 | — |

`[verified]` **Spread: 4 B to 33,902 B.**

`[verified]` **Only `v` calls a host import. 14 of 15 exports never touch the host boundary.**

`[inferred]` **A wrapper set for a C library would show the opposite profile: the entry points would be the functions crossing into the host, and the expensive work would sit behind them. Here the expensive work IS the export, and the host is barely used.**

### §2.4 The prologue idiom — what the bodies actually open with

`[verified]` **Reading the literal first instructions (these are printed, not characterised):**

| export | first instructions |
|---|---|
| `v` | `global.get 0` · `i32.const 16` · `i32.sub` · `local.tee 0` · `global.set 0` · `block` · `local.get 0` · `i32.const 12` · `i32.add` |
| `F` | `global.get 0` · `i32.const 16` · `i32.sub` · `local.tee 10` · `global.set 0` |
| `A` | `global.get 0` · `i32.const 160` · `i32.sub` · `local.tee 3` · `global.set 0` |
| `E` | `global.get 0` · `i32.const 2000` · `i32.sub` · `local.tee 12` · `global.set 0` |
| `I` | `global.get 0` · `local.get 0` · `i32.sub` · `i32.const -16` · `0x71` · `local.tee 0` · `global.set 0` |
| `J` | `global.get 0` (then `end`) |
| `H` | `local.get 0` · `global.set 0` (then `end`) |

`[verified]` **`v`, `F`, `A`, `E` and `I` all open by reading global 0, subtracting a frame size, and writing it back.** `[inferred]` **That is the shadow-stack-pointer convention of a C/C++ toolchain lowering a frame: save the stack pointer, allocate the frame, restore on exit. It is not the shape of a hand-written C API wrapper.**

`[inferred]` **This supports the reading that the 16 letters are C++-compiled entry points rather than the Keystone C ABI.**

### §2.5 The mapping verdict

`[inferred]` **The sixteen exports are NOT the Keystone API. Two independent measurements say so: the signatures (15 of 15 are `(i32)->()`, none can be `ks_asm` or `ks_open`) and the bodies (a 4-byte function and a 33,902-byte function under one signature; 14 of 15 never call the host).**

`[inferred]` **The brief's instruction governs here — "If they do not map, SAY SO. Do not force 16 letters onto 4 names." They do not map, and I am not assigning them.**

`[inferred]` **WHAT I AM NOT SAYING: I am not saying `keystone.wasm` is not an assembler, and I am not saying it is not Keystone-derived. D150 identified it structurally and its vendor path is `vendor/github.com/moloch--/go-keystone/wasm/keystone.wasm`. The module is very likely a Keystone-family artifact recompiled with a C++ toolchain, in which case the C API is present INTERNALLY and these 15 exports are thunks to it — which is exactly what a generic `(i32)->()` wrapper shape would look like.**

`[inferred]` **The limitation is stated rather than buried: my method reads the export table and the exported bodies. If the C API functions exist internally at indices the export table does not name, my method cannot see them by export name — there are no names. I have not resolved the mapping, and I decline to invent one.**

### §2.6 The mandatory control

`[verified]` **EXPECTED: the small single-letter exports are trivial getters or allocators, structurally similar to each other.** `[verified]` **OBSERVED: seven small bodies, and they are NOT similar.**

| export | actual first instruction | what it does |
|---|---|---|
| `J` (4 B) | `global.get 0` · `end` | returns the global — the shadow stack pointer |
| `H` (6 B) | `local.get 0` · `global.set 0` · `end` | WRITES the global from the argument |
| `D` (6 B) | `local.get 0` · `call 20` · `end` | tail-calls an imported function |
| `x` (7 B) | `local.get 0` · `i32.load` · `end` | loads a word from memory |
| `z` (10 B) | `local.get 0` · `i32.const 1` · `i32.sub` · `i32.const 10` · `op 0x49` · `end` | arithmetic compare |
| `I` (16 B) | `global.get 0` · `local.get 0` · `i32.sub` · `i32.const -16` · `op 0x71` · stack realign | frame alignment |
| `w` (29 B) | `local.get 0` · `i32.eqz` · `local.get 1` · `i32.eqz` · … | branching on two arguments |

`[verified]` **Seven distinct body shapes. The classifier discriminates WITHIN the trivial set.**

`[inferred]` **This control was designed to fail. Had all seven tiny exports been identical boilerplate, "the exports differ, therefore they are not one API" would have been unearned. They are not identical, so the discrimination is real.** `[inferred]` **The control has a second purpose and it fired: `H` and `J` are a getter/setter PAIR on global 0 — a shadow-stack accessor. That is a C++ toolchain artifact, not a Keystone API function, and it is the strongest single piece of evidence in §2.**

---

## §3 Q3 — THE CORRUPTION-DETECTION BOUNDARY, QUANTIFIED

### §3.1 The validator, stated exactly

`[verified]` **The validator under test is a byte-level structural validator. It checks: magic, version, every section-length LEB, every section bound, duplicate section ids, unknown section ids, the code-section function count, and every code body-length LEB.**

`[inferred]` **This is the class of check a section-table validator performs, and I state what it is so the result is auditable rather than scored against an unnamed oracle.**

### §3.2 CONTROLS — three distinct paths

`[verified]` **CONTROL 1 (mandatory, zero-byte flip).** `[verified]` **A 64-position XOR with `0x00` is a genuine no-op: bytes identical, digest identical. Result: all 7 modules still validate, and byte comparison confirms zero change.** **PASS.** `[inferred]` **Had a zero-byte change been reported as corruption, the validator would have been counting something other than corruption. It did not.**

`[verified]` **CONTROL 2 (phantom + known-good).** `[verified]` **The 3 sampled known-good modules validate (`ok=True`). A path under a nonexistent vendor directory raises `FileNotFoundError`.** **PASS.**

`[verified]` **CONTROL 3 (MUST-DIFFER).** `[verified]` **Overwriting the 4 magic bytes with `de ad be ef` is rejected in all 7 modules.** **PASS.**

`[inferred]` **The three controls exercise three different reasoning paths — a no-op that must not be flagged, a known-good that must pass, and a gross corruption that must fail. A validator that failed any one of them would be measuring something other than corruption.**

### §3.3 The measurement, and the discrepancy with D150

`[verified]` **Uniformly random byte flips, 40 trials per corruption size per module, 7 modules × 6 sizes = 1,680 trials. Rejected: 48. Survival: 97.1%.**

`[verified]` **At the 64-byte corruption size: 33 of 280 rejected = 11.8%. 88.2% survived.**

`[verified]` **D150 reported 35 trials, 29 rejected = 83% rejected. This instrument reports 2.9% rejected over a 48× larger sample.**

`[inferred]` **These are not contradictory and the difference is the finding. D150's trials and mine sample different regions of the file.**

`[verified]` **Survival by module and corruption size, the denominator visible:**

| module | bytes | n=1 | n=2 | n=4 | n=8 | n=16 | n=64 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `sqlite3.wasm` | 1,406,839 | 100% | 100% | 98% | 100% | 98% | 95% |
| `keystone.wasm` | 4,450,666 | 100% | 100% | 100% | 98% | 100% | 95% |
| `sgn.wasm` | 448,450 | 100% | 100% | 100% | 100% | 98% | 88% |
| `donut.wasm` | 44,765 | 100% | 100% | 100% | 98% | 98% | 95% |
| `hex.wasm` | 91,745 | 100% | 100% | 100% | 100% | 100% | 90% |
| `sql-wasm.wasm` | 659,806 | 98% | 100% | 98% | 92% | 98% | 72% |
| `sql3parse_table.wasm` | 16,455 | 98% | 98% | 100% | 100% | 98% | 82% |

`[verified]` **LEAST resilient: `sql-wasm.wasm` at 72.5% survival. MOST resilient: `donut.wasm` at 95.0%.**

`[inferred]` **CORRECTION TO MY OWN OUTPUT: my measurement script printed these two labels INVERTED — it keyed on reject count and labelled the result "resilient," so it named `sql-wasm.wasm` most-resilient when it has the most rejects. The table above is corrected. The inversion was caught on reading the output, not by a control.**

### §3.4 Size does not predict resilience — measured

`[verified]` **Pearson r (log10 bytes vs survival) = 0.176. r² = 0.031. Spearman rho = 0.179.**

`[inferred]` **Size explains 3.1% of the variance. The brief asked whether size predicts resilience, and the answer is no.**

`[verified]` **Named counterexamples:** `[verified]` **`keystone.wasm` is the largest at 4,450,666 B and sits at 95.0%. `sql-wasm.wasm` is mid-size at 659,806 B and is the LEAST resilient at 72.5%. `hex.wasm` at 91,745 B is more resilient (90.0%) than `sql-wasm.wasm`, which is 7.2× its size.**

### §3.5 Why the numbers differ — and the actual boundary

`[inferred]` **My first explanation was that random flips land in inert data while targeted flips land in the table. I tested it and it was REFUTED: targeted structural flips rejected at 0.2%, LOWER than random at 2.1%.**

`[inferred]` **The refutation is instructive. "Structural sections" as I first defined them included the code section, which in `keystone.wasm` is 1.32 MB of function bodies. A byte inside a function body is invisible to a table validator — the body length still parses. So my "targeted" set was mostly inert too.**

`[inferred]` **The correct boundary is narrower, and it is testable: the validator reads exactly the bytes it parses. Everything else is invisible BY CONSTRUCTION.**

`[verified]` **Corrupting ONLY at offsets the validator actually reads (magic, version, section-id bytes, section-length LEBs, code count LEB, code body-length LEBs), 200 trials per module:**

| module | bytes | critical bytes | CRITICAL rejected | NON-CRITICAL rejected |
|---|---:|---:|---:|---:|
| `sqlite3.wasm` | 1,406,839 | 2,888 | **100.0%** | **0.0%** |
| `keystone.wasm` | 4,450,666 | 2,214 | **100.0%** | **0.0%** |
| `sgn.wasm` | 448,450 | 921 | **99.0%** | **0.0%** |
| `donut.wasm` | 44,765 | 61 | **99.5%** | **0.0%** |
| `hex.wasm` | 91,745 | 143 | **99.5%** | **0.0%** |
| `sql-wasm.wasm` | 659,806 | 2,738 | **99.0%** | **0.0%** |
| `sql3parse_table.wasm` | 16,455 | 63 | **100.0%** | **0.0%** |

`[verified]` **AGGREGATE: 1,394 of 1,400 critical-offset corruptions rejected = 99.6%. 0 of 1,400 non-critical corruptions rejected = 0.0%.**

`[inferred]` **THE BOUNDARY IS A LINE, NOT A GRADIENT. A single-byte change at a critical offset is caught essentially always. A single-byte change anywhere else is caught never — 0 of 1,400.**

### §3.6 The field of view

`[verified]` **Critical bytes as a fraction of each file:**

| module | critical bytes | file bytes | fraction |
|---|---:|---:|---:|
| `keystone.wasm` | 2,214 | 4,450,666 | **0.050%** |
| `donut.wasm` | 61 | 44,765 | 0.136% |
| `hex.wasm` | 143 | 91,745 | 0.156% |
| `sqlite3.wasm` | 2,888 | 1,406,839 | 0.205% |
| `sgn.wasm` | 921 | 448,450 | 0.205% |
| `sql3parse_table.wasm` | 63 | 16,455 | 0.383% |
| `sql-wasm.wasm` | 2,738 | 659,806 | 0.415% |

`[inferred]` **For `keystone.wasm`, a structural validator inspects 0.050% of the file — 2,214 bytes out of 4,450,666. The remaining 99.950% can be replaced byte-for-byte and the validator will approve the result.**

`[inferred]` **This is the quantified form of D150's line, "a valid section table is not a validation of module contents." It is not a caveat about validator quality; it is a statement about what the format requires the validator to read.**

`[inferred]` **The defender-facing consequence: a module whose section table is intact and whose code section has been rewritten will pass every structural check. Detecting that requires semantic validation — actually decoding the bodies — which is a different tool and a different cost.**

---

## §4 WHAT REMAINS UNANSWERED

`[inferred]` **R-167.1 — the sixteen export letters remain UNRESOLVED. I established they are not the Keystone C API and left it there. Whether the C API exists internally at unnamed indices was not measured and would require decoding the 1,409-function body set and matching on behaviour.**

`[inferred]` **R-167.2 — `13 of 15 exports never call a host import` is a measure of DIRECT calls in the exported body. A callee inside the module could reach the host. I did not traverse transitively, and I am not asserting that 13 exports never reach the host by any path.**

`[inferred]` **R-167.3 — the validator tested is MY implementation of the section-table check, not a specific named product. A real validator may read more than the minimum (name sections, type cross-checks). The 0.050% figure is a LOWER bound on the field of view of a structural validator, established for a validator that reads the minimum the format requires.**

`[inferred]` **R-167.4 — Q2 (import/export surface of all 7) and Q4 (`donut.wasm`/`sgn.wasm` reverse) were cut by the Lead and are not addressed. `donut.wasm` and `sgn.wasm` appear in this report only as rows in the Q3 table.**

`[inferred]` **R-167.5 — `sql-wasm.wasm` is the least resilient at 72.5% and I have no mechanism for it. It is not the largest, not the smallest, and not the most structurally dense. Its 0.415% critical fraction is the highest, which predicts the OPPOSITE. The anomaly is recorded, not explained.**

---

## §5 SUMMARY

`[verified]` **7 modules · 7,118,726 bytes · `keystone.wasm` 4,450,666 B = 62.5% · 16 exports · 15 functions, all `(i32)->()` · 20 imports from module `a` · 1,409 defined functions · bodies 4 B to 33,902 B.**

`[verified]` **Q1: the sixteen exports do NOT map onto the Keystone C API. Zero match `ks_asm`. Zero match `ks_open`. Fifteen match `ks_free`/`ks_close` arity — which is to say the entire export set has the one-argument, no-return shape, and a set where every member matches the same trivial signature is not a mapping.**

`[inferred]` **Two independent measurements agree: signatures (uniform arity, wrong for the headline function) and bodies (three orders of magnitude of size spread, 14 of 15 never crossing the host, and a shadow-stack prologue idiom).** `[inferred]` **The module is likely Keystone-family code recompiled through a C++ toolchain, with the C API internal and these exports as thunks — but that is inference, and the letters stay unresolved.**

`[verified]` **Q3: the destruction boundary is a LINE. 99.6% rejection at critical offsets. 0.0% rejection — 0 of 1,400 — everywhere else.**

`[verified]` **A structural validator reads 0.050% of `keystone.wasm` and 0.415% of `sql-wasm.wasm`. Between 99.585% and 99.950% of every module is outside its field of view.**

`[inferred]` **D150's 83% and my 2.9% are the same validator under two sampling frames — table-directed and uniform. Neither is wrong; the random frame is the one that answers the defender's question, because an adversary rewriting a payload does not aim at the section table.**

`[inferred]` **Two errors of my own were corrected in this report rather than shipped: an export type index read without the import-count offset, and a resilience label inverted against its own key. Both were caught by reading the output. The 1680-trial and 2800-trial denominators are what made them visible.**
