# D161 — R-147.1: THE SOURCE SIDE OF THE LANGUAGE BOUNDARY, AND THE `guard present` / `guard dominates` DISTINCTION

**Author:** `havoc-deep` · **Lane:** `havoc-deep` · **Round:** 9
**Method:** Go source read of the Havoc teamserver tree + byte-level and instruction-level reads of every Go binary in the corpus whose version is readable. No execution. No network. No live C2. No REA.
**Write scope:** this file and the `D161_*` instruments under `07_OUTPUT/binlayer/`. `D1`–`D160` protected and untouched.

**SCOPE:** three questions left open by D147 — (Q1) whether the nil-check idiom and guard-before-deref ordering changed between Go 1.21 and Go 1.27, answered by measurement rather than assertion; (Q2) the exact structure at `demons.go:5253-5265`, and whether the guard **dominates** every dereference of the same value; (Q3) the caller side of the nil return.
**DEFINER SCOPE:** the pair's fixed half (D89) was read in D147 and is **adopted, not re-derived**. What is newly established here is read from `agent.go`, `demons.go` and `handlers.go` directly, at line numbers cited per quote.
**CONDITIONAL SCOPE:** the Q1 table is a census over **corpus binaries only**. The direction of every count is stated per row. **The central Q1 result is a NEGATIVE and its scope is the corpus, not Go.**
**COUNTED:** 4 distinct nil-path returns in `ParseDemonRegisterRequest`, **3 nil** · 6 `DemonInfo` uses between parse and guard, **2 unambiguous dereferences** · 3 callers of the function, **2 correctly guarded, 1 not** · 7 distinct Go binaries, **2 distinct Go versions (1.27.1, 1.27.2)** · **0 Go 1.21 binaries** · 4 `CMP RAX,0` occurrences in every binary measured · 0 `toolchain` directives in 6 `go.mod` files.

---

## §0 — HEADLINE

**Q2 is the real result, and it is sharper than D89 or D147 stated: `guard present` is not `guard dominates`, and at `demons.go:5265` the guard dominates NOTHING.**

**The guard sits 12 lines after the parse, and SIX uses of `DemonInfo` precede it — two of which are unambiguous nil-dereferences.** The guard at `:5265` is **outside** the `if/else` block that contains every one of those uses. Its branch body contains **only message-formatting code**. It is a message-selection check written 12 lines too late to function as a validity check. [source: §2]

**That the guard's dominance is zero is not an inference from adjacency — it is demonstrated by a controlled comparison three ways on the identical call.** `ParseDemonRegisterRequest` has three callers. Two place the guard **one line** after the call, and in both the guarded block **contains every subsequent dereference**. The third does neither. [source: §4]

**Q1's answer is a NEGATIVE and it must be delivered as one: the corpus contains NO Go 1.21 binary, so the 1.21→1.27 idiom question CANNOT be answered by measurement from this corpus.** What the corpus does support is measured and tabulated: the idiom is **stable across 1.27.1→1.27.2 across two independent codebases** — `TEST reg,reg` followed by a branch in **93.3% / 93.4% / 94.2%** of occurrences, with `CMP reg,0` an invariant **4** in every binary. [source: §3]

**A structural finding that narrows D147's own transfer limit:** Havoc's `go 1.21.0` is a `go.mod` **language floor, not a compiler pin** — the module carries **no `toolchain` directive**, and **no build recipe, CI file or image tag in the tree pins a Go version.** Whether Havoc's artifact would come out 1.21-compiled or 1.27-compiled is **undetermined by the tree**, and D147's stated five-minor gap may therefore be **zero in practice.** [source: §5]

**Q3 answered by reading, not inference: the caller guards exist, and the two that are correct are correct in the same way.** [source: §4]

---

## §1 — METHOD AND THE FIXED HALF

### 1.1 What was adopted rather than re-derived

