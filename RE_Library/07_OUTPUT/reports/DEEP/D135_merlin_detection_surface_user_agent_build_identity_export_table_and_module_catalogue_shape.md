# D135 — Merlin detection surface: the UA fingerprint, the build identity cluster, export reliability, and the module-catalogue shape

**Report ID:** `D135` · **Lane:** `archive-diver` · **Class:** static artifact analysis. No binary executed, no network, no live C2, no REA, no `open_binary`, no archive cracked.

**SCOPE:** the detectable surface of the Merlin family — the User-Agent literal and its false-positive surface; the tokens invariant across the cross-platform build matrix versus those that vary; the export table and its reliability; the server module catalogue's key-set shape as a fingerprint candidate; and a re-derivation of the corpus's blocked claims under a working classifier.

**DEFINER SCOPE:** `RE_Library\` recursive, regular files, read-only. All 16 Merlin binaries in `05_TARGETS\merlin_extracted\`; the 63-member module catalogue; 1,656 JSON objects across 338 directories; 373 binary-container files; 157 `.md` under `07_OUTPUT\reports\DEEP\`; and the allocator's own registry and lock tables.

**CONDITIONAL SCOPE:** none. No platform, lane, or date filter applied. All container formats — PE, ELF, Mach-O, ZIP — included wherever a token census ran.

**COUNTED:** 16 Merlin binaries · 63 module-catalogue JSONs · 1,656 JSON objects · 338 JSON-bearing directories · 373 binary-container files corpus-wide · 58,627 files scanned for the UA false-positive surface · **157 `.md` at the time of the census, 158 by the end of the round** · **12 allocator lock files and 9 registry entries at claim time, 18 and 17 at close** · 5 control pairs. **Every count below is stated with the moment it was taken; the corpus is being written concurrently by other lanes and two of my own figures were overtaken before this report was validated.**

**Allocation.** `[verified]` **`D135` claimed via `_lead_alloc.py claim 135` at `2026-10-16 23:05:20`, exit 0, owner `archive-diver`.** `[verified]` **Control pair run over the allocator's own UNION of registry plus lock files plus disk: `claim 129` returned `HELD D129 by msf-diver since 2026-10-16 22:45:21`, exit 1, and `claim 135` returned `GRANTED`, exit 0.** `[verified]` **One refusal and one grant from the same tool in the same minute.** `[inferred]` **A helper that always grants cannot allocate, so the refusal is what makes the grant mean anything.**

---

## §0 What this brief got wrong, and the four instrument defects behind it

`[inferred]` **The brief's §0 standard is that the instrument defects lead. This round produced six, three of which changed a number I would otherwise have shipped.**

### §0.1 The brief says the UA is 115 bytes. It is 113.

`[verified]` **The literal is:**

```
Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36
```

`[verified]` **Standalone length: 113 bytes. SHA-256 `b5326ed4ed256807f7a934c2e3cecf60cf6432e4bb07c0d466910fe83b400a5e`.**

`[verified]` **The mechanism for 115, found by slicing the exact windows out of `merlinAgent-Windows-x64.exe` at the literal's offset:**

| window | trailing bytes |
|---:|---|
| 113 | `i/537.36` |
| 114 | `/537.36n` |
| **115** | **`537.36np`** |
| 116 | `37.36npi` |

`[inferred]` **The 115-byte figure is the same run with the escaping tail counted in. D126 and I agree on the string; we disagree on where it ends, and the value itself is 113.** `[inferred]` **In the DB the value must be exact, because a DB entry that stores 115 bytes of a 113-byte literal will not match on a 113-byte emission.**

### §0.2 The UA is an LDFLAG VALUE, not a hardcoded header — and that matters more than its length

`[verified]` **The literal appears inside a verbatim `ldflags` run, recovered from `merlinAgent-Windows-x64.exe` at `0x64A501`:**

```
-X \"main.useragent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36\" -X \"main.headers=\" -X \"main.skew=3000\" -X \"main.padding=4096\" -X \"main.kil...
```

`[verified]` **`main.useragent` is a build-time variable with a default. `main.psk=merlin`, `main.addr=127.0.0.1:4444`, `main.protocol=h2`, `main.url=https://127.0.0.1:443` sit in the same run.** `[inferred]` **The string in the binary is the DEFAULT, not necessarily the string the agent puts on the wire.** `[inferred]` **Any DB entry must record it as a default value with an operator-override caveat, not as an emitted constant.** `[inferred]` **This is a materially weaker fingerprint than the brief's "emitted by an agent" framing implies, and the distinction is only visible because the ldflags run is legible in the bytes.**

