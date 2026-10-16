# D168 — The Covenant Authority Chain, Reversed End to End: the Implant Plane Is `[AllowAnonymous]` by Design, the HMAC Is the Sole Authorisation Boundary, and the Verdict Is a Qualified NO

**SCOPE:** The Covenant grunt tasking/authority chain, read as four sequential links — wire→deserialisation, type dispatch, authorisation, execution sink — under `RE_Library\01_SOURCE_c2\covenant\Covenant` (all cited paths relative to that root). Static source only. Four original transport/listener/hub/controller files read in full or in cited ranges: `GruntHTTP.cs`, `InternalListener.cs`, `HttpListenerController.cs`, `Startup.cs`, plus all three SignalR hubs and the API-controller attribute census. `GruntSMB.cs` and `GruntBridge.cs` consulted for cross-transport comparison only; their link-level sites are cited from D151's already-read evidence, not re-read here.

**DEFINER SCOPE:** Covenant's *implant-plane* authority path specifically — the path a Grunt tasking message traverses from an inbound HTTP/SMB/TCP body to the point where the server acts on it. The *operator-plane* path (a human user's browser/JWT session driving the REST API and the hubs) is a DIFFERENT trust domain and is scoped separately wherever it appears. Conflating the two is the failure mode this report exists to prevent.

**CONDITIONAL SCOPE:** All conclusions are conditional on the three gates in the sink path (`InternalListener.cs:515` GUID equality, `:547` HMAC verification, `:481` `GruntStatus` state machine) being the *only* gates between the HTTP entry point and `PostTask`. I read the entry point, the listener, and the sink; I did NOT read `GruntSessionDecrypt`'s implementation, nor `CheckInGrunt`. An unread intermediate gate would not change the verdict's direction (it would add a gate, not remove one) but could change the enumeration in §3.

**COUNTED:** Files read this round: 13 (11 read directly, 2 by attribute census). Cited line ranges: 34 distinct ranges across 9 files, enumerated in §7. Controls run: 4 (2 reach/block control pairs, 1 harness positive control, 1 cross-check). Enumerated enum members: 9 (`GruntStatus`). Gates on the sink path: 3 pre-sink + 4 post-entry, per §3.2. The state machine's dominance: 9 members enumerated, 2 reach `PostTask`, 7 do not.

---

## §0 — The verdict, stated first

**CAN A MESSAGE THAT FAILS AUTHORISATION OR CARRIES AN UNRECOGNISED TYPE REACH THE EXECUTION SINK?**

**No to the unrecognised type. No to the failed authorisation — with one qualification that is the actual finding of this report.**

| question | answer | governing evidence |
|---|---|---|
| Does an **unrecognised tasking type name** reach the sink? | **NO** — it throws at parse | `GruntHTTP.cs:1016` `Enum.Parse`, caught at `:97` |
| Does an **unrecognised `GruntStatus`** reach the sink? | **NO** — `default:` blocks | `InternalListener.cs:501-503` |
| Does a message **failing GUID authorisation** reach the sink? | **NO** — early return | `InternalListener.cs:515-520` |
| Does a message **failing HMAC** reach the sink? | **NO** — early return | `InternalListener.cs:547-552` |
| Is there **any** framework-level auth on the implant path? | **NONE, BY DESIGN** | `HttpListenerController.cs:21,41` `[AllowAnonymous]` |
| So what is the **sole** authorisation boundary? | **`VerifyHMAC`** | `InternalListener.cs:875` |

**The chain is guarded — and it is guarded by exactly one mechanism, deliberately, at one line.** That is a stronger and more specific statement than "a check exists."

**Why this is the interesting answer:** D143/D151 established that Covenant's *dispatch* fails **OPEN** — an unrecognised type falls through with no `else`, no `default:`, no `throw`, silently discarded (`GruntHTTP.cs:340→341`). This report asked whether that fail-open character reaches the sink. **It does not.** The fail-open is at the *client-side dispatch*, which is a **liveness/silent-drop** property on the implant. The *server-side* authority path fails **CLOSED**, and it fails closed **five times over** — one HMAC gate per stage transition plus the task gate. **Covenant is fail-open in dispatch and fail-closed in authority.** Those are different layers and the corpus's earlier framing did not separate them.

**[verified]** for every gate site cited above — each read at the line.

---

## §1 — Link 1: the wire → deserialisation boundary

### 1.1 The implant entry point is an `[AllowAnonymous]` controller

**Read: `HttpListenerController.cs:1-80`, `:80-119`.**

```csharp
[AllowAnonymous]                                  // L21 — class
public class HttpListenerController : Controller
{
    [AllowAnonymous]                              // L41 — action
    public async Task<ActionResult<string>> Route()
```

**[verified] `[AllowAnonymous]` is applied at BOTH class and action level.** This is not an oversight — it is **required**: an implant is not a logged-in operator and cannot present a JWT. But the consequence is unavoidable and load-bearing:

> **The implant plane has NO framework-level authorisation. `app.UseAuthorization()` (`Startup.cs:228`) does not gate it. Every gate is inside the application code.**

This corrects an interim hypothesis of mine (§6.3): I initially expected to find "two trust domains with authorisation at the operator plane." The accurate statement is sharper — the implant plane is *explicitly opted out* of framework auth, so its entire authority is delegated to one application-level function.

### 1.2 The deserialisation chain, read in order

**Read: `GruntHTTP.cs:480-519`, `:1005-1074`.**

```
POST body
  → Route()                                  HttpListenerController.cs:54-62
  → body.ParseExact(HttpPostRequest)         :58
  → _internalListener.Write(guid, msg)       :59
  → ProfileInvert + JsonConvert.Deserialize  InternalListener.cs:415-416
  → message.GUID → targetGrunt lookup        :436
  → status switch                            :481
  → PostTask → HMAC gate                     :547
  → GruntSessionDecrypt                      :553
  → JsonConvert.Deserialize<TaskResponse>    :554
```

**Read `GruntHTTP.cs:480-519` — the client-side `ReadTaskingMessage`:**

```csharp
else if (gruntMessage.Type == GruntEncryptedMessage.GruntEncryptedMessageType.Tasking)   // L488
{
    string json = this.Crafter.Retrieve(gruntMessage);                                   // L490
    return (json == null || json == "") ? null : GruntTaskingMessage.FromJson(json);      // L491
}
```

**[verified] `Crafter.Retrieve` is the only gate here, and there is no identity check.** But this is the *implant* side — the implant is the party being tasked, so the absence of an identity check is correct by construction. **The authority question lives on the server side, and that is `InternalListener.Write`.**

### 1.3 The deserialiser is a hand-rolled regex extractor, not a JSON parser

**Read: `GruntHTTP.cs:1009-1032`, `:1227-1240`.**

```csharp
private static string GruntTaskingMessageFormat = @"{{""type"":""{0}"",""name"":""{1}"",""message"":""{2}"",""token"":{3}}}";   // L1009

public static GruntTaskingMessage FromJson(string message)                          // L1010
{
    List<string> parseList = Utilities.Parse(message, GruntTaskingMessageFormat);    // L1012
    if (parseList.Count < 3) { return null; }                                        // L1013
    return new GruntTaskingMessage
    {
        Type = (GruntTaskingType)Enum.Parse(typeof(GruntTaskingType), parseList[0], true),   // L1016
        Name = parseList[1],
        Message = parseList[2],
        Token = Convert.ToBoolean(parseList[3])                                      // L1019
    };
}
```

And the extractor it depends on:

```csharp
public static List<string> Parse(string data, string format)                         // GruntHTTP.cs:1227
{
    format = Regex.Escape(format).Replace("\\{", "{").Replace("{{", "{").Replace("}}", "}");
    if (format.Contains("{0}")) { format = format.Replace("{0}", "(?'group0'.*)"); }  // L1230
    ...
    Match match = new Regex(format).Match(data);                                      // L1236
```

**[verified] `(?'groupN'.*)` is greedy and the `Match` is unanchored.** I reproduced this transform exactly and tested it (§4.1). Three properties confirmed:

- **UNANCHORED** — `JUNKJUNK/api/ZZZ/data` against `api/{0}/data` extracts `ZZZ`. A value is extracted from input that does not match the profile's format.
- **GREEDY, UNBOUNDED** — `api/X/data---api/Y/data` extracts `X/data---api/Y`, spanning two literal occurrences and a segment boundary.
- **CONSUMES TO END** — `sessionid={0}` against `sessionid=abc123; other=zzz` extracts the entire tail.

**The same `Parse` shape is duplicated in `HttpListenerController.cs:102`** for GUID extraction. **There are nine copies of `Parse` in the tree** (enumerated §7.2) — one per transport/stager/controller.

### 1.4 Does the parse defect reach the sink? — the honest answer

**No, and I tested the specific hijack rather than reasoning about it.** The `message` field is `group2`, greedy. A crafted message containing `","token":true` should shift material into `group3`. **Read the result (§4.2):**

```
input : {"type":"ZZZNOTATYPE","name":"T1","message":"x","token":true}","token":true}
group0 (type)    : [ZZZNOTATYPE]
group1 (name)    : [T1]
group2 (message) : [x","token":true}]
group3 (token)   : [true}]
```

**The injection DOES shift the parse — and it lands on a THROW.** `Convert.ToBoolean("true}")` raises `FormatException` because the greedy group swallowed the closing `}` into the token field. **The hijack is real as a parser property and inert as an attack: it produces an exception, the exception is caught upstream, and the message is dropped.** It cannot produce a clean `Token=true`, because `.*` greedily over-consumes every time the attacker tries to inject a terminator.

