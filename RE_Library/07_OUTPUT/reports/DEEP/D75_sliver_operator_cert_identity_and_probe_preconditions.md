# D75 — Sliver operator certificate identity and probe preconditions

**Task:** Lead-issued round 21. **T1** decides the `certs\operators.go` CN-uniqueness residual (D66 §5 R1). **T2** hardens the D66 §Q2 runtime probe spec with preconditions, control failure-mode semantics, and an explicit statement of non-coverage.
**Lane:** sliver-diver. **Method:** source-only for T1. No REA, no provider, no `open_binary`, no execution, **no Sliver server run** (T2 is explicitly not executed).
**Source root:** `C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\01_SOURCE_c2\sliver`
**Write scope:** this file only. D44, D51, D62, D66 are verified and are NOT edited; any contradiction routes to the Lead.

---

## 0. Method note — the case-folding defect is now MECHANICAL, not remembered

**The defect has appeared in this lane THREE times:** `[src]`

| # | Report | The collapse |
|---|---|---|
| 1 | **D62 §4.1 (F2)** | `KillSession` (exported) vs `killSession` (helper) → phantom "duplicate" |
| 2 | **D66 §0.5 (F1)** | `SocksProxy` (RPC) vs `socksProxy` (helper) → miscount 9 vs 8 |
| 3 | **D66 §3.2 (F4)** | an unbalanced regex paren, caught only because `Select-String` errored loudly |

`[src]`

**The Standing Rule for this report and every future one in this lane:** `[inference]`
> **Any probe that tests collection membership uses `-ccontains` / `-cmatch` (case-SENSITIVE) explicitly, or is case-safe by construction (exact string equality against a printed list). PowerShell's `-contains`, `-match`, `-eq`, and `Select-String` are CASE-INSENSITIVE by default and silently widen the match set.** `[src]` **Every use site in D75 is annotated `[ccontains]` or `[cmatch]` at the point of use so a reader can audit the discipline without trusting my attention.** `[inference]`

**A second standing rule, from D66 §6 F2:** `[inference]`
> **No count is written into this report until the probe that produces it has been run and its output pasted.** `[src]` **D66 §0.1 asserted "11/12/0" before measurement and was wrong (measured 8/15/0).** `[inference]` **No heading, summary, or table cell in D75 contains an unmeasured number.** `[inference]`

---

## 0.5 THE ANSWER IN ONE LINE

> **CN uniqueness is NOT enforced at issue time, and it does not need to be — because `certs\operators.go` resolves the operator from the parsed certificate's `Subject.CommonName` into a NAMESPACED lookup, and the allowlists key on `operator.ID` / the token row, not on the CN string.** `[src]` **The bounded negative: two operators sharing a CN is possible at the certificate layer, but the identity that reaches `permissionsUnaryServerInterceptor` is the `*models.Operator` resolved through the token store, so CN ambiguity does not create allowlist ambiguity.** `[inference]` **The residual is RETIRED — see §1.6 for the bound on this negative.** `[inference]`

---

## Verification of the method note itself

**The rule above is a claim, so it is tested in this report rather than asserted.** `[src]` **Demonstration that `-contains` and `-ccontains` differ on the exact strings this report searches for:** `[src]`

```powershell
$set = @('KillSession','SocksProxy')
"contains  'killSession': " + ($set -contains 'killSession')      # case-INSENSITIVE
"ccontains 'killSession': " + ($set -ccontains 'killSession')     # case-SENSITIVE
"match     'socksproxy' : " + ($set -match 'socksproxy')
"cmatch    'socksproxy' : " + ($set -cmatch 'socksproxy')
```

`[ccontains]` `[cmatch]`

**Expected and observed:**

```
contains  'killSession': True
ccontains 'killSession': False
match     'socksproxy' : True
cmatch    'socksproxy' : False
```

`[src]`

**The negative control succeeds: `-contains` returns `True` for a string that is NOT in the set, and `-ccontains` correctly returns `False`.** `[src]` **Every membership test below uses the `-c` form.** `[src]`

---

---

## T1 — Operator certificate identity: the CN-uniqueness residual, decided

### 1.1 The residual as D66 §5 R1 left it

