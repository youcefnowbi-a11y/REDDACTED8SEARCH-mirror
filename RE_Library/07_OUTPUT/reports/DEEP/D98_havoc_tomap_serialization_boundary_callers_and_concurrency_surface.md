# D98 — HAVOC Demon `ToMap`: THE SERIALIZATION BOUNDARY, ITS CALLERS, AND THE CONCURRENCY SURFACE

**Closes D89 D-1 and D-2; bounds D-3; bounds D86 C-1. Lane: source-layer load-bearing mechanisms.**
**Chosen mechanism, and why:** `ToMap` is the **serialization boundary** — the single function deciding which agent state crosses to the operator UI and to webhooks. It is load-bearing because **four separate consumers depend on it**, and because **D89 published a negative (the nil window is structural-only) whose premise was an unmeasured concurrency assumption.** A published negative resting on an unmeasured assumption is where the next defect lives. The other two candidate mechanisms open new surfaces; this one **closes an open premise on work already published.**

**Artifact:** `teamserver/` Go sources. **Method:** pure source read. No REA. No execution. No network. **No Ruby toolchain exists; nothing here is `[executed]`.**

**Line-count convention:** 1-based line numbers as printed by the read oracle, line 1 = first line of file. **No `-Skip` display value is ever used as a line number.**

**Tags:** `[verified]` read verbatim here; `[read]` read here without full quotation; `[inferred]` derived from reads, NOT measured; `[absence]` a negative with its enumeration printed beside it.

**Reporting vocabulary:** `latent` / `unreachable-from-corpus`. **Nothing here is called "live" or "fixed."** Goroutine interleaving is **not executable from a corpus-only method**, so every concurrency claim is `[inferred]` and labelled as such.

---

## §0 — SCOPE, AND WHAT THIS FILE INHERITS

### 0.1 The mechanism in one paragraph

**`ToMap` (`agent.go:1193-1222`) converts an `*Agent` into a `map[string]interface{}`.** To do so it **temporarily nulls `a.Pivots.Parent` (`:1201`), serializes with `structs.Map` (`:1203`), and restores the field (`:1216`) only if it was non-nil (`:1214`).** **The null-out exists so `.Parent` does not appear in the serialized map — the struct field and the `Parent` key are both deleted at `:1210`.**

**That save/clear/restore is a read-modify-write sequence on a field that no mutex protects.**

### 0.2 Inherited probes

| Probe | Source | Status after this report |
|---|---|---|
| **D-1** — Can `ToMap` run concurrently with a `.Parent` reader? | D89 §2.3, §6 | **BOUNDED — §3** |
| **D-2** — Who calls `ToMap`? | D89 §6 | **CLOSED — §2.8** |
| **D-3** — Is a nil `Pivots.Links` entry reachable at `demons.go:5233`? | D89 §3.3 | **BOUNDED, not closed — §4** |
| **D86 C-1** — Are the unguarded `.Parent` derefs at `agent.go:784-813` reachable? | D86 §4 | **CLOSED — §5** |

### 0.3 Method rules applied, and one that was applied too late in D86/D89

**Every census line in this report carries a comment-membership test.** **The test is stated at §2.2 and its result is printed beside the claim.** **D89 found `agent.go:580` was inside a comment block only after the census was published; this report builds the test into the enumeration rather than bolting it on.** [source: D89 §0.1]

---

## §1 — THE MECHANISM, READ CONTIGUOUSLY (Rule 21)

### 1.1 The function, verbatim

```go
// ToMap returns the agent info as a map
func (a *Agent) ToMap() map[string]interface{} {
	var (
		ParentAgent *Agent
		Info        map[string]any
		MagicValue  string
	)

	ParentAgent = a.Pivots.Parent
	a.Pivots.Parent = nil

	Info = structs.Map(a)

	Info["Info"].(map[string]interface{})["Listener"] = nil

	delete(Info, "Connection")
	delete(Info, "SessionDir")
	delete(Info, "JobQueue")
	delete(Info, "Parent")

	MagicValue = fmt.Sprintf("%08x", a.Info.MagicValue)

	if ParentAgent != nil {
		Info["PivotParent"] = ParentAgent.NameID
		a.Pivots.Parent = ParentAgent
	}

	Info["MagicValue"] = MagicValue

	return Info
}
```
[source: `pkg/agent/agent.go:1192-1222`, verbatim]

### 1.2 The read-modify-write, stated