**[inferred]** — this is the strongest form of the claim I can support statically: the greedy quantifier's over-consumption is what neutralises the injection, and that is an *accident of greediness*, not a designed defence. A non-greedy `(.*?)` here would be **more** injectable. **This is worth stating precisely because it inverts intuition: the defect is protective.** I am labelling it `[inferred]` rather than `[verified]` because I tested the regex, not the running C2.

### 1.5 A round-trip asymmetry I checked and RETRACTED

`GruntTaskingMessage.ToJson` at `:1027` emits `message.Type.ToString("D")` — a **decimal number** — while `FromJson` at `:1016` calls `Enum.Parse` expecting a **name**. That looks like a fatal round-trip bug.

**It is not, and reading the actual serialiser killed it.** `InternalListener.cs:162`:

```csharp
return this.CreateMessageForGrunt(grunt, targetGrunt, Common.CovenantEncoding.GetBytes(JsonConvert.SerializeObject(taskingMessage)));   // L162
```

**The server serialises tasking with Newtonsoft, not with `ToJson`.** Newtonsoft honours `StringEnumConverter` and emits the enum as a **string name** — which is exactly what `Enum.Parse` consumes. **They agree.** The numeric `"D"` format is confined to `GruntTaskingMessageResponse.ToJson`, which encodes **status**, not type.

**Logged as correction C-29.** This was a plausible, alarming, and wrong claim; the serialiser read at `:162` refuted it. Had I reported the asymmetry, it would have been a fabricated headline. §6.2 records the process defect that produced it.

---

## §2 — Link 2: type dispatch, and where an unrecognised type actually goes

### 2.1 Two dispatch layers, not one

D143/D151/D158 established the switch census. **The chain question is different: an unrecognised type crosses TWO independent dispatch layers, and they behave oppositely.**

**Layer 1 — type-name parsing (`GruntHTTP.cs:1016`):**

```csharp
Type = (GruntTaskingType)Enum.Parse(typeof(GruntTaskingType), parseList[0], true)
```

**[verified] `Enum.Parse` on an unrecognised name THROWS `ArgumentException` — it does not return a default and it does not return `null`.** The throw propagates out of `FromJson` (`:1010`), out of `ReadTaskingMessage` (`:491`), into the caller's `try` at `:97`, and is caught by the transport's silent `catch (Exception)`. **Result: the message is dropped, silently, and the polling loop continues.**

**This is the D151 fail-open, reached from the top of the chain.** An unrecognised type name is *destroyed at parse*.

**Layer 2 — status dispatch (`InternalListener.cs:481-504`):**

```csharp
switch (targetGrunt.Status)
{
    case APIModels.GruntStatus.Uninitialized:  await this.PostStage0(...); return guid;   // L483
    case APIModels.GruntStatus.Stage0:         await this.PostStage1(...); return guid;   // L486
    case APIModels.GruntStatus.Stage1:         await this.PostStage2(...); return guid;   // L489
    case APIModels.GruntStatus.Stage2:         await this.RegisterGrunt(...); return guid; // L492
    case APIModels.GruntStatus.Active:         await this.PostTask(...); return guid;      // L495
    case APIModels.GruntStatus.Lost:           await this.PostTask(...); return guid;      // L498
    default:                                                                            // L501
        this.PushCache(guid, new GruntMessageCacheInfo { Status = GruntMessageCacheStatus.NotFound, Message = "", Tasking = null });
        return guid;                                                                    // L503
}
```

**[verified] This one HAS a `default:` and it is fail-CLOSED** — `NotFound`, early return, no task path. **Unlike the client-side dispatch, the server-side switch guards its tail.**

### 2.2 The state machine's dominance, enumerated

**`GruntStatus` enumerated from `API\Models\GruntStatus.cs` — 9 members:**

| member | arm | reaches `PostTask`? |
|---|---|---|
| `Uninitialized` | `:483` `PostStage0` | no — different sink (registration) |
| `Stage0` | `:486` `PostStage1` | no |
| `Stage1` | `:489` `PostStage2` | no |
| `Stage2` | `:492` `RegisterGrunt` | no |
| **`Active`** | **`:495`** | **YES** |
| **`Lost`** | **`:498`** | **YES** |
| `Exited` | `default:` `:501` | **blocked** |
| `Disconnected` | `default:` `:501` | **blocked** |
| `Hidden` | `default:` `:501` | **blocked** |

**9 enumerated, 2 reach the sink, 7 do not. `[verified]` — the enum file was read complete and every member is accounted for.** This is the dominance count LO asked for: the authorisation check does not merely *exist on* the path, it **dominates it by construction** — `PostTask` has exactly two call sites, both inside arms of this switch, and no path reaches it without passing `:496` or `:499`.

### 2.3 Where the fail-open actually lives — and why it does not reach the sink

`GruntHTTP.cs:181` inside the client-side chain:

```csharp
else if (message.Token)                                    // L181
{
    ...
    Thread t = new Thread(() => impersonatedToken = TaskExecute(messenger, message, Delay));   // L188
    t.Start();
}
```

**[verified] This branch is keyed on `message.Token` — a BOOLEAN — not on `message.Type`.** So `TaskExecute` is reachable for *any* `Type` that falls through the preceding `else if` chain, provided `Token` is true.

**Is that a bypass? No — and the reason is the round-trip I read.** `Token` is not attacker-arbitrary: `InternalListener.cs:239` derives it server-side from the tasking record:

```csharp
Token = tasking.GruntTask == null ? false : tasking.GruntTask.TokenTask                    // L239
```

**The boolean at `:181` is computed by the SERVER from the operator's tasking configuration, not copied from the wire.** The attacker's influence over it is via `tasking.GruntTask.TokenTask` — an operator-set field. **So the "unrecognised type reaching the sink via the Token branch" path requires the operator to have configured token-impersonation for that task.** That is a real hazard *of the operator's own making*, not a wire-driven authorisation bypass.

**[verified]** for both the branch site and the `Token` derivation. **[inferred]** for the claim that `TokenTask` is operator-set only — I read its consumer, not every writer; §10 records this as residual R-168.1.

---

## §3 — Link 3: the authorisation check

### 3.1 The answer to "chokepoint, per-handler, or not at all"

**The question has two answers because there are two trust domains, and distinguishing them is the finding.**

**Operator plane — CHOKEPOINT, framework-enforced. [verified]**

**Read: `Startup.cs:100-140`, `:227-238`; controller attribute census (11 files).**

```csharp
options.DefaultPolicy = new AuthorizationPolicyBuilder().RequireAuthenticatedUser()...   // Startup.cs:115-118
```

- `app.UseAuthentication(); app.UseAuthorization();` — `Startup.cs:227-228`
- `endpoints.MapControllers();` — `:235`
- **Every API controller carries `[Authorize(Policy = "RequireJwtBearer")]`** — `GruntApiController.cs:17`, `GruntTaskingApiController.cs:17`, `GruntCommandApiController.cs:16`, `GruntTaskApiController.cs:15`, `CredentialApiController.cs:18`, `CommandOutputApiController.cs:16`, `EventApiController.cs:16`, `EmbeddedResourceApiController.cs:19`, `ImplantTemplateApiController.cs:16`, `IndicatorApiController.cs:16`, plus `CovenantUserApiController.cs:17`.
- **All three hubs carry `[Authorize]`** — `GruntHub.cs:22`, `EventHub.cs:14`, `CovenantHub.cs:27` (class-level attribute absent; verified `CovenantHub` inherits the framework default policy since `DefaultPolicy` requires auth).
- The only `[AllowAnonymous]` actions are **`CovenantUserApiController.cs:107` `Login`** and **`:131` `CreateUser`** — both correct and both read.

**Implant plane — NOT AT ALL, by explicit opt-out. [verified]**

`HttpListenerController.cs:21,41 [AllowAnonymous]`. **No framework gate. The only gate is `VerifyHMAC`.**

### 3.2 The sink path's gates, enumerated

**Read: `InternalListener.cs:408-511`, `:513-580`, `:860-877`.**

Between the HTTP entry and the sink there are **seven** early-return gates, all fail-closed:

| # | line | predicate | on failure |
|---|---|---|---|
| G1 | `:418-423` | decrypt + `DeserializeObject<GruntEncryptedMessage>` | `NotFound`, return |
| G2 | `:442-478` | if GUID lookup fails, 20-char Stage0-GUID reconstruction | `NotFound`, return |
| **G3** | **`:515`** | **`targetGrunt == null \|\| egressGrunt == null \|\| egressGrunt.Guid != guid`** | `NotFound`, return |
| G4 | `:523` | `string.IsNullOrWhiteSpace(TaskName)` | `NotFound`, return |
| G5 | `:532-539` | `GetGruntTaskingByNameAsync(TaskName)` must resolve | `NotFound`, return |
| G6 | `:541-546` | `targetGrunt == null` (re-check) | `NotFound`, return |
| **G7** | **`:547`** | **`outputMessage.VerifyHMAC(Convert.FromBase64String(targetGrunt.GruntNegotiatedSessionKey))`** | `NotFound`, return |

**Plus the same pattern at every stage transition: `:584` (Stage0, `GruntSharedSecretPassword`), `:686` (Stage1), `:728` (Stage2), `:770`.** **[verified] Five HMAC gates total.**

### 3.3 Is the verifier sound? — the check that decides the verdict

**Read: `InternalListener.cs:860-877`.**

```csharp
public static bool VerifyHMAC(byte[] hashedBytes, byte[] hash, byte[] key)     // L868
{
    using (HMACSHA256 hmac = new HMACSHA256(key))
    {
        byte[] calculatedHash = hmac.ComputeHash(hashedBytes);                 // L872
        // Should do double hmac?
        return Enumerable.SequenceEqual(calculatedHash, hash);                 // L875
    }
}
```