**D147 §1 established the pair's fixed half.** D89's source-side answer — guard at `:5265`, dereference at `:5254`, four returns of which three are nil — is **adopted here as a premise** and is **independently re-verified** in §2.2 rather than trusted. The re-verification was performed because Q2 changes the framing: D89 filed **one** dereference; §2.3 finds **six uses, two of them dereferences.** [source: D89 §1.2–§1.5 via D147 §1; §2 below]

### 1.2 Instruments

- **Byte-level idiom scanner:** counts `TEST r64,r64` (`REX.W 0x85` with ModRM `mod=11`) and `CMP RAX,0` (`48 83 F8 00`) in raw file bytes. **Depends on no symbol table.**
- **Byte-level ordering scanner:** counts `TEST r64,r64` immediately preceded by `CALL rel32` (`0xE8`) and immediately followed by `Jcc` (`0x70-0x7F` short, `0x0F 0x80-0x8F` near). **Depends on no symbol table.**
- **Instruction reader:** `D147_NilGuardGen.java` (D147, proven), Ghidra 12.1.4 headless, positional via `.bat`, never `-readOnly`, function name baked in because `gate.bat:42` has one script-argument slot.
- **Symbol reader:** `DumpSyms.java`, which prints `total=` / `named=` / `bodybytes=` as a **denominator**.

**Why the byte-level instruments carry Q1:** §3.3 shows the symbol reader is **useless on one of the four binaries** (`named=1` of 41,528). A measurement that depends on symbol mapping would have silently reported the stripped binary as having no idiom at all.

---

## §2 — Q2: THE STRUCTURE AT `:5253`–`:5265`, IN FULL

### 2.1 The block, read directly

```
5222   var DemonInfo *Agent                                    <- declared NIL
5223
5224   // if agent exist then just retrieve the instance by agent id
5225   if teamserver.AgentExist(AgentHdr.AgentID) {
5226
5227       DemonInfo = teamserver.AgentInstance(AgentHdr.AgentID)   <- ARM A: assigned
...
5250   } else {
5251       // if the agent doesn't exist then we assume that it's a register request from a new agent
5252
5253       DemonInfo = ParseDemonRegisterRequest(AgentHdr.AgentID, AgentHdr.Data, "")   <- ARM B: MAY BE NIL
5254       DemonInfo.Pivots.Parent = a
5255
5256       a.Pivots.Links = append(a.Pivots.Links, DemonInfo)
5257       teamserver.LinkAdd(a, DemonInfo)
5258
5259       DemonInfo.Info.MagicValue = AgentHdr.MagicValue
5260
5261       teamserver.AgentAdd(DemonInfo)
5262       teamserver.AgentSendNotify(DemonInfo)
5263   }
5264
5265   if DemonInfo != nil {
5266       Message["Type"] = "Good"
5267       Message["Message"] = "[SMB] Connected to pivot agent [" + a.NameID + "]-<>-<>-[" + DemonInfo.NameID + "]"
5268   } else {
5269       Message["Type"] = "Error"
5270       Message["Message"] = "[SMB] Failed to connect: failed to parse the agent"
5271   }
```

**Read as structure, four facts follow.** [source: `demons.go:5222-5271`]

### 2.2 Fact 1 — the guard is evaluated after BOTH arms, and covers neither

**`DemonInfo` is declared nil at `:5222` and assigned in both arms** — `:5227` (registry hit) and `:5253` (parse). **The guard at `:5265` is outside the `if/else` that closes at `:5263`.** It therefore runs after either assignment, and **neither assignment is checked.**

### 2.3 Fact 2 — six uses precede the guard, two are unambiguous dereferences

| line | use | dereferences `DemonInfo`? |
|---|---|---|
| `:5254` | `DemonInfo.Pivots.Parent = a` | **YES** — field write through `DemonInfo` |
| `:5256` | `append(a.Pivots.Links, DemonInfo)` | **NO** at this line — pointer passed by value; but a possibly-nil pointer is **stored into `a.Pivots.Links`** |
| `:5257` | `teamserver.LinkAdd(a, DemonInfo)` | **callee-dependent** — not read here |
| `:5259` | `DemonInfo.Info.MagicValue = ...` | **YES** — field write through `DemonInfo` |
| `:5261` | `teamserver.AgentAdd(DemonInfo)` | **callee-dependent** |
| `:5262` | `teamserver.AgentSendNotify(DemonInfo)` | **callee-dependent** |
| **`:5265`** | **`if DemonInfo != nil`** | **the guard — after all six** |

