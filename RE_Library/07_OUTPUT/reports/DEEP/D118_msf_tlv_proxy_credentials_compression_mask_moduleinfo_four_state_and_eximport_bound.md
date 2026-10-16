# D118 - MSF: C2 proxy credentials on the wire, the COMPRESSED mask exclusion, ModuleInfo four-state, and the EXIMPORT bound

**Lane:** Metasploit core framework (engine only). **Owner:** msf-diver.
**Round 25, re-deploy of the briefed D109 (D109 failed mid-run; D118 is its replacement allocation).**

## 0. Allocation, conventions, and instrument record

### 0.1 Allocation line - D109 is a FAILED allocation, not a gap

**This document is D118. D109 was briefed, run, and died mid-report. It never landed and never will.**
`D109_*.md` does not exist and is **not** a missing document. The next reader must not hunt for it.

Allocated by enumeration over `07_OUTPUT/reports/DEEP` (191 files), with a positive control that the
regex bites a known filename. `[verified]`

| state | numbers |
| --- | --- |
| occupied (>= D95) | D95 D96 D97 D98 D99 D100 D101 D102 D103 D104 D105 D106 D107 D108 D110 D111 D113 D114 D115 |
| absent, in flight, not yet landed | D112 D116 D117 |
| **absent, failed allocation** | **D109** |
| allocated by this document | **D118** |

Control: `^D102` matched `D102_..._d90_u1_closure.md` (count = 1). Without the control the negative is
worthless - a broken pattern returns the same empty result as a true absence.

### 0.2 Line-count convention

A line is an LF-delimited record (`0x0A`). `file.rb:NNN` is the 1-based ordinal of the physical line,
counting blank lines and comments. LF count = count of `0x0A` bytes. `[verified]`

### 0.3 Confidence tags

- `[verified]` - read byte-for-byte out of the corpus in this session.
- `[read]` - read, but the surrounding semantics are not fully closed.
- `[inferred]` - reasoned from source. **No Ruby toolchain exists on this host; every Ruby/Rex dynamic claim is `[inferred]`.**
- `[absence]` - a measured zero, with its bound stated.

**NO RUBY TOOLCHAIN EXISTS ON THIS HOST.** `ruby`, `gem`, `bundle` are all absent. Nothing in this
document was executed. Where a claim depends on Ruby semantics it carries `[inferred]` **at the claim**.

### 0.4 Instrument record - the failures, stated as failures

**Shape 21 (`-match` is case-insensitive), re-stated because it is the sharpest instrument result in this lane.**

A `'proto'` / `'Proto'` census run under `-match` returned **48 / 48**. Under a corrected `-cmatch` it
returned **35 lowercase / 13 capital** corpus-wide, and **1 lowercase vs 8 capital** narrowed to sites
that actually reach a `Rex::Socket::Parameters` hash. **PowerShell `-match` is case-insensitive;
`-cmatch` is case-sensitive.**

The instructive part is not the wrong number. It is that **the probe did not fail. It succeeded and
returned a plausible number.** A quiet wrong answer is more dangerous than a loud crash, and only a
control that MUST fail catches it. The control here was the positive string, which matched BOTH
patterns and exposed the insensitivity.

**Shape 33 (a verifier making the exact error it exists to catch), re-stated.**

A probe whose entire job was catching a `%s` format applied against a tuple made that exact error
itself. **If you write a verifier, verify it against a known-correct document BEFORE believing its
failures.** A verifier with no positive control reports every document as broken, and a report full of
false failures is indistinguishable from a report full of real ones.

**New shape caught in this run (candidate for the ledger).** A *too-narrow* classifier regex inflated
an unresolvable count. Demanding the literal RHS form `TLV_TYPE_EXTENSION_\w+ + TLV_EXTENSIONS` routed
137 lines of the genuine form `TLV_META_TYPE_X | (TLV_EXTENSIONS + N)` into an `OTHER/unresolvable`
bucket. **The inflated number read as a hard problem; the truth was a broken pattern.** Caught only by
reading the mislabelled output rather than trusting the summary line.

**And one instrument I discarded outright.** A brace-depth-accumulating census of top-level
`update_info` keys returned 86 entries including `cookie`, `uri`, `method`, `data`, `headers`, `lang`.
Those are HTTP request hashes, not ModuleInfo keys - my `$inInfo` latch never re-armed, so the trigger
stayed hot for the rest of every file. **That census is used nowhere in this document.** A number I
cannot vouch for is worse than no number. Disclosed so a later reader does not re-derive it and
believe it.

---

## T1 - EXIMPORT: the option type, and why the finding is BOUNDED

**Task:** a single module passes one datastore value to **both** a shell command string **and** a
`Rex::Socket::Parameters` hash. Determine whether the value is free-text (a cross-sink interaction)
or constrained (a bounded finding).

### T1.1 The declaration, verbatim from the file

`[source: modules/exploits/linux/local/exim4_deliver_message_priv_esc.rb:70]` `[verified]`

```ruby
    register_options(
      [
        OptInt.new('EXIMPORT', [ true, 'The port exim is listening to', 25 ])
      ]
    )

```

**`EXIMPORT` is `OptInt`.** Not `OptPort`. Not `OptString`. The brief offered two options and the file
contains a third; the third is the safe one.

### T1.2 The three sinks - the same value, three routes

`[source: modules/exploits/linux/local/exim4_deliver_message_priv_esc.rb]` `[verified]`

```ruby
  def open_tcp_connection
    socket_subsystem = Rex::Post::Meterpreter::Extensions::Stdapi::Net::Socket.new(client)
    params = Rex::Socket::Parameters.new({
      'PeerHost' => '127.0.0.1',
      'PeerPort' => datastore['EXIMPORT']
    })
    begin
```

```ruby
    else
      unless cmd_exec("/bin/bash -c 'exec 3<>/dev/tcp/localhost/#{datastore['EXIMPORT']}' "\
                      '&& echo true').chomp.to_s == 'true'
        fail_with(Failure::NotFound, "Port #{datastore['EXIMPORT']} is closed")
      end
```

```ruby

      res = cmd_exec("/bin/bash -c 'exec 3</dev/tcp/localhost/#{datastore['EXIMPORT']} && "\
                     "(read -u 3 && echo $REPLY) || echo false'")
      if res == 'false'
```

**Three routes out of one datastore key:**

| route | site | sink |
| --- | --- | --- |
| A | `:94` | `'PeerPort'` into `Rex::Socket::Parameters.new` |
| B | `:146` | interpolation into `/bin/bash -c 'exec 3<>/dev/tcp/localhost/#{...}'` |
| C | `:210` | interpolation into `/bin/bash -c 'exec 3</dev/tcp/localhost/#{...} && ...'` |

### T1.3 What actually constrains it - the assignment path

`[source: lib/msf/core/opt_int.rb:22-26]` `[verified]`

```ruby
    def valid?(value, check_empty: true, datastore: nil)
      return false if check_empty && empty_required_value?(value)
      return false if value.present? && !value.to_s.match(/^0x[0-9a-fA-F]+$|^-?\d+$/)
      super
    end
  end
```

`[source: lib/msf/core/opt_int.rb:14-20]` `[verified]`

```ruby
    def normalize(value)
      if value.to_s.match(/^0x[a-fA-F\d]+$/)
        value.to_i(16)
      elsif value.present?
        value.to_i
      end
    end

```

`[source: lib/msf/core/data_store.rb:70-84]` `[verified]`

