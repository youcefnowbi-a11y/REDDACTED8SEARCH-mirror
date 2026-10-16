# D117 — HAVOC: THE THREE-WAY DISCRIMINANT DIFF, `SendResponse` ON A CLOSED CLIENT, AND THE SCOPE ASSERTION

**Lane: source-layer load-bearing mechanisms, Havoc continuation.** Five tasks: the client-side mirrored-consumer census (T1), `SendResponse` on a closed connection (T2), the four bare `#if TRANSPORT_*` tests (T3), `TESTING_MATCHING_ROUTINE` fully (T4), and the rule-entry audit (T5).

**Method:** pure source read, plus read-only inspection of the tree's build files. **No execution. No REA. No `open_binary`. No network. No live C2.** **Nothing here is `[executed]`.** **D-11 remains OPEN and was not attempted.**

**Line-count convention:** 1-based per the read oracle. **No `-Skip` display value is used as a line number** — every read uses an explicit `Begin{$i=N} -Process{…; $i++}` counter.

**Tags:** `[verified]` read verbatim; `[read]` read without quotation; `[inferred]` derived, NOT measured; `[absence]` a negative with its enumeration printed.

---

## §0 — THE SCOPE ASSERTION, APPLIED FROM THE FIRST LINE

**This is T5's output, used here rather than merely described.** **Every census in this report declares its scope before printing a number.**

```
SCOPE:           <what was enumerated>
DEFINER SCOPE:   <what can DEFINE what is tested>
COUNTED:         <cardinality of the input actually scanned>
```

**The justification is a count, and it is the audit T5 asked for. Rule 22/31 has fired FIVE times from this lane across three reports, four of them the same defect:**

| # | Report | Instance | Boundary that was unstated |
|---|---|---|---|
| 1 | **D105 §1.4** | `PackageCreate` site census | **path-scoped to one file's sites; the type/site distinction** |
| 2 | **D111 §6.1** | `DEMON_COMMAND_*` prefix enumeration | **a name prefix — `DEMON_PACKAGE_DROPPED` has no prefix** |
| 3 | **D115 §1.5** | "never-defined macro" probe | **the source tree — the definer is `CMakeLists.txt`** |
| 4 | **D115 §2.1** | §6.1's own citation | **never asked whether `Package.c:311` is inside `#if TRANSPORT_SMB`** |
| 5 | **D115 §1.1** | 379 openings vs 375 `#endif` | **a GLOBAL sum; imbalance is only detectable per file** |

**CASE 5 IS THE CLEANEST AND THE LEAD CORRECTED IT CORRECTLY: the imbalance did not exist.** **The fix was one probe — balance per file — and the tell was in my own report, where I wrote that my matcher "counts globally and cannot localise which file." That sentence describes a check that cannot detect an imbalance.** **Recorded as a sixth instrument failure: named the flaw, did not act on my own naming.** [source: §4.1]

**Would an up-front assertion have caught all five? YES.** **Cases 1-4 are literally "state the boundary"; case 5 is forced by the `COUNTED` line, because a per-file cardinality cannot be produced by a global sum.** **This is the first report in this lane to carry the header, and it is used in every section below.** [source: §1.1, §2.1, §3.1, §4.1]

### 0.1 THE SCOPE ASSERTION CAUGHT A SIXTH INSTANCE, IN THIS REPORT

**The T1 census was scoped to `client/**` for `DEMON_COMMAND_*` and `DOTNET_INFO_*` — and the client tree contains ZERO occurrences of either.** **But the same probe, run as a positive control, found the agent-side response namespace `DEMON_INFO` / `DEMON_OUTPUT` / `DEMON_ERROR` / `DEMON_EXIT` — a name space my D111 census NEVER ENUMERATED.** **So D111's "61 `DEMON_COMMAND_*` + 1 `DEMON_PACKAGE_DROPPED`" denominator excluded an entire sibling namespace in the same file.** **Sixth instance. Caught by the header on the first census that carried it.** [source: §1.4]

---

## §1 — T1: THE THREE-WAY DISCRIMINANT DIFF

### 1.1 SCOPE AND METHOD

```
SCOPE:         payloads/Demon/include/core/Command.h  (agent defines)
               teamserver/pkg/agent/commands.go        (server constants)   [D111 §2.6]
               client/**/*.{h,hpp,cpp,cc}              (client bindings)
DEFINER SCOPE: the agent's wire vocabulary is defined in Command.h; the client's
               rendering vocabulary is defined in the CLIENT tree; the server's
               is a hand-transcribed duplicate. NONE of the three derives from
               the others at build time.
COUNTED:       165 files scanned in the balance probe; 85 files in client/**
               (42 .cc, 28 .hpp, 12 .h, 3 .cpp); 155 lines in the sole binding header.
```

**The C-vs-C++ shape question I flagged before writing is REAL and it changes the comparison.** **The client does not use `#define`s. It uses a C++ `enum class`:**

