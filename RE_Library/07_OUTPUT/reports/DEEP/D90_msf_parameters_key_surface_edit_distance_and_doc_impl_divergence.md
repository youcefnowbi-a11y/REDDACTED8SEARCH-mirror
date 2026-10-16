# D90 — the key-acceptance surface of `parameters.rb`: edit-distance class, doc/impl divergence census, and U1 closed

**Task:** D90 (T1 close D77 U1; T2 confusable key pairs; T3 doc/impl key divergence)
**Lane:** metasploit core
**Status:** COMPLETE
**Deliverable:** `RE_Library\07_OUTPUT\reports\DEEP\D90_msf_parameters_key_surface_edit_distance_and_doc_impl_divergence.md` (write scope: this file only)
**Method:** pure source. **Ruby is absent on this host — nothing was executed.** Rex/OpenSSL contract claims are `[inferred]`.
**Tags:** `[verified]` / `[read]` / `[inferred]` / `[absence]`. **Line counts are LF-delimited lines** (`-split "\r?\n"`), final unterminated line counted.
**Numbering:** `D90` verified **UNOCCUPIED by enumeration** — §0.1.

---

## §0 Preface: the mechanism, reused

**T1 is the second instance of the same error, and the phrase from D82 §6.2 applies without amendment:**

> **Both substituted a pattern for a census. A pattern filters text; a census enumerates call sites. The difference only surfaces when a second count disagrees.**

**D70 counted the VALUE `'SSLVerifyMode' => 'NONE'` (it appears twice) and inferred two sites shared a context. The primitive is the CONSTRUCTOR.** §1 enumerates the constructors. **Both sites are client connects. D70's count was 2; the true count is 0.**

**This is the third consecutive round where the primitive-vs-value distinction produced a correction** — D82 §0.2 (one site), D82 §6.2 (my false-zero regex), D90 §1 (the pair). Filed as the round's operating rule rather than three anecdotes.

### §0.1 Occupancy by enumeration

```powershell
Get-ChildItem $DEEP -File | Where-Object { $_.Name -match '^D9|90' }
```
```
D9_msf_core_library.md    161013 B
```
**`[verified]` No D90. Total files = 131.** Control in the same invocation: `^D8` returned **8** files. **The probe bites.**
**`[verified]` `D85`, `D87`, `D89` are also unoccupied** — noted because `D86`/`D88` exist, so **the numbering is not sequential and a next lane cannot assume the next number is free.** **Enumerate; do not increment.**

---

## §1 T1 — U1 CLOSED. D70's "two server-side `NONE` consumers" = **0**

### §1.1 The test applied to both sites: what is the CONSTRUCTOR?

**`[verified]` Site A — `openssl_altchainsforgery_mitm_proxy.rb:166-176`:**
```ruby
:145    @proxy = Rex::Socket::SslTcpServer.create(     # <- the LISTENER (server)
:146      'LocalHost' => local_host,
:147      'LocalPort' => local_port,
:148      'SSLContext' => context,
:149      'Context' => { 'Msf' => framework, 'MsfExploit' => self }
:154    )
        ...
:166    server = Rex::Socket::Tcp.create(              # <- CLIENT CONNECT
:167      'PeerHost' => host,
:168      'PeerPort' => port,
:169      'SSL' => true,
:170      'SSLVerifyMode' => 'NONE',
:171      'Context' => { 'Msf' => framework, 'MsfExploit' => self }
:176    )
```
**`[verified]` `:170`'s `'SSLVerifyMode'` belongs to `:166`'s `Rex::Socket::Tcp.create` — a CLIENT connect.**

**`[verified]` Site B — `jsse_skiptls_mitm_proxy.rb:107-151`:**
```ruby
:107    @proxy = Rex::Socket::TcpServer.create(        # <- the LISTENER (server), NO SSLVerifyMode
:108      'LocalHost' => local_host,
:109      'LocalPort' => local_port,
:110      'Context' => { 'Msf' => framework, 'MsfExploit' => self }
:114    )
        ...
:128    fake_server = Rex::Socket::Tcp.create(         # <- CLIENT CONNECT  (note the variable name)
:129      'PeerHost' => fake_host,
:130      'PeerPort' => fake_port,
:131      'SSL' => true,
:132      'SSLVerifyMode' => 'NONE',
:133      'Context' => { 'Msf' => framework, 'MsfExploit' => self }
:138    )
        ...
:143    server = Rex::Socket::Tcp.create(              # <- CLIENT CONNECT, no SSL
:144      'PeerHost' => host,
:145      'PeerPort' => port,
:146      'Context' => { 'Msf' => framework, 'MsfExploit' => self }
:151    )
```
**`[verified]` `:132`'s `'SSLVerifyMode'` belongs to `:128`'s `Rex::Socket::Tcp.create` — a CLIENT connect.**

