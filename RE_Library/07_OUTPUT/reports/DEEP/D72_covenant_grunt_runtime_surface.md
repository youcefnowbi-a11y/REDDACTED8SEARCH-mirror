# D72 — Covenant grunt runtime surface: the Brute token defect taken to ground truth

**Targets:** `Covenant/Data/Grunt/{Brute,GruntBridge,GruntHTTP,GruntSMB}/*.cs` (8 files, 268,749 B) · `Covenant/Data/Tasks/SharpSploit.Credentials.yaml` · `Covenant/Models/Listeners/InternalListener.cs` · `Covenant/Core/CovenantService.cs` · `Covenant/API/Models/GruntTask.cs`
**Method:** pure source; no provider, no build, no execution. **Scripts written to files, never inline.** Comments stripped before every classification. Paths **enumerated, never constructed**. Every number carries its invocation and its denominator.
**Write scope:** this file only. D40/D46/D50/D52/D57/D60 unmodified.

---

## 0. Corrections and the lead

### 0.1 **CORRECTION 1 — D60 understated the `Brute` thread-state defect. It is not one divergence; it is an internally inconsistent pair, and it produces a HARD FAILURE, not just invisibility.**

**D60 §1.4 reported `Brute` uses `ThreadState.Running` where its three siblings use `IsAlive`.** **That was correct but incomplete. Measured now:**

| Site | Brute | GruntBridge | GruntHTTP | GruntSMB |
|---|---|---|---|---|
| `Tasks` list-empty check | `:137` **`ThreadState.Running`** | `:146` `IsAlive` | `:152` `IsAlive` | `:146` `IsAlive` |
| `Tasks` enumeration | `:142` **`ThreadState.Running`** | `:151` `IsAlive` | `:157` `IsAlive` | `:151` `IsAlive` |
| `TaskKill` match | `:148` **`ThreadState.Running`** | `:157` `IsAlive` | `:163` `IsAlive` | `:157` `IsAlive` |
| match consumed | `:155` `matched.First()` | `:164` `matched.First()` | `:170` `matched.First()` | `:164` `matched.First()` |
| `Abort()` | `:156` | `:165` | `:171` | `:165` |
| **post-abort liveness** | **`:158` `IsAlive`** | `:167` `IsAlive` | `:173` `IsAlive` | `:167` `IsAlive` |
| `Suspend()` | `:160` | `:169` | `:175` | `:169` |

**`Brute.cs:155-160` uses `ThreadState.Running` to FIND a task and `IsAlive` to KILL it — the two predicates disagree inside the same three-line block.** **No sibling does this.** The other three are internally consistent.

**And the consequence is a hard failure, not silence:** `matched.First()` (`Brute:155`) throws `InvalidOperationException` when the match set is empty. **A task that is `WaitSleepJoin`-blocked is excluded by `ThreadState.Running` at `:148`, so `First()` throws** — inside the loop's `try`, caught at `Brute.cs:188` `catch (Exception e)` → increments `ConnectAttemptCount` and writes to stderr. **The operator sees a failed kill; the task survives.** **`Tasks` (`:137`) can likewise report `"No active tasks!"` while tasks are running.**

**This correction RAISES D60's severity for this item.** `[source: 7 predicate sites per family, all printed; `First()` call sites enumerated per family]`

### 0.2 **CORRECTION 2 — D60 implied the family contradiction might express through the placeholders. It does not. The placeholders resolve correctly; the contradiction is LATENT.**

**D60 §2.1 said `Brute`'s placeholder set declares it an HTTP family while its `TaskExecute` disagrees.** **True. But Q3 asked what happens when an HTTP placeholder is used on `Brute`, and the answer is: nothing bad — `Brute` has the full HTTP `Profile` machinery and the server substitutes the HTTP template.** **The contradiction does not surface through the placeholders at all.** It is a **marker** of a mis-grouping whose only *expressed* symptom is the `TokenTask` dead branch. **§3 states this precisely.**

### 0.3 The lead — Q1's severity answer is **silent failure**, and here is why it is not a no-op

**§1 proves it:** the five assemblies call `SharpSploit.Credentials.Tokens` methods whose contract is impersonation **on the calling thread**, and `SharpSploit` source is **not vendored in this corpus** — so the dependency is established from the task bodies plus the server-side flag semantics, **not from reading `Tokens.cs`.** **§1.4 states exactly what that costs.**