**Two unambiguous dereferences, and `:5254` is the FIRST statement executed on the parse result.** [source: `demons.go:5253-5265`]

### 2.4 Fact 3 — the guard's block contains no dereference of its own to protect

**The `if` body at `:5266-5267` sets two map entries and builds a string.** The only use of `DemonInfo` inside it is `DemonInfo.NameID` at `:5267`. **Every dereference the guard could have protected is outside it and before it.** The guard's branch body is message formatting.

### 2.5 Fact 4 — the guard is a MESSAGE-SELECTION check, and that is its mechanism

**The defect's mechanism is now nameable rather than merely located.** The guard exists to choose between `"Good"` and `"Error"` in a status message — the `else` at `:5268` writes *"Failed to connect: failed to parse the agent"*, which is **exactly the nil case it is too late to handle.** The author knew the parse could fail; the guard is in the right *shape* for that knowledge and in the wrong *position*. **`guard present` is satisfied. `guard dominates` is not.**

### 2.6 D89's fixed half, independently re-verified

**`ParseDemonRegisterRequest` spans `agent.go:328-606` (279 lines).** Four returns, **three nil**, read directly:

| line | statement | preceding context |
|---|---|---|
| `:409` | `return nil` | `if AgentID != DemonID {` / `if AgentID != 0 {` / *"Failed to decrypt agent init request"* |
| `:596` | `return Session` | the **only** success path |
| `:599` | `return nil` | *"Agent: %x, Command: REGISTER, Invalid packet"* |
| `:604` | `return nil` | *"Agent: %x, Command: REGISTER, Invalid packet"* |

**Three of four returns are nil, confirming D89 from source.** [source: `agent.go:409`, `:596`, `:599`, `:604`]

---

## §3 — Q1: THE VERSION/IDIOM TABLE, AND THE NEGATIVE IT PRODUCES

### 3.1 The corpus cannot answer the question as posed, and that is the first finding

**The question is 1.21 vs 1.27. The corpus contains no Go 1.21 binary.**

**Every binary corpus-wide over 300 KB (60 files) was scanned for a `Go buildinf` header (whole-file, not a window): 12 carry readable buildinfo, and all 12 are `go1.27.2`.** The distinct set is 7 binaries after SHA-256 deduplication — 6 Merlin artifacts that ship `.zdebug_info`, and 1 Sliver binary. **The two distinct Go versions present are `1.27.1` and `1.27.2`: a PATCH difference.** [source: §3.2; dedup by SHA-256]

**`go 1.21.0` appears in this corpus only as a `go.mod` directive** — in the Havoc teamserver, the very target under study. **No artifact compiled by it exists here.** [source: §5.1]

**Therefore: the 1.21→1.27 idiom question is NOT answerable by measurement from this corpus.** What follows is what the corpus *does* support, with its scope stated per row.

### 3.2 The Go binaries present, with denominators

| binary | Go version | symbols (`named`/`total`) | symbol source | SHA-256 distinct |
|---|---|---|---|---|
| `sliver-client_windows-amd64.exe` | **1.27.1** | **1 / 41,528** | none mapped | yes |
| `merlinServer-Windows-x64.exe` | 1.27.2 | 16,971 / 17,265 | compressed DWARF | yes |
| `merlinCLI-Windows-x64.exe` | 1.27.2 | (DWARF) | compressed DWARF | yes |
| `merlin.x64.dll` | 1.27.2 | (DWARF) | compressed DWARF | yes |
| `merlin.x86.dll` | 1.27.2 | (DWARF) | compressed DWARF | yes |
| `merlinAgent-Windows-x64.exe` | 1.27.2 | (DWARF) | compressed DWARF | yes |
| `merlinAgent-Windows-x64-Debug.exe` | 1.27.2 | (DWARF) | compressed DWARF | yes |

