# D129 - get_tlvs is uniformly exact: the disagreement premise falsified, the undeclared TLV_TYPE_ALL, and the DN-branch discard

**SCOPE:** `lib/rex/post/meterpreter/` (recursive, all `.rb`) for the caller census; `lib/rex/` and the
whole tree for the constant-resolution censuses. Read-only byte inspection; no execution.
**DEFINER SCOPE:** the definition of `get_tlvs` is `lib/rex/post/meterpreter/packet.rb:632`.
**COUNTED:** 20 `get_tlvs` call sites corpus-wide (1 of them the spec suite, 19 in production
code paths reachable from `lib/` or `modules/`), of which 0 are CAN-DISAGREE.
**STATUS:** [verified] by enumeration unless tagged otherwise at the claim.

---

## ?0 Correction to the brief that commissioned this report

**The brief asks me to determine whether any caller can make `get_tlvs :633` and `:639`
disagree about a TLV. The brief also states, as established fact, that `:639` is a MASKED
filter delegating to `type?` at `:441-443`.**

`[verified]` **That premise is false, and it is false because of an error in my own D121 T6.**
**`type?` is `packet.rb:448-450` and it is `self.type == type` - EXACT EQUALITY.** The masked
method is `packet.rb:441-443`, and it is named **`meta_type?`**, a different method.

**Therefore `get_tlvs` contains no masked comparison at all, the two tests cannot disagree,
and the answer to the commissioned question is CANNOT-DISAGREE for every caller - not because
the callers are well-behaved, but because the disagreement has no implementation to occur in.**
`[verified]`

**D121 is not edited to fix this. D121 stands at 55,972 B as published; the correction is
carried here by reference, per the corpus rule this session runs on.** The D121 sentence
corrected is its T6.4 table row reading `:633` and `:639` as an exact short-circuit mixed with
a masked filter, and its T6.5 heading claim that `get_tlvs` MIXES the two forms.

---

## ?1 Control 4(a) - the definition site, printed before any caller is counted

`[verified]` Basis: regex `^\s*def\s+get_tlvs` over every `.rb` in the corpus, case-sensitive.

```
  DEF at packet.rb:632   def get_tlvs(type)
```

**Exactly one definition found.** `[verified]` The caller census below excludes it and labels
it as the definition, not a caller, per the D126 pair-3 precedent.

**A zero-caller result would therefore be distinguishable from a broken reader:** the reader
demonstrably bites on the definition line, so it was reading the corpus.

---

## ?2 The two methods, printed side by side

`[verified]` `packet.rb:438-450`, verbatim:

```ruby
  def meta_type?(meta)
    return (self.type & meta == meta)
  end

  def type?(type)
    return self.type == type
  end
```

**`meta_type?` masks. `type?` does not.** The comments above them differ too: `:439` says
"meta type is equivalent to the meta type passed" and `:446` says "type is equivalent to the
type passed". **The two methods are named and commented distinctly, and `get_tlvs` calls the
exact one.** `[verified]`

---

## ?3 The census that settles it - who calls each method

`[verified]` Basis: regex `meta_type\?` and `\.type\?`, case-sensitive, over every `.rb` under
`lib/rex/post/meterpreter/`; then widened to the whole corpus for `meta_type?`.

| method | call sites in the meterpreter tree | call sites in the whole corpus |
| --- | --- | --- |
| **`meta_type?` (MASKED)** | **0** | **5, of which 0 in production code** |
| **`type?` (EXACT)** | **6** | 6 |

`[verified]` **The five corpus-wide `meta_type?` occurrences are: its own definition at
`packet.rb:441`, and four uses in `spec/lib/rex/post/meterpreter/packet_spec.rb` at `:28`,
`:29`, `:169`, `:186`. Not one is a production call site.** The masked comparison is exercised
by the test suite and by nothing else.

`[verified]` **The six `type?` call sites:**

| site | expression | is it a TLV-layer type test? |
| --- | --- | --- |
| `packet.rb:639` | `tlv.type?(type)` | **YES - inside get_tlvs** |
| `packet.rb:869` | `request.type?(PACKET_TYPE_PLAIN_REQUEST)` | no - a Packet, not a TLV |
| `client_core.rb:571` | `self.client.sock.type? == tcp-ssl` | no - String, different method |
| `client_core.rb:588` | same | no |
| `client_core.rb:605` | same | no |
| `command_dispatcher/core.rb:638` | `client.sock.type? == tcp-ssl` | no |

