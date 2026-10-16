# D134 - Meterpreter TLV framing and type vocabulary as a detection surface

**SCOPE:** the Meterpreter TLV protocol layer as an observable wire surface - outer packet
framing, the TLV type vocabulary, and the accessor semantics that constrain what a parser can
conclude. Source: `lib/rex/post/meterpreter/` and the Metasploit tree. Read-only bytes.
**DEFINER SCOPE:** every framing claim is defined in `lib/rex/post/meterpreter/packet.rb`.
**CONDITIONAL SCOPE:** the framing constants are unconditional; the ENCRYPTED_FLAGS branch is
conditional on a non-zero flag, and the AES branch additionally on a supplied key. Where a
claim holds only under one branch, the branch is named at the claim.
**COUNTED:** 355 accessor call sites over 8,570 `.rb` files; 32-byte outer header; 8-byte inner
TLV header; 8 cited TLV constants ABSENT from the entire tree.
**STATUS:** [verified] by enumeration unless tagged otherwise at the claim.

---

## ?1 The detection primitive: outer framing

`[verified]` **The wire form is a 32-byte XOR-obfuscated header followed by an 8-byte TLV
header and payload.** The layout is stated in the source comment at `packet.rb:805-827` and
the constants at `:831-835` match it exactly:

```
  805:   # The Packet container itself has a custom header that is slightly different than the
  808:   # XOR KEY        - 4 bytes
  809:   # Session GUID   - 16 bytes
  810:   # Encrypt flags  - 4 bytes
  811:   # Packet length  - 4 bytes
  812:   # Packet type    - 4 bytes
  813:   # Packet data    - X bytes

  831:   XOR_KEY_SIZE = 4
  832:   ENCRYPTED_FLAGS_SIZE = 4
  833:   PACKET_LENGTH_SIZE = 4
  834:   PACKET_TYPE_SIZE = 4
  835:   PACKET_HEADER_SIZE = XOR_KEY_SIZE + GUID_SIZE + ENCRYPTED_FLAGS_SIZE + PACKET_LENGTH_SIZE + PACKET_TYPE_SIZE
```

`[verified]` `GUID_SIZE = 16` at `:165`. **Therefore `PACKET_HEADER_SIZE = 4 + 16 + 4 + 4 + 4 = 32` bytes.**
`[verified]` `HEADER_SIZE = 8` at `:319` and it is a DIFFERENT quantity: the inner TLV header
(4-byte length + 4-byte type), used at `:503`:

```ruby
  503:     [raw.length + HEADER_SIZE, self.type].pack("NN") + raw
```

**Two sizes, two layers, easy to conflate.** 32 is the outer packet header; 8 is the inner
TLV header. A detector must key on the 32-byte one.

### The obfuscation is a fixed repeating XOR, and the key is self-describing

`[verified]` `:981` generates a random 4-byte key with each byte in 1..254:

```ruby
  981:     xor_key = (rand(254) + 1).chr + (rand(254) + 1).chr + (rand(254) + 1).chr + (rand(254) + 1).chr
  996:     xor_key + xor_bytes(xor_key, raw)
```

`[verified]` `xor_bytes` at `:1037-1044` repeats the key cyclically:

```ruby
 1041:     bytes.each_byte do |b|
 1042:       result << (b ^ xor_key[i % xor_key.length]).chr
```

**`[verified]` This is the single most important detection property in this report: the key
is transmitted in the first 4 bytes of the packet, in the clear.** The obfuscation is
self-inverting with no secret. `[inferred]` A passive observer who can read the byte stream can
recover the entire header without any credential - **inferred from the arithmetic above, not
from running the code.**

**`[verified]` Consequence for detection: the outer framing is parseable by a passive device,
and the 16-byte session GUID is recoverable in plaintext from every packet.** That GUID is a
**stable per-session identifier** and is the highest-value passive fingerprint in this layer,
because it groups packets into a session without decrypting any payload.

### The streaming reassembly rule

`[verified]` `:925-939` is the primitive a TCP-reassembling detector must reproduce:

```ruby
  927:     if self.raw.length >= PACKET_HEADER_SIZE
  930:       xor_key = self.raw.unpack('a4')[0]
  931:       decoded_bytes = xor_bytes(xor_key, raw[0, PACKET_HEADER_SIZE])
  932:       _, _, _, length, _ = decoded_bytes.unpack('a4a16NNN')
  933:       length + PACKET_HEADER_SIZE - HEADER_SIZE - self.raw.length
  937:       PACKET_HEADER_SIZE - self.raw.length
```

