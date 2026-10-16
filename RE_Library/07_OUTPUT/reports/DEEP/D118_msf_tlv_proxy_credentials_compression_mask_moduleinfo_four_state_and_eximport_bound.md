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
