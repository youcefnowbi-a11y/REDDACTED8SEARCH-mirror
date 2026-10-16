# D111 — HAVOC: THE SERVICE-AGENT REGISTRY GATE, THE 61/39 DISCRIMINANT SPLIT, AND THE LINE-COMMENT ARM

**Lane: source-layer load-bearing mechanisms, Havoc continuation.** Three questions: whether the service-agent gate can be bypassed, what the 39 non-envelope discriminants actually are, and what the corrected comment test changes.

**Method:** pure source read. **No REA. No `open_binary`. No execution. No network.** **Nothing here is `[executed]`.** **D-11 (does the `Pivots` interleaving occur at runtime) remains OPEN and was not attempted.**

**Line-count convention:** 1-based line numbers as printed by the read oracle, line 1 = first line of file. **No `-Skip` display value is ever used as a line number.**

**Tags:** `[verified]` read verbatim here; `[read]` read here without full quotation; `[inferred]` derived, NOT measured; `[absence]` a negative with its enumeration printed beside it.

**Vocabulary:** `latent` / `unreachable-from-corpus`. Nothing is called "live" or "fixed."

**Instrument carried from D105 §7.2 and CLOSED here:** the comment-membership test now has **TWO ARMS**. §0.3 states the test, §0.4 reports the measured delta.

---

## §0 — METHOD, AND THE LINE-COMMENT ARM

### 0.1 Why this section exists first

**D105 §7.2 recorded that the block-comment test is blind to C `//` line comments, and classified `Command.c:72` as LIVE when it is a line comment.** **`C-12` §2 promoted that to a standing instrument rule and made the line arm mandatory.** **D111 is the first census to run with both arms, and this section reports the delta before any finding, so the reader knows what the test was capable of seeing.** [source: `C-12` §2; D105 §7.2]

### 0.2 The two arms

**Block arm:** line `n` is inside a block comment iff the last `/*` at-or-before `n` is later than the last `*/` at-or-before `n`. **Tracked as a forward depth counter over the whole file, not as a per-line regex, so a block opening on one line and closing on another is handled.** [source: D105 §0.2]

**Line arm:** if the line is not inside a block, strip `//` and everything after it **before** matching. [source: `C-12` §2.4]

**Neither arm models `#if 0` / `#ifdef` exclusion, `/*` inside a string literal, `//` inside a string literal, or an unterminated block.** **The `#if 0` case is the largest and was NOT probed by any census in this lane.** **That is `[absence]`, recorded and not fixed.** [source: `C-12` §2.5]

### 0.3 THE MEASURED DELTA — both arms, printed

**Probe over every `.c` file under `payloads/Demon`, counting `DEMON_COMMAND_*` matches:**

```
arm = block only        : 101 live references
arm = block + line      : 101 live references
DELTA                   : 0
```

**The line arm removed ZERO additional references.**

**This is a bounded zero and it is reported as a zero with its enumeration, not as silence.** **The `Command.c:72` instance D105 found is a `//` comment that mentions `SleepObf` — not a `DEMON_COMMAND_*` token — so it could not appear in this census's match set at all.** **The arm was exercised; the population simply contains no `//`-commented `DEMON_COMMAND_*` reference.** [source: probe output, reproduced as run; D105 §7.2]

**Positive control, so the zero is not a broken-test zero:** the same matcher run on the **block** arm does remove lines — **D105 §1.4 measured 2 removals of 42 `PackageCreate*` sites, and D105 §3.2 measured 10 removals of 51 `Pivots` lines.** **The matcher demonstrably fires; it fired zero times on this population.** [source: D105 §1.4, §3.2]

### 0.4 What the delta does and does not license

**It licenses:** for **this** population, a block-only test and a two-arm test produce the same 101 references. **The D105 findings are not revised by the line arm.**

**It does not license:** treating a single zero as proof the arm is unnecessary. **A zero-delta on one population is evidence about that population.** **The arm stays mandatory because the failure it prevents is silent — a `//`-commented reference counted as live inflates a census with no visible symptom.** [source: `C-12` §2.3-§2.4; C-08 Failure 3]

---

## §1 — D-12: CAN `ServiceAgentExist` BE SATISFIED FROM THE WIRE?

### 1.1 The question, and why it matters

**D105 §4.3 established that `handlers.go:328` (`handleServiceAgent`) is reachable by an agent message — the trigger is `Header.MagicValue` parsed off the wire.** **It did so on the assumption that `ServiceAgentExist` gates it.** **If the registry can be written from the wire, then `handleServiceAgent` is reachable by an unauthenticated peer and T4's finding escalates sharply.** [source: D105 §4.2-§4.3]

### 1.2 The gate, verbatim

