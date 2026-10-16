# D165 — Four Residuals from D155: `nomsgpack`, the `$Tags` Bound, the Verb-List Generalisation, and the Audited Denominator

**SCOPE:** the six target roots under `RE_Library\01_SOURCE_c2` — covenant, havoc, metasploit,
mythic, pupy, sliver — non-vendor paths only, at every file type; plus **every vendored tree
present in the corpus** (sliver only) searched for dependency-level build constraints.

**DEFINER SCOPE:** `//go:build` and `// +build` directives above the `package` clause; the
literal `nomsgpack` and `msgpack` in any vendored `.go` file; `TAGS=` assignments at every
`make` call site; and the set of **build-invocation verbs** present in carrier files.

**CONDITIONAL SCOPE:** a verb counts toward Q3 only when it occurs in a **carrier** — a file
whose *type* can hold a build invocation (Makefile, Dockerfile, `*.yml/*.yaml`, `*.sh/*.ps1`,
`CMakeLists.txt`, `Cargo.toml`, `pom.xml`, `*.csproj`, `package.json`, `Gemfile`, `Rakefile`,
`setup.py`, …) **and** on a line that is not prose. Without that test the census measures the
English language and the string `cmake` inside a directory name. Both the raw and carrier-only
counts are printed so the artifact population is auditable against the real one.

**COUNTED:** 1,850 non-vendor `.go` files (per-target below) · 163 constraint-bearing ·
139 `//go:build` · 30 `// +build` · **169 directives, 163 files, 6 files carrying BOTH** ·
10,923 vendored `.go` files in sliver's tree, **1,981 of them newly measured as constrained,
206 distinct tags** · **0 occurrences of `nomsgpack` in 10,923 vendored files** · 63 `make`
call sites on sliver, **0 passing `TAGS=`** · **15 build-verb families with real carriers,
of which D155's Go-only verb list covered 1**.

**Allocation:** D165, lane `source-diver`. Follows D155 in the same lane.

**No execution · no network · no live C2 · no REA · no `open_binary` · no `go` toolchain.**
Static only. Every "does it build" claim remains `[inferred]` — there is no `go` on PATH.
Nothing frozen was edited. Nothing outside `D165_*` / `_d165_*` was written. `[verified]`

---

## §0 Headlines

**Q1 — Mythic's `nomsgpack`: the two-reading split CLOSES, and neither reading was right.**

> **Mythic does not vendor.** `vendor dirs = 0`, `modules.txt = 0`, 399 `.go` files. The
> dependency source is **not in the corpus**, so the discriminator I named in D155 cannot be
> run in-tree. **But the consumer is identified by NAME from Mythic's own `go.mod`.**
>
> **`github.com/ugorji/go/codec v1.3.1` is an indirect dependency of
> `mythic\mythic-docker\src\go.mod`, and `ugorji/go/codec` is the package that implements
> the `nomsgpack` build tag.** `[source]` `[inferred]` — the dependency edge is `[source]`;
> the package's tag name is `[inferred]` from the package's known design, **not** read here.
>
> **So: reading (a) is CORRECT IN KIND — a dependency consumes the tag — and (b) vestigial is
> NOT supported.** The tag is supplied because a dependency reads it; the mechanism is
> **cross-module**, which is exactly why an in-tree constraint census must return zero and be
> right. `[source]` `[verified]` on the zero; `[inferred]` on the consumer.

**Q1's control is the load-bearing part, and it came back strong — because the scanner was
shown to work.**

> **sliver's vendored tree: 10,923 `.go` files, 1,981 constrained, 206 distinct tags.**
> Named controls behaved as predicted: `go-sqlite3` **36/44 constrained** (`cgo`,
> `libsqlite3`, `sqlite_omit_load_extension`); `modernc.org/sqlite` **22/33** (`sqlite.dmesg`,
> `!sqlite.dmesg`, `rlimit.go→freebsd`). **The scanner demonstrably reads vendored build tags.**
>
> **Therefore the zero is a FINDING, not a blind spot.** `nomsgpack` appears **0 times** in
> 10,923 vendored `.go` files, in a tree where the same instrument finds 1,981 constraints.
> **That is the difference between "I did not find it" and "it is not there to find."**

**Q2 — sliver's `$Tags`: an answer by construction.**

