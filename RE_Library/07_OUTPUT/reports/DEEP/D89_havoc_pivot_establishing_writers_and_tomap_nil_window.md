# D89 — HAVOC PIVOT ESTABLISHING WRITERS AND THE `ToMap` NIL WINDOW

**Converts D86 C-2 and C-4 into verdicts; bounds `teamserver.go:471`.**
**Artifact:** `teamserver/` Go sources. **Method:** pure source read. No REA. No execution. No network.
**Write scope:** this file only. **D1–D88 are protected and untouched. Corrections to D76 and D86 are made here.**

**Line-count convention:** every line number is the 1-based line number printed by the read oracle, where line 1 is the file's first line. **No `-Skip` display value is ever used as a line number.**

**Tags:** `[verified]` read verbatim in this report; `[read]` read in this report without full verbatim quotation; `[inferred]` derived from reads; `[absence]` a negative established by an enumeration printed beside it.

---

## §0 — HEADLINE, AND A CORRECTION TO MY OWN D86

### 0.1 CORRECTION: `agent.go:580` IS DEAD CODE. D86's census contained a raw-text match inside a comment block.

**D86 §3.1 listed `agent.go:580 PivotSession.Pivots.Parent = Session` as one of the "THREE ESTABLISHING WRITERS D76 missed."** **It is inside a comment.**

**Probe, printed:**

```
$L = Get-Content agent.go ; range 500..600 ; record lines matching /\* and \*/
/* opens at: 538
*/ closes at: 592
```

**The block is `/*for {` at `:538` … `}*/` at `:592`.** **`:580` sits inside it.** **Probe, printed — same test applied to all six D86 sites:**

```
agent.go:1201               lastOpen=1180 lastClose=1180  -> LIVE CODE
agent.go:1216               lastOpen=1180 lastClose=1180  -> LIVE CODE
demons.go:5242              lastOpen=3853 lastClose=3875  -> LIVE CODE
demons.go:5254              lastOpen=3853 lastClose=3875  -> LIVE CODE
teamserver.go:471           lastOpen=398  lastClose=398   -> LIVE CODE
agent.go:580                last /*=538, first */ after=592  -> :580 IS INSIDE a comment spanning 538..592
```

**Corrected D86 census: five live assignment sites, not six. `:580` is struck.** [source: probes above; `agent.go:538`, `:592`]

### 0.2 The three "missed establishing writers" were TWO, and both are now bounded

**D86 said `:580`, `:5254`, `:471`.** **`:580` is dead.** **The live pair is `demons.go:5254` and `teamserver.go:471`.** **Both are answered below.** [source: §0.1; §1.2; §3]

### 0.3 T3 is the live defect-shaped finding: `teamserver.go:471` stores a nil with no guard

**Branch named: the `if err == nil` at `teamserver.go:470` guards the ERROR, not the RESULT.** **`AgentInstance(parentID)` returning nil is assigned unchecked.** **The same function has the identical shape on `Links` at `:475-476`.** **The runtime paths guard; the startup rehydration path does not.** [source: §3.1]

### 0.4 T1's verdict is not uniform — the invariant is maintained by one writer and not the other

**The `:5233` invariant is a SYMMETRY, not a nil check.** **§1.1 reads what it actually requires.** **`:5254` dereferences `DemonInfo.Pivots` before its own nil guard at `:5265`.** **Stated without inflation: `:5254`'s exposure is a nil-deref on a parse failure, not a data-integrity break.** [source: §1.1, §1.3]

### 0.5 T2's window is STRUCTURAL-ONLY, and the enumeration shows why

**Read-site enumeration printed at §2.1.** **No `.Parent` reader is reachable inside `:1201-:1216`.** **The window cannot be observed because the only code that runs inside it is `structs.Map` at `:1203`, and no `.Parent` reader is on that path.** [source: §2.2]

### 0.6 Carry-forward discipline

**A-4a stays retired as measured. It is NOT re-opened.** **Where a result is a negative, §5 states what the negative does NOT cover rather than letting it read as a confirmation.** [source: D86 §1.3; §5]

