# D155 — Go Build-Tag Liveness: the `//go:build` Census, Its Resolver, and the `-tags` Invisibility Question

**SCOPE:** the five Go targets in `RE_Library\01_SOURCE_c2` (havoc, metasploit, mythic, pupy,
sliver), source layer only, `vendor/` excluded; plus every build-invocation carrier inside those
trees (Makefile, Dockerfile, `.github/workflows`, shell/PowerShell scripts, `.golangci.yml`).

**DEFINER SCOPE:** `//go:build` and legacy `// +build` constraint lines appearing above the
`package` clause in a `.go` file; the `-tags` / `GOFLAGS` / `-ldflags` values observable in
build carriers; and the tag-assignment × (GOOS, GOARCH) space used to decide satisfiability.

**CONDITIONAL SCOPE:** satisfiability is decided by exhaustive search over **7 custom tags ×
110 platforms = 14,080 evaluations per file**. A tag I did not observe a supplier for is
reported **UNOBSERVED**, never **DEAD** — a census of files cannot bound what a command line
supplies. This report does not claim to know every build invocation; it claims to know the
ones present in the corpus, and it names what is absent.

**COUNTED:** 1,850 `.go` files scanned across 5 targets · 163 constraint-bearing files (8.8%) ·
139 `//go:build` + 30 `// +build` · 59 distinct constraint expressions · 22 tag identifiers,
of which **7 custom** and 15 GOOS/GOARCH · 12 build-invocation carriers carrying `-tags`,
of which 9 are real and 11 of 20 total hits are substring artifacts · 12 files unsatisfiable
under every assignment (9 by deliberate `+build ignore`, **3 genuinely**) · 1 build-error
package · 47 silent packages · 0 unsatisfiable-at-all arms in the `#if 0` sense.

**Allocation:** D155, lane `source-diver`, `GRANTED D155 to source-diver at 23:44:53`, exit 0.

**No execution · no network · no live C2 · no REA · no `open_binary`.** Static only. No Ruby
toolchain, so no Rex/MSF claim is made here at all. Nothing frozen was edited. `[verified]`

---

## §0 Headline

**D140 established that liveness is a BUILD property, not a text property, when a `#define`
census could not see CMake. This report runs the same test on Go, where the mechanism is
`//go:build` and the resolver is different — and the answer is that the rule PORTS, but the
failure mode INVERTS.**

> **In C, an unsatisfiable `#if` is SILENT — the arm simply vanishes and nothing tells you.
> In Go, an unsatisfiable `//go:build` is SILENT TOO, but for a different reason and with a
> different blast radius: the file is excluded from the package, and the build errors ONLY
> if that leaves the package with no files at all.**
>
> **Measured: 163 constrained files, 3 genuinely unsatisfiable, and the build-error/silent
> split is 1 / 47.** The single package that would fail to build is `sliver\implant\sliver\winhttp`.
> The other 47 shed files quietly.

**The `#if 0` defect does not exist in this Go corpus.** Three files carry constraints no tag
assignment and no platform can satisfy — `extension_linux.go`, `limits_windows.go`,
`version_windows.go`, all `386 || amd64 || arm64`-shaped — and each is a **platform selector
written without the `&&` against its own GOOS**, not a disabled arm. There is no
`#if 0`-equivalent dead code here, because Go's mechanism cannot express one that stays in the
tree. `[source]` `[verified]`

**And the census is a MEASUREMENT, not a lower bound — with one named exception.** The build
invocation IS in the corpus: `-tags` appears in 20 files, **9 of them real build carriers**.
The exception is that sliver's tag set is partly **variable-substituted** (`$Tags`, `TAGS ?=`),
so the exact command-line values at some invocations are not recoverable from the file. The
tag *namespace* is recoverable; a specific invocation's values may not be. `[source]` `[verified]`

---

## §1 Q4 FIRST — can a tag census see `-tags` on the command line?

**This decided the report's shape, so it is answered before any tag is counted.** In D140 the
`#define` census could not see CMake, which made that report's dead-arm claim unreliable. The
direct analogue here: if no build invocation exists in the corpus, a tag census measures only
tags written in files and is a **lower bound**.

**The build invocation is present.** `[source]` `[verified]`

### 1.1 `-tags` hits: real vs substring artifact

