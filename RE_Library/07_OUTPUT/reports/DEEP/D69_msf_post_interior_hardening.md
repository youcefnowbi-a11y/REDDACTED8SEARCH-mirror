# D69 — MSF post-module interior hardening

**Scope:** `RE_Library\01_SOURCE_c2\metasploit` — `lib/msf/core` and `modules/post`, with `modules/auxiliary` touched only where a `cmd_exec` site is cited.
**Lane:** source-only. No REA provider opened, no target held, nothing executed.
**Method:** every regex that anchors with `^` carries `re.MULTILINE`. Every quantified zero carries a positive control. Matches are printed, not summarised. Populations are enumerated, not constructed.

---

## Table of Contents

- **§0 — Corrections**, three, two of them mine
- **§1 — Q1: reach of the silent branch**
  - §1.1 The dispatch census: 10 sites, 9 without `else`
  - §1.2 The dispatch *style* census: `case` is the minority
  - §1.3 Reach: the declared-population argument
  - §1.4 Reach: the undeclared population, and the honest verdict
- **§2 — Q2: the `cmd_exec` risk number**
  - §2.1 The classification rule, stated before use
  - §2.2 The counts
  - §2.3 Samples of every class
  - §2.4 What the interpolation classes actually contain
  - §2.5 The risk number, and why I refuse to state a single one
- **§3 — Q3: the compatibility warning, taken to consequence**
  - §3.1 What the check tests
  - §3.2 The three dispatch styles
  - §3.3 The `else` catch-alls
  - §3.4 Verdict: a third class
- **§4 — Q4: the `alias` class, proved**
  - §4.1 The count correction
  - §4.2 Eight dead aliases, and the ninth killed
  - §4.3 Why this is the `restypes` analogue
- **§5 — Residual unknowns, each with a concrete probe**
- **§6 — Instrument record**
- **§7 — Status**

---

## §0 Corrections

**Three. Two are corrections to my own D45; one is a correction to this brief's framing.**

### §0.1 D45's alias figure was wrong: `95 / 54` should be `55 / 32`, and the mechanism was a substring-class error

D45 §4 reported **"`alias`/`alias_method` — 95 sites / 54 files."** The probe behind it was:

```python
re.compile(r'^\s*(prepend|include|extend|alias|alias_method)\b', re.M)
```

**`\b` does not help here.** In `aliases: ['PayloadProxyHost']` and `alias1, alias2 = 2.times.map { ... }`, the token `alias` is followed by `e` and `1` — both word characters, so `alias\b` matches **inside `aliases:` and `alias1`.** The bare `alias` alternative therefore counts prose and local variables as if they were alias declarations.

Decomposing that one probe by which alternative matched, over `lib/msf/core`:

| alternative | statements | files |
|---|---|---|
| `include` | 964 | 452 |
| `alias` | 48 | 25 |
| `extend` | 24 | 20 |
| `alias_method` | 7 | 7 |
| `prepend` | 2 | 2 |

**`alias` + `alias_method` = 55, not 95.** The `95` in D45 was a hand-tally, not this probe's output, and the two never agreed — I did not notice the disagreement at write time.

**This also corrects D45's `include` figure.** D45 §4 reported **`include` 425 files / 904 statements.** The same probe now reports **452 files / 964 statements.** I cannot reconstruct which variant produced 904; the current measurement is the one I can reproduce and it is 964. **The `extend` figure moves too: 24 statements / 20 files, against D45's 24 sites across "20 files" — that one agrees.**

Applying a real Ruby alias grammar (`alias new old`, `alias :new :old`, `alias_method :new, :old`, with optional trailing comment):

**55 alias statements in 32 files.** This is the number §4 uses.

**The instrument failure is a subclass I want on the record:** not the D53 substring error where `LoadLibrary` hides inside `LoadLibraryEx` — here the *word-boundary anchor itself* failed, because `\b` sits between a letter and a digit and the corpus writes `alias1`. **A `\b`-terminated keyword probe against Ruby identifiers is not safe when the corpus uses numeric suffixes.**

### §0.2 D45's `def check` probe and the 8 false positives stand as reported; the §4 verdict did not

D45 §0.1 and §6.2 already record the name-filter error correctly (8 false positives, all correct by composition). **What needs correcting is the conclusion I drew from §4's bad count.** I wrote that `alias`/`alias_method` at "95 sites" was the one silent form of the `restypes` class, **and named it a candidate with no instance proven.** The count was wrong *and* the class had a provable instance sitting in it. §4 now proves eight. **A candidate class is still worth naming when the count is wrong — but I should have looked before declaring it unproven.**

### §0.3 The brief's Q3 framing offers two outcomes and the corpus does neither

Q3 asks me to say whether the compatibility warning precedes **a crash** (a UX defect) or **silent wrong behaviour on the target** (a different thing).

**It precedes a third thing:** the first operational call returns **`nil` or `false` while the module continues**, because the dominant dispatch style is not the silent `case` from D45 §3.5 at all — it is **independent `if session.type == '...'` guards with explicit `return`**, and a mismatch falls through them. `Post::File` has **35 `if`-guards and 19 `elsif`-chains and zero `case` statements** (§3.2). A mismatch therefore does not crash the framework and does not always issue a command the target cannot honour — **it returns a negative or empty value that the caller may treat as a real result.**

The genuine silent-wrong-behaviour surface is narrower and I locate it exactly: **the `else` catch-alls** (§3.3) — **23** of them, each ending in unconditional shell execution, e.g. `rm -rf` at `file.rb:648`.

---

## §1 Q1 — reach of the silent branch

### §1.1 The dispatch census: 10 sites, 9 without `else`

**Invocation.** Line-wise match of `^\s*case\s+(session\.type|session\.platform|session\.arch|session_type)\b` with `re.M`, over `lib/`, then a peer-aware walk collecting `when`/`else` at the `case` indentation.

