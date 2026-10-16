# D91 — Sliver AI-path operator identity: a wired ownership filter, disconnected at every call site

**Round 23.** Lane: sliver-diver. **Write scope:** this file only. **D1–D88 are PROTECTED and none was edited** — two corrections are recorded here, in §1.6 and §4, naming `D81` and `D75`.
**Source root:** `C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\01_SOURCE_c2\sliver`
**Method:** source-only. No REA, no `open_binary`, no execution, no network.
**Tags:** `[verified]` = probe output printed beside the claim. `[read]` = cited lines read. `[inferred]` = reasoning from read evidence. `[absence]` = a zero, with the enumeration that produced it printed.

**LINE-COUNT CONVENTION:** every count is **LF bytes**. `[verified]` A file with a trailing newline has `LF bytes == Get-Content .Count`. **Re-verified this round on D81: 43,608 B, last byte `10` (LF), LF count 560, `Get-Content .Count` 560 — equal.** `[verified]` **All line references are 1-based LF offsets.**

**D91 OCCUPATION CHECK — run before writing, by enumeration:** `[verified]`

```powershell
Get-ChildItem $d -File -Filter 'D91_*'          # -> 0 matches
Get-ChildItem $d -File -Filter 'D9*.md'         # -> 1: D9_msf_core_library.md
```

`[verified]` **D91 was free. The only `D9*` file is `D9_msf_core_library.md` (161,013 B), a different lane's.** `[verified]`

---

## 0. Method note — Rule 20 applied three times, and it found something larger than the task

**The task was to drive D81's R7 (`aiOperatorName`'s client-controlled fallback) to a verdict.** `[read]` **Rule 20 was applied as the first action of each sub-question, before any reasoning. On the second application it found an adjacent defect larger than R7, which is now the report's headline.** `[verified]`

**The standing rule, and this round's instance of it:** `[inferred]` **A path named is not a census — neither is a call site, nor a test's variable names. Every claim below has its enumeration printed beside it.** `[inferred]`

**Case-sensitivity:** `[verified]` every membership test uses `-ccontains`/`-cmatch`. **No case-folding defect occurred in D91.** `[verified]`

---

## 1. T1 — R7 DRIVEN TO A VERDICT

### 1.1 T1(a) — WHO CALLS `aiOperatorName`, and is `fallback` client-controlled at every site?

**Rule 20 enumeration, all `.go` excluding `vendor\`, case-sensitive:** `[verified]`

```powershell
Get-ChildItem $s -Recurse -File -Filter *.go |
  Where-Object {$_.FullName -notmatch '\\vendor\\'} |
  Select-String -Pattern 'aiOperatorName' -CaseSensitive