```ruby
  def []=(k, v)
    k = find_key_case(k)

    opt = @options[k]
    unless opt.nil?
      if opt.validate_on_assignment?
        unless opt.valid?(v, check_empty: false)
          raise Msf::OptionValidateError.new(["Value '#{v}' is not valid for option '#{k}'"])
        end
        v = opt.normalize(v)
      end
    end

    @user_defined[k] = v
  end

```

**The chain that bounds the finding:**

1. `OptInt` inherits `validate_on_assignment?` from `OptBase:112`, which returns **`true`**. `[verified]`
2. `data_store.rb:75` therefore runs the validator on every `datastore[k] = v` assignment. `[verified]`
3. `OptInt#valid?:24` rejects any value not matching `^0x[0-9a-fA-F]+$|^-?\d+$`, raising
   `Msf::OptionValidateError` at `:77`. `[verified]`
4. `OptInt#normalize:14-20` additionally maps the value through `value.to_i`, which truncates at the
   first non-digit. `[inferred]` - `String#to_i` semantics are Ruby runtime behaviour.

### T1.4 Verdict - BOUNDED

**The interpolation is integer-constrained. `#{datastore['EXIMPORT']}` cannot carry a shell
metacharacter through the operator-facing assignment path.**

Filed as bounded, with the constraint named, and **not** inflated. The constraint is:

- The gate is `OptInt`'s own shape check plus `to_i`. **Two independent mechanisms, both numeric.**
- The gate lives on the *assignment* path. `data_store.rb:98 store()` **skips validation entirely** -
  `[source: lib/msf/core/data_store.rb:96-100]`, comment at `:96` reads *"Skips option validation
  entirely"*. `[verified]` **A caller using `store()` rather than `[]=` bypasses the gate.** No caller
  in this module does; the bound is stated rather than assumed.
- `OptInt` is not `OptPort`. `OptPort` would additionally bound the range; `OptInt` accepts any
  integer, including negative values and values above 65535. **The finding is bounded against
  injection, not against a nonsensical port number.** Negative and out-of-range values are a
  separate, much smaller matter: `to_i` at `:18` and the raw integer both reach the shell string,
  where `-1` renders as `-1` and the `/dev/tcp/` connect simply fails. `[inferred]`

### T1.5 What I did NOT claim

`[absence]` **No execution was performed and none is possible.** There is no Ruby toolchain on this
host. The `valid?` -> `raise` -> `normalize` sequence is read from source, not observed. Every
dynamic statement in this section is `[inferred]`.

`[absence]` **Whether an operator can reach this module before assignment validation runs is not
established here.** The bound is on the documented assignment path.
---

## T2 - TLV residuals: the C2 proxy credential pair is LIVE

### T2.1 Declarations - and a correction to D102

`[source: lib/rex/post/meterpreter/packet.rb:125-126]` `[verified]`

```ruby
TLV_TYPE_C2_PROXY_USER         = TLV_META_TYPE_STRING | 711 # Proxy user name
TLV_TYPE_C2_PROXY_PASS         = TLV_META_TYPE_STRING | 712 # Proxy password
```

**CORRECTION TO D102.** D102 described `TLV_TYPE_C2_PROXY_USER` / `_PASS` as a
"BARE-ABSOLUTE (no `|` meta-type!)" pair. **That is wrong.** Both carry
`TLV_META_TYPE_STRING |` - the meta-type is present and explicit. D102 is a protected
document and is not edited; **D118 names the error so it is not repeated.**

- `TLV_TYPE_C2_PROXY_USER` = `TLV_META_TYPE_STRING | 711` `[verified]`
- `TLV_TYPE_C2_PROXY_PASS` = `TLV_META_TYPE_STRING | 712` `[verified]`

They are adjacent, same meta-type, same species. The D102 labelling error did not affect
its value census (711/712 are correct); it affected only the description.

### T2.2 The four-state test (D82 discipline), applied

| state | USER (711) | PASS (712) | site |
| --- | --- | --- | --- |
| DECLARED | yes | yes | `packet.rb:125-126` |
| OFFERED | yes, 2 writers | yes, 2 writers | `config.rb:123-124`, `client_core.rb:963-968` |
| READ | yes | yes | `client_core.rb:165-166` |
| HONOURED | yes, partial | yes, partial | `core.rb:920-921` renders them |

**Verdict: LIVE.** This is the opposite result from D90's `SSLClientCert`/`SSLClientKey`,
which were declared and read but dead. `[verified]`

### T2.3 WRITE SIDE A - payload generation (offline config)

`[source: lib/rex/payloads/meterpreter/config.rb:123-124]` `[verified]`

```ruby
        c2_tlv.add_tlv(MET::TLV_TYPE_C2_PROXY_USER, opts[:proxy_user]) unless (opts[:proxy_user] || '').empty?
        c2_tlv.add_tlv(MET::TLV_TYPE_C2_PROXY_PASS, opts[:proxy_pass]) unless (opts[:proxy_pass] || '').empty?
```

Both gated on `unless (opts[:X] || '').empty?`. **Paired and adjacent.** `[read]`

### T2.4 WRITE SIDE B - session-side transport add

`[source: lib/rex/post/meterpreter/client_core.rb:957-969]` `[verified]`

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

**Here the pair is NOT adjacent.** `:963-965` (USER) and `:966-968` (PASS) are separate
nested `if` blocks. Both write URL, then USER, then PASS - same order as side A. `[verified]`

**DEFECT FOUND IN THIS PASS - credentials are silently dropped without a proxy host.**

`opts[:proxy_user]` (`:963`) and `opts[:proxy_pass]` (`:966`) are nested **inside** the
`if opts[:proxy_host] && opts[:proxy_port]` guard opened at `:957`. `[verified]`

`[inferred]` **An operator who runs `transport add -U <user> -N <pass>` without also passing
`-H <host>` and `-P <port>` supplies both credentials and both are discarded with no message.**
The CLI reader is `core.rb:849`/`:851`; the guard is `client_core.rb:957`. Nothing between them
warns. This is the **same species as the `'proto'` lowercase drop**: an input that is accepted,
silently ignored, and produces a plausible result.

`[absence]` **Bound:** this is read from source, not observed. Whether the CLI parser rejects
`-U` without `-H` earlier is not established here. If it does, the defect is unreachable and is
a latent-shape rather than a live one. Stating the bound rather than assuming the worse case.

### T2.5 READ SIDE - and the consumer chain that makes it HONOURED

`[source: lib/rex/post/meterpreter/client_core.rb:143-172]` `[verified]`

```ruby
  def transport_list
    request = Packet.create_request(COMMAND_ID_CORE_TRANSPORT_LIST)
    response = client.send_request(request)

    result = {
      :session_exp => response.get_tlv_value(TLV_TYPE_SESSION_EXPIRY),
      :transports  => []
    }

    response.each(TLV_TYPE_C2) { |t|
      # TODO: Consider adding more information to the output for malleable profiles?
      # TLV_TYPE_C2_GET, TLV_TYPE_C2_POST, TLV_TYPE_C2_PREFIX, TLV_TYPE_C2_SUFFIX, TLV_TYPE_C2_ENC_INBOUND, TLV_TYPE_C2_ENC_OUTBOUND,
      # TLV_TYPE_C2_PREFIX_SKIP, TLV_TYPE_C2_SUFFIX_SKIP,
      # TLV_TYPE_C2_UUID_COOKIE, TLV_TYPE_C2_UUID_GET, TLV_TYPE_C2_UUID_HEADER
      # Not sure if this stuff is useful for this display though.
      result[:transports] << {
        :url            => t.get_tlv_value(TLV_TYPE_C2_URL),
        :comm_timeout   => t.get_tlv_value(TLV_TYPE_C2_COMM_TIMEOUT),
        :retry_total    => t.get_tlv_value(TLV_TYPE_C2_RETRY_TOTAL),
        :retry_wait     => t.get_tlv_value(TLV_TYPE_C2_RETRY_WAIT),
        :ua             => t.get_tlv_value(TLV_TYPE_C2_UA),
        :proxy_host     => t.get_tlv_value(TLV_TYPE_C2_PROXY_URL),
        :proxy_user     => t.get_tlv_value(TLV_TYPE_C2_PROXY_USER),
        :proxy_pass     => t.get_tlv_value(TLV_TYPE_C2_PROXY_PASS),
        :cert_hash      => t.get_tlv_value(TLV_TYPE_C2_CERT_HASH),
        :custom_headers => t.get_tlv_value(TLV_TYPE_C2_HEADERS)
      }
    }

    result
```