```cpp
enum class Commands {
    CHECKIN                 = 100,
    CALLBACK                = 10,
    CONSOLE_MESSAGE         = 0x80,
    BOF_CALLBACK            = 0x81,
    SLEEP                   = 11,
    PROC_LIST               = 12,
    FS                      = 15,
    INLINE_EXECUTE          = 20,
    JOB                     = 21,
    INJECT_DLL              = 22,
    INJECT_SHELLCODE        = 24,
    INJECT_DLL_SPAWN        = 26,
    TOKEN                   = 40,
    PROC                    = 0x1010,
    INLINE_EXECUTE_ASSEMBLY = 0x2001,
    ASSEMBLY_LIST_VERSIONS  = 0x2003,
    NET                     = 2100,
    CONFIG                  = 2500,
    SCREENSHOT              = 2510,
    PIVOT                   = 2520,
    TRANSFER                = 2530,
    SOCKET                  = 2540,
    KERBEROS                = 2550,

    OUTPUT  = 90,
    ERROR   = 91,
    EXIT    = 92,
};
```
[source: `client/include/Havoc/DemonCmdDispatch.h:23-51`, verbatim]

**26 entries.** **A declaration order that is roughly sorted but not uniformly — the last three (`OUTPUT`, `ERROR`, `EXIT`) are separated by a blank line and reordered, and `CALLBACK`/`CONSOLE_MESSAGE`/`BOF_CALLBACK` sit near the top while their values (10, 0x80, 0x81) do not follow `CHECKIN = 100`.** [source: `DemonCmdDispatch.h:24-50`]

### 1.2 The three-way numbers

```
AGENT defines in Command.h : 61
CLIENT enum entries        : 26
```
[source: probe output, reproduced as run; server-side figures from D111 §2.3/§2.6]

| Side | Source | Form | Count |
|---|---|---|---|
| **AGENT** | `Command.h` | **C `#define`** | **61 `DEMON_COMMAND_*`** (+ additional namespaces, §1.4) |
| **SERVER** | `commands.go:119-164` | **Go `const`** | **21 compared families** `[D111 §2.6]` |
| **CLIENT** | `DemonCmdDispatch.h:23-51` | **C++ `enum class`** | **26** |

**The three are independent hand-transcriptions in three languages. NONE derives from another at build time — no shared header, no codegen.** [source: §1.1; D111 §2.6]

### 1.3 THE VALUE CHECK — 17 of 17 AGREE, ZERO CONFLICTS

**Every client entry whose name has an exact `DEMON_COMMAND_<NAME>` counterpart was compared by VALUE:**

```
=== paired NAME->VALUE comparison: agent DEMON_COMMAND_<X> vs client <X> ===
   exact name+value pairs agreeing: 17
   exact name+value pairs conflicting: 0
```
[source: probe output, reproduced as run]

**17 exact name-and-value pairs, 17 agreeing, ZERO conflicting.**

**THIS EXTENDS D111 §2.7 TO A THIRD TABLE.** **D111 §2.7 found 21/21 agreement between the C `#define`s and the independently hand-transcribed Go constants.** **D117 adds a C++ `enum class` written by a different component, and it agrees on all 17 of its name-matched pairs.** **Three independent tables, three languages, no drift.** [source: §1.3; D111 §2.7]

**The load-bearing reason this matters is unchanged: one mistranscription would be a `case` that silently never fires, or a client that renders nothing for a command the agent implements — the C-08 Failure 3 shape.** **It is not present.** [source: D111 §2.7]

### 1.4 THE SIX NEW NAME SPACES — and this is where the census was scoped too narrowly

**The nine client-only entries are NOT all client-only. `DEMON_PACKAGE_DROPPED` was D111 §6.1's finding; the same file carries SIX more namespaces D111 never enumerated.** **Full non-`DEMON_COMMAND_` define list from `Command.h`, printed:**

```
     30: DEMON_PACKAGE_DROPPED              = 2570
     32: DEMON_INFO                         = 89
     33: DEMON_OUTPUT                       = 90
     34: DEMON_ERROR                        = 91
     35: DEMON_EXIT                         = 92
     36: DEMON_KILL_DATE                    = 93
     37: BEACON_OUTPUT                      = 94
     38: DEMON_INITIALIZE                   = 99
     45: DOTNET_INFO_PATCHED                = 0x1
     46: DOTNET_INFO_NET_VERSION            = 0x2
     47: DOTNET_INFO_ENTRYPOINT_EXECUTED    = 0x3
     48: DOTNET_INFO_FINISHED               = 0x4
     49: DOTNET_INFO_FAILED                 = 0x5
     51: CALLBACK_ERROR_WIN32               = 0x1
     52: CALLBACK_ERROR_COFFEXEC            = 0x2
     53: CALLBACK_ERROR_TOKEN               = 0x3
     56: DEMON_CONFIG_SHOW_ALL              = 0
     58: DEMON_CONFIG_IMPLANT_SLEEPMASK     = 1
     59: DEMON_CONFIG_IMPLANT_SPFTHREADADDR = 3
     60: DEMON_CONFIG_IMPLANT_VERBOSE       = 4
     61: DEMON_CONFIG_IMPLANT_SLEEP_TECHNIQUE = 5
     62: DEMON_CONFIG_IMPLANT_COFFEE_THREADED = 6
     63: DEMON_CONFIG_IMPLANT_COFFEE_VEH    = 7
     65: DEMON_CONFIG_MEMORY_ALLOC          = 101
     66: DEMON_CONFIG_MEMORY_EXECUTE        = 102
     68: DEMON_CONFIG_INJECTION_TECHNIQUE   = 150
     69: DEMON_CONFIG_INJECTION_SPOOFADDR   = 151
     71: DEMON_CONFIG_INJECTION_SPAWN64     = 152
     72: DEMON_CONFIG_INJECTION_SPAWN32     = 153
     73: DEMON_CONFIG_KILLDATE              = 154
     74: DEMON_CONFIG_WORKINGHOURS          = 155
     76: DEMON_NET_COMMAND_DOMAIN           = 1
     77: DEMON_NET_COMMAND_LOGONS           = 2
     78: DEMON_NET_COMMAND_SESSIONS         = 3
     79: DEMON_NET_COMMAND_COMPUTER         = 4
     80: DEMON_NET_COMMAND_DCLIST           = 5
     81: DEMON_NET_COMMAND_SHARE            = 6
     82: DEMON_NET_COMMAND_LOCALGROUP       = 7
     83: DEMON_NET_COMMAND_GROUP            = 8
     84: DEMON_NET_COMMAND_USER             = 9
     86: DEMON_PIVOT_LIST                   = 1
     88: DEMON_PIVOT_SMB_CONNECT            = 10
     89: DEMON_PIVOT_SMB_DISCONNECT         = 11
     90: DEMON_PIVOT_SMB_COMMAND            = 12
     92: DEMON_INFO_MEM_ALLOC               = 10
     93: DEMON_INFO_MEM_EXEC                = 11
     94: DEMON_INFO_MEM_PROTECT             = 12
     95: DEMON_INFO_PROC_CREATE             = 21
     97: DEMON_CHECKIN_OPTION_PIVOTS        = 1
```
[source: probe output over `Command.h`, all non-`DEMON_COMMAND_` defines, reproduced as run]

