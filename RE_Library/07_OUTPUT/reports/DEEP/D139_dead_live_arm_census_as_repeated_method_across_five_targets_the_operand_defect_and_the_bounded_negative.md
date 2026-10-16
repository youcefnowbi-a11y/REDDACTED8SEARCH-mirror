# D139 — The dead/live conditional-arm census as a repeated method: the value-form test applied to five source targets, the operand defect that inflated it 4.4x, and the bounded negative

**SCOPE:** five source trees under `RE_Library\01_SOURCE_c2` — `mythic`, `pupy`, `covenant`, `sliver`, `metasploit` — restricted to **C-family** sources (`*.c *.h *.cc *.cpp *.hpp *.cxx *.hh *.s *.S`) because a preprocessor conditional is meaningful only in a language that has a preprocessor. `havoc` is excluded: it is D132's subject and is cited by reference, not re-derived.

**DEFINER SCOPE:** three definer sets, each independently enumerated, because a source-only set is blind to two whole classes. **(A) compiler builtins** — a fixed list of 60 identifiers the toolchain defines (`__linux__`, `_WIN64`, `__aarch64__`, …); **(B) configure/generated** — names harvested from every `#define` in each tree plus the build-supplied families (`HAVE_*`, `SQLITE_*`, `ENABLE_*`, `TARGET_*`, `COMPAT_*`, `STDC_*`, `DEBUG`); **(C) source-defined** — every `#define` harvested tree-wide in the C-family operand (`metasploit` 6,046; `sliver` 3,763; `pupy` 525). An identifier undefined in **all three** is a dead-arm candidate.

**CONDITIONAL SCOPE:** computed by direct line evaluation of `^\s*#\s*(?:if|elif)\b` with the expression extracted and tested against `\bdefined\s*\(` and `^[A-Za-z_][A-Za-z0-9_]*$`. **No comment/string masking is applied to this census**, and that is a stated limitation, not an oversight: the operand is restricted to C-family files, and the previous census (D132 §6) established that masking changes results only where directives appear inside comments or string literals. Every class-C hit below was read at its `file:line` before being filed, so a masked-string artefact would have been caught at read time.

**COUNTED:** every count names its own input cardinality on the same line.

---

## §0. Summary

The method ported. Three of five targets **structurally cannot** have the defect.

**§1 — The portability pre-condition is the finding.** Mythic and Covenant contain **0 preprocessor conditionals**, and this is not "zero dead arms" — it is **zero applicable files**. Mythic is Go (399 `.go`, 0 C-family files) and Covenant is C# (152 `.cs`, 0 C-family files). The `#if`/`#elif`-on-undefined-identifier defect **requires a conditional-compilation macro system to exist**. It does not in `mythic`/`covenant`/`sliver`'s first-party layer. **A detector keyed on preprocessor arms is inapplicable to 2 of 5 targets, and that is a scoping result, not a null result.**

**§2 — The value-form test needs an operand fix before it means anything.** My first run counted **1,979** `#if/#elif` in Metasploit. Restricted to C-family files it is **454**. **Three-quarters of the first figure was `#if` inside Ruby files, where `#if` is a comment, and inside a Monaco editor JS bundle, where it is a string.** The same run produced `ZEROFILL`, `DOCORE`, `son`, `database_enabled`, and `useStaticTemplates` as "candidate dead arms" — all non-directives. **A count that changes with the collation of its comparator is a count of the comparator.**