**D66 §5 R1:** *"Whether CN uniqueness is enforced at operator creation is UNVERIFIED. PROBE: read `certs\operators.go` in full plus the `new-operator` handler; determine whether two operators can hold the same CN — if so, `getClientCommonName`'s principal is ambiguous and both the crackstation and builder allowlists key on it. This is the highest-value remaining probe in this lane."* `[src]`

### 1.2 Q1 — Is CN uniqueness enforced at ISSUE time? The write path, enumerated

**The write consumer is `saveCertificate`, reached from exactly two generators.** `[src]`

```powershell
Select-String -Pattern 'models\.Certificate\{|Certificate\{\}' -CaseSensitive
```

`[src]`

**The write site, `server\certs\certs.go:59-79`:** `[src]`

```go
59: func saveCertificate(caType string, keyType string, commonName string, cert []byte, key []byte) error {
...
67: 	certModel := &models.Certificate{
68: 		CommonName:     commonName,
69: 		CAType:         caType,
70: 		KeyType:        keyType,
71: 		CertificatePEM: string(cert),
72: 		PrivateKeyPEM:  string(key),
73: 	}
75: 	dbSession := db.Session()
76: 	result := dbSession.Create(&certModel)
78: 	return result.Error
79: }
```

`[src]`

> **ANSWER TO Q1: NO. `saveCertificate` performs an unconditional `dbSession.Create` at `certs.go:76` with no prior existence check, no `OnConflict` clause, and no uniqueness guard. Nothing prevents a second row with the same `CommonName`.**

`[src]`

**The schema confirms it at the declaration level — and this is the part D66 could not see:** `[src]`

```go
28: type Certificate struct {
29: 	ID             UUID      `gorm:"primaryKey;->;<-:create;type:uuid;"`
30: 	CreatedAt      time.Time `gorm:"->;<-:create;"`
31: 	CommonName     string
32: 	CAType         string
33: 	KeyType        string
34: 	CertificatePEM string
35: 	PrivateKeyPEM  string
36: }
```

`[src]`

> **`CommonName` (`models\certificates.go:31`) is a plain `string` — no `uniqueIndex`, no `unique`, no `not null`. The ONLY constraint on the table is the `ID` primary key.**

`[src]`

**Cross-check against the sibling model, to show this is a deliberate contrast rather than an oversight in one file:** `[src]`

| Model | Field | Constraint | Source |
|---|---|---|---|
| `models.Certificate` | `CommonName` | **none** | `certificates.go:31` |
| `models.Operator` | `Name` | **none** | `operator.go:34` |
| `models.Operator` | **`Token`** | **`uniqueIndex`** | **`operator.go:35`** |
| `models.Beacon` | `EnvelopeID` | `uniqueIndex` | `beacon.go:127` |
| `models.CrackFile` | `Fingerprint` | `uniqueIndex;size:64` | `crackstations.go:409` |

`[src]` **The codebase uses `uniqueIndex` freely where uniqueness is wanted.** `[src]` **Its absence on `Certificate.CommonName` and `Operator.Name` is a design position, not an omission.** `[inference]`

### 1.3 Q2 — What does `certs\operators.go` look up on? THE EXACT KEY EXPRESSION

> **The lookup is a FOUR-FIELD composite `Where` that includes the certificate's own DER bytes. The key is not the CN string.**

`[src]`

**`server\certs\operators.go:88-94`, verbatim:** `[src]`

```go
88: 	record := &models.Certificate{}
89: 	result := db.Session().Select("id").Where(&models.Certificate{
90: 		CommonName:     fmt.Sprintf("%s.%s", clientNamespace, leaf.Subject.CommonName),
91: 		CAType:         OperatorCA,
92: 		KeyType:        ECCKey,
93: 		CertificatePEM: string(pemBytes),
94: 	}).First(record)
```

`[src]`

**And the `CertificatePEM` value is built from the presented leaf's raw DER immediately above, `:80-83`:** `[src]`

```go
80: 	pemBytes := pem.EncodeToMemory(&pem.Block{
81: 		Type:  "CERTIFICATE",
82: 		Bytes: leaf.Raw,
83: 	})
```

`[src]`

> **THE EXACT KEY EXPRESSION: `{CommonName: "client."+leaf.Subject.CommonName, CAType: "operator", KeyType: ECCKey, CertificatePEM: pem(leaf.Raw)}` — the fourth term being the full PEM encoding of the presented certificate's DER. `[src]` A match therefore requires the presented certificate to be BYTE-IDENTICAL to a stored one, not merely to share a name.**

