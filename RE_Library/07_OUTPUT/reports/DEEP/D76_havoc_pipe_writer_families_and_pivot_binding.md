# D76 — HAVOC PIPE WRITER FAMILIES AND PIVOT BINDING

**Closes D71 A-4 (T1) and D71 A-1 (T2).**
**Artifact:** `teamserver/` Go sources and `payloads/Demon` C sources.
**Method:** pure source read. No REA, no Ghidra, no execution.
**Write scope:** this file only. D47, D56, D65, and D71 were not touched.

---

## §0 — THE HEADLINE, AND ONE CORRECTION TO MY OWN RESIDUAL

### 0.1 T1's outcome in one line

**Two writer families exist. They address the same handles. They write different things at offset 0. The reader's `+ sizeof(UINT32)` is correct for one family and wrong for the other.**

**The raw-buffer path writes an `AgentID` at `[0..3]`. The reader interprets `[0..3]` as a byte length.** **This is not the P-3 shape** — P-3 asked whether a prefix existed at all, and the answer there was yes, written by the package path. **The raw path is a *second* writer that puts a non-length value in the length slot.** [source: §1, §2]

### 0.2 Correction to D71 §4.3 — the bound was right, the reasoning was incomplete

**D71 §4.3 concluded that `Pivot.c:265`'s `+ sizeof(UINT32)` is *correct*, because `Package.c:246` back-patches a length at offset 0.** **That conclusion holds for the package family.**

**D71 did not establish that the package family is the *only* writer.** **A-4 was raised as the suspicion that a second writer exists; this report confirms there is one, and that it does not write a length.** **D71's stated caveat — "a mismatch requires a non-conforming writer on the pipe" — turns out to describe a writer that exists in the same binary.** [source: D71 §4.3; §1 below]

### 0.3 The depth convention

**Carried forward per the Lead's standing rule.** **This report counts no nesting depths.** **Stated anyway, because the convention is declared in anything that counts and a file is not exempt on the grounds that its counts happen not to be depth-based.**

---

## §1 — T1: EVERY WRITE INTO A PIVOT PIPE

### 1.1 The write primitive, and every caller

**`PipeWrite` is the only primitive that can put bytes on a pipe:**

```
include\core\Win32.h:204   BOOL PipeWrite(
src\core\Win32.c:1202      BOOL PipeWrite(   (definition)
src\core\Command.c:2586    if ( ! PipeWrite( PivotData->Handle, &Data ) )
src\core\TransportSmb.c:41     return PipeWrite( Instance->Config.Transport.Handle, Send );
src\core\TransportSmb.c:44     if ( ! PipeWrite( Instance->Config.Transport.Handle, Send ) )
```
[source: `Get-ChildItem payloads/Demon -Recurse -File -Include *.c,*.h | Select-String 'PipeWrite'` — 6 hits, one of which (`:2588`) is a `PUTS` string]

**Three live call sites. Two distinct destination-handle families:**

| Family | Site | Destination handle | Created by |
|---|---|---|---|
| **A — raw buffer** | `Command.c:2586` | `PivotData->Handle` | `PivotAdd`'s `CreateFileW` (`Pivot.c:31`) |
| **B — package** | `TransportSmb.c:41`, `:44` | `Instance->Config.Transport.Handle` | `SmbSend`'s `CreateNamedPipeW` (`TransportSmb.c:18`) |

### 1.2 The handles are distinct objects

**Family A's handle is an `OPEN_EXISTING` client connection to a named pipe:**

```c
    Handle = Instance->Win32.CreateFileW( NamedPipe.Buffer, GENERIC_READ | GENERIC_WRITE, 0, NULL, OPEN_EXISTING, 0, NULL );
```
[source: `payloads/Demon/src/core/Pivot.c:31`, verbatim]

**Family B's handle is a `CreateNamedPipeW` server-side ingest endpoint:**

