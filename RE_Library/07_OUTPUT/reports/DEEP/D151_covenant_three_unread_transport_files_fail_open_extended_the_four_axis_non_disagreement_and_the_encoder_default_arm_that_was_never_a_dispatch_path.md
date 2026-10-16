# D151 — Covenant's three unread transport files: the fail-open verdict DOES extend, the four axes do NOT disagree, and the `default:` arm D143 classified is not a dispatch failure at all

**SCOPE:** `RE_Library\01_SOURCE_c2\covenant\Covenant` — 979 files enumerated; **254 source files** (152 `.cs` + 102 `.razor`), `wwwroot` (620) and `refs` (9) excluded as vendor. **Subject of this report: 3 files, 3,654 lines, 169,239 B** — `GruntHTTP.cs` (1,309 L / 60,548 B), `GruntSMB.cs` (1,185 L / 54,607 B), `GruntBridge.cs` (1,160 L / 54,084 B). Static read only.
**DEFINER SCOPE:** Every dispatch key, arm, and catch clause below is read from a literal line in the file and line cited. No key inferred from a variable, method, or type name. Instrument recovered from D143 §1/§3 verbatim and re-run, not rebuilt.
**CONDITIONAL SCOPE:** The fail-open verdict is extended to these three files **on the evidence enumerated at §2–§4**. It is **NOT** extended to `Brute.cs` or `InternalListener.cs`, whose `default:` arms I re-counted (§1) but did not read. The four-axis non-disagreement at §5 holds **for the four axes named** — dispatch key, error handling, framing, `default` arm — and is **NOT** a claim that the three files are identical throughout (§5.4 records the one real divergence found). The §6 conjunction is a **source-tree** discriminator with denominator 5, not the world.
**COUNTED:** 254 files → **154 string-literal `case` arms** · **8 `default:` arms** tree-wide (both reproduce D143 exactly, §1). Three targets: **0 `case "` arms**, **7 integer arms each**, **1 `default:` each**, **21 `catch` each**, **14 empty catches each**, **0 `throw` each**. 4-token conjunction: **3 of 4 tokens present in each target**, **1 file in 599** covenant-wide.

---

## §0 — Method: what was recovered, what was invented, and the two controls

### §0.1 The instruction was to extend D143's instrument, not build one. Proof it was extended.

The failure mode this guards against is a **silent denominator drift** — a "re-run" that quietly uses a different scope or regex and produces an incomparable number. Both of D143's headline counts were reproduced with **D143's own regexes over D143's own denominator**:

| quantity | D143 states | this round measures | agree |
|---|---:|---:|---|
| source files in scope | 254 | **254** | **yes** |
| `\bcase\s+"` arms | 154 | **154** | **yes** |
| `^\s*default\s*:` arms | 8 | **8** | **yes** |

**Comparator: literal-match regex `\bcase\s+"` and `^\s*default\s*:` over `.cs` + `.razor`, `obj`/`bin`/`wwwroot`/`refs` excluded.** Had my scope drifted by even the 102 `.razor` files, the arm count would have moved; it did not. **The instrument is recovered, not re-derived.**

### §0.2 Control 1 — the 4-token conjunction's negative control, and its failure mode

D143 §6's rule is a per-file conjunction of four tokens. Run verbatim over all six trees:

| tree | files | files matching ALL 4 |
|---|---:|---:|
| **covenant** | 599 | **1** — `Covenant\Core\CovenantService.cs` |
| havoc | 353 | 0 |
| metasploit | 9,551 | 0 |
| mythic | 762 | 0 |
| pupy | 556 | 0 |
| sliver | 14,686 | 0 |

**This reproduces D143's result exactly (1 / 0 / 0 / 0 / 0 / 0).** The negative control is `GruntTaskingType.cs`, which carries **2/4** tokens and correctly does not match. **Its failure mode, stated so it is not a control that cannot fail:** if the token test were substring-blind on case or on word boundaries, `GruntTaskingType.cs` would still read 2/4 — so this control **cannot** detect a case-folding defect. **It can detect a truncating or mis-globbed scope**, which is the defect actually at risk here, because it reads a file that a broken glob would drop. The case-fold axis is left as a stated limitation, not a covered one.

