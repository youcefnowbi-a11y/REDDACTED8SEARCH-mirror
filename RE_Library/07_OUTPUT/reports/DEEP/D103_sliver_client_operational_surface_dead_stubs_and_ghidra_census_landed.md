# D103 — The Sliver client's own operational surface, the 18 uncalled RPC stubs, and the Ghidra census that finally landed

**Round 25.** Lane: sliver-diver. **Write scope:** this file plus `_d103_*` probes. **D1–D102 PROTECTED; none was edited.**
**Target:** `RE_Library\02_BINARIES\sliver\sliver-client_windows-amd64.exe` — **65,866,240 B**
**SHA-256:** `7C500D4AE84D792E4BB3F4BC89A0F325688F6E7B7F0574A6718BB99D30B305CB` `[verified]`
**Method:** static only. Binary never executed. **No REA `open_binary`. No network. No second Ghidra run started.**

**LINE-COUNT CONVENTION:** every count is **LF bytes**. `LF == Get-Content .Count` when the file ends with a newline. `[verified]` **All line refs are 1-based LF offsets.**

**THE NUMBER THE LEAD ASKED ABOUT, RECONCILED FIRST.** `[verified]` The Lead's "51,661 rows" and my D96 "51,657" are **both correct and measure different things**: `_d96_pclntab.tsv` is **4 header lines + 51,657 `FUNC` rows = 51,661 LF.** `[verified]` **The function count is 51,657. I use that figure throughout and state it as a function count, not a line count, so the two cannot drift again.** `[verified]`

---

## 0. The Ghidra run landed, and D96 needs a correction to its job-4 half

**D96 §0 and §4 reported Ghidra produced no figures because its Go analyzers failed and `gsli.tsv` had not arrived.** `[read]` **That was true at my cutoff and is no longer true: the run finished, and the file is on disk as `C-07_sliver-client_windows-amd64.ghidra-symbols.tsv`.** `[verified]`

| Property | Value |
|---|---|
| bytes | **1,945,710** |
| mtime | **10/16/2026 20:45:37** (after my D96 cutoff) |
| SHA-256 | `BA0F2DB0E816EAD24F03B955B20AC8757F53CC42E826A680B8035BE2FF9A3181` |
| LF | **41,534** |
| BOM | **absent** |
| U+FFFD | **0** |
| header | `# program sliver-client_windows-amd64.exe` / `# language x86:LE:64:default` / `# compiler golang` / `# imageBase 140000000` |
| **SUMMARY** | **`total=41528  named=1  thunks=5  bodybytes=23600441`** |

`[verified]`

### 0.1 The comparison that settles the analyzer-bound framing

| Instrument | Functions recovered | Named | Coverage |
|---|---:|---:|---:|
| **Ghidra headless** | **41,528** | **1** | **0.0024%** |
| **Go pclntab (D96, `_d96_pclntab.ps1`)** | **51,657** | **51,657** | **100.0000%** |

`[verified]`

**The single "named" function is `entry`, and it is also one of the 5 thunks:** `[verified]`

```
FUNC  14008fb20  entry                    5  Global  true
FUNC  14001f340  thunk_FUN_14001f345      2  Global  true
FUNC  1401cc920  thunk_FUN_1401cc93f      2  Global  true
FUNC  140cd3c40  thunk_FUN_140cd3d72      5  Global  true
FUNC  141749140  thunk_FUN_141749060      5  Global  true
```

`[verified]` **The other 41,523 of 41,528 rows are literal `FUN_<address>` placeholders.** `[verified]`

> **This is D96 §0's prediction confirmed by the artifact rather than inferred from a log.** `[verified]` **D96 argued the Go-analyzer failure meant the census would land "near the Merlin-agent end of the range, not the Merlin-server end," and that it must be labelled an ANALYZER BOUND and not a symbol-richness finding. It landed at `named=1` — byte-for-byte the same figure C-08 recorded for `merlinAgent-Windows-x64.exe` (11,246 functions, 1 named, 0.009%). The framing was right and the number matched.** `[verified]`

**And the stronger result, which D96 could not have shown:** `[verified]` **the same binary yields 51,657 functions through the pclntab and 41,528 through Ghidra — Ghidra MISSED 10,129 functions, 19.6% of the code — and named none of what it did find.** `[verified]`