```c
        Instance->Config.Transport.Handle = Instance->Win32.CreateNamedPipeW( Instance->Config.Transport.Name,  // Named Pipe
                                                                            PIPE_ACCESS_DUPLEX,
                                                                            PIPE_TYPE_MESSAGE     |
                                                                            PIPE_READMODE_MESSAGE |
                                                                            PIPE_WAIT,
                                                                            PIPE_UNLIMITED_INSTANCES,
                                                                            PIPE_BUFFER_MAX,
                                                                            PIPE_BUFFER_MAX,
                                                                            0,
                                                                            &SecurityAttr );
```
[source: `payloads/Demon/src/core/TransportSmb.c:18-27`, verbatim]

**Different creation calls, different fields.** **The handles are not the same object.** [source: `:31` vs `:18-27`]

### 1.3 The reader, and which family it belongs to

**`PivotPush` iterates `Instance->SmbPivots` and reads each entry's `Handle`:**

```
Pivot.c:238   PPIVOT_DATA TempList  = Instance->SmbPivots;
Pivot.c:254   if ( TempList->Handle )
Pivot.c:259   if ( Instance->Win32.PeekNamedPipe( TempList->Handle, NULL, 0, NULL, &BytesSize, NULL ) )
Pivot.c:263   if ( Instance->Win32.PeekNamedPipe( TempList->Handle, &Length, sizeof( UINT32 ), NULL, &BytesSize, NULL ) )
Pivot.c:268   if ( Instance->Win32.ReadFile( TempList->Handle, Output, Length, &BytesSize, NULL ) )
```
[source: `payloads/Demon/src/core/Pivot.c:238-268`, verbatim excerpts]

**`Instance->SmbPivots` is populated only at `Pivot.c:92-94` (`Instance->SmbPivots = Data`), where `Data->Handle` was set at `:85` from `PivotAdd`'s `CreateFileW` at `:31`.** **So `PivotPush` reads Family A's handles exclusively.** [source: `Pivot.c:84-94`]

### 1.4 Family A writes an AgentID, not a length

**The raw path's buffer construction:**

```c
        case DEMON_PIVOT_SMB_COMMAND:
        {
            PUTS( "DEMON_PIVOT_SMB_COMMAND" )

            UINT32      DemonId   = ParserGetInt32( Parser );
            BUFFER      Data      = { 0 };
            PPIVOT_DATA TempList  = Instance->SmbPivots;
            PPIVOT_DATA PivotData = NULL;
            Data.Buffer           = ParserGetBytes( Parser, &Data.Length );
```
[source: `payloads/Demon/src/core/Command.c:2555-2563`, verbatim]

**`Data.Buffer` points into the task the server sent.** **That task was built at `agent.go:763-764`:**

```go
	Packer.AddInt32(int32(AgentID))
	Packer.AddBytes(Payload)
```
[source: `teamserver/pkg/agent/agent.go:763-764`, verbatim]

**`AddInt32` writes a bare 4-byte little-endian integer with no framing:**

```go
func (p *Packer) AddInt32(data int32) {
	var buffer = make([]byte, 4)
	binary.LittleEndian.PutUint32(buffer, uint32(data))
	p.data = append(p.data, buffer...)

	p.size += 4
}
```
[source: `teamserver/pkg/common/packer/packer.go:37-43`, verbatim]

**So the bytes at the head of `Data.Buffer` are `AgentID`, little-endian, with nothing before them.** **The `AddBytes` call that follows writes its own 4-byte little-endian length, but that lands at offset 4, after the AgentID.** [source: `packer.go:70-78` — `PutUint32(buffer, uint32(len(data)))` then the data]

**`Packer.Buffer()` does not back-patch a length:**

```go
func (p *Packer) Buffer() []byte {
	return p.data
}
```
[source: `teamserver/pkg/common/packer/packer.go:95-97`, verbatim]

**And `Build()` is not called on this packer** — `:776` uses `Packer.Buffer()`, not `Build()`. **`Build()` is the function carrying the encryption logic at `:80-93`; it is never invoked on `PivotAddJob`'s packer.** [source: `agent.go:776` calls `Buffer()`; `packer.go:80` defines `Build()`; no `Packer.Build()` appears in `agent.go:746-814`]