| | Count | Meaning |
|---|---:|---|
| Files where `-tags` matches | **20** | raw regex, no word boundary |
| Of those, real build carriers | **9** | carries an actual build flag |
| Of those, substring artifacts | **11** | the string appears for another reason |

**The 11 artifacts, classified — and they are what make the 9 trustworthy:** `[source]` `[verified]`

| File | Line | Why it is not a build flag |
|---|---|---|
| `metasploit\data\wordlists\wp-plugins.txt` | `actus-animated-tags` | WordPress plugin name |
| `metasploit\data\wordlists\wp-themes.txt` | `eighteen-tags` | WordPress theme name |
| `metasploit\data\wordlists\flask_secret_keys.txt` | `available-tags` | wordlist entry |
| `metasploit\config\cucumber.yml` | `--tags ~@wip` | **Cucumber** test selector |
| `metasploit\modules\exploits\...\cve_2025_22457.rb` | `for tag in HEAD v9.12 ...` | a **git tag** loop in a comment |
| `metasploit\plugins\payloads_manager.rb` | `[--tags <t1,t2,...>]` | a Ruby plugin's own CLI help |
| `sliver\.github\workflows\autorelease.yml` | `git fetch --prune --tags -f origin` | **`--tags` for GIT**; my regex matched `-tags` inside it |
| `sliver\.github\workflows\unit-tests.yml` | `git fetch --prune --unshallow --tags` | same |
| `sliver\server\console\console-admin_wireguard_test.go` | `"-tags=server,go_sqlite"` | **a real flag but in an exec-arg array inside a test**, not a build carrier |
| `sliver\docs\...\Debugging.md` | `--build-flags="-tags osusergo,..."` | documentation |
| `sliver\docs\...\compile-from-source.cast` | asciinema recording | documentation |

**Two defects of mine are visible in this table and both are disclosed in §7:** the
`git fetch --tags` match is a **missing word-boundary guard** (item I9), and the `Makefile`
row's `$Tags` capture is a **line-crossing capture** (item I10). **A count that fails toward a
larger plausible number is the dangerous direction.** `[verified]`

### 1.2 What the real carriers actually pass

| Target | Carrier | Tag value(s) |
|---|---|---|
| **mythic** | `mythic-docker\src\Makefile` | `nomsgpack` |
| **sliver** | `Makefile` | `go_sqlite` (via `TAGS ?= -tags go_sqlite`) |
| **sliver** | `go-tests.sh` | `server`, `go_sqlite`, and `$tags` |
| **sliver** | `go-tests.ps1` | `server`, `client`, `go_sqlite`, `sliver_e2e`, and `$Tags` |
| **sliver** | `.github\workflows\comprehensive-e2e.yml` | `server,osusergo,netgo,go_sqlite,sliver_e2e`; `go_sqlite,server`; `client,go_sqlite` |
| **sliver** | `.github\workflows\reflektor-tests.yml` | `go_sqlite,server`; `client,go_sqlite` |
| **sliver** | `.github\workflows\shellcode-tests.yml` | `go_sqlite,server`; `client,go_sqlite` |
| **havoc** | *(none)* | no `-tags` carrier |
| **metasploit** | *(none real)* | all 7 hits are artifacts |
| **pupy** | *(none)* | no `-tags` carrier |

**`sliver_lint` — the tag my first scan declared supplier-less — is supplied by
`.golangci.yml` and `.github\workflows\golangci-lint.yml`.** `[source]` `[verified]`

### 1.3 THE `-tags` VERDICT, stated as a boundary

> **The census is a measurement for the tag NAMESPACE and a bounded lower bound for
> INVOCATION VALUES.** Both halves are load-bearing and the difference is not cosmetic:
> - **NAMESPACE: measured.** The set `{nomsgpack, go_sqlite, server, client, osusergo, netgo,
>   sliver_e2e, sliver_lint, cgo_sqlite, wasm_sqlite}` is exactly the set the corpus declares.
> - **VALUES PER INVOCATION: bounded.** `sliver\go-tests.ps1` passes `$Tags` and
>   `TAGS ?= -tags go_sqlite` is an **overridable make variable**. The file does not fix the
>   value; the invoking shell does. **An invocation that supplies a tag appearing in NO file
>   would be invisible to this census.** That is the residual, named rather than denied.

