# D82 — `SSLVerifyMode` in three places, the `Context`/`SSLContext` key census, and the refutable one-line probe

**Task:** D82 (T1 refutation spec for D77 §1.2; T2 the `Context` key; T3 the datastore side of `ssl_verify_mode`)
**Lane:** metasploit core
**Status:** COMPLETE
**Deliverable:** `RE_Library\07_OUTPUT\reports\DEEP\D82_msf_verify_mode_three_places_and_context_key_census.md` (write scope: this file only)
**Method:** pure source. **Ruby is absent on this host — nothing was executed.** Every Rex/OpenSSL contract claim is `[inferred]`.
**Tags:** `[verified]` / `[read]` / `[inferred]` / `[absence]`. **Line counts are LF-delimited lines** (`-split "\r?\n"`), counting a final unterminated line as a line.
**Numbering:** `D82` confirmed **UNOCCUPIED by enumeration** before writing — see §0.1.

---

## §0 Corrections

### §0.1 Occupancy checked by enumeration, not memory

```powershell
Get-ChildItem $DEEP -File | Where-Object { $_.Name -match '^D8|82' }
```
```
D8_msf_exploit_side.md                                        50353 B
D80_covenant_false_positive_tasks_and_taskingtype_reach.md    28713 B
```
**`[verified]` Neither is D82. Total files in `DEEP` = 103.** Control in the same invocation: the pattern `^D7` returned **11** files. **The probe bites; the absence is bounded.**

**`[verified]` `D81` is also unoccupied** — recorded because the number was not asked for and a later lane may need it.

### §0.2 A correction to D70 §2.3 — the `NONE` at `:170` is NOT inert

**D70 §2.3 stated that `openssl_altchainsforgery_mitm_proxy.rb:170`'s `'SSLVerifyMode' => 'NONE'` is a no-op because `makessl` never reads `ssl_verify_mode`.** **That is WRONG, and the reason is that I read one site as one construction.**

**`[verified]` The method contains TWO socket constructions, and they are different calls:**
```ruby
:145    @proxy = Rex::Socket::SslTcpServer.create(      # SERVER
:146      'LocalHost' => local_host,
:147      'LocalPort' => local_port,
:148      'SSLContext' => context,                      # <-- the one 'SSLContext' pass site
:149      'Context' => { 'Msf' => framework, 'MsfExploit' => self }
:154    )

:166    server = Rex::Socket::Tcp.create(               # CLIENT  <-- different primitive
:167      'PeerHost' => host,
:168      'PeerPort' => port,
:169      'SSL' => true,
:170      'SSLVerifyMode' => 'NONE',                    # <-- CLIENT connect
:171      'Context' => { 'Msf' => framework, 'MsfExploit' => self }
:176    )
```

**`[inferred]` `:170`'s `'SSLVerifyMode' => 'NONE'` is passed to `Rex::Socket::Tcp.create` — a CLIENT connect — where `ssl_tcp.rb:116` DOES read `ssl_verify_mode`.** The value is **live, not inert.** D70 §2.3's classification was applied to the wrong construction.

**`[inferred]` The corrected count: of the two `'SSLVerifyMode' => 'NONE'` sites D70 identified as server-side, ONE is server-side and inert (`jsse_skiptls_mitm_proxy.rb:132`, passed to a server creation) and ONE is client-side and live (`openssl_altchainsforgery:170`).** I did not re-verify `jsse_skiptls` in this pass — see **U1**, which is the honest bound on this correction.

**`[inferred]` The lesson is Rule 20's opposite face.** D70 counted **sites** (`'SSLVerifyMode' => 'NONE'` appeared twice) and inferred a shared context. **The primitive is `Rex::Socket::SslTcpServer.create` vs `Rex::Socket::Tcp.create`** — and enumerating *that* separates the two. **A census of the value is not a census of the primitive.**

### §0.3 A correction to D58/D70's `'SSLContext'` caller count

**D58 and D70 recorded `'SSLContext'` as having "1 in-corpus caller," citing `openssl_altchainsforgery:148`.** The census below finds the key written at `parameters.rb:120-121` and passed at exactly one site — **`:148` is correct.** **`[verified]` But the count of 1 was reached by naming a known path, not by enumerating.** This pass enumerated; **`'SSLContext'` key-passing total = 0 by pattern, 1 by inspection of `:148`** — the pattern missed it because `:148` uses `'SSLContext' => context,` and my first regex required `(=>|:)` after the quote while the literal has a space. **Named result right, method wrong.** See §6.2.