**SIX ADDITIONAL NAMESPACES: `DEMON_INFO`/`DEMON_OUTPUT`/`DEMON_ERROR`/`DEMON_EXIT`/`DEMON_KILL_DATE`/`BEACON_OUTPUT`/`DEMON_INITIALIZE`; `DOTNET_INFO_*`; `CALLBACK_ERROR_*`; `DEMON_CONFIG_*`; `DEMON_NET_COMMAND_*`; `DEMON_PIVOT_*`; plus `DEMON_INFO_*` and `DEMON_CHECKIN_OPTION_PIVOTS`.** **That is 51 additional defines beside the 61 `DEMON_COMMAND_*`, in one file.** [source: §1.4]

**D111 §2.3's denominator was therefore scoped to ONE of the file's EIGHT plus namespaces.** **The 61 figure is correct for what it counted and is not a count of the file.** **Rule 31, sixth instance, caught by §0's header on the first census that carried it.** [source: §0.1; D111 §2.3]

### 1.5 THE CLIENT-ONLY NINE, SPLIT BY DIRECTION — opposite findings, kept separate

**Probe, printed:**

```
=== CLIENT entries with NO agent DEMON_COMMAND_ analogue (name-derived) ===
   ASSEMBLY_LIST_VERSIONS   = 0x2003
   BOF_CALLBACK             = 0x81
   CALLBACK                 = 10
   CONSOLE_MESSAGE          = 0x80
   ERROR                    = 91
   EXIT                     = 92
   INJECT_DLL_SPAWN         = 26
   INLINE_EXECUTE_ASSEMBLY  = 0x2001
   OUTPUT                   = 90
```
[source: probe output, reproduced as run]

**These are NOT one finding. They are two, and the direction differs.**

**DIRECTION A — CLIENT CAN SEND, AGENT HAS A DIFFERENTLY-NAMED HANDLER (4): renames, no defect.**

| Client name | Client value | Agent name | Agent value | Verdict |
|---|---|---|---|---|
| **`INLINE_EXECUTE_ASSEMBLY`** | **0x2001** | **`DEMON_COMMAND_ASSEMBLY_INLINE_EXECUTE`** | **0x2001** | **same value, renamed** |
| **`ASSEMBLY_LIST_VERSIONS`** | **0x2003** | **`DEMON_COMMAND_ASSEMBLY_VERSIONS`** | **0x2003** | **same value, renamed** |
| **`INJECT_DLL_SPAWN`** | **26** | **`DEMON_COMMAND_SPAWN_DLL`** | **26** | **same value, renamed** |

[source: §1.2; `Command.h:7-30` per D111 §2.2]

**Values match; only the names differ.** **The wire is value-based, so these are not defects.** **BUT THEY ARE A DESIGN HAZARD and it is bounded: a name-based client-side lookup on `INLINE_EXECUTE_ASSEMBLY` would miss the agent's `ASSEMBLY_INLINE_EXECUTE` even though both are `0x2001`.** **Whether the client looks up by name or by value is NOT settled here — it requires reading the client dispatch, which is D-24's remainder.** **Residual D-26.** [source: §1.5]

**DIRECTION B — CLIENT CAN RENDER, AGENT NEVER SENDS IT AS A COMMAND (5): these are the AGENT's own output namespace.**