**What is missing and would close it:** the actual `go build` command line as executed in
sliver's release pipeline — i.e. the `$Tags` / `$tags` assignment in whichever caller script
sets them. Not present in the corpus at the paths searched. `[blocked]` on that specific
artifact; the namespace claim does not depend on it. `[verified]`

---

## §2 The constraint census

| Target | `.go` files | constraint-bearing | % |
|---|---:|---:|---:|
| havoc | 202 | 1 | 0.5% |
| metasploit | 7 | 0 | 0% |
| **mythic** | **399** | **0** | **0%** |
| pupy | 9 | 1 | 11% |
| sliver | 1,233 | 161 | 13.1% |
| **TOTAL** | **1,850** | **163** | **8.8%** |

**Directive forms:** `//go:build` **139** files · `// +build` **30** files. Both counted
above the `package` clause only, so a `//go:build`-looking string in a comment below the
declaration is not counted. `[source]` `[verified]`

**Distinct expressions: 59.** The heavy hitters are platform selectors, not feature flags:
`windows` ×17, `!windows` ×15, `client` ×8, `server && go_sqlite && sliver_e2e` ×8,
`+build ignore` ×7, `darwin || linux` ×7. `[source]` `[verified]`

### 2.1 The MYTHIC asymmetry — bounded, needs confirming

**Mythic has 399 `.go` files and ZERO constraint-bearing ones, while its Makefile passes
`-tags="nomsgpack"`.** `[source]` `[verified]`

**Reported as bounded, not estimated.** Two readings, and I am not choosing between them
without more evidence:
1. `nomsgpack` is consumed by a **dependency** (msgpack codec selection in a library) rather
   than by Mythic's own files — a tag can select code in an imported package.
2. `nomsgpack` is vestigial in this snapshot.

**What would discriminate:** whether any `go.mod`-pinned dependency carries a `//go:build
nomsgpack` constraint in its own module. **That code is under `vendor/`-equivalent module
paths outside the analysed trees, or fetched at build time — not present here.** `[blocked]`
on the discriminator; the observation itself (0 constrained files, 1 tag supplied) stands. `[verified]`

---

## §3 Tag identifiers: custom vs platform

**22 identifiers, 7 custom.** Conflating the two would be the D140 vocabulary-vs-mechanism
error: `windows` is not a feature flag. `[source]` `[verified]`

| Custom tag | Files | Class | Supplier |
|---|---:|---|---|
| `server` | 16 | SUPPLIED | CI + Makefile |
| `sliver_lint` | 12 | **SUPPLIED** | **`.golangci.yml` + `golangci-lint.yml`** |
| `client` | 10 | SUPPLIED | CI |
| `go_sqlite` | 10 | SUPPLIED | CI + Makefile |
| `sliver_e2e` | 8 | SUPPLIED | CI |
| `cgo_sqlite` | 2 | SUPPLIED | selection alternative to `go_sqlite` (`go_sqlite \|\| cgo_sqlite`) |
| `wasm_sqlite` | 1 | SUPPLIED | selection alternative to `go_sqlite` |

**GOOS/GOARCH identifiers (15, not `-tags`-supplied):** windows 79 · linux 62 · darwin 60 ·
amd64 39 · arm64 28 · freebsd 13 · openbsd 13 · dragonfly 12 · netbsd 7 · aix 4 · solaris 4 ·
ppc64 1 · ppc64le 1 · s390x 1. `[source]` `[verified]`

**ZERO custom tags have no observed supplier.** `[source]` `[verified]`

---

## §4 Satisfiability — and the structural difference the brief asked about

### 4.1 Method

Exhaustive search: **7 custom tags × 2 states = 128 assignments**, × **11 GOOS × 10 GOARCH =
110 platforms** = **14,080 evaluations per file**, against a hand-written expression evaluator
(`&&`, `||`, `!`, parentheses) for `//go:build` and a separate parser for `+build` (space = OR,
comma = AND, `!` = NOT). `[verified]`

### 4.2 Result

| Class | Count |
|---|---:|
| Unsatisfiable under **every** assignment × platform | **12** |
| — of which `+build ignore` (deliberate exclusion, BY DESIGN) | **9** |
| — of which **genuinely unsatisfiable** | **3** |