---

## §1 T1 — the one-line probe, stated so it can FAIL

### §1.1 The claim under test

**`[inferred]` D77 §1.2 asserts a crossed wire in `parameters.rb`:**
- `:409` `attr_writer :bare` — the writer writes **`@bare`**
- `:410-412` `def bare` → **`@comm || false`** — the reader reads **`@comm`**
- `:282-283` `def bare?` → `return (bare == true)` — an **exact** comparison, not truthiness
- `:188` `self.comm = hash['Comm']` — `@comm` receives a **Comm object** on real sockets

**`[inferred]` Predicted result of the probe: `false`, on two independent grounds** — (a) `@comm` is a Comm object, and `Comm_object == true` is `false`; (b) even if `@comm` were `nil`, `bare` returns `false` and `false == true` is `false`.

### §1.2 The probe

```ruby
p Rex::Socket::Parameters.from_hash('Server' => true, 'SSL' => true, 'Bare' => true).bare?
```

**`[inferred]` What this line would prove if it returns `false`:** that passing the documented key with the value the documentation implies produces a parameter object whose `bare?` is `false`. **That is the crossed wire, observed end-to-end through the public interface, with no reference to `@comm` or `@bare` by name.**

**`[inferred]` Why this line and not a narrower one:** it exercises `from_hash` (`:112-113` write), the accessor (`:410-412` read), and `bare?` (`:282-283` comparison) in one expression. **A probe that reads `bare` directly would isolate the accessor; this one tests the feature as a caller would use it.** Both are useful; this one is the load-bearing one because it is the caller's path.

### §1.3 REFUTATION CONDITIONS — what would falsify the finding

**`[inferred]` The finding is refuted by any of the following. Each names a distinct mechanism, and each is independently checkable:**

**R1 — `bare?` returns `true`.** The crossed-wire claim is dead immediately: if the reader returns `@bare`'s value in practice, then either the source I read is not what runs, or Ruby resolves `@comm` to something `== true`. **A single `true` refutes the whole of D77 §1.2.**

**R2 — `Parameters.from_hash` does not route `'Bare'` through `:112-113`.** If `from_hash` is not the constructor I read, or `'Bare'` is consumed earlier and transformed, the write may never reach `@bare`. **Refutes the mechanism, not necessarily the conclusion.**

**R3 — `@comm` is never a Comm object at the moment `bare?` is called.** If `:188`'s assignment is deferred, overridden, or the hash omits `'Comm'` on this path, then `@comm` is `nil`, `bare` returns `false`, and `bare?` is false — **the same observable result by ground (b) rather than ground (a).** **This refutes ground (a) but NOT the finding.** Stated separately because it is the most plausible partial refutation.
- **The probe in §1.2 passes `'Server'` and `'SSL'` but NOT `'Comm'`** — so under R3 the probe still returns `false`, via `nil`. **A `false` from this probe therefore does not by itself distinguish ground (a) from ground (b).** The discriminating variant is:
  ```ruby
  p Rex::Socket::Parameters.from_hash('Comm' => Rex::Socket::Comm::Local).bare
  ```
  **`[inferred]` If this returns a Comm object, ground (a) is confirmed and the reader is demonstrably reading `@comm`. If it returns `false`, ground (a) is wrong and only ground (b) survives.**

**R4 — Ruby's `BasicObject#==` or a Comm override makes `Comm == true` true.** **`[inferred]` Refuted by inspection: no `==` override on the Comm class was found in this pass, and `Object#==` is identity.** **Not fully bounded** — see U2.

**R5 — `attr_writer :bare` does not create `@bare`.** It does, by Ruby's `attr_writer` contract. **`[inferred]`, and it is the least interesting refutation because it would mean the source is not Ruby 3.x as documented.**

### §1.4 What a `false` return does and does NOT establish — given `:283` is an exact `== true`

**This is the part where the probe's power is easy to overstate, and the brief asked for it explicitly.**

**`[inferred]` A `false` return ESTABLISHES:**
1. **The key `'Bare' => true` does not produce a bare-flagged parameter through the public constructor.** That is a real, caller-visible defect regardless of mechanism.
2. **Combined with R3's discriminating probe, WHICH mechanism:** `@comm`-is-an-object vs `@comm`-is-nil.