### §1.2 The pair, reported as asked

| Site | `'SSLVerifyMode' => 'NONE'` at | Constructor | Direction | Reads `ssl_verify_mode`? |
|---|---|---|---|---|
| `openssl_altchainsforgery_mitm_proxy.rb` | **`:170`** | `Rex::Socket::Tcp.create` (`:166`) | **CLIENT** | **YES** — `ssl_tcp.rb:116` |
| `jsse_skiptls_mitm_proxy.rb` | **`:132`** | `Rex::Socket::Tcp.create` (`:128`) | **CLIENT** | **YES** — `ssl_tcp.rb:116` |

> **`[inferred]` `[verified]` ANSWER: D70 §2.3's "two server-side `NONE` consumers" is 0.** **Both are client connects.** The value is **live** at both sites — `ssl_tcp.rb:116` reads `params.ssl_verify_mode`, resolves `VERIFY_NONE` via `const_get` (`:117`), and the `VERIFY_PEER` fallback (`:120`) **does not fire at either site.**

**`[verified]` Corroborating census — the register of `NONE`-setting sites:**
- `[verified]` **Each file has exactly ONE `'SSLVerifyMode'` pass site**, both client-side, both the only one in-file.
- `[verified]` **`jsse_skiptls:107`'s listener passes no `SSLVerifyMode` at all** — a third constructor (`TcpServer.create`, not `SslTcpServer.create`) with no verification key in its hash.
- `[verified]` **`openssl_altchainsforgery:145`'s listener likewise passes no `SSLVerifyMode`.**
- **`[absence]` So NEITHER file sets a verification mode on its listener. The field is used twice in these two files and both uses are outbound.**

### §1.3 What this does to D70 §2.3, and what survives

**D70 §2.3's claim was: "Two SERVER-context `NONE` consumers … set an INERT value. Field is WRITE-ONLY on the server path."**

**`[inferred]` Both halves need restating:**
1. **"Two server-context consumers" → 0.** Neither is server-context. **§0.2 of D82 already caught site A; T1 catches site B, and the pair is now closed.**
2. **"The field is WRITE-ONLY on the server path" → still TRUE, and now better supported.** The server path's write is `parameters.rb:131-132`; the read is absent from `makessl`. **`[verified]` No server-side `'SSLVerifyMode'` pass site remains in these two files to muddy it.**
3. **`[inferred]` "Two independent examples of an inert server value" → COLLAPSES. It was zero examples, and the inert-value finding rested on them.**

**`[inferred]` Bound on point 3:** the inert-value claim **does not depend on these two sites.** It stands on the **structural** evidence — `parameters.rb:131-132` writes `ssl_verify_mode`, `ssl.rb:120-158`'s `makessl` never reads it, and `tcp_server.rb:20-32` never registers the option. **The two files were corroboration, not foundation, and the corroboration was miscounted.** **D70 shape #20 (validated-then-unread) survives; these two exhibits do not.**