> **63 `make` call sites on sliver. ZERO pass `TAGS=`.** Every caller runs bare `make`, a named
> target (`make clients`, `make servers`, `make windows-amd64`), or `make clean && make`.
> **The Makefile's own default is what ships: `sliver\Makefile:10` `TAGS ?= -tags go_sqlite`.**
> With the `$(TAGS),server` / `$(TAGS),client` expansion, the effective flag is
> **`go_sqlite,server`** or **`go_sqlite,client`** per artifact. `[source]` `[verified]`
>
> **D155's lower bound is now closed.** The namespace was already measured; the *value* is the
> default, because no caller overrides it. `[source]` `[verified]`

**Q3 — the verb-list rule generalised, and D155's scope was narrow.**

> **15 build-verb families have real carriers in this corpus. D155's Go-only verb list
> covered 1 of them.** `make` 14 · `bundler` 19 · `gem` 15 · `docker` 34 · `pip` 8 · `npm` 6 ·
> `rake` 5 · `msbuild` 4 · `autotools` 3 · `cmake` 2 · `cargo` 1 · `dotnet` 1 · `podman` 1 ·
> `yarn` 1. `[source]` `[verified]`
>
> **A rule stated in D155 and now demonstrated against its own author: a census is bounded by
> its verb list. D155's verb list was `go build|test|run|install|generate` — one family out of
> fifteen. It was correct for the question it was asked and silent about fourteen others.**

**Q4 — the denominator audits exactly.**

> **1,850 non-vendor `.go` files reproduced; 139 `//go:build` reproduced; 30 `// +build`
> reproduced; 163 constraint-bearing reproduced.** Per-target figures printed in §4.
> **The 30-vs-31 is fully resolved and it is a COUNTING-UNIT difference, not a scope
> difference** — see §4.2. `[source]` `[verified]`

---

## §1 Q1 — Mythic's `nomsgpack`

### 1.1 Does each target vendor?

| Target | vendor dirs | `modules.txt` | `.go` files |
|---|---:|---:|---:|
| covenant | 0 | 0 | 0 |
| havoc | 0 | 0 | 202 |
| metasploit | 0 | 0 | 7 |
| **mythic** | **0** | **0** | **399** |
| pupy | 0 | 0 | 9 |
| **sliver** | **4** | **2** | 14,229 |

**Sliver's vendor trees:** `sliver\vendor` (`modules.txt`, 2,428 lines), `sliver\implant\vendor`
(`modules.txt`, 329 lines), plus two `testdata` fixtures under `server\gogo\goname\testdata\`.

**`sliver\vendor\modules.txt` — measured 2,428 lines by `\n` count in this run, 2,429 by D140's
method (which counted the trailing unterminated remainder as a line).** The two figures differ
by exactly the final-line treatment. **D140's 2,429 is not wrong and neither is 2,428: they are
different counting units over the same file.** Recorded rather than reconciled to one number.
`[source]` `[verified]`

### 1.2 Mythic does not vendor — the hinge resolves

**`mythic vendor dirs = 0`.** Mythic's dependency source is **not in the corpus**, so D155's
named discriminator ("does any go.mod-pinned dependency carry its own `//go:build nomsgpack`?")
**cannot be run in-tree.** That is a real boundary and it is stated rather than papered over.

### 1.3 The `nomsgpack` search, and why the zero is a finding

| Search | Count |
|---|---:|
| vendored `.go` files searched | **10,923** |
| of those, **constrained** (scanner field test) | **1,981** |
| distinct tags seen in the vendored tree | **206** |
| occurrences of `nomsgpack` anywhere in a vendored tree | **0** |
| vendored files mentioning `msgpack` (any form) | **1** — and it is `chroma\v2\lexers\embedded\nu.xml:20`, a **syntax-highlighting word list**, not Go |

**The mandatory control, done as specified:** `[source]` `[verified]`

| Package | Expected | Measured |
|---|---|---|
| `github.com\mattn\go-sqlite3` | **constrains** | `.go=44`, **constrained=36** — `cgo`, `libsqlite3`, `sqlite_omit_load_extension`, `!sqlite_omit_load_extension` |
| `modernc.org\sqlite` | **constrains** | `.go=33`, **constrained=22** — `sqlite.dmesg`, `!sqlite.dmesg`, `rlimit.go→freebsd` |
| `github.com\pmezard\go-difflib` | not to constrain | `.go=0` — **not vendored at all** |
| `github.com\davecgh\go-spew` | not to constrain | `.go=0` — **not vendored at all** |

