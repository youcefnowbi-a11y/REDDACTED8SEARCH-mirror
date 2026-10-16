# D158 — The D143 arm re-attribution sweep: every `default:` arm classified by what it selects, the encoder family is FOUR not three, and D143's method could not see 57 of the covenant's 65 switches

**SCOPE:** `RE_Library\01_SOURCE_c2\covenant\Covenant` — 979 files enumerated, **254 source files** (152 `.cs` + 102 `.razor`), `wwwroot` (620) and `refs` (9) excluded as vendor. Static read only. **Subject: all 8 `default:` arms tree-wide, and all 65 `switch` statements tree-wide.**
**DEFINER SCOPE:** each arm's enclosing method is read from the literal declaration line above it and cited by line. Each arm's class is decided by **what the arm selects** — a handler, a transform, or a value — not by the presence of a `default:` token, not by the enclosing file, and not by a method name. Every switch is brace-matched, not window-truncated.
**CONDITIONAL SCOPE:** the corrected arm population and the DISPATCH subpopulation hold **for the covenant tree at the 254-file denominator**. The §5 method-limit verdict is a claim about **the instrument D143 used**, not about D143's competence and not about any other tree. Enum-family switches (44 of the 65) are classified as a family, not read arm by arm; their exhaustive-case property is D143 §4's finding, reproduced here only as a count.
**COUNTED:** 254 files → **8 `default:` arms** (reproduces D143 and D151 exactly) · **65 `switch` statements** (new) · **57 switches with no `default:`** (new) · **154 string-literal `case "` arms** (reproduces D143 exactly) · **4 encoder arms** · **3 DISPATCH arms** · **1 OTHER arm** · **13 non-enum switches lacking a `default:`** · 5 predictions made before execution, 5 confirmed.

---

## §0 The brief's premise, checked first, and one part of it is false

The brief states: *"the other `default:` arms in `Brute.cs` and `InternalListener.cs` are unread, re-counted only."*

`[verified]` **There are no other `default:` arms in either file.** `Brute.cs` contains **exactly one** (`:995`) and `InternalListener.cs` contains **exactly one** (`:501`). Both were already enumerated by D143 and both are read in this report. The complete 8 is closed: `CovenantService.cs` x2, `Utilities.cs` x1, `Brute.cs` x1, the three transports x3, `InternalListener.cs` x1.

`[inferred]` **The premise was reasonable and false in a specific way worth naming: the two files LO named are the two that DO have an unread arm each — but not *additional* ones.** `Brute.cs`'s arm was never read as *its own* object (D143 printed its body and classified it anyway); `InternalListener.cs`'s was read. So the count was right and the description over-stated it.

`[verified]` **What IS unread in `InternalListener.cs` is more interesting than what the brief expected: two switches with NO `default:` arm at all** (`:335`, `:1038`). §4 reads both. **One of them fails open and D143's arm-based method structurally could not have found it.**

---

## §1 The instrument is recovered, not rebuilt — scope and count controls

`[verified]` **Both of D143's headline counts reproduce exactly under my independent enumeration:**

| quantity | D143 | D151 | this sweep | agree |
|---|---:|---:|---:|---|
| source files in scope | 254 | 254 | **254** | **yes** |
| `^\s*default\s*:` arms | 8 | 8 | **8** | **yes** |
| `\bcase\s+"` arms | 154 | 154 | **154** | **yes** |

`[verified]` **The scope control has a failure mode and it was tested.** Had my walk dropped the 102 `.razor` files, the `case "` count would fall from 154 toward 119 (23 arms live in `.razor` — D143 §0(a)). **It returned 154, so the glob is not truncating.** `[inferred]` **This control can detect a dropped extension; it CANNOT detect a case-folding defect, because a case-blind test on the same scope returns the same 154.** That axis is a stated limitation, not a covered one.

---

## §2 The classifier, fixed before execution, and the 5 predictions it made

**The question the brief asks — "what method is it IN?" — is the right instinct, but it is not sufficient on its own.** A method name is a *label*; a reader who classifies on names is doing authorship by convention, which is Rule 29's defect class. **The class is decided by what the arm SELECTS:**

