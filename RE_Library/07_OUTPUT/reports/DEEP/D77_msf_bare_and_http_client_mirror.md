# D77 — `bare?`'s unreachable gate, and the HTTP client mirror

**Task:** D77 (T1 `bare?`; T2 `rex\proto\http\client.rb`) — follow-on to D70
**Lane:** metasploit core
**Status:** COMPLETE
**Deliverable:** `RE_Library\07_OUTPUT\reports\DEEP\D77_msf_bare_and_http_client_mirror.md` (write scope: this file only)
**Method:** pure source. **Ruby is absent on this host — nothing was executed.** Contract claims are labelled `[inferred]`.
**Tags:** `[verified]` / `[read]` / `[inferred]` / `[absence]`. **Every number carries its invocation. Zeros carry a control.**

---

## §0 A pattern finding, not two findings

**`[verified]` Two independent instances of cached class-level key material exist in this corpus:**

**Instance 1 — `lib\metasploit\framework\login_scanner\vmauthd.rb:99-100`:**
```ruby
ctx = OpenSSL::SSL::SSLContext.new(:SSLv3)
@@cached_rsa_key ||= OpenSSL::PKey::RSA.new(1024){}
```

**Instance 2 — `rex-socket-0.1.71\src\lib\rex\socket\ssl.rb:66-74` (D54 §4's subject):**
```ruby
# This defines the global certificate provider for all consumers of the mixin
# Beware that altering this at runtime in one consumer will affect all others
# Providers must expose at least the class methods given above accepting the
# same calling convention.
@@cert_provider = Rex::Socket::Ssl::CertProvider

def self.cert_provider=(val)
  @@cert_provider = val
end
```

> **`[inferred]` These are ONE pattern finding, not two findings: both cache cryptographic key material in a mutable class variable on a module that is included into other types.** A class variable is per-hierarchy, not per-instance, so the cache is shared across every consumer of the mixin or module.

**`[inferred]` The pattern is worse in instance 2 and the source says so itself.** `ssl.rb:67` — *"Beware that altering this at runtime in one consumer will affect all others"* — **is the authors documenting the exact hazard**, four lines above the construct. `[inferred]` Instance 1 has no such note and no setter, so its blast radius is limited to the memoised 1024-bit key; instance 2 has a public writer (`:72-74`) that any caller can use to redirect certificate generation for every consumer at once.

**`[verified]` And the project's own `AGENTS.md` forbids the construct outright:** *"Avoid mutable global and class variables in modules and libraries."* **`[inferred]` Two instances of a pattern the repository prohibits, in the SSL subsystem, one of them carrying a warning comment about its own consequences.** D54 §4 established instance 2 is latent (no in-corpus `cert_provider=` write exists). **Instance 1's key is live but its value is a memoised RSA key with no external setter.**

---

## §1 Q1 — `bare?`: who sets it, and is it reachable from the HTTP service path?

### §1.1 The field is defined but no corpus code ever sets the parameter key

**`[verified]` `bare` occurs 14 times in the entire `rex-socket` gem — the complete list:**
```
parameters.rb :60    # @option hash [Bool] 'Bool' Create a bare socket     <- doc (note: mislabelled key)
parameters.rb :113   self.bare = hash['Bare']                             <- the ONLY write
parameters.rb :279   # Returns true if the socket is a bare socket that does not inherit from
parameters.rb :282   def bare?
parameters.rb :283     return (bare == true)
parameters.rb :406   # Whether or not this is a bare (non-extended) socket instance that should
parameters.rb :409   attr_writer :bare
parameters.rb :410   def bare
parameters.rb :411     @comm || false                                     <- see §1.2
ssl_tcp.rb    :337   # Prevent a sysread from the bare socket             <- prose
ssl_tcp.rb    :344   # Prevent a sysread from the bare socket             <- prose
comm\local.rb :110   if !param.bare?                                       <- READ (ip path)
comm\local.rb :292   if !param.bare?                                       <- READ (server path)
comm\local.rb :403   if !param.bare?                                       <- READ (client path)
comm\local.rb :427   if !param.bare? && param.ssl                          <- READ (client SSL)
```

**`[verified]` The exact parameter key `'Bare'` appears in exactly 3 places corpus-wide:**
```
[gem] parameters.rb :112   if (hash['Bare'])
[gem] parameters.rb :113   self.bare = hash['Bare']
[msf] lib\rubocop\cop\lint\bare_check_code_in_non_exploit.rb :30   'Bare `CheckCode` will raise a NameError at runtime.'
```

**`[verified]` Control: the identical probe shape for the key `'SSL' =>` returns 565 hits across the same two trees.** The probe bites.

**`[inferred]` The third hit is a FALSE POSITIVE of the pattern and is named here so the count is honest:** `bare_check_code_in_non_exploit.rb:30` is a RuboCop **message string** about a bare `CheckCode` constant. It is not the socket parameter key.

> **`[verified]` `[absence]` NOT ONE module, lib file, spec, payload, adapter, or handler in the Metasploit tree sets `'Bare'`.** The only two real occurrences of the key are the reader and the writer inside `parameters.rb` itself.

**`[inferred]` Bound on that `[absence]`, stated in the D70 §2.6 form:** this is a claim about **this corpus**. `'Bare'` is a documented public parameter key (`parameters.rb:60`), so an external consumer — a plugin, a downstream gem, an out-of-tree module — could pass it. **"Never set in corpus" ≠ "cannot be set."** What is established is that **no code shipped in this corpus exercises the parameter.**

### §1.2 The getter reads the WRONG INSTANCE VARIABLE — so `bare?` cannot be true even if it were set

**`[verified]` `parameters.rb:406-412`, verbatim:**
```ruby
# Whether or not this is a bare (non-extended) socket instance that should
# be created.
# @return [Bool]
attr_writer :bare
def bare
  @comm || false
end
```

**`[verified]` Compare the correct sibling accessor, `parameters.rb:365-369`:**
```ruby
# The {Comm} instance that should be used to create the underlying socket.
# @return [Comm]
attr_writer :comm
def comm
  return @comm unless @comm.nil?
  ...
```

**`[inferred]` The `bare` getter was cloned from the `comm` accessor and never corrected.** `attr_writer :bare` writes `@bare`; the getter reads `@comm`. **Two different instance variables, and the reader never touches the one the writer sets.**

**`[inferred]` The consequence chain:**
1. `parameters.rb:113` `self.bare = hash['Bare']` sets **`@bare`**.
2. `bare?` (`:282-283`) calls `bare` → returns **`@comm || false`** — never `@bare`.
3. `bare?` then evaluates **`(@comm || false) == true`**.
4. `parameters.rb:188` `self.comm = hash['Comm']` sets `@comm` to a **Comm object** on real sockets.
5. **`Comm_object == true` is `false`.** `[inferred]` So `bare?` returns `false`.

> **`[verified]` `[inferred]` `bare?` is structurally incapable of returning `true` on any socket whose `Comm` is set — which is every real socket.** The parameter is dead on arrival: even a caller who set `'Bare' => true` correctly would find `bare?` false, because the getter reads a different variable.

**`[inferred]` Note the exact-comparison style compounds it.** `:283` is `return (bare == true)`, not truthiness. **If the getter were fixed to read `@bare`, a caller passing `'Bare' => 'yes'` or `1` would still get `false`** — only literal `true` passes. `[inferred]` The two defects are independent: fixing either one alone does not make the parameter work.

**`[inferred]` One more consequence, stated because it is a real hazard even though it is unreachable:** if the getter *were* corrected and `bare?` could return `true`, then `comm\local.rb:292` would skip class extension and `initsock` entirely. **A server created with `'Bare' => true, 'SSL' => true` would produce a plaintext listener with no `makessl`, no certificate, and no TLS** — a silent downgrade of an SSL-requesting socket. **The defect in `:410-412` currently prevents that, by accident.**

### §1.3 Is `bare?` reachable from the HTTP service path? — YES, and the gate is OPEN

**`[verified]` The D70 Q1 route, re-confirmed as reaching the gated block:**

```
rex\proto\http\server.rb:92   Rex::Socket::TcpServer.create('SSL'=>…, 'SSLCert'=>…)
  → socket.rb:51-52           create_param → param.comm.create(param)
  → comm\local.rb:289         if param.server?            → true
  → comm\local.rb:292         if !param.bare?             → :292-306
  → comm\local.rb:296         klass = SslTcpServer  (because param.ssl)
  → comm\local.rb:305         sock.initsock(param)
  → ssl_tcp_server.rb:47      self.sslctx = makessl(params)
```

**`[verified]` `parameters.rb:185` `self.server = hash['Server']`; `:196` `self.server = false` when unset.** `[inferred]` So `TcpServer.create` (`socket.rb:65-67`, which merges `'Server' => true`) takes the `:289` branch, and the client mirror takes `:403`/`:427`.

**`[verified]` And the answer: the gate at `:292` is OPEN, because `bare?` is false — §1.2 shows it is false on every real socket, and §1.1 shows nothing sets the key in the first place.** Two independent reasons, either of which alone suffices.

> **`[inferred]` `[absence]` `bare?` is NOT reachable as `true` from the HTTP service path — or from any corpus path. D70 Q1's answer therefore stands WITHOUT an exception.** The third path reaching no constructor exists in the code and **cannot be entered by any code in this corpus.**

### §1.4 The fourth gate, and a pass-through result for D70's U7

**`[verified]` `comm\local.rb:421-430` — the client-side SSL block:**
```ruby
current_proxy = param.proxies.last
proxy(sock, current_proxy.scheme, param.peerhost, param.peerport)
end

# Now extend the socket with SSL and perform the handshake
if !param.bare? && param.ssl
  sock.extend(Rex::Socket::SslTcp)
  sock.initsock(param)
end
```

**`[inferred]` This resolves D70's residual U7 for the client path: the SSL upgrade sits at `:427`, AFTER the proxy walk at `:423`.** SSL is applied at the endpoint, not per-hop — consistent with D26's finding that `Local` walks the proxy chain itself and TLS is applied after. **`[inferred]` Bound: this is the non-jruby client path; the jruby path (`comm\local.rb:59-90`) has no proxy walk at all, so there is nothing to order there.**

**`[inferred]` The four reads, and what each gates — `bare?` being false means all four are open:**
| Site | Gates | Open because |
|---|---|---|
| `:110` | `Rex::Socket::Ip` extension + `initsock` (ip path) | `bare?` false |
| `:292` | server class selection + `initsock` | `bare?` false |
| `:403` | client class selection + `initsock` | `bare?` false |
| `:427` | client SSL upgrade + handshake | `bare?` false |

**`[inferred]` Three of the four gates protect the constructor call itself.** A working `bare?` would mean **sockets with no Rex class extension**, which is the documented intent (`parameters.rb:60` *"Create a bare socket"*). **The parameter is a deliberate escape hatch that cannot be reached.**

---

## §2 Q2 — the HTTP client mirror

### §2.1 It takes the SAME route as the server — the generic factory, not the direct route

**`[verified]` `rex\proto\http\client.rb:177-190`, the connection construction:**
```ruby
self.conn = Rex::Socket::Tcp.create(
  'PeerHost'       => hostname,
  'PeerHostname'   => config['ssl_server_name_indication'] || config['vhost'],
  'PeerPort'       => port.to_i,
  'LocalHost'      => local_host,
  'LocalPort'      => local_port,
  'Context'        => context,
  'SSL'            => ssl,
  'SSLVersion'     => ssl_version,
  'SSLKeyLogFile'  => sslkeylogfile,
  'Proxies'        => proxies,
  'Timeout'        => timeout,
  'Comm'           => comm
)
```

**`[inferred]` So the answer to the mirror question is: the SAME route as the server.** The client uses `Rex::Socket::Tcp.create` — the **generic** factory — with `'SSL' => ssl`, then `socket.rb:51` → `Comm::Local:403/:427` → `SslTcp` + `initsock` → `ssl_tcp.rb:68/:75` → `initsock_with_ssl_version`.

> **`[inferred]` Neither half of the HTTP service uses the direct `SslTcpServer.create` route. Both go through the generic factory and have their class upgraded inside `Comm::Local`.** The direct route is taken only by the two SSL handlers (`reverse_tcp_ssl.rb:56`, `reverse_tcp_double_ssl.rb:78`) and two auxiliary modules. **This makes `Comm::Local` the single TLS chokepoint for the HTTP service in both directions** — and therefore the place where `bare?`, `ssl`, and `server?` jointly determine everything downstream.

**`[verified]` `comm\local.rb:427`'s `&& param.ssl` means the client's SSL upgrade is additionally conditional on the SSL flag — so no `SslTcp` extension occurs for a plaintext HTTP connect.** `[inferred]` Consistent: `Rex::Proto::Http::Client` is used for both `http://` and `https://` (`ssl` is a constructor parameter, `:24`).

### §2.2 The mirror is a CONSUMER of `SSLKeyLogFile` — and inert for every other SSL key

**`[verified]` Same probe shape applied to both files — nine keys, same pattern, with the control built in by running it on both:**

| Parameter key | `server.rb` | `client.rb` |
|---|---|---|
| `SSLCert` | **1** | 0 |
| `SSLCompression` | **1** | 0 |
| `SSLCipher` | **1** | 0 |
| `SSLVersion` | 1 | **1** |
| **`SSLKeyLogFile`** | **0** | **1** |
| `SSLVerifyMode` | 0 | 0 |
| `SSLContext` | 0 | 0 |
| `Bare` | 0 | 0 |

**`[inferred]` The two files are almost exactly complementary.** The server passes certificate, compression, and cipher; the client passes the key-log. **Both pass `SSLVersion`. Neither passes `SSLVerifyMode`, `SSLContext`, or `Bare`.**

**`[inferred]` The control is the table itself: the probe finds 4 keys in `server.rb` and 2 in `client.rb`, so it demonstrably bites on both operands.** A zero in one column is a bounded absence, not a failed pattern.

> **`[verified]` `[inferred]` The answer to "is the client mirror a consumer or on the inert side": it is a CONSUMER of `SSLKeyLogFile` (`:186`) and INERT for the rest.** It forwards the key-log path to the client constructor, where `ssl_tcp.rb:87-97` writes session keys to disk.

### §2.3 The mirror is a CONSUMER of the key-log — which makes D70 Q3's exposure sharper

**`[verified]` `client.rb:24`** — the constructor parameter: `..., comm: nil, subscriber: nil, sslkeylogfile: nil`
**`[verified]` `client.rb:36`** — `self.sslkeylogfile = sslkeylogfile`
**`[verified]` `client.rb:746-749`** — `# The SSL key log file for the connected socket.` / `attr_accessor :sslkeylogfile`

**`[verified]` `[inferred]` D70 §3.1 established the key-log is registered by three CLIENT mixins (`auth_brute.rb:45`, `http_client.rb:58`, `tcp.rb:70`), each defaulting to `ENV['SSLKeyLogFile']`.** This site is the **downstream end of that chain**: `http_client.rb:761-762`'s `datastore['SSLKeyLogFile']` flows into `Http::Client.new(..., sslkeylogfile:)` and lands here at `:186`.

**`[inferred]` One bound worth stating:** D70 §3.1's `[absence]` (no handler registration) stands, and **this file is client-side** — it is on the initiating end of a connection, not the listening end. **`[verified]` A server listener created by `rex\proto\http\server.rb` cannot reach this site: `server.rb` has `SSLKeyLogFile` = 0 occurrences (§2.2) and passes five other keys.** So the key-log is **one-directional**: outbound HTTP clients write it; inbound HTTP servers do not.

**`[inferred]` That asymmetry is itself reportable.** A `reverse_https` handler receiving an implant's connection produces **no** key log; an exploit module scanning an HTTPS target **does**, if `SSLKeyLogFile` is set in the environment. **The forensic artifact appears on the attack-outbound side, not the C2-inbound side** — the opposite of where an analyst looking at a C2 session would think to look.

### §2.4 The mirror has NO verification control, and this is a capability gap rather than an inert field

**`[verified]` `client.rb` contains 0 occurrences of `SSLVerifyMode`, 0 of `SSLContext`.** It does not pass either key.

**`[verified]` And the read-site count for `ssl_verify_mode` across the MSF tree — 27 occurrences, none in `client.rb`:**
```
lib\metasploit\framework\login_scanner\postgres.rb :20, :22, :69
lib\metasploit\framework\login_scanner\rex_socket.rb :21, :23
lib\metasploit\framework\tcp\client.rb :91        'SSLVerifyMode' => opts['SSLVerifyMode'] || ssl_verify_mode
lib\msf\core\exploit\remote\tcp.rb :111, :317
lib\postgres\postgres-pr\connection.rb :360
lib\rex\proto\mssql\client.rb :26, :93
modules\auxiliary\scanner\*  (13 *_login.rb sites)
spec\lib\rex\proto\postgresql\client_spec.rb :32
```

**`[verified]` `Rex::Proto::Http::Client` is NOT among the consumers.**

> **`[inferred]` This is a DIFFERENT result from D70 §2.3, and the distinction is the point.** On the **server** path, `SSLVerifyMode` is a *validated-then-unread* value — the field exists, is accepted, and is ignored. On the **HTTP client** path, the field is **never even passed**: `client.rb` has no way to set it. **D70's twentieth instrument shape covers the first case; this is the second case — a capability absent rather than a capability unread.**

**`[inferred]` The practical consequence:** an HTTP client built through `Rex::Proto::Http::Client` **cannot choose** its verification mode. It inherits `initsock_with_ssl_version`'s fallback, `VERIFY_PEER` (`ssl_tcp.rb:118-120`), plus the record-and-proceed callback (`:131-134`). **`[inferred]` So it verifies in the sense that it computes a verdict, and proceeds regardless — and T2 shows the caller has no way to ask for anything else.**

**`[inferred]` Bound, in the D70 §2.6 form:** `[absence]` in this corpus. `ssl_verify_mode` is a public accessor on several client mixins, and `initsock_with_ssl_version:116` *does* read the parameter — **so the capability exists at the transport layer and this caller simply does not expose it.** "Not exposed here" ≠ "not implementable."

### §2.5 `Bare` is not set here either

**`[verified]` `client.rb` contains 0 occurrences of `Bare`** (§2.2 table, control in the same run). **`[inferred]` The mirror cannot enter `bare?`'s branch any more than the server can** — §1's conclusion holds on both paths independently.

---

## §3 Residual unknowns, each with a probe

**U1 — D70 U5 / this report's U5: no execution.** Ruby absent. **`[inferred]`**: the `@comm`-vs-`@bare` consequence at `parameters.rb:410-412`; `Comm_object == true` evaluating `false`; `VERIFY_PEER`'s effective behaviour under the record-and-proceed callback. **Probe:** one Ruby session — `p Rex::Socket::Parameters.from_hash('Server'=>true,'SSL'=>true,'Bare'=>true).bare?` would settle §1.2 directly and convert `[inferred]` to `[verified]`. **This is now the single highest-value probe in this lane: it would confirm a defect and its inertness in one line.**

**U2 — the `Context` key at `client.rb:183` and `server.rb:95` is passed but unexamined.** Both files forward a `'Context'` hash. **Probe:** enumerate `'Context'` consumers in the gem. `[inferred]` likely the `Msf`/`MsfPayload` framework handle rather than anything TLS-related, but it is a second forwarded key I have not traced and D70's §1.1 count was scoped to SSL-named keys.

**U3 — `client.rb:554-557` reads `conn.peer_cert` for NTLM channel binding.** `if !conn.respond_to?(:peer_cert) or conn.peer_cert.nil?` → `Net::NTLM::ChannelBinding.create(OpenSSL::X509::Certificate.new(conn.peer_cert))`. **`[inferred]` This is the ONLY place in the HTTP client that inspects a peer certificate** — and it uses it for channel binding, not for trust. **Probe:** confirm no other `peer_cert` consumer in this file, and whether `ssl_tcp.rb:304`'s `peer_cert` is reached on a non-verifying context. **`[inferred]` A `VERIFY_NONE` context can still expose a peer certificate, so channel binding is unaffected — but that is an inference, not a measurement.**

**U4 — the jruby paths (`comm\local.rb:53-90`) select the same classes but were not read end to end.** **`[inferred]` `:65`/`:73` mirror `:296`/`:427`'s logic, and `:110`-equivalent gating may differ.** **Probe:** read `:90-110` to confirm whether the jruby server path gates on `bare?` at all.

**U5 — `has_read_data?`, `sysread`, `syswrite` at `ssl_tcp.rb:224/:339/:346` were not re-read for the `peer_verified` dead-end.** D70 §2.6 established `peer_verified` has no in-corpus reader. **Probe:** none available beyond the enumeration already run; recorded as a closed negative.

---

## §4 Instrument record

### §4.1 No instrument failure — and this pass added nothing new to the defence

**Every zero carried its control in the same invocation, and the controls were meaningful rather than decorative:**
- **§1.1** — the `'Bare'` key probe printed its **three** hits, and I named the third as a **false positive of the pattern** (a RuboCop string). **A count that includes its own false positive is more trustworthy than one that silently excludes it.** Control: `'SSL' =>` returned **565** by the identical pattern.
- **§2.2** — the client/server key table is **its own control**: the same probe returns 4 keys in one operand and 2 in the other. **A zero column is bounded by a probe demonstrably biting on the row's neighbours.**
- **§2.4** — the `ssl_verify_mode` read-site enumeration printed all **27** occurrences with file and line, so "`client.rb` is not among them" is a statement about a complete list rather than a failed pattern.

### §4.2 The finding that would have been missed by a targeted probe

**`[inferred]` A probe for `'Bare'` would have returned "0 in the MSF tree, 2 in `parameters.rb`" and I would have reported an unused parameter.** That is the correct answer to the question as asked — and it is **not the interesting one.**

**`[inferred]` The defect at `parameters.rb:410-412` is only visible by reading the accessor next to its sibling.** The reader returns `@comm` where the writer sets `@bare`. **Reading `bare?` alone shows a plausible implementation (`bare == true`); reading `def bare` alone shows a plausible accessor (`@comm || false`); only the pair exposes the mismatch** — and only comparing against `def comm` (`:368-369`) shows *which* variable was intended.

> **`[inferred]` The method: when a field is declared, written, and read in three places, reading those three places in one contiguous pass is what catches a crossed wire.** Enumerating occurrences finds all three; it does not make them adjacent.

**`[inferred]` This is a sub-shape of D70 §6.3's *is it declared / is it offered / is it read*** — here all three answers were "yes" and the field was still inert, **because the read was pointed at a different variable.** A field can be declared, written, offered, and read, and still never connect.

### §4.3 A note on the `'Bool'` doc string

**`[verified]` `parameters.rb:60`: `# @option hash [Bool] 'Bool' Create a bare socket`.**

**`[inferred]` The documented key is `'Bool'`; the implemented key is `'Bare'`.** `:112-113` read and write `hash['Bare']`. **`[inferred]` An operator or module author following the documentation would pass `'Bool' => true` and be silently ignored** — no error, no warning, `bare` stays unset. The documentation and the implementation disagree on the name of the parameter.

**`[inferred]` This is the same species as D42 §6.1 and D70 §1.2: a name that does not denote the thing it is attached to.** Here it is a doc-comment rather than a path, but the failure mode is identical — **a caller acting on the stated name gets no result and no diagnostic.**

---

*End of D77.*