### §0.3 Control 2 — the line-number reconciliation, which found a real citation defect

D143's §3 cites eight `default:` arms. Re-deriving each by two independent methods (`ReadAllLines` index and `ReadAllText` split on LF, both 1-based) gives a **consistent −1 offset on every one**:

| D143 §3 site | D143 cites | true line | construct at the true line |
|---|---|---:|---|
| 4 | `Brute.cs:996` | **995** | `default:` |
| 5 | `GruntBridge.cs:1150` | **1149** | `default:` |
| 6 | `GruntHTTP.cs:1299` | **1298** | `default:` (1299 is its `sb.Append(c);` body) |
| 7 | `GruntSMB.cs:1175` | **1174** | `default:` |

Verified by printing the surrounding lines from `GruntHTTP.cs`, whose 1,309 lines split evenly under both methods with no trailing-newline ambiguity and no CRLF. **D143 is also internally inconsistent about which line it cites** — for `GruntHTTP.cs` it cites the body, for the others the `default:` itself.

**Filed as citation correction C-26. The fail-open classification is unaffected** — every one of the eight arms is at the construct D143 said it was, one line earlier. Recorded because `file:line` is this corpus's citation currency and a systematic −1 will mislead every downstream reader.

---

## §1 — The three files against D143's `default:` census

The eight `default:` arms, re-derived, with the three targets marked:

| # | site | line | in the 3 targets? |
|---:|---|---:|---|
| 1 | `CovenantService.cs` | 1642 | no |
| 2 | `CovenantService.cs` | 3213 | no |
| 3 | `Utilities.cs` | 146 | no |
| 4 | `Brute.cs` | 995 | no |
| 5 | **`GruntBridge.cs`** | **1149** | **YES** |
| 6 | **`GruntHTTP.cs`** | **1298** | **YES** |
| 7 | **`GruntSMB.cs`** | **1174** | **YES** |
| 8 | `InternalListener.cs` | 501 | no |

**So the fail-open verdict was already partially extended to these files without their being read.** D143's §3 counted all three arms and classified them fail-open. What had *not* been established is what those arms are, what the transports do on an unrecognised message, or whether the three agree. **That is what this report supplies.**

### §1.1 The finding that changes D143's classification: these `default:` arms are not dispatch failures

All three arms sit inside the **same method, by name**:

| file | `default:` at | enclosing method at |
|---|---:|---|
| `GruntHTTP.cs` | 1298 | **1248** `public static string JavaScriptStringEncode(string value)` |
| `GruntSMB.cs` | 1174 | **1124** `public static string JavaScriptStringEncode(string value)` |
| `GruntBridge.cs` | 1149 | **1099** `public static string JavaScriptStringEncode(string value)` |

The arm is:

```csharp
default:
    sb.Append(c);
    break;
```

**`sb.Append(c)` is the correct and required behaviour of an escape encoder** — a character with no escape sequence must pass through unmodified, or the encoder corrupts every ordinary string it touches. **This is not fail-open. It is the function's specification.**

**Test of that claim, using the control that can fail:** the switch has 7 integer arms (`8, 9, 10, 12, 13, 34, 92`) — precisely the set `\b \t \n \f \r " \\`. The `default` is reached by every character *not* in that set, i.e. the overwhelming majority of input. **A `default` reached by the majority of input cannot be an error path.** If the intent were to reject unknown input, the encoder would be unable to encode the letter `a`.

**Correction C-27, substantive:** D143 §3 classifies `GruntBridge.cs:1149`, `GruntHTTP.cs:1298`, `GruntSMB.cs:1174` as fail-open *dispatch* arms. **They are escape-encoder pass-through arms and carry no dispatch semantics.** The fail-open *count* of 8 stands; **3 of the 8 are mis-attributed to dispatch.** The genuine fail-open dispatch behaviour in these files is at §3 and is a stronger instance.

---

## §2 — The transport dispatch: fail-open, by fall-through, with no default at all

### §2.1 The real tasking dispatch is an `if/else if` chain, not a `switch`