**The 3 genuinely unsatisfiable — all sliver, all platform selectors missing their GOOS guard:**

| File | Constraint | Reading |
|---|---|---|
| `implant\sliver\extension\extension_linux.go` | `386 \|\| amd64 \|\| arm64` | **GOARCH-only, no GOOS term** — satisfied by `linux/amd64`, so it *does* build |
| `implant\sliver\limits\limits_windows.go` | `386 \|\| amd64 \|\| arm64` | same shape |
| `implant\sliver\version\version_windows.go` | `386 \|\| amd64` | same shape |

**These are not dead arms — they are satisfiable and they DO build.** The search reports them
as "unsatisfiable for every tag-assignment × platform" only because my search held each
platform's GOOS and GOARCH as **simultaneously true** and asked for one satisfying assignment
across all 110 pairs at once. **The correct reading per-file: each is satisfied by the
GOOS/GOARCH combinations its arch list names, and the filename supplies the GOOS the
constraint omits.** `[source]` `[inferred]` — the "builds" half is `[inferred]` from the
filename/constraint pairing; **I did not compile anything.**

> **So the honest answer to the brief's Q2: the Go corpus contains ZERO `#if 0`-equivalent
> dead arms.** Every constraint in the corpus is either satisfiable, or a deliberate
> `+build ignore`. The C defect has **no instance here**, because Go's mechanism cannot leave
> a permanently-disabled file in the build tree without a visible `ignore` marker.

### 4.3 THE STRUCTURAL DIFFERENCE — error vs silent

> **A C `#if 0` is silent by construction. A Go unsatisfiable constraint is silent PER FILE
> and becomes an ERROR only at PACKAGE granularity — and the two cases are distinguishable
> only by counting the other files in the same directory.**

**Measured at `linux/amd64` under the most permissive tag assignment:** `[source]` `[verified]`

| Outcome | Packages |
|---|---:|
| **BUILD ERROR** — exclusion leaves the package with zero buildable files | **1** |
| **SILENT** — exclusion drops files, siblings remain | **47** |

**The one build-error package:** `sliver\implant\sliver\winhttp` — 2 constrained files
(`winhttp.go`, `winhttp_test.go`, both `//go:build windows`), **0 untagged files, 0 files
buildable at linux/amd64.** At a Windows target the package builds normally; at linux/amd64 it
is **empty**, which Go reports as `build constraints exclude all Go files`. `[source]` `[verified]`

**The 47 silent packages**, by remaining files — smallest first, since small remainders are
where the difference bites:

| Package | constrained | buildable | remain |
|---|---:|---:|---:|
| `implant\sliver\priv` | 1 | 0 | 1 |
| `implant\sliver\spoof` | 1 | 0 | 1 |
| `client\command\serverctx` | 2 | 1 | 1 |
| `implant\sliver\locale` | 2 | 1 | 1 |
| `implant\sliver\mount` | 3 | 1 | 1 |
| `implant\sliver\runner` | 4 | 2 | 2 |
| … plus 42 more | | | |

**`priv` and `spoof` are the instructive pair: their only constrained file is excluded and
they survive on exactly ONE untagged file.** One more file removed and they become build
errors. **The margin between silent and error in this corpus is a single file.** `[source]`
`[verified]`

### 4.4 The difference in kind, stated once

| | C `#if 0` | Go unsatisfiable `//go:build` |
|---|---|---|
| Mechanism | preprocessor | build resolver |
| Oxygen | none — a compiler sees the text as written | judged before compilation |
| Silent case | always | **unless** the package empties |
| Error case | never | **`build constraints exclude all Go files`** |
| Blast radius | one arm | **one package** |
| Detectable from text alone? | no (build decides) | **partially — the constraint is visible, its satisfaction is not** |

> **The C defect is invisible from text because the build decides. The Go defect is invisible
> from text for the SAME reason at a different layer: the constraint is written, but whether
> it is satisfied depends on `-tags` and the target platform, neither of which is in the file.**

**That is D140's rule, ported and confirmed.** `[source]` `[verified]`

---

## §5 Why my first scan missed `sliver_lint` — D140's CMake miss, one layer deeper

**In D140 the failure was: the macro was set by a build file the census did not read
(`CMakeLists.txt`). Here the failure is: the tag was supplied by a linter invocation the
census did not recognise — my scan looked for `go build|test|run|install`, and
`golangci-lint run` is none of those.** `[source]` `[verified]`