| class | definition |
|---|---|
| **DISPATCH** | the arm selects **which handler/method runs** |
| **ENCODER** | the arm selects a **transform of one character** |
| **OTHER** | the arm selects a **value** — neither handler nor per-char transform |

`[verified]` **Five predictions were stated before the classifying run, so that a hit could fail:**

| # | site | predicted | observed |
|---|---|---|---|
| 1 | `switch((int)c)` in `JavaScriptStringEncode` | **ENCODER x4** | **4** |
| 2 | `switch(targetGrunt.Status)` with `PostX()` bodies | **DISPATCH x1** | **1** |
| 3 | `switch(profile.Type)` returning `CodeTemplate` | **DISPATCH x1** | **1** |
| 4 | `switch(cred.Type)` loosening to a broader query | **DISPATCH x1** | **1** |
| 5 | `switch(language)` returning `".cs"` | **OTHER x1** | **1** |

**5 of 5.** The predictions are stated because a classifier whose output is reported without a prior claim is a classifier that cannot be caught being wrong.

---

## §3 The corrected population, arm by arm

`[verified]` **The discriminator that carries the classification is the SWITCH EXPRESSION, not the method name.** Every arm below was read with its `switch(...)` head and its enclosing declaration:

| # | site | switches on | arm body | class |
|---:|---|---|---|---|
| 1 | `CovenantService.cs:1642` | `profile.Type` | `return CodeTemplate;` | **DISPATCH** |
| 2 | `CovenantService.cs:3213` | `cred.Type` | broader `FirstOrDefaultAsync` | **DISPATCH** |
| 3 | `Utilities.cs:146` | `language` | `return ".cs";` | **OTHER** |
| 4 | `Brute.cs:995` | **`(int)c`** | `sb.Append(c);` | **ENCODER** |
| 5 | `GruntBridge.cs:1149` | **`(int)c`** | `sb.Append(c);` | **ENCODER** |
| 6 | `GruntHTTP.cs:1298` | **`(int)c`** | `sb.Append(c);` | **ENCODER** |
| 7 | `GruntSMB.cs:1174` | **`(int)c`** | `sb.Append(c);` | **ENCODER** |
| 8 | `InternalListener.cs:501` | `targetGrunt.Status` | `PushCache(NotFound); return guid;` | **DISPATCH** |

| class | count |
|---|---:|
| ENCODER | **4** |
| DISPATCH | **3** |
| OTHER | **1** |
| **total** | **8** |

`[verified]` **SUM CHECK: 4 + 3 + 1 = 8, the total. The partition closes.** `[inferred]` **This is stated as a check rather than as evidence, because a partition that sums proves only that the buckets were counted twice consistently, not that they were defined correctly.** C-09 §4 supplies the standing rule — *a summary that partitions a population must sum to the population* — and here it does; that is necessary, not sufficient.

### §3.1 The encoder family is FOUR arms, not three

`[verified]` **D151 read three transport files and reported three encoder arms. The source contains four.** `Brute.cs:995` is `switch ((int)c)` inside `public static string JavaScriptStringEncode(string value)` — the identical construct, the identical body (`sb.Append(c);`), the identical method name.

`[verified]` **And D143's own §3 table already printed it:** row 4 reads `Brute.cs:996` → **`sb.Append(c);`** — passes the character through. **D143 had the evidence that arm 4 is a pass-through, printed it, and classified it fail-open anyway.** `[inferred]` **The misclassification did not require a missed read. It required only that the `default:` token, once seen, was never asked what it selects.**

`[verified]` **The structural signature is exact and 1:1.** `switch ((int)c)` occurs **4 times tree-wide** and all 4 are in `JavaScriptStringEncode`:

```text
Brute.cs:972        in JavaScriptStringEncode
GruntBridge.cs:1126 in JavaScriptStringEncode
GruntHTTP.cs:1275  in JavaScriptStringEncode
GruntSMB.cs:1151   in JavaScriptStringEncode
```

**Control that could have returned the wrong answer:** the question is whether the encoder family is LARGER than the `default:` census can see — a `JavaScriptStringEncode` with no `default:` arm would be invisible to an arm-based method. **Measured: 4 files mention `JavaScriptStringEncode`, 4 have the `default:` arm within the method, 0 do not.** The arm census sees the whole family.

