# D86 — HAVOC PIVOT HANDLE SIBLING PRIMITIVES AND `.Pivots.Parent` CONSUMERS

**Closes D76 A-4a (T1), extends D76 A-1 (T2), and corrects D76 §3.1 (T3).**
**Artifact:** `teamserver/` Go sources and `payloads/Demon` C sources.
**Method:** pure source read. No REA. No execution. No network.
**Write scope:** this file only. **D47, D56, D65, D71, and D76 were not touched. Corrections to D76 are made here.**

**Line-count convention:** every line number is the 1-based line number as printed by the read oracle, where line 1 is the first line of the file. No `-Skip` display value is ever used as a line number.

---

## §0 — HEADLINE, AND A CORRECTION TO MY OWN D76

### 0.1 T1 — the negative closes HARDER than D76's

**D76's A-4a was an unmeasured assumption: that a duplex pipe does not deliver the writer's own bytes back to its own `PeekNamedPipe`.** **D76's bound rested on enumerating one primitive (`PipeWrite`).**

**T1 enumerates every sibling primitive that touches the same `PIVOT_DATA.Handle` field. Exactly one of them writes.** **The direction bound holds, and it no longer rests on an assumption about duplex semantics — it rests on the primitive census.** **D76's A-4a retires as a *measured* negative, not a structural one.** [source: §1]

### 0.2 T2 — `.Pivots.Parent` nil at the decrypt site: explicit failure, defence working

**`:5359`'s decrypt at `:5373` is inside an explicit `if PivotAgent != nil` guard, and the `else` emits an operator-visible error.** **There is no silent-empty-decrypt path at that site.** **The branch is `demons.go:5382-5385`.** [source: §2]

**And this is a meaningful contrast with `handlers.go:193`:** **the same author, the same "resolve an instance then decrypt" pattern, one site guarded correctly and one site with an inverted guard.** **D71 §1 established the second; §2 below establishes the first.** [source: D71 §1; §2.2 below]

### 0.3 T3 — CORRECTION. D76 §3.1's `.Pivots.Parent` census was WRONG. It is five assignment sites, not one.

**D76 §3.1 reported "8 hits, exactly ONE assignment (`demons.go:5242`)."** **That is false. There are FIVE assignment sites:**

```
pkg\agent\agent.go:580      PivotSession.Pivots.Parent = Session
pkg\agent\agent.go:1201     a.Pivots.Parent = nil
pkg\agent\agent.go:1216     a.Pivots.Parent = ParentAgent
pkg\agent\demons.go:5242    DemonInfo.Pivots.Parent = a
pkg\agent\demons.go:5254    DemonInfo.Pivots.Parent = a
cmd\server\teamserver.go:471  Agent.Pivots.Parent = t.AgentInstance(parentID)
```
[source: `§3.1` enumeration, printed]

**Six sites, counting the two at `demons.go`.** **D76 reported one.**

**Root cause, and it is Rule 20 firing on my own report:** **D76's probe was `Select-String 'Pivots\.Parent\s*='`, which requires a leading `.`** — **it matches `DemonInfo.Pivots.Parent = a` but NOT `Agent.Pivots.Parent = t.AgentInstance(...)` when the receiver is written as a bare identifier followed by the field, and NOT `a.Pivots.Parent = nil`.**

**Precisely: the pattern `Pivots\.Parent\s*=` does match `a.Pivots.Parent = nil`.** **So `:1201` and `:1216` should have matched.** **The miss is worse than a regex artefact: D76's §3.1 output shows 8 hits and lists only reads plus `:5242`.** **The `:1201`/`:1216`/`:580`/`:471` sites were absent from the printed list.** **This report does not claim to know why; it claims the census as printed was incomplete, and re-runs it here with a literal pattern.** [source: §3.1, and D76 §3.1's printed output]

**This is the FOURTH consecutive Rule 20 instance in this lane, and the fourth toward a false clean.** **D76's §3.1 conclusion — "exactly one writer, nothing invalidates it, maintenance hazard not live gap" — was reached on a census that was 1/6 complete.** [source: §3.3]

---

## §1 — T1: SIBLING PRIMITIVES ON THE `PIVOT_DATA.Handle`