---

## §1 — T1: THE `:5233` INVARIANT, AND EACH ESTABLISHING WRITER

### 1.1 What `:5233` literally requires

```go
									if DemonInfo.Pivots.Parent != nil {
										for i := range DemonInfo.Pivots.Parent.Pivots.Links {
											if DemonInfo.Pivots.Parent.Pivots.Links[i].NameID == fmt.Sprintf("%08x", AgentHdr.AgentID) {
												DemonInfo.Pivots.Parent.Pivots.Links = append(DemonInfo.Pivots.Parent.Pivots.Links[:i], DemonInfo.Pivots.Parent.Pivots.Links[i+1:]...)
												break
											}
										}
									}
```
[source: `pkg/agent/demons.go:5231-5238`, verbatim]

**`:5233` is NOT a parent-binding test.** **It is a LINK-LIST CLEANUP.** **It iterates the PARENT's `Pivots.Links` looking for an entry whose `NameID` equals the CHILD's ID (`AgentHdr.AgentID`), and removes it (the `:5234` splice).** **The commented-out intent is legible at `:5232`'s context: a reconnecting child must not appear twice in its parent's link list.** [source: `:5231-5238`]

**What it requires to be meaningful:**

1. `DemonInfo.Pivots.Parent != nil` — **guarded explicitly at `:5231`.** `[verified]`
2. `Parent.Pivots.Links` contains an entry whose `NameID == fmt.Sprintf("%08x", AgentHdr.AgentID)` — **i.e. the CHILD's ID appears among the PARENT's links.**
3. That the iteration and splice operate on a live slice.

**And `:5242`-`:5244` then establishes the symmetry:**

```go
										DemonInfo.Pivots.Parent = a

										a.Pivots.Links = append(a.Pivots.Links, DemonInfo)
```
[source: `demons.go:5242-5244`, verbatim]

**The invariant, stated as it is actually enforced: `child.Pivots.Parent == a` AND `a.Pivots.Links ∋ child`. The connect path maintains BOTH halves adjacently.** [source: `:5242`, `:5244`]

### 1.2 Writer `demons.go:5254` — the register path

```go
									} else {
										// if the agent doesn't exist then we assume that it's a register request from a new agent

										DemonInfo = ParseDemonRegisterRequest(AgentHdr.AgentID, AgentHdr.Data, "")
										DemonInfo.Pivots.Parent = a

										a.Pivots.Links = append(a.Pivots.Links, DemonInfo)
										teamserver.LinkAdd(a, DemonInfo)

										DemonInfo.Info.MagicValue = AgentHdr.MagicValue

										teamserver.AgentAdd(DemonInfo)
										teamserver.AgentSendNotify(DemonInfo)
									}
```
[source: `demons.go:5250-5263`, verbatim]

**Symmetry verdict: MAINTAINED.** `:5254` sets `.Parent = a` and `:5256` appends to `a.Pivots.Links`. **Both halves, adjacent.** [source: `:5254`, `:5256`]

**But there is a real defect in the ordering, and it is a nil-deref, not an integrity break.**

**`ParseDemonRegisterRequest` returns `*Agent` and can return nil. Its return paths, enumerated from the definition at `agent.go:328` to its close at `:606`:**

```
agent.go:409   return nil      (AgentID != DemonID — decryption failed)
agent.go:596   return Session  (success)
agent.go:599   return nil      (CanIRead set failed — "Invalid packet")
agent.go:604   return nil      (Parser.Length() < 48 — "Invalid packet")
```
[source: `agent.go:328`, `:380`, `:402`, `:409`, `:596`, `:599`, `:604`, `:606`; all four returns read]

**`:5254` dereferences `DemonInfo.Pivots` with no nil check.** **The check on `DemonInfo` occurs at `:5265`, eleven lines later:**