`[verified]` **The unpack template `a4a16NNN` at `:932` is the framing schema written out:**
4 bytes ASCII (key), 16 bytes ASCII (GUID), then three big-endian `N` fields = encrypt flags,
length, type. **A detector needs exactly this 32-byte read and one XOR pass to obtain the
length field, and can then frame the stream without any further knowledge.**

`[verified]` The byte-count arithmetic at `:933` subtracts `HEADER_SIZE` because the length
field counts the inner TLV block, not the outer header. **A detector that assumes `length`
means total packet size will mis-frame every packet by 8 bytes.** That is the sharpest
implementation trap in this layer and it is named here.

---

## ?2 The encryption branch, and what it does NOT hide

`[verified]` `:839-841`: `ENC_FLAG_NONE = 0x0`, `ENC_FLAG_AES256 = 0x1`, `ENC_FLAG_AES128 = 0x2`.

`[verified]` `:986-993`, the conditional branch:

```ruby
  986:     if @type != PACKET_TYPE_CONFIG && key && key[:key] && (key[:type] == ENC_FLAG_AES128 || key[:type] == ENC_FLAG_AES256)
  988:       iv, ciphertext = aes_encrypt(key[:key], tlv_data[HEADER_SIZE..-1])
  990:       raw << [key[:type], iv.length + ciphertext.length + HEADER_SIZE, self.type, iv, ciphertext].pack('NNNA*A*')
  991:     else
  992:       raw << [ENC_FLAG_NONE, tlv_data].pack('NA*')
```

`[verified]` **The header is NOT encrypted in either branch.** The key, GUID, flags, length
and type are assembled before encryption; only `tlv_data[HEADER_SIZE..-1]` - everything after
the inner 8-byte header - is passed to `aes_encrypt` at `:988`. **The inner TLV length and
type remain readable even under AES256.** `[inferred]` That follows from the slice bounds, not
from executing the cipher.

`[verified]` **Two conditions exclude encryption:** `@type != PACKET_TYPE_CONFIG`, and a
supplied key of matching flag type. **A CONFIG packet is never encrypted.** `[inferred]` That is
the session-negotiation packet and is therefore observable, which is consistent with its
purpose - it carries the parameters the session needs before a key exists.

**Detection consequence, `[inferred]` at the claim:** a detector does not need to break AES to
fingerprint a Meterpreter session. **The 32-byte header, the flags field, the packet type and
the session GUID are all in the clear under every branch**, and an all-zero flags field plus a
parseable TLV block is itself a strong signature because it means an unencrypted session.

---

## ?3 The TLV type vocabulary as a fingerprint

`[verified]` **The absolute sentinel that makes the vocabulary a fingerprint is `TLV_TYPE_ANY`:
`packet.rb:54 TLV_TYPE_ANY = TLV_META_TYPE_NONE | 0`, i.e. `0`.**

`[verified]` The base offset structure, from `packet.rb`: `TLV_RESERVED = 0`,
`TLV_EXTENSIONS = 20000`, `TLV_USER = 40000`, `TLV_TEMP = 60000`. **Extension families are
declared as `TLV_META_TYPE_<M> | (TLV_EXTENSIONS + N)`, so the offset itself names the family.**

`[verified]` The meta-type bits, `:21-29`:

| meta type | value |
| --- | --- |
| `TLV_META_TYPE_NONE` | 0 |
| `TLV_META_TYPE_STRING` | 1 << 16 |
| `TLV_META_TYPE_UINT` | 1 << 17 |
| `TLV_META_TYPE_RAW` | 1 << 18 |
| `TLV_META_TYPE_BOOL` | 1 << 19 |
| `TLV_META_TYPE_QWORD` | 1 << 20 |
| `TLV_META_TYPE_COMPRESSED` | 1 << 29 |
| `TLV_META_TYPE_GROUP` | 1 << 30 |
| `TLV_META_TYPE_COMPLEX` | 1 << 31 |

`[verified]` **`TLV_META_MASK` at `:31-41` is the bitwise OR of all of the above EXCEPT
`COMPRESSED`** - the comment at `:31-32` says compressed is excluded because other meta types
can also be compressed. **`[absence]` The mask is not itself a fingerprint; it is a display
helper.** It is referenced exactly twice corpus-wide: at its definition `:33` and at `:366`
inside `def inspect`. **No functional code consults it.**

`[inferred]` **Therefore a detection signature keyed on the type word should use the meta bits
directly, not `TLV_META_MASK`.** A detector that masks with a value the protocol does not use
for matching is a detector measuring its own convention.

---

## ?4 DEFINED versus MENTIONED - the constant audit a fingerprint DB needs

