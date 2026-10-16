# D85 — MSF operator-data shell reach: escaping census of the interpolated `cmd_exec` population

**Lane:** source-lane RE (read-only, no target).
**Owner:** `source-diver`. **Round 22.**
**Predecessors:** D74 (this lane, round 21) → D69 → D45.
**Status:** complete for T1/T2/T3. Every number carries its invocation. Nothing outside this file was edited.

---

## Table of Contents

- §0 Scope, line convention, and what this file does not touch
- §1 T1 — the escaping census: the number that converts provenance into reach
- §2 T2 — reducing the largest UNRESOLVABLE cause
- §3 T3 — the network-fetch bounded class, and the fourth provenance class it exposed
- §4 Instrument record
- §5 Residual unknowns, each with a probe
- §6 Status

---

## §0 Scope, line convention, and what this file does not touch

**Line-count convention (stated per Lead's constraint).** A "line" is an LF-delimited record. `file.rb:NNN` is the **1-based ordinal of the physical line** in the source file, counting every line including blanks and comments. Where a call spans multiple physical lines, the reported line is the line on which the **`cmd_exec` / `create_process` token** appears. `LF count` for this file is the count of `0x0A` bytes, which equals the number of lines when the file ends with a newline.

**Population of record.** The 131-site / 197-expression population is inherited from D74 with one correction:
- D74 shipped **130 sites / 174 expressions** from `_d74_p7_prov3.py`.
- D85 recomputes **131 sites / 197 expressions** from `_d85_p3_escapecensus.py`.
- **The difference is not drift, it is a defect in D74's resolver that D85 fixes**, and the fix is §2.1 and instrument entry §4.2. D74's site count was **one site short** (`cups_root_file_read.rb:60`) and its expression count was **23 short** because it resolved a 3-token interpolation to its first token only.

**Direction of the correction.** D74's headline was *"62 expressions / 49 sites resolve to operator data."* D85 **confirms the 49** and **finds a defect it did not look for**: **0 of those 49 escape**. The 49 was not generous, as I suspected it might be — it was **accurate and incomplete**, because accuracy about provenance is not accuracy about reach.

**Not touched.** D7, D8, D9, D22, D42, D58, and the two frozen artefacts **D45** and **D69** were not opened for writing. D74 was not edited. Confirmed by the `git status` in §6.

---

## §1 T1 — the escaping census

### §1.1 The rule, stated before application

**Rule (D85-T1).** For each of the 131 interpolated `cmd_exec` call sites, classify every `#{...}` expression into exactly one **escaping** verdict:

| verdict | meaning |
|---|---|
| **ESCAPED** | the interpolated value reaches the shell through an escaping primitive, either inline in the argument or bound to it by a resolvable chain |
| **RAW** | no escaping primitive is present anywhere on the resolvable chain to the value |
| **UNRESOLVABLE_ESC** | the value cannot be traced, so its escaping status cannot be decided |

**The escaping primitive set is derived from the corpus, not from memory.** This matters and it is Rule 20 applied to my own vocabulary: my first census (`_d85_p1_primcensus.py`) listed fifteen primitives **from memory**, and **`.shelljoin` was not among them** — yet `cups_root_file_read.rb:60` uses it. The corrected census (`_d85_p3_escapecensus.py`) enumerates the *family* and lets the corpus decide which members exist:

| primitive family member | occurrences | files |
|---|---|---|
| `shell_command` | 70 | 18 |
| `Rex::Text.decode_base64` | 30 | 21 |
| **`shellescape`** | **13** | **6** |
| `Rex::Text.encode_base64` | 9 | 4 |
| `escape` | 6 | 6 |
| `shellwords` | 4 | 4 |
| **`shelljoin`** | **3** | **3** |
| `sanitize` | 2 | 1 |
| `Shellwords.escape` | 2 | 1 |
| `quote` | 2 | 1 |
| `escaping` | 1 | 1 |

**Rejected from the primitives, with the control that rejected each.** A primitive counts only if it can defeat shell metacharacter interpretation:

| candidate | occurrences | verdict | control |
|---|---|---|---|
| `.encode('UTF-16LE' / 'UTF-16be')` | 76 | **NOT an escaper** | read sites: `ad_to_sqlite.rb:104-170` (DB column conversion), `zip.rb:109` (file write). **Character encoding, not shell quoting.** |
| `.inspect` | 29 | **NOT an escaper** | quotes for Ruby display; the quotes are the defect, not the fix |
| `Rex::Text.decode_base64` | 30 | **NOT an escaper** | it **decodes**; a decoder is the opposite direction |
| `CGI.escape`, `URI.encode` | 0 | absent | `[absence]`; positive control: `.gsub` = 274 occurrences, so the scanner sees method calls |
| `escape_single_quotes`, `escape_double_quotes` | 0 | absent | `[absence]` |
| `Rex::Text.encode_base64` | 9 | **escaper by alphabet** | base64's alphabet excludes every shell metacharacter, so it defeats injection **as a side effect of its alphabet, not by design** |

**Instrument failure caught here.** The uncorrected pattern `.encode` reported **76 occurrences / 9 files**, which would have entered the census as a large escaping surface. **The true count of `.encode` sites that escape for a shell is 1** (`sonic_pi.rb:132`, base64-into-`echo | base64 -D`). The other 75 are character-set conversions. **Recorded in §4.1.**

### §1.2 The escaping test, and the line-scope error it exposed

My first test (`_d85_p5_esctest.py`) searched for an escaping primitive **inside the argument text only**, over all 131 sites. Result: **ESCAPED 2 / RAW 129.**

I did not ship it, because the primitive census contradicted it. The census shows **13 `shellescape` occurrences and 3 `shelljoin`**, but the same-line test could only find two. Re-reading every occurrence by eye explained the gap — **the corpus escapes on the previous line**:

```ruby
# modules/post/osx/capture/screen.rb
     45|     file_type = datastore['FILETYPE'].shellescape
     46|     exe_path  = datastore['EXE_PATH'].shellescape
     47|     tmp_path  = datastore['TMP_PATH'].gsub('<random>', Rex::Text.rand_text_alpha(8)).shellescape
...
     76|     ... cmd_exec("... #{exe_path} ... #{file_type} ...")
```

**Sixteen of the eighteen escaping occurrences bind into a variable, not into the argument.** A same-line escaping test therefore measures the wrong thing, and it would report `2 of 131 escaped` — a number that would have been read as *"almost nothing escapes"* when the truth is *"escaping happens one line up and is invisible to this test."*

**This is the D74 `puppet_exe` shape, relocated.** In D74 the lesson was that a bare local is not an unknown but an untraced value. Here: **an unescaped argument is not necessarily an unescaped value.**

### §1.3 The corrected test: escaping through the chain

`_d85_p6_esctrace.py` points D74's resolver at a new predicate — *does an escaping primitive appear anywhere on the resolution chain to this value* — and prints the chain for every hit.

**Result over 197 interpolated expressions:**

| verdict | expressions | share |
|---|---|---|
| **NOT_ESCAPED** | **182** | 92.4% |
| **ESCAPED** | **15** | 7.6% |

**The 15 escaped expressions, with their chains.** Every chain is printed so the classification is checkable:

| site | token | chain |
|---|---|---|
| `multi/gather/unix_kerberos_tickets.rb:91` | `file_pattern` | `assign L89: Shellwords.escape(file_pattern)` |
| `osx/capture/keylog_recorder.rb:104` | `pid` | `assign L95(run_ruby_code) -> def run_ruby_code body carries escaper` |
| `osx/capture/keylog_recorder.rb:134` | `pid` | `kill_process(pid) -> assign L95(run_ruby_code) -> def … escaper` |
| `osx/capture/screen.rb:76` | `exe_path` | `assign L46: datastore['EXE_PATH'].shellescape` |
| `osx/capture/screen.rb:76` | `file_type` | `assign L45: datastore['FILETYPE'].shellescape` |
| `osx/manage/mount_share.rb:136` | `security_path` | `get_keyring_shares(security_path) -> assign L68: datastore['SECURITY_PATH'].shellescape` |
| `osx/manage/mount_share.rb:161` | `sidebar_plist_path` | `get_favorite_shares(...) -> assign L69: … .gsub(/^~/, …) .shellescape` |
| `osx/manage/mount_share.rb:165` | `sidebar_plist_path` | same chain |
| `osx/manage/mount_share.rb:182` | `recent_plist_path` | `get_recent_shares(...) -> assign L70: … .shellescape` |
| `osx/manage/mount_share.rb:195` | `osascript_path` | `def osascript_path body carries escaper` |
| `osx/manage/mount_share.rb:201` | `osascript_path` | `def osascript_path body carries escaper` |
| `osx/manage/record_mic.rb:126` | `@pid` | `assign L80(output) -> assign L76: cmd_exec(['ruby','-e',ruby_cmd].shelljoin)` |
| `osx/manage/sonic_pi.rb:96` | `osc_port` | `def osc_port body carries escaper` |
| `osx/manage/sonic_pi.rb:110` | `sonic_pi` | `def sonic_pi body carries escaper` |
| `osx/manage/webcam.rb:146` | `@pid` | `assign L89(output) -> assign L85: cmd_exec(['ruby','-e',ruby_cmd].shelljoin)` |

**The distribution is the finding.** Every one of the 15 sits in `osx/capture/` or `osx/manage/`, plus one in `multi/gather/`. **Escaping in this corpus is an OSX-module convention, not a framework convention.** There is no `Msf::Post::Common` helper that escapes; each OSX module that needs it reaches for `String#shellescape` locally. `linux/`, `multi/` and `windows/` modules interpolate operator data with no escape at all.

### §1.4 The headline: the defect count

**Cross-tabulated by class × escaping verdict, over all 131 sites:**

| class | sites | ESCAPED | RAW | escaped share |
|---|---|---|---|---|
| **DATASTORE** | **49** | **0** | **49** | **0.0%** |
| UNRESOLVABLE | 45 | 1 | 44 | 2.2% |
| HARDCODED | 14 | 1 | 13 | 7.1% |
| MIXIN_HELPER | 11 | 0 | 11 | 0.0% |
| SESSION_TARGET | 8 | 0 | 8 | 0.0% |
| LOCAL_TOOL_PATH | 2 | 0 | 2 | 0.0% |
| METHOD_BODY_UNRESOLVED | 2 | 0 | 2 | 0.0% |
| **total** | **131** | **2** | **129** | 1.5% |

**The headline, in the form the objective wants:**

> **49 of 49 operator-data (`datastore[...]`) interpolations reach a shell unescaped. Zero escape.**
>
> **All 8 target-derived (SESSION_TARGET) interpolations reach a shell unescaped. Zero escape.**
>
> **57 sites interpolate either operator-set or target-derived data into a shell command line with no escaping primitive anywhere on the chain.**

**Why "57" and not a single blended number.** Some sites carry both an operator value and a target-derived value. Counting sites rather than expressions makes the two classes disjoint: **49 + 8 = 57**, and no site is double-counted because each site has exactly one highest-risk class (§1.5 of D74 states the precedence rule).

**The escaping column is 2, not 0, and the two are not in the 57.** They are `cups_root_file_read.rb:60` (chain-escaped by `.shelljoin`, class UNRESOLVABLE→SESSION_TARGET upon resolution) and `play_youtube.rb:115` (`/bin/sh -c #{joe.shellescape}`, class HARDCODED). **Neither is operator data.**

### §1.5 What "unescaped" does and does not mean here

**It does not mean "exploitable," and the difference is mechanical.**

- A `datastore` value is **operator-set**, not attacker-set. `datastore['PASSWORD']` on `enable_support_account.rb:128` is chosen by the person running the module. Escaping it matters when the *value* is untrusted — e.g. a password read out of a config file, a target's response, or a value assembled from a scan.
- **Interpolation into a quoted position is not the same as interpolation into an unquoted position.** `cmd_exec("net user x #{datastore['PASSWORD']}")` and `cmd_exec('net user x "#{...}"')` differ in whether a space survives, but **neither survives a `";` or a backtick**. Double quotes in `sh` still expand `` ` ``, `$()` and `$VAR`. **A double-quoted interpolation is not a mitigated interpolation.**
- **What D85 establishes is reach, not exploitability.** The 57 is the count of values that *arrive at a shell with no escaping applied*. Whether any particular value can be induced to contain a metacharacter is a question about **who controls that value**, and that is D74's provenance question plus a trust analysis D85 does not perform.

**Stated as a bound rather than a conclusion:** **57 is an upper bound on the escaped-defect count and a lower bound on the raw-interpolation count.** It counts *sites*, not *reachable inputs*. **A reader who converts 57 into an exploit count is reading a number D85 did not produce** — the same refusal D74 made about its own 49, applied one level further.

### §1.6 The escaping-primitive call sites, enumerated

Rule 20 requires the enumeration beside the claim. **All 18 escaping-primitive occurrences in `modules/post`, with their site:**

| # | site | form | bound into |
|---|---|---|---|
| 1 | `multi/escalate/cups_root_file_read.rb:60` | `[user].shelljoin` | **inline in `cmd_exec` arg** |
| 2 | `multi/gather/unix_kerberos_tickets.rb:89` | `Shellwords.escape(file_pattern)` | variable → used `:91` |
| 3 | `multi/manage/play_youtube.rb:115` | `joe.shellescape` | **inline in `cmd_exec` arg** |
| 4 | `osx/capture/keylog_recorder.rb:70` | `ruby_code(opts).shellescape` | variable → used `:104` |
| 5 | `osx/capture/screen.rb:45` | `datastore['FILETYPE'].shellescape` | variable → used `:76` |
| 6 | `osx/capture/screen.rb:46` | `datastore['EXE_PATH'].shellescape` | variable → used `:76` |
| 7 | `osx/capture/screen.rb:47` | `datastore['TMP_PATH']….shellescape` | variable |
| 8 | `osx/manage/mount_share.rb:68` | `datastore['SECURITY_PATH'].shellescape` | variable → used `:136` |
| 9 | `osx/manage/mount_share.rb:69` | `datastore['SIDEBAR_PLIST_PATH']….shellescape` | variable → used `:161`, `:165` |
| 10 | `osx/manage/mount_share.rb:70` | `datastore['RECENT_PLIST_PATH']….shellescape` | variable → used `:182` |
| 11 | `osx/manage/mount_share.rb:222` | `datastore['OSASCRIPT_PATH'].shellescape` | variable → `:195`, `:201` |
| 12 | `osx/manage/record_mic.rb:76` | `['ruby','-e',ruby_cmd].shelljoin` | **ordered-array first arg of `cmd_exec`** |
| 13 | `osx/manage/sonic_pi.rb:88` | `datastore['SonicPiPath'].shellescape` | variable → `:96`, `:110` |
| 14 | `osx/manage/sonic_pi.rb:92` | `datastore['RubyPath'].shellescape` | variable → `:96`, `:110` |
| 15 | `osx/manage/vpn.rb:52` | `datastore['SCUTIL_PATH'].shellescape` | variable |
| 16 | `osx/manage/vpn.rb:53` | `datastore['NETWORKSETUP_PATH'].shellescape` | variable |
| 17 | `osx/manage/webcam.rb:85` | `['ruby','-e',ruby_cmd].shelljoin` | **ordered-array first arg of `cmd_exec`** |
| 18 | `multi/gather/unix_kerberos_tickets.rb:88` | *(comment line naming `Shellwords.escape`)* | **not a call** |

**Two of these are not in the 131-site population at all**: rows 12 and 17 pass an **ordered array** as the first argument (`cmd_exec(['ruby','-e',ruby_cmd].shelljoin)`). My population filter requires a **single-quoted first argument**, so array-form calls are excluded by construction. **This is a named boundary of the population, not an oversight** — see §5.2.

### §1.7 The five all-datastore sites, confirmed by two methods

D69's headline `5 of 143` is confirmed. Both methods find exactly the same five:

| site | command |
|---|---|
| `linux/busybox/set_dmz.rb:30` | `iptables -D FORWARD -d #{datastore['TARGET_HOST']} -j ACCEPT` |
| `linux/busybox/set_dmz.rb:33` | `iptables -A FORWARD -d #{datastore['TARGET_HOST']} -j ACCEPT` |
| `linux/manage/dns_spoofing.rb:32` | `iptables -t nat -A OUTPUT -p udp --dport #{datastore['ORIGIN_PORT']} -j DNAT --to-destination #{datastore['DESTINY_IP']}:#{datastore['DESTINY_PORT']}` |
| `linux/manage/dns_spoofing.rb:33` | same, `-p tcp` |
| `multi/manage/zip.rb:120` | `zip -D -q -r #{datastore['DESTINATION']} #{datastore['SOURCE']}` |

**All five are RAW.** D69's `5` was correct as a count of *pure* operator-data interpolations; what it could not see is that **the same class has 44 more members once bare locals are traced.** The 5 was not wrong — it was **scoped to the directly-readable form**.

---

## §2 T2 — reducing the largest UNRESOLVABLE cause

### §2.1 First: D74's cause label was not a census

D74 §1.5 named five causes **with one instance each**. **A named instance is not a census** (Rule 20). `_d85_p7_causes.py` classifies all 45:

| D85 cause | count |
|---|---|
| **BLOCK_VARIABLE** | **29** |
| OTHER | 15 |
| EXPRESSION_NOT_NAME | 1 |

**Largest cause: `BLOCK_VARIABLE`, 29 of 45.** But the audit in §2.2 shows this label was **itself too coarse** — it lumped together three mechanisms. The corrected traversal (`_d85_p10_t2final.py`) splits them:

| corrected cause | count |
|---|---|
| BLOCK_VARIABLE (true: `x.each do \|v\|`) | 29 |
| LOCAL_ASSIGN_UNCLASSIFIED | 8 |
| NO_ASSIGNMENT_FOUND | 3 |
| PARAMETER_OF_ENCLOSING_DEF | 2 |
| INSTANCE_VAR (`@pid`) | 2 |
| EXPRESSION_NOT_NAME (`[user].shelljoin`) | 1 |

**16 of the 45 were never block-variable sites at all.** `hashdump.rb:110-118,228`, `record_mic.rb:126`, `webcam.rb:146`, `viscosity.rb`-class sites — those interpolate **method-return values** and **instance variables**, and D74's label sent a reader looking for an `each` block that does not exist. **Corrected here.**

### §2.2 The reduction, and the two numbers that differ

**Automatic reduction: 0 of 29.** `_d85_p8_blockreduce.py` found the enclosing block header for all 29 and printed the iteration chain for each — and **inherited a class in zero cases.** That is not a probe failure; it is the shape of the corpus. The chains show why:

```
enum_osx.rb:248  u <- L247 iter: users.each
                    users was built by:  L239 users = []   then   L244 users << u.chomp
                                         where L241 u <- users_folder.each_line
                                         and   L240 users_folder = cmd_exec('/bin/ls','/Users')
```

**The iterated collection is an append-only accumulator (`<<`) built inside a *previous* block from a *previous* `cmd_exec`.** My resolver follows `=`, `||=` and `def`. **It has no rule for `<<`.** The collection is not assigned — it is *grown*.

**Hand-audited reduction: 15 of 45**, via `_d85_p10_t2final.py`, which adds shovel-accumulation chasing and instance-variable lookup across the whole method:

| verdict | sites |
|---|---|
| **REDUCED → SESSION_TARGET** | **14** |
| **REDUCED → DATASTORE** | **1** |
| INSTANCE_VAR_UNRESOLVED | 2 |
| **STILL_UNRESOLVED** | **28** |
| **total** | **45** |

**Both numbers are reported because they measure different things.** `0` is what the general resolver achieves. `15` is what a resolver with a shovel rule plus a human reading each chain achieves. **Reporting only the first understates the corpus; reporting only the second pretends a tracer exists that does not.** The honest statement is: **a `<<`-aware resolver would recover ~15; the general resolver recovers 0 because the accumulation idiom is not an assignment.**

**The 15 reductions, with chains:**

| site | class | chain |
|---|---|---|
| `linux/busybox/ping_net.rb:33` | **DATASTORE** | `ip <- L31 iter: Rex::Socket::RangeWalker.new(datastore['RANGE']).each` |
| `linux/gather/tor_hiddenservices.rb:71` | SESSION_TARGET | `config <- L61 = cmd_exec("locate 'torrc' …").split("\n")` |
| `multi/gather/firefox_creds.rb:358` | SESSION_TARGET | `files <- L344 session.fs.dir.foreach(path)` |
| `osx/gather/enum_osx.rb:217` | SESSION_TARGET | `ssh_folder <- L212 = cmd_exec('/bin/ls -ma ~/.ssh').split(', ')` |
| `osx/gather/enum_osx.rb:232` | SESSION_TARGET | `gnugpg_folder <- L227 = cmd_exec('/bin/ls -ma ~/.gnupg')…` |
| `osx/gather/enum_osx.rb:257` | SESSION_TARGET | `users <- L239 users = []` (shovel from `cmd_exec`) + `ssh_folder <- L252` |
| `osx/gather/enum_osx.rb:272` | SESSION_TARGET | `users` shovel + `gpg_folder <- L267` |
| `osx/gather/enum_osx.rb:293` | SESSION_TARGET | `loginwindow_pids <- L290 = cmd_exec("/bin/ps aux \| /usr/bin/awk …")` |
| `osx/gather/enum_osx.rb:295` | SESSION_TARGET | same |
| `osx/gather/enum_osx.rb:296` | SESSION_TARGET | same |
| `osx/gather/enum_osx.rb:330` | SESSION_TARGET | `root_folder <- L324 = cmd_exec('/bin/ls -ma ~/').split(', ')` |
| `osx/gather/enum_osx.rb:345` | SESSION_TARGET | `users` shovel + `user_folder <- L339` |
| `osx/gather/enum_osx.rb:359` | SESSION_TARGET | `current_user_folder <- L353 = cmd_exec('/bin/ls -ma ~/')…` |
| `osx/gather/enum_osx.rb:381` | SESSION_TARGET | `keychain_files <- L379 = cmd_exec("/usr/bin/sudo -u #{u} -i …")` |
| `osx/gather/enum_osx.rb:392` | SESSION_TARGET | `keychain_files <- L390 = cmd_exec('/usr/bin/security list-keychains')` |

**One DATASTORE in fifteen.** The iteration source is `Rex::Socket::RangeWalker.new(datastore['RANGE'])` — and I initially reported this site UNRESOLVED because `origin_of` looked only at `<<` and `=`, **never at the iterated expression itself**, which literally contains `datastore['RANGE']`. Fixed in §4.4.

### §2.3 What the reduction changes about the whole corpus

**The 45 unresolvable were not a random tail. Fourteen of fifteen resolvable ones are SESSION_TARGET** — target directory listings, `ps aux` output, keychain enumeration. And note what they are interpolated *into*: `cat`, `ls -ma`, `find`, `system_profiler`, `security list-keychains`.

**That is the actual shape of the 138.** It is not "23% of bare locals are datastore." It is: **MSF post modules read the target's filesystem and then paste the target's own filenames back into further shell commands.** The value is attacker-influenceable because **a filename on the target is target-controlled** — a directory named `` ; rm -rf / `` is a legal Unix filename.

**This reframes the defect.** D74 said *"49 sites interpolate operator-set data."* D85 adds: **at least 14 more sites interpolate target-controlled strings — filenames, process names, account names — that the target itself chooses.** For an attacker who can create a file in a directory the module lists, `enum_osx.rb`'s `cmd_exec("/bin/cat ~/.ssh/#{k}")` is reachable with `k` chosen by the attacker.

**Reported as an explicit inference, not a measurement.** The chain proves the *provenance* of `k`. Whether a particular target's filesystem is attacker-writable, and whether a filename containing `$()` survives `bash -c` expansion inside the quoting used, are **not measured here**. Tagged `[inferred]`.

### §2.4 The 28 still unresolved, by cause

| cause | sites | why it still fails |
|---|---|---|
| BLOCK_VARIABLE (chain not recoverable) | 17 | the accumulator or its origin is a method parameter, a hash literal, or a multi-line `= [`/`= {` that my single-line assignment scanner cannot read |
| LOCAL_ASSIGN_UNCLASSIFIED | 8 | assigned from a `map`/`select`/string op whose own operand is not a name |
| INSTANCE_VAR | 2 | `@pid` assigned in a method never called in-file |
| PARAMETER_OF_ENCLOSING_DEF | 1 | the only caller is in another file |

**The two `@pid` sites are the interesting ones.** `record_mic.rb:126` and `webcam.rb:146` interpolate `@pid` into `/bin/kill -9 #{@pid}`. `@pid` is assigned in `start`/`stop` from `cmd_exec(...).split` — **a target-derived process id.** The escaping trace already resolved one of them (`record_mic.rb:126 → @pid → L80(output) → L76 shelljoin`), so **`@pid` is target-derived and its value reaches `kill -9` with no escaping.** A negative PID or a value with a shell metacharacter terminates a different process. **`[inferred]` — the provenance is proven, the exploitability is not.**

---

## §3 T3 — the network-fetch bounded class

### §3.1 The class, defined and enumerated

**Definition.** A site where `cmd_exec` / `create_process` receives an argument containing a **network-fetching tool token** — `curl`, `wget`, `fetch`, `nc`, `ncat`, `netcat`, `telnet`, `ftp`, `tftp`, `scp`, `sftp`, or the PowerShell forms `Invoke-WebRequest` / `Invoke-RestMethod` / `iwr` / `irm` / `DownloadString` / `DownloadFile` / `bitsadmin` / `certutil`.

**This is a bounded class, enumerated over all `cmd_exec` sites, not restricted to the interpolated population.** Rule 20: the population is defined by the primitive, not by what I already know.

**Result: 11 sites.**

| site | tool | fetches |
|---|---|---|
| `linux/busybox/wget_exec.rb:36` | wget | `-O #{random_file_path} #{datastore['URL']}` |
| `linux/gather/vcenter_secrets_dump.rb:875` | curl | `http://localhost:7080/idm/tenant/#{base_fqdn}/certificates?scope=TENANT` |
| `linux/manage/geutebruck_post_exp.rb:54` | curl | `http://localhost/test/../uapi-cgi/snapshot.fcgi -o /usr/www/uapi-cgi/viewer/image.fcgi` |
| `multi/escalate/aws_create_iam_user.rb:168` | curl | `curl --version` (capability probe) |
| `multi/escalate/aws_create_iam_user.rb:172` | curl | `curl #{url}` |
| `multi/escalate/aws_create_iam_user.rb:174` | curl | `curl #{url}iam/` |
| `multi/escalate/aws_create_iam_user.rb:176` | curl | `curl #{url}iam/security-credentials/` |
| `multi/escalate/aws_create_iam_user.rb:177` | curl | `curl #{url}iam/security-credentials/#{resp}` |
| `multi/gather/aws_ec2_instance_metadata.rb:50` | curl | `curl --version` (capability probe) |
| `multi/gather/aws_ec2_instance_metadata.rb:100` | curl | `curl -s #{url}` |
| `osx/capture/keylog_recorder.rb:107` | nc | `nc localhost #{port}` |

**Distribution (mandatory print):** curl 9, wget 1, nc 1. By interpolation: `HAS_interp` 7, `NO_interp` 3, `HAS_datastore` 1. By destination host: **10 of 11 have no discernible destination host** (the URL is in a variable); 1 is a literal `localhost`.

**Control, per Rule 20.** `curl`/`wget` occur **31 times tree-wide** in `modules/post`, and **10 times inside a `cmd_exec` argument.** The other 21 are comments, documentation strings, and non-executed literals. **The 11-site class is the executed subset, and the control shows the scanner sees both.**

### §3.2 The fourth provenance class: CLOUD_METADATA

**The T3 sites expose a class my four-way provenance rule never had.**

`aws_ec2_instance_metadata.rb:100` and `aws_create_iam_user.rb:172-177` fetch from a `#{url}` that is not the target and not the operator. It is the **cloud instance metadata service** — an in-guest HTTP endpoint (`169.254.169.254` or its equivalents) serving **instance credentials**.

**The provenance lattice has a fourth member:**

| class | who controls the value |
|---|---|
| DATASTORE | the operator (or the operator's config) |
| SESSION_TARGET | the target host's filesystem/processes |
| **CLOUD_METADATA** | **the cloud provider's in-guest endpoint — credentials issued to the instance** |
| HARDCODED | the module author |

**Why it is distinct and why it lacks escaping entirely:** a metadata fetch returns **a live credential**. `aws_create_iam_user.rb:177` interpolates `#{resp}` — **a value read back from the metadata endpoint** — directly into a further `curl` argument. The next request's **path `/iam/security-credentials/#{resp}` is built from a value the metadata service returned.** If the metadata response can be influenced, so can the URL.

**The 8 sites in this class are 0-escaped and 4-interpolated.** Provenance: metadata-derived. **Reported as `[read]`** — the sites and their arguments are read; the assertion that the endpoint serves credentials is standard cloud behaviour **`[inferred]`** and is not measured by reading this corpus.

**This converts D74's weakest cell from a zero into a named population.** D74's `REMOTE_RESPONSE = 0` was a real zero **for direct-socket reads**, and the reason is now named: **MSF post modules do not use `Net::HTTP` to read remote content — they shell out to `curl`, whose output arrives as a `cmd_exec` return value and therefore lands in `SESSION_TARGET`.** The 0 was not an absence of remote reads; it was **an absence of remote reads *through a Ruby HTTP client*.** The bounded class is now enumerated and its true size is 11 sites, 8 of which are metadata reads.

### §3.3 The `wget_exec.rb` site is the one fully-operator-controlled fetch

`wget_exec.rb:36` — `"wget -O #{random_file_path} #{datastore['URL']}"`.

- The **first** interpolated value, `random_file_path`, is a local temp path (`[read]`: assigned from a mixin helper).
- The **second**, `datastore['URL']`, is **the operator's URL, interpolated raw into a shell command line.**

Under D74's **first-argument-only** rule this site classes INTERPOLATED, and both expressions are visible. Under D69's rule it was one of the **138** bare locals — and it is the single clearest case in the whole population of an operator-supplied URL reaching `wget` with no escaping. **It is in the 49 DATASTORE sites (§1.4) and it is RAW.**

---

## §4 Instrument record

**Six entries. Four are defects in instruments I wrote this round. Two are reconciliations. Every one is recorded in place, unsmoothed.**

### §4.1 `[instrument]` — a primitive census built from memory missed the primitive that mattered

**What I did.** Listed fifteen shell-escaping primitives **from memory** and searched for them. `.shelljoin` was not on the list.

**What broke.** `cups_root_file_read.rb:60` uses `.shelljoin` — the array form of `Shellwords.escape`. The site appeared in the population (it is the `EXPRESSION_NOT_NAME` cause) but its **escaping status was invisible**, because the primitive was not being searched for.

**What caught it.** The site itself: D74 listed it as UNRESOLVABLE, I read it by eye, and the eye-read found `.shelljoin`. **Rule 20 fired against my own vocabulary** — a named path (my memorized list) is not a census (the corpus's actual primitives).

**Fix.** The primitive set became an **output**: `_d85_p3_escapecensus.py` enumerates the escaping *family* by regex and reports which members occur. `.shelljoin` (3 occurrences / 3 files) and `Shellwords.escape` (2/1) appeared immediately.

**Generalisable rule.** *A hand-built list of things-to-search-for is an unvalidated instrument. Derive the list from the corpus and report its members.*

### §4.2 `[instrument]` — a same-line escaping test measured the wrong line

**What I did.** Searched for escaping primitives **inside the argument text**.

**Result.** ESCAPED 2 / RAW 129 over 131 sites — a number that reads as *"almost nothing escapes."*

**What broke.** Sixteen of eighteen escaping occurrences bind into a **variable on the preceding line**. `screen.rb:45-47` escapes into `file_type`, `exe_path`, `tmp_path`; `:76` uses them. **A same-line test can only see the two that are inline.**

**What caught it.** The primitive census. 13 `shellescape` + 3 `shelljoin` occurrences versus 2 same-line hits is a contradiction that cannot survive unexamined.

**Fix.** `_d85_p6_esctrace.py` — point the **resolution chain** at an escaping predicate, not the argument text. 2 → **15**.

**Generalisable rule.** *An escaping test scoped to the call site measures whether escaping is INLINE, not whether it happened.* **This is D74's `puppet_exe` lesson moved from provenance to escaping.**

### §4.3 `[instrument]` — a parameter resolver that ate its own `def` signature

**What I did.** Wrote a second resolver with **paren-less `def` parameter parsing** — an improvement over D74's version — and in the rewrite **deleted a guard line** that D74's resolver had.

**What broke.** The parameter branch searches for call sites of the enclosing method with `method\s*\(args\)`. **That pattern also matches the `def method(...)` line itself.** Without the guard, resolving parameter `uri` in `def osx_open(uri)` found `osx_open(uri)`, fed `uri` back in as the argument, and recursed on the same name at the same depth until the depth limit — returning **`UNRESOLVABLE` for a resolvable parameter**.

**Measured effect: 11 sites changed class.** DATASTORE **49 → 43**, UNRESOLVABLE 45 → 55. A six-site movement in the headline class.

**What caught it.** I re-ran the population with the **first** resolver and compared. **Two independently-written resolvers disagreeing on 11 sites is the signal.** Reading all 11 by eye showed every one was a paren-less or parenthesized parameter — and the fixed resolver agreed with the original on all 11.

**Fix.** Restored the guard, with a comment naming the failure. The re-run reproduces the first resolver **exactly**: DATASTORE 49 / UNRESOLVABLE 45 / SESSION_TARGET 8 / MIXIN_HELPER 11.

**Generalisable rule.** *A call-site search that does not exclude the declaration site will bind a parameter to itself and report "unresolvable" for every name under test.* **A silent wrong answer on exactly the names the probe is for — the same shape as the `\b`-after-`?` defect (D69 §6.7).** No distributional tell; only an independent method exposes it.

**And note the sequence:** the improvement (paren-less parsing) was real, the regression (deleted guard) came with it, and **the regression would have shipped as a corrected headline** — *"49 was too high, the true number is 43."* That direction is the dangerous one: **a correcting number that is itself wrong is harder to challenge than an original claim.**

### §4.4 `[instrument]` — `origin_of` never inspected the iterated expression

**What I did.** In the block reducer, looked for how a collection got its value via `<<` or `=`, then via enclosing-def parameter.

**What broke.** `ping_net.rb:33` iterates:

```ruby
Rex::Socket::RangeWalker.new(datastore['RANGE']).each do |ip|
```

**`datastore['RANGE']` is inside the iterated expression itself.** No `<<`, no `=`, no parameter — so `origin_of` returned nothing and the site was reported `STILL_UNRESOLVED` when the answer is `DATASTORE`.

**Fix.** Classify the **iterated expression** before chasing its terminal name. This is the **only** DATASTORE recovery in the whole T2 pass, so the defect was suppressing the single highest-consequence answer available.

**Generalisable rule.** *When tracing through a block, the iteration source is itself a candidate expression. Do not only look for how the collection was assigned.*

### §4.5 `[instrument]` — a match object consumed as text

**What I did.** In the reducer, `for e in INTERP.finditer(s["cmd"]): inner = e[2:-1].strip()`.

**What broke.** `finditer` yields **match objects**; `e[2:-1]` raises `IndexError: no such group`. In my earlier probe I had correctly written `[x.group(0) for x in INTERP.finditer(...)]` first and worked from the string. **In the rewrite I dropped the `.group(0)`.**

**Caught by:** the crash, immediately.

**Generalisable rule.** *This is the same family as D74's `findall`-returns-the-group defect (§4.2 there): a regex API whose return shape differs from expectation, consumed without checking.* **In D74 the symptom was silent (all 197 expressions misclassified); here it was loud.** **The silent form is the dangerous one, and it has now occurred twice in two rounds on the same API pair.**

### §4.6 `[instrument]` — cross-check by second method, and which figures are stable

Method 2 (`_d85_p12_crosscheck.py`) **blanks comments and string literals before counting** and uses an independent depth-counting scanner.

| figure | method 1 | method 2 | verdict |
|---|---|---|---|
| `cmd_exec`/`create_process` sites, raw text | 463 | **463** | **exact** |
| same, comments+strings blanked | 459 | **459** | **exact** |
| first-arg LITERAL | 227 | 229 | **stable** (±2) |
| first-arg INTERPOLATED | 141 | 142 | **stable** (±1) |
| interpolated expressions | 197 | 194 | **stable** (±3) |
| **all-datastore sites** | **5** | **5** | **exact — D69's headline independently confirmed** |
| interp first-arg VARIABLE + OTHER | 82 + 9 = 91 | 90 | **stable** |

**The raw/blanked pair is the one to read.** 463 raw, 459 blanked: **the 4-site difference is `cmd_exec` tokens appearing inside comments**, and it reconciles D74's churn series exactly (455 / 457 / 459 across rounds — see D74 §4.1). **459 is the shipped figure, and it is shipped with the raw 463 beside it** so a reader can see what the filter removed.

**One deliberate non-reconciliation, carried forward from D74.** Three `datastore` counts exist — **16** (literal `datastore[` text inside an interpolation), **62** (expressions resolving to datastore), **49** (sites whose highest-risk class is DATASTORE). **They answer three different questions.** D74 §4.6 additionally warns that a 300-character windowed count also returns **49** by coincidence. **That coincidence is not agreement and D85 does not treat it as one.**

---

## §5 Residual unknowns, each with a probe

**§5.1 The escaping question for the 44 unresolvable-then-unreduced sites.** 28 sites remain UNRESOLVED after T2; their escaping status is undecided because their value is undecided. **Probe:** extend the resolver with map/select/hash-literal operand parsing and re-run `_d85_p6_esctrace.py`.

**§5.2 The ordered-array first argument.** Two escaping occurrences (`record_mic.rb:76`, `webcam.rb:85`) pass `['ruby','-e',ruby_cmd].shelljoin` as `cmd_exec`'s **first argument**. My population filter requires a single-quoted first argument, so **array-form calls are outside the 131**. **Probe:** widen the filter to accept array literals and report the delta to 141. **Named here because it is a boundary of the population, and a boundary that is not named gets mistaken for a complete set.**

**§5.3 Non-grep/sed shell metacharacter exposure.** D85 classifies *escaping*, not *quoting context*. `cmd_exec("cat #{x}")` and `cmd_exec("cat \"#{x}\"")` both classify RAW. **Probe:** classify each of the 57 by whether the interpolation sits inside single quotes, double quotes, or unquoted. **This is the second half of reach and D85 does not measure it.**

**§5.4 The `create_process` analogue.** D74 established that all 8 `create_process` sites pass argv **arrays** and none interpolate. **Probe:** confirm over the widened population from §5.2 and report whether any `create_process` argument reaches a shell.

**§5.5 CLOUD_METADATA as a provenance class, corpus-wide.** §3.2 names 8 sites. **Probe:** enumerate every `169.254.169.254` / metadata-endpoint reference in the tree and classify by whether the returned credential is interpolated into a further command. **The class is currently 8 and the number is a floor, not a census.**

**§5.6 Escaping outside `modules/post`.** D85 censuses `modules/post` only (436 files). **Probe:** run `_d85_p3_escapecensus.py` against `modules/exploit` and `modules/auxiliary` and report the primitive distribution. **`exploit/` is where a shell-escape defect is most consequential, and it is untraced.**

---

## §6 Status

**Deliverable:** this file, sole owner `source-diver`.
**Files written:** this report; probes `_d85_p1_primcensus.py`, `_d85_p2_drift.py`, `_d85_p3_escapecensus.py`, `_d85_p4_reconcile.py`, `_d85_p5_esctest.py`, `_d85_p6_esctrace.py`, `_d85_p7_causes.py`, `_d85_p8_blockreduce.py`, `_d85_p9_t2audit.py`, `_d85_p10_t2final.py`, `_d85_p11_t3.py`, `_d85_p12_crosscheck.py`; plus `_d85_pop.json`, `_d85_sites.json`, `_d85_esc.json`, `_d85_esctrace.json`, `_d85_causes.json`, `_d85_t2.json`, `_d85_t2audit.json`, `_d85_t2final.json`, `_d85_t3.json`. **Retained, not deleted.**

**Broken or superseded probes retained and labelled:**
- **`_d85_p4_reconcile.py` — BROKEN.** Its `__file__`-relative path join resolved against the workspace root instead of `metasploit/`, so every source read failed with `MISSING`. The path bug was fixed inline in a subsequent read; **the original file is kept as written.** The eleven moved sites it was written to identify were recovered by the corrected read.
- **`_d85_p4_reconcile.py` — SECOND DEFECT, in the heading-census probe used to verify THIS file.** A Markdown heading census pattern `(?m)^(#+)\s+(.+)$` matched the **Ruby comment line `# modules/post/osx/capture/screen.rb`** inside §1.2's fenced code block, reporting **30 headings where the true count is 29**. Same family as D41's `Â` finding, mirrored: **a detector whose subject is a document containing source code will be matched by that source code's own comment syntax.** Fix: exclude fenced-code regions before census, or require a heading marker **not** followed by a path-looking token. **Recorded because the same pattern will match any Ruby, shell or PowerShell comment in any future report of mine.**
- **`_d85_p5_esctest.py` — SUPERSEDED, and its result was not shipped.** It reports ESCAPED 2 / RAW 129. **That number is wrong** (§4.2) and the probe is retained precisely so the wrong number stays visible next to the right one (15 / 182).
- **`_d85_p9_t2audit.py` — SUPERSEDED by `_d85_p10_t2final.py`.** Its first verdict pass reported `REDUCED 14 / STILL 15 / NO_BLOCK 16`; the second pass corrects the cause census and recovers one more DATASTORE site via §4.4. **Retained for the series.**
- **`_d85_p3_escapecensus.py` — BUGGED AS FIRST RUN, then fixed in place.** Its first run deleted D74's declaration-skip guard (§4.3). **The file now contains the fix; the 43/55 output it produced is recorded in this report and in `_d85_pop.json` is the correct 49/45.** The buggy behaviour is preserved here in §4.3 rather than in the file.

**Acceptance.** T1 answered: escaping primitive set derived from the corpus and enumerated (§1.1, §1.6); escaping test through the chain rather than the call site (§1.2–1.3); **headline defect count 49 of 49 operator-data sites RAW, plus 8 of 8 target-derived sites RAW, 57 total (§1.4)**; boundary explicitly stated and the count refused as an exploit count (§1.5). T2 answered: causes recensused (§2.1), **automatic reduction 0 and hand-audited reduction 15 both reported (§2.2)**, new resolved/unresolved split, and the reframing that 14 of 15 are target-derived filenames (§2.3). T3 answered: **the network-fetch class enumerated at 11 sites with a control (§3.1)**, and it exposed a fourth provenance class, CLOUD_METADATA, converting D74's weakest zero into a named 8-site population (§3.2). Instrument record: 6 entries, 4 of them my own defects (§4).

**No verified artefact was modified.** D7/D8/D9/D22/D42/D58 untouched; **D45 and D69 untouched and remain frozen by Lead's ruling**; **D74 untouched.** No `open_binary`, no network, no execution, no build.

**Unverified-by-me, flagged:** all counts are from static reading of the on-disk tree. No claim here is runtime-verified. `confirm by corpus-read, not by memory` was applied to every population.