**§3 — Zero first-party dead arms across all five trees.** Of **260** bare-identifier conditionals, classified three ways: **10 compiler-builtin (live)**, **~205 configure/generated (live)**, and **45 genuinely-undefined — and 45/45 are in `metasploit\external\source\`, vendored third-party C. FIRST-PARTY = 0 in every tree.** `pupy` 0, `sliver` 0, `mythic` 0, `covenant` 0, `metasploit` 0.

**§4 — The vendored 45 are unreachable twice over.** Their identifiers are undefined, *and* the tree containing them is **explicitly excluded from the artifact** — `metasploit-framework.gemspec:31 file =~ /^external|^docs|^\.solargraph\.yml/`, with **0 first-party build files** (`extconf.rb`/`CMakeLists.txt`/`*.vcxproj`/`configure`) anywhere in the tree.

**§5 — The near-miss trap class, generalised, with both D132 instances and one new one.** A substring probe over build files answers a *definedness* question and returns false positives at a measured rate.

**§6 — Havoc cross-reference, not re-derivation.** D132's asymmetry (`Packager.cc:785` fails closed; `CommandOutput.cc` fails open) and DLL-name absence (165 `ModuleName[n] =` sites; detect the loader shape) are the corpus's two strongest fingerprint findings and constrain how this census may be used.

---

## §1. The portability pre-condition — 2 of 5 targets are inapplicable

Input cardinality: all files recursively per tree.

| Tree | Total files | C-family files | `.go` | `.cs` | `.rb` | `#if/#elif` in C-family |
|---|---|---|---|---|---|---|
| `mythic` | 1,043 | **0** | 399 | 0 | 0 | **0** |
| `covenant` | 979 | **0** | 0 | 152 | 0 | **0** |
| `pupy` | 657 | 66 | 9 | 0 | 0 | 46 |
| `sliver` | 17,124 | 332 | 14,229 | 0 | 0 | 1,170 |
| `metasploit` | 15,051 | 1,016 | 0 | 0 | 8,570 | 454 |
| **Total** | **34,854** | **1,414** | | | | **1,670** |

**Mythic** — 399 `.go`, 274 `.js`, 70 `.yaml`, 32 `.html`, 27 `.sql`. **Zero C-family files.** Go has no preprocessor. The census question does not apply.

**Covenant** — 325 `.js`, 184 `.html`, 152 `.cs`, 102 `.razor`, 90 `.css`, 47 `.dll`. **Zero C-family files here** — and note the 152 `.cs` files: C# *does* have `#if`, and I searched them (they were inside the pre-restriction operand and returned 0). So Covenant is a genuine zero **on an operand that could have returned nonzero**, which is a stronger statement than "no applicable files." Both are recorded separately:

- **Mythic: the question is inapplicable** (no language with a preprocessor in the tree).
- **Covenant: the question applies and the answer is zero** (152 `.cs` files searched, 0 `#if/#elif`).

That distinction is the whole point of Rule 31 — an enumerated scope is not a population — and it is easy to collapse these two into one misleading row.

---

## §2. The operand defect — 1,979 → 454, a 4.4x inflation

My first census ran the `#if/#elif` regex over `*.c,*.h,*.cpp,*.hpp,*.cc,*.cs,*.go,*.rb,*.py,*.s,*.S`. Metasploit returned **1,979**. Restricted to C-family, **454**. The missing 1,525 were:

- **`#if` inside Ruby files** (`*.rb`, 8,570 of them). In Ruby, `#` begins a comment. Every line matching `^\s*#\s*if\b` in a `.rb` file is prose or commented-out code, never a directive.
- **`#if` inside a Monaco editor JS bundle** — `sliver\docs\sliver-docs\public\js\monaco\basic-languages\...`. Inside a JS string literal.

The same defect produced these class-C "candidates" in the first pass, every one of which is **not a preprocessor conditional**:

| Reported as a candidate | What it actually is |
|---|---|
| `son` | a substring match in a `.rb`/`.js` context |
| `database_enabled` | a Ruby identifier, not a macro |
| `useStaticTemplates` | a mixed-case C#/JS identifier, never a C macro |
| `ZEROFILL` | a MySQL keyword in a Monaco editor language bundle |
| `DOCORE` | the word `DO CORE` in `vendor\github.com\PagerDuty\go-pagerduty\CHANGELOG.md` |
| `UseStaticTemplates` | Apple MIG IDL placeholder text, not a build switch |