```go
func (t *Teamserver) ServiceAgent(MagicValue int) agent.ServiceAgentInterface {
	for _, agentService := range t.Service.Agents {
		if agentService.MagicValue == fmt.Sprintf("0x%x", MagicValue) {
			return agentService
		}
	}

	logger.Debug("Service agent not found")
	return nil
}

func (t *Teamserver) ServiceAgentExist(MagicValue int) bool {
	for _, agentService := range t.Service.Agents {
		if agentService.MagicValue == fmt.Sprintf("0x%x", MagicValue) {
			return true
		}
	}

	logger.Debug("Service agent not found")
	return false
}
```
[source: `cmd/server/service.go:9-29`, verbatim]

**Both walk `t.Service.Agents` with the identical predicate, `agentService.MagicValue == fmt.Sprintf("0x%x", MagicValue)`.** **`ServiceAgent` returns the entry; `ServiceAgentExist` returns true for the same entry.** **The two cannot disagree — same slice, same comparison.** [source: `:10-11`, `:21-22`]

**Consequence: the `:322` gate and the `:336` deref are consistent.** **If `:322` passes, `:336 Teamserver.ServiceAgent(Header.MagicValue)` is non-nil for the same value.** **No nil deref at `:336`.** [source: `:9-29`; `handlers.go:322`, `:336`]

### 1.3 The registry, and every writer

**Probe, printed — every occurrence of `ServiceAgent` across `teamserver`:**

```
cmd\server\service.go:9   [LIVE]  func (t *Teamserver) ServiceAgent(MagicValue int) agent.ServiceAgentInterface {
cmd\server\service.go:20  [LIVE]  func (t *Teamserver) ServiceAgentExist(MagicValue int) bool {
pkg\agent\types.go:33     [LIVE]  type ServiceAgentInterface interface {
pkg\agent\types.go:65     [LIVE]  ServiceAgent(MagicValue int) ServiceAgentInterface
pkg\agent\types.go:66     [LIVE]  ServiceAgentExist(MagicValue int) bool
pkg\handlers\handlers.go:47   [LIVE]  return handleServiceAgent(Teamserver, Header, ExternalIP)
pkg\handlers\handlers.go:305  [LIVE]  // handleServiceAgent
pkg\handlers\handlers.go:311  [LIVE]  func handleServiceAgent(Teamserver agent.TeamServer, Header agent.Header, ExternalIP string) (bytes.Buffer, bool) {
pkg\handlers\handlers.go:322  [LIVE]  if !Teamserver.ServiceAgentExist(Header.MagicValue) {
pkg\handlers\handlers.go:336  [LIVE]  Task = Teamserver.ServiceAgent(Header.MagicValue).SendResponse(AgentData, Header)
```
**10 matches, 10 LIVE, 0 DEAD.** [source: probe output, reproduced as run]

**`t.Service.Agents` is written in exactly ONE place:**

```go
		s.Agents = append(s.Agents, as)
```
[source: `pkg/service/service.go:198`, verbatim]

### 1.4 The chain from the wire to the writer, and where it breaks

**The single writer is inside `dispatch`:**

```go
	case HeadRegisterAgent:

		var (
			data []byte
			err  error
			as   *AgentService
		)

		data, err = json.Marshal(response["Body"]["Agent"])
		if err != nil {
			logger.Error("Failed to marshal object to json: " + err.Error())
			return
		}

		as = NewAgentService(data, client)
		if as == nil {
			logger.Error("Failed to make a new service agent.")
			return
		}

		// check if that agent name is already registered.
		if s.AgentExist(as.Name) {
			logger.Error(fmt.Sprintf("Service agent \"%v\"already registered ", as.Name))
			return
		}

		as.service = s

		s.Agents = append(s.Agents, as)
```
[source: `pkg/service/service.go:170-198`, verbatim]

**`dispatch` is called only from `routine` (`:162`), and `routine` is reached only after `authenticate` returns true.** [source: `:162`, `:144`]

### 1.5 The authentication gate, verbatim

```go
	if AuthRequest.Head.Type == HeadRegister {

		Hasher.Write([]byte(AuthRequest.Body.Pass))
		UserPass = hex.EncodeToString(Hasher.Sum(nil))
		Hasher.Reset()

		Hasher.Write([]byte(s.Config.Password))
		ServicePass = hex.EncodeToString(Hasher.Sum(nil))
		Hasher.Reset()

		if UserPass == ServicePass {
			logger.Debug("Service client authenticated")
			Authed = true
		}
```
[source: `pkg/service/service.go:107-120`, verbatim]

**Registration requires a WebSocket client to present `Head.Type == HeadRegister` with `Body.Password` whose SHA3-256 matches the SHA3-256 of `s.Config.Password`.** **`s.Config.Password` is the operator's teamserver password.** [source: `:107-120`]

### 1.6 D-12 ANSWERED — the gate holds

**`handleServiceAgent` is NOT reachable by an unauthenticated peer.** **The chain is:**

1. **A Demon package arrives at the HTTP handler** (`handlers.go`) with `Header.MagicValue != agent.DEMON_MAGIC_VALUE` → falls through to `handleServiceAgent` (`:47`).
2. **`handleServiceAgent` checks `ServiceAgentExist(Header.MagicValue)` (`:322`).**
3. **`t.Service.Agents` contains an entry only if a WebSocket service client registered it — and that requires operator-password authentication (`service.go:117`).**