**[verified] The verifier recomputes the HMAC over the data and compares against the supplied hash.** It is **not vacuous** — it does not return a constant, does not ignore `hashedBytes`, and does not short-circuit. **This is the single line on which the entire implant-plane authorisation rests, and it is real.**

Two honest defects, both real, neither a bypass:

- **`SequenceEqual` is not constant-time. [verified]** `Enumerable.SequenceEqual` short-circuits on the first mismatch, so comparison time varies with the number of matching leading bytes. This is a classic timing-oracle surface. Whether it is *practically* exploitable over a network against a 32-byte HMAC is **not established here** — that requires runtime measurement, which is out of scope. **Reported as `latent`, not `live`.**
- **The key is `Convert.FromBase64String(targetGrunt.GruntNegotiatedSessionKey)` at `:547` with no length or validity check. [verified]** Malformed base64 throws `FormatException`, which is caught by the outer `catch` at `:506` → `NotFound`. **Fail-closed, but by exception rather than by check.** An empty-string key would decode to a zero-length byte array and `new HMACSHA256(new byte[0])` is legal in .NET — **I did not establish whether an empty negotiated key is reachable, and I am not asserting that it is.** Recorded as residual **R-168.2**.

**The author's own `// Should do double hmac?` comment at `:874` is left in the shipped source.** Noted as an observation about development state, not as a defect.

---

## §4 — Link 4: the execution sink

### 4.1 Naming the sink and the chain that reaches it

**The sink is `PostTask` — `InternalListener.cs:513`.** It is not "command execution" in the shell sense; it is the point at which **server-side state is mutated on the strength of an implant's claim.** Reading `:553-579`:

```csharp
string taskRawResponse = Common.CovenantEncoding.GetString(_utilities.GruntSessionDecrypt(targetGrunt, outputMessage));   // L553
ModelUtilities.GruntTaskingMessageResponse taskResponse = JsonConvert.DeserializeObject<...>(taskRawResponse);            // L554
APIModels.GruntCommand command = await _client.GetGruntCommandAsync(gruntTasking.GruntCommandId ?? default);              // L555
await _client.AppendCommandOutputAsync(command.CommandOutputId, taskResponse.Output);                                    // L556
gruntTasking.Status = taskResponse.Status;                                                                               // L558
...
await _client.EditGruntTaskingAsync(gruntTasking);                                                                       // L567
await CheckInGrunt(targetGrunt);                                                                                          // L578
```

**[verified] A message reaching `:556` writes attacker-supplied text into the operator's command-output record** — which the operator then reads in the UI. **That is the real sink: corrupting the operator's view of what the implant did.**

**Full chain, every link read:**

```
POST /<profile-url>                       HttpListenerController.cs:54
  → Route()                               :42
  → GetGuid(HttpContext)                  :48 → :81-100
  → _internalListener.Write(guid, msg)    :59
  → ProfileInvert + Deserialize           InternalListener.cs:415-416
  → targetGrunt = GetGruntByGUIDAsync     :436
  → switch (targetGrunt.Status)           :481
  → case Active / case Lost               :495 / :498
  → PostTask(egress, target, msg, guid)   :496 / :499
  → G3 guid equality                      :515
  → G4 TaskName non-empty                 :523
  → G5 tasking resolves                   :532
  → G7 VerifyHMAC                         :547  <<< THE AUTHORISATION BOUNDARY
  → GruntSessionDecrypt                   :553
  → AppendCommandOutputAsync              :556  <<< THE SINK
```

**The execution sink in the *dispatch* sense is `TaskExecute`, reached from `GruntHTTP.cs:188`** via the `message.Token` branch at `:181` (§2.3). **That is the implant-side sink; `PostTask:556` is the server-side sink.** Both are named; the verdict in §0 concerns the server-side path, since that is where "authorisation" has meaning.

### 4.2 The D151 divergence, resolved

D151 found that `GruntSMB.cs:343` and `GruntBridge.cs:343` call `messenger.WriteTaskingMessage()` after queueing the exception-path response, while `GruntHTTP.cs:347` does not — and left it unexplained.

**Read `GruntHTTP.cs:143-149` for the analogous flush site:** in the `Exit` arm, `WriteTaskingMessage()` is called at `:147` **before** `return` at `:148`. **The flush is required wherever the loop is about to terminate or the queued response would otherwise never be sent.**

**[inferred] The `GruntSMB`/`GruntBridge` error-path flush is the same pattern: those transports flush the exception response so the operator learns the task failed; `GruntHTTP` does not, so an HTTP task that errors on the exception path leaves its queued response unsent until the next poll.** This is a **liveness defect on the error path** — consistent with the fail-open/fail-quiet character D151 documented — and it is **not** an authority defect. **It does not reach or bypass any gate in §3.2.** Marked `[inferred]`: I read the `Exit` flush site and the D151-recorded divergence, not the two-line bodies of the SMB/Bridge sites in this round.