1. **`:1200`** `ParentAgent = a.Pivots.Parent` — **READ**
2. **`:1201`** `a.Pivots.Parent = nil` — **WRITE**
3. **`:1203`** `Info = structs.Map(a)` — **serialize in the nulled state**
4. **`:1206`** `Info["Info"].(map...)["Listener"] = nil` — **type-asserted deref of a nested map**
5. **`:1214`** `if ParentAgent != nil` — **branch on the saved local**
6. **`:1216`** `a.Pivots.Parent = ParentAgent` — **WRITE (restore)**

**Between step 2 and step 6, `a.Pivots.Parent` is nil on the live object.** **Any concurrent reader of `.Parent` in that interval observes nil.** [source: `:1200-1216`]

### 1.3 The field's protection state

**The `Agent` struct's mutexes, verbatim:**

```go
	Info   *AgentInfo
	Pivots Pivots

	/* TODO: make a map called "Optional" where to put demon/3rd party
	 * 		 specific data (either use type "any" or map lets see).
	 * 		 to avoid having some unnecessary data for 3rd party agent */
	Downloads   []*Download
	PortFwds    []*PortFwd
	PortFwdsMtx sync.Mutex
	SocksCli    []*SocksClient
	SocksCliMtx sync.Mutex
	SocksSvr    []*SocksServer
	SocksSvrMtx sync.Mutex
```
[source: `pkg/agent/types.go:149-161`, verbatim]

**`Pivots` (`:150`) has no mutex.** **The three mutexes are adjacent and belong to `PortFwds` (`:157`), `SocksCli` (`:159`), `SocksSvr` (`:161`).** **`Downloads` (`:155`) is also unmutexed.** [source: `:149-161`]

**`[verified]`:** `Pivots` is unguarded. **The `TODO` at `:152-154` was placed directly above `Downloads`, so the author was aware of per-field grouping and still left `Pivots` unmutexed.** [source: `:150-161`]

---

## §2 — D-2: THE CALLER ENUMERATION

### 2.1 Probe, printed

```
$ Get-ChildItem havoc -Recurse -File -Filter *.go | Select-String 'ToMap'
teamserver\cmd\server\agent.go:111    t.WebHooks.NewAgent(Agent.ToMap())
teamserver\cmd\server\dispatch.go:286 a.SendTask(pk.Body.Info, t.Agents.Agents[i].ToMap())
teamserver\pkg\agent\agent.go:1192    // ToMap returns the agent info as a map
teamserver\pkg\agent\agent.go:1193    func (a *Agent) ToMap() map[string]interface{} {
teamserver\pkg\agent\agent.go:1227    jsonBytes, err := json.Marshal(a.ToMap())
teamserver\pkg\handlers\handlers.go:328  AgentData = Agent.ToMap()
teamserver\pkg\profile\yaotl\gohcl\decode.go:45   return decodeBodyToMap(body, ctx, val)
teamserver\pkg\profile\yaotl\gohcl\decode.go:234  func decodeBodyToMap(body hcl.Body, ctx *hcl.EvalContext, v reflect.Value) hcl.Diagnostics {
```
[source: `Get-ChildItem teamserver -Recurse -File -Filter *.go | Select-String 'ToMap'`]

### 2.2 Comment-membership test, printed beside the census

**Test applied:** for each candidate line `n`, record the last `/*` at or before `n` and the last `*/` at or before `n`; the line is inside a comment iff the last `/*` is later than the last `*/`.

```
cmd\server\agent.go:111        lastOpen= (none) lastClose= (none)  -> LIVE
cmd\server\dispatch.go:286     lastOpen= (none) lastClose= (none)  -> LIVE
pkg\agent\agent.go:1227        lastOpen=1180   lastClose=1180      -> LIVE
pkg\handlers\handlers.go:328   lastOpen=321    lastClose=321       -> LIVE
```

**All four call sites are LIVE code.** [source: probe above]

**This test is the mitigation D89 §7 mandated.** **D89's `agent.go:580` was a raw match inside `/*…*/` spanning `:538`-`:592`; the same class of probe here is comment-checked before counting, not after.** [source: D89 §0.1, §7]

### 2.3 The four callers, classified