**The two negative controls FAILED to prove anything, and that is reported rather than fixed.**
I chose packages I expected *not* to constrain; **neither is present in the tree**, so both
returned `.go=0` and neither exercised the negative case. **A control that returns the expected
answer for the wrong reason is not a control.** The positive controls carry the discrimination:
two packages, 58 constrained files, four named canonical tags.

> **Both conclusions, stated separately as the Lead required:**
> 1. **This is a FINDING, not a blind spot**, because the same instrument finds **1,981**
>    constraints in the same tree with the same code path. A search that cannot see vendored
>    build tags would have returned zero *constrained files*, not 1,981.
> 2. **What the finding is about:** it establishes that **no vendored dependency in the corpus
>    constrains on `nomsgpack`.** It does **NOT** establish that no dependency anywhere does —
>    Mythic's dependencies are not vendored and were not read. `[blocked]` on that.

### 1.4 The consumer, named

**`mythic\mythic-docker\src\go.mod` (2,741 B) requires, among its indirect dependencies:**

```
github.com/ugorji/go/codec v1.3.1 // indirect
```

**`ugorji/go/codec` is the package whose build-tag surface includes `nomsgpack`** — the tag
disables its msgpack codec path. `[inferred]` — the dependency edge is `[source]` (read from
`go.mod`); the tag's association with that package is **`[inferred]` from the package's known
design and is NOT read from source here**, because that source is not in the corpus.

**Verdict for Q1:** `[source]` `[verified]` `[inferred]`

> **Reading (a) is correct in kind: a dependency consumes the tag. `nomsgpack` is a
> CROSS-MODULE tag, supplied on the command line by Mythic's Makefile, consumed inside
> `github.com/ugorji/go/codec`, and therefore invisible to any census of Mythic's own files.**
> **Reading (b), vestigial, is NOT supported** — the tag has a purpose outside the tree, and
> Mythic's `go.mod` names a plausible consumer for it.
> **The residual is precise: I cannot prove `ugorji/go/codec` is the consumer, only that it is
> present and is the right kind of package. Proving it needs that module's source, which is
> absent.** `[blocked]` `[verified]`

**This also resolves D155's §2.1 asymmetry as EXPECTED, not anomalous.** Mythic: 399 `.go`,
0 constrained, 1 tag supplied. **That is precisely the signature of a cross-module tag.** The
observation and the mechanism now agree.

---

## §2 Q2 — sliver's `$Tags`, bounded from the callers

### 2.1 Every `make` caller

**63 files/lines reference `make` on sliver.** The non-documentation call sites, all of them:
`[source]` `[verified]`

| Caller | Line |
|---|---|
| `.github\workflows\autorelease.yml` | `make clients`; `make servers` |
| `.github\workflows\codeql-scanning.yml` | `run: make` |
| `.github\workflows\unit-tests.yml` | `make windows-amd64`; `make linux-arm64`; `make linux-amd64`; `make clean && make && ./sliver-server unpack --force && ./go-tests.sh …`; `make macos-amd64`; `make macos-arm64`; `make clients` |

**`TAGS=` passed at a call site: 0.** `[source]` `[verified]`

### 2.2 The default is what ships

```
sliver\Makefile:10     TAGS ?= -tags go_sqlite
sliver\Makefile:24     ifneq (,$(findstring cgo_sqlite,$(TAGS)))
sliver\Makefile:116    ... $(TAGS),client $(LDFLAGS) -o sliver-client ./client/...
sliver\Makefile:120    GOOS=darwin GOARCH=amd64 ... $(TAGS),server $(LDFLAGS) ...
sliver\Makefile:234    $(call windows_exec,...,$(TAGS)$(COMMA)$(5),...)
```

**`TAGS ?=` is a conditional assignment: it takes the default unless overridden on the command
line or in the environment. Zero call sites override it. Therefore the default ships.**
`[source]` `[verified]` `[inferred]` on "ships" — no build was run.