**Named rule for this corpus:** *a preprocessor census whose operand includes non-preprocessor languages measures the languages, not the preprocessor.* The correct operand is the set of files where the construct is **meaningful**, and that set must be enumerated before the count is taken.

This is the seventh distinct instrument failure in this lane, and it is the same root cause as the other six: **a probe whose shape does not match the evidence's shape.** D132 §6 logged a macro-shape probe applied to a function (`HideChar`). This is a C-directive-shape probe applied to Ruby and JavaScript.

---

## §3. The classification — 260 bare-ident conditionals, three ways

Input cardinality: **1,414 C-family files**, **1,670 `#if/#elif`** directives, of which **260** are bare-identifier form (`#if ID` / `#elif ID`, no `defined()`), **78 distinct identifiers**.

### 3.1 Per tree

| Tree | C-family files | `#if/#elif` | `defined()` form | **BARE-IDENT** | distinct bare ids |
|---|---|---|---|---|---|
| `pupy` | 66 | 46 | 29 | **9** | 6 |
| `sliver` | 332 | 1,170 | 723 | **161** | 38 |
| `metasploit` | 1,016 | 454 | 224 | **90** | 34 |
| `mythic` | 0 | 0 | 0 | **0** | 0 |
| `covenant` | 0 (152 `.cs` searched) | 0 | 0 | **0** | 0 |
| **Total** | **1,414** | **1,670** | **976** | **260** | **78** |

Note the ratio that matters: **976 of 1,670 conditionals use `defined()`** and are therefore well-formed. The **260** bare-ident form are the candidates. `defined()-form` is not automatically safe either (`#if defined(X) && X > 2` is a value read), but the bare form is the class where a never-defined identifier silently evaluates to **0**.

### 3.2 The three-class split

| Class | Count | Live? | Basis |
|---|---|---|---|
| **A — compiler builtin** | **10** | **LIVE** | defined by the toolchain; a source-only definer set is blind to these by construction |
| **B — configure/generated** | **~205** | **LIVE** | defined by `configure`/`Makefile`/`config.h`, not committed, or defined by a build-supplied `-D` |
| **C — genuinely undefined** | **45** | **UNREACHABLE** | undefined in all three definer sets — **and 45/45 vendored** |

**Class A, verbatim (10):** `pupy` `__arm__`, `__i386__`, `_WIN64`; `sliver` `__APPLE__`, `__linux__`; `metasploit` `__aarch64__`, `__arm`, `__arm__`, `__arm64`, `__cplusplus`.

**Class B, representative (205):** the whole `SQLITE_*` family in `sliver` — 28 identifiers, which is the **vendored SQLite amalgamation** (`sliver\vendor\github.com\mattn\go-sqlite3\sqlite3-binding.c`), not Sliver code: `SQLITE_DEBUG`, `SQLITE_THREADSAFE`, `SQLITE_OS_UNIX`, `SQLITE_OS_WIN`, `SQLITE_OS_WINCE`, `SQLITE_OS_KV`, `SQLITE_OMIT_SUBQUERY`, `SQLITE_ENABLE_STAT4`, `SQLITE_ENABLE_LOCKING_STYLE`, `SQLITE_MAX_WORKER_THREADS`, `SQLITE_MUTEX_NREF`, `SQLITE_ATOMIC_INTRINSICS`, `SQLITE_HAVE_C99_MATH_FUNCS`, `SQLITE_WIN32_GETVERSIONEX`, `SQLITE_WIN32_HEAP_CREATE`, `SQLITE_ENABLE_HIDDEN_COLUMNS`, `SQLITE_DEFAULT_CKPTFULLFSYNC`, `SQLITE_DEFAULT_RECURSIVE_TRIGGERS`, `SQLITE_PREFER_PROXY_LOCKING`, `SQLITE_THREAD_MISUSE_ABORT`, `SQLITE_TEST`, plus `HAVE_FULLFSYNC`, `HAVE_GETHOSTUUID`, `HAVE_GMTIME_R`, `HAVE_LOCALTIME_R`, `HAVE_MREMAP`, `HAVE_STRCHRNUL`. In `metasploit`: `ENABLE_KASLR_BYPASS`, `ENABLE_SMEP_BYPASS`, `ENABLE_SMEP_SMAP_BYPASS`, `ENABLE_AUTO_TARGETING`, `ENABLE_FALLBACK_HELPERS`, `ENABLE_SYSTEM_CHECKS`, `COMPAT_GETFSSTAT`, `HAVE_CONFIG_H`, `STDC_HEADERS`, `DEBUG`.

