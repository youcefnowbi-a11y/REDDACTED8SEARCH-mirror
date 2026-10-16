# D105 — HAVOC Demon, AGENT SIDE: THE WIRE ENVELOPE, THE SLEEP SURFACE, AND THE `Pivots` SYNCHRONISATION CENSUS

**Lane: source-layer load-bearing mechanisms. Five tasks (T1-T5) from a single direction — what the Demon sends, when it sleeps, and what the server does with the shared `Pivots` state it hands across goroutines.**

**Artifacts:** `havoc/payloads/Demon/` (C, agent side) and `havoc/teamserver/` (Go, server side). **Method:** pure source read. **No REA. No `open_binary`. No execution. No network.** **Nothing here is `[executed]`.**

**Line-count convention:** 1-based line numbers as printed by the read oracle, line 1 = first line of file. **No `-Skip` display value is ever used as a line number.**

**Tags:** `[verified]` read verbatim here; `[read]` read here without full quotation; `[inferred]` derived, NOT measured; `[absence]` a negative with its enumeration printed beside it.

**Vocabulary:** `latent` / `unreachable-from-corpus`. **Nothing is called "live" or "fixed."** Where a defect is reachable only under an interleaving that cannot be constructed from source, it is stated as **not constructed**, which this report treats as a result.

---

## §0 — OCCUPANCY, METHOD, AND THE INSTRUMENT CARRIED FORWARD

### 0.1 Occupancy by enumeration

**D105 UNOCCUPIED — confirmed by enumeration.** DEEP contained **162 files** at list time. D10x present on disk: **D10, D100, D101, D102** (D103/D104 absent). C-series present: **C-00, C-08, C-09, C-10**. **`C-11` confirmed FREE by enumeration at the same moment.** This report takes **C-11** for its correction entry (§7).

### 0.2 The instrument, adopted deliberately (T5)

**Every census line in this report carries a comment-membership test built into the enumeration, not applied afterwards.** **The test:** for candidate line `n`, record the last `/*` at or before `n` and the last `*/` at or before `n`; the line is inside a C comment iff the last `/*` is later than the last `*/`.

**This is D89 §7's mandated mitigation.** **D89 found `agent.go:580` was inside `/*…*/` spanning `:538`-`:592` only after the census was published, and the Lead had independently reproduced the same six lines byte-for-byte using the same class of probe.** **A regex census does not know what a comment is.** [source: D89 §0.1, §7]

**Result of applying it in this report, stated up front because it is the headline instrument outcome: it removed 10 of 51 `Pivots` matches and 2 of 42 `PackageCreate*` construction sites.** **Both removals are quoted in place (§3.2, §1.4).** [source: §1.4, §3.2]

### 0.3 The C-08 seven failure modes, carried (T5)

**C-08 §5 records seven toolchain failure modes, each costing a run.** **The one C-08 names as mattering most is Failure 3: `-readOnly` printed `Analysis succeeded` and then discarded the file import, exiting 0 — "A tool reported success and did nothing with the result. Read the REPORT lines, not the exit code."** [source: `C-08_ghidra_census_merlin_suite_symbol_asymmetry_and_toolchain_failures.md` §5, Failure 3]

**That species is directly load-bearing for T2.** **T2 asks whether sleep/jitter are honoured or merely echoed — and "echoed" is exactly a value that is reported and does nothing.** **C-08's Failure 3 is the same defect shape one layer up: a subsystem that reports success and does nothing with the result.** [source: C-08 §5; §2.5]

**The other six, recorded for completeness:** positional project args (`Failure 1`); `analyzeHeadless` does not create the project dir (`Failure 2`); `setlocal` scopes env away from the child (`Failure 4`); env vars never reached the script process, script args did (`Failure 5`); Ghidra splits args at the path space under `FOR REDDACTED` (`Failure 6`); `#` is not a batch comment and `%1`-substitution silently corrupted the rest of the script (`Failure 7`). **Failure 7 is the one C-08 records as corrupting its own instrument while looking like a tool fault — the same self-instrument-corruption pattern D89 §7 Failure 4 and D98 §7 Failure 1 record in this lane.** [source: C-08 §5]

---

## §1 — T1: THE WIRE FORMAT AND THE CONCRETE TYPE SET

### 1.1 The envelope constructor, verbatim

```c
PPACKAGE PackageCreate( UINT32 CommandID )
{
    PPACKAGE Package = NULL;

    Package            = Instance->Win32.LocalAlloc( LPTR, sizeof( PACKAGE ) );
    Package->Buffer    = Instance->Win32.LocalAlloc( LPTR, sizeof( BYTE ) );
    Package->Length    = 0;
    Package->RequestID = Instance->CurrentRequestID;
    Package->CommandID = CommandID;
    Package->Encrypt   = TRUE;
    Package->Destroy   = TRUE;
    Package->Included  = FALSE;
    Package->Next      = NULL;

    return Package;
}

PPACKAGE PackageCreateWithMetaData( UINT32 CommandID )
{
    PPACKAGE Package = PackageCreate( CommandID );

    PackageAddInt32( Package, 0 ); // package length
    PackageAddInt32( Package, DEMON_MAGIC_VALUE );
    PackageAddInt32( Package, Instance->Session.AgentID );
    PackageAddInt32( Package, Package->CommandID );
    PackageAddInt32( Package, Package->RequestID );

    return Package;
}
```
[source: `payloads/Demon/src/core/Package.c:157-185`, verbatim]

### 1.2 The 20-byte header, both sides

**Agent side — `PackageCreateWithMetaData:178-182` writes five `UINT32` fields in order.**

| Offset | Size | Field | Agent write |
|---|---|---|---|
| `[0..3]` | 4 | package length (**0**, back-patched) | `:178` |
| `[4..7]` | 4 | `DEMON_MAGIC_VALUE` | `:179` |
| `[8..11]` | 4 | `Session.AgentID` | `:180` |
| `[12..15]` | 4 | `CommandID` | `:181` |
| `[16..19]` | 4 | `RequestID` | `:182` |