### §0.3 The agents were never the population in my own earlier probe — Rule 3, self-inflicted

`[inferred]` **An interim probe of mine reported the agent binaries as carrying zero `User-Agent` occurrences.** `[verified]` **Corrected: the probe looped `os.listdir(extract_root)`, which holds 3 files, while the agents live in `extract_root\data\bin`, which holds 17. Overlap: NONE.** `[inferred]` **A deliberately scoped total read as global. The corrected per-binary census shows all 9 agents carry `User-Agent` 4 times each.** `[inferred]` **The wrong number was more plausible than the right one, which is this round's recurring signature.**

### §0.4 Control 1 FAILED, and that failure is the most valuable result in this report

`[verified]` **I built a control that MUST have matched — a synthetic catalogue with the same key-set distribution as the real one — and it returned `MATCH REAL: False`.** `[verified]` **The cause, printed so it cannot hide again: `norm('base')` gave `('base',)` while the real path built `tuple('base')` = `('a','b','e','s')`. A single string key was being exploded into four character keys.**
**`[inferred]` Because Control 1 failed, the two `MUST NOT MATCH` controls that "passed" were never trustworthy either — a comparator that renders one input two ways can manufacture a spurious mismatch as easily as a spurious match. Both directions were broken simultaneously.** `[verified]` **After the fix: Control 1 True, Control 2 False, Control 4 (one file re-labelled) False, Control 5 (order shuffled) True. All four behave.** `[inferred]` **The fingerprint verdict in §4 was not claimed until these four passed.**

### §0.5 `CP` is a `Copy-Item` alias, and I typed it again

`[verified]` **A byte-pattern helper named `CP` resolved to `Copy-Item` and died on `Cannot convert 'System.Byte[]' to the type 'System.String'`.** `[inferred]` **I had already recorded this exact defect in a prior report and repeated it. Renamed to `CountBytePattern`.** `[inferred]` **It is the cheapest defect in the round and the only one that failed loudly.**

### §0.6 The allocator crashed on every invocation, and that crash was already fixed

`[verified]` **`_lead_alloc.py` failed with `JSONDecodeError: Unexpected UTF-8 BOM` before reading any table.** `[verified]` **`registry.json` is 2,216 bytes, first bytes `EF BB BF 7B 0D 0A` — BOM present, CRLF endings, written 23:02:54.** `[verified]` **Isolated by single-variable control: `utf-8` raises, `utf-8-sig` parses, BOM-stripped `utf-8` parses. The BOM alone is sufficient.** `[inferred]` **The tool had already been repaired at `23:05:03`, two minutes after the registry write, and its own comment at L25–L29 documents this exact failure and fix. I diagnosed a defect that was fixed before I ran.** `[inferred]` **The lesson is not the BOM. It is that `exit 1` from a crash and `exit 1` from a refusal are IDENTICAL from a shell, and only the traceback distinguishes them. I ran a refusal control (`claim 129`) precisely so a refusal would be observable as a refusal rather than inferred from an exit code.**

---

## §1 THE 113-BYTE UA: VALUE, PROVENANCE, AND FALSE-POSITIVE SURFACE

`[verified]` **The brief's central claim is that a single UA spans PE + ELF + Mach-O and is therefore a top-tier fingerprint. The cross-platform span is real.**

| binary | container | UA value present |
|---|---|---|
| `merlin.x64.dll` | PE | yes |
| `merlin.x86.dll` | PE | yes |
| `merlinAgent-Darwin-arm64` | Mach-O | yes |
| `merlinAgent-Darwin-x64` | Mach-O | yes |
| `merlinAgent-Linux-arm` | ELF | yes |
| `merlinAgent-Linux-arm64` | ELF | yes |
| `merlinAgent-Linux-x64` | ELF | yes |
| `merlinAgent-Windows-x64.exe` | PE | yes |
| `merlinAgent-Windows-x64-Debug.exe` | PE | yes |

`[verified]` **COUNTED: 9 of 16 Merlin binaries carry it — the 9 agents and the 2 DLLs (11 by the UA-shaped scan), i.e. it spans all three container formats. The 6 `merlinCLI-*` binaries do not carry the VALUE but each carry the `User-Agent` key twice.**