**The comment at `:153-157` enumerates ten unread C2 types** (`C2_GET`, `C2_POST`, `C2_PREFIX`,
`C2_SUFFIX`, `C2_ENC_INBOUND`, `C2_ENC_OUTBOUND`, `C2_PREFIX_SKIP`, `C2_SUFFIX_SKIP`,
`C2_UUID_COOKIE`, `C2_UUID_GET`, `C2_UUID_HEADER`). **Comment-membership test: these are NOT
use sites.** They are a TODO enumerating deliberate non-reads. `[verified]`

### T2.6 The HONOURED chain, end to end

`[source: lib/rex/post/meterpreter/ui/console/command_dispatcher/core.rb]` `[verified]`

```ruby
      when '-U'
        opts[:proxy_user] = val
      when '-N'
        opts[:proxy_pass] = val
      when '-A'
```

```ruby
        columns << 'Proxy User'
        columns << 'Proxy Pass'
        columns << 'Cert Hash'
```

```ruby
          entry << t[:ua]
          entry << t[:proxy_host]
          entry << t[:proxy_user]
          entry << t[:proxy_pass]
          entry << (t[:cert_hash] || '').unpack("H*")[0]
        end

```

**Full round trip, six stages, all source-verified:**

1. `core.rb:849` - operator types `transport add -U <user>`; value lands in `opts[:proxy_user]`.
2. `client_core.rb:963-964` - `if opts[:proxy_user]` then `add_tlv(TLV_TYPE_C2_PROXY_USER, ...)`.
3. `packet.rb:496` - egress; compression bit may be set. Type is `STRING | 711`.
4. `packet.rb:520` - ingress; compression bit stripped if present.
5. `client_core.rb:165` - `get_tlv_value(TLV_TYPE_C2_PROXY_USER)` into `:proxy_user`.
6. `core.rb:920` - `entry << t[:proxy_user]`, rendered under the `'Proxy User'` column
   (`core.rb:902`) when `-v` is passed (`core.rb:917`).

**`TLV_TYPE_C2_PROXY_USER` / `PASS` are LIVE: written, transmitted, read back, and displayed.**
`[verified]` for every file:line above; `[inferred]` for the wire transit between 3 and 4, which
no execution on this host can observe.

### T2.7 U1 - the 103 unresolved TLV expressions: RESOLVED TO ZERO

`[verified]` **Full resolution across all 18 `tlv.rb` files: resolved to a number = 393,
aliases = 5, STILL UNRESOLVABLE = 0, distinct values = 356.**

Arithmetic closes: 393 + 5 = 398 extension declarations, matching D102's 398 exactly.

**The three `TLV_TYPE_EXTENSION_*` sentinels are all `0`:**

| name | value | file:line |
| --- | --- | --- |
| `TLV_TYPE_EXTENSION_EXTAPI` | 0 | `extensions/extapi/tlv.rb:8` |
| `TLV_TYPE_EXTENSION_SNIFFER` | 0 | `extensions/sniffer/tlv.rb:10` |
| `TLV_TYPE_EXTENSION_RAILGUN` | 0 | `extensions/stdapi/railgun/tlv.rb:35` |

**Because all three are `0`, every `X + TLV_EXTENSIONS + N` collapses to `20000 + N`
regardless of which extension declares it.** `[inferred]`

**The 5 aliases, all mechanical and all resolving:**

- `extensions/android/tlv.rb:51` `TLV_TYPE_COLLECT_RESULT_WIFI = TLV_TYPE_WLAN_GROUP`
- `extensions/android/tlv.rb:52` `TLV_TYPE_COLLECT_RESULT_BSSID = TLV_TYPE_WLAN_BSSID`
- `extensions/android/tlv.rb:53` `TLV_TYPE_COLLECT_RESULT_SSID = TLV_TYPE_WLAN_SSID`
- `extensions/android/tlv.rb:54` `TLV_TYPE_COLLECT_RESULT_LEVEL = TLV_TYPE_WLAN_LEVEL`
- `extensions/stdapi/tlv.rb:126` `TLV_TYPE_ROOT_KEY = TLV_TYPE_HKEY`

### T2.8 The collision count rises 14 -> 23, and one of them is not a collision

Nine collisions were invisible to D102 purely because extapi/sniffer/railgun names could not
be resolved. `[verified]`

**Value `0` is shared by the three `TLV_TYPE_EXTENSION_*` names. It is a SENTINEL, not a
collision, and is reported as such for the reason that all three are deliberate `0` bases.**

| value | members |
| --- | --- |
| 85537 | POWERSHELL_SESSIONID, SAM_HASHES, PYTHON_STDOUT |
| 85538 | INCOGNITO_LIST_TOKENS_DELEGATION, LANATTACKS_OPTION_NAME, POWERSHELL_CODE, PYTHON_STDERR |
| 85539 | INCOGNITO_LIST_TOKENS_IMPERSONATION, POWERSHELL_RESULT |
| 85540 | EXT_WINDOW_ENUM_TITLE `extapi/tlv.rb:13`, PEINJECTOR_TARGET_EXECUTABLE `peinjector/tlv.rb:11`, WEBCAM_NAME `stdapi/tlv.rb:282` |
| 85541 | INCOGNITO_IMPERSONATE_TOKEN, PEINJECTOR_RESULT |
| 85542 | EXT_WINDOW_ENUM_CLASSNAME `extapi/tlv.rb:15`, INCOGNITO_GENERIC_RESPONSE, PYTHON_NAME |
| 85543 | INCOGNITO_USERNAME, PYTHON_RESULT_VAR |
| 85544 | INCOGNITO_PASSWORD, PYTHON_RESULT |
| 85545 | INCOGNITO_SERVERNAME `incognito/tlv.rb:15`, RAILGUN_LIBNAME `stdapi/railgun/tlv.rb:46` |
| 85546 | INCOGNITO_GROUPNAME, SNIFFER_ADDITIONAL_FILTER `sniffer/tlv.rb:24`, RAILGUN_FUNCNAME `stdapi/railgun/tlv.rb:47` |
| 85637 | BOFLOADER_EXECUTE_BUFFER_ENTRY, KIWI_CMD_RESULT |
| 151073 | RAILGUN_SIZE_OUT `stdapi/railgun/tlv.rb:36`, UNHOOK_ERROR_CODE, WINPMEM_ERROR_CODE |
| 151074 | EXT_WINDOW_ENUM_PID, PEINJECTOR_SHELLCODE_SIZE, SNIFFER_INTERFACE_ID, WEBCAM_INTERFACE_ID |
| 151075 | LANATTACKS_UINT, SNIFFER_INTERFACE_HANDLE, WEBCAM_QUALITY |
| 151076 | INCOGNITO_LIST_TOKENS_ORDER, POWERSHELL_ASSEMBLY_SIZE, PYTHON_CODE_LEN, SNIFFER_PACKET_COUNT |
| 151077 | PYTHON_CODE_TYPE, SNIFFER_BYTE_COUNT |
| 151086 | EXT_SERVICE_ENUM_STATUS `extapi/tlv.rb:21`, RAILGUN_MEM_LENGTH `stdapi/railgun/tlv.rb:52` |
| 282145 | LANATTACKS_OPTION, PEINJECTOR_SHELLCODE, WEBCAM_IMAGE |
| 282147 | PYTHON_CODE, RAILGUN_BUFFERBLOB_IN |
| 282148 | LANATTACKS_RAW, RAILGUN_BUFFERBLOB_INOUT |
| 282149 | POWERSHELL_ASSEMBLY, RAILGUN_BACK_BUFFERBLOB_OUT |
| 1073761825 | EXT_WINDOW_ENUM_GROUP `extapi/tlv.rb:10`, SNIFFER_INTERFACES `sniffer/tlv.rb:12` |

