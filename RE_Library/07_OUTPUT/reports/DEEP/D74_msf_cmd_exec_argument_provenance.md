# D74 — MSF `cmd_exec` / `create_process` argument provenance

**Lane:** `source-diver` (source-only). **Scope:** `RE_Library\01_SOURCE_c2\metasploit`.
**Basis:** D69 (`D69_msf_post_interior_hardening.md`, verified, frozen) §2.5, §5.3, §5.4.
**Owner:** this file only. D7/D8/D9/D22/D42/D58/D45/D69 untouched.

**Convention note.** Byte counts here are LF bytes. Where I quote file sizes I say which convention.
**Claim tags.** `[source]` read from the tree · `[measured]` produced by an invocation shipped with the claim · `[inferred]` my reasoning over both · `[absence]` a zero with a positive control · `[instrument]` a probe defect.

---

## Table of Contents

- §0 Corrections — D69's 5/138 split was wrong in three ways
- §1 T1 — provenance of the non-datastore interpolated arguments
  - §1.1 The rule, stated before application
  - §1.2 The resolution engine, and the two blindnesses it had to be taught
  - §1.3 Result: the provenance table
  - §1.4 The priority subset, and why that boundary
  - §1.5 The unresolvable 44, named
- §2 T2 — second arguments, and the delta
  - §2.1 Definition, forced by the 3-argument calls
  - §2.2 The delta: 141 → 168
  - §2.3 The four sites that justify T2 being asked
- §3 What the two tasks together change
- §4 Instrument record
- §5 Residual unknowns, each with a probe
- §6 Status

---

## §0 Corrections

**D69 §2.5 reported `5 / 138 / 13`: 5 sites interpolating operator data, 138 interpolating bare locals, 13 unclassified.** All three sub-figures are wrong, and the 138 is wrong in the direction that **flattered the split's honesty**. Stated first, because a report that buries this is a summary defect.

| figure | D69 | D74 `[measured]` | why D69 was wrong |
|---|---|---|---|
| interpolated first args | 143 | **141** | probe churn (§4.1) |
| sites interpolating `datastore[...]` **directly** | 5 | **5** — correct, but **collapsed** | 5 is right and hid a middle class |
| sites interpolating a bare local | 138 | **131** | 7 sites were double-counted as bare-local |
| **bare locals that RESOLVE to operator data** | *not measured — implied "unknown"* | **62 expressions / 49 sites** | **the count asked a lexical question and reported it as a provenance answer** |
| total call sites (first-arg basis) | 455 | **459** | probe churn (§4.1) |

**The substantive correction §0 must carry:**

> **D69 said 138 sites interpolate a bare local, with provenance explicitly deferred to an open question. D74 answers that question, and the answer is that the majority of them are resolvable — 62 of 174 interpolated expressions terminate in `datastore[...]` once method-definition returns and parameter bindings are followed. The "138 unknowns" were 131 sites, and most of those unknowns were an artefact of a tracer that could not read `def`.**

**The instrument defect that made this a wrong summary rather than a wrong measurement:** D69 §5.4 correctly named the trace as unperformed and correctly refused a headline. **But it then printed `5 / 138 / 13` as if the middle term were a provenance class.** It was a *lexical* class wearing a provenance label. `puppet_exe`, `facter_exe`, `ansible_inventory`, `tmp_path` are all bare locals, and **all four resolve to `datastore`** — `puppet.rb:44 def puppet_exe` returns `datastore['PUPPET']` at `:47`. **A bare local is not an unknown; it is an untraced value, and the difference is the whole task.**

**Second correction, from T2:** D69's rule scored the **first argument only**, so `cmd_exec('cmd.exe', "/c net user support_388945a0 #{datastore['PASSWORD']}")` was classed **LITERAL**. **T2 adds 27 sites (141 → 168), and two of them interpolate an operator password into a shell command line.**

---

## §1 T1 — provenance of the non-datastore interpolated arguments

### §1.1 The rule, stated before application

Applied per **interpolation expression**, then rolled up **per site**.