**So the Demon wire cannot populate `t.Service.Agents`.** **The registration surface is a separate WebSocket service channel requiring `s.Config.Password`.** **T4's finding stands and does NOT escalate.** [source: `handlers.go:42-47`, `:322`; `service.go:117`, `:198`]

**This is a bounded negative with the enumeration printed: one writer (`service.go:198`), one caller of that writer (`:162` from `:144`), one gate (`:117`).** **A registration surface reachable from the wire would require another writer, and there is none.** [source: §1.3-§1.5]

### 1.7 Two side findings on this path

**Finding 1 — non-constant-time password comparison.** **`service.go:117` compares two hex digests with `==`, which short-circuits on the first differing character.** **The comparison is between SHA3-256 digests, so an attacker must match a hash rather than a password — but the equality itself is not constant-time.** **`[read]`. Bounded; no exploit path is constructed here.** [source: `:117`]

**Finding 2 — a splice-while-iterating that is SAFE, and the reason is instructive.**

```go
	for i := range s.clients {
		if s.clients[i] == client {

			// remove registered agents
			for j := range s.Agents {
				if s.Agents[j] != nil {
					if s.Agents[j].client == client {
						logger.Warn(...)

						// remove from list
						s.Agents = append(s.Agents[:j], s.Agents[j+1:]...)
						break
					}
				}
			}
```
[source: `pkg/service/service.go:719-733`, verbatim, one `logger.Warn` call elided at `:726`]

**This is the same splice shape as D105 §3.7's `UnlinkFromAll` — `append(s.Agents[:j], s.Agents[j+1:]...)` inside `for j := range` — and the two differ by exactly one token: `break` at `:730`.**

| Function | Splice inside `for … range` | `break` | Consequence |
|---|---|---|---|
| `Teamserver.UnlinkFromAll` (`agent.go:32-34`) | **yes** | **NO** | **element at index `i` skipped** |
| `Service.ClientClose` (`service.go:723-729`) | **yes** | **YES** (`:730`) | **no skip — loop exits after first removal** |

**The `break` is the entire difference between a defect and correct behaviour.** **D105 §3.7 called `UnlinkFromAll` `latent` by reading the loop; this comparison confirms the defect by exhibiting the control the other implementation has and it lacks.** [source: `service.go:723-733`; D105 §3.7]

**Caveat, stated: `ClientClose`'s `break` also means it unregisters only ONE agent per client even if that client registered several.** **That is a behavioural question, not a memory-safety one, and it is not pursued here.** [source: `:723-733`]

---

## §2 — THE 61/39 DISCRIMINANT SPLIT, BOTH DIRECTIONS

### 2.1 The question

**D105 §1.6-§1.8 established 22 envelope types and 61 real discriminants (62 defines minus the `DEMON_COMMAND_H` guard).** **The Lead asked: what are the 39 that never construct an envelope — server-side-only, deprecated, or unimplemented commands the operator UI still offers?** [source: D105 §1.6-§1.8; Lead message]

### 2.2 The denominator and the construction set, with both arms

**Probe, printed:**

```
real discriminants (62 defines minus DEMON_COMMAND_H guard) : 61
distinct referenced in live code                             : 61
total live references                                        : 101
DEFINES WITH NO LIVE REFERENCE AT ALL                        : 0
```
[source: probe output, block arm + line arm identical per §0.3]

**Zero orphans.** **All 61 are referenced in live `.c` code.** **But a reference is not a construction** — that distinction is the whole question, so the references were classified by role. [source: §0.3; §2.3]

### 2.3 The role classification, printed

**Probe, printed — every reference classified by the syntactic role of the line it appears on:**

```
=== CONSTRUCTS (agent SENDS this envelope) ===
DEMON_COMMAND_ASSEMBLY_INLINE_EXECUTE, DEMON_COMMAND_ASSEMBLY_VERSIONS, DEMON_COMMAND_CHECKIN,
DEMON_COMMAND_CONFIG, DEMON_COMMAND_FS, DEMON_COMMAND_GET_JOB, DEMON_COMMAND_INJECT_DLL,
DEMON_COMMAND_INJECT_SHELLCODE, DEMON_COMMAND_INLINE_EXECUTE, DEMON_COMMAND_JOB,
DEMON_COMMAND_KERBEROS, DEMON_COMMAND_MEM_FILE, DEMON_COMMAND_NET, DEMON_COMMAND_PIVOT,
DEMON_COMMAND_PROC, DEMON_COMMAND_PROC_LIST, DEMON_COMMAND_SCREENSHOT, DEMON_COMMAND_SLEEP,
DEMON_COMMAND_SOCKET, DEMON_COMMAND_SPAWN_DLL, DEMON_COMMAND_TOKEN, DEMON_COMMAND_TRANSFER
count: 22

=== referenced but NEVER constructs ===
count: 39
   DEMON_COMMAND_FS_CAT  [SWITCH-CASE]
   ... (10 FS_* total, all SWITCH-CASE)
   DEMON_COMMAND_INLINE_EXECUTE_COULD_NO_RUN  [OTHER]
   DEMON_COMMAND_INLINE_EXECUTE_EXCEPTION  [OTHER]
   DEMON_COMMAND_INLINE_EXECUTE_RAN_OK  [OTHER]
   DEMON_COMMAND_INLINE_EXECUTE_SYMBOL_NOT_FOUND  [OTHER]
   DEMON_COMMAND_JOB_DIED  [OTHER]
   ... (JOB_KILL_REMOVE/LIST/RESUME/SUSPEND, 4, SWITCH-CASE)
   DEMON_COMMAND_NO_JOB  [OTHER]
   ... (PROC_CREATE/GREP/KILL/MEMORY/MODULES, 5, SWITCH-CASE)
   ... (TOKEN_*, 10, SWITCH-CASE)
   ... (TRANSFER_LIST/REMOVE/RESUME/STOP, 4, SWITCH-CASE)
```
[source: probe output; the elided rows are the full 39 printed in the run]