> **Q2 ANSWER: `go_sqlite` is the answer, and it is the answer BY CONSTRUCTION rather than by
> observation.** The effective per-artifact flag is **`go_sqlite,server`** for the server and
> **`go_sqlite,client`** for the client. D155's "invocation values are a lower bound" is
> **closed for the corpus as delivered**, and stays a bound only for an out-of-corpus caller
> that invokes `make TAGS=…` from outside this tree — which is unfalsifiable from here and is
> stated as such rather than claimed absent. `[inferred]`

---

## §3 Q3 — the verb-list rule, generalised

### 3.1 The artifact problem, caught before publication

**My first pass matched raw file content with no location test. It produced:**
`make` 76 files — including `covenant\LICENSE`, where the GPL text says "make sure" 14 times.
`cmake` 19 files — including `wwwroot\dist\codemirror\...`, matching the **string** `cmake` in a
CodeMirror language-mode directory. `msbuild` 225 files in metasploit, overwhelmingly prose.
`docker` 373 files.

> **That is D140's `post_ex` substring failure and D155's `-tags`-inside-`--tags` failure, for
> the third time, by the same author, in the same family. A verb census over content is not a
> verb census.** Disclosed as **I7** in §6. Not shipped.

### 3.2 Artifact vs real, with the carrier test applied

| Tool | Raw files | **Real carriers** | dropped |
|---|---:|---:|---:|
| `docker` | 373 | **34** | 339 |
| `msbuild` | 225 | **4** | 221 |
| `make` | 54 | **14** | 40 |
| `gem` | 53 | **15** | 38 |
| `bundler` | 49 | **19** | 30 |
| `dotnet` | 45 | **1** | 44 |
| `rake` | 42 | **5** | 37 |
| `pip` | 35 | **8** | 27 |
| `npm` | 28 | **6** | 22 |
| `ninja` | 22 | **0** | 22 |
| `autotools` | 17 | **3** | 14 |
| `yarn` | 7 | **1** | 6 |
| `cmake` | 6 | **2** | 4 |
| `maven` | 4 | **0** | 4 |
| `podman` | 4 | **1** | 3 |
| `gradle` | 3 | **0** | 3 |
| `cargo` | 1 | **1** | 0 |
| `setup.py` | 1 | **0** | 1 |

**`msbuild` 225 → 4 is a factor of 56. `docker` 373 → 34 is a factor of 11.** `[source]` `[verified]`

**Carrier-test control — it discriminates:** `sliver\Makefile` → **True**;
`sliver\LICENSE` → **False**; `metasploit\Gemfile` → **True**;
`covenant\...\codemirror\CHANGELOG.md` → **False**. **Each probe could have gone the other way.**
`[verified]`

### 3.3 Real carriers, per target

| Verb | covenant | havoc | metasploit | mythic | pupy | sliver |
|---|---:|---:|---:|---:|---:|---:|
| `go build` | 0 | 1 | 0 | 4 | 0 | 6 |
| `make` | 0 | 0 | 8 | 0 | 4 | 2 |
| `bundler` | 0 | 0 | 19 | 0 | 0 | 0 |
| `gem` | 0 | 0 | 15 | 0 | 0 | 0 |
| `docker` | 1 | 0 | 15 | 15 | 2 | 1 |
| `pip` | 0 | 0 | 0 | 1 | 7 | 0 |
| `npm` | 1 | 0 | 2 | 2 | 0 | 1 |
| `rake` | 0 | 0 | 5 | 0 | 0 | 0 |
| `msbuild` | 0 | 0 | 4 | 0 | 0 | 0 |
| `autotools` | 0 | 0 | 2 | 0 | 1 | 0 |
| `cmake` | 0 | 2 | 0 | 0 | 0 | 0 |
| `cargo` | 0 | 0 | 0 | 0 | 0 | 1 |
| `dotnet` | 1 | 0 | 0 | 0 | 0 | 0 |
| `podman` | 0 | 0 | 1 | 0 | 0 | 0 |
| `yarn` | 0 | 0 | 0 | 0 | 0 | 1 |
| **total** | **3** | **3** | **71** | **22** | **14** | **12** |

### 3.4 The coverage verdict