| class | definition |
|---|---|
| `DATASTORE` | the value reads `datastore[...]` / `datastore.`, directly or through any chain that terminates there |
| `SESSION_TARGET` | an identity or attribute of the target, or **content the target returned** (`nvram get`, `dmesg`, `grep`, `cat`, `reg query`, `grab_*`, `enum_*`) |
| `REMOTE_RESPONSE` | value read from a network response (`Net::HTTP`, `HTTPClient`, `Rex::Proto`, `Rex::Socket`, `SMBSimpleClient`, `.recv`, `.body`, `.read`) |
| `MIXIN_HELPER` | framework `Post::` helper return (`get_env`, `get_envs`, `writable_dir`, `temp_dir`, `Rex::Text`, `File.join`, `expand_path`, `report_*`) |
| `LOCAL_TOOL_PATH` | the location of a binary, from `whereis` / `which` / `command -v` / `file?` / `executable?` |
| `HARDCODED` | literal, constant, or a path assembled only from literals |
| `UNRESOLVABLE` | no assignment, no `def`, and no parameter binding terminates the chain within depth 8 |

**Boundary decision, and it is the one I got wrong first (`§4.3`):** `LOCAL_TOOL_PATH` is separated from `SESSION_TARGET`. `cups_root_file_read.rb:149 ctl_path ||= whereis('cupsctl')` flows to `:156 def whereis(exe)` → `:157 cmd_exec("whereis #{exe}")`. **A `cmd_exec` appears in the chain, but the value that flows out is a filesystem path to a local binary, and the tainted token (`'cupsctl'`) is hardcoded.** My first rule matched `cmd_exec` in the body and called it `SESSION_TARGET` — **over-inclusion, 15 → 9 expressions once fixed.** **A class defined by "a dangerous function appears in the body" is the D56 name-filter error pointed at a call graph.**

The site roll-up takes the **highest-risk class among the site's expressions**, ordered `REMOTE_RESPONSE > SESSION_TARGET > DATASTORE > MIXIN_HELPER > LOCAL_TOOL_PATH > HARDCODED > UNRESOLVABLE`.

### §1.2 The resolution engine, and the two blindnesses it had to be taught

The tracer's resolution order for a name at a site: **(1)** parameter of the enclosing `def` → recurse into the caller's argument; **(2)** nearest preceding assignment in the enclosing method; **(3)** any assignment to that name anywhere in the file; **(4)** `def name` in the file → classify the body; **(5)** `UNRESOLVABLE`.

**Blindness A — a name that is a `def` is not a local.** The first tracer searched assignments only, and reported `puppet_exe` as unresolved **142 times across the interior**. `[source]` `linux/gather/puppet.rb:44-54`:

```ruby
def puppet_exe
  return @puppet if @puppet
  ['/opt/puppetlabs/puppet/bin/puppet', datastore['PUPPET']].each do |exec|
    next unless file?(exec)
    next unless executable?(exec)
    @puppet = exec
  end
  @puppet
end
```

**That is operator data with a hardcoded fallback, and it is only visible by reading the method.** `facter_exe:56` is the same shape. `ansible.rb:49 def ansible_inventory` reads `datastore['ANSIBLEINVENTORY']`. **Four of the top bare locals in D69's list are `def`s, not variables.**

**Blindness B — a name that is a parameter belongs to the caller.** `[source]` `linux/capture/grandstream_gxp1600_sip.rb:198,202-203`:

```ruby
def nvram_get(pvalue)
def nvram_set(pvalue, data)
  cmd_exec("/usr/bin/nvram xet #{pvalue}=\"#{data.to_s.gsub('"', '\\"')}\"")
```

`pvalue` is a parameter; the callers at `:265` pass `pvalue_array[idx]`, itself filled from an `nvram get` read. **Provenance is 2 hops up, and a same-method assignment search cannot see any of it.**

**Blindness C — the assignment may sit in a different method of the same file.** `xen_420_dos.rb:186` interpolates `@writeable_folder`, assigned at `:46` in `initialize` — outside the calling method. Resolution step (3) exists for this.

### §1.3 Result: the provenance table

`[measured]` — invocation: `python _d74_p7_prov3.py`, over all 436 `post` `.rb` files.
Population: **the 130 sites whose first argument interpolates ≥1 non-`datastore[...]` expression** — **174 expressions.**

| class | expressions | % | sites | % |
|---|---:|---:|---:|---:|
| **DATASTORE** | **62** | 35.6% | **49** | 37.7% |
| UNRESOLVABLE | 61 | 35.1% | 44 | 33.8% |
| HARDCODED | 24 | 13.8% | 14 | 10.8% |
| MIXIN_HELPER | 13 | 7.5% | 11 | 8.5% |
| **SESSION_TARGET** | **9** | 5.2% | **8** | 6.2% |
| LOCAL_TOOL_PATH | 3 | 1.7% | 2 | 1.5% |
| METHOD_BODY_UNRESOLVED | 2 | 1.1% | 2 | 1.5% |
| **REMOTE_RESPONSE** | **0** | 0% | **0** | 0% |