**Class B correction, recorded because I got it wrong first.** My first pass classified `ENABLE_KASLR_BYPASS`, `ENABLE_SMEP_BYPASS`, `DOCORE`, `AKDEBUG`, `FREE_HMODULE_AFTER_LOAD`, `HASH_NONFATAL_OOM`, `OS_VXWORKS`, `TREETRACE_ENABLED`, `SQLITE_THREADSAFE` as "genuinely undefined." A second, tree-wide `#define` harvest proves all nine **are** defined in-tree (Metasploit `#define` set 6,046; Pupy 525; Sliver 3,763). The first pass under-harvested. **The direction of the error was toward MORE findings, which is the direction that manufactures defects.**

---

## §4. The 45 class-C sites are VENDORED — first-party is zero

Input cardinality: the class-C guard sites in all three conditional-bearing trees.

| Tree | Class-C guard sites | **VENDORED** | **FIRST-PARTY** |
|---|---|---|---|
| `metasploit` | 45 | **45** | **0** |
| `sliver` | 0 | — | **0** |
| `pupy` | 0 | — | **0** |
| `mythic` | 0 (no applicable files) | — | — |
| `covenant` | 0 (152 `.cs` searched) | — | **0** |

**Every one of the 45 is in `metasploit\external\source\`.** The 20 distinct identifier/file pairs, verbatim:

```
__MigTypeCheck              external\source\exploits\CVE-2016-4669\task.c
AKDEBUG                     external\source\pxesploit\regeditor\ntreg.c
DETOUR_DEBUG                external\source\byakugan\detours\creatwth.cpp
DETOUR_DEBUG                external\source\byakugan\detours\detours.h
DETOUR_DEBUG                external\source\byakugan\injectsu\detours.h
DOCORE                      external\source\pxesploit\regeditor\ntreg.c
EMS_SUPPORTED               external\source\vncdll\winvnc\libjpeg\jmemdos.c
EXNDEBUG                    external\source\pxesploit\regeditor\ntreg.c
FB_DEBUG                    external\source\pxesploit\regeditor\ntreg.c
IOCONNECT_NO_32B_METHODS    external\source\exploits\CVE-2016-4655\headers\IOKit\IOKitLib.h
IOCONNECT_NO_32B_METHODS    external\source\exploits\CVE-2017-13861\headers\IOKit\IOKitLib.h
TARGET_COS                  external\source\exploits\CVE-2021-22555\exploit.c
TARGET_UBUNTU               external\source\exploits\CVE-2021-22555\exploit.c
TRANSFORMS_SUPPORTED        external\source\vncdll\winvnc\libjpeg\jpegtran.c
TRANSFORMS_SUPPORTED        external\source\vncdll\winvnc\libjpeg\transupp.c
TRANSFORMS_SUPPORTED        external\source\vncdll\winvnc\libjpeg\transupp.h
UseStaticTemplates          external\source\exploits\CVE-2016-4669\task.c
XMS_SUPPORTED               external\source\vncdll\winvnc\libjpeg\jmemdos.c
ZEROFILL                    external\source\pxesploit\regeditor\ntreg.c
ZEROFILLONLOAD              external\source\pxesploit\regeditor\ntreg.c
```

Exact guard sites for the four with the most hits: `TARGET_UBUNTU` — **7 sites, all in `external\source\exploits\CVE-2021-22555\exploit.c`** (`:118`, `:411`, `:484`, `:611`, `:829`, `:854`, `:865`). `TARGET_COS` — **5 sites, same file** (`:174`, `:360`, `:831` `#elif`, `:857` `#elif`, `:867` `#elif`). `DETOUR_DEBUG` — **3 sites** (`byakugan\detours\creatwth.cpp:338`, `byakugan\detours\detours.h:415`, `byakugan\injectsu\detours.h:415`). `IOCONNECT_NO_32B_METHODS` — **2 sites** (`CVE-2016-4655\headers\IOKit\IOKitLib.h:1477`, `CVE-2017-13861\headers\IOKit\IOKitLib.h:1477`).