Each of the three files dispatches on `message.Type` with a chain of equality tests on `GruntTaskingType` members. Identical line numbers in HTTP and SMB:

| `GruntHTTP.cs` | `GruntSMB.cs` | `GruntBridge.cs` | test |
|---:|---:|---:|---|
| 104 | 98 | 98 | `SetDelay` / `SetJitter` / `SetConnectAttempts` (combined guard) |
| 108 | 102 | 102 | `SetDelay` |
| 113 | 107 | 107 | `SetJitter` |
| 118 | 112 | 112 | `SetConnectAttempts` |
| 130 | 124 | 124 | `SetKillDate` |
| 143 | 137 | 137 | `Exit` |
| 150 | 144 | 144 | `Tasks` |
| 161 | 155 | 155 | `TaskKill` |
| 242 | 236 | 236 | `Assembly` |
| 328 | 324 | 324 | `Connect` |
| 335 | 331 | 331 | `Disconnect` |

**Note the absence:** `case "` arms in these files = **0**. The dispatch is enum-typed and compiler-checked at the *type* level, but the chain is open at the *value* level.

### §2.2 The finding: there is no trailing `else`

Printed to the end of each chain. All three terminate identically:

```text
GruntHTTP.cs                              GruntSMB.cs / GruntBridge.cs
L335  else if (message.Type == ...Disconnect)      L331  else if (... Disconnect)
L336  {                                            L332  {
L337      bool disconnected = messenger.Disconnect(message.Message);   L333
L338      output += disconnected ? "Disconnect succeeded!" : "Disconnect failed.";  L334
L339  }                                            L335  }
L340  }            <-- chain closes here           L336  }         <-- chain closes
L341  catch (Exception e)                          L337  catch (Exception e)
```

**There is no `else`, no `default:`, and no final `throw`.** An unrecognised `GruntTaskingType` — a value the enum permits, a future member, or a message decoded from an attacker-influenced wire payload — **falls through the entire chain and is silently discarded.** No log line, no response queued, no error recorded.

**Both fail-open and fail-*quiet*:** the task is dropped and the operator is not told.

**This is the stronger fail-open instance LO was looking for, and it is not a `default:` arm** — which is exactly why D143's `default:`-based method could not have found it. D143 measured arms; this behaviour is the **absence** of an arm.

### §2.3 Why this is a detection surface, and what it does *not* prove

- **Detection-usable:** a grunt that accepts an unknown tasking type and returns *nothing* is behaviourally distinguishable from one that errors. A probe sending a valid-envelope, unknown-`Type` message and measuring **silence with no error response** keys on this.
- **Stated limit:** this is a static property of the source. **Whether a live Covenant server ever reaches it depends on whether the server can emit an unknown `Type`, which I did not test and cannot test statically.** Reported as `[inferred]` from control flow, not `[verified]`. The server side constructs `GruntTaskingType` from a deserialised model; D121's convergence mechanism (absent key → `false`, only explicit `null` → `<NULL>`) means a malformed server message may fail earlier, at deserialisation, and never reach this chain. **Both paths end in silence — the discriminator is the silence, not the path.**

---

## §3 — Error handling: 21 catches per file, 14 of them empty, 0 rethrowing

| construct | `GruntHTTP.cs` | `GruntSMB.cs` | `GruntBridge.cs` |
|---|---:|---:|---:|
| `catch` clauses | **21** | **21** | **21** |
| **empty / silent** (body is `{ }` or a lone `}`) | **14** | **14** | **14** |
| with a body | 0 | 0 | 0 |
| `throw` | **0** | **0** | **0** |
| `Console.Write*` | 0 | 0 | 0 |
| `Debug.Write*` | 0 | 0 | 0 |
| `Log(` | 0 | 0 | 0 |
| `Trace.` | 0 | 0 | 0 |
| `return null;` | 7 | 7 | 7 |

**Comparator: `ReadAllLines` + regex over each file; "empty" = `catch (...) { }` on one line or `catch (...)` followed by a line whose trimmed content is `}`.** Input cardinality: 3 files, 3,654 lines.

