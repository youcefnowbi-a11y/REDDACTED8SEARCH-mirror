# D102 — Meterpreter TLV wire constants, the handler↔payload contract, and the closure of D90's two carried censuses

**Lane:** Metasploit binary/payload mechanism (round 24).
**Owner:** `msf-diver`. **Round 24.**
**Write scope:** this file + `_d102_*`. Nothing else touched.
**Predecessors read this round:** `D85` (escaping census), `D90` (key surface), `D77` (bare/HTTP mirror).
**Tags:** `[verified]` = read from bytes this session with the count printed · `[read]` = read but not censused · `[inferred]` = reasoning over the corpus, no execution · `[absence]` = a negative with its bound stated.
**Line convention.** A "line" is an LF-delimited record. `file.rb:NNN` is the **1-based ordinal of the physical line**, counting blanks and comments. Multi-line constructs are reported at the line bearing the token under discussion. "LF count" = count of `0x0A` bytes. **Stated once, applies throughout.**

**BLOCKED, NOT ATTEMPTED (Lead's standing order).** D77's U1 (`Rex::Socket::Parameters.from_hash(...).bare?`) requires a Ruby toolchain. **There is none on this host.** `ruby` / `gem` / `bundle` are all absent. **Nothing in this report was executed.** Every Rex/MSF runtime claim is `[inferred]`. **No installation was attempted.**

---

## Table of Contents

- §0 Occupancy, and the three things inherited from D85/D90 without re-derivation
- §1 T1 — the Meterpreter TLV wire format: constants and opcodes
- §2 T2 — the handler↔payload contract, and where it is (not) validated
- §3 T3 — D90 U1 CLOSED: the `SSLClientCert`/`SSLClientKey` pair is LIVE, not latent
- §4 T4 — the `from_hash` consumers and the unknown-key dependency
- §5 Instrument record
- §6 Residual unknowns, each with a probe
- §7 Status

---

## §0 Occupancy, and what is inherited rather than re-derived

### §0.1 Occupancy by enumeration

```powershell
Get-ChildItem $DEEP -File | Where-Object { $_.Name -match '^D10[0-9]|^D9[5-9]' }
```
**`[verified]` Returns NOTHING. `D102` is unoccupied.**
**`[verified]` Control in the same invocation:** `^D9` returns **6** files (`D9_msf_core_library.md`, `D90`, `D91`, `D92`, `D93`, `D94`). **The filter bites — the zero is a real absence, not a broken probe.**

### §0.2 Inherited without re-derivation (Lead's instruction)

- **From D85:** *"49 of 49 operator-data interpolations reach a shell unescaped; 0 escape; 57 total with the 8 target-derived sites."* **I did not re-derive this and did not re-derive "2/129" or "15/182" — D85 records that the 16-of-18 preceding-line binding made the same-line figure wrong.** **`[read]` Taken as D85's corrected result. The 15 hand-audited escapes are `shellescape`/`shelljoin` and are an **OSX-module convention**, not a framework convention.**
- **From D90:** the 30-key accept surface, the 1 type-A / 6 type-B divergence, and **the confusable-key class of 3** (`'Context'`/`'SSLContext'`, `'SSLClientCert'`/`'SSLClientKey'`, `'Bool'`/`'Bare'`).
- **From D77:** `bare?` is a dead gate (never set in-corpus **and** the getter reads `@comm`).

### §0.3 The one thing this round adds to the frame

**D90 §0's meta-point is now load-bearing for a fourth time, and T4 sharpens it.** D90 wrote: *"A pattern filters text; a census enumerates call sites — and the difference only surfaces when a second count disagrees."* **§5.1 of this report is a case where a second count disagreed twice in a row and BOTH numbers were wrong.** The rule survives; the corollary is new: **a wrong census can be wrong in a direction that looks like a finding.** Recorded in §5.1.

---

## §1 T1 — the Meterpreter TLV wire format

### §1.1 The tree, censused

**`[verified]` `lib\rex\post\meterpreter\` = 203 files.** Sixteen of the 23 extension subdirectories carry a `command_ids.rb` + `tlv.rb` pair:

| extension | command_ids | tlv | | extension | command_ids | tlv |
|---|---|---|---|---|---|---|
| android | 1217 | 5850 | | powershell | 528 | 558 |
| appapi | 514 | 675 | | priv | 719 | 1098 |
| bofloader | 391 | 550 | | python | 354 | 790 |
| espia | 310 | 397 | | sniffer | 704 | 1276 |
| extapi | 1374 | 8464 | | **stdapi** | **10067** | **12139** |
| incognito | 680 | 911 | | unhook | 296 | 206 |
| kiwi | 293 | 280 | | winpmem | 305 | 284 |
| lanattacks | 877 | 454 | | | | |
| peinjector | 326 | 556 | | | | |

**`[verified]` SEVEN `stdapi_*` subdirectories carry NEITHER file:** `stdapi_audio`, `stdapi_fs`, `stdapi_net`, `stdapi_railgun`, `stdapi_sys`, `stdapi_ui`, `stdapi_webcam`. **`[inferred]` Their IDs are declared in the parent `stdapi/` pair — a split that is the reason `stdapi`'s files are 3–5× the size of any other extension's.**

### §1.2 The packet-type constants — actual values, not prose

**`[verified]` `packet.rb:21-29` — the type lattice. Nine meta-types; values are literal:**

| constant | expression | value |
|---|---|---|
| `TLV_META_TYPE_NONE` | `0` | **0** |
| `TLV_META_TYPE_STRING` | `(1 << 16)` | **65536** |
| `TLV_META_TYPE_UINT` | `(1 << 17)` | **131072** |
| `TLV_META_TYPE_RAW` | `(1 << 18)` | **262144** |
| `TLV_META_TYPE_BOOL` | `(1 << 19)` | **524288** |
| `TLV_META_TYPE_QWORD` | `(1 << 20)` | **1048576** |
| `TLV_META_TYPE_COMPRESSED` | `(1 << 29)` | **536870912** |
| `TLV_META_TYPE_GROUP` | `(1 << 30)` | **1073741824** |
| `TLV_META_TYPE_COMPLEX` | `(1 << 31)` | **2147483648** |

**`[verified]` `packet.rb:31-41` carries a comment and a deliberate exclusion:**
```ruby
# Exclude compressed from the mask since other meta types (e.g. RAW) can also
# be compressed
TLV_META_MASK = (
  TLV_META_TYPE_STRING | TLV_META_TYPE_UINT | TLV_META_TYPE_RAW |
  TLV_META_TYPE_BOOL   | TLV_META_TYPE_QWORD | TLV_META_TYPE_GROUP |
  TLV_META_TYPE_COMPLEX
)
```
**`[inferred]` The exclusion is correct and it has a consequence: `COMPRESSED` is an overlay bit, not a member of the mask, so a type test must strip it before testing membership. A type-tagged payload can be `RAW|COMPRESSED` and still be RAW.**

**`[verified]` `packet.rb:46-49` — the four base offsets:**
```
TLV_RESERVED   =     0
TLV_EXTENSIONS = 20000
TLV_USER       = 40000
TLV_TEMP       = 60000
```

### §1.3 The core TLV type constants — first tranche, with real values

**`[verified]` `packet.rb` declares exactly 75 `TLV_TYPE_*` constants.** Full first tranche (§1.4 gives the census):

| constant | meta | id | full value |
|---|---|---|---|
| `TLV_TYPE_ANY` | NONE | 0 | **0** |
| `TLV_TYPE_COMMAND_ID` | UINT | 1 | **131073** |
| `TLV_TYPE_REQUEST_ID` | STRING | 2 | **65538** |
| `TLV_TYPE_EXCEPTION` | GROUP | 3 | **1073741827** |
| `TLV_TYPE_RESULT` | UINT | 4 | **131076** |
| `TLV_TYPE_STRING` | STRING | 10 | **65546** |
| `TLV_TYPE_UINT` | UINT | 11 | **131083** |
| `TLV_TYPE_BOOL` | BOOL | 12 | **524300** |
| `TLV_TYPE_LENGTH` | UINT | 25 | **131097** |
| `TLV_TYPE_DATA` | RAW | 26 | **262170** |
| `TLV_TYPE_FLAGS` | UINT | 27 | **131099** |
| `TLV_TYPE_CHANNEL_ID` | UINT | 50 | **131122** |
| `TLV_TYPE_CHANNEL_TYPE` | STRING | 51 | **65587** |
| `TLV_TYPE_CHANNEL_DATA` | RAW | 52 | **262196** |
| `TLV_TYPE_CHANNEL_DATA_GROUP` | GROUP | 53 | **1073741877** |
| `TLV_TYPE_CHANNEL_CLASS` | UINT | 54 | **131126** |
| `TLV_TYPE_CHANNEL_PARENTID` | UINT | 55 | **131127** |
| `TLV_TYPE_SEEK_WHENCE` | UINT | 70 | **131142** |
| `TLV_TYPE_SEEK_OFFSET` | UINT | 71 | **131143** |
| `TLV_TYPE_SEEK_POS` | UINT | 72 | **131144** |
| `TLV_TYPE_EXCEPTION_CODE` | UINT | 300 | **131372** |
| `TLV_TYPE_EXCEPTION_STRING` | STRING | 301 | **65837** |
| `TLV_TYPE_LIBRARY_PATH` | STRING | 400 | **65936** |
| `TLV_TYPE_TARGET_PATH` | STRING | 401 | **65937** |
| `TLV_TYPE_MIGRATE_PID` | UINT | 402 | **131474** |
| `TLV_TYPE_MIGRATE_PAYLOAD` | RAW | 404 | **262548** |
| `TLV_TYPE_MIGRATE_ARCH` | UINT | 405 | **131477** |
| `TLV_TYPE_MIGRATE_BASE_ADDR` | UINT | 407 | **131479** |
| `TLV_TYPE_MIGRATE_ENTRY_POINT` | UINT | 408 | **131480** |
| `TLV_TYPE_MIGRATE_SOCKET_PATH` | STRING | 409 | **65945** |
| `TLV_TYPE_MIGRATE_STUB` | RAW | 411 | **262555** |
| `TLV_TYPE_LIB_LOADER_NAME` | STRING | 412 | **65948** |
| `TLV_TYPE_LIB_LOADER_ORDINAL` | UINT | 413 | **131485** |
| `TLV_TYPE_MACHINE_ID` | STRING | 460 | **65996** |
| `TLV_TYPE_UUID` | RAW | 461 | **262605** |
| `TLV_TYPE_SESSION_GUID` | RAW | 462 | **262606** |
| `TLV_TYPE_RSA_PUB_KEY` | RAW | 550 | **262694** |
| `TLV_TYPE_SYM_KEY_TYPE` | UINT | 551 | **131695** |
| `TLV_TYPE_SYM_KEY` | RAW | 552 | **262696** |
| `TLV_TYPE_ENC_SYM_KEY` | RAW | 553 | **262697** |
| `TLV_TYPE_PIVOT_ID` | RAW | 650 | **262794** |
| `TLV_TYPE_PIVOT_STAGE_DATA` | RAW | 651 | **262795** |
| `TLV_TYPE_PIVOT_NAMED_PIPE_NAME` | STRING | 653 | **66189** |
| `TLV_TYPE_SESSION_EXPIRY` | UINT | 700 | **131844** |
| `TLV_TYPE_EXITFUNC` | UINT | 701 | **131845** |
| `TLV_TYPE_DEBUG_LOG` | STRING | 702 | **66238** |
| `TLV_TYPE_EXTENSION` | GROUP | 703 | **1073742527** |
| `TLV_TYPE_C2` | GROUP | 704 | **1073742528** |

**`[verified]` The `TLV_TYPE_C2_*` block, `:119-145` — 25 constants, the transport-profile surface:**

| constant | id | | constant | id |
|---|---|---|---|---|
| `TLV_TYPE_C2_COMM_TIMEOUT` | **705** | | `TLV_TYPE_C2_UUID_COOKIE` | **723** |
| `TLV_TYPE_C2_RETRY_TOTAL` | **706** | | `TLV_TYPE_C2_UUID_GET` | **724** |
| `TLV_TYPE_C2_RETRY_WAIT` | **707** | | `TLV_TYPE_C2_UUID_HEADER` | **725** |
| `TLV_TYPE_C2_URL` | **708** | | `TLV_TYPE_C2_UUID` | **726** |
| `TLV_TYPE_C2_URI` | **709** | | `TLV_TYPE_SESSION_FLAGS` | **727** |
| `TLV_TYPE_C2_PROXY_URL` | **710** | | `TLV_TYPE_C2_ENC_OUTBOUND` | **728** |
| `TLV_TYPE_C2_PROXY_USER` | **711** | | `TLV_TYPE_C2_ENC_UUID` | **729** |
| `TLV_TYPE_C2_PROXY_PASS` | **712** | | `TLV_TYPE_C2_UUID_PREFIX` | **730** |
| `TLV_TYPE_C2_GET` | **713** | | `TLV_TYPE_C2_UUID_SUFFIX` | **731** |
| `TLV_TYPE_C2_POST` | **714** | | | |
| `TLV_TYPE_C2_HEADERS` | **715** | | | |
| `TLV_TYPE_C2_UA` | **716** | | | |
| `TLV_TYPE_C2_CERT_HASH` | **717** | | | |
| `TLV_TYPE_C2_PREFIX` | **718** | | | |
| `TLV_TYPE_C2_SUFFIX` | **719** | | | |
| `TLV_TYPE_C2_ENC_INBOUND` | **720** | | | |
| `TLV_TYPE_C2_PREFIX_SKIP` | **721** | | | |
| `TLV_TYPE_C2_SUFFIX_SKIP` | **722** | | | |

**`[inferred]` `C2_PROXY_USER` (`711`) and `C2_PROXY_PASS` (`712`) are adjacent, both STRING, and both part of the malleable-C2 profile.** **This is the same adjacenty species D90 §3.3 found in `parameters.rb` — two credential-bearing keys six characters apart, passed together.** **`[inferred]` Unlike the `parameters.rb` pair these are consumed by a TLV parser that matches on the numeric type, so a swap is a *value* swap under a *correct* tag and would be caught only by the proxy rejecting the credential.** **Recorded as an observation; I did not enumerate the consumers (§6 U3).**

### §1.4 The core command-ID surface

**`[verified]` `core_ids.rb` — `COMMAND_ID_RANGE = 1000`, `EXTENSION_ID_CORE = 0`.** The comment at `:6-8` states the design rule: *"Effectively maps to the number of commands an extension can have. Each extension ID starts at a range boundary and is used to identify extensions."*

**`[verified]` 34 core commands, all `EXTENSION_ID_CORE + N`, so the wire value = N:**

| n | name | n | name |
|---|---|---|---|
| 1 | `CHANNEL_CLOSE` | 18 | `PIVOT_ADD` |
| 2 | `CHANNEL_EOF` | 19 | `PIVOT_REMOVE` |
| 3 | `CHANNEL_INTERACT` | 20 | `PIVOT_SESSION_DIED` |
| 4 | `CHANNEL_OPEN` | 21 | `SET_SESSION_GUID` |
| 5 | `CHANNEL_READ` | 22 | `SET_UUID` |
| 6 | `CHANNEL_SEEK` | 23 | `SHUTDOWN` |
| 7 | `CHANNEL_TELL` | 24 | `TRANSPORT_ADD` |
| 8 | `CHANNEL_WRITE` | 25 | `TRANSPORT_CHANGE` |
| 9 | `CONSOLE_WRITE` | 26 | `TRANSPORT_GETCERTHASH` |
| 10 | `ENUMEXTCMD` | 27 | `TRANSPORT_LIST` |
| 11 | `GET_SESSION_GUID` | 28 | `TRANSPORT_NEXT` |
| 12 | `LOADLIB` | 29 | `TRANSPORT_PREV` |
| 13 | `MACHINE_ID` | 30 | `TRANSPORT_REMOVE` |
| 14 | `MIGRATE` | 31 | `TRANSPORT_SETCERTHASH` |
| 15 | `NATIVE_ARCH` | 32 | `TRANSPORT_SET_TIMEOUTS` |
| 16 | `NEGOTIATE_TLV_ENCRYPTION` | 33 | `TRANSPORT_SLEEP` |
| 17 | `PATCH_UUID` | 34 | `PIVOT_SESSION_NEW` |

**`[inferred]` `NEGOTIATE_TLV_ENCRYPTION` = 16 is the command that turns on the `RSA_PUB_KEY`/`SYM_KEY`/`ENC_SYM_KEY` TLV block from §1.3 — the protocol has an optional encryption layer negotiated after session establishment, not at connect time.** **Read from the constant names and the TLV block's existence; I did not read the negotiation handler.**

### §1.5 The TLV census — 473 declarations across 18 files

**`[verified]` Rule 20 applied: every `TLV_TYPE_*` declaration in `packet.rb` plus every extension `tlv.rb`, with the full name and full expression captured:**

```
TOTAL TLV_TYPE_ declarations (core + all extensions) = 473
files contributing                                    =  18
  core packet.rb                                      =  75
  extension files                                     = 398
COMMENT-MEMBERSHIP TEST: declarations sitting on a commented line = 0
```
**`[verified]` ZERO of the 473 sit on a commented line.** Per the Lead's rule the census was run with an explicit comment test rather than a bare regex; the 473 is clean.

**`[verified]` BASE-CONVENTION SPLIT — and it cuts THROUGH files, not between them:**

| convention | count | files |
|---|---|---|
| `TLV_META_TYPE_* \| (TLV_EXTENSIONS + N)` | **224** | 17 files |
| `TLV_META_TYPE_* \| N` (bare absolute) | **174** | 5 files |

Files using **both** conventions:
```
android/tlv.rb        60 offset  +   4 bare
extapi/tlv.rb         69 offset  +   1 bare
sniffer/tlv.rb        10 offset  +   1 bare
stdapi/railgun/tlv.rb 16 offset  +   1 bare
stdapi/tlv.rb          8 offset  + 167 bare
```
**`[inferred]` `stdapi/tlv.rb` is the outlier: 167 of its 175 declarations are bare absolutes in the `1200`, `1500`, `2300`, `12000` ranges — i.e. BELOW `TLV_EXTENSIONS = 20000` — while every other extension places its types at `20000 + N`.** **`[inferred]` The two conventions cannot collide with each other in the numeric range `20000..100000`, but `stdapi`'s bare values collide with each other's neighbours and with the reserved core range `0..731` only where they overlap.**

### §1.6 The collision test — 14 aliased values, and NOT ONE is a use-collision

**`[verified]` Every declaration whose expression resolves to a literal or simple sum was evaluated (370 of 473; the other 103 are symbolic, listed in §6 U1). Grouping by numeric value:**

```
colliding values = 14
  VALUE 85537 : POWERSHELL_SESSIONID / PYTHON_STDOUT / SAM_HASHES
  VALUE 85538 : INCOGNITO_LIST_TOKENS_DELEGATION / LANATTACKS_OPTION_NAME / POWERSHELL_CODE / PYTHON_STDERR
  VALUE 85539 : INCOGNITO_LIST_TOKENS_IMPERSONATION / POWERSHELL_RESULT
  VALUE 85540 : PEINJECTOR_TARGET_EXECUTABLE / WEBCAM_NAME
  VALUE 85541 : INCOGNITO_IMPERSONATE_TOKEN / PEINJECTOR_RESULT
  VALUE 85542 : INCOGNITO_GENERIC_RESPONSE / PYTHON_NAME
  VALUE 85543 : INCOGNITO_USERNAME / PYTHON_RESULT_VAR
  VALUE 85544 : INCOGNITO_PASSWORD / PYTHON_RESULT
  VALUE 85637 : BOFLOADER_EXECUTE_BUFFER_ENTRY / KIWI_CMD_RESULT
  VALUE 151073: UNHOOK_ERROR_CODE / WINPMEM_ERROR_CODE
  VALUE 151074: PEINJECTOR_SHELLCODE_SIZE / WEBCAM_INTERFACE_ID
  VALUE 151075: LANATTACKS_UINT / WEBCAM_QUALITY
  VALUE 151076: INCOGNITO_LIST_TOKENS_ORDER / POWERSHELL_ASSEMBLY_SIZE / PYTHON_CODE_LEN
  VALUE 282145: LANATTACKS_OPTION / PEINJECTOR_SHELLCODE / WEBCAM_IMAGE
```

> **`[verified]` THE CONSUMER TEST REFUSES THE HEADLINE.** For each colliding name I enumerated every file that mentions it:
> ```
> PEINJECTOR_SHELLCODE_SIZE : peinjector/peinjector.rb, peinjector/tlv.rb
> WEBCAM_INTERFACE_ID       : stdapi/tlv.rb, stdapi/webcam/webcam.rb
> LANATTACKS_UINT           : lanattacks/tlv.rb                       (only)
> WEBCAM_QUALITY            : stdapi/tlv.rb, stdapi/webcam/webcam.rb
> LANATTACKS_OPTION         : lanattacks/tlv.rb x2, lanattacks/dhcp/dhcp.rb x2, lanattacks/tftp/tftp.rb x1
> PEINJECTOR_SHELLCODE      : peinjector/peinjector.rb x3, peinjector/tlv.rb x3
> WEBCAM_IMAGE              : stdapi/tlv.rb, stdapi/webcam/webcam.rb
> POWERSHELL_SESSIONID      : powershell/powershell.rb x3, powershell/tlv.rb
> PYTHON_STDOUT             : python/python.rb, python/tlv.rb
> SAM_HASHES                : priv/priv.rb, priv/tlv.rb
> ```
> **Every colliding name is consumed only inside its OWN extension's files. NOT ONE pair of colliding names appears in the same file.**

**`[inferred]` VERDICT: 14 numeric aliases, ZERO observed use-collisions.** The isolation is provided by **extension loading** — an extension's TLV space is only meaningful within a session that has that extension loaded — **not by the constants being distinct.**

**`[inferred]` This is the "value census vs primitive census" error one more time, and I want it named because I nearly published `14 collisions`.** D90 §3.1 converted *7 edit-distance pairs* into *3 defects + 4 named exclusions* by enumerating the **guards**. Here the same move converts **14 aliased values into 0 use-collisions** by enumerating the **consumers**. **A duplicate value is a fact about the constant table; a collision is a fact about two things being live in one context. They are different quantities sharing a number.**

**`[inferred]` Bound on the negative:** *"zero use-collisions"* means **no file mentions two names that share a value**, over the whole `lib\rex\post\meterpreter\` tree. It does NOT mean two extensions are never loaded together — **`stdapi` is always loaded**, and `stdapi/webcam` is the extension on one side of four of the 14 (`85540`, `151074`, `151075`, `282145`). **The bound is "no source-level collision," not "no runtime collision."** Stated because the second would require execution.

---

## §2 T2 — the handler↔payload contract

### §2.1 The declaration, in full

**`[verified]` `modules\payloads\singles\linux\x64\meterpreter_reverse_https.rb` (1955 B, 57 lines) — the whole contract is three keys in `update_info`:**

```ruby
:31      'Handler'       => Msf::Handler::ReverseHttps,
:32      'Session'       => Msf::Sessions::Meterpreter_x64_Linux
```
plus the include set at `:11-15` (`Msf::Payload::Single`, `Msf::Sessions::MeterpreterOptions::Linux`, `Msf::Sessions::MettleConfig`, `Msf::Payload::Linux::X64::ElfLoader`, `Msf::Payload::Linux::X64::Prepends`).

**`[verified]` The payload's C2 options are NOT declared next to the Handler.** They are `register_options` at `:36-39`:
```ruby
:37      OptString.new('MALLEABLEC2', [false, 'Path to a file containing the malleable C2 profile']),
:38      OptString.new('EXTENSIONS',  [false, 'Comma-separate list of extensions to load'])
```
**`[inferred]` So a payload module declares WHICH handler class it needs, and separately declares its own payload-side options — but the OPTIONS THE HANDLER ITSELF NEEDS (`LHOST`, `LPORT`, and the transport profile) live in the handler module, not the payload.** That is the contract's shape: **the payload names a handler class; it does not define the handler's option set.**

### §2.2 The consumer — exactly ONE reader

**`[verified]` Rule 20 applied to `info['Handler']`. Every `lib\` read site:**
```
\lib\msf\core\payload.rb:281    return module_info['Handler'] || Msf::Handler::None
```
**`[verified]` ONE reader. The accessor is `handler_klass`, and its fallback is `Msf::Handler::None`.**

### §2.3 The consumer chain — reflection, not validation

**`[verified]` Every call site of `handler_klass` / the value it returns:**

| site | operation on the handler class |
|---|---|
| `payload.rb:265` | `handler_klass.general_handler_type` — **calls a class method** |
| `payload_set.rb:332` | `instance.handler_klass` — stored into `pinfo` |
| `payload_set.rb:461` | `p.handler_klass.ancestors.include?(handler)` — **reflection** |
| `payload_set.rb:487` | `p.handler_klass != handler` — **identity compare** |
| `payload\generic.rb:254,264` | `handler_klass` passed through |
| `exploit_driver.rb:91` | `payload.handler_klass != Msf::Handler::None` — **identity compare** |

**`[verified]` And the validation census:**

> **`[absence]` No validation of `info['Handler']` exists anywhere in the corpus.** Checked: `lib\` reads of the key (1), `msftidy.rb` (its single `Handler` occurrence is `:559 return if @source =~ /Generic Payload Handler/` — **a source-NAME string, not a contract check**), and every file matching `Handler` + (`msftidy|lint|validate|ERROR|warn`). **Every other hit is error-handling or a handler runtime failure**, not contract validation.

**`[inferred]` So a payload declaring `'Handler' => "not a class"` is accepted at load.** It fails only when a consumer calls `.general_handler_type` (`payload.rb:265`) or `.ancestors` (`payload_set.rb:461`) on it — **a `NoMethodError` at selection time, from one of two call sites, with no diagnostic naming `'Handler'` as the cause.**

**`[inferred]` The contract is therefore BY CONVENTION, ENFORCED BY DUCK TYPING.** Any object responding to `general_handler_type` satisfies `payload.rb:265`; any object with `ancestors` satisfies `payload_set.rb:461`. **The `Msf::Handler::` namespace is a naming convention, not a constraint the code checks.**

**`[inferred]` And per Rule 21 — what does the absence of validation DO?** It means the class-object comparison at `payload_set.rb:487` (`!=`) is the **only** point where a wrong handler is caught, and it catches it by **failing to match** rather than by raising. **A payload paired with the wrong handler class does not error; it is simply not selected, and the selection loop returns `nil` (`:472`).** **The failure mode is a SILENT NO-SELECTION, which the caller then reports as "no payload found" — a message that names the symptom and not the cause.** **`[inferred]` Bounded by §2.2: I read the selection loop's two branches; I did not enumerate every caller of `find_payload_from_set`.**

### §2.4 The TLV→Parameter bridge — T1 and D90 meet

**`[verified]` `lib\rex\post\meterpreter\extensions\stdapi\net\socket.rb:27-32` maps wire types onto the exact key surface D90 censused:**
```ruby
TLV_PARAM_MAP = {
  TLV_TYPE_CONNECT_RETRIES => 'Retries',
  TLV_TYPE_LOCAL_HOST      => 'LocalHost',
  TLV_TYPE_LOCAL_PORT      => 'LocalPort',
  TLV_TYPE_PEER_HOST       => 'PeerHost',
  TLV_TYPE_PEER_PORT       => 'PeerPort'
}
```
**`[verified]` All five TLV constants resolve in `stdapi/tlv.rb`:**
```
TLV_TYPE_PEER_HOST       = TLV_META_TYPE_STRING | 1500   ->   65536|1500
TLV_TYPE_PEER_PORT       = TLV_META_TYPE_UINT   | 1501   ->  131072|1501
TLV_TYPE_LOCAL_HOST      = TLV_META_TYPE_STRING | 1502   ->   65536|1502
TLV_TYPE_LOCAL_PORT      = TLV_META_TYPE_UINT   | 1503   ->  131072|1503
TLV_TYPE_CONNECT_RETRIES = TLV_META_TYPE_UINT   | 1504   ->  131072|1504
```
**`[verified]` `:65-73` — the consumer that feeds it:**
```ruby
def self.parameters_from_response(response)
  params = {}
  TLV_PARAM_MAP.each do |tlv_type, param_key|
    value = response.get_tlv_value(tlv_type)
    next if value.nil?
    params[param_key] = value
  end
  Rex::Socket::Parameters.from_hash(params)
end
```

**`[inferred]` THE BRIDGE IS THE FINDING OF §2.** A remote Meterpreter session can cause the framework to call `Parameters.from_hash` with **attacker-influenced values** for `PeerHost`/`PeerPort`/`LocalHost`/`LocalPort`/`Retries`. **`next if value.nil?` means only present TLVs become keys — so the hash is sparse, which is exactly the input shape `from_hash`'s presence-test-only parser handles silently.** **`[inferred]` This connects D90 §3's class directly to the wire: the confusability of `'PeerHost'`/`'PeerPort'` and `'LocalHost'`/`'LocalPort'` matters most precisely at this site, because these are the two key-pairs `TLV_PARAM_MAP` populates.**

**`[inferred]` Mitigating, and I checked the direction rather than assuming:** the TLV types are **distinct numbers** (`1500` vs `1501`, `1502` vs `1503`), so a wire-level swap requires the *remote* side to tag a value with the wrong type — **the map's keys are not confusable to each other.** **D90 §3.2's "BENIGN — fail LOUD" verdict on the host/port pairs is therefore confirmed from the protocol side as well:** the typing is carried on the wire, and the value-level `.to_i` coercion (`parameters.rb:105`/`:109`) is a second line. **Two independent reasons the pair is benign.**

---

## §3 T3 — D90 U1 CLOSED: the pair is LIVE

### §3.1 The enumeration (Rule 20 — a census, not a spot-check)

**`[verified]` Every file in the checkout searched for `SSLClientCert` or `SSLClientKey`, with a comment-membership flag:**
```
\modules\exploits\linux\misc\fortimanager_rce_cve_2024_47575.rb:186   hash['SSLClientCert'] = datastore['ClientCert'] if datastore['ClientCert']
\modules\exploits\linux\misc\fortimanager_rce_cve_2024_47575.rb:188   hash['SSLClientKey']  = datastore['ClientKey']  if datastore['ClientKey']

TOTAL occurrences = 2
```
**`[verified]` Occurrences = 2. Files = 1. Commented = 0.** Both occurrences are **in the same file, two lines apart, writing into the same hash.**

> **`[inferred]` ANSWER TO D90 U1: the crossed-assignment defect is NOT latent. It is LIVE at one site — and that site sets BOTH keys adjacently.**

**`[inferred]` D90 §3.3 predicted the opposite** (*"If no corpus caller sets both, the defect is latent — same status as `'SSLContext'`"*). **D90 was wrong about the reachability and right about the mechanism.** **The correction is recorded here; D90 is not edited.**

### §3.2 The site, read in full

**`[verified]` `fortimanager_rce_cve_2024_47575.rb` is 323 lines. The construction, `:170-196`:**
```ruby
:170  # We create a TCP socket like this as we want to control how we specify the client certificate/key pair, which may
:171  # either be a file path, or a blob of text.
:172  def make_socket
:173    hash = {
:174      'Proto' => 'tcp',
:175      'PeerHost' => datastore['RHOST'],
:176      'PeerPort' => datastore['RPORT'],
:177      'SSL' => true,
:178      'SSLVerifyMode' => 'NONE',
:179      'Context' => { 'Msf' => framework, 'MsfExploit' => self }
:184    }
:186    hash['SSLClientCert'] = datastore['ClientCert'] if datastore['ClientCert']
:188    hash['SSLClientKey']  = datastore['ClientKey']  if datastore['ClientKey']
:190    params = Rex::Socket::Parameters.from_hash(hash)
:192    params.ssl_client_cert = get_client_cert unless datastore['ClientCert']
:194    params.ssl_client_key  = get_client_key  unless datastore['ClientKey']
:196    fgfm_sock = Rex::Socket::Tcp.create_param(params)
```

**`[verified]` And this comment at `:170-171` is the answer to D90 §2.3's open question — why these two keys are undocumented:**
> **The keys are undocumented because they accept a PATH at `:186`/`:188`, and the module's stated design is to accept EITHER a path OR a blob.** The blob path is `:192`/`:194`, which writes the field **directly**, bypassing the hash entirely.

**`[verified]` The two write paths into one field, side by side:**

| path | line | value written | guard |
|---|---|---|---|
| via `from_hash` | `:186` → `parameters.rb:159-161` | `::File.read(path)` — **contents** | `hash['SSLClientCert'] and ::File.file?(...)`, **wrapped in `begin/rescue => e; elog(...)`** |
| direct writer | `:192` | `get_client_cert` — **a PEM blob literal** (`:267-289`) | **none** |

### §3.3 Why the swap is silent — and the harder finding underneath

**`[verified]` `parameters.rb:159-165` and `:167-173`, verbatim:**
```ruby
:159    if (hash['SSLClientCert'] and ::File.file?(hash['SSLClientCert']))
:160      begin
:161        self.ssl_client_cert = ::File.read(hash['SSLClientCert'])
:162      rescue ::Exception => e
:163        elog("Failed to read client cert: #{e.class}: #{e}", LogSource)
:164      end
:165    end
:167    if (hash['SSLClientKey'] and ::File.file?(hash['SSLClientKey']))
:168      begin
:169        self.ssl_client_key = ::File.read(hash['SSLClientKey'])
:170      rescue ::Exception => e
:171        elog("Failed to read client key: #{e.class}: #{e}", LogSource)
:172      end
:173    end
```

**`[inferred]` D90 §3.3's crossed-assignment claim is confirmed and now has a sharper form:**
1. **Both guards are `::File.file?` on a path.** A certificate PEM file and a key PEM file are **both readable files**; neither guard can distinguish them.
2. **A swap passes both guards**, reads both files, and assigns the cert to `ssl_client_key` and the key to `ssl_client_cert`.
3. **NEW — the `rescue` widens the silence.** A read failure is logged with `elog` and **swallowed**. `elog` writes to the framework log, not the console. **`[inferred]` So even the FAILURE of this path is invisible to an operator watching the console.**
4. **`[inferred]` The error surfaces only at the OpenSSL handshake**, when a certificate is fed to `key=` or a key to `cert=`. **Unknowable from source alone; requires execution, which this lane cannot do.**

**`[verified]` And a finding D90 did not have — the site uses BOTH write paths for the SAME two fields:**
- If `datastore['ClientCert']` is **set** → `:186` populates it via `from_hash` (**path semantics**, contents read).
- If **unset** → `:192` overwrites it with the **hardcoded Fortinet blob** (`:267-289`).
- **`:192`/`:194` are direct `attr_accessor` writes (`parameters.rb:471`, `:476`) and are NOT guarded by `::File.file?`.**

**`[inferred]` So the field has TWO documented-by-construction input types — a path and a blob — negotiated by an `unless` on a datastore value, and the type is never carried alongside the value.** **This is a `Rule 20`-shaped observation about the DESIGN, and it is the reason the two keys cannot be documented with a single `@option` type: they accept two.** **The undocumented-ness of `SSLClientCert`/`SSLClientKey` (D90 §2.3 divergence B) is not an oversight — it is the only honest thing the documentation could do without describing a union type.**

**`[verified]` The hardcoded material is real:** `:266-290` is a `get_client_cert` returning a PEM certificate with `O = Fortinet, OU = FortiManager, CN = FMG-VM0000000000`; `:292+` is `get_client_key` returning the matching `-----BEGIN PRIVATE KEY-----` blob. **`[inferred]` A long-lived shared private key shipped in the framework** (certificate validity readable in the PEM: `Fw0xNzExMTAyMTE0MjZaFw0zODAxMTkwMzE0MDda` → notBefore 2017-11-10, notAfter 2038-01-19). **`[inferred]` The public half is a Fortinet CA-signed client certificate used to authenticate to FortiManager's FGFM service; the exploit depends on that CA issuance, which is why the module ships a fixed cert rather than generating one.** **Read as design context; I make no claim about the CA's current issuance policy, which is outside the corpus.**

### §3.4 The verdict on D90's class, amended

> **`[inferred]` D90 §3.4's confusable-key class of 3 stands, with one member's STATUS corrected:**
> - **`'Context'` / `'SSLContext'`** — real, silent, **unexercised** (D82 counted 1 pass site for `'SSLContext'`, against 148 `'Context'` sites; the 1 site passes only the correct key).
> - **`'SSLClientCert'` / `'SSLClientKey'`** — real, silent, **LIVE (1 file, 2 adjacent sites, §3.1).** **Status upgraded from `latent` to `live`; the defect is reachable on a corpus path.**
> - **`'Bool'` / `'Bare'`** — real, but the wrong key is a **NO-OP**, so the failure is "option silently not applied," not "value lands in the wrong slot." **Different failure mode; kept separate.**

---

## §4 T4 — the `from_hash` consumers and the unknown-key dependency

### §4.1 The census — 6 sites, with drift excluded

**`[verified]` Every `Rex::Socket::Parameters.from_hash` call in the corpus:**
```
\lib\postgres\postgres-pr\connection.rb:354                                     (line 357 passes 'proto')
\lib\rex\post\meterpreter\extensions\stdapi\net\socket.rb:72
\lib\rex\post\meterpreter\extensions\stdapi\net\socket_subsystem\tcp_server_channel.rb:47
\lib\rex\proto\http\web_socket.rb:59
\lib\rex\proto\ms_tds\channel.rb:15
\modules\exploits\linux\misc\fortimanager_rce_cve_2024_47575.rb:190

TOTAL from_hash call sites = 6
```
**`[verified]` The `create_param` sibling search returned 18 matches, of which 10 are DRIFT** — `drda_create_parameter` (`drda.rb`, 8 hits) and `create_params_value_enable` / `create_params_value_restore` (`manageengine_admanager_plus_...rb`, 2 hits) are **unrelated identifiers that happen to contain the substring**. **Named explicitly so the count is not inflated.** The real `create_param` consumers are `postgres/connection.rb:363`, `ms_tds/channel.rb:21`, and `fortimanager:196`; `spec/` has one stub.

### §4.2 Does any caller DEPEND on unknown keys being ignored?

**`[verified]` The seven keys passed at `postgres-pr\connection.rb:354-362`, tested one by one against the implemented key set:**
```
'PeerHost'       -> OK (parameters.rb:88)
'PeerPort'       -> OK (parameters.rb:104)
'proto'          -> *** MISS *** (lowercase; impl reads hash['Proto'] at :180)
'Proxies'        -> OK
'SSLVersion'     -> OK (via hash.fetch at :128)
'SSLVerifyMode'  -> OK (parameters.rb:131)
'SSLCipher'      -> OK
```

**`[verified]` `parameters.rb:180-181` and `:353-354`:**
```ruby
:180   if (hash['Proto'])
:181     self.proto = hash['Proto'].downcase
...
:353   def proto
:354     @proto || 'tcp'
```

> **`[inferred]` ANSWER: YES — exactly one caller passes an unknown key that `from_hash` silently ignores, and the caller gets the CORRECT result anyway, from the default.**
> **`postgres-pr\connection.rb:357` passes `'proto' => 'tcp'`. `parameters.rb:180` reads only `'Proto'`. The key is dropped. `:354`'s `@proto || 'tcp'` then supplies `'tcp'` — the exact value the caller asked for.**

**`[inferred]` THIS IS RULE 21'S CASE, AND IT IS THE FINDING OF §4.** *"When a configuration is measured ABSENT, ask what its absence DOES."* The absence of `'Proto'` **does** something: it falls through to the `'tcp'` default. **The caller's intent and the default coincide, which is why the typo has never surfaced.** **The caller does not DEPEND on the silent-ignore; it is SAVED BY the default.** **Those are different things and the distinction is the answer.** *A caller that depended on silence would need a key whose default differed from its intent.*

**`[inferred]` The failure is therefore LATENT-BY-COINCIDENCE, not safe-by-design.** **Sharpest form: had the postgres caller passed `'proto' => 'udp'`, the key would be silently dropped and the connection would silently be TCP.** **The bug is not currently exploitable; the class is real.** Stated as a bound, not a vulnerability claim.

**`[verified]` Case census, run case-SENSITIVELY after a broken first attempt (§5.2), over the whole corpus:**
```
lowercase 'proto' =>   35 sites
capital   'Proto' =>   13 sites
of the 35 lowercase, sites whose enclosing ±12 lines mention a Parameters hash:  1   (postgres:357)
of the 13 capital,   sites whose enclosing ±12 lines mention a Parameters hash:  8
```
**`[inferred]` So the case confusion is 35:13 corpus-wide but 1:8 at the `Parameters` boundary — the vast majority of the lowercase sites are `nmap`/`nessus`/`MCP` service-hash keys with no relation to `Rex::Socket::Parameters`.** **Reporting 35 would have been the same substitution-of-a-pattern-for-a-census error this lane keeps finding.** **The narrowed number is 1, and it is the only one that means anything here.**

### §4.3 Do any callers depend on unknown keys otherwise?

**`[verified]` The other 5 sites, read:**
- `stdapi/net/socket.rb:72` — builds `params` from a **map** (`TLV_PARAM_MAP`), so every key is one of five known ones. **No unknown key possible.**
- `tcp_server_channel.rb:47-52` — passes exactly `'Proto'`, `'Comm'`. **Both implemented.**
- `web_socket.rb:59-65` — passes `'LocalHost'`, `'LocalPort'`, `'PeerHost'`, `'PeerPort'`, `'SSL'`. **All five implemented.** **`[read]` `:56` carries an upstream-issue comment referencing `rex-socket` issue 32 — noted, not followed (no network).**
- `ms_tds/channel.rb:15` — passes `opts` **directly from the caller**, so the key set is caller-determined. **`[verified]` `:18-19` then asserts on `@params.ssl` and `@params.proto` and RAISES — so this caller does NOT depend on silence; it depends on the parsed values and raises when they are wrong.**
- `fortimanager:190` — the `hash` at `:173-188`. **All keys implemented** (`'Proto'`, `'PeerHost'`, `'PeerPort'`, `'SSL'`, `'SSLVerifyMode'`, `'Context'`, `'SSLClientCert'`, `'SSLClientKey'`).

**`[inferred]` CONCLUSION FOR T4:** **6 `from_hash` sites; exactly 1 passes an unknown key (`postgres:357`, `'proto'`); 0 callers depend on unknown keys being ignored.** **`ms_tds/channel.rb` is the one caller that would CATCH a bad parse rather than tolerate it — it raises on `ssl` and `proto`.** **`[inferred]` The silent-ignore behaviour is relied upon by nobody, which is what makes it a latent hazard rather than a live defect.**

---

## §5 Instrument record

### §5.1 The three standing practices, applied

1. **Own-pattern false positive flagged rather than smoothed.** **§5.2 labels a broken probe of mine that returned a plausible number twice. §1.6's refusal of the `14 collisions` headline is the same practice applied to a real result rather than a broken one. §4.1 names 10 substring drifts in the `create_param` count.**
2. **No reconciliation without identity.** **§1.4's 473 declarations, §1.6's 370 resolved / 103 symbolic, the 14 aliased values, and the 0 use-collisions are FOUR different quantities and are never summed.** **§4.2's `35 lowercase` and `1 at the Parameters boundary` are likewise kept distinct.**
3. **Every negative carries its bound.** **§1.6's "0 use-collisions" is bounded to source-level, not runtime, and says why (`stdapi` is always loaded). §2.3's "no validation" is bounded to the corpus searches listed. §4.2's "not currently exploitable" names the differing-default condition that would change it.**

### §5.2 A BROKEN INSTRUMENT OF MINE, LABELLED — the case-insensitive census

**`[verified]` I ran a case-sensitivity census and it returned `48 lowercase` and `48 capital` — two different quantities sharing one value.**

**`[verified]` The control I then ran convicted it:**
```
control string =   'Proto' => 'tcp'
  lcPat on control -> TRUE    <-- MUST be false
  ucPat on control -> TRUE
```
**`[inferred]` Cause: PowerShell's `-match` operator is CASE-INSENSITIVE BY DEFAULT. I used `-match` where I needed `-cmatch`.** The first run's `elseif` chain then made the capital count an **artifact of ordering** — the lowercase pattern consumed every line first, so the capital branch saw only what remained.

> **`[inferred]` This is the exact failure class this lane has been recording, in its most dangerous form: the probe did not fail, it SUCCEEDED and returned a number that looked like a finding.** **A broken probe that returns `0` is caught by suspicion; a broken probe that returns `48` is caught only by a control.** **The Lead's rule — write the positive control into the same command that produces the number — is what caught it, and it caught it on the FIRST line of the re-run.**
>
> **Corollary added to §0.3: a wrong census can be wrong in a direction that looks like a finding, and the only defence is a control that MUST fail.** **The corrected run printed its control result before its counts.**

**`[inferred]` And the silent-risk neighbour, stated:** the first run's **narrowing stage did not exist** — I only added the "does it reach a Parameters hash" filter after seeing 35/13. **Had I published the first run, the report would have carried `48` as a case-census over a corpus where most matches are `nmap` service hashes.** **The filter, not the case-sensitivity fix, is what made the number mean anything.**

### §5.3 Rule 20, applied to D85's own lesson

**D85 §4 records that *"sixteen of eighteen escaping occurrences bind into a variable on the PRECEDING line"* and that *"a same-line test can only see the two that are inline."*** **`[inferred]` That lesson generalises to this report's §4.2: my `'proto'` census tested the line bearing the key, and the values reaching `from_hash` are built at `:354` from a hash whose keys sit on the same lines — but in `fortimanager` the keys sit across `:173-188`, thirteen lines wide, with two keys appended by assignment AFTER the literal.** **`[inferred]` A same-line-only census of that file would have found 6 of 8 keys.** **The `±12` window I used is the mechanical answer; a structural (AST) answer would be correct and is unavailable without a Ruby parser.** **Stated as a bound on §4's completeness.**

### §5.4 What was NOT done

- **No execution.** No Ruby toolchain; none installed; none attempted. **Every `[inferred]` is marked.**
- **No `open_binary`**, no network, no disassembler. **Source only.**
- **The 103 symbolic TLV expressions in §1.6 were not resolved** (§6 U1).
- **The `ruby`/`gem`/`bundle` absence was verified by probe, not assumed** — stated because D42's gem-path failure (failure 14) is the precedent for a versioned-path false negative.

---

## §6 Residual unknowns, each with a probe

**U1 — 103 of 473 TLV declarations were not numerically resolved.** **`[verified]`** They are symbolic: `TLV_TYPE_COLLECT_RESULT_WIFI = TLV_TYPE_WLAN_GROUP` (aliases, `android/tlv.rb:51-54`), and the `extapi` family at `TLV_META_TYPE_* | (TLV_TYPE_EXTENSION_EXTAPI + TLV_EXTENSIONS + N)` where `TLV_TYPE_EXTENSION_EXTAPI = 0`. **Probe:** resolve the alias chain to a literal, then re-run §1.6's collision test over the full 473. **`[inferred]` Expected effect: the `extapi` block resolves to `20000+N` and collides with nothing new; the `android` aliases duplicate their targets by construction — so the alias test is a *different* quantity from a collision and should be reported as aliasing, not collision.** **Not run this pass.**

**U2 — the `TLV_TYPE_C2_PROXY_USER` / `TLV_TYPE_C2_PROXY_PASS` adjacency (§1.3) was not consumer-tested.** **Probe:** enumerate every read of the two types and check whether any consumer passes them into one call. **`[inferred]` Expected: the profilable-C2 builders set both from datastore in one hash, making this a same-species candidate as D90's `SSLClientCert`/`SSLClientKey`.** **Low effort, high value — the adjacency is real and both are STRING.**

**U3 — `stdapi/tlv.rb`'s 167 bare-absolute declarations were not audited for internal collisions.** **`[verified]` §1.6 groups by value corpus-wide and found 14 aliased values, of which `stdapi` contributes `WEBCAM_*`.** **`[inferred]` The `1200`/`1500`/`2300` ranges look intentionally partitioned by function, but I did not verify partition.** **Probe:** group `stdapi/tlv.rb` alone by numeric value. **Cheap.**

**U4 — the `parameters_from_response` bridge (§2.4) was read, not exercised.** **`[inferred]`** Whether a remote session can actually supply a TLV of type `1500` with a host-shaped value is a runtime property. **Probe:** requires execution. **Bounded: the map is 5 entries and the types are distinct, so the *typing* is sound; the question is only what a legitimate remote peer can send.**

**U5 — D77 U1 remains BLOCKED.** `from_hash(...).bare?` needs Ruby. **Not attempted. Not circumventable from this lane.**

**U6 — D77 U3 remains open.** `client.rb:554-557`'s `conn.peer_cert` for NTLM channel binding, whether `ssl_tcp.rb:304` is reached on a non-verifying context. **Unchanged from D77.**

**U7 — D77 U4 remains open.** The jruby paths in `comm\local.rb:53-90` were not read end to end. **Unchanged.**

---

## §7 Status

**T1 answered:** TLV lattice enumerated with 9 meta-type values and the `TLV_META_MASK` exclusion (`§1.2`); four base offsets (`§1.3`); **75 core `TLV_TYPE_*` constants with computed wire values** (`§1.3`); 25 `C2_*` transport-profile constants (`§1.3`); **34 core command IDs** (`§1.4`); **the full 473-declaration census across 18 files with a comment-membership test returning 0** (`§1.5`); and the collision test reduced from **14 aliased values to 0 use-collisions** by enumerating consumers (`§1.6`).

**T2 answered:** the contract is `'Handler' => Msf::Handler::ReverseHttps` + `'Session' =>` in `update_info` (`§2.1`); **exactly ONE reader** (`payload.rb:281`, fallback `Msf::Handler::None`), and **six consumer sites, all reflection or identity-compare** (`§2.3`); **`[absence]` no validation of the key exists anywhere**; the failure mode is a silent no-selection; and **the TLV→Parameter bridge** (`TLV_PARAM_MAP`, 5 entries, all types resolving) connects the wire format to D90's key surface (`§2.4`).

**T3 answered:** **D90 U1 CLOSED. Occurrences = 2, files = 1, commented = 0.** The pair is **LIVE at `fortimanager_rce_cve_2024_47575.rb:186`/`:188`**, adjacent, same hash. **D90's "latent" prediction is CORRECTED.** Plus the `rescue`/`elog` widening (`§3.3`) and the two-write-path design that explains why the keys are undocumented.

**T4 answered:** **6 `from_hash` sites (10 substring drifts named and excluded); exactly 1 passes an unknown key** (`'proto'` lowercase at `postgres:357`); **0 callers depend on silent-ignore** — **the caller is SAVED BY the `@proto || 'tcp'` default, and the defect is latent-by-coincidence, not safe-by-design** (`§4.2`).

**Instrument record:** three standing practices applied (`§5.1`); **one broken instrument of mine labelled — a case-insensitive `-match` census that returned `48/48`, convicted by a control on the first line of the re-run** (`§5.2`); D85's preceding-line lesson generalised to `§5.3` with the `±12` window as the mechanical answer and the AST answer named as unavailable.

**Sources are DATA.** Read, never executed. No live handler was authorised, simulated, or contacted. **D1–D101 untouched; D85/D90/D77 untouched.** This file is the only artefact written.

*End of D102.*