---

## 1. Q1 — what the five token tasks actually do on `Brute`

### 1.1 The five tasks are `TaskingType: Assembly`, all in one file

**Denominator: `Data\Tasks\` enumerated = 19 files.** The five live in **`SharpSploit.Credentials.yaml`** (49,455 B):

| Task | Line | `TaskingType` | `TokenTask` |
|---|---:|---|---|
| `MakeToken` | **1** | Assembly | **true** |
| `GetSystem` | **139** | Assembly | **true** |
| `ImpersonateProcess` | **232** | Assembly | **true** |
| `ImpersonateUser` | **334** | Assembly | **true** |
| `RevertToSelf` | **661** | Assembly | **true** |

`[source: per-task `Name:` search across 19 enumerated files; line numbers printed]`

### 1.2 **The `Token` flag is a SERVER-SIDE declaration — traced end to end**

**`TokenTask` = 10 hits across 152 Covenant `.cs` files. Every one is server/launcher side:**

| Site | Role |
|---|---|
| `API\Models\GruntTask.cs:32` | ctor parameter `bool? tokenTask` |
| `API\Models\GruntTask.cs:50` | `TokenTask = tokenTask;` |
| `API\Models\GruntTask.cs:146-147` | `[JsonProperty(PropertyName = "tokenTask")] public bool? TokenTask { get; set; }` |
| `Core\CovenantService.cs:2292` | `updatingTask.TokenTask = task.TokenTask;` |
| `Models\Grunts\GruntTask.cs` | **ZERO hits** — the grunt-side model does not carry the concept |

**And the single consumption site that puts it on the wire — `Models\Listeners\InternalListener.cs:239`, verbatim:**

```csharp
Token = tasking.GruntTask == null ? false : tasking.GruntTask.TokenTask
```

**So: the server declares "this task's assembly expects impersonation," puts `Token: true` in the `GruntTaskingMessage`, and the grunt is expected to apply it.** `GruntTaskingMessage` carries `{Type, Name, Message, Token}` (D57 §2.3). **The grunt-side implementation of that expectation is the `message.Token` branch — which on `Brute` is the dead branch D60 §1.3 proved.**

### 1.3 **What the assemblies do — read verbatim from the task bodies**

**`MakeToken` (`:13-48`)** — the clearest case, because its own return string states the contract:

```csharp
using (Tokens t = new Tokens())
{
    Win32.Advapi32.LOGON_TYPE lt = ...;                       // :27  LogonType resolution
    if (t.MakeToken(Username, Domain, Password, lt))          // :36  IMPERSONATES
    {
        return "Successfully made and impersonated token for user: " + Domain + "\\" + Username;
    }
    else { return "Failed to make token for user: " + ...; }
}
```

**Its `Description` (`:3`), verbatim:** *"Makes a new token with a specified username and password, and **impersonates it to conduct future actions as the specified user**."*

**`GetSystem` (`:139`)** — *"Impersonate the SYSTEM user. Equates to ImpersonateUser("NT AUTHORITY\SYSTEM")."* (`:141`), body `using (Tokens t = new Tokens())` (`:161`).

**`ImpersonateProcess` (`:232`)**, **`ImpersonateUser` (`:334`)**, **`RevertToSelf` (`:661`)** — same shape; `RevertToSelf`'s `Options: []` at `:702` confirms it takes no parameters and is a pure thread-state operation.

**Every one is `Tokens t = new Tokens()` followed by a `t.<Method>(...)` call.** The assemblies are **thin wrappers**: they construct the SharpSploit `Tokens` object, call one method, and format a string.

### 1.4 **VERDICT: SILENT FAILURE, not a no-op — and the reasoning is stated so it can be falsified**

**The assemblies are NOT self-contained.** Three independent lines of evidence:

1. **The contract is thread-scoped, not object-scoped.** `MakeToken` returns *"Successfully made **and impersonated**"* — the impersonation is a side effect on the **calling thread**, and the description says **"to conduct future actions as the specified user."** **"Future actions" are the host process's actions, not the assembly's.** A self-contained assembly would have nothing to say about future actions.
2. **`RevertToSelf` exists as a separate `TokenTask: true` task (`:661`) with zero parameters (`:702`).** A task whose entire purpose is to *undo* an impersonation is meaningless unless the impersonation persists **on the host thread past the assembly's return.** **It persisting is the whole design.**
3. **The grunt-side `message.Token` branch on the three working families exists to apply a token the assembly produced and then LEFT APPLIED** — `GruntHTTP:187-197` captures `TaskExecute`'s `IntPtr` return and calls `WindowsIdentity(impersonatedToken).Impersonate()`. **If the assemblies were self-contained, that entire branch would be redundant on `GruntHTTP`/`GruntSMB`/`GruntBridge` too.** It is not redundant; it is the mechanism.

**Therefore on `Brute`:** the task executes, `Tokens.MakeToken` may succeed, the assembly returns `"Successfully made and impersonated token for user: ..."`, `TaskExecute` returns `void`, the token is dropped, **the success string is queued to the server as `GruntTaskingStatus.Completed`, and the grunt is still running as its original identity.**

**The operator reads "Successfully made and impersonated token for user: DOMAIN\user" and the impersonation did not happen. That is the defect: a false positive reported by the tool's own success message.**

**What would falsify this:** reading `SharpSploit\SharpSploit\Credentials\Tokens.cs` and finding that `MakeToken` spawns a thread or otherwise impersonates outside the caller. **That source is not in this corpus (§1.5), so this is the strongest available reading, not a closed loop.**

### 1.5 **The residual that bounds Q1 — `SharpSploit` source is NOT VENDORED**

**Positive control first:** the probe finds `.cs` files by name throughout the Covenant tree (152 excl obj/bin). **Then, for `Tokens.cs` / a `SharpSploit` directory: the task YAMLs reference `SharpSploit\SharpSploit\` as a `ReferenceSourceLibraries` **`Location:`** — and enumerating `01_SOURCE_c2` for a `SharpSploit` directory returns nothing.** **The library is an external build-time dependency, resolved at compile time by the launcher, not shipped in this tree.**

**Consequence, stated plainly:** **§1.4's verdict rests on the task bodies, the `TokenTask` semantics at `InternalListener.cs:239`, and the three siblings' `Impersonate()` branches — not on `Tokens.cs`.** **If the delegating lane wants Q1 closed to certainty rather than to the strongest static reading, the probe is: obtain `SharpSploit`'s `Tokens` implementation and read `MakeToken`/`ImpersonateUser` for a thread-scope side effect (`ImpersonateLoggedOnUser`, `SetThreadToken`, or `WindowsIdentity.Impersonate`).** **The evidence available points one way; I am naming the limit rather than eliding it.**

---

## 2. Q2 — does the encrypted envelope survive the named-pipe path?

### 2.1 **YES. The pipe carries ciphertext. The encrypt call is named.**

**The write chain, `GruntBridge.cs` (identical structure in all four):**

```csharp
public void QueueTaskingMessage(string Message, string Meta = "")     // :476
{
    GruntEncryptedMessage gruntMessage = this.Crafter.Create(Message, Meta);   // :478  <-- ENCRYPT
    string uploaded = this.Profile.FormatWrite(gruntMessage);                  // :479  <-- wrap
    lock (_MessageQueueLock) { this.MessageQueue.Enqueue(uploaded); }          // :480-483
}