```go
									if DemonInfo != nil {
										Message["Type"] = "Good"
										Message["Message"] = "[SMB] Connected to pivot agent [" + a.NameID + "]-<>-<>-[" + DemonInfo.NameID + "]"
									} else {
										Message["Type"] = "Error"
										Message["Message"] = "[SMB] Failed to connect: failed to parse the agent"
									}
```
[source: `demons.go:5265-5271`, verbatim]

**So the author wrote a nil guard and placed it AFTER three dereferences of the same pointer (`:5254` `.Pivots`, `:5256` `append(..., DemonInfo)`, `:5261` `AgentAdd(DemonInfo)`).** **If `ParseDemonRegisterRequest` returns nil at `:5253`, `:5254` panics before `:5265` can report it.** [source: `:5253-5254`, `:5265`]

**Contrast, same function, same author: `handlers.go:273-274` does it correctly:**

```go
	if Agent = agent.ParseDemonRegisterRequest(Header.AgentID, Header.Data, ExternalIP); Agent == nil {
		return Response, false
	}
```
[source: `pkg/handlers/handlers.go:273-274`, verbatim]

**Nil is checked on the RETURN of the same call in one place and after three derefs in another.** [source: `:273-274` vs `demons.go:5254`/`:5265`]

### 1.3 Writer `teamserver.go:471` — DB rehydration. See §3.

**Symmetry verdict: UNKNOWN, and the failure mode is the subject of T3.** [source: §3]

### 1.4 Writer `agent.go:580` — STRUCK, dead code

**Inside the comment block `538..592`.** **Does not execute.** **The recursive `PivotSession` registration path it belongs to (`:568` call included) is entirely commented out.** [source: §0.1]

### 1.5 T1 verdict table

| Writer | Line | Symmetry maintained? | Nil-guard quality |
|---|---|---|---|
| connect path | `demons.go:5242` + `:5244` | **Yes** | Guarded (`:5231`) |
| register path | `demons.go:5254` + `:5256` | **Yes** | **NO — guard at `:5265` is after three derefs** |
| DB rehydration | `teamserver.go:471` | **Unknown** | **NO — see §3** |
| SMB registration | `agent.go:580` | **N/A — DEAD CODE** | N/A |

**C-2 converts to a verdict: the symmetry is maintained by both live establishing writers; the defect D86's census pointed at is not an integrity break but a nil-deref ordering error at `demons.go:5254`.** [source: §1.2, §1.4]

---

## §2 — T2: THE `ToMap` NIL WINDOW — READ-SITE ENUMERATION

### 2.1 The window, verbatim

```go
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
```
[source: `pkg/agent/agent.go:1200-1217`, verbatim]

**The window is `:1201` (`= nil`) to `:1216` (`= ParentAgent`).** **Note `:1216` is inside `if ParentAgent != nil` (`:1214`) — so if the saved value was nil, the restore is skipped and `.Parent` stays nil, which is a no-op preserving the prior state.** [source: `:1200`, `:1201`, `:1214`, `:1216`]

### 2.2 Every `.Parent` READ site, enumerated (Rule 20)

**Probe invocation:** `Get-ChildItem teamserver -Recurse -File -Filter *.go | Select-String '\.Parent'`

**Every `Pivots.Parent` READ (excluding the six assignments from D86, and the assignment at `:471` found by D86):**

```
agent.go:651       if a.Pivots.Parent != nil {
agent.go:784       if pivots.Parent.Pivots.Parent == nil {
agent.go:789       pivots.Parent.Encryption.AESKey, pivots.Parent.Encryption.AESIv
agent.go:792       strconv.ParseInt(pivots.Parent.NameID, 16, 32)
agent.go:810       pivots = &pivots.Parent.Pivots
agent.go:813       pivots.Parent.JobQueue = append(pivots.Parent.JobQueue, PivotJob)
agent.go:1200      ParentAgent = a.Pivots.Parent
agent.go:1214      if ParentAgent != nil {
agent.go:1215      Info["PivotParent"] = ParentAgent.NameID
demons.go:5231     if DemonInfo.Pivots.Parent != nil {
demons.go:5232     DemonInfo.Pivots.Parent.Pivots.Links
demons.go:5233     DemonInfo.Pivots.Parent.Pivots.Links[i].NameID == ...
demons.go:5234     DemonInfo.Pivots.Parent.Pivots.Links = append(...)
events/demons.go:74    if Agent.Pivots.Parent != nil {
events/demons.go:75    InfoMap["PivotParent"] = Agent.Pivots.Parent.NameID
dispatch.go:201    if t.Agents.Agents[i].Pivots.Parent != nil {
```
[source: `Get-ChildItem teamserver -Recurse -File -Filter *.go | Select-String '\.Parent'`]

