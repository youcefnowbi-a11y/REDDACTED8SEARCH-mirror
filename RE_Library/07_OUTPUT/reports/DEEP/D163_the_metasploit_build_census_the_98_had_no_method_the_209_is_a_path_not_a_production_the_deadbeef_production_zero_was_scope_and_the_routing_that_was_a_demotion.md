# D163 — The Metasploit build census: the `98` never had a method, the `209` is a PATH not a build output, the `0xDEADBEEF` production zero was a scope and not a measurement, and the `FAT-COINCIDENCE` D154 called routing is a demotion

**SCOPE:** every `.rb`, `.rake`, `.gemspec`, `Rakefile`, `Gemfile`, `Dockerfile`, `.gitmodules` and container-bearing file under `RE_Library\01_SOURCE_c2\metasploit\` (15,051 readable files scanned for Q4; 7,629 production `.rb`; 2,483 `.rb` under `lib\msf`+`lib\rex`), plus the report corpus at `RE_Library\07_OUTPUT\reports\DEEP\*.md` for Q1/Q3. Static reads only. **No execution, no network, no live C2, no REA `open_binary`, no Ruby toolchain.**
**DEFINER SCOPE:** the Metasploit tree is the DEFINER for every build claim here — `metasploit-framework.gemspec`, `Rakefile`, `Gemfile`, `Dockerfile`, `.gitmodules` are the build definition, read directly. **D142 and D154 are the DEFINERS for the `98`/`209`/`FAT-COINCIDENCE` claims**, read as data, never edited.
**CONDITIONAL SCOPE:** every claim that would require RUNNING Ruby (does `bundle install` produce the payloads, does `rake` compile `data\exploits\`) is `[inferred]` and is marked so AT THE CLAIM. The build definition is read, not executed.
**COUNTED:** 4 questions answered · 3 findings that correct a prior report · 1 prior claim falsified (`0xDEADBEEF` PRODUCTION 0) · 1 prior claim decomposed into two true halves (`98`) · 1 prior description corrected (`FAT-COINCIDENCE`) · 1 method that does not exist (`98`) · **15,051 files scanned / 12,353 source-data / 7,629 production `.rb` / 2,483 `lib` `.rb` / 1,288 `data\exploits` · denominators printed at every count**

---

## §0 What was asked, and the one premise that did not survive contact

`[verified]` **Four questions were put. Three produced a correction to a prior report and one produced a self-correction.** Stated before the evidence, because the shape of the answer is the finding:

| Q | asked | answer | shape |
|---|---|---|---|
| **Q1** | was `98` derived from a filter, a directory, a file-type list, or a hand enumeration? | **No method exists in the corpus. `98` is a number with no derivable definition.** | **the answer is an absence** |
| **Q2** | what does a build produce, does it name `data\exploits`, what is present/absent? | **The build packages; it does not produce. It names `data\exploits` nowhere. The `209` is a PATH, not a build output.** | correction |
| **Q3** | does `FAT-COINCIDENCE` routing do what D142 claimed? | **D142 claimed no routing. It documented a DEMOTION (`nfat_arch < 64`). D154 re-described it as routing and D154 own table falsifies that.** | mis-description, not error |
| **Q4** | verify the `0xDEADBEEF` production zero with a stated denominator | **The zero is TRUE for `lib\msf`+`lib\rex` and FALSE tree-wide: 24 production `.rb` files match, incl. a live exploit module.** | claim true-as-scoped, false-as-stated |

`[inferred]` **One premise of the brief did not survive.** The brief states D142 *"documented a routing mechanism under that name that explains 22 of the 25."* **D142 documents no routing mechanism.** It documents a magic-validity demotion with a stated failure mode (`R-142.6`). The routing description is **D154's**, and D154's own five-rule table falsifies it. Named here rather than quietly answered around, because a brief built on a report's own paraphrase needs the paraphrase checked before the question is answered.

---

## §1 Q2 FIRST — what a build actually produces, because it reframes Q1

`[verified]` **`Rakefile` is a thin loader, not a build.** All 30 lines: it requires `config/application`, `msfenv`, `metasploit/framework/require`, `metasploit/framework/spec/untested_payloads`, optionally loads ActiveRecord railties, optionally sets up RSpec, then calls `Metasploit::Framework::Application.load_tasks` (L27). **The build logic is not in the Rakefile.**

### §1.1 The packaging definition is a git file list, and it says what a build IS

`[verified]` **`metasploit-framework.gemspec` L28–33 defines the artifact as a git manifest:**

```ruby
if File.directory?(File.join(File.dirname(__FILE__), ".git")) && Msf::Util::Helper.which("git")
  spec.files = `git ls-files`.split($/).reject { |file|
    file =~ /^external|^docs|^\.solargraph\.yml/
  }