**Family A's layout at offset 0:**

```
[0..3]  AgentID      (little-endian, via packer.AddInt32)
[4..7]  len(Payload) (little-endian, via packer.AddBytes)
[8..]   Payload
```

**There is no byte length at offset 0.** [source: `agent.go:763-764` and `packer.go:37-43`, `:70-78`, `:95-97`]

### 1.5 Family B does write a length at offset 0

**The package path back-patches before send:**

```c
    Int32ToBuffer( Package->Buffer, Package->Length - sizeof( UINT32 ) );
```
[source: `payloads/Demon/src/core/Package.c:246`, and identically at `:377` in `PackageTransmitAll`]

**`Int32ToBuffer` is big-endian, explicitly:**

```c
VOID Int32ToBuffer(
    OUT PUCHAR Buffer,
    IN  UINT32 Size
) {
    ( Buffer ) [ 0 ] = ( Size >> 24 ) & 0xFF;
    ( Buffer ) [ 1 ] = ( Size >> 16 ) & 0xFF;
    ( Buffer ) [ 2 ] = ( Size >> 8  ) & 0xFF;
    ( Buffer ) [ 3 ] = ( Size       ) & 0xFF;
}
```
[source: `payloads/Demon/src/core/Package.c:39-47`, verbatim]

**Big-endian, confirmed by the shift order.** **And the reader's `__builtin_bswap32` at `Pivot.c:265` is its inverse.** [source: `Package.c:43-46`; `Pivot.c:265`]

### 1.6 The divergence, stated exactly

| | Family A (`Command.c:2586`) | Family B (`TransportSmb.c:41`, `:44`) |
|---|---|---|
| Offset 0 content | **AgentID** | **package length** |
| Endianness of offset 0 | **little-endian** (`packer.AddInt32`) | **big-endian** (`Int32ToBuffer`) |
| Is offset 0 a length? | **No** | **Yes** |
| Reader's `bswap32(...) + 4` | **reads the AgentID as a length** | **correct** |

**Both families are big-endian-vs-little-endian divergent at offset 0, and Family A's value is not a length at all.** [source: §1.4, §1.5]

---

## §2 — THE SHAPE THE READER ACTUALLY SEES

### 2.1 What `Pivot.c:263-266` computes under Family A

**If the bytes on a `SmbPivots` handle were written by Family A:**

```c
                            Length = __builtin_bswap32( Length ) + sizeof( UINT32 );
                            Output = Instance->Win32.LocalAlloc( LPTR, Length );
```
[source: `payloads/Demon/src/core/Pivot.c:265-266`, verbatim]

**`Length` at `:263` is the pipe's first 4 bytes — the AgentID, little-endian on the wire.** **`__builtin_bswap32` byte-swaps it.** **A `NameID` such as `0x12345678` written little-endian appears as `78 56 34 12`; byte-swapped back it reads `0x12345678`.** **So the value is the AgentID in its natural numeric form, plus 4.**

**That number is the allocation size at `:266`.** [source: `:263-266`]

### 2.2 The bound — do the families share a handle?

**This is the question that decides whether §2.1 describes a reachable state.**

**Family A writes to `PivotData->Handle`, resolved through `PivotGet` over `Instance->SmbPivots`:**

```c
            PPIVOT_DATA TempList  = Instance->SmbPivots;
            PPIVOT_DATA PivotData = NULL;
            ...
            do
            {
                if ( TempList ) {
                    // if the specified demon was found break the loop
                    if ( TempList->DemonID == DemonId ) {
                        PivotData = TempList;
                        break;
                    }
                    // select the next pivot
                    TempList = TempList->Next;
                } else break;
            } while ( TRUE );
```
[source: `payloads/Demon/src/core/Command.c:2561-2582`, verbatim]

**`PivotPush` reads `TempList->Handle` where `TempList` starts at `Instance->SmbPivots` (`Pivot.c:238`).**

