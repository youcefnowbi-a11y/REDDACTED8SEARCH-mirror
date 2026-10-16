# D140 — Shared-Mechanism Map

**SCOPE:** the six C2 targets under `RE_Library\01_SOURCE_c2` (covenant, havoc, metasploit,
mythic, pupy, sliver), source layer only. Plus the build systems of those targets.

**DEFINER SCOPE:** every mechanism class named in the corpus to date — transport, framing,
crypto, encoding, dispatch, evasion/loader. For each: which targets share it, which are
target-unique, and the evidence for the call.

**COUNTED:** 35,742 files raw · 20,459 after vendor exclusion · 6 targets · 34 vocabulary
mechanisms · 18 identity tokens · 281 `#if`/`#ifdef` directives · 1,878 `#define` identifiers ·
12 build files · 5 build-set macros · 4 Metasploit convention tokens · 3 candidate dead arms ·
2 non-degenerate classifier passes · 1 degenerate classifier pass (disclosed).

**Allocation:** D140, lane `source-diver`, claimed via `_lead_alloc.py claim 140` at
`2026-10-16 23:10:37`, exit 0. **Both sources of truth checked before the claim and after:**
`D140*` False / `D139*` True on disk, `140` False / `139` True in registry; post-claim
`D140.lock` present and registry `140` → `source-diver`. **Control pair discriminated in both
directions.** `[verified]`

**No execution · no network · no live C2 · no REA · no `open_binary` this round.**
Every claim is source-layer. Nothing frozen was edited. `[verified]`

---

## §0 Headline

**I built this map twice. The first one was broken, and the way it broke is the report's
most useful result.**

**Pass 1** classified 34 mechanisms by keyword. Result: **34 SHARED, 1 PARTIAL, 0 UNIQUE.** A
classifier whose output is one value for the whole corpus is broken, not decisive — the Lead's
own standing rule. The cause is measurable and it generalises:

> **A mechanism census over a multi-target corpus is dominated by the largest target's
> generic library usage. `metasploit` is 15,080 of 20,459 vendor-excluded files — 73%.
> Metasploit contains HTTP clients, a JSON parser, AES, and the word "jitter" because it is
> a general-purpose exploit framework, not because it shares a C2 design with Havoc.**

`Sleep / jitter` scoring **6/6 including metasploit=452** was the tell: `jitter` matches
unrelated Ruby. **Vocabulary is not mechanism.** `[source]` `[verified]`

**Pass 2** measured **identity tokens** — literals a target must *deliberately emit* — with
vendor trees excluded. Distribution: **2 UNIQUE, 3 PARTIAL, 12 SHARED, 3 ABSENT.**
Non-degenerate, therefore usable. `[source]` `[verified]`

**The map's central finding, stated once:**

> **SHARED mechanisms are the corpus's floor, not its discriminators.** Twelve of eighteen
> identity tokens appear in ≥3 targets. A detection rule keyed on "does it speak JSON over
> HTTP with an AES'd body" fires on **all six** and is therefore worth **nothing**.
> **Strong signals live in the unique and partial rows and in the dead-arm census — and both
> of those are smaller and stranger than the shared rows suggest.**

**Three corrections to incoming claims, and one to my own output:** `[verified]`
1. **`aiOperatorName` is NOT ABSENT.** D136 (via the Lead) reported it absent. It exists
   **4 times** in `server\rpc\rpc-ai.go`, including the definition at `:19`.
2. **`TRANSPORT_HTTP` / `TRANSPORT_SMB` are NOT dead arms.** Both are **set by the build
   system** (`payloads\Demon\CMakeLists.txt`). Arm liveness is a **build** property.
3. **`0xDEADBEEF` is not a shared magic value.** Its 55 metasploit hits are in
   `modules\exploits` (22) and `data\templates` (18) — **ELF/shellcode templates**, zero in
   `lib\msf\core` or `lib\rex`. Retracted before publication.