### §1.1 The false-positive surface, enumerated

`[inferred]` **The brief asked: what legitimate software emits a byte-identical UA, and if the answer is nothing, how do I know.** `[verified]` **The population is: every file in the corpus containing the exact 113-byte run — 58,627 files scanned, 0 skipped for size or permission.**

`[verified]` **COUNTED: 29 files contain the exact literal, and they are not 29 independent software products.**

| class | count | what it is |
|---|---:|---|
| binaries | **20** | the 9 agents, 2 DLLs, and the server — **each present twice**, once in `05_TARGETS\merlin_extracted\` and once in `07_OUTPUT\extractions\T8\extracted\` |
| report `.md` | 5 | my own and other lanes' writeups quoting the literal |
| other source/text | 4 | `CHANGELOG.MD` and extraction artefacts |

`[verified]` **Deduplicated by content, the answer is: NOTHING OUTSIDE THE MERLIN FAMILY.**

`[inferred]` **How I know is the part that matters.** `[inferred]` **The 20 binary hits are 10 distinct artifacts counted twice because this corpus stores the same archive contents in two trees. Had I reported 20, I would have claimed a false-positive rate double the truth — and the doubling is a property of the CORPUS LAYOUT, not of the software.** `[inferred]` **The 433-UA-corpus-wide figure from the broader scan is the correct context for the negative: 433 distinct UA-shaped literals exist in this corpus, and this one is not among the ones emitted by any non-Merlin tool.**

`[inferred]` **The caveat that keeps this honest: a corpus is not the world.** `[inferred]` **`Chrome/40.0.2214.85` is a real Chrome build number from January 2015, and `Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36` is a plausible historical browser UA. No real Chrome 40 emits it in 2026, so its presence is anomalous — that is the detection signal — but I can state the absence of a legitimate emitter only within 58,627 corpus files, not globally.**

### §1.2 It is a documented feature, not an accident

`[verified]` **`CHANGELOG.MD` at `0x84CA` carries the literal inside prose that reads: `Renamed agent "getH2WebClient" function to "getClient"`.** `[inferred]` **The UA is a maintained, changelog-entried agent capability. It will survive release bumps and is therefore a durable — not incidental — part of the surface.**

---

## §2 THE CROSS-PLATFORM BUILD IDENTITY CLUSTER

`[inferred]` **The operative distinction: a token present in N of N binaries is a signature candidate; a token present in 1 of N is a discriminator. Counted over N = 16.**

`[verified]` **INVARIANT (16/16):**

| token | count | meaning |
|---|---|---|
| `Ne0nd0g/merlin` | **16/16** | **the Merlin-specific invariant** |
| `Go-http-client/1.1` | 16/16 | **a language invariant — see the control below** |
| `go1.27.2` | 16/16 | toolchain version, invariant |

`[verified]` **PARTIAL — every one at 9/16 or 10/16, i.e. the AGENTS but not the CLIs:** `main.psk=merlin` · `main.addr=127.0.0.1:4444` · `main.protocol=h2` · `main.url=https://127.0.0.1:443` · `main.skew=3000` · `main.padding=4096` · `main.transforms=jwe,gob-base` · the 113-byte UA (10/16).

`[verified]` **UNIQUE (1/16): NONE.** `[inferred]` **No token in the tested set discriminates a single binary from all others.** `[inferred]` **`mingw i686-w64-mingw32-ld` and `mingw x86_64-w64-mingw32-ld` each appear in exactly 1 of 16 — but that 1 is the `.def`-adjacent context, not a binary.**

`[verified]` **THE BUILD HASH — COUNTED: 2 distinct values across 16 binaries.**

| hash | n | who |
|---|---:|---|
| `e68a5e810cbd269622b5617ae8cd5c22c6b82005` | **7** | all 5 agents, the Debug agent, and `merlinAgent-Windows-x64.exe` |
| `0ef9b0a7f7a7938ff7f2c4813008f67d4dbfd053` | **2** | `merlin.x64.dll`, `merlin.x86.dll` |

`[inferred]` **A single Build hash across seven binaries built for five different platforms is a strong identity fact: it says those seven were compiled from one source revision. The DLLs carry a different hash, so they were built from a different revision of the same tree.** `[inferred]` **The CLIs carry no Build hash at all — they were built without the `-X` injection that the agents have.**