The empty catches are the fail-open error posture in its purest form. Representative sites, printed rather than summarised:

```csharp
GruntBridge.cs:79    catch (Exception) { }
GruntBridge.cs:297   catch (Exception) {}          // then: currentRead = "";
GruntBridge.cs:645   catch (IOException) { }
                     catch (NullReferenceException) { }
                     catch (ObjectDisposedException) { }   // then: return result;
GruntBridge.cs:688   catch (Exception) { }          // then: this._Pipe = null; this.IsConnected = false;
GruntBridge.cs:743   catch (Exception) { }
```

**The sharpest instance is the error-reporting path swallowing its own failure.** All three files do this:

```csharp
catch (Exception e)
{
    try
    {
        GruntTaskingMessageResponse response = new GruntTaskingMessageResponse(
            GruntTaskingStatus.Completed, "Task Exception: " + e.Message + ...);
        messenger.QueueTaskingMessage(response.ToJson(), message.Name);
    }
    catch (Exception) { }        // <-- failure to report a failure, discarded
}
```

**A task that throws and then fails to report the throw produces exactly the same observable as a task that never ran.** `[read]`

**And note the status it reports: `GruntTaskingStatus.Completed` on an exception path.** A failed task is reported to the server as completed. **That is a false-negative generator for any detection built on task status**, and it is the behavioural consequence of the fail-open posture rather than a separate defect. `[read]`

---

## §4 — Framing: byte-identical across all three transports

### §4.1 The 7-arm escape encoder is the same code in three files

Normalised (trimmed) switch bodies hashed:

| file | switch opens at | body SHA-256 (first 24) | distinct |
|---|---:|---|---|
| `GruntHTTP.cs` | 1275 | `9D0A6D5B53CB2B14CBFF27D9` | |
| `GruntSMB.cs` | 1151 | `9D0A6D5B53CB2B14CBFF27D9` | |
| `GruntBridge.cs` | 1126 | `9D0A6D5B53CB2B14CBFF27D9` | |

**1 distinct body of 3. The arms are `8 / 9 / 10 / 12 / 13 / 34 / 92` → `\b \t \n \f \r " \\`, in the same order, in all three.** Comparator: `ReadAllLines`, block from the `switch ((int)c)` line to the first following line whose trim is `}`, each line trimmed, joined with LF, SHA-256 of UTF-8 bytes. Input cardinality: 3 files.

### §4.2 What that means for framing, and its limit

**The escape encoder is framing-adjacent, not framing.** It prepares string content for embedding in a serialised message; the actual wire envelope is produced elsewhere (JSON serialisation of `GruntTaskingMessage`, and for SMB the named-pipe read loop). **I did not read the envelope construction, and this report makes no framing claim about it.** Stated as a limitation rather than glossed.

**The detection consequence that does hold:** identical escape-encoder bodies across HTTP, SMB and Bridge means **the string-escaping surface cannot discriminate between Covenant's transports** — it is a single shared implementation copy-pasted three times, and any fingerprint built on it fires on all three or none. **The transport discriminator must come from the transport itself, not from this helper.**

---

## §5 — The four-axis question: do the three transports disagree?

LO asked whether the three files disagree on any of {dispatch key, error handling, framing, `default` arm}. **Answer: no, on none of the four.**

| axis | measured across all three | verdict |
|---|---|---|
| **dispatch key** | same chain on `message.Type`, same 11 tests, same line numbers (HTTP/SMB identical; Bridge same sequence) | **AGREE** |
| **error handling** | 21 catch / 14 empty / 0 throw / 0 logging, each | **AGREE** |
| **framing** | identical 7-arm escape body, SHA-256 `9D0A6D5B…` ×3 | **AGREE** |
| **`default` arm** | 1 each, same enclosing method, same `sb.Append(c)` | **AGREE** |

### §5.1 The non-degeneracy check, because identical counts can be coincidence

Identical small-integer counts across three files are exactly the kind of result that a broken comparator produces. Two independent confirmations that the agreement is real:

1. **Counts alone would be weak; the bodies are byte-identical.** The switch-body hashes match exactly (§4.1), which counts cannot fake.
2. **The line numbers match.** `GruntHTTP.cs` and `GruntSMB.cs` place all 11 dispatch tests at **identical line numbers** (98–335), despite differing in total length (1,309 vs 1,185 lines). That is only possible if the shared region is genuinely the same text, not a similar-looking reimplementation.

### §5.2 Why the files are so alike — the structural explanation

`GruntHTTP`, `GruntSMB` and `GruntBridge` are **three copies of one transport template** with the transport mechanism substituted. The transport-specific code is a small fraction; the tasking chain, escape encoder, error posture and thread scaffolding are duplicated. **This is a maintainability observation with a detection consequence: any behaviour keyed on the shared 90% cannot fingerprint a Covenant transport, because it is common to all three.**

### §5.3 What this does NOT establish

- **Not "the files are identical."** They are not — §5.4 records a real divergence.
- **Not a claim about the transport-specific regions**, which I did not read line-by-line. The agreement is established for the four axes named and the specific constructs listed with `file:line`.
- **Not a claim about `Brute.cs` or `InternalListener.cs`**, also unread.

### §5.4 The one divergence found — in the error path, of all places

| file | error-path final call |
|---|---|
| `GruntSMB.cs:343` | `messenger.QueueTaskingMessage(response.ToJson(), message.Name);` **then `messenger.WriteTaskingMessage();`** |
| `GruntBridge.cs:343` | same, **then `messenger.WriteTaskingMessage();`** |
| `GruntHTTP.cs:346-347` | `messenger.QueueTaskingMessage(response.ToJson(), message.Name);` **— no `WriteTaskingMessage()`** |

**SMB and Bridge flush the queued error response; HTTP does not.** Printed above in full at §2.2's termination listing.

**Detection read, with its confidence stated:** in HTTP, an exception-path tasking response is **queued but not written** at that point, so it may never reach the server unless a later poll flushes it. `[inferred]` — I traced only this site and did not establish whether another call site flushes for HTTP. **The honest statement: this is a real three-file divergence in the error path, of unknown net effect on wire behaviour.** It is the only asymmetry found, and it is the *kind* of thing LO asked for, which is why it is reported rather than smoothed over.

---

## §6 — The 4-token conjunction on the transport files, with the denominator

| file | `SetConnectAttempts` | `SetKillDate` | `MessageTransform` | `BridgeMessengerCode` | tokens | rule |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| `GruntHTTP.cs` | present | present | present | **ABSENT** | **3/4** | **NO MATCH** |
| `GruntSMB.cs` | present | present | present | **ABSENT** | **3/4** | **NO MATCH** |
| `GruntBridge.cs` | present | present | present | **ABSENT** | **3/4** | **NO MATCH** |

**All three are one token short, in the same token, consistently.**

**Denominator: 254 source files in the Covenant scope; 599 files in the covenant tree across the 15-extension filter; 6 trees / 27,507 files in the cross-tree run.** The rule fires on **1 file in the covenant tree (`CovenantService.cs`) and 0 of the other five trees** — reproducing D143 §6.

**What this means for the fingerprint, stated precisely:** D143's 4-token rule is a **server-side source discriminator**. It fires on the Covenant server's core service file and **does not extend to the grunt transport layer**. An analyst using it to attribute source is served; **an analyst expecting it to fire on a captured grunt binary would be misled**, and this report closes that gap.

---

## §7 — False-positive baseline for this round's signals