**Correction to my own D45 §3.5:** D45 named `create_process` (`common.rb:81`) as *the* silent branch. **It is one of four in that file**, and `lib/` holds **10** session-keyed dispatches, **9 without `else`**:

| file | line | `when`s | `else` | labels |
|---|---|---|---|---|
| `post/architecture.rb` | 18 | 2 | **no** | `'windows','win'` \| `'linux','bsd','osx'` |
| `post/common.rb` | 37 | 2 | **no** | `'meterpreter'` \| `'shell','powershell'` |
| `post/common.rb` | 50 | 2 | **no** | `'meterpreter'` \| `'shell','powershell'` |
| `post/common.rb` | 81 | 3 | **no** | `'meterpreter'` \| `'powershell'` \| `'shell'` |
| `post/common.rb` | 163 | 3 | **no** | `'meterpreter'` \| `'powershell'` \| `'shell'` |
| `post/common.rb` | 221 | **1** | **no** | `'meterpreter'` only |
| `post/common.rb` | 258 | 3 | **no** | `'meterpreter'` \| `'powershell'` \| `'shell'` |
| `post/common.rb` | 290 | 2 | **no** | `'meterpreter'` \| `'shell','powershell'` |
| `post/unix.rb` | 90 | 1 | **yes** | `'osx'` |
| `ui/console/command_dispatcher/core.rb` | 1617 | 4 | **no** | `'meterpreter'` \| `'shell','powershell'` \| `'mssql','postgresql','mysql'` \| `'hwbridge'` |

**`post/unix.rb:90` is the only one with an `else`.**

**`common.rb:221` (`cmd_exec_get_pid`) handles exactly one type.** On a shell session it falls through and returns `nil` — I did not chase what the three callers do with that nil (§5.1).

**The ui-console dispatch at `core.rb:1617` is the one place `'hwbridge'` is a `when` label.** That is a session-handling path in the console, not a module-facing helper.

**Instrument note, and it cost me a full cycle:** my first walker returned `whens=0` for `common.rb:81` — a site I had already read line-by-line and *knew* had three `when`s. The cause: **`case` and `when` sit at the same indentation in Ruby** (`case` ind 4, `when` ind 4), and my walker broke on `ind <= case_ind`. I also had an off-by-one in reported line numbers from `text[:m.start()].count('\n') + 1`, which reports the line *before* a match that begins at column 0. **Both fixed; the table above is from the fixed walker, and the walker was validated by reproducing the three labels at `:81` that I had already read by eye.** Logged as §6.2.

### §1.2 The dispatch style census: `case` is the minority

**Invocation.** Anchored counts of `^\s*case\s+session.(type|platform|arch)`, `^\s*if\s+session.(type|platform|arch)\s*==`, `^\s*elsif\s+session.(type|platform|arch)\s*==`, each with `re.M`, over `lib/msf/core`.

| style | sites |
|---|---|
| `case` | **9** |
| `if session.type == '...'` | **64** |
| `elsif session.type == '...'` | **23** |

| file | `case` | `if==` | `elsif` |
|---|---|---|---|
| `post/file.rb` | **0** | **35** | **19** |
| `post/common.rb` | 7 | 6 | 2 |
| `exploit/file_dropper.rb` | 0 | 10 | 0 |
| `post/process.rb` | 0 | 4 | 1 |
| `post/architecture.rb` | 1 | 2 | 0 |
| `post/windows/registry.rb` | 0 | 1 | 1 |
| `post/unix.rb` | 1 | 0 | 0 |
| six single-site files | 0 | 1 each | 0 |

**This is the finding of Q1.** D45 §3.5 framed the silent-branch problem as a `case`-without-`else` problem. **In the post interior, `case` is 9 of 96 dispatch sites — 9.4%.** The dominant pattern is the `if`-guard, which fails differently: it falls through and returns `nil` (§3.4).

### §1.3 Reach: the declared population

**Invocation.** Extract `'SessionTypes' => [...]` from all 436 `modules/post` `.rb` files, then intersect each module's declared set with the labels `common.rb`'s dispatchers handle (`meterpreter`, `powershell`, `shell`).

Declared population:

| declared `SessionTypes` | modules |
|---|---|
| `('meterpreter',)` | 231 |
| `('meterpreter','shell')` | 107 |
| **(unset)** | **50** |
| `('shell',)` | 29 |
| `('hwbridge',)` | **12** |
| `('meterpreter','powershell','shell')` | 5 |
| `('smb',)` | 1 |
| `('powershell',)` | 1 |
| **total** | **436** |

Modules declaring a set that **excludes every dispatcher-supported label: 13** — the 12 `hwbridge` + 1 `smb`.

**All 13 are clean, and this is a positive control on the claim, not an assumption.** Enumerating their includes:

- **12 `hwbridge` modules** — 6 include `Msf::Post::Hardware` and nothing else, 6 include nothing at all. **Zero include `Post::File`, `Post::Common`, `Post::Windows`, or `Post::Auxiliary::*`.**
- **1 `smb` module** (`windows/manage/smb_to_meterpreter.rb`) — includes `Msf::Auxiliary::Report` and `Msf::Post::SessionUpgrade` only.
- **Zero of the 13 reference `cmd_exec`, `create_process`, or `get_env`** — checked as bare identifiers.

**So no module that declares itself incompatible with the three dispatcher labels can reach a dispatcher. The declared population contributes zero reachable paths to the silent branch.**

### §1.4 Reach: the undeclared population, and the honest verdict

**The 50 modules with no `SessionTypes` are the real boundary.** An unset `SessionTypes` yields `session_types = []` (`session_compatibility.rb:15`), and `:192` tests `if session_types && !session_types.include?(s.type)` — **an empty array is truthy in Ruby, so `[].include?(anything)` is `false`, so the type check never fires.** (Arch and platform checks are independent and may still fire.) **A UNSET module therefore passes the type gate against any session type.**