**Sample of each class, with the resolved chain printed:**

**DATASTORE (49 sites)** — `linux/gather/puppet.rb:69`, `#{puppet_exe}` → `def puppet_exe at L44` → `method body -> DATASTORE`. Also `openvpn_credentials.rb:76` → `def tmp_path at L51` → `datastore['TMP_PATH']`; `android/capture/screen.rb:54` → `assign L45: datastore['EXE_PATH']`; `linux/dos/xen_420_dos.rb:203` → `FILE-LEVEL assign L46: datastore['WritableDir'].to_s + @rand_folder`.

**SESSION_TARGET (8 sites)** — `linux/capture/grandstream_gxp1600_sip.rb:214` → `assign L211: cmd_exec('/usr/bin/nvram get dbus_session')`; `multi/gather/wlan_geolocate.rb:192` → `assign L188: cmd_exec("dmesg | grep -i wlan | cut -d ':' -f1 | uniq")`; `osx/gather/hashdump.rb:73` → `assign L65: grab_shadow_blob(user)` → `def grab_shadow_blob at L227`.

**LOCAL_TOOL_PATH (2 sites)** — `multi/escalate/cups_root_file_read.rb:122,136,137` → `ctl_path ||= whereis('cupsctl')` → `def whereis at L156` → `cmd_exec("whereis #{exe}")`.

**HARDCODED (14 sites)** — `osx/gather/enum_osx.rb:300` → `picture_name := Time.now.strftime('%Y%m%d%H%M%S')`; `windows/gather/local_admin_search_enum.rb:88` → `/c #{cmd}` where `cmd := 'gpresult /SCOPE COMPUTER'`.

**REMOTE_RESPONSE = 0** `[absence]` — **with the positive control that matters: the class is not unreachable in principle.** `aws_create_iam_user.rb:174-177` builds `#{url}` from `"http://#{datastore['METADATA_IP']}/2012-01-12/meta-data/"` and reads it back with `cmd_exec("curl #{url}...")` into `resp`. **`url` is DATASTORE and `resp` is SESSION_TARGET under my rule, because the read is via `cmd_exec` rather than a socket.** **So a target-controlled HTTP response that is then interpolated into another command would be classed SESSION_TARGET, not REMOTE_RESPONSE.** The zero is real **for the direct-socket route**, not for target-derived data generally. **This is the weakest cell in the table and §5.1 names the probe.**

### §1.4 The priority subset, and why that boundary

**I traced all 130 non-datastore sites rather than a subset, so the "boundary" here is the population boundary, not a sample.** Justification for bounding *there*: the 141 interpolated first-argument sites are exactly the population where D69's provenance question is load-bearing, and the other 318 sites are literal or variable first arguments whose injection surface is the **escaping** question (D45's territory), not the provenance question.

**Within the traced set, the priority ranking is by consequence of the class, not by count:**

1. **DATASTORE, 49 sites** — operator-set. **Highest consequence and lowest ambiguity:** these are trivially attacker-influenceable by anyone who can set a module option or reach `msfconsole`/`msfrpcd`. **`datastore['PASSWORD']`, `['SOURCE']`, `['DESTINATION']`, `['TMP_PATH']`, `['URL']`, `['METADATA_IP']`.**
2. **SESSION_TARGET, 8 sites** — target-returned content. Consequence depends on whether the target is already the adversary.
3. **MIXIN_HELPER, 11 sites** — framework-controlled.
4. **UNRESOLVABLE, 44 sites** — named in §1.5.

**`create_process` contributes ZERO interpolated arguments** `[measured]` — all 8 sites pass literals or variables, and their `args:` are **argv arrays**, e.g. `pam_backdoor.rb:182 create_process('uname', args: ['-m'])`, `cve_2026_46333_chage.rb:297 create_process('gcc', args: ['-O2', c_path, '-o', bin_path])`. **This is the D45/`AGENTS.md` design point confirmed by measurement: `create_process` separates executable from arguments so no shell parses them. All 8 argv arrays contain zero `#{`.** The three `create_process` modules are therefore **not** part of the interpolation surface at all.