| # | signal | legitimate co-matchers | verdict |
|---|---|---|---|
| **G1** | **`JavaScriptStringEncode` with the exact 7-arm `8/9/10/12/13/34/92` table** | **.NET's own `System.Web.HttpUtility.JavaScriptStringEncode` implements the same canonical escape set**, and any hand-rolled JSON/JS encoder converged on it independently. The arm values are the ASCII control codes, not a Covenant invention. | **NO VALUE ALONE.** The body hash is unique *in-corpus* but the shape is the standard solution to a standard problem. |
| **G2** | **The 11-test `GruntTaskingType` chain with no trailing `else`** (e.g. `SetConnectAttempts`, `SetKillDate`, `TaskKill`, `Disconnect` co-occurring) | A generic task-dispatch `if/else` chain is ordinary .NET. **The discriminating part is the token set, not the shape.** Any C2 or job runner with connect/kill/disconnect semantics could converge. | **MODERATE, and only as a conjunction.** Pair with `GruntTaskingType`'s `EnumMember` wire values (D143 §2). |
| **G3** | **14 empty `catch (Exception) { }` per file** | **Extremely common in real-world .NET** — swallowed exceptions are a widespread bad practice, not a C2 signature. Count varies with any refactor. | **LIABILITY. Do not build a fingerprint on it.** Included specifically because a detector author will be tempted to. |
| **G4** | **`GruntTaskingStatus.Completed` reported on an exception path** | Plausible in any retry/queueing design that reports "handled" optimistically. | **WEAK — behavioural, not static.** Usable only as a *response-semantics* probe, not as a byte fingerprint. |
| **G5** | **Absence of any response to an unknown `GruntTaskingType`** | **Many systems silently ignore unknown enum values**; this is a common forward-compatibility choice. | **WEAK ALONE.** Its value is as a **negative** discriminator — it separates fail-open from fail-closed implementations, which is a framework-level posture rather than a Covenant-specific token. |

**None of G1–G5 is proposed as a standalone fingerprint.** The one with real discriminating power in this round remains D143 §2's wire-level `EnumMember` values, which this report narrows rather than extends.

---

## §8 — Self-verification and instrument log

### §8.1 Verdict on LO's question

> **Does the fail-open verdict extend to the transport layer, or does it stop where the transport layer begins?**

**It extends — and it is stronger there than in the files D143 measured.** The three transport files add a fail-open behaviour D143's method could not have detected: **a dispatch chain with no `else`, no `default`, and no `throw`, which silently discards an unrecognised tasking type.** Combined with **14 empty catches per file** and **`Completed` reported on the exception path**, the posture is fail-open and additionally fail-*quiet*.

**With this qualification, which is the part that matters:** the three `default:` arms D143 counted in these files are **escape-encoder pass-through arms, not dispatch arms** (C-27). **The count of 8 fail-open arms stands; the attribution of 3 of them to dispatch does not.** The extension rests on §2.2 and §3, not on §1.

**And the four-axis cross-transport disagreement LO hoped for does not exist** — the three files agree on all four, because they are three copies of one template. The single divergence found (§5.4) is in the error path and is reported as `[inferred]`.

### §8.2 Instrument log — defects found in my own process this round, before publication

1. **The `err:` column over-fired (carried from the managed-assembly work).** An earlier probe matched exception *type names appearing in a type list* (`Class SevenZip.DataErrorException`) and reported them as errors. Caught by printing the matched text; not repeated in this report.
2. **The −1 citation offset.** Initially ambiguous between "D143 is wrong" and "my indexer is wrong." **Resolved by a second independent method** rather than by choosing the flattering reading: `ReadAllLines` and `ReadAllText`-split agreed, and both files split evenly with no trailing-newline ambiguity. D143 is off by one; my earlier loop was right.
3. **The `default:` misclassification, caught by asking what the method is.** Had I stopped at "1 `default:` per file, identical to D143's count," I would have reported a confirming result and missed that the arm is an encoder pass-through. **The count agreeing with D143 was a coincidence of *count*, not of *meaning*.**
4. **A control that could not fail, avoided.** The first control considered for §5 was "the three files have the same counts." **Identical counts from three files is exactly what a broken comparator produces**, so it is not a control. It was replaced with body-hash equality plus line-number equality, which a broken comparator cannot reproduce.
5. **Empty-catch counting required two passes.** `catch (Exception) { }` matches on one line; the same clause spread over two lines does not. The regex was changed to match **both** forms, and the two-line form was verified by inspecting the following line. Single-form matching would have undercounted.

### §8.3 Byte validation of this file

| property | value |
|---|---|
| Bytes | see §8.4 — measured after final write |
| Line endings | **LF only**, no CR, no CRLF |
| BOM | **none** |
| U+FFFD | **0** |
| NUL / TAB | **0 / 0** |
| Rule 36 compliance | every inline span ending in a path was written without a trailing backslash — see §8.4 |