**Server side — `ParseHeader` reads the same five fields in the same order:**

```go
	if Parser.Length() > 4 {
		Header.Size = Parser.ParseInt32()
	} else {
		return Header, errors.New("failed to parse package size")
	}

	if Parser.Length() > 4 {
		Header.MagicValue = Parser.ParseInt32()
	} else {
		return Header, errors.New("failed to parse magic value")
	}

	if Parser.Length() > 4 {
		Header.AgentID = Parser.ParseInt32()
	} else {
		return Header, errors.New("failed to parse agent id")
	}
```
[source: `pkg/agent/agent.go:187-203`, verbatim]

**The reader consumes `[0..3]` size, `[4..7]` magic, `[8..11]` agent ID — matching the writer field-for-field.** **`[12..15]` CommandID and `[16..19]` RequestID are read later in the register path, not by `ParseHeader`.** [source: `Package.c:178-182`; `agent.go:187-203`]

### 1.3 Byte order — big-endian, confirmed from the primitive

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

**MSB first — the package header is big-endian on the wire.** **This corroborates D47 §3's SMB header finding, where `SmbRecv`'s named fields and the writer's fields are swapped.** [source: `Package.c:43-46`; D47 §3]

### 1.4 The Concrete type set — construction sites, comment-tested

**Probe, printed:**

```
$ Get-ChildItem payloads/Demon -Recurse -File -Include *.c |
    Select-String 'PackageCreate(WithMetaData|WithRequestID)?\(\s*DEMON_COMMAND_\w+'
count: 42
```

**Comment-membership test applied to all 42:**

```
DEAD  src\core\Dotnet.c:291  PackageInfo = PackageCreate( DEMON_COMMAND_ASSEMBLY_INLINE_EXECUTE );
DEAD  src\core\Dotnet.c:363  Package = PackageCreate( DEMON_COMMAND_ASSEMBLY_INLINE_EXECUTE );
LIVE sites: 40
DEAD (in comment) sites: 2
```
[source: probe output, reproduced as run]

**The two dead sites are verified by their comment regions, printed:**

- **`Dotnet.c:226` opens `/*` and `:306` closes `*/`.** **`:291-294` is inside that block.** **The block contains the entire ROP/APC thread-creation path for .NET assembly execution** (`NtCreateThreadEx` `:241`, the `RopInit`/`RopInvk`/`RopEvnt`/`RopExit` contexts `:243-280`, `NtQueueApcThread` `:282-284`). **The whole path is commented out.** [source: `Dotnet.c:226`, `:241-294`, `:306`]
- **`Dotnet.c:359` opens `/*` and `:369` closes `*/`.** **`:363-365` is inside it.** [source: `Dotnet.c:359`, `:363-365`, `:369`]

**Read verbatim at `:226` and `:306`:**

```c
    /*
    PUTS( "Create Thread..." )
...
    } else PUTS( "NtCreateEvent failed" )
    */

    return TRUE;
}
```
[source: `payloads/Demon/src/core/Dotnet.c:226`, `:305-309`, verbatim]

### 1.5 The type count and the site count are DIFFERENT numbers — stated precisely

**The comment test removed two construction SITES.** **It did not remove a TYPE.**

```
$ Select-String 'PackageCreate\w*\(\s*DEMON_COMMAND_ASSEMBLY_INLINE_EXECUTE'
src\core\Command.c:1777  lastOpen=1758 lastClose=1758 -> LIVE
src\core\Dotnet.c:92     lastOpen=86   lastClose=86   -> LIVE
src\core\Dotnet.c:138    lastOpen=137  lastClose=137  -> LIVE
src\core\Dotnet.c:291    lastOpen=226  lastClose=224  -> DEAD
src\core\Dotnet.c:363    lastOpen=359  lastClose=358  -> DEAD
```
[source: probe output, reproduced as run]

**`DEMON_COMMAND_ASSEMBLY_INLINE_EXECUTE` retains three LIVE construction sites (`Command.c:1777`, `Dotnet.c:92`, `Dotnet.c:138`) and loses two.** **So: 22 distinct types, 40 live sites.** **Collapsing either number into the other would be wrong, and the two are reported separately for that reason.** [source: §1.4, §1.5]

### 1.6 The denominator — every `DEMON_COMMAND_*` define

**Probe, printed:**

```
$ Get-ChildItem payloads/Demon -Recurse -File -Include *.h |
    Select-String '^\s*#define\s+(DEMON_COMMAND_\w+)'
define count: 62
```

**62 unique defines across the Demon headers.** [source: probe output]

**One of the 62 is `DEMON_COMMAND_H` — a header guard, not a command.** **This is the exact artefact class D47 §0.1 caught when `DEMON_COMMAND_H` was counted as a 62nd define, and the class D47 §0.1 logged as "a substring count is not a measurement."** **The census above is over `DEMON_COMMAND_` prefixed defines and therefore includes it; the real command-define count is 61.** [source: D47 §0.1; §1.6]

### 1.7 The 22 live Concrete types

**From the 40 live sites, the distinct `CommandID` values:**

