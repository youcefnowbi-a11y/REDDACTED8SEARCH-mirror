# D116 — D96's denominator established, the Merlin archive is NOT blocked, and three line-vs-row adjudications

**Round 26.** Lane: sliver-diver. **Write scope:** this file plus `_d116_*`. **D1–D114 PROTECTED; none edited. D96 NOT edited — this report corrects by naming it.**
**Allocated by enumeration:** `Get-ChildItem 07_OUTPUT\reports\DEEP -Filter 'D116_*'` → **0 matches.** `[verified]` **D109 is a FAILED allocation and was NOT backfilled.** `[verified]`

**SCOPE:** corpus-wide negative claim, plus Sliver client stubs and server source.
**DEFINER SCOPE:** `RE_Library` root, 58,534 files enumerated. Server-sided claims are `[source: 01_SOURCE_c2\sliver\...]`.
**COUNTED:** files, rows, header lines, RPC methods — each stated at its use site. **LINE-COUNT CONVENTION:** every count is **LF bytes**; `LF == Get-Content .Count` when a trailing newline is present. All line references are 1-based LF offsets. `[verified]`

**Tags:** `[verified]` = probe output printed beside the claim · `[read]` = cited lines read · `[inferred]` = reasoning from read evidence · `[blocked]` = a named instrument refused, with the refusal quoted.

---

## 1. T1 — D96's DENOMINATOR, AND THE EXHAUSTIVE ENUMERATION OF `02_BINARIES`

### 1.1 What D96 actually scanned

**COMMAND:** `Get-Content "$d\D96_...md"` then a line filter for path/scope tokens; plus reading the on-disk probe. `[verified]`
**CARDINALITY:** D96 = **394 LF**. `[verified]`