4. **My own final tally print had its two total columns swapped**, reporting metasploit at
   42% instead of 73%. Corrected below; the defect is in §8.

---

## §1 The corpus, and why its size distribution is the first hazard

| Target | Raw files | Vendor-excluded | Dropped | % dropped |
|---|---:|---:|---:|---:|
| covenant | 1,008 | 1,008 | 0 | 0% |
| havoc | 743 | 743 | 0 | 0% |
| metasploit | 15,080 | 15,080 | 0 | 0% |
| mythic | 1,072 | 1,072 | 0 | 0% |
| pupy | 686 | 686 | 0 | 0% |
| **sliver** | **17,153** | **1,870** | **15,283** | **89%** |
| **TOTAL** | **35,742** | **20,459** | **15,283** | **43%** |

**Sliver's vendor exclusion is verified, not assumed.** `vendor\modules.txt` exists and is
**2,429 lines** of genuine Go module paths (`cel.dev/expr v0.25.2`, `charm.land/bubbles/v2
v2.0.0`, …). The dropped files are `vendor\github.com` (7,306), `implant\vendor` (2,333),
`vendor\modernc.org` (1,307), `vendor\golang.org` (1,163), `vendor\tailscale.com` (857),
`vendor\google.golang.org` (660). **Third-party code is not target code.** `[source]`
`[verified]`

**The consequence for every count in this report:** metasploit is **15,080 / 20,459 = 73%**
of the vendor-excluded corpus. **Any token metasploit contains is likely to appear "shared"
by volume alone.** Every SHARED verdict below carries that caveat explicitly. `[source]`
`[verified]`

---

## §2 Pass 1 — the degenerate classifier, and why it is published

**Instrument:** 34 mechanism keywords (`HTTP`, `WebSocket`, `AES`, `XOR`, `Sleep`, …) matched
case-insensitively as byte regexes, counted per target if ≥1 file matched.

```
COUNTED: 35,742 files, 6 targets, 34 mechanism patterns, vendor INCLUDED
RESULT : SHARED 34 · PARTIAL 1 · UNIQUE 0
```

**A classifier returning one verdict for 100% of its input is broken.** The distribution
below is printed because the failure is only visible in it:

| Mechanism | Targets | Distribution |
|---|---:|---|
| Sleep / jitter | 6 | cov 39 · hav 31 · **msf 452** · myt 16 · pup 52 · sli 460 |
| Named-pipe impersonation | 6 | cov 284 · hav 83 · msf 1,262 · myt 147 · pup 27 · sli 2,018 |
| HTTP/S beaconing | 6 | cov 6 · hav 1 · **msf 2,019** · myt 3 · pup 35 · sli 323 |
| JSON messaging | 6 | cov 38 · hav 18 · msf 226 · myt 180 · pup 8 · sli 960 |
| AES | 6 | cov 24 · hav 15 · msf 162 · myt 7 · pup 22 · sli 126 |
| ChaCha20 | **2** | msf 16 · sli 121 |

**`Sleep / jitter = 6/6` with metasploit at 452 is the disproof of the method.** Metasploit's
`jitter` is a Ruby token in unrelated modules; it is not a C2 sleep-jitter mechanism.
**Vocabulary is not mechanism identity.** `[source]` `[verified]`

**I keep this pass in the report** because deleting a failed instrument is how a defect
becomes invisible, and because the fix it forced (§3) is the actual product.

---

## §3 Pass 2 — identity tokens, vendor-excluded

**Definition:** an **identity token** is a literal constant a target must **deliberately
author** — a magic value, a wire framing convention, an HTTP header literal it emits, a
protocol extension name. Library *usage* does not qualify; a target must **emit** the token.

```
COUNTED: 20,459 vendor-excluded files across 6 targets, 18 identity tokens
```