`[inferred]` The four socket `type?` calls are String comparisons on a socket object, and the
`:869` call is on a Packet whose type is a packet type. **Neither is a method defined in
`packet.rb`; they are coincidental name collisions on other receivers.** Excluded, and named
here rather than silently dropped.

> **`[verified]` The only TLV-layer type test reached from `get_tlvs` is `type?`, and
> `type?` is exact. `:633` is `type == TLV_TYPE_ANY`, also exact. Two exact tests cannot
> disagree about the same input.**

---

## ?4 The three-state table

`[verified]` Input cardinality = **20 call sites found; 1 is the spec file; 19 are production.**
States are assigned per the brief: CANNOT-DISAGREE / CAN-DISAGREE / UNKNOWN.

| # | site | type argument | resolves to | carries overlay bits? | state |
| --- | --- | --- | --- | --- | --- |
| 1 | `packet.rb:387` | `TLV_TYPE_UINT` | UINT(1<<17) OR 11 | yes | CANNOT-DISAGREE |
| 2 | `appapi/appapi.rb:47` | `TLV_TYPE_APPS_LIST` | STRING(1<<16) OR EXT+2911 | yes | CANNOT-DISAGREE |
| 3 | `extapi/adsi/adsi.rb:94` | `TLV_TYPE_ANY` | NONE(0) OR 0 = **0** | **no** | CANNOT-DISAGREE |
| 4 | `extapi/adsi/adsi.rb:147` | `TLV_TYPE_ALL` | **UNDECLARED** | **n/a** | **see ?6** |
| 5 | `stdapi/fs/dir.rb:84` | `TLV_TYPE_FILE_NAME` | STRING OR 1201 | yes | CANNOT-DISAGREE |
| 6 | `stdapi/fs/dir.rb:85` | `TLV_TYPE_FILE_SHORT_NAME` | STRING OR 1205 | yes | CANNOT-DISAGREE |
| 7 | `stdapi/fs/dir.rb:86` | `TLV_TYPE_FILE_PATH` | STRING OR 1202 | yes | CANNOT-DISAGREE |
| 8 | `stdapi/fs/dir.rb:89` | `TLV_TYPE_STAT_BUF` | COMPLEX(1<<31) OR 1221 | yes | CANNOT-DISAGREE |
| 9 | `stdapi/fs/dir.rb:91` | `TLV_TYPE_STAT_BUF32` | COMPLEX OR 1220 | yes | CANNOT-DISAGREE |
| 10 | `stdapi/fs/dir.rb:137` | `TLV_TYPE_FILE_PATH` | STRING OR 1202 | yes | CANNOT-DISAGREE |
| 11 | `stdapi/fs/dir.rb:140` | `TLV_TYPE_STAT_BUF` | COMPLEX OR 1221 | yes | CANNOT-DISAGREE |
| 12 | `stdapi/fs/dir.rb:142` | `TLV_TYPE_STAT_BUF32` | COMPLEX OR 1220 | yes | CANNOT-DISAGREE |
| 13 | `stdapi/mic/mic.rb:32` | `TLV_TYPE_AUDIO_INTERFACE_NAME` | STRING OR EXT+13 | yes | CANNOT-DISAGREE |
| 14 | `stdapi/webcam/webcam.rb:31` | `TLV_TYPE_WEBCAM_NAME` | STRING OR EXT+4 | yes | CANNOT-DISAGREE |
| 15 | `modules/post/multi/gather/memory_search.rb:161` | `TLV_TYPE_MEMORY_SEARCH_RESULTS` | GROUP(1<<30) OR 2651 | yes | CANNOT-DISAGREE |
| 16 | `modules/post/multi/gather/memory_search.rb:221` | same | same | yes | CANNOT-DISAGREE |
| 17 | `spec/.../packet_spec.rb:367` | `TLV_TYPE_STRING` | STRING OR 10 | yes | CANNOT-DISAGREE |
| 18 | `spec/.../packet_spec.rb:374` | `TLV_TYPE_ANY` | 0 | **no** | CANNOT-DISAGREE |
| 19 | `spec/.../packet_spec.rb:379` | `TLV_TYPE_BOOL` | BOOL(1<<19) OR 12 | yes | CANNOT-DISAGREE |
| 20 | `spec/.../packet_spec.rb:383` | literal `55555555` | computed literal | n/a | CANNOT-DISAGREE |