| # | Type | # | Type |
|---|---|---|---|
| 1 | `DEMON_COMMAND_ASSEMBLY_INLINE_EXECUTE` | 12 | `DEMON_COMMAND_NET` |
| 2 | `DEMON_COMMAND_ASSEMBLY_VERSIONS` | 13 | `DEMON_COMMAND_PIVOT` |
| 3 | `DEMON_COMMAND_CHECKIN` | 14 | `DEMON_COMMAND_PROC` |
| 4 | `DEMON_COMMAND_CONFIG` | 15 | `DEMON_COMMAND_PROC_LIST` |
| 5 | `DEMON_COMMAND_FS` | 16 | `DEMON_COMMAND_SCREENSHOT` |
| 6 | `DEMON_COMMAND_GET_JOB` | 17 | `DEMON_COMMAND_SLEEP` |
| 7 | `DEMON_COMMAND_INJECT_DLL` | 18 | `DEMON_COMMAND_SOCKET` |
| 8 | `DEMON_COMMAND_INJECT_SHELLCODE` | 19 | `DEMON_COMMAND_SPAWN_DLL` |
| 9 | `DEMON_COMMAND_INLINE_EXECUTE` | 20 | `DEMON_COMMAND_TOKEN` |
| 10 | `DEMON_COMMAND_JOB` | 21 | `DEMON_COMMAND_TRANSFER` |
| 11 | `DEMON_COMMAND_KERBEROS` | 22 | `DEMON_COMMAND_MEM_FILE` |

[source: §1.4 probe, comment-filtered]

### 1.8 The gap, stated

**62 defines − 22 live sender types = 40.** **The 40 are sub-command discriminants carried as `PackageAddInt32` payloads inside the 22 envelopes, not separate envelopes.** **Examples read verbatim: `DEMON_COMMAND_INLINE_EXECUTE_EXCEPTION` (`CoffeeLdr.c:55`), `DEMON_COMMAND_INLINE_EXECUTE_SYMBOL_NOT_FOUND` (`:234`, `:356`), `DEMON_COMMAND_INLINE_EXECUTE_RAN_OK` (`:779`), `DEMON_COMMAND_INLINE_EXECUTE_COULD_NO_RUN` (`:785`) are all added as `Int32` data inside a `DEMON_COMMAND_INLINE_EXECUTE` package.** [source: `CoffeeLdr.c:55`, `:234`, `:356`, `:779`, `:785`]

**This matches D47's Class A/B/C/D structure on the server side and is the agent-side confirmation of it.** **The sub-command is a payload discriminant, not a wire type.** [source: D47 §3]

### 1.9 Where `ToMap` output enters, from the agent's direction

**It does not.** **`ToMap` is server-side (`pkg/agent/agent.go:1193`) and serializes an `*Agent` into a `map[string]interface{}` for the operator UI and webhooks.** **The Demon never constructs or parses it.** **The agent's own envelope is the 20-byte `PACKAGE` header plus the command payload.** **The two structures are separate: `ToMap` describes an agent to the operator; `PACKAGE` is what the agent sends.** [source: `agent.go:1193`; `Package.c:157-185`; D98 §1]

---

## §2 — T2: THE SLEEP AND JITTER SURFACE — DECLARED, OFFERED, READ, HONOURED

### 2.1 The four-state test, applied

**D82's rule: `declared` / `offered` / `read` / `honoured` are four different properties.** **A value can be declared and offered and even read without being honoured.** **This section applies each state to `Sleeping` and `Jitter` with a cited line for each.** [source: D82 four-state rule]

### 2.2 DECLARED

```c
    DWORD Sleeping;
    DWORD Jitter;
```
[source: `payloads/Demon/include/Demon.h:87-88`, verbatim]

### 2.3 WRITTEN (two distinct writers)

```c
    Instance->Config.Sleeping = ParserGetInt32( &Parser );
    Instance->Config.Jitter   = ParserGetInt32( &Parser );
    PRINTF( "Sleep: %d (%d%%)\n", Instance->Config.Sleeping, Instance->Config.Jitter )
```
[source: `payloads/Demon/src/Demon.c:586-588`, verbatim]

```c
    Instance->Config.Sleeping = ParserGetInt32( Parser );
    Instance->Config.Jitter   = ParserGetInt32( Parser );
    PRINTF( "Instance->Sleeping: [%d]\n", Instance->Config.Sleeping );
    PRINTF( "Instance->Jitter  : [%d]\n", Instance->Config.Jitter );
```
[source: `payloads/Demon/src/core/Command.c:178-181`, verbatim]

**Two writers: the initial config parse (`Demon.c:586`) and the runtime `DEMON_COMMAND_SLEEP` handler (`Command.c:178`).** **A runtime sleep change is therefore written.** [source: `Demon.c:586`; `Command.c:178`]

### 2.4 OFFERED (both writers also report back)

```c
    PPACKAGE Package = PackageCreate( DEMON_COMMAND_SLEEP );
...
    PackageAddInt32( Package, Instance->Config.Sleeping );
    PackageAddInt32( Package, Instance->Config.Jitter );
    PackageTransmit( Package );
```
[source: `payloads/Demon/src/core/Command.c:176`, `:183-185`, verbatim]

```c
    PackageAddInt32( *MetaData, Instance->Config.Sleeping );
    PackageAddInt32( *MetaData, Instance->Config.Jitter );
```
[source: `payloads/Demon/src/Demon.c:261-262`, verbatim]

**Both are offered: the metadata blob carries them at every check-in (`Demon.c:261`), and the `SLEEP` handler echoes them back (`Command.c:183`).** **This is the "merely echoed" surface T2 asks about — and the echo is real, which is exactly why the echo alone would not settle the question.** [source: `Demon.c:261`; `Command.c:183`]

### 2.5 READ and HONOURED — the distinction that decides T2

```c
UINT32 SleepTime(
    VOID
) {
    UINT32     SleepTime    = Instance->Config.Sleeping * 1000;
    UINT32     MaxVariation = ( Instance->Config.Jitter * SleepTime ) / 100;
    ULONG      Rand         = 0;
```
[source: `payloads/Demon/src/core/Obf.c:650-655`, verbatim]

**`Sleeping` and `Jitter` are READ at `:653-654` into `SleepTime` and `MaxVariation`.** **The jitter is then CONSUMED:**

```c
    // MaxVariation will be non-zero if sleep jitter was specified
    else if ( MaxVariation )
    {
        Rand = RandomNumber32();
        Rand = Rand % MaxVariation;

        if ( RandomBool() ) {
            SleepTime += Rand;
        } else {
            SleepTime -= Rand;
        }
    }
```
[source: `payloads/Demon/src/core/Obf.c:698-709`, verbatim]