### §3.2 Why the encoder arm is not merely "probably fine" — the source proves it twice

`[verified]` **Reading `Brute.cs:945-1002` in full settles it, and settles it more strongly than the "7 case values" argument D151 gave.**

**First, line 960:** `if (!needEncode) { return value; }` — **the method returns the input UNMODIFIED as its primary path.** A method whose normal path is "pass the character through" cannot have an error path that means "unhandled character." **The `default: sb.Append(c)` is the same semantics as line 960, expressed for the residual case.**

**Second, line 966 — the guard immediately above the switch:**

```csharp
if (c >= 0 && c <= 7 || c == 11 || c >= 14 && c <= 31 || c == 39 || c == 60 || c == 62)
{
    sb.AppendFormat("\\u{0:x4}", (int)c);
}
else
{
    switch ((int)c)   // <-- reached only by characters that survived the filter
```

`[verified]` **The switch is reached only by characters already excluded from `\uXXXX` escaping.** The seven cases handle `8, 9, 10, 12, 13, 34, 92`. **Every other printable character — the letter `a`, digits, spaces — lands on `default:`.** `[verified]` **D151's falsification test is confirmed and now provable from two independent lines: a `default` reached by the majority of input is not an error path.**

`[inferred]` **The correction to D143 is therefore not a judgement call about intent. It is a statement about what the code does on the input it will overwhelmingly receive.**

---

## §4 The 57 switches D143's method could not see

`[verified]` **Tree-wide, the covenant has 65 `switch` statements. 8 carry a `default:` arm. 57 carry none.**

| quantity | count |
|---|---:|
| `switch` statements tree-wide | **65** |
| switches WITH a `default:` arm | **8** |
| switches WITHOUT a `default:` arm | **57** |

`[verified]` **SUM CHECK 8 + 57 = 65.**

`[verified]` **44 of the 57 are the generated enum family** (`ToSerializedValue` / `ParseX` pairs), whose exhaustive-case property is D143 §4's finding and is not re-adjudicated here. **13 are not**, and those are the ones worth reading:

| file | line | switches on |
|---|---:|---|
| `InternalListener.cs` | **335** | `cacheEntry.Status` |
| `InternalListener.cs` | 1038 | `node.Name` |
| `CovenantService.cs` | 1522 | `grunt.DotNetVersion` |
| `CovenantService.cs` | 3456 | `indicator.Type` |
| `CreateCredential.razor` | 21 | `credential.Type` |
| `CreateIndicator.razor` | 21 | `indicator.Type` |
| `CreateLauncher.razor` | 166 | `aLauncher.Name` |
| `CreateLauncher.razor` | 237 | `Launcher.Name` |
| `CredentialForm.razor` | 144 | `type` |
| `IndicatorForm.razor` | 134 | `type` |
| `GruntInteractTerminal.razor` | 158 | `e.Key` |
| `LauncherForm.razor` | 134 | `Launcher.Name` |
| `LauncherForm.razor` | 298 | `this.Launcher.Type` |

### §4.1 `InternalListener.cs:335` fails open, and it is not a `default:` arm

`[verified]` **Read in full. Two cases, no `default:`, and the fall-through returns an empty string:**

```csharp
switch (cacheEntry.Status)          // L335
{
    case GruntMessageCacheStatus.NotFound:
        await this.MarkTasked(cacheEntry.Tasking);
        throw new ControllerNotFoundException(cacheEntry.Message);   // L339  LOUD
    case GruntMessageCacheStatus.Ok:
        await this.MarkTasked(cacheEntry.Tasking);
        return cacheEntry.Message;                                    // L342
}
return "";                                                           // L345  SILENT
```

`[inferred]` **This is fail-open AND fail-quiet: an unmatched status returns `""` as though the message were empty.** The caller sees a normal return carrying no content. Nothing logged, nothing thrown.

