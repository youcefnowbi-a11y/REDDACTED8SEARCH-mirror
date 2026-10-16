# D144 - Meterpreter wire fingerprint DB entry: the minimum firing set, GUID entropy, and a computed false-positive rate

**SCOPE:** a detection rule for the Meterpreter transport as an observable byte stream -
the minimum feature conjunction that fires on Meterpreter and on nothing else in this
corpus, with a computed false-positive rate per feature and for the conjunction.
**DEFINER SCOPE:** every feature is defined in `lib/rex/post/meterpreter/packet.rb`; the GUID
derivation is defined in `lib/msf/base/sessions/mettle_config.rb`; the only competing
structure in this corpus is `lib/msf/core/payload/uuid.rb`.
**CONDITIONAL SCOPE:** the GUID feature is conditional on `stageless == false` - see ?3. The
encryption features are conditional on the packet type not being `PACKET_TYPE_CONFIG`.
Where a rate holds only under one branch, the branch is named at the rate.
**COUNTED:** 234 unclassified `xor` lines remain after classification (from 971 raw); 5 packet
types; 3 encrypt flags; 122 GUID entropy bits; conjunction rate 1 in 7.87e19.
**STATUS:** [verified] by enumeration unless tagged otherwise at the claim.

---

## ?0 Correction to the commissioning brief

`[verified]` The brief proposed **four candidate primitives** - 32-byte outer header,
16-byte GUID in the clear, the `PACKET_TYPE_CONFIG`-is-always-unencrypted property, and the
XOR-key-prefixed shape - and asked for the minimum firing set. **The measurement refuses
three of the four as standalone primitives, and the refusal is the finding.**

| proposed primitive | verdict as a STANDALONE rule | measured reason |
| --- | --- | --- |
| 32-byte outer header | **not sufficient** | two fields are unconstrained integers; it is a size, not a signature |
| 16-byte GUID in the clear | **not sufficient** | the well-formed-shape rate is **1 in 64** (?3) |
| `PACKET_TYPE_CONFIG` always unencrypted | **not sufficient, and rare** | it is one of five types and occurs once per session |
| XOR-key-prefixed shape | **actively dangerous alone** | a near-identical 16-byte XOR structure exists in `payload/uuid.rb` (?2) |

`[verified]` **No single proposed primitive is a fingerprint. The conjunction is the
fingerprint.** ?4 computes the conjunction and ?5 states the rule.

---

## ?1 The observable, stated as bytes

`[verified]` From `packet.rb:996` (emit) and `:1017` (parse), the first 32 bytes of any
Meterpreter transport frame are:

| offset | size | field | constrained by |
| --- | --- | --- | --- |
| 0 | 4 | XOR key | 4 bytes, each 1..254 (`:981`) |
| 4 | 16 | session GUID | see ?3 |
| 20 | 4 | encrypt flags | `{0,1,2}` (`:839-841`) |
| 24 | 4 | length | big-endian, counts the inner TLV block |
| 28 | 4 | packet type | `{0,1,2,10,11}` (`:12-16`) |

`[verified]` **Input cardinality for every constrained set below: the definitions were
enumerated from source, not assumed.** `packet.rb` contains exactly 5 `PACKET_TYPE_*` value
definitions and exactly 3 `ENC_FLAG_*` definitions.

**Control pair on the enumeration instrument:**

```
  PACKET_TYPE_RESPONSE defined = True   (KNOWN TRUE)
  PACKET_TYPE_NOSUCH   defined = False  (KNOWN FALSE)
```

`[verified]` The XOR key bytes are constrained to **1..254** by `:981` `(rand(254) + 1)`.
**`[inferred]` A zero byte is impossible in that field**, so an all-zero 4-byte prefix is a
positive exclusion - inferred from the arithmetic at `:981`, not from observing traffic.

`[verified]` **The XOR is removed before any field is read.** `:930-932` takes the key from
the first 4 bytes, applies `xor_bytes` over the whole 32-byte header, and only then unpacks
`a4a16NNN`. **So the observable fields are post-XOR and require only the key that is
transmitted with them.** No credential is involved at any step.

---

## ?2 The false-positive surface: what else looks like this

`[verified]` **Input cardinality: 8,570 `.rb` files; 971 lines matching `xor` outside
comments.** Classification by area:

| category | lines | why it cannot be confused with the wire |
| --- | --- | --- |
| payload encoders (`modules/encoders/`) | 199 | XOR shellcode bytes **at rest**, before embedding; never a stream |
| inline assembler / byte strings | 548 | an instruction operand or a literal, not a key read from input |
| crypt/credential helpers | 32 | decrypt a stored blob; no length/type pair, no framing |
| **unclassified** | **234** | examined individually below |