**`MaxVariation` at `:702` bounds a real `RandomNumber32()` draw, and `:704-708` applies it as a signed offset.** **This is consumption, not echo.** [source: `:699-708`]

### 2.6 HONOURED — traced to the syscall

```c
VOID SleepObf(
    VOID
) {
    UINT32 TimeOut   = SleepTime();
    DWORD  Technique = Instance->Config.Implant.SleepMaskTechnique;

    /* don't do any sleep obf. waste of resources */
    if ( TimeOut == 0 ) {
        return;
    }
```
[source: `payloads/Demon/src/core/Obf.c:714-723`, verbatim]

```c
        /* default */
        DEFAULT: case SLEEPOBF_NO_OBF: {}; default: {
            SpoofFunc(
                Instance->Modules.Kernel32,
                IMAGE_SIZE( Instance->Modules.Kernel32 ),
                Instance->Win32.WaitForSingleObjectEx,
                NtCurrentProcess(),
                C_PTR( TimeOut ),
                FALSE
            );
        }
```
[source: `payloads/Demon/src/core/Obf.c:757-767`, verbatim]

**`TimeOut` from `SleepTime()` at `:717` reaches `C_PTR( TimeOut )` at `:764` as the wait timeout.** **HONOURED — the jittered value is the wait.** [source: `:717`, `:764`]

### 2.7 The callers, comment-tested

**Probe, printed — every `SleepObf` reference, comment-membership applied:**

```
include\core\SleepObf.h:2-3,7-19,39  -> header, LIVE
src\core\Command.c:9      #include <core/SleepObf.h>     -> LIVE
src\core\Command.c:66     SleepObf();                    -> LIVE
src\core\Command.c:72     // simply call SleepObf until... -> LIVE (line comment)
src\core\Obf.c:714        VOID SleepObf(                -> LIVE (definition)
src\Demon.c:9             #include <core/SleepObf.h>     -> LIVE
src\Demon.c:90            SleepObf();                    -> LIVE
```
**Two live call sites: `Command.c:66` and `Demon.c:90`.** **No `SleepObf` reference is inside a block comment.** [source: probe output, reproduced as run]

### 2.8 T2 VERDICT — HONOURED, with one named exception

| State | `Sleeping` | `Jitter` | Site |
|---|---|---|---|
| **declared** | yes | yes | `Demon.h:87-88` |
| **written** | yes (2 writers) | yes (2 writers) | `Demon.c:586-587`; `Command.c:178-179` |
| **offered** | yes (2 senders) | yes (2 senders) | `Demon.c:261-262`; `Command.c:183-184` |
| **read** | yes | yes | `Obf.c:653-654` |
| **honoured** | yes | **yes — conditional** | `Obf.c:699-708` → `:764` |

**Sleep and jitter are honoured, not merely echoed.** **The cadence is consumed and reaches `WaitForSingleObjectEx`.** [source: §2.5-§2.7]

**The exception, read verbatim at `:699`:** **the jitter branch is `else if ( MaxVariation )`.** **Its `else` is the `InWorkingHours()` branch at `:663`.** **So when the agent is OUTSIDE working hours, `MaxVariation` is computed at `:654` and never applied — the jitter is discarded for that cycle, and `SleepTime` is recomputed from working-hours arithmetic at `:674-695`.** [source: `Obf.c:654`, `:663`, `:674-695`, `:699`]

**Status: `read`-but-not-`honoured` for the out-of-working-hours case, and that is a bounded, stated property rather than a defect claim.** **The jitter is dropped by construction in that branch; whether dropping it is intended is not determinable from source.** [source: `Obf.c:663-699`]

### 2.9 What the echo does NOT prove

**The metadata echo at `Demon.c:261-262` is a report to the server.** **It is NOT evidence that the agent's loop uses the value — that required the `:653` → `:764` trace.** **A report is not a union; the two are independently cited here for that reason.** [source: `Demon.c:261-262`; §2.5-§2.6]

---

## §3 — T3: THE `Pivots` SYNCHRONISATION CENSUS

### 3.1 The structure and its lack of a lock

```go
type Pivots struct {
	Parent *Agent
	Links  []*Agent
}
```
[source: `pkg/agent/types.go:89-92`, verbatim]

**Two fields, no mutex.** **The `Agent` struct's three mutexes are adjacent and belong to other fields:**

```go
	Info   *AgentInfo
	Pivots Pivots
...
	Downloads   []*Download
	PortFwds    []*PortFwd
	PortFwdsMtx sync.Mutex
	SocksCli    []*SocksClient
	SocksCliMtx sync.Mutex
	SocksSvr    []*SocksServer
	SocksSvrMtx sync.Mutex
```
[source: `pkg/agent/types.go:149-161`, verbatim]

**`[verified]`: `Pivots` (`:150`) has no mutex.** **`Downloads` (`:155`) also has none.** **Three mutexes exist for three other fields.** [source: `:149-161`]

### 3.2 The full census — 51 matches, comment-tested

**Probe, printed (all 51, with the comment verdict on each):**