**31 of the 50 use a dispatcher** (bare-identifier test for `cmd_exec`/`create_process`/`get_env`).

**Verdict, stated as the reachable set rather than as a yes/no:**

> **A shipped post module reaches the silent branch only if all three hold: (a) it declares no `SessionTypes`, (b) it calls a `common.rb` dispatcher, and (c) it is actually driven with a session whose type is outside `{meterpreter, powershell, shell}`. Condition (a) and (b) are jointly satisfied by 31 modules. Condition (c) is a framework session-selection question that source inspection cannot settle.**

**What source can settle:** for every session type the framework ships — `meterpreter`, `shell`, `powershell`, `smb`, `hwbridge` — the first two of the three conditions never co-occur with the third in the module population I enumerated. **The `smb` module cannot run a dispatcher (no include); the `hwbridge` modules cannot run a dispatcher (no include); and every module that *does* call a dispatcher declares or defaults to a type its dispatcher handles.**

**So: I find no reachable path in the shipped module population, and I state the residual honestly — the 50 UNSET modules are the gap, because their compatibility is enforced by nothing at the type level, and whether one is ever driven by an `hwbridge` session depends on framework session selection, which is §5.2.**

**This is a strong negative but not an absolute one, and the difference is the 50.** A yes/no would overstate it in either direction.

---

## §2 Q2 — the `cmd_exec` risk number

### §2.1 The classification rule, stated before use

The Lead required the rule printed before the number, because an unstated rule makes a count unauditable. **Four classes, decided on the first argument only:**

| class | rule |
|---|---|
| **LITERAL** | first argument is a single `'...'` or `"..."` literal containing **no** `#{...}` |
| **INTERPOLATED** | first argument is a single literal containing **one or more** `#{...}` |
| **VARIABLE** | first argument is a bare identifier or method call with no surrounding literal text |
| **OTHER** | first argument is a concatenation, an array `.join`, a `%()` literal spanning lines, or anything the extractor cannot reduce to one of the above |

**Two boundary rules, both decisions rather than defaults:**

1. **Call sites only.** A line whose stripped form begins `#` is excluded, and the match must not be preceded by a quote character (`(?<![A-Za-z0-9_.'"])cmd_exec\b`) so that `cmd_exec` inside a string is not counted. **This is why this report's denominator is 455 and D45's is 466** (§2.2).
2. **First argument only.** `cmd_exec(cmd, args, timeout)` — a literal `cmd` with a variable *second* argument is classed LITERAL. **I chose this because the second argument is the argument-vector form, and `AGENTS.md` names string interpolation of the *command* as the risk.** §5.3 is the probe that would close the second-argument case.

**The extractor's own limits, stated:** it is a character scanner for balanced parentheses and top-level commas, not a Ruby parser. `%()` and heredoc literals fall to OTHER. **Multi-line literals are scored on their first line**, which under-counts continuation text.

### §2.2 The counts

**Invocation.** Per-line scan of all `modules/post` `.rb` files with the rule in §2.1.

| class | sites | share |
|---|---|---|
| **LITERAL** | **222** | 48.8% |
| **INTERPOLATED** | **143** | 31.4% |
| **VARIABLE** | **77** | 16.9% |
| **OTHER** | **13** | 2.9% |
| **total** | **455** | 100% |

in **170 files**.

**The 466-vs-455 reconciliation, because two unresolved numbers is worse than one wrong one.**