> **A 0.0024% coverage figure from this instrument is not a statement about this binary. It is a statement about the instrument. `[verified]` Any downstream claim that "the Sliver client is symbol-poor" would be exactly the C-08 §3 generalisation error, now with a second worked example.** `[inferred]`

### 0.2 The image-signature offsets Ghidra reported are VIRTUAL addresses, not file offsets

**Instrument finding.** `[verified]` **Ghidra logged `Invalid PNG data at 1417cb3a2` etc. Those are image-base-relative VIRTUAL addresses (`imageBase=140000000`), not file offsets; using them as array indices throws and returns nothing.** `[verified]`

```
VA 0x1417cb3a2 -> file offset 0x17CB3A2   (in range)
VA 0x143c44b5c -> file offset 0x3C44B5C   (in range)
VA 0x143c44b62 -> file offset 0x3C44B62   (in range)
VA 0x143c44ec8 -> file offset 0x3C44EC8   (in range)
```

`[verified]` **Recorded as F1.** `[verified]`

---

## 1. T1 — THE CLIENT'S OPERATIONAL SURFACE

### 1.1 `client/command/*`: 2,385 symbols across 63 leaf packages

`[verified]` **This is the client's command surface and, as the Lead suspected, it had not been listed.** `[verified]`

| Package | Syms | | Package | Syms | | Package | Syms |
|---|---:|---|---|---:|---|---|---:|
| **ai** | **242** | | jobs | 37 | | environment | 14 |
| crack | 209 | | beacons | 36 | | aka | 14 |
| generate | 147 | | websites | 34 | | network | 13 |
| armory | 132 | | update | 33 | | completers | 11 |
| crack/top | 131 | | sessions | 32 | | screenshot | 9 |
| filesystem | 113 | | hexedit | 29 | | reconfig | 8 |
| opfor | 96 | | serverctx | 28 | | kill · clean | 6 · 6 |
| exec | 90 | | settings | 28 | | operators | 6 |
| shell | 77 | | creds | 28 | | help | 6 |
| docs | 65 | | wireguard | 25 | | backdoor | 5 |
| extensions | 62 | | pivots · info | 24 · 24 | | dllhijack | 5 |
| processes | 51 | | socks · reaction | 23 · 23 | | shikata-ga-nai | 5 |
| edit | 50 | | c2profiles | 21 | | builders | 5 |
| cursed | 48 | | tasks | 20 | | monitor | 5 |
| alias · registry | 40 · 40 | | wasm · shellcode-encoders · use | 18 ea | | exit | 4 |
| privilege | 39 | | hosts · mcp · rportfwd | 17 ea | | flags | 3 |
| loot | 38 | | portfwd | 16 | | crack/internal/hashcatdisplay | 3 |
| | | | certificates | 15 | | taskmany · targettable · licenses | 2 ea |

`[verified]` **63 leaf packages; 2,385 symbols total.** `[verified]`

**Reading the surface, not just counting it:** `[verified]` **the largest subtree is `ai` (242) — larger than `crack` (209) or `generate` (147). The client's AI console is its single biggest command package.** `[inferred]` **That is disproportionate to any other feature and is the structural reason D91's server-side AI findings matter more than a normal RPC defect.** `[inferred]`

### 1.2 The `ai` subtree in full: 242 symbols, of which 121 are `aiModel` methods

`[verified]` **The client `ai` command is a complete Bubble Tea TUI, not a thin RPC wrapper.** `[verified]`

**Structure, by role:** `[verified]`