**KEY STRUCTURAL INSIGHT.** All extensions sit at the SAME base (`TLV_EXTENSIONS = 20000`)
and the same `+1..+N` low offsets. `railgun/tlv.rb` is a **stdapi subdirectory** whose types are
`META | (TLV_TYPE_EXTENSION_RAILGUN + TLV_EXTENSIONS + N)` = `20000 + N` - **so railgun collides
with every other extension's low range, and with stdapi proper.** `[verified]`

### T2.9 U3 - stdapi's bare absolutes: ZERO internal collisions

`[source: lib/rex/post/meterpreter/extensions/stdapi/tlv.rb]` - 297 lines. `[verified]`

Classifier (after the U1 fix): **bare absolutes (`META|N`, no `TLV_EXTENSIONS`) = 166,
`TLV_EXTENSIONS`-offset = 8, bare aliases = 1.** Closure: 166 + 8 + 1 = 175 = total `TLV_TYPE_`
declarations. `[verified]`

**Comment-membership test: total `TLV_TYPE_` declarations = 175, commented = 0.** `[verified]`

**STANDAPI INTERNAL COLLISIONS = 0.** No value in `stdapi/tlv.rb` is shared by two names in
that file. `[verified]`

`[absence]` **Bound:** this is an INTERNAL test - two names in the same file sharing a value.
It is not a claim that stdapi is collision-free against other extensions; per T2.8, railgun (a
stdapi subdirectory) shares values with stdapi proper. The zero is bounded to the file.

**Reconciliation note (stated, not smoothed).** D102's earlier census recorded stdapi at
x167 bare absolutes; this pass measures 166 bare + 1 alias. The one-value difference is the
alias `TLV_TYPE_ROOT_KEY = TLV_TYPE_HKEY` at `:126`, which the earlier classifier counted as
bare. **Two different quantities sharing a value is not confirmation** - the buckets are now
stated explicitly so the closure can be checked by hand: 166 + 8 + 1 = 175.
---

## T3 - TLV_META_MASK excludes COMPRESSED: what the filter does

### T3.1 The constants and the exclusion, verbatim

`[source: lib/rex/post/meterpreter/packet.rb:21-41]` `[verified]`

```ruby
TLV_META_TYPE_NONE          = 0
TLV_META_TYPE_STRING        = (1 << 16)
TLV_META_TYPE_UINT          = (1 << 17)
TLV_META_TYPE_RAW           = (1 << 18)
TLV_META_TYPE_BOOL          = (1 << 19)
TLV_META_TYPE_QWORD         = (1 << 20)
TLV_META_TYPE_COMPRESSED    = (1 << 29)
TLV_META_TYPE_GROUP         = (1 << 30)
TLV_META_TYPE_COMPLEX       = (1 << 31)

# Exclude compressed from the mask since other meta types (e.g. RAW) can also
# be compressed
TLV_META_MASK = (
  TLV_META_TYPE_STRING |
  TLV_META_TYPE_UINT |
  TLV_META_TYPE_RAW |
  TLV_META_TYPE_BOOL |
  TLV_META_TYPE_QWORD |
  TLV_META_TYPE_GROUP |
  TLV_META_TYPE_COMPLEX
)

```

| constant | value | bit |
| --- | --- | --- |
| `TLV_META_TYPE_NONE` | 0 | - |
| `TLV_META_TYPE_STRING` | 65536 | 16 |
| `TLV_META_TYPE_UINT` | 131072 | 17 |
| `TLV_META_TYPE_RAW` | 262144 | 18 |
| `TLV_META_TYPE_BOOL` | 524288 | 19 |
| `TLV_META_TYPE_QWORD` | 1048576 | 20 |
| `TLV_META_TYPE_COMPRESSED` | 536870912 | **29** |
| `TLV_META_TYPE_GROUP` | 1073741824 | 30 |
| `TLV_META_TYPE_COMPLEX` | 2147483648 | 31 |

**Bit 29 is DISJOINT from every other meta bit.** The mask is STRING|UINT|RAW|BOOL|QWORD|GROUP|COMPLEX
= all meta bits EXCEPT bit 29. The comment at `:31-32` gives the reason verbatim:
*"Exclude compressed from the mask since other meta types (e.g. RAW) can also be compressed"*.
`[verified]`

**So COMPRESSED is an OVERLAY BIT, not a meta-type.** A compressed STRING is `COMPRESSED|STRING`.
The mask answers "which meta-type is this, ignoring compression".

### T3.2 Complete census of `TLV_META_MASK` references

Control in the same invocation: positive string matched, typo string did not. `[verified]`

**`TLV_META_MASK` has EXACTLY 2 references corpus-wide, both in `packet.rb`:**

| site | role |
| --- | --- |
| `packet.rb:33` | the definition |
| `packet.rb:366` | **the only consumer** |

`[source: lib/rex/post/meterpreter/packet.rb:363-375]` `[verified]`

```ruby
  def inspect
    utype = type ^ TLV_META_TYPE_COMPRESSED
    group = false
    meta = case (utype & TLV_META_MASK)
      when TLV_META_TYPE_STRING; "STRING"
      when TLV_META_TYPE_UINT; "INT"
      when TLV_META_TYPE_RAW; "RAW"
      when TLV_META_TYPE_BOOL; "BOOL"
      when TLV_META_TYPE_QWORD; "QWORD"
      when TLV_META_TYPE_GROUP; group=true; "GROUP"
      when TLV_META_TYPE_COMPLEX; "COMPLEX"
      else; 'unknown-meta-type'
      end

```

**The single consumer is inside `def inspect` - a DISPLAY function.** `[read]`

### T3.3 Complete census of every COMPRESSED bit operation

`[verified]` **15 sites in the whole corpus, all inside `packet.rb`, zero outside:**

| site | operation | direction |
| --- | --- | --- |
| `:335` | `type & TLV_META_TYPE_STRING == ...` | `Tlv#initialize` test |
| `:364` | `utype = type ^ TLV_META_TYPE_COMPRESSED` | `inspect`, defensive XOR |
| `:366` | `utype & TLV_META_MASK` | **the only mask use** |
| `:472` | `self.type & TLV_META_TYPE_STRING == ...` | `to_r`, egress |
| `:474` | `self.type & TLV_META_TYPE_UINT == ...` | `to_r`, egress |
| `:476` | `self.type & TLV_META_TYPE_QWORD == ...` | `to_r`, egress |
| `:478` | `self.type & TLV_META_TYPE_BOOL == ...` | `to_r`, egress |
| `:496` | `self.type = self.type \\| TLV_META_TYPE_COMPRESSED` | **SET** - `to_r` |
| `:515` | `self.type & TLV_META_TYPE_COMPRESSED == ...` | test before strip |
| `:520` | `self.type = self.type ^ TLV_META_TYPE_COMPRESSED` | **STRIP** - `from_r` |
| `:529` | `self.type & TLV_META_TYPE_STRING == ...` | `from_r` value decode |
| `:535` | `self.type & TLV_META_TYPE_UINT == ...` | `from_r` value decode |
| `:537` | `self.type & TLV_META_TYPE_QWORD == ...` | `from_r` value decode |
| `:540` | `self.type & TLV_META_TYPE_BOOL == ...` | `from_r` value decode |
| `:668` | `type & TLV_META_TYPE_GROUP == ...` | group iteration |
| `:773` | `type & TLV_META_TYPE_GROUP == ...` | group iteration |