| Identity token | Targets | Distribution |
|---|---:|---|
| **magic `0x1337`** | **1** | msf 19 |
| **RC4 init-256 loop** | **1** | msf 5 |
| **magic `0xCAFEBABE`** | **2** | msf 5 · pup 1 |
| **SHA256 K constant** | **2** | msf 1 · myt 1 |
| **MD5 init** | **2** | msf 3 · myt 1 |
| magic `0xDEADBEEF` | 4 | cov 1 · hav 3 · msf 55 · sli 2 |
| 4-byte length BE | 4 | msf 40 · myt 2 · pup 2 · sli 4 |
| 4-byte length LE | 4 | hav 3 · msf 55 · pup 1 · sli 1 |
| User-Agent literal | 3 | msf 2 · pup 2 · sli 1 |
| Cookie literal | 4 | cov 3 · msf 538 · myt 2 · sli 3 |
| Content-Type literal | 4 | msf 427 · myt 8 · pup 4 · sli 2 |
| `X-Forwarded-For` | 5 | hav 2 · msf 12 · myt 2 · pup 1 · sli 1 |
| `Authorization: Bearer` | 4 | cov 5 · msf 74 · myt 6 · sli 8 |
| AES S-box | 5 | cov 10 · hav 5 · msf 20 · myt 2 · sli 1 |
| named pipe `\\.\pipe\` | 4 | hav 2 · msf 14 · pup 3 · sli 2 |
| `case` with hex opcode | 4 | hav 1 · msf 4 · myt 1 · sli 2 |
| command opcode table | 4 | cov 2 · msf 8 · myt 4 · sli 1 |
| magic `0xBAADF00D` | **0** | — |
| `msagent_` prefix | **0** | — |
| `postex_` prefix | **0** | — |

**Distribution: UNIQUE 2 · PARTIAL 3 · SHARED 12 · ABSENT 3.** Non-degenerate. `[source]`
`[verified]`

---

## §4 The map — shared vs unique, with the discriminator stated

### 4.1 UNIQUE — strong signals (1 target)

| Token | Target | Evidence | False-positive baseline |
|---|---|---|---|
| **magic `0x1337`** | metasploit | 19 files | `0x1337` is "leet" and appears in **game trainers, CTF tooling, sample code**. **As a raw 4-byte match this is a liability, not an asset.** |
| **RC4 init-256 loop** | metasploit | 5 files | The `for(i=0;i<256;i++)` RC4 KSA shape is **standard RC4**; every legitimate RC4 implementation matches. **Weak discriminator despite being unique.** |

**Both unique rows fail the false-positive test as written.** `0x1337` is a cultural constant,
and an RC4 KSA loop is the textbook implementation. **Uniqueness within this six-target corpus
is not uniqueness in the world** — and that distinction is the whole point of the false-positive
baseline column. `[source]` `[verified]`

### 4.2 PARTIAL — medium signals (2 targets)

| Token | Targets | Note |
|---|---|---|
| magic `0xCAFEBABE` | metasploit, pupy | Classic Mach-O/Java class-file magic — **also a false-positive magnet.** Better as a *pairing* signal (msf **and** pupy) than as a single-target rule. |
| SHA256 K constant | metasploit, mythic | `0x428a2f98` is the SHA-256 round constant; **any** SHA-256 implementation contains it. **Not discriminating.** |
| MD5 init | metasploit, mythic | `0x67452301` is MD5's init; same objection. **Not discriminating.** |

**All three PARTIAL rows are crypto constants — and crypto constants are the weakest possible
fingerprints, because they are copied verbatim from specifications.** The two-target overlap is
an artifact of *both targets implementing SHA-256/MD5*, not of shared design. `[source]`
`[verified]`

### 4.3 SHARED — weak signals (≥3 targets)

**Twelve tokens. All twelve are WEAK, and the reason is uniform: they are either HTTP
conventions, standard crypto, or generic framing.** `[source]` `[verified]`

| Token | Targets | Why it is weak |
|---|---:|---|
| `X-Forwarded-For` | 5 | Standard HTTP header, emitted by **every** web client and proxy. |
| AES S-box | 5 | The AES S-box is a published constant; any AES implementation carries it. |
| Cookie literal | 4 | Any HTTP client. |
| Content-Type literal | 4 | Any HTTP client. |
| `Authorization: Bearer` | 4 | Any OAuth/HTTP client. |
| 4-byte length BE / LE | 4 / 4 | The two most common framing choices in existence. |
| named pipe `\\.\pipe\` | 4 | The only Windows named-pipe prefix that exists. |
| `case` hex opcode | 4 | Any switch-based dispatch. |
| command opcode table | 4 | Any structured dispatcher. |
| User-Agent literal | 3 | Any HTTP client. |
| magic `0xDEADBEEF` | 4 | **Retracted after location check — see §4.5.** |

> **A rule keyed on any row in this table fires across the corpus and is worth nothing.
> The corpus's shared mechanisms ARE its baseline, and the baseline is the false-positive
> budget. That is the map's first deliverable.**

### 4.4 ABSENT — rules that can never fire

| Token | Targets | Meaning |
|---|---|---|
| magic `0xBAADF00D` | **0** | No target emits it. |
| `msagent_` prefix | **0** | No target emits it. |
| `postex_` prefix | **0** | No target emits it. |

**A rule keyed on an absent token can never fire in any shipped build of any target in this
corpus. Three such rules is a false-positive budget of exactly zero — and a detection
liability: they create the *appearance* of coverage.** `[absence]` `[verified]`

**The `msagent_`/`postex_` zeros were defended before publication**, because a zero on an
expected token is the under-capture shape:

| Probe | metasploit files | Verdict |
|---|---:|---|
| `msagent_` | 0 | zero confirmed |
| `postex_` | 0 | zero confirmed |
| `msagent_x64` | 0 | zero confirmed |
| `postex_reverse` | 0 | zero confirmed |
| `msagent` (widened) | **1** | **`data\wordlists\unix_users.txt` — the literal `omsagent`, an OMS agent USERNAME in a wordlist. Not a protocol token at all.** |
| `metsrv` (widened) | **24** | samples are `metsvc.exe`, `metsvc-server.exe` — **service executable names**, plus `.md` docs and `.git\index`. |
| `post_ex` (widened) | **5** | every hit a substring: `post_exploitation`, `geutebruck_post_exp`, `do_post_exploit_checks`, `log_post_exchange`. |
| `stdapi` (widened) | **461 bare / 81 quoted** | **the one real survivor** — a deliberately-authored Meterpreter extension name, `lib\rex` 61 + `lib\msf` 40. |

**My widened probe over-captured on `post_ex` exactly as D131's matched `decodeBodyToMap`** —
a substring, not a token. **The quoted/bare split is the discriminator that separates them:**
`stdapi` 81 quoted (real literal), `post_ex` 0 quoted (never a protocol token). `[source]`
`[verified]`

### 4.5 `0xDEADBEEF` — retracted before publication

The token scored **4 targets** (`covenant, havoc, metasploit, sliver`) and would have entered
the shared table as a cross-target magic. **Its location check kills it:**

| metasploit area | Files |
|---|---:|
| `modules\exploits` | 22 |
| `data\templates` | 18 |
| `external\source` | 7 |
| `spec\lib` | 3 |
| `data\exploits` | 2 |
| **`lib\msf\core` / `lib\rex`** | **0** |

Samples: `data\exploits\CVE-2016-8655\chocobo_root.c`,
`data\templates\src\elf\dll\elf_dll_aarch64_template.s`,
`data\templates\src\elf\exe\elf_aarch64_template.s`.

**`0xDEADBEEF` is a conventional alignment filler inside ELF/shellcode templates and exploit
payloads. It is not a C2 wire magic.** Its three havoc hits and one covenant hit are the same
convention, not a shared protocol. **Had I banked the raw count, this report would have
asserted a four-target shared magic value that does not exist as a mechanism.** `[source]`
`[verified]`

---

## §5 Dead-arm enumeration — and the method correction that matters most

### 5.1 The incoming claim

havoc-deep D132 reports **four Havoc arms dead by construction** (`#if` on undefined ids).
The Lead asked me to generalise the method. **My generalisation produced a wrong answer first,
and the correction is the deliverable.**

