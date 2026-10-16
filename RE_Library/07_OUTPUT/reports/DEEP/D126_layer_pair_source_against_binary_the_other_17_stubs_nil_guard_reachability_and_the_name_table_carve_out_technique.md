# D126 — The layer pair: source against binary

**SCOPE:** three questions that can only be settled by holding a source census beside a binary
measurement — (1) whether the D103 18-stub census survives a binary pass, (2) whether any caller
of `ParseDemonRegisterRequest` guards the nil before `demons.go:5254`, (3) whether the name-table
carve-out built for PAIR 1 generalises to C-11's config-string claims.

**DEFINER SCOPE:** D103 §1.4's 18-method table; `havoc/teamserver/pkg/{agent,handlers}`; C-11's
four string-in-binary claims; the sliver client PE and two Merlin Linux binaries.

**COUNTED:** 144 `.md` under `DEEP` at write time · 18 stub methods · 3 call sites · 201 client
methods · 9 config-bearing Merlin binaries · 3 carve-out targets · 4 claim classes.

**This report is D126 by allocation.** `_ALLOC/registry.json` records `"126": {"lane":
"source-diver"}` at `2026-10-16 22:20:14`, registered by the Lead before this pass began.
`D121`–`D122` were taken by four and one other lanes respectively during the PAIR work, with no
lock files written; the allocator post-dates those collisions.

---

## §0 Headline

**Three results, one of which overturns a method I used in my own previous pass.**

1. **The D103 18-stub census does NOT convert to a binary measurement, and the reason is
   structural — not a tool limit.** All 18 client stubs are present in the pclntab name table,
   **18 of 18**, because `protoc-gen-go` emits a client method for **every** ServiceDesc entry
   unconditionally. D103 already said this in R2. **What D103 could not say is *how
   non-discriminating* it is: I measured a cross-tabulation over all 201 client methods, and
   symbol presence is uniform — 201 of 201.** `[binary]` `[verified]`

2. **The probe built to test that non-discriminating signal recovered a real, source-free
   discriminator.** A per-method distribution print — mandatory under my own instrument rule —
   found exactly two of the 18 without a `.func1` closure. Those two are **exactly** the two
   whose generated stubs are `grpc.ServerStreamingClient`. Extended to all 201 methods:
   **streaming 6/6 WITHOUT `func1`, unary 195/195 WITH it, zero exceptions.** `[binary]`
   `[source]` `[verified]`

3. **The name-table carve-out generalises, and on its first non-sliver target it caught a live
   false positive.** On `merlinCLI-Linux-x64`, `main.main` returns **1 hit outside the name table
   and 1 inside** — so a naive "is `main.main` in the binary?" probe returns a hit on a binary that
   has **no** `main.*` config blob at all. The carve-out separates the entry-point reference from
   a config string. `[binary]` `[verified]`

**One self-correction, stated first because it is mine:** in the intermediate pass I reported
*"6 fields captured, 2 distinct field-sets"* for the Merlin config. That was **my regex
under-capturing the escaped `-X \"main.k=v\"` run**. Corrected: **19 fields, 1 distinct field-set,
every value identical across 9 binaries.** The corrected number is stronger than the one I first
printed, and it agrees with C-11 §2. `[binary]` `[verified]`

---

## §1 PAIR 1 residue — the other 17 stubs

### 1.1 The question, and why it is not answerable as posed

D103 §1.4 lists 18 methods with zero call sites under either of two source patterns, and D103:403
(R2) states the limitation itself:

> **R2 — the 18 uncalled stubs are asserted from a source call-site census, not from the binary.**
> `[verified]` **PROBE:** the pclntab can confirm the *stub* is present, but "uncalled" is a
> property of the client source, not of the artifact.

**R2 is correct, and the measurement below shows it is correct for a reason R2 did not name.**
The brief asked whether a stub *present in the name table* is "not a stub — it is a function
someone calls." **That inference does not hold, and the failure is structural rather than
instrumental.** `[binary]` `[verified]`

### 1.2 The measurement — 18 of 18, and the control that proves the pattern is real