**These are upstream build switches.** `ntreg.c` (pxesploit's registry editor), `detours` (Microsoft Research's detour library), `libjpeg` `transupp`, `jmemdos`, and the two macOS IOKit CVE PoCs all expect their **upstream** Makefile to pass `-DTARGET_UBUNTU=1` / `-DDETOUR_DEBUG` / `-DIOCONNECT_NO_32B_METHODS`. No definition exists in the Metasploit tree because Metasploit does not build them.

**And the second, independent reason they are unreachable** (§5) makes the finding stronger than "the macro is undefined."

---

## §5. The vendored tree is excluded from the artifact, by name

Input cardinality: all build files in the Metasploit tree outside `external\` and `vendor\` — **15 found**.

The single reference to `external` in any of them:

```
metasploit-framework.gemspec:31    file =~ /^external|^docs|^\.solargraph\.yml/
```

That is an **exclusion pattern** in the gemspec's file list — `external` is removed from the packaged gem, alongside `docs` and `.solargraph.yml`.

And: **first-party build files = 0.** A search for `extconf.rb`, `CMakeLists.txt`, `*.vcxproj`, `configure` anywhere in Metasploit outside `external\` returns **0**. The 15 makefiles that do exist are in `data\` (`data\cmd_exec\makefile.mk`, `data\exploits\CVE-2019-13272\Makefile`, `data\exploits\CVE-2021-22204\Makefile`, `data\exploits\CVE-2022-0847\Makefile`, `data\exploits\osx\dump_keychain\Makefile`, `data\exploits\redis\exp\Makefile`, `data\exploits\redis\rmutil\Makefile`, `data\exploits\redis\Makefile`), `kubernetes\`, `lib\anemone\docs\`, and `test\` — **payload source compiled on the target, not by the framework.**

**So the 45 class-C sites are unreachable for two independent reasons:**
1. Their identifiers are undefined in all three definer sets (A: not a builtin; B: not configure-generated; C: no `#define` in-tree).
2. The subtree containing them is **excluded by name** from the packaged artifact, and **no first-party build rule compiles it.**

**That is the answer to the assignment, and it is a bounded negative.** The method ported cleanly, the operand was corrected, and the result is that **the class this method detects does not occur in first-party code in any of the five targets.**

---

## §6. The near-miss class — a named trap, with three measured instances

A substring probe over build files, answering a *definedness* question, returns false positives. D132 §2.1 established this for Havoc; the same shape recurs.

**Instance 1 — Havoc `SHELLCODE` (D132, cited).** `-SimpleMatch 'SHELLCODE'` over the 4 Havoc build files returns **7 hits** and *reads as "defined in the build."* All 7 are the literal word in non-directive text in `payloads\Shellcode\makefile`: `:10 EXECUTABLE_X64 = Bin/Shellcode.x64.exe`, `:11` the x86 twin, `:12`/`:13` the raw-binary output paths, and `:17`/`:23`/`:34` inside `@ echo` strings. **Zero are `-D` flags.** Independent spot-check this session: `CMakeLists.txt` carries **9 define-directives and 0 `SHELLCODE`/`SEND_LOGS`/`SVC_EXE` hits**; all three makefiles carry **0 define-directives**.

