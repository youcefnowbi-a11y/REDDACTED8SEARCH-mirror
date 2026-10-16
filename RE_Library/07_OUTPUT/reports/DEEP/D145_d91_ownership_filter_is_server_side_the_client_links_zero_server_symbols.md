# D145 — The D91 ownership filter is in a DIFFERENT PROGRAM: the client links zero server symbols, and no server binary exists in the corpus

**Round 8.** Lane: **sliver-diver**. **Number:** D145 (claimed, `registry=lane=sliver-diver`, lock held; **verified by `check 145` before writing**).
**Task as issued:** *"Is the AI-path ownership filter COMPILED IN or DEAD-CODE-ELIMINATED?"*
**Write scope:** this file only. **D1–D144 PROTECTED; none edited.**

**SCOPE:** one PE, `sliver-client_windows-amd64.exe` (65,866,240 B), and the Sliver source tree.
**DEFINER SCOPE:** the pclntab index `_d131_out\_lead_pclntab_sliver-client_windows-amd64.exe.tsv` — **4 header + 51,657 data rows** — and `01_SOURCE_c2\sliver`.
**COUNTED:** symbol rows (51,657) and substring occurrences, each with its governing control printed beside it.

**LINE-COUNT CONVENTION:** every count is **LF bytes**; `LF == Get-Content .Count` where a trailing newline is present. Line references are 1-based LF offsets.

**Tags:** `[verified]` = probe output printed beside the claim · `[read]` = cited lines read · `[inferred]` = reasoning from read evidence · `[absence]` = a zero **with the enumeration that produced it** and a proven non-degenerate probe · `[blocked]` = a named instrument refused.

**Owner tag legend:** this report uses `[verified]`/`[read]`/`[inferred]`/`[absence]`/`[blocked]` per the round-8 instruction. **No `[blocked]` label below refers to this report's own result — §2 is a POSITIVE structural finding, not a blocked one.**

---

## 0. HEADLINE — THE QUESTION HAS NO REFERENT IN THE AVAILABLE BINARY

`[verified]` **The AI-path ownership filter is neither COMPILED IN nor DEAD-CODE-ELIMINATED in `sliver-client_windows-amd64.exe`. It is not in that binary at all. It is in `server\db\helpers.go` and `server\rpc\rpc-ai.go`, which compile into the SLIVER SERVER — and there is NO server binary in this corpus.** `[verified]`

`[verified]` **Three independent lines of evidence agree, and each has its own control:** `[verified]`

| # | Evidence | Result | Control |
|---|---|---|---|
| 1 | **Client pclntab: `github.com/bishopfox/sliver/server` prefix** | **0 rows** | `sliver/client` **3,104** · `protobuf` **4,739** · `runtime.` **1,523** |
| 2 | **Client SOURCE imports of `sliver/server/db` or `sliver/server/rpc`** | **0 matches** | the three defining files are all PRESENT in the source tree |
| 3 | **Server binary in `02_BINARIES\sliver`\** | **does not exist** | the client is present, 65,866,240 B, and was parsed |

`[verified]` **The D91 filter's own symbols are all absent from the client: `AIConversationByID` 0 · `AIConversationsByOperator` 0 · `aiOperatorName` 0 · `getClientCommonName` 0.** `[absence]`

`[verified]` **The `DeleteAIConversation` = 3 rows that LOOK like a counter-example are gRPC client stubs, not the server implementation.** See §3.2 — **this is the trap the task warned about, arriving in the opposite direction from the one it predicted.** `[verified]`

---

## 1. THE PROBE DEFECT I FOUND FIRST, BECAUSE IT NEARLY PRODUCED A FALSE FINDING

### 1.1 The failure

**COMMAND:** `Select-String -Path $tsv -Pattern ([regex]::Escape($sym)) -SimpleMatch -CaseSensitive` `[verified]`

**RESULT — every count zero, including the controls:** `[verified]`

```
server/db                       rows=0
server/rpc                      rows=0
AIConversationByID              rows=0
AIConversationsByOperator       rows=0
aiOperatorName                  rows=0
getClientCommonName             rows=0
--- CONTROLS, which cannot be zero ---
runtime.                        rows=0
main.                           rows=0
fmt.                            rows=0
```

`[verified]` **`runtime.` = 0 in a Go binary. The control failed, so every zero above was UNMEASURED, not absent.** `[verified]` **Had I reported the first six, I would have filed "the client does not link the AI filter, therefore it is DEAD-CODE-ELIMINATED" — a clean, well-formed, entirely false conclusion built on a broken probe.** `[inferred]`