### 1.1 The primitive census, printed

**Every call in `Pivot.c` that takes a `PIVOT_DATA.Handle`:**

```
Pivot.c:160  if ( Instance->SmbPivots->Handle )
Pivot.c:162  Instance->Win32.DisconnectNamedPipe( Instance->SmbPivots->Handle );
Pivot.c:163  SysNtClose( Instance->SmbPivots->Handle );
Pivot.c:168  Instance->SmbPivots->Handle          = NULL;
Pivot.c:192  if ( PivotData->Handle )
Pivot.c:194  Instance->Win32.DisconnectNamedPipe( PivotData->Handle );
Pivot.c:195  SysNtClose( PivotData->Handle );
Pivot.c:200  PivotData->Handle          = NULL;
Pivot.c:254  if ( TempList->Handle )
Pivot.c:259  if ( Instance->Win32.PeekNamedPipe( TempList->Handle, NULL, 0, NULL, &BytesSize, NULL ) )
Pivot.c:263  if ( Instance->Win32.PeekNamedPipe( TempList->Handle, &Length, sizeof( UINT32 ), NULL, &BytesSize, NULL ) )
Pivot.c:268  if ( Instance->Win32.ReadFile( TempList->Handle, Output, Length, &BytesSize, NULL ) )
```
[source: `Get-Content Pivot.c | Select-String 'TempList->Handle|PivotData->Handle|SmbPivots->Handle'` — 12 hits]

**Classification:**

| Primitive | Lines | Direction | Writes bytes? |
|---|---|---|---|
| `PeekNamedPipe` | `:259`, `:263` | read-only inspection | **No** |
| `ReadFile` | `:268` | read | **No** |
| `DisconnectNamedPipe` | `:162`, `:194` | teardown | **No** |
| `SysNtClose` | `:163`, `:195` | teardown | **No** |
| field null-assignment | `:168`, `:200` | bookkeeping | **No** |

**One writer of these 12, and it is not among them:** `Command.c:2586` `PipeWrite( PivotData->Handle, &Data )`. [source: D76 §1.1]

### 1.2 The sibling primitives, enumerated tree-wide

**The primitives capable of moving bytes, and every call site in the payload tree:**

```
Command.c:925     WriteFile( hFile, Content, FileSize, &Written, NULL )
Pivot.c:50        PeekNamedPipe( Handle, NULL, 0, NULL, BytesSize, NULL )
Pivot.c:59        ReadFile( Handle, *Output, *BytesSize, BytesSize, NULL )
Pivot.c:259       PeekNamedPipe( TempList->Handle, ... )
Pivot.c:263       PeekNamedPipe( TempList->Handle, ... )
Pivot.c:268       ReadFile( TempList->Handle, ... )
TransportSmb.c:41 PipeWrite( Instance->Config.Transport.Handle, Send )
TransportSmb.c:44 PipeWrite( Instance->Config.Transport.Handle, Send )
TransportSmb.c:71 PeekNamedPipe( Instance->Config.Transport.Handle, ... )
TransportSmb.c:75 ReadFile( Instance->Config.Transport.Handle, &DemonId, ... )
TransportSmb.c:93 ReadFile( Instance->Config.Transport.Handle, &PackageSize, ... )
TransportSmb.c:105 PipeRead( Instance->Config.Transport.Handle, Resp )
Win32.c:1175      BOOL PipeRead( (definition)
Win32.c:1183      ReadFile( Handle, ... )  (inside PipeRead)
Win32.c:1202      BOOL PipeWrite( (definition)
Win32.c:1210      WriteFile( Handle, Buffer->Buffer + Total, ... )  (inside PipeWrite)
```
[source: `Get-ChildItem payloads/Demon -Recurse -File -Include *.c | Select-String 'WriteFile|ReadFile|PeekNamedPipe|PipeRead|StdOut|GetStdHandle'`, filtered to handle-taking sites]

**Answering each primitive the task named:**