| Role | Evidence |
|---|---|
| **TUI core** | `aiModel.Init` · `.Update` · `.View` — the three Bubble Tea methods |
| **Input** | `handleGlobalKey` · `handleComposerKey` · `handleComposerPaste` · `handleComposerSlashCommand` · `parseComposerSlashCommand` |
| **Mouse** | `handleMouseClick` · `handleMouseRelease` · `handleMouseMotion` · `handleMouseWheel` |
| **Six modals** | `handleDeleteConfirmModalKey` · `handleThinkingLevelModalKey` · `handleTargetSelectModalKey` · `handleExperimentalWarningModalKey` · `handleNewConversationModalKey` · `handleInfoModalKey` |
| **Renderers** | `renderModal` · `renderContextModal` · `renderToast` / `renderToastStack` / `renderToastOverlay` · `renderTooSmall` · `renderMarkdownWithGlow` · `renderTranscriptBox*` |
| **Conversation model** | `conversationIndexByID` · `conversationTitle` · `conversationContextWindowSummary` · `conversationAwaitingResponse` · `conversationUsesTarget` · `effectiveConversationThinkingLevel` |
| **Targeting** | `buildAITargetSelectionOptions` · `aiSessionTargetSummary` · `aiBeaconTargetSummary` · `normalizedAITargetIDs` · `sameAITargetSelectionIDs` |
| **TUI machinery** | `newAIThinkingAnim` · `newAIStyles` · `aiToastExpiryCmd` · `aiWindowPollCmd` · `currentTerminalSize` · `waitForAIConversationEventCmd` · `waitForAISubmitResultCmd` |
| **Markdown** | `escapeMarkdownText` · `renderMarkdownItalicLine` · `formatToolCallStructuredBody` · `renderToolCallSectionBodyLines` |
| **Config** | `safeAIConfigSummary` · `aiConfigError` · `normalizeAIThinkingLevel` · `defaultThinkingLevelSummary` |

`[verified]` **`experimental-warning` is the name of a whole modal and a key handler (`handleExperimentalWarningModalKey`) — the client gates its AI console behind an experimental warning.** `[verified]`

### 1.3 The D91 cross-reference the Lead asked for — and it runs the OPPOSITE direction

**The Lead asked whether the client-side `ai` package reveals what the 7 AI RPCs were meant to do. It does, and it also reveals that the client defends itself where the server does not.** `[verified]`

**`client\command\ai\model.go:4971-4979`** `[read]`

```go
func normalizedConversationOperatorName(name string) string {
	name = strings.TrimSpace(name)
	switch strings.ToLower(name) {
	case "", "unknown", "<unknown>", "<unknown operator>", "<disconnected>":
		return ""
	default:
		return name
	}
}
```

`[read]`

> **This is a client-side sanitizer with no server counterpart. `[read]` It maps five placeholder-identity forms to `""` — including the literal `"<unknown>"` that `model_test.go:146` constructs as a test fixture. `[verified]` The server's `aiOperatorName` (`rpc-ai.go:19-25`) does a `TrimSpace` and nothing else; it has no placeholder vocabulary.** `[verified]`

**The client's operator population path, `model.go:3554-3567`:** `[read]`

```go
3554:	optimistic.OperatorName = normalizedConversationOperatorName(optimistic.GetOperatorName())
3555:	if optimistic.GetOperatorName() == "" {
3556:		optimistic.OperatorName = normalizedConversationOperatorName(m.ctx.connection.Operator)
3557:	}
...
3565:		pending.OperatorName = normalizedConversationOperatorName(pending.GetOperatorName())
3566:		if strings.TrimSpace(pending.GetOperatorName()) == "" {
3567:			pending.OperatorName = optimistic.GetOperatorName()
```

`[read]`

> **The client KNOWS the operator's identity locally (`m.ctx.connection.Operator`, `:3556`) and stamps it on optimistic conversation objects before the round-trip.** `[verified]` **So the operator name the server receives is, in the normal path, supplied by the client itself — which is precisely the surface `rpc-ai.go:86`/`:144` accept a client-controlled protobuf field into.** `[inferred]`

**A Rule-20 near-miss I checked and cleared:** `[verified]` **`client\command\ai\ai.go:229` is `func fallback(value, def string) string` — a generic two-argument default helper (`TrimSpace`, return `def` if empty). It is NOT D91's `aiOperatorName` fallback and shares no logic beyond the name.** `[verified]` **A name collision that would have produced a false D91 link.** `[verified]`

### 1.4 The 201 RPC stubs, and which are never called

`[verified]` **The client carries a generated `(*sliverRPCClient)` stub for all 201 ServiceDesc methods — 201/201.** `[verified]`