| # | Verb family | Real carriers | In D155's verb list? |
|---:|---|---:|---|
| 1 | `go build`/`install`/`run`/`test`/`generate` | 11 | **YES** |
| 2 | `make` | 14 | **NO** |
| 3 | `bundler` | 19 | **NO** |
| 4 | `gem` | 15 | **NO** |
| 5 | `docker` | 34 | **NO** |
| 6 | `pip` | 8 | **NO** |
| 7 | `npm` | 6 | **NO** |
| 8 | `rake` | 5 | **NO** |
| 9 | `msbuild` | 4 | **NO** |
| 10 | `autotools` | 3 | **NO** |
| 11 | `cmake` | 2 | **NO** |
| 12 | `cargo` | 1 | **NO** |
| 13 | `dotnet` | 1 | **NO** |
| 14 | `podman` | 1 | **NO** |
| 15 | `yarn` | 1 | **NO** |

> **COUNTED: 15 build-verb families with real carriers. D155's verb list covered 1.**
> `[source]` `[verified]`

**D155's rule, applied to D155.** D155 wrote: *"A census is bounded by its verb list, not only
by its file list. Missing a file shows up as an unread path; missing a verb is invisible,
because every file IS read and the answer still comes back empty."*

> **That sentence was written about `golangci-lint`, and the D155 census itself is an instance
> of it. The Go tag census read every `.go` file in scope and was correct — and it was silent
> about fourteen build systems in the same corpus, because its verb list named one family.
> This is not a defect in D155's answer; it is the scope of D155's answer, now measured
> instead of assumed.** `[source]` `[verified]`

**The generalised rule:** `[verified]`

> **VERB-LIST BOUNDEDNESS IS INVISIBLE IN A SINGLE-SYSTEM CENSUS AND ONLY VISIBLE IN A
> MULTI-SYSTEM ONE.** A Go-only census that returns a Go answer looks complete because it was
> never asked about `bundler`. **The failure mode is not a wrong number; it is an
> unstated denominator.** Any census must print the verb list it used, in the same way it must
> print the file list.

---

## §4 Q4 — the denominator, audited

### 4.1 Per-target, printed

**Scope condition for a file to count:** (1) extension `.go`; (2) no `\vendor\` component in
its directory path; (3) under one of the six enumerated target roots. `[verified]`

| Target | `.go` total | **non-vendor** | `//go:build` | `// +build` |
|---|---:|---:|---:|---:|
| covenant | 0 | **0** | 0 | 0 |
| havoc | 202 | **202** | 0 | 1 |
| metasploit | 7 | **7** | 0 | 0 |
| mythic | 399 | **399** | 0 | 0 |
| pupy | 9 | **9** | 0 | 1 |
| sliver | 14,229 | **1,233** | **139** | **28** |
| **TOTAL** | **14,846** | **1,850** | **139** | **30** |

**Reproduced exactly: 1,850 · 139 · 30.** The Lead independently reproduced 1,850, 163 and 139
and got **31** for `// +build`. §4.2 resolves that. `[source]` `[verified]`

### 4.2 The 30-vs-31 — a COUNTING-UNIT difference, not a scope difference

**6 files carry BOTH directives** — Go's documented migration convention, where the legacy
`+build` line is kept alongside the modern `//go:build` and kept in sync: `[source]` `[verified]`

| File | `go:build` | `+build` |
|---|---|---|
| `sliver\implant\sliver\priv\priv_windows.go` | `windows` | `windows` |
| `sliver\implant\sliver\ps\ps_darwin.go` | `darwin` | `darwin` |
| `sliver\implant\sliver\ps\ps_linux.go` | `linux` | `linux` |
| `sliver\implant\sliver\ps\ps_windows.go` | `windows` | `windows` |
| `sliver\implant\sliver\taskrunner\dotnet_windows.go` | `windows` | `windows` |
| `sliver\util\encoders\base58_genalphabet.go` | `ignore` | `ignore` |

**The arithmetic closes exactly:** `[verified]`

```
files with //go:build only   133
files with // +build only     24
files with BOTH                6
------------------------------------------------
FILES carrying a constraint  163        <- D155's 163
//go:build DIRECTIVES        139  (133+6)   <- D155's 139
// +build  DIRECTIVES          30  ( 24+6)   <- D155's 30
total DIRECTIVE occurrences  169
```

> **139 + 30 = 169 directives over 163 files, and 169 − 163 = 6 is exactly the overlap.
> Both the file count and the directive count are correct; they are different units.**

