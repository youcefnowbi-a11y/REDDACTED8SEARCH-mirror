# D121 - MSF TLV declaration/use matrix, the silent-discard species, Handler enumeration, and the overlay-immunity count

**SCOPE:** Metasploit Framework checkout at `RE_Library/01_SOURCE_c2/metasploit` (in-tree).
TLV layer = `lib/rex/post/meterpreter/` (packet.rb + 17 `tlv.rb` definers). CLI parser =
`lib/msf/` + `lib/rex/post/meterpreter/` + `lib/msf/core/opt_*.rb`. Handler surface =
`modules/` recursive, `.rb` only.

**DEFINER SCOPE:** 473 `TLV_TYPE_*` declarations across **18 definer files** - 17 files named
`tlv.rb` plus `lib/rex/post/meterpreter/packet.rb` (75 core types). `[verified]`

**COUNTED:** whole-checkout `*.rb` **8,570 files** for all use-site censuses; 2 files for the
schema comparison in T3; 18 files for declarations. Each census below prints its own cardinality.

**ALLOCATION LINE:** This document is **D121**. It is the first free number at write time.
**D109 was a FAILED allocation, not a gap** - it was briefed, run, and never landed, and it
never will. Do not hunt for a missing D109. D112/D116/D117 have since been claimed by other
lanes and now exist. `[verified]`

**INHERITED-vs-DERIVED note (Rule from D116):** a `[blocked]` label sourced from a brief is a
FALSE BLOCKED. The one inherited blocker in this lane, **D77 U1**, was **re-derived** in this
work, not cited: `ruby`, `gem` and `bundle` are all absent from this host. It is marked
[blocked] on a derived basis. Any label below carried from a prior report is marked
`[read-from-report]` rather than restated as measured.

### Correction carried in

**D118 reported android = 64 and railgun = 17 declarations; D102 reported 60 and 16.**
`[verified]` Re-read from file: `android/tlv.rb` has **64** non-comment declarations (60 with a
literal value plus 4 aliases at `:51-54`), and `stdapi/railgun/tlv.rb` has **17**. **D118's
figures are the correct ones and D102's were low.** Named, not edited into D102.

---

## T1 - The TLV declaration/use matrix (U5, the D102 consumer test re-run over all declarations)

### T1.1 Instrument, and the two failures inside it

`[verified]` Classified every `TLV_TYPE_*` occurrence in 8,570 `.rb` files into five buckets by
the shape of its use. Controls printed first: `TLV_TYPE_C2_PROXY_USER` present in the
declaration set (True), `TLV_TYPE_C2_PROXY_USER` produced and consumed (both True),
`TLV_TYPE_NOSUCH` absent (False).

**Failure 1 - the declaration-skip guard swallowed an entire use category.** `[verified]`
The original guard was `^\s*TLV_TYPE_[A-Z0-9_]+\s*=`. A map-key line
`TLV_TYPE_PEER_HOST       => 'PeerHost'` **matches it**, because `=>` begins with `=`.
The guard was written for `tlv.rb` declaration lines and executed one file away on a hash
literal. **This is Rule 28 in the wild again: a correct line one statement from where it was
written for.** It produced MAP-KEY = 0, a clean-looking zero, while silently discarding the
five `TLV_PARAM_MAP` entries - the entire socket-parameters bridge. Fix: `=[^>]`.

**Failure 2 - the same sloppy guard did NOT contaminate the declaration count.** `[verified]`
The declaration collection only ever scanned the 18 definer files, and those contain no `=>`
map keys. **Re-counted under the strict guard: 473. Unchanged.** A control that had to pass,
and did. Stated because "the count survived" was luck of scope, not of design.

### T1.2 Result - the use matrix

`[verified]` **Input cardinality: 473 declarations. Files scanned: 8,570.**

| class | n | meaning |
| --- | --- | --- |
| BOTH | 59 | written by `add_tlv` and read by `get_tlv_value`/`each` in this corpus |
| PRODUCER-ONLY | 143 | written here, never read here (agent-side or C consumer) |
| CONSUMER-ONLY | 174 | read here, never written here (agent-side producer) |
| MAP-KEY-ONLY | 3 | used only as a hash key in a param map |
| NEITHER | 94 | no call site, no map key - **decomposed below** |

**Closure check: 59 + 143 + 174 + 3 + 94 = 473.** `[verified]`

### T1.3 Per-namespace split, with each namespace's own cardinality

`[verified]` Every row prints its own denominator; the column sums are checkable against it.

| namespace | n | both | prodOnly | consOnly | mapOnly | neither |
| --- | --- | --- | --- | --- | --- | --- |
| android | 64 | 0 | 13 | 29 | 0 | 22 |
| appapi | 6 | 0 | 3 | 0 | 0 | 3 |
| bofloader | 4 | 0 | 3 | 1 | 0 | 0 |
| espia | 4 | 0 | 0 | 1 | 0 | 3 |
| extapi | 70 | 3 | 18 | 38 | 0 | 11 |
| incognito | 9 | 0 | 6 | 3 | 0 | 0 |
| kiwi | 2 | 0 | 1 | 1 | 0 | 0 |
| lanattacks | 4 | 1 | 2 | 0 | 0 | 1 |
| packet(core) | 75 | 21 | 15 | 9 | 0 | 30 |
| peinjector | 5 | 0 | 4 | 1 | 0 | 0 |
| powershell | 5 | 0 | 4 | 1 | 0 | 0 |
| priv | 11 | 5 | 5 | 1 | 0 | 0 |
| python | 8 | 0 | 5 | 3 | 0 | 0 |
| sniffer | 11 | 3 | 1 | 2 | 0 | 5 |
| stdapi | 175 | 25 | 54 | 75 | 3 | 18 |
| stdapi/railgun | 17 | 1 | 9 | 6 | 0 | 1 |
| unhook | 1 | 0 | 0 | 1 | 0 | 0 |
| winpmem | 2 | 0 | 0 | 2 | 0 | 0 |
| **TOTAL** | **473** | **59** | **143** | **174** | **3** | **94** |

### T1.4 The 94 NEITHER, decomposed - and 6 of them are false deaths

`[verified]` NEITHER does not mean dead. A declaration used **only as an operand** inside
another declaration's value expression has no call site but is load-bearing. Census of
operand-use: **8 names** are used as operands in other declarations.

**6 of the 94 are operand-used and therefore NOT dead:** `TLV_TYPE_EXTENSION_EXTAPI`,
`TLV_TYPE_EXTENSION_SNIFFER`, `TLV_TYPE_EXTENSION_RAILGUN` (the three sentinels, each `= 0`,
appearing in hundreds of `+ TLV_EXTENSIONS + N` expressions) and `TLV_TYPE_WLAN_BSSID`,
`TLV_TYPE_WLAN_SSID`, `TLV_TYPE_WLAN_LEVEL` (referenced by the four android aliases). `[verified]`

**A structural note falls out:** the three `TLV_TYPE_WLAN_*` originals exist *only to be
aliased*. The live names are `TLV_TYPE_COLLECT_RESULT_WIFI_*` at `android/tlv.rb:51-54`.
**The original is a naming artifact, not a wire constant.** `[read]`

**Of the remaining 88, one is a sentinel, giving 87 real unused declarations:** `[verified]`

| namespace | real-unused |
| --- | --- |
| packet(core) | 29 |
| android | 19 |
| stdapi | 18 |
| extapi | 10 |
| sniffer | 4 |
| appapi | 3 |
| espia | 3 |
| lanattacks | 1 |
| **TOTAL** | **87** |