### T3.4 The answer: does anything re-add the bit?

**`[verified]` NO reader re-adds it. And the reason is structural, not lucky.**

**The strip happens at the single ingress point.** `[source: packet.rb:509-527]` `[verified]`

```ruby
  def from_r(raw)
    self.value  = nil

    length, self.type = raw.unpack("NN");

    # check if the tlv value has been compressed...
    if( self.type & TLV_META_TYPE_COMPRESSED == TLV_META_TYPE_COMPRESSED )
      # set this TLV as using compression
      @compress = true
      # remove the TLV_META_TYPE_COMPRESSED flag from the tlv type to restore the
      # tlv type to its original, allowing for transparent data compression.
      self.type = self.type ^ TLV_META_TYPE_COMPRESSED
      # decompress the compressed data (skipping the length and type DWORD's)
      raw_decompressed = Rex::Text.zlib_inflate( raw[HEADER_SIZE..length-1] )
      # update the length to reflect the decompressed data length (+HEADER_SIZE for the length and type DWORD's)
      length = raw_decompressed.length + HEADER_SIZE
      # update the raw buffer with the new length, decompressed data and updated type.
      raw = [length, self.type].pack("NN") + raw_decompressed
    end
```

**`from_r` is the entry point for all wire data.** At `:515` it tests for the compressed bit;
at `:520` it strips it with XOR; at `:522` it decompresses. **Every downstream type test therefore
sees a clean type.** `[inferred]` - that all wire data arrives via `from_r` is a call-graph
property read from source, not an observed invariant.

### T3.5 Why the OTHER tests are immune without needing the mask

Every type test outside `inspect` uses the **equality form**:

```ruby
  self.type & TLV_META_TYPE_X == TLV_META_TYPE_X
```

**This form is immune to overlay bits.** If `type = COMPRESSED|STRING`, then
`type & STRING == STRING` is still TRUE, because `&` selects the STRING bit which is set
regardless of bit 29 being set. `[inferred]` - bitwise AND semantics.

| test shape | survives an overlay bit? | needs the mask? |
| --- | --- | --- |
| `type & X == X` | **yes**, by construction | no |
| `type & TLV_META_MASK` then `case` | no - returns the meta only | **yes** |

**This is why exactly one site needs the mask and it is the one that switches on the WHOLE type**
**rather than testing one bit.** `:366` asks "what is this?" - a question the overlay bit would
corrupt. `:472`, `:529` etc. ask "is the STRING bit set?" - a question it cannot corrupt.

### T3.6 The one site that is safe only by coincidence

`[source: packet.rb:335]` `[verified]`

```ruby
      if (type & TLV_META_TYPE_STRING == TLV_META_TYPE_STRING)
```

`Tlv#initialize` tests the string bit on a type that may ALREADY carry COMPRESSED (a Tlv can be
constructed with a compressed type and `to_r` will set the bit at `:496`). `[read]`

**It does not strip COMPRESSED and does not need to** - same equality-form immunity. Stated
because it is the site that LOOKS wrong at a glance and is not.

### T3.7 Verdict

**The mask that drops a bit is a filter over a DISPLAY question, and its exclusion is correct.**

`[verified]` The exclusion is necessary: without it, `case (utype & TLV_META_MASK)` would never
match anything for a compressed TLV, because `COMPRESSED|STRING` masked against a mask that
INCLUDED COMPRESSED would yield `COMPRESSED|STRING`, which matches no `when TLV_META_TYPE_STRING`
branch and falls to `'unknown-meta-type'` at `:374`. `[inferred]`

**`[absence]` No correctness-forcing bug is present at this layer.** The COMPRESSED bit is set at
one egress site, stripped at one ingress site, and every intervening test is overlay-immune.
**Bound:** this is a static reading of `packet.rb`. Ruby semantics are `[inferred]`. Nothing was
executed, and `TLV_META_TYPE_COMPRESSED` must be an INTEGER with only bit 29 set for the argument
to hold - which `:27` reading `1 << 29` establishes. `[verified]`
---

## T4 - ModuleInfo keys: read, never validated, and what each absence DOES

### T4.1 The headline shape - absence and invalid-value are DIFFERENT STATES, and the code conflates them

`'Handler'` is the template. It is read at exactly ONE site in all of `lib/`.

`[source: lib/msf/core/payload.rb:280-282]` `[verified]`

```ruby
  def handler_klass
    return module_info['Handler'] || Msf::Handler::None
  end
```

**The `|| Msf::Handler::None` covers ABSENCE ONLY.** `[verified]`

| state of `module_info['Handler']` | result of `handler_klass` |
| --- | --- |
| key absent | `Msf::Handler::None` - **safe default** |
| key => valid class | the class - correct |
| key => **present but wrong** (`"not a class"`) | **`"not a class"` passed through UNTOUCHED** |

`[inferred]` A `String` is truthy in Ruby, so `'Handler' => 'not a class'` short-circuits the
`||` and returns the string. **The default guards absence and is blind to invalidity.**

### T4.2 `'Handler'` is on the critical path for a SECOND key

`[source: lib/msf/core/payload.rb:264-266]` `[verified]`

```ruby
  def connection_type
    handler_klass.general_handler_type
  end
```

**`connection_type` is DERIVED from `handler_klass.general_handler_type`.** `[verified]`

So a present-but-wrong `'Handler'` breaks **two** keys, and the second is a method CALL on the
passthrough value. `[inferred]` **`'Handler' => 'not a class'` raises `NoMethodError` at
`payload.rb:265`** on the first `connection_type` call, with no `rescue` between.

### T4.3 Where the NoMethodError surfaces, and whether anything catches it

`[verified]` **There are two distinct downstream failure modes, and they differ in kind:**

**Mode 1 - `NoMethodError` (loud).** `[source: lib/msf/core/payload_set.rb:461]`

```ruby
      next if (handler and not p.handler_klass.ancestors.include?(handler))
```

`p.handler_klass.ancestors` - **a method call on the value.** A string raises `NoMethodError`.
`[inferred]` This is the ONLY path that fails loudly.

**Mode 2 - SILENT NO-SELECTION (quiet, and the dangerous one).**
`[source: lib/msf/core/payload_set.rb:487]` `[verified]`

```ruby
      next if (handler and p.handler_klass != handler)
```

`p.handler_klass != handler` - **a comparison, not a call.** A wrong value is simply `!=` the
requested handler, so `next` skips the candidate. `[inferred]` **The loop exhausts and returns
`nil` at `:472`, which the caller reports as "no payload found".**

**The same malformed value produces a raised error on one path and a silent miss on the other.**
`'Handler'` is consumed by reflection, never validated. `[verified]`

### T4.4 `[absence]` There is NO ModuleInfo-key validation layer anywhere in `lib/`

`[verified]` Every `def validate*` in `lib/` concerns options, credentials, RPC inputs, NTLM
blobs, Kerberos, X.509, or config. **Not one validates a ModuleInfo key.**