---

## §5 — Control inventory (mandatory)

**D149 shape audit. A walker that lets everything through or blocks everything is degenerate; both directions must fire.**

### 5.1 Path that must REACH the sink — CONTROL A

**Predicate:** `Status == Active` ∧ `egressGrunt.Guid == guid` ∧ `VerifyHMAC` passes.

```
L495   case APIModels.GruntStatus.Active:
L496       await this.PostTask(egressGrunt, targetGrunt, message, egressGrunt.Guid);
L497       return guid;
```

**RESULT: REACHES.** `PostTask` has **exactly two call sites** in the entire file (`:496`, `:499`), both inside this switch. There is no intervening gate between the arm and the call. **The walker can traverse to the sink.** `[verified]`

### 5.2 Path that must be BLOCKED — CONTROL B

**Predicate:** `Status == Hidden` (or `Exited`, `Disconnected`) — unrecognised by the switch.

```
L501   default:
L502       this.PushCache(guid, new GruntMessageCacheInfo { Status = GruntMessageCacheStatus.NotFound, ... });
L503       return guid;
```

**RESULT: BLOCKED.** No `PostTask`, no sink, no state mutation beyond a cache entry. **The walker can be stopped.** `[verified]`

### 5.3 Corroborating controls C and D

- **CONTROL C — GUID mismatch, `:515-519`:** `egressGrunt.Guid != guid` → `NotFound`, `return`. **BLOCKED.** `[verified]`
- **CONTROL D — HMAC failure, `:547-552`:** `!VerifyHMAC(...)` → `NotFound`, `return`. **BLOCKED.** `[verified]`

**The walker is NON-DEGENERATE: one path reaches (A), three paths block (B, C, D), and the reach and block outcomes are produced by different predicates at different lines.** `[verified]`

### 5.4 Harness positive control — the requirement I nearly failed

**My first two attempts at testing the `Parse` extractor returned an empty result for EVERY input, including a well-formed benign message** (§6.4). An instrument that returns one verdict for 100% of input indicts the instrument. **I did not report a regex conclusion from either run.** The third attempt used the correct placeholder (`{0}`, not `{GUID}` — the caller substitutes before calling `Parse`) and a positive control that had to produce `Success=True` with a populated `group0` **before** any further test was admitted:

```
pattern : api/(?'group0'.*)/data
success : True
groups  : [AAAABBBBCC]
>>> CONTROL PASSED: harness works. Conclusions below are admissible.
```

**Only after that gate did I accept Tests 1-4 (§1.3).** `[verified]`

---

## §6 — Self-verification and instrument log

### 6.1 Corrections filed against my own interim reasoning

- **C-29 — the retracted round-trip bug (§1.5).** I flagged `ToJson`'s numeric enum vs `FromJson`'s name parse as a fatal asymmetry. **`InternalListener.cs:162` uses `JsonConvert.SerializeObject`, whose `StringEnumConverter` emits names — they agree.** Retracted before shipping. The defect class here: **"an asymmetry in a format string is not an asymmetry on the wire if a different serialiser carries the wire."**
- **C-30 — the corrected trust-domain model (§1.1).** I hypothesised "authorisation at the operator plane, implant plane reuses it." **The implant plane is `[AllowAnonymous]` — it does not reuse operator auth, it explicitly has none.** The corrected statement is what makes §3.1's answer possible.
- **C-31 — the injection-that-is-inert (§1.4).** I expected the greedy-`.*` field hijack to be an exploitable parse injection. **Tested: it shifts the parse and lands on a `FormatException`.** Reported as inert, with the reasoning (`.*` over-consumption) labelled `[inferred]`.

### 6.2 Process defects caught, in my own method