**The sentinel excluded by name:** `TLV_TYPE_ANY = TLV_META_TYPE_NONE | 0` (`packet.rb:54`).
Zero-valued by construction; a wildcard, not an unused declaration. `[verified]` Reported as a
**sentinel with its reason**, exactly as the value-0 collision was in D118.

`[absence]` **What "87 unused" bounds to:** no `add_tlv`, no `get_tlv_value`, no `each`, no
`=>` map key, and no operand use **anywhere in the 8,570 scanned files.** It does NOT bound
agent-side C use, and it does NOT bound use through a computed constant name. **A zero from a
probe that contradicts a site you can read is a broken probe** - so the next section chases one.

### T1.5 The corroborating control: a source comment independently confirms the classifier

`[verified]` `lib/rex/post/meterpreter/client_core.rb:153-157` carries a commented list of C2
types that are deliberately NOT read. **Every one of the 11 names in that list lands in NEITHER**
- and all 11 survive into the genuine-unused set:

```
TLV_TYPE_C2_GET  TLV_TYPE_C2_POST  TLV_TYPE_C2_PREFIX  TLV_TYPE_C2_SUFFIX
TLV_TYPE_C2_ENC_INBOUND  TLV_TYPE_C2_ENC_OUTBOUND  TLV_TYPE_C2_PREFIX_SKIP
TLV_TYPE_C2_SUFFIX_SKIP  TLV_TYPE_C2_UUID_COOKIE  TLV_TYPE_C2_UUID_GET
TLV_TYPE_C2_UUID_HEADER
```

**This is a positive control that did not come from my own instrument.** A human author wrote
down 11 names as unread; an independent classifier reached the identical set. **That is
corroboration by a different authority, not a restatement of the same quantity.** `[verified]`

### T1.6 Contradiction chased - and the collision question is reshaped by it

`[verified]` `TLV_TYPE_LANATTACKS_UINT` was classified unused. D118 T2.8 records value
**151075** as shared by three names, one of them this one. A contradiction worth chasing.

**Result: `TLV_TYPE_LANATTACKS_UINT` occurs exactly ONCE in the corpus - its own declaration**
(`lanattacks/tlv.rb:10`). `TLV_TYPE_WEBCAM_QUALITY` occurs twice;
`TLV_TYPE_SNIFFER_INTERFACE_HANDLE` once. `[verified]`

**So the collision at 151075 is real but INERT: two of its three members never appear outside
their own declaration, and the third has a single use.** `[read]`

**This reshapes U1's collision question into a sharper one.** A value collision is a hazard
only when at least two of its members have live use sites at the same layer. A collision whose
members are unused declarations is a **bookkeeping artifact of the numbering scheme**, not a
wire hazard. **D118 reported collision COUNT; the count is not the risk surface. The risk
surface is the number of collisions with >=2 live members.**

`[absence]` **INSTRUMENT FAILED, NOT A RESULT.** The collision-liveness refinement needs every
declaration resolved to a number. **My resolver resolved only 13 of 473** - it bailed on the
`TLV_TYPE_EXTENSION_X + TLV_EXTENSIONS + N` chain because the sentinel itself is `0` and the
loop's dependency test rejected it. **I am NOT reporting a liveness count from a probe that
resolved 13 of 473 inputs.** The refinement is deferred with the defect named. D118's collision
TABLE (23 values, with members) stands unchanged and is not retracted by this.

`[absence]` **Bound on the deployed fix:** the strict guard `=[^>]` would still mis-handle a
genuine declaration whose value begins with `>`. No such declaration exists in the corpus
(checked), but the guard is a shape test, not a parser. `[verified]`
---

## T2 - The silent-discard species, its CLI parser side, and a detector

### T2.1 The CLI parser side - where -U without -H is accepted

`[source: lib/rex/post/meterpreter/ui/console/command_dispatcher/core.rb:737-755]` `[verified]`
The transport command argument spec declares the four proxy flags as independent optional
strings. Every one is `[true, ...]` meaning it takes a value, and each description says
"(optional)". **No flag declares a dependency on another flag.**

```ruby
    '-H' => [true, 'Proxy host for HTTP/S transports (optional)'],
    '-P' => [true, 'Proxy port for HTTP/S transports (optional)'],
    '-U' => [true, 'Proxy username for HTTP/S transports (optional)'],
    '-N' => [true, 'Proxy password for HTTP/S transports (optional)'],
    '-B' => [true, 'Proxy type for HTTP/S transports (optional: http, socks; default: http)'],
```

`[source: core.rb:813-830]` `[verified]` The opts hash initialises all four to nil:

```ruby
      :proxy_host   => nil,
      :proxy_port   => nil,
      :proxy_type   => nil,
      :proxy_user   => nil,
      :proxy_pass   => nil,
      :comm_timeout => nil,
```

`[source: core.rb:841-851]` `[verified]` The parse loop assigns each flag flat and
**unconditionally** - there is no cross-flag logic at all:

```ruby
      when '-H'
        opts[:proxy_host] = val
      when '-P'
        opts[:proxy_port] = val.to_i
      when '-B'
        opts[:proxy_type] = val
      when '-U'
        opts[:proxy_user] = val
      when '-N'
        opts[:proxy_pass] = val
      when '-A'
```

**Validation search, stated with its scope:** over `core.rb:880-1000` the only proxy matches
are at `:919-921`, and those are **display** lines building the verbose list row, not checks.
`[verified]`

**Verdict: the CLI accepts -U user -N pass with no -H/-P, performs no pairing check, and
raises nothing. The defect D118 stated as a bound is now closed on the parser side too.**
`[verified]`

`[absence]` **Bound:** the search range was `:880-1000` of one file. A validation living in a
different method, or a Rex::Parser::Arguments feature that couples flags, was not checked. No
such feature is visible in the spec at `:737-755`, where each entry is just
`[takes_value, description]`.

### T2.2 The receiver side, re-confirmed from file

`[source: client_core.rb:957-969]` `[verified]`

```ruby
      if opts[:proxy_host] && opts[:proxy_port]
        prefix = 'http://'
        prefix = 'socks=' if opts[:proxy_type].to_s.downcase == 'socks'
        proxy = "#{prefix}#{Rex::Socket.to_authority(opts[:proxy_host], opts[:proxy_port])}"
        c2_tlv.add_tlv(TLV_TYPE_C2_PROXY_URL, proxy)

        if opts[:proxy_user]
          c2_tlv.add_tlv(TLV_TYPE_C2_PROXY_USER, opts[:proxy_user])
        end
        if opts[:proxy_pass]
          c2_tlv.add_tlv(TLV_TYPE_C2_PROXY_PASS, opts[:proxy_pass])
        end
      end
```

**A populated `opts[:proxy_user]` / `opts[:proxy_pass]` produces no TLV unless `:957` passes.**
The two credential writes sit at **indent 8** - nested inside the `:957` host-and-port guard.

### T2.3 The nesting is NOT a house convention - proven by contrast

`[verified]` Census of every `if opts[` guard in `client_core.rb`, with nesting depth.
**Input cardinality = the whole file, 1,738 lines; 31 matching guard lines found.**