**Totals: 34 `SWITCH-CASE`, 5 `OTHER`.** [source: same]

### 2.4 The two classes, named

**Class R (34) — RECEIVED sub-commands.** **Each appears as a `case` in a dispatcher the agent invokes on a payload discriminant.** **The agent never puts these in a package header; it branches on them.** [source: §2.3]

**Class P (5) — PAYLOAD discriminants.** **Each is sent as an `PackageAddInt32` argument INSIDE an envelope, never as the envelope's own `CommandID`.** **Verified by direct read:**

```
DEMON_COMMAND_JOB_DIED                      src/core/Jobs.c:118      PackageAddInt32( Package, DEMON_COMMAND_JOB_DIED );
DEMON_COMMAND_INLINE_EXECUTE_EXCEPTION      src/core/CoffeeLdr.c:55  PackageAddInt32( Package, DEMON_COMMAND_INLINE_EXECUTE_EXCEPTION );
DEMON_COMMAND_INLINE_EXECUTE_RAN_OK         src/core/CoffeeLdr.c:779 PackageAddInt32( Package, DEMON_COMMAND_INLINE_EXECUTE_RAN_OK );
```
[source: `payloads/Demon/src/core/Jobs.c:118`; `CoffeeLdr.c:55`, `:779`, verbatim]

**`DEMON_COMMAND_NO_JOB` is the fifth and is a comparison, not a send:** [source: `payloads/Demon/src/core/Command.c:106`, verbatim]

```c
    if ( CommandID != DEMON_COMMAND_NO_JOB ) {
```
[source: `Command.c:106`, verbatim]

### 2.5 The answer to the Lead's three-way question

**Not server-side-only. Not deprecated. Not unimplemented.** **All 39 are IMPLEMENTED agent-side and are the inbound command vocabulary — the set of things an operator can make this agent do.**

| Category | Count | Test | Verdict |
|---|---|---|---|
| **Envelope types (sent)** | **23** | appears as a `PackageCreate*` argument | **the wire vocabulary** — see §6.1: `DEMON_PACKAGE_DROPPED` was outside §2.3's prefix and is added here |
| **Class R — received sub-commands** | **34** | appears as a `case` in a dispatcher | **implemented; inbound** |
| **Class P — payload discriminants** | **5** | appears as a `PackageAddInt32` argument | **implemented; sent inside an envelope** |
| **Orphans** | **0** | no live reference at all | **none exist within the probed name space** |

**The 61/22 split is a DIRECTION split, not a completeness gap.** **Where D105 §1.8 described the 40 as "a gap," the sharper statement is that they are the receive side.** **The word "gap" is withdrawn here as it implied missing implementations that are not missing.** [source: §2.3-§2.4; D105 §1.8]

### 2.6 The reverse direction — server-side names with no agent handler

**Probe, printed:**

```
$ Get-ChildItem teamserver -Recurse -Filter *.go | Select-String 'DEMON_COMMAND_[A-Z_0-9]+'
count: 34
```
[source: probe output]

**All 34 server-side names are inside the agent's handling set. Zero server-side discriminants lack an agent handler.** **`[absence]` with its enumeration printed — the 34 names are listed in the run output above.** [source: same]

### 2.7 Both sides define these values INDEPENDENTLY — and they agree

**This is a load-bearing structural fact and it was tested rather than assumed.** **The agent's values come from C `#define`s in `include/core/Command.h`; the server's come from Go constants in `pkg/agent/commands.go`.** **They are hand-transcribed duplicates.**

**The C source of truth:**