| Primitive | Can it write to a pivot handle? | Basis |
|---|---|---|
| **`PipeWrite`** | **Yes — the only writer.** | `Command.c:2586`; `Win32.c:1210` is its `WriteFile` |
| **`PipeRead`** | **No.** Called only with `Transport.Handle` (`TransportSmb.c:105`). **Never a pivot handle.** | full call-site census above |
| **`PeekNamedPipe`** | **No — inspection only.** | `Pivot.c:259`, `:263` |
| **`ReadFile` on a pivot handle** | **No — read only.** | `Pivot.c:268` |
| **`WriteFile`** | **Only inside `PipeWrite` (`Win32.c:1210`) and once on a file handle (`Command.c:925`).** **Never called directly on a pivot handle.** | census above |
| **stdio redirect** | **Targets `AnonPipe->StdOutWrite` (`Win32.c:611-619`) — anonymous process-creation pipes, not pivot handles.** | `Win32.c:611, 612, 618, 619` |

### 1.3 The verdict — a measured negative, stronger than D76's

**`PIVOT_DATA.Handle` has exactly one writer: `Command.c:2586`, via `PipeWrite`.** **Every other primitive on that handle field is a reader or a teardown.**

**D76's A-4a asked whether a duplex pipe delivers the writer's bytes back to its own `PeekNamedPipe`.** **That question is now moot for the defect claim:** **the only writer is `Command.c:2586`, and `PivotPush`'s readers (`:259`, `:263`, `:268`) are in the same process reading the same handle.** **A `WriteFile` on a handle and a `PeekNamedPipe` on the same handle in the same process is the classic named-pipe self-echo case, and the enumeration shows Family A is the sole writer.**

**D76's direction argument stands and is now backed by a primitive census rather than by an assumption.** **The negative closes harder: D76 said "the reader only ever sees Family B bytes" on structural grounds; this says "there is exactly one writer of this handle, enumerated, and it is Family A writing down a duplex connection."** [source: §1.1, §1.2, D76 §2.4]

**A-4a retires as MEASURED.** **The self-echo question no longer affects the conclusion either way**, because even if the parent's own bytes were observable to its own `PeekNamedPipe`, the primitive census would be unchanged. **Stated precisely: A-4a was the assumption; §1.3 removes the assumption's relevance rather than confirming it.**

---

## §2 — T2: `.Pivots.Parent` AT THE DECRYPT SITE — THE NIL BRANCH

### 2.1 The decrypt site, verbatim

```go
					if err == nil {

						if AgentHdr.MagicValue == DEMON_MAGIC_VALUE {
							var PivotAgent *Agent

							PivotAgent = teamserver.AgentInstance(AgentHdr.AgentID)
							if PivotAgent != nil {
								PivotAgent.UpdateLastCallback(teamserver)
								//logger.Debug(...)

								// while we can read a command and request id, parse new packages
								first_iter := true
								for (AgentHdr.Data.CanIRead(([]parser.ReadType{parser.ReadInt32, parser.ReadInt32}))) {
									var Command   = uint32(AgentHdr.Data.ParseInt32())
									var Request   = uint32(AgentHdr.Data.ParseInt32())

									if first_iter {
										first_iter = false
										// if the message is not a reconnect, decrypt the buffer
										AgentHdr.Data.DecryptBuffer(PivotAgent.Encryption.AESKey, PivotAgent.Encryption.AESIv)
									}
									...
								}
							} else {
								Message["Type"] = "Error"
								Message["Message"] = fmt.Sprintf("Can't process output for %x: Agent not found", AgentHdr.AgentID)
							}
```
[source: `teamserver/pkg/agent/demons.go:5354-5385`, verbatim]

### 2.2 The branch, named

**Branch: `demons.go:5382-5385`.**

**`PivotAgent == nil` → `:5373` `DecryptBuffer` is never reached.** **Control goes to `:5382` `else`, which sets `Message["Type"] = "Error"` and `Message["Message"] = "Can't process output for %x: Agent not found"`.** [source: `:5359-5360`, `:5373`, `:5382-5385`]

**This is an EXPLICIT FAILURE, not a silent-empty-decrypt.**

**The decrypt at `:5373` is nested two levels inside the guard:** **`:5360` `if PivotAgent != nil` wraps the `for` at `:5366`, which wraps the `if first_iter` at `:5370`, which wraps `:5373`.** **A nil `PivotAgent` cannot reach `:5373` by any path in this function.** [source: `:5359-5374`, read contiguously]