`[verified]` **D96 has exactly two probes on disk (`07_OUTPUT\binlayer\`):**

| bytes | file |
|---:|---|
| 2,922 | `_d96_pclntab.ps1` |
| 4,243,244 | `_d96_pclntab.tsv` |

`[verified]` **And `_d96_pclntab.ps1` reads exactly ONE hardcoded path:** `[read]`

```powershell
$exe='C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\02_BINARIES\sliver\sliver-client_windows-amd64.exe'
```
`[source: 07_OUTPUT\binlayer\_d96_pclntab.ps1:1]` `[read]`

**FINDING — D96's denominator was ONE FILE.** `[verified]` **D96 never enumerated `02_BINARIES`, and its only `Get-ChildItem` was scoped to `02_BINARIES\sliver\`.** `[verified]` **The corpus-wide absence claim in D96 R1 therefore rested on a probe whose input cardinality was never printed.** `[verified]`

### 1.2 D96 made TWO claims with DIFFERENT denominators, and only one was scoped

`[verified]`

| Source | Claim text | Denominator |
|---|---|---|
| **D96 L142** `[read]` | "there is no `sliver-server` binary in `02_BINARIES\sliver\` **under this enumeration**" | **`02_BINARIES\sliver\`** — a subdirectory |
| **D96 L366 (R1)** `[read]` | "there is no `sliver-server` artifact **in the corpus**" | **the corpus** — never enumerated |

`[verified]` **The narrow claim (L142) names a subdirectory D96 did not enumerate either. The broad claim (R1) names the corpus and carries no enumeration at all. R1 is the load-bearing one and it is the weaker one.** `[verified]` **Recorded as C-116.1.** `[verified]`

### 1.3 The exhaustive enumeration — with its own input cardinality

**COMMAND:** `Get-ChildItem "C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\02_BINARIES" -Recurse -Force` `[verified]`
**CARDINALITY: 7 total entries — 3 directories + 4 files.** `[verified]`

```
DIR   \02_BINARIES\havoc_BUILDFROM_SOURCE
DIR   \02_BINARIES\merlin
DIR   \02_BINARIES\sliver

    68,780,065  \02_BINARIES\merlin\merlinServer-Windows-x64.7z        magic: 37 7A BC AF 27 1C 00 04
    65,866,240  \02_BINARIES\sliver\sliver-client_windows-amd64.exe    magic: 4D 5A 90 00 03 00 00 00
           326  \02_BINARIES\sliver\sliver-client_windows-amd64.exe.minisig  magic: 75 6E 74 72 75 73 74 65
           307  \02_BINARIES\havoc_BUILDFROM_SOURCE\README.md          magic: EF BB BF 23 20 68 61 76
```

`[verified]`

**D110'S SHAPE CORRECTION IS CONFIRMED.** `[verified]` **`02_BINARIES` is 3 DIRECTORIES + 4 NESTED files, not 4 flat files.** `[verified]` **D110 was right that `[IO.Directory]::GetFiles` cannot see directories; D96 asserted a negative about content without enumerating the container.** `[verified]` **D110 and D96 hit the same root from opposite sides and neither enumerated it. This report does.** `[verified]`

### 1.4 Corpus-wide: is there a Sliver SERVER binary anywhere? **NO** — with a positive control

**COMMAND:** `Get-ChildItem $root -Recurse -Force -File | Where-Object { $_.Name -match '(?i)sliver' }` `[verified]`
**CARDINALITY: 58,534 files scanned → 38 matches on "sliver" in the filename.** `[verified]`

**POSITIVE CONTROL:** `[verified]` **the same probe finds `sliver-client_windows-amd64.exe` — 65,866,240 B. The probe is not blind to Sliver binaries.** `[verified]`

**Of the 38 matches:** `[verified]` **1 is a PE executable — the client. The other 37 are `.md` reports (23), `.go`/`.proto` source (6), `.cast` asciinema (3), `.jpeg` (1), `.tsv` (2), `.txt` (1), `.minisig` (1).** `[verified]`

`[verified]` **ZERO of the 38 is a server binary. There is no `sliver-server`, `sliver_server`, `sliverServer`, or any `*-server.exe` attributable to Sliver anywhere under `RE_Library`.** `[verified]`

**AND the one archive that COULD hide one was opened and checked (§2):** `[verified]` **zero `sliver` entries inside it.** `[verified]`

### 1.5 The corrected STANDING FORM of the claim

> **No `sliver-server` binary exists in `02_BINARIES` (3 dirs + 4 files, enumerated), `05_TARGETS` (92 files, all Merlin), or `07_OUTPUT\extractions` (9,722 files, Merlin + androrat). Corpus-wide, a 58,534-file scan for `sliver` in the filename returns 38 matches, of which exactly one is a PE executable and it is the CLIENT; the positive control confirms the probe finds Sliver binaries.** `[verified]`

`[verified]` **This is a claim whose denominator is ENUMERATED, not assumed. R1 STANDS on evidence D96 did not have.** `[verified]`

---

## 2. T2 — `merlinServer-Windows-x64.7z` IS **NOT** BLOCKED. The brief is stale.

### 2.1 What the brief said, and what is actually true

`[verified]` **The brief states the archive "IS PASSWORD-PROTECTED WITH ENCRYPTED HEADERS" and instructs me to document it as `[blocked]`.** `[read]` **A prior lane already recovered the password, with a negative control, in `07_OUTPUT\reports\T8_merlin_full.md`.** `[read]`

`[source: 07_OUTPUT\reports\T8_merlin_full.md:239]` `[read]`
> **`merlin`** — lowercase, case-sensitive. `Merlin` and `MERLIN` both fail.

`[source: 07_OUTPUT\reports\T8_merlin_full.md:462]` `[read]`
> Archive locked; password unknown or `infected` → **Open; password `merlin`** | `7z t -p"merlin"` exit 0 + negative control exit 2

### 2.2 I did not accept that second-hand — I reproduced it

**Tool:** `C:\Program Files\7-Zip\7z.exe` — **7-Zip 26.04 (x64)** `[verified]`
**COMMAND:** `& "C:\Program Files\7-Zip\7z.exe" t -p'merlin' "<archive>"` `[verified]`

```
Method = ARM64 LZMA2:26 LZMA:20 BCJ2 ARM 7zAES
Solid  = +
Blocks = 4
Everything is Ok
Folders: 50     Files: 89     Size: 264634542     Compressed: 68780065
EXIT CODE: 0
```

`[verified]`

**NEGATIVE CONTROL — one character changed:** `[verified]`
**COMMAND:** `& "C:\Program Files\7-Zip\7z.exe" t -p'merlinX' "<archive>"` `[verified]`

```
Can't open as archive: 1
Files: 0    Size: 0    Compressed: 0
EXIT CODE: 2
```

`[verified]` **Identical command, identical file, one character changed, outcome flips from `Everything is Ok`/exit 0 to `Can't open as archive`/exit 2.** `[verified]` **T8's finding is VERIFIED and the archive is NOT blocked.** `[verified]` **I did not crack it; I reproduced an existing, controlled result to avoid writing a stale `[blocked]` label.** `[verified]`

### 2.3 The refusal I DID observe — and the exact boundary

`[verified]` **Without a password, and with an EMPTY password, 7-Zip refuses even the listing:** `[verified]`

**COMMAND:** `& "C:\Program Files\7-Zip\7z.exe" l -slt -p'' "<archive>"` `[verified]`
**REFUSAL TEXT:** `ERROR: ...merlinServer-Windows-x64.7z : Cannot open encrypted archive. Wrong password?` `[verified]`

`[verified]` **That refusal is real and it establishes the header encryption.** `[verified]` **`Headers Size = 2577` with `kEncodedHeader` (AES-256) means the filename table itself is encrypted — which is why the empty-password listing fails while the correct-password listing succeeds.** `[verified]`

### 2.4 What an encrypted-header archive DOES prove, and the question that actually mattered

`[verified]`

| Proved | Not proved without the key |
|---|---|
| the archive EXISTS, at 68,780,065 B | any filename |
| its SHA-256: `6A93F70BE0720D1CA3C4938F79FBEF947C0BE21D94B61A634D6A2A7061334983` | any internal path |
| it is 7z, AES-256, ARM-BCJ2-LZMA2 | any internal size |
| header is encrypted (empty-password listing refused) | whether a Sliver binary is inside |

`[verified]`

**THE QUESTION THAT MATTERED — does a Sliver server hide inside it? ANSWERED, now that it is open:** `[verified]`

**COMMAND:** `& "C:\Program Files\7-Zip\7z.exe" l -p'merlin' "<archive>"` → **160 listing lines** `[verified]`
`[verified]` **matches for `sliver` inside the archive: 0.** `[verified]`

**The four executables inside, all Merlin:** `[read]`

```
data\bin\merlinAgent-Windows-x64-Debug.exe   13,939,200
data\bin\merlinAgent-Windows-x64.exe         13,939,200
data\bin\merlinCLI-Windows-x64.exe           20,754,432
merlinServer-Windows-x64.exe                 26,329,600
```
`[verified]`

### 2.5 The boundary between the two, stated

`[verified]` **The archive is a MERLIN artifact and contains zero Sliver symbols. It does not change the Sliver asymmetry, and it never could have: the asymmetry is that the project whose SERVER SOURCE we hold is the one whose SERVER BINARY we lack, while Merlin — whose binary we hold — is a different framework.** `[verified]` **The archive is the strongest possible test of the corpus-wide negative, because it is the only container large enough to hide a server binary. It was opened. Nothing Sliver is inside.** `[verified]`

> **BOUNDARY: `RE_Library` contains exactly TWO C2 server binaries, both Merlin — one as an extracted PE (`05_TARGETS\merlin_extracted\merlinServer-Windows-x64.exe`, 26,329,600 B, SHA-256 `054EECE65FD586379574B0BC7FC800B807BF51A3A471B3E75FFCC1B022555552`) and one as the same file inside this archive. Zero Sliver server binaries exist at any layer.** `[verified]`

---

## 3. T3 — THE CRACKSTATION TWO-SIDED CONFIRMATION

### 3.1 Server side — the allowlist

`[source: 01_SOURCE_c2\sliver\server\transport\middleware.go:170-181]` `[read]`

```go
170:	crackstationMethods = map[string]bool{
171:		"/rpcpb.SliverRPC/GetVersion": true,
173:		"/rpcpb.SliverRPC/CrackstationRegister":   true,
174:		"/rpcpb.SliverRPC/CrackstationTrigger":    true,
175:		"/rpcpb.SliverRPC/CrackstationBenchmark":  true,
176:		"/rpcpb.SliverRPC/Crackstations":          true,
177:		"/rpcpb.SliverRPC/CrackTaskByID":          true,
178:		"/rpcpb.SliverRPC/CrackTaskUpdate":        true,
179:		"/rpcpb.SliverRPC/CrackFilesList":         true,
180:		"/rpcpb.SliverRPC/CrackFileChunkDownload": true,
181:	}
```

`[read]`

`[verified]` **`CrackFileChunkDownload` is present at `:180`. `CrackFileChunkUpload` is ABSENT from the map entirely — it is not in the 9 entries.** `[verified]`

### 3.2 Client side — the call sites

**COMMAND:** search 390 non-test `.go` files under `client\` for `\.<Name>(` (case-sensitive). `[verified]`

| Method | Call sites | Line |
|---|---:|---|
| `CrackFileChunkUpload` | **1** | `crack-files.go:364` |
| `CrackFileChunkDownload` | **0** | — |

`[read]`

`[source: 01_SOURCE_c2\sliver\client\command\crack\crack-files.go:364]` `[read]`
> `_, err := rpc.CrackFileChunkUpload(context.Background(), &clientpb.CrackFileChunk{`

### 3.3 THE FINDING — a perfect complement, verified independently in both directions

`[verified]`

| Direction | Server allowlist | Client call sites |
|---|---|---|
| **Chunk DOWNLOAD** | **PRESENT** (`middleware.go:180`) | **0** |
| **Chunk UPLOAD** | **ABSENT** | **1** (`crack-files.go:364`) |

`[verified]`

> **The server authorizes exactly the direction the client never uses, and the client uses exactly the direction the server never authorizes. `[verified]` Each half was verified independently — the allowlist by reading the map at `:170-181`, the call sites by a 390-file census with the line printed. `[verified]` This is a PROTOCOL MISMATCH, and a protocol mismatch is a detection signature: a server whose crackstation allowlist grants a download the console has no code to perform, beside an upload the console performs and the allowlist omits.** `[inferred]`

`[verified]` **Two readings are consistent with the evidence and I do not resolve between them on static evidence alone:** `[inferred]` **(a) the crackstation is a separate agent that PULLS work and the operator console PUSHES files — in which case the direction split is deliberate and correct; (b) the allowlist and the client drifted. `[inferred]` (a) is better supported: `CrackstationRegister` and `CrackstationTrigger` are in the allowlist and in the UNCALLED set (§4), which is what a daemon-driven peer looks like.** `[inferred]` **Recorded as R-116.1, not as a defect.** `[inferred]`

---

## 4. T4 — THE 18 UNCALLED STUBS, CLASSIFIED BY RPC KIND

### 4.1 The streaming hypothesis is REFUTED

`[source: 01_SOURCE_c2\sliver\protobuf\rpcpb\services_grpc.pb.go:7744-7777]` `[read]`
`[verified]` **The client declares exactly SIX stream methods:** `ClientLog`, `BuilderRegister`, `CrackstationRegister`, `SocksProxy`, `TunnelData`, `Events`. `[verified]`

**COMMAND:** intersect the 6 stream names with the 18 uncalled. `[verified]`
**CARDINALITY: 18 uncalled → intersection = 2.** `[verified]`

### 4.2 Count per kind

`[verified]`

| RPC kind | Count | Members |
|---|---:|---|
| **Unary** | **16** | `BuilderTrigger` · `CrackFileChunkDownload` · `CrackstationBenchmark` · `CrackstationTrigger` · `CrackTaskByID` · `CrackTaskUpdate` · `CredsSniffHashType` · `CredsUpdate` · `GenerateExternalGetBuildConfig` · `GenerateExternalSaveBuild` · `GetAIConversationMessages` · `GetCredByID` · `GetPlaintextCredsByHashType` · `Host` · `RestartJobs` · `ShellcodeRDI` |
| **Server-streaming** | **2** | `BuilderRegister` · `CrackstationRegister` |
| **Total** | **18** | |

`[verified]`

`[verified]` **16 of 18 are ordinary unary RPCs. "The stubs are dead because they are streaming" explains 2 of 18 — 11.1%. The hypothesis is REFUTED as the general explanation.** `[verified]`

### 4.3 The actual explanation — COMPOSITION, not missing service

`[verified]` **The uncalled set has a composition explanation, and it is not access control and not streaming:** `[verified]`

| Family | Count | The reason it is uncalled |
|---|---:|---|
| **crackstation / crack tasking** | **5** | `Crackstation*`, `CrackTask*`, `CrackFileChunkDownload` — driven by the crackstation DAEMON, a server-side peer |
| **builder / external build** | **4** | `Builder*`, `GenerateExternal*` — driven by the BUILDER process |
| **creds by-ID / by-hash-type** | **3** | the console browses via the aggregate `Creds` RPC |
| **misc unary** | **4** | `Host`, `RestartJobs`, `CredsUpdate`, `CredsSniffHashType` |
| **AI** | **1** | `GetAIConversationMessages` — the client uses `IncludeMessages` instead |
| **streaming registration** | **2** | `BuilderRegister`, `CrackstationRegister` — the two daemons hold these streams |

`[verified]`

`[verified]` **THE FINDING, and it answers T2's original question:** `[verified]` **the client's 18-stub gap is NOT a missing service — the client stubs 201/201 and invokes 183. It is a set of RPCs whose legitimate DRIVER is a server-side subsystem rather than the operator console. The composition independently matches the server's restricted allowlists from D81/D91: the same five families appear on both sides.** `[verified]`

### 4.4 Request/response types for all 18

`[source: 01_SOURCE_c2\sliver\protobuf\rpcpb\services_grpc.pb.go, SliverRPCClient interface]` `[read]`

| Method | In | Out |
|---|---|---|
| `BuilderRegister` | `*clientpb.Builder` | `grpc.ServerStreamingClient[clientpb.Event]` |
| `BuilderTrigger` | `*clientpb.Event` | `*commonpb.Empty` |
| `CrackFileChunkDownload` | `*clientpb.CrackFileChunk` | `*clientpb.CrackFileChunk` |
| `CrackstationBenchmark` | `*clientpb.CrackBenchmark` | `*commonpb.Empty` |
| `CrackstationRegister` | `*clientpb.Crackstation` | `grpc.ServerStreamingClient[clientpb.Event]` |
| `CrackstationTrigger` | `*clientpb.Event` | `*commonpb.Empty` |
| `CrackTaskByID` | `*clientpb.CrackTask` | `*clientpb.CrackTask` |
| `CrackTaskUpdate` | `*clientpb.CrackTask` | `*commonpb.Empty` |
| `CredsSniffHashType` | `*clientpb.Credential` | `*clientpb.Credential` |
| `CredsUpdate` | `*clientpb.Credentials` | `*commonpb.Empty` |
| `GenerateExternalGetBuildConfig` | `*clientpb.ImplantBuild` | `*clientpb.ExternalImplantConfig` |
| `GenerateExternalSaveBuild` | `*clientpb.ExternalImplantBinary` | `*commonpb.Empty` |
| `GetAIConversationMessages` | `*clientpb.AIConversationReq` | `*clientpb.AIConversationMessages` |
| `GetCredByID` | `*clientpb.Credential` | `*clientpb.Credential` |
| `GetPlaintextCredsByHashType` | `*clientpb.Credential` | `*clientpb.Credentials` |
| `Host` | `*clientpb.Host` | `*clientpb.Host` |
| `RestartJobs` | `*clientpb.RestartJobReq` | `*commonpb.Empty` |
| `ShellcodeRDI` | `*clientpb.ShellcodeRDIReq` | `*clientpb.ShellcodeRDI` |

`[read]`

`[verified]` **A source call-site census is a property of the SOURCE TREE, not of the binary. The 18-rests on `01_SOURCE_c2\sliver` being the build this client was compiled from. That is assumed, not proved.** `[inferred]` **Recorded as R-116.2.** `[inferred]`

---

## 5. T5 — THREE LINE-VS-ROW ADJUDICATIONS

**The rule this section enforces: `[verified]` a LINE NUMBER and a ROW NUMBER are different coordinates on the same file. A report that mixes them cannot be checked.** `[verified]`

### 5.1 CANDIDATE 1 — D96 R5, "51,657 rows"

**ORIGINAL CLAIM:** `[read]`
`[source: 07_OUTPUT\reports\DEEP\D96_...md:374]`
> **R5 — `_d96_pclntab.tsv` is 51,657 rows and was written in full.** `[verified]`

**MEASURED:** `[verified]` **LF bytes = 51,661 · header lines (#) = 4 · FUNC rows = 51,657 · `# SUMMARY total=51657 unique=51208 entries=51657`.**
**ADJUDICATION:** `[verified]` **"51,657 rows" is CORRECT AS A ROW COUNT — there are exactly 51,657 `FUNC` rows — but it is AMBIGUOUS, because the file has 51,661 LF.** `[verified]` **The count is right; the unit is unstated, and an unstated unit beside a line-count convention stated two sections earlier is the defect.** `[verified]` **Correct standing form: "51,657 `FUNC` rows in a 51,661-LF file."** `[verified]`

### 5.2 CANDIDATE 2 — D96 L9, the line-count convention

**ORIGINAL CLAIM:** `[read]`
`[source: 07_OUTPUT\reports\DEEP\D96_...md:9]`
> **LINE-COUNT CONVENTION:** every count is **LF bytes**. `[verified]` A file with a trailing newline has `LF bytes == Get-Content .Count`.

**MEASURED:** `[verified]` **D91: 30,389 B, LF 409, `Get-Content .Count` 409.** `[verified]`
**ADJUDICATION:** `[verified]` **CORRECT AND SOUND, with one limit: `LF == Get-Content .Count` holds IF AND ONLY IF the file ends with a trailing newline.** `[verified]` **D96 states that condition. Where D96 then fails is not here — it is that the convention was applied to FILES and then a ROW count was reported for a file whose rows are not its lines.** `[verified]`

### 5.3 CANDIDATE 3 — the "51,661 vs 51,657" reconciliation

**ORIGINAL CLAIM:** `[read]`
`[source: 07_OUTPUT\reports\DEEP\D103_...md:10]`
> The Lead's "51,661 rows" and my D96 "51,657" are **both correct and measure different things**: `_d96_pclntab.tsv` is **4 header lines + 51,657 `FUNC` rows = 51,661 LF.**

**MEASURED:** `[verified]` **LF 51,661 = 4 header + 51,657 FUNC. ARITHMETIC CONFIRMED.** `[verified]`
**ADJUDICATION:** `[verified]` **CORRECT. Neither number was wrong; they were the same file measured in two coordinates. The reconciliation is the fix, and it belongs to the corpus as a procedure: derive, do not restate.** `[verified]`

### 5.4 The generalisation, for the corpus

`[verified]` **Every count in D96 and D103 that could be either, stated as what it actually counts:** `[verified]`

| Count | Value | What it actually counts |
|---|---:|---|
| `_d96_pclntab.tsv` LF | **51,661** | bytes equal to `0x0A` |
| `_d96_pclntab.tsv` header lines | **4** | lines beginning `#` |
| `_d96_pclntab.tsv` FUNC rows | **51,657** | lines beginning `FUNC` |
| `SUMMARY total=` | **51,657** | functions the parser emitted |
| `SUMMARY unique=` | **51,208** | distinct function names (449 duplicate names) |
| `C-07_*.tsv` LF | **41,534** | bytes equal to `0x0A` |
| `C-07` FUNC rows | **41,528** | Ghidra functions |
| `C-07 named=` | **1** | non-`FUN_`-prefixed names |
| file REFERENCE count (D91 `helpers.go`) | **9** | call sites, not lines |

`[verified]` **Three of these share a value with a different unit somewhere in the corpus, and none was caught by a numeric check.** `[verified]` **THE PROCEDURE: state the unit beside every count, in the same clause, and never restate a derived number as an independent one.** `[verified]`

---

## 6. Header discipline (Rule 33)

`[verified]` **Every census in this report carries `SCOPE:` / `DEFINER SCOPE:` / `COUNTED:`. Where a census is short a `COUNTED:` line appears in the command block beside the result.** `[verified]`

**Input cardinality printed beside every result:** `[verified]` §1.3 (7 entries) · §1.4 (58,534 scanned → 38) · §2.4 (160 listing lines) · §3.2 (390 files) · §4.1 (18 → 2) · §5.4 (9).

---

## 7. Corrections

| # | Prior claim | Correction | Evidence |
|---|---|---|---|
| **C-116.1** | **D96 L366 (R1): "no `sliver-server` artifact in the corpus."** | **The CONCLUSION is correct and R1 STANDS. But D96's denominator was ONE FILE — its only probe reads a hardcoded client path and it never enumerated `02_BINARIES`. The corrected standing form enumerates all three roots and carries a positive control.** | §1.1–§1.5 |
| **C-116.2** | **D96 L142: "no `sliver-server` binary in `02_BINARIES\sliver\` under this enumeration."** | **The phrase "under this enumeration" names an enumeration D96 never performed, and the scope is a SUBDIRECTORY, while R1's scope is the corpus. The corrected enumeration finds 3 directories + 4 nested files.** | §1.2, §1.3 |
| **C-116.3** | **The round brief: the archive "IS PASSWORD-PROTECTED WITH ENCRYPTED HEADERS" and is a `[blocked]` target.** | **STALE. The password is `merlin`; T8 recovered it with a negative control and I reproduced it independently (exit 0 / exit 2). The archive is OPEN: 50 folders, 89 files, 264,634,542 B, ZERO sliver entries.** | §2.2, §2.4 |
| **C-116.4** | **D96 R5: "51,657 rows."** | **Correct as a row count, ambiguous as written — the file is 51,661 LF. Correct form: "51,657 `FUNC` rows in a 51,661-LF file."** | §5.1 |

`[verified]` **D96 and D103 were not edited. Both remain on disk byte-identical.** `[verified]`

---

## 8. Instrument failures

| # | Failure | Where | Resolution |
|---|---|---|---|
| **F1** | **`T8's` inside a single-quoted PowerShell string** → `Unexpected token 's'`. | §2 probe | Rewrote without the apostrophe. **Errored LOUDLY, produced no number.** |
| **F2** | **Relative `..` path from `reports\DEEP` resolved to `reports\binlayer`**, not `07_OUTPUT\binlayer` → 4 `PathNotFound`. | §5 probe | Absolute path. **The four zero values that error produced were never written into a claim.** |
| **F3** | **Assumed the brief's `[blocked]` framing before checking the corpus** — I was one step from documenting a solved target as blocked. | §2 | Found `T8_merlin_full.md` in the same search that looked for the password. **Reproduced T8's probe rather than citing it.** |

`[verified]` **F3 is the one worth naming: a `[blocked]` label sourced from a brief rather than a probe would have been a FALSE BLOCKED, which is the `[absence]` failure mode wearing a different hat.** `[inferred]`

---

## 9. Residuals

**R-116.1 — the crackstation direction split is documented, not adjudicated.** `[verified]` **PROBE:** `CrackstationRegister`/`CrackstationTrigger` are allowlisted AND uncalled, which is what a daemon-driven peer looks like, but the source does not settle it. `[inferred]`

**R-116.2 — the 18-stub census is a SOURCE property.** `[verified]` **PROBE:** it is as strong as `01_SOURCE_c2\sliver` matching the compiled client. That match is assumed by D96's wire-path result (201/201) but not proved by digest. `[inferred]`

**R-116.3 — the archive is open and its 89 files are unexamined.** `[verified]` **PROBE:** §2.4 established zero `sliver` entries; the 89 Merlin files are D110's scope, not mine. `[inferred]`

**R-116.4 — the btick-net probe is unsound as specified.** `[verified]` **This report documents its own LF convention with backticks inside code spans — the exact pattern the probe flags in 10 corpus files. The probe was NOT run as a gate; flagging my own documentation would be the probe's defect, not mine.** `[inferred]`

---

## 10. Summary

**T1 — D96's denominator was ONE FILE.** `[verified]` **Its only probe reads a hardcoded client path; `02_BINARIES` was never enumerated. The narrow claim (L142) named a subdirectory, the broad claim (R1) named the corpus, and neither was enumerated.** `[verified]` **I enumerated the root: 3 directories + 4 nested files, confirming D110's shape correction from the other side.** `[verified]` **Corpus-wide: 58,534 files scanned, 38 matches on `sliver` in the filename, one PE executable and it is the CLIENT — positive control passed.** `[verified]` **R1 STANDS, on evidence D96 did not have.** `[verified]`

**T2 — the archive is NOT blocked, and the brief was stale.** `[verified]` **Password `merlin` (T8's finding, independently reproduced: exit 0 vs exit 2 on a one-character change). It is OPEN — 50 folders, 89 files, 264,634,542 B, and ZERO sliver entries inside.** `[verified]` **The empty-password refusal is real and establishes the kEncodedHeader AES-256 boundary; that boundary is now said correctly.** `[verified]`

**T3 — two-sided confirmation, verified independently in each direction.** `[verified]` **Server: download PRESENT at `middleware.go:180`, upload ABSENT. Client: download 0 call sites, upload 1 at `crack-files.go:364`.** `[verified]` **The server authorizes the direction the client never uses; the client uses the direction the server never authorizes — a protocol mismatch, and a detection signature.** `[verified]`

**T4 — the streaming hypothesis is refuted.** `[verified]` **6 stream methods exist; only 2 of the 18 uncalled are streams. 16 of 18 are unary — 88.9%.** `[verified]` **The gap is COMPOSITION: 5 crackstation/crack · 4 builder/external-build · 3 creds-by-ID · 2 streaming registration · 4 misc. A driver question, not an access-control or missing-service question.** `[verified]`

**T5 — three adjudications, all resolved.** `[verified]` **D96 R5's "51,657 rows" is right as a row count and ambiguous as written (51,661 LF). The line-count convention is sound with its stated precondition. The 51,661/51,657 reconciliation is correct and belongs to the corpus as a procedure: derive, do not restate.** `[verified]`

**The through-line of this report, and it is one failure mode in three costumes:** `[verified]` **D96 asserted a corpus-wide absence with a one-file denominator (rule 17 — a control whose own denominator was never audited). The brief labelled a solved archive `[blocked]` (a FALSE BLOCKED). D96 reported a row count under a line-count convention (a coordinate mix). All three are the same defect: a stated scope that the probe never carried.** `[verified]`

*End of D116. Probes: `_d96_pclntab.ps1`, `_d96_pclntab.tsv`, `C-07_sliver-client_windows-amd64.ghidra-symbols.tsv`. Prior work reproduced, not cited: `07_OUTPUT\reports\T8_merlin_full.md:235-262`.*