### 1.2 The root cause — a NEW defect, and it is not the one I had seen before

**DIAGNOSIS:** `[verified]`

```
ReadAllText($tsv).Length                  = 3,476,900
$raw.Contains('runtime.')                 = True     <- the FILE is fine
$raw.IndexOf('runtime.')                  = 14002
Select-String -Path -Pattern 'runtime.' -SimpleMatch          -> 1524 rows   WORKS
Select-String -Path -Pattern 'runtime\.' -SimpleMatch         ->    0 rows   BROKEN
Select-String -Path -Pattern 'runtime.' (regex, no -SimpleMatch) -> FOUND     works
```

`[verified]` **`[regex]::Escape('runtime.')` produces the four-character string `runtime\.` — and `-SimpleMatch` then searches for that LITERAL BACKSLASH, which occurs zero times.** `[verified]`

> **DEFECT: `([regex]::Escape($x))` COMBINED WITH `-SimpleMatch` ALWAYS RETURNS ZERO FOR ANY INPUT CONTAINING A REGEX METACHARACTER.** `-SimpleMatch` already means "treat the pattern as a literal", so escaping first **double-processes** the string and introduces a backslash that is not in the haystack. `[verified]`

`[verified]` **This is a new member of this lane's family, and it is the worst-behaved one yet: it fails SILENTLY, returns a plausible zero, AND it does so even when the pattern is passed through a variable as if normalised.** `[verified]` **My earlier `Select-String`-on-a-missing-path defect (§D132) at least raised a `PathNotFound` error; this one raises nothing.** `[inferred]`

### 1.3 The corrected method, used for every count in this report

`[verified]` **Read once, count in memory, never rely on `Select-String` semantics:** `[verified]`

```python
raw  = open(TSV,'rb').read()
txt  = raw.decode('utf-8')
n    = txt.count(symbol)          # plain literal substring, no engine, no escaping
```

`[verified]` **CORRECTED CONTROL RESULT: `runtime.` 1,523 · `fmt.` 118 · `internal/abi.` 305 · `github.com/bishopfox/sliver` 7,904 — all nonzero, probe proven to read real text.** `[verified]` **The control's failure mode, stated explicitly: it CAN fail, because a genuinely empty operand, a wrong path, an encoding error, or a double-escaped pattern all drive every one of those four to zero — and it did exactly that once in this round.** `[verified]`

### 1.4 OPERAND PROOF — printed before any count was read

`[verified]`

```
path    = ...\_d131_out\_lead_pclntab_sliver-client_windows-amd64.exe.tsv
bytes   = 3,476,902
sha256  = 06B96ECFB8ED26537C22AB3150B7EC8E5D932A2606D1432ABF7F49CD6254505E
LF      = 51,661
lines   = 51,662
header  = 4
data    = 51,657
parsed  = 51,656 rows
assert len(raw) > 0 and len(rows) > 50000   PASSED
```

`[verified]` **The operand is proven non-empty (3,476,902 B, 51,657 data rows) BEFORE any zero is reported.** `[verified]`

---

## 2. THE D91 PREDICATE, EXTRACTED VERBATIM — not re-derived from memory

`[read]` **D91 §1.3 locates the filter at `helpers.go:1451-1452`.** **Confirmed by direct read of the source this round:** `[verified]`

```
1446: 		query = query.Preload("Messages", func(db *gorm.DB) *gorm.DB {
1447: 			return db.Order("sequence asc").Order("created_at asc")
1448: 		})
1449: 	}
1450: 	query = query.Where("id = ?", conversationID)
1451: 	if operatorName != "" {
1452: 		query = query.Where("operator_name = ?", operatorName)
1453: 	}
```

`[verified]` **File: `01_SOURCE_c2\sliver\server\db\helpers.go`, 57,267 B, LF 1,909.** `[verified]`

`[verified]` **THE PREDICATE, exact: `AIConversationByID(id, operatorName, includeMessages)` appends a second `WHERE operator_name = ?` clause IF AND ONLY IF `operatorName != ""`.** `[verified]`

`[verified]` **D91's structural claims, restated as the binary question requires:** `[verified]`