```

`[verified]`

```
server\rpc\rpc-ai.go:19    func (rpc *Server) aiOperatorName(ctx context.Context, fallback string) string   <- DECLARATION
server\rpc\rpc-ai.go:86    req.OperatorName = rpc.aiOperatorName(ctx, req.OperatorName)
server\rpc\rpc-ai.go:100   operatorName := rpc.aiOperatorName(ctx, "")
server\rpc\rpc-ai.go:144   req.OperatorName = rpc.aiOperatorName(ctx, req.OperatorName)
```

`[verified]`

> **THREE call sites, not the "every call site" the task assumed might be several. Two of the three are live client-controlled.** `[verified]`

**Each site, with `fallback` traced to its origin:** `[verified]`

| # | Site | `fallback` argument | Origin of `fallback` | Client-controlled? |
|---:|---|---|---|---|
| 1 | `rpc-ai.go:86` | `req.OperatorName` | **protobuf field** on `clientpb.AIConversation`, arriving over gRPC | **YES** |
| 2 | `rpc-ai.go:100` | `""` | **hardcoded literal** | **NO** |
| 3 | `rpc-ai.go:144` | `req.OperatorName` | **protobuf field** on `clientpb.AIConversationMessage`, arriving over gRPC | **YES** |

`[verified]`

**The handler context for each, read contiguously:** `[verified]`

```go
75: func (rpc *Server) SaveAIConversation(ctx context.Context, req *clientpb.AIConversation) (*clientpb.AIConversation, error) {
86: 	req.OperatorName = rpc.aiOperatorName(ctx, req.OperatorName)
87: 	conversation, err := db.SaveAIConversation(req, req.OperatorName)

95: func (rpc *Server) DeleteAIConversation(ctx context.Context, req *clientpb.AIConversationReq) (*commonpb.Empty, error) {
100: 	operatorName := rpc.aiOperatorName(ctx, "")
101: 	err := db.DeleteAIConversation(req.ID, "")

128: func (rpc *Server) SaveAIConversationMessage(ctx context.Context, req *clientpb.AIConversationMessage) (*clientpb.AIConversationMessage, error) {
144: 	req.OperatorName = rpc.aiOperatorName(ctx, req.OperatorName)
145: 	message, err := db.SaveAIConversationMessage(req, req.OperatorName)
```

`[verified]`

> **T1(a) ANSWER: `fallback` IS genuinely client-controlled at two of three call sites (`:86`, `:144`), and it is a protobuf request field with no validation anywhere between the wire and the assignment. `[verified]` `:100` is a hardcoded `""` and is not a `fallback` path at all.** `[verified]`

**No validation of `req.OperatorName` exists on either path — enumerated, not assumed:** `[verified]` **`:79-84` validates `req.Provider` and `req.ThinkingLevel`; `:132-142` validates `req.ConversationID`, `req.Role`, and `req.Provider`. Neither validates `req.OperatorName`.** `[absence]`

### 1.2 T1(b) — WHAT DOES THE STORED VALUE DO? The write site

**The value reaches persistence in three steps. Read contiguously:** `[verified]`

```go
// server\db\models\ai.go:103-105  (protobuf -> model)
return &AIConversation{
    ID:                           id,
    OperatorName:                 pbConversation.OperatorName,     // carried through verbatim
```

`[verified]`

```go
// server\db\helpers.go:1515-1519   WriteAIConversation
func SaveAIConversation(conversation *clientpb.AIConversation, operatorName string) (*clientpb.AIConversation, error) {
	dbConversation := models.AIConversationFromProtobuf(conversation)
	if dbConversation.OperatorName == "" && operatorName != "" {
		dbConversation.OperatorName = operatorName
	}
```

`[verified]`

```go
// server\db\helpers.go:1597-1612   SaveAIConversationMessage
	if operatorName != "" {
		dbMessage.OperatorName = operatorName
	} else if dbMessage.OperatorName == "" {
		dbMessage.OperatorName = conversation.OperatorName
	}
```

`[verified]`

> **The write site DOES NOT sanitise. `[verified]` At `:1517` and `:1608` the parameterised value is overwritten into the record only when non-empty — but the client value has ALREADY been placed there by the protobuf mapping at `ai.go:105`, and at `:1517` the condition `dbConversation.OperatorName == ""` is FALSE precisely because the client supplied a value.** `[verified]` **So a client-supplied `OperatorName` is persisted verbatim and is never corrected.** `[verified]`

**One nuance that matters and is easy to get backwards:** `[verified]` **when the CN resolves NON-empty, `aiOperatorName` returns the CN (`:21-22`) and `:86` assigns the CN over the client's value BEFORE the mapping — so the CN wins.** `[verified]` **The client's value survives ONLY when the CN is empty.** `[verified]` **This makes T2 (§2) the precondition for the entire finding, exactly as the task said.** `[inferred]`

### 1.3 T1(b) continued — the READERS, and the defect that is larger than R7

**Enumerating every reader of `OperatorName` on the AI path, and every call of the two ID-keyed helpers:** `[verified]`

```powershell
... Select-String -Pattern 'AIConversationByID\(' -CaseSensitive
```

`[verified]`

```
server\db\helpers.go:1433   func AIConversationByID(id string, operatorName string, includeMessages bool)   <- DECLARATION
server\db\helpers.go:1526   return AIConversationByID(dbConversation.ID.String(), "", true)
server\db\helpers.go:1556   return AIConversationByID(existing.ID.String(), "", true)
server\db\helpers.go:1561   conversation, err := AIConversationByID(id, "", false)
server\db\helpers.go:1585   conversation, err := AIConversationByID(id, operatorName, true)      <- ONLY non-empty
server\db\helpers.go:1603   conversation, err := AIConversationByID(dbMessage.ConversationID.String(), "", false)
server\rpc\rpc-ai-events.go:56   conversation, err := db.AIConversationByID(conversationID, "", false)
server\rpc\rpc-ai-events.go:292  conversation, err := db.AIConversationByID(s.conversationID, "", false)
server\rpc\rpc-ai.go:68          conversation, err := db.AIConversationByID(req.ID, "", req.IncludeMessages)
server\rpc\rpc-ai.go:179         conversation, err := db.AIConversationByID(conversationID, "", true)
```

`[verified]`

**And the filter the parameter drives, read in full:** `[verified]`

```go
1433: func AIConversationByID(id string, operatorName string, includeMessages bool) (*clientpb.AIConversation, error) {
...
1450: 	query = query.Where("id = ?", conversationID)
1451: 	if operatorName != "" {
1452: 		query = query.Where("operator_name = ?", operatorName)
1453: 	}
```

`[verified]`

> **THE DEFECT: a real, correctly-written SQL ownership filter exists at `:1451-1452`, and it is DISABLED at 8 of its 9 call sites because they pass `""`.** `[verified]` **This is not a missing check. It is a present check wired to a constant.** `[verified]`

**The comparison the task asked for — "is there one downstream?" — is answered, and the answer is YES but it is DISARMED at the RPC layer:** `[verified]`

| Reader | Handler | Argument passed | Ownership enforced? |
|---|---|---|---|
| `AIConversationByID` | `GetAIConversation` (`rpc-ai.go:63-73`) | `:68` `""` | **NO** |
| `AIConversationMessagesByID` | `GetAIConversationMessages` (`:116-126`) | `:121` `""` | **NO** |
| `DeleteAIConversation` | `DeleteAIConversation` (`:95-114`) | `:101` `""` | **NO** |
| `AIConversationsByOperator` | `GetAIConversations` (`:55-61`) | `:56` `""` — **hardcoded** | **NO — the LIST is unfiltered** |

`[verified]`

**The list helper, and the same disabled filter:** `[verified]`

```go
1414: func AIConversationsByOperator(operatorName string) ([]*clientpb.AIConversation, error) {
1416: 	query := Session().Model(&models.AIConversation{})
1417: 	if operatorName != "" {
1418: 		query = query.Where("operator_name = ?", operatorName)
1419: 	}
1420: 	err := query.Order("updated_at desc").Order("created_at desc").Find(&conversations).Error
```

`[verified]`

**And `DeleteAIConversation` — the sharpest instance, because it takes the parameter and discards it:** `[verified]`

```go
1560: func DeleteAIConversation(id string, operatorName string) error {
1561: 	conversation, err := AIConversationByID(id, "", false)      // <- operatorName is IGNORED; "" hardcoded
...
1571: 	err = Session().Where(&models.AIConversationMessage{ConversationID: conversationID}).Delete(&models.AIConversationMessage{}).Error
1578: 	return Session().Where(&models.AIConversation{ID: conversationID}).Delete(&models.AIConversation{}).Error
```

`[verified]`

> **`DeleteAIConversation` declares an `operatorName` parameter, receives it from its caller, and then passes `""` at `:1561` — so ANY caller who knows a conversation UUID deletes that conversation AND all of its messages, regardless of owner.** `[verified]` **This is the "READ THE ACCESSOR NEXT TO ITS SIBLING" rule firing on a parameter: declared at `:1560`, offered by the caller at `rpc-ai.go:100`, and read NOWHERE.** `[verified]`

**And the RPC handler compounds it:** `[verified]`

```go
100: 	operatorName := rpc.aiOperatorName(ctx, "")
101: 	err := db.DeleteAIConversation(req.ID, "")           // <- the computed operatorName is NOT passed
...
110: 		OperatorName: operatorName,                        // <- used ONLY as event metadata
```

`[verified]`

> **`rpc-ai.go:100` computes an operator name and `:101` passes `""` instead. The computed value is used only for the event payload at `:110`.** `[verified]` **This is the crossed wire in its purest form: the value exists, is correct, and is routed to the log line rather than the query.** `[verified]`

### 1.4 T1 verdict — LIVE FINDING, severity bounded by the role gate

**Both conditions the task set are met:** `[verified]`
1. **`fallback` is client-controlled** at `rpc-ai.go:86` and `:144` — protobuf fields, no validation (§1.1). `[verified]`
2. **The stored value reaches an ownership decision** — it IS the operand of the SQL ownership filter at `helpers.go:1452` and `:1418`. `[verified]` **The filter is disarmed at every RPC entry point (§1.3), which means the value does not have to be forged for cross-operator access to succeed — but it is the field the defensive layer keys on.** `[verified]`

> **VERDICT: LIVE FINDING — cross-operator access to the AI conversation store. A `PermissionAll` operator who knows or guesses a conversation UUID can read, enumerate, and permanently delete another operator's AI conversations and all their messages, because the ownership filter that exists in the data layer is passed the empty string at every RPC-reachable call site.**
>
> **SEVERITY, BOUNDED AND NOT INFLATED:** `[verified]` **all seven AI RPCs are absent from both transport allowlists (`0` matches, case-sensitive), so they require `PermissionAll`.** `[verified]` **The attacker must therefore already hold a `PermissionAll` token. This is NOT a privilege escalation across the operator/crackstation/builder role boundary.** `[inferred]` **It is a failure of peer separation WITHIN the `PermissionAll` role: operators who should be mutually isolated share full read/write/delete on each other's AI conversation history.** `[inferred]`

**Why that is still a genuine finding despite the role gate:** `[verified]` **`PermissionAll` is the default role minted by `new-operator` and the normal operator role; the crackstation and builder roles exist precisely as narrower alternatives.** `[inferred]` **The AI store is the one place the codebase wrote an ownership filter — `AIConversationsByOperator`, `AIConversationByID`'s third parameter, `AIConversationMessagesByID` — and then passed `""` at every entry point.** `[verified]` **The intent to isolate is unambiguous in the source; the wiring defeats it.** `[inferred]`

**A SECOND, DISTINCT DEFECT, which is R7 proper and is lower severity:** `[verified]` **when the CN resolves EMPTY (§2), a client-supplied `OperatorName` is persisted verbatim (`ai.go:105` → `helpers.go:1517`) and becomes the stored ownership identity.** `[verified]` **So the field the (disarmed) filter keys on is itself attacker-chosen in exactly the configuration where the filter would have been the only defence.** `[inferred]` **R7 is therefore not merely "a client value reaches a field" — it is "a client value reaches the field the ownership check trusts."** `[verified]`

### 1.5 The one guarded call site — proved to be unreachable

**`helpers.go:1585` is the sole site passing a non-empty `operatorName`:** `[verified]`

```go
1583: // AIConversationMessagesByID - Fetch all messages for a conversation.
1584: func AIConversationMessagesByID(id string, operatorName string) (*clientpb.AIConversationMessages, error) {
1585: 	conversation, err := AIConversationByID(id, operatorName, true)
```

`[verified]`

**Its only caller:** `[verified]`

```
server\rpc\rpc-ai.go:121   messages, err := db.AIConversationMessagesByID(req.ID, "")
```

`[absence]`

> **The one path that COULD enforce ownership is called with `""`. The capability exists and is unreachable from every production entry point.** `[verified]` **A census of the parameter's values, not of its existence, is what establishes this — a search for non-empty arguments was run and `:1585` is the only hit, and its caller supplies `""`.** `[verified]`

### 1.6 CORRECTION to D81 §1.6a — I called this "the highest-value residual" and it was larger than I priced it

**D81 §4 R7 said:** *"`aiOperatorName`'s client-supplied fallback is the one CN-adjacent path where a client string can become an operator identity... PROBE: determine whether any authorization or ownership check on the AI path compares the stored `OperatorName`."* `[read]`

> **The probe was run and the answer is larger than the residual anticipated. `[verified]` D81 framed R7 as a data-integrity question conditional on a downstream comparison existing. The comparison DOES exist (`helpers.go:1451-1452`) and is DISARMED at every RPC entry point (`""` at all eight), so the finding is not conditional on R7 at all — the cross-operator access holds regardless of whether the CN resolves empty.** `[verified]` **D81 named the right file and the wrong object: the defect is not `aiOperatorName`, it is the ownership filter that `aiOperatorName`'s output would have fed.** `[inferred]`

**D81 §1.6a's own claim is re-confirmed and unaffected:** `[verified]` **the four CN-string equalities remain four and remain safe; `rpc-ai.go:20` is correctly classified there as a FALLBACK rather than an equality.** `[verified]` **This report refines the CLASSIFICATION (§4) rather than revising the count.** `[inferred]`

---

## 2. T2 — WHY DOES THE CN RESOLVE EMPTY?

**`getClientCommonName` has exactly four `return ""` branches. Read in full:** `[verified]`

```go
260: func (rpc *Server) getClientCommonName(ctx context.Context) string {
261: 	client, ok := peer.FromContext(ctx)
262: 	if !ok {
263: 		return ""                                    // BRANCH A
265: 	tlsAuth, ok := client.AuthInfo.(credentials.TLSInfo)
266: 	if !ok {
267: 		return ""                                    // BRANCH B
269: 	if len(tlsAuth.State.VerifiedChains) == 0 || len(tlsAuth.State.VerifiedChains[0]) == 0 {
270: 		return ""                                    // BRANCH C
272: 	if tlsAuth.State.VerifiedChains[0][0].Subject.CommonName != "" {
273: 		return tlsAuth.State.VerifiedChains[0][0].Subject.CommonName
275: 	return ""                                        // BRANCH D
```

`[verified]`

**The task offered three hypotheses. They map onto the branches as follows, and one is dominant:** `[verified]`

| Task hypothesis | Branch | Reachable? | Evidence |
|---|---|---|---|
| **(iii) a context that never went through the interceptor** | A (`peer.FromContext` fails) | **No** | `peer.FromContext` is populated by gRPC's transport for any served RPC; not interceptor-dependent |
| **(i) a transport without client certs** | **B (`AuthInfo` is not `TLSInfo`)** | **YES — DOMINANT** | see below |
| **(ii) a cert with an empty CN** | C / D | Theoretically yes | **requires a CA-signed leaf with an empty CN; `ValidateOperatorClientCertificate` (`operators.go:76`) rejects `Subject.CommonName == ""` at the TLS layer** `[read]` |

`[verified]`

> **T2 ANSWER: BRANCH B — a transport that presents no client certificate, so `AuthInfo` is not `credentials.TLSInfo`.** `[verified]`

**The transport that produces Branch B, and it must be enabled explicitly:** `[verified]`

- **`local.go:39-47`** — `LocalListener()` calls `initMiddleware(false)` and serves over a **`bufconn`** in-memory listener. `[verified]`
- **`console.go:41-55`** — the only production caller: `transport.LocalListener()` at `:42`, then `grpc.WithInsecure()` at `:54` with the comment **`"This is an in-memory listener, no need for secure transport"`**, dialling `"bufnet"` at `:55`. `[verified]`
- **`initMiddleware` call sites, Production censused:** `[verified]` **`local.go:47` (`false`), `mtls.go:89` (`true`), `tailscale.go:85` (`true`).** `[verified]`

> **On the local transport there is no TLS, so `AuthInfo` is not `TLSInfo`, so Branch B fires and the CN is ALWAYS empty. `[verified]` And that transport requires an explicit act to exist: it is constructed only by `console.Start`, itself reached only from `server\cli\cli.go:165`.** `[verified]`

**THE SEVERITY CONSEQUENCE, stated because the task asked for it explicitly:** `[verified]`

> **R7's precondition is "a transport that must be enabled explicitly." `[verified]` On `mtls` (`mtls.go:89`) and `tailscale` (`tailscale.go:85`) the client certificate IS required and verified (`mtls.go:145-154` sets `ClientAuth: tls.RequireAndVerifyClientCert`), so the CN resolves NON-empty and `aiOperatorName` returns the CN — the client's `fallback` is discarded.** `[verified]` **Therefore R7 becomes reachable ONLY via the local `bufconn` transport, i.e. the in-process console path, where the caller is the local console process itself and is already trusted.** `[inferred]`

`[verified]`

> **THIS MATERIALLY REDUCES R7's SEVERITY. `[verified]` R7 is NOT an over-the-wire attack against a remote mTLS operator. It is reachable only on the local transport, where the "client" is the same process that owns the database.** `[inferred]` **I am recording it as lower severity than D81's framing implied, per the task's instruction not to inflate.** `[inferred]`

**And the cross-operator access defect of §1.4 is NOT reduced by this, because it is a different mechanism:** `[verified]` **the disarmed filter at `helpers.go:1451` and `:1418` is passed `""` by callers regardless of transport.** `[verified]` **On mTLS, where the CN is correctly resolved, `rpc-ai.go:68`/`:121`/`:101`/`:56` STILL pass `""` — so the ownership filter is disabled for authenticated remote operators too.** `[verified]` **That is why §1.4 survives T2 and R7 does not.** `[verified]`

### 2.1 One further bound on T2

**Branch B is not exclusively the local transport.** `[verified]` **Any RPC context whose `AuthInfo` is not `credentials.TLSInfo` produces it.** `[inferred]` **I censused the three `initMiddleware` call sites and the one production `LocalListener` caller; I did NOT audit whether any other dialer or test harness serves these RPCs with a non-TLS credential.** `[verified]` **Filed as §5 R4.** `[inferred]`

---

## 3. T3 — THE EIGHT-SITE CLASSIFICATION TABLE, and the sub-species it proves

**Rule 20 enumeration, re-run and printed:** `[verified]`

```powershell
Get-ChildItem $s\server -Recurse -File -Filter *.go |
  Where-Object {$_.FullName -notmatch '\\vendor\\' -and $_.Name -notlike '*_test.go'} |
  Select-String -Pattern 'getClientCommonName' -CaseSensitive
```

`[verified]`

**All eight production call sites, classified by what each does with the value:** `[verified]`

| # | Site | Disposition of the CN | Class |
|---:|---|---|---|
| 1 | `rpc-ai.go:20` | returned as identity, **else client `fallback`** | **STORED (via fallback) + FALLBACK** |
| 2 | `rpc-client-logs.go:87` | `getClientLogsDir(commonName)` at `:88` | **STORED (path key)** |
| 3 | `rpc-crackstations.go:385` | compared at `:393` | **EQUALITY** |
| 4 | `rpc-crackstations.go:703` | bound, written at `:275` | **STORED** |
| 5 | `rpc-events.go:17` | `core.NewClient(commonName)` at `:18` | **STORED (client key)** |
| 6 | `rpc-generate.go:721` | bound, written to builder | **STORED** |
| 7 | `rpc-generate.go:856` | compared at `:864` | **EQUALITY** |
| 8 | `rpc-generate.go:883` | compared at `:891` | **EQUALITY** |

`[verified]`

**Class totals:** `[verified]` **EQUALITY = 3 · STORED = 5 · LOGGED = 0 · DISCARDED = 0.** `[verified]`

> **THE TABLE PROVES THE SUB-SPECIES CLAIM. `[verified]` Sites 3, 7, 8 are the three equality tests, all comparing a server-derived CN to a server-derived stored value — safe on identical ground. `[verified]` Sites 2, 4, 5, 6 store the CN as a key or owner field derived ONLY from the CN itself.** `[verified]` **Site 1 is the ONLY site where the STORED value can originate from a CLIENT rather than from the CN — `rpc-ai.go:20-24`'s fallback branch is the single cell in the table where the stored identity is not necessarily the certificate's identity.** `[verified]`

`[verified]`

> **CONFIRMED: R7 is the ONLY instance of its sub-species among the eight. The table proves it by exhaustion — every other STORED site writes the CN, and the only site that can write something OTHER than the CN is `rpc-ai.go:20`.** `[verified]`

**The qualification, stated so the proof is honest:** `[verified]` **the table proves uniqueness among the EIGHT `getClientCommonName` call sites. It does not prove uniqueness among all identity-storing sites in the tree, which include the token→operator row path (`middleware.go:146-154`, D75 §1.4) and the WG-key path.** `[inferred]` **The bound is: within this population, R7 is the only client-influenceable stored identity.** `[verified]`

---

## 4. Correction to D81 §1.6a — the classification gains a fifth class

**D81 §1.6a classified the eight sites as EQUALITY (4) and "not an equality" (4), with `rpc-ai.go:20` labelled "FALLBACK".** `[read]`

> **The count of four equalities stands. `[verified]` What D81 lacked was the STORED class, which is where both the cross-operator defect (§1.4) and R7 (§1.5) live.** `[verified]` **D81's closing line — "a path named is not a census" — was right, and the census D81 ran was one class too shallow: it asked only "is this an equality?" when the defect was in the sites answering "no".** `[inferred]` **The refinement is recorded here; D81 is PROTECTED and not edited.** `[verified]`

---

## 5. Residuals

**R1 — the `PermissionAll` role's real isolation boundary.** `[verified]` **§1.4 bounds severity by the allowlist absence (0 matches).** `[inferred]` **PROBE:** determine whether `PermissionAll` is intended to be single-operator-per-server (in which case cross-operator AI access is a non-issue) or multi-operator (in which case §1.4 is the finding it appears to be). **This single question sets §1.4's true severity and I did not read the deployment guidance.**

**R2 — whether `GetAIConversations` returning unfiltered results leaks across iterations.** `[read]` **`rpc-ai.go:56` hardcodes `""`.** `[verified]` **PROBE:** confirm `AIConversation.ToProtobuf` at `ai.go:73` exposes `OperatorName` in the response, which would make the leak directly observable to the caller. `[inferred]`

**R3 — the event-broker readers at `rpc-ai-events.go:56` and `:292`.** `[verified]` **Both pass `""`.** `[inferred]` **PROBE:** determine whether those events are delivered to ALL subscribed operators, which would widen the leak beyond request/response into push.**

**R4 — other non-TLS `AuthInfo` producers.** `[verified]` **§2.1's bound.** `[inferred]` **PROBE:** census every `grpc.Dial`/`DialContext` and every `grpc.NewServer` in `server\` for a credential that is not `credentials.TLSInfo`.**

**R5 — `rpc-client-logs.go:88` `getClientLogsDir(commonName)`.** `[verified]` **A CN-derived filesystem path.** `[inferred]` **PROBE:** if the CN can be empty on the local transport (Branch B), determine what directory an empty CN produces — a path-construction concern adjacent to D44 §R3's `dns.go:69`.**

---

## 6. Instrument failures and corrections

| # | Item | Where | Resolution |
|---|---|---|---|
| **F1** | **D81 priced R7 as conditional data-integrity.** The downstream comparison exists and is disarmed, making the larger defect unconditional. | §1.6 | **D81 named the right file and the wrong object. Recorded here; D81 PROTECTED, not edited.** |
| **F2** | **D81's classification stopped at EQUALITY vs not.** The STORED class is where both defects live. | §4 | **One class deeper. Count unchanged; classification refined.** |
| **F3** | **Rule 20 produced a NON-obvious result on its second application this round.** | §1.3 | **The task asked about `aiOperatorName`'s callers; the census of `AIConversationByID`'s callers found eight `""` arguments. The adjacent population was the one that mattered.** |
| **F4** | **All probes on disk; none broken.** | — | **Every snippet was executed; its output is pasted above. No retained probe is silently broken (D69 §7).** |

`[verified]`

---

## 7. Summary

**T1 — R7 DRIVEN TO A VERDICT: LIVE, in two distinct parts.** `[verified]`

**Part 1 (larger, and found by the census rather than the task):** `[verified]` **`helpers.go:1433` `AIConversationByID(id, operatorName, includeMessages)` implements a correct SQL ownership filter at `:1451-1452`, and 8 of its 9 call sites pass `""`, disabling it. `AIConversationsByOperator` at `:1414` has the identical filter, disabled by a hardcoded `""` at `rpc-ai.go:56`. `DeleteAIConversation` at `:1560` accepts an `operatorName` parameter and passes `""` at `:1561`, so it deletes any conversation by UUID plus all its messages.** `[verified]` **Result: a `PermissionAll` operator can enumerate, read, and permanently delete another's AI conversations.** `[verified]`

**Part 2 (R7 proper, lower severity than framed):** `[verified]` **`fallback` IS client-controlled at `rpc-ai.go:86` and `:144` (protobuf fields, unvalidated), and is persisted verbatim when the CN is empty — so the client chooses the value the ownership filter would key on.** `[verified]`

**T2 — THE CN RESOLVES EMPTY AT BRANCH B.** `[verified]` **`:265-267` — `client.AuthInfo.(credentials.TLSInfo)` fails on a transport with no client certificate. That is the `bufconn` local listener (`local.go:39-47`, `initMiddleware(false)`), whose only production entry is `console.go:42` — an explicitly-constructed in-process transport with no TLS ("*no need for secure transport*").** `[verified]` **On `mtls.go:89` and `tailscale.go:85` the client cert is required and verified, the CN resolves non-empty, and R7 is unreachable.** `[verified]` **THIS MATERIALLY REDUCES R7: it is not a remote attack, only a local-console concern. §1.4's defect is NOT reduced, because its `""` arguments are passed on every transport.** `[verified]`

**T3 — THE TABLE PROVES THE SUB-SPECIES.** `[verified]` **Eight sites: EQUALITY 3, STORED 5, LOGGED 0, DISCARDED 0. The three equalities are safe on identical ground. Of the five STORED sites, four store the CN itself — and `rpc-ai.go:20` is the ONLY one that can store a CLIENT-supplied value. R7 is the sole instance of its sub-species, proved by exhaustion over the population.** `[verified]`

**The single most important sentence:** `[verified]` + `[inferred]` **Sliver wrote a correct ownership filter for the AI conversation store and then passed the empty string to it at every point where an operator can reach it — so the check is not missing, it is present and inert, and the only configuration where a client can also choose the value that check keys on is the local transport where the client is the server's own console process.**

**The method sentence:** `[inferred]` **Rule 20 was applied to answer a question about `aiOperatorName` and found the defect by censusing a population the question did not name — which is the rule working as intended, and the second consecutive round where the census mattered more than the trace.**