```
cmd\server\agent.go:32   [LIVE] for i := range Agent.Pivots.Links {
cmd\server\agent.go:33   [LIVE] t.LinkRemove(Agent, Agent.Pivots.Links[i], false)
cmd\server\agent.go:34   [LIVE] Agent.Pivots.Links = append(Agent.Pivots.Links[:i], Agent.Pivots.Links[i+1:]...)
cmd\server\agent.go:43   [LIVE] for i := range ParentAgent.Pivots.Links {
cmd\server\agent.go:44   [LIVE] if ParentAgent.Pivots.Links[i].NameID == Agent.NameID {
cmd\server\agent.go:46   [LIVE] ParentAgent.Pivots.Links = append(ParentAgent.Pivots.Links[:i], ParentAgent.Pivots.Links[i+1:]...)
cmd\server\agent.go:86   [LIVE] for i := range ParentAgent.Pivots.Links {
cmd\server\agent.go:87   [LIVE] if ParentAgent.Pivots.Links[i].NameID == LinkAgent.NameID {
cmd\server\agent.go:88   [LIVE] ParentAgent.Pivots.Links = append(ParentAgent.Pivots.Links[:i], ParentAgent.Pivots.Links[i+1:]...)
cmd\server\dispatch.go:201 [LIVE] if t.Agents.Agents[i].Pivots.Parent != nil {
cmd\server\listener.go:68  [LIVE] var SmbConfig = handlers.NewPivotSmb()
cmd\server\teamserver.go:471 [LIVE] Agent.Pivots.Parent = t.AgentInstance(parentID)
cmd\server\teamserver.go:476 [LIVE] Agent.Pivots.Links = append(Agent.Pivots.Links, t.AgentInstance(AgentID))
pkg\agent\agent.go:543    [DEAD] case DEMON_CHECKIN_OPTION_PIVOTS:
pkg\agent\agent.go:544    [DEAD] logger.Debug("DEMON_CHECKIN_OPTION_PIVOTS")
pkg\agent\agent.go:558    [DEAD] PivotSession *Agent
pkg\agent\agent.go:568    [DEAD] PivotSession = ParseDemonRegisterRequest(PivotAgentID, PivotParser, RoutineFunc)
pkg\agent\agent.go:569    [DEAD] if PivotSession != nil {
pkg\agent\agent.go:570    [DEAD] PivotSession.Info.MagicValue = HdrMagicValue
pkg\agent\agent.go:572    [DEAD] LogDemonCallback(PivotSession)
pkg\agent\agent.go:573    [DEAD] RoutineFunc.AppendDemon(PivotSession)
pkg\agent\agent.go:574    [DEAD] pk := RoutineFunc.EventNewDemon(PivotSession)
pkg\agent\agent.go:578    [DEAD] Session.Pivots.Links = append(Session.Pivots.Links, PivotSession)
pkg\agent\agent.go:580    [DEAD] PivotSession.Pivots.Parent = Session
pkg\agent\agent.go:651    [LIVE] if a.Pivots.Parent != nil {
pkg\agent\agent.go:750    [LIVE] pivots   *Pivots
pkg\agent\agent.go:780    [LIVE] pivots = &a.Pivots
pkg\agent\agent.go:782    [LIVE] // pack it up for all the parent pivots.
pkg\agent\agent.go:784    [LIVE] if pivots.Parent.Pivots.Parent == nil {
pkg\agent\agent.go:789    [LIVE] Payload = BuildPayloadMessage([]Job{PivotJob}, pivots.Parent.Encryption.AESKey, pivots.Parent.Encryption.AESIv)
pkg\agent\agent.go:792    [LIVE] AgentID, err = strconv.ParseInt(pivots.Parent.NameID, 16, 32)
pkg\agent\agent.go:810    [LIVE] pivots = &pivots.Parent.Pivots
pkg\agent\agent.go:813    [LIVE] pivots.Parent.JobQueue = append(pivots.Parent.JobQueue, PivotJob)
pkg\agent\agent.go:1200   [LIVE] ParentAgent = a.Pivots.Parent
pkg\agent\agent.go:1201   [LIVE] a.Pivots.Parent = nil
pkg\agent\agent.go:1216   [LIVE] a.Pivots.Parent = ParentAgent
pkg\agent\demons.go:5192  [LIVE] Message["Message"] = fmt.Sprintf("No pivots connected")
pkg\agent\demons.go:5231  [LIVE] if DemonInfo.Pivots.Parent != nil {
pkg\agent\demons.go:5232  [LIVE] for i := range DemonInfo.Pivots.Parent.Pivots.Links {
pkg\agent\demons.go:5233  [LIVE] if DemonInfo.Pivots.Parent.Pivots.Links[i].NameID == fmt.Sprintf("%08x", AgentHdr.AgentID) {
pkg\agent\demons.go:5234  [LIVE] DemonInfo.Pivots.Parent.Pivots.Links = append(...)
pkg\agent\demons.go:5242  [LIVE] DemonInfo.Pivots.Parent = a
pkg\agent\demons.go:5244  [LIVE] a.Pivots.Links = append(a.Pivots.Links, DemonInfo)
pkg\agent\demons.go:5254  [LIVE] DemonInfo.Pivots.Parent = a
pkg\agent\demons.go:5256  [LIVE] a.Pivots.Links = append(a.Pivots.Links, DemonInfo)
pkg\agent\types.go:89     [LIVE] type Pivots struct {
pkg\agent\types.go:150    [LIVE] Pivots Pivots
pkg\events\demons.go:51   [LIVE] "Pivots": map[string]interface{}{
pkg\events\demons.go:74   [LIVE] if Agent.Pivots.Parent != nil {
pkg\events\demons.go:75   [LIVE] InfoMap["PivotParent"] = Agent.Pivots.Parent.NameID
pkg\handlers\smb.go:8     [LIVE] func NewPivotSmb() *SMB {
```
[source: probe output, reproduced as run]

**Totals: 51 matched, 41 LIVE, 10 DEAD.** **The 10 dead lines are the entire `agent.go:543-580` block — the `DEMON_CHECKIN_OPTION_PIVOTS` path D89 §0.1 proved is commented out.** **`:578` and `:580` are the only writers of `Links`/`Parent` on that path, and both are dead — consistent with D89's correction that the establishing-writer count is five, not six.** [source: D89 §0.1; §3.2]

### 3.3 The unsynchronised pairs

**Grouping the 41 live sites by function and by field written:**