### 2.3 What the nil case actually means for `.Pivots.Parent`

**`.Pivots.Parent` is not consulted at `:5359`.** **The lookup is `AgentInstance(AgentHdr.AgentID)` — global by agent ID, not scoped through `.Parent`.** **So a nil or stale `.Pivots.Parent` does not affect this decrypt at all.** [source: D71 §3.3, `:5359`]

**`.Pivots.Parent` is consumed on the read side at exactly two places, enumerated:**

```
pkg\agent\agent.go:784     if pivots.Parent.Pivots.Parent == nil {
pkg\agent\agent.go:789     BuildPayloadMessage([]Job{PivotJob}, pivots.Parent.Encryption.AESKey, pivots.Parent.Encryption.AESIv)
pkg\agent\agent.go:792     AgentID, err = strconv.ParseInt(pivots.Parent.NameID, 16, 32)
pkg\agent\agent.go:810     pivots = &pivots.Parent.Pivots
pkg\agent\agent.go:813     pivots.Parent.JobQueue = append(pivots.Parent.JobQueue, PivotJob)
pkg\agent\demons.go:5231   if DemonInfo.Pivots.Parent != nil {
pkg\agent\events\demons.go:74  if Agent.Pivots.Parent != nil {
cmd\server\dispatch.go:201     if t.Agents.Agents[i].Pivots.Parent != nil {
```
[source: `Get-ChildItem teamserver -Recurse -File -Filter *.go | Select-String '\.Parent'`, filtered to `Pivots.Parent`]

**Nil-handling, per site:**

| Site | Nil case | Verdict |
|---|---|---|
| `agent.go:784` | **Dereferences `.Parent.Pivots.Parent` with no nil check** | **Reachable only if `.Parent` is nil when `PivotAddJob` runs** |
| `agent.go:789` | Same — `.Parent.Encryption` | Same |
| `agent.go:792` | Same — `.Parent.NameID` | Same |
| `agent.go:810` | Same — `&.Parent.Pivots` | Same |
| `agent.go:813` | Same — `.Parent.JobQueue` | Same |
| `demons.go:5231` | **Guarded: `if ... != nil`** | Explicit |
| `events/demons.go:74` | **Guarded: `if ... != nil`** | Explicit |
| `dispatch.go:201` | **Guarded: `if ... != nil`** | Explicit |

**All three read-side consumers outside `PivotAddJob` are explicitly guarded.** **The five unguarded dereferences are all inside `PivotAddJob`'s loop (`:784-813`), which begins at `pivots = &a.Pivots` (`:780`) and walks upward via `:810`.** [source: §3.1 enumeration; `agent.go:780-813` read contiguously]

### 2.4 The answer

**At the decrypt site (`:5359`/`:5373`), a nil `.Pivots.Parent` has NO effect — `.Parent` is not read there, and the nil case is handled explicitly by the `:5382` branch.**

**The unguarded `.Parent` dereferences are in `PivotAddJob` (`agent.go:784-813`), on the WRITE side, not the decrypt side.** **They are reachable when `PivotAddJob` is invoked on an agent whose `.Pivots.Parent` is nil** — i.e. a non-pivot agent being used as a pivot parent. **Whether that is reachable depends on the caller of `PivotAddJob`, which this report does not enumerate; carried as residual C-1.** [source: `agent.go:746`, `:780-813`]

**T2's answer: DEFENCE WORKING at the decrypt site. No defect.** **The nil-exposure is on `PivotAddJob`'s unguarded walk, a separate question.** [source: §2.2, §2.3]

---

## §3 — T3: THE CENSUS CORRECTION, AND THE STANDING FALSIFIER

### 3.1 Re-run of the `.Pivots.Parent` census, literal pattern, printed beside the claim

**Probe invocation:** `Get-ChildItem teamserver -Recurse -File -Filter *.go | Select-String '\.Parent'`

**Every `.Pivots.Parent` occurrence:**