**`[verified]` Instrument-fault disclosure.** The first classification run returned
**499 unclassified**, because the classifier regex was written inside a double-quoted
PowerShell string where `\\x` was read as an escape, and the regex **threw**
`Insufficient hexadecimal digits`. **No number from that run is used.** Re-run with the
pattern in a single-quoted string: **234 unclassified, a difference of 265 lines that the
broken pattern had mis-bucketed.** The corrected figure is used throughout.

`[verified]` **The one genuine competitor, and it is close.**
`lib/msf/core/payload/uuid.rb:132-138` emits exactly 16 bytes:

```
  optimal 0  : puid           8 bytes   SecureRandom / seed
  offset 8   : plat_xor       1 byte
  offset 9   : arch_xor       1 byte
  offset 10  : plat_xor ^ plat_id    1 byte
  offset 11  : arch_xor ^ arch_id    1 byte
  offset 12  : time_xor ^ tstamp     4 bytes
  TOTAL 16 bytes      pack('C4N') at :138, unpack('a8C4N') at :152
```

`[verified]` **This shares the XOR-key-prologue shape with the Meterpreter header and is the
single most plausible source of a false positive in this corpus.**

`[verified]` **The discriminator is structural, not statistical.** The payload UUID packs
`C4N` - no big-endian length word and no type word. **A rule that requires a length field at
offset 24 and a type field at offset 28 physically cannot fire on it.** The two structures
differ by 16 bytes of absent schema, not by a probability.

`[verified]` **`xor_decrypt` at `modules/post/windows/gather/credentials/thycotic_secretserver_dump.rb:642-648`
is a second repeating-key XOR in the corpus, and it is not a wire format** - it decrypts a
stored credential blob and emits no length/type pair.

---

## ?3 GUID entropy, and why it is NOT a fingerprint by itself

`[verified]` **The derivation is conditional on staging, and this is the decisive fact.**
`lib/msf/base/sessions/mettle_config.rb:157-161`:

```ruby
  157:         guid = "\\x00" * 16
  158:         unless opts[:stageless] == true
  159:           guid = [SecureRandom.uuid.gsub('-', '')].pack('H*')
  160:         end
  161:         opts[:session_guid] = Base64.encode64(guid).strip
```

`[verified]` **STAGED sessions: 16 random bytes from `SecureRandom.uuid`. STAGELESS
sessions: 16 ZERO bytes.** `client.rb:186` defaults to `"\\x00" * 16` and
`packet_dispatcher.rb:471-472` treats an all-zero GUID as unassigned and adopts the
packet value. **A stageless session therefore presents 16 zero bytes at offset 4, which is
not a fingerprint at all - it is the absence of one.**

`[verified]` **Entropy of the staged case: 122 bits, not 128.** `SecureRandom.uuid` is an
RFC 4122 version-4 UUID: the high nibble of byte 6 is fixed to `0100` (4 bits) and the top two
bits of byte 8 are fixed to `10` (2 bits). `128 - 6 = 122`.

### The rate a detector actually faces

`[inferred]` **A detector does not search for one known GUID; it tests whether the bytes at
offset 4 have GUID shape.** That is a different probability, computed below from the RFC 4122
fixed-bit structure - the arithmetic is exact; the framing of it as a detection rate is an
inference from that structure.

| feature | condition | P(random bytes satisfy) |
| --- | --- | --- |
| F1 GUID shape | byte 6 high nibble `4`, byte 8 top bits `10` | `1/16 * 1/4` = **1/64** |

`[inferred]` **1 in 64. A GUID-shape test alone is not a usable fingerprint.** The 122-bit
figure is a true statement about the entropy of a *specific* GUID and a misleading one about
the selectivity of a *shape* test. **The two numbers differ by 116 bits and the larger is
irrelevant to a detector.**

`[inferred]` The GUID earns its place in the conjunction as a **grouping key, not a
matcher**: once a frame candidate passes the other features, the GUID partitions frames into
sessions. **That is a post-detection use and it should not be sold as a detection feature.**

---

## ?4 The conjunction, with a computed rate

`[inferred]` **Each feature is scored as the probability that a uniformly random byte run
satisfies it.** This is the honest null hypothesis for a passive sensor with no model of the
traffic it is watching. **It is a rate against random bytes, NOT against real internet
traffic** - see ?6 for why that distinction is load-bearing.