**`[inferred]` A `false` return does NOT establish on its own:**
1. **That the crossed wire is the cause.** Because `:283` is `bare == true` and not truthiness, **`false` is the expected result even for a correctly-wired accessor if the value is not literally `true`.** A `false` is therefore **consistent with the crossed wire AND with a correctly-wired reader whose value failed the exact comparison.** **Two mechanisms, one observable.** This is the honest limit and it is why the finding rests on the read of `:410-412`, not on the probe.
2. **That no value can set it.** `[inferred]` **If the getter were corrected to `@bare`, the exact comparison at `:283` would still reject `'yes'`, `1`, `:true`, or any truthy non-`true`.** **So "the parameter is dead" has TWO independent sufficient causes, and `false` does not tell you which is load-bearing.**
3. **The reachability conclusion of D77 §1.3.** The probe tests the *parameter's* behaviour. **Reachability is a separate claim that rests on the caller census (`'Bare'` = 0 real pass sites corpus-wide), which this probe does not touch.**

**`[inferred]` The strongest statement the probe supports, precisely:** *the documented parameter key, given the value its documentation implies, does not produce a bare-flagged socket through the public constructor.* **Everything beyond that — the crossed wire specifically, the exact-comparison second cause, and unreachability — needs the source reads it already has.**

**`[inferred]` And note the asymmetry the brief is pointing at:** **a `true` return would refute the crossed wire outright (R1). A `false` return cannot confirm it.** The probe is **falsifying but not verifying** — one-directional evidence. **`[inferred]` That is a general property worth keeping: a test whose failure is decisive and whose success is ambiguous should be reported as a falsification instrument, not as a confirmation.**

---

## §2 T2 — `'Context'` vs `'SSLContext'`: is it the `'Bool'`/`'Bare'` species?

### §2.1 The answer: NO. Two distinct keys, two types, two storage slots, two consumers

**`[verified]` `parameters.rb:60`** — the D77 asymmetry: `# @option hash [Bool] 'Bool' Create a bare socket` (doc says **`'Bool'`**) vs `:112-113` reading/writing **`'Bare'`** (impl). **A documented name that is not the implemented name.**

**`[verified]` The `Context` family, by contrast, is two keys that are each internally consistent:**
```
:63    # @option hash [OpenSSL::SSL::SSLContext] 'SSLContext' Use a pregenerated SSL Context   <- DOC
:120   if hash['SSLContext']                                                                  <- READ
:121     self.sslctx = hash['SSLContext']                                                     <- WRITE
:421   # Pre configured SSL Context to use
:422   # @return [OpenSSL::SSL::SSLContext]

:77    # @option hash [Hash] 'Context' A context hash that can allow users of                        <- DOC
:191     self.context   = hash['Context']                                                      <- WRITE
```

| | `'SSLContext'` | `'Context'` |
|---|---|---|
| Documented type | `OpenSSL::SSL::SSLContext` (`:63`) | `Hash` (`:77`) |
| Doc/impl agree? | **YES** | **YES** |
| Stored on | `self.sslctx` (`:121`) | `self.context` (`:191`) |
| Doc comment | `:63` | `:77` |
| Representative value | a real `SSLContext` | `{ 'Msf' => framework, 'MsfExploit' => self }` |

> **`[inferred]` NOT the same species.** `'Bool'`/`'Bare'` is **one key with two names** — a caller following the documentation is silently ignored. `'Context'`/`'SSLContext'` is **two keys with two names**, both documented, both implemented, both type-distinct, **and the near-identical spelling is the hazard rather than a naming defect.**

**`[inferred]` The real risk this pair creates is DIFFERENT and worth naming:** the two keys differ by six characters (`'Context'` vs `'SSLContext'`), they are passed **in the same hash, often adjacent** (see §2.2), and the wrong one is **silently accepted** — `parameters.rb:120` and `:191` both test for presence, and neither errors on the other's key. **A caller who writes `'Context' => some_ssl_context` gets no SSL context and no diagnostic.**

### §2.2 The census — Rule 20 applied. PRINTED BESIDE THE CLAIM

**`[verified]` Census A — every site passing the literal key `'SSLContext'`:**
```
[gem] parameters.rb :120   if hash['SSLContext']        <- READ (the consumer)
[gem] parameters.rb :121   self.sslctx = hash['SSLContext']  <- WRITE to sslctx
[msf] modules\auxiliary\server\openssl_altchainsforgery_mitm_proxy.rb :148   'SSLContext' => context,
```
**`[verified]` Call sites that PASS the key = 1. Consumers that READ it = 1 (`parameters.rb:120`).**