**Instance 2 — Havoc `EXE` (D132, cited).** `'EXE'` returns **19 hits**, all `-e,`/`exe`/`EXECUTABLE_X64` substrings, 0 real definitions.

**Instance 3 — Metasploit `external` (NEW, this report).** The probe "does Metasploit's build reference `external`?" returns **1 hit** — `metasploit-framework.gemspec:31` — and it *reads as "yes, the build references it."* It is an **exclusion** (`file =~ /^external|.../`), i.e. the exact opposite of a reference to build. **A substring probe answered a polarity question and inverted the polarity.**

**Why this belongs in the record as a named trap.** A rule built on "this code path exists in source" is a rule that can never fire if the path is dead, and a rule built on "this symbol appears in the build files" can fire on a filename, an echo string, a comment, or an *exclusion*. **Both failure modes are false-positive generators on the front end of a detection DB, and both are one substring probe away from being baked in.** The countermeasure is the one D132 applied and this report repeats: **read the hit at its `file:line` before filing it**, and state the operand.

---

## §7. Havoc cross-reference (not re-derived)

D132's §3 and §4 constrain how this census may be used downstream.

**The two dispatch axes (D132 §3).** The numeric axis is compiler-checked and **fails closed** — `Packager.cc:785-786 default: spdlog::error("[PACKAGE] Command not found")`, package dropped. The string axis is compiler-unchecked and **fails open** — `CommandOutput.cc` compares 12 literals (`"Error"`, `"Erro"`, `"Good"`, `"Info"`, `"Warning"`, `"Warn"`, `"screenshot"`, `"download"`, `"ProcessUI"`, `"FileExplorer"`, `"disconnect"`, `"reconnect"`) and an unmatched value is an unmatched branch, not an error. **A rule that keys on the string axis detects what the client renders; a rule that keys on the numeric axis detects what the protocol permits.** The string literals cannot be optimised away; the numeric cases are regenerable from a shared header.

**The DLL-name absence (D132 §4).** Havoc's Demon carries **0** DLL-name string literals because all 13 runtime libraries are loaded through names built one character at a time — **165 `ModuleName[ n ] =` assignment sites, all in `Runtime.c`**, at **scrambled indices**, each byte wrapped in `HideChar` (a function: `MiniStd.h:26 BYTE HideChar( BYTE C );`, 259 hits tree-wide), with `MemZero` on **both** the success and failure paths. **Detect the loader SHAPE, not the name.**

**How these bound this census.** §3's finding is that the dead-arm class is **absent from first-party code in all five targets**. That does *not* mean preprocessor arms are a safe basis for detection — it means the *dead-arm* direction is empty. The live direction is where Havoc's own D132 §2 result sits: `TRANSPORT_HTTP` / `TRANSPORT_SMB` / `DEBUG` / `AES256` are **defined in the build** (`CMakeLists.txt:77-79`, `:69`) and therefore **select real, compiler-verified code**, while `SEND_LOGS` / `SVC_EXE` / `SHELLCODE` / `TESTING_MATCHING_ROUTINE` select **nothing in any build this tree can produce**. **A DB must key on the four live macros and must not key on the four dead ones.** That asymmetry — same file, same shape, opposite reachability — is D132's result and is the reason this method was worth porting at all.

---

## §8. Instrument record

Four failures this session, all mine, all caught before a number was filed.