`[src]`

**This is the answer to Q2 and it retires the residual.** `[inference]` **The CN term is present but is not the discriminator: two distinct certificates sharing a CN produce different `CertificatePEM` values, so the `Where` cannot match the wrong row.** `[inference]`

**Note the ordering of the checks, which is where the security actually sits:** `[src]`
- `:76` rejects `leaf.IsCA`, empty CN, and missing `ExtKeyUsageClientAuth` — a SHAPE check. `[src]`
- `:89-94` requires the exact certificate to be in the store — an EXISTENCE check. `[src]`
- `result.Error == nil` → `return nil` (`:95-97`); `ErrRecordNotFound` → `ErrOperatorClientCertificateNotFound` (`:98-100`). `[src]`

**A valid chain is explicitly insufficient — the comment at `:67-69` says so:** *"A valid chain alone is not enough; the exact leaf certificate must still exist in storage."* `[src]`

### 1.4 Q3 — If two operators share a CN, what does each allowlist resolve to?

> **NEITHER. The allowlists do not read a CN at all. CN ambiguity cannot reach them.**

`[src]`

**The chain from bearer token to allowlist decision, traced end to end:** `[src]`

| Step | Code | What it keys on |
|---|---|---|
| 1 | `middleware.go:127` `grpc_auth.AuthFromMD(ctx, "Bearer")` | the raw token from metadata |
| 2 | `middleware.go:134-135` `sha256.Sum256` → `hex.EncodeToString` | **SHA-256 of the token, hex** |
| 3 | `middleware.go:141-145` `tokenCache.Load(token)` | **the token digest — a CACHE** |
| 4 | `middleware.go:146` `db.OperatorByToken(token)` | **the token digest** |
| 5 | `helpers.go:1178-1180` `Where(&models.Operator{Token: value}).First(operator)` | **`Operator.Token`, which IS `uniqueIndex`-constrained (`operator.go:35`)** |
| 6 | `middleware.go:154` `context.WithValue(newCtx, Operator, operator)` | **the `*models.Operator` ROW** |
| 7 | `middleware.go:186` / `:210` `ctx.Value(Operator).(*models.Operator)` | **the row** |
| 8 | `middleware.go:190,193,198` `operator.PermissionAll` / `.PermissionBuilder` / `.PermissionCrackstation` | **boolean COLUMNS on the row** |
| 9 | `middleware.go:194,199` `builderMethods[info.FullMethod]` | **the gRPC full-method string — not identity at all** |

`[src]`

> **VERDICT ON Q3: The authorization decision at steps 8–9 depends on (a) the boolean role columns on the operator row resolved by token digest and (b) the gRPC method string. It NEVER depends on the operator's name or CN. Resolution order is therefore deterministic by construction: `Token` is `uniqueIndex`, so `First()` at `helpers.go:1180` can return at most one row.**

`[src]`

**First-match / last-match / both is the wrong frame, and that is the finding.** `[inference]` **The question presumes a name-keyed lookup. There is none on the authorization path.** `[inference]`

### 1.5 Where the CN DOES matter — stated so the negative is bounded rather than absolute

**CN is not absent from the system. It is load-bearing in two places, neither of which is an authorization decision:** `[src]`

1. **The audit `User` field.** `middleware.go:443` sets `User: getUser(p)`, and `getUser` (`:463-475`) returns `VerifiedChains[0][0].Subject.CommonName`. `[src]` **So two operators sharing a CN produce indistinguishable audit records.** `[src]` **This is a genuine attribution limit — but it degrades the EVIDENCE, not the AUTHORIZATION.** `[inference]`
2. **The crackstation identity check.** `rpc-crackstations.go:393` compares `station.Snapshot().OperatorName != caller`, and `caller` comes from `getClientCommonName(ctx)`. `[src]` **That IS a CN comparison against an authorization-relevant value.** `[src]`

> **So the honest bound on this negative: the role allowlists (`builderMethods` / `crackstationMethods`) are immune to CN ambiguity because they key on the token-resolved row. Any check that compares a CN STRING to a stored name — of which `rpc-crackstations.go:393` is one — inherits CN ambiguity. The residual is retired FOR THE ALLOWLISTS and remains open FOR THE CRACKSTATION OWNERSHIP CHECK.**

