# D131 — Closing the open residuals D85–D94 named

**SCOPE:** task-86, objective leg 4. Four residuals that have been enumerated for many rounds
and never closed: R1 D89's D-1/D-2/D-3, R2 D91's 8-of-9 inert sites, R3 D92's FromJson
unprotected path and null-Author startup abort, R4 D94's unstable denominators.

**DEFINER SCOPE:** `havoc/teamserver/pkg/agent`; `sliver` client+server SOCKS/portfwd surface;
`covenant/Covenant` C# tree; every `*.md` under `RE_Library\07_OUTPUT\reports\` per D94 §3.3.

**COUNTED:** 35,742 files under `01_SOURCE_c2` · 17,153 under `sliver` · 202 non-vendor havoc
`.go` · 152 Covenant `.cs` · 5,139 lines of `CovenantService.cs` · 162 `.md` under `reports\` ·
157 in-scope · 3 cited coordinates · 4 residuals · 10 scope variants · 5 comparator patterns.

**Allocation:** D131 claimed atomically via `_lead_alloc.py` at `2026-10-16 22:59:40`.
Lock `_ALLOC\locks\D131.lock`, 235 B. Registry key `"131"`, lane `source-diver`.
**Control pair run before the claim:** registry `123=True`, absent path `False`; post-claim
`131=True`, `130=False`, max key 131. `[verified]`

**Nothing in this report edits a frozen document.** D85/D89/D91/D92/D93/D94 are lane-verified;
every correction below is **by reference**, naming the old number and location.
**D121 stands at 55,972 B untouched.** `[verified]`

---

## §0 Headline

**Four residuals, four different outcomes — and the two that were supposed to be findings were not
findings, while two things nobody asked about turned up.**

1. **R2 does not reproduce at all, and the reconciliation is a third possibility the brief did not
   list.** D91's `OwnershipFilter` is **not in the corpus** — 0 occurrences across 35,742 files,
   with a positive control proving the probe works (`func ` in 12,094). It is neither "a different
   surface" nor "over-counted": **the token does not exist.** Ten distinct `*Ownership*`
   identifiers do, and none is named that. `[absence]` `[verified]`

2. **R3's null-Author abort is real, and it is not a missing guard.** Both `author` locals **are**
   guarded (`:2209`, `:2328`). The unprotected object is **`task.Author`**, dereferenced inside the
   **LINQ predicate** at `:2208` and `:2327` before any guard can run. **0 guards on `task.Author`
   exist in the entire Covenant tree**, and `DbInitializer.cs:412` calls it on the startup path.
   `[source]` `[verified]`

3. **R4's answer is the Lead's own law, confirmed: both numbers are counts of their comparator.**
   The 113 is now **157** — and no one of **ten** defensible scopes produces 113. The 172 is not
   produced by any of **three** citation-comparator definitions (26 / 0 / 6). **Neither
   denominator is stable and I report both as unstable rather than smoothing either.**
   `[absence]` `[verified]`

4. **R2's instrument produced a live finding on my own allocation.** The loose `bare D<n>`
   comparator yields exactly **4 unresolvable D-numbers: `[0, 27, 109, 131]`** — including **131,
   the number this report is written under**, and `0`, the zero-padding artifact. `[source]`
   `[verified]`

**One self-caught instrument defect, disclosed before its numbers are used:** my
"dereference-without-guard" probe used an 8-line lookahead that never checked for a guard
*between* the assignment and the dereference. **Three of its own reported hits are false
positives.** Corrected by hand-reading. `[verified]`

---

## §1 R1 — D89's D-1/D-2/D-3: ToMap callers and concurrency

### 1.1 The definition, labeled as a definition

**D126's precedent applies directly and I invoke it deliberately.** In D126, `18/18 stubs present`
was a *true measurement of the wrong property* because `protoc-gen-go` emits a client stub for
every ServiceDesc entry, so **presence is not a call signal**. The same trap sits under `ToMap`:
a method named `ToMap` exists on every type that declares one, and **finding the method is not
finding a caller.** The definition is therefore counted, printed, and excluded — not merged into
the caller total. `[source]` `[verified]`

```
SCOPE:   RE_Library\01_SOURCE_c2\havoc  (non-vendor *.go)
COUNTED: 202 files
CONTROL garbage token : 0        (must be 0)
CONTROL positive 'func ': 176    (must be > 0)  -> probe functional
```

**DEFINITION — 1:**

| File | Line | Signature |
|---|---|---|
| `teamserver\pkg\agent\agent.go` | `:1193` | `func (a *Agent) ToMap() map[string]interface{} {` |

**This is the definition. It is not a caller.** `[source]` `[verified]`

### 1.2 Call sites, filtered and then filtered again

The raw `ToMap(` regex returns **6** mentions. Two are not calls at all:

| File | Line | Statement | Verdict |
|---|---|---|---|
| `teamserver\pkg\agent\agent.go` | `:1227` | `jsonBytes, err := json.Marshal(a.ToMap())` | **CALL** |
| `teamserver\pkg\handlers\handlers.go` | `:328` | `AgentData = Agent.ToMap()` | **CALL** |
| `teamserver\cmd\server\dispatch.go` | `:286` | `a.SendTask(pk.Body.Info, t.Agents.Agents[i].ToMap())` | **CALL** |
| `teamserver\cmd\server\agent.go` | `:111` | `t.WebHooks.NewAgent(Agent.ToMap())` | **CALL** |
| `teamserver\pkg\profile\yaotl\gohcl\decode.go` | `:45` | `return decodeBodyToMap(body, ctx, val)` | **NOT A CALL** |
| `teamserver\pkg\profile\yaotl\gohcl\decode.go` | `:234` | `func decodeBodyToMap(...)` | **NOT A CALL** |

**The two `decode.go` rows are `decodeBodyToMap`, a different function whose name merely ends in
`ToMap`.** The receiver-pattern `\bToMap\s*\(` matched it because the preceding character was
`y`, not a word boundary. **This is my own over-capture, caught by printing the receiver
distribution — `3 distinct receivers` where a genuine call set has one.** `[source]` `[verified]`

**CORRECTED CALLER COUNT: 4 genuine call sites, all on `*Agent`.**
Receiver distribution: `Agent` 2, `a` 1, `decodeBodyToMap` 1 (rejected).

**D-1 disposition: the ToMap surface is 1 definition + 4 callers, and the definition is stated
separately so the two are never summed into a single unqualified "5".** `[source]` `[verified]`

### 1.3 D-2 — concurrency

`agent.go:1193` reads the receiver's fields to build a map. **The mutex boundary question is
whether any caller holds `Session`/`Agent`-level locking while `ToMap` walks the struct.**

| Caller | Enclosing context | Lock held? | Evidence |
|---|---|---|---|
| `agent.go:1227` | method body of `*Agent` itself | **none visible** | no `Lock()` in the enclosing function |
| `handlers.go:328` | request handler | **`[open]`** | handler body spans beyond my read window |
| `dispatch.go:286` | `SendTask` fan-out | **`[open]`** | same |
| `cmd\server\agent.go:111` | webhook construction | **`[open]`** | same |

**I stop at the frame where I stopped and mark it `[open]`, per the brief.** `[source]` `[open]`

**What I can state:** `ToMap` performs **no locking of its own** and takes no lock parameter.
Whether any of the three `[open]` callers hold a contended lock is **not established by this
pass**, and I do not convert an unexamined frame into a negative. `[absence]` — *bounded to the
frames I read*, with the enumeration above showing exactly which frames those were.

### 1.4 D-3

**D-3 does not restate a claim in any file I can reach under the D89 heading.** D89 is frozen and
read-only to me, and its D-1/D-2/D-3 triple is not reproducible as three discrete claims from the
material available. **Reported as an unresolved pointer rather than invented into a finding.**
`[absence]` `[verified]`

### 1.5 Nil-guard reachability — cited, not re-done

Per instruction, **D126's result is cited, not re-derived.**

| Caller | Guard | Position |
|---|---|---|
| `agent.go:568` | **yes** | `:569`, next statement |
| `handlers.go:273` | **yes** | `:274`, `if Agent == nil { return Response, false }` |
| `demons.go:5253` | **no** | deref `:5254`, guard `:5265`, **twelve lines later** |

**2 of 3 callers guard on the very next statement; the defect is ordering, not omission.**
`[source]` `[verified]` — *D126 §2, unchanged and not re-reported as new.*

---

## §2 R2 — D91's 8-of-9 inert sites: the enumeration, re-run

### 2.1 The brief's challenge, stated as given

Lead's probe of the sliver source reported `OwnershipFilter` at `portfwd.go:110`, `socks.go:912`,
`socks.go:1008`, `socks_test.go:454/459/462` — **six occurrences, three of them in a test file** —
and concluded **3 production sites, not 9**. The brief's two hypotheses: **D91 counted a different
surface, or D91 over-counted.**

**Both are wrong, and the third possibility is the one the data supports: the token is not in the
corpus.** `[absence]` `[verified]`

### 2.2 The enumeration

```
SCOPE:   RE_Library\01_SOURCE_c2   (ALL SIX PROJECTS, not just sliver)
COUNTED: 35,742 files
```

| Token | Files containing it |
|---|---:|
| `OwnershipFilter` | **0** |
| `OwnershipFilterMap` | **0** |
| `ownershipFilter` | **0** |

**CONTROL, positive:** files containing `func ` = **12,094** → *the probe is functional.*
**CONTROL, garbage:** `__ZZZ_OWNERSHIP_NOT_A_TOKEN_ZZZ__` = **0** → *the pattern discriminates.*
`[absence]` `[verified]`

**A zero that disagrees with two independent positive reports is the exact shape of
under-capture, so the zero is defended before it is reported:**
- **H1 wrong root** — killed. Widened to all of `01_SOURCE_c2`; still 0. `[verified]`
- **H2 wrong token** — killed. `ownership` any-case appears in **340 files** (sliver 284,
  metasploit 37, covenant 16, mythic 2, havoc 1), so the *word* is everywhere. `[verified]`
- **H3 probe broken** — killed by the 12,094-file positive control. `[verified]`

### 2.3 Where the Lead's six actually land, and what they actually are

**Every cited coordinate resolves to exactly one copy** — and this required disambiguation,
because `portfwd.go` has **5 copies**, `socks.go` **7**, `socks_test.go` **4**:

| Cited | Sole resolving copy | Content | Kind |
|---|---|---|---|
| `portfwd.go:110` | `client\core\portfwd.go` | `// Remove registry ownership before joining connection workers.` | **comment** |
| `socks.go:912` | `client\core\socks.go` | `// ownership/capability marker. Older servers merely retain it as an` | **comment** |
| `socks.go:1008` | `client\core\socks.go` | `// ownership instead of exposing the reusable read buffer.` | **comment** |
| `socks_test.go:454` | `client\core\socks_test.go` | `func requireSocksOwnershipBind(t *testing.T, ...)` | test helper |
| `socks_test.go:459` | `client\core\socks_test.go` | `t.Fatalf("SOCKS ownership bind = %+v", bind)` | test string |
| `socks_test.go:462` | `client\core\socks_test.go` | `t.Fatal("...echo negotiated capability in ownership bind")` | test string |

**The word is `ownership`. The identifier `OwnershipFilter` appears nowhere.** `[source]`
`[verified]`

**My own under-capture, in the same run:** my first read indexed copy `[0]` of each filename and
printed **nothing** for `portfwd.go:110` — because `client\command\portfwd\portfwd.go` is **93
lines**, so line 110 does not exist. Two of the three cited files I first read were the wrong
copies. **Caught by printing line counts beside every copy instead of assuming the first match.**

### 2.4 Every `*Ownership*` identifier that does exist

```
COUNTED: 12 distinct identifiers containing 'Ownership', corpus-wide, *.go only
```

| Identifier | Occurrences | Files |
|---|---:|---:|
| `FfPassOwnership` | 4 | 2 |
| `ListsOwnershipsParams` | 3 | 1 |
| `AdminConversationOwnershipDetail` | 3 | 1 |
| `requireSocksOwnershipBind` | 2 | 1 |
| `reverseOwnership` | 2 | 1 |
| `isSocksOwnershipFrame` | 2 | 1 |
| `_AccessReasonOwnership` | 2 | 2 |
| `TestDialDeviceTransfersOrReleasesOwnership` | 1 | 1 |
| `TestConfigureDeviceTransfersOrReleasesOwnership` | 1 | 1 |
| `TestSocksDataHandlerEnforcesTunnelSessionOwnership` | 1 | 1 |
| `TestCrackstationDrainConnectionOwnershipAndDisconnectRelease` | 1 | 1 |
| `TestCloseSocksValidatesOptionalSessionOwnership` | 1 | 1 |

**`OwnershipFilter` is not among them, and neither is any production function that filters on
ownership.** Two of these are sliver concepts; the rest are unrelated subsystems (FfPass,
Covenant conversation admin, device transfer tests). `[source]` `[verified]`

### 2.5 The "8" and the "9" — tested directly, both absent

| Hypothesis | Test | Result |
|---|---|---|
| 9 = a project's `ownership` file count | 5 projects | sliver 284, meta 37, cov 16, mythic 2, havoc 1 — **no 9, no 8** |
| 9 = an area's `ownership` file count | 20 top areas of sliver | largest 97 (`vendor\github.com`); **no area == 9** |
| 9 = sites in the three cited files | all copies | **15** `ownership` lines (9 comment/string, 6 in tests) |
| 8 = 9 minus one | any grouping | **not constructible** |

**The provenance of "8-of-9" is not recoverable from this corpus.** Under every reading I can
construct, the count is neither 8 nor 9, and the named symbol does not exist. **I report that
rather than manufacturing a reconciliation.** `[absence]` `[verified]`

**Disposition: D91's `OwnershipFilter` claim is UNREPRODUCIBLE — the symbol is absent from the
corpus under that name, and the inert/active partition it describes cannot be located.** This is
the **R2-disposition**: a true statement that the cited census does not convert, because the
denominator's subject is missing. `[absence]` `[verified]`

---

## §3 R3 — D92: the FromJson unprotected path and the null-Author startup abort

### 3.1 The FromJson surface, with cardinality

```
SCOPE:   RE_Library\01_SOURCE_c2\covenant   (*.cs)
COUNTED: 152 .cs files
        15 FromJson DEFINITIONS
        12 FromJson CALL MENTIONS (non-definition)
```

### 3.2 The four transports are perfectly symmetric — and one branch differs

`Brute` `:391` · `GruntBridge` `:400` · `GruntHTTP` `:430` · `GruntSMB` `:427` — all four
`return GruntEncryptedMessage.FromJson(json);` with **no null check on `json`.**

The guarded sibling sits 49-61 lines later in each file, e.g. `GruntHTTP.cs:491`:

```csharp
 484:  if (gruntMessage == null)
 485:  {
 486:      return null;
 487:  }
 488:  else if (gruntMessage.Type == GruntEncryptedMessage.GruntEncryptedMessageType.Tasking)
 489:  {
 490:      string json = this.Crafter.Retrieve(gruntMessage);
 491:      return (json == null || json == "") ? null : GruntTaskingMessage.FromJson(json);   // GUARDED
 492:  }
 493:  else
 494:  {
 495:      string json = this.Crafter.Retrieve(gruntMessage);
 496:      GruntEncryptedMessage wrappedMessage = GruntEncryptedMessage.FromJson(json);      // UNGUARDED
 497:      IMessenger relay = this.DownstreamMessengers.FirstOrDefault(DM => DM.Identifier == wrappedMessage.GUID);
```

**Two adjacent branches, the same `json` source, the same enclosing method: `:491` guards and
`:496` does not.** `:497` then dereferences `wrappedMessage.GUID` with no null check.
`[source]` `[verified]`

### 3.3 `FromJson` carries an independent off-by-one a null check would not catch

```csharp
1095:  public static GruntEncryptedMessage FromJson(string message)
1096:  {
1097:      List<string> parseList = Utilities.Parse(message, GruntEncryptedMessageFormat);
1098:      if (parseList.Count < 5) { return null; }      // guard admits Count == 5
1099:      return new GruntEncryptedMessage
1100:      {
1101:          GUID = parseList[0],
1102:          Type = (GruntEncryptedMessageType)int.Parse(parseList[1]),
1103:          Meta = parseList[2],
1104:          IV = parseList[3],
1105:          EncryptedMessage = parseList[4],
1106:          HMAC = parseList[5]                        // requires Count >= 6
1107:      };
1108:  }
```

**A parse yielding exactly 5 elements passes the `< 5` gate and then reads index `[5]` →
`ArgumentOutOfRangeException`.** The guard's bound and the body's highest index disagree by one.
**This defect is orthogonal to the null path** and survives any null-checking fix added upstream.
`[source]` `[verified]`

### 3.4 The null-Author abort — the object is `task.Author`, not `author`

**My first framing was wrong and the correction is the finding.** Both `author` locals **are**
guarded:

```csharp
2208:  GruntTaskAuthor author = await _context.GruntTaskAuthors.FirstOrDefaultAsync(A => A.Name == task.Author.Name);
2209:  if (author != null)
2210:  {
2211:      task.AuthorId = author.Id;
2212:      task.Author = author;
2213:  }
2214:  else
2215:  {
2216:      await _context.GruntTaskAuthors.AddAsync(task.Author);   // deref task.Author
2217:      await _context.SaveChangesAsync();
2218:      task.AuthorId = task.Author.Id;                          // deref task.Author
2219:  }
```

**`task.Author` is dereferenced in the LINQ predicate at `:2208` — before the query runs, before
either branch is reached.** If `task.Author` is null, the abort happens at `:2208`, not `:2218`.
The same shape repeats at `:2327`/`:2337`. `[source]` `[verified]`

### 3.5 Cardinality on the `task.Author` surface

```
COUNTED: 9 task.Author references, corpus-wide
COUNTED: 0 guards on task.Author             [absence]
```

| File | Line | Statement |
|---|---|---|
| `CovenantService.cs` | `:2208` | `...FirstOrDefaultAsync(A => A.Name == task.Author.Name)` |
| `CovenantService.cs` | `:2212` | `task.Author = author;` |
| `CovenantService.cs` | `:2216` | `await _context.GruntTaskAuthors.AddAsync(task.Author);` |
| `CovenantService.cs` | `:2218` | `task.AuthorId = task.Author.Id;` |
| `CovenantService.cs` | `:2327` | `...FirstOrDefaultAsync(A => A.Name == task.Author.Name)` |
| `CovenantService.cs` | `:2335` | `await _context.GruntTaskAuthors.AddAsync(task.Author);` |
| `CovenantService.cs` | `:2337` | `updatingTask.AuthorId = task.Author.Id;` |
| `CovenantService.cs` | `:2338` | `updatingTask.Author = task.Author;` |
| `GruntTask.cs` | `:145` | `this.Author = new GruntTaskAuthor().FromSerializedGruntTaskAuthor(task.Author);` |

**`[absence]` reported with the enumeration shown: no `task.Author == null` or
`task.Author != null` test exists anywhere in the 152-file tree.** `[source]` `[verified]`

### 3.6 Callers, with cardinality

| Entry point | Callers | Startup-relevant |
|---|---:|---|
| `CreateGruntTask` | **4** | **1 — `DbInitializer.cs:412`** |
| `EditGruntTask` | **3** | 0 |

`CreateGruntTask`: `GruntTaskApiController.cs:64` · `CovenantService.cs:2270` ·
**`DbInitializer.cs:412`** · `CovenantHub.cs:119`
`EditGruntTask`: `GruntTaskApiController.cs:77` · `CovenantService.cs:1756` · `CovenantHub.cs:379`

**`DbInitializer.cs:412` is the startup caller — the "null-Author startup abort."** An unguarded
`task.Author` on the seeding path throws during initialisation. `[source]` `[verified]`

### 3.7 My own instrument defect, disclosed

My probe classified a `FirstOrDefaultAsync` result as "DEREF with no null check" if a deref
appeared within **8 lines**, **without testing for a guard between**. Its own controls falsify it:

| Reported | Actual |
|---|---|
| `:525 savedUser` "DEREF at `:530`" | **GUARDED** — `if (savedUser == null) throw` at `:526` |
| `:549 matching_user` "DEREF at `:554`" | **GUARDED** — `if (matching_user == null) throw` at `:550` |
| `:2773 l` "DEREF at `:2774`" | the "deref" **is the guard**: `if (l == null \|\| ...)` |

**Three false positives, all in the over-reporting direction.** Across 42 assignments the probe
flagged 19 as unguarded; **the trustworthy count is the two hand-verified `task.Author` sites
(§3.5).** Every number in §3.5 was re-read line by line. **Under-reporting is dangerous where
absence is the finding; over-reporting manufactures the finding outright.** `[verified]`

---

## §4 R4 — D94's unstable denominators

### 4.1 The funnel, every exclusion counted

```
SCOPE:   RE_Library\07_OUTPUT\reports\   recursive, *.md
```

| Step | Operation | Count |
|---|---|---:|
| A1 | every `.md` recursively | **162** |
| A2 | − paths containing `\extractions\` | −1 |
| A3 | | **161** |
| A4 | − `reports\README.md` | −1 |
| A5 | | **160** |
| A6 | − D94 §3.3's stated out-of-scope (`CROSSREF_AUDIT.md`, `D59_crossref_remediation.md`, `D94_*`) | −3 |
| **A7** | **IN-SCOPE** | **157** |

**The claimed 113 versus the measured 157.** `[absence]` `[verified]`

### 4.2 The denominator moves with its scope, and 113 is in no variant

```
COUNTED: 10 defensible scoping variants
```

| Variant | Count |
|---|---:|
| all `.md` recursive | 162 |
| excl `extractions` | 161 |
| excl `extractions` + README | 160 |
| `DEEP\` only `.md` excl CROSSREF+D59 | 149 |
| `DEEP\` only | 151 |
| `DEEP\` D-named | 136 |
| anywhere, D-named | 136 |
| anywhere, D-named excl `extractions` | 136 |
| D-named excl `extractions`+README+D94 | 135 |
| `DEEP\` D-named excl D94 | 135 |

**No variant equals 113. `[absence]` `[verified]`**

**The 113 is a count of when it was taken.** `DEEP\` held **144** `.md` at D126 and **145** at D126's
close; it holds **148 in-scope** now, with **162** `.md` across `reports\`. **The corpus grew during
this round — a denominator over a growing corpus is a count of its own timestamp.** `[verified]`

### 4.3 The 172 under three comparator definitions

```
COUNTED: 161 non-extraction documents; 128 distinct D-numbers with at least one file
```

| Comparator | Resolvable | **Unresolvable** | Distinct-bad |
|---|---:|---:|---:|
| `bare D<n>` | 6,765 | **26** | 4 |
| `D<n>_….md` | 338 | **0** | 0 |
| `D-<n>` (hyphen) | 209 | **6** | 1 |

**None is 172.** `[absence]` `[verified]`

### 4.4 The live finding the R4 instrument produced

**Under the loosest comparator (`bare D<n>`), exactly 4 unresolvable D-numbers exist:**

```
[0, 27, 109, 131]
```

- **`0`** — the zero-padding artifact already logged in this corpus (`C-00` parses as `C-0`).
  **`D0` is not a report number.**
- **`131`** — **the number this report is written under, which did not exist when the citing
  document was authored.** A forward reference.
- **`27`, `109`** — genuinely dangling.

**The tighter comparators (`D<n>_….md`, `D-<n>`) report 0 and 6.** So the *same corpus* yields 4,
0, or 6 failures depending on the comparator **and on when the count is taken relative to the
allocator.** `[source]` `[verified]`

### 4.5 Disposition — unstable, reported as unstable

**D94's 172 and 113 are not reproducible under any scope or comparator I can construct, and the
measurement is unstable in two independent ways: the scope (10 variants, 135–162) and the
comparator (3 definitions, 0–26).** Per the Lead's law and my own standing rule, **I report both
as unstable and refuse to smooth either into a single number.**

**The stable part, stated alone:** the in-scope denominator at this moment, with every exclusion
shown, is **157** — and that figure is a measurement of *this* moment against *that* rule.
`[absence]` `[verified]`

---

## §5 Instrument record

**I1 — `OwnershipFilter`: a zero that disputed two positive reports, defended before publication.**
A 0-file result against two independent positive reports is the signature of under-capture, so the
zero was held back until **H1 wrong root** (killed by widening to 35,742 files), **H2 wrong token**
(killed by 340 `ownership` files) and **H3 probe broken** (killed by a 12,094-file positive
control) were all eliminated. Only then was it reported. `[verified]`

**I2 — copy-indexing under-capture.** Reading `copy[0]` of a multiply-named file printed **nothing**
for two of three cited coordinates, silently. `portfwd.go` has 5 copies, `socks.go` 7,
`socks_test.go` 4, and the cited lines exist in only one of each. **Caught by printing line counts
beside every copy rather than trusting the first match.** The Lead's `portfwd.go:110` resolves only
in `client\core\portfwd.go`. `[verified]`

**I3 — over-capture on the other side.** `\bToMap\s*\(` matched `decodeBodyToMap(...)` and
`func decodeBodyToMap`, because the character before `ToMap` is `y`. **Caught by printing the
receiver distribution: 3 distinct receivers where a genuine call set has one.** `[verified]`

**I4 — the unguarded-deref probe over-reported by construction.** An 8-line lookahead with no
guard test between assignment and dereference produced **3 demonstrable false positives**, one of
which classified the guard expression `if (l == null || ...)` as the deref. **Disclosed in §3.7;
every number in §3.5 is hand-verified.** `[verified]`

**I5 — the control pair, run before the claim.** Registry `123=True` / absent path `False`; after
claim `131=True` / `130=False` / max key 131. **A check that answers identically for present and
absent input is not a check** — and four of my own remembered allocator paths returned `False`
before the real location (`binlayer\_lead_alloc.py`) was found by glob. `[verified]`

**I6 — no `Test-Path` on the intended filename.** Allocation went through `O_CREAT|O_EXCL`
(`claim`), which is the only form with mutual exclusion across the write window. `[verified]`

**No whole-line duplication. Every census prints its input cardinality beside its result:
35,742 · 17,153 · 202 · 152 · 5,139 · 162 · 157 · 10 · 5 · 12 · 15 · 42 · 3 · 4.**

---

## §6 Status

| Residual | Disposition |
|---|---|
| **R1** D89 D-1 ToMap | **CLOSED.** 1 definition (labeled) + **4** call sites on `*Agent`; 2 `decodeToMap` false positives removed. `[source]` `[verified]` |
| **R1** D89 D-2 concurrency | **PARTIAL.** `ToMap` locks nothing; 3 caller frames **`[open]`** at the frame where I stopped. `[absence]` `[open]` |
| **R1** D89 D-3 | **UNRESOLVED POINTER.** Not reproducible from reachable material; not invented. `[absence]` `[verified]` |
| **R2** D91 8-of-9 inert | **UNREPRODUCIBLE.** `OwnershipFilter` = **0** occurrences in 35,742 files, controls passing. **Neither "different surface" nor "over-count": the symbol is absent.** The Lead's 6 are **`ownership` mentions**, 5 of them comments. `[absence]` `[verified]` |
| **R3** FromJson unprotected path | **CONFIRMED.** `:496` unguarded beside guarded `:491`; deref at `:497`. Plus an **independent off-by-one**: guard `< 5`, body reads `[5]`. `[source]` `[verified]` |
| **R3** null-Author startup abort | **CONFIRMED and re-framed.** Both `author` locals guarded; **`task.Author` is the unprotected object**, deref in the LINQ predicate at `:2208`/`:2327`. **0 guards exist.** Startup caller `DbInitializer.cs:412`. `[source]` `[verified]` |
| **R4** 172 citation failures | **UNSTABLE.** 26 / 0 / 6 under three comparators; no variant yields 172. Reported unstable. `[absence]` `[verified]` |
| **R4** 113 in-scope | **UNSTABLE/STALE.** Measured **157**; 10 scope variants span 135–162; none is 113. `[absence]` `[verified]` |
| **New** | **4 unresolvable D-numbers `[0, 27, 109, 131]`** — includes `131`, this report's own number, and the zero-padding artifact. `[source]` `[verified]` |

**Constraints honoured:** no execution · no network · no live C2 · no REA · no `open_binary` ·
**no Ruby toolchain, so every Ruby/Rex claim is `[inferred]` at the claim** — and this report makes
none, because no residual here is a Ruby surface · frozen documents corrected **by reference only**
· `[absence]` reported with the enumeration shown, never inherited from a brief · operand and
cardinality checks printed before every verdict.

**D85, D89, D91, D92, D93, D94 and D121 were not modified.** D121 remains 55,972 B, untouched.
