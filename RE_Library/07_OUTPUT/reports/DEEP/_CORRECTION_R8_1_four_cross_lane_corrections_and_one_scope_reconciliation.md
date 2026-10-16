# _CORRECTION_R8_1_four_cross_lane_corrections_and_one_scope_reconciliation — a `#define` census cannot see a build property, and three lanes corrected each other before the Lead read either report

**Author:** `lead` · **Round 8** · **Class:** cross-lane reconciliation
**Not a numbered report. Claims no number. Edits no lane artefact.**
**SCOPE:** every D14x/D15x claim made in round 8 that a *different* lane's measurement contradicts or narrows.
**DEFINER SCOPE:** the four conflicting pairs, each re-measured here by the Lead against source or the pclntab operand directly.
**CONDITIONAL SCOPE:** reconciliation only. Where both statements are true over different populations, **both are recorded and neither is withdrawn.**
**COUNTED:** four correction pairs; the Lead re-measured three by direct source read and one by re-running the enumeration. No new corpus-wide census is claimed.

---

## 0. Why this file exists

**Three lanes independently corrected claims made by other lanes, and did so before the Lead had read either side.** That is the behaviour this round was designed to produce — Rule 33's corollary, *"confirming a cited site is not verifying a census"* — and it is the only reason the two most expensive errors of the round were caught.

**The Lead adds one item the lanes could not see**, because it is the Lead's own published error. It is §1.

I verified each pair myself rather than accepting whichever lane reported second. **In one case (§4) I found a third answer that neither lane had, and in one case (§2) I found the disagreement was not a disagreement at all.**

---

## 1. **LEAD-PUBLISHED ERROR — `TRANSPORT_HTTP` and `TRANSPORT_SMB` are LIVE, not dead**

**This is an error in a claim the Lead carried into this round's dispatch briefs.**

**THE CLAIM, as I have been repeating it:** *"havoc's `TRANSPORT_HTTP`/`TRANSPORT_SMB`/`DEBUG`/`AES256` are defined and select compiler-verified code; `SEND_LOGS`/`SVC_EXE`/`SHELLCODE`/`TESTING_MATCHING_ROUTINE` select nothing."*

**Read as a partition of eight into four-live and four-dead, the first clause is TRUE and the second clause is FALSE for two of its four members.**

**MEASURED — the defining site, direct read this round:**

```
01_SOURCE_c2\havoc\payloads\Demon\CMakeLists.txt
  L77: add_compile_definitions( TRANSPORT_HTTP )
  L78: add_compile_definitions( TRANSPORT_SMB )
  L79: add_compile_definitions( AES256 )
```

**`TRANSPORT_HTTP` and `TRANSPORT_SMB` are set by the build at `:77-78`.** They are **live**. The report that flagged them as dead read a `#define` census over source text and did not consult the build.

> ### THE GENERALISED RULE, and it is source-diver's phrasing: **A `#define` CENSUS OVER SOURCE TEXT CANNOT DETERMINE WHETHER AN ARM COMPILES. LIVENESS IS A BUILD PROPERTY.**

**Build-set for the Demon payload, measured: exactly five macros — `QT_NO_DEBUG_OUTPUT`, `DEBUG`, `TRANSPORT_HTTP`, `TRANSPORT_SMB`, `AES256`.**

**Survivors as candidate-dead: `SEND_LOGS`, `SHELLCODE`, `OBF_SYSCALL` — three, not four.**

**Detection-DB consequence, and it changes the artefact:** a rule keyed on `TRANSPORT_HTTP` or `TRANSPORT_SMB` as *"a macro that selects nothing"* would be keyed on **two macros that select compiled code**. The catalogue must key on the three survivors, and must not key on the five build-set macros in either direction.

**Status of the correction:** the Lead does not edit the prior report that carries the error. **The correction is written here and the old claim is named**, per the verify-only rule. **R-C-R8.1: locate every artefact repeating the four-dead partition and name it.** Not done in this file.

---

## 2. **`aiOperatorName` — NOT a disagreement. A SCOPE disagreement.**

**D145 (sliver-diver):** `aiOperatorName` **0 rows**.
**D140 (source-diver):** `aiOperatorName` **4 occurrences in source, definition at `:19`**.

**These look contradictory and are not.** Re-measured by the Lead, both directions:

```
01_SOURCE_c2\sliver\server\rpc\rpc-ai.go        13,553 B
  L19:  func (rpc *Server) aiOperatorName(ctx context.Context, fallback string) string {
  L86:  req.OperatorName    = rpc.aiOperatorName(ctx, req.OperatorName)
  L100: operatorName        = rpc.aiOperatorName(ctx, "")
  L144: req.OperatorName    = rpc.aiOperatorName(ctx, req.OperatorName)

client pclntab, literal substring count:
  aiOperatorName  ->  0
```

**The function EXISTS in source and is ABSENT from the client binary.** Both lanes are exactly right. **D145 scoped to the client pclntab; D140 scoped to the source tree.**

**Reconciliation: `absent` is not a property of a symbol. It is a property of a symbol IN A SCOPE.** D140's phrasing is the correct fix and is adopted: ***"Absent" must name its scope and show its enumeration.***

**No report is changed. Both stand, now with their scopes stated.** This is the third instance this session of a true-absence claim being read as a false one, or the reverse (§4 is the fourth).

---

## 3. **D143's `default:` arms — the classification correction, verified in full**

**D143 (covenant-diver):** 8 `default:` arms in the Covenant source; the fingerprint is *"fail-open."*
**D151 (covenant-deep):** **3 of those 8 are not dispatch arms at all** — they are the required behaviour of a JavaScript string-escaping encoder.

**THE LEAD RE-MEASURED IT, and D151 is right.** The definition:

```
GruntHTTP.cs:1248    public static string JavaScriptStringEncode(string value)
  :1275    switch ((int)c)
  :1277      case 8:  sb.Append("\\b"); ...
  :1280      case 9:  sb.Append("\\t");
  :1283      case 10: sb.Append("\\n");
  :1286      case 12: sb.Append("\\f");
  :1289      case 13: sb.Append("\\r");
  :1292      case 34: sb.Append("\\\"");
  :1295      case 92: sb.Append("\\\\");
  :1298      default: sb.Append(c);      <-- the arm in question
  :1299          break;
```

**The switch handles exactly seven values — `8, 9, 10, 12, 13, 34, 92`. Every other character, INCLUDING THE LETTER `a`, reaches the `default:`.**

> ### **A DEFAULT REACHED BY THE MAJORITY OF INPUT IS NOT AN ERROR PATH.** It is the encoder's normal case. `default: sb.Append(c);` is **correct and required** — it is what makes the function an encoder.

**D151's falsification test is the right kind: it can fail.** Had the switch covered all 256 `char` values, the `default:` would be unreachable and the claim would collapse. It covers seven.

**Same arm, four files, verified line-exact by the Lead:**

| file | encoder defined | `default:` | body |
|---|---:|---:|---|
| `Brute.cs` | 945 | **995** | 996 `sb.Append(c);` |
| `GruntBridge.cs` | 1099 | **1149** | 1150 `sb.Append(c);` |
| `GruntSMB.cs` | 1124 | **1174** | 1175 `sb.Append(c);` |
| `GruntHTTP.cs` | 1248 | **1298** | 1299 `sb.Append(c);` |

**So: the 8-arm count STANDS. Three of the eight were mis-attributed to dispatch.** The `default:`-arm population for *dispatch* purposes in these three files is **zero**, and the fail-open finding must rest on §4's structural evidence instead — which it does, and which is stronger.

### 3.1 The `−1` citation offset — settled, and it is a convention clash, not an error

**D151 corrected D143's citations as *"off by exactly −1"*: `Brute.cs:996`→995, `GruntBridge.cs:1150`→1149, and so on.**
**Measured: D143 cites the BODY line; D151 cites the `default:` line. Both name the same arm.**

**This is a citation-convention disagreement, not a defect, and it is recorded as such.** D143's citation is defensible — for a `switch` arm the *statement* is often meant. **The rule this suggests, and it is a small one: A `case`/`default` ARM HAS TWO LINES, AND A CITATION MUST SAY WHICH.** `:1298` is the label; `:1299` is the statement; `:1298-1299` is unambiguous.

**No number in either report is affected.**

---

## 4. **`0xDEADBEEF` — both lanes right, over different populations; and the Lead found the reconciliation neither had**

**D140 (source-diver):** *"0xDEADBEEF's 55 metasploit hits are `modules\exploits` 22 + `data\templates` 18 … **ZERO in `lib\msf\core` or `lib\rex`**."* Retracted from the shared-magic table on that basis.
**LEAD'S FIRST COUNT:** **9** matches whose path contains `lib\msf` or `lib\rex`.

**Both numbers are correct.** The reconciliation, measured:

```
DEADBEEF matches corpus-wide, metasploit         : 121
  whose path contains lib\msf or lib\rex         :   9
    ... of those, in a spec/ directory            :   9   <-- ALL NINE
    ... of those, PRODUCTION (no spec in path)    :   0   <-- source-diver's figure
```

**All 9 are test fixtures:**

```
spec\lib\msf\core\exploit\remote\mongodb_spec.rb:40       [0xdeadbeef].pack('V')   # requestID
spec\lib\msf\core\exploit\remote\smb\relay\kerberos\server_client_spec.rb:137   session_id = 0xdeadbeef
spec\lib\rex\proto\dhcpv6\packet_spec.rb:16 / :58 / :119  0xdeadbeef as an IAID fixture
spec\lib\rex\proto\kerberos\kerberos_logger_subscriber_spec.rb:733/770/791/881  Key: deadbeef
```

**`spec/lib/msf/...` is a test file whose PATH contains `lib/msf`. `lib/msf/...` is production code.** A path-substring test and a production-code test **differ by exactly the `spec`\ directory, and the difference here is 9 versus 0.**

> ### **SCOPE — a path-substring test is not a code-role test.** This is Rule 33's own failure mode re-arriving through a *filter* rather than a header.

**D140's correction is UPHELD: `0xDEADBEEF` is not a shared C2 magic.** Its metasploit presence is alignment filler in exploit payloads and test fixtures. The retraction was correct and the Lead's 9 does not disturb it.

### 4.1 And the Lead's own probe defect, disclosed

**My second attempt at this count reported `0` and was BROKEN** — I filtered `$_.Path` on strings a previous pipeline had already rewritten, so `Path` was absent and the predicate matched nothing. **A zero that agreed with source-diver was the most dangerous possible output here: it would have "confirmed" a lane's correction using a probe that never ran.**

**What caught it:** I had already printed `9` from the correct probe, so a second probe printing `0` on the same operand was self-contradictory. **Without the earlier number I would have had one zero and no reason to doubt it.** This is `Rule 37`'s family again — **the Lead's own instruments, not the lanes'.**

---

## 5. Correction tally

| # | claim | source | Lead's re-measurement | outcome |
|---|---|---|---|---|
| 1 | `TRANSPORT_HTTP`/`TRANSPORT_SMB` dead | **Lead-published** | **live**, `CMakeLists.txt:77-78` | **LEAD ERROR — corrected here** |
| 2 | `aiOperatorName` absent | D145 vs D140 | present in source, 0 in client | **both true — SCOPE** |
| 3 | 3 of 8 `default:` arms are encoder arms | D143 vs D151 | **verified, four files, line-exact** | **D151 UPHELD** |
| 3a | citations off by −1 | D151 vs D143 | body-line vs label-line | **convention clash** |
| 4 | `0xDEADBEEF` zero in `lib/msf`/`lib/rex` | D140 vs Lead | 9 path-matches, **all in `spec`\**, 0 production | **BOTH TRUE — SCOPE** |

**Of five items: one Lead error, one lane correction upheld, one narrowed to a convention, and two dissolutions into scope.**

---

## 6. The pattern, stated once

**Three of these five were not disagreements.** They were **two true statements about two populations, made without printing the population.** `aiOperatorName` (binary vs source) · `0xDEADBEEF` (path-substring vs code-role) · the citation offset (label line vs statement line). **Only one item — §1 — is an error, and it is the Lead's, and its cause is a census that could not see the property it was asked about.**

**The lanes that found these did it by asking *where does the match live* rather than *how many matches are there.*** That question has now caught six separate defects across four lanes this round.

**And the counter-example is instructive:** the one item that was a real error (§1) **was invisible to every lane**, because **no lane had a reason to re-measure a build property they had been told by the Lead was a text property.** ***An error in the question is not detectable in the answers.***

---

*End of reconciliation. No lane artefact edited. No number claimed. Forward references: R-C-R8.1 (enumerate artefacts repeating the four-dead partition) · the `spec`\ vs `lib`\ scope lesson belongs in Rule 33's scope clause.*

**Rule 36 self-check, disclosed:** the first draft of THIS file contained **four** Rule-36 violations — three lines, four spans — at the very lines written to explain the `spec`\ versus `lib`\ distinction. **Fixed in place to the `spec`\ form (separator outside the span).** Left as a note rather than silently corrected: **a reconciliation record about scope confusion, whose own first draft confused its own spans, is the fifth instance this round of the defect surviving inside the document that names it.**