**Correction to my own earlier claim in this round: `pupy\services\proxy\limits_linux.go` IS
in my scope.** It is a **non-vendor** path (`pupy` non-vendor `.go` = 9, `// +build` = 1), and
it is counted in my 30. I briefly asserted that a vendor exclusion accounted for the
difference; **my own denominator print contradicts that assertion, and the assertion is
withdrawn.** `[source]` `[verified]`

**The file, read:** 20 lines, `// +build linux` at line 1, **no `//go:build` line**, `package
main`, importing `github.com/sirupsen/logrus` and `syscall`; it sets `RLIMIT_NOFILE` to its max
in `init()`. **It is a Go helper living inside a Python RAT, on legacy syntax only.** `[source]`

**Does a vendored Go helper exist under pupy?** The path is `pupy\services\proxy\`, **not**
`pupy\vendor\` — so under my condition 2 it counts. Whether pupy's helper was *fetched* from a
dependency is a separate question the corpus does not answer. `[verified]` on the path;
`[blocked]` on provenance.

---

## §5 Cross-check: the 20,459 denominator

**My Q3 carrier scan walked 20,459 files — which is exactly D140's vendor-excluded corpus
figure for the six targets.** `[source]` `[verified]`

**Two independent scripts in two reports, with different purposes and different filters,
agreeing on the same denominator is a consistency check on the target enumeration itself.**
D140 reached 20,459 by excluding `vendor/`; this run reached 20,459 by walking the same six
roots and excluding `vendor/` and `.git/` with a size cap. **The `.git/` exclusion and the
4 MB cap did not change the count, which means no file in scope is under `.git/` and none
exceeds 4 MB.** `[source]` `[verified]`

---

## §6 Instrument record — three failures, all mine

**I7 — a tool census over file CONTENT with no location test.** My first Q3 pass reported
`make` 76, `cmake` 19, `msbuild` 225, `docker` 373. The samples exposed it:
`covenant\LICENSE` (GPL prose, "make sure" ×14) and
`wwwroot\dist\codemirror\...` (**the string `cmake` in a directory name**).
**This is D140's `post_ex` and D155's `--tags`-inside-`--tags` failure, third occurrence, same
author, same family.** Fixed with a carrier-type test plus a prose-line test; the raw and real
columns are both printed so the artifact population stays auditable.
**225 → 4 for `msbuild` is a factor of 56; a count that large and that wrong is the finding.**
`[verified]`

**I8 — `(?m)` mid-pattern.** `re.error: global flags not at the start of the expression at
position 15`. Python requires global flags at position 0; my `make` alternation had `(?m)` in
the second branch. **Same family as D155's I1 (a bytes literal where a compiled regex was
wanted): the pattern object was not the shape the caller assumed.** Caught by the interpreter.
`[verified]`

**I9 — a prose assertion my own measurement contradicted, caught before publication.** In
`_d165_q4_denominator.py` I wrote a conditional line asserting that `\vendor\` exclusion
dropped `pupy\services\proxy\limits_linux.go`. **The script's own output on the preceding line
showed the path is non-vendor and counted.** **A claim in a print statement that the same
script's data contradicts.** Withdrawn in §4.2. This is D140's I4 (a number that changes with
the print statement) in prose form: **an assertion that changes with the statement that prints
it is a claim about the statement.**

**Two controls failed to prove anything, reported as such:**
- The **negative** vendored-package controls (`go-difflib`, `go-spew`) are **not vendored** —
  `.go=0` — so they never exercised the negative case. **A control that gives the expected
  answer for the wrong reason is not a control.** Not silently replaced.
- The **`pupy` Go-helper provenance** question is `[blocked]`, not answered by the path.

**Control inventory, final:** `[verified]`

| Control | Construction | Can it fail? | Result |
|---|---|---|---|
| Vendored-tag field test | scanner on a tree known to constrain | **yes** — could be 0 | **1,981 constrained / 10,923** |
| Positive pkg control A | `go-sqlite3` | **yes** | **36/44**, 4 named tags |
| Positive pkg control B | `modernc.org/sqlite` | **yes** | **22/33** |
| Negative pkg control A | `go-difflib` | **yes** | **`.go=0` — INVALID, package absent** |
| Negative pkg control B | `go-spew` | **yes** | **`.go=0` — INVALID, package absent** |
| Carrier test | `Makefile` vs `LICENSE` vs `CHANGELOG.md` | **yes** | **True / False / False** |
| `TAGS=` at call site | 63 `make` sites scanned | **yes** | **0 overrides** |
| Directives-vs-files | 169 vs 163 vs 6 overlap | **yes** | **closes to zero residual** |
| `ZZQQ_NO_SUCH_TAG_ANYWHERE` | over 1,850 non-vendor and 10,923 vendored | **yes** — can be >0 | **0, discriminates** |
| `ZZQQ_NO_SUCH_BUILD_TOOL_ANYWHERE` | over 20,459 files | **yes** | **0, discriminates** |
| Any `X >= 0` / `len(X) >= 0`? | inspected in emitted forms | — | **none present** |
| D155's I4 re-check | negated tags satisfied by OMISSION | **yes** | **evaluator truth table 9/9, `!client` both states** |

---

## §7 Status

| Item | Disposition |
|---|---|
| **Q1 `nomsgpack`, reading (a) vs (b)** | **SPLIT CLOSES: (a) CORRECT IN KIND, (b) NOT SUPPORTED.** Cross-module tag; Mythic does not vendor; consumer named as `github.com/ugorji/go/codec v1.3.1` in `go.mod`. §1.4 `[source]` `[verified]` `[inferred]` |
| **Q1 mandatory control** | **Scanner PROVEN to see vendored tags: 1,981/10,923, 206 tags.** `nomsgpack` = **0** is a **finding**, not a blind spot. §1.3 `[source]` `[verified]` |
| **Q1 negative controls** | **FAILED to prove anything** — both packages absent from the tree. Reported, not replaced. §1.3 `[verified]` |
| **Q1 residual** | Proving `ugorji/go/codec` is the consumer needs that module's source — **absent.** §1.4 `[blocked]` |
| **Q2 `$Tags`** | **ANSWER BY CONSTRUCTION: `go_sqlite`.** 63 `make` callers, **0 pass `TAGS=`**; `TAGS ?=` default ships; effective flags `go_sqlite,server` / `go_sqlite,client`. §2.2 `[source]` `[verified]` |
| **Q3 verb generalisation** | **15 build-verb families with real carriers; D155's verb list covered 1.** §3.4 `[source]` `[verified]` |
| **Q3 artifact problem** | My first census matched prose and directory names — **third occurrence of this family.** §3.1, §6 I7 `[verified]` |
| **Q4 denominator** | **1,850 / 163 / 139 / 30 all reproduce exactly**, per-target printed. §4.1 `[source]` `[verified]` |
| **Q4 30-vs-31** | **COUNTING UNITS, not scope: 169 directives, 163 files, 6 files carry BOTH.** Arithmetic closes with zero residual. §4.2 `[source]` `[verified]` |
| **Q4 pupy file** | **IN MY SCOPE** — non-vendor path. My earlier opposite assertion is **withdrawn**. §4.2 `[verified]` |
| **Cross-check** | 20,459 files = D140's vendor-excluded denominator, reproduced independently. §5 `[source]` |
| **Instrument failures** | **3 of mine (I7, I8, I9) + 2 invalid negative controls**, all disclosed. §6 `[verified]` |

**Constraints honoured:** static only · no execution · no network · no live C2 · no REA · no
`open_binary` · no `go` toolchain (every building claim `[inferred]`) · `[absence]` and
`[blocked]` each carry their enumeration or their missing artifact · frozen documents untouched
· **every failure disclosed rather than deleted.**

**Cross-references (cited, not re-derived):** D140 §1 (vendor exclusion, 20,459) and D140 §5.4
(liveness is a BUILD property) — D155 ported it to Go and D165 measures its verb-list bound.
D155 §2.1 (`nomsgpack` asymmetry) — resolved here as EXPECTED rather than anomalous.
D149 (the tautological control shape) — §6's control inventory audited against it.
`_INSTRUMENT_RULE_34` and `_INSTRUMENT_RULE_37` — read as required pre-reading.

**D155's census is NOT re-derived here.** It is verified and reused; §4.1 reprints its
denominator only because the Lead asked for it to be auditable rather than asserted.