| # | feature | P(random run satisfies) |
| --- | --- | --- |
| F1 | GUID shape at offset 4 | 1/64 = 1.563e-2 |
| F2 | flags at offset 20 in `{0,1,2}` | 3/2^32 = 6.99e-10 |
| F3 | length at offset 24 consistent with bytes actually present | see ?5 |
| F4 | type at offset 28 in `{0,1,2,10,11}` | 5/2^32 = 1.16e-9 |

`[inferred]` **F1 AND F2 AND F4 = 1.27e-20, i.e. 1 in 7.87e19 random 32-byte windows.**

`[inferred]` Context for that figure: a 1 Gbit/s sensor sees roughly 3.1e7 packets per
second at 1500 bytes. At the computed rate a false hit is expected after approximately
**2.5e12 seconds** - about 80,000 years - **of uniformly random payload.**

`[inferred]` **F3 is deliberately excluded from the product.** A length field is only
meaningful when checked against the number of bytes actually available in the reassembly
buffer, which is a property of the capture and not of the bytes. Including it would inflate
the rate with a factor that is not a probability.

**`[verified]` The arithmetic is stated so it can be checked:** 3/2^32 * 5/2^32 / 64 =
15 / (64 * 2^64) = 1.2705e-20.

---

## ?5 The reassembly rule, and the observable that detects mis-framing

`[verified]` `packet.rb:932-933`:

```ruby
  932:       _, _, _, length, _ = decoded_bytes.unpack('a4a16NNN')
  933:       length + PACKET_HEADER_SIZE - HEADER_SIZE - self.raw.length
```

`[verified]` **`length` counts the inner TLV block. The frame is `length + 32 - 8` bytes of
wire, i.e. `length + 24` beyond what the length field alone suggests.**

**`[inferred]` The rule a parser must implement, stated as the source implements it:**

```
  1. Buffer until >= 32 bytes are available.
  2. key   = bytes[0..3]
 3. hdr   = xor_bytes(key, bytes[0..31])
  4. length = BE32(hdr[24..27])
  5. wait until buffered >= length + 32 - 8 = length + 24 bytes
  6. frame = consume(length + 24)
```

`[inferred]` **The wrong rule, which is the natural one to write, is to treat `length` as the
total frame size.** Step 5 would then wait for `length` bytes instead of `length + 24`,
**consuming 24 bytes too few on every frame.**

### The observable that separates a correct parse from a mis-framed one

`[inferred]` **A mis-framed parse does not fail - it silently produces a stream of plausible
garbage, which is why it belongs in the DB caveats rather than the DB features.** The
discriminating observable is **the second frame's header**:

- `[inferred]` Under the **correct** rule, offset 0 of every subsequent window is a fresh XOR
  key and offset 28 is a type in `{0,1,2,10,11}`. **The type check keeps passing.**
- `[inferred]` Under the **wrong** rule the parser is 24 bytes short of the real boundary, so
  the bytes it reads as offset 28 are **not the type field**, and the type check fails within
  one or two frames on any real session.

**`[inferred]` Practical form of the rule: a parser that frames correctly sees the type field
stay inside its 5-value set across an entire session. A parser mis-framed by 24 bytes cannot.
That persistence test - not a single-frame parse - is the observable.**

`[verified]` **A second, sharper trap composes with the first.** `:986` exempts
`PACKET_TYPE_CONFIG` from encryption unconditionally, but **the inner TLV header is never
encrypted even under AES256** - `:988` passes only `tlv_data[HEADER_SIZE..-1]` to
`aes_encrypt`. **So a detector can read the inner TLV length and type on every frame,
encrypted or not, and never needs to distinguish the flags value to frame the stream.**

---

## ?6 What the corpus cannot establish

**`[blocked]` - the false-positive rate in ?4 is against RANDOM bytes. The rate against REAL
traffic is not established, and the missing ingredient is named: this corpus contains no
captured Meterpreter or comparable encrypted-tunnel traffic, and no capture of any other
target lane's wire format, so the competing-traffic rate cannot be measured.**

`[inferred]` Real traffic is not random. It is biased toward low bytes, toward structure, and
toward repetition, so **the true collision rate is higher than 1 in 7.87e19 and the
direction of the error is known while its magnitude is not.** A fingerprint DB entry that
quotes only the random-byte figure is quoting a bound, not a rate.

`[verified]` **A second limitation, from the stageless branch of ?3:** on a stageless session
the GUID is 16 zero bytes, so **F1 contributes no selectivity at all** and the conjunction
reduces to F2 AND F4 = 15/2^64. **The rule degrades to a weaker one on exactly the sessions
that send the fewest packets.**