**`[verified]` A definedness question cannot be answered by substring search.** The precedent
is the earlier finding that a `SHELLCODE` token appeared 7 times and all seven were the literal
word inside `echo` strings. **A constant that is merely NAMED is not a constant that EXISTS.**

`[verified]` Instrument: DEFINED = matches `^\s*NAME\s*=[^>]`; a bare token that does not match
is MENTION-ONLY. **The `=[^>]` form is required because `=` is a prefix of `=>`, so a naive
`=` pattern also matches hash keys - a defect this corpus has hit before.**

**Control pair, printed BEFORE the result:**

```
  TLV_TYPE_ANY  defined (KNOWN TRUE)  = 1
  TLV_TYPE_NOSUCHTHING (KNOWN FALSE)  = 0
```

**The instrument discriminates.** Result over the constants this capstone cites, searching
`lib/rex/post/meterpreter/`, input cardinality = all `.rb` files in that tree:

| constant | occurrences | defs | verdict | first definition |
| --- | --- | --- | --- | --- |
| `TLV_TYPE_ANY` | 7 | 1 | DEFINED | `packet.rb:54` |
| `TLV_TYPE_STRING` | 4 | 1 | DEFINED | `packet.rb:61` |
| `TLV_TYPE_UINT` | 7 | 1 | DEFINED | `packet.rb:62` |
| `TLV_TYPE_BOOL` | 8 | 1 | DEFINED | `packet.rb:63` |
| `TLV_TYPE_REQUEST_ID` | 6 | 1 | DEFINED | `packet.rb:56` |
| `TLV_TYPE_EXCEPTION` | 1 | 1 | DEFINED | `packet.rb:57` |
| `TLV_TYPE_RESULT` | 6 | 1 | DEFINED | `packet.rb:58` |
| `TLV_TYPE_UUID` | 5 | 1 | DEFINED | `packet.rb:96` |
| `TLV_TYPE_SESSION_GUID` | 5 | 1 | DEFINED | `packet.rb:97` |
| `TLV_TYPE_C2_PROXY_USER` | 3 | 1 | DEFINED | `packet.rb:125` |
| `TLV_TYPE_C2_PROXY_PASS` | 3 | 1 | DEFINED | `packet.rb:126` |
| `TLV_TYPE_CHANNEL_ID` | 18 | 1 | DEFINED | `packet.rb:69` |
| `TLV_TYPE_CHANNEL_DATA` | 4 | 1 | DEFINED | `packet.rb:71` |
| `TLV_TYPE_CHANNEL_CLASS` | 2 | 1 | DEFINED | `packet.rb:73` |
| `TLV_TYPE_STAT_BUF` | 7 | 1 | DEFINED | `stdapi/tlv.rb:44` |
| `TLV_TYPE_STAT_BUF32` | 4 | 1 | DEFINED | `stdapi/tlv.rb:43` |
| **`TLV_TYPE_ALL`** | **1** | **0** | **NOT DEFINED** | - |
| **`TLV_TYPE_RAW`** | **0** | **0** | **ABSENT** | - |
| **`TLV_TYPE_GROUP`** | **0** | **0** | **ABSENT** | - |
| **`TLV_TYPE_COMPLEX`** | **0** | **0** | **ABSENT** | - |
| **`TLV_TYPE_METHOD`** | **0** | **0** | **ABSENT** | - |
| **`TLV_TYPE_TRANS_URL`** | **0** | **0** | **ABSENT** | - |
| **`TLV_TYPE_TRANS_TYPE`** | **0** | **0** | **ABSENT** | - |
| **`TLV_TYPE_TRANS_TIMEOUT`** | **0** | **0** | **ABSENT** | - |
| **`TLV_TYPE_CHANNEL_URL`** | **0** | **0** | **ABSENT** | - |

`[verified]` **Input cardinality: 25 constants cited, 16 DEFINED, 1 MENTION-ONLY, 8 ABSENT.**
**Closure: 16 + 1 + 8 = 25.**

### The eight ABSENT constants are confirmed absent, not unread

`[verified]` A zero from a broken reader is worthless, so the reader was proved able to find
known-present tokens in the same pass, over the same 8,570 files:

```
  KNOWN-PRESENT TLV_TYPE_CHANNEL_ID  files=   11
  KNOWN-PRESENT TLV_META_TYPE_RAW    files=   12
  KNOWN-PRESENT packet.rb            files=    2
  KNOWN-PRESENT require              files= 2784
  KNOWN-PRESENT TLV_TYPE_ANY         files=    3
```

`[verified]` **`TLV_TYPE_ANY` returns 3 files - the same family the eight zeros belong to - so
the reader has a working name table and the zeros are real absences.**