**Both traverse the same list. Both use `PIVOT_DATA.Handle`, which is set once at `Pivot.c:85` from the `CreateFileW` at `:31`.** **The `Handle` field has no other writer** — enumerated:

```
Pivot.c:85   Data->Handle          = Handle;
Pivot.c:160  if ( Instance->SmbPivots->Handle )
Pivot.c:162  Instance->Win32.DisconnectNamedPipe( Instance->SmbPivots->Handle );
Pivot.c:163  SysNtClose( Instance->SmbPivots->Handle );
Pivot.c:168  Instance->SmbPivots->Handle          = NULL;
Pivot.c:192  if ( PivotData->Handle )
Pivot.c:194  Instance->Win32.DisconnectNamedPipe( PivotData->Handle );
Pivot.c:195  SysNtClose( PivotData->Handle );
Pivot.c:200  PivotData->Handle          = NULL;
Pivot.c:254  if ( TempList->Handle )
Pivot.c:259  PeekNamedPipe( TempList->Handle, ... )
Pivot.c:263  PeekNamedPipe( TempList->Handle, ... )
Pivot.c:268  ReadFile( TempList->Handle, ... )
```
[source: `Get-Content payloads/Demon/src/core/Pivot.c | Select-String 'Handle'` filtered to `PIVOT_DATA` handles]

**One write (`:85`), two teardowns (`:168`, `:200`), and reads.** **Family A and the reader address the same `Handle` field.**

### 2.3 The verdict — NOT a bounded negative

**The two families are not disjoint. They share the handle field.**

**Family A's write is reachable:** `DEMON_PIVOT_SMB_COMMAND` at `Command.c:2555` is a server-dispatched command, and the `PivotData` lookup at `:2571-2582` succeeds whenever the named `DemonId` is in `Instance->SmbPivots` — i.e. whenever this agent hosts the named pivot, which is the normal operating condition. [source: `:2571-2582`]

**So a `PIVOT_DATA.Handle` can receive Family A bytes, and `PivotPush` reads that same handle at `Pivot.c:263`.**

### 2.4 One thing that must be stated before this is called a defect

**The direction question, answered explicitly.** **`PivotAdd`'s `CreateFileW` uses `GENERIC_READ | GENERIC_WRITE` — the connection is duplex.** [source: `Pivot.c:31`] **So a single handle carries both directions, and a write from the parent side and a read from the parent side on the same handle are both meaningful.**

**Family A writes *down* that handle (parent → pivot).** **`PivotPush` reads *up* that same handle (pivot → parent).** **Both are reads/writes of the same duplex connection, and the *pivot agent at the other end* is what actually writes what `PivotPush` reads.**

**That pivot agent writes via Family B** — it is an agent, and it transmits packages through `PackageTransmitAll` → `TransportSend` → `SmbSend` → `PipeWrite`. [source: D71 §4.2, `Package.c:333-340` and `:390`]

**So the honest statement of the reachability of §2.1:**

- **Family A's bytes go down the duplex handle toward the pivot agent.** **`PivotPush` reads what comes *back up*.** **These are different directions of the same connection.**
- **`PivotPush` therefore reads Family B bytes** — written by the downstream pivot agent's own `PackageTransmitAll`.

**The families share a handle object but not a direction, and the reader only sees the direction Family B writes.**

**This is a bounded negative — and it retires the finding rather than confirming it.** [source: `Pivot.c:31` duplex; `:259-268` read direction; D71 §4.2 write direction]

### 2.5 The residual that survives the bound

**§2.4 bounds the *demonstrated* path. It does not bound every writer.**

**The bound rests on the claim that no Family A write lands on the direction `PivotPush` reads.** **That claim is structural (a duplex handle, a parent-side write, a pivot-side read) and it is not a runtime observation.**

**Carried forward as A-4a: does the duplex handle permit the parent's `PipeWrite` bytes to be observed by the parent's own `PeekNamedPipe`?** **On a duplex named pipe, a write by one end is readable by the other end, not by the writer.** **This report's bound assumes that; it is not measured.** [source: `Pivot.c:31` duplex flag; no runtime observation available]