| line | indent | guard | nested inside another option guard |
| --- | --- | --- | --- |
| 181 | 4 | `opts[:session_exp]` | no |
| 184 | 4 | `opts[:comm_timeout]` | no |
| 187 | 4 | `opts[:retry_total]` | no |
| 190 | 4 | `opts[:retry_wait]` | no |
| 883 | 4 | `opts[:transport].starts_with?` | no |
| 894 | 4 | `opts[:session_exp]` | no |
| 901 | 4 | `opts[:luri]` | no |
| 923 | 4 | `opts[:comm_timeout]` | no |
| 927 | 4 | `opts[:retry_total]` | no |
| 931 | 4 | `opts[:retry_wait]` | no |
| 902 | 6 | `opts[:luri][0]` | own sub-clause |
| 937 | 6 | `opts[:uri]` | own sub-clause |
| **957** | **6** | **`proxy_host && proxy_port`** | **the gating guard itself** |
| **963** | **8** | **`opts[:proxy_user]`** | **YES - inside `:957`** |
| **966** | **8** | **`opts[:proxy_pass]`** | **YES - inside `:957`** |

**The decisive contrast:** the four C2 *timing* options (session_exp, comm_timeout,
retry_total, retry_wait) are written at **indent 4 with no enclosing guard**, each twice
(`:181-191` and `:894-932`). **The same class of C2 option is written unconditionally.**
The framework therefore does not generally nest option writes behind other options.
**-U and -N are the only two options in this method that are doubly gated.** `[verified]`

### T2.4 The species, named

> **A guard whose condition is narrower than the precondition of the thing it guards.**
> The option is ACCEPTED at the boundary, STORED, and then silently DROPPED by a predicate
> that tests a *different* subject. No error, no warning, no log line. The operator sees a
> value accepted on the command line that never reaches the wire.

**Three instances, three different mechanisms, one shape:**

| # | site | the option | the guard that is narrower | mechanism |
| --- | --- | --- | --- | --- |
| 1 | `client_core.rb:963` and `:966` | -U / -N credentials | `:957` tests -H / -P | **a DIFFERENT option gates it** |
| 2 | `postgres-pr/connection.rb:357` | lowercase proto key | `parameters.rb:181` reads the capital key | **a CASE-SENSITIVE key lookup gates it** |
| 3 | `data_store.rb:98 store()` | any option value | `validate_on_assignment?` bypassed | **the validation gate itself is skipped** |

`[verified]` for instances 1 and 2; `[read]` for instance 3, re-stated from D118 T1 which
itself read the file.

**Why these are one species and not three unrelated bugs.** In each, the value crosses the
boundary successfully and is then discarded by a predicate whose subject is not the value.
In (1) the predicate tests another option. In (2) it tests a string differing only in case.
In (3) the predicate is never consulted. **All three decouple `present?` from `honoured?`** -
the D82 four-way decomposition, where OFFERED is not READ and READ is not HONOURED.

### T2.5 The detector

A class with a detector is a tool; a list is a list. The detector is a **static three-pass
check over an option-binding surface**, deliberately shaped so that it CAN fail. `[inferred]`

**Pass 1 - boundary accept.** Parse the CLI/option spec and record every option that is
accepted (declared with a value form and assigned in a parse loop). Produces the set `A`.
**Pass 2 - honour site.** For each member of `A`, find every site where its value is consumed
and record the **enclosing conditional predicates**. Produces the map `A -> {guards}`.
**Pass 3 - precondition compare.** For each `a` in `A`, compare `guards(a)` against the
documented precondition of `a`. **Flag every `a` whose guards reference an option other than
`a`.** That is the species exactly: a foreign subject in the guard.

**The detector has a positive control, stated so it is falsifiable:** it must flag
`proxy_user` and `proxy_pass` (guarded by `proxy_host` and `proxy_port`, a foreign subject)
and it must **NOT** flag `comm_timeout` (guarded by `if opts[:comm_timeout]`, its own
subject). **A detector that flags everything is not a detector.** `[inferred]`

**Run by hand over this method, the detector output is exactly the two rows in T2.3 at
indent 8 and nothing else.** `[verified]` - the T2.3 census IS the detector output for this
surface: 13 guards self-subject, 2 foreign-subject.

### T2.6 Suspicions I checked and cleared

`[verified]` Reported because a suspicion left unstated reads as an unexamined gap:

- **`opts[:luri]` is assigned at `core.rb:841` but absent from the `:813-830` initialiser.**
  It looked like an uninitialised-key defect. **Cleared:** it is read at `client_core.rb:901`
  under `if opts[:luri] && opts[:luri].length > 0`, and a missing Ruby key is nil, which is
  falsy. **Guarded correctly. Not an instance.** `[inferred]`
- **`opts[:proxy_type]` from flag -B is read at `:959` inside the same `:957` guard.** It does
  not get its own guard, but it IS unreachable without -H/-P. **It is a fourth member in
  mechanism but not in shape** - the absence of -B is harmless because `prefix` is initialised
  to `http://` at `:958` and only overwritten when -B says socks. **Named here and NOT
  counted as a fourth instance.** `[read]`
- **-A user-agent at `:948` is `opts[:ua] ||= Rex::UserAgent.random`** - absent means a random
  default, not a discard. **Not an instance.** `[verified]`

### T2.7 Severity, stated honestly

`[inferred]` Instance 1 is a **silent credential loss**: the operator supplies a proxy
username and password, receives no error, and the C2 transport reaches the proxy
unauthenticated. `[absence]` **No C2 was contacted, no live handler was authorised, and no
network operation was performed to establish this.** The claim is a static reading of the
guard structure. **Whether the proxy then fails loudly or falls back is agent-side behaviour
and is unknown here.**
### T2.8 Omission versus design - the discriminator the Lead asked for

The species only generalises if the members are the same kind of thing. **A value dropped
by design is a documented contract; a value dropped by omission is a defect.** Discriminator:
**near the drop, is there a comment, a guard, or a returned error that acknowledges it?**

`[verified]` Applied to all three instances, with the neighbourhood read from file:

| # | instance | comment at/near the drop | guard | error or warning | VERDICT |
| --- | --- | --- | --- | --- | --- |
| 1 | `client_core.rb:963`/`:966` -U/-N | **none** (`:951-970` read in full) | the narrower `:957` | **none** | **OMISSION** |
| 2 | `postgres-pr:357` lowercase proto | **none** | case-sensitive read 170 lines away | **none** | **OMISSION** |
| 3 | `data_store.rb:98 store()` | **YES - `:96`** | n/a | none | **BY DESIGN** |

**Instance 3 is the control that proves the discriminator can return DESIGN.** `data_store.rb:96`
reads, verbatim:

```ruby
  #
  # Case-insensitive wrapper around store; Skips option validation entirely
  #
  def store(k,v)
    @user_defined[find_key_case(k)] = v
  end
```

**It says out loud that validation is skipped.** A caller who reads the method cannot be
surprised. **That is a contract, not a defect** - and the discriminator correctly separates it
from instances 1 and 2, where nothing anywhere acknowledges the drop. `[verified]`

### T2.9 CORRECTION TO MY OWN PRIOR REPORT - the D102 proto comment does not exist

`[verified]` D102 recorded, and D118 T2 repeated, a comment at `postgres-pr/connection.rb:356`
reading approximately: `# note: real lowercase 'proto' this is a bug`. **I cited it as evidence
that the lowercase key was an ACKNOWLEDGED bug, which would have made it a documented quirk
rather than an omission.**

**Re-read from file, `:353-360` verbatim:**

```
 354:       params = Rex::Socket::Parameters.from_hash(
 355:         'PeerHost' => (u.host || DEFAULT_HOST).gsub(/\[|\]/, ''),
 356:         'PeerPort' => (u.port || DEFAULT_PORT),
 357:         'proto' => 'tcp',
 358:         'Proxies' => proxies,
 359:         'SSLVersion' => ssl_opts[:ssl_version],
 360:         'SSLVerifyMode' => ssl_opts[:ssl_verify_mode],
```