**`[verified]` Census B — `'Context'` key-passing sites = 148 across both trees.** The complete list is long; the representative shape is uniform:
```
[msf] handler\reverse.rb:99 · bind_tcp.rb:128 · bind_sctp.rb:131 · bind_udp.rb:131 · bind_named_pipe.rb:273
[msf] handler\reverse_tcp_ssl.rb:62 · reverse_tcp_double_ssl.rb:84 · reverse_sctp.rb:80 · reverse_udp.rb:117
[msf] exploit\remote\tcp.rb:117 · tcp_server.rb:69 · udp.rb:45 · ftp.rb:296/:310 · dcerpc.rb:166
[msf] rex\proto\http\client.rb:183 · rex\proto\http\server.rb:95 · rex\proto\ftp\server.rb:54/:153/:281
[gem] socket\ssh_factory.rb:36
```
**`[verified]` Every sampled value is `{ 'Msf' => framework, 'MsfExploit' => … }` or a variable of that shape.** `[inferred]` **This is the framework handle, passed to nearly every socket constructor — not TLS configuration.**

**`[verified]` Control: `'Context'` (460 occurrences MSF-tree) vs `'SSLContext'` (1 pass site). A 460:1 ratio is itself the finding — the collision-prone key is the common one, and the SSL-specific key is nearly unused.**

### §2.3 The dangerous adjacency, in a real call site

**`[verified]` `openssl_altchainsforgery_mitm_proxy.rb:145-154` passes BOTH keys, three lines apart:**
```ruby
@proxy = Rex::Socket::SslTcpServer.create(
  'LocalHost' => local_host,
  'LocalPort' => local_port,
  'SSLContext' => context,          # :148  the SSL context
  'Context' =>                      # :149  the framework handle
    {
      'Msf' => framework,
      'MsfExploit' => self
    }
)
```

**`[inferred]` This is the only site in the corpus that passes both, and it is the one place where the six-character difference is load-bearing.** `[inferred]` It is also the site both D58 and D70 cited — correctly — which is a reminder that **a correct citation of a rare site is not evidence that the site was rare.**

### §2.4 Does `'SSLContext'` have the same doc/impl mismatch as `'Bare'`? — NO

**`[verified]` `:63` documents `'SSLContext'`; `:120-121` implement `'SSLContext'`. Identical spelling.** **`[absence]` No second spelling of this key was found.** By contrast `'Bare'` has `'Bool'` in the doc at `:60`. **`[inferred]` The `'Bool'`/`'Bare'` mismatch is unique among the SSL-adjacent keys examined — the other four (`'SSL'`, `'SSLVersion'`, `'SSLVerifyMode'`, `'SSLCompression'`, `'SSLCipher'`) are internally consistent.** **Bounded: I checked the doc block for `:20-90` by reading it; I did not pattern-scan for every doc/impl pair in the file.**

---

## §3 T3 — `ssl_verify_mode` in the THIRD place: the datastore side

### §3.1 The answer: it IS plumbed through — and the deciding line is `tcp.rb:317-319`

**`[verified]` The datastore→socket chain, complete:**
```ruby
tcp.rb:68    OptEnum.new('SSLVerifyMode', [ false, 'SSL verification method', 'PEER',
                                            %W{CLIENT_ONCE FAIL_IF_NO_PEER_CERT NONE PEER}])   # registration
tcp.rb:317   def ssl_verify_mode
tcp.rb:318     datastore['SSLVerifyMode']                                                        # THE DECIDING LINE
tcp.rb:319   end
tcp.rb:111   'SSLVerifyMode' =>  opts['SSLVerifyMode'] || ssl_verify_mode,                       # into the hash
   → socket.rb:51  create_param → Comm::Local → ssl_tcp.rb:116   if params.ssl_verify_mode
   → ssl_tcp.rb:117  const_get("VERIFY_#{params.ssl_verify_mode}")
```

> **`[inferred]` The datastore side is a live, working consumer. It is neither validated-then-unread (the server) nor absent (the HTTP client). It is the ONE place the field functions as designed.**

**`[verified]` Census — every datastore read of the key = 14 sites:**
```
lib\msf\core\exploit\remote\tcp.rb :318                    <- the method above
modules\auxiliary\scanner\{acpp,afp,db2,ftp,mqtt,mssql,mysql,pop3,postgres,telnet,vnc,...}\*_login.rb
  → 13 sites, all the shape  ssl_verify_mode: datastore['SSLVerifyMode'],
```