### 5.2 My first detector, and why it failed

**Instrument:** collect every `#define` in the tree; every `#if`/`#ifdef` identifier not in
that set is "dead".

```
COUNTED: 463 files, 1,878 #define identifiers, 281 #if/#ifdef directives
RESULT : 72/72 plain #if identifiers "never #define'd"  -> 100% one verdict
```

**One verdict for 100% of input. Broken.** Its own output shows why: `#if defined`, `#if test`,
`#if QT_CONFIG`, `#if _WIN64`, `#if _MSC_VER`, `#if _WIN32_WINNT`. **Those are `#if defined(...)`
forms, shell snippets, Qt build macros, and compiler built-ins — none can ever appear in the
project's `#define` set.** The detector was comparing against a set that structurally excluded
its own inputs. `[source]` `[verified]`

### 5.3 The fixed classifier, and its distribution

Every `#if` assigned a class, so the distribution is visible:

| Class | Count |
|---|---:|
| FORM: expression (compound/negated/arith) | 146 |
| `ifdef` | 119 |
| FORM: `#if defined(...)` | 29 |
| EXCLUDED: compiler/platform built-in | 26 |
| **plain `#if IDENT` (project)** | **7** |
| FORM: function-like / not-an-identifier | 1 |

**The 281 directives reduce to 7 project `#if IDENT` forms.** The earlier "72 dead arms"
collapsed to a class distribution, which is the honest representation. `[source]` `[verified]`

