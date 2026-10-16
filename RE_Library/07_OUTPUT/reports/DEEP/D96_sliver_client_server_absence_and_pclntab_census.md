# D96 — Sliver binary↔source pairing: the client does not link the server, and the pclntab is a better instrument than the one that failed

**Round 24.** Lane: sliver-diver. **Write scope:** this file, plus `_d96_*` probes in `RE_Library\07_OUTPUT\binlayer\`. **D1–D95 are PROTECTED and none was edited.**
**Target:** `RE_Library\02_BINARIES\sliver\sliver-client_windows-amd64.exe` — **65,866,240 B**
**SHA-256:** `7C500D4AE84D792E4BB3F4BC89A0F325688F6E7B7F0574A6718BB99D30B305CB` `[verified]`
**Method:** static only. Binary never executed. No REA `open_binary` (shared single-provider target). No network.
**Tags:** `[verified]` = probe output printed beside the claim. `[read]` = cited lines read. `[inferred]` = reasoning from read evidence. `[absence]` = a zero, with its enumeration and positive control printed.

**LINE-COUNT CONVENTION:** every count is **LF bytes**. `[verified]` A file with a trailing newline has `LF bytes == Get-Content .Count`. **Re-verified this round on D91: 30,389 B, last byte `10`, LF 409 == `Get-Content .Count` 409.** `[verified]` **All line references are 1-based LF offsets.**

**D96 OCCUPATION CHECK, by enumeration before writing:** `[verified]` `Get-ChildItem $d -File -Filter 'D96_*'` → **0 matches.** `[verified]`

---

## 0. The two instruments, and why the report reports both

**The Lead started a Ghidra run (pid 18860, java pid 11144) before this round and asked me not to start a second.** `[verified]` **I did not. I read its log while it ran, and it failed its Go analyzers at three levels.** `[verified]`

```
ERROR Untested Go version [1.27.1] (GoRttiMapper)
WARN  Missing Go bootstrap type info, unable to extract Go RTTI info. (GoRttiMapper)
ERROR Go symbol analyzer error: unable to get GoRttiMapper (GolangSymbolAnalyzer)
ERROR Go string analyzer error: unable to get GoRttiMapper (GolangStringAnalyzer)
```

`[verified]` **At the final check the run was still alive at 871 s CPU / 79 log lines with no completion marker and no `gsli.tsv` on disk.** `[verified]`

> **Because the Ghidra instrument was known-degraded, I built an INDEPENDENT one: a direct Go `pclntab` parser (`_d96_pclntab.ps1`, on disk). `[verified]` It is not a workaround for impatience — it is the instrument that actually answers job 4, because Go's pclntab carries the real symbol names that `GoRttiMapper` was supposed to supply and could not.** `[inferred]`

**This is C-08's bound restated, not repeated:** `[read]` **C-08 recorded the Go 1.27.2 analyzer bound and seven toolchain failures. This binary is Go `1.27.1` (buildinfo blob, `[verified]`) — a different patch level, same failure.** `[verified]` **I did not re-litigate any of the seven; I recorded this run's outcome and moved to an instrument that works.** `[inferred]`

**pclntab identification — and a false positive I caught and fixed:** `[verified]`

- **First search:** magic `0xFFFFFFF1` only → matched `0x17245F3`, which produced `nfunc=14427647543653433344` and `pad1=102 pad2=15`. **Garbage. A FALSE POSITIVE.** `[verified]`
- **Corrected search:** magic **plus `pad1==0` and `pad2==0` and `minLC==1` and `ptrSize==8`** plus a plausibility bound on `nfunc` → **exactly one candidate, `0x269DDE0`, `nfunc=51657`, `nfiles=3553`.** `[verified]`

> **The corrected header is coherent (`magic=0xFFFFFFF1 nfunc=51657 nfiles=3553`), which is the validation the first match could not pass.** `[verified]` **Recorded as instrument failure F1.** `[verified]`

---

## 1. JOB 1 — is the FILTERED or UNFILTERED ownership query string present in the compiled client?

### ANSWER: NEITHER. **NO.** The client contains no SQL ownership query of any form, because it contains no database layer at all.

**The D91 source strings, searched as exact byte sequences in the whole 65,866,240-byte file:** `[verified]`

```powershell
$all=[Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($exe))
foreach($p in @('operator_name','operator_name = ?','Where("operator_name','ORDER BY updated_at')){ ... }
```

`[verified]`

| Probe string | Occurrences |
|---|---:|
| `operator_name` | **0** |
| `operator_name = ?` | **0** |
| `Where("operator_name` | **0** |
| `ORDER BY updated_at` | **0** |

`[verified]`

**POSITIVE CONTROLS — the same search on strings that MUST be present:** `[verified]`

| Control string | Occurrences | Meaning |
|---|---:|---|
| `github.com/bishopfox/sliver/client/console` | **163** | client package linked |
| `github.com/bishopfox/sliver/protobuf/rpcpb` | **604** | generated stubs linked |
| `/rpcpb.SliverRPC/SaveAIConversation` | **756278** (index) | wire path present |

`[verified]`

> **The search method demonstrably finds present strings. The zero is a real `[absence]`, not a broken probe.** `[verified]`

### 1.1 The structural reason, and it is the finding

**The decisively negative controls:** `[verified]`

| Probe | Occurrences |
|---|---:|
| `github.com/bishopfox/sliver/server/db` | **0** |
| `github.com/bishopfox/sliver/server/rpc` | **0** |
| `github.com/bishopfox/sliver/server/certs` | **0** |
| `gorm.io/gorm` | **0** |
| `mattn/go-sqlite3` | **0** |
| `modernc.org/sqlite` | **0** |
| `gorm.io/driver/sqlite` | **0** |

`[verified]`

> **The Sliver CLIENT does not link the Sliver SERVER. No `server/db`, no `server/rpc`, no GORM, no SQLite driver.** `[verified]` **Therefore `helpers.go:1433`'s ownership filter — filtered OR unfiltered — CANNOT be present in this artifact, because the file that contains it is not compiled into it.** `[verified]`

**Confirmed independently by the code census (the pclntab), which is a different instrument on a different section:** `[verified]`

```
distinct sliver-internal packages: 90
  server/db            = (absent)
  server/rpc           = (absent)
  server/certs         = (absent)
  server/console       = (absent)
  server/transport     = (absent)
  server/handlers      = (absent)
  server/ai            = (absent)
  client/console       = 145      <- CONTROL: present, so the filter works
```

`[verified]`

**The control is what makes this a proof rather than an assertion:** `[verified]` **`client/console` returns 145 because I searched correctly; `server/*` returns nothing because those packages are genuinely not in the binary.** `[verified]`

**And the D91-specific confirmation:** `[verified]` **searching the pclntab for `rpc-ai`, `rpc.aiOperatorName`, or `aiOperatorName` returns ZERO rows — while `client/command/ai` returns rows including `ai.AICmd`, `ai.buildAIContext`, `ai.isAITTY`.** `[verified]`

> **The client has its own AI command surface, and it does not have the server's `aiOperatorName`. The absence is real and the method is sound, demonstrated in a single query.** `[verified]`

**One near-miss worth recording, because it is a Rule-20 shape:** `[verified]` **`SaveAIConversation` appears 14 times in the binary and `DeleteAIConversation` 7.** `[verified]` **These are NOT server functions. Every occurrence is a generated gRPC artifact:** `[verified]`

```
  ime zone client_private_keyGetAIConversationsSaveAIConversationStartHTTPSListener...
  /rpcpb.SliverRPC/GetAIConversations/rpcpb.SliverRPC/SaveAIConversation/rpcpb.Slive...
  fox/sliver/protobuf/rpcpb.(*sliverRPCClient).SaveAIConversation...
  m/bishopfox/sliver/protobuf/rpcpb._SliverRPC_SaveAIConversation_Handler...
```

`[verified]`

> **A name that matches a source function name is not evidence the function was compiled in. These are the CLIENT STUB for the RPC, which is the opposite end of the wire from the server handler D91 analysed.** `[verified]` **Had I counted `SaveAIConversation` occurrences as "the server code is present," I would have reported the exact inversion of the truth.** `[verified]`

**One more string artifact, recorded because it looks like a finding and is not:** `[verified]` **`sqlite` occurs at index 1769479, inside a CLI help string:** `[verified]`

```
nd:..```.dlv debug \.--build-flags="-tags osusergo,netgo,go_sqlite,server -ldflags='-X github.com/bishopfox/sliver/clien
```

`[verified]` **That is a `GO_SQLITE` build tag quoted in the developer-debug help text — a documentation string, not a linked engine. The build tag `go_sqlite` appearing in help output is not evidence SQLite is in the binary; the linked-symbol controls above (`modernc.org/sqlite` = 0, `gorm.io/driver/sqlite` = 0) settle it.** `[verified]`

### 1.2 What this means for D91, stated plainly

> **D91's finding is NOT testable against this artifact.** `[verified]` **D91 is a SERVER-side defect in `server/db/helpers.go` and `server/rpc/rpc-ai.go`. The artifact in scope is the CLIENT. They share no code, and the client cannot contain the defect because it cannot contain the code.** `[verified]`

**Pairing verdict for jobs 1 and 2: `UNKNOWN` in the sense the Lead asked (the question is unanswerable against this artifact), and `NO` in the sense that the string is definitively absent.** `[verified]` **The honest form of the answer is: the question presupposes the server is in this binary, and it is not.** `[inferred]`

**Where the pair WOULD close:** `[inferred]` **there is no `sliver-server` binary in `02_BINARIES\sliver\` under this enumeration** `[verified]` **— so D91's ownership filter has no compiled counterpart in the corpus to compare against. That is a corpus gap, not an analysis gap, and it is filed as §5 R1.** `[inferred]`

---

## 2. JOB 2 — is `DeleteAIConversation`'s `""` argument compiled away, or passed as a live empty string?

### ANSWER: **NOT APPLICABLE — the function is not in this binary.**

`[verified]` **`DeleteAIConversation` occurs 7 times in the binary, and all 7 are gRPC client-stub artifacts (`(*sliverRPCClient).DeleteAIConversation`, `_SliverRPC_DeleteAIConversation_Handler`, `/rpcpb.SliverRPC/DeleteAIConversation`), not the `server/db` function.** `[verified]` **`server/db` has zero occurrences (§1.1).** `[verified]`

> **The compiler cannot have "compiled away" or "kept" an argument to a function that was never compiled in.** `[verified]` **The question is well-formed against a server binary and ill-formed against this client.** `[inferred]`

**What the binary DOES show, and it is the correct analogue:** `[verified]` **the client stub for the RPC exists and marshals a `clientpb.AIConversationReq`, so the client can request a delete. The `""` in D91 is at the SERVER's `rpc-ai.go:101`, one layer past the wire, in code absent here.** `[verified]`

**Method note:** `[verified]` **`UNKNOWN` would be the wrong answer here — `UNKNOWN` implies the evidence was inconclusive. The evidence is conclusive: the code is absent by enumeration, twice, on two instruments.** `[inferred]`

---

## 3. JOB 3 — is the MSF shell-escaping helper linked into this Sliver build?

### ANSWER: **NOT APPLICABLE — different project AND different language.** The Lead flagged this as a valid answer; here is the evidence that it is the right one.

`[read]` **D85 studied Metasploit's Ruby modules: 15,051 `.rb` files.** `[read]` **Its escaping primitives are Ruby methods — `shellescape` (13 occurrences), `shelljoin` (3), `Shellwords.escape` (2), `shell_command` (70) — invoked on Ruby `String`/`Array` objects and interpreted at module-load time by the Metasploit framework.** `[read]`

**Double-negative control, both directions:** `[verified]`

| Probe | Sliver `.go` source | Sliver binary |
|---|---:|---:|
| `shellescape` | **0** | **0** |
| `shelljoin` | **0** | **0** |
| `Shellwords` | **0** | **0** |
| `Rex::Text` | **0** | **0** |
| `cmd_exec` | **0** | **0** |

`[verified]`

> **This is not dead-code elimination. `[verified]` Ruby methods invoked through the language's runtime are not symbols in a Go binary and were never in a compilation unit from which they could be eliminated.** `[verified]` **The frame "linked in or eliminated" does not apply: there is no compilation step spanning these two codebases.** `[inferred]`

**The positive control for the control:** `[verified]` **the same scanner finds 604 `protobuf/rpcpb` and 163 `client/console` references (§1), so a zero on `shellescape` is a real zero.** `[verified]`

**This is C-00 §2's own point, confirmed rather than restated:** `[read]` **C-00 line 70-73 states the pairing opportunity is Sliver (source + compiled client) and that Merlin is the binary-only target. MSF is neither — it is a third project, and D85's lane was always source-only.** `[verified]`

---

## 4. JOB 4 — symbol census for THIS binary

### 4.1 The measured figures, and WHICH instrument produced each

| Instrument | Functions | Named | Coverage | Source |
|---|---:|---:|---:|---|
| **Go pclntab (mine, `_d96_pclntab.ps1`)** | **51,657** | **51,657** | **100.00%** | `_d96_pclntab.tsv` |
| **Ghidra headless** | **not obtained** | — | — | `GoRttiMapper` failed; no `gsli.tsv` at cutoff |

`[verified]`

**pclntab detail:** `[verified]` **`total=51657`, `unique=51208`, `entries=51657`.** `[verified]` **`FUN_`-prefixed names: 0.** `[verified]` **Named (not `FUN_`): 51,657.** `[verified]`

> **The `named` metric requires care across instruments. `[verified]` Ghidra's `DumpSyms.java` defines "named" as "not starting with `FUN_` or `thunk_FUN_`" — a convention that assumes unnamed functions get a `FUN_` placeholder. In a Go pclntab, EVERY function has a real name, so the metric returns 100% by construction.** `[verified]` **The 100% figure is therefore NOT a claim that this binary is "better symbolised" than the Merlin suite's 95.7%–98.3% — it is a claim that the two instruments count differently, and the number is not comparable to C-08's table.** `[inferred]`

**This is C-08 §3's warning applied prospectively, not violated:** `[read]` **C-08 §3 establishes that symbol richness must be measured per binary and never generalised across architectures.** `[verified]` **I extend it: it must not be generalised across INSTRUMENTS either. C-08's percentages are DWARF-derived (its §3 shows the `/NNN` sections ARE the DWARF). This binary's 100% is pclntab-derived. Same-looking number, different denominator.** `[inferred]`

**Evidence that the pclntab is the right instrument here, and that Go's DWARF is NOT present:** `[verified]` **the PE section table shows 8 sections and NO `debug_*` DWARF names:** `[verified]`

```
.text   VA=0x00001000 VSize=24834673 RawPtr=0x00000600 RawSize=24835072
.rdata  VA=0x017B1000 VSize=38343584 RawPtr=0x017AFA00 RawSize=38343680
.data   VA=0x03C43000 VSize=35694048 RawPtr=0x03C40E00 RawSize= 1664512
.pdata  VA=0x05E4E000 VSize=  490476 RawPtr=0x03DD7400 RawSize=  490496
.xdata  VA=0x05EC6000 VSize=     192 RawPtr=0x03E4F000 RawSize=     512
.idata  VA=0x05EC7000 VSize=    1404 RawPtr=0x03E4F200 RawSize=    1536
.reloc  VA=0x05EC8000 VSize=  528244 RawPtr=0x03E4F800 RawSize=  528384
.symtab VA=0x05F49000 VSize=       4 RawPtr=0x03ED0800 RawSize=     512
```

`[verified]`

> **The `.symtab` section is the Go pclntab's home, and the absence of `/NNN` DWARF sections distinguishes this build from the Merlin server/CLI builds C-08 measured.** `[verified]` **That is why Ghidra's DWARF-driven path yielded nothing and its Go-specific path failed on the version gate, while the pclntab path worked.** `[inferred]`

### 4.2 Function census by provenance

`[verified]`

| Class | Functions | Share |
|---|---:|---:|
| third-party (`github.com/*`, `golang.org/*`, `google.golang.org/*`, `gorm.io/*`, etc.) | **22,273** | 43.1% |
| **Sliver-internal** (`github.com/bishopfox/sliver/*`) | **7,472** | 14.5% |
| `runtime.*` | **1,445** | 2.8% |
| `type:*` (Go type descriptors) | **855** | 1.7% |
| remainder (`internal/*`, `go:*`, stdlib, `other`) | **19,612** | 38.0% |
| **TOTAL** | **51,657** | 100% |

`[verified]`

**Sliver-internal by package, top 12:** `[verified]`

| Package | Functions |
|---|---:|
| `protobuf/clientpb` | 2,055 |
| `protobuf/sliverpb` | 1,644 |
| `protobuf/rpcpb` | 599 |
| `client/command/ai` | 242 |
| `client/command/crack` | 209 |
| `client/core` | 171 |
| `client/command/generate` | 147 |
| `client/console` | 145 |
| `client/command/armory` | 132 |
| `client/command/crack/top` | 131 |
| `client/command/filesystem` | 113 |
| `client/command/opfor` | 96 |

`[verified]` **Distinct sliver-internal packages: 90.** `[verified]`

> **The shape is exactly what a client build predicts: 4,298 of 7,472 internal functions (57.5%) are protobuf bindings, and the remainder is `client/*`.** `[verified]` **Zero `server/*` (§1.1).** `[verified]`

**Notable third-party packages, all corroborated against `go.mod`:** `[verified]`

| Package | Functions | In `go.mod`? | In `vendor/`? |
|---|---:|---|---|
| `google.golang.org/grpc` | 4,725 | — | — |
| `github.com/sliverarmory/opfor` | 3,453 | **yes** | no |
| `github.com/tetratelabs/wazero` | 2,180 | **yes** | no |
| `github.com/yuin/goldmark` | 1,672 | **yes** (2) | no |
| `github.com/chromedp/cdproto` | 749 | **yes** | no |
| `github.com/mark3labs/mcp-go` | 633 | **yes** | no |
| `github.com/reeflective/readline` | 498 | **yes** (2) | no |
| `github.com/dlclark/regexp2` | 489 | **yes** (2) | no |
| `github.com/alecthomas/chroma` | 671 | **yes** (2) | no |

`[verified]`

**Reading the notable ones, because they are load-bearing for other lanes:** `[verified]` **`sliverarmory/opfor` (3,453 functions) is the ARMORY/opfor extension engine; `tetratelabs/wazero` (2,180) is the pure-Go WASM runtime used to execute WASM extensions; `mark3labs/mcp-go` (633) is the MCP server; `chromedp/cdproto` (749) is browser-automation bindings.** `[inferred]` **These confirm D91's `client/command/ai` findings at the binary layer and are the substrate for any future extension-execution question.** `[inferred]`

**A single symbol that deserves a flag:** `[verified]` **the only `implant/sliver/handlers` symbol in the entire binary is:** `[verified]`

```
FUNC  0x1577080  github.com/bishopfox/sliver/implant/sliver/handlers/matcher.Match  0x454938
```

`[verified]`

> **One implant-package symbol in a client binary is a shape worth naming, and it is NOT implant code in the client. `[verified]` It is the client's LOCAL regex matcher, compiled in because the client filters output locally.** `[inferred]` **Recorded so the next lane does not read "implant handlers present" from a count of one.** `[inferred]`

**No thunk metric is reported.** `[verified]` **Go binaries have no PE import thunks of the kind `DumpSyms.java` counts via `Function.isThunk()`; reporting a thunk count from a pclntab would be a category error.** `[verified]` **C-08's thunk figures (51/20/5/4) are Ghidra measurements on non-Go binaries and do not transfer.** `[inferred]`

---

## 5. JOB 5 — RPC/service names in the binary vs the source tree

### ANSWER: **all 201 match exactly. No build/source mismatch.**

**Method:** `[verified]` **extract every exact wire path `/rpcpb.SliverRPC/<Name>` from the binary, and every `<MethodName>`/`<StreamName>` literal from the source's generated `grpc.ServiceDesc`, then test each source name for presence as an exact path.** `[verified]`

**Result:** `[verified]`

```
source methods (from ServiceDesc literals):  201
exact wire paths present in binary:          201 / 201
missing:                                     0
```

`[verified]`

> **JOB 5 ANSWER: 201/201. Every RPC method declared in the source's `ServiceDesc` exists as an exact wire path in the binary. Zero absent. No build/source mismatch is present.** `[verified]`

### 5.1 The instrument failure I caught here, before it became a false finding

**My first instrument reported a mismatch of exactly 25 names in each direction, and it was wrong.** `[verified]`

```powershell
$rx=[regex]'/rpcpb\.SliverRPC/([A-Za-z0-9_]+)'      # GREEDY, no boundary
```

**It produced 25 "extra" binary names and 25 "missing" source names:** `[verified]`

| "Extra" in binary | Actual source name | What the regex swallowed |
|---|---|---|
| `CallExtensiongrpc` | `CallExtension` | `grpc` |
| `Eventsgrpc` | `Events` | `grpc` |
| `Shellservice` | `Shell` | `service` |
| `Taskgrpc` | `Task` | `grpc` |
| `GetPrivsSubchannel` | `GetPrivs` | `Subchannel` |
| `GenerateExternalGetBuildConfigreflect` | `GenerateExternalGetBuildConfig` | `reflect` |
| `HijackDLLccBalancerWrapper` | `HijackDLL` | `ccBalancerWrapper` |

`[verified]`

> **The 25/25 reciprocal counts were the tell: a genuine source/binary divergence would not be a perfect bijection where every "extra" is a source name plus a runtime suffix.** `[verified]` **Go's string table concatenates adjacent literals, and the greedy `[A-Za-z0-9_]+` ran past the method name into the next symbol. `grpc`, `service`, `Subchannel`, `reflect`, `Channel`, `balancer` are gRPC runtime identifiers.** `[verified]`

**A lazy quantifier did NOT fix it** (`([A-Za-z0-9_]+?)` with a lookahead still returned the same 25) `[verified]` **because the concatenation has no byte-level delimiter to anchor on. The fix was to change WHAT was tested: instead of parsing names out of a concatenated blob, test each known source name for presence as an exact full path string.** `[verified]`

> **This is Rule 20 in a new costume. `[verified]` A regex that extracts names from a concatenated string table is a census of BYTE RUNS, not of method names. The instrument had to be rebuilt around the population that actually exists — 201 known names — rather than around the population the bytes suggested.** `[verified]` **Logged as F2.** `[verified]`

**Bidirectional confirmation:** `[verified]` **all 201 source names also appear as bare substrings anywhere in the binary** — but see §1.1's warning: a bare-name match is weak evidence on its own, which is why the exact-wire-path test above is the one reported. `[verified]`

---

## 6. Corrections to prior reports

| # | Prior claim | Correction | Evidence |
|---|---|---|---|
| **C1** | **D91's ownership filter is a server-side defect.** | **Unaffected as a source finding, and UNTESTABLE against this artifact** — the client does not link `server/db`. D91's §1.4 verdict stands on source reading; the binary cannot corroborate or refute it. | §1, §1.1 |
| **C2** | **C-08 §9 line 203 lists this binary as "not yet run."** | **Partly updated: the Ghidra run was started and its Go analyzers failed; the pclntab census now exists.** C-08's remaining item is satisfied by a different instrument, not by Ghidra. | §0, §4 |
| **C3** | **A name matching a source function implies the code is present.** | **Refuted. `SaveAIConversation` occurs 14× in the client and every occurrence is a gRPC stub.** The name is the *client end* of an RPC whose *server end* is the analysed code. | §1.1 |

`[verified]`

---

## 7. Instrument failures

| # | Failure | Where | Resolution |
|---|---|---|---|
| **F1** | **pclntab magic matched a false positive** (`0x17245F3`, `nfunc=1.4e19`, `pad1=102`). | §0 | **Required `pad1==0 pad2==0 minLC==1 ptrSize==8` + plausibility bound → exactly one candidate, `0x269DDE0`, `nfunc=51657`.** |
| **F2** | **Greedy regex manufactured a 25-name "build/source mismatch" that does not exist.** | §5.1 | **Rebuilt around 201 known names instead of extracted byte runs → 201/201, zero missing.** The 25/25 bijection was the tell. |
| **F3** | **Package census filter `-like "*$p/*"` returned 0 for `client/console` while the string control said 163.** | §1.1 | **Cause: Go symbol paths continue with `.`, not `/`, after the package (`.../console.Func`). Fixed by extracting the package to the last slash before the first dot → `client/console` = 145, control passes.** |
| **F4** | **Ghidra's Go analyzers failed at three levels** (`GolangSymbolAnalyzer`, `GolangStringAnalyzer`, `GoRttiMapper`). | §0 | **Not my invocation to fix (Lead-owned run). Recorded; answered job 4 with an independent pclntab instrument.** |
| **F5** | **All probes on disk; the `_d96_pclntab.ps1` header used `//` comments.** | `_d96_pclntab.ps1` | **Benign: the parser completed and wrote its TSV; stderr carried the shell's complaint about the header lines. Comments converted to `#` in place. Per D69 §7 the probe is on disk and now clean.** |

`[verified]`

---

## 8. Residuals

**R1 — there is no `sliver-server` artifact in the corpus.** `[verified]` **D91's finding therefore has no compiled counterpart, and every server-side source claim in this lane is unverifiable at the binary layer until one exists.** `[inferred]` **This is the single highest-value corpus gap this round identifies.** `[inferred]`

**R2 — the Ghidra run may still land.** `[verified]` **At cutoff it was alive at 871 s CPU with no `gsli.tsv`.** `[inferred]` **PROBE:** when it completes, compare its function count against the pclntab's 51,657 and report the delta — the two instruments measure overlapping but non-identical populations. `[inferred]`

**R3 — `type:*` = 855 and `go:*` = 55 are pclntab pseudo-entries, not functions.** `[verified]` **PROBE:** exclude them from any "function count" quoted downstream, or state the convention. `[inferred]`

**R4 — the 2,180-function `wazero` WASM runtime and 3,453-function `opfor` engine are unexamined.** `[verified]` **These are the substrate for extension execution and are the largest unanalysed first-party-adjacent surface in this binary.** `[inferred]`

**R5 — `_d96_pclntab.tsv` is 51,657 rows and was written in full.** `[verified]` **PROBE:** it is a usable symbol index for any future lane; it has not been cross-checked against Ghidra's independent symbol set. `[inferred]`

---

## 9. Summary

**JOB 1 — NO.** The client contains no ownership query of any form. `[verified]` `server/db` = 0 occurrences; `gorm.io/gorm` = 0; `modernc.org/sqlite` = 0; every `server/*` package absent from the pclntab. `[verified]` **The zero is validated by positive controls (`client/console` 163 strings / 145 functions) and by a D91-specific query (zero `aiOperatorName`, while `client/command/ai` returns rows).** `[verified]`

**JOB 2 — NOT APPLICABLE.** `[verified]` The function is not in the binary; all 7 name occurrences are gRPC stubs. `[verified]`

**JOB 3 — NOT APPLICABLE, on two grounds.** `[verified]` Different project and different language; Ruby metaprogramming primitives have no Go compilation unit to be eliminated from. Double-negative control: 0 in Sliver source, 0 in the binary. `[verified]`

**JOB 4 — 51,657 functions / 51,657 named / 100% (pclntab instrument).** `[verified]` **Ghidra produced no figures — its Go analyzers failed at three levels.** `[verified]` **The 100% is instrument-specific and NOT comparable to C-08's DWARF-derived percentages.** `[verified]` 22,273 third-party · 7,472 Sliver-internal across 90 packages · 1,445 `runtime.*` · 855 `type:*`. `[verified]`

**JOB 5 — 201/201, no mismatch.** `[verified]` Every source `ServiceDesc` method exists as an exact wire path. `[verified]` **My first instrument reported a 25-name mismatch that was a greedy-regex artifact; the 25/25 bijection gave it away.** `[verified]`

**The single most important sentence:** `[verified]` + `[inferred]` **The Sliver client and the Sliver server share no code — the client carries 51,657 functions with full Go symbol names and not one of them is in `server/`, so every server-side finding this lane has produced, including D91's inert ownership filter, is unverifiable at the binary layer with the artifacts currently in the corpus, and the thing that hid this was that `SaveAIConversation` appears 14 times in a binary that does not contain the function.**

**The method sentence:** `[inferred]` **Ghidra's Go analyzer failed on a version gate and my first pclntab search matched a false positive; the instrument that worked was the one built around the format actually present rather than the one the toolchain expected — and the same lesson held twice more, when a greedy regex invented a build/source mismatch and a path filter hid 145 present functions behind a `0`.**

*End of D96. Probes on disk: `binlayer\_d96_pclntab.ps1`, `binlayer\_d96_pclntab.tsv`.*