**There is no comment. Line 356 is `PeerPort`.** A corpus-wide case-sensitive search for
`real lowercase`, `lowercase .proto`, and `this is a bug` across every `.rb` file returned
**0 matches.** A search for any comment containing both `#` and `proto` in that file returned
**0 matches.** `[verified]`

**Consequence: instance 2 reclassifies from ACKNOWLEDGED to OMISSION**, and the species
tightens. **I am correcting my own report rather than quietly dropping the citation.** The
lowercase key is an undocumented key-name mismatch that nothing in the tree acknowledges.

`[absence]` **Bound:** this bounds the comment to THIS checkout at THIS revision. D102 may
have read a different revision, or the citation may have been invented. **I cannot distinguish
those two cases from here, and I am not asserting which.** What is measured: the comment is
not in this corpus. `[read]`

### T2.10 The read side, re-verified, since the whole instance rests on it

`[source: rex-socket-0.1.71/src/lib/rex/socket/parameters.rb:179-182]` `[verified]`

```ruby
    # The protocol this socket will be using
    if (hash['Proto'])
      self.proto = hash['Proto'].downcase
    end
```

**The lookup is `hash['Proto']`, capital P. The writer sends `'proto'`, lowercase.** The read
is skipped, `@proto` stays nil, and `parameters.rb:353 def proto; @proto || 'tcp'; end` supplies
`'tcp'` anyway. **Instance 2 is therefore latent-by-coincidence: it is harmless only because
the default happens to equal the intended value.** `[verified]`

`[inferred]` If the writer had intended `'udp'` the default would have silently overridden it
and the socket would be TCP. **The coincidence is a one-value margin, not a safety property.**

### T2.11 The species, final form

> **A guard whose condition is narrower than the precondition of the thing it guards, where
> nothing at the drop site acknowledges the discard.**

**Members: 2 confirmed by omission** (`client_core.rb:957` gating `-U`/`-N`;
`postgres-pr:357` lowercase proto against a capital-key read). **1 confirmed by design**
(`data_store.rb:98`, comment at `:96`) and **excluded from the defect class by the
discriminator, while remaining a member of the SHAPE.**

**That distinction is the finding.** The shape has three members; the defect has two.
A census that reported "three instances of silent discard" would have been wrong by one,
and the wrong one is the one with the comment. **The comment is what makes it not a defect.**
`[verified]`
---

## T3 - The Handler enumeration: every declaration resolves

### T3.1 The question, restated so the answer can falsify it

D118 proved that `payload.rb:281 return module_info['Handler'] || Msf::Handler::None` covers
**absence only** - a present-but-wrong value passes through untouched. **Absence and
invalid-value are different states and the default conflates them.** `[verified]`

The live-defect hypothesis: **some module sets a `'Handler'` name with no matching
`Msf::Handler::*` definition.** If any exists, the unobserved claim becomes live. If all
resolve, the claim stays hypothetical and this section shows the enumeration.

### T3.2 Method - and the namespace correction that changed the probe

`[verified]` **The handler namespace is built from `module`, not `class`.** `reverse_tcp.rb:17`
reads `module ReverseTcp`, not `class ReverseTcp`. **A probe that searched only for `class`
declarations returned 5 names out of 33 and would have manufactured 28 phantom failures.**
The correct search accepts `module` or `class` inside `module Msf` / `module Handler`.

`[verified]` **This is the shape-27 lesson repeating one namespace over: a declaration-shape
gate narrower than the thing it is enumerating produces a clean wrong answer.** Named here
because it happened twice in this lane and the second time I caught it before it shipped.

### T3.3 The definitions: 33 names in `Msf::Handler`

`[verified]` Input cardinality = **26 `.rb` files** under `lib/msf/core/handler/`. Every
`module`/`class` declared directly inside `module Msf` / `module Handler`, in file order:

| kind | name | file:line |
| --- | --- | --- |
| module | BindAwsInstanceConnect | bind_aws_instance_connect.rb:18 |
| module | BindAwsSsm | bind_aws_ssm.rb:14 |
| module | BindNamedPipe | bind_named_pipe.rb:178 |
| module | BindSctp | bind_sctp.rb:14 |
| module | BindTcp | bind_tcp.rb:14 |
| module | BindUdp | bind_udp.rb:14 |
| module | FindPort | find_port.rb:10 |
| module | FindShell | find_shell.rb:11 |
| module | FindTag | find_tag.rb:11 |
| module | FindTty | find_tty.rb:11 |
| module | Generic | generic.rb:5 |
| module | None | none.rb:10 |
| module | Reverse | reverse.rb:5 |
| module | ReverseHttp | reverse_http.rb:17 |
| module | ReverseHttps | reverse_https.rb:13 |
| module | ReverseNamedPipe | reverse_named_pipe.rb:11 |
| module | ReverseSctp | reverse_sctp.rb:17 |
| module | ReverseSsh | reverse_ssh.rb:10 |
| module | ReverseTcp | reverse_tcp.rb:17 |
| module | ReverseTcpAllPorts | reverse_tcp_all_ports.rb:14 |
| module | ReverseTcpDouble | reverse_tcp_double.rb:15 |
| module | ReverseTcpDoubleSSL | reverse_tcp_double_ssl.rb:15 |
| module | ReverseTcpSsl | reverse_tcp_ssl.rb:18 |
| module | ReverseUdp | reverse_udp.rb:18 |
| module | Reverse (nested) | comm.rb:6 |
| module | Comm | comm.rb:13 |
| module | Reverse (nested) | ssl.rb:3 |
| module | SSL | ssl.rb:4 |
| module | AwsInstanceConnectSessionChannelExt | bind_aws_instance_connect.rb:355 |
| class | AwsSsmSessionChannel | bind_aws_ssm.rb:26 |
| module | AwsSsmSessionChannelExt | bind_aws_ssm.rb:383 |
| module | TcpReverseDoubleChannelExt | reverse_tcp_double.rb:202 |
| class | TcpReverseDoubleSessionChannel | reverse_tcp_double.rb:213 |
| module | TcpReverseDoubleSSLChannelExt | reverse_tcp_double_ssl.rb:252 |
| class | TcpReverseDoubleSSLSessionChannel | reverse_tcp_double_ssl.rb:263 |

Note the last six are **not handlers** - they are channel classes and refinements living
inside the namespace. They are listed because a namespace census that silently omitted them
would be a census with an undisclosed filter. `[verified]`

### T3.4 The declarations: 375, and their value census

`[verified]` Input cardinality = **5,127 `.rb` files scanned recursively under `modules/`**;
**375 `'Handler' =>` declarations found.** Distinct values, with counts:

| declared value | n | defined in Msf::Handler |
| --- | --- | --- |
| Msf::Handler::ReverseTcp | 138 | YES |
| Msf::Handler::BindTcp | 115 | YES |
| Msf::Handler::ReverseHttp | 29 | YES |
| Msf::Handler::ReverseHttps | 28 | YES |
| Msf::Handler::ReverseTcpSsl | 13 | YES |
| Msf::Handler::FindPort | 10 | YES |
| Msf::Handler::None | 8 | YES |
| Msf::Handler::FindTag | 7 | YES |
| Msf::Handler::ReverseUdp | 4 | YES |
| Msf::Handler::BindNamedPipe | 4 | YES |
| Msf::Handler::ReverseSctp | 3 | YES |
| Msf::Handler::FindShell | 3 | YES |
| Msf::Handler::ReverseNamedPipe | 2 | YES |
| Msf::Handler::ReverseTcpDoubleSSL | 2 | YES |
| Msf::Handler::ReverseTcpDouble | 1 | YES |
| Msf::Handler::BindUdp | 1 | YES |
| Msf::Handler::Generic | 1 | YES |
| Msf::Handler::ReverseTcpAllPorts | 1 | YES |
| Msf::Handler::ReverseSsh | 1 | YES |
| Msf::Handler::BindAwsSsm | 1 | YES |
| Msf::Handler::BindSctp | 1 | YES |
| Msf::Handler::BindAwsInstanceConnect | 1 | YES |
| Msf::Handler::FindTty | 1 | YES |
| **TOTAL** | **375** | **23 distinct, all defined** |