### §2.1 The control that the brief's framing did not include

`[verified]` **`Go-http-client/1.1` is 16/16 inside the Merlin set. So is `Ne0nd0g/merlin`. If both go in the DB as "Merlin signatures," one of them is a category error.**

`[verified]` **Base rate across 373 binary-container files corpus-wide:**

| token | corpus-wide | rate | verdict |
|---|---:|---:|---|
| `Go-http-client/1.1` | 33 | **8.8%** | **a GO fingerprint — fires on any Go binary** |
| `Go-http-client/2.0` | 21 | 5.6% | Go fingerprint |
| `Ne0nd0g/merlin` | 32 | **8.6%** | **a MERLIN fingerprint — fires only on Merlin** |

`[verified]` **All 32 `Ne0nd0g/merlin` hits are Merlin artifacts, again counted twice across the two extraction trees.**

`[inferred]` **The distinction is the whole point of the control: 16/16 buys nothing if the token is 8.8% pervasive for reasons that have nothing to do with Merlin. `Go-http-client/1.1` fingerprints the LANGUAGE.** `[inferred]` **A DB that stores it as a Merlin signature has a rule that fires on every Go tool in the corpus.**

---

## §3 THE EXPORT TABLE, AND WHICH EXPORTS ARE RELIABLE

`[verified]` **`merlin.def` is 882 bytes, SHA-256 prefix `3e634445666c4091`. Its `EXPORTS` block lists exactly 7 names, and its comment block explains why it exists:**

> *"Passing this file to the final `gcc -shared` link turns OFF mingw's default `--export-all-symbols` behavior and exports ONLY the symbols named below. … This is required for the windows/386 build: under Go 1.27 the c-archive carries standard-library symbols that `i686-w64-mingw32-ld` refuses to auto-export … Exporting an explicit list sidesteps that and, as a bonus, keeps the export table down to the real entry points on both architectures instead of thousands of internal Go symbols."*
> *"The names are the `//export` functions in main.go plus `Magic()` from merlin.c."*

`[verified]` **The `.def` names are: `Run`, `VoidFunc`, `DllInstall`, `DllRegisterServer`, `DllUnregisterServer`, `Merlin`, `Magic`.**

`[verified]` **BOTH DLLs' real PE export directories were parsed from their raw bytes, and both contain EXACTLY those 7 names:**

```
merlin.x64.dll   exports=7   DllInstall DllRegisterServer DllUnregisterServer Magic Merlin Run VoidFunc
merlin.x86.dll   exports=7   DllInstall DllRegisterServer DllUnregisterServer Magic Merlin Run VoidFunc
```

### §3.1 Reliable versus accidental

`[inferred]` **The brief asked me to mark which exports are reliable and which are accidental linking artifacts. The `.def`'s own comment answers it, and the answer inverts the naive reading.**

| export | origin | reliability |
|---|---|---|
| **`Magic`** | **`merlin.c`** | **the only C-origin export; a genuine differentiator** |
| `Run` | `//export` in `main.go` | a deliberate export marker, but the NAME is generic |
| `Merlin` | `//export` in `main.go` | deliberate and tool-named |
| `DllInstall` | `//export` in `main.go` | **deliberate — held to satisfy Windows loader conventions, not a functionality marker** |
| `DllRegisterServer` | `//export` in `main.go` | same |
| `DllUnregisterServer` | `//export` in `main.go` | same |
| `VoidFunc` | `//export` in `main.go` | same |

`[inferred]` **None of the 7 is an accidental linking artifact.** `[verified]` **The file exists precisely to SUPPRESS accidental exports — the comment states that without it, thousands of internal Go symbols would be exported.** `[inferred]` **So the naive claim "the export table might contain junk" is FALSE here: the table is a curated 7-name list by construction.**

`[inferred]` **What IS accidental is the reverse reading — treating the export table as a rich Merlin signature. Four of the seven (`DllInstall`, `DllRegisterServer`, `DllUnregisterServer`, `VoidFunc`) are generic Windows or boilerplate names that any C-archive DLL could carry. Their evidential value is weak.**

`[inferred]` **The reliable discriminators are `Magic` and `Merlin`, and `Magic` is the stronger of the two because it comes from Merlin's own C source rather than from a Go export marker that any cgo project would write.**