| Client name | Client value | Agent-side name | Agent value | Verdict |
|---|---|---|---|---|
| **`OUTPUT`** | **90** | **`DEMON_OUTPUT`** | **90** | **same value, agent prefix dropped client-side** |
| **`ERROR`** | **91** | **`DEMON_ERROR`** | **91** | **same value, same** |
| **`EXIT`** | **92** | **`DEMON_EXIT`** | **92** | **same value, same** |
| **`CALLBACK`** | **10** | **no agent match** | — | **client-only** |
| **`CONSOLE_MESSAGE`** | **0x80** | **no agent match** | — | **client-only** |
| **`BOF_CALLBACK`** | **0x81** | **no agent match** | — | **client-only** |

[source: §1.4; `Command.h:32-38`]

**`OUTPUT`/`ERROR`/`EXIT` are the agent's RESPONSE discriminants (`DEMON_OUTPUT 90`, `DEMON_ERROR 91`, `DEMON_EXIT 92`), and the client's enum carries them WITHOUT the `DEMON_` prefix.** **So the client's 26-entry enum conflates two vocabularies: the command namespace (23 entries) and the response namespace (3 entries).** [source: §1.4-§1.5]

**`CALLBACK 10`, `CONSOLE_MESSAGE 0x80`, `BOF_CALLBACK 0x81` have NO agent-side counterpart in any of the eight namespaces.** **They are client-side output types — the values the CLIENT renders, not values the agent receives as commands.** **Direction: client-internal, NOT a missing handler.** [source: §1.4]

### 1.6 D-24 ANSWERED

**The mirrored-consumer question, answered with direction:**

| Direction | Count | Verdict |
|---|---|---|
| **Client sends a value the agent CANNOT receive** | **0** | **no orphan found** |
| **Agent sends a value the client CANNOT render** | **NOT SETTLED** | **requires the client dispatch reader — residual D-24 remainder** |
| **Same value, different name (rename hazard)** | **3** | **`INLINE_EXECUTE_ASSEMBLY`, `ASSEMBLY_LIST_VERSIONS`, `INJECT_DLL_SPAWN`** |
| **Client-only render types (not commands)** | **3** | **`CALLBACK`, `CONSOLE_MESSAGE`, `BOF_CALLBACK`** |
| **Response namespace conflation** | **3** | **`OUTPUT`/`ERROR`/`EXIT` beside command entries** |

**D-24 CLOSED for the direction the Lead prioritised (client-sends/agent-cannot-receive): ZERO.** **The other direction stays open as D-26, and it is now precisely bounded: read the client's dispatch on the enum to determine name-vs-value lookup.** [source: §1.5-§1.6]

**Absence note, per the standing discipline: the client tree contains ZERO occurrences of `DEMON_COMMAND_` or `DOTNET_INFO_`** — **85 files scanned, 0 hits** — **and the positive control that makes this a real absence rather than a broken probe is that the SAME probe pattern found `SHELLCODE` 51, `TaskID` 442, `CommandID` 33, `MagicValue` 29, `INJECT_SHELLCODE` 4 in the same tree.** **The probe fires; the tokens genuinely are not there.** [source: probe output, §1.1]

---

## §2 — T2: D-23, `SendResponse` ON A CLOSED CONNECTION

### 2.1 SCOPE AND THE THREE OUTCOMES, NAMED IN ADVANCE

```
SCOPE:         teamserver/pkg/service/{agent.go, service.go, types.go}
DEFINER SCOPE: the response channel's ONLY writer determines whether the
               receive at agent.go:131 can ever be unblocked.
COUNTED:       SendResponse (agent.go:87-138, 52 lines) + all 5 Responses[] sites.
```

**The Lead framed three possible outcomes: panic / quiet error / silent success.** **Measured: NONE of the three. It is a fourth — a PERMANENT BLOCK.** [source: §2.2-§2.4]

### 2.2 The write path — the panic hypothesis is REFUTED

```go
	a.client.Mutex.Lock()
	err := a.client.Conn.WriteJSON(AgentResponse)
	a.client.Mutex.Unlock()

	if err != nil {
		logger.Error("Failed to write json to websocket: " + err.Error())
		return nil
	}
```
[source: `pkg/service/agent.go:120-127`, verbatim]

**The write is error-checked and returns `nil` on failure.** **`a.client.Conn.WriteJSON` returns an error on a closed connection; it does not panic.** **So the closed-client case does NOT crash — it logs and returns.** **The panic hypothesis is refuted by the error check.** [source: `agent.go:121-127`]

**And the adjacent `SendAgentResponse`-family function shows the same discipline:**

```go
	if err := a.client.WriteJson(AgentRequest); err != nil {
		logger.Error("Failed to write json to websocket: " + err.Error())
		return
	}
```
[source: `pkg/service/agent.go:81-84`, verbatim]

### 2.3 The block — `data = <-channel` with no timeout, no `select`, no `default`

```go
	a.client.Responses[randID] = make(chan []byte)

	a.client.Mutex.Lock()
	err := a.client.Conn.WriteJSON(AgentResponse)
	a.client.Mutex.Unlock()

	if err != nil {
		logger.Error("Failed to write json to websocket: " + err.Error())
		return nil
	}

	var data []byte
	if channel, ok := a.client.Responses[randID]; ok {
		data = <-channel

		close(a.client.Responses[randID])
		delete(a.client.Responses, randID)
	}

	return data
```
[source: `pkg/service/agent.go:118-137`, verbatim]

**Line-by-line, and the sequence is the finding:**