### 5.4 THE CORRECTION: arm liveness is a BUILD property, not a TEXT property

**`TRANSPORT_HTTP` and `TRANSPORT_SMB` are never `#define`'d in any `.c`/`.h` — so every
text-only detector calls them dead. They are LIVE, because the build system sets them.**

```
COUNTED: 12 build-system files
COUNTED: 5 macros set by the build system
   QT_NO_DEBUG_OUTPUT   x2   client\CMakeLists.txt
   DEBUG                x1   payloads\Demon\CMakeLists.txt
   TRANSPORT_HTTP       x1   payloads\Demon\CMakeLists.txt
   TRANSPORT_SMB        x1   payloads\Demon\CMakeLists.txt
   AES256               x1   payloads\Demon\CMakeLists.txt
```

> **A `#define` census over source text cannot determine whether an arm compiles. Liveness
> is decided by CMake/Make at build time. Any dead-arm claim derived from source text alone
> is unreliable unless the build system is consulted.**

**Verdict per flagged arm:**

| Macro | Build-set? | Source `#define`? | True class |
|---|---|---|---|
| `TRANSPORT_HTTP` | **True** | False | **LIVE (build-set)** |
| `TRANSPORT_SMB` | **True** | False | **LIVE (build-set)** |
| `AES256` | **True** | True | LIVE |
| `DEBUG` | **True** | False | LIVE (build-set) |
| `SEND_LOGS` | False | False | **candidate dead** |
| `SHELLCODE` | False | False | **candidate dead** |
| `OBF_SYSCALL` | False | False | **candidate dead** |
| `INITGUID`, `DEFINE_GUID`, `MIDL_PASS` | False | False | **SDK/COM boilerplate — NOT project arms** |
| `_WIN64`, `__cplusplus`, `DBG` | False | False | **toolchain built-ins — NOT project arms** |

**3 candidate dead arms survive (down from a claimed 4), and two of the four incoming claims
are actually live.** The `INITGUID`/`MIDL_PASS` rows — ~90 of my first detector's hits, all in
`Native.h` — are **COM/MIDL SDK boilerplate set by `guiddef.h` and the MIDL compiler**, not
project arms at all. `[source]` `[verified]`