`[verified]` **The asymmetry inside four lines is what makes it a measurement rather than a reading.** Arm `NotFound` at L339 **does** `throw new ControllerNotFoundException`. **The same switch, three lines later, silently returns `""`.** `[inferred]` **A file that demonstrably knows how to fail loudly, and does so in one arm, is not a file where the silent arm is a style choice. The loud arm is the control: it proves the construct is reachable and that the author used it.**

`[inferred]` **And this is precisely what D151 predicted D143's method would miss — except D151 predicted it of the transports, and it is here, in the one file D143 called its sharpest site.** D143 §3 named `InternalListener.cs:501` *"the sharpest and the one worth a rule"* and filed it as corroborating. **The sharper instance sits 166 lines above it in the same file, and it has no `default:` token to match on.**

### §4.2 `InternalListener.cs:1038` — same shape, bounded elsewhere, and reported as bounded

`[verified]` **`switch (node.Name)` in `FromXmlString` has 8 cases and no `default:`.** An unrecognised XML element is silently ignored.

`[verified]` **But the enclosing region bounds it:** `else { throw new Exception("Invalid XML RSA key."); }` at L1053, and `rsa.ImportParameters(parameters)` at L1056 **will reject a structurally invalid key downstream.** `[inferred]` **So an ignored element degrades the key rather than silently succeeding with one — the failure surfaces at import. Report is BOUNDED, not fail-open.**
`[inferred]` **Stated as a limit on my own finding: I did not execute `ImportParameters` and cannot prove it rejects every such case. This is a static reading of the guard structure. `[blocked]` magnitude, direction argued.**

---

## §5 D143 §3 restated against the corrected denominator, and the method limit

`[verified]` **D143's sentence is: *"All eight are fail-OPEN. Not one logs, throws, or rejects."***

`[inferred]` **The INDIVIDUAL verdicts survive for the three DISPATCH arms. The DENOMINATOR does not survive.**

| | D143 | corrected |
|---|---:|---:|
| arms classed fail-open | 8 | — |
| of which ENCODER (carry no dispatch semantics) | 0 | **4** |
| of which not a dispatch arm | 0 | **4** |
| **dispatch denominator** | **8** | **3** |

`[verified]` **The fail-open verdict holds for all three DISPATCH arms:** arm 1 returns the unmodified template silently; arm 2 loosens to a broader query; arm 8 caches `NotFound` and returns normally. **All three select a handler or a query and all three fail open.** `[inferred]` **The finding does not collapse. The count is 3, not 8.**

`[inferred]` **Arm 3 (`Utilities.cs:146`, unrecognised language silently becomes `.cs`) belongs to the same FAMILY — a silent wrong answer instead of an error — but it selects a VALUE, not a handler.** It is left in OTHER so a reader can decide whether the family or the dispatch count is the quantity they want. **Collapsing it into DISPATCH to make the number larger would be the same error in the opposite direction.**

### §5.1 THE METHOD LIMIT — the arm-based method structurally cannot find the stronger instance

`[verified]` **D151 established the transport fail-open structurally: an `if / else if` chain on `message.Type` with no trailing `else`, no `default:`, and no final `throw`.** An unrecognised tasking type falls through the entire chain and is discarded with no log and no response.

`[verified]` **And §4.1 above establishes the same shape in `InternalListener.cs:335`: no `default:`, silent `return ""`.**

`[inferred]` **D143's instrument cannot find either one, and the reason is structural rather than incidental: it searches for the token `default:`. A construct defined by the ABSENCE of that token is not a near-miss for that search — it is outside its range entirely.** The method is not weak here. It is blind here, and it is blind in the direction where the strongest evidence lives.

`[verified]` **The measurable consequence: D143 found 8 arms and missed 57 switches.** `[inferred]` **Of the 57, 44 are the exhaustively-cased enum family (a real and separate D143 finding), and 13 are not; those 13 are where the uncounted decision points are.** **Two of the 13 were read here and one fails open.**

`[inferred]` **Stated as a limit on this report: I read 2 of the 13. I do NOT claim the other 11 fail open, and I do NOT claim only one does.** `[blocked]` **The count of failing non-enum switches is not established here and requires reading 11 more switch bodies — each needing its enclosing guard read too. Naming it as unfinished work is the honest close.**

---

## §6 Controls, each with the failure mode it cannot cover