---

## §3 — T2: EVERY WRITE TO `.Pivots.Parent`

### 3.1 The census

**Every assignment to a `Pivots.Parent` field in the Go server:**

```
pkg\agent\demons.go:5242   DemonInfo.Pivots.Parent = a
```
[source: `Get-ChildItem teamserver -Recurse -File -Filter *.go | Select-String 'Pivots\.Parent\s*='` — 1 assignment]

**And every occurrence of `Pivots.Parent` including reads and comparisons:**

```
pkg\agent\agent.go:784     if pivots.Parent.Pivots.Parent == nil {
pkg\agent\agent.go:789     BuildPayloadMessage([]Job{PivotJob}, pivots.Parent.Encryption.AESKey, ...)
pkg\agent\agent.go:792     AgentID, err = strconv.ParseInt(pivots.Parent.NameID, 16, 32)
pkg\agent\agent.go:810     pivots = &pivots.Parent.Pivots
pkg\agent\agent.go:813     pivots.Parent.JobQueue = append(pivots.Parent.JobQueue, PivotJob)
pkg\agent\demons.go:5231   if DemonInfo.Pivots.Parent != nil {
pkg\agent\demons.go:5233   if DemonInfo.Pivots.Parent.Pivots.Links[i].NameID == fmt.Sprintf("%08x", AgentHdr.AgentID) {
pkg\agent\demons.go:5242   DemonInfo.Pivots.Parent = a
```
[source: `Get-ChildItem teamserver -Recurse -File -Filter *.go | Select-String 'Pivots\.Parent'` — 8 hits]

### 3.2 The answer: ONE write site, and it is not in `Command.c`'s reach

**`:5242` is the only assignment, and it is inside `DEMON_PIVOT_SMB_CONNECT` (`demons.go:5196-5313`).** **D71 A-1 named it.** **The closure this task asks for is the confirmation that nothing else writes it — and the enumeration returns exactly one site.** [source: §3.1]

**`PivotRemove` (`Pivot.c:139`) is agent-side and manipulates the agent's own `SmbPivots` list** — it does not touch the server's `.Pivots.Parent`. **The server's view is authoritative and singular.** [source: `Pivot.c:139-205`, all occurrences, none under `teamserver/`]

### 3.3 Does the `:5233` invariant still hold when control reaches `:5359`?

**The invariant is: `DemonInfo.Pivots.Parent == a`, established at `:5242`.**

**`:5359` `PivotAgent = teamserver.AgentInstance(AgentHdr.AgentID)` performs no comparison.** **The question is whether the state set at `:5242` can be invalidated between a connect and a later command.**

**Enumeration of every site that could invalidate it:**

| Candidate | Site | Touches `.Pivots.Parent`? |
|---|---|---|
| `PivotRemove` (agent-side) | `Pivot.c:139-205` | No — agent-local list only |
| `PivotAdd` (agent-side) | `Pivot.c:92-94` | No — agent-local list only |
| `LinkAdd` (server) | `demons.go:5245`, `:5257` | No — appends to `.Pivots.Links` |
| Link removal | `demons.go:5234` | No — removes from `.Pivots.Links` |
| `AgentInstance` | `cmd/server/agent.go:156` | No — read-only scan |