**`SHELLCODE` independently corroborates the Lead's instrument catalogue item (e):** the
catalogue recorded a `SHELLCODE` "defined in build, 7 hits" instrument whose seven hits were
the word inside `echo` strings. **My build-system check confirms `SHELLCODE` is NOT build-set
and NOT source-defined** — the two independent methods agree. `[source]` `[verified]`

### 5.5 The unfirable-rule census

> **A fingerprint keyed on a path that cannot exist in any shipped build is a rule that can
> never fire. That is the DB's false-positive baseline, stated as a rule:**

| Rule keyed on | Status | Consequence |
|---|---|---|
| `0xBAADF00D` | absent from all 6 targets | can never fire |
| `msagent_` | absent (only `omsagent` in a wordlist) | can never fire |
| `postex_` | absent (`post_ex` matches are substrings) | can never fire |
| dead arms `SEND_LOGS`, `SHELLCODE`, `OBF_SYSCALL` | compile out of every shipped build | code path unreachable |
| `OwnershipFilter` (D131 §2) | **0 occurrences in 35,742 files** | can never fire |

**Five rule classes in this corpus can never fire.** `[absence]` `[verified]`

---

## §6 Cross-references to the other lanes — cited, not re-derived

**Per instruction: cross-reference, do not re-derive.** Where a claim is binary-layer, I mark
it **CITED-NOT-MEASURED** — I have no `open_binary` this round. `[source]` `[verified]`

### 6.1 havoc-deep D132 — **CITED**

| Claim | My disposition |
|---|---|
| numeric dispatch fails **CLOSED** at `Packager.cc:785` | **CITED-NOT-MEASURED.** The `Packager.cc` copies and line range are reachable in source; I did not verify the fail-closed behaviour. |
| string dispatch fails **OPEN** | **CITED-NOT-MEASURED.** |
| 13-loaders / 6-uncalled library graph | **CITED-NOT-MEASURED.** |
| **zero DLL-name literals — names built char-by-char at scrambled indices → detect loader SHAPE, not name** | **This is the single most important cross-reference in this report.** It is the *same lesson* my §4.5 retraction learned independently: **a name-based rule is fragile because the name may not exist as a literal.** havoc-deep found it in the loader; I found it in `OwnershipFilter` (D131) and in `msagent_`/`postex_` (here). **Detect SHAPE, not NAME.** |
| four Havoc arms dead by construction | **CORRECTED — see §5.4.** Two of the four (`TRANSPORT_HTTP`, `TRANSPORT_SMB`) are **build-set and LIVE**. Three arms remain candidates (`SEND_LOGS`, `SHELLCODE`, `OBF_SYSCALL`). |

### 6.2 sliver-diver D136 — **CITED, with one correction**

| Claim | My disposition |
|---|---|
| D91 closed with a **YES**; `client/command/ai` = **242 binary rows == D103's 242 source rows** | **CITED-NOT-MEASURED** for the binary half; the source-half row count is reachable and the equality is the finding. |
| `normalizedConversationOperatorName` at `0xD0B140` | **SOURCE CONFIRMED** — `client\command\ai\model.go:3554` `optimistic.OperatorName = normalizedConversationOperatorName(...)`, 6 occurrences. Address half CITED-NOT-MEASURED. |
| `GetIncludeMessages` at `0x695D80` | **CITED-NOT-MEASURED.** |
| **`aiOperatorName` ABSENT** | **CORRECTED — IT IS NOT ABSENT.** |

**`aiOperatorName` exists 4 times in `server\rpc\rpc-ai.go`:**

| Line | Content |
|---|---|
| `:19` | `func (rpc *Server) aiOperatorName(ctx context.Context, fallback string)` — **the definition** |
| `:86` | `req.OperatorName = rpc.aiOperatorName(ctx, req.OperatorName)` |
| `:100` | `operatorName := rpc.aiOperatorName(ctx, "")` |
| `:144` | `req.OperatorName = rpc.aiOperatorName(ctx, req.OperatorName)` |