Method: count `rpcpb.(*sliverRPCClient).<Name>` and `rpcpb._SliverRPC_<Name>_Handler` in the
65,866,240-byte client PE. A garbage token is included as a mandatory discrimination control.

| # | Method | Family | Client stub | Any mention | Handler | Verdict |
|---:|---|---|---:|---:|---:|---|
| 1 | `BuilderRegister` | builder | 1 | 6 | 1 | PRESENT |
| 2 | `BuilderTrigger` | builder | 1 | 7 | 2 | PRESENT |
| 3 | `CrackFileChunkDownload` | crack | 1 | 7 | 2 | PRESENT |
| 4 | `CrackstationBenchmark` | crackstation | 2 | 14 | 2 | PRESENT |
| 5 | `CrackstationRegister` | crackstation | 1 | 6 | 1 | PRESENT |
| 6 | `CrackstationTrigger` | crackstation | 1 | 7 | 2 | PRESENT |
| 7 | `CrackTaskByID` | crack | 1 | 7 | 2 | PRESENT |
| 8 | `CrackTaskUpdate` | crack | 1 | 7 | 2 | PRESENT |
| 9 | `CredsSniffHashType` | creds | 1 | 7 | 2 | PRESENT |
| 10 | `CredsUpdate` | creds | 1 | 7 | 2 | PRESENT |
| 11 | `GenerateExternalGetBuildConfig` | external build | 1 | 7 | 2 | PRESENT |
| 12 | `GenerateExternalSaveBuild` | external build | 1 | 7 | 2 | PRESENT |
| 13 | `GetAIConversationMessages` | AI | 1 | 7 | 2 | PRESENT |
| 14 | `GetCredByID` | creds | 1 | 7 | 2 | PRESENT |
| 15 | `GetPlaintextCredsByHashType` | creds | 1 | 7 | 2 | PRESENT |
| 16 | `Host` | hosts | 4 | 552 | 2 | PRESENT |
| 17 | `RestartJobs` | jobs | 1 | 7 | 2 | PRESENT |
| 18 | `ShellcodeRDI` | shellcode | 1 | 31 | 2 | PRESENT |

**COUNTED: 18 methods from D103 §1.4. Distribution print: PRESENT 18/18 (100%), 1 distinct
verdict.** `[binary]` `[verified]`

**A classifier returning one value for 100% of its input is broken or badly posed.** The mandatory
distribution print flagged this before it entered the report, and the diagnosis is not a dead
instrument — see the control.

**Positive controls (5), methods D103 says ARE called:**

| Control | Client stub | Any mention | Result |
|---|---:|---:|---|
| `GetVersion` | 1 | 26 | PRESENT |
| `GetSessions` | 1 | 10 | PRESENT |
| `SaveAIConversation` | 2 | 14 | PRESENT |
| `GetBeacons` | 1 | 9 | PRESENT |
| `GetAIConversation` | 3 | 21 | PRESENT |

**CONTROLS PASSED: 5 / 5.** And the discrimination control:

```
rpcpb.(*sliverRPCClient).GetVersion              1
rpcpb.(*sliverRPCClient).ZZZ_NOT_A_METHOD_ZZZ    0      <- must be 0
rpcpb.(*sliverRPCClient).Host                    4
rpcpb.(*sliverRPCClient).BuilderRegister         1
```

**The garbage token returns 0, so the pattern is discriminating.** Therefore 18/18 PRESENT is a
**true measurement of the wrong property**. The generated client stub exists whether or not any
code path invokes it. `[binary]` `[verified]`

### 1.3 What discriminates, tested

Four candidate signals were run across three ground-truth groups — 5 called controls, 17 uncalled
stubs, 1 falsified member:

| Group | n | method-path literal | `_Handler` | `.func1` |
|---|---:|---:|---:|---:|
| CALLED (control) | 5 | **0 / 5** | 5 / 5 | **5 / 5** |
| UNCALLED per D103 | 17 | **0 / 17** | 17 / 17 | **15 / 17** |
| Falsified by D121 | 1 | 0 / 1 | 1 / 1 | 1 / 1 |