`[verified]` **Counts: CANNOT-DISAGREE 20 (subject to ?6), CAN-DISAGREE 0, UNKNOWN 0.**
**Closure: 20 + 0 + 0 = 20.**

**The distribution does NOT return one distinct verdict for a spurious reason.** The brief
warns that a uniform verdict should be treated as a broken classifier. Here the uniformity is
explained by ?3: **the masked comparison is not reachable from `get_tlvs` at all**, verified by
the 0-versus-6 call-site split. **The uniformity is a property of the code, and the code is
printed above so the reader can check it rather than trust the verdict.** `[verified]`

---

## ?5 Control 4(b) - one call site hand-checked

`[verified]` **Hand-checked: `stdapi/fs/dir.rb:84-91`.** `dir.rb` is 404 lines; the surrounding
method reads:

```ruby
   80:     request.add_tlv(TLV_TYPE_DIRECTORY_PATH, client.unicode_filter_decode(name))
   82:     response = client.send_request(request)
   84:     fname = response.get_tlvs(TLV_TYPE_FILE_NAME)
   85:     fsname = response.get_tlvs(TLV_TYPE_FILE_SHORT_NAME)
   86:     fpath = response.get_tlvs(TLV_TYPE_FILE_PATH)
   88:     if response.has_tlv?(TLV_TYPE_STAT_BUF)
   89:       sbuf = response.get_tlvs(TLV_TYPE_STAT_BUF)
   90:     else
   91:       sbuf = response.get_tlvs(TLV_TYPE_STAT_BUF32)
```

**The provenance determination is confirmed:** every argument is a bare literal constant, not
a parameter and not computed. `TLV_TYPE_FILE_NAME` resolves at `stdapi/tlv.rb:28` to
`TLV_META_TYPE_STRING | 1201`; **so the argument DOES carry overlay bits**, and my reading of it
as overlay-carrying is correct rather than assumed. `[verified]`

**This is the strongest available check of the classifier, and it PASSES.** Rows 5 through 9
of ?4 are the six arguments I hand-read, and their state assignment did not change on reading.
**It also demonstrates why the uniform verdict is not a classifier failure:** here the
arguments genuinely carry overlay bits, and they still CANNOT-DISAGREE - because the test they
are compared against is exact on both sides. **An overlay-carrying argument is harmless when
the comparison is `==`.**

---

## ?6 The one caller that is not a mask question - call site #4

`[verified]` `extapi/adsi/adsi.rb:147`:

```ruby
   146:     when TLV_TYPE_EXT_ADSI_DN
   147:       values = v.get_tlvs(TLV_TYPE_ALL)
```

`[verified]` **`TLV_TYPE_ALL` is declared NOWHERE in the corpus.** Basis: a byte-level search
for the token `TLV_TYPE_ALL` across **every file of every type** in the Metasploit tree returned
**exactly 1 file** - `adsi.rb` itself. A separate search for the declaration form
`^\s*TLV_TYPE_ALL[A-Z_]*\s*=[^>]` under `lib/rex/` returned only three rows, all of them
different constants: `TLV_TYPE_ALLOCATION_TYPE`, `TLV_TYPE_ALLOC_BASE_ADDRESS`,
`TLV_TYPE_ALLOC_PROTECTION` - **prefix collisions, not the name**.

`[verified]` **The file is live.** `extapi/extapi.rb:8` requires it, `:43` instantiates it, and
it is reachable from `lib/msf/core/post/windows/ldap.rb:139` and from post modules including
`modules/post/windows/gather/credentials/gpp.rb:230`. **This is not a dead file.**

`[verified]` **A sibling 53 lines above uses a different constant for the same intent:**
`:94 tlv_container.get_tlvs(TLV_TYPE_ANY)`. **`TLV_TYPE_ANY` is declared at `packet.rb:54` as
`TLV_META_TYPE_NONE | 0`, i.e. `0`.** `TLV_TYPE_ALL` is declared nowhere.

`[inferred]` **In Ruby, reading an undeclared constant raises `NameError`** - so this line
cannot return a value, and the `TLV_TYPE_EXT_ADSI_DN` branch of `extract_value` would raise
rather than produce a value. **That is an inference about Ruby semantics, not a measurement,
and no Ruby was run to confirm it.**