| # | Site | Context | Arrival path |
|---|---|---|---|
| 1 | `cmd/server/agent.go:111` | `t.WebHooks.NewAgent(Agent.ToMap())` inside **`AgentAdd`** (`:108`) | **agent-facing** |
| 2 | `cmd/server/dispatch.go:286` | `a.SendTask(pk.Body.Info, t.Agents.Agents[i].ToMap())` | **operator task path** |
| 3 | `pkg/agent/agent.go:1227` | `json.Marshal(a.ToMap())` inside **`ToJson`** (`:1224`) | **either (see §2.5)** |
| 4 | `pkg/handlers/handlers.go:328` | `AgentData = Agent.ToMap()` | **agent-facing (HTTP check-in)** |

**The three `yaotl` hits at `decode.go:45`/`:234` are a DIFFERENT NAME SPACE** — `decodeBodyToMap`, an HCL/profile decoder, unrelated to `*Agent`. **Excluded. This is the "wrong name space zero" hazard in D47 §0.1 and D65 §2: a substring match over `ToMap` catches `decodeBodyToMap`.** [source: `decode.go:45`, `:234`; D47 §0.1]

### 2.4 D-2 CLOSED — headline

**`ToMap` has FOUR matched call sites; THREE are reachable.** **Site 3 (`:1227`) sits inside `ToJson`, which has zero callers (§2.5).** **The three live paths are the webhook path, the operator task path, and the agent HTTP check-in path.** [source: §2.1, §2.3, §2.5, §2.8]

### 2.5 `ToJson`, and its own census — MEASURED

**Probe, printed:**

```
$ Get-ChildItem teamserver -Recurse -File -Filter *.go | Select-String 'ToJson'
pkg\agent\agent.go:1224  func (a *Agent) ToJson() string {  -> LIVE
--- count: 1
```

**`ToJson` has EXACTLY ONE occurrence across the whole teamserver tree: its own definition at `:1224`.** **Zero call sites.** **`[absence]` — established by the enumeration printed above, comment-tested.**

### 2.6 `ToJson` body, verbatim

```go
func (a *Agent) ToJson() string {
	// TODO: add Agents pivot links too

	jsonBytes, err := json.Marshal(a.ToMap())
	if err != nil {
		logger.Error("Failed to marshal object to json: " + err.Error())
		return ""
	}
```
[source: `pkg/agent/agent.go:1224-1232`, verbatim]

**Two things follow.**

**First, `ToJson` is not a live consumer of `ToMap` — it is dead-weight.** **The fourth `ToMap` call site at `:1227` is unreachable-from-corpus because nothing calls `:1224`.** **D-2's live caller count is therefore THREE, not four.** [source: §2.5, `:1227`]

**Second, `:1225`'s `// TODO: add Agents pivot links too` is evidence of intent about the very field this report is about.** **The author knew `ToMap` was dropping pivot links and left the gap open.** **The `delete(Info, "Parent")` at `:1210` is the related, deliberate omission.** [source: `:1225`, `:1210`]

### 2.7 `AgentAdd` detail

**`cmd/server/agent.go:108-121`, verbatim:**

```go
func (t *Teamserver) AgentAdd(Agent *agent.Agent) []*agent.Agent {
	if Agent != nil {
		if t.WebHooks != nil {
			t.WebHooks.NewAgent(Agent.ToMap())
		}
	}

	err := t.DB.AgentAdd(Agent)
	if err != nil {
		logger.Error("Could not add agent to database: " + err.Error())
	}

	return t.Agents.AgentsAppend(Agent)
}
```
[source: `cmd/server/agent.go:108-121`, verbatim]

**`ToMap` at `:111` is guarded by `Agent != nil` at `:109` and gated on `t.WebHooks != nil` at `:110`.** **So site 1 is only reachable when an operator has configured a webhook.** **`[read]`** [source: `:109-111`]

### 2.8 D-2 CLOSED — final shape

| # | Site | Live? | Reachability |
|---|---|---|---|
| 1 | `cmd/server/agent.go:111` | **LIVE** | **Gated on `t.WebHooks != nil`** |
| 2 | `cmd/server/dispatch.go:286` | **LIVE** | Operator task path |
| 3 | `pkg/agent/agent.go:1227` | **LIVE line, DEAD function** | **Unreachable — `ToJson` has zero callers** |
| 4 | `pkg/handlers/handlers.go:328` | **LIVE** | Agent HTTP check-in path |

**Three reachable call sites, not four.** **D-2 CLOSED.** [source: §2.5-§2.8]

---

## §3 — D-1: THE CONCURRENCY SURFACE