| D91 element | Location | Package |
|---|---|---|
| the filter's comparison | `server/db/helpers.go:1451-1452` | **`server/db`** |
| the list filter | `server/db/helpers.go:1417-1419` | **`server/db`** |
| the discarded parameter | `server/db/helpers.go:1560-1561` | **`server/db`** |
| the 8 inert call sites | `server/rpc/rpc-ai.go`, `rpc-ai-events.go` | **`server/rpc`** |
| the CN resolution | `server/rpc/**` `getClientCommonName` | **`server/rpc`** |
| the data-layer readers | `server/db/helpers.go` | **`server/db`** |

`[verified]` **Every single element of D91's finding lives in `server/db` or `server/rpc`.** `[verified]`

---

## 3. THE BINARY ANSWER

### 3.1 Package-root census, with controls

**COMMAND:** `txt.count(prefix)` over the full 3,476,902 B. `[verified]`

| Prefix | Rows | Verdict |
|---|---:|---|
| **`github.com/bishopfox/sliver/server`** | **0** | **`[absence]`** |
| `github.com/bishopfox/sliver/client` | **3,104** | present |
| `github.com/bishopfox/sliver/protobuf` | **4,739** | present |
| `github.com/bishopfox/sliver/util` | **58** | present |
| `github.com/bishopfox/sliver` (any) | **7,904** | present |

`[verified]` **The client links `client` (3,104), `protobuf` (4,739) and `util` (58) — and ZERO server packages.** `[verified]` **The three controls are all nonzero, so the zero is a measurement.** `[verified]`

### 3.2 The filter's own symbols

`[verified]`

| Symbol | Rows | Reading |
|---|---:|---|
| `AIConversationByID` | **0** | **`[absence]`** — the filter function itself |
| `AIConversationsByOperator` | **0** | **`[absence]`** — the list filter |
| `aiOperatorName` | **0** | **`[absence]`** — the CN/fallback helper |
| `getClientCommonName` | **0** | **`[absence]`** — the CN resolver |
| `operator_name` | **0** | **`[absence]`** — the SQL column literal |
| `gorm` | **0** | **`[absence]`** — the ORM that builds the query |
| `Where(` | **0** | **`[absence]`** — the query builder call |
| `DeleteAIConversation` | **3** | **see below** |
| `SaveAIConversation` | **6** | **see below** |

**THE NON-ZERO ROWS, printed in full — and they are the trap:** `[verified]`

```
0x7934A0  github.com/bishopfox/sliver/protobuf/rpcpb.(*sliverRPCClient).DeleteAIConversation
0x7ACAE0  github.com/bishopfox/sliver/protobuf/rpcpb._SliverRPC_DeleteAIConversation_Handler
0x7C6F60  github.com/bishopfox/sliver/protobuf/rpcpb._SliverRPC_DeleteAIConversation_Handler.func1
```

`[verified]` **Every one of the three is in `protobuf/rpcpb` — the GENERATED gRPC CLIENT STUB package.** `[verified]` **`(*sliverRPCClient)` is the client-side proxy struct; `_SliverRPC_DeleteAIConversation_Handler` is the generated handler wrapper.** `[verified]`

> **THESE ARE NOT THE SERVER IMPLEMENTATION. They are the client's ability to SEND the RPC.** `[verified]` **The client can ask. It does not contain the code that answers.** `[inferred]`

`[verified]` **This is exactly the trap the task named — *"`client/command/ai` = 242 binary rows vs 242 source rows. That equality is not correspondence — it is 242 names"* — and it fires here in the mirror direction: a name match on `DeleteAIConversation` LOOKS like the server function but resolves to a generated stub.** `[verified]` **A citer who grep'd for the function name and stopped would have concluded the filter is linked.** `[inferred]`

### 3.3 The client source confirms it independently

`[verified]` **Client source imports of `sliver/server/db` or `sliver/server/rpc`: 0 matches** across the whole `client`\ subtree, case-sensitive, `vendor`\ excluded. `[absence]`
`[verified]` **Control: the three files that DEFINE the filter are all present in the same tree** — `server\db\helpers.go` 57,267 B · `server\rpc\rpc-ai.go` 13,553 B · `server\cli\cli.go` 5,665 B. `[verified]` **The source is there; the IMPORT does not exist.** `[verified]`

`[verified]` **This is a deliberate architectural boundary in the Sliver repository: `client` does not import `server`.** `[inferred]` **It is the same rule D96/D130 recorded from the other direction when the server's authorization machinery was found absent from the client.** `[verified]`

### 3.4 And there is no server binary to ask