**`[inferred]` And a naming trap worth recording:** `jsse_skiptls:128`'s variable is called **`fake_server`**. The name says server; the constructor says client. **`[inferred]` D70's classification is the most likely way that name was consumed.** A variable name is a claim, not a measurement — the same species as *"a comment is a claim, not a measurement"* (D26/D54's lesson), applied to identifiers.

---

## §2 T3 — the doc/impl key divergence census (computed first; its output is T2's input)

### §2.1 The two lists, enumerated

**`[verified]` DOCUMENTED keys (`# @option hash [Type] 'Key'`) = 24**, at `:52-84`:
```
PeerHost(53) PeerHostname(55) SSLKeyLogFile(56) PeerAddr(57) PeerPort(54) LocalHost(58)
LocalPort(59) Bool(60) Server(61) SSL(62) SSLContext(63) SSLVersion(64) SSLCert(66)
SSLCipher(68) SSLCompression(69) SSLVerifyMode(70) Proxies(72) Proto(73) IPv6(74)
Comm(75) Context(77) Retries(79) Timeout(81) Interface(83)
```
*(line numbers are the `:NN` anchors of each `# @option` line)*

**`[verified]` IMPLEMENTED keys (`hash['Key']` or `hash.fetch('Key')`) = 29:**
```
PeerHost PeerHostname PeerAddr LocalHost LocalAddr PeerPort LocalPort Bare SSL SSLContext
SSLKeyLogFile SSLVersion SSLVerifyMode SSLCompression SSLCipher VHOST SSLCommonName SSLCert
SSLClientCert SSLClientKey Proxies Proto Server Comm Context Retries Timeout Interface IPv6
```

### §2.2 DIVERGENCE A — documented but NOT implemented: **exactly ONE**

```
'Bool'
```
> **`[verified]` `'Bool'` is the ONLY key in the doc list that the implementation never reads.**
**`[verified]` `:60`** `# @option hash [Bool] 'Bool' Create a bare socket` — **`[verified]` impl reads `'Bare'` at `:112-113`.**
**`[verified]` `'Bool'` appears ZERO times as a `hash[...]` key anywhere in the file** (the census printed 0 impl refs for it).

**`[inferred]` So D77's finding is a CLASS OF ONE, and the class is closed.** The doc/impl divergence exists, is real, is **uniquely `'Bool'`/`'Bare'`**, and **no other key has the property.** **`[inferred]` That is a strong result: the defect is severe but NOT systemic — it is one typo, not a pattern of drift.**

### §2.3 DIVERGENCE B — implemented but NOT documented: **SIX**

```
'LocalAddr'        :95-96    elsif (hash['LocalAddr'])          -> self.localhost
'Bare'             :112-113  if (hash['Bare'])                  -> self.bare
'VHOST'            :143-144  if (hash['VHOST'])                 -> self.ssl_cn
'SSLCommonName'    :147-148  if (hash['SSLCommonName'])         -> self.ssl_cn
'SSLClientCert'    :159-161  if (hash['SSLClientCert'] and File.file?(...))  -> self.ssl_client_cert
'SSLClientKey'     :167-169  if (hash['SSLClientKey']  and File.file?(...))  -> self.ssl_client_key
```

**`[inferred]` Three of the six are SSL-material keys that a caller cannot discover from the documentation:** `SSLClientCert`, `SSLClientKey`, `SSLCommonName`. **`[inferred]` And `SSLClientCert`/`SSLClientKey` are the client-certificate pair — security-relevant, undocumented, and (§4) the closest confusable pair in the entire surface.**

**`[inferred]` The asymmetry matters and is the opposite of §2.2's:** **A is a usability trap that silently disables a feature. B is a discoverability gap** — the feature works, and the documentation does not admit it exists. **The two are not the same defect and are not reconciled here.**

### §2.4 A THIRD divergence, in the doc TEXT rather than the key name — NEW

**`[verified]` `parameters.rb:70-71`:**
```
# @option hash [String] 'SSLVerifyMode' SSL certificate verification
#   mechanism. One of 'NONE' (default), 'CLIENT_ONCE', 'FAIL_IF_NO_PEER_CERT ', 'PEER'
```

**`[verified]` Three problems in two lines:**
1. **`'NONE' (default)` — the documented default is WRONG.** `[verified]` `Msf::Exploit::Remote::Tcp` registers `OptEnum.new('SSLVerifyMode', [ false, 'SSL verification method', 'PEER', %W{...}])` at **`tcp.rb:68`** — **default `'PEER'`**. And `[verified]` `ssl_tcp.rb:119-120` falls back to **`VERIFY_PEER`** when the parameter is absent. **`[inferred]` A caller reading the docs would believe verification is off by default. It is on by default in every direction I can measure.**
2. **`'FAIL_IF_NO_PEER_CERT '` has a TRAILING SPACE** inside the quotes, before the closing `'`.
3. **`[verified]` The allow-list at `:130` is `%W{CLIENT_ONCE FAIL_IF_NO_PEER_CERT NONE PEER}` — no trailing space.** **`[inferred]` So the documented spelling `'FAIL_IF_NO_PEER_CERT '` would be REJECTED by the `include?` check at `:131` and silently dropped.**

> **`[inferred]` Point 3 is the sharpest form of the class: a doc typo that, copied faithfully by a caller, SILENTLY DISABLES the security option — the `include?` guard drops it without error and the constructor falls back to `VERIFY_PEER`.** **The fallback is the strict value, so this particular typo fails SAFE.** **The inverse typo would not: a caller writing `'NONE '` or `'none'` is dropped and gets `VERIFY_PEER`, not `VERIFY_NONE` — which is the safe direction. Stated because I checked the direction rather than assuming it.**

**`[inferred]` This is a doc/impl divergence of the same SPECIES as `'Bool'`/`'Bare'` — a name in the documentation that the implementation does not accept — but the divergence is in a VALUE, not a key, and it fails safe.** **Recorded separately; not merged with §2.2.**

---

## §3 T2 — confusable key pairs: a class of FIVE, and a class of ONE

### §3.1 Method, stated because the raw metric is not the test

**`[verified]` 30 distinct keys in the accept surface (24 documented ∪ 29 implemented).** Levenshtein distance computed over all 435 pairs; **pairs at d=1..3 = 7.** **The distance is the FILTER, not the finding** — the test that matters is:

> **Would the wrong key's value be SILENTLY ACCEPTED by the right key's guard?**
> A pair is dangerous iff (a) the keys are within typos of each other, **and** (b) **both guards are presence-tests** — no type coercion, no allow-list, no error on the unexpected key — **and** (c) neither key's absence is reported.

**`[verified]` Every guard for the candidate members, printed:**
```
:88   if (hash['PeerHost'])          :89   self.peerhost   = hash['PeerHost']
:98   if (hash['LocalHost'])         :99   self.localhost  = hash['LocalHost']
:104  if (hash['PeerPort'])          :105  self.peerport   = hash['PeerPort'].to_i
:108  if (hash['LocalPort'])         :109  self.localport  = hash['LocalPort'].to_i
:112  if (hash['Bare'])              :113  self.bare      = hash['Bare']
:120  if hash['SSLContext']          :121  self.sslctx    = hash['SSLContext']
:143  if (hash['VHOST'])             :144  self.ssl_cn    = hash['VHOST']
:147  if (hash['SSLCommonName'])     :148  self.ssl_cn    = hash['SSLCommonName']
:159  if (hash['SSLClientCert'] and ::File.file?(hash['SSLClientCert']))
:167  if (hash['SSLClientKey']  and ::File.file?(hash['SSLClientKey']))
:191  self.context   = hash['Context']        # no guard
:188  self.comm      = hash['Comm']           # no guard
```
**`[verified]` Every guard in the candidate set is a presence-test. There is no type check, no `raise`, and no unknown-key rejection anywhere in `from_hash`.** **`[inferred]` So criterion (b) is satisfied universally — the discriminating test reduces to (a) plus the SILENT direction.**

### §3.2 The pairs, by distance, each adjudicated

| d | Pair | Both real? | Silent? | Verdict |
|---|---|---|---|---|
| 2 | **`'LocalHost'`** vs **`'LocalPort'`** | YES | **NO — different guards, no shared slot** | **BENIGN** |
| 2 | **`'PeerHost'`** vs **`'PeerPort'`** | YES | **NO — different guards, no shared slot** | **BENIGN** |
| 3 | **`'Bare'`** vs `'Bool'` | **`'Bool'` = 0 impl refs** | **YES — `'Bool'` is a NO-OP** | **DEFECT (§2.2)** |
| 3 | `'Bool'` vs `'SSL'` | NO — `'Bool'` is not a key | n/a | **BENIGN (artifact)** |
| 3 | `'Bool'` vs `'Comm'` | NO — `'Bool'` is not a key | n/a | **BENIGN (artifact)** |
| 3 | **`'Context'`** vs **`'SSLContext'`** | **YES, both real** | **YES — neither guard rejects the other's value** | **DEFECT (D82 §2)** |
| 3 | **`'SSLClientCert'`** vs **`'SSLClientKey'`** | **YES, both real** | **YES — same guard shape, both `File.file?`** | **NEW DEFECT** |

**`[inferred]` `'LocalHost'`/`'LocalPort'` and `'PeerHost'`/`'PeerPort'` are benign for a structural reason worth stating:** **Levenshtein distance measures spelling, and these pairs differ by a suffix on a word that already distinguishes them.** A caller mixing them up gets a **host string where a port was expected** (`:105`/`:109` `.to_i` → `0`) or **a port where a host was expected** → **an immediate connection failure, not a silent misconfiguration.** **`[inferred]` These pairs FAIL LOUD. They are not in the class.**

**`[inferred]` The two `'Bool'` pairs are ARTIFACTS of including a non-key in the set** — `'Bool'` is documented but never implemented, so it cannot collide with anything at runtime. **Reported so the count of 7 is honest rather than overstated as 7 dangers; the real class is smaller.**

### §3.3 NEW DEFECT — `'SSLClientCert'` vs `'SSLClientKey'`, d=3

**`[verified]` The two guards are IDENTICAL in shape:**
```ruby
:159  if (hash['SSLClientCert'] and ::File.file?(hash['SSLClientCert']))
:161    self.ssl_client_cert = ::File.read(hash['SSLClientCert'])
:167  if (hash['SSLClientKey'] and ::File.file?(hash['SSLClientKey']))
:169    self.ssl_client_key = ::File.read(hash['SSLClientKey'])
```

**`[inferred]` The failure mode:** both guards test **`File.file?`** — a path-shaped string — and both accept **ANY existing file path**. **A caller who swaps the two keys passes both guards, reads both files successfully, and assigns the CERTIFICATE to `ssl_client_key` and the KEY to `ssl_client_cert`.**
- **`[inferred]` No exception at the parameter layer.** Neither guard can distinguish a PEM certificate from a PEM key.
- **`[inferred]` The error surfaces only later**, when OpenSSL consumes `ssl_client_key` at `ssl_tcp.rb:99-107`'s client cert/key block, or when `ssl.rb:136-138` assigns `ctx.key`/`ctx.cert`.

> **`[inferred]` This is the same SPECIES as `'Context'`/`'SSLContext'` but strictly harder to detect: the `'Context'` pair produces a missing SSL context (a wrong value silently ignored), while this pair produces a CROSSED ASSIGNMENT (both values accepted, each landing in the wrong slot).** **`[inferred]` The failure is deferred to the OpenSSL handshake, which is out of this corpus's reach — so its latency is unknowable from source alone.**

**`[inferred]` Bound:** `[absence]` of an in-corpus swap. **I did not enumerate call sites of these two keys across the corpus** (§5 U2). If no corpus caller sets both, the defect is latent — **which would make it the same status as `'SSLContext'`: real, silent, and unexercised.**

### §3.4 The class, stated

> **`[inferred]` CONFUSABLE-KEY CLASS = 3 members: `'Context'`/`'SSLContext'` (d=3, wrong-value-ignored), `'SSLClientCert'`/`'SSLClientKey'` (d=3, wrong-value-crossed), `'Bool'`/`'Bare'` (d=3, documented-name-never-implemented). A 4th candidate pair existed at d=3 (`'Bool'` vs `'SSL'`, `'Bool'` vs `'Comm'`) and is an artifact of a non-key.**

**`[inferred]` The unifying property is NOT the spelling distance — it is that `from_hash` is a PRESENCE-TEST-ONLY parser with no unknown-key rejection and no type validation.** Any two keys whose values satisfy each other's guards are silently interchangeable. **The edit distance is what makes the collision LIKELY; the absence of validation is what makes it SILENT.** **Rule 20's discipline applies to the fix as well: enumerating the guards found the class; an edit-distance scan alone would have reported 7 pairs and 4 non-findings.**

---

## §4 A pattern across all three tasks

**`[inferred]` All three defects have the same shape at the point of failure: a NAME that is not the thing it denotes.**
- `'Bool'` (a documented name) is not `'Bare'` (the implemented key)
- `'fail_if_no_peer_cert '` (a documented value) is not `'FAIL_IF_NO_PEER_CERT'` (the accepted value)
- `fake_server` (a variable name) is not a server — it is a client connect (`jsse_skiptls:128`)
- `'SSLClientCert'` and `'SSLClientKey'` are names close enough to each other to be exchanged

**`[inferred]` None of these is detectable by looking at the name. Each required reading the thing the name is attached to.** **This is the same lesson as *"a comment is a claim, not a measurement"* generalised to identifiers and documentation.** **`[verified]` D70 §1.1 and D58 §0.1 established it for PATHS; D90 establishes it for KEYS, VALUES, and VARIABLE NAMES.**

---

## §5 Residual unknowns, each with a probe

**U1 — `'SSLClientCert'`/`'SSLClientKey'` swap sites not enumerated.** **Probe:** Rule 20 census — every corpus site passing either key; then check whether any passes BOTH, and in which order. **`[inferred]` Expected: few or zero, making the defect latent.** **Not run in this pass; it is the one genuinely unfinished census here.**

**U2 — `hash.fetch('SSLVersion', nil)` uses a different accessor than every other key.** **`[verified]` `SSLVersion` appears 0 times as `hash['SSLVersion']`.** **`[inferred]` Consequence: it is the ONE key that cannot be discovered by a `hash[...]` census** — my own §2.1 list required a separate `fetch` branch to find it. **Probe:** enumerate every `hash.fetch` in the file to confirm `SSLVersion` is the only one. **`[inferred]` Likely yes; asserted as `[inferred]`, not `[verified]`, because I did not run the fetch-only census.**

**U3 — the `include?` drop at `:131` is silent for EVERY out-of-set value, not just the doc typo.** **Probe:** none needed beyond the read; **recorded as a design observation, not an unknown.**

**U4 — `'Interface'` and `'IPv6'` were not mechanism-tested for the pair class.** **`[verified]` both have guards printed (`:199`, `:187`); neither is within d=3 of another key, so neither is in the class.** **Closed by the distance computation.**

**U5 — no execution.** `[inferred]` throughout. **D77 §1.2's one-line probe remains the highest-value execution, unchanged.**

---

## §6 Instrument record

### §6.1 A BROKEN INSTRUMENT OF MINE, LABELLED — the Levenshtein parse failure

**`[verified]` My first edit-distance implementation FAILED TO PARSE:**
```
At line 28 char:46
+     $d[$i,$j]=[Math]::Min([Math]::Min($d[$i-1,$j]+1,$d[$i,$j-1]+1),$d ...
                                             ~ Missing ']' after array index expression
```
**`[inferred]` Cause: PowerShell's parser mis-tokenises the 2-D index `$d[$i-1,$j]` when nested inside `[Math]::Min(...)` — the `$i-1` reads as a terminator.** **Fix: rewrote with two explicit 1-D row arrays (`$prev`/`$cur`) and separate `$del`/`$ins`/`$sub` temporaries, which parsed and ran.**

> **`[inferred]` This is a TOOL failure, not a corpus finding, and it is labelled BROKEN rather than quietly re-run.** **Had I reported the distance table without noticing, the failure would have been a silent zero — the same direction Rule 20 warns about.** **It exited non-zero, which is why it was caught: a loud failure is the good kind.**

### §6.2 The pattern-for-a-census error, now three instances and a standing rule

| Instance | What was counted | What the primitive was | Result |
|---|---|---|---|
| D70 §2.3 | the VALUE `'SSLVerifyMode' => 'NONE'` | the CONSTRUCTOR | 2 → **0** (closed here) |
| D82 §6.2 | a regex over `'SSLContext' =>` | the key-passing sites | **1 → 0 false zero** (my own) |
| D90 §3.1 | raw edit distance | the GUARDS | 7 pairs → **3 defects + 4 non-findings** |

**`[inferred]` All three erred toward a tidier answer, and all three were caught only because a second count disagreed.** **§3.1 is the cheapest of the three to have avoided: the guard enumeration took one invocation and converted a 7-pair "class" into a 3-member class with four named exclusions.**

### §6.3 The three standing practices, applied

1. **Own-pattern false positive flagged, not smoothed.** **§3.2 labels the two `'Bool'` pairs as ARTIFACTS of a non-key in the set and `'LocalHost'`/`'PeerHost'`/`'PeerPort'`/`'LocalPort'` as BENIGN-by-construction** — so the d=1..3 count of 7 is not presented as 7 dangers. **§6.1 labels my own broken parser.**
2. **No reconciliation without identity.** **§2.2 (1 key), §2.3 (6 keys), §2.4 (1 value typo) are three different quantities and are never summed.** **The d=3 count (7 pairs) and the defect count (3) are also distinct and not merged.**
3. **Every negative carries its bound.** **§2.2's "class of ONE" is bounded to this file's doc block; §3.3's latent-swap claim carries U1 as its open end; §1.3's "inert value survives" is bounded to the structural evidence rather than the collapsed exhibits.**

---

*End of D90.*