**Reads inside the `:1201-:1216` range: `agent.go:1214`, `:1215`.** **Both read the LOCAL `ParentAgent`, not `a.Pivots.Parent`.** **`:1214` `if ParentAgent != nil` and `:1215` `ParentAgent.NameID`.** **Neither dereferences the field that `:1201` nulled.** [source: `:1214`, `:1215`]

**Reads outside the range that dereference `a.Pivots.Parent`: `:651`, `:784`, `:789`, `:792`, `:810`, `:813`, `:1200`, `demons.go:5231-5234`, `events/demons.go:74-75`, `dispatch.go:201`.** **None of these is inside the window.** [source: §2.2 enumeration]

### 2.3 Verdict — STRUCTURAL-ONLY

**No `.Parent` reader is reachable inside `:1201-:1216`.**

**The code that runs inside the window is `:1203 structs.Map(a)` and the four `delete` calls at `:1207-:1210`.** **`structs.Map` reflects over the struct and is the reason the field is nulled in the first place — the author is preventing `.Parent` from appearing in the serialized map.** **`:1214-1216` then restores it and adds `PivotParent` as a string.** [source: `:1200-1216`]

**So the window is: (a) not observed by any `.Parent` reader in this source, and (b) the value is restored before the function returns unless it was already nil.**

**T2 verdict: STRUCTURAL-ONLY, not live.** **The window exists in the source; no reader in this artifact is positioned to observe it.** [source: §2.2, §2.3]

**What this does NOT cover — stated so the negative does not read as a confirmation:**

- **Concurrency is not assessed.** **`ToMap` is a method on `*Agent` with no visible lock in `:1193-1222`.** **If a caller invokes `ToMap` while another goroutine runs a `.Parent` reader, the window is observable regardless of this enumeration.** **This is residual D-1, and it is the difference between "no reader is inside the range" and "no reader can ever be inside the range."** [source: `:1193-1222`; no mutex read]
- **`ToMap`'s callers are not enumerated in this report.** **Residual D-2.** [source: `:1193`]

---

## §3 — T3: `teamserver.go:471` AND WHAT HAPPENS ON NIL

### 3.1 The function, verbatim

```go
	// load all existing Agents from the DB
	Agents := t.DB.AgentAll()
	for _, Agent := range Agents {
		t.AgentAdd(Agent)
	}

	for _, Agent := range Agents {
		// check if the agent has a parent
		parentID, err := t.ParentOf(Agent)
		if err == nil {
			Agent.Pivots.Parent = t.AgentInstance(parentID)
		}
		// check if the agent has any links
		AgentsIDs := t.LinksOf(Agent)
		for _, AgentID := range AgentsIDs {
			Agent.Pivots.Links = append(Agent.Pivots.Links, t.AgentInstance(AgentID))
		}
	}
```
[source: `cmd/server/teamserver.go:461-478`, verbatim]

### 3.2 The branch, named

**Branch: `teamserver.go:471` inside `if err == nil` at `:470`.**

**`ParentOf(Agent)` returns `(parentID, err)`.** **`:470` tests the ERROR.** **`:471` assigns the RESULT of `AgentInstance(parentID)` with NO check.**

**`AgentInstance` returns nil on a miss.** **The definition, read verbatim:**