`[verified]` **Every count above carries a control, and each control's blind direction is named.** D149 §2.1 found a control whose condition (`len(dead) >= 0`) is true for every input, so it announced `DISCRIMINATES` on a zero. **Checked for that shape here:**

| # | control | required | observed | blind direction |
|---|---|---|---|---|
| 1 | scope and count vs D143/D151 | 254 / 8 / 154 | **254 / 8 / 154** | cannot see a case-fold defect |
| 2 | `switch((int)c)` selects only encoders | 4, all encoders | **4 of 4** | cannot see an encoder with no `default:` — **tested, 0 exist** |
| 3 | 5 predictions before execution | all 5 match | **5 of 5** | predicted a count, not a class |
| 4 | partition sums | 4+3+1 = 8 | **8** | proves consistency, NOT correct definitions |
| 5 | brace-matched switch scan | 8 + 57 = 65 | **65** | cannot see a switch inside a one-line lambda |

`[verified]` **Control 2 is the one built to D149's warning.** Its falsifiable form is a `JavaScriptStringEncode` **without** a `default:` arm — which would prove the arm census blind to its own family. **Measured: 4 with, 0 without.** `[inferred]` **This control COULD have returned the wrong answer and it is the direction the instrument's own claim lives in — unlike a control that checks that my buckets sum, which cannot fail while the buckets are defined the way they are.**

### §6.1 One instrument defect of my own, disclosed

`[verified]` **My first switch scan reported 7 switches with a `default:` against 8 `default:` arms — a partition that did not close. The defect was my own scan window closing at the first `}` it met, which cut off the long `HTTP` case body in `GruntTemplateReplace` and then mis-attributed its default to a different switch.**
`[verified]` **Corrected by brace-matching: `switch (profile.Type)` at L1584 DOES carry the `default:` at L1642 — 58 lines below it. 8 switches, 8 arms.**
`[inferred]` **This is Shape 30 recurring: a probe that truncates its own input and returns a plausible number.** It was caught by the sum check — 7 + 57 != 65 — and not by reading the output, which looked entirely reasonable. **The partition check is what made it visible.**

---

## §7 What this report does and does not do

- `[verified]` **Corrects D143 §3's denominator from 8 arms to 3 DISPATCH arms**, and identifies the 4-arm encoder family, including the fourth (`Brute.cs:995`) that D151 did not read.
- `[verified]` **Confirms D151's encoder classification in full**, and strengthens it from two source facts (the `!needEncode` early return at L960 and the `\uXXXX` guard at L966).
- `[verified]` **Confirms the fail-open finding survives at n=3.** D143's conclusion is not retracted; its count is.
- `[verified]` **Reports that D143's method could not see 57 of 65 switches**, and read 2 of the 13 non-enum ones — finding one fail-open (`InternalListener.cs:335`) that is sharper than D143's own named sharpest site, in the same file.
- `[absence]` **NOT established: whether the other 11 non-enum switches fail open.** Not claimed, not estimated.
- `[inferred]` **NOT a Ruby claim; no Ruby toolchain was used and no Ruby was read.**
- **No execution, no network, no live C2, no handler, no `open_binary`.** Every line cited was read from disk with `ReadAllText`.
- **No artefact edited.** D143, D151, D152 and C-09 are cited, never modified. D151's C-26 (−1 line-offset correction) is adopted and this report's line numbers are 1-based as read.

---

## §8 Residuals

- **R-158.1** — **11 non-enum switches unread** (`CovenantService.cs:1522`, `:3456`, both `CreateX.razor`, both `XForm.razor`, `GruntInteractTerminal.razor:158`, `LauncherForm.razor:134`, `:298`, `CreateLauncher.razor:237`). Named, not estimated.
- **R-158.2** — the `.razor` switches dispatch on UI events and names; their fail mode is operator-visible and may be categorically different. **Not read; the distinction is flagged, not resolved.**
- **R-158.3** — `InternalListener.cs:1038`'s downstream bound (`ImportParameters`) is argued from guard structure, not executed. **Static only.**
- **R-158.4** — D143's 22-file `return null;` API-model family was not re-adjudicated here; it is a separate population from the 8 arms.

*End of D158.*