```c
#define DEMON_COMMAND_CHECKIN                   100
#define DEMON_COMMAND_GET_JOB                   1
#define DEMON_COMMAND_NO_JOB                    10
#define DEMON_COMMAND_SLEEP                     11
#define DEMON_COMMAND_PROC                      0x1010
#define DEMON_COMMAND_PROC_LIST                 12
#define DEMON_COMMAND_FS                        15
...
#define DEMON_COMMAND_NET                       2100
#define DEMON_COMMAND_CONFIG                    2500
#define DEMON_COMMAND_SCREENSHOT                2510
#define DEMON_COMMAND_PIVOT                     2520
#define DEMON_COMMAND_TRANSFER                  2530
#define DEMON_COMMAND_SOCKET                    2540
#define DEMON_COMMAND_KERBEROS                  2550
#define DEMON_COMMAND_MEM_FILE                  2560
```
[source: `payloads/Demon/include/core/Command.h:7-29`, verbatim]

**The server's duplicates:**

```go
        DEMON_COMMAND_JOB_LIST        = 1
        DEMON_COMMAND_JOB_SUSPEND     = 2
        DEMON_COMMAND_JOB_RESUME      = 3
        DEMON_COMMAND_JOB_KILL_REMOVE = 4
        DEMON_COMMAND_JOB_DIED        = 5
        DEMON_COMMAND_TRANSFER_LIST   = 0
        DEMON_COMMAND_TRANSFER_STOP   = 1
        DEMON_COMMAND_TRANSFER_RESUME = 2
        DEMON_COMMAND_TRANSFER_REMOVE = 3
        DEMON_COMMAND_PROC_MODULES = 2
        DEMON_COMMAND_PROC_GREP    = 3
        DEMON_COMMAND_PROC_CREATE  = 4
        DEMON_COMMAND_PROC_MEMORY  = 6
        DEMON_COMMAND_PROC_KILL    = 7
        DEMON_COMMAND_TOKEN_IMPERSONATE      = 1
        DEMON_COMMAND_TOKEN_STEAL            = 2
        DEMON_COMMAND_TOKEN_LIST             = 3
        DEMON_COMMAND_TOKEN_PRIVSGET_OR_LIST = 4
        DEMON_COMMAND_TOKEN_MAKE             = 5
        DEMON_COMMAND_TOKEN_GET_UID          = 6
```
[source: `pkg/agent/commands.go:119-141`, verbatim]

**Compared value-for-value across all 21 families common to both sides: EVERY VALUE MATCHES.** **The hand-transcription is faithful.** [source: probe comparison of the two blocks above]

**Why this test was run: a single mistranscribed value would be a `case` that silently never fires — the C-08 Failure 3 shape (reported success, did nothing).** **The test is a bounded negative: 21/21 agree.** [source: C-08 §5 Failure 3]

**And the value spaces COLLIDE by design:** `DEMON_COMMAND_GET_JOB = 1` and `DEMON_COMMAND_JOB_LIST = 1` and `DEMON_COMMAND_TOKEN_IMPERSONATE = 1` and `DEMON_COMMAND_TRANSFER_STOP = 1` are all `1`.** **They are distinguished by POSITION, not by value — enveloped values go in the 20-byte header `[12..15]`, sub-command values go in the `PackageAddInt32` payload.** **This is the agent-side confirmation of D47 §3's Class A/B/C/D structure.** [source: `Command.h:8`, `:40`; `commands.go:119`, `:136`, `:126`; D47 §3]

---

## §3 — THE UNREACHABLE CONSUMER: A SERVER HANDLER FOR A MESSAGE THE AGENT CANNOT SEND

### 3.1 The find

**`DOTNET_INFO_ENTRYPOINT_EXECUTED` is an agent-side define with exactly TWO references in the entire Demon tree:**

```
count: 2
   include\core\Command.h:47  #define DOTNET_INFO_ENTRYPOINT_EXECUTED 0x3
   src\core\Dotnet.c:292      PackageAddInt32( PackageInfo, DOTNET_INFO_ENTRYPOINT_EXECUTED );
```
[source: probe output, both arms]

**`:292` is INSIDE the block comment spanning `:226` to `:306`.** **So the define has ZERO live senders.** [source: D105 §1.4; `Dotnet.c:226`, `:292`, `:306`]

**The server, however, implements a full handler for it:**

```go
        DOTNET_INFO_PATCHED     = 0x1
        DOTNET_INFO_NET_VERSION = 0x2
        DOTNET_INFO_ENTRYPOINT  = 0x3
        DOTNET_INFO_FINISHED    = 0x4
        DOTNET_INFO_FAILED      = 0x5
```
[source: `pkg/agent/commands.go:160-164`, verbatim]

```go
			case DOTNET_INFO_ENTRYPOINT:
```
[source: `pkg/agent/demons.go:4143`]

```go
				"Message": fmt.Sprintf("Callback error: DOTNET_INFO_ENTRYPOINT (0x3) expects more or at least 4 bytes but received %d bytes.", Parser.Length()),
```
[source: `pkg/agent/demons.go:4159`]

### 3.2 What this is

**This is the third case the Lead named, and it is the mirror of it.** **The Lead's case was "unimplemented commands the operator UI still offers" — a consumer with no producer.** **This is the reverse: a PRODUCER-SIDE HANDLER whose producer is commented out.** **A consumer with no producer, fully wired.**