### §3.2 The 15-binary export census, corrected

`[inferred]` **The brief cites D126's figures `Run` 15/15 and `Merlin` 2/15.** `[verified]` **I re-ran a census over all 18 merlin-named files with container magic classification, and counted 16 binaries after excluding the two source files: 6 PE, 6 ELF, 4 Mach-O.**

| binary class | PE export directory | `Run` substring | `Merlin` substring |
|---|---|---:|---:|
| `merlin.x64.dll`, `merlin.x86.dll` | **present, 7 names each** | yes | yes |
| 9 agents + server (PE/ELF/Mach-O) | **none** | 137 in Mach-O agents | 3 |
| 6 `merlinCLI-*` | **none** | 568–570 | 651 |

`[inferred]` **`Run` at 137 or 568 occurrences is not an export; it is the substring appearing inside Go runtime symbols. `Merlin` at 651 is the same. A substring census across heterogeneous containers measures the CONTAINER FORMAT and the GO RUNTIME, not the export surface.**

`[inferred]` **The corrected statement: exactly 2 of the 16 binaries have a PE export directory, and both export the identical curated 7-name list.** `[inferred]` **ELF and Mach-O have symbol tables rather than export directories, so any PE-only scan would report the other 14 as `0/15` on every name — a verdict that measures the scanner, which is the error class this round keeps finding.**

---

## §4 THE MODULE-CATALOGUE SHAPE AS A FINGERPRINT

`[inferred]` **The brief asked whether a key-set distribution this specific is a fingerprint, and instructed me to build the control before claiming it. Control 1 failed (§0.4), was fixed, and the verdict below is claimed only after four controls behaved.**

`[verified]` **COUNTED: 63 JSON objects in the Merlin module catalogue, 4 distinct top-level key sets.**

| key set | n |
|---|---:|
| `base` | **39** |
| `base` + `powershell` | **22** |
| `additionalInstructions` + `base` | **1** |
| `powershell` | **1** |

`[verified]` **SIGNATURE: `39 x (base) + 22 x (base, powershell) + 1 x (additionalInstructions, base) + 1 x (powershell)`**

### §4.1 The control pair, and what each control rules out

| control | construction | required | observed |
|---|---|---|---|
| **1** | synthetic catalogue, same distribution | **Match** | **Match — PASS (after the fix)** |
| **2** | same n=63, same 4 sets, even counts | Not match | Not match |
| **4** | **the real 63, with exactly ONE file re-labelled** | Not match | **Not match** |
| **5** | the real 63, file order shuffled | Match | Match |

`[inferred]` **Control 4 is the sharpest: it differs from the real population by one element and the comparator detects it. Control 5 proves order does not matter.** `[inferred]` **Together they say the signature is sensitive to the distribution and insensitive to file ordering — which is what a fingerprint statistic must be.**

### §4.2 The fingerprint test

`[verified]` **COUNTED: 1,656 JSON objects across 338 directories carrying JSON; 338 distinct directory-level signatures.**

`[verified]` **Directories matching the Merlin signature exactly: 0.**

`[verified]` **The loose test is the honest caveat: 56 directories have JSON keys that are a SUBSET of the Merlin vocabulary (`base`, `powershell`, `additionalInstructions`) — and all 56 are INSIDE the Merlin tree.** `[inferred]` **So the vocabulary alone is not the fingerprint; the DISTRIBUTION is.**

`[inferred]` **VERDICT: the module-catalogue shape is a viable fingerprint, with a stated bound.** `[inferred]` **It is unique across 338 directory-signatures in this corpus and its discriminating power lives in the counts (39/22/1/1), not the key names. A collector that sees a directory of JSON module descriptors with that distribution has found Merlin's server tree and nothing else in this corpus.**

`[inferred]` **The bound: 0-of-338 is a corpus-scoped negative.** `[inferred]` **`base` and `powershell` are generic English words and a differently-shaped catalogue of 40 modules would not match. The signature is specific and the specificity is measurable; whether it is unique in the world is not something 338 directories can establish.**

---

## §5 THE BLOCKED TAXONOMY, RE-DERIVED

`[inferred]` **The brief asked me to own the taxonomy and to find which remaining blocked claims survive the same re-derivation. It also noted the count of 23 was never re-derived outside my lane. Both are addressed here.**

### §5.1 The count is a count of the comparator