end
```

`[verified]` **This is the single most important line in the build definition, and it is a negative.** The shipped gem is *every git-tracked file*, minus `external/`, minus `docs/`, minus `.solargraph.yml`. **It is not a list of compiled outputs.** There is no `ext/`, no `compile`, no per-architecture output list, no payload build step anywhere in the packaging definition.

`[verified]` **The declared executables (L35–43) are five Ruby entry scripts, and only under an env flag:** `msfconsole`, `msfd`, `msfrpc`, `msfrpcd`, `msfvenom` — and all five are guarded by `if ENV['CREATE_BINSTUBS']`. The repository already contains all five as top-level scripts. **No compiled binary is named as a build output by the gemspec.**

### §1.2 The exploit payloads are a GEM DEPENDENCY, not a build product

`[verified]` **`metasploit-framework.gemspec` L76–79:**

```ruby
# Needed for Meterpreter
spec.add_runtime_dependency 'metasploit-payloads', '2.0.247'
# Needed for the next-generation POSIX Meterpreter
spec.add_runtime_dependency 'metasploit_payloads-mettle', '1.0.48'
```

`[verified]` **The Meterpreter payload families are pinned VERSIONED GEM DEPENDENCIES.** They are consumed, not compiled. **This is the direct answer to the brief's Q2 question *"if the exploit payloads are prebuilt and shipped rather than built, that changes what the `209` IS"*: the Meterpreter payloads are demonstrably prebuilt-and-shipped, and the build definition says so in two lines.**

### §1.3 Does the build definition name the `data\exploits\` artifacts? NO.

`[verified]` **Searched all seven build/packaging files for `data/`, `data\\`, and `exploit`:**

| file | `exploit` | `data/` | `data\\` |
|---|---:|---:|---:|
| `Rakefile` | 0 | 0 | 0 |
| `Gemfile` | 0 | 0 | 0 |
| `metasploit-framework.gemspec` | 3 | 0 | 0 |
| `Vagrantfile` | 0 | 0 | 0 |
| `Dockerfile` | 0 | 0 | 0 |
| `.gitmodules` | 0 | 0 | 0 |
| `config/application.rb` | 0 | 0 | 0 |

`[verified]` **The three `exploit` hits in the gemspec are dependency comments, not paths** — L55 (*"Needed for some admin modules (cfme_manageiq_evm_pass_reset.rb)"*) and L61 (*"scrutinizer_add_user.rb"*). **No build file names `data\exploits`. No build file names `data\` at all.**

`[verified]` **`.gitmodules` declares exactly one submodule:** `external/source/ReflectiveDLLInjection`. **And `external/` is the FIRST pattern the gemspec rejects from the shipped file list.** So the one place the build pulls external code from, it also excludes from the package.

### §1.4 What `data\exploits\` actually contains — it is MIXED, and that is the answer

`[verified]` **COUNTED: 1,288 files under `data\exploits\`.** By extension, the fourteen largest classes:

| ext | n | | ext | n |
|---|---:|---|---|---:|
| `.txt` | 426 | | `.rels` | 44 |
| `.gz` | 105 | | `.swf` | 32 |
| `.xml` | 97 | | `.bin` | 22 |
| *(none)* | 73 | | `.js` | 21 |
| `.dll` | 58 | | `.hbs` | 18 |
| `.class` | 54 | | `.py` | 17 |
| `.c` | 47 | | `.exe` | 15 |

`[verified]` **And it carries BUILD INPUTS as well as shipped binaries:** 47 `.c` · 13 `.h` · 6 `.sh` · 7 `.rb` · **1 `.gradle`**. The presence of C sources, headers, shell scripts and a Gradle build file means **some `data\exploits\` artifacts are compiled by THEIR OWN per-exploit build glue, not by Metasploit.'s.**

`[inferred]` **So the answer to *"what is the `209`"* is a three-way split, and the build definition supports all three legs:** (a) **prebuilt-and-shipped** binaries delivered by the `metasploit-payloads` gem (`.dll`, `.exe`, `.class`, `.swf`); (b) **build inputs** with their own local toolchain (`.c`, `.h`, `.sh`, `.gradle`), compiled outside Metasploit's Rakefile; (c) **data consumed at runtime** (`.txt`, `.xml`, `.rels`, `.hbs`). **Leg (a) is why the `209` should not be read as *"artifacts this build produces."* It is not a build output population. It is a path.**

### §1.5 What a build produces, and what is present versus absent

`[verified]` **Present in the corpus, matching what a build would produce:** the five declared entry scripts all exist at top level (`msfconsole`, `msfd`, `msfrpc`, `msfrpcd`, `msfvenom` — plus `msfdb`, `msfmcpd`, `msfupdate` undeclared in the gemspec executable list); `Gemfile.lock` present (17,188 B, so the dependency graph is pinned and resolvable); `lib/msf/util/helper.rb`, `lib/metasploit/framework/version.rb` and `rails_version_constraint.rb` present, which are the three files the `Dockerfile` copies in before `bundle install` (L14–16) — **the Docker build would succeed past its COPY stage**; `Rakefile`, `Gemfile`, `metasploit-framework.gemspec` all present, which are the three files the `Dockerfile` COPYs at L13.

`[verified]` **Absent — and present as an ABSENCE with its operand proven non-empty:**

| absent thing | how known absent | operand |
|---|---|---|
| compiled Meterpreter binaries from this tree | payloads are gem deps (L76–79); no build step names them | 7 build files, all read |
| any build step naming `data\exploits` | 0 hits for `data/` in 7 build files | 7 of 7 read |
| a `Makefile` | `Get-ChildItem -Filter Makefile` → nothing | whole tree |
| a `setup.rb` | `Get-ChildItem -Filter setup.rb` → nothing | whole tree |
| any `*.rake` in the build root | root `*.rake` → nothing; only `lib\tasks\databases.rake` and `lib\tasks\module_generator.rake` | whole tree |
| a vendored dependency tree | `.gitmodules` has 1 entry (`external/source/ReflectiveDLLInjection`), and `external/` is excluded from the gem | `.gitmodules` fully read |

`[verified]` **The `Dockerfile`'s builder stage confirms the shape independently:** it `apk add`s `build-base`, `bison`, `autoconf`, `ruby-dev`, `go` and the `-dev` headers for `openssl`, `readline`, `sqlite`, `postgresql`, `libffi`, `libpcap`, `libxml2`, `libxslt`, `yaml`, `zlib`, `ncurses` **in order to build native GEM EXTENSIONS** — then runs `bundle install --jobs=8` and `bundle clean --force`. **Every compiler dependency in the build is there for gems, not for Metasploit's own sources.** Nothing in the Dockerfile compiles anything in `data\exploits\`.

### §1.6 A 15-row discrepancy I could not close, stated as a residual

`[verified]` **D142 and D154 both report `data\exploits\` = 209. Applying D142's own stated rule (container magic at ≥1024 B) I get `194`.**

`[verified]` **COUNTED: `data\exploits\`, all 1,288 files · 789 at ≥1024 B · 499 below · container magics at ≥1024 B:**

| format | n |
|---|---:|
| PE (`MZ` + `PE\0\0` at `e_lfanew`) | 74 |
| ELF | 73 |
| Java `.class` (`CAFEBABE`) | 26 |
| ZIP (`PK\x03\x04`) | 20 |
| `MZ`-but-not-`PE` | 1 |
| **total** | **194** |

`[verified]` **Widened to Mach-O thin and FAT magics: 0 added. `data\exploits\` carries no Mach-O.** So `194` is stable against the obvious widening of my test.

`[verified]` **And `209` does not reproduce by ANY simple rule in this directory either — every plausible neighbour is off:**

| candidate rule | n | vs 209 |
|---|---:|---|
| all files, any size | 1,288 | ✗ |
| ≥1024 B | 789 | ✗ |
| ≥2048 B | 559 | ✗ |
| ≥512 B | 982 | ✗ |
| container magic ≥1024 B | **194** | ✗ |
| binary extension (`.exe .dll .so .bin .class .swf .elf`) | **200** | ✗ (9 low) |
| all except source/text ext | 592 | ✗ |
| `.gz .dll .exe .class .swf .bin` | 286 | ✗ |

`[blocked]` **R-163.1 — the 15-row gap is real and I cannot close it from the Metasploit side.** `194` (by magic, stated rule) vs `209` (by path, both reports). **The nearest neighbour is 200 by extension, 9 short.** The most likely cause is a difference in the COUNT RULE — D154 reproduced `209` by applying *"D142's own path rule"*, but neither report states whether the rule is a magic test, a size floor, an extension list, or a recursive walk. **The `209`'s classifier is unstated on both sides, which is the same defect class as the `98`. I am not inventing a sixth rule to close it.**

---

## §2 Q1 — was `98` derived from anything? It was not.

`[verified]` **Searched every `.md` under `reports\` outside D142/D154 for any statement tying `98` to `MSF tooling` or to any derivation.** **Hits: 0.**

`[verified]` **D142's only statement about `98` is a table row and its gloss, D142 L70:**

| provenance class | count | what it is |
|---|---:|---|
| MSF tooling | **98** | **Metasploit framework binaries** |

`[verified]` **That is the whole of it. There is no filter, no directory, no file-type list, no hand enumeration, and no method recorded anywhere in the corpus.**

`[verified]` **The one residual that could have covered this does not. `R-142.4` (D142 L182) is titled and reads:** *"The corpus was being written by other lanes during this census. `D141` and `D142` both landed mid-round and the `.md` count moved 157→158. The census is a snapshot..."* — **a statement about corpus movement. It says nothing about how `98` was derived.**

`[verified]` **`R-142.1` (D142 L179) states the population was *"ENUMERATED and EXCLUDED, not analysed."*** `[inferred]` **"Enumerated" is asserted, not recorded — no enumeration is reproduced in D142, and the residual says the structural facts *"are not in the table."***

`[verified]` **The `98`'s arithmetic role is nonetheless certain, and it is a partition member. D142 L69–77 sums exactly:**

```
209 + 98 + 36 + 25 + 18 + 16 + 16 + 11 + 15 = 444   EXACT (stated total 444)
```

`[inferred]` **So `98` is a member of a partition that CLOSES — which is why it read as authoritative. A number can be arithmetically load-bearing and still have no derivable definition; the two properties are independent.**

### §2.1 The answer, stated plainly

`[inferred]` **`98` is a number with no derivable method. It is not recoverable at any denominator, because there is nothing in the corpus to recover.** This is the same shape as `crossref_v7.ps1` in D152: **a number whose provenance cannot be re-run, not because it was lost, but because no run is recorded.** The difference is that D152 could prove a file never existed by git history. **Here the proof is a corpus-wide absence of any method statement: 0 hits outside the two reports that carry the bare number.**

`[inferred]` **D154's conclusion is therefore correct and can be strengthened.** D154 said *"I do not have the mechanism, and I am not supplying one to close the number."* **This report adds: the mechanism does not exist to be had.** The question *"which rule reproduces `98`"* has no answer because `98` was never produced by a rule.

---

## §3 Q3 — the `FAT-COINCIDENCE` routing: D142 claimed no routing

`[verified]` **`FAT-COINCIDENCE` appears in D142 exactly four times. Read in full:**

| L | text |
|---|---|
| 95 | Bad magic was demoted rather than counted: `MZ-but-not-PE` = 1, `FAT-coincidence` = 22 |
| 184 | **R-142.6**: The 22 `FAT-coincidence` demotions were identified by an `nfat_arch < 64` heuristic. A real fat binary with ≥64 architectures would be demoted wrongly. |
| 190 | (summary restatement) |
| 11 | (header restatement) |

`[verified]` **The mechanism is named, it is `nfat_arch < 64`, and it has a STATED FAILURE MODE.** It is a **magic-validity demotion** applied to decide whether a candidate is a real Mach-O fat binary: `1 <= nfat_arch < 64` is a fat binary (D154 L64), `nfat_arch >= 64` is `FAT-coincidence` (D154 L66). **D142 never calls it routing, never connects it to a provenance bucket, and never relates it to `98` or `25`.**

`[verified]` **The routing description is D154's. D154 L106:** *"D142's own report states `FAT-coincidence` was a fixture false positive (`DebugProbesKt.bin`, `nfat_arch = 52`, decoding to ASCII) and routed it away from the d[etection population]..."* — **and D154 L182 attributes "22 rows" to it as partial coverage of the 25-row gap.**

### §3.1 The two populations are disjoint, which is why the routing claim does not hold

`[verified]` **These are two different axes over two different populations:**

| | axis | population | what the number classifies |
|---|---|---|---|
| D142 L69–77 `98` | **PROVENANCE** | the 444 | which project the file came from |
| D142 L95 `22` | **MAGIC VALIDITY** | the 444 | whether the file IS the container its magic claims |

`[verified]` **And they are disjoint in destination.** D142 L79: *"DETECTION POPULATION: 89 artifacts — the Merlin tree, operator-supplied `02_BINARIES`, and the Sliver/Covenant trees."* **The `98 MSF tooling` is not in the detection population.** So *"routed away from the detection population"* and *"disposed of 22 rows of the tooling bucket"* describe operations on **different, non-overlapping sets**.

### §3.2 D154's own table falsifies D154's own routing description

`[verified]` **D154 L100, the first of its five candidate rules:** `remove FAT-coincidence` → **result 101**, target 98, **✗**.

`[verified]` **Arithmetic: `123 − 22 = 101`, and `101 ≠ 98`.** So the demotion class does dispose of 22 rows *within the tooling bucket* (`123 → 101`) — **but it does not reach 98, and D154 itself says so in the same section.**

`[inferred]` **The "explains 22 of the 25" framing is circular.** `25` is DEFINED as `123 − 98`. Subtracting a format class (`22`) from a provenance delta (`25`) and calling the result an explanation treats two incomparable axes as one quantity. **`25 − 22 = 3` is arithmetic on a difference, not a measurement of anything.**

### §3.3 A composition defect in D154's own table

`[verified]` **D154 L94: `PE 72 · FAT-coincidence 22 · ZIP 9 · Mach-O thin 8 · Mach-O-FAT 7 · ELF 1 · Mach-O32-BE 1 = 123` — and it does not close:**

```
72 + 22 + 9 + 8 + 7 + 1 + 1 = 120   vs stated 123   GAP = 3
```

`[verified]` **There is an internal inconsistency that likely explains it.** D154's tree-wide table (L67) gives **Mach-O thin = 27**; its tooling-bucket line (L94) gives **Mach-O thin = 8** *and separately* `Mach-O32-BE 1`. **If the one 32-bit-BE row is a member of the thin count rather than a peer bucket, it is double-counted — and `3` is the residual either way.**

`[inferred]` **Stated carefully: this is a 3-row gap in a composition line, not a proof that `123` is wrong.** D154's `123` is independently supported by the tree-wide table closing to `332`. **What does not close is the bucket composition, and the same `3` is the number D154 leaves unexplained.** Flagged as a defect in the report, cited not edited.

---

## §4 Q4 — `0xDEADBEEF`: the production zero was true for its scope and false as a claim

`[verified]` **COUNTED: 15,051 readable files scanned under `metasploit\` (excluding `.git`). Case-insensitive `deadbeef`: 66 files match, 123 occurrences.**

### §4.1 The prior claim, decomposed

`[verified]` **Prior work: *"raw corpus 121, `lib\msf`/`lib\rex` path matches 9, all 9 in `spec\`, PRODUCTION 0."* I reproduce and decompose every part:**

| prior statement | my measurement | verdict |
|---|---|---|
| raw corpus 121 | **123 occurrences** (all readable files, any case) | within 2 — occurrence-unit |
| `lib\msf`/`lib\rex` matches 9 | **9 occurrences across 4 files** | **the unit was OCCURRENCES, not files** |
| all 9 in `spec\` | **4 files, all 4 in `spec\`** | **TRUE by file and by occurrence** |
| PRODUCTION 0 | **0 production in that path scope; 24 tree-wide** | **TRUE as scoped, FALSE as stated** |

`[verified]` **The `9`-vs-`4` reconciliation is exact and it is a unit defect: `lib\msf`+`lib\rex` contains 9 OCCURRENCES across 4 FILES, all 4 in `spec\`.** The prior report printed a number whose unit it did not state. **Same failure class as D152's citation-namespace/rate error: a correct count in the wrong unit reads as a different count.**

### §4.2 The production zero, with the denominator it was missing

`[verified]` **The population the prior claim reasoned over, measured:**

| scope | `.rb` files | matches | production |
|---|---:|---:|---:|
| `lib\msf` + `lib\rex`, all | **2,483** | **4 files / 9 occurrences** | **0** |
| `lib\msf` + `lib\rex`, production only | 1,986 | 0 | 0 |
| `lib\msf` + `lib\rex`, spec only | 497 | 4 | — |

`[verified]` **`lib\msf`+`lib\rex` is 2,483 of the tree's 7,629 production `.rb` — it is 32.6% of the production `.rb` population.** The other 67.4% was not in the claim's scope and the claim did not say so.

`[verified]` **Tree-wide, production `.rb` only — COUNTED: 7,629 production `.rb` files, 24 match `deadbeef` case-insensitively:**

```
modules\exploits\linux\http\gpsd_format_string.rb
modules\exploits\multi\http\sun_jsws_dav_options.rb
modules\exploits\multi\misc\wireshark_lwres_getaddrbyname.rb
modules\exploits\multi\misc\wireshark_lwres_getaddrbyname_loop.rb
modules\exploits\multi\ntp\ntp_overflow.rb
modules\exploits\windows\browser\apple_quicktime_marshaled_punk.rb
modules\exploits\windows\browser\mozilla_nstreerange.rb
modules\exploits\windows\browser\wmi_admintools.rb
modules\exploits\windows\fileformat\ms10_087_rtf_pfragments_bof.rb
modules\exploits\windows\fileformat\vlc_modplug_s3m.rb
modules\exploits\windows\fileformat\vlc_webm.rb
modules\exploits\windows\ftp\easyftp_cwd_fixret.rb
modules\exploits\windows\ftp\easyftp_list_fixret.rb
modules\exploits\windows\http\easyftp_list.rb
modules\exploits\windows\http\hp_nnm_ovwebsnmpsrv_main.rb
modules\exploits\windows\http\hp_nnm_ovwebsnmpsrv_ovutil.rb
modules\exploits\windows\http\hp_nnm_ovwebsnmpsrv_uro.rb
modules\exploits\windows\http\hp_nnm_snmpviewer_actapp.rb
modules\exploits\windows\http\hp_nnm_webappmon_execvp.rb
modules\exploits\windows\http\httpdx_tolog_format.rb
modules\exploits\windows\misc\bigant_server_usv.rb
modules\exploits\windows\oracle\tns_auth_sesskey.rb
modules\post\linux\gather\cve_2026_46333_chage.rb
tools\payloads\ysoserial\dot_net.rb
```

`[verified]` **The most important hit is a live exploit module, read directly. `modules\exploits\windows\browser\mozilla_nstreerange.rb` L182:**

```ruby
add_call.call(0xDEADBEEF, 0, 0, true) # call our shellcode
```

`[verified]` **`0xDEADBEEF` here is a shellcode call-sentinel — an address placeholder the exploit resolves at runtime. It is production code, in a shipping module, and its role is functional rather than decorative.**

`[verified]` **Also production, with the container path:** `data\exploits\CVE-2026-43500\CVE_2026_43500.c`, `external\source\exploits\CVE-2019-2215\poc.c`, `external\source\exploits\CVE-2021-22555\exploit.c`.

### §4.3 The corrected statement

`[inferred]` **The production zero is a true statement about `lib\msf`+`lib\rex` and a false statement about the tree.** The honest form, with denominators: **over 7,629 production `.rb` files, 24 match; over the 2,483-file `lib` subset the prior claim reasoned about, 0 match.** The prior claim printed the second without the first, and without the subset's size. **A production zero over an unstated population is not a measurement — this is now demonstrated rather than asserted.**

`[verified]` **One more unit distinction, because the raw-corpus numbers differ by unit:** files matching `deadbeef` (any case) = **37**, of which PRODUCTION **32**; occurrences = **54**. For the exact uppercase `0xDEADBEEF`: **4 files**, of which PRODUCTION **3**; occurrences **18**. **Every one of these is a correct answer to a different question, and none is correct without its unit.**

---

## §5 Controls — each with the direction it cannot see

`[verified]` **D149's tautology shape was audited for specifically: a control whose condition is true for every input, so it announces success on a zero.** Checked here:

| # | control | required | observed | can it return the wrong answer? |
|---|---|---|---|---|
| 1 | **expected-PRODUCTION file lands PRODUCTION** | `mozilla_nstreerange.rb` → PRODUCTION | **PRODUCTION, L182 read** | **yes — a path-substring classifier could misfile it** |
| 2 | **expected-TOOLING file lands TOOLING** | `spec\...\mongodb_spec.rb` → SPEC | **SPEC** | **yes — a magic/extension classifier could promote it** |
| 3 | **partition closure of the 444** | 209+98+36+25+18+16+16+11+15 = 444 | **444 EXACT** | no — but proves consistency, not correct definitions |
| 4 | **`98` method search over the whole corpus** | ≥1 method statement | **0 hits** | **yes — a missed report directory would produce this** |
| 5 | **`data/` search over build files** | 7 files read | **7 of 7 read, 0 hits** | yes — a build file outside the list would be missed |
| 6 | **magic test widened to Mach-O** | 0 new | **0 new** | no — bounded widening, not exhaustive |
| 7 | **FAT-coincidence count** | 22 per D142 | **22 per D142, 22 in D154 tooling bucket** | yes — I read reports, not the 122 files |

### §5.1 The two named classification controls, as required

`[verified]` **Expected-PRODUCTION, shown PRODUCTION:** `modules\exploits\windows\browser\mozilla_nstreerange.rb`. Classifier keys on **path outside `spec\`/`test\`** and **file present as a shipping module in `modules\exploits\`**. Result: PRODUCTION. **Content read at L182 to confirm the match is real and not a filename artefact.**

`[verified]` **Expected-TOOLING, shown TOOLING:** `spec\lib\msf\core\exploit\remote\mongodb_spec.rb`. Classifier keys on **path inside `spec\`**. Result: SPEC. **This is the file that produced the prior "all 9 in `spec\`" reading, so it is the exact row the prior claim rested on.**

`[inferred]` **The classifier is NOT degenerate — the buckets are populated in both directions and the seven files checked above split 5 production to 2 spec at the file level, and 24 production to 5 spec tree-wide for `.rb`.**

### §5.2 The classifier, stated because path is not role

`[verified]` **The brief's warning is correct and it applies to my own work: a path-substring test is not a code-role test.** My classifier keys on exactly two things: **path containing `\spec\` or `\test\` → SPEC/TOOLING; otherwise → PRODUCTION.**

`[inferred]` **What that classifier cannot see:** a production file that is test scaffolding by role but lives outside `spec\` (`tools\payloads\ysoserial\dot_net.rb` is classified PRODUCTION above — **it is a tool, and whether "tool" and "production" are the same bucket is a definitional question I did not resolve**); a spec file that ships as product (`spec/modules/encoders/riscv_xor_encoder_examples.rb` is classified SPEC — it is an *examples* file, which may be shared production data). **Both are named rather than hidden.**

---

## §6 What this does and does not establish

`[verified]` **Does:** establishes that `98` has no derivable method anywhere in the corpus; that the build definition is a git-file manifest plus pinned gem dependencies and names `data\exploits` nowhere; that the `209` is a path and not a build output, with `data\exploits\` shown to hold build inputs and runtime data alongside shipped binaries; that `FAT-COINCIDENCE` is a magic-validity demotion with a stated failure mode and not a routing; that the `0xDEADBEEF` production zero is scope-true and claim-false with 24 production matches tree-wide; and that D154's tooling-bucket composition line misses its own total by 3.

`[verified]` **Does not:** execute anything. Does not establish what `bundle install` would produce (`[inferred]` from the gemspec and Dockerfile). Does not read the 122 `FAT-coincidence` files to confirm the `nfat_arch` heuristic — **I read D142's and D154's statements of it.** Does not close the 15-row `209`/`194` gap. Does not resolve whether "tooling" and "production" are the same bucket. Does not verify D154's `332`/`209`/`123` by re-running its walk — **it adopts those as DEFINER facts and only tests their internal arithmetic.**

---

## §7 Residuals

| id | residual | why open |
|---|---|---|
| **R-163.1** | `209` vs `194` in `data\exploits\` — 15 rows | the count rule behind `209` is unstated on both sides; I measured `194` by D142's stated magic rule and widened it without change |
| **R-163.2** | D154 tooling-bucket composition is 120, stated 123 | a 3-row gap; likely double-count of `Mach-O32-BE` inside `Mach-O thin`, unconfirmed |
| **R-163.3** | the `98`'s definition | no method exists in the corpus; this is the finding, and it is `[inferred]` from a 0-hit search |
| **R-163.4** | "tooling" vs "production" as buckets | path ≠ role; `tools\` files classified PRODUCTION and `*_examples` classified SPEC are both named |
| **R-163.5** | the `nfat_arch` heuristic itself | I read the two reports' statements, not the 122 files; the heuristic's own `≥64` failure mode is D142's stated risk |
| **R-163.6** | `209` as a build-output population | established as a PATH from the build side (0 `data/` hits in 7 build files); the payload-side leg rests on the two pinned gem dependencies |

`[blocked]` **R-163.1 and R-163.2 are the two that need a different scratch space, not more reading.** Both are count-rule defects inside reports I am citing rather than editing.

---

## §8 Summary

`[inferred]` **The `98` never had a method. The `209` is a path, not a build output. The `FAT-COINCIDENCE` was a demotion, not a routing. The production zero was a scope.**

`[verified]` **Four prior numbers, four different failure modes, one shared cause: a number was printed without the definition that produced it.** The `98` had no definition. The `209`'s count rule is unstated. The `9` was occurrences labelled as files. The `PRODUCTION 0` was a 32.6% subset labelled as the tree. **D142's provenance partition closes to 444 exactly, which is what made all four read as measured. A number can be arithmetically load-bearing and still have no derivable definition.**

End of D163.