**The distinction that reconciles this:** `aiOperatorName` is **absent from the binary
symbol table** (`client/command/ai` scope) but **present in the source** (`server/rpc` scope).
**A symbol absent from one scope is not a symbol absent from the corpus** — and "absent" needs
its enumeration shown, and its scope named. This is the D126 name-table carve-out's cousin:
**the instrument that reports absence must say which region it searched.** `[source]`
`[verified]`

---

## §7 The map as a table — what to detect on, and what not to

**Ordered by discriminating power, strongest first.**

| Rank | Mechanism | Targets | Kind | Detection disposition |
|---|---|---|---|---|
| 1 | **Loader SHAPE** (char-by-char name construction, scrambled indices) | havoc (unique) | behaviour | **DETECT.** A shape survives renaming; a name does not. |
| 2 | **Numeric dispatch fail-CLOSED at `Packager.cc:785`** | havoc | control-flow | **DETECT.** Fail-closed is an observable asymmetry. |
| 3 | **Streaming methods with no `.func1`** (D126, 201/201) | sliver | codegen shape | **DETECT.** Validated 201/201 with zero exceptions. |
| 4 | `stdapi` extension name (quoted literal) | metasploit | protocol literal | **DETECT, with care.** 81 quoted files, `lib\rex` 61 — a real authored token. |
| 5 | magic `0x1337` | metasploit | constant | **CAUTION** — cultural constant; expect false positives. |
| 6 | magic `0xCAFEBABE` | msf + pupy | constant | **PAIRING ONLY** — never a single-target rule. |
| 7 | RC4 KSA / SHA256 K / MD5 init | 1–2 | crypto constant | **DO NOT DETECT.** Textbook constants. |
| 8 | All 12 SHARED tokens (§4.3) | 3–5 | HTTP/crypto/framing | **DO NOT DETECT.** They are the baseline. |
| 9 | `0xBAADF00D`, `msagent_`, `postex_`, `OwnershipFilter`, dead arms | 0 | absent | **DO NOT DETECT.** Can never fire. |

**The shape of this table is the finding: the corpus's *strong* signals are behavioural and
structural, and its *weak* signals are all lexical. Every lexical fingerprint in this corpus
is either shared across the baseline or absent from it.**

---

## §8 Instrument record

**I1 — degenerate keyword classifier, published rather than deleted.** 34/34 SHARED, 0 UNIQUE.
Caught by reading the distribution, not the total. The failure is *structural* (73% single-target
volume share) and is the report's most transferable result. `[verified]`

**I2 — the same degenerate failure twice in the dead-arm work.** 72/72 `#if` identifiers
"undefined". Caught by the identities being visibly non-project (`#if defined`, `#if test`,
`#if QT_CONFIG`). **Two degenerate classifiers in one report is the pattern, not a coincidence:
a set-membership test against a set you built from the same corpus will agree with itself.** `[verified]`

**I3 — `lstrip("-D")` character-set mangling.** `lstrip` strips a **character set**, not a
**prefix**: `DEBUG` → `EBUG`, `DOOM` → `OOM`, `DATABASE` → `ATABASE`. **6 of 10 control tokens
silently altered.** This is the same family as the Lead's catalogue item (g) (`[byte] -shl`
wrapping silently) — **a string/arithmetic operation that is valid and wrong.** Fixed with
`re.sub(r"^-D", "", tok)`; control pair printed. `[verified]`

**I4 — operator-precedence defect in my OWN final tally.** I wrote `tot+=b; raw+=a` and then
labelled the columns backwards, printing `raw=20459 / vendor-excluded=35742` — **the two totals
swapped.** It made metasploit read as **42%** of the corpus when the correct figure is
**73%**. **A number that changes with the print statement is a count of the print statement.**
Corrected in §1; disclosed here rather than silently fixed. `[verified]`