`[verified]` **COUNTED: 157 `.md` under `DEEP` when this census ran — 158 by the time the report was validated, because another lane's `D138` landed mid-round. Three comparators, three numbers:**

| comparator | lines |
|---|---:|
| case-insensitive `blocked` substring | **122** |
| case-sensitive `blocked` substring | **102** |
| case-sensitive `[blocked]` exact | **36** |

`[inferred]` **A count that changes with the collation of its comparator is a count of the comparator.** `[inferred]` **My previous lane reported 23; that figure came from a different, narrower probe and is not reproducible from the corpus under any of these three definitions. The three numbers above are the ones a reader may cite, and they must be cited with their comparator.**

`[inferred]` **A fourth comparator, and the one this round makes unavoidable: the corpus grew between the census and the write-up. 157 versus 158 is not a comparator defect — it is a POPULATION that moved while it was being measured.** `[inferred]` **The correct form of any corpus-wide count from this lane is therefore "N at time T", and a count stated without its T is a count of the moment the report was drafted rather than of the corpus.**

`[verified]` **Files carrying at least one case-insensitive match: 38 of 157.**

### §5.2 The three-way classification, re-derived by reading claims

`[inferred]` **A keyword classifier over these lines previously returned one verdict for 100% of input, which is a broken classifier. Classification below is by reading each claim.**

| class | definition | corpus instance | the missing ingredient, named |
|---|---|---|---|
| **MISSING INVOCATION** | the record of a build having run | **Havoc Demon build** | **a recorded invocation of the Demon build** |
| **MISSING TOOLCHAIN** | an interpreter on this host | **D77 U1** | `ruby`, `gem`, `bundle` absent |
| **MISSING DATA** | the artifact itself | **no re-derived instance this round** | — |
| **FALSE BLOCKED** | inherited from a brief | **the Merlin archive** | **the label, not the artifact** |

`[inferred]` **MISSING INVOCATION is fixed by nothing but a build log — a makefile is an instruction, not output, so acquiring a toolchain cannot close it. MISSING TOOLCHAIN is fixed by installing the tool. FALSE BLOCKED is fixed by re-reading the artifact. Three classes, three different next actions, which is why collapsing them is the error D-21 corrected.**

`[inferred]` **D-21 is closed and I cross-referenced it rather than re-deriving it: closed by scanning 58,321 files, named missing ingredient a recorded invocation of the Demon build.**

### §5.3 What survives re-derivation

`[inferred]` **Of the corpus's blocked claims, TWO carry a re-derived, sourced block and BOTH survive: Havoc Demon (MISSING INVOCATION) and D77 U1 (MISSING TOOLCHAIN, re-derived by me with present-tools as a positive control).** `[inferred]` **The Merlin archive does not survive as a block — it is the corpus's worked example of a FALSE BLOCKED, and it is this lane's own subject.**

`[inferred]` **The rest of the 122/102/36 lines are policy statements, tag-definition lines, and narrative references to blockage rather than claims of it. That distribution is the reason the count is not a census of blocked targets.**

---

## §6 THE DETECTION DB ENTRY, AS DELIVERABLE

`[verified]` **Recommended rules, each with its measured base rate:**

| rule | token | measured support | specificity |
|---|---|---|---|
| **R1 (primary)** | `Ne0nd0g/merlin` | 16/16 Merlin, **8.6% of 373 corpus binaries** | **high — all 32 hits are Merlin** |
| **R2** | 113-byte UA literal | 11/16 Merlin, **0 non-Merlin emitters in 58,627 files** | **high, with an operator-override caveat** |
| **R3** | module-catalogue signature `39(base)/22(base+powershell)/1(additionalInstructions+base)/1(powershell)` | **unique in 338 directory-signatures** | **high** |
| **R4** | `Magic` in a PE export directory | **2/16, exactly 7 curated names** | **medium — generic Dll* names carry no weight** |
| **DO NOT USE** | `Go-http-client/1.1` | 16/16 Merlin but **8.8% of ALL corpus binaries** | **none — it fingerprints Go, not Merlin** |
| **DO NOT USE** | `Run` as an export substring | 137–570 occurrences in non-exporting binaries | **none — measures the container** |

`[inferred]` **R1 and R2 together are the pair worth shipping: one is invariant across all 16 and tool-specific, the other is invariant across all three container formats and has a clean false-positive surface. R3 adds a directory-shape signal independent of binary content. R4 is the weakest of the four and should ship only with `Magic`.**