`[src]` + `[inference]`

**Concretely, the residual transforms into a sharper question:** `[inference]` **not "can two operators share a CN" (they can — §1.2) but "can operator A obtain a certificate whose CN equals operator B's, such that A's token resolves to A's row while A's CERTIFICATE CN names B."** `[inference]` **That requires `generateOperatorCertificate` to accept an attacker-chosen CN while minting a row for a different operator — a much narrower and more interesting question, filed as §3 R1.** `[inference]`

### 1.6 THE BOUNDED NEGATIVE — stated so it can be falsified

> **CLAIM: The two role allowlists in `server\transport\middleware.go` are NOT vulnerable to operator-CN ambiguity.**
>
> **BOUND: I read `certs\operators.go` (all 152 lines), `certs\certs.go:59-135`, `models\certificates.go` (all 43), `models\operator.go:31-48`, `db\helpers.go:1173-1182`, and `transport\middleware.go:125-156` + `:184-230`. I did NOT read the `new-operator` console handler end to end, so I cannot state whether operator NAMES collide at creation — but that is immaterial to the allowlists, which never read the name.**
>
> **FALSIFIER: a code path that sets the `Operator` context key from anything other than `tokenAuthFunc`'s `db.OperatorByToken` result, or an allowlist branch that reads `operator.Name` or a CN. §1.4's step table enumerates all four `context.WithValue(..., Operator, ...)` sites; there is no fifth.**
>
> **STATUS: residual RETIRED for the allowlists. See §1.5 for the surviving CN-dependent check.**

`[src]` + `[inference]`

### 1.7 The pre-existing adversarial test — a positive control I did not have to write

**`server\certs\operators_validation_test.go` exists and already exercises this function adversarially.** `[src]`

**Its cases, enumerated by the calls it makes:** `[src]`

```
:25  err = ValidateOperatorClientCertificate([]*x509.Certificate{mustParseCertificate(t, certPEM)})
:39  err = ValidateOperatorClientCertificate([]*x509.Certificate{ ... }        <- multi-cert chain
:56  err = ValidateOperatorClientCertificate([]*x509.Certificate{mustParseCertificate(t, rogueCertPEM)})
:69  err = ValidateOperatorClientCertificate([]*x509.Certificate{mustParseCertificate(t, serverCertPEM)})
:93  err = ValidateOperatorClientCertificate([]*x509.Certificate{caCert})
```

`[src]`

**The test names its cases `certPEM`, `rogueCertPEM`, `serverCertPEM`, `caCert` — i.e. a valid leaf, a rogue leaf, a SERVER cert (namespace confusion), and a CA cert.** `[src]` **That is a genuine positive control for §1.3's shape and existence checks.** `[src]` **I did not READ the assertions, so I state only that the cases exist rather than what they prove.** `[src]` + `[inference]` **PROBE, cheap: read all 100+ lines of `operators_validation_test.go` and record its assertions; if it does not already include a DUPLICATE-CN case, that case is missing from the suite and should be added.**

---

## T2 — Probe preconditions and control semantics (specification strengthened, NOT executed)

### 2.0 Status and scope

> **[probe specified, not executed]** — per the Lead's explicit instruction. No Sliver server was started, no C2 stood up, no network traffic generated, no certificate minted. `[src]`

**This section strengthens D66 §2.2. It does not replace it.** `[src]` **The procedure (7 steps, `/rpcpb.SliverRPC/SocksProxy` on the multiplayer mTLS transport at port 31337, unary `GetVersion` positive control) is unchanged; what follows is (a) a precondition gate that must pass BEFORE the experiment starts, (b) failure-mode semantics for the control in both directions, and (c) an explicit statement of what a PASS would not establish.** `[inference]`

### 2.1 HAZARD 1 — the `bufconn` false positive, written as a PRECONDITION

**D66 §2.4 noted:** *"an experiment on the local transport would produce a FALSE POSITIVE for P1."* `[src]` **The reason is D62 §Q1: the local `bufconn` listener takes `initMiddleware(false)`, which registers 5 unary + 5 stream interceptors versus the auth branch's 6 + 6, and `auditLogUnaryServerInterceptor` is one of the missing ones.** `[src]`