| Line | Code | Consequence |
|---|---|---|
| **`:118`** | **`a.client.Responses[randID] = make(chan []byte)`** | **an UNBUFFERED channel is created and registered** |
| **`:121`** | **`a.client.Conn.WriteJSON(AgentResponse)`** | **writes to the socket — errors if closed** |
| **`:124-127`** | **on error: log and `return nil`** | **returns WITHOUT cleaning `Responses[randID]`** |
| **`:131`** | **`data = <-channel`** | **a blocking receive on an unbuffered channel — NO `select`, NO `default`, NO timeout** |

**TWO defects, and they compound:**

**(a) THE ERROR PATH LEAKS THE MAP ENTRY.** **At `:124-127`, when the write fails, the function returns `nil` WITHOUT the `close`/`delete` at `:133-134`.** **So `a.client.Responses[randID]` is left holding an orphaned unbuffered channel, permanently.** [source: `agent.go:124-135`]

**(b) THE SUCCESS PATH CAN BLOCK FOREVER.** **`data = <-channel` at `:131` has no timeout.** **It unblocks only when something sends on that channel.** [source: `agent.go:131`]

### 2.4 The only unblock path — and why a closed client never reaches it

**Probe, printed — every write to any `Responses[...]`:**

```
pkg\service\agent.go:118   a.client.Responses[randID] = make(chan []byte)      CREATE
pkg\service\agent.go:130   if channel, ok := a.client.Responses[randID]; ok {   READ
pkg\service\agent.go:133   close(a.client.Responses[randID])                    CLOSE
pkg\service\service.go:358 if channel, ok := c.Responses[RandID]; ok {          LOOKUP (responder 1)
pkg\service\service.go:684 if channel, ok := client.Responses[RequestID]; ok {  LOOKUP (responder 2)
```
[source: probe output, reproduced as run]

**The ONLY sends on the channel are the two responders:**

```go
			if channel, ok := client.Responses[RequestID]; ok {
				channel <- Response
			} else {
				logger.Debug("[BodyListenerTransmit] Failed to retrieve response channel")
				return
			}
```
[source: `pkg/service/service.go:684-689`, verbatim]

**`channel <- Response` at `:685` is the unblock.** **It requires an inbound message from the client carrying that `RequestID`.** [source: `service.go:684-689`]