```go
func (t *Teamserver) AgentInstance(AgentID int) *Agent {
	for _, demon := range t.Agents.Agents {
		NameID, err := strconv.ParseInt(demon.NameID, 16, 64)
		if err != nil {
			logger.Debug("Failed to convert NameID string to AgentID: " + err.Error())
			return nil
		}
		if AgentID == int(NameID) {
			return demon
		}
	}
	return nil
}
```
[source: `cmd/server/agent.go:155-164`]

**So `:471` STORES THE NIL AND CONTINUES.** **There is no guard, no log, no early return.** **The loop proceeds to `:474-477` with `Agent.Pivots.Parent == nil`.** [source: `:471`, `:473-477`]

### 3.3 The same shape on `Links`, one object later

**`:475-476`: `AgentID` comes from `t.LinksOf(Agent)`, and `t.AgentInstance(AgentID)` is appended with no nil check.**

**So a nil LINK can also be stored.** **A `nil` entry in `Pivots.Links` would be dereferenced by `demons.go:5233`'s `Links[i].NameID` — which is guarded only by `:5231`'s check on `.Parent`, NOT on the individual link.** [source: `:475-476`; `demons.go:5231-5234`]

**Reachability of that specific deref: it requires (a) a nil link stored at startup, (b) a subsequent `DEMON_PIVOT_SMB_CONNECT` for a child whose `.Parent` is the agent holding the nil link, and (c) the loop reaching that index.** **Stated as a HYPOTHESIS, not asserted — residual D-3.** [source: `:471-476`, `demons.go:5231-5234`]

### 3.4 T3 verdict

**`:471` STORES THE NIL AND RETURNS.** **The failure mode is now bounded:**

| Condition | Behaviour |
|---|---|
| `ParentOf` errors | `.Parent` untouched (`:470` skips) |
| `ParentOf` succeeds, `AgentInstance` finds the parent | `.Parent` set correctly |
| **`ParentOf` succeeds, `AgentInstance` returns nil** | **`.Parent` = nil, stored, no guard, loop continues** |

**The asymmetry to record: `:5231`, `:569` (dead), and `handlers.go:274` all guard a resolved agent for nil. The startup rehydration path at `:471` and `:476` does not.** **D86 flagged `:471` as the one establishing writer whose failure mode was unbounded; it is now bounded, and the bound is "stores nil silently."** [source: §3.1–3.3]

---

## §4 — THE INVARIANT TEST RESULTS, CONSOLIDATED

| Site | Live? | Writes `.Parent` | Maintains symmetry | Nil-guarded |
|---|---|---|---|---|
| `demons.go:5242` | **Live** | Yes | **Yes** (`:5244`) | Yes (`:5231`) |
| `demons.go:5254` | **Live** | Yes | **Yes** (`:5256`) | **No — `:5265` is after 3 derefs** |
| `teamserver.go:471` | **Live** | Yes | **Unknown** | **No — stores nil** |
| `agent.go:1201`/`:1216` | **Live** | Yes (temp) | N/A (save/restore) | Yes (`:1214`) |
| `agent.go:580` | **DEAD (comment 538–592)** | **No** | N/A | N/A |

**The D86 census, corrected: six raw matches → five live sites, one dead.**

---

## §5 — WHAT EACH NEGATIVE DOES NOT COVER

**T1's negative** — "the symmetry is maintained by both live establishing writers" — **does not cover whether the symmetry holds after a `PivotRemove`, `LinkRemove`, or agent deletion.** **Those paths were not enumerated in this report.** **Residual D-4.** [source: D76 §3.3 for `PivotRemove`; not re-enumerated here]

**T2's negative** — "no reader is inside the window" — **does not cover concurrency, and does not cover callers of `ToMap` outside this file.** **Residuals D-1, D-2.** [source: §2.3]

**T3's bound** — "stores the nil" — **does not cover whether a stored nil `.Parent` is later repaired by any path.** **The rehydration loop runs at startup; nothing in this report re-establishes `.Parent` afterwards except the connect and register paths.** **Residual D-5.** [source: `:467-478`]

**A-4a remains retired as measured. Not re-opened. Not re-litigated.** [source: D86 §1.3]

---