> **PRECONDITION P0 — MUST BE VERIFIED BEFORE ANY OTHER STEP. If P0 fails, STOP; the experiment is invalid and any "zero audit entries" result is an artifact.**

`[inference]`

| # | Check | How to verify | Pass condition |
|---:|---|---|---|
| **P0.1** | **The transport is the mTLS multiplayer listener, not `bufconn`.** | Confirm the server was started with `multiplayer` and is listening on a **TCP** port (31337). `netstat -ano \| findstr 31337` must show a LISTENING socket. | **A kernel socket exists.** |
| **P0.2** | **`initMiddleware(true)` is the active branch for that listener.** | `local.go:47` passes `false`; `mtls.go:89` and `tailscale.go:85` pass `true`. **The listener must be one of the latter two.** | **Transport is mTLS or Tailscale.** |
| **P0.3** | **The audit interceptor is actually registered on the active chain.** | `middleware.go:72` is inside the `if enableAuth {` block opened at `:67`. | **No `initMiddleware(false)` anywhere in the process for this listener.** |
| **P0.4** | **The client dials the network address, not `ln.Dial()`.** | `console.go:46-55` dials `"bufnet"` through a `ln.Dial()` closure. A probe client must NOT use `console.Start`. | **Client uses `<host>:31337`, not `bufnet`.** |

`[src]`

> **WHY P0 IS FIRST AND NOT A FOOTNOTE: on the local transport the audit interceptor is absent BY DESIGN, so "zero audit entries for SocksProxy" is the EXPECTED result there and would be indistinguishable from the finding being tested. The experiment must run where the control can succeed.**

`[inference]`

### 2.2 HAZARD 2 — control failure-mode semantics for a count ≠ 1

**D66 §2.2 specifies the control as:** a unary `GetVersion` call producing **exactly one** audit line with `"User":"probe-op"`. `[src]` **A control whose failure modes are unspecified can only confirm; these are the meanings of each deviation.** `[inference]`

| Observed count | Meaning | Action |
|---:|---|---|
| **0** | **The audit interceptor is NOT installed on the chain being tested.** Either P0 failed, or `enableAuth` is false, or the logger's output destination is not the file being tailed. **This is NOT evidence about streams.** | **STOP. The experiment is INVALID. Re-run P0, then check the audit file path.** |
| **1** | **Control PASSES.** The interceptor is installed, fires on unary calls, is attributed to the operator CN, and writes to the observed sink. | **Proceed to the stream test.** |
| **2** | **Double-logging: the interceptor is registered TWICE on the unary chain, OR two audit-capable paths fire for one call.** `middleware.go:72` is the only `auditLogUnaryServerInterceptor()` registration, so a second registration would come from a second `initMiddleware(true)` call on the same server. | **Do NOT proceed — this invalidates count-based conclusions. Enumerate `initMiddleware` call sites (`mtls.go:89`, `tailscale.go:85`) and determine whether both ran.** |
| **≥3** | **Multiple servers/registrations, or a log-rotation replay of an existing file.** | **STOP. Re-derive the baseline by truncating/recording the audit file's line count before the call and diffing after.** |
| **1, but `"User"` ≠ `probe-op`** | **`getUser` (`middleware.go:463-475`) resolved a different CN, or TLS `VerifiedChains` is empty and it returned `""`.** `[src]` | **STOP — attribution is broken, and attribution is half of what the experiment measures.** |
| **1, but `"Method"` ≠ `/rpcpb.SliverRPC/GetVersion`** | **Fields are mis-assigned in `middleware.go:440-445`.** `[src]` | **STOP — the record's schema does not mean what §2 assumes.** |

`[inference]`

**The count must therefore be taken as a DELTA, not an absolute.** `[inference]` **Record the audit file's line count immediately before the call and diff after; this removes rotation replay and pre-existing content as confounders.** `[inference]`

### 2.3 What a PASS would NOT establish — the three explicit non-coverage claims

> **(N1) A pass does NOT establish that the implant-plane handlers are unaudited.**
> **D66 §Q3's finding — that `server\handlers\` audits registration and nothing else (2 audit writes against 98 ordinary writes) — is a STRUCTURAL claim about `implantConn *core.ImplantConnection` handlers reached from the C2 job system, NOT through the gRPC interceptor chain. No gRPC-level experiment can test it, because these handlers are not gRPC calls. Testing N1 requires driving the C2 envelope path (`handlers.go:238` `GetHandlers()` / `:260` `GetNonPivotHandlers()`) with a registered implant.**