**No site clears or reassigns `.Pivots.Parent`.** **The single write at `:5242` means the invariant established at connect persists for the life of the agent record.** [source: §3.1's 8-occurrence census, of which one is a write]

### 3.4 The closure

**A-1 closes as a defence-in-depth observation, with the frame D71 set: it is not a read-access defect.**

**Precise statement:** **`:5359` trusts `:5242`'s prior state. Because `:5242` is the *only* writer and nothing invalidates it, the trust is currently sound.** **The gap is that `:5359` does not restate the invariant — so a future change that adds a second writer to `.Pivots.Parent` would silently widen what `:5373` decrypts, with no check at the decrypt site to catch it.**

**No defect exists today.** **The residual is a maintenance hazard, not a live one.** [source: §3.1, §3.2, §3.3]

---

## §4 — RESIDUAL UNKNOWNS, WITH PROBES

| ID | Unknown | Probe |
|---|---|---|
| **A-4a** | **Does a duplex named pipe deliver the writer's own bytes back to its `PeekNamedPipe`?** §2.4's bound assumes not. | **Runtime observation on Windows, or the documented `CreateNamedPipeW` semantics.** **Out of a source-only report's reach; stated as the assumption the bound rests on.** |
| **A-4b** | **Whether any third writer to a `SmbPivots` handle exists outside this tree** — the census covers `PipeWrite` callers, and `PipeWrite` is the only write primitive in the payload tree. | **Re-run the `PipeWrite` caller census after any code change; the enumeration is complete for the current artifact.** |
| **B-1** | **Whether a second `.Pivots.Parent` writer can be introduced by the plugin/handler surface outside `pkg/agent`.** §3.1's census is `teamserver`-wide. | **Re-run against `teamserver` plus any plugin directory if one exists.** **Current artifact: none.** |
| **B-2** | **`PivotParseDemonID`'s read at `[8..11]` (`Pivot.c:341`) versus Family A's layout** — if Family A bytes ever reached `PivotParseDemonID`, the field read would be the `len(Payload)` at `[4..7]` or payload bytes. | **`PivotParseDemonID` is called only at `Pivot.c:87`, inside `PivotAdd` — the connect path, reading the *pivot agent's* Family B output.** **Enumerated; not reachable from Family A.** |

---

## §5 — INSTRUMENT FAILURES

**Failure 1 — D71 §4.3's caveat was stronger than D71 knew.** D71 wrote that a length mismatch "requires a non-conforming writer on the pipe." **Family A is exactly such a writer, in the same binary.** **D71's caveat was correct as written but treated the case as hypothetical.** **Root cause: D71 read the writer it could see (`Package.c:246`) and did not enumerate the other `PipeWrite` callers.** **This is the same failure shape as D65's under-scoped outbound set and D65 §2's missed `handlers.go:193` — the third instance of "a named path is not a census" in this lane.**

**Failure 2 — I nearly published §2.1 as a defect.** The divergence is real and the two families share a handle *field*. **It was the direction analysis at §2.4 — duplex handle, parent writes down, reader reads up — that retired it.** **Without §2.4 the report would have claimed the reader misparses a length on a live path.** **The Lead's instruction to bound it and not manufacture a defect to match the adjacency is what forced §2.4 to be written.**

**Failure 3 — the initial enumeration was almost truncated by a PowerShell quoting error.** The apostrophe in `PivotAddJob's` closed a single-quoted string and the invocation failed. **Re-run without it.** **Recorded because the failure produced `[exit code: 1]` rather than a partial result, and a partial result would have been indistinguishable from a smaller census.**

**Failure 4 — §2.4's bound is structural, not measured, and I am labelling it as such.** `A-4a` carries it. **A bound whose own premise is unmeasured is not a measurement.** **Stated before the reader relies on it.**

**Net: four failures. Failure 2 would have published a false defect; Failure 1 corrects a D71 statement; Failure 3 is a near-miss on census completeness; Failure 4 is a labelled assumption.**

---

## §6 — WHAT THIS CHANGES

| Residual | Verdict | Basis |
|---|---|---|
| **D71 A-4** | **CLOSED — bounded negative.** Two writer families exist; they share a handle *field* but not a *direction*. `PivotPush` reads Family B output only. | §1, §2.4 |
| **D71 A-1** | **CLOSED — no defect today.** `.Pivots.Parent` has exactly one writer (`demons.go:5242`) and no invalidator. `:5359` trusts it without restating the invariant. **Maintenance hazard, not a live gap.** | §3 |

**One correction to D71 §4.3, reported in place:** D71 called the divergent-writer case hypothetical. **It is real (`Command.c:2586`) but bounded by direction (§2.4).** **D71's conclusion that `Pivot.c:265` is correct for the reachable writer path stands.**

**No contradiction with D47, D56, or D65.**

---

**End of D76.**