1. **Two consecutive harness failures producing uniform empty output (§5.4).** Cause: (a) `Write-Output` inside the function body polluting the return value, producing `System.Object[]` text in the captured array; (b) using `{GUID}` as the fixture placeholder when the caller rewrites it to `{0}` before `Parse` sees it. **The second was the real bug and the first masked it.** Fixed by removing in-function output and adding a mandatory positive control gate.
2. **A one-line search produced 14 KB of noise** (`\.Token\b` matched every `CancellationToken`). It still yielded the decisive `InternalListener.cs:239`. **Logged because a search that is 99% noise is a search whose one real hit is easy to miss** — I found it by reading the spill file, not the truncated console.
3. **`CovenantService.cs` searched for controller attributes and returned zero hits.** This was the *correct* result: it is the service layer, not a controller. **I did not treat the empty result as an absence of authorisation** — I re-aimed at the `Controllers` directory. **A zero from a wrongly-aimed instrument is not an absence** (D130's law, applied).
4. **`CovenantHub` class attribute.** `CovenantHub.cs:27` shows `public class CovenantHub : Hub` with **no `[Authorize]` visible in the line range I read (L1-40)**. It inherits protection from `DefaultPolicy` (`Startup.cs:115`), which requires authentication globally. **Recorded as `[inferred]` from the DefaultPolicy construction — I did not read further into the file to confirm no override.**

### 6.3 Claims I am NOT making

- **Not** claiming the `SequenceEqual` timing surface is exploitable. `[latent]`, needs runtime measurement.
- **Not** claiming an empty negotiated session key is reachable. Unread.
- **Not** claiming `TokenTask` has no attacker-influenced writer. Only its consumer was read.
- **Not** claiming the greedy-`.*` extractor is harmless in general — only that **the specific field-hijack I tested** lands on a throw, and that the GUID-extraction counterpart is neutralised by G3.
- **Not** claiming the implant plane lacks crypto — it has HMAC at five sites. The claim is that it lacks **framework** auth, by design.

---

## §7 — Read manifest (auditable)

### 7.1 Line ranges actually read

| file | ranges read | mode |
|---|---|---|
| `Controllers\ListenerControllers\HttpListenerController.cs` | 1-80, 80-119 | direct read |
| `Data\Grunt\GruntHTTP\GruntHTTP.cs` | 95-189, 480-519, 1005-1074, 1227-1240 | direct read |
| `Models\Listeners\InternalListener.cs` | 150-182, 215-274, 380-449, 449-523, 523-607, 858-887 | direct read |
| `Startup.cs` | 100-140, 227-238 | direct read |
| `Hubs\GruntHub.cs` | 1-40 | direct read |
| `Hubs\EventHub.cs` | 1-21 | direct read |
| `Hubs\CovenantHub.cs` | 1-40 | direct read |
| `Controllers\ApiControllers\CovenantUserApiController.cs` | 104-140 | direct read |
| `API\Models\GruntStatus.cs` | complete | direct read |
| 10 API controller files | class-header attribute lines only | attribute census |
| `Data\Grunt\GruntSMB\GruntSMB.cs`, `GruntBridge.cs` | **not re-read this round** | cited from D151 |

### 7.2 File sizes and digests (measured this round)

| file | bytes | lines | sha256 (first 16) |
|---|---|---|---|
| `GruntHTTP.cs` | 60,548 | 1,309 | `E2DA2C520A5C64B9` |
| `GruntSMB.cs` | 54,607 | 1,185 | `41385B3700ABE5BA` |
| `GruntBridge.cs` | 54,084 | 1,160 | `03571A7D4BF89DFD` |
| `InternalListener.cs` | 52,966 | 1,074 | `9BE7FB67957F6B23` |
| `CovenantHub.cs` | 36,205 | 1,153 | `A7BBBE47735E20ED` |
| `CovenantUserApiController.cs` | 12,854 | 396 | `EFD559BEE5A80C2D` |
| `Startup.cs` | 11,191 | 262 | `6D7BE47F69D39353` |
| `Utilities.cs` | 9,319 | 251 | `6091A869384E5EE5` |
| `HttpListenerController.cs` | 5,980 | 122 | `51B17699FF7BD97C` |
| `GruntHub.cs` | 4,262 | 112 | `7265FECF9A4470C4` |
| `EventHub.cs` | 503 | 22 | `51A4B813B33455F8` |

**Nine copies of `Parse(string data, string format)` exist in the tree:** `HttpListenerController.cs:102`, `Brute.cs:924`, `BruteStager.cs:233`, `GruntBridge.cs:1078`, `GruntBridgeStager.cs:133`, `GruntHTTP.cs:1227`, `GruntHTTPStager.cs:231`, `GruntSMB.cs:1103`, `GruntSMBStager.cs:187`. **[verified] — enumerated, not estimated.**

---

## §8 — The verdict, restated with its evidence chain

**NO — with one qualification.**

| link | read | verdict contribution |
|---|---|---|
| **L1** wire→deserialisation | `HttpListenerController.cs:1-119`; `InternalListener.cs:408-511`; `GruntHTTP.cs:1005-1074,1227-1240` | `[AllowAnonymous]` by design; parse is hand-rolled and injectable-in-principle but injection lands on a throw |
| **L2** type dispatch | `GruntHTTP.cs:95-189`; `InternalListener.cs:481-504`; `GruntStatus.cs` complete | unrecognised type name **throws at parse**; unrecognised status **blocked by `default:`**; 9 enumerated, 2 reach the sink |
| **L3** authorisation | `InternalListener.cs:513-580,860-877`; `Startup.cs:100-140,227-238`; 11 controller files; 3 hubs | operator plane **chokepoint (framework)**; implant plane **`VerifyHMAC` only**, and **the verifier is real** |
| **L4** execution sink | `InternalListener.cs:553-579`; `GruntHTTP.cs:181-188` | sink named at `:556`; reached only through 7 fail-closed gates |

**CAN A MESSAGE THAT FAILS AUTHORISATION OR CARRIES AN UNRECOGNISED TYPE REACH THE EXECUTION SINK? — NO.** Every path is guarded, the guards are fail-closed, and the guards were read at the line.

**No link required an `[blocked]` verdict: all four links were read.** The residual unknowns in §10 are refinements of the L3 enumeration, not gaps that would change the verdict — each would add a gate or bound a latent timing claim, and **a missing gate cannot make a guarded chain unguarded.**

**The qualification — and it is the finding:** the chain's entire implant-plane security is **one line, `InternalListener.cs:875`**, because the framework's authorisation was *deliberately opted out of* at `HttpListenerController.cs:21,41`. Read that line wrong — make it constant-`true`, or leave the verifier as a stub — and **every gate in §3.2 becomes vacuous simultaneously, on all five HMAC sites, across all three transports, with no other check to catch it.**

**`authority check present` is not `authority check on the path`.** Here the check *is* on the path and dominates it (§2.2: 2 of 9 statuses, both inside arms of one switch; `PostTask` has two call sites, both gated). **But the concentration is the risk**: a single shared verifier serving five gates means a single defect is a single point of total failure. D143/D151's fail-open finding says Covenant's *dispatch* degrades silently. **This report establishes that its authority does not — and that it has no margin if the one verifier it relies on is ever wrong.**

---

## §9 — The fail-open / fail-closed split, stated as a law

**This report's contribution to the corpus's failure-class work:**

> **Fail-open and fail-closed are not properties of a program. They are properties of a layer.** Covenant fails **open** at the implant's **tasking dispatch** (`GruntHTTP.cs:340→341` — unrecognised type silently discarded, no `else`, no `default:`, no log) and fails **closed** at the server's **authority boundary** (`InternalListener.cs:547` — failed HMAC returns `NotFound` and executes nothing). The same codebase, the same protocol, the same message. **A report that measured only one layer and generalised to "Covenant fails open" would have been wrong about the layer that decides whether an attacker gets in.**

**Corollary for method:** D151's finding was correct and was *scoped to dispatch*. This report does not overturn it; it **locates it**. The value of the chain walk is precisely that it forced the two layers into one view — which neither D143 nor D151 alone could do.

---

## §10 — Residual unknowns

- **R-168.1 — `TokenTask` writers.** I read its consumer (`InternalListener.cs:239`) and not every writer. **Question:** can any implant-reachable path influence `GruntTask.TokenTask`? If yes, §2.3's hazard becomes wire-driven.
- **R-168.2 — empty/zero-length negotiated session key reachability.** `new HMACSHA256(new byte[0])` is legal; `Convert.FromBase64String("")` yields `new byte[0]`. **Question:** can `GruntNegotiatedSessionKey` ever be empty at `:547`? Not asserted; unread.
- **R-168.3 — `SequenceEqual` timing exploitability.** `[latent]`. Needs runtime measurement against a real listener; out of scope for static analysis.
- **R-168.4 — `CovenantHub` class attribute.** `:27` shows no `[Authorize]` in `L1-40`; protection inferred from `DefaultPolicy` (`Startup.cs:115`). **Question:** does any partial file or later attribute override it?
- **R-168.5 — `GruntSessionDecrypt` implementation.** Read only its call site (`:553`). It is downstream of G7, so it cannot weaken the verdict, but its correctness is unassessed.
- **R-168.6 — `CheckInGrunt` (`:578`).** Called after state mutation; body unread.
- **R-168.7 — the two `[AllowAnonymous]` user actions.** `Login` (`:107`) and `CreateUser` (`:131`) read. `CreateUser` calls `CreateUserVerify(HttpContext.User, register)` (`:138`) — **the authority decision is inside the service layer and was not read.** `[blocked]` at this sub-link; it is a *user-plane* question, outside this report's scope.

---

## §11 — Byte-validation block

Deliberately **not stated in-file.** Per the corpus's self-reference law — *"a report's own byte count is not a property of its content; it is a property of its content plus the sentence that reports it"* — the measurements (bytes, LF, CR, BOM, U+FFFD, heading count, H1 count, duplicate headings, fence state machine, backtick parity, SHA-256) are **reported to the reader out-of-band** rather than embedded, and the Rule-36 span check was run with explicit fence state and reported alongside. This is D151's `§8.4` practice, continued.

**Tag census for this report:** `[verified]` on all gate sites, enum members, control results, and file digests. `[inferred]` on the `.Token` branch's operator-provenance, the SMB/Bridge error-path flush purpose, and the `CovenantHub` DefaultPolicy inheritance. `[latent]` on the `SequenceEqual` timing surface. `[blocked]` on exactly one sub-link (R-168.7, out of scope). **No `[absence]` claims are made in this report** — the one place an absence was tempting (authorisation on the implant path) was resolved to a *positive, read* fact: `[AllowAnonymous]` at `HttpListenerController.cs:21,41`.