## §6 — RESIDUAL UNKNOWNS, WITH PROBES

| ID | Unknown | Probe |
|---|---|---|
| **D-1** | **Can `ToMap` run concurrently with a `.Parent` reader?** | Read `ToMap`'s callers and any mutex on `Agent`/`Teamserver`. |
| **D-2** | **Who calls `ToMap`?** | Enumerate `ToMap()` call sites. |
| **D-3** | **Is a nil entry in `Pivots.Links` reachable at `demons.go:5233`?** §3.3. | Trace whether `AgentInstance` in `:476` can return nil given the same DB snapshot that populated `LinksOf`. |
| **D-4** | **Does the symmetry survive agent removal paths?** §5. | Enumerate `PivotRemove`, `LinkRemove`, `AgentRemove`. |
| **D-5** | **Is a nil `.Parent` from `:471` ever repaired?** §5. | Enumerate every post-startup `.Parent` writer — D86 §3.1 lists three. |

---

## §7 — INSTRUMENT FAILURES

**Failure 1 — D86 §3.1 contained a raw-text match inside a comment block, and it survived BOTH my write and the Lead's byte-for-byte re-run of the census.** **`agent.go:580` is inside `/*…*/` spanning `:538`-`:592`.** **The Lead reproduced the six lines exactly because the same class of probe — a pattern match over raw text — was used by both of us.** **A regex census does not know what a comment is.** **This is the second time Rule 20 fired on my own D86, and the fifth consecutive instance in this lane.** **Mitigation now required: every census line must be tested for comment-region membership before it is counted.** [source: §0.1]

**Failure 2 — the Lead's round-21 verification of D76 was "checking `:5242` EXISTS," which is a citation check, not a census.** **The Lead named this himself: "CONFIRMING A CITED SITE IS NOT VERIFYING A CENSUS."** **Recorded here because it is the second distinct verification-method failure in this lane, and it is the reason D76's "one writer" survived review.** [source: Lead, round 23 message]

**Failure 3 — D86's "THREE establishing writers" was really two live plus one dead.** **The count was reported as three; the corrected count is two.** **Reported in place, not silently amended.** [source: §0.2, §1.5]

**Failure 4 — the comment-region test itself was written only after the deadness was noticed by eye, not by probe.** **The probe at §0.1 is retrospective.** **A census that checks comment membership as it enumerates would have caught this in D86.** **Recorded as the reason the mitigation is now mandatory rather than advisory.**

**Failure 5 — a probe that dies returns `[exit code: 1]`, never a partial result.** **Carried from D86 Failure 3 and re-affirmed: no invocation in this report returned a partial result that could pass for a smaller census.** **Stated so the absence of failures here is itself evidenced rather than assumed.** [source: D86 §5 Failure 3]

**Net: five failures. Failure 1 invalidates one line of a published, Lead-verified report and is the sharpest instance of Rule 20 in this lane to date.**

---

## §8 — WHAT THIS CHANGES

| Item | Verdict | Basis |
|---|---|---|
| **D86 C-2** | **CLOSED.** Both live establishing writers maintain the symmetry. **The defect is not an integrity break but a nil-deref ordering error at `demons.go:5254`** (guard at `:5265` after three derefs; `handlers.go:274` does it correctly on the same call). | §1.2, §1.5 |
| **D86 C-4** | **CLOSED as STRUCTURAL-ONLY.** No `.Parent` reader is inside `:1201-:1216`. **Does not cover concurrency — D-1, D-2 open.** | §2.3 |
| **D86 §3.1 census** | **CORRECTED here: `agent.go:580` is dead code.** Five live sites, not six. | §0.1 |
| **`teamserver.go:471`** | **BOUNDED.** Stores nil silently; same shape at `:476` for `Links`. | §3.2, §3.3 |
| **A-4a** | **Stays retired as measured. Not re-opened.** | §5 |

**No contradiction with D47, D56, or D65. Two corrections to D86, one line of it struck; one correction to D76's census basis carried from D86.**

---

**End of D89.**