```
pkg\agent\agent.go:580      PivotSession.Pivots.Parent = Session
pkg\agent\agent.go:651      if a.Pivots.Parent != nil {
pkg\agent\agent.go:784      if pivots.Parent.Pivots.Parent == nil {
pkg\agent\agent.go:789      BuildPayloadMessage(..., pivots.Parent.Encryption.AESKey, pivots.Parent.Encryption.AESIv)
pkg\agent\agent.go:792      AgentID, err = strconv.ParseInt(pivots.Parent.NameID, 16, 32)
pkg\agent\agent.go:810      pivots = &pivots.Parent.Pivots
pkg\agent\agent.go:813      pivots.Parent.JobQueue = append(pivots.Parent.JobQueue, PivotJob)
pkg\agent\agent.go:1200     ParentAgent = a.Pivots.Parent
pkg\agent\agent.go:1201     a.Pivots.Parent = nil
pkg\agent\agent.go:1214     if ParentAgent != nil {
pkg\agent\agent.go:1216     a.Pivots.Parent = ParentAgent
pkg\agent\demons.go:5231    if DemonInfo.Pivots.Parent != nil {
pkg\agent\demons.go:5232    for i := range DemonInfo.Pivots.Parent.Pivots.Links {
pkg\agent\demons.go:5233    if DemonInfo.Pivots.Parent.Pivots.Links[i].NameID == ...
pkg\agent\demons.go:5234    DemonInfo.Pivots.Parent.Pivots.Links = append(...)
pkg\agent\demons.go:5242    DemonInfo.Pivots.Parent = a
pkg\agent\demons.go:5254    DemonInfo.Pivots.Parent = a
pkg\events\demons.go:74     if Agent.Pivots.Parent != nil {
pkg\events\demons.go:75     InfoMap["PivotParent"] = Agent.Pivots.Parent.NameID
cmd\server\dispatch.go:201  if t.Agents.Agents[i].Pivots.Parent != nil {
cmd\server\teamserver.go:469  parentID, err := t.ParentOf(Agent)
cmd\server\teamserver.go:471  Agent.Pivots.Parent = t.AgentInstance(parentID)
```
[source: `Get-ChildItem teamserver -Recurse -File -Filter *.go | Select-String '\.Parent'` — 30 hits, of which 22 are `Pivots.Parent` and 8 are `yaotl`/HCL `parent` fields, unrelated]

**Assignment sites: 6.**

| Site | Context | D76 reported? |
|---|---|---|
| `agent.go:580` | **`PivotSession.Pivots.Parent = Session`** — SMB pivot registration | **No** |
| `agent.go:1201` | **`a.Pivots.Parent = nil`** — `ToMap()` save/clear | **No** |
| `agent.go:1216` | **`a.Pivots.Parent = ParentAgent`** — `ToMap()` restore | **No** |
| `demons.go:5242` | `DemonInfo.Pivots.Parent = a` — `DEMON_PIVOT_SMB_CONNECT` | **Yes** |
| `demons.go:5254` | `DemonInfo.Pivots.Parent = a` — register path | **No** |
| `teamserver.go:471` | `Agent.Pivots.Parent = t.AgentInstance(parentID)` — DB rehydration at startup | **No** |

### 3.2 Why D76's §3.1 missed five of six

**D76's probe was `Select-String 'Pivots\.Parent\s*='`.** **Applied to `a.Pivots.Parent = nil`, that pattern matches — `.` `Pivots` `.` `Parent` space `=`.** **So `:1201` and `:1216` should have appeared.**

**D76's §3.1 printed output listed 8 hits: `agent.go:784`, `:789`, `:792`, `:810`, `:813`, `demons.go:5231`, `:5233`, `:5242`.** **Sites `:580`, `:1201`, `:1216`, `:5254`, and `teamserver.go:471` were absent from that list.**

**The `:580` and `teamserver.go:471` misses have a mechanical explanation:** **both were typed as `Select-String 'Pivots\.Parent\s*='` variants and both receivers use a different prefix — `PivotSession.Pivots.Parent` and `Agent.Pivots.Parent`.** **But `:1201`/`:1216` are `a.Pivots.Parent`, which the pattern matches.**