`[absence]` **`'Handler'` has no validation anywhere** - not in `lib/`, not in `msftidy`.
`tools/dev/msftidy.rb` (32,551 chars) contains exactly ONE `Handler` occurrence, unrelated:
`L559: return if @source =~ /Generic Payload Handler/`. `[verified]`

**A NEAR-MISS that must not be reported as a validator.** `[source: lib/msf/core/module/module_info.rb:7]` `[verified]`

```ruby
  UpdateableOptions = ['Name', 'Description', 'Alias', 'PayloadCompat', 'Stance'].freeze
```

`UpdateableOptions` is an allow-list for *updateable* keys, governing `update_info` MERGING.
**It is not value validation.** A key on the list is still unvalidated when set. `[read]`

### T4.5 The generalisation - every core ModuleInfo key with a `lib/` bracket read

`[source: lib/msf/core/payload.rb, handler.rb, module.rb]` `[verified]`

| key | read site | default? | absent state | present-invalid state |
| --- | --- | --- | --- | --- |
| `'Handler'` | `payload.rb:281` | `\\|\\| Msf::Handler::None` | safe default | **`NoMethodError` (`:265`) or silent miss (`:487`)** |
| `'Session'` | `payload.rb:289` | **none** | `nil` propagates | **`NoMethodError` at `payload_set.rb:464`** |
| `'HandlerName'` | `handler.rb:67` | **none** | `nil` | interpolated into a display string |
| `'BadChars'` | `payload.rb:112` | **none** | `nil` | `nil` treated as "no bad chars" |
| `'SaveRegisters'` | `payload.rb:120` | **none** | `nil` | `nil` treated as "nothing to save" |
| `'Dependencies'` | `payload.rb:247` | `[]` at `:59` | safe default | non-array propagates |
| `'Convention'` | `payload.rb:257` | **none** | `nil` = "any convention" | wrong symbol = no stage match |
| `'SymbolLookup'` | `payload.rb:273` | **none** | `nil` | wrong value propagates |
| `'Payload'` | `payload.rb:66`, `:217`, `:224`, `:232`, `:240` | hash `||` guards | staged defaults written | wrong shape propagates |
| `'Stage'` | `payload.rb:67-74` | `{}` written | safe defaults | wrong shape propagates |
| `'PayloadCompat'` | **not read in `lib/` via brackets** | merged to `'Compat'` | - | - |

`[verified]` **Six of eleven have NO default at all** - a bare `module_info['X']` return. Absence
yields `nil`, and what `nil` DOES depends entirely on the consumer.

### T4.6 Rule 21, in both directions

**When a key is ABSENT, what does its absence DO?**

- `'Handler'` absent -> `Msf::Handler::None` -> `general_handler_type` returns a value, and the
  handler-selection comparison at `:487` runs against `None`. **The absence is LOAD-BEARING:**
  it does not error, it selects the None handler. A payload with no handler is treated as
  handler-less by DESIGN, not by accident. `[read]`
- `'Dependencies'` absent -> `[]` written at `:59`. **Absence is normalised on first read.** `[verified]`
- `'Stage'` absent -> a `{}` skeleton with three keys is written at `:71-74`. **Absence is
  repaired, not defaulted.** `[verified]`
- `'Convention'` absent -> `nil`, which the stage-compatibility logic reads as "no constraint".
  **Absence is PERMISSIVE, not safe.** `[inferred]` *Never set in corpus* is not the same claim
  as *cannot be set*, and neither is the same as *would be rejected*.

**When a key is PRESENT-INVALID, what does it do?**

This is the state the code has no story for. `'Handler'` present-invalid reaches
`.general_handler_type` (`:265`), `.ancestors` (`:461`), and `!= handler` (`:487`).
**Two loud and one quiet. The quiet one is `find_payload_from_set` returning `nil` at `:472`. `[inferred]`**

### T4.7 What I did NOT claim

`[absence]` **No execution.** `NoMethodError` vs silent-nil is a Ruby-semantics prediction from
source. Nothing was run. **`'Handler' => 'not a class'` is a HYPOTHETICAL input** - the corpus
contains no such module, and the claim is about what the code would do, not what it has done.

`[absence]` **The 1,828-key bracket census that produced the broader key landscape is NOT cited
here as a count.** Only the sites printed in T4.5 are claimed. The wider census carried an
instrument defect disclosed in section 0.4 and is not load-bearing.
---

## T5 - `Rex::Socket::Parameters`, field by field, four-state

`[source: RE_Library/04_TOOLS/gems/rex-socket-0.1.71/src/lib/rex/socket/parameters.rb]` - 13,250 bytes,
505 lines. `[verified]`

### T5.1 The four states, defined for this struct

| state | meaning for a Parameters field |
| --- | --- |
| **ABSENT** | no `from_hash` key offers it and no caller sets the writer; the accessor's own default applies |
| **DECLARED-EMPTY** | a caller passes the key with `nil`/`''`; the `if hash['X']` guard is falsy so the writer never runs |
| **DECLARED-WITH-VALUE** | a caller passes a truthy value; the writer runs |
| **DECLARED-WITH-INVALID-VALUE** | a caller passes a value of the wrong kind; the guard is truthy so the writer runs and the bad value is STORED |

**The critical structural fact: every `from_hash` guard is a bare presence-test.** `[verified]`
There is not one type check among them. **State 4 is indistinguishable from state 3 at the guard.**

### T5.2 The 26 declared fields with their accessor kinds

`[verified]` **12 `accessor`, 13 `writer`-only, 1 `reader`-only.** The asymmetry matters: a
writer-only field needs a hand-written getter, and that is where defaults and defects live.

| line | declaration | getter | default when absent |
| --- | --- | --- | --- |
| 309 | `attr_accessor :peerhost` | accessor | `nil` |
| 314 | `attr_accessor :peerhostname` | accessor | `nil` |
| 319 | `attr_accessor :sslkeylogfile` | accessor | `nil` |
| 323 | `attr_writer :peerport` | `:324` | `0` |
| 330 | `attr_writer :localhost` | `:332` | `'0.0.0.0'` or `'::'` |
| 344 | `attr_writer :localport` | `:345` | `0` |
| 352 | `attr_writer :proto` | `:353` | **`'tcp'`** |
| 360 | `attr_writer :server` | `:361` | `nil` |
| 367 | `attr_writer :comm` | `:388` | `nil` |
| 387 | `attr_writer :context` | `:388` | `nil` |
| 394 | `attr_writer :retries` | `:395` | `nil` |
| 401 | `attr_writer :timeout` | `:402` | `nil` |
| 409 | `attr_writer :bare` | **`:410` returns `@comm`** | **`@comm \\|\\| false`** |
| 416 | `attr_writer :ssl` | `:289 ssl?` | `nil` |
| 423 | `attr_accessor :sslctx` | accessor | `nil` |
| 427 | `attr_reader :ssl_version` | reader | `nil` |
| 453 | `attr_accessor :ssl_cipher` | accessor | `nil` |
| 457 | `attr_accessor :ssl_cn` | accessor | `nil` |
| 462 | `attr_accessor :ssl_cert` | accessor | `nil` |
| 466 | `attr_accessor :ssl_compression` | accessor | `nil` |
| 471 | `attr_accessor :ssl_client_cert` | accessor | `nil` |
| 476 | `attr_accessor :ssl_client_key` | accessor | `nil` |
| 480 | `attr_accessor :ssl_verify_mode` | accessor | `nil` |
| 485 | `attr_writer :v6` | `:296 v6?` | `nil` |
| 492 | `attr_accessor :proxies` | accessor | `nil` |
| 496 | `attr_accessor :interface` | accessor | `nil` |

