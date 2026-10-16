# D123 — Havoc: orphan accumulation in `ClientService.Responses`, the stuck request goroutine, the blocked Demon build evidence, the client dispatch key, and the conditional scope table

**Document number:** D123 (reserved atomically 2026-10-16 22:20:05 via `_lead_alloc.py`, `O_CREAT|O_EXCL`, first claimant)
**Author / lane:** `havoc-deep`
**Scope owner:** the Havoc C2 tree at `RE_Library\01_SOURCE_c2\havoc\`
**Supersedes-in-part:** none. **Corrects by reference:** D111 §6.1 (reproduced mechanically, not edited), D115 (the `SHELLCODE`/`SEND_LOGS` definedness question, closed here), D105 (the Demon build-evidence gap, re-scoped here), D117 (refusal retained and NOT undone).

---

## §0 — Provenance, method, and the four counters

### §0.1 Rule 33 header — stated once here, restated at every census

- **SCOPE:** the Havoc tree under `RE_Library\01_SOURCE_c2\havoc\`, read statically. **No corpus binary executed. No live C2. No REA, no `open_binary`, no network.**
- **DEFINER SCOPE:** for every preprocessor condition cited, whether a build file in that target's own tree defines the macro. Four build files exist under `payloads\`: `Demon\CMakeLists.txt` (2,295 B), `Demon\makefile` (85 B), `DllLdr\makefile` (579 B), `Shellcode\makefile` (1,320 B). `[verified]`
- **CONDITIONAL SCOPE:** the enclosing `#if`/`#ifdef` stack of each cited site, computed by a character-class-aware state machine (see §5.1), not by regex.
- **COUNTED:** the input cardinality of every census, printed beside its result.

### §0.2 The instrument's own control, stated before its output

§5's table is produced by `condscope.ps1` v4, which walks each line char-by-char through five states (normal, block comment, line comment, double-quote string, char literal) and marks a byte as code only in normal state; a directive is recognised only if the first *code* byte of a line is `#`.

**v3 FAILED the control and v4 is the fix.** The fixture (`condscope_fixture.c`, 18 lines) contains a `#if 0";` sequence **inside a multi-line string** (lines 6–7). v3 recorded that line as **a directive with a condition string** — a plausible, confidently wrong answer of exactly the shape Rule 32 warns about, and worse than a crash because it produces a number. Cause: the escape branch consumed the backslash *and the following newline*, desyncing line boundaries so the `#` stayed masked-true. v4 stops treating backslash-before-newline as an escape. **All 14 expected depths reproduce exactly under v4**, with all four distinguishing cases (block comment, line comment, multi-line string, char literal) separating. `[verified]`

**A table of conditional scopes produced by an unvalidated state machine is a table of the state machine.** The control is not decoration.

### §0.3 What this document does not claim

It does not claim the Havoc Demon was ever built anywhere, by anyone, from this tree, in any configuration. It does not claim any of the defects below has been triggered. It reports what the tree says about itself. Every reachability statement is **`latent`** — reachable from the source as read — never "live" and never "fixed."

---

## §1 — T1 / D-27: orphan accumulation in `ClientService.Responses`

### §1.1 The declaration and the only delete

**SCOPE:** `havoc\teamserver\**\*.go`, recursive · **COUNTED: 202 files.**

`types.go:16` declares the map:

```
Responses map[string]chan []byte
```

A recursive scan for the identifier `Responses` over those 202 files returns **nine occurrences in total**:

| file:line | role |
|---|---|
| `agent.go:114` | `if a.client.Responses == nil` |
| `agent.go:115` | `a.client.Responses = make(map[string]chan []byte)` |
| `agent.go:118` | `a.client.Responses[randID] = make(chan []byte)` |
| `agent.go:130` | `if channel, ok := a.client.Responses[randID]; ok` |
| `agent.go:133` | `close(a.client.Responses[randID])` |
| `agent.go:134` | `delete(a.client.Responses, randID)` |
| `service.go:358` | `if channel, ok := c.Responses[RandID]; ok` |
| `service.go:684` | `if channel, ok := client.Responses[RequestID]; ok` |
| `types.go:16` | the declaration |

Across **28 `delete(` sites in those 202 files, `agent.go:134` is the only `delete` of that map.** `[verified]`

### §1.2 The insert path, printed verbatim

`agent.go:87–138`, the `SendResponse` body. The block the Lead required printed in full:

```go
	// send request
	if a.client.Responses == nil {
		a.client.Responses = make(map[string]chan []byte)
	}

	randID := ...
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

Line numbers as read: `:114`/`:115` guard-and-make, `:118` insert, `:120` `Mutex.Lock`, `:121` `WriteJSON`, `:122` `Mutex.Unlock`, `:124–127` error return, `:129–135` receive-and-cleanup, `:137` `return data`. `[read]`

**The `:118`-before-`:122` ordering the Lead asked me to confirm as `[read]` rather than assumed: CONFIRMED.** The insert at `:118` precedes the `Mutex.Lock` at `:120` and the `Mutex.Unlock` at `:122`. `[verified]`

### §1.3 THE LEAK: closed-but-not-deleted versus deleted-but-not-closed

The Lead's requirement was to say **which** the leak is, because the two are different leaks.

**MEDIUM 1 — the unbuffered channel at `:118`.** `make(chan []byte)` with no capacity. The insert completes without blocking, but the **receive at `:131` (`data = <-channel`)** blocks until some goroutine sends. Nothing in the insert path bounds that wait.

**MEDIUM 2 — the error return at `:124–127` skips the cleanup at `:133–134` entirely.** When `WriteJSON` fails, the function returns `nil` at `:126`. The map entry created at `:118` is **never deleted and never closed** — it is an **orphan**: a live `chan []byte` in a map keyed by a random 6-character ID that no future request can ever collide with. `[verified]`

**So the answer to "closed-but-not-deleted or deleted-but-not-closed": NEITHER, on the error path — it is never-closed-and-never-deleted.** On the success path the cleanup is correct: `:133` closes and `:134` deletes, in that order, both inside the `ok` branch.

**The leak species is therefore: an insert with a conditional cleanup, where the condition that skips cleanup is an error return.** `[read]`

**And the failure is not one-shot.** `:124–127` returns `nil` *after* logging. The calling handler at `handlers.go:336` assigns the result to `Task`; a `nil` `[]byte` is written into the response buffer at `:339`. The orphan persists in the map for the lifetime of the `ClientService`.

### §1.4 THE SCALING QUESTION: replaced or reused on reconnect

The Lead's requirement: is `AgentService` replaced or reused, i.e. does entry count scale per-request or per-request-per-connection?

**Answer: the map accumulates PER REQUEST, and the `ClientService` is REUSED across requests, so the orphan count is unbounded in request count — not bounded by connection count.** `[read]`

**The structural reason, and it is the stronger statement:** the map's lifetime is the `ClientService`'s lifetime, and **nothing on any teardown path owns the map.**

**SCOPE:** the `service` package · **COUNTED: 9 occurrences, 6 files enumerated.**

**Teardown path 1 — `service.go:713`:**

```go
func (s *Service) ClientClose(client *ClientService)
```

**This is the only `func *Close` in the package.** Its body runs `:719–733`, including `:723 for j := range s.Agents` and `:729 s.Agents = append(s.Agents[:j], s.Agents[j+1:]...)` with `:730 break`. **Its entire job is to remove the client from `s.Agents`. It does not touch `c.Responses`. `[verified]`**

**Teardown path 2 — `teamserver.go:773`:**

```go
func (t *Teamserver) RemoveClient(ClientID string)
```

**It also does not touch `c.Responses`. `[verified]`**

**These are the only two teardown paths, and neither dereferences the map.**

**Therefore the finding is not "`ClientClose` forgot the map." It is that `ClientService.Responses` has no owner in any teardown path at all.** `[verified]`

That is a strictly stronger statement, and it is the one D-27 resolved to. A future reader who fixes `ClientClose` alone would leave `RemoveClient` as a second leak of the same map; a reader who fixes both would still not have assigned ownership, because neither is the reason the map exists.

### §1.5 The responder half, and why only one site unblocks

**SCOPE:** the `service` package · **COUNTED: 2 responders.**

- **`service.go:358`** — `if channel, ok := c.Responses[RandID]; ok` — reads the map. This is a **lookup**, not a send.
- **`service.go:684`** — `if channel, ok := client.Responses[RequestID]; ok { channel <- Response }` — **this is the only send in the package.** `[verified]`

**Far more `delete(` sites exist than cleanup paths:** 28 across 202 files, exactly one of which (`agent.go:134`) targets this map. `[verified]`

**Consequence for §1.3:** the only unblock for the `:131` receive is `:684`. If `:684` never fires — because the agent never answers, because the connection is wedged (§2), or because the entry was orphaned by the error path at `:124–127` and there is no future request to pair it with — then `:131` blocks forever and the goroutine holding it is not reclaimable.

### §1.6 The stuck request goroutine: T2 / D-28

**The goroutine chain, enumerated in full:**

| site | what it does |
|---|---|
| `http.go:211` | `h.GinEngine.POST("/*endpoint", h.request)` — Gin/net-http |
| `http.go:93` | `func (h *HTTP) request(ctx *gin.Context)` |
| `http.go:186` | `if Response, Success := parseAgentRequest(...)` |
| `handlers.go:23` | `func parseAgentRequest(...) (bytes.Buffer, bool)` |
| `handlers.go:42` | `if Header.MagicValue == agent.DEMON_MAGIC_VALUE` |
| `handlers.go:43` | `return handleDemonAgent(...)` |
| **`handlers.go:47`** | **`return handleServiceAgent(Teamserver, Header, ExternalIP)`** |
| **`handlers.go:311`** | **`func handleServiceAgent(...) (bytes.Buffer, bool)` — plain function, NO `go`, no context parameter** |
| `handlers.go:336` | `Task = Teamserver.ServiceAgent(Header.MagicValue).SendResponse(AgentData, Header)` |
| **`agent.go:131`** | **`data = <-channel`** |

**`external.go:50`** is the second `parseAgentRequest` call site.

**`http.go:211` registers a net/http handler. Go's `net/http` serves each connection on its own goroutine and runs the handler inline on it.** There is no `go` keyword on any link of this chain. **So the handler goroutine and the connection goroutine are the same goroutine, and `agent.go:131` blocks it while holding the connection open.** `[verified]`

**The enumeration the Lead required — `select`, `context`, or a deadline anywhere on this path:**

| file | hits | detail |
|---|---|---|
| `handlers.go` | **0** | — |
| `agent.go` | **0** | — |
| `types.go` | **0** | — |
| `service.go` | **1** | `:39`, `upgrade.Upgrade(...)` — the WebSocket upgrade in the service package |
| `http.go` | **2** | `:278` `ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)` and `:284 select {` — **both inside `Stop()`** |

**Both `http.go` hits are in the shutdown path, not the request path.** `[verified]`

**And both `http.Server` literals carry only two fields:**

```go
h.Server = &http.Server{
    Addr:    ...,
    Handler: h.GinEngine,
}
```

at `http.go:230` and `http.go:262`. **No `ReadTimeout`. No `WriteTimeout`. No `IdleTimeout`. No `ReadHeaderTimeout`.** `[verified]`

**Conclusion, stated flatly as the Lead required:** a blocked `agent.go:131` holds the net/http connection goroutine **and** the HTTP connection open indefinitely, bounded by nothing on the server side.

**The client side of the same question:** whether the Havoc client puts a deadline on this request is a separate read and is **not asserted here**; the server-side bound is `none`, which is sufficient for the finding independent of the client.

**The species:** `handler goroutine == connection goroutine` + `no server timeout` + `unbounded channel receive` = one unresponded request costs a permanent goroutine and a permanent connection. `[read]`

---

## §2 — T3 / D-21: the Demon build evidence is genuinely absent

**CLOSED `[blocked]` WITH A NAMED MISSING INGREDIENT.**

**SCOPE:** `RE_Library\` recursive · **COUNTED: 58,321 files.**

| probe | result |
|---|---|
| `compile_commands.json` | **0** |
| `CMakeCache.txt` | **0** |
| `CMakeFiles` | **0** |
| CI config | **66 hits, all issue templates and docs — there is no `workflows\` directory in the Havoc tree at all** |
| logs | **15 hits, all Metasploit spec fixtures** |
| MSVC projects | **134** — all Metasploit or Covenant |
| object files | **10** — all Metasploit or Covenant |
| PE artifacts | **211** — all Metasploit or Covenant |

**No artifact from the Demon target is present in any of these.**

**The named missing ingredient: a recorded invocation of the Demon build.** A makefile is a build **instruction**, not build **output**. It cannot answer what the compiler did, which macros it defined, or whether the target was built at all. `[verified]`

**D117's refusal is not undone.** D117 declined to characterise the Demon's compiled behaviour on this evidence, and nothing here changes that.

**The provenance contrast the Lead asked to be noted, because the labels match while the provenance does not:** **D116 closed a `[blocked]` by INHERITING it from a brief, and then caught itself doing so.** D-21 was closed **by scanning 58,321 files.** D116's rule — **"a `[blocked]` sourced from a brief is a FALSE BLOCKED"** — is what this section is written against: the label is the same, the provenance is opposite, and only the scan licenses the label.

**And the lead's own D123 brief contained a false premise this section corrects:** the brief said the 7z was blocked. **A value sourced from a brief is an untested value.**

---

## §3 — T4 / D-26: the client dispatch key

### §3.1 The wire is numeric

**SCOPE:** `client\src\Havoc\Demon\` · **COUNTED: 27 sites in `CommandSend.cc`.**

Every outgoing command packet in `client\src\Havoc\Demon\CommandSend.cc` carries its discriminant as a **string-encoded integer**:

```cpp
{ "CommandID", to_string( static_cast<int>( Commands::X ) ).c_str() }
```

at lines **36, 53, 69, 84, 104, 128, 152, 170, 187, 212, 236, 260, 279, 297, 315, 334, 354, 373, 389, 408, 437, 472, 491, 510, 528, 549, 569.** `[verified]`

The receiving side parses the string back to an integer and switches on it — `Packager.cc:715` `int CommandID = QString( Package->Body.Info[ "CommandID" ].c_str() ).toInt();` then `:718 switch ( CommandID )`, with cases `:720` `CONSOLE_MESSAGE`, `:735` `BOF_CALLBACK`, `:770` `CALLBACK`, and `:785–786` `default: spdlog::error( "[PACKAGE] Command not found" )`. `[verified]`

**`Packager.cc:50` declares the envelope type as `const int Util::Packager::Session::ReceiveCommand = 0x4;`** — a **Session** envelope, sent by **zero** Go files. `[verified]`

### §3.2 The three renames are structurally safe on the wire — DOWNGRADED TO A DOCUMENTATION DEFECT

`client\include\Havoc\DemonCmdDispatch.h:23–51` declares `enum class Commands` with 26 entries. Against the agent's 61 `DEMON_COMMAND_*` values, three pairs differ **in name while agreeing in value**:

| client name | agent name | value |
|---|---|---|
| `INLINE_EXECUTE_ASSEMBLY` | `ASSEMBLY_INLINE_EXECUTE` | `0x2001` |
| `ASSEMBLY_LIST_VERSIONS` | `ASSEMBLY_VERSIONS` | `0x2003` |
| `INJECT_DLL_SPAWN` | `SPAWN_DLL` | `26` |

**Each pair agrees on its value, and the wire is numeric (§3.1). A rename that preserves the value cannot break a numeric dispatch.** `[verified]`

**The Lead's caveat, and its answer.** The downgrade holds **only if** the agent's values are independently assigned rather than derived from the client enum — because a derived table would propagate a client-side value change into the agent.

**SCOPE:** the Havoc tree · **COUNTED: 24 script/build files; 80 C/H/HPP files under `payloads\`; 210 client files.**

| probe | result |
|---|---|
| `Commands::` in `payloads\**\*.{c,h,hpp}` | **0 hits** |
| `DemonCmdDispatch` in `payloads\**\*.{c,h,hpp}` | **0 hits** |
| `enum class Commands` in `payloads\**\*.{c,h,hpp}` | **0 hits** |
| code generators (`parse.*enum`, `generate.*define`) | **0 hits** |
| `DemonCmdDispatch` in client build files | **1 hit — `client\CMakeLists.txt:73 include/Havoc/DemonCmdDispatch.h`** |

**The one `DemonCmdDispatch` hit in a build file is in the CLIENT's `CMakeLists.txt`, not the payload's.** The Demon payload's `CMakeLists.txt` never mentions the header.

**Structural confirmation:** the client enum is **`enum class Commands` — C++.** The agent's `Command.h` is **C** and includes only `<core/Parser.h>` (`Command.h:4`). Different language, different compilation unit, no include path between them.

**VERDICT: the values are INDEPENDENTLY ASSIGNED. The rename downgrade to a documentation defect STANDS.** `[verified]`

**The residual is real and is not a wire defect:** a value-preserving rename is safe to *compile* and safe on the *wire*, and remains **a maintenance hazard** — a future edit that renumbers one side to restore name-value correspondence would be a wire break. The defect is that the correspondence is maintained by convention and pinned by nothing.

### §3.3 The second dispatch axis is by STRING

The Lead asked for this on its own line, and it is a **different and independent** rename hazard.

**`Commands.cc:13`** declares `std::vector<DemonCommands::Command_t> DemonCommands::DemonCommandList`, keyed by each entry's `.CommandString` — lowercase verb strings (`"help"`, `"sleep"`, `"checkin"`, `"job"`, `"task"`, `"proc"`). `[read]`

**`CommandOutput.cc` (110 lines, read in full)** dispatches the *response* path on string literals:

- `:19` `MessageType = JsonDocument[ "Type" ].toString()`
- `:26` `if ( MessageType == "Error" || MessageType == "Erro" )`
- `:28` `"Good"` · `:30` `"Info"` · `:32` `"Warning" || "Warn"`
- `:53` `Type = JsonDocument[ "MiscType" ].toString()`
- `:56` `"screenshot"` · `:63` `"download"` · `:71` `"ProcessUI"` · `:85` `"FileExplorer"` · `:99` `"disconnect"` · `:103` `"reconnect"`

**On this axis a rename is not safe.** Changing `"ProcessUI"` to `"Process_UI"` on either side silently routes the response to the `default` branch — `Packager.cc:786` `spdlog::error( "[PACKAGE] Command not found" )` — with no compile error on either side. **A string dispatch axis has no compiler check at all.** `[verified]`

**The tolerance for `"Erro"` at `:26`** is a misspelling folded into the accepted set. Whether it is a defensive accommodation for an agent-side typo or itself the residue of one is **not determined here**; it is recorded because a tolerance of that shape propagates — a third variant would not be caught by a compiler either.

### §3.4 The collision question, both sets on one axis

The Lead required both sets on one axis and a stated direction.

**Client enum (26):** `CHECKIN=100 · CALLBACK=10 · CONSOLE_MESSAGE=0x80 · BOF_CALLBACK=0x81 · SLEEP=11 · PROC_LIST=12 · FS=15 · INLINE_EXECUTE=20 · JOB=21 · INJECT_DLL=22 · INJECT_SHELLCODE=24 · INJECT_DLL_SPAWN=26 · TOKEN=40 · PROC=0x1010 · INLINE_EXECUTE_ASSEMBLY=0x2001 · ASSEMBLY_LIST_VERSIONS=0x2003 · NET=2100 · CONFIG=2500 · SCREENSHOT=2510 · PIVOT=2520 · TRANSFER=2530 · SOCKET=2540 · KERBEROS=2550 · OUTPUT=90 · ERROR=91 · EXIT=92`

**26 = 20 request entries + 3 render entries (`CALLBACK`, `CONSOLE_MESSAGE`, `BOF_CALLBACK`) + 3 response entries (`OUTPUT`, `ERROR`, `EXIT`).** Of the 20 request entries, **17 match agent names exactly and 3 are the renames of §3.2.**

**THE FREQUENCY TABLE — counted over the agent's 61 `DEMON_COMMAND_*` values:**

| client value | collides with | occurrences |
|---|---|---|
| `CALLBACK = 10` | `DEMON_COMMAND_NO_JOB` 10, `DEMON_COMMAND_TOKEN_FIND_TOKENS` 10, `DEMON_COMMAND_FS_CAT` 10 | **3** |
| `CONSOLE_MESSAGE = 0x80 = 128` | — | **0** |
| `BOF_CALLBACK = 0x81 = 129` | — | **0** |
| `OUTPUT = 90` | — | **0** |
| `ERROR = 91` | — | **0** |
| `EXIT = 92` | — | **0** |

**The direction, which is the whole point:** `CALLBACK = 10` collides **numerically** with three values in the `DEMON_COMMAND_*` namespace. But those two sets are read at **different points in the protocol**:

- `CALLBACK` is read **on the response path**, inside the `ReceiveCommand` branch (`Packager.cc:707`, case at `:770`) — it discriminates **a response envelope**.
- `10` is read as a **request sub-command ID** inside the `DEMON_COMMAND_*` space.

**Different discriminants, different envelopes, mutually exclusive branches.** `[verified]`

**And the collision is separated a second time by the nested sub-op space.** `DEMON_COMMAND_FS = 15` is a top-level command; `DEMON_COMMAND_FS_DIR = 1` through `DEMON_COMMAND_FS_CAT = 10` is a **sub-op range** inside it. `DEMON_COMMAND_FS_CAT = 10` and `DEMON_COMMAND_NO_JOB = 10` therefore occupy the same integer **inside two different value spaces**, reached only after the outer discriminant has already been consumed. The same holds for `DEMON_COMMAND_TOKEN_FIND_TOKENS = 10` inside `TOKEN = 40`.

**Reading: NUMERICALLY COINCIDENT, STRUCTURALLY DISJOINT.** `[verified]`

**The `2560` question, resolved.** The agent list carries `2560`; the client enum does not. **SCOPE:** agent `Command.h` vs 210 client files · **COUNTED: 1 agent define, 0 client hits.**

| side | result |
|---|---|
| `Command.h:29` | `#define DEMON_COMMAND_MEM_FILE 2560` |
| client, literal `2560` | **0 hits across 210 files** |
| client, `MEM_FILE` | **0 hits across 210 files** |

**Verdict: agent-only. No client-side counterpart exists.** `[verified]`

**This is a finding in its own right, not merely a collision answer.** The neighbouring memory ops in the same block are `DEMON_INFO_MEM_ALLOC 10`, `DEMON_INFO_MEM_EXEC 11` (`Command.h:92–94`), and those *do* have client-reachable paths. `DEMON_COMMAND_MEM_FILE` names a memory-file operation that **no client build can request.** It is either an unimplemented client feature or a removed one. **Stated as `[absence]` with the enumeration shown; not classified as dead code, because a third-party client is not in scope.**

**And the `ReceiveCommand = 0x4` declaration (`Packager.cc:50`)** is a **Session** envelope type sent by **zero** Go files — a second named-but-unrequested discriminant on the same side of the protocol as `MEM_FILE`. **Two instances of the same shape.**

---

## §4 — T5: the conditional scope table, with the DEFINER SCOPE column

### §4.1 Why this table exists

D111 §6.1 cites `Package.c:311`'s `DEMON_PACKAGE_DROPPED` as a transport-conditional site. D115 records `SHELLCODE` and `SEND_LOGS` as macros in a definedness class.

**A count whose sites are inside `#if` blocks is a count of the source, not of the build.** The table below resolves each site against (a) the `#if` stack that encloses it and (b) whether the target's own build files define the macro. **The two are different questions, and the third column is where the interesting cases live.**

**SCOPE:** `payloads\Demon\` · **COUNTED: 5 files parsed, all distinct.**

### §4.2 The table

| Site | Enclosing condition | Depth | Build defines it? | Category |
|---|---|---|---|---|
| `Command.h` — 111 `#define` sites | `#ifndef DEMON_COMMAND_H` (include guard) | 1 | n/a (guard) | **non-conditional by construction** |
| `Package.c:311` `DEMON_PACKAGE_DROPPED` | `#if TRANSPORT_SMB` | 1 | **YES** (`CMakeLists.txt:78`) | **present in all builds** |
| `Package.c:352` `DEMON_COMMAND_GET_JOB` | — | **0** | n/a | **unconditional** |
| `Macros.h:43` `#if SEND_LOGS` | `#ifndef DEMON_MACROS_H >> #ifdef DEBUG` | **2** | **NO** | **present under NO defined condition** |
| `Macros.h:49` `#elif SHELLCODE` | `#ifndef DEMON_MACROS_H >> #ifdef DEBUG >> [elif SVC_EXE]` | **3** | **NO** | **present under NO defined condition** |
| `Macros.h:62` `#if SEND_LOGS` (PUTS) | `#ifndef DEMON_MACROS_H >> #ifdef DEBUG` | **2** | **NO** | **present under NO defined condition** |
| `Native.h:9798` `#ifdef TESTING_MATCHING_ROUTINE` | `#if !defined(_NTDLL_) >> #if !defined(_NTLSA_IFS_) >> #if (_WIN32_WINNT >= 0x0501)` | **3** | **NO** | **present under NO defined condition** |
| `MainDll.c:34` `!defined(SHELLCODE) && defined(DEBUG)` | — | **0** | n/a | **unconditional site** |
| `MainDll.c:40` `#ifdef SHELLCODE` | — | **0** | **NO** | see §4.4 |

### §4.3 The DEFINER SCOPE join — every macro the sites test, against four build files

**SCOPE:** `payloads\` · **COUNTED: 4 build files — `Demon\CMakeLists.txt`, `Demon\makefile`, `DllLdr\makefile`, `Shellcode\makefile`.**

| macro | defined in build? | evidence |
|---|---|---|
| `TRANSPORT_HTTP` | **YES** | `CMakeLists.txt:77 add_compile_definitions( TRANSPORT_HTTP )` |
| `TRANSPORT_SMB` | **YES** | `CMakeLists.txt:78 add_compile_definitions( TRANSPORT_SMB )` |
| `DEBUG` | **YES** | `CMakeLists.txt:69 add_compile_definitions( DEBUG )` |
| `AES256` | **YES** | `CMakeLists.txt:79 add_compile_definitions( AES256 )` |
| `CONFIG_BYTES` / `CONFIG_SIZE` / `CONFIG_KEY_BYTES` / `CONFIG_KEY_SIZE` / `SERVICE_NAME` | **YES** | `CMakeLists.txt:71–75` |
| **`SHELLCODE`** | **NO** | 7 raw matches, **all false positives** — see §4.4 |
| **`SEND_LOGS`** | **NO** | **0** |
| **`SVC_EXE`** | **NO** | **0** |
| **`TESTING_MATCHING_ROUTINE`** | **NO** | **0** |
| `DEMON_COMMAND_H` / `DEMON_MACROS_H` | **NO** | include guards, 0 — correct |
| `WIN_X64` / `WIN_X86` / `DBG` / `_WIN64` / `USE_LPC6432` | **NO** | **0** each |

**And the second half of the join — is the macro `#define`d at any SOURCE site?** **SCOPE:** all `payloads\**\*.{c,h,hpp}` · **COUNTED: 0 sites for `SHELLCODE`, `SVC_EXE`, `SEND_LOGS`, `WIN_X64`, `WIN_X86`, `DBG`.**

**So these macros are defined in NO build file and `#define`d at NO source site. That is the third category, and it is populated.**

### §4.4 The `SHELLCODE` false positive — a substring probe answering a definedness question

My first pass reported `SHELLCODE` as **DEFINED-IN-BUILD: YES, 7 hits**, matching in `payloads\Shellcode\makefile`. **Reading the file shows all seven are the literal lowercase word "shellcode" — not a `-D` flag:**

- `:17`, `:23`, `:34` — inside `echo` strings
- `:10`, `:11` — the `EXECUTABLE_X64` / `EXECUTABLE_X86` names
- `:12`, `:13` — the output `.bin` paths

**And the makefile's `CFLAGS` (`:4–8`) contains no `-D` flag at all:** `-Os -fno-asynchronous-unwind-tables -nostdlib -fno-ident -fpack-struct=8 -falign-functions=1 -s -ffunction-sections -falign-jumps=1 -w -falign-labels=1 -fPIC -Wl,-TScripts/Linker.ld -Wl,-s,--no-seh,--enable-stdcall-fixup`. `[verified]`

**A second false positive of the same class:** `EXE` returned 19 hits, all of them `-e,` / `exe` / `EXECUTABLE_X64` substrings.

**And the false positives extend to the flag syntax itself:** a `-D\s*[A-Za-z_]` scan over all four build files returns **one hit, `makefile:4 rm -rf cmake-build-debug`** — the `-d` of `cmake-build-debug`. **The scan for definition flags matched a hyphenated directory name.** `[verified]`

**Generalisation: confirming a cited site is not verifying a census, and a substring probe answering a definedness question is not a definedness test.** The class is the same one that produced this document's §4.3: the honest count comes from reading the file, not from matching a token in it.

### §4.5 D-25 CLOSED: `SHELLCODE` is defined nowhere

This answers the question D115 opened.

**`SHELLCODE` is defined in no build file and `#define`d at no source site.** `[verified]`

**And the reason it is nonetheless *tested* is now visible.** `MainDll.c`'s two direct consumers are at **depth 0**:

- `MainDll.c:5` `#ifndef SHELLCODE`
- `MainDll.c:34` `#if !defined(SHELLCODE) && defined(DEBUG)`
- `MainDll.c:40` `#ifdef SHELLCODE`

**The two sites that test `SHELLCODE` sit outside every enclosing condition.** So the macro is referenced unconditionally while being defined nowhere — which is exactly why it lands in D115's definedness class.

**And `CMakeLists.txt:55–64` compiles all three entry points into ONE target:**

```
:55 src/Demon.c
:57-58 # windows exe   / src/main/MainExe.c
:60-61 # windows dll   / src/main/MainDll.c
:63-64 # windows service / src/main/MainSvc.c
:65 )
```

**All three in one `MAIN_SOURCE` list, compiled unconditionally.** `[verified]`

**So the entry-point selection is not made by the build. It is made by preprocessor conditions inside `MainDll.c` that test a macro nobody defines.** `[read]`

`SHELLCODE` is therefore present in no build — not because a condition excludes it, but because **no build sets the condition and the sites that read it are unguarded.**

### §4.6 `#if` on an undefined macro is not a conditional build — it is a dead arm

**This is the structural consequence of §4.3, and it is load-bearing. `Macros.h:40–72`, printed verbatim:**

```c
41: // DEBUG
42: #ifdef DEBUG
43: #if SEND_LOGS
44: #define PRINTF( f, ... )                { DemonPrintf( "[DEBUG::%s::%d] " f, __FUNCTION__, __LINE__, __VA_ARGS__ ); }
45: #define PRINTF_DONT_SEND( f, ... )      { ; }
46: #elif SVC_EXE
47: #define PRINTF( f, ... )                { DbgPrint( "[DEBUG::%s::%d] " f, __FUNCTION__, __LINE__, __VA_ARGS__ ); }
48: #define PRINTF_DONT_SEND( f, ... )      { DbgPrint( "[DEBUG::%s::%d] " f, __FUNCTION__, __LINE__, __VA_ARGS__ ); }
49: #elif SHELLCODE
50: #define PRINTF( f, ... )                { LogToConsole( "[DEBUG::%s::%d] " f, __FUNCTION__, __LINE__, __VA_ARGS__ ); }
51: #define PRINTF_DONT_SEND( f, ... )      { LogToConsole( "[DEBUG::%s::%d] " f, __FUNCTION__, __LINE__, __VA_ARGS__ ); }
52: #else
53: #define PRINTF( f, ... )                { printf( "[DEBUG::%s::%d] " f, __FUNCTION__, __LINE__, __VA_ARGS__ ); }
54: #define PRINTF_DONT_SEND( f, ... )      { printf( "[DEBUG::%s::%d] " f, __FUNCTION__, __LINE__, __VA_ARGS__ ); }
55: #endif
56: #else
57: #define PRINTF( f, ... )                { ; }
58: #define PRINTF_DONT_SEND( f, ... )      { ; }
59: #endif
```

with the identical shape repeated for `PUTS` at `:61–72`.

**In C preprocessing, `#if SEND_LOGS` where `SEND_LOGS` is undefined evaluates the identifier to `0`.** Only `#ifdef` / `#ifndef` / `defined()` test mere definedness. So:

- **`:43` `#if SEND_LOGS` → always false.** The `DemonPrintf` arm never compiles.
- **`:46` `#elif SVC_EXE` → always false.** The `DbgPrint` arm never compiles.
- **`:49` `#elif SHELLCODE` → always false.** The `LogToConsole` arm never compiles.
- **`:52` `#else` → taken.** With `DEBUG` defined (`CMakeLists.txt:69`), **`PRINTF` resolves to plain `printf`.**

**This is the third category doing real work: an arm that is not "conditionally compiled" but *unreachable by construction*, because the condition it tests is an undefined identifier in an expression context, not a definedness test.** `[verified]`

**A reader auditing this file for a debug-logging path would find four arms and count four outcomes. Three of them are dead, and the file gives no signal — no `#error`, no comment — that says so.** The registration of these names in D115's definedness class is what makes the arms legible; without it, the table reads as a dispatch.

**One consequence worth stating:** `DEMON_MACROS_H` as an include guard appears at depth 1 — so a nested `PRINTF` definition inside a guard is fine, but nothing in this file can detect that `SEND_LOGS` and `SVC_EXE` were *intended* to be set. **Two build configurations described by these arms (`SEND_LOGS`, `SVC_EXE`) cannot be produced by any build file in the tree.**

### §4.7 The two unconditional `TRANSPORT_SMB` sites

`Package.c:292 #if TRANSPORT_SMB` wraps `:311 Package = PackageCreateWithRequestID( DEMON_PACKAGE_DROPPED, RequestID )` with `:315 #endif` — **depth 1, defined in the build.** D111 §6.1's cite reproduced mechanically. `[verified]`

Also inside `TRANSPORT_SMB`: `:345`, `:357`. And `:352 PackageCreateWithMetaData( DEMON_COMMAND_GET_JOB )` is at **depth 0** — **unconditional, running regardless of transport.** `[verified]`

**So on a `TRANSPORT_HTTP`-only build, `DEMON_PACKAGE_DROPPED` disappears while `DEMON_COMMAND_GET_JOB` survives — two adjacent packet constructions, one conditional and one not, in the same function.** That asymmetry is the thing a source-level census misses and a conditional-scope census catches.

**Note also that `TRANSPORT_HTTP` and `TRANSPORT_SMB` are both defined unconditionally at `CMakeLists.txt:77–78`** — so **both are present in every build this tree can produce**, and the `#if` is a source-level switch with no build-level effect. `[verified]`

---

## §5 — Cross-cutting: what the four counters say

| counter | verifiable? | note |
|---|---|---|
| `Responses` occurrences (9) | **yes** — enumerable identifier | the only delete is `agent.go:134` |
| `delete(` sites (28) | **yes** | one targets the map |
| teardown paths (2) | **yes** | neither touches the map |
| conditional sites (5 files) | **yes**, with a control-validated state machine | §5.1 |
| `DEMON_COMMAND_*` (61) | **yes** | independently assigned |
| collision frequency | **yes** | `CALLBACK=10` is the only multi-collision |
| client `2560` hits (0) | **yes** | agent-only |

**§5.1 — the instrument carried a control that failed before it passed.** `condscope.ps1` v3 produced a plausible, confidently wrong answer on the fixture's multi-line string (a `#if 0";` recorded as a directive with a condition string). It was caught because the fixture contained a case whose correct answer is "not a directive." **A table of conditional scopes produced by an unvalidated state machine is a table of the state machine** — and the failure mode here was a number, not an exception, which is why the fixture existed.

**§5.2 — the five-count closure in this document balances per file, then sums.** §4.2's 5 parsed files, §4.3's 4 build files, §1.1's 202 Go files, §1.4's 6 declared-identifier files, §3.2's 24 + 80 + 210. **No global sum is used as a balance check anywhere in this document.**

---

## §6 — Residuals, stated as open

| id | residual |
|---|---|
| **R-123.1** | Whether the Havoc **client** places a deadline on the request whose server side is unbounded (§3.3). Server side is `none`; client side is unwritten here. `[open]` |
| **R-123.2** | Whether `DEMON_COMMAND_MEM_FILE 2560` is an unimplemented client feature or a removed one (§3.4). **A third-party client is not in scope.** `[open]` |
| **R-123.3** | Whether `"Erro"` at `CommandOutput.cc:26` is defensive accommodation or the residue of a misspelling (§3.3). `[open]` |
| **R-123.4** | Whether any caller relies on `get_tlvs`' mixed exact/masked form — **`msf-diver`'s open thread, not this document's.** `[open, elsewhere]` |
| **R-123.5** | Whether the three `TRANSPORT_HTTP`/`TRANSPORT_SMB` sites behave differently in a real build. **D-21 stands: no recorded build invocation exists, so this cannot be answered from the corpus.** `[blocked]` |
| **R-123.6** | Whether the orphan accumulation at §1.3 is *exploitable* or merely *a leak*. Requires an unresponded-request condition that this static read cannot establish. **`latent`, not `live`.** `[blocked]` |

**§6.1 — D-27's structural conclusion, restated for the reader who skims.** The `Responses` map is declared at `types.go:16`, inserted at `agent.go:118`, deleted exactly once at `agent.go:134`, and **owned by no teardown path.** Both teardown paths (`service.go:713 ClientClose`, `teamserver.go:773 RemoveClient`) skip it. **Fixing either one alone does not fix the ownership, and neither is the reason the map exists.** The error return at `agent.go:124–127` is where entries become orphans, and it is reachable on every failed `WriteJSON`.

---

## §7 — Method record

**Probes run:** 4 build files read in full (2295 + 85 + 579 + 1320 B); `Macros.h:40–72` printed verbatim; `CMakeLists.txt:55–85` read; `CommandOutput.cc` read in full (110 lines); `Commands.cc` and `CommandSend.cc` enumerated for the packet idiom; `condscope.ps1` v4 against a 10-site table with a validated 14-assertion fixture; identifier and `delete(` enumerations over 202 Go files; a definedness join over 4 build files; two substring false positives caught and corrected (§4.4).

**Instrument failures, all self-caught:**
- **I1** — `condscope.ps1` v1: `[string[]]$Sites` corrupted `[pscustomobject]` entries crossing the script boundary; `$s.Path` null → `Test-Path` bind failure. Fixed with `[string]$SitesJson` + `ConvertFrom-Json`.
- **I2** — string-literal state was masked *true* in the code mask, so `#` at line start inside a string read as a directive. Fixed before running.
- **I3** — `condscope.ps1` v3 killed a fixture assertion by consuming backslash+newline as an escape, desyncing line boundaries. **Caught by the fixture's multi-line-string case.** Fixed in v4.
- **I4** — `SHELLCODE` reported DEFINED-IN-BUILD on 7 hits that were the literal word in echo strings and paths. **A substring probe answering a definedness question.** Fixed by reading the file.
- **I5** — `-D\s*[A-Za-z_]` matched `-d` inside `cmake-build-debug`. Same class as I4.
- **I6** — a duplicate-key hashtable error from putting directive names and depths in one table. Fixed by splitting.
- **I7** — the D121 four-lane collision. **My enumeration of D121 was correct and the instrument was structurally incapable of failing** — a `Test-Path` on one's own intended filename is false for every number. **Not my error; the instrument's.** D123 was reserved atomically at 22:20:05.

**Allocation:** D123 reserved at 22:20:05 via `_lead_alloc.py` (`O_CREAT|O_EXCL`). Nothing renamed. The four D121 files stand at D121.

---

**Tags used:** `[verified]` · `[read]` · `[inferred]` · `[absence]` · `[blocked]` · `[open]`.

**Statement of scope:** every claim in this document is static, from source, read-only. **No corpus binary was executed. No live C2 was contacted. No REA, no `open_binary`, no network. No handler was authorised, simulated, or contacted.** D111, D115, D105 and D117 are **corrected by reference and were not edited.**

**End of D123.**