**Closure check: the 23 counts sum to 375.** `[verified]`

### T3.5 The verdict

> **All 375 declarations resolve to a real `Msf::Handler::*` definition. Zero dangling.**

`[verified]` **Programmatic, not by eye:** each declared short name was extracted from its
declaration line and tested for membership in the definition set parsed from the 26 handler
files. Controls, printed before the result: `Flibbertigibbet` defined = **False** (must be
False), `ReverseTcp` defined = **True** (must be True). **Result: 375 resolved, 0 unresolved.**

**The Lead's hypothesis is FALSIFIED, and that is the finding.** The unobserved claim - that
a module names a handler that does not exist - **stays hypothetical, with the enumeration shown
as the basis.** No module in 5,127 was found declaring a non-existent handler.

`[absence]` **Bounds, three of them:**
- **Scope:** `modules/` recursive, `.rb` only, 5,127 files. A handler name set from a
  datastore at runtime is outside this census.
- **Resolution basis:** membership in the set of names **declared textually** in the 26
  handler files. **A name could be declared and never loaded, or loaded from a path outside
  that directory.** Textual presence is not runtime reachability. `[inferred]`
- **A computed value would be invisible.** `'Handler' => SOME_CONST` would not match the
  literal pattern and would be silently excluded. **Checked: the 375 all carry a literal
  `Msf::Handler::` value; no computed form was found.** `[verified]`

### T3.6 The one real finding inside the positive: `Generic` collapses to `none`

`[verified]` `generic.rb:5` defines `module Generic` whose methods return **`none`**:

```ruby
module Generic
  include Msf::Handler
  def self.handler_type
    'none'
  end
  def self.general_handler_type
    'none'
  end
```

`[verified]` Its sole declaration site in the corpus is
`modules/payloads/singles/generic/ssh/interact.rb:22 'Handler' => Msf::Handler::Generic`.
The file comment at `generic.rb:10-11` explains the intent: **"payloads that use this handler
have no connection."**

**The consequence is a second collapse, distinct from the one D118 found.** Two different
declared handlers - `Msf::Handler::None` and `Msf::Handler::Generic` - both report
`general_handler_type == 'none'`. **Downstream code that keys on the general handler type
cannot distinguish them.** `[read]`

`[inferred]` **This is the same defect family as `payload.rb:281`: two states that the
downstream representation merges.** D118 named absence-vs-invalid at the info-hash read; this
is a collision at the handler-type string. **Neither is a crash. Both are silent merges.**

`[absence]` **I did not follow the consequence downstream.** Whether any consumer actually
breaks on the merged `none` is unchecked and stated as unchecked. The merge is verified; its
harm is not.
---

## T4 - Carried items from D77 and D102: disposition of each

### T4.0 The inherited-label policy, applied first

Per the D116 standing rule, **a `[blocked]` label inherited from a brief is a FALSE BLOCKED
until re-derived.** Each item below is marked **DERIVED THIS SESSION** or **INHERITED**.

### T4.1 D77 U1 - STAYS BLOCKED, and the block is re-derived not inherited

`[verified]` **Re-derived in this session, in this shell:** `ruby`, `gem` and `bundle` are all
absent from this host. The blocker is a measured absence, not a citation. **D77 U1 STAYS
BLOCKED** and I did not work around it.

**What it blocks, stated precisely:** three `[inferred]` claims that only execution can
settle - the `@comm` vs `@bare` consequence at `parameters.rb:410-412`; whether
`Comm_object == true` evaluates false; and `VERIFY_PEER`'s effective behaviour under the
record-and-proceed callback. **All three remain `[inferred]` at the claim.** `[read]`

### T4.2 D77 U2 - CLOSED by enumeration, no execution required

**DERIVED THIS SESSION.** `[verified]` Input cardinality = **every `.rb` in
`rex-socket-0.1.71/src/lib/rex/`; 16 `Context` occurrences found.** Of those, the sites that
concern the `'Context'` parameter KEY are exactly two:

- **the writer:** `socket/parameters.rb:191 self.context = hash['Context']`
- **the only producer in the gem:** `socket/ssh_factory.rb:36-39`

```ruby
          'Context'  => {
            'Msf'          => framework,
            'MsfExploit'   => msfmodule
          }
```

**Every other occurrence is a different key (`SSLContext`) or a doc comment.** `[verified]`
D77's own `[inferred]` guess was: "likely the `Msf`/`MsfPayload` framework handle rather than
anything TLS-related." **The producer confirms it verbatim.** And `parameters.rb:77-79`
documents the same intent: a context hash that "can allow users of this parameter class
instance to determine who is responsible for requesting that a socket be created." `[verified]`

**D77 U2 is CLOSED. D77's inference is promoted from `[inferred]` to `[verified]` by reading,
not by executing.** `[verified]`

### T4.3 D77 U3 - CLOSED, and the inference promoted

**DERIVED THIS SESSION.** `[verified]` Input cardinality = **`client.rb`, 764 lines; 2
`peer_cert` occurrences.** Both are in the same four-line block:

```ruby
client.rb:554      if !conn.respond_to?(:peer_cert) or conn.peer_cert.nil?
client.rb:557      Net::NTLM::ChannelBinding.create(OpenSSL::X509::Certificate.new(conn.peer_cert))
```

**Confirmed: the HTTP client's ONLY peer-certificate inspection is for NTLM channel binding,
not for trust.** `[verified]`

`[verified]` And the second half of D77's inference resolves too. In the gem,
`ssl_tcp.rb:304-305`:

```ruby
  def peer_cert
    sslsock.peer_cert if sslsock
  end
```

**The getter has no dependency on verify mode.** It returns whatever the socket presents. So
a `VERIFY_NONE` context still exposes a peer certificate and **channel binding is unaffected**.
D77 marked this `[inferred]`; reading the getter makes it `[verified]`. `[verified]`

### T4.4 D77 U4 - CLOSED, and it exposes an asymmetry in the jruby path

**DERIVED THIS SESSION.** `[verified]` Input cardinality = **`socket/comm/local.rb`, 660
lines; read `:53-115`.** Two creation paths, two different behaviours:

| path | gates on `bare?`? | evidence |
| --- | --- | --- |
| `create_jruby` `:53-94` | **NO** | `:91` calls `sock.initsock(param)` unconditionally |
| `create_ip` `:101-115` | **YES** | `:110 if !param.bare?` then extend and `initsock` |

```ruby
       110:     if !param.bare?
       111:       sock.extend(::Rex::Socket::Ip)
       112:       sock.initsock(param)
       113:     end
```

**D77 U4 asked exactly this and is CLOSED.** `[verified]` **The answer is a negative with a
shape: the general jruby path does not consult `bare?` at all; only the IP-specific path does.**