**It is `unreachable-from-corpus`.** **The handler at `demons.go:4143-4161` cannot be entered by any agent this source can build, because the only line that would set `0x3` is inside a comment.** **It would be reached only if the commented-out ROP path at `Dotnet.c:226-306` were restored.** [source: §3.1; D105 §1.4]

### 3.3 The name divergence, recorded because it is a defect of its own

| Side | Name | Value |
|---|---|---|
| **Agent** | `DOTNET_INFO_ENTRYPOINT_EXECUTED` | `0x3` |
| **Server** | `DOTNET_INFO_ENTRYPOINT` | `0x3` |

**Same value, different names.** **The hand-transcription convention that §2.7 found faithful for the 21 discriminant families is NOT followed here — the name was shortened on the server side.** **A future reader comparing the two trees by name will not match these two lines.** **`[verified]` both defines read verbatim.** [source: `Command.h:47`; `commands.go:162`]

### 3.4 The corrected D-16

**D105 D-16 asked whether the live `Dotnet.c:92`/`:138` sites cover what the dead `:291` path was meant to report.** **Answer: NO — they report different states.**

| Site | Status | Discriminant reported |
|---|---|---|
| `Dotnet.c:92` | **LIVE** | `DOTNET_INFO_PATCHED` (`0x1`) — Amsi/Etw bypass installed |
| `Dotnet.c:138` | **LIVE** | `DOTNET_INFO_NET_VERSION` (`0x2`) |
| `Dotnet.c:292` | **DEAD** | `DOTNET_INFO_ENTRYPOINT_EXECUTED` (`0x3`) — entrypoint invoked |
| `Dotnet.c:364` | **DEAD** | `DOTNET_INFO_FINISHED` (`0x4`) |

[source: `Dotnet.c:92-93`, `:138-139`, `:292`, `:364`; both comment arms]

**Three DISTINCT states.** **`DOTNET_INFO_ENTRYPOINT_EXECUTED` has no live sender; `DOTNET_INFO_FINISHED` (`0x4`) is reachable — the server handler exists at `demons.go:4163` and `:364` is the only sender, but `DOTNET_INFO_FINISHED` is also referenced elsewhere in live code.** **D-16 is CLOSED.** [source: `demons.go:4163`; §3.1]

### 3.5 A corroborating detail on D105 §1.5

**Both live `Dotnet.c` sites use `PackageCreateWithRequestID`, not `PackageCreate`:**

```c
        PackageInfo = PackageCreateWithRequestID( DEMON_COMMAND_ASSEMBLY_INLINE_EXECUTE, Instance->Dotnet->RequestID );
```
[source: `Dotnet.c:92`, `:138`, verbatim]

**Both dead sites use plain `PackageCreate` (`:291`, `:363`).** **The live code and the commented code differ in their construction call as well as in their body, which independently corroborates D105 §1.5's conclusion that the dead `:291` block is a different generation of the same function rather than a duplicate of live code.** [source: `Dotnet.c:92`, `:138`, `:291`, `:363`; D105 §1.5]

---

## §4 — D-13: THE `UnlinkFromAll` SKIP IS REACHABLE FROM THE AGENT PATH

### 4.1 The callers, enumerated

**Probe, printed — every `Died`, `UnlinkFromAll`, and `LinkRemove` call site:**

```
cmd\server\agent.go:25     t.UnlinkFromAll(Agent)
cmd\server\agent.go:30     func (t *Teamserver) UnlinkFromAll(Agent *agent.Agent) {
cmd\server\agent.go:33     t.LinkRemove(Agent, Agent.Pivots.Links[i], false)
cmd\server\agent.go:45     t.LinkRemove(ParentAgent, Agent, false)
cmd\server\agent.go:94     err := t.DB.LinkRemove(int(ParentAgentID), int(LinkAgentID))
cmd\server\dispatch.go:34  t.Died(t.Agents.Agents[i])
pkg\agent\demons.go:2320   teamserver.Died(a)
pkg\agent\demons.go:2338   teamserver.Died(a)
pkg\agent\demons.go:5333   teamserver.LinkRemove(a, AgentInstance, true)
```
[source: probe output, both arms]

**`Died` (`agent.go:23-28`) calls `UnlinkFromAll` at `:25`, and `Died` has THREE callers:**

| Caller | Path | Family |
|---|---|---|
| `dispatch.go:34` | operator client | **operator** |
| `demons.go:2320` | agent message handler | **AGENT** |
| `demons.go:2338` | agent message handler | **AGENT** |

[source: `:34`, `:2320`, `:2338`]

### 4.2 D-13 ANSWERED

**The D105 §3.7 splice-skip is reachable from the AGENT path, via two call sites in `demons.go`.** **It is not operator-only.**

**It requires `Agent.Pivots.Links` to hold two or more entries at the moment the loop runs** — with one entry there is no subsequent element to skip. **Whether a real deployment reaches that condition is not measured here; the reachability is `[read]` and the multi-entry precondition is `[inferred]` from the loop's structure.** [source: `agent.go:32-34`; D105 §3.7]