`[verified]` **Bound on the negative, stated:** the reader skipped 7 files larger than 4 MB.
**All 7 are non-`.rb`** - five John-the-Ripper character sets (`data/jtr/*.chr`),
`db/modules_metadata_base.json`, and a font blob under `external/`. **Their first 4 MB was
searched for all eight absent names and returned no hit.** **Zero `.rb` files were skipped.**

`[verified]` **The absent names are the META-TYPE names under the wrong prefix.** `TLV_TYPE_RAW`
does not exist, but `TLV_META_TYPE_RAW` exists in 12 files, `TLV_META_TYPE_GROUP` in 6,
`TLV_META_TYPE_COMPLEX` in 2. **A fingerprint DB that lists `TLV_TYPE_RAW` as a meterpreter
type word would be listing a name the protocol never emits.**

---

## ?5 The silent-miss limitation, quantified

**This is a detection LIMITATION, not a detection signal, and a detector that assumes TLV
replies are complete will under-read.**

`[verified]` `get_tlvs` at `:632-646` returns `[]` when nothing matches; it does not raise.
**And the comparison is EXACT.** `:639` calls `type?`, which is `:448-450 self.type == type`,
NOT the masked `meta_type?` at `:441-443`. **Corrected by reference to D121 T6, whose headline
count of 1 functional mask-dependent test is corrected to 0 by D129.** The masked method has
**zero production callers** corpus-wide.

`[verified]` **The whole accessor family funnels through `:632`:**

| accessor | line | delegates to |
| --- | --- | --- |
| `get_tlvs` | 632 | - (the primitive) |
| `get_tlv` | 693 | `get_tlvs(type)` at `:694` |
| `get_tlv_value` | 707 | `get_tlv` at `:708` |
| `get_tlv_values` | 716 | `get_tlvs(type)` at `:717` |
| `has_tlv?` | 723 | `get_tlv` at `:724` |

`[verified]` **Input cardinality: 8,570 `.rb` files scanned. 355 accessor call sites total.**

| accessor | call sites |
| --- | --- |
| `.get_tlv` | 58 |
| `.get_tlv_value` | 263 |
| `.get_tlv_values` | 7 |
| `.get_tlvs` | 20 |
| `.has_tlv?` | 7 |
| **TOTAL** | **355** |

`[verified]` **The count is stable under collation of its comparator.** A first pass using a
`\b`-anchored `get_tlv` pattern risked counting `get_tlv_value` and `get_tlv_values` twice;
re-run with explicit `elseif` precedence the total is **355 both ways, difference 0.** **A
count that changes with the collation of its comparator is a count of the comparator - this one
does not change, so it is a count of the call sites.**

**`[inferred]` The detection consequence, at the claim:** all 355 sites inherit one exact
comparison. **A producer that emits a TLV with a type word differing by a single meta bit - or
by the COMPRESSED overlay bit at 1<<29 - is silently invisible to every reader, with no error,
no log line, and no distinguishable empty result.** The reader cannot tell "the agent did not
send this" from "the agent sent this under a type I did not predict". **For a detector this is a
bounded claim of incompleteness, not a signature.**

---

## ?6 What the corpus cannot establish

### ?6.1 `TLV_TYPE_ALL` - MENTION-ONLY, reachability unknown

`[verified]` `extapi/adsi/adsi.rb:147 values = v.get_tlvs(TLV_TYPE_ALL)`. **`TLV_TYPE_ALL` is
declared nowhere** - a token search across every file of every type returned exactly 1 file,
the call site itself. A sibling 53 lines above at `:94` correctly uses `TLV_TYPE_ANY`. **The
file is live** (required at `extapi/extapi.rb:8`, instantiated `:43`, reachable from
`lib/msf/core/post/windows/ldap.rb:139` and `modules/post/windows/gather/credentials/gpp.rb:230`).

**`[blocked]` - and the missing ingredient is named: the reachability of the DN arm is UNKNOWN
because the agent-side C source that would emit a DN-typed group does not exist in this
corpus.** `[inferred]` Ruby reading an undeclared constant raises `NameError`, so the branch
cannot return a value if reached - **but whether it is reached is not established, and that is
the whole claim.** **No Ruby was run; every Ruby claim here is inferred at the claim.**

### ?6.2 The 2560 question - settled, and it must not be misattributed

`[verified]` `Command.h:29 #define DEMON_COMMAND_MEM_FILE 2560` is **agent-side.** In this
corpus, `DEMON_COMMAND_MEM_FILE` occurs in **0 files**.