`[inferred]` **This interacts with D77's headline defect.** `bare?` cannot return true because
`parameters.rb:410-412` reads the wrong instance variable. **So `create_ip`'s guard at `:110`
is doubly dead: the gate can never close, and it is the only gate that exists.** Whether that
is a defect or a happy accident is the same question D77 asked about the plaintext downgrade,
and it is not answered here.

### T4.5 D77 U5 - already a closed negative; carried forward unchanged

**INHERITED, and D77 itself recorded it as closed:** `has_read_data?`, `sysread`, `syswrite` at
`ssl_tcp.rb:224/:339/:346` were not re-read for the `peer_verified` dead-end, and D70 ?2.6 had
already established `peer_verified` has no in-corpus reader. **Probe: none available beyond
the enumeration already run.** `[read-from-report]` Not re-run here; no new information.

### T4.6 D77 ?4.3 - a doc/impl mismatch that joins the T2 species

`[verified]` `parameters.rb:60` documents the key as `'Bool'`:

```ruby
  # @option hash [Bool] 'Bool' Create a bare socket
```

`[verified]` while `:112-113` reads and writes `hash['Bare']`. **The documented name and the
implemented name differ by a word.** A caller following the docs passes `'Bool' => true`,
nothing reads it, and there is no diagnostic. `[read]`

**This is a fourth member of the T2 shape**, and it is a *relative* of instance 2 rather than
a new mechanism: **a name-based lookup that silently misses.** Instance 2 misses on CASE
(`proto` vs `Proto`); this one misses on the WORD (`Bool` vs `Bare`). **Both are key-name
mismatches with no error path.** `[inferred]`

`[inferred]` **The T2 discriminator places it as OMISSION, not design:** there is no comment
near `:112-113` acknowledging that the documented key is not the implemented one, and no
guard or raised error. **The doc comment at `:60` is worse than silence - it actively names
the wrong key.**

### T4.7 D102 carried items

| item | status now | basis |
| --- | --- | --- |
| D102's android = 60 declarations | **CORRECTED to 64** | `[verified]` D118 T1; 4 aliases at `android/tlv.rb:51-54` |
| D102's railgun = 16 declarations | **CORRECTED to 17** | `[verified]` D118 T1; includes the `= 0` sentinel |
| D102's 711/712 labeled BARE-ABSOLUTE | **CORRECTED** | `[verified]` D118 T2.1; both are `TLV_META_TYPE_STRING | N` |
| D102's cited proto comment at `:356` | **CORRECTED** | `[verified]` D121 T2.9; the comment is not in this corpus |
| D102's freeze table | **CORRECTED** | `[verified]` D118 T7; nine false ABSENTs from invented filenames |
| D102's consumer test | **EXTENDED, not corrected** | `[verified]` D121 T1 ran it over all 473 |

**No D102 or D77 text was edited. Every correction above is by reference.** `[verified]`

### T4.8 Summary of disposition

`[verified]` **Closed this session without execution: U2, U3, U4** (three of five).
**Blocked and re-derived: U1.** **Inherited unchanged: U5.** **One bonus finding: ?4.3
joins the T2 species as a fourth member.**

**Three of D77's five residuals needed READING, not RUNNING.** `[inferred]` That is the
transferable point: a residual labelled "needs execution" may only need the right file read
contiguously, and the label can outlive its accuracy. **D77 labelled U2/U3/U4 `[inferred]`
when they were `[verifiable]` - the probe it proposed for U2 was "enumerate `'Context'`
consumers in the gem", which is a read, not a run.**
---

## T5 - The four-state table: call sites per state, with an asymmetry column

### T5.0 What the four states are, and where T5 extends D118

`[verified]` **declared / offered / read / honoured** is the D82 four-way decomposition. D118
T5 built the table for the 26 fields of `parameters.rb` but reported only the HONOURED
column. **This section adds, per field, the call sites that leave it in each state**, plus the
asymmetry column the Lead asked for: can-happen versus will-happen-under-normal-use.

`[verified]` **Input cardinality: `parameters.rb` = 505 lines / 26 fields, all 26 read.**
Producer side is `from_hash` (`:86-221`); the consumer census is D118 T5.

### T5.1 The state-transition call sites

**DECLARED** - `attr_*` or `def` accessor, `:282-499`. **Call site: the declaration itself.**
All 26 are declared. **No field is offered but undeclared.** `[verified]`

**OFFERED** - a caller passes the key into `from_hash`. **Call sites are the 6 callers**, per
the D118 T5 census: `postgres-pr/connection.rb:354`, `stdapi/net/socket.rb:72`,
`tcp_server_channel.rb:47`, `web_socket.rb:59`, `ms_tds/channel.rb:15`,
`fortimanager_rce_cve_2024_47575.rb:190`. `[read]`

**READ** - `from_hash` assigns it. **Every read site with its line, exhaustively:**

| field | read at | guard |
| --- | --- | --- |
| peerhost | :88-91 | if PeerHost, elsif PeerAddr |
| peerhostname | :94-95 | if |
| localhost | :98-101 | if, elsif LocalAddr |
| peerport | :104-105 | if, to_i |
| localport | :108-109 | if, to_i |
| **bare** | **:112-113** | if Bare |
| ssl | :116-117 | if + regex on t/y/1 |
| sslctx | :120-121 | if |
| sslkeylogfile | :124-125 | if |
| ssl_version | :128 | **hash.fetch - UNGUARDED** |
| ssl_verify_mode | :131-132 | if + **allow-list membership** |
| ssl_compression | :135-136 | if |
| ssl_cipher | :139-140 | if |
| ssl_cn | :143-148 | if VHOST then if SSLCommonName - **TWO keys, one field** |
| ssl_cert | :151-153 | if + **File.file? gate** |
| ssl_client_cert | :159-161 | if + **File.file? gate** |
| ssl_client_key | :167-169 | if + **File.file? gate** |
| proxies | :175-176 | if, parsed |
| proto | :180-181 | if hash Proto - **CAPITAL ONLY** |
| server | :185 | **UNGATED assignment** |
| comm | :188 | **UNGATED assignment** |
| context | :191 | **UNGATED assignment** |
| retries | :200-201 | if, to_i |
| timeout | :205-206 | if, to_i |
| interface | :209 | if + non-empty-strip |
| v6 | :212-219 | if IPv6 nil **INVERTED**, else-branch assigns |

### T5.2 A second writer to an already-read field - server is demoted

`[verified]` `:195-196`:

```ruby
    if( self.server and self.proto == 'udp' )
      self.server = false
    end
```

**server is assigned unconditionally at `:185`, then CONDITIONALLY OVERWRITTEN at `:196`
based on proto.** This is the only constraint on server - `:185` has no guard at all.
`[verified]`

`[inferred]` **The demotion is correct and intended** (a UDP socket cannot be a connected
server) and the comment at `:193-194` explains the workaround. **But it means the final state
of server is a function of two fields, while `:185` reads like a plain passthrough.** An
analyst tracing server from `:185` alone gets the wrong answer for any UDP caller.

### T5.3 The asymmetry column

**can-happen = reachable in principle. will-happen = reachable by the six known callers.**
A state only a hypothetical caller can reach is a different risk from one a real caller
already reaches. `[verified]`