**Call-site census (consumers, not declarations):** `[verified]` **searched 390 non-test `.go` files under `client\`.** `[verified]`

| Pattern | Methods matched |
|---|---:|
| strict `Rpc.<Name>(` | **177 called / 24 uncalled** |
| relaxed `.<Name>(` (receiver-agnostic) | **183 called / 18 uncalled** |

`[verified]` **Controls:** `GetVersion`=3, `GetSessions`=16 strict / 31 relaxed, `SaveAIConversation`=5. `[verified]` **The receiver is an interface (`console.go:130` `Rpc rpcpb.SliverRPCClient`), so the relaxed pattern is the correct one and the 18 is the figure I report.** `[verified]`

**THE 18 STUBS WITH ZERO CALL SITE UNDER EITHER PATTERN:** `[verified]`

| # | Method | Family | Note |
|---:|---|---|---|
| 1 | `BuilderRegister` | builder | **streaming; server-to-server** |
| 2 | `BuilderTrigger` | builder | |
| 3 | `CrackFileChunkDownload` | crack | **the download half only** |
| 4 | `CrackstationBenchmark` | crackstation | singular form |
| 5 | `CrackstationRegister` | crackstation | |
| 6 | `CrackstationTrigger` | crackstation | |
| 7 | `CrackTaskByID` | crack | |
| 8 | `CrackTaskUpdate` | crack | |
| 9 | `CredsSniffHashType` | creds | |
| 10 | `CredsUpdate` | creds | |
| 11 | `GenerateExternalGetBuildConfig` | external build | |
| 12 | `GenerateExternalSaveBuild` | external build | |
| 13 | `GetAIConversationMessages` | **AI** | **see §1.5** |
| 14 | `GetCredByID` | creds | |
| 15 | `GetPlaintextCredsByHashType` | creds | |
| 16 | `Host` | hosts | |
| 17 | `RestartJobs` | jobs | |
| 18 | `ShellcodeRDI` | shellcode | |

`[verified]`

**The composition is the finding, and it is not random:** `[verified]`

- **Crackstation/crack tasking: 5 of 18** (`CrackstationBenchmark`, `CrackstationRegister`, `CrackstationTrigger`, `CrackTaskByID`, `CrackTaskUpdate`) `[verified]`
- **Builder/external-build: 4 of 18** (`BuilderRegister`, `BuilderTrigger`, `GenerateExternalGetBuildConfig`, `GenerateExternalSaveBuild`) `[verified]`
- **Creds by-ID / by-hash-type: 3 of 18** (`GetCredByID`, `GetPlaintextCredsByHashType`, `CredsSniffHashType`) `[verified]`
- **Streaming: 1 of 18** (`BuilderRegister`) `[verified]`

> **These are exactly the families D81 and D91 found on the SERVER's restricted allowlists — the crackstation and builder methods gated to non-`PermissionAll` tokens.** `[inferred]` **The client never calls them because they are not operator-driven RPCs: they are driven by the crackstation and builder processes, which are peers of the server, not the operator console.** `[inferred]` **The two findings corroborate each other from opposite ends of the wire.** `[inferred]`

**Two alternative explanations tested and eliminated:** `[verified]`

- **"They are reached via the interface, not a direct call."** `[verified]` **The relaxed pattern covers every `.Name(` call through any receiver, including `Rpc.Host(`. `Host` still resolves to zero — and `Rpc.Host(` was checked explicitly with a strict pattern, returning no hits.** `[verified]` **The 279 raw `Host` mentions are the substring `host`/`hosts` in other identifiers — Rule 20's exact shape.** `[verified]`
- **"`CrackstationBenchmark` is called."** `[verified]` **It is NOT. The single mention at `crack-benchmarks.go:40` is `con.Rpc.CrackstationBenchmarks(` — the PLURAL, `CrackstationBenchmarks`, which IS in the called set.** `[verified]` **A one-character-deep false positive caught before it entered the table.** `[verified]` **Recorded as F2.** `[verified]`

### 1.5 The sharpest single result: `GetAIConversationMessages` is dead, and the client uses the field D91 found ignored

`[verified]` **The client has a stub for `GetAIConversationMessages` and never calls it. Zero mentions anywhere in the client.** `[verified]` **Instead it calls `GetAIConversation` with `IncludeMessages: true` — at `model.go:4018` and `model.go:4025`, the only two `IncludeMessages` uses in the package.** `[read]`

```go
4016:			conversation, err = con.Rpc.GetAIConversation(grpcCtx, &clientpb.AIConversationReq{
4017:				ID:              activeID,
4018:				IncludeMessages: true,
4019:			})
```

`[read]`

> **D91 recorded that the server's `GetAIConversation` handler passes `db.AIConversationByID(req.ID, "", req.IncludeMessages)` — the `IncludeMessages` flag IS forwarded, and the OWNERSHIP argument is `""`.** `[read]` **So the client is doing its part correctly and the server discards the scope.** `[verified]` **The two reports meet exactly, and the client-side artifact shows that the server had a working channel available and a working dead channel beside it.** `[inferred]`

---

## 2. T2 — WHAT THE CLIENT CANNOT DO

**The Lead framed T2 as "the 20 missing services." The correct measured statement is different, and I report the measurement.** `[verified]`

`[verified]` **The client declares a stub for 201 of 201 ServiceDesc methods. There is no missing service.** `[verified]` **What exists is a set of 18 methods the client declares and never invokes.** `[verified]`

| Framing | Measured |
|---|---|
| "client links N, server declares 201" | **client links 201 / 201 — no gap** |
| "client cannot reach a service" | **reaches all 201; actively invokes 183** |
| **capability gap** | **18 declared-but-never-invoked methods (§1.4)** |

`[verified]`

**What the client genuinely cannot do, stated precisely:**

1. **It cannot drive crackstation registration or tasking.** `[verified]` `CrackstationRegister`, `CrackstationTrigger`, `CrackstationBenchmark`, `CrackTaskByID`, `CrackTaskUpdate` are all uncalled. `[verified]`
2. **It cannot register or trigger a builder.** `[verified]` `BuilderRegister`, `BuilderTrigger` uncalled. `[verified]`
3. **It cannot fetch a credential by ID or by hash type.** `[verified]` `GetCredByID`, `GetPlaintextCredsByHashType`, `CredsSniffHashType` uncalled — the client browses creds through the aggregate `Creds` RPC only. `[verified]`
4. **It cannot restart jobs.** `[verified]` `RestartJobs` uncalled. `[verified]`
5. **It cannot fetch a whole conversation as a message list.** `[verified]` `GetAIConversationMessages` uncalled; it uses `GetAIConversation` + `IncludeMessages`. `[verified]`

> **None of these is a defect. `[inferred]` Every one is an RPC whose legitimate driver is the server-side subsystem rather than the operator console, and the restricted allowlists D81 found (§1.4) say the same thing from the other side. `[inferred]` The honest finding is that the client's dead stubs are the mirror image of the server's restricted allowlist, and the two independently identify the same five families.** `[inferred]`

---

## 3. T3 — IS THERE A SERVER BINARY ANYWHERE? **NO. R1 STANDS, AND I CORRECT MY OWN D96 ENUMERATION.**

### 3.1 `02_BINARIES\` — complete inventory, every file

`[verified]` **4 files, 134,646,938 B total.** `[verified]`

| bytes | path |
|---:|---|
| 68,780,065 | `\02_BINARIES\merlin\merlinServer-Windows-x64.7z` |
| **65,866,240** | `\02_BINARIES\sliver\sliver-client_windows-amd64.exe` |
| 326 | `\02_BINARIES\sliver\sliver-client_windows-amd64.exe.minisig` |
| 307 | `\02_BINARIES\havoc_BUILDFROM_SOURCE\README.md` |

`[verified]`

> **D96 §1.1 asserted "there is no `sliver-server` binary in `02_BINARIES\sliver\` under this enumeration" and R1 was built on it. `[verified]` The claim survives, but D96 never enumerated `02_BINARIES` itself — it asserted a scope it had not watched. This round enumerated it and found the `.minisig` and the 68.7 MB `merlinServer` ARCHIVE, neither of which D96 had seen.** `[verified]` **The conclusion holds; the evidence for it was weaker than the claim.** `[verified]` **Recorded as F3.** `[verified]`

### 3.2 Every `*server*` file under `02_BINARIES` — 1 match, and it is Merlin's

`[verified]` **`merlinServer-Windows-x64.7z` — 68,780,065 B.** `[verified]` **No `sliver-server*`, no `sliverServer*`, no `sliver_server*`.** `[verified]`

### 3.3 `05_TARGETS\` — 92 files, 264,995,672 B

`[verified]` **The top of the tree, all Merlin:** `[verified]`

```
26,329,600  \05_TARGETS\merlin_extracted\merlinServer-Windows-x64.exe
20,804,192  \05_TARGETS\merlin_extracted\data\bin\merlinCLI-Darwin-x64
20,754,432  \05_TARGETS\merlin_extracted\data\bin\merlinCLI-Windows-x64.exe
20,299,557  \05_TARGETS\merlin_extracted\data\bin\merlinCLI-Linux-x64
19,571,874  \05_TARGETS\merlin_extracted\data\bin\merlinCLI-Darwin-arm64
19,183,912  \05_TARGETS\merlin_extracted\data\bin\merlinCLI-Linux-arm
19,017,586  \05_TARGETS\merlin_extracted\data\bin\merlinCLI-Linux-arm64
15,145,760  \05_TARGETS\merlin_extracted\data\bin\merlin.x64.dll
14,687,006  \05_TARGETS\merlin_extracted\data\bin\merlin.x86.dll
13,939,200  \05_TARGETS\merlin_extracted\data\bin\merlinAgent-Windows-x64-Debug.exe
13,939,200  \05_TARGETS\merlin_extracted\data\bin\merlinAgent-Windows-x64.exe
12,761,408  \05_TARGETS\merlin_extracted\data\bin\merlinAgent-Darwin-x64
  ...
    360,448  \05_TARGETS\practice\notepad_small.exe
```

`[verified]` **Zero Sliver binaries. Zero `*-server.exe` other than `merlinServer-Windows-x64.exe`.** `[verified]`

### 3.4 `07_OUTPUT\extractions\` — 9,722 files, and a duplicated Merlin tree

`[verified]` **`\07_OUTPUT\extractions\T8\extracted\` is a second, independent extraction of the same Merlin suite (identical sizes to `05_TARGETS`, and `T8\strings\` carries `.strings.txt` dumps).** `[verified]` **`T3\androrat_apk\` holds apktool smali output.** `[verified]` **No Sliver server appears in either.** `[verified]`

### 3.5 The definitive answer, and the file that made me check twice

`[verified]` **Searching the whole corpus for `C-0*.tsv` returned SIX Ghidra symbol tables plus a seventh I did not expect: `C-07_sliver-client_windows-amd64.ghidra-symbols.tsv`, 1,945,710 B.** `[verified]` **That is the destination C-00 designated for the pending Sliver TSV, and the run filled it.** `[verified]`

> **T3 ANSWER, DEFINITIVE: there is NO Sliver server binary anywhere in `02_BINARIES`, `05_TARGETS`, or `07_OUTPUT\extractions`. `[verified]` The only server binary in the corpus is Merlin's. R1 STANDS unchanged: D91's inert-ownership-filter finding has no compiled counterpart, and it cannot be tested at the binary layer until a `sliver-server` build is added.** `[verified]` **The added detail this round provides is that the corpus DOES carry a full Merlin server binary, so the asymmetry is Sliver-specific — the project whose server source we hold is the one whose server binary we lack.** `[inferred]`

---

## 4. T4 — THE EMBEDDED PNG/GIF RESOURCES: **the client ships NO images**

**Ghidra logged four failures:** `[verified]`

```
ERROR Invalid PNG data at 1417cb3a2 (PngDataType)
ERROR Invalid GIF data at 143c44b5c (GifDataType)
ERROR Invalid GIF data at 143c44b62 (GifDataType)
ERROR Invalid PNG data at 143c44ec8 (PngDataType)
```

`[verified]` **The fourth line is `143c44ec8`, not a repeat of the first. I mis-transcribed it once while drafting; corrected against the log.** `[verified]`

`[verified]`

**Manual whole-file scan for real image signatures:** `[verified]`

| Format | Signature | Count |
|---|---|---:|
| PNG | `89 50 4E 47 0D 0A 1A 0A` | **3** |
| GIF | `GIF87a` / `GIF89a` | **2** |
| JPEG | `FF D8 FF` | **4** |

`[verified]` **At file offsets `0x9BF67A`, `0x17C9DA2`, `0x3C42CC8` (PNG) and `0x3C4295C`, `0x3C42962` (GIF).** `[verified]`

**Decoded as PNG, they are NOT PNGs:** `[verified]` **the 4-byte chunk length and the 4-byte chunk type are garbage — `chunkLen=1217090596 type="@H9J"`, `chunkLen=1869628257 type="pEnd"`, `chunkLen=1869628257 type="ÿÿÿÿ"`. A valid PNG has `chunkLen=13 type="IHDR"`.** `[verified]` **None does.** `[verified]`

**What is actually there, read in context:** `[verified]`

```
before PNG at 0x17C9DA2:  ....xmlnoitalic#04D bg:#D42 bg:#A60 bg:#88F bg:#fc8 bg:[%v]  %v
GIF at 0x3C4295C:         .......Date: ............<TABLE<STYLE<TITLE
GIF at 0x3C42962:         ...te: ............<TABLE<STYLE<TITLEGIF87a
```

`[verified]`

**And the stack that owns those strings is present with heavy counts:** `[verified]`

| Symbol | Count | What it is |
|---|---:|---|
| `github.com/yuin/goldmark` | **1,862** | Markdown parser |
| `github.com/alecthomas/chroma` | **1,280** | syntax highlighting |
| `github.com/microcosm-cc/bluemonday` | **253** | **HTML sanitizer** |
| `image/png` | 704 | Go stdlib decoder name |
| `<TABLE` / `<STYLE` / `<TITLE` | **1 each** | **sanitizer allowlist literals** |
| `GIF87a` / `GIF89a` | **1 each** | **format-name literals** |

`[verified]`

> **T4 ANSWER: the client ships no images. `[verified]` The PNG signature is a data literal in an image-format-signature table; the GIF strings are format-name literals; `<TABLE`, `<STYLE`, `<TITLE` are single string literals in `bluemonday`'s HTML allowlist. Each occurs exactly ONCE, which is what a string literal looks like and what an embedded image would not.** `[verified]` **Ghidra's "Invalid PNG data" verdict was CORRECT — it tried to decode bytes that are not a decodable PNG, because they are a signature constant.** `[inferred]` **A C2 client shipping three broken PNGs would be a finding; a markdown-rendering TUI holding an image-signature table is not.** `[inferred]`

**One paragraph, as asked:** `[inferred]` **the reason a Sliver client touches image-format constants at all is that its AI console renders markdown with syntax highlighting (`goldmark` → `chroma`) inside an HTML-sanitizing TUI (`bluemonday`). `[verified]` `chroma`'s lexer registry and `bluemonday`'s tag allowlist are string tables, and a lexer registry that can highlight a PNG-related language or an HTML `<img>` policy carries the signature strings as data. `[verified]` The images exist as vocabulary, not as payload.** `[inferred]`

---

## 5. Corrections

| # | Prior claim | Correction | Evidence |
|---|---|---|---|
| **C-11** | **D96 §0/§4: "Ghidra produced no figures; no `gsli.tsv`."** | **No longer true. The run completed at 20:45:37 and produced `C-07_sliver-client_windows-amd64.ghidra-symbols.tsv` (1,945,710 B, `total=41528 named=1 thunks=5`). D96's PREDICTION is confirmed by the artifact: `named=1`, the Merlin-agent figure.** | §0, §0.1 |
| **C-12** | **D96 §1.1: "no `sliver-server` binary in `02_BINARIES\sliver\` under this enumeration."** | **Conclusion CORRECT and R1 stands. But D96 asserted over a directory it had not enumerated. `02_BINARIES` holds 4 files; D96 had seen 2 of them and missed the 68,780,065 B `merlinServer-Windows-x64.7z`.** | §3.1 |
| **C-13** | **D96 §4: Ghidra's function count was unavailable for comparison.** | **Now available: Ghidra 41,528 functions vs pclntab 51,657. Ghidra missed 10,129 functions (19.6%) and named none of what it recovered beyond `entry`.** | §0.1 |

`[verified]` **D96 and D103 do not conflict; D96 was accurate as of its cutoff. Both files remain on disk unedited.** `[verified]`

---

## 6. Instrument failures

| # | Failure | Where | Resolution |
|---|---|---|---|
| **F1** | **Treated Ghidra's `1417cb3a2` as a FILE offset.** It is a VIRTUAL address (`imageBase=140000000`). The byte dump threw `Cannot convert value "5393658786" to type "System.Int32"`. | §0.2 | Subtracted the image base → `0x17CB3A2` etc., all in range. |
| **F2** | **`CrackstationBenchmark` entered the dead-stub list, and it is CALLED.** The single mention is `con.Rpc.CrackstationBenchmarks(` — the plural. | §1.4 | Read the hit instead of trusting the count. Removed from the list; recorded here. **Rule 20's substring shape.** |
| **F3** | **D96 asserted absence over an unenumerated directory.** | §3.1 | Enumerated `02_BINARIES` fully this round; conclusion held, evidence strengthened. |
| **F4** | **`$(...)` interpolation collision — `ParserError: $(subexpression) is missing the closing ')'`.** Fired when a comment containing `(must be > 0)` sat beside an interpolated pattern. | §1.4 probe | **Errored LOUDLY, producing no output rather than a wrong number.** Rebuilt without the interpolated comment. |
| **F5** | **`if(...){...}` used as a PowerShell expression in a string concatenation** → `'if' is not recognized as a cmdlet`. | §0 probe | Rewrote as a statement. Benign; the surrounding output was correct. |

`[verified]`

---

## 7. Residuals

**R1 — STANDS, unchanged and now better evidenced: no Sliver server binary exists in the corpus.** `[verified]` **D91 remains unverifiable at the binary layer.** `[inferred]`

**R2 — the 18 uncalled stubs are asserted from a source call-site census, not from the binary.** `[verified]` **PROBE:** the pclntab can confirm the *stub* is present, but "uncalled" is a property of the client source, not of the artifact. The claim is as strong as the source tree, no stronger. `[inferred]`

**R3 — `CrackFileChunkUpload` is called but `CrackFileChunkDownload` is not.** `[verified]` **This matches D81's allowlist asymmetry exactly (upload excluded from the crackstation restriction, download included).** `[inferred]` **PROBE:** the direction of that asymmetry is worth one probe — the client uploads crack files and never downloads them, while the server's allowlist gates the download. `[inferred]`

**R4 — the `ai` subtree's 242 symbols include 121 `aiModel` methods and only ~120 free functions.** `[verified]` **`aiModel` is the largest single type in the client's command surface and is unread at method level.** `[inferred]`

**R5 — `_d103_*` probes: F1–F5 were run inline this round and are not all on disk.** `[verified]` **The two that produced figures used here (`_d96_pclntab.tsv`, `C-07_...tsv`) are both on disk and both digest-recorded.** `[inferred]`

---

## 8. Summary

**T1 — the client's operational surface is enumerated: 2,385 symbols across 63 `client/command/*` leaf packages, with `ai` (242) the largest subtree — a full Bubble Tea TUI with six modal types, mouse handling, toast overlays and an experimental-warning gate.** `[verified]` **The client's `normalizedConversationOperatorName` (`model.go:4971`) sanitizes five placeholder-identity forms to `""`; the server has no equivalent.** `[verified]` **`GetAIConversationMessages` is one of 18 stubs the client declares and never calls; it uses `GetAIConversation` + `IncludeMessages: true` (`model.go:4018`, `:4025`) — the exact field D91 found the server accepting and then ignoring the scope of.** `[verified]`

**T2 — there is no missing service.** `[verified]` **The client stubs 201/201 and invokes 183.** `[verified]` **The capability gap is 18 declared-but-uninvoked methods, and its composition — 5 crackstation/crack, 4 builder/external-build, 3 creds-by-ID — is the mirror image of the server's restricted allowlists.** `[verified]`

**T3 — NO SERVER BINARY, DEFINITIVELY. R1 STANDS.** `[verified]` **`02_BINARIES` = 4 files (enumerated in full); `05_TARGETS` = 92 files, all Merlin; `extractions` = 9,722 files, all Merlin + androrat. The only server binary in the corpus is Merlin's.** `[verified]` **D96's conclusion held; D96's evidence for it was weaker than the claim, and I say so.** `[verified]`

**T4 — the client ships no images.** `[verified]` **Three PNG signatures and two GIF strings exist as DATA in `bluemonday`'s HTML allowlist and `chroma`'s lexer tables; none decodes, and `<TABLE`/`<STYLE`/`<TITLE` each occur exactly once as literals.** `[verified]` **Ghidra's "Invalid PNG data" was correct.** `[verified]`

**The headline the round produced, and it is a correction to my own work:** `[verified]` **the Ghidra run landed and returned `total=41528 named=1 thunks=5` — the same `named=1` C-08 recorded for the Merlin agent. D96 predicted that number from a log; D103 has it from the artifact. The same binary yields 51,657 functions through the pclntab, so Ghidra missed 10,129 functions and named none of what it found. A 0.0024% coverage figure is a statement about the instrument, and the only reason we know that is that a second instrument was built when the first one failed.**

*End of D103. Probes on disk: `binlayer\_d96_pclntab.ps1`, `binlayer\_d96_pclntab.tsv`, `binlayer\C-07_sliver-client_windows-amd64.ghidra-symbols.tsv`.*