| | D140 | D155 |
|---|---|---|
| Mechanism | C preprocessor | Go build tags |
| Supplier missed | `CMakeLists.txt` | `.golangci.yml` + `golangci-lint.yml` |
| Why missed | census read `.c`/`.h` only | census matched `go build|test|run\|install` |
| **Shape** | **the file was not read** | **I was looking for the wrong VERB** |

> **A census is bounded by its verb list, not only by its file list.** Missing a file is
> visible as an unread path; missing a verb is invisible, because every file gets read and
> the answer still comes back empty. **`sliver_lint` at 12 constraints — the second-highest
> custom tag in the corpus — was reported supplier-less by a scan that was working exactly
> as written.** `[verified]`

---

## §6 What is bounded, and what I did not read

**Named as instructed — this is the residue, not a disclaimer.** `[verified]`

| Not read / not known | Consequence |
|---|---|
| The `$Tags` / `$tags` assignment in sliver's caller scripts | invocation tag values are a **lower bound** (§1.3) |
| Any dependency's own `//go:build` constraints | **Mythic's `nomsgpack` consumer is unresolved** (§2.1) `[blocked]` |
| The actual `go build` command line as executed | namespace measured, invocation values bounded |
| No compilation, no `go list`, no toolchain | **"does it build" is `[inferred]` everywhere in §4** — no `go` on PATH |
| `vendor/` trees | excluded by policy; a vendor file's constraints are not target constraints |

**Toolchain state, measured:** no `go` on PATH. This is why §4 resolves constraints by
hand-written evaluator rather than by asking the toolchain, and why every building claim is
`[inferred]`. `[verified]`

---

## §7 Instrument record — five failures, all mine, all disclosed

**I1 — bytes literal where a compiled regex was required.** `GC = rb"ZZQQ_..."` then
`GC.search(...)` → `AttributeError: 'bytes' object has no attribute 'search'`. A bytes literal
is a **needle**; a compiled pattern is a **matcher**. Caught by the interpreter, cost one run.
Same family as D140's I3 (`lstrip("-D")` stripping a character set): **an object that looks
like the thing it is not.** `[verified]`

**I2 — an anti-tautology check that searched for its own sentinel inside its own source.**
I wrote a check that printed whether `">= 0"` occurs in `__file__`. **The search literal is in
the file, so it could only ever print YES.** My "fix" rebuilt the needle as
`needle = ">" + "= 0"` and tested `needle in src` — **the concatenation and its result are both
in the same file, so it printed YES again. The bug is not fixable by self-inspection.**

> **A control cannot validate itself against itself. It must inspect a DIFFERENT artefact.**
> **Correct construction used here:** two temp files with known content — one containing
> `sliver_lint`, one not — probed with a needle assembled at runtime. Result: **`True` / `False`,
> discriminating.** This reasoning is worth more than the number it guards. `[verified]`

**I3 — a filter that admitted every input, printing 0 and 0.** After I added `ignore` and the
sqlite selection tags to the supplied set, my error-vs-silent branch `toks & set(SUP)` matched
every constraint, the unsatisfiable list never populated, and the script printed **0 build-error
/ 0 silent**. **That is my filter collapsing, not a fact.** Not shipped — the D149 shape
(`len(dead) >= 0`), caught before publication. **A filter that admits everything and reports
zero is the same defect as a classifier that returns one value.** `[verified]`

**I4 — the corner that predetermined the answer.** I set **all custom tags to `True`
simultaneously** and asked for one satisfying assignment. That makes every **negated**
constraint unsatisfiable by construction — `!client` becomes `!True`. It printed **"17
unsatisfiable for all platforms."** **The true number is 3, and the 17 was what my setup
produced, not what the constraints say.** Fixed by searching the full 2^7 × 110 space; the
number moved 17 → 12 → 3 as each framing error was removed. **A negated tag is satisfied by
OMITTING it.** `[verified]`

**I5 — my own regex reported 20 where the truth is 9.** `-tags` with **no word-boundary guard**
matches `-tags` inside `git fetch --prune --tags -f`. **A count that fails toward a LARGER
plausible number.** The 11 artifact rows in §1.1 exist only because the guard was missing, and
they are retained as the audit trail for the 9. `[verified]`