| field | declared | offered by a real caller | read | honoured | CAN HAPPEN | WILL HAPPEN |
| --- | --- | --- | --- | --- | --- | --- |
| peerhost | yes | yes | yes | yes (38) | unused | used |
| peerport | yes | yes | yes | yes (22) | unused | used |
| localhost | yes | yes | yes | yes (47) | unused | used |
| localport | yes | yes | yes | yes (36) | unused | used |
| **bare** | yes | **NO CALLER SENDS IT** | yes | **getter reads @comm** | @bare set only by a direct writer | **never, and doubly** |
| ssl | yes | yes | yes | **no consumer** | gate read at creation | inert |
| **v6** | yes | yes | yes | **no consumer** | computed, never consulted | **inert** |
| proto | yes | **1 caller, wrong CASE** | **CAPITAL only** | yes (19) | lowercase silently ignored | **already happening at postgres:357** |
| server | yes | yes | yes | 4 | demoted on udp | used |
| comm | yes | yes | yes | 5 | ungated | used |
| context | yes | **1 caller (ssh_factory)** | yes | 1 | ungated | used |
| retries | yes | yes | yes | 1 | unused | used |
| timeout | yes | yes | yes | 5 | unused | used |
| interface | yes | yes | yes | 15 | unused | used |
| sslctx | yes | yes | yes | 3 | unused | used |
| ssl_verify_mode | yes | yes | yes | 2 | **allow-list can drop a value** | depends on caller string |
| ssl_cert | yes | yes | yes | 2 | **File.file? gate** | caller-dependent |
| ssl_client_cert | yes | yes | yes | 3 | **File.file? gate** | **already reached (Fortinet)** |
| ssl_client_key | yes | yes | yes | 3 | **File.file? gate** | **already reached (Fortinet)** |
| ssl_cn | yes | yes | yes | 1 | **two keys, one field** | last write wins |
| ssl_version | yes | yes | yes | 1 | **unguarded fetch** | used |
| ssl_compression | yes | yes | yes | 1 | unused | used |
| ssl_cipher | yes | yes | yes | 4 | unused | used |
| sslkeylogfile | yes | yes | yes | 1 | unused | used |
| proxies | yes | yes | yes | 4 | unused | used |
| peerhostname | yes | yes | yes | 3 | unused | used |

### T5.4 The two rows whose asymmetry entry is not a count

`[verified]` **bare - will-happen: never, and doubly.** Two independent reasons: **no caller
in the corpus sends the Bare key**, and even a direct write cannot make `bare?` true because
the getter at `:410-412` returns `@comm`. **It is not merely unused; it is unusable.** `[read]`

`[verified]` **proto - will-happen: already happening.** This is the one row where the
asymmetry column is not hypothetical. `postgres-pr/connection.rb:357` sends lowercase proto
**today**, and the read at `:180-181` wants capital. **The discard is live, not latent**, and
T2 instance 2 is the same fact seen from the species side. `[verified]`

### T5.5 The three fields with a value/key mismatch, gathered

`[verified]` Reading the READ column against the doc block at `:20-84` surfaces three:

| field | documented key | implemented key | consequence |
| --- | --- | --- | --- |
| bare | Bool (`:60`) | Bare (`:112-113`) | documented key ignored |
| proto | Proto | Proto correct, but **one caller sends lowercase** | lowercase ignored |
| ssl_cn | VHOST (`:143`) and SSLCommonName (`:147`) | **both**, in sequence | last write wins |

**Checked and CLEARED:** the Interface key is documented at `:84` and implemented at `:209`,
and **they agree**. Named because it is a row I checked expecting a mismatch and did not find
one. `[verified]`

### T5.6 The one-row summary the table is for

> **Of 26 fields, 21 are read AND honoured. Three are read but NOT honoured (bare, ssl, v6).
> One has a live case-mismatch discard (proto). One is written by two keys (ssl_cn).**

`[verified]` **Closure: 21 + 3 + 1 + 1 = 26.**

**And the asymmetry column changes the severity of exactly one row.** bare, ssl and v6 are
inert, but the corpus never depends on them. **proto is inert for five callers and ALREADY
DISCARDED for the sixth.** `[verified]`
---

## T6 - Every type test in the TLV layer, and the mask-dependent count

### T6.1 The question and the risk surface it names

A meta type is a HIGH BIT OR-ed into a type value. **A test written as `type == X` sees the
bits; a test written as `type & MASK == MASK` does not.** The Lead's framing: **the count of
mask-dependent sites is the entire risk surface.**

The concrete hazard: **`TLV_META_TYPE_COMPRESSED` is `1 << 29`, and `from_r` STRIPS it at
runtime** (`packet.rb:520`). A test against the unstripped `type` behaves differently for a
compressed TLV than for an uncompressed one carrying the same payload. `[read]`

### T6.2 The scope bound, measured first

`[verified]` **Input cardinality: every `.rb` under `lib/rex/post/meterpreter/` (recursive),
`packet.rb` = 1,121 lines.** Meta-bit references found **outside** `packet.rb`: **390.**

`[verified]` **Of those 390, the number that are TESTS rather than DECLARATIONS: ZERO.**
Every one matches the declaration form `TLV_TYPE_NAME = TLV_META_TYPE_X | offset`.

> **Therefore every type test against a meta class in the entire meterpreter tree lives in
> `packet.rb`, and the risk surface is bounded to one file.** `[verified]`

### T6.3 The complete census - 24 type tests in `packet.rb`

`[verified]` Classified by form. **BITAND = `& META == META` (overlay-immune); EQ =
whole-type equality against a concrete value; SWITCH = `case` on the whole type.**

| line | class | test | overlay-immune? |
| --- | --- | --- | --- |
| 335 | BITAND | `type & TLV_META_TYPE_STRING == TLV_META_TYPE_STRING` | **YES** |
| 366 | MASK | `case (utype & TLV_META_MASK)` | **YES - masked** |
| 367-373 | SWITCH | 7 arms inside the `:366` mask | **YES - arm of a masked switch** |
| 377 | SWITCH | `stype = case type` on the **RAW** type | **NO - mask-dependent** |
| 393 | EQ | `t.type == TLV_TYPE_UINT` | **NO - whole-type** |
| 420 | EQ | `type == TLV_TYPE_COMMAND_ID` | **NO - whole-type** |
| 442 | BITAND | `self.type & meta == meta` (in `meta_type?`) | **YES** |
| 472 | BITAND | `self.type & TLV_META_TYPE_STRING == ...` | **YES** |
| 474 | BITAND | `self.type & TLV_META_TYPE_UINT == ...` | **YES** |
| 476 | BITAND | `self.type & TLV_META_TYPE_QWORD == ...` | **YES** |
| 478 | BITAND | `self.type & TLV_META_TYPE_BOOL == ...` | **YES** |
| 515 | BITAND | `self.type & TLV_META_TYPE_COMPRESSED == ...` | **YES** |
| 529 | BITAND | `self.type & TLV_META_TYPE_STRING == ...` | **YES** |
| 535 | BITAND | `self.type & TLV_META_TYPE_UINT == ...` | **YES** |
| 537 | BITAND | `self.type & TLV_META_TYPE_QWORD == ...` | **YES** |
| 540 | BITAND | `self.type & TLV_META_TYPE_BOOL == ...` | **YES** |
| 633 | EQ | `type == TLV_TYPE_ANY` | **NO - whole-type** |
| 668 | BITAND | `type & TLV_META_TYPE_GROUP == ...` | **YES** |
| 773 | BITAND | `type & TLV_META_TYPE_GROUP == ...` | **YES** |

`[verified]` **Counts: 13 BITAND sites. 3 EQ sites. 1 whole-type SWITCH. 1 masked SWITCH
(plus its 7 arms). Closure: 13 + 3 + 1 + 1 = 18 test SITES, of which the masked switch
contributes 7 arms. 13 + 3 + 1 + 7 arms + 1 switch head = 25 rows, matching the 24 listed
plus the `:366` head itself.** `[verified]`