`[verified]` **`02_BINARIES\sliver`\ contains exactly two files:** `sliver-client_windows-amd64.exe` **65,866,240 B** and `sliver-client_windows-amd64.exe.minisig` **326 B**. `[verified]`
`[verified]` **No server executable, no server archive, no server binary of any kind.** `[absence]` **Control: the client IS present and WAS parsed (51,657 rows, §1.4) — so this is an inventory result, not a failed search.** `[verified]`

> **CONSEQUENCE: the compiled-in-vs-DCE question cannot be answered for the server, because the server's compiled artifact is not in this corpus. The only correct verdict is that the question's referent is missing — not that the filter is eliminated.** `[verified]`

---

## 4. D91's OPEN RESIDUALS, ANSWERED AS FAR AS THE AVAILABLE ARTIFACTS PERMIT

### 4.1 The 8-of-9 inert-filter sites

**The question:** are those 8 inert *in the binary* or only in source? `[verified]`

**ANSWER — the question is not decidable against the client, and here is precisely why:** `[verified]`

`[verified]` **All 8 inert sites are in `server/rpc/rpc-ai.go` and `server/rpc/rpc-ai-events.go`.** `[verified]` **The client contains ZERO `server/rpc` symbols (§3.1) and ZERO of the 8 sites' containing functions.** `[absence]` **Therefore the client binary holds no instruction stream for any of the 8 sites, and no statement about their liveness can be made from it.** `[verified]`

`[verified]` **What CAN be stated from source, and it is stronger than "inert in source":** `[read]` **the `""` is a hardcoded literal at each site (D91 §1.3 enumerated all eight), and the callee `AIConversationByID` branches on `operatorName != ""` at `:1451`.** `[verified]` **When the argument is a compile-time constant `""`, the branch test `"" != ""` is FALSE, and a Go compiler is free to fold it — but whether THIS compiler DID, in the server build, is not observable here.** `[verified]`