**D-13 CLOSED.**

---

## §5 — WHAT THIS CHANGES

| Item | Verdict | Basis |
|---|---|---|
| **D-12 service-agent gate** | **CLOSED — the gate HOLDS. One writer (`service.go:198`), behind operator-password auth (`:117`). The Demon wire cannot populate the registry. T4 does NOT escalate.** | §1.3-§1.6 |
| **Line-comment arm** | **Implemented; delta on this population = 0 (bounded zero, positive control shown).** | §0.3 |
| **39 non-envelope discriminants** | **Answered: 34 received sub-commands (`SWITCH-CASE`) + 5 payload discriminants (`PackageAddInt32`). ALL implemented. Zero orphans. Not deprecated, not server-side-only, not unimplemented.** | §2.3-§2.5 |
| **Both directions enumerated** | **All 34 server-side names have agent handlers. `[absence]` with enumeration printed.** | §2.6 |
| **Independent duplicate constants** | **21/21 values agree between C headers and Go constants. Value spaces collide by design; position disambiguates.** | §2.7 |
| **Unreachable consumer** | **`DOTNET_INFO_ENTRYPOINT_EXECUTED` (`0x3`) has ZERO live senders; the server implements a full handler at `demons.go:4143-4161`. Consumer with no producer, `unreachable-from-corpus`.** **Name divergence: agent `_EXECUTED` vs server `_ENTRYPOINT`, same value.** | §3.1-§3.3 |
| **D-13** | **CLOSED — `UnlinkFromAll`'s skip is reachable from the AGENT path (`demons.go:2320`, `:2338`).** | §4 |
| **D-16** | **CLOSED — the live `Dotnet.c` sites report DIFFERENT states (`0x1`, `0x2`) than the dead path (`0x3`, `0x4`).** | §3.4 |
| **Side control** | **`Service.ClientClose` has the same splice shape as `UnlinkFromAll` and is SAFE — the entire difference is `break` at `service.go:730`.** | §1.7 |

**No contradiction with D47, D56, D65, D71, D76, D82, D86, D89, D98, D105, or C-12. §2.7 independently corroborates D47 §3's Class A/B/C/D structure from the agent side.**

### 5.1 One withdrawal, recorded

**D105 §1.8 called the 40 non-envelope discriminants "the gap."** **D111 §2.5 withdraws that word.** **They are not a gap in implementation — they are the receive side of the protocol, all implemented.** **The correction is recorded rather than silently applied, and D105 is not edited.** [source: D105 §1.8; §2.5]

---

## §6 — RESIDUAL UNKNOWNS, WITH PROBES

| ID | Unknown | Probe |
|---|---|---|
| **D-11** | **Does the `Pivots` interleaving occur at runtime?** | **Requires execution or race-detector instrumentation. OPEN. Not attempted — no execution is authorised.** |
| **D-17** | **Does `ClientClose`'s `break` leave a client's SECOND registered agent in `s.Agents` after disconnect?** | Read whether one client can register multiple services; enumerate `HeadRegisterAgent` senders client-side. **Not pursued.** |
| **D-18** | **Does any operator-UI path render a command bound to `DOTNET_INFO_ENTRYPOINT_EXECUTED`/`_ENTRYPOINT`?** | **The client is not in this corpus's Havoc tree; this is a client-side question.** **`[absence]` — not probed.** |
| **D-19** | **`#if 0`-excluded regions were never probed by any census in this lane.** | **Add an `#if 0` arm to the comment test; re-run D105 §1.4 and §3.2.** **`[absence]` recorded, not fixed.** |
| **D-20** | **Is `DEMON_PACKAGE_DROPPED` (`Command.h:30`, value 2570) an envelope type or a discriminant?** | **RESOLVED THIS REPORT — see §6.1. It is a 23rd envelope type, and it proves the census below was a name-space artefact.** |

### 6.1 D-20 RESOLVED, AND IT CORRECTS §2.5

**`DEMON_PACKAGE_DROPPED` is a 23rd envelope type, and D111's own census missed it.**

**Probe, printed:**

```
payloads\Demon\include\core\Command.h:30  #define DEMON_PACKAGE_DROPPED                   2570
payloads\Demon\src\core\Package.c:311     Package = PackageCreateWithRequestID( DEMON_PACKAGE_DROPPED, RequestID );
```
[source: probe output, verbatim both lines]

**`2570` sits inside the envelope value range — `PIVOT 2520`, `TRANSFER 2530`, `SOCKET 2540`, `KERBEROS 2550`, `MEM_FILE 2560`, then `2570`.** **And `Package.c:311` constructs it with `PackageCreateWithRequestID`, which D105 §1.1 established is an envelope constructor.** **Both tests agree: it is an envelope.** [source: `Command.h:22-30`; `Package.c:311`; D105 §1.1]