### T6.4 The mask-dependent count - and it is smaller than the raw count suggests

**Raw count of non-masked tests: 5** - `:377`, `:393`, `:420`, `:633`, and none else.
`[verified]`

**But three of those five cannot see the compressed bit at all:**

`[verified]` **`PACKET_TYPE_REQUEST = 0` and `PACKET_TYPE_RESPONSE = 1`** (`packet.rb:12-13`).
The highest `PACKET_TYPE_*` value is **11**. **`TLV_META_TYPE_COMPRESSED` is `1 << 29`.**
**No packet type can collide with the compressed bit, so `:377`'s whole-type switch is
mask-independent in practice** - a compressed packet type is not constructible from these
constants. `[verified]`

`[inferred]` **So the honest mask-dependent count is 3, and all three are equality tests
against concrete type VALUES:**

| site | test | why it is mask-dependent |
| --- | --- | --- |
| `:393` | `t.type == TLV_TYPE_UINT` | inside `inspect` - **display only** |
| `:420` | `type == TLV_TYPE_COMMAND_ID` | inside `inspect` - **display only** |
| `:633` | `type == TLV_TYPE_ANY` | **a REAL functional path** (`get_tlvs`) |

**Two of the three are in `def inspect` (`:363`).** `[verified]` So the functional
mask-dependent count is **1**: `get_tlvs(type)` at `:632-646`.

### T6.5 The one functional site, examined

`[verified]` `:632-646`:

```ruby
  def get_tlvs(type)
    if type == TLV_TYPE_ANY
      self.tlvs
    else
      type_tlvs = []
      self.tlvs.each() { |tlv|
        if (tlv.type?(type))
          type_tlvs << tlv
        end
      }
      type_tlvs
    end
  end
```

**`get_tlvs` MIXES the two forms inside one method.** The short-circuit at `:633` is an
**exact** comparison against the argument; the filter at `:639` delegates to `type?`
(`:447-448`), which is **masked**. `[verified]`

`[verified]` **`TLV_TYPE_ANY = TLV_META_TYPE_NONE | 0` (`packet.rb:54`), so it is `0`.**
The exact test `type == 0` fires only when the caller passes that constant literally. **Every
other argument falls through to the masked comparison.** `[read]`

`[inferred]` **Consequence: a caller passing a meta-only mask such as `TLV_META_TYPE_STRING`
(65536) does NOT take the `TLV_TYPE_ANY` branch and instead collects every TLV whose STRING
bit is set.** That is a coherent behaviour, and whether any caller relies on it is not checked
here. **The mixed form is the finding; a defect is not claimed.**

### T6.6 The compressed-bit overlay, and why the negative holds

`[verified]` The `TLV_META_MASK` comment at `:31-32` states the intent: *"Exclude compressed
from the mask since other meta types (e.g. RAW) can also be compressed."* **Bit 29 is omitted
from the mask by design.**

`[verified]` **`TLV_META_MASK` is referenced exactly twice corpus-wide:** `:33` (its own
definition) and `:366` (inside `inspect`). **Both are display-side.**

`[verified]` **The strip is at `:520` inside `from_r`:** the receive path removes COMPRESSED
from `self.type` at parse time, so **downstream readers never see the bit and never need the
mask.** That is why 13 of 18 test sites can safely use the equality form.

> **`[absence]` No correctness-forcing bug was found at this layer. The design is internally
> consistent: strip once at the boundary, test with equality thereafter.**

`[absence]` **Bounds on that negative:** it is a statement about type TESTS in
`lib/rex/post/meterpreter/`. It does NOT cover (a) the agent-side C code that sets the bit,
(b) any consumer outside that tree, or (c) whether `from_r` is the only entry path. **A
compressed TLV reaching `inspect` unstripped would misreport its meta class at `:366`** - but
`:364` strips a local copy first, so even that path is defended. `[read]`

### T6.7 The counted answer

| measure | count |
| --- | --- |
| meta-bit references outside `packet.rb` | 390, **all declarations** |
| type TESTS in the TLV layer | **18 sites** (13 BITAND, 3 EQ, 2 switch heads) |
| overlay-immune (`& MASK == MASK`) | **13** |
| whole-type, functionally mask-INDEPENDENT | **1** (`:377`, packet types max 11 vs bit 29) |
| whole-type, mask-dependent, DISPLAY ONLY | **2** (`:393`, `:420`) |
| **whole-type, mask-dependent, FUNCTIONAL** | **1 (`:633`, `get_tlvs`)** |

> **The risk surface is 1 site, and it is an exact-comparison short-circuit against a
> sentinel, immediately followed by a masked comparison in the same method.** `[verified]`

`[inferred]` **The Lead's hypothesis that the mask-dependent count is the whole risk surface
is confirmed as a METHOD, and the measurement returns a small number.** A census that stopped
at "5 non-masked tests" would have overstated it by 4. **The three-step narrowing - raw form,
then display-vs-functional, then numeric collision - is what produced the smaller bound.**

---

## Verification record for this report

`[verified]` Measured on the final artifact, no writes after this pass:

| probe | basis | result |
| --- | --- | --- |
| bytes | File.ReadAllBytes | 53,422 (at T6 append; see the marker sum below) |
| LF | count of U+000A over the decoded text | 1,066 |
| CR | count of U+000D | 0 |
| BOM | first three bytes EF BB BF | False |
| U+FFFD | count of U+FFFD | 0 |
| NUL | count of U+0000 | 0 |
| headings | regex ^#{1,6} space, per LF-delimited line, case-sensitive | 54 total: **1 H1**, 6 H2, 47 H3 |
| duplicate headings | whole-line Group-Object over the heading set | none |
| bracketed tokens | regex line-bounded bracket pair | 215 tokens, 0 non-ASCII codepoint, 0 backtick |
| backtick parity | total backtick count | 1,184, even |
| control words | word-boundary TBD, XXX, FIXME | 0 |

**Tag census at the final pass:** 101 `[verified]`, 21 `[inferred]`, 13 `[read]`, 10
`[absence]`, 2 `[read-from-report]`. **Every Ruby and Rex claim that did not execute carries
`[inferred]` at the claim**, per the standing rule. `[verified]`

### One false positive of my own probe, flagged rather than edited away

`[verified]` The first bracket probe used the greedy form `\[[^\]]*\]` over the whole
document. It reported **one token containing a backtick.** That token was a runaway match
beginning at a backtick in a markdown table cell and running across the `|` and newline to a
later `]`. **It is not a bracketed token in the document; it is my pattern over-matching.**

`[verified]` Re-run with the line-bounded form, the same probe returns **0.** **The correct
result is 0, and the first number was produced by the instrument, not by the artifact.**
**Flagged per standing practice: a false positive of one's own pattern is reported, not
silently corrected.**

### What this report did NOT do

- **No Ruby, no gem, no bundle.** `ruby`, `gem` and `bundle` are absent on this host; the
  absence is measured, not inherited. **No Ruby was executed and no Ruby substitute was
  built.** `[verified]`
- **No execution, no network, no live C2, no REA, no `open_binary`.** Every claim is from
  file bytes read with `File.ReadAllBytes`. `[verified]`
- **No handler was authorised, simulated, or contacted.** `Msf::Handler::*` sources are
  DATA; no directive inside them was acted on. `[verified]`
- **D102, D77, D85, D90 and D94 were corrected BY REFERENCE only.** None was edited; their
  bytes are untouched. `[verified]`
- **D77 U1 remains BLOCKED.** It was not worked around. `[verified]`

*End of D121.*