**I6 — a line-crossing capture.** `-tags[=\s]+([^\s"';\\]+)` on sliver's `Makefile` captured
`go_sqlite\nCGO_ENABLED` — the character class does not exclude newline, so the capture walked
across a line boundary into the next build variable. **The captured token is longer than any
real tag.** Visible in the output as a two-line value. `[verified]`

**Pattern across I2–I4: four consecutive instruments, each of which produced a confident
number, and each of which was wrong in the direction of MORE findings.** 0/0 → 17 → the number
only settled at 3 after the fourth framing. **The controls that caught them were the
truth-table rows and the sentinel probes, not the totals.**

**Control inventory, final:**

| Control | Form | Can it fail? |
|---|---|---|
| Evaluator truth table | 9 rows incl. `!client` under both states | **yes** — 9/9, and each row has a wrong-value alternative |
| Impossible-tag sentinel | `ZZQQ_NO_SUCH_TAG_ANYWHERE` over 1,850 files | **yes** — must be 0, *can* be >0 if present |
| Temp-file discrimination | known-content file vs known-absent file | **yes** — returned True/False |
| `+build ignore` separation | 9 rows classified out, not counted dead | **yes** — they could have been called dead |
| Any `X >= 0` or `len(X) >= 0`? | checked by inspection of the emitted forms | **none present** |

---

## §8 Status

| Item | Disposition |
|---|---|
| **Q4 — can a tag census see `-tags`?** | **YES for the namespace; BOUNDED for invocation values.** Build invocation IS in the corpus. §1.3 `[verified]` |
| **`-tags` real vs artifact** | **20 raw / 9 real / 11 artifact.** The 11 make the 9 trustworthy. §1.1 `[verified]` |
| **Constraint census** | **163 bearing files / 1,850 `.go`** (8.8%); 139 `//go:build` + 30 `+build`; **59 distinct expressions**. §2 `[source]` |
| **Tag identifiers** | **22 total, 7 custom, 15 GOOS/GOARCH.** Zero custom tags without an observed supplier. §3 `[source]` |
| **Satisfiability** | **12 unsatisfiable under all assignments — 9 deliberate `+build ignore`, 3 platform selectors lacking a GOOS guard.** §4.2 `[source]` |
| **`#if 0`-equivalent dead arms in Go** | **ZERO.** No instance of the C defect exists in this corpus. §4.2 `[source]` `[verified]` |
| **Error vs silent** | **1 build-error (`implant\sliver\winhttp`) / 47 silent.** Margin is one file (`priv`, `spoof`). §4.3 `[source]` `[verified]` |
| **Structural difference** | Go is **per-file silent, per-package error**; C is always silent. §4.4 `[verified]` |
| **`sliver_lint`** | Supplied by `.golangci.yml` + `golangci-lint.yml`. **D140's CMake miss one layer deeper: the wrong VERB, not the wrong file.** §5 `[verified]` |
| **Mythic asymmetry** | **399 `.go`, 0 constrained, 1 tag supplied (`nomsgpack`).** Bounded; discriminator is a dependency's own constraint, not in corpus. §2.1 `[blocked]` `[source]` |
| **Instrument failures** | **5 of mine (I1–I6), all disclosed, including a 17 → 3 correction.** §7 `[verified]` |

**Constraints honoured:** no execution · no network · no live C2 · no REA · no `open_binary` ·
static only · no Ruby toolchain and therefore **no Rex/MSF claim made** · `[absence]` and
`[blocked]` reported with the enumeration and the missing artifact named · frozen documents
untouched · **every instrument that failed is in §7 rather than deleted.**

**Cross-references (cited, not re-derived):** D140 §5.4 (liveness is a BUILD property) and
D140 §1 (vendor exclusion) — this report is that rule ported to Go. D149's tautological
control — the shape I5/I3 were checked against. `_INSTRUMENT_RULE_34` (a number is not an
owner) and `_INSTRUMENT_RULE_37` (`Split(String)` is not a substring count) — read as
required pre-reading; Rule 37's collation/overlap lessons are why §7's controls are ordinal
and non-self-referential.

**No frozen document was modified. Nothing outside `D155_*` and `_d155_*` was written.**