### §1.5 The unresolvable 44, named

**44 of 130 sites (33.8%) did not resolve.** Reported as a result, not hidden. Causes, each with an instance:

| cause | instance | why it does not resolve |
|---|---|---|
| call site outside any `def` (top-level / `run` block without parseable bounds) | `linux/busybox/ping_net.rb:33` `#{ip}` | no enclosing method found → no assignment window |
| variable assigned from another local by a construct the tracer will not follow | `linux/gather/puppet.rb:81` `#{file[0]}` → `file := file.split(' ')` | split of an unresolved value |
| block/iterator variable (`|x|`) | `thunderbird_creds.rb:120` `#{path + item}` → `path` from an `each` block | block parameters are not `def` parameters |
| concatenation expression, not a bare name | `multi/gather/dns_srv_lookup.rb:81` `ns_opt + "#{srv}#{domain}"` | the token is an expression, not a name |
| OpenStruct / `profile['dir']` member access on an opaque object | `skype_enum.rb:125` `#{profile['dir']}` | provenance is inside the object, not in the file |

**I am not claiming these are unknowable in principle.** Each has a named next probe (§5.2–§5.4). **They are unresolvable *by this tracer*, and the count is what a lexical trace honestly yields.**

---

## §2 T2 — second arguments, and the delta

### §2.1 Definition, forced by the 3-argument calls

`cmd_exec(cmd, args = nil, time_out = 15, opts = {})`. **87 sites carry ≥2 arguments.** For the 4 sites with ≥3, the third argument is `time_out` — `saltstack_salt.rb:54` passes `datastore['TIMEOUT']`, `skype_enum.rb:144` the same, `rpcapd_start.rb:103` passes `30`. **So "second argument" is well-defined as the command tail, and I define it as the text between the first and second top-level comma.**

**Class distribution of the second argument:** `ABSENT 372 · LITERAL 30 · INTERPOLATED **28** · VARIABLE 19 · OTHER 11`.

### §2.2 The delta: 141 → 168