`[verified]` **Third: this rule covers the transport framing only.** It says nothing about
TLV-layer content, and D134 ?5 establishes that a type mismatch at that layer is silently
invisible. **Framing successfully a session whose contents are mis-typed yields a confident
empty result - the same failure shape as a probe that returns a plausible zero.**

---

## ?7 The DB entry, in the form a rule takes

```
name        : meterpreter-transport-frame
fires_on    : 32-byte window, post-XOR, satisfying ALL of:
                flags[20..23] in {0,1,2}
                type[28..31]  in {0,1,2,10,11}
                length[24..27] + 24 == bytes consumed to next boundary
                GUID shape at [4..19] (v4)  -- OPTIONAL, 1/64 alone, omit to
                                               widen stageless coverage
false_pos_random : 1 in 7.87e19 windows (F1 AND F2 AND F4)
false_pos_real   : NOT ESTABLISHED - no competing-traffic capture in corpus
caveat_1    : length counts the inner TLV block, NOT the frame. Off-by-24.
caveat_2    : stageless sessions carry 16 ZERO GUID bytes - F1 is inert there.
caveat_3    : successful framing does NOT imply readable contents; TLV type
              mismatch is silently invisible (D134 section 5).
caveat_4    : the XOR key is transmitted in the clear by design; this is
              obfuscation, not encryption, and confers no confidentiality.
```

`[inferred]` **Caveat 4 is the one a defensive reader is most likely to
misread.** The first four bytes are a key, which invites the conclusion that the traffic is
encrypted. **It is not: the key travels with the data and is self-inverting.**

---

## ?8 Cross-reference

`[verified]` **This rule and the D91 pair are complementary halves and must not be merged.**
`sliver-diver` established the binary-side presence of the ownership filter
(`normalizedConversationOperatorName` at `0xD0B140`, `GetIncludeMessages` at `0x695D80`,
`aiOperatorName` = 0 server-side). **This report states what an observer can conclude from
the wire alone, and the named conditions under which that conclusion fails.** The first is a
claim about a binary; the second is a claim about a byte stream. **Where this report needs a
binary-side fact it cites D91 and does not re-derive it.**

`[verified]` `D134` is the protocol description this rule is built from; **the 355-accessor
silent-miss result there is the source of caveat 3 here.** `D130` supplies the constraint that
every zero needs its operand proven non-empty - **applied in ?2, where the 234 unclassified
lines are a corrected count whose failed predecessor is disclosed.**

`[verified]` `D123` is not re-opened. Its open item on the 2560 constant was closed by D134.

---

## ?9 Instrument-fault record, continued

`[verified]` **A sixth member of the species, filed because it is the same defect class.**
A classifier regex was constructed inside a double-quoted PowerShell string; `\\x` was read as
an escape; the regex **threw** `Insufficient hexadecimal digits`. **The throw was visible, but
the counts had already been accumulated under the broken pattern and were plausible** - 499
unclassified, a number that looks like a finding. **The corrected value is 234.**

**`[verified]` The control that caught it was printing the number beside the claim that the
pattern had failed.** Without that comparison the 499 would have been filed.

`[verified]` **A second incident, in the allocation protocol, and it validates the tooling:**
`check 142` returned **FREE (exit 1)** and moments later the exclusive create of `D142.lock`
**failed because the file existed** - another lane had claimed it in the interval. **A
registry-only probe would have produced a collision with a report already on disk. The
exclusive create is the only non-stale test, and that is why the rule is attempt-then-claim
rather than read-then-claim.**

`[verified]` **Allocation also produced a live instance of the lock/registry divergence D134
described:** `check 144` reports `registry=False disk=False lock=True` with `VERDICT: HELD`
and flags the three sources as disagreeing. **The tool now carries the finding rather than
assuming registry truth.**

---

## ?10 What this report does NOT do

- **`[verified]` No execution.** No Ruby toolchain on this host; every Ruby/Rex claim is
  `[inferred]` at the claim. `bare?` remains blocked-by-toolchain and is cross-referenced to
  D127 section B-2.
- **`[verified]` No network, no live C2, no handler authorised, simulated or contacted.**
- **`[verified]` No REA, no `open_binary`.**
- **`[verified]` The false-positive rate is computed, not measured against traffic.** ?6 names
  the missing capture explicitly rather than substituting a plausibility argument.
- **`[verified]` D121, D129 and D134 are not edited.** Each is cited by reference.

*End of D144.*