`[absence]` **Stated bound on the above: what could NOT be determined from bytes alone is
whether an enclosing namespace defines `TLV_TYPE_ALL` at load time.** The declaration search
covered the corpus on disk; it cannot cover a constant injected at runtime. **However, the
nesting chain is fully printed - `adsi.rb:3-8` opens `Rex` / `Post` / `Meterpreter` /
`Extensions` / `Extapi` / `Adsi` - and `extapi.rb` declares no TLV constants of its own, so no
enclosing lexical scope in this corpus supplies the name.** `[verified]`

`[inferred]` **`TLV_TYPE_ALL` appears to be a typo for `TLV_TYPE_ANY`**, written by someone
reaching for the same intent as `:94` in the same file. **I am not asserting intent**; I am
asserting that the only declared constant in this namespace that lexically resembles it is
`TLV_TYPE_ANY`, that `:94` uses that constant, and that `:147` does not.

### Why this is NOT the defect this task was commissioned to find

**The commissioned question was about mask disagreement. This is an undeclared constant.**
They are different failure classes: the first is a silent wrong-answer, the second is a hard
raise. **Reporting the second as if it answered the first would be exactly the species of
substitution this session keeps catching** - a plausible finding answering the wrong question.
**So it is reported separately, in its own section, under its own heading.**

`[absence]` **And its own reachability is NOT established.** The `TLV_TYPE_EXT_ADSI_DN` arm is
reached only when a received TLV has that exact type, which depends on the agent-side ADSI
implementation. **No agent-side C source is present in this corpus**, so whether a DN-typed
group is ever returned is **UNKNOWN**, and I stopped at that frame.

---

## ?7 Residuals, each with the frame where I stopped

| # | residual | stopped at | status |
| --- | --- | --- | --- |
| U1 | Does Ruby raise on `TLV_TYPE_ALL`? | Ruby semantics reasoned, not run. **No Ruby toolchain; not re-derived here.** | [inferred] |
| U2 | Is the `DN` arm ever reached? | agent-side C that would emit the TLV - **absent from corpus** | [absence] |
| U3 | Is `meta_type?` intended to be dead? | its 5 corpus occurrences read; no production caller found | [verified] negative |
| U4 | Was `TLV_TYPE_ALL` ever declared and later removed? | no version history in this checkout | [open] |

**U2 is the frame I stopped at, stated plainly: the producer of the DN-typed group is not in
this corpus, so the reachability of the branch is not determined and no claim is made about
it either way.**

---

## ?8 What this report changes

`[verified]`** One correction, by reference, to D121 T6:**` get_tlvs` does NOT mix an exact
short-circuit with a masked filter. It mixes nothing. Both tests are exact, and the masked
method `meta_type?` is unreachable from it.

`[inferred]` **The consequence for D121 T6's headline count:** D121 reported the functional
mask-dependent count as **1**. Corrected, **it is 0.** `get_tlvs` was the only functional
candidate and it is exact throughout; the other four non-masked tests were already shown to be
either display-only or numerically incapable of collision. **The mask-dependent risk surface in
the TLV layer is empty, not one.**

`[inferred]` **This strengthens rather than weakens D121 T6's method.** The step that found it
was the same step D121 T6 used on everything else: **read the callee, do not trust the call
site.** D121 T6 trusted a method NAME at `:639` and attributed it to the wrong definition.
**A name is not a definition; that is the same failure as Rule 20's "a named path is not a
census", one level down.**

---

## ?9 Census cardinalities, gathered

| census | input | result |
| --- | --- | --- |
| `get_tlvs` definitions | all `.rb` corpus-wide | 1 (`packet.rb:632`) |
| `get_tlvs` call sites | all `.rb` corpus-wide | 20 (19 production + 1 spec) |
| `meta_type?` occurrences | all `.rb` corpus-wide | 5 (1 def + 4 spec) |
| `meta_type?` production callers | all `.rb` corpus-wide | **0** |
| `.type?` call sites | meterpreter tree | 6 (1 TLV-layer, 5 other receivers) |
| `TLV_TYPE_ALL` files | every file, every type | **1 (the call site itself)** |
| `TLV_TYPE_ALL*` declarations | `lib/rex/` | 3, all different names |
| argument constants resolved | 13 distinct names | **12 resolved, 1 undeclared** |

*End of D129.*