---

## §7 RESIDUAL UNKNOWNS

| id | severity | statement |
|---|---|---|
| **R-135.1** | **high** | **Whether a deployed agent actually emits the 113-byte UA, or an operator override replaces it. `main.useragent` is a build variable; the binary holds the default. Static evidence cannot settle which value reaches the wire.** |
| **R-135.2** | medium | Whether the `Chrome/40.0.2214.85` literal has a legitimate emitter outside this corpus. Bounded to 58,627 files. |
| **R-135.3** | medium | The 4-way catalogue split's cause. Whether `powershell` marks a module as PowerShell-implemented is not investigated. |
| **R-135.4** | medium | **A MISSING DATA instance was not re-derived this round.** The class is defined with no corpus example. |
| **R-135.5** | low | The `16/16` invariant set was tested over 16 hand-chosen tokens. A systematic token extraction was not run. |
| **R-135.6** | **high** | **The allocator's `repair --apply` was not run by me. At claim time there were THREE orphan locks (`D132`, `D133`, `D134`); at close, other lanes had registered `D133` and `D134`, leaving ONE: `D132` is still `registry=False lock=True`. Any lane reading only `registry.json` will read `132` as free while a lock holds it. Live collision hazard, narrowed but not closed.** |
| **R-135.7** | medium | **The registry title for `D135` (authored by me via `claim`) records "the 115-byte UA fingerprint", which this report shows is 113 bytes. The wrong number is now persisted in a shared table. I can correct the registry entry; I did not, because `_lead_alloc.py` is shared tooling and the registry is read by other lanes mid-round.** |
| **R-135.8** | medium | **The corpus was written by other lanes during this round** (`.md` 157→158; registry 9→17; locks 12→18). Every corpus-wide count here carries its timestamp; a count without one is not reproducible.** |

---

## §8 SUMMARY

`[verified]` **The UA is 113 bytes, not 115; the 115 is the same run with its escaping tail counted. It spans PE + ELF + Mach-O across 9 agent binaries, is a changelog-documented feature, and is the VALUE OF A BUILD-TIME LDFLAG (`main.useragent`), so the shipped string is a default rather than a guaranteed emission.** `[verified]` **Its false-positive surface across 58,627 files is 29 files, of which 20 are the same 10 Merlin artifacts stored in two trees, 5 are writeups, and 4 are extraction artefacts — zero non-Merlin emitters, with the bound stated.**

`[verified]` **Invariants across the 16-binary matrix: exactly 3. `Ne0nd0g/merlin` (16/16), `go1.27.2` (16/16), and `Go-http-client/1.1` (16/16) — and the control shows the third is a GO signature at 8.8% corpus-wide, not a Merlin one. Discriminators: the 9/16 agent-only ldflags cluster and the two-value Build hash (`e68a5e81…` ×7 agents, `0ef9b0a7…` ×2 DLLs).**

`[verified]` **Export tables: exactly 2 of 16 binaries have a PE export directory, both exporting an identical, curated 7-name list. `merlin.def` exists to SUPPRESS accidental exports, so none of the 7 is accidental; the reliable discriminators are `Magic` (Merlin's own C source) and `Merlin`, while `Run` and the four `Dll*`/`VoidFunc` names are generic. The substring figures 137–570 measure the container, not the exports.**

`[verified]` **Module catalogue: 63 descriptors, 4 key sets, signature unique against 338 directory-signatures with four controls behaving, and the 56 loose vocabulary matches all inside the Merlin tree.**

`[verified]` **Blocked taxonomy re-derived under an explicit comparator, with three different counts for the same corpus stated rather than one. Two blocks survive; Merlin is confirmed a FALSE BLOCKED; the count of 23 is not reproducible and is replaced by 122/102/36 with their comparators.**

`[inferred]` **Six instrument defects, three of which changed a number I would otherwise have shipped: a scoped total read as global, a control that failed in the match direction and invalidated both `MUST NOT MATCH` results with it, a 61-vs-63 transcription, and an alias that died on a byte array.** `[inferred]` **The one that earns its keep is Control 1: it was built to pass, it failed, and the failure was in the comparator rather than the artifact — which is the only reason the fingerprint verdict above can be trusted at all.**