**Failure 1 — C-directive regex over non-preprocessor languages.** First census reported **1,979** `#if/#elif` in Metasploit; the C-family figure is **454**. The 1,525 difference is `#if` as a **Ruby comment** and as a **JavaScript string**. The same run produced six non-directive "candidates" (`son`, `database_enabled`, `useStaticTemplates`, `ZEROFILL`, `DOCORE`, `UseStaticTemplates`). **Fix:** restrict the operand to C-family extensions, and report the operand's file count beside every count.

**Failure 2 — under-harvested definer set.** Nine identifiers were first classified "genuinely undefined" (`ENABLE_KASLR_BYPASS`, `ENABLE_SMEP_BYPASS`, `DOCORE`, `AKDEBUG`, `FREE_HMODULE_AFTER_LOAD`, `HASH_NONFATAL_OOM`, `OS_VXWORKS`, `TREETRACE_ENABLED`, `SQLITE_THREADSAFE`) that a tree-wide `#define` harvest proves **are** defined in-tree. **The error direction was toward more findings** — the direction that manufactures defects. **Fix:** harvest `#define` across the whole tree into a set first, then classify against the set.

**Failure 3 — a source-only definer set is structurally blind to two whole classes.** Compiler builtins (10 identifiers) and configure-generated names (~205) are defined by the toolchain and by `configure`/`config.h`, **not in the source**. A source-only definer set reports both as dead. **Fix:** three independent definer sets (A builtin / B generated / C source), declared in the header.

**Failure 4 — `#define HideChar` → 0 hits (carried from D132 §6).** The symbol is a **function**, `MiniStd.h:26 BYTE HideChar( BYTE C );`; the real count is **259**. A macro-definition shape applied to a function-shaped symbol. This report's Failure 1 is the same root cause at a larger scale.

**The common root, stated once:** *a probe whose shape does not match the evidence's shape.* D132 logged it for a source symbol; this report logs it for a language and for a definer set.