**`[verified]` Census — every registration of the key = 2:**
```
lib\msf\core\exploit\remote\tcp.rb :68   OptEnum.new('SSLVerifyMode', [ false, …, 'PEER', %W{…}])
modules\exploits\windows\ibm\ibm_was_dmgr_java_deserialization_rce.rb :61   OptRaw.new('SSLVerifyMode', [true, …, 'CLIENT_ONCE'])
```

**`[verified]` Census — registrations in every SERVER/HTTP mixin = 0:**
```
lib\msf\core\handler\reverse_https.rb           SSLVerifyMode x0 | ssl_verify_mode x0
lib\msf\core\handler\reverse\ssl.rb             SSLVerifyMode x0 | ssl_verify_mode x0
lib\msf\core\exploit\remote\tcp_server.rb       SSLVerifyMode x0 | ssl_verify_mode x0
lib\msf\core\exploit\remote\http_server.rb      SSLVerifyMode x0 | ssl_verify_mode x0
lib\msf\core\exploit\remote\http_client.rb      SSLVerifyMode x0 | ssl_verify_mode x0
```

### §3.2 The three-way split — same field, three different states

| Place | State | Deciding site |
|---|---|---|
| **Datastore / `Remote::Tcp` client** | **LIVE** — read, plumbed, honoured | `tcp.rb:318` → `:111` → `ssl_tcp.rb:116` |
| **Server (`makessl`)** | **VALIDATED-THEN-UNREAD** (D70 shape 20) | `parameters.rb:132` writes; **`makessl` never reads** |
| **HTTP client (`Rex::Proto::Http::Client`)** | **NOT PLUMBED THROUGH** | `client.rb` passes `SSLVersion`+`SSLKeyLogFile` only (D77 §2.2) |
| **Server mixins (`TcpServer`, `http_server`, handlers)** | **NOT EVEN OFFERED** | 0 registrations (§3.1) |

> **`[inferred]` Four distinct states for one field, in one framework.** *Declared / offered / read / honoured* are **four** questions, not the three D70 §6.3 named — and this field answers **yes, no, partly, and yes** depending on where you stand.

### §3.3 By construction or by omission? — BY CONSTRUCTION, and here is the file:line

**The brief's question: if the HTTP client cannot ask for anything other than `VERIFY_PEER`, is that by construction or by omission?**

**`[verified]` Deciding sites, both:**
1. **`parameters.rb:130-132`** — the allow-list **exists and is enforced**: `supported_ssl_verifiers = %W{CLIENT_ONCE FAIL_IF_NO_PEER_CERT NONE PEER}` with `include?` guarding the write. **A value outside that set is silently dropped, not rejected.**
2. **`ssl_tcp.rb:116-120`** — the consumer: `if params.ssl_verify_mode` → `const_get`; `else` → `VERIFY_PEER`.

**`[inferred]` The answer is BY CONSTRUCTION, and the construction has three deliberate parts:**
- **The transport layer faithfully implements a four-value option** (`parameters.rb:130-132`, `ssl_tcp.rb:116-117`). **The capability is real and reachable.**
- **The strict default is deliberate and documented** — `ssl_tcp.rb:119` `# Could also do this as graceful faildown …`, and the registration default is `'PEER'` (`tcp.rb:68`). **The authors chose verifying-by-default.**
- **`Rex::Proto::Http::Client` simply does not forward the key** — `client.rb` passes `SSLVersion` and `SSLKeyLogFile` (`:185-186`) and nothing else verification-related. **`[inferred]` Its callers therefore inherit `VERIFY_PEER`, and the option's absence from the hash means `ssl_verify_mode` is `nil` at `ssl_tcp.rb:116`, so the `else` branch fires by definition.**

> **`[inferred]` It is construction in the sense that the fallback is deliberate and documented — not an accidental omission. But it is also a GAP: `Http::Client` is the framework's most-used HTTPS primitive and it exposes no verification control at all, while `Remote::Tcp` — its sibling — exposes four.**

**`[inferred]` And the sharpest form of the asymmetry:** the allow-list accepts **`NONE`** (`parameters.rb:130`). **So the capability to disable verification exists at the transport layer, is honoured by the client constructor, is reachable from `Remote::Tcp` modules via the datastore — and is NOT reachable from `Http::Client`.** **`[verified]` `'SSLVerifyMode'` occurrences in `http_client.rb` = 0 and in `client.rb` = 0** (§3.1). **A module wanting `VERIFY_NONE` on an HTTPS request must drop to a hand-built socket** — which is exactly what D70 §4.2 found six exploit modules doing.