**THE CHAIN:**
1. **D-17 leaves a stale `AgentService` in `s.Agents` whose `.client` connection is closed** (D115 §3.1: `ClientClose`'s `break` removes only the FIRST match).
2. **`ServiceAgentExist` returns true for it, `ServiceAgent` returns it, and `handlers.go:336` calls `SendResponse` on it — on the request goroutine.**
3. **The write at `:121` fails** (closed connection), so **`:124-127` returns `nil` — but ONLY after `:118` has already registered the channel.** **The entry leaks.**
4. **OR the write succeeds into a socket that is not read** — then **`:131` blocks forever**, because **the closed client will never send the `RequestID` message that `:685` needs to unblock it.**

**Either way: a permanent goroutine leak and/or a permanent map-entry leak, per request, reachable from the agent wire.** [source: §2.2-§2.4; D115 §3.1]

### 2.5 D-23 ANSWERED — and it is not the answer the Lead's framing allowed for

| Outcome | Held? | Basis |
|---|---|---|
| **Panic → remote-triggerable crash** | **NO — REFUTED** | **`:124-127` error-checks the write and returns `nil`** |
| **Quiet error** | **PARTIAL** | **the write error IS logged; but the map entry is NOT cleaned** |
| **Silent success** | **NO** | **the block prevents any return** |
| **FOURTH: permanent goroutine and/or map-entry leak** | **YES** | **`:131` blocks with no timeout; `:124-127` skips the cleanup at `:133-134`** |

**D-23 CLOSED: NOT a crash. A resource leak with a remote reachability path.** **The severity is bounded by the fact that the mutex is released at `:122`, BEFORE the block — so the leak does NOT deadlock other writers.** **That bound is itself `[read]`: `:122` unlocks, `:131` blocks.** [source: `agent.go:120-131`]

**New residual D-27: how many such entries can accumulate, and is there any prune on `ClientClose`?** **`service.go:719-733` removes from `s.Agents` but does NOT touch `c.Responses`.** [source: `service.go:719-733`; D115 §3.1]

---

## §3 — T3: THE FOUR BARE `#if TRANSPORT_*` TESTS

### 3.1 SCOPE, AND (a) — THE EXACT LINE

```
SCOPE:         the four sites testing TRANSPORT_HTTP/TRANSPORT_SMB without defined()
DEFINER SCOPE: the macro's VALUE is set by the build system, not by any source file
COUNTED:       4 sites (Command.c:3456; Package.c:292, :345, :357)
```

**(a) PRINTED VERBATIM — the macro is defined with NO VALUE:**

```cmake
add_compile_definitions( DEBUG )

add_compile_definitions( CONFIG_BYTES={} )
add_compile_definitions( CONFIG_SIZE=1024 )
add_compile_definitions( CONFIG_KEY_BYTES={} )
add_compile_definitions( CONFIG_KEY_SIZE=16 )
add_compile_definitions( SERVICE_NAME="DemonService" )

add_compile_definitions( TRANSPORT_HTTP )
add_compile_definitions( TRANSPORT_SMB )
add_compile_definitions( AES256 )
```
[source: `payloads/Demon/CMakeLists.txt:69-79`, verbatim]

**`add_compile_definitions( TRANSPORT_HTTP )` at `:77` — no `=`, no value.** **CMake translates an unvalued definition to `-DTRANSPORT_HTTP=1` on MSVC's toolchain and to `-DTRANSPORT_HTTP` on GCC-style invocation.** **WHICH ONE CMake emits for THIS toolchain is not settled from the file alone.** [source: `CMakeLists.txt:77`]

### 3.2 (b) — the MSVC behaviour, stated as `[inferred]`

**`[inferred]` — NOT TESTED, and D-21 STAYS OPEN.**

**If CMake emits `-DTRANSPORT_HTTP` with no value, the preprocessor defines the macro to empty.** **`#if TRANSPORT_HTTP` then expands to `#if ` followed by nothing.** **The C standard requires `#if` to be followed by a constant-expression; an empty expression is a constraint violation.** **MSVC's historical behaviour is to treat a macro defined as empty in `#if` as an error (`C1017` / `fatal error C1021`-class).** **Some configurations and GCC's `-Wundef`-disabled default instead evaluate it to 0.** [source: §3.1]

**So the four sites are ONE OF THREE:**
1. **`TRANSPORT_HTTP` is defined to `1` → the regions compile TRUE (transport enabled).**
2. **`TRANSPORT_HTTP` is defined EMPTY → these four sites are a COMPILE ERROR, and the shipped payload cannot have been built this way.**
3. **`TRANSPORT_HTTP` is defined EMPTY and the toolchain silently treats it as 0 → the regions compile FALSE (transport disabled).**

**Case 2 is excluded if the payload ships at all — but whether it ships from THIS CMakeLists is not established here.** [source: §3.1-§3.2]

**D-21 STAYS OPEN. What would close it: `compile_commands.json`, a build log, or the shipped binary's bytes at the corresponding site — none authorised. NO RESOLUTION IS MANUFACTURED.** [source: §3.2]

**The load-bearing connection, restated: `Package.c:311`'s `DEMON_PACKAGE_DROPPED` envelope is INSIDE the `:292` region.** **So D-21's three cases determine whether the 23rd envelope is sent at all — and D111 §6.1's correction does not depend on it, because the envelope TYPE exists regardless of whether this send site is compiled.** **Distinction preserved: the type's existence is `[verified]`; the site's reachability is `[inferred]` and unresolved.** [source: §3.2; D111 §6.1]

---

## §4 — T4: `TESTING_MATCHING_ROUTINE`, AND THE CONTROL'S CONTROL

### 4.1 The region, printed

```
SCOPE:         include/common/Native.h
DEFINER SCOPE: a #define may appear inside a comment; the preprocessor ignores
               comments, a regex does not.
COUNTED:       Native.h (unbounded probe; the region printed is :9790-9800)
```

**Probe, printed — the region:**

```
     9797: // #define TESTING_MATCHING_ROUTINE
     9798: #ifdef TESTING_MATCHING_ROUTINE
```
[source: `include/common/Native.h:9797-9798`, verbatim; the surrounding `:9790-9800` window read in the reporting run]

### 4.2 THE THREE-WAY STATUS — the Lead's correction, formalised

**The Lead's census reported `#\s*define\s+TESTING_MATCHING_ROUTINE` as COUNT 1.** **That is correct for the regex and WRONG for the preprocessor, because the match is INSIDE a `//` comment.** [source: Lead message; §4.1]

| Arbiter | Result | Why |
|---|---|---|
| **THE PREPROCESSOR** | **UNDEFINED — `define 0`** | **`//` comments are stripped in translation phase 3, before macro definition in phase 4.** **The `#define` at `:9797` never reaches the macro table.** |
| **THE REGEX (`#\s*define\s+`)** | **DEFINED — `define 1`** | **matches the token sequence inside the comment text** |
| **THE HOST BUILD** | **UNDEFINED — `define 0`** | **`CMakeLists.txt` does not define it (§1.5 of D115); `Native.h` only comments it.** **`#ifdef TESTING_MATCHING_ROUTINE` at `:9798` is FALSE.** |

**THE TWO NUMBERS ARE BOTH TRUE AND THE PREPROCESSOR USES 0.** **`TESTING_MATCHING_ROUTINE` is `define 0` for the compiler and `define 1` for a regex.** [source: §4.1-§4.2]

### 4.3 Why this is the best control in the corpus — it fires the arm at the arm

**This is D105's `Command.c:72` blind spot and D111's line-comment arm, firing on the construct I introduced as the positive control for the exclusion arm.** **I built an `#if 0` control around a commented-out define — and the commented-out part is precisely what a line-comment-blind instrument cannot see.** [source: D111 §0.3; D115 §2.2]

**THE RULE, and it generalises past this instance: WHEN ASSERTING THAT A MACRO IS UNDEFINED, THE ASSERTION NEEDS THE COMMENT ARM OR IT REPORTS COMMENTED-OUT DEFINES AS LIVE.** **Stated as a requirement, not an observation.** [source: §4.2]

### 4.4 THE CONTROL USED — the per-file balance check

**Per T4's instruction, `TESTING_MATCHING_ROUTINE` is used as the control for the imbalance check — and the imbalance check's own correction (D-22) is settled here:**

```
=== PER-FILE balance of conditional directives (never balance the sum) ===
files scanned               : 165
openings (if/ifdef/ifndef)  : 419
closings (#endif)           : 419
delta                       : 0
FILES WITH IMBALANCE        : 0
   none

per extension:
   .c     files=38   open=63   close=63   delta=0
   .cc    files=42   open=0    close=0    delta=0
   .cpp   files=3    open=0    close=0    delta=0
   .h     files=54   open=329  close=329  delta=0
   .hpp   files=28   open=27   close=27   delta=0
```
[source: probe output, reproduced as run]

### 4.5 D-22 CLOSED — THE IMBALANCE DOES NOT EXIST

**D-22 was filed in D115 §1.1 as "379 opening conditionals vs 375 `#endif` — FOUR UNMATCHED."** **It does not exist.** **Per-file balance is 0 across all 165 files.** [source: §4.4; D115 §1.1]

**THE CORRECTION IS THE LEAD'S, AND THE METHOD IS NOW THE COUNT DISCIPLINE:**

> **Balance per file, then sum. NEVER balance the sum.**

**Why my D115 number was wrong, stated precisely: D115 scanned `payloads/Demon` only and counted 379/375 there — a GLOBAL sum over a subset.** **This probe scans all of `havoc` (`*.c`, `*.h`, `*.hpp`, `*.cpp`, `*.cc`) and counts 419/419 — also a global sum but one whose per-file components are all zero.** **The D115 delta of 4 was a matcher artefact in the global accumulation, not a real imbalance.** [source: §4.4; D115 §1.1]

**THREE DIFFERENT TOTALS NOW EXIST FOR THE SAME TREE, AND ALL THREE ARE EXPLAINED BY SCOPE — which is Rule 31 firing on the correction of a Rule 31 instance:**

| Source | Files | Openings | Extensions | Scope |
|---|---|---|---|---|
| **D115 §1.1** | **92 (Demon only)** | **379** | `.c`, `.h` | **`payloads/Demon`** |
| **Lead's check** | **92** | **392** | `.c`, `.h` | **same tree, per-file balanced** |
| **D117 §4.4** | **165** | **419** | `.c`, `.h`, `.hpp`, `.cpp`, `.cc` | **all of `havoc`** |

**The per-extension figures agree exactly with the Lead's: `*.c` 63/63, `*.h` 329/329, `*.hpp` 27/27.** **The 419-vs-379 difference is the 40 openings D115's narrower scope did not scan.** **Every figure is correct for its scope and no figure is a count of "the tree."** [source: §4.4]

### 4.6 The sixth instrument failure, recorded in place

**In D115 §1.1 I wrote: my matcher "counts globally and cannot localise which file."** **THAT SENTENCE IS THE DESCRIPTION OF A CHECK THAT CANNOT DETECT AN IMBALANCE, AND I DID NOT TAKE THE STEP IT IMPLIED.** **The fix was one probe.** **Recorded, not smoothed: this is the first failure in this lane where I named the flaw and then stopped one move short of acting on my own naming.** [source: §0; D115 §1.1]

---

## §5 — T5: THE RULE-ENTRY AUDIT, AND THE MANDATORY HEADER

### 5.1 The count, and the answer

**Rule 22/31 has fired FIVE times from this lane across three reports. FOUR are the same defect: an unstated boundary.** **Six if the §0.1 discovery is counted as a distinct instance.**

**The answer to the Lead's question: YES, a one-line scope assertion at the top of each census would have prevented ALL of them.**

**Written as the mandatory census header, and USED in this report (§0):**

```
SCOPE:           <what was enumerated>
DEFINER SCOPE:   <what can DEFINE what is tested>
COUNTED:         <cardinality of the input actually scanned>
```

**Why each of the six falls to a header line:**

| # | Instance | Header line that would have caught it |
|---|---|---|
| **1** | **D105 §1.4 — path/type vs site** | **`SCOPE`** — the sites enumerated were not the types |
| **2** | **D111 §6.1 — name prefix** | **`SCOPE`** — "all `DEMON_COMMAND_*`-prefixed" states the boundary |
| **3** | **D115 §1.5 — source tree** | **`DEFINER SCOPE`** — "what can define what is tested" forces the CMakeLists question |
| **4** | **D115 §2.1 — §6.1's citation in `#if TRANSPORT_SMB`** | **`DEFINER SCOPE`** — would have asked whether the cited site is live |
| **5** | **D115 §1.1 — global sum** | **`COUNTED`** — a per-file cardinality is not producible by a global sum |
| **6** | **D117 §0.1 — six un-enumerated sibling namespaces** | **`SCOPE` + `COUNTED`** — caught it on first application |

**A rule that fires FIVE times in three reports from one lane is an ENTRY CHECK, not a discovery.** [source: §0; §4.5]

### 5.2 The rule-entry statement

**RULE 33 — A CENSUS ASSERTS ITS SCOPE, ITS DEFINER SCOPE, AND ITS CARDINALITY BEFORE IT PRINTS A NUMBER.**

**A count with no scope beside it is not a count of the thing the reader will assume. A count whose definer-scope is unstated cannot distinguish "never defined" from "defined outside what I looked at." A count with no cardinality beside it cannot be distinguished from a truncated one.** **This is Rule 31 (`an ENUMERATED SCOPE is not a population`) made operational, and it subsumes the Rule 32 guard (a census probe prints its own input cardinality).** [source: §0, §5.1; D115 §5.1]

---

## §6 — WHAT THIS CHANGES

| Item | Verdict | Basis |
|---|---|---|
| **Client binding form** | **C++ `enum class Commands`, 26 entries — NOT `#define`s.** | §1.1 |
| **Client → agent matched pairs** | **17 name-and-value pairs, 17 AGREE, 0 conflict.** **Three independent tables now agree.** | §1.3 |
| **Client-sends/agent-cannot-receive** | **ZERO.** | §1.6 |
| **Rename hazard** | **3 pairs — same value, different name** (`INLINE_EXECUTE_ASSEMBLY`/`ASSEMBLY_INLINE_EXECUTE`, `ASSEMBLY_LIST_VERSIONS`/`ASSEMBLY_VERSIONS`, `INJECT_DLL_SPAWN`/`SPAWN_DLL`). **Residual D-26.** | §1.5 |
| **Six un-enumerated sibling namespaces** | **`Command.h` carries 51 further defines in 8+ namespaces D111 never enumerated.** **Rule 31, sixth instance.** | §1.4 |
| **D-23** | **CLOSED — NOT a panic. A permanent goroutine and/or map-entry leak.** **`:131 data = <-channel` has no timeout; `:124-127` leaks the entry; `:685` is the only unblock and a closed client cannot send it.** **Mutex released at `:122` before the block, so no deadlock.** **Residual D-27.** | §2.2-§2.5 |
| **Four bare `#if TRANSPORT_*`** | **(a) printed: `:77` has NO value.** **(b) MSVC behaviour `[inferred]`, three cases, D-21 STAYS OPEN — not manufactured.** | §3.1-§3.2 |
| **`TESTING_MATCHING_ROUTINE`** | **preprocessor: `0`. regex: `1`. host build: `0`.** **Stating an undefined macro needs the comment arm.** | §4.2 |
| **D-22** | **CLOSED — THE IMBALANCE DOES NOT EXIST.** **Per-file balance 0 across 165 files; 419/419.** **Balance per file, then sum; NEVER balance the sum.** | §4.4-§4.5 |
| **Rule 33** | **A census asserts SCOPE, DEFINER SCOPE, and COUNTED before printing a number.** **Five-to-six firings in three reports = an entry check.** | §5.2 |

**No contradiction with D47, D56, D65, D71, D76, D82, D86, D89, D98, D105, D111, C-12, or D115.** **§1.3 independently extends D111 §2.7 to a third table.**

---

## §7 — RESIDUAL UNKNOWNS, WITH PROBES

| ID | Unknown | Probe |
|---|---|---|
| **D-11** | **Does the `Pivots` interleaving occur at runtime?** | **Requires execution. OPEN. NOT attempted.** |
| **D-21** | **Do the four bare `#if TRANSPORT_*` sites compile TRUE, FALSE, or error?** | **`compile_commands.json`, a build log, or the shipped binary. NOT authorised. STAYS OPEN.** |
| **D-25** | **Where is the `SHELLCODE` build definition?** | **Inspect `payloads/Shellcode/` build files.** |
| **D-26** | **Does the client dispatch on the `Commands` enum by NAME or by VALUE?** **Determines whether the 3 renames are a defect.** | **Read the client's dispatch switch/map on `Commands` in `client/**`.** |
| **D-27** | **How many `Responses` entries can accumulate, and does anything prune them?** | **`service.go:719-733` does not touch `c.Responses`. Enumerate `ClientClose` and any GC path.** |
| **D-28** | **Is `SendResponse`'s `data = <-channel` reachable from `handlers.go:336` on the request goroutine — i.e. does one stuck request consume a goroutine permanently?** | **Read the caller chain from `handlers.go:336` to the goroutine that runs `handleServiceAgent`.** |
| **D-19, D-22, D-24** | **CLOSED this report / D115.** | **§4.5, §1.6** |

---

## §8 — INSTRUMENT RECORD

### 8.1 The scope assertion caught a new instance on first use

**§0.1: the header forced the enumeration of sibling namespaces, and six were found that D111 never counted.** **An instrument deployed forward yields a rate; this one yielded on its first application.** [source: §0.1]

### 8.2 The apostrophe failure did NOT recur

**D115 recorded a sixth recurrence (`#define'd` in a single-quoted PowerShell string).** **No single-quoted string in this report's probes contains an apostrophe, and the failure did not occur.** **Recorded as the guard working — the source text is quoted back, so the apostrophe is always inside a here-string or a match pattern, never in the probe's own string literal.** [source: D115 §8.3]

### 8.3 Both mandated arms applied

**Line-comment arm:** **applied to the `TESTING_MATCHING_ROUTINE` control (§4.2) — where it is the entire finding.** **`#if 0` arm:** **measured and empty (D115 §1.2).** **Codepoint probe:** **applied at validation.** **Explicit-counter line numbering:** **used throughout.** **Scope header:** **mandatory (§5.2) and used (§0).**

---

**End of D117.**