**Distinct Go versions: 2. Distinct codebases: 2 (Merlin, Sliver). Distinct binaries: 7.** [source: buildinfo scan; SHA-256 dedup]

### 3.3 The reader fails on one binary, and the failure is the reason the control matters

**`sliver-client` returns `named=1` out of `total=41,528`.** Compare Merlin: `named=16,971` of `17,265` (98.3%).

**Cause, measured:** the Sliver binary is **stripped**. `.zdebug_info` count is **1** in the Merlin binaries (compressed DWARF present) and **0** in Sliver. Both hit the identical Ghidra RTTI failure — `ERROR Untested Go version [1.27.1]` and `[1.27.2]`, `Missing Go bootstrap type info` — **so the version is not the cause; the debug-info state is.**

**Substantive control:** Sliver's bytes **do** contain the names — `github.com/bishopfox` **10,266** occurrences, `runtime.panic` **23**, `runtime.gcStart` **5**, `main.main` **1**. **The names exist in the file; Ghidra did not map them to addresses.**

**This is the distinction the brief demanded, in its exact form.** `named=1` is **NOT** evidence that Sliver has no named functions. It is evidence that **the reader could not map them.** Those are different conclusions, and **only one of them is about Sliver.** Had Q1 been measured by symbol lookup, the stripped binary would have contributed a row of zeros indistinguishable from a real result. **This is why Q1 is measured at the byte level.** [source: §3.4; symbol TSVs `D147_merlinServer.ghidra-symbols.tsv`, `D161_sliver.ghidra-symbols.tsv`]

### 3.4 The idiom table — byte-level, symbol-independent

**`TEST r64,r64`** is the Go nil/zero test (`REX.W 0x85` with `mod=11`). **`CMP RAX,0`** is the contrasting immediate form (`48 83 F8 00`).

| binary | Go ver | `TEST reg,reg` | `CMP RAX,0` | ratio |
|---|---|---|---|---|
| merlinServer | 1.27.2 | **23,806** | **4** | 5,952 : 1 |
| merlinCLI | 1.27.2 | **18,273** | **4** | 4,568 : 1 |
| merlinAgent | 1.27.2 | **17,586** | **4** | 4,397 : 1 |
| sliver-client | **1.27.1** | **61,850** | **4** | 15,463 : 1 |

**The idiom is uniformly `TEST reg,reg`.** The contrast form is **4 in every binary** — identical across four unrelated binaries of two versions and two codebases. **That invariance is itself a control:** a scanner that had mis-tuned its opcode match would not produce the same small constant four times. [source: byte scan, §3.5]

### 3.5 The ordering table — the guard-after-call pattern

**`TEST reg,reg` immediately preceded by `CALL rel32`, and immediately followed by `Jcc`.**

| binary | Go ver | `TEST reg,reg` | preceded by `CALL` | followed by `Jcc` | rate |
|---|---|---|---|---|---|
| merlinServer | 1.27.2 | 23,806 | 4,263 | **22,240** | **93.4%** |
| merlinCLI | 1.27.2 | 18,273 | 3,133 | **17,048** | **93.3%** |
| sliver-client | **1.27.1** | 61,850 | 12,185 | **58,261** | **94.2%** |

**The pattern is stable across the version change and across two independent codebases**, within 0.9 percentage points. [source: byte scan, §3.5]

### 3.6 What the table does and does not establish

| claim | status |
|---|---|
| The idiom is `TEST reg,reg`, not `CMP reg,0` | **measured**, 4 binaries, both versions |
| The idiom is **stable across 1.27.1 → 1.27.2** | **measured**, 3 binaries, 2 codebases, ≤0.9pp spread |
| `TEST reg,reg` is usually followed by a branch | **measured**, 93.3–94.2% |
| The idiom is **stable across 1.21 → 1.27** | **NOT ESTABLISHED** — **no 1.21 binary exists in this corpus** |
| Any specific guard in Havoc sits before its deref | **NOT CLAIMED** — no Havoc artifact exists |