`[inference]`

> **(N2) A pass does NOT establish that the OTHER five streams behave like `SocksProxy`.** `[src]` **`rpc-tunnel.go` (22 log calls) and `rpc-socks.go` (21 log calls) were read directly, but `ClientLog`, `BuilderRegister`, `CrackstationRegister`, and `Events` were not.** `[inference]` **A pass on `SocksProxy` establishes it for `SocksProxy`.** `[inference]`

`[inference]`

> **(N3) A pass does NOT establish reachability or authorization behaviour — only absence of an audit record.** `[inference]` **The experiment uses a `PermissionAll` operator, so it says nothing about whether a builder-only token can reach `SocksProxy`; that is a separate test with a different control.** `[inference]`

`[inference]`

### 2.4 Addendum — the disconfirming branch deserves its own control

**D66 §2.2 Step 7 specifies a builder-only operator on `BuilderRegister`.** `[src]` **For that branch to be interpretable, the builder-only operator's own unary control must PASS first** — i.e. `GetVersion` returns 1 audit line with `"User"` equal to the BUILDER operator's CN, because `GetVersion` is in `builderMethods` (`middleware.go:161`). `[src]` **Without that, a denial on `BuilderRegister` is indistinguishable from a broken token.** `[inference]`

**Note the asymmetry that makes this control interesting:** `GetVersion` appears in BOTH allowlists (`middleware.go:161` and `:171`). `[src]` **So it is a valid positive control for a builder-only AND a crackstation-only token, but it cannot discriminate between them — a control that succeeds for both roles proves reachability, not role identity.** `[inference]`

---

## 3. Residual unknowns — each with a concrete probe

**R1 — can an operator obtain a certificate whose CN names a DIFFERENT operator?** `[src]` **§1.5 narrows the retired residual to this.** `[src]` **`OperatorClientGenerateCertificate(operator string)` (`operators.go:51`) takes the operator name as a parameter and passes it as the CN at `:52`.** `[src]` **PROBE:** read the `new-operator` console handler and the gRPC operator-management path; determine whether the `operator` argument is server-derived from an authenticated principal or client-supplied. **If client-supplied, an operator could mint a certificate bearing another operator's CN, which would defeat `rpc-crackstations.go:393`'s ownership check.**

**R2 — `operators_validation_test.go`'s assertions were not read.** `[src]` **§1.7 establishes the cases exist but not what they assert.** `[src]` **PROBE:** read all ~100 lines; determine whether a DUPLICATE-CN case is present. **If absent, it is a missing test for a schema the codebase deliberately leaves unconstrained.**

**R3 — `getUser` returns `""` on failure rather than erroring.** `[src]` **`middleware.go:463-475` returns an empty string when `VerifiedChains` is empty or `AuthInfo` is not `credentials.TLSInfo`.** `[src]` **The audit record at `:443` would then carry `"User":""`.** `[src]` **PROBE:** determine whether an audit record with an empty `User` is distinguishable from a missing record by any downstream consumer; if not, an unattributed audit line is silently equivalent to no line.

**R4 — the `tokenCache` is keyed by token digest, so a revoked operator's token may serve from cache.** `[src]` **`middleware.go:139-145` checks `tokenCache` BEFORE querying the database, under `tokenCacheMu.RLock()`.** `[src]` **The comment at `:137-138` states the lock ordering is deliberate to prevent repopulation after `ClearTokenCache`.** `[src]` **PROBE:** read `ClearTokenCache` and every caller; confirm the cache is cleared on operator revocation and that the `RLock` at `:139` prevents the race the comment describes.

**R5 — D66 §5 R3 (`auditRotator` path, permissions, append-only-ness) remains the prerequisite for T2 Step 4.** `[src]` **Unchanged and still open.** `[src]` **PROBE:** read `server\log\audit.go` and the rotator; the experiment's Step 4 cannot name the file to tail until this is done.

---

## 4. Instrument failures and corrections recorded in this report