---

## §4 Residual unknowns, each with a probe

**U1 — the §0.2 correction rests on `jsse_skiptls_mitm_proxy.rb:132` being a SERVER context.** **I did not re-verify it in this pass.** **Probe:** read `jsse_skiptls_mitm_proxy.rb:110-140` and confirm whether `:132`'s `'SSLVerifyMode' => 'NONE'` is passed to a server creation (inert) or a client connect (live). **If it is a client connect, D70 §2.3's "two server-side `NONE` consumers" becomes "zero," and the inert-value example collapses to a single case.** **This is the open end of §0.2 and it is the highest-value residual here.**

**U2 — R4 (a `Comm` `==` override) is not fully bounded.** **Probe:** enumerate `def ==` across the gem's `Comm` classes. **`[inferred]` Expected: none.** **If one exists, §1.3's ground (a) needs restating.**

**U3 — the §2.4 doc/impl consistency check was scoped to reading the doc block, not scanning every pair.** **Probe:** for each `# @option hash` line in `parameters.rb:15-90`, extract the documented key and test that the literal appears in the corresponding `if hash[...]` block. **`[inferred]` This would mechanise the `'Bool'`/`'Bare'` detection and may find more.**

**U4 — the 148 `'Context'` pass sites were counted, not each inspected.** The uniform sampled shape is strong; **a non-framework-handle value would be a finding.** **Probe:** filter the 148 for values that are NOT `{ 'Msf' => …, 'MsfExploit' => … }` and inspect those.

**U5 — no execution.** `[inferred]` throughout; U1 of D77 remains the one-line probe that would settle §1.2 (§1.2 here).

---

## §6 Instrument record

### §6.1 Rule 20 applied — every claim of the form "the set is N" carries its enumeration

**Three claims in this report are Rule-20 claims, and each printed its census beside it:**
- **§2.2** — *"`'SSLContext'` has 1 pass site"* → the enumeration printing **3 occurrences total, 1 of which passes the key**.
- **§3.1** — *"`ssl_verify_mode` has 14 datastore reads and 2 registrations"* → both full enumerations printed, **plus the 0/0 server-mixin table.**
- **§0.2** — *"two constructions in one method"* → **both constructor calls printed with line numbers.**

### §6.2 A BROKEN instrument, labelled — and it is mine, this round

**`[verified]` My first `'SSLContext'`-pass-site pattern returned 0**, while the correct count is 1:
```
'"SSLContext\b\s*(=>|:)"    →  0 hits
```
**Cause: `openssl_altchainsforgery:148` is `'SSLContext' => context,`** — the pattern required `=>` **immediately** after the closing quote, but there is a **space**. **The regex was too tight and produced a false zero on the exact site D58 and D70 had named.**

> **`[inferred]` This is a false zero in the direction Rule 20 warns about (toward a clean result), caught only because the earlier reports had named the site and the two counts disagreed.** **Had this been a fresh question, `'SSLContext'` would have been reported as unreachable — a confident non-answer.**

**`[inferred]` And the meta-point, which is the round's best lesson:** **the correction in §0.2 and the broken instrument in §6.2 have the SAME root.** D70 read two `'SSLVerifyMode' => 'NONE'` sites as one context; my regex read `'SSLContext' =>` as zero sites. **Both substituted a pattern for a census of the primitive.** **A pattern is a filter over text; a census is an enumeration of call sites. They are not interchangeable, and the difference only shows when a second count disagrees.**

### §6.3 What went right, restated as standing practice

**Per the brief, three things to repeat:**
1. **Own-pattern false positive flagged, not smoothed.** D77 §1.1's third `'Bare'` hit was a RuboCop message string; **named as a false positive rather than counted as clean.** This round: §6.2's false zero is labelled **BROKEN** against that same standard.
2. **No reconciliation without identity.** The four `ssl_verify_mode` states in §3.2 are **not** collapsed: 14 datastore reads and 2 registrations **are different quantities** and are never added. **Two counts sharing a number is not corroboration.**
3. **Every negative carries its bound.** §0.1's occupancy check is bounded by a control; §1.4 lists what the probe does **not** establish; §3.3's "by construction" is bounded by naming both deciding lines.

---

*End of D82.*