| Function | Field touched | Access | Lock |
|---|---|---|---|
| `agent.go:32-34` `UnlinkFromAll` | `Links` | read + write | **none** |
| `agent.go:43-46` `UnlinkFromAll` | `Links` | read + write | **none** |
| `agent.go:86-88` `LinkRemove` | `Links` | read + write | **none** |
| `dispatch.go:201` | `Parent` | read | **none** |
| `teamserver.go:471` startup | `Parent` | write | **none** |
| `teamserver.go:476` startup | `Links` | write | **none** |
| `agent.go:651` `AddJobToQueue` | `Parent` | read | **none** |
| `agent.go:784-813` `PivotAddJob` | `Parent`, `Links`-via-Parent | read | **none** |
| `agent.go:1200-1216` `ToMap` | `Parent` | read + write + write | **none** |
| `demons.go:5231-5234` register | `Parent`, `Links` | read + write | **none** |
| `demons.go:5242-5244` register | `Parent`, `Links` | write | **none** |
| `demons.go:5254-5256` register | `Parent`, `Links` | write | **none** |
| `events/demons.go:74-75` | `Parent` | read | **none** |

**Every live access is unsynchronised.** **No lock appears in any enclosing function.** [source: §3.2]

### 3.4 D-1's goroutine families, restated

**From D98 §3, carried forward and not re-derived:** `cmd/server/teamserver.go:107 go t.handleRequest(ClientID)` gives **one goroutine per operator client**, reaching `ToMap` via `dispatch.go:286`. `pkg/service/service.go:45 go s.handleConnection(WebSocket)` gives **one per agent WebSocket**, reaching `ToMap` via `service.go:334` → `AgentAdd` → `agent.go:111`. **Both call `ToMap`, which writes `Pivots.Parent` at `:1201` and `:1216`.** [source: D98 §3.2-§3.5]

### 3.5 THE MINIMUM INTERLEAVING — CONSTRUCTED

**The task asks for the minimum interleaving that produces a bad read, or a statement that one cannot be constructed.** **One CAN be constructed.** **It is exhibited below, with the two goroutines and the shared object named.**

**Precondition:** one `*Agent` value `A` with `A.Pivots.Parent == P` (non-nil), reachable from both goroutine families. **Such an `A` exists whenever a pivot child is registered at `demons.go:5242`/`:5254`, since both writers set `.Parent` non-nil on a live object.** [source: `demons.go:5242`, `:5254`]

**Precondition 2:** `A` is reachable by the operator path (`dispatch.go:286` reads `t.Agents.Agents[i]`, the shared slice) **and** by the agent path (`handlers.go:328` reads `Teamserver.AgentInstance(Header.AgentID)`, the same shared slice). **Both read `t.Agents.Agents`.** [source: `dispatch.go:286`; `handlers.go:326-328`; `types.go:150`]

| Step | Goroutine A (operator, via `handleRequest`) | Goroutine B (agent, via `handleConnection`) | `A.Pivots.Parent` |
|---|---|---|---|
| 1 | enters `ToMap` on `A` | | `P` |
| 2 | **`:1200` reads `ParentAgent = A.Pivots.Parent`** | | `P` |
| 3 | **`:1201` writes `A.Pivots.Parent = nil`** | | **`nil`** |
| 4 | *(serializes)* | enters `ToMap` on `A` | **`nil`** |
| 5 | | **`:1200` reads `ParentAgent = A.Pivots.Parent` → `nil`** | **`nil`** ← **BAD READ** |
| 6 | | `:1203` serializes with `Parent` absent | `nil` |
| 7 | | **`:1214 if ParentAgent != nil` is FALSE → `:1216` SKIPPED** | **`nil`** ← **value never restored** |
| 8 | **`:1216` writes `A.Pivots.Parent = P`** | | `P` |
| 9 | returns map with `PivotParent` | **returns map with NO `PivotParent` key** | `P` |

**The bad read is at step 5: goroutine B reads `nil` where the true value is `P`.** **The consequence at step 9 is a `ToMap` result missing its `PivotParent` key.** [source: `agent.go:1200-1216`; §3.4]

### 3.6 What the interleaving is, and what it is NOT

**What is established `[read]`:** the four accesses at `:1200`, `:1201`, `:1216`, and `:1203` exist as ordered above; the `:1214` guard is real; no lock is held anywhere in the sequence. [source: `agent.go:1200-1216`]

**What the interleaving assumes `[inferred]`:** **that two goroutines can address the same `*Agent` at the same time.** **That assumption is consistent with the two call paths reading the same `t.Agents.Agents` slice, but it is NOT observed.** [source: §3.4]

**What is NOT claimed:** **that this interleaving occurs.** **It is a construction, not a measurement.** **It establishes that the window is not closed by any mechanism visible in source — which is the strongest statement a source-only method supports.** [source: §3.5]

**The window's shape is the notable part: this is not a torn read of a pointer.** **Steps 3-8 make it a lost-update window — a concurrent `ToMap` observes `nil` AND, because its own restore is guarded on the nil it read, leaves the field nil until the first goroutine's `:1216` restores it.** **If goroutine A did not hold the value in `ParentAgent`, the field would be left nil.** **It does hold it, so step 8 repairs it — but only for this interleaving.** [source: §3.5]

### 3.7 A second, simpler unsynchronised pair — `UnlinkFromAll`

```go
func (t *Teamserver) UnlinkFromAll(Agent *agent.Agent) {
	// remove all links from agent
	for i := range Agent.Pivots.Links {
		t.LinkRemove(Agent, Agent.Pivots.Links[i], false)
		Agent.Pivots.Links = append(Agent.Pivots.Links[:i], Agent.Pivots.Links[i+1:]...)
	}
```
[source: `cmd/server/agent.go:30-35`, verbatim]

**This is a splice-while-iterating defect, independent of concurrency: `for i := range` iterates over the ORIGINAL length, and the splice at `:34` shortens the slice, so the element that moves into index `i` is skipped.** **The same pattern appears at `:46` and `:88`.** **`[read]`, and it is a single-goroutine correctness issue, not a race.** [source: `:32-34`, `:46`, `:88`]