public void WriteTaskingMessage()                                     // :486
{
    lock (_UpstreamLock) { lock (_MessageQueueLock) {
        this.UpstreamMessenger.Write(this.MessageQueue.Dequeue());    // :494  <-- TRANSPORT
```

**The encrypt call, `GruntBridge.cs:812` / `GruntSMB.cs:837`, verbatim:**

```csharp
byte[] encryptedMessagePacket = Utilities.AesEncrypt(Message, this.SessionKey.Key);
```

**And the HMAC, `GruntBridge.cs:1030-1031` / `GruntSMB.cs:1055-1056`:**

```csharp
HMACSHA256 SessionHmac = new HMACSHA256(key);
return SessionHmac.ComputeHash(data);
```

**Encryption happens in `Crafter.Create` — ONE LAYER ABOVE the transport.** `WriteTaskingMessage` (`:494`) dequeues a **string that is already the encrypted, formatted envelope** and hands it to `UpstreamMessenger.Write`. **`UpstreamMessenger` is the base messenger in every family** (`Brute:417`, `GruntBridge:426`, `GruntHTTP:456`, `GruntSMB:453`).

**Same transform, same layers, on both paths — the pipe is NOT a raw carrier.** `[source: QueueTaskingMessage/WriteTaskingMessage verbatim; AesEncrypt + HMACSHA256 sites per family; UpstreamMessenger assignment per family]`

### 2.2 **The structural nuance D72 adds — `GruntSMB` and `GruntBridge` are BRIDGES, so the pipe is the DOWNSTREAM leg and the relay forwards the sealed object**

**This is where the `(Grunt, Stager)` pair structure D57 called out becomes load-bearing.**

| Family | Base messenger (`baseMessenger =`) | Downstream messenger |
|---|---|---|
| **Brute** | `:53` `new HttpMessenger(...)` | — |
| **GruntHTTP** | `:67` `new HttpMessenger(...)` | `:548` `new SMBMessenger(Hostname, PipeName)` |
| **GruntSMB** | `:62` `new SMBMessenger(ServerPipe, PipeName)` | `:545` `new SMBMessenger(Hostname, PipeName)` |
| **GruntBridge** | `:61` `new BridgeMessenger(CovenantURI, GUID, ProfileWriteFormat)` | `:518` `new SMBMessenger(Hostname, PipeName)` |

**`GruntSMB`/`GruntBridge` are relays: they hold a pipe **downstream** and forward to child grunts.** The relay path, `GruntBridge.cs:465-472`:**

```csharp
string json = this.Crafter.Retrieve(gruntMessage);                    // :465  AES DECRYPT (own layer)
GruntEncryptedMessage wrappedMessage = GruntEncryptedMessage.FromJson(json);   // :466  still a SEALED envelope
IMessenger relay = this.DownstreamMessengers.FirstOrDefault(DM => DM.Identifier == wrappedMessage.GUID);  // :467
if (relay != null) { relay.Write(this.Profile.FormatRead(wrappedMessage)); }   // :470  writes SEALED object
```

**The relay decrypts its OWN transport layer (`:465`), then re-wraps and writes a `GruntEncryptedMessage` downstream (`:470`) — still sealed, still requiring the session key.** **`FormatRead`/`FormatWrite` (`GruntBridge:388-389`, `GruntSMB:415-416`) format the envelope; they do not unseal it.** **So both pipe legs — upstream relay and downstream child — carry the encrypted envelope.**

### 2.3 **The Q2 conclusion, stated exactly**

**The `WorldSid` `FullControl` pipe ACL (§D60 §3.3) exposes a channel whose payload is AES-CBC encrypted with HMAC over the ciphertext, verified before decryption (D57 §2.2). The crypto layer is intact on the pipe path — the pipe is not a plaintext carrier anywhere in the chain.**

**What that does and does not buy:**

- **Confidentiality and integrity of the payload: YES, present on the pipe path** — same `Utilities.AesEncrypt`/`AesDecrypt` and `HMACSHA256` calls as HTTP.
- **Peer authentication of the CHANNEL: NO.** The envelope proves *someone holding the session key* wrote it. **Everyone on the host can open the pipe (`WorldSid`, §D60 §3.3).** So any local principal can **connect, read ciphertext, and inject ciphertext.**
- **The gap this leaves:** an injected frame is rejected only if it fails HMAC or parse. **A principal that can read the process's memory — or that has read the shared secret from the parent grunt's config/logs — can forge frames.** **The ACL's breadth does not break the crypto; it removes the *second* layer that would have made a leaked key non-fatal.**

**This is a compensating-controls finding, not a crypto break. It is stated that way deliberately.**

---

## 3. Q3 — the family contradiction, taken to consequence

### 3.1 **`Brute` HAS the full HTTP `Profile` machinery — the placeholders resolve and work**

**`Profile` class present in all four families**, with format methods matched to their transport:

| Family | `class Profile` | Format methods | Relay/queue call sites |
|---|---:|---|---|
| **Brute** | **`:362`** | `:378` `FormatGetResponse`, `:379` `FormatPostRequest` | `:462`, `:471` |
| GruntHTTP | `:401` | `:417` `FormatGetResponse`, `:418` `FormatPostRequest` | `:500`, `:509` |
| GruntSMB | `:400` | `:415` `FormatReadFormat`, `:416` `FormatWriteFormat` | `:497`, `:506` |
| GruntBridge | `:373` | `:388` `FormatRead`, `:389` `FormatWrite` | `:470`, `:479` |

**`Brute`'s `Profile` API is `FormatGetResponse`/`FormatPostRequest` — the HTTP naming — identical to `GruntHTTP`'s.** `[source: `class Profile` line per family + all four format call sites, printed]`

### 3.2 The resolution site — `CovenantService.cs`, three templates

**`REPLACE_PROFILE*` = 51 hits across 152 files; the substitution sites are `Core\CovenantService.cs` in three blocks:**

| Block | Lines | Substitutions | Family it targets |
|---|---|---:|---|
| **HTTP template** | **`:1592-1609`** | **18** | HTTP — includes `PROFILE_HTTP_HEADER_NAMES/VALUES/URLS/GET_RESPONSE/POST_REQUEST/POST_RESPONSE`, `VALIDATE_CERT`, `USE_CERT_PINNING`, `COVENANT_URIS`, `COVENANT_CERT_HASH` |
| **Pipe template** | `:1614-1623` | 10 | pipe — `PROFILE_READ_FORMAT`, `PROFILE_WRITE_FORMAT`, `PIPE_NAME`, plus the universal set |
| **Bridge template** | `:1630-1641` | 10 | bridge — `BRIDGE_MESSENGER_CODE`, `COVENANT_URI` (singular) |

**Representative, verbatim:**

```csharp
:1592  .Replace("// {{REPLACE_PROFILE_MESSAGE_TRANSFORM}}", profile.MessageTransform)
:1593  .Replace("{{REPLACE_PROFILE_HTTP_HEADER_NAMES}}", this.FormatForVerbatimString(string.Join(",", httpProfile.HttpHeaderNames...)))
:1597  .Replace("{{REPLACE_PROFILE_HTTP_POST_REQUEST}}", this.FormatForVerbatimString(httpProfile.HttpPostRequest...))
:1599  .Replace("{{REPLACE_VALIDATE_CERT}}", grunt.ValidateCert ? "true" : "false")
:1600  .Replace("{{REPLACE_USE_CERT_PINNING}}", grunt.UseCertPinning ? "true" : "false")
:1601  .Replace("{{REPLACE_PIPE_NAME}}", grunt.SMBPipeName)
```

**Note `:1601` and `:1617` and `:1634`: `{{REPLACE_PIPE_NAME}}` is replaced in the HTTP, pipe, AND bridge templates — but §D60 §2.1 measured it present in `GruntSMB.cs` only (1 hit).** **Covenant substitutes a placeholder the HTTP and bridge sources do not contain — a harmless no-op `Replace`, but it confirms the three templates share a substitution list that is not tailored to each template's actual contents.** `[source: all `.Replace("{{REPLACE_*` sites printed with line numbers]`

### 3.3 **THE ANSWER TO Q3 — neither silent wrong behavior nor hard failure. The contradiction is LATENT.**

**`Brute` is compiled from the HTTP template** (its placeholder census matched `GruntHTTP` 16/16, §D60 §2.1), **it has the HTTP `Profile`, and the server substitutes its placeholders correctly (`CovenantService.cs:1592-1609`).** **`{{REPLACE_PROFILE_HTTP_POST_REQUEST}}` on `Brute` resolves to the real profile value and the code path that consumes it (`Brute.cs:471` `FormatPostRequest`) works.**

**So the placeholders are NOT where the contradiction bites. Nothing in the substitution logic (`CovenantService.cs:1592-1641`) consults `TaskExecute`'s return type or the thread-state predicate.** The template is selected by the **grunt's transport family**, and `Brute` is grouped with HTTP — correctly, because `Brute` *does* speak HTTP (`HttpMessenger`, `:53`).

**The contradiction is therefore structural and LATENT:**

> **`Brute` is an HTTP transport that was forked from `GruntHTTP` but only partially re-typed. Its build identity (template + placeholders + `Profile` API) is HTTP; its runtime dispatch (`TaskExecute` → `void`, `ThreadState.Running`) is a divergent variant. The two paths are reconciled nowhere, and the only place the disagreement is OBSERVABLE is the `TokenTask` branch — because that is the one code path whose correctness depends on `TaskExecute`'s signature.**

**Blast radius, stated:** **the mis-grouping is silent by construction.** An operator cannot detect it from the placeholder layer, the build logs, or the grunt's registration — **the grunt registers and runs normally as an HTTP grunt.** **It is detectable only by running a `TokenTask: true` task against a `Brute` grunt and NOT getting the escalation the success message claims.** **That is the worst place for a defect to live: invisible until precisely the moment it matters.**

---

## 4. Q4 — the thread-state measurement

### 4.1 **`Brute`'s divergence is UNIQUE, and it is worse than D60 reported**

**Full measurement, 7 sites per family (table in §0.1).** **Summary of the discriminating sites:**

| Predicate | Brute | GruntBridge | GruntHTTP | GruntSMB |
|---|---|---|---|---|
| Task liveness — **3 sites each** (`Tasks` empty check, `Tasks` list, `TaskKill` match) | **`ThreadState.Running`** | `IsAlive` | `IsAlive` | `IsAlive` |
| Post-`Abort()` re-check | `IsAlive` | `IsAlive` | `IsAlive` | `IsAlive` |
| `matched.First()` on potentially-empty set | **yes `:155`** | yes `:164` | yes `:170` | yes `:164` |
| Thread creation callback | `void` (`:168`,`:175`) | `IntPtr` (`:182`,`:202`) | `IntPtr` (`:188`,`:208`) | `IntPtr` (`:182`,`:202`) |

**`Brute` is the only family whose liveness predicate differs, and the only family that mixes the two predicates within one operation.** **Blocked-task invisibility is unique to `Brute`. Confirmed as a measurement, not a flag.**

### 4.2 The `First()` parallelism — a shared hazard, correctly scoped

**All four families call `matched.First()` on a `Where(...)` result.** **The `ThreadState.Running` predicate makes `Brute`'s match set empty in strictly more cases than its siblings', so the shared hazard is *more reachable* on `Brute`.** **But `First()`-on-empty is a corpus-wide pattern here, not a `Brute` invention — I am not attributing the exception-throwing idiom to the Brute divergence.** **What is attributable to `Brute` is the widened trigger set.**

**Both `First()` and the `Tasks`/`TaskKill` behaviour sit inside `try` blocks with a broad `catch (Exception e)` that increments `ConnectAttemptCount` (`Brute.cs:188-191`) — so the failure is not a crash, it is a swallowed exception that looks like a connection problem.** `[source: all `ThreadState`/`IsAlive`/`First()`/`Abort()`/`Suspend()`/`catch` sites enumerated per family, printed]`

---

## 5. Residual unknowns, each with a concrete probe

| # | Unknown | Probe |
|---:|---|---|
| 1 | **Whether `SharpSploit.Credentials.Tokens.MakeToken` impersonates on the calling thread** (Q1's closed loop). | **Obtain `SharpSploit`'s `Tokens.cs`** (not in this corpus, §1.5) and check for `ImpersonateLoggedOnUser` / `SetThreadToken` / `WindowsIdentity.Impersonate`. |
| 2 | **Whether any operator path actually builds a `Brute` grunt with a `TokenTask: true` task.** Severity depends on it. | Trace `Data\Launchers\` for the Brute template and cross-reference the task picker's per-family filtering. |
| 3 | **Whether `GruntSMBStager.cs:61`'s `PipeSecurity` is the same `WorldSid` grant.** D60 residual 3, still open. | Read `GruntSMBStager.cs:55-70`. |
| 4 | **Whether `Brute`'s `ThreadState.Running` was ever `IsAlive`** (regression vs. original fork). | No VCS in this tree; `git log -S 'ThreadState.Running'` if a repo is reachable. |
| 5 | **Whether `Brute`'s HTTP template selection is name-based.** §3.3 infers it from the placeholder census. | Read the template-selection switch in `CovenantService.cs` around the three blocks. |

---

## 6. Instrument failures, this report

| # | Failure | Caught by | Effect |
|---:|---|---|---|
| 1 | **A `Select-String 'Location:'` loop matched every reference assembly** (hundreds of `net35\mscorlib.dll` lines), flooding output to a spill file | reading the truncation notice | **none — but the useful result was buried.** Narrowed to the `SharpSploit\SharpSploit\` line explicitly |
| 2 | **`Data\Models\GruntTask.cs` does not exist** — constructed the path instead of enumerating | `DirectoryNotFoundException` | **none — re-enumerated and found TWO `GruntTask.cs` (`API\Models\` and `Models\Grunts\`), which is itself the finding at §1.2: only the API-side model carries `TokenTask`.** **This is D60's shape 15 recurring in the same lane; it was caught by the exception, not by discipline.** |

**Failure 2 is the one to keep: I made the exact error the brief warns about, and only the thrown exception stopped it. The enumeration-first habit needs to be mechanical (enumerate → then filter), not remembered.**

---

## 7. The four answers, consolidated

| Q | Answer |
|---|---|
| **Q1** | **SILENT FAILURE, not a no-op.** The five assemblies are **thin wrappers** around `SharpSploit.Credentials.Tokens`, whose contract is **thread-scoped impersonation** (`MakeToken`'s own description: *"impersonates it to conduct future actions as the specified user"*; `RevertToSelf` exists separately with zero parameters). **The token flag is a server-side declaration** (`API\Models\GruntTask.cs:147` → `CovenantService.cs:2292` → `InternalListener.cs:239` → wire). **On `Brute` the token is produced, dropped at `TaskExecute`'s `void` return, and the task reports `GruntTaskingStatus.Completed` with the string "Successfully made and impersonated token..." — a false positive from the tool's own message.** **Bounded by: `SharpSploit` source is not vendored, so this is the strongest static reading, not a closed loop (residual 1).** |
| **Q2** | **YES — the encrypted envelope survives the pipe. The pipe is not a raw carrier.** Encrypt is `Utilities.AesEncrypt(Message, this.SessionKey.Key)` at **`GruntBridge.cs:812` / `GruntSMB.cs:837`**, HMAC at **`:1030-1031` / `:1055-1056`**, **both one layer ABOVE the transport** in `Crafter.Create`; `WriteTaskingMessage` (`GruntBridge:494`) hands the already-sealed string to `UpstreamMessenger.Write`. **`GruntSMB`/`GruntBridge` are bridges: the relay (`:465-470`) decrypts its own layer, re-wraps, and writes a still-sealed `GruntEncryptedMessage` downstream.** **What the pipe ACL removes is channel authentication, not payload confidentiality.** |
| **Q3** | **Neither — the contradiction is LATENT.** `Brute` has the full HTTP `Profile` (`:362`, `FormatGetResponse`/`FormatPostRequest`) and is compiled from the HTTP template (`CovenantService.cs:1592-1609`), so `{{REPLACE_PROFILE_HTTP_POST_REQUEST}}` resolves and works. **No substitution logic consults `TaskExecute`'s shape.** The mis-grouping is observable **only** at the `TokenTask` branch. **Silent by construction; detectable only by running a token task and not getting the escalation the success message claims.** |
| **Q4** | **`Brute`'s divergence is UNIQUE — measured, 7 sites per family.** Three liveness sites use `ThreadState.Running` on `Brute` vs `IsAlive` on all three siblings. **Worse than D60 reported: `Brute:148` finds with `ThreadState.Running` then `:158` checks `IsAlive` after `Abort()` — two predicates in one three-line block.** **A blocked task is invisible to `Tasks`, unmatched by `TaskKill`, and `First()` throws into a broad `catch` at `:188` that increments `ConnectAttemptCount` — the kill fails and looks like a connection problem.** `First()`-on-empty is corpus-wide; **the widened trigger set is `Brute`-specific.** |

---

*End of D72. Pure source; no provider, no build, no execution. Scripts written to files. Comments stripped before classification; paths enumerated, never constructed; every count carries its invocation and its denominator. Two corrections: D60 understated the `Brute` thread-state defect (it is a hard failure, not just invisibility), and D60 implied the family contradiction might express through the placeholders (it does not — it is latent). Two instrument failures, one of which was me repeating shape 15 and only the exception catching it.*