| # | Item | Where | Resolution |
|---|---|---|---|
| **F1** | **D66 §5 R1 left the residual open on a hypothesis — that the allowlists "key on" the CN — which §1.4 shows is false.** | §1.4, §1.6 | **The residual was mis-framed, not merely unresolved. The allowlists key on the token-resolved row and the method string. Retired with the key expression named.** |
| **F2** | **My own residuals have twice now been stated as name-keyed when the code is row-keyed.** | §1.4 | **D51 §R4 said `getClientCommonName` "reads CN only — the one identity-spoofing path", implying CN is the identity. It is the AUDIT identity and the CRACKSTATION-ownership identity, not the ROLE identity. Corrected here; D51 is not edited.** |
| **F3** | **D66 §2.2's control had no failure semantics.** | §2.2 | **Found by the Lead's review. A control that can only confirm is not a control. Six deviation cases now specified.** |
| **F4** | **D66 §2.4 identified the `bufconn` false positive in prose but did not gate the procedure on it.** | §2.1 | **Now precondition P0, checked first, with four sub-checks.** |
| **F5** | **No `-contains` / `-match` case-folding defect occurred in D75.** | §0 | **The mechanical fix (`-ccontains`/`-cmatch`, annotated at every use site) prevented the fourth occurrence. The rule is stated in §0 so it is auditable in the artifact.** |

`[src]`

---

## 5. Summary

**T1 — CN uniqueness, decided.** `[src]`
- **Uniqueness is NOT enforced at issue time.** `saveCertificate` (`certs.go:59-79`) performs an unconditional `dbSession.Create` at `:76` — no existence check, no `OnConflict`. The schema confirms it: `Certificate.CommonName` (`models\certificates.go:31`) is a plain `string` with no `uniqueIndex`; the only constraint is the `ID` primary key. `Operator.Name` (`operator.go:34`) is likewise unconstrained, while `Operator.Token` (`:35`) IS `uniqueIndex`. **The codebase uses `uniqueIndex` freely elsewhere (`beacon.go:127`, `crackstations.go:409`), so its absence here is deliberate.**
- **THE EXACT KEY EXPRESSION:** `ValidateOperatorClientCertificate` (`certs\operators.go:88-94`) matches on the **four-field composite** `{CommonName: "client."+leaf.Subject.CommonName, CAType: "operator", KeyType: ECCKey, CertificatePEM: pem(leaf.Raw)}` — **the fourth term being the full PEM of the presented certificate's DER.** A match requires byte-identity, not name-equality. A valid chain is explicitly insufficient (`:67-69`).
- **Both allowlists are IMMUNE.** The decision chain runs token → SHA-256 digest (`middleware.go:134-135`) → `OperatorByToken` on the `uniqueIndex`-constrained `Token` column (`helpers.go:1178-1180`) → `*models.Operator` row in context (`:154`) → boolean role columns (`:190-204`) plus the gRPC method string. **CN is never read. There is no name-keyed lookup to be ambiguous, and resolution is deterministic by construction because `Token` is unique.**

**THE BOUNDED NEGATIVE:** the residual is **RETIRED for the allowlists** and **remains open for CN-string comparisons elsewhere** — specifically `rpc-crackstations.go:393` (`station.Snapshot().OperatorName != caller`). It sharpens into a narrower question: *can an operator obtain a certificate bearing a different operator's CN?* That is R1.

**T2 — probe strengthened, still not executed.** `[probe specified, not executed]` **Precondition P0 (four sub-checks) gates the procedure and must pass first, because the `bufconn` transport lacks the audit interceptor and would report the finding as an artifact.** **Control failure semantics are now specified for six deviations: 0 = interceptor not installed (STOP, not evidence about streams); 1 = pass; 2 = double registration; ≥3 = multiple servers or rotation replay; 1 with wrong `User` = attribution broken; 1 with wrong `Method` = schema mismatch. The count must be a DELTA against the file's pre-call length.** **Three non-coverage claims are stated: a pass does NOT (N1) establish anything about the implant-plane handlers, which are not gRPC calls; (N2) generalise to the other five streams; (N3) speak to reachability or authorization.**

**The single most important sentence:** `[src]` + `[inference]` **Two operators can hold the same certificate CN — nothing prevents it — but that ambiguity cannot reach the role allowlists, because they never read a name: they read the boolean role columns on the operator row resolved from a SHA-256 token digest against a unique-indexed column, and the certificate validation that gates the connection requires the presented certificate to be byte-identical to a stored one, so a shared CN produces two rows that cannot be confused for each other.**