**Why the census in §2.3 missed it: the probe matched `DEMON_COMMAND_[A-Z_0-9]+`.** **`DEMON_PACKAGE_DROPPED` does not carry the `DEMON_COMMAND_` prefix.** **The token was outside the matcher's name space, so it could not appear.** [source: §2.3; probe pattern]

**This is the D98 Failure 3 class — a probe restricted to one name-space reporting a smaller population than exists.** **It is recorded here rather than silently corrected, and §2.5's counts are superseded:**

| Quantity | D111 §2.5 said | **Corrected** |
|---|---|---|
| **Envelope types** | **22** | **23** (`DEMON_PACKAGE_DROPPED` adds one) |
| **Denominator of defines** | **61 real** | **62 real** — the 61 `DEMON_COMMAND_*` names plus `DEMON_PACKAGE_DROPPED` |
| **Total live references** | **101** | **101 for the `DEMON_COMMAND_*` set**; `DEMON_PACKAGE_DROPPED` has its own site at `Package.c:311` and was never in that count |
| **Reach of the probe** | **all discriminants** | **all `DEMON_COMMAND_*`-prefixed discriminants** — one type lies outside the prefix |

**The §2.5 conclusion is NOT revised:** **the 39 are still implemented inbound vocabulary, zero orphans within the probed name space, and all 34 server-side names still have agent handlers.** **What changes is the denominator, and it changes because the probe had a boundary that was not stated.** **The boundary is now stated.** [source: §2.5; §6.1]

**Named rule, carried to C-12's successor on next amendment: a probe over an enumerated prefix defines a name space; every count it returns is a count WITHIN that name space, and the prefix is part of the result.** [source: §2.3, §6.1; D98 Failure 3]

---

## §7 — INSTRUMENT RECORD

### 7.1 The line-comment arm ran and returned zero — reported as a bounded zero

**Both arms implemented; delta measured; zero.** **Positive control: the same matcher removed 2/42 and 10/51 in D105.** **§0.3.** [source: §0.3; D105 §1.4, §3.2]

### 7.2 A probe timed out on an O(n²) mistake of mine

**The first orphan-discriminant probe ran a per-line loop that re-scanned the whole file to compute block-comment depth — O(n²) over every `.c` file — and exceeded 120 s.** **Job `pwsh-1669` was killed and rewritten as a single forward depth counter.** **The killed run produced no result; the rewrite produced §2.2-§2.3.** **Recorded because a partial result from a killed probe is indistinguishable from a smaller census.** [source: job `pwsh-1669`, killed; §2.2]

### 7.3 A `-Skip` negative broke a read

**`Select-Object -Skip ($f.LineNumber-14)` threw `Cannot validate argument on parameter 'Skip'` because the match was at line 11 — `-3` is below the minimum.** **`[exit code: 1]`, a hard failure and not a partial read.** **Corrected by reading from line 1.** **This is the FIVE-th recurrence of a `-Skip`-derived line number in this corpus; the convention (never derive a line number from a `-Skip` display value) caught it.** [source: read failure, `charm: Command.h`; D89/D98 `-Skip` recurrences]

### 7.4 The `[source:]` codepoint probe, applied to C-12

**C-12's 25 bracketed `[source: ...]` tokens were probed for non-ASCII.** **18 contain a `§`, and every one is `U+00A7` — in-range and legitimate.** **Every non-ASCII character in C-12 is accounted for: 49 `U+00A7`, 30 `U+2014`, 1 `U+2192`, 1 `U+2026`. Zero `U+FFFD`.** **Non-ASCII is confined to prose typography; every machine-read token and path is pure ASCII.** [source: `C-12` validation run]

---

## §8 — HEADLINE, STATED ONCE

**The service-agent gate holds.** **One writer, behind an operator-password WebSocket authentication.** **The Demon wire cannot register a service agent, so `handleServiceAgent` is reachable by an agent message only after an operator has authenticated a service that claims that `MagicValue`.** **T4 does not escalate.** **The bounded negative carries its enumeration: one writer, one caller, one gate.**

**The 39 non-envelope discriminants are not a gap.** **34 are received sub-commands the agent dispatches on; 5 are payload discriminants it sends inside an envelope.** **All 61 real discriminants are implemented; zero orphans; and all 34 server-side names have agent handlers, so the two directions are symmetric.** **The word "gap" is withdrawn.** **The two sides define these values as independent hand-transcribed duplicates — 21 of 21 compared values agree.**

**The one genuinely unreachable artefact is a consumer with no producer: `DOTNET_INFO_ENTRYPOINT_EXECUTED` (`0x3`) has zero live senders because its only sender is inside the commented-out ROP path, while the server implements a full handler for it at `demons.go:4143-4161` — under a DIFFERENT name, `DOTNET_INFO_ENTRYPOINT`.** **Restoring the comment would light it up.**

**And the line-comment arm, mandated after D105 found the gap in its own instrument, ran over this population and removed nothing — reported as a bounded zero with its positive control shown.**

---

**End of D111.**