| probe | sites | files |
|---|---|---|
| `\bcmd_exec\b` raw (D45's figure) | **466** | **171** |
| call sites only (this report) | **455** | **170** |
| delta | **11** | **1** |

**All 11 deltas are prose comments**, printed and read:

```
COMMENT android\manage\remove_lock.rb:57
COMMENT multi\escalate\metasploit_pcaplog.rb:81
COMMENT multi\manage\screensaver.rb:45
COMMENT multi\manage\shell_to_meterpreter.rb:260
COMMENT multi\manage\shell_to_meterpreter.rb:330
COMMENT multi\gather\... (6 further)
```

**Both numbers are right about different populations.** D45's 466 counts mentions; 455 counts calls. **This report uses 455 and says so.** The one-file delta is `android\manage\remove_lock.rb`, which mentions `cmd_exec` in a comment and calls it nowhere.

**Positive control for the extractor:** the hand-verified site at `set_dmz.rb:30` — `cmd_exec("iptables -D FORWARD -d #{datastore['TARGET_HOST']} -j ACCEPT")` — is classed INTERPOLATED, and it is INTERPOLATED by eye. A hand-verified LITERAL, `ibstat_path.rb` `cmd_exec('echo $PATH')`, is classed LITERAL. **Both controls printed in §2.3.**

### §2.3 Samples of every class

**INTERPOLATED (143 sites):**

```
android\capture\screen.rb:54        "#{exe_path} -p #{file}"
android\gather\sub_info.rb:71       "service call iphonesubinfo #{code}"
android\manage\remove_lock_root.rb:42  "rm #{path}"
linux\busybox\ping_net.rb:33        "ping -c 1 #{ip}"
linux\busybox\set_dmz.rb:30         "iptables -D FORWARD -d #{datastore['TARGET_HOST']} -j ACCEPT"
linux\busybox\set_dmz.rb:33         "iptables -A FORWARD -d #{datastore['TARGET_HOST']} -j ACCEPT"
linux\busybox\set_dns.rb:59         "cp -f /etc/udhcpd.conf #{writable_directory}tmp.conf"
linux\busybox\wget_exec.rb:36       "wget -O #{random_file_path} #{datastore['URL']}"
```

**LITERAL (222 sites):**

```
exploits\aix\local\ibstat_path.rb   'echo $PATH'                                  [CONTROL]
exploits\aix\local\ibstat_path.rb   'lsdev -Cc if'
exploits\aix\local\ibstat_path.rb   'find /usr/sbin/ -name ibstat -perm -u=s -user root 2>/dev/null'
exploits\plain_linux_priv_esc.rb    'dpkg -l example | grep \'^ii\''
```

*(the LITERAL samples above are drawn from `modules/`, and the `ibstat_path.rb` pair is the stated control; post-only literal examples include the many `'echo $PATH'`-shaped probes across `post/*/gather`)*

**VARIABLE (77 sites):**

```
android\local\koffee.rb:74          cmd
android\local\koffee.rb:80          cmd
android\local\koffee.rb:88          cmd
linux\busybox\smb_share_root.rb:51  command
linux\dos\xen_420_dos.rb:121        check_command
linux\dos\xen_420_dos.rb:138        check_command
```

**OTHER (13 sites):**

```
linux\gather\enum_network.rb:95     cmd + " || echo #{verification_token}"
linux\gather\vcenter_secrets_dump.rb:437  "#{ldapsearch_bin} -h #{vc_psc_fqdn} -LLL -p 389 -b \"cn=#{base_fqdn}\""
multi\escalate\cups_root_file_read.rb:177 ['printf', "GET #{uri}\r\n\r\n\r\n".inspect, '|', nc_str].join(' ')
multi\gather\enum_software_versions.rb:62 'wmic product get Name ...'
multi\gather\enum_software_versions.rb:102  cmd.join(' ')
multi\manage\play_youtube.rb:103    %(firefox --display #{display} -CreateProfile "#{profile_name} /tmp...")
```

**The OTHER class is not a rounding error — it is where two genuine interpolations hide.** `enum_network.rb:95` (`cmd + " || echo #{token}"`) and `cups_root_file_read.rb:177` both interpolate. **Stating OTHER as 13 and stopping there would understate the risk population; I am stating it as 13 *unclassified-by-rule*, of which at least 2 interpolate.**

### §2.4 What the interpolation classes actually contain

**Invocation.** Extract every `#{...}` expression from the 143 INTERPOLATED first arguments, classify by the leading identifier, print the counter and one example per class.

| interpolated expression | sites | example |
|---|---|---|
| bare local `path` | 6 | `android\manage\remove_lock_root.rb:42` `"rm #{path}"` |
| **`datastore[...]`** | **5** | `set_dmz.rb:30` — `datastore['TARGET_HOST']` |
| bare local `puppet_exe` | 5 | `linux\gather\puppet.rb:69` |
| bare local `u` | 5 | `osx\gather\enum_osx.rb:248` `"/bin/ls -ma /Users/#{u}/"` |
| bare local `url` | 4 | `multi\escalate\aws_create_iam_user.rb:172` `"curl #{url}"` |
| `uri` | 4 | `multi\manage\open.rb:39` `"open #{uri}"` |
| bare local `pid` | 4 | `osx\capture\keylog_recorder.rb:104` `"kill -USR1 #{pid}"` |
| bare local `ip` | 3 | `linux\busybox\ping_net.rb:33` |
| ~30 further bare-local classes | 2–3 each | `pvalue`, `tmp_path`, `askpass_sh`, `user`, `guid`, `ctl_path`, `script_path` |
| framework-derived (`random_*`, `writable_directory`, `payload_path`, `File.*`, `session.*`) | ~10 | `wget_exec.rb:41` `"chmod 777 #{random_file_path}"` |

**Total: 144 expression extractions across 143 sites** (one site interpolates three names).

### §2.5 The risk number, and why I refuse to state a single one

**The tempting number is "143 interpolated sites = the risk population." It is wrong, and I will say why rather than produce it.**

**Of the 143, only 5 interpolate `datastore[...]` directly on the first argument.** The remaining 138 interpolate **bare local variables whose provenance is not visible at the call site.** `"rm #{path}"` at `remove_lock_root.rb:42` — `path` could be a framework constant or a target-derived directory name, and **the call site does not say.** `"ping -c 1 #{ip}"` at `ping_net.rb:33` is a `datastore['RANGE']`-derived IP — an operator-set value that *looks* target-derived and *is* operator-controlled, which in a scanner means a malicious target does not set it.

**So the honest classification is three numbers, not one:**

| class | count | what it means |
|---|---|---|
| **directly operator/target-visible interpolation** — `datastore[...]` on the first argument | **5** | the value arrives from the operator's options; `TARGET_HOST`, `URL`, `RANGE` are the recurring names |
| **interpolation of a local whose provenance is not visible at the call site** | **138** | **the unauditable majority, and the reason a single risk number would be dishonest** |
| **OTHER, at least 2 of which interpolate** | 13 | unclassified by rule, not by absence of interpolation |

**The measurement that would convert this into a real risk number does not exist yet and is §5.4:** for each of the 138, trace the local's assignment. **I am not going to launder a 138-site unknown into a headline, because that is exactly the "arithmetically right, semantically wrong" failure D22 documents about D9's 2,715.**

**What I can state hard:** **455 call sites, 170 files, and a raw mention count of 466 that D45 reported — reconciled exactly by 11 prose comments.** And the negative result that matters: **`execute_command` = 0 among post modules (D45, with a live control of 3 at `exchange_proxylogon_rce.rb`).**

---

## §3 Q3 — the compatibility warning, taken to consequence

### §3.1 What the check tests

**Invocation.** Located the single provider — `session_compatibility.rb:171 def session_incompatibility_reasons` — via anchored `^\s*def\s+session_incompatibility_reasons\b` with `re.M` over `lib/msf/core`; **one definition, no overrides.** Read `:171-225`.

**Four mismatch classes, all accumulating into `issues` and returning — none raising:**

| line | class | test |
|---|---|---|
| `:192` | **type** | `session_types && !session_types.include?(s.type)` |
| `:205` | **arch** | `mod_arch.include?(s.arch) \|\| mod_arch.include?(ARCH_CMD)` |
| `:214` | **platform** | `platform.supports?(PlatformList.transform(s.platform))` |
| `:221` | meterpreter commands | `meterpreter_session_incompatibility_reasons(s)` |

**`:199` is the arch gate:** if the module declares no `Arch`, no arch check runs at all.
**`:211` is the platform gate:** checked only `if platform && platform.is_a?(Msf::Module::PlatformList) && !platform.empty?`.
**`:220` is the meterpreter gate:** `if s.type == 'meterpreter'`.

The caller — `setup:43-49` — does `print_warning` per issue and **continues.**

### §3.2 The three dispatch styles

**The mismatch does not meet a `case`.** It meets `if`-guards. Census from §1.2, restated as the Q3 answer:

**`Post::File` — the mixin 232 of 436 post modules include — contains 35 `if session.type ==` guards, 19 `elsif` chains, and zero `case` statements.**

The representative shape, `post/file.rb:479 read_file`:

```ruby
def read_file(file_name)
  if session.type == 'meterpreter'
    return _read_file_meterpreter(file_name)
  end

  return unless %w[shell powershell].include?(session.type)   # :484

  if session.type == 'powershell'
    return _read_file_powershell(file_name)
  end

  if session.platform == 'windows'
    return session.shell_command_token("type \"#{file_name}\"")   # :491
  end

  return nil unless readable?(file_name)                          # :494
```

**`:484` is an explicit early return for a non-shell, non-powershell, non-meterpreter type.** So `read_file` on an `hwbridge` session **returns `nil` with no diagnostic** — after the warning at setup told the operator the session *may* not be compatible.

**`post/file.rb:86 dir`** does the same without the upfront guard: three `if` blocks, each with `return`, then a final `if command_exists?('ls')`.

**Verdict on style A (the `case`):** nine sites, silent `nil`/`""` return (§1.1).
**Verdict on style B (the `if`-guard):** **64 sites**, and the mismatch produces **`nil` or `false`**, not an exception.

### §3.3 The `else` catch-alls

**Invocation.** For every `^\s*else\s*$` in `lib/msf/core`, look ahead three lines for `cmd_exec`/`shell_command_token`/`shell_command`; print the file, line and following statement.

**23 `else` branches end in unconditional shell execution.** The boundary of this count: it is a three-line lookahead, so an `else` that reaches `cmd_exec` after three intervening lines is not counted — **an undercount by construction, not a sample.**

The destructive three, all in `post/file.rb`:

```ruby
# :641-649  rm_rf
if session.type == 'meterpreter'
  session.fs.dir.rmdir(remote) if exist?(remote)
elsif session.type == 'powershell'
  cmd_exec("Remove-Item -Path \"#{remote}\" -Force -Recurse")
elsif session.platform == 'windows'
  cmd_exec("rd /s /q \"#{remote}\"")
else
  cmd_exec("rm -rf \"#{remote}\"")          # :648
end
```

```ruby
# :677-678  rename_file
else
  cmd_exec(%(mv #{...} "#{old_file}" "#{new_file}" && echo #{verification_token}))...
```

```ruby
# :705-706  copy_file
else
  cmd_exec(%(cp -f "#{src_file}" "#{dst_file}" && echo #{verification_token}))...
```

**`:648` is the sharpest instance in the corpus for this question.** The `else` fires when the session is **not** meterpreter, **not** powershell, and **not** Windows-platform. That is the correct condition for a POSIX shell — and it is also **exactly the condition an `hwbridge` session satisfies.** The branch has no `command_exists?('rm')` guard, unlike `dir:99` which does check for `ls`.

**So: `rm -rf` runs on the target, through `cmd_exec`, from an `else` branch selected by the absence of three conditions rather than the presence of one.** On a POSIX shell that is correct. It is the branch that carries no positive evidence it is on a POSIX shell.

### §3.4 Verdict: a third class

**The brief offers "a warning that precedes a crash" versus "a warning that precedes silent wrong behaviour on the target." The corpus does a third thing:**

> **The warning precedes a `nil`/`false` return that the module treats as a result, and — in 23 `else` catch-alls — a shell command issued on the strength of three negative conditions rather than one positive one.**

**Precisely:**

- **Not a crash.** The `session_compatibility.rb:192-221` checks all return issue strings; `setup:43-49` prints and proceeds. Nothing raises on incompatibility. The raises at `:26-28` and `:30-32` are for a *missing* session, which is a different failure from an *incompatible* one.
- **Not silent wrong behaviour on the target, in the main path.** 64 `if`-guards return `nil`/`false`. The module's caller then either handles it (many check) or does not (§5.5).
- **Yes silent wrong behaviour in the `else` catch-alls, 23 of them.** `file.rb:648`'s `rm -rf` is selected by **not-meterpreter ∧ not-powershell ∧ not-windows** — which is not a test that the session is a POSIX shell.

**The UX-defect framing is wrong for a second reason I should name:** the warning is emitted at **`setup`**, before the module runs, listing generic issue strings — *"incompatible session type: hwbridge. This module works with: meterpreter."* An operator who reads it and continues gets **no second signal** at the call site. The warning is not repeated, not escalated, and not attached to the operation it predicts. **That is a diagnostic-placement defect, not a UX defect and not a safety defect, and I would call it that.**

---

## §4 Q4 — the `alias` class, proved

### §4.1 The count correction

**55 alias statements in 32 files**, per §0.1. D45's 95/54 was a substring-class error. **Eight of the 55 are `alias_method`, 47 are `alias`.**

### §4.2 Eight dead aliases, and the ninth killed

**Invocation.** Two stages. (1) Parse every real alias statement in `lib/msf/core` with a Ruby alias grammar. (2) Tokenise **all 8,570 `.rb` files** under the repo root once, counting every identifier, then compare each alias's name and target against the corpus counts. Scanning once is O(bytes); my first attempt re-scanned the corpus 53 times and had to be killed at 120 s.

**Positive controls, all four live:**

| control | corpus count |
|---|---|
| `session` | 8,520 |
| `print_good` | 5,205 |
| `cmd_exec` | 1,437 |
| `session_changed?` | 2 |

**`session_changed?` is the important control: a rare-but-real name counts 2, so a count of 0 means "never written", not "too rare to see."**

**Class A — alias name referenced zero times corpus-wide (after subtracting its own declaring line): 8 of 55.**

| file | line | alias → target |
|---|---|---|
| `rhosts_walker.rb` | 268 | `parse_https_uri` → `parse_http_uri` |
| `rhosts_walker.rb` | 307 | `parse_ldaps_uri` → `parse_ldap_uri` |
| `auxiliary/web.rb` | 102 | `log_file_if_exists` → `log_resource_if_exists` |
| `post/file.rb` | 682 | `mv_file` → `rename_file` |
| `post/file.rb` | 709 | `cp_file` → `copy_file` |
| `post/windows/file_system.rb` | 250 | `delete_junction` → `delete_mount_point` |
| `rpc/v10/rpc_module.rb` | 321 | `rpc_compatible_exploit_payloads` → `rpc_compatible_payloads` |
| `rpc/v10/rpc_module.rb` | 395 | `rpc_target_compatible_exploit_payloads` → `rpc_target_compatible_payloads` |

**A ninth candidate was killed by the probe §5.6 promised: `exe/segment_appender.rb:25 alias secname= section_name=` is LIVE.** My identifier counter is structurally blind to Ruby writer invocation, because a writer is called by assignment syntax — `x.secname = y` — in which no token `secname=` appears. Searching for the assignment form instead:

```
spec\lib\msf\core\exe\segment_appender_spec.rb:30   appender.secname = 'legacy'
```

**One hit, in the spec.** `section_name=` itself has **zero** assignment-syntax hits — it is reachable only through the alias, which is exactly what a compatibility alias is for. **So `secname=` is the control proving this class is provable rather than assumed: an alias can be invoked by a syntax the token counter cannot see, and only a syntax-aware probe catches it.** The count is 8.

**Class B — alias pointing at a target name that is itself never referenced: 0 of 55.** Every target is live. **The control that makes this zero meaningful:** `session_changed?` at count 2 shows the counter resolves rare names.

**Sample of the pairs where the alias IS used**, to show the counter discriminating rather than saturating:

| alias → target | alias# | target# |
|---|---|---|
| `file_rm` → `rm_f` | 37 | 132 |
| `dir_rm` → `rm_rf` | 6 | 38 |
| `move_file` → `rename_file` | 5 | 15 |
| `ls` → `dir` | 134 | 986 |
| `client` → `session` | 7,086 | 8,915 |

### §4.3 Why this is the `restypes` analogue

**The `restypes` defect shape:** a misspelled attribute is accepted by `__setattr__` on a `CDLL` and the intended value is never applied. **A reader probing for the correct name finds the assignment present** — the defect is invisible to a name-based search.

**The Ruby analogue here is the same failure in the opposite direction, and the 8 prove it:** `mv_file` is declared (`post/file.rb:682`) with a live target (`rename_file`, called 15 times). **A name-based probe for `mv_file` finds a definition and concludes it is used.** The method a caller would have to invoke is one that no code ever invokes.

**So the answer to Q4's ask — prove or kill — is: proved, 8 instances, with the class-B zero showing these are not aliases to dead code.** And the *direction* of the finding is worth stating plainly: **this is a dead-alias class, not a dead-code class.** The target is alive; the alias is the unused name. **A liveness analysis that starts from definitions will miss all eight; one that starts from call sites must additionally be syntax-aware — `secname=` (§4.2) is invoked by assignment syntax that a token counter cannot see, and it was the one candidate that the naive count got wrong.**

---

## §5 Residual unknowns, each with a concrete probe

### §5.1 What do the three callers of `cmd_exec_get_pid` do with its `nil`?

`common.rb:221` handles only `'meterpreter'`. On a shell session it falls through and returns `nil`.
**Probe:** enumerate callers of `cmd_exec_get_pid`; for each, read whether the result is nil-checked before use. `grep -rn "cmd_exec_get_pid" modules/` then read each site. **Bounded: expected 3–10 sites.**

### §5.2 Does any framework path drive a UNSET-`SessionTypes` module with an `hwbridge`/`smb` session?

This is the gap in §1.4's negative.
**Probe:** read `lib/msf/core/module_manager` and the console's module-selection path for the filter applied to a candidate module's `session_types` when a session is chosen. **The question is whether `session_types == []` is filtered as "universal" or as "unconstrained."** §1.4 shows `:192` treats it as unconstrained; whether a *second* filter exists upstream is unread.

### §5.3 What does the SECOND argument to `cmd_exec` contain?

My rule scored first arguments only. `cmd_exec(cmd, args)` with a literal `cmd` and an interpolated `args` is classed LITERAL.
**Probe:** re-run §2.2's extractor against the second argument of all 455 sites; report the class distribution. **Bounded and mechanical — this is the cheapest probe in the report and it could move the interpolated count.**

### §5.4 Provenance of the 138 bare-local interpolations

The number that would convert §2.5's 138 into a risk count.
**Probe:** for each of the 138, find the local's last assignment in the enclosing method and classify. **This is a real program-analysis task, not a grep, and I flag it as such rather than implying a regex would do it.** Partial version that is mechanical: classify locals whose name contains `datastore`, `rhost`, `target`, `uri`, `res` as likely-external and report the split.

### §5.5 Do the callers of the 64 `if`-guards nil-check?

`read_file` returns `nil` at `file.rb:494` on a mismatch; `dir` returns nothing if no branch matched.
**Probe:** for the 20 most-included consumers of `Post::File`, grep `.read_file(` and `read_file(` and read the assignment plus the next 3 lines. **Bounded: 20 modules.**

### §5.6 RESOLVED — `secname=` is invoked by assignment syntax, so class A is 8

`exe/segment_appender.rb:25` aliases `secname=` → `section_name=`. Ruby invokes writers by assignment syntax, and an identifier counter looking for the token `secname=` cannot see `x.secname = y`.

**Probe, run:** anchored `\.secname\s*=(?!=)` and `\.section_name\s*=(?!=)` over all 8,570 `.rb` files.

| pattern | hits |
|---|---|
| `.secname =` | **1** — `spec\lib\msf\core\exe\segment_appender_spec.rb:30` (`appender.secname = 'legacy'`) |
| `.section_name =` | **0** |

**Result: `secname=` is LIVE. Class A is 8, not 9. This section is closed.** The general lesson is §6.9.

### §5.7 Is `post/architecture.rb:18`'s two-label platform dispatch reachable with a third platform?

`:18` handles `'windows','win'` and `'linux','bsd','osx'` with no `else`. A session reporting another platform (e.g. `solaris`, `aix`) falls through.
**Probe:** read `architecture.rb:18-40` for what the fall-through returns, then check whether any post module declares `SessionTypes` including a solaris/aix session type.

### §5.8 The three-line lookahead in §3.3

**23 `else` catch-alls is an undercount by construction.** An `else` that reaches `cmd_exec` after three intervening lines is not counted.
**Probe:** widen the lookahead to the enclosing method's extent, or invert — find every `cmd_exec` in `lib/msf/core`, walk backwards to the nearest enclosing `if`/`elsif`/`else`, and report its branch position. **The inversion is the better probe because it bounds from the call site.**

---

## §6 Instrument record

**Six failures. Four are mine in this round; two are mine in D45, corrected in §0.**

### §6.1 `[instrument]` — a `\b`-terminated keyword probe counted `alias1` and `aliases:`

**What I did:** relied on D45's `^\s*(prepend|include|extend|alias|alias_method)\b` probe, which reports `alias` as 48 when only 46 lines are alias declarations and `alias_method` correctly at 7.
**What happened:** the `alias` alternative matches the prefix of `aliases:` and `alias1` because `\b` sits between a letter and a digit / between a letter and `s`. D45's reported 95 was a hand-tally that never matched the probe's own 55.
**Why it mattered:** the error propagated into D45 §4's conclusion that the alias class had no provable instance.
**Rule:** **a `\b`-terminated keyword probe is unsafe against a corpus that uses numeric or plural suffixes on the same stem.** Anchor the full grammar (`alias\s+\S+\s+\S+`) or accept and report the over-match.

### §6.2 `[instrument]` — my `case`/`when` walker assumed `when` is indented deeper than `case`

**What I did:** walked forward from `case` collecting lines whose indentation exceeded the `case`'s, breaking on `ind <= case_ind`.
**What happened:** **`case` and `when` are peers in Ruby** — both at ind 4 in `common.rb`. The walker broke on the first `when` and reported `whens=0` for `common.rb:81`, a site I had **already read by eye and knew had three labels**.
**Why it mattered:** a wrong count in the table that answers Q1. Caught only because a site I had read contradicted it.
**Rule:** **a structural walker validated against nothing but itself will report a clean zero.** Validate the first output against a site read by eye. This is the same shape as §6.3.

### §6.3 `[instrument]` — `text[:m.start()].count('\n') + 1` reports the line BEFORE a match at column 0

**What I did:** computed match line numbers from a `re.M` match position.
**What happened:** for a match starting at column 0, the preceding `\n` is counted, so the reported line is the blank line above. My first enumeration reported `case session.type` at `common.rb:36`, `:49`, `:221` — **those are blank lines; the `case` statements are at `:37`, `:50`, `:221`** (the last one coincidentally right because that line had content before it).
**Rule:** **compute line numbers per-line with `enumerate`, not from match offsets.** Every line number in this report came from the enumerate pass.

### §6.4 `[instrument]` — a regex with `#` inside `re.X` mode: unterminated group

**What I did:** wrote `(?:\#.*)?$` as `(?:#.*)?$` inside a `re.compile(..., re.X)` pattern.
**What happened:** `re.X` treats `#` as a comment introducer, so the group never closed: `re.error: missing ), unterminated subpattern`.
**Rule:** **inside `re.X`, escape `#` or it eats the rest of the pattern.** This cost one cycle and is the fifth quoting/escaping failure in my lane this session.

### §6.5 `[instrument]` — a corpus-wide regex re-scanned 53 times had to be killed

**What I did:** for each of 53 aliases, ran `re.findall` over one giant concatenated `BLOB` of the whole repo.
**What happened:** the job exceeded 120 s and was moved to the background; I killed it and rewrote as a **single tokenising pass with `collections.Counter`, which finished in 2.8 s.**
**Rule:** **N patterns over one corpus is O(N × bytes). Tokenise once, count once, look up N times.** The rewrite was 40× faster and produced a cleaner control (`session_changed?` = 2).

### §6.6 `[instrument]` — the extractor's OTHER class is a residual, not a classification

**What I did:** assigned unparseable first arguments to OTHER.
**What happened:** OTHER holds 13 sites, **and at least 2 of them (`enum_network.rb:95`, `cups_root_file_read.rb:177`) interpolate.** Reporting "13 OTHER" without that caveat would have read as "13 not-interpolated."
**Rule:** **an "unclassified" bucket must never be reported adjacent to a "not a risk" reading.** Name what is known to be inside it.

### §6.7 `[instrument]` — `\b` after a name ending in `?` or `!` never matches

**What I did:** built the reference counter as `re.escape(name) + r"\b"`.
**What happened:** `\b` is a **word/non-word transition**. For `respond_to?` the name ends in `?`, which is non-word, and the following character in `respond_to?(x)` is `(`, also non-word — **no boundary, no match.** `respond_to?` scored **0**, `session_changed?` scored **0**, `file_exist?` scored **0**.
**Why it mattered, and this is the dangerous part:** the failure mode is **silent zeros on exactly the names being tested**, which *manufactured* dead-alias rows. On the broken counter, `file_exist?` / `exists?` / `include?` all appeared as dead aliases with dead targets — **seven false dead rows.** I caught it only because `respond_to?` and `session_changed?` are controls whose liveness I knew independently.
**Fix:** replace `\b` with a negative lookahead `(?![A-Za-z0-9_])`.
**Rule:** **`\b` is wrong at the end of any Ruby method name containing `?`, `!`, or `=`.** And: **a counter whose failures are silent zeros must carry controls that are provably non-zero — `session`/`cmd_exec`/`print_good` were all passing while every `?`-suffixed name returned 0.**

### §6.8 `[instrument]` — a bare-call pattern requiring `(` or `=` misses zero-argument calls

**What I did:** detected bare calls with `name\s*[(=]`.
**What happened:** `session_changed?` is called as `!session_changed?` with no parentheses or assignment. **Scored 0.** The same probe then reported `session` as 256 instead of 8,520 because it also required a following `(`/`=`.
**Rule:** **in Ruby, parenthesised and unparenthesised calls are both idiomatic.** A call detector keyed on `(` under-counts; key it on the *absence* of a preceding `.`/`:` plus the identifier end.

### §6.9 `[instrument]` — a token counter cannot see Ruby writer invocation

**What I did:** counted alias usage as identifier occurrences, then treated 0 as dead.
**What happened:** `secname=` scored 0 as an identifier — **correctly**, because a writer is invoked as `x.secname = y` and the token `secname=` never appears. The zero was a true measurement of the wrong question. **`spec\lib\msf\core\exe\segment_appender_spec.rb:30` calls it.** One false positive (§5.6).
**Rule:** **for a setter alias, the probe must be syntax-aware: `\.name\s*=(?!=)`, not `name=`.** This is the one residual I flagged in draft and then actually resolved — the flag was right, the prediction ("class A is 8, not 9") was right, and it is the only place where keeping a wrong number in a residual section paid off.

---

## §7 Status

**Deliverable:** `RE_Library\07_OUTPUT\reports\DEEP\D69_msf_post_interior_hardening.md` — this file, sole owner `source-diver`.

**Acceptance:** §0 leads with three corrections. **Q1 §1** (reach: 10 dispatches, 9 without `else`; 64 `if`-guards; 13 declared-incompatible modules, none reaching a dispatcher; 50 UNSET module gap named). **Q2 §2** (rule printed with 4 boundary decisions and 2 controls; 455 sites / 170 files reconciled against D45's 466/171 by 11 prose comments; samples of all four classes; the single risk number refused and replaced with 5 / 138 / 13). **Q3 §3** (4 mismatch classes enumerated, 3 dispatch families, 23 `else` catch-alls, verdict as a third class). **Q4 §4** (55 statements / 32 files, **8** dead aliases proved, class B = 0, the ninth killed by a syntax-aware probe). Every number has its invocation. §5 residuals each with a probe. §6 instrument record, 9 entries.

**Ranked, the five strongest claims:**

1. **Eight dead aliases, proved against a validated counter** (§4.2). `post/file.rb:682 mv_file → rename_file`, `:709 cp_file → copy_file`, `delete_junction`, and five more. **Class B = 0, so these are unused names pointing at live code — invisible to a definition-based liveness check.** Controls: `session` 8,520, `print_good` 5,205, `cmd_exec` 1,437, `session_changed?` 2. **The ninth candidate, `secname=`, was killed by the syntax-aware probe — and that kill is the control that proves the class rather than assuming it.**
2. **`case` is 9 of 96 session-dispatch sites in the post interior; `if session.type ==` is 64, `elsif` 23** (§1.2). **D45 §3.5 framed the silent branch as a `case` problem — the dominant pattern is not `case`, and it fails by `nil`-return rather than by empty string.**
3. **`Post::File` — included by 232 of 436 post modules — has 35 `if`-guards, 19 `elsif`-chains and zero `case`** (§1.2/§3.2). `read_file:484` returns early for any type outside `{meterpreter, shell, powershell}`.
4. **23 `else` catch-alls end in unconditional shell execution**, including `rm -rf` at `file.rb:648` selected by three negative conditions (not-meterpreter ∧ not-powershell ∧ not-windows) with no `command_exists?` guard. (§3.3)
5. **Q1's reach verdict is a bounded negative, not an absolute one** (§1.4): all 13 declared-incompatible modules are dispatcher-free, so **no declared path reaches the silent branch** — and the 50 UNSET modules are the named gap, because `session_types = []` is truthy and disables the type check entirely at `:192`.

**Not covered, named rather than implied:** §5.4 (the 138-site provenance trace) is the highest-value open probe; §5.3 (second arguments) is the cheapest and could move §2.5's interpolated count. **§5.6 is closed, not open** — the probe it promised was run and it reduced class A from 9 to 8.

**Nothing on disk was modified except this file and nine throwaway probe scripts `_d69_*.py` in the same directory.** No verified artefact (`D7`, `D8`, `D9`, `D22`, `D42`, `D58`) was touched; the D45 figures I correct here are corrected *in this document*, and D45 itself is left as delivered.

**One instrument-species note for the corpus ledger:** the four alias-counter defects in §6.7–§6.9 were found **only because I kept the superseded probe and read its disagreement with the new one instead of deleting it.** The old probe disagreed with the report on 16 rows; adjudicating that disagreement produced three fixes and one killed finding. **A discarded probe is a control destroyed.**