**The negative is the deliverable.** A table showing stability across a patch revision is **consistent with** stability across five minors; it is **not evidence of it.** Stating otherwise would be the Rule 32 error — a probe that produced a **plausible number** in place of the one it could not reach. [source: §3.1]

### 3.7 The scanner's limits, stated

- **`TEST reg,reg` counts ALL self-tests**, not only nil checks — boolean results (`TEST AL,AL`) and other zero tests are included. **It measures idiom preference, not guard semantics.**
- **`followed by Jcc` does not assert the branch TESTS the value** or where it goes. **It measures adjacency, not dominance.** Dominance is established in §2 and §4 by reading structure, not by this scan.
- **`CMP reg,0` counts only the `RAX` form.** Other registers were not scanned. **The `4` is a lower bound on one form, not a total.**

---

## §4 — Q3: THE CALLER SIDE, AND THE CONTROLLED COMPARISON THAT SETTLES Q2

**`ParseDemonRegisterRequest` has exactly three callers in the tree.** Read in full: [source: tree-wide grep, `pkg/agent/agent.go`, `pkg/agent/demons.go`, `pkg/handlers/handlers.go`]

### 4.1 `handlers.go:273` — CORRECT

```
273   Agent = agent.ParseDemonRegisterRequest(Header.AgentID, Header.Data, ExternalIP)
274   if Agent == nil {
275       return Response, false
276   }
277
278   Agent.Info.MagicValue = Header.MagicValue
279   Agent.Info.Listener = nil
...
281   Teamserver.AgentAdd(Agent)
```

**Guard one line after the call, as an early return, and every subsequent dereference is dominated by it.** [source: `handlers.go:273-282`]

### 4.2 `agent.go:568` — CORRECT

```
568   PivotSession = ParseDemonRegisterRequest(PivotAgentID, PivotParser, RoutineFunc)
569   if PivotSession != nil {
570       PivotSession.Info.MagicValue = HdrMagicValue
...
580       PivotSession.Pivots.Parent = Session
581   }
```

**Guard one line after the call, and ALL six dereferences are INSIDE the guarded block.** [source: `agent.go:568-581`]

### 4.3 `demons.go:5253` — DEFECT

**Guard 12 lines after the call, and every dereference is OUTSIDE the guarded block and BEFORE it.** [source: §2]

### 4.4 The comparison, and precisely what it establishes

| caller | guard offset | guard body contains the dereferences? | verdict |
|---|---|---|---|
| `handlers.go:273` | **+1 line** | **yes** — early return dominates all | **CORRECT** |
| `agent.go:568` | **+1 line** | **yes** — block encloses all six | **CORRECT** |
| `demons.go:5253` | **+12 lines** | **no** — block holds message formatting only | **DEFECT** |

**Same function. Same nil-return contract. Three call sites. Two correct, one not.**

**This is what converts Q2 from an observation about line distance into a structural claim.** The two correct callers share a property the defective one lacks: **the guard's block contains every dereference.** Distance is a symptom; **containment is the property.** `guard present` is satisfied in all three. `guard dominates` is satisfied in two. [source: §4.1–§4.3]

**And the third caller's own comment names the author's awareness:** `:5251` reads *"if the agent doesn't exist then we assume that it's a register request from a new agent"*, and `:5253` calls a function whose failure mode is documented by its own three nil returns. [source: `demons.go:5250-5253`]

---

## §5 — THE TOOLCHAIN QUESTION, AND A CORRECTION TO D147'S STATED GAP

**D147 §3 recorded *"Go 1.27.2 measured vs Havoc's `go 1.21.0` — a five-minor gap"* as a transfer limit. Reading the tree narrows that limit, and the narrowing is a correction to my own prior framing.**

### 5.1 `go 1.21.0` is a language floor, not a compiler pin

```
module Havoc

go 1.21.0

require ( ... )
```

**The module directive is `go 1.21.0`. There is NO `toolchain` directive.** Under Go's toolchain semantics the `go` directive sets the **minimum language version** the module requires; it does **not** select the compiler that builds it. **Any Go ≥ 1.21.0 builds this module.** [source: `teamserver/go.mod`]