**The method-path literal `/rpcpb.SliverRPC/<Name>"` is 0 in all three groups — including the
called controls. It is non-discriminating and I report it as such rather than discarding it
silently.** `[binary]` `[verified]`

**`_Handler` presence is 23 of 23 — also non-discriminating.** `[binary]` `[verified]`

**`.func1` is 15 of 17 in the uncalled group — the first signal with a non-uniform result.**
Distribution print for the uncalled group: `func1 only` 15 (88%), `neither` 2 (12%).
**The two `neither` members are `BuilderRegister` and `CrackstationRegister`.** `[binary]`
`[verified]`

### 1.4 The recovered discriminator — validated across all 201

Hypothesis: the two outliers are the streaming stubs. Tested against the generated source, then
against the full method set.

**Source side, `sliver/protobuf/rpcpb/services_grpc.pb.go`:**

```go
func (c *sliverRPCClient) BuilderRegister(ctx context.Context, in *clientpb.Builder, opts ...grpc.CallOption)
    (grpc.ServerStreamingClient[clientpb.Event], error)
func (c *sliverRPCClient) CrackstationRegister(ctx context.Context, in *clientpb.Crackstation, opts ...grpc.CallOption)
    (grpc.ServerStreamingClient[clientpb.Event], error)
func (c *sliverRPCClient) CrackstationTrigger(ctx context.Context, in *clientpb.Event, opts ...grpc.CallOption)
    (*commonpb.Empty, error)
func (c *sliverRPCClient) BuilderTrigger(ctx context.Context, in *clientpb.Event, opts ...grpc.CallOption)
    (*commonpb.Empty, error)
```

`[source: sliver/protobuf/rpcpb/services_grpc.pb.go]` `[verified]`

**Both outliers are `ServerStreamingClient`; both non-outliers in the same family are unary.**

**Full cross-tabulation — COUNTED: 201 client methods recovered from `services_grpc.pb.go`,
classified streaming (6) versus unary (195) by return type, then probed in the binary:**

| source signature | `.func1` present | n |
|---|---|---:|
| streaming | False | **6** |
| streaming | True | **0** |
| unary | False | **0** |
| unary | True | **195** |

```
streaming WITHOUT func1 :  6 / 6
streaming WITH    func1 :  0 / 6
unary     WITHOUT func1 :  0 / 195
unary     WITH    func1 : 195 / 195
```

**Perfect separation across 201 of 201, zero exceptions.** `[binary]` `[source]` `[verified]`

**The six streaming methods, exhaustively:**

| Method | Return type |
|---|---|
| `ClientLog` | `grpc.ClientStreamingClient[clientpb.ClientLogData, commonpb.Empty]` |
| `BuilderRegister` | `grpc.ServerStreamingClient[clientpb.Event]` |
| `CrackstationRegister` | `grpc.ServerStreamingClient[clientpb.Event]` |
| `SocksProxy` | `grpc.BidiStreamingClient[sliverpb.SocksData, sliverpb.SocksData]` |
| `TunnelData` | `grpc.BidiStreamingClient[sliverpb.TunnelData, sliverpb.TunnelData]` |
| `Events` | `grpc.ServerStreamingClient[clientpb.Event]` |

### 1.5 The mechanism, read out of the name table

The name table stores fully-qualified symbols null-terminated and back to back. Streaming stubs
appear **once**; unary stubs appear **twice**.

```
Events      _Handler hits=1   0x27E67B5  rpcpb._SliverRPC_Events_Handler|<next symbol>
ClientLog   _Handler hits=1   0x27E2D18  rpcpb._SliverRPC_ClientLog_Handler|<next symbol>
SocksProxy  _Handler hits=1   0x27E668E  rpcpb._SliverRPC_SocksProxy_Handler|<next symbol>
TunnelData  _Handler hits=1   0x27E676C  rpcpb._SliverRPC_TunnelData_Handler|<next symbol>
GetVersion  _Handler hits=2   0x27E2CCF  rpcpb._SliverRPC_GetVersion_Handler|<next symbol>
                              0x27E684F  rpcpb._SliverRPC_GetVersion_Handler.func1|<next symbol>
```