| basis | interpolated sites |
|---|---:|
| first argument only (D69's rule) | 141 |
| second argument only | 28 |
| **either argument** | **168** |
| **delta attributable to T2** | **+27** |

**Sites where both arguments interpolate: 0** — the two classes are disjoint, so the union is exact and no site is double-counted.

**Provenance of the 28:** `ALL_DATASTORE 8 · MIXED 5 · NON_DATASTORE 15`.

### §2.3 The four sites that justify T2 being asked

**T2 was called the cheap probe. It is not merely a count adjustment — it reaches a named injection pattern:**

`[source]` `windows/manage/enable_support_account.rb:128`
```ruby
cmd_exec('cmd.exe', "/c net user support_388945a0 #{datastore['PASSWORD']}")
```
`[source]` `windows/manage/rid_hijack.rb:193`
```ruby
cmd_exec('cmd.exe', "/c net user #{username} #{datastore['PASSWORD']}")
```

**Both interpolate an operator-supplied password into a shell command line as a separate argument. Both were classed LITERAL under D69's first-argument rule.** `AGENTS.md` names `cmd_exec("command #{user_input}")` as *the* injection pattern; these reach it through the second position.

Also `windows/manage/portproxy.rb:124,126` interpolate `datastore['LOCAL_PORT']` into a `netsh` rule, and `bitlocker_fvek.rb:104,113` interpolate `drive_letter` into `manage-bde`.

**The honest consequence:** any count built on the first argument alone **systematically under-reports**, because `cmd_exec('interpreter', "tail #{operator_data}")` is a common MSF idiom — the interpreter is the literal first argument and the operator data rides in the second.

---

## §3 What the two tasks together change

**D69 §2.5's `5 / 138 / 13` becomes, on the corrected basis:**

| | D69 §2.5 | D74 |
|---|---|---|
| interpolated sites, first-arg rule | 143 | **141** |
| interpolated sites, both-arg rule | not measured | **168** |
| interpolating **operator data** | 5 | **49 sites** (first arg) |
| interpolating target-returned content | not measured | **8 sites** |
| unresolvable by lexical trace | 138 (implied) | **44 sites** |

**The framing that changes:** D69 refused a headline number because "138 of 143 are unauditable at the call site." **The right refusal was correct and the reason was wrong.** 138 was not the size of an unknowable set — it was the size of an **untraced** set, and tracing it moved the largest single class (operator data) from 5 to 49. **The number to state is not "5 dangerous of 143"; it is "at least 49 sites interpolate operator-set data into a shell command line, 8 interpolate target-returned content, and 44 remain untraceable by this method with named causes."**

**What does not change:** the escaping question. **Provenance decides whether a value is adversary-influenceable; escaping decides whether interpolation reaches a shell.** D74 answers only the first. **A DATASTORE value in a quoted, escaped position is not automatically an exploitable injection** — `osx/capture/screen.rb` escapes `tmp_path` with `.shellescape`, and `grandstream_gxp1600_sip.rb:203` escapes quotes with `.gsub('"', '\\"')`. **D74 does not measure escaping, and any reader who takes the 49 as an exploit count is reading a number I did not produce.**

---

## §4 Instrument record

### §4.1 `[instrument]` — probe churn: 455 / 457 / 459 and 143 / 141

Four successive extractors reported **455, 457, and 459** total call sites and **143 vs 141** interpolated. The spread is comment-line filtering and multi-line call bodies. **The number I ship is 459 / 141, and both carry the invocation.** **Rule: when a series of probes disagree by small integers, the report must show the series, not just the survivor** — the D69 lesson (`a discarded probe is a control destroyed`) applied pre-emptively.

### §4.2 `[instrument]` — a greedy `\b`-adjacent regex returned the group, not the match

`INTERP.findall(r"#\{([^{}]|\{[^{}]*\})*\}`)` with **one** capturing group returns the group; `expr_class` then sliced `[2:-1]` off a non-match string. **Symptom: every one of 197 expressions classified `DATASTORE`.** `[measured]` The tell was the *echo* of `e` printing real interpolations while the class column said DATASTORE for all of them. **Fix: `finditer(...).group(0)`; never slice a presumed match.** **Rule: a classifier returning the same value for 100% of its input is broken, not decisive — print the input alongside the label.**

### §4.3 `[instrument]` — a class defined by "a dangerous function appears in the body"

`SESSION_TARGET` initially matched the literal string `cmd_exec` anywhere in a resolved body, so `ctl_path → whereis → cmd_exec("whereis #{exe}")` became SESSION_TARGET even though the tainted token was hardcoded. **15 → 9 expressions after correction.** **This is the D56 name-filter error relocated into a call graph: filtering by the presence of a callee's name instead of tracing what value the callee returns.**

### §4.4 `[instrument]` — an assignment-only tracer cannot see `def` or parameters

The first tracer reported `puppet_exe` unresolved across 142 call sites. `puppet_exe` is `def puppet_exe` at `puppet.rb:44` and returns `datastore['PUPPET']`. **Two resolutions were missing: `def`-as-provider and parameter binding.** **Rule: in Ruby, `foo` may be a local, an ivar, a method call, or a block parameter — a tracer that assumes local-or-unresolved manufactures unknowns.**

### §4.5 `[instrument]` — an `OTHER` bucket swallowed a real interpolation

Probe 8's `cls_of` classified `ns_opt + "#{srv}#{domain}"` as `OTHER` because it is not a single literal. **Method 2's independent count said 28 second-arg interpolations; probe 8 said 27.** Adjudication found the missing row. **D69 §6.6 already logged this species; it recurred here, which is evidence the species is chronic rather than incidental.**

### §4.6 `[instrument]` — cross-check by second method, and which figures are stable

| figure | method 1 | method 2 | verdict |
|---|---|---|---|
| argument-count distribution | 1:372, 2:64, 3:19, 4:4 | **identical** | **stable** |
| sites with ≥2 args | 87 | **87** | **stable** |
| second-arg interpolated | 27 | 28 | **adjudicated → 28** (§4.5) |
| total call sites | 459 | 463 raw / 421 blanked | **series reproduced, 459 retained** (§4.1) |

**One figure I must explicitly refuse to reconcile, because reconciling it would create a false agreement.** Three different `datastore` counts exist in this report and **they answer three different questions**:

| count | question it answers | invocation |
|---|---|---|
| **16** | how many interpolations contain the literal text `datastore[` | probe 1b |
| **62** | how many expressions *resolve* to datastore after `def` + parameter tracing | probe 7 |
| **49** | how many **sites** have DATASTORE as their highest-risk class | probe 7 |

**A windowed variant of the question ("does `datastore[` appear in the 300 chars following a call site") yields 49 by coincidence** — a different 49 from the 49 *sites*. **That coincidence is not agreement, and a reader who treats the two 49s as confirming each other has been misled by a numeric collision.** The shipped figures are the resolved pair, **62 expressions / 49 sites**, and neither is a count of `datastore[` text. **Recorded here rather than smoothed, because a table in which two different quantities share a value is a table that will be read wrong.**

---

## §5 Residual unknowns, each with a probe

**§5.1 Is the `REMOTE_RESPONSE = 0` a real zero or a rule artefact?** §1.3 argues a target HTTP response read via `cmd_exec("curl ...")` lands in SESSION_TARGET, not REMOTE_RESPONSE. **Probe:** for each of the 8 SESSION_TARGET sites, check whether the producing command's *output* is network content (`curl`, `wget`, SMB) rather than local state (`dmesg`, `nvram`, `grab_*`). **If any is network, REMOTE_RESPONSE is ≥1 and the class boundary needs a fourth rule.**

**§5.2 The 4 top-level sites with no enclosing `def`.** `ping_net.rb:33`, `remove_lock_root.rb:42`, `sub_info.rb:71`, `ecryptfs_creds.rb:54`. **Probe:** widen the search window to file scope for sites outside any method. **Expected yield: 4 sites, possibly all DATASTORE.**

**§5.3 Block-parameter and iterator provenance.** `thunderbird_creds.rb:120` derives `path` from an `each` block. **Probe:** parse `do |x|` / `{ |x| }` block headers between the assignment and the site, then trace the iterated collection. **This is the largest single unmodelled construct in T1.**

**§5.4 OpenStruct / hash-member provenance.** `skype_enum.rb:125` `profile['dir']`. **Probe:** resolve the constructor that builds `profile` and follow the hash key.

**§5.5 Escaping — the question D74 does not answer.** For the 49 DATASTORE sites, is the interpolated value ever `.shellescape`d, quote-escaped, or passed as a separate argv element? **Probe:** classify each of the 49 by sink shape. **This is the number that converts provenance into exploitability, and it is D45's boundary, not D74's.**

**§5.6 Does the same provenance profile hold on the exploit/auxiliary side?** D74 is `modules/post` only. **D45 measured the scanner/auxiliary side and did not do this trace. Probe: run `_d74_p7_prov3.py` with `POST` repointed at `modules/auxiliary`.**

---

## §6 Status

**Deliverable:** this file, sole owner `source-diver`.
**Files written:** this report; probes `_d74_p1_population.py`, `_d74_p1b_fixed.py`, `_d74_p2_sitesplit.py`, `_d74_p3_provenance.py`, `_d74_p4_diagnose.py`, `_d74_p5_prov2.py`, `_d74_p6_prov2.py`, `_d74_p7_prov3.py`, `_d74_p8_t2.py`, `_d74_p9_crosscheck.py`, plus `_d74_t1_raw.json`, `_d74_t1v2.json`, `_d74_t1v3.json`, `_d74_t2.json`. **Probes and JSON retained per instruction, not deleted** (verified on disk: 10 `.py`, 4 `.json`; the four JSON files are gitignored, the `.py` files untracked).

**Non-working probe retained deliberately, and labelled.** `_d74_p5_prov2.py` will not run — it references two helpers (`find_assign_in`, `find_assign_anywhere`) that were never defined; it was superseded mid-write by `_d74_p6_prov2.py`. **It is kept as the record of the false start that revealed blindnesses A/B/C, not as an instrument.** A retained probe that is silently broken is worse than a deleted one: **this line exists so that a later reader does not cite it.**

**Acceptance:** §0 leads with the corrections and names D69 §2.5 as the thing corrected. T1 answered with a stated rule, a populated provenance table, samples of every class, and a named unresolvable set (§1.5). T2 answered with a forced definition, the delta, and four consequence-bearing sites (§2.3). Every number carries its invocation. Second-method cross-check with stable/unstable labels (§4.6). Instrument record, 6 entries, including the one I got wrong twice.

**Not covered, named:** escaping (§5.5) is the exploitability half and belongs to D45. The exploit/auxiliary side (§5.6) is untraced.

**No verified artefact was modified.** D7/D8/D9/D22/D42/D58/D45/D69 untouched; D45 frozen by ruling and D69 frozen by ruling.