### 5.2 Nothing in the tree pins a builder, and the control for that is honest

**Searched:** every `Makefile`, `Dockerfile`, `*.yaml`, `*.yml`, `*.sh`, `*.md`, `*.txt` under the Havoc tree for `golang:`, `GO_VERSION`, `go-version`, `go1.2*`. **No pin found.** `Install.sh` exists at the tree root; no Go version string appears in it.

**CONTROL, and it matters:** **0 of 6 `go.mod` files in this corpus carry a `toolchain` directive.** The form is **absent from the corpus entirely** — including `sliver/go.mod` (`go 1.27.2`, no toolchain) and `mythic-docker/src/go.mod` (`go 1.25.1`, no toolchain).

**Therefore the absence of a `toolchain` directive in Havoc is NOT evidence that Havoc deliberately declined to pin.** It is evidence that **no project in this corpus uses the form** — which is a statement about the corpus, not about Havoc. **Those are different conclusions and the control is what separates them.** [source: 6 `go.mod` files; control above]

### 5.3 The tree is datable from its dependency pins, by comparison within the corpus

| dependency | Havoc | Sliver |
|---|---|---|
| `golang.org/x/crypto` | **v0.27.0** | v0.55.0 |
| `golang.org/x/text` | **v0.18.0** | v0.41.0 |
| `golang.org/x/net` | **v0.29.0** (indirect) | v0.58.0 |

**Havoc's pins sit at roughly half Sliver's version numbers** — a within-corpus comparison of two C2 source trees. **This corroborates that the Havoc tree predates the Sliver tree by a substantial margin**, consistent with `go 1.21.0` against `go 1.27.2`. [source: both `go.mod` files]

### 5.4 What this does to D147's transfer limit

| D147's statement | corrected reading |
|---|---|
| "1.27.2 measured vs Havoc's 1.21.0 — five-minor gap" | **the gap is not fixed by the tree** — `go 1.21.0` is a floor and no builder is pinned |

**The practical consequence:** whoever builds Havoc today with whatever Go they have installed produces a binary compiled by **that** compiler — **possibly 1.27.x**, in which case D147's mechanism result is measured on **the very version that would build it**, and the gap is **zero**. The tree does not decide this. **`[inferred]` — the tree licenses the reading; it does not measure a build.** [source: §5.1–§5.3]

**No binary can be produced to test this: `go` is not on PATH on this machine, and the no-execution constraint holds independently.** [source: toolchain probe]

---

## §6 — Q3 CLOSED, Q1 ANSWERED AS A NEGATIVE, Q2 SHARPENED

| question | answer | basis |
|---|---|---|
| **Q1** — did the idiom change 1.21→1.27? | **NOT MEASURABLE HERE** — no 1.21 binary exists. Idiom **stable across 1.27.1→1.27.2**, 2 codebases, ≤0.9pp | §3 |
| **Q2** — what is the structure, and does the guard dominate? | **Guard at `:5265` DOMINATES ZERO** of 6 preceding uses; 2 are dereferences; guard is a message-selection check. **Controlled 3-way comparison: 2 correct callers, 1 not** | §2, §4 |
| **Q3** — what does the caller do with a nil? | **Three callers. Two guard correctly (+1 line, block encloses all derefs). One does not (+12 lines, block encloses none)** | §4 |

---

## §7 — RESIDUALS