### T5.3 The `bare` defect, verbatim, and its chain into `bare?`

`[source: parameters.rb:409-412]` `[verified]`

```ruby
  attr_writer :bare
  def bare
    @comm || false
  end
```

`[source: parameters.rb:282-284]` `[verified]`

```ruby
  def bare?
    return (bare == true)
  end
```

**`attr_writer :bare` writes `@bare`. `def bare` returns `@comm`. `bare?` tests `bare == true`,
i.e. `(@comm || false) == true`. `[verified]`**

| action | written ivar | read by `bare` | read by `bare?` |
| --- | --- | --- | --- |
| `'Bare' => true` via `from_hash:112-113` | `@bare` | **`@comm`** | **`@comm`** |
| `params.bare = true` (direct) | `@bare` | **`@comm`** | **`@comm`** |

**`@bare` is write-only dead storage. `bare?` can only ever return true if `@comm` is exactly
`true` - and `@comm` is the socket object (`from_hash:188`), never a boolean. `[inferred]`**

**Independent confirmation by a different route.** `[verified]` A corpus-wide census of
`params.<field>` uses over `lib/`, `modules/` and the rex-socket gem found `params.bare` used
**zero** times and `params.bare?` used **4** times (`local.rb:110`, `:292`, `:403`, and one more).
The field is declared, offered by `from_hash`, and **honoured by nobody**.

**This is D77's "`bare?` is a dead gate" finding, reached independently from the field census. `[verified]`**

### T5.4 Fields DECLARED but never used as `params.<x>` anywhere in the corpus

`[verified]` The single-pass census (control: positive string matched, typo did not) over
`lib/`, `modules/` and the rex-socket gem gives **exactly three fields with zero consumers:**

| field | declared | hand-written getter | consumers |
| --- | --- | --- | --- |
| `bare` | `:409` | `:410` (defective) | **0** |
| `ssl?` | `:289` | is itself a getter over `ssl` | **0** |
| `v6?` | `:296` | is itself a getter over `v6` | **0** |

`[absence]` **Bound:** this is a census of the literal accessor forms `params.X` / `.X`. A field
read through `send`, through a local alias, or through `instance_variable_get` would not appear.
**Zero here means "no direct accessor call site", not "dead by design".** `[read]`

`[read]` Note `ssl` and `v6` (the raw ivars behind `ssl?`/`v6?`) are written by `from_hash` at
`:116` and `:219` and read by `ssl?`/`v6?` themselves. So they are WIRED but their public
predicates have no callers. **Wired-but-unqueried, not unwired.**

### T5.5 Offered-by-caller: the `from_hash` key surface

`[verified]` The `from_hash` reader has **three shapes**, and they differ in how they treat absence:

- `if hash['X']` ... `self.x = hash['X']` - **presence-guarded** (22 keys)
- `self.x = hash['X']` with **no guard** - **unconditional** (3 keys: `'Server' :185`,
  `'Comm' :188`, `'Context' :191`). A caller passing the key with an explicit `nil` OVERWRITES
  whatever was there. `[verified]`
- `hash.fetch('SSLVersion', nil)` at `:128` - **fetch-form**, invisible to a `hash['X']` pattern.
  This is the `SSLVersion` blind spot D90 recorded; it is restated here because it is the reason
  a `hash[\'...']` census UNDERCOUNTS. `[verified]`

### T5.6 Honoured: the transport consumers, enumerated

`[source: rex-socket .../socket/ssl_tcp.rb]` `[verified]`

| site | field consumed |
| --- | --- |
| `ssl_tcp.rb:100-101` | `params.ssl_client_cert` -> `sslctx.cert` |
| `ssl_tcp.rb:105-106` | `params.ssl_client_key` -> `sslctx.key` |
| `ssl_tcp.rb:116-117` | `params.ssl_verify_mode` -> `sslctx.verify_mode` |
| `ssl_tcp.rb:126-127` | `params.ssl_cipher` -> `sslctx.ciphers` |
| `ssl_tcp.rb:150` | `params.timeout` -> `Timeout.timeout` |
| `ssl_tcp.rb:168` | `params.peerhost` / `params.peerport` -> error message |
| `ssl.rb:122-123` | `params.ssl_cert` |
| `ssl.rb:125` | `params.ssl_cn` |
| `ssl.rb:141-142` | `params.ssl_cipher` |
| `ssl.rb:148` | `params.ssl_compression` |
| `tcp.rb:66` | `params.ssl_version` |
| `tcp_client_channel.rb:56` | `params.retries` |
| `local.rb:110`, `:292`, `:403` | `params.bare?` (**always false - see T5.3**) |
| `local.rb:165`, `:173`, `:176` | `params.interface` |
| `socket.rb:90` | `params.server?` |
| `client.rb:36` | `params.sslkeylogfile` |
| `bind_aws_ssm.rb:273-274` | `params.comm`, `params.peerhostname` |

**Every one of these is `[inferred]` at the behavioural level.** The call sites are `[verified]`;
what the transport does with the value is not executed here.

### T5.7 The four-state table - the deliverable artifact

| field | absent | declared-empty | declared-with-value | declared-invalid | honoured? |
| --- | --- | --- | --- | --- | --- |
| `peerhost` | nil | guard falsy, unset | stored | stored as-is | yes |
| `peerhostname` | nil | guard falsy, unset | stored | stored | yes |
| `sslkeylogfile` | nil | guard falsy, unset | stored | stored | yes |
| `peerport` | `0` | guard falsy -> `0` | `to_i` at `:105` | `"abc".to_i` = 0 | yes |
| `localhost` | `'0.0.0.0'`/`'::'` | guard falsy | stored | stored | yes |
| `localport` | `0` | guard falsy -> `0` | `to_i` at `:109` | 0 | yes |
| `proto` | **`'tcp'`** | guard falsy -> `'tcp'` | `downcase` at `:181` | stored | yes |
| `server` | nil | **UNGUARDED `:185` -> nil** | stored | stored | yes |
| `comm` | nil | **UNGUARDED `:188` -> nil** | stored | stored | yes |
| `context` | nil | **UNGUARDED `:191` -> nil** | stored | stored | yes |
| `retries` | nil | guard falsy | `to_i` at `:201` | 0 | yes |
| `timeout` | nil | guard falsy | `to_i` at `:206` | 0 | yes |
| `bare` | **`@comm \\|\\| false`** | guard falsy | `@bare` written | `@bare` written | **NO - T5.3** |
| `ssl` | nil | guard falsy | **`/^(t\\|y\\|1)/i` coercion `:116`** | non-matching -> unset | via `ssl?` |
| `sslctx` | nil | guard falsy | stored | stored | yes |
| `ssl_version` | nil | `fetch` -> nil | stored | stored | yes (`tcp.rb:66`) |
| Others | nil | guard falsy | stored | stored | - |

**`'SSL'` is the one field with a REAL coercion** (`:116`, `=~ /^(t\\|y\\|1)/i`). `[verified]`
**`'SSLCompression'` at `:135-136` has NONE** - bare truthiness, so a string `'false'` is
truthy and enables compression. `[read]` (D90 recorded this; restated as a four-state row.)

**`'SSLVerifyMode'` at `:130-132` is the one field with a REAL allow-list** - `include?` against
`%W{CLIENT_ONCE FAIL_IF_NO_PEER_CERT NONE PEER}`, and a non-member is **silently dropped**, not
rejected. That is state 4 behaving as state 2. `[verified]`

---

## T6 - D85's `osx/` escaping sites do NOT route through `Rex::Socket::Parameters`

### T6.1 The result

`[verified]` **`modules/post/osx/` contains ZERO references to `Rex::Socket`.**