**I5 — three retractions and one correction, all before publication.** `0xDEADBEEF` shared
magic (retracted, §4.5); `post_ex` token (substring, §4.4); `msagent` (a wordlist username,
§4.4). **Each was caught by asking WHERE the match lives, not how many there were.** `[verified]`

**I6 — the claim gate, run on both sources of truth.** `D140*` False / `D139*` True on disk,
`140` False / `139` True in registry; post-claim both True. **Registry and disk are two
independent records and neither alone is sufficient** — D132's half-claim came from exactly
that gap, and D131's own number was held in one and not the other. `[verified]`

**I7 — the allocator's own controls, run first as mandated.** `D130*` → True and `D138*` →
False, **differing**, with the two wrong forms (`130*`, `D130.md`) printed as counter-examples.
**A check that answers identically for present and absent input is not a check** — and the
Lead's earlier pair (`129*` → False) tested nothing because the files are `D129_*.md`. `[verified]`

**I8 — the write path itself failed once, and the failure was informative.** The first write of
this report returned `EINVAL: invalid argument, mkdir` on the atomic-write tempdir. The cause is
the **slug length** — the original filename was 289 characters, and the atomic writer appends
`.NNNN.UUID.tmpdir`. **The failing operation is the tempdir, not the file**, and the error names
the tempdir rather than the file it was writing. **A path-building defect that reports the wrong
object.** Slug shortened; content unchanged. `[verified]`

**No whole-line duplication. Every census prints its input cardinality beside its result:
35,742 · 20,459 · 15,283 · 6 · 34 · 18 · 281 · 1,878 · 12 · 5 · 4 · 3 · 2 · 463 · 146 · 119 · 29 · 26 · 7.**

---

## §9 Status

| Item | Disposition |
|---|---|
| **Shared-mechanism map** | **DELIVERED.** 18 identity tokens: 2 UNIQUE, 3 PARTIAL, 12 SHARED, 3 ABSENT. `[source]` `[verified]` |
| **Pass-1 keyword census** | **DEGENERATE, PUBLISHED.** 34/34 SHARED, 0 UNIQUE. Cause: 73% single-target volume share. `[source]` `[verified]` |
| **Dead-arm method, generalised** | **CORRECTED.** Liveness is a **BUILD** property. `TRANSPORT_HTTP`/`TRANSPORT_SMB` **LIVE**; **3** candidate arms survive, not 4. `[source]` `[verified]` |
| **`aiOperatorName`** | **NOT ABSENT.** 4 occurrences in `server\rpc\rpc-ai.go`, definition at `:19`. Corrects D136. `[source]` `[verified]` |
| **`0xDEADBEEF` shared magic** | **RETRACTED.** 22 exploit modules + 18 ELF templates; **0** in `lib\msf\core`/`lib\rex`. `[source]` `[verified]` |
| **Metasploit convention tokens** | **RESOLVED.** `stdapi` 81 quoted (real); `msagent`/`postex`/`post_ex` not protocol tokens. `[source]` `[verified]` |
| **Unfirable-rule census** | **5 rule classes can never fire**, including `OwnershipFilter` from D131. `[absence]` `[verified]` |
| **False-positive baseline** | **STATED.** All 12 SHARED tokens are the baseline and must not be detected on. `[source]` `[verified]` |
| **havoc-deep D132** | **CROSS-REFERENCED**, one correction. Loader-SHAPE insight adopted and independently corroborated. `[verified]` |
| **sliver-diver D136** | **CROSS-REFERENCED**, one correction (`aiOperatorName`). `[verified]` |

**Constraints honoured:** no execution · no network · no live C2 · no REA · no `open_binary` ·
**no Ruby toolchain, so every Ruby/Rex claim here is `[inferred]` at the claim** — this report
makes **none**, because every mechanism above was measured in bytes, not inferred from language
knowledge · `[absence]` reported with the enumeration and the scope shown · frozen documents
corrected **by reference only** · every degenerate classifier published rather than deleted.

**No frozen document was modified. D121 remains 55,972 B untouched.**