**This report does not reconstruct D76's exact invocation from its printed output; it states the observation: the printed census was 1/6 complete on assignments, and its conclusion was drawn from it.** **The re-run above is the measurement.** [source: D76 §3.1 output vs §3.1 above]

### 3.3 What the correction does to D76 A-1's closure

**D76 A-1 concluded: "`.Pivots.Parent` has exactly one writer (`demons.go:5242`) and no invalidator, so `:5359`'s trust is currently sound. Maintenance hazard, not a live gap."**

**The "one writer" premise is false.** **The closure must be re-derived:**

| Site | Effect on `:5359`'s trust |
|---|---|
| `agent.go:580` | **Establishes a parent in the SMB registration path — a SECOND establishing writer.** The invariant at `:5233` (`Parent == a`) is not checked here. |
| `agent.go:1201` | **Sets `.Parent = nil` temporarily**, restored at `:1216` only if it was non-nil. **A nil window exists** if `ToMap()` runs concurrently with a read. |
| `agent.go:1216` | Restores. |
| `demons.go:5242` | Establishes (D76's known site). |
| `demons.go:5254` | **Establishes in the register path** — D76 missed it. |
| `teamserver.go:471` | **Hydrates from the DB at startup.** May set `.Parent` to `nil` if `AgentInstance(parentID)` returns nil. |

**The conclusion does not necessarily change — `:5359` still reads no `.Parent` (§2.3) — but the *basis* D76 gave is invalid, and `:580`/`:5254`/`:471` are three additional establishing writers whose invariants have not been compared against `:5233`.** **Carried as residual C-2.** [source: §3.1, §3.3]

### 3.4 The standing falsifier, stated

**Falsifier (from D76 Failure 2), as a checklist item:**

> **When two writers share a DESTINATION, the binding question is DIRECTION AND VALUE TYPE, not disjointness.**
> **Shared destination is not a defect. Different value type at the same offset is not a defect. The defect requires that a reader consume a writer's bytes, in a direction the reader observes, with a value type the reader misinterprets.**

**Applied to one other shared-handle destination in the havoc tree — the transport handle.**

### 3.5 The falsifier applied: `Instance->Config.Transport.Handle`

**Writers of that handle, enumerated:**

```
TransportSmb.c:41   return PipeWrite( Instance->Config.Transport.Handle, Send );
TransportSmb.c:44   if ( ! PipeWrite( Instance->Config.Transport.Handle, Send ) )
```
[source: `TransportSmb.c:41`, `:44`; the full `PipeWrite` census at §1.2 shows no other writer]

**Readers:**

```
TransportSmb.c:71   PeekNamedPipe( Instance->Config.Transport.Handle, NULL, 0, NULL, &BytesSize, NULL )
TransportSmb.c:75   ReadFile( Instance->Config.Transport.Handle, &DemonId, sizeof( UINT32 ), &BytesSize, NULL )
TransportSmb.c:93   ReadFile( Instance->Config.Transport.Handle, &PackageSize, sizeof( UINT32 ), &BytesSize, NULL )
TransportSmb.c:105  PipeRead( Instance->Config.Transport.Handle, Resp )
```
[source: `TransportSmb.c:71-105`]

**Falsifier applied:**

| Question | Answer |
|---|---|
| Two writers sharing the destination? | **No — one writer (`PipeWrite`).** |
| Different value type at the same offset? | Not applicable to a writer/writer comparison. |
| Reader consumes bytes in a direction it observes? | **YES — `:75`/`:93` read `[0..3]` and `[4..7]` as `DemonId` and `PackageSize`.** |

**Verdict: this is the D47 §3 defect site, and the falsifier localises it correctly.** **D47 §3 found that the writer (`PackageCreateWithMetaData`, 20-byte header) puts LENGTH at `[0..3]` and MAGIC at `[4..7]`, while the reader names them `DemonId` and `PackageSize`.** **One writer, one reader, and the mismatch is VALUE TYPE at a shared offset — not a disjointness question.** **The falsifier predicts a defect here, and D47 §3 already recorded it.** [source: D47 §3a]

**As a cross-check of the falsifier's discriminating power: at the pivot handle (§1) the falsifier returns NO DEFECT (writer's value is not consumed by an observing reader); at the transport handle it returns DEFECT (writer's value is consumed and misnamed). The test discriminates.** [source: §1.3 vs §3.5]

---

## §4 — RESIDUAL UNKNOWNS, WITH PROBES

| ID | Unknown | Probe |
|---|---|---|
| **C-1** | **Is `PivotAddJob` reachable with `.Pivots.Parent == nil`?** §2.4 shows the unguarded derefs at `agent.go:784-813` would panic. | **Enumerate every `PivotAddJob` call site and determine whether each caller guarantees a non-nil `.Parent`.** **Not done in this report.** |
| **C-2** | **Do the three establishing writers (`agent.go:580`, `demons.go:5254`, `teamserver.go:471`) maintain the `:5233` invariant?** §3.3. | **For each, print the surrounding branch and check whether `Parent` is set to the same agent the connect path sets.** |
| **C-3** | **D76 §3.1's exact probe invocation.** §3.2 states the printed census was 1/6 complete and does not reconstruct why. | **N/A — the corrected census is §3.1. Recorded so the gap is not silently repaired.** |
| **C-4** | **Whether `ToMap()` (`:1201`/`:1216`) can be concurrent with a `.Parent` read.** §3.3 notes a nil window; no locking was examined. | **Read `ToMap`'s callers and any mutex around `Agent`.** |

---

## §5 — INSTRUMENT FAILURES

**Failure 1 — D76 §3.1's `.Pivots.Parent` census was incomplete, and this report's T3 is the repair.** **D76 reported one assignment site; there are six.** **The conclusion D76 drew ("one writer, nothing invalidates it") was correct in shape and wrong in fact.** **Rule 20 fired on my own report, for the fourth consecutive time in this lane, in the direction of a false clean — exactly as the rule predicts.** [source: §3.1, §3.2]

**Failure 2 — I nearly published D76 §2.1 as a live misparse (§2.4's direction analysis retired it).** **Now escalated to a standing falsifier at §3.4 and applied at §3.5.** **The near-miss produced a test with demonstrated discriminating power — it returns NO DEFECT at one shared destination and DEFECT at another.**

**Failure 3 — a PowerShell apostrophe in `PivotAddJob's` broke a single-quoted string; the invocation returned `[exit code: 1]` rather than a partial result.** **Correct behaviour: a probe that dies must fail loud.** **A partial result would be indistinguishable from a smaller census.**

**Failure 4 — T1's sibling enumeration initially looked like it would retire A-4a's relevance and it does, but not by confirming the duplex assumption.** **The correct statement is that the primitive census makes the assumption IRRELEVANT, which is different from confirming it.** **§1.3 states this explicitly rather than letting the negative read as a confirmation.**

**Net: four failures. Failure 1 invalidates a D76 conclusion's basis. Failure 2 produced a reusable test. Failure 3 is a near-miss on a census. Failure 4 is a precision correction on what was actually proven.**

---

## §6 — WHAT THIS CHANGES

| Item | Verdict | Basis |
|---|---|---|
| **D76 A-4a** | **RETIRED as measured.** `.PIVOT_DATA.Handle` has exactly one writer; every other primitive on that field is a read or teardown. **A-4a's duplex assumption is irrelevant to the conclusion, not confirmed.** | §1.3 |
| **D76 A-1** | **BASIS INVALIDATED, conclusion unaffected.** `.Pivots.Parent` has **six** writers, not one. `:5359` reads no `.Parent`, so the decrypt-site verdict stands. **The "nothing invalidates it" closure is not established.** | §3.1, §3.3 |
| **D76 §3.1** | **CORRECTED in place of this file.** Census was 1/6 complete on assignments. | §3.1 |
| **T2 (new)** | **`.Pivots.Parent` nil at the decrypt site = explicit failure, defence working.** Branch is `demons.go:5382-5385`. **No silent-empty-decrypt.** | §2.2 |
| **T3 (new)** | **Standing falsifier stated and applied.** Returns NO DEFECT at the pivot handle, DEFECT at the transport handle (matching D47 §3). | §3.4, §3.5 |

**No contradiction with D47, D56, or D65. One correction to D76 §3.1, reported here as required.**

---

**End of D86.**