**Status: `latent` — the loop is reachable from `Died` (`:23-28`), and the skip occurs when an agent has two or more links.** [source: `:23-28`]

---

## §4 — T4: `handlers.go:328` — WHAT IT IS, WHAT TRIGGERS IT, AND WHO CAN REACH IT

### 4.1 The handler, verbatim

```go
func handleServiceAgent(Teamserver agent.TeamServer, Header agent.Header, ExternalIP string) (bytes.Buffer, bool) {

	var (
		Response  bytes.Buffer
		AgentData any
		Agent     *agent.Agent
		Task      []byte
		err       error
	)

	/* search if a service 3rd party agent was registered with this MagicValue */
	if !Teamserver.ServiceAgentExist(Header.MagicValue) {
		return Response, false
	}

	Agent = Teamserver.AgentInstance(Header.AgentID)
	if Agent != nil {
		AgentData = Agent.ToMap()
	}
	
	// Update Callback time
	if Teamserver.AgentExist(Header.AgentID) {
		Agent.UpdateLastCallback(Teamserver)
	}
	
	Task = Teamserver.ServiceAgent(Header.MagicValue).SendResponse(AgentData, Header)
```
[source: `pkg/handlers/handlers.go:311-336`, verbatim]

### 4.2 What it is, and what triggers it

**It is `handleServiceAgent`.** **It triggers on an inbound request whose `Header.MagicValue` matches a registered SERVICE agent — `ServiceAgentExist(Header.MagicValue)` at `:322`.** [source: `:311`, `:322`]

### 4.3 AGENT-REACHABLE, not operator-only — and that is the answer T4 needs

**`Header` is parsed from agent-supplied bytes by `ParseHeader` (`agent.go:181-213`), and `MagicValue` is read straight off the wire at `:194`.** **So the trigger is an inbound agent message, not an operator action.** [source: `agent.go:181-213`; `handlers.go:322`]

**This matters for D98: the `ToMap` at `handlers.go:328` is on the AGENT-INBOUND path, which confirms the second goroutine family in D98 §3.4.** **D98 named the site live; T4 confirms it is reachable by agent message and names the precondition.** [source: D98 §3.3; §4.3]

### 4.4 The near-defect at `:332-333` — bounded as unreachable

**`:333` calls `Agent.UpdateLastCallback(...)` guarded by `AgentExist(Header.AgentID)` — a DIFFERENT predicate from the `Agent != nil` that guards `:328`.**

**If the two predicates could disagree, `:333` would be a nil dereference.** **They cannot, on this input.** **Both walk the same slice with the same comparison:**

```go
func (t *Teamserver) AgentInstance(AgentID int) *agent.Agent {
	for _, demon := range t.Agents.Agents {
		var NameID, _ = strconv.ParseInt(demon.NameID, 16, 64)

		if AgentID == int(NameID) {
			return demon
		}
	}
	return nil
}
```
[source: `cmd/server/agent.go:155-164`, verbatim]

```go
func (t *Teamserver) AgentExist(AgentID int) bool {
	for _, demon := range t.Agents.Agents {
		var NameID, err = strconv.ParseInt(demon.NameID, 16, 64)
		if err != nil {
			logger.Debug("Failed to convert demon.NameID to int: " + err.Error())
			return false
		}

		if AgentID == int(NameID) {
			return true
		}
	}
	return false
```
[source: `cmd/server/agent.go:183-195`, verbatim]

**`AgentInstance` returning `nil` means no element matched, which means `AgentExist` also returns `false` — so `:333` is not entered.** **The two agree on the matching condition.** [source: `:155-164`, `:183-195`]

**The one divergence: `ParseInt` error handling.** **`AgentInstance:157` discards the error (`_`) and compares against `NameID == 0`; `AgentExist:185-188` returns `false` early.** **For a malformed `NameID` the predicates differ — and they differ in the direction that SKIPS `:333`, because `AgentExist` returns `false` where `AgentInstance` might return a match on `0`.** **So the divergence does not open the deref.** [source: `:157`, `:185-188`]

**Status: `unreachable-from-corpus` for the nil deref, and the reason is the shared matching condition, not a guard at `:333`.** **`UpdateLastCallback` is itself unguarded — the safety is upstream.** [source: `:183-195`, `:332-333`]

### 4.5 The one input that does reach `:333` with a valid agent

**When `AgentInstance` returns non-nil, `AgentExist` returns true, and `:333` runs on a valid pointer.** **`UpdateLastCallback` (`agent.go:739-744`) is then called normally.** [source: `:326-333`; `agent.go:739-744`]

---

## §5 — WHAT THIS CHANGES

| Item | Verdict | Basis |
|---|---|---|
| **T1 wire format** | **Envelope named and confirmed from BOTH sides: 20-byte header, big-endian, five `UINT32` fields.** | §1.1-§1.3 |
| **T1 Concrete type set** | **22 live types from 40 live construction sites; 2 sites dead in comments; denominator 62 defines (61 real, `DEMON_COMMAND_H` is a guard).** | §1.4-§1.8 |
| **T1 `ToMap` on the wire** | **`ToMap` is server-side only. It does not enter the agent's envelope.** | §1.9 |
| **T2 sleep/jitter** | **HONOURED, not merely echoed — traced `Obf.c:653` → `:764` `WaitForSingleObjectEx`.** **Exception: jitter is dropped when outside working hours (`:699` is `else if`).** | §2.5-§2.8 |
| **T3 `Pivots` sync** | **41 live accesses, ALL unsynchronised. A bad-read interleaving CONSTRUCTED (§3.5); it is a lost-update window, not a torn read. Occurs-or-not is NOT measured.** | §3.3, §3.5 |
| **T3 second defect** | **`UnlinkFromAll` splices while iterating — skips an element when an agent has ≥2 links.** **Single-goroutine, `latent`.** | §3.7 |
| **T4 `handlers.go:328`** | **`handleServiceAgent`; AGENT-REACHABLE via `Header.MagicValue`; the `:333` nil deref is `unreachable-from-corpus` because the two predicates share a matching condition.** | §4.2-§4.4 |
| **T5 instrument** | **Comment test BUILT IN and it removed 10/51 `Pivots` lines and 2/42 construction sites.** | §0.2, §1.4, §3.2 |