**A named `.func1` closure symbol is a unary-only artifact of the gRPC Go generator.** All five
offsets sit inside the carve-out region `0x269DE28 .. 0x2F86498`, which is why they are symbol
names and not literals. `[binary]` `[verified]`

**Stated positively, as an instrument:** *in a Go gRPC client binary, a client method whose
`_Handler` symbol has no adjacent `_Handler.func1` symbol is a streaming method.* `[binary]`
`[verified]`

### 1.6 What this does and does not do to D103

- **It does NOT refute the 18-stub census.** The census is a source claim and my binary pass
  cannot reach it. D103 R2 said exactly this. `[source]` `[verified]`
- **It DOES confirm R2's reasoning by measurement.** R2 says the pclntab can confirm the stub and
  not the call site. Measured: 201 of 201 stubs present, uniform. **R2 is not merely cautious — it
  is the correct characterisation of the artifact.** `[binary]` `[verified]`
- **It DOES NOT falsify any additional member.** D121 falsified exactly one member
  (`GetAIConversationMessages`, via its registered gRPC path and method-logger entry). The other 17
  stand as source-census claims. `[source]` `[verified]`
- **It DOES add a result R2 did not anticipate:** the `.func1` absence test, which is orthogonal to
  the stub question and holds across the whole method set. `[binary]` `[verified]`

---

## §2 PAIR 3 second half — nil-guard reachability across every caller

### 2.1 The disassembly half is unavailable, by citation

D-21 is closed `[blocked]` by `havoc-deep` with a named missing ingredient: 58,321 files scanned,
zero `compile_commands.json`, zero `CMakeCache.txt`, no `workflows\` directory, and the named
missing ingredient is a recorded Demon build invocation. **That is D121's enumeration and I cite it
rather than re-scanning.** The only binary in `02_BINARIES` is the sliver client; `havoc_BUILDFROM_SOURCE`
is a 307-byte README. **There is no compiled Havoc demon to disassemble, and the question is
resolved from source.** `[absence]` `[verified]`

### 2.2 The enumeration

```
SCOPE:   RE_Library\01_SOURCE_c2\havoc  (all *.go, recursive)
COUNTED: 4 occurrences of ParseDemonRegisterRequest across the tree
         1 definition, 3 call sites