Census: **23 `.rb` files, 23 total `Rex::*` references.** Enumerated:

| file | reference |
| --- | --- |
| `modules/post/osx/capture/screen.rb` | `Rex::Text` x2, `Rex::Post` |
| `modules/post/osx/escalate/tccbypass.rb` | `Rex::Version` x3, `Rex::Text` |
| `modules/post/osx/gather/enum_adium.rb` | `Rex::Text` |
| (remaining 20 files) | no `Rex::*` reference at all |

**`[absence]` Not one `Rex::Socket`, not one `Socket::Parameters`, not one `SSLSocket`.**
Controls in the same invocation: a positive string matched `Rex::Socket` and a typo string did not.

### T6.2 What that means for the Lead's hypothesis

The hypothesis was: **if an `osx/` escaped site routed through `Rex::Socket::Parameters`, the
escaping would be a transport-contract question rather than a module convention.**

**The hypothesis is FALSIFIED for the `osx/` population.** D85's 49 escaped expressions reach a
shell, not a socket. The escaping question stays entirely inside the module-convention lane.
**D85's `49 of 49` is not re-derived here**, per standing instruction; only the routing question
is answered.

### T6.3 The one corpus-wide intersection, and it is not `osx/`

`[verified]` A corpus-wide intersection (files that build a `Socket::Parameters` hash AND do shell
interpolation) returns **exactly ONE module:**

```
modules/exploits/linux/local/exim4_deliver_message_priv_esc.rb
```

**That is T1's module.** The only place in the corpus where a shell string and a `Parameters`
hash receive the same datastore value. **T1's `OptInt` verdict therefore closes both tasks:**
there is exactly one candidate for a cross-sink interaction anywhere in the corpus, and its
value is integer-constrained.

`[absence]` **Bound:** the intersection test keyed on the literal strings `Socket::Parameters`
and `cmd_exec`/`shell_command`/`command_string`. A module reaching a socket through a helper, or
a shell through a different helper name, would not appear. **One is a floor, not a proven total.**
---

## T7 - Status, blocked items, and residual unknowns

### T7.1 Blocked

**D77 U1 remains BLOCKED.** It is named here rather than worked around. `[absence]` No attempt
was made to resolve it in this run and no partial result is offered. **The blocker is the absence
of a Ruby toolchain on this host**, restated in section 0.3. Resolving it requires execution.

### T7.2 Confirmed-corrected from prior reports

**D102 corrected (not edited):** `TLV_TYPE_C2_PROXY_USER`/`_PASS` were described as
"BARE-ABSOLUTE (no `|` meta-type!)". **They carry `TLV_META_TYPE_STRING |`.** `[verified]`

**D90 corrected (not edited):** `SSLClientCert`/`SSLClientKey` were predicted latent. D102
established the crossed-assignment defect is LIVE at
`modules/exploits/linux/misc/fortimanager_rce_cve_2024_47575.rb:186`/`:188`. D118 does not
re-derive this; it is restated because T5's four-state table depends on the same two fields.
`[verified]`

**D102's consumer test must be re-run over 23 collisions, not 14.** `[absence]` **Not done in
this document.** T2.8 enumerates all 23 values with members, but the per-name consumer test
(does any name collide with another INSIDE a shared file?) is re-run only for stdapi (T2.9).
**The other 17 files are not re-tested here.** Named as open rather than implied closed.

### T7.3 Residual unknowns

| id | status | question | why it is open |
| --- | --- | --- | --- |
| U1 | **BLOCKED** | D77 U1 | no Ruby toolchain |
| U2 | resolved | C2 proxy credential liveness | **LIVE** - T2.6, six-stage chain |
| U3 | resolved | 103 unresolved TLV expressions | **0 unresolvable** - T2.7 |
| U4 | resolved | stdapi internal collisions | **0** - T2.9 |
| U5 | **open** | D102's consumer test over all 23 collisions | T7.2 - only stdapi re-run |
| U6 | **open** | whether the CLI parser rejects `-U` without `-H` | T2.4 bound |
| U7 | **open** | `'Handler' => 'not a class'` is hypothetical; no such module exists | T4.7 |
| U8 | **open** | D85 U1 / jruby paths / `client.rb:554-557` NTLM | carried from D77/D102, untouched |

### T7.4 Self-flagged instrument defects

Per standing practice: **a false positive of my OWN pattern is reported rather than left to read clean.**

- The `module_info['Handler']` bracket census returned 3 hits; only `payload.rb:281` is a
  ModuleInfo read. The other two (`session_upgrade.rb:44`, `:48`) are `datastore['HANDLER']` -
  a different quantity. **A bracket regex cannot distinguish them.** `[verified]`
- The `create_param` pattern produced 10 false positives out of 18 hits on `drda_*` and
  `*_params_value_*` helper names. `[verified]`
- The `params.<field>` single-pass census reported one name with `n=0` (`fuzzable.rb:33`), which
  is a match-inside-another-word artifact, not a field use. `[verified]`

### T7.5 Standing bounds stated with every negative

- `[absence]` **"Never set in corpus" is not "cannot be set".** Ids above are corpus-bounded.
- `[absence]` **A zero produced by a probe that contradicts a site you can read is a BROKEN probe.**
  No such contradiction was found in this run; the disclosure in T5.4 stands as the bound.
- `[absence]` **No live handler was authorised, simulated, or contacted.** Static source reading only.
- `[absence]` **Nothing was executed.** No Ruby, no network, no REA, no `open_binary`.

---

## T8 - Summary of headline results

1. **T1 - `EXIMPORT` is `OptInt`, not `OptPort`, not `OptString`. Finding BOUNDED.** The only
   corpus-wide shell/socket cross-sink shares an integer-constrained value.
2. **T2 - `TLV_TYPE_C2_PROXY_USER` (711) / `PASS` (712) are LIVE.** Declared, offered by two
   writers, read back at `client_core.rb:165-166`, rendered at `core.rb:920-921`. A proxy
   credential with a full six-stage round trip. **Plus a new defect:** both are nested inside
   the `proxy_host && proxy_port` guard at `client_core.rb:957`, so `-U`/`-N` without `-H`/`-P`
   is silently discarded.
3. **T2 - 103 unresolved TLV expressions -> 0.** Collisions rise **14 -> 23**, of which one
   (value `0`) is a **sentinel, not a collision**. stdapi internal collisions = **0**.
4. **T3 - the COMPRESSED mask exclusion is CORRECT and display-scoped.** `TLV_META_MASK` has
   exactly **2** references corpus-wide; the sole consumer is `inspect:366`. The strip is at
   `from_r:520`; **nothing re-adds the bit**; every non-mask test uses the overlay-immune
   equality form `type & X == X`.
5. **T4 - absence and invalid-value are DIFFERENT STATES and `'Handler'` conflates them.**
   `payload.rb:281`'s `|| Msf::Handler::None` guards absence only; a present-but-wrong value
   passes through and reaches `.general_handler_type` (`:265`), `.ancestors` (`:461`) and
   `!= handler` (`:487`) - **two loud failures and one silent no-selection.**
6. **T5 - `bare` is write-only dead storage.** `attr_writer :bare` writes `@bare`; `def bare`
   returns `@comm`; so `bare?` (`:283`) can never return true. D77's dead-gate finding
   confirmed independently from the field census. Three fields have ZERO consumers.
7. **T6 - D85's `osx/` escaping does NOT route through `Rex::Socket::Parameters`.**
   `modules/post/osx/` has **zero** `Rex::Socket` references across 23 files. The hypothesis
   is falsified; the escaping stays a module-convention question.

**End of D118.**