### 3.1 The goroutine census, printed

```
$ Get-ChildItem teamserver -Recurse -File -Filter *.go | Select-String '^\s*go '
cmd\server\dispatch.go:839   go func() {
cmd\server\teamserver.go:107  go t.handleRequest(ClientID)
cmd\server\teamserver.go:126  go func(Host, Port string) {
pkg\agent\demons.go:1885     go func(SocketId int) {
pkg\agent\demons.go:1965     go func() {
pkg\agent\demons.go:5867     go func() {
pkg\handlers\http.go:224     go func() {
pkg\handlers\http.go:261     go func() {
pkg\logr\server.go:38        go func() {
pkg\service\service.go:45    go s.handleConnection(WebSocket)
pkg\socks\socks.go:57        go s.handler(s, con)
```
[source: `Get-ChildItem teamserver -Recurse -File -Filter *.go | Select-String '^\s*go '`]

### 3.2 The per-client goroutine, which is the operator path

```go
		t.Clients.Store(ClientID,
			&Client{
				Username:      "",
				GlobalIP:      WebSocket.RemoteAddr().String(),
				Connection:    WebSocket,
				ClientVersion: "",
				Packager:      packager.NewPackager(),
				Authenticated: false,
			})

		// Handle connections in a new goroutine.
		go t.handleRequest(ClientID)
	})
```
[source: `cmd/server/teamserver.go:96-108`, verbatim]

**Every WebSocket connection — i.e. every operator client — is handled in its own goroutine.** **`handleRequest` is the dispatch entry that reaches `dispatch.go:286`'s `ToMap`.** [source: `:107`; `dispatch.go:286`]

### 3.3 The agent-facing path reaches `ToMap` through `AgentAdd`

```
$ Select-String 'AgentAdd\('
cmd\server\agent.go:108     func (t *Teamserver) AgentAdd(Agent *agent.Agent) []*agent.Agent {
cmd\server\agent.go:115     err := t.DB.AgentAdd(Agent)
cmd\server\teamserver.go:464  t.AgentAdd(Agent)
pkg\agent\demons.go:5261    teamserver.AgentAdd(DemonInfo)
pkg\agent\types.go:48       AgentAdd(agent *Agent) []*Agent
pkg\db\agents.go:12         func (db *DB) AgentAdd(agent *agent.Agent) error {
pkg\handlers\handlers.go:281  Teamserver.AgentAdd(Agent)
pkg\service\service.go:334    s.Teamserver.AgentAdd(AgentInstance)
pkg\service\types.go:20       AgentAdd(agent *agent.Agent) []*Agent
```
[source: `Get-ChildItem teamserver -Recurse -File -Filter *.go | Select-String 'AgentAdd\('`]

**Three live callers reach the `ToMap` inside `AgentAdd`:**
- **`pkg/handlers/handlers.go:281`** — the agent HTTP check-in path
- **`pkg/service/service.go:334`** — the agent service (WebSocket) path, itself spawned per connection at `service.go:45`
- **`pkg/agent/demons.go:5261`** — the SMB pivot register path

**`[read]`** each of these three. [source: `handlers.go:281`; `service.go:334`; `demons.go:5261`]

### 3.4 The two goroutine families, and where they meet

**Family A — operator:** `teamserver.go:107 go t.handleRequest(ClientID)` → `dispatch.go:286` → `ToMap`.
**Family B — agent:** `service.go:45 go s.handleConnection(WebSocket)` → `service.go:334` → `AgentAdd` → `agent.go:111` → `ToMap`.

**Both families call `ToMap` on `*Agent` values drawn from the same `t.Agents.Agents` slice.** **`Pivots` has no mutex (§1.3).** [source: §1.3, §3.2, §3.3]

### 3.5 D-1 BOUNDED — and the bound is stated as a bound, not a measurement

**`[inferred]` — NOT measured.** **Two goroutine families both invoke `ToMap`.** **`ToMap` performs a read-modify-write on `a.Pivots.Parent` with no lock.** **Therefore a nil window exists that a concurrent reader could in principle observe.**

**What this does and does not establish:**

- **Does establish:** the field is unguarded (§1.3, `[verified]`), `ToMap` mutates it (§1.2, `[verified]`), and more than one goroutine family calls `ToMap` (§3.2-3.4, `[read]`).
- **Does NOT establish:** that any two such calls actually interleave, or that they address the **same** `*Agent` at the same moment. **Establishing interleaving requires execution, which this corpus-only method cannot provide.**
- **Does NOT establish:** whether Go's runtime or a higher-level serialization already prevents it. **No such mechanism was read.**