```

| # | Site | Statement |
|---:|---|---|
| D | `teamserver\pkg\agent\agent.go:328` | `func ParseDemonRegisterRequest(AgentID int, Parser *parser.Parser, ExternalIP string) *Agent {` |
| 1 | `teamserver\pkg\agent\agent.go:568` | `PivotSession = ParseDemonRegisterRequest(PivotAgentID, PivotParser, RoutineFunc)` |
| 2 | `teamserver\pkg\agent\demons.go:5253` | `DemonInfo = ParseDemonRegisterRequest(AgentHdr.AgentID, AgentHdr.Data, "")` |
| 3 | `teamserver\pkg\handlers\handlers.go:273` | `Agent = agent.ParseDemonRegisterRequest(Header.AgentID, Header.Data, ExternalIP)` |

`[source: havoc/teamserver/pkg]` `[verified]`

### 2.3 The return-path census

Four returns; three are nil. `[source: havoc/teamserver/pkg/agent/agent.go:328-606]` `[verified]`

| Line | Statement | Outcome |
|---:|---|---|
| `:409` | `return nil` | **nil** — AES-decrypt failure |
| `:596` | `return Session` | success — sole non-nil path |
| `:599` | `return nil` | **nil** — invalid packet |
| `:604` | `return nil` | **nil** — short buffer |

**3 of 4 paths return nil.**

### 2.4 Guard placement, per caller

**Call site 1 — `agent.go:568`, guarded on the next line:**

```go
568:  PivotSession = ParseDemonRegisterRequest(PivotAgentID, PivotParser, RoutineFunc)
569:  if PivotSession != nil {
570:      PivotSession.Info.MagicValue = HdrMagicValue
...
578:      Session.Pivots.Links = append(Session.Pivots.Links, PivotSession)
579:
580:      PivotSession.Pivots.Parent = Session
581:  }
```

**GUARDED.** The dereference at `:570` and the field write at `:580` are both inside the guard.
`[source: havoc/teamserver/pkg/agent/agent.go:568-581]` `[verified]`

**Call site 3 — `handlers.go:273`, guarded on the next line:**

```go
273:  Agent = agent.ParseDemonRegisterRequest(Header.AgentID, Header.Data, ExternalIP)
274:  if Agent == nil {
275:      return Response, false
276:  }
277:
278:  Agent.Info.MagicValue = Header.MagicValue
279:  Agent.Info.Listener = nil
```

**GUARDED, with an early return.** The dereference at `:278` is after the guard.
`[source: havoc/teamserver/pkg/handlers/handlers.go:273-279]` `[verified]`

**Call site 2 — `demons.go:5253`, not guarded before its dereferences:**

```go
5253:  DemonInfo = ParseDemonRegisterRequest(AgentHdr.AgentID, AgentHdr.Data, "")
5254:  DemonInfo.Pivots.Parent = a
...
5256:  a.Pivots.Links = append(a.Pivots.Links, DemonInfo)
...
5259:  DemonInfo.Info.MagicValue = AgentHdr.MagicValue
...
5265:  if DemonInfo != nil {
```

**UNGUARDED.** Three dereferences precede the guard, which arrives twelve lines later.
`[source: havoc/teamserver/pkg/agent/demons.go:5253-5265]` `[verified]`

### 2.5 Verdict

**2 of 3 callers guard the nil on the very next statement. `demons.go:5253` is the only caller that
defers its guard past its own dereferences.** `[source]` `[verified]`

**The reachability claim therefore HOLDS, and it is narrower than a pattern claim and stronger than
a hunch:**

- It is **not** a stylistic norm in this codebase. Both sibling callers handle the nil correctly,
  and one of them performs the **same field write** — `PivotSession.Pivots.Parent = Session` at
  `agent.go:580` — correctly guarded. `[source]` `[verified]`
- The author **knew** the function returns nil: the guard exists at `:5265`. The defect is
  **ordering**, not omission. `[source]` `[verified]`
- **The control case was already in the tree.** `agent.go:580` and `demons.go:5254` are the same
  operation on the same struct type; one is reachable-nil, one is not.

**D121's correction to D89 stands on this enumeration.** `DemonInfo.Pivots.Parent = a` is **one**
dereference of `DemonInfo` plus a constant-offset store — `.Pivots` is a **value** field
(`types.go:89-92 { Parent *Agent; Links []*Agent }`, declared `Pivots Pivots` at `types.go:150`).
`agent.go:750`'s `pivots *Pivots` is an unrelated local inside `PivotAddJob`. `[source]` `[verified]`

**Guard fate:** the `if DemonInfo != nil` at `:5265` is real and survives optimisation
`[inferred]` — its only use is building `Message["Type"]`, and no data flow lets the optimiser prove
non-nil. **It is dead on the nil path: execution panics at `:5254` first.** `[source]`
`[inferred]` `[verified]`

---

## §3 The name-table carve-out, generalised

### 3.1 The instrument

**Problem.** On a Go binary every symbol name is a null-terminated string inside the pclntab name
table. A substring search for a short literal such as `main.` or `unknown` therefore matches
**function names**, and the claim "string X is in the binary" becomes unfalsifiable — every symbol
counts as a hit.

**Fix.** Locate the pclntab by magic (`0xFFFFFFF1` / `FA` / `F0`), derive the name-table region
from its own header (`base + funcnameOff` .. `base + pclnOff`), and report **INSIDE** versus
**OUTSIDE** separately.

- **OUTSIDE** — a real compiled string literal.
- **INSIDE** — a function or symbol name. **Not evidence of a literal.**

**Mandatory control.** Every run includes a garbage token. If it returns greater than zero the
pattern is not discriminating and the whole table is void.

`RE_Library\07_OUTPUT\binlayer\_d126_carveout.py` — self-tests on three targets, prints its own
region bounds and the control hit count.

### 3.2 Region bounds, printed per target

| Target | bytes | pclntab base | name-table region | size | % of image | control |
|---|---:|---|---|---:|---:|---:|
| `sliver-client_windows-amd64.exe` | 65,866,240 | `0x269DDE0` | `0x269DE28..0x2F86498` | 9,340,528 | 14.2% | 0 |
| `merlinAgent-Linux-x64` | 12,492,924 | `0x5F0C20` | `0x5F0C68..0x8503C8` | 2,488,160 | 19.9% | 0 |
| `merlinCLI-Linux-x64` | 20,299,557 | `0x69BDA0` | `0x69BDE8..0x93A368` | 2,745,728 | 13.5% | 0 |

`[binary]` `[verified]`

### 3.3 The live false positive the technique caught

**COUNTED: 5 tokens × 3 targets.**

| token | sliver | merlinAgent | merlinCLI |
|---|---|---|---|
| `main.main` | SYMBOL-ONLY (0/1) | SYMBOL-ONLY (0/2) | **BOTH (1/1)** |
| `main.secure` | ABSENT | **LITERAL (2/0)** | ABSENT |
| `main.useragent` | ABSENT | **LITERAL (2/0)** | ABSENT |
| `<unknown>` | **LITERAL (1/0)** | ABSENT | ABSENT |
| `GetAIConversationMessages` | BOTH (4/3) | ABSENT | ABSENT |

`[binary]` `[verified]`

**The `main.main` row on `merlinCLI-Linux-x64` is the case that matters.** It returns **1 hit
outside the name table and 1 inside**. Without the carve-out, the outside hit reads as evidence
that the CLI carries a `main.*` string — **on a binary that carries no `main.*` config blob at all.**
The outside hit is an entry-point reference, not a config literal. **This is the exact false
positive the instrument exists to prevent, observed on its first non-sliver target.** `[binary]`
`[verified]`

### 3.4 Applied to C-11

C-11 makes four string-in-binary claims. Three positive, one negative.

**S1 / S3 — the user-agent is identical across platforms.** `[source]`

```
SCOPE:   RE_Library\05_TARGETS\merlin_extracted\data\bin
COUNTED: 17 files in the bin tree; 9 carry a parseable main.useragent blob
```

| Hash of UA region | Binaries |
|---|---|
| `10414243ccfea98b` | `merlin.x64.dll`, `merlin.x86.dll` |
| `b221e659cc8db4cf` | Darwin-arm64, Darwin-x64, Linux-arm, Linux-arm64, Linux-x64, Windows-x64-Debug |
| `eb535e3dfda4ff2e` | `merlinAgent-Windows-x64.exe` |

**DISTINCT user-agent values: 1.** 115 bytes:
`Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36`

**CONFIRMED — every one of the nine config-bearing builds carries the same user-agent, spanning
PE, ELF, and Mach-O and three operating systems.** C-11 §3 says "three platforms, same 115-byte
string"; the blob reaches **nine** binaries. `[binary]` `[verified]`

**The three-way hash split is the release-vs-Debug delta and the DLL build class**, not a
user-agent difference — the user-agent is byte-identical across all nine. `[binary]` `[inferred]`

**S2 — the config field set.** `[source]`

```
COUNTED: 9 binaries with a parseable -X run
union of fields across all 9: 19
distinct field-SETS: 1   (n=19, all nine)
```

`main.addr · main.auth · main.headers · main.host · main.httpClient · main.killdate ·
main.listener · main.maxretry · main.padding · main.parrot · main.protocol · main.proxy ·
main.psk · main.secure · main.skew · main.sleep · main.transforms · main.url · main.useragent`

**Per-field value identity: 19 of 19 fields IDENTICAL across all nine binaries.**
**CONFIRMED, and stronger than C-11 claimed** (C-11 §2 says "six agent platforms"; the blob is in
nine artifacts including both DLLs). `[binary]` `[verified]`

**S4 — the six CLIs carry NO `main.*` config string.** `[source]` NEGATIVE.

```
COUNTED: 17 files; 6 CLIs
```

| probe | CLI | AGENT |
|---|---:|---:|
| `-ldflags` | **2** | 2 |
| `main.psk` | **0** | 2 |
| `main.sleep` | **0** | 2 |
| `main.httpClient` | **0** | 2 |
| `main.useragent` | **0** | 3 |
| `useragent` | **0** | 3 |

**Controls proving the probe works on the CLI unchanged:** `Go build` 1, `runtime.main` 11,
`goroutine` 72, `http` 2072. `[binary]` `[verified]`

**The CLI carries the word `-ldflags` twice but zero `main.*` injection pairs. The negative is
CONFIRMED with the enumeration shown, not substituted from another artifact.** `[absence]`
`[verified]`

### 3.5 The mechanism, visible in the agent's own bytes

The agent embeds its linker command line as a compiled literal at `0x5EE747`, outside the name
table:

```
-X \"main.url=https://127.0.0.1:443\" -X \"main.host=\" -X \"main.httpClient=go\"
-X \"main.psk=merlin\" -X \"main.secure=false\" -X \"main.sleep=30s\" -X \"main.proxy=\"
-X \"main.useragent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36
   (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36\" -X \"main.headers=\"
-X \"main.skew=3000\" -X \"main.padding=4096\" -X \"main.killdate=0\"
-X \"main.maxretry=7\" -X \"main.parrot=\"
-buildid=.build.-tags=-trimpath.build.CGO_ENABLED=0.build.GOARCH=amd64
.build.GOOS=linux.build.GOAMD64=v1
```

`[binary]` `[verified]`

**Build configuration recovered from the embedded `build.` run:** `-trimpath`,
`CGO_ENABLED=0`, `GOARCH=amd64`, `GOOS=linux`, `GOAMD64=v1`, distinct `-buildid` per binary.
`[binary]` `[inferred]`

**This is the same extraction technique working on a non-sliver target, and it is why the S4
negative is provable:** the config arrives as a literal *outside* the name table, so carving the
name table out leaves exactly the artifact that answers the question. `[binary]` `[verified]`

---

## §4 The two-part general instrument

The round produces one instrument with two independent halves, both target-agnostic:

**(a) Name-table carve-out — answers "is this a literal or a symbol name?"**
Locate pclntab by magic; derive `base + funcnameOff` .. `base + pclnOff`; report INSIDE versus
OUTSIDE; include a garbage-token control. **Applicable to every string-in-binary claim in the
layer-pair work.** Harness: `RE_Library\07_OUTPUT\binlayer\_d126_carveout.py`.

**(b) `.func1` absence test — answers "is this gRPC client method streaming?"**
In a Go gRPC client binary, a method whose `_Handler` symbol has no adjacent `_Handler.func1`
symbol is streaming. **Validated 201/201 with zero exceptions.**

**A third, target-specific result:** the `-ldflags -X` run is embedded as a plain literal in Go
binaries built with injected config, recoverable by locating `-X \"main.` and scanning to
`-buildid=`. This is how C-11's 19-field set was measured.

**All three share the same failure mode and the same defence:** a short substring probe against a
Go binary is dominated by symbol names unless the name table is excluded, and the exclusion is only
trustworthy when a garbage-token control returns zero.

---

## §5 Instrument record

**I1 — the distribution print caught a badly-posed question, not a broken tool.** The 18/18 PRESENT
result triggered my own standing rule ("a classifier returning one value for 100% of its input is
broken, not decisive"). Diagnosis required the control, which returned 0, proving the pattern
discriminating and relocating the fault from the instrument to the question. **Without the
mandatory distribution print this would have been written up as a finding that "all 18 stubs are
present in the binary" — true, and completely uninformative.** `[binary]` `[verified]`

**I2 — my own regex under-captured, and I printed the wrong number first.** An intermediate pass
reported *"6 fields, 2 distinct field-sets."* The raw byte dump visibly showed 19 fields. Cause: the
key/value regex only matched pairs falling inside a fixed-width window, dropping everything before
the window start. **Corrected by locating the full `-X` run and parsing it end to end: 19 fields,
1 field-set.** The corrected number is stronger than the erroneous one, which is the reverse of the
usual failure direction. `[binary]` `[verified]`

**I3 — PowerShell nested-quote terminator.** A `python -c` invocation containing escaped double
quotes inside a double-quoted PowerShell string produced `TerminatorExpectedAtEndOfString`. Not a
tool failure; a shell-layering fault. **Fix: write the probe to a `.py` file.** This is the standing
convention and the brief's "no apostrophe in probe strings" rule is the same fault one character
over. `[binary]` `[verified]`

**I4 — str pattern against a bytes object.** `re.finditer` raised
`TypeError: cannot use a string pattern on a bytes-like object`. Encode the pattern. Recurrence of a
logged species. `[binary]` `[verified]`

**I5 — `edit` rejected a two-space indent against a one-space file.** `old_string` was not found
because I transcribed the JSON with two-space indentation and the file uses one. **Fix: read the
file and copy the exact bytes.** The filesystem guard behaved correctly. `[binary]` `[verified]`

**I6 — no task existed to claim.** The brief instructed "run the `claim` command first." **No
`D126` task exists on the shared board**; the allocation lives in
`_ALLOC/registry.json`, where the Lead had already registered
`"126": {"lane": "source-diver"}` at `22:20:14`. I populated the `title` field from `pending` and
proceeded. **The only `in_progress` board item is `task-16`, a RETIRED-SUPERSEDED disposition from an
earlier round, which I declined to claim because claiming it would reopen a settled question.**
`[binary]` `[verified]`

**I7 — `D121` was taken by four lanes with no lock files while I performed the PAIR work.** The
allocator that would have prevented this post-dates the collision. Recorded, not re-litigated; `D126`
was reserved before this pass and no conflict exists as of the final check (COUNTED: 144 `.md`, zero
`D126*` files). `[binary]` `[verified]`

**No whole-line duplication detected in this report. All counts printed beside their input
cardinality: 17 files, 9 config-bearing binaries, 6 CLIs, 18 methods, 201 methods, 3 call sites,
4 claim classes, 5 controls, 144 `.md`.**

---

## §6 Status

| Item | Disposition |
|---|---|
| PAIR 1 residue — the other 17 | **ANSWERED.** 18/18 present; the binary cannot discriminate. R2 confirmed by measurement. `[binary]` `[verified]` |
| `.func1` streaming discriminator | **NEW, VALIDATED 201/201.** `[binary]` `[source]` `[verified]` |
| PAIR 3 disassembly half | **UNAVAILABLE by citation to D-21.** `[absence]` `[verified]` |
| PAIR 3 nil-guard reachability | **ANSWERED. HOLDS.** 2 of 3 callers guard correctly; `demons.go:5253` is the sole deferring caller. `[source]` `[verified]` |
| Name-table carve-out, generalised | **DONE.** Region bounds printed per target; garbage-token control passes on 3 of 3; live false positive caught on first non-sliver target. `[binary]` `[verified]` |
| C-11 S1/S3 user-agent identity | **CONFIRMED**, across 9 binaries not 3. `[binary]` `[verified]` |
| C-11 S2 field set | **CONFIRMED**, 19 fields × 9 binaries, all values identical. `[binary]` `[verified]` |
| C-11 S4 CLI negative | **CONFIRMED** with the enumeration shown. `[absence]` `[verified]` |
| PAIR 4 | Unchanged from D121: `[absence]` / NOT APPLICABLE. `[absence]` `[verified]` |
| PAIR 5 | Unchanged: BLOCKED, final, not written around. No Ruby toolchain; `bare?` unreachable by construction. `[inferred]` |

**Constraints honoured:** no execution · no REA · no `open_binary` · no network · no Ruby toolchain
(so every Rex/MSF claim stays `[inferred]`, never "executed") · D91/D85/D89/D93 corrected **by
reference, not edited** · every census prints input cardinality beside its result · no apostrophe in
probe strings · comment test on every census · `[absence]` reported with the enumeration shown, never
substituted from another artifact.

**D103 and D89 are read-only to this report and were not modified.**