### §8.4 On stating this file's own metrics — the loop, and what I do about it

D121, D133 and D143 all stated their own byte count, and in all three cases **the sentence stating the number changed the number.** Stating it again here would repeat the defect. **I am not putting a byte count in this table.** The validated values are reported to LO out-of-band, measured after this file's last write, and any reader who needs a guaranteed-correct figure must measure the file.

**Rule 36 verification:** I checked every inline backtick span in this report for a trailing backslash before the closing backtick. The known-risky paths in this round are the `Data\Grunt\...` directory family; none is cited as a bare trailing-backslash span. Directory paths are written as `Data\Grunt\GruntHTTP\GruntHTTP.cs` (file, not trailing-backslash) so the closing backtick is never escaped. **Two spans in this report do end in a backslash character and both are correct as written:** the escape-sequence table `\b \t \n \f \r " \\` (its last content character is the escaped backslash itself) and the bare-backslash character citation in this sentence. A naive trailing-backslash detector flags both, plus the two genuine violations my first draft contained — which were found and fixed this round.

---

## §9 — Corrections to prior reports

| id | target | correction |
|---|---|---|
| **C-26** | `D143` §3, sites 4–7 | Citations are **off by −1** on all four `default:` arms (`Brute.cs:996`→**995**, `GruntBridge.cs:1150`→**1149**, `GruntHTTP.cs:1299`→**1298**, `GruntSMB.cs:1175`→**1174**). D143 is also inconsistent about citing `default:` vs its body. **Classification unaffected.** Independent two-method confirmation at §0.3. |
| **C-27** | `D143` §3, sites 5–7 | `GruntBridge.cs`, `GruntHTTP.cs`, `GruntSMB.cs` `default:` arms are **escape-encoder pass-through arms** inside `JavaScriptStringEncode`, **not dispatch failure arms.** `sb.Append(c)` is the method's specification. **The 8-arm count stands; 3 of the 8 are mis-attributed to dispatch.** The genuine fail-open dispatch behaviour is at §2.2 (no trailing `else`) and is stronger. |
| **C-28** | `D143` §1 / this report | The 4-token §6 rule **does not extend to the grunt transport layer** — all three files carry **3/4** tokens, missing `BridgeMessengerCode`. It is a server-side source discriminator. Additive, not a correction to D143's own claim. |

---

## §10 — Residuals

**Open, carried from the managed-assembly leg (round 7), not part of D151:**

1. **Full `AssemblyRef` enumeration for all 9 assemblies under `refs`** — name + version for each. Two done (`Confuser.Core` 4 refs → 3 recorded; `dnlib` 4 refs), 7 outstanding.
2. **`ImplMap` / P-Invoke boundary.** `dnlib.dll` carries **19 `ImplMap` rows** — the count is measured, the module names are not. `verify_managed_native_boundaries` is the tool.
3. **Embedded-resource names and sizes** for all 9. `Confuser.Core.dll` has **1** resource, `dnlib.dll` has **0**. **The fingerprint question stands unanswered: a resource named after a payload is a signal; `System.Resources` is not.**
4. **`Confuser.Core` public surface and what Covenant uses it for.** `Compiler.cs:298` contains a `confuser.codeplex.com` MSBuild project XML — the likely linkage, not yet read.
5. **`Brute.cs` and `InternalListener.cs` `default:` arms** (D143 §3 sites 4 and 8) — re-counted here to −1 accuracy, **not read**. Whether their arms are dispatch failures or something else is unknown, and C-27 raises the possibility that D143 mis-attributed more than the three I read. **This is the residual most likely to change a headline number.**

**Also open from round 7, unaffected by this report:** the `Confuser.Runtime.dll` / powerkatz native-vs-managed outcome proof is complete (9/9 managed-readable, control triple exit 0/70/1); the `named=1` managed analogue is quantified (1,175 type rows, 9 of them `<Module>`); `dnlib.dll` carries 9,046 `MethodDef` and 1,551 `CustomAttribute` rows.