**So D-1's status is: the window is `latent` — reachable in principle, not observed.** **D89's "structural-only" verdict is amended to: structural-only *within a single goroutine*; the cross-goroutine case is `latent` and unmeasured.** [source: D89 §2.3; §1.2, §1.3, §3.2-3.4]

**This is the discipline D86 established: a negative must state what it does not cover rather than let it read as a confirmation.** [source: D86 §5]

---

## §4 — D-3 BOUNDED

### 4.1 The nil-link path

**`teamserver.go:475-476` appends `t.AgentInstance(AgentID)` with no nil check** (D89 §3.3). **`demons.go:5233` dereferences `Links[i].NameID`, guarded by `:5231`'s check on `.Parent` only — never on the individual link.** [source: D89 §3.3; `demons.go:5231-5234`]

### 4.2 What this report adds

**The reachability requires three conjuncts (D89 §3.3), and the report can now bound the third:** **a nil link must be stored, then a `DEMON_PIVOT_SMB_CONNECT` must arrive for a child whose `.Parent` is that agent, and the loop must reach the nil index.**

**Whether `AgentInstance` can return nil while `LinksOf` returned that ID for the same agent is a DB-consistency question.** **Not enumerated here. `D-3` remains open — bounded, not closed.** [source: D89 §3.3]

---

## §5 — D86 C-1 CLOSED: THE SINGLE CALLER GUARDS THE DEREF

### 5.1 The derefs

**`agent.go:784`, `:789`, `:792`, `:810`, `:813` dereference `pivots.Parent` with no nil check, inside `PivotAddJob`'s loop.** [source: D86 §4; `agent.go:780-813`]

### 5.2 The caller census — MEASURED

```
$ Get-ChildItem teamserver -Recurse -File -Filter *.go | Select-String 'PivotAddJob'
pkg\agent\agent.go:653  a.PivotAddJob(job)  -> LIVE
pkg\agent\agent.go:746  func (a *Agent) PivotAddJob(job Job) {  -> LIVE
--- count: 2
```

**`PivotAddJob` has exactly ONE caller: `:653`.** **And `:653` is guarded.** [source: probe above]

### 5.3 The guard, verbatim

```go
func (a *Agent) AddJobToQueue(job Job) []Job {
	// store the RequestID									
	a.AddRequest(job)
	// if it's a pivot agent then add the job to the parent
	if a.Pivots.Parent != nil {
		//logger.Debug("Prepare command for pivot demon: " + a.NameID)
		a.PivotAddJob(job)
		// if it's a direct agent add the job to the direct agent
	} else {
		a.JobQueue = append(a.JobQueue, job)
	}
	return a.JobQueue
}
```
[source: `pkg/agent/agent.go:647-659`, verbatim]

**`:651 if a.Pivots.Parent != nil` wraps the only call at `:653`.** **`PivotAddJob` cannot be entered with nil `.Parent` from any caller in this corpus.** [source: `:651-653`]

### 5.4 C-1 CLOSED — with the precise reason

**D86 C-1 asked whether the unguarded derefs at `:784-813` are reachable with `.Parent == nil`.** **They are not, and the reason is NOT that the derefs are safe — it is that the sole entry point is guarded.** **The unguarded derefs remain latent-but-unreachable: a defect class that is currently dead by call-path, not by construction.** [source: §5.2, §5.3; D86 §4]

**Stated precisely, because this is exactly the distinction D86's Failure 4 required: the derefs are unguarded; their reachability is closed by a guard one frame up. Modify `:651` and the chain re-opens.** [source: D86 §5 Failure 4]

### 5.5 A second guard on the same field, adjacent

**`AddJobToQueue` (`:647`) and `RequestCompleted` (`:638`) are adjacent functions operating on `a.Tasks` and `a.JobQueue` with no lock** — the same unmutexed-state pattern as §1.3, on different fields. **`[read]`, not developed here.** [source: `:638-659`]

---

## §5A — THE `:1225` TODO AND WHAT IT REVEALS ABOUT THE DESIGN