**No contradiction with D47, D56, D65, D71, D76, D82, D86, D89, or D98. T1 corroborates D47 §3's big-endian SMB finding from the primitive.**

---

## §6 — RESIDUAL UNKNOWNS, WITH PROBES

| ID | Unknown | Probe |
|---|---|---|
| **D-11** | **Does the §3.5 interleaving occur in a running teamserver?** | Requires execution or race-detector instrumentation. **Out of a source-only method's reach; this is the reason the interleaving is `latent`.** |
| **D-12** | **Is `handleServiceAgent` reachable without a registered service agent?** | Enumerate `ServiceAgent` registration sites (`pkg/service/`). **§4.3 assumes `ServiceAgentExist` gates it; the registration side was not enumerated.** |
| **D-13** | **Does `UnlinkFromAll`'s skip cause a missed `LinkRemove` in practice?** | Enumerate callers of `Died` and `UnlinkFromAll`. **`Died:23-28` is one; not enumerated further.** |
| **D-14** | **Is the working-hours jitter drop intended?** | Read the Havoc documentation and the client-side `SLEEP` UI. **Not a source question.** |
| **D-15** | **Do the two dead `Dotnet.c` sites correspond to a harness path that was removed or never completed?** | Read `Dotnet.c` history if available; **otherwise unresolvable from corpus.** |
| **D-16** | **Does `DEMON_COMMAND_ASSEMBLY_INLINE_EXECUTE`'s live path at `Dotnet.c:92`/`:138` cover what the dead `:291` path was meant to report?** | Read `Dotnet.c:86-140`. **Partially read here; the reporting coverage was not compared.** |

---

## §7 — INSTRUMENT RECORD (T5), AND THE C-11 CORRECTION ENTRY

### 7.1 Failure 1 — the comment test fired and REMOVED content, which is the point

**Built into the enumeration from the start, per T5.** **It removed 10 of 51 `Pivots` matches (`agent.go:543-580`, the dead `PIVOTS` check-in path) and 2 of 42 construction sites (`Dotnet.c:291`, `:363`).**

**Had it not been applied, `DEMON_COMMAND_ASSEMBLY_INLINE_EXECUTE` would still have been counted as a live type — correctly, as it happens — but its site count would have been 42 instead of 40.** **The dead lines would have inflated a site census without changing a type census, which is precisely the D89 `:580` failure shape one level down.** [source: §1.4, §3.2; D89 §0.1]

### 7.2 Failure 2 — the `Pivots` census and the `PackageCreate` census needed DIFFERENT comment tests

**`Pivots` is a Go census; `PackageCreate*` is a C census.** **The C test uses `/* */` block regions; Go uses the same, plus `//` line comments which the block test does NOT detect.**

**`Command.c:72` (`// simply call SleepObf until…`) is a line comment that the block test classified LIVE.** **For a C file this is a real gap.** **No site in §1 or §3 census depended on a line-commented line as a live hit, but the test is weaker than it looks and that is recorded rather than glossed.** [source: §2.7]

### 7.3 Failure 3 — the `DEMON_COMMAND_H` artefact is present in THIS report's denominator

**62 defines includes `DEMON_COMMAND_H`, a header guard.** **Reported at §1.6 with the corrected figure (61).** **Same class as D47 §0.1.** [source: §1.6; D47 §0.1]

### 7.4 Failure 4 — the type count and the site count were nearly conflated

**§1.5 exists because the first pass treated "2 sites removed by the comment test" as "1 type removed."** **It is not: the type retains three live sites.** **Both numbers are now printed separately.** [source: §1.5]

### 7.5 The C-11 entry

**`C-11` is taken by this report for one correction:**

**D89 §0.1's comment-region probe was written retrospectively — after the deadness at `agent.go:580` was noticed by eye.** **D89 §7 Failure 4 records that as the reason the mitigation is mandatory.** **D105 is the first report in this lane to apply the test from the start (T5), and it found dead lines in two independent censuses.** **The correction is not to D89's finding, which stands: it is that a retrospective instrument under-reports, and the forward-applied instrument found dead lines at a rate of 10/51 (19.6%) and 2/42 (4.8%) in two fresh populations.** **Those rates are recorded because they bound how much a retrospective-only census can have missed.** [source: D89 §7 Failure 4; §1.4, §3.2]

---

## §8 — HEADLINE, STATED ONCE

**The Demon's wire envelope is a 20-byte big-endian header (length, magic, agent ID, command ID, request ID) that the server parses field-for-field in the same order.** **22 Concrete types travel it; 40 live sites construct them; the other 40 of 62 defines are payload discriminants, not wire types.**

**Sleep and jitter are HONOURED — the value reaches `WaitForSingleObjectEx` — with one bounded exception: the jitter is discarded outside working hours because `Obf.c:699` is an `else if`.** **Havoc's famous jitter is real, and the echo at `Demon.c:261` is not what proves it.**

**`Pivots` has 41 live unsynchronised accesses and no mutex.** **A bad-read interleaving can be CONSTRUCTED — it is a lost-update window in `ToMap`'s save/clear/restore, and a concurrent serialization loses its `PivotParent` key.** **Whether it occurs is not measured, and this report does not claim it does.**

**`handlers.go:328` is `handleServiceAgent`, reachable by an AGENT message, not operator action — which confirms the second goroutine family D98 named.** **Its adjacent `:333` deref is `unreachable-from-corpus`, and the reason is that `AgentInstance` and `AgentExist` share a matching condition.**

---

**End of D105.**