| id | residual | status |
|---|---|---|
| **D161-R1** | **R-147.1 remains OPEN.** A build of `teamserver/` would settle the mechanism on Havoc's own artifact. **The instrument is written and proven; the operand is sourced and read; the missing piece is NAMED: a Go toolchain and an artifact.** `go` is not on PATH; no execution permitted. | **`[blocked]`** |
| **D161-R2** | The 1.21→1.27 idiom question is unanswerable from this corpus — **0 Go 1.21 binaries.** | **`[blocked]`** — corpus boundary |
| **D161-R3** | The builder's Go version for Havoc is **undetermined by the tree** (no `toolchain`, no CI pin). | `[inferred]` — §5 |
| **D161-R4** | `agent.go:5256` stores a possibly-nil `DemonInfo` into `a.Pivots.Links` before any check. **Whether a nil element there is later dereferenced is NOT read here.** | **open** — new |
| **D161-R5** | Three callee-dependent uses (`LinkAdd :5257`, `AgentAdd :5261`, `AgentSendNotify :5262`) were **not read**; whether any dereferences a nil is unestablished. | **open** — new |
| **D161-R6** | The `:5231` arm reads `DemonInfo.Pivots.Parent` on the registry-return path; **whether `AgentInstance` can return nil for an ID `AgentExist` reported present is NOT read.** | **open** — new |
| **D161-R7** | D89's D-1/D-2/D-3 (concurrency; `ToMap` callers) **remain open and are NOT advanced.** No data-race analysis performed. **Runtime reachability is not claimed anywhere in this report.** | inherited |

---

## §8 — CONTROL INVENTORY

**D149 shape audit.** Every count below can fail, and its failure mode is named.

| control | expected | measured | failure mode if broken |
|---|---|---|---|
| **NS-1** version histogram | >1 distinct version | **2** (1.27.1, 1.27.2) | if the whole-file scan were windowed, versions past the window would vanish — the D147 failure 6 shape |
| **NS-2** stripped-binary reader | symbol reader **fails** | `named=1` of 41,528 | **fires as expected**; if it had returned a plausible count, the control would be degenerate |
| **NS-3** names-exist-in-bytes check | nonzero | `github.com/bishopfox` **10,266** | proves `named=1` is a **mapping** failure, not an absence |
| **NS-4** `CMP RAX,0` invariance | small constant across binaries | **4 / 4 / 4 / 4** | a mis-tuned opcode match would not produce the same constant 4× |
| **NS-5** caller comparison | must DIFFER | **2 correct / 1 defective** | if all three matched, the instrument could not distinguish correct from defective — the conclusion would be about my reader, not the code |
| **NS-6** `toolchain` directive | — | **0 of 6** | **fires as an ABSENCE, used correctly**: it forbids concluding Havoc declined to pin |
| **NS-7** register control pair | must DIFFER | `D161*` **1** · `D162*` **1** (neighbour, occupied) · `D160*` **0** · `D166*` **0** · `D167*` **0** · `D169*` **0** · `D999*` **0** | a constructed-name probe that cannot fail proves nothing; the two-zero-wide negative half is what makes the pair discriminate |

**NS-7 was mislabeled in the first draft and the correction is recorded here rather than silently applied.** The first pair used `D162*` as the negative half on the assumption that the next number was free. **It is not — `D162` is another lane's live report** (*"the server half exists in no artifact, the client carries all 201 RPC stubs…"*). **A negative control that returns 1 because the number is occupied is not a control at all**; it is the cannot-fail assertion wearing a control's clothing. The pair above was re-run against the real directory and now spans **three distinct states** — occupied (`1`), unallocated (`0`), and the target under test. **The registry is read, never assumed.**

**The one that carries the most weight is NS-5.** A single defective call site proves a defect exists. **Two correct call sites on the same function prove the defect is a defect** — that the guard the author wrote is elsewhere written correctly, so the difference is positional and not a property of `ParseDemonRegisterRequest`'s contract.

---

## §9 — METHOD LIMITS

- **No execution.** No binary was run. No build was performed. `go` is not on PATH.
- **No network.** No live C2.
- **No REA `open_binary`.** One shared active provider target across lanes; untouched.
- **Ghidra 12.1.4 headless, positional via `.bat`, never `-readOnly`.**
- **The byte-level scanners depend on no symbol table** — deliberately, because §3.3 shows the symbol reader fails on one of the four binaries.
- **The instruction-level result in D147 remains as delivered** and is **not** re-measured here.
- **`guard dominates` is established structurally by reading block containment**, not by the adjacency scan. §3.7 states that limit explicitly.

---

**End of D161.**