**`ToJson`'s `// TODO: add Agents pivot links too` (`:1225`) sits in a function nothing calls.** **Combined with `delete(Info, "Parent")` (`:1210`) and the null-out at `:1201`, the pattern is consistent: pivot relationship data is deliberately excluded from serialization, with one abandoned wrapper that intended to include it.** [source: `:1210`, `:1201`, `:1225`]

**This is the mechanism-level finding: `ToMap` intentionally drops the parent field, which is WHY the save/clear/restore at `:1200-1216` exists.** **The read-modify-write is not incidental — it is the implementation of a deliberate omission.** [source: §1.2, `:1210`]

---

## §6 — RESIDUAL UNKNOWNS, WITH PROBES

| ID | Unknown | Probe |
|---|---|---|
| **D-7** | **Does any `*Agent` reach `ToMap` from two goroutines at once?** §3.5. | Runtime instrumentation is required. **Out of a source-only method's reach; stated as the reason D-1 stays `latent`.** |
| **D-9** | **Does `structs.Map` itself take a lock or walk `Pivots`?** §1.2 step 3. | Read the `structs` package's `Map` implementation. **Not read in this report.** |
| **D-10** | **Is `Pivots.Parent` written by any path that holds a lock the readers also take?** §1.3. | Enumerate lock acquisition in `demons.go:5242`/`:5254` and `teamserver.go:471`. **D89 established no lock exists near those sites; not re-verified here.** |

**Closed by this report:** **D-6** (single caller, guarded — §5.4) and **D-8** (`ToJson` has zero callers — §2.5). [source: §2.5, §5.2]

---

## §7 — INSTRUMENT RECORD

**Failure 1 — a declared census with no reproduced invocation, caught in draft and FIXED rather than shipped.** **The first draft of §2.5-§2.8 asserted a `ToJson` caller census whose probe output was not printed.** **Rather than leave it as a labelled defect, the probe was run and the result folded in: `ToJson` has exactly one occurrence — its own definition — and ZERO callers.** **The Rule 20 defect class was present, named, and then removed by measurement.** [source: §2.5; §2.2]

**Failure 2 — D89's `agent.go:580` failure mode was a raw match inside a comment, and this report's §2.2 builds the comment-membership test into the enumeration.** **Recorded because the mitigation is being demonstrated, not merely cited.** [source: D89 §0.1; §2.2]

**Failure 3 — the `ToMap` substring probe catches `decodeBodyToMap` in a different package.** **Three of eight hits were a name-space artefact.** **Same class as D47 §0.1's `DEMON_COMMAND_H` 62nd-define artefact and D65 §2's missed `handlers.go:193`.** [source: §2.1, §2.3; D47 §0.1]

**Failure 4 — every concurrency statement in §3 is `[inferred]`, and the report says so at each point rather than once.** **Goroutine interleaving is not measurable from source.** **A report that asserts a race from a goroutine list has manufactured a defect; this one asserts a `latent` window and names the missing measurement.** [source: §3.5]

**Net: four failures. Failure 1 is a live instrument defect in this report; Failures 2-4 are methodological and labelled.**

---

## §8 — WHAT THIS CHANGES

| Item | Verdict | Basis |
|---|---|---|
| **D89 D-1** | **AMENDED, not closed.** D89's "structural-only" holds **within a single goroutine**. Cross-goroutine, the window is **`latent`** — two goroutine families call `ToMap`, `Pivots` has no mutex. **Interleaving is unmeasured.** | §3.5 |
| **D89 D-2** | **CLOSED.** Four matched call sites; **three reachable**, one (`:1227`) inside a zero-caller function. All comment-tested LIVE. | §2.5, §2.8 |
| **D89 D-3** | **Bounded, still open.** Requires a DB-consistency question not enumerated here. | §4 |
| **D86 C-1** | **CLOSED.** `PivotAddJob` has ONE caller (`:653`), guarded by `:651 if a.Pivots.Parent != nil`. **The unguarded derefs are unreachable-by-call-path — dead by guard, not by construction.** | §5.2-§5.4 |
| **Mechanism verdict** | **`ToMap` is load-bearing: three reachable consumers, and it mutates shared state without a lock.** **The defect class is a data race on `Pivots.Parent` — `latent`, not observed.** **The read-modify-write is the implementation of a DELIBERATE omission (`delete(Info,"Parent")` at `:1210`), not incidental.** | §1, §5A |

**No contradiction with D47, D56, D65, D71, D76, D86, or D89. One amendment to D89 D-1, reported here as required.**

---

**End of D98.**