**Two probes killed mid-run** for being oversized for the question asked (recursive `Select-String` across `sliver`'s 17,124 files and across both trees for a second time). Both had already produced the answer in their first block of output. Recorded because a probe that runs for minutes after answering the question is a probe whose result nobody will trust.

---

## §9. Residual unknowns

- **Class B is reported as ~205, not exactly.** The boundary between "configure-generated" and "build-supplied `-D`" is drawn by name prefix (`HAVE_`, `SQLITE_`, `ENABLE_`, `TARGET_`, `COMPAT_`, `STDC_`, `DEBUG`, `CONFIG_`, `USE_`, `WITH_`), which is **a heuristic, not a measurement**. The exact count depends on where that boundary is drawn, and the report says so rather than printing a precise-looking figure. Probe: read each of the 78 distinct identifiers' definition site.
- **Whether `defined()`-form conditionals are safe.** `#if defined(X) && X > 2` reads a **value** of a possibly-undefined `X`, which is 0 — a different defect from the bare form. **976** `defined()`-form conditionals were counted but **not** tested for this. Probe: extract every `defined()` expression containing a comparison operator.
- **`covenant`'s 152 `.cs` files** are counted as zero `#if/#elif`. That is a genuine zero on an applicable operand, but the C# preprocessor has additional forms (`#define`, `#pragma`, `#region`) not tested. Probe: `#define` census in the `.cs` tree.
- **`mythic`'s Go build tags.** Go uses `//go:build` constraints rather than `#if` — a **functionally equivalent dead-arm mechanism** with entirely different syntax. **Not tested in this report.** This is the most important residual: the method ported to three trees and *did not port* to Mythic, and the Go equivalent is untested. Probe: census `//go:build` / `// +build` lines across the 399 `.go` files against the build-tag set actually used.
- **Metasploit's 15 makefiles under `data\`** compile target-side payloads. Whether any of them passes a `-D` for a `TARGET_*`-style switch is unread. Probe: read each of the 15.
- **D-11 unchanged** (Pivots interleaving; needs execution, not attemptable in this lane).
- **D138 remains held** by `sliver-diver` for the R-130.3 PE-section job; not taken.

---

## §10. Validation

Recorded as measured numbers, not as a claim that a check passed.

| Property | Expected | Measured |
|---|---|---|
| Bytes | — | **27,552** |
| `\n` count | — | **268** |
| `\r` count | 0 | **0** |
| BOM | none | **absent** (first three bytes not `EF BB BF`) |
| UTF-8 strict decode (`UTF8Encoding($false,$true)`) | valid | **valid, no exception** |
| U+FFFD | 0 | **0** |
| Headings `^# [^#]` | exactly one H1 | **1 H1** |
| Headings `^## [^#]` | — | **11 H2** |
| Headings `^### [^#]` | — | **2 H3** |
| Fence lines `^``` ` | even (balanced) | **4, balanced** |
| Tail | `**End of D139.**` | **present** |
| SHA-256 | — | `12E36B79C0CEED1E48C59FF8753682D67814B1AA33B78F727276C854D763A902` |

**This table is a snapshot of one instant, and it says so because it demonstrated the problem on itself.**

The previous revision reported **25,826 bytes / 258 LF** with digest `9EEA1BA2…`; correcting it produced **27,552 / 268** with digest `12E36B79…`; correcting *that* — the text you are reading — produced **27,754** with digest `AAC4B4A2…`. **The act of correcting the table invalidated every number in it, three times running.** This is the D132 §8 result reproduced on the file that states the result, and it converges to a fixed point only in the direction that matters: **the heading counts, fence balance, encoding properties, and tail are TRUE of the final file** (re-measured after the last write: **1 H1 / 11 H2 / 2 H3, 4 fences balanced, no BOM, no CR, strict UTF-8, 0 U+FFFD, tail present, LF 268**). **Only the byte count is unstable, and only because the text describing the instability has bytes.**

**The resolution: the digest is authoritative, the byte count is a property of the digest.** The table above quotes the values as of `12E36B79…`. The final file's digest is `AAC4B4A2…` at **27,754 bytes / 268 LF**. Both are recorded because both are true of *a* revision, and a table that reported only the last one would be reporting a number it cannot re-verify.

Backtick parity is deliberately **not** reported anywhere in this file: the paragraphs discussing it introduce additional inline spans, so any figure quoted would be superseded by the text quoting it. **A metric that the reporting of it perturbs is not a metric of the file; it is a metric of the measurement order.** The structural checks that *are* stable are the ones quoted above.

**Two further corrections, recorded rather than silently replaced.** Placeholders I wrote before measuring (`10 H2`, `1 H3`) are replaced by measured **11 H2, 2 H3, 4 fence lines**.

**And a fifth instrument failure — the same family as the other four.** The first counting run returned **`h1/h2/h3 : 0 / 0 / 0` and `fence lines: 0`**. The file was fine: `$L[0]` begins `U+0023 U+0020` (`# `), a direct `-Match '^# [^#]'` on `$L[0]` returns **True**, and `Select-String -Pattern '^# '` finds the heading at `:1`. **The counter was composed inside a string-concatenation expression, where the pipeline was not evaluated as written.** Re-run with an explicit `foreach` accumulator and its own counters, it returns **1 / 11 / 2**. The durable form is the one already in this lane's guard list: **accumulate in a loop and print the counter, rather than composing a count inside a concatenation.**

What the broken counter printed is the part that matters: **zero.** Had it been trusted, the report would have asserted "0 headings" against a file whose first line is a heading, and "0 fence lines" against a file with 4. **A counter that fails toward zero does not look like a failure — it looks like a clean absence.** That is Rule 32's tell, and it is why the heading count is now taken and confirmed two independent ways before being written down.

The heading regex is stated with its basis: `#{1,}` for H1 would also match `##` and `###`, so it is the wrong regex. Counts use anchored, non-overlapping forms `^# [^#]`, `^## [^#]`, `^### [^#]`.

**End of D139.**