`[verified]` The integer `2560` occurs **exactly 5 times** tree-wide, and **not one is a
command ID:**

| site | what it is |
| --- | --- |
| `data/wordlists/vxworks_collide_20.txt:3862` | a wordlist entry |
| `documentation/.../udp_amplification.md:66` | a progress line, "2560 of 4608 hosts" |
| `documentation/.../hikvision_cve_2021_36260_blind.md:253` | a stager progress line, "2560/6557 bytes" |
| `modules/exploits/unix/webapp/vicidial_agent_authenticated_rce.rb:447` | a browser width |
| `modules/exploits/unix/webapp/vicidial_agent_authenticated_rce.rb:472` | a browser width |

**`[verified]` The capstone must not attribute 2560 to a Meterpreter command ID, and a
`\b2560\b` search would have invited exactly that error.** The value is agent-side and this
corpus carries no trace of it.

---

## ?7 Instrument-fault record - three tools that returned a confident wrong answer

`[verified]` Filed because all three are the same species: **a tool that fails by returning a
plausible answer instead of refusing.**

| # | fault | how it presented | why it was caught |
| --- | --- | --- | --- |
| 1 | `registry.json` rewritten by PowerShell `Set-Content -Encoding UTF8` (PS 5.1 emits a BOM) while `_lead_alloc.py:26` read `encoding='utf-8'` | `status` and `claim` died with `JSONDecodeError: Unexpected UTF-8 BOM` for EVERY lane | `claim` crashed rather than refusing |
| 2 | the same crash left `D132.lock` created at `:69` but the registry never saved at `:77` | **a LOCK-HELD, UNREGISTERED number** | a lane reading `registry.json` alone would have called D132 free and collided |
| 3 | `repair` computed "next free" over registry+locks only | printed `next free: D27` - **a number with a report already on it** | D1-D122 predate the registry and are on disk |

**`[verified]` The structural lesson, and it is counterintuitive: the LOCK is authoritative and
the REGISTRY is the derived view.** The registry looks like "the data" and the lock like an
implementation detail; **the reverse is true**, because a lock is created before the record
that describes it. **A reader that trusts the more legible source gets the wrong answer during
exactly the window where it matters.**

**`[verified]` The right response to a shared-resource fault is to diagnose and decline, not to
repair.** This fault was observed independently by three lanes; all three reported and none
patched, so it was **fixed once, by its owner, at the source** - `load()` to `utf-8-sig`,
`save()` with explicit `newline='\n'`, and a `repair` operation reconciling registry, locks and
disk. **A silent local repair would have left the tool broken for every other lane.**

`[verified]` **And the repair is itself the fourth instance of the same species, caught by the
same rule:** `repair` printed a confident `next free` computed over the wrong scope. **A tool
that answers a free-number question without consulting the disk will hand out a number that is
already taken.**

---

## ?8 Cross-reference

`[verified]` **This report and the D91 pair close on the same question from opposite ends.**
`sliver-diver` established that the ownership filter **is** present in the compiled sliver client
(`normalizedConversationOperatorName` at `0xD0B140`, `GetIncludeMessages` at `0x695D80`,
`aiOperatorName` = 0 server-side, `client/command/ai` = 242 rows matching the D103 source count).
**That is a binary-side YES.** **This report is the protocol-side statement of the same
property:** what an observer can conclude from the wire alone, and the named conditions under
which that conclusion fails. **They cross-reference and do not duplicate.**

`[verified]` `D130` supplies a constraint this report obeys: **name coverage is two-tier and
binary-specific**, demonstrated by `named=1` on the merlin Windows agents and the sliver client
where `main.`, `runtime.`, `fmt.`, `Split` and `strings.` all return zero and a Go binary cannot
lack `runtime.` **`named=1` is a non-loaded name table, NOT an absence.** **Every zero in this
report was therefore instrument-controlled before it was filed** - see ?4, where the reader
returned 3 files for `TLV_TYPE_ANY` in the same pass as the eight zeros.

---

## ?9 What this report does NOT do

- **`[verified]` No execution.** No Ruby toolchain; every Ruby/Rex claim is `[inferred]` at the
  claim. `bare?` stays blocked-by-toolchain and is cross-referenced to D127 ?B-2, which
  re-derived that absence with a positive control in the same pass.
- **`[verified]` No network, no live C2, no handler authorised, simulated or contacted.**
- **`[verified]` No REA, no `open_binary`.**
- **`[verified]` No agent-side C source was available**, which is why ?6.1 stops at `[blocked]`.
- **`[verified]` D121 is not edited.** It stands at 55,972 B as published; the T6 correction is
  carried here and in D129 by reference.

*End of D134.*