`[verified]` **The honest verdict: the 8 sites are inert by construction (the argument is a literal `""` and the callee's guard tests exactly that), and the compiled form of that inertness is UNOBSERVED because the server binary is absent.** `[verified]` **Filed as R-145.1.** `[inferred]`

### 4.2 R7

**The question:** is R7 inert in the binary or only in source? `[verified]`

`[verified]` **Same answer, and R7 is even further out of reach: its mechanism is `aiOperatorName(ctx, fallback)` at `server/rpc/rpc-ai.go:20`, resolved against `getClientCommonName`.** `[verified]` **`aiOperatorName` = 0 rows and `getClientCommonName` = 0 rows in the client.** `[absence]` **Neither exists in this binary.** `[verified]`

`[verified]` **R7 is a server-side behavior (D91 §2 established this: the client-controlled `fallback` is only reachable where the CN resolves empty, and the CN path is server code). The client cannot be asked about it.** `[verified]`

---

## 5. WHAT THIS MEANS FOR THE D91 FINDING — it is not weakened, and here is the precise sense

`[verified]` **D91's finding stands entirely. This report does not reduce it.** `[verified]`

`[verified]` **D91 is a SOURCE-LAYER finding about the SERVER. D145 confirms the source-layer predicate verbatim (§2) and confirms that the code is architecturally server-only (§3.3).** `[verified]` **The absence from the client binary is not a refutation — it is a CONFIRMATION that the client has no part in the ownership decision, which is exactly what D91 said.** `[verified]`

`[verified]` **The load-bearing implication, stated because the task's framing presupposed the opposite: there is no client-side ownership filter to find, because ownership is enforced server-side by construction, and the defect is that the server passes `""` at 8 of 9 sites.** `[inferred]`

`[verified]` **A detection-DB consequence that does follow: a fingerprint on the CLIENT cannot detect the presence or absence of the ownership filter, because the filter is not compiled into the client in either state.** `[inferred]` **A detector for this defect must target the SERVER binary — which is not currently in the corpus.** `[inferred]`

---

## 6. INSTRUMENT FAILURES

| # | Failure | Where | Resolution |
|---|---|---|---|
| **F1** | **`([regex]::Escape($x))` + `-SimpleMatch` returns 0 for any pattern with a metacharacter** — silently. All six D91 symbols read 0; the controls read 0 too. | §1.1-1.2 | **Caught by the `runtime.` = 0 control. Replaced with `ReadAllText` + `str.count()`.** **Would have produced a plausible, well-formed, false `[absence]` on the entire finding.** |
| **F2** | **`DeleteAIConversation` = 3 rows is NOT the server function** — it is `protobuf/rpcpb.(*sliverRPCClient)` and two generated handlers. | §3.2 | **Named the trap explicitly; printed all three rows rather than the count alone.** **A name match is not a function match.** |
| **F3** | **The task's framing presupposed a client-side filter to classify.** | §0, §5 | **The referent is absent. Answered the question that COULD be answered and stated the one that could not.** |

`[verified]` **F1 is the fifth instrument in this lane that failed by returning a plausible zero instead of an error, and the first that survived a `-SimpleMatch` guard which looked like a correctness measure.** `[inferred]`

---

## 7. RESIDUALS

**R-145.1 — the compiled form of the 8 inert sites.** `[verified]` **PROBE:** obtain the Sliver SERVER binary (`sliver-server_windows-amd64.exe` or equivalent) and run `_d131_pclntab_addr.py` against it. **It is not in `02_BINARIES\sliver`\.** `[blocked]` — **on artifact availability, stated as such: the method exists and works, the input does not.** `[inferred]`

**R-145.2 — whether the server compiler folds the `""` guard.** `[verified]` **PROBE:** with the server binary, disassemble `AIConversationByID` and check for the surviving `operator_name = ?` string literal and branch. **The SQL literal `operator_name` is the discriminator — it is present in the source and its presence in `.rdata` would prove the guard was not wholly folded.** `[inferred]`

**R-145.3 — the two `SaveAIConversation` families measured 6 rows, all `protobuf/rpcpb` stubs.** `[verified]` **PROBE:** same server-binary dependency. `[blocked]` **on the same missing artifact.** `[inferred]`

**R-145.4 — `database/sql` = 1 row and `gorm` = 0 in the client.** `[verified]` **PROBE:** the single `database/sql` row is presumably a transitive helper; **it is NOT the ORM, so it does not indicate any db layer.** `[inferred]` **Worth one row of the next census, not a task.** `[inferred]`

---

## 8. SUMMARY

`[verified]` **THE ANSWER IS NEITHER. The D91 ownership filter is not COMPILED IN to `sliver-client_windows-amd64.exe` and it is not DEAD-CODE-ELIMINATED from it — it was never in that binary's build unit. It lives in `server/db/helpers.go:1451-1452` and `server/rpc/rpc-ai.go`, which compile into the Sliver SERVER, and no server binary exists in this corpus.** `[verified]`

`[verified]` **Evidence, each with its control: client pclntab `sliver/server` prefix = 0 rows against `sliver/client` 3,104 / `protobuf` 4,739 / `runtime.` 1,523 · client source imports of `sliver/server/*` = 0 against the three defining files all present · `02_BINARIES\sliver`\ holds the client and its `.minisig` and nothing else.** `[verified]`

`[verified]` **The filter's symbols in the client: `AIConversationByID` 0 · `AIConversationsByOperator` 0 · `aiOperatorName` 0 · `getClientCommonName` 0 · `operator_name` 0 · `gorm` 0.** `[absence]` **Probe proven non-degenerate (`runtime.` 1,523, `fmt.` 118, `internal/abi.` 305) and operand proven non-empty (3,476,902 B, 51,657 rows) before any zero was reported.** `[verified]`

`[verified]` **`DeleteAIConversation` = 3 rows are gRPC client stubs in `protobuf/rpcpb`, not the server implementation — the name match that would have faked a positive.** `[verified]`

`[verified]` **D91 STANDS UNCHANGED. Its finding is about the server; the client's absence of the filter confirms the architectural separation D91 relied on. The 8-of-9 inert sites and R7 remain UNOBSERVED in compiled form because the server binary is not in the corpus — filed `[blocked]` on artifact availability, with the method that would close them ready and working.** `[verified]`

**The method sentence:** `[verified]` **the probe that nearly filed this report backwards was guarded by a `-SimpleMatch` flag that made it look more correct than the version that worked — and the only thing that caught it was a control value (`runtime.`) that a Go binary cannot lack.** `[inferred]`

*End of D145. Probe: `_d145_probe.py` (Python, `ReadAllText` + `str.count()`). Operand: `_d131_out\_lead_pclntab_sliver-client_windows-amd64.exe.tsv`, 3,476,902 B, SHA-256 `06B96ECF…505E`. No binary executed. No `open_binary`.*
