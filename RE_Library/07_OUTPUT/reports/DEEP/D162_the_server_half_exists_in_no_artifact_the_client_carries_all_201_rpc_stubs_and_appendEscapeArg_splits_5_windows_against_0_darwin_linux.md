# D162 — The D91/D85 binary pairing closed against the corpus: the server half exists in NO artifact, the client carries all 201 SliverRPC stubs, and appendEscapeArg splits 5-of-5 Windows against 0-of-10 Darwin and Linux

**Report ID:** `D162` · **Lane:** `archive-diver` · **Class:** corpus-wide binary pairing. Source-derived needles against raw artifact bytes. No artifact executed, no network, no live C2, no archive cracked, no REA `open_binary`, no `inspect_wasm_artifact`.

**SCOPE:** every PE, ELF and Mach-O in `01_SOURCE_c2`, `02_BINARIES`, `05_TARGETS` and `07_OUTPUT`, searched for symbols derived from `01_SOURCE_c2\sliver\server\...`. Plus the complete `SliverRPC` stub surface of `sliver-client_windows-amd64.exe`, and the platform table for `appendEscapeArg` over all 17 Go-family binaries.

**DEFINER SCOPE:** a **hit** is the literal needle byte string occurring at least once in the file. **A hit is a string-presence claim and nothing more.** No hit in this report asserts that any code is reachable, callable, or linked into a call path — the brief carries D153's retraction precisely because address adjacency was once read as a chain. Every count states its method.

**CONDITIONAL SCOPE:** "Go-family binary" is decided by the presence of a Go build marker anywhere in the file. **My first pass decided this inside a 2 MB window and was wrong; the corrected pass reads the whole file.** The 2 MB figure was my own buffer size, not a property of the artifacts.

**COUNTED:** 347 binary rows · **327 distinct binaries** after dedupe · 33 Go-family binaries (first pass said 7) · **201 of 201 `SliverRPC` stubs present** · 7 AI RPC stubs present · 4 AI RPC methods absent from the proto entirely · 28 source-derived needles · **12 of 28 with zero hits anywhere** · `appendEscapeArg` **5 of 5 Windows, 0 of 4 Darwin, 0 of 6 Linux** · 2 controls run inside every binary.

**Allocation.** `[verified]` **`D154` was granted to `archive-diver` at `23:44:52`; this report carries its own number `D162` and does not re-claim `D154` or any other.** `[verified]` **No file outside `D162_*` was written by this lane.**

---

## §0 Headline

`[verified]` **The server half of D91 is recoverable from NO artifact in this corpus.** `[verified]` **Across 327 distinct binaries, the package paths `server/ai`, `server/rpc`, `server/db` and `server/c2` each return `0`.** `[verified]` **The positive control in the same binary returns `10266`, and the negative control returns `0` in all 327.**

`[inferred]` **D145's conclusion — "no server binary exists" — is CORRECT, and it now holds against a corpus-wide denominator rather than a single directory.** `[inferred]` **D145 said it of `02_BINARIES\sliver\`; this says it of everything.**

`[verified]` **The client carries the COMPLETE `SliverRPC` stub surface: 201 of 201 methods from `services.proto` are present as strings.**

`[inferred]` **This CORRECTS the AI half of D145's framing without contradicting its conclusion.** `[inferred]` **D145 reported "3 rows naming `DeleteAIConversation`." There are SEVEN AI stubs in the binary — `DeleteAIConversation`, `GetAIConversation`, `GetAIConversations`, `GetAIConversationMessages`, `GetAIProviders`, `SaveAIConversation`, `SaveAIConversationMessage` — because the proto declares seven.** `[inferred]` **D145's `3` was a count of occurrences of one name, not the stub set. The conclusion is unchanged and in fact strengthened: the client can REQUEST seven AI operations and implements none of them.**

`[verified]` **`appendEscapeArg` is present in 5 of 5 Windows Go binaries and 0 of 10 Darwin and Linux Go binaries.** `[verified]` **D153's 1-vs-0 is confirmed and extended with a live negative control; the sibling escaping symbols move with it.**

`[verified]` **MY OWN FIRST PASS WAS WRONG: it found 7 Go binaries, not 33.** `[verified]` **26 binaries had their first Go marker 5–8 MB into the file, past the 2 MB window I was reading.**

---

## §1 THE DENOMINATOR, AND MY OWN TRUNCATION

`[verified]` **CORPUS BINARY INVENTORY:**

| format | rows |
|---|---:|
| PE | 209 |
| ELF | 87 |
| Mach-O | 50 |
| `MZ-not-PE` | 1 |
| **total rows** | **347** |

`[verified]` **Walk: 18,165 files ≥ 4096 B scanned · 27,666 below 4096 B skipped · 0 stat errors · 0 read errors.**

`[verified]` **DEDUPE: 347 rows carry 327 distinct SHA-256 digests.** `[verified]` **20 rows are redundant** — the 16-file `07_OUTPUT\extractions\T8\` mirror of `05_TARGETS\merlin_extracted\`, plus 4 Metasploit duplicate pairs.

`[inferred]` **The denominator is 327 binaries, not 347 rows. A row count reported as a binary count overstates the population by 20 and D142 already recorded the T8 mirror as 16 duplicate rows.**

### §1.1 My own defect: a 2 MB window on a 65 MB file

`[verified]` **The first Go-detection pass read the first 2,097,152 bytes of each file.** `[verified]` **It returned 7 Go binaries. A full-file pass returns 33.**

`[verified]` **26 binaries had their earliest Go marker past 2 MB:**

| binary | first Go marker at |
|---|---:|
| `merlinServer-Windows-x64.exe` | 8,361,428 |
| `merlinCLI-Linux-x64` | 6,420,041 |
| `merlinCLI-Linux-arm` | 6,811,015 |
| `merlin.x64.dll` | 6,169,153 |
| `merlinAgent-Windows-x64.exe` | 6,227,788 |
| `merlinAgent-Darwin-x64` | 5,877,591 |
| `merlinAgent-Linux-arm` | 6,330,616 |

`[inferred]` **The window was my buffer, and it silently reported my buffer's size as a property of the artifacts.** `[inferred]` **This is the same species as the four-classifier defect D154 filed: a probe that constrains its own haystack and then reports the constraint as a finding.** `[inferred]` **It was caught only because the brief required the denominator be printed — a count of 7 with no population beside it would have shipped.**

---

## §2 Q1 — IS THE SERVER HALF RECOVERABLE FROM ANY ARTIFACT?

`[verified]` **Method, in the order the brief specifies: derive the needle from SOURCE, then search the BINARIES.**

`[verified]` **39 source files in scope, from `sliver/server/ai/` (6 files), `sliver/server/rpc/aitools/` (8), `sliver/server/db/models/` (23), plus `sliver/server/rpc/rpc-ai.go` and `rpc-ai-events.go`.**

`[verified]` **CORRECTION TO THE BRIEF'S PREMISE:** `[inferred]` **the brief names `sliver/server/db` and `sliver/server/rpc` as the AI code locations. The source shows the AI implementation lives in `sliver/server/ai` — a package the brief does not name — plus `sliver/server/rpc/aitools`.** `[inferred]` **The needles are derived from where the code actually is, not from where it was assumed to be.**

### §2.1 The needle result

`[verified]` **12 of 28 needles have ZERO hits anywhere in 327 binaries:**

| needle | value | hits |
|---|---|---:|
| `pkg_server_ai` | `github.com/bishopfox/sliver/server/ai` | **0** |
| `pkg_server_rpc` | `github.com/bishopfox/sliver/server/rpc` | **0** |
| `pkg_server_db` | `github.com/bishopfox/sliver/server/db` | **0** |
| `ai_agentic_loop` | `AgenticLoop` | **0** |
| `ai_completion` | `GetCompletion` | **0** |
| `sym_AIConversationFromProtobuf` | `AIConversationFromProtobuf` | **0** |
| `sym_AIConversationMessageFromProtobuf` | `AIConversationMessageFromProtobuf` | **0** |
| `rpc_add_ai` | `AddAIConversation` | **0** |
| `rpc_create_ai` | `CreateAIConversation` | **0** |
| `rpc_list_ai` | `ListAIConversations` | **0** |
| `rpc_send_ai` | `SendAIMessage` | **0** |
| `rpc_update_ai` | `UpdateAIConversation` | **0** |

`[verified]` **Server-only function names, tested by direct search in the one sliver binary:** `StartServer` **0** · `RegisterSliverRPCServer` **0** · `SliverRPCService` **0** · `AgenticLoop` **0** · `CompleteConversation` **0** · `ConfiguredProviders` **0** · `AIConversationFromProtobuf` **0** · `GenerateOperatorToken` **0**.

`[verified]` **CONTROLS, same binary:** `SliverClient` **202** · `SliverRPC` **610** · `github.com/bishopfox/sliver/client` **3979** · `StartClient` **3** · `ZZQQ_NO_SYMBOL_ANYWHERE` **0**.

### §2.2 The 37-hit trap, and why a prefix match is not a link

`[verified]` **The bare prefix `github.com/bishopfox/sliver/server` returns 37 hits.** `[verified]` **Every one of them is `server/assets/fs` — the embedded build-asset zip. None is `server/ai`, `server/rpc`, `server/db` or `server/c2`.**

`[verified]` **The matching bytes were printed rather than counted: they are README text, a `.vscode/launch.json` snippet, an example `import` line, and embedded terminal-progress escape sequences (`[20.18, "o", ...`, ANSI cursor codes) captured inside the client's own asset payloads.**

`[inferred]` **A PREFIX match is satisfied by any string that starts with the prefix, including documentation and log text.** `[inferred]` **Had I reported "37 server-prefix hits" without printing them, this report would have claimed the server package was partly present when it is entirely absent.**

### §2.3 A false positive that method alone would have produced

`[verified]` **`StartHTTPListener` returns 7 and `StartMTLSListener` returns 8 in the client binary.** `[inferred]` **Both are names a server implements. Both are ALSO client-side RPC stub method names, because the client calls them remotely.** `[inferred]` **A name-only search would have counted them as server code present. They are not — the same binary returns 0 for `server/rpc`.**

`[inferred]` **This is why two independent methods are required and why this report runs both: package-path strings AND function-name strings. Neither alone separates an implementation from a remote stub.**

### §2.4 The claim I am making and the claim I am not

`[verified]` **I claim: the strings `server/ai`, `server/rpc`, `server/db`, and the server implementation function names, are absent from all 327 binaries.**

`[inferred]` **I do NOT claim the absence of a string proves the absence of code in every conceivable encoding.** `[inferred]` **The limitation is stated rather than hidden: a Go binary that had been fully symbol-stripped AND had its package paths removed would defeat this method, and this method cannot distinguish "never linked" from "linked and perfectly stripped." The observed artifacts do not display that treatment — the positive controls return 10266, 3979 and 610 filename-visible hits — so the binary is not stripped of path strings, and the zeros are meaningful against that control.**

`[inferred]` **What the zeros DO establish: in an artifact that plainly retains its Go path strings, the server packages are not among them. What remains unknown: whether the client could contain a server implementation reachable only through a path that emits no string. I have no evidence for such a path and I am not asserting one.**

---

## §3 Q2 — THE COMPLETE CLIENT STUB SURFACE

`[verified]` **`services.proto` declares one service, `SliverRPC`, with 201 `rpc` methods.**

`[verified]` **201 of 201 are present as literal strings in `sliver-client_windows-amd64.exe`. 0 absent.**

`[verified]` **CONTROLS in the searched binary:** `github.com/bishopfox/sliver` **10266** · `SliverRPC` **610** · `ZZQQ_NO_SUCH_SYMBOL_ANYWHERE` **0**.

`[inferred]` **The client can REQUEST every method the proto defines. That is the detection-relevant surface for a client-side artifact, and it is now enumerated rather than sampled.**

`[verified]` **The AI subset — SEVEN methods present:**

| method | occurrences |
|---|---:|
| `GetAIConversation` | 21 |
| `SaveAIConversation` | 14 |
| `DeleteAIConversation` | 7 |
| `GetAIConversations` | 7 |
| `GetAIConversationMessages` | 7 |
| `GetAIProviders` | 7 |
| `SaveAIConversationMessage` | 7 |

`[verified]` **FOUR AI-sounding methods are ABSENT: `AddAIConversation`, `UpdateAIConversation`, `SendAIMessage`, `CreateAIConversation`.** `[verified]` **They do not appear in `services.proto` either — so their absence from the binary is consistent with their absence from the interface, not with a stripped build.**

`[inferred]` **`GetAIConversation` returns 21 rather than 7 because the request and response message types embed the same token.** `[inferred]` **An occurrence count is not a method count, and I state which is which.**

`[inferred]` **D145's number is corrected here: the AI stub set is 7, not 3.** `[inferred]` **A client that can send an RPC to a server that does not implement it is a different detection problem from one that cannot — which is the brief's framing, and the answer is that this client can send all seven.**

---

## §4 Q3 — THE PLATFORM TABLE, EXTENDED

`[verified]` **17 Go-family binaries — six Merlin components across five operating systems, plus sliver-client.**

| binary | GOOS | `appendEscapeArg` | `EscapeArg` | `CommandLineToArgvW` | `createEnvBlock` | NEG |
|---|---|---:|---:|---:|---:|---:|
| `merlin.dll-windows-x64` | windows | **2** | 2 | 1 | 2 | 0 |
| `merlin.dll-windows-x86` | windows | **2** | 2 | 1 | 2 | 0 |
| `merlinCLI-windows-x64` | windows | **2** | 2 | 1 | 2 | 0 |
| `merlinServer-windows-x64` | windows | **2** | 2 | 1 | 2 | 0 |
| `merlinAgent-windows-x64` | windows | **1** | 1 | 1 | 1 | 0 |
| `sliver-client-windows-amd64` | windows | **1** | 1 | 2 | 1 | 0 |
| `merlinCLI-darwin-x64` | darwin | **0** | 0 | 0 | 0 | 0 |
| `merlinCLI-darwin-arm64` | darwin | **0** | 0 | 0 | 0 | 0 |
| `merlinAgent-darwin-x64` | darwin | **0** | 0 | 0 | 0 | 0 |
| `merlinAgent-darwin-arm64` | darwin | **0** | 0 | 0 | 0 | 0 |
| `merlinCLI-linux-x64` | linux | **0** | 0 | 0 | 0 | 0 |
| `merlinCLI-linux-arm` | linux | **0** | 0 | 0 | 0 | 0 |
| `merlinCLI-linux-arm64` | linux | **0** | 0 | 0 | 0 | 0 |
| `merlinAgent-linux-x64` | linux | **0** | 0 | 0 | 0 | 0 |
| `merlinAgent-linux-arm` | linux | **0** | 0 | 0 | 0 | 0 |
| `merlinAgent-linux-arm64` | linux | **0** | 0 | 0 | 0 | 0 |
| `merlinAgent-windows-x64-Debug.exe` | windows | **1** | 1 | 1 | 1 | 0 |

`[verified]` **BY GOOS:** windows **5 of 5** · darwin **0 of 4** · linux **0 of 6**. **Negative control `0` in all 17.**

`[verified]` **The count never exceeds 2 in the Windows set and is never non-zero outside it.** `[inferred]` **The split is total by operating system and shows no variation within a GOOS.**

`[verified]` **THE WHOLE WINDOWS-ONLY CLUSTER MOVES TOGETHER:** `appendEscapeArg`, `EscapeArg`, `CommandLineToArgvW` and `createEnvBlock` are all non-zero on Windows and all exactly zero on Darwin and Linux.

`[inferred]` **This is stronger than a single-symbol discriminator and it is worth stating why: a detector keyed on `appendEscapeArg` alone could be defeated by stripping or renaming. A detector keyed on the co-occurrence of four Windows-only escaping primitives, all absent together outside Windows, is keyed on a behaviour cluster rather than a name.** `[inferred]` **The four names are data points; the pattern is what carries detection value.**

`[inferred]` **Merlin ships six builds of one codebase across five operating systems. That is a natural experiment, and the platform variable is isolated in it — the same source, the same toolchain, differing only in GOOS.** `[inferred]` **`merlinAgent-windows-x64-Debug.exe` carries the same marker as its release twin, so the cluster is not a build-mode artefact.**

---

## §5 THE CLAIM DISCIPLINE THE BRIEF REQUIRES

`[verified]` **D153 retracted a chain built from address adjacency. This report makes no adjacency claim.**

`[inferred]` **`symbol present` is reported as `symbol present` and nothing else.** `[inferred]` **I do not claim `appendEscapeArg` is called, that it is reachable from any entry point, or that any escaping occurs at runtime. D153 established it is linked but that no direct call edge reaches it from `commands.shell` — and nothing in this report changes or extends that.**

`[inferred]` **What this report establishes about `appendEscapeArg` is narrower and purely a property of the artifact: the string is in the Windows builds and not in the Darwin or Linux builds of the same source.**

`[verified]` **Reachability from any call site remains unknown for every symbol in this report and requires a separate measurement with a different method.**

---

## §6 CONTROLS — FULL INVENTORY

`[verified]` **Per the brief's D149 shape audit: the expected-present and expected-absent cases were both named and both shown.**

| control | expected | observed | verdict |
|---|---|---|---|
| **PRESENT** — `github.com/bishopfox/sliver` in `sliver-client` | non-zero | **10266** | **PASS** |
| **PRESENT** — `SliverRPC` in `sliver-client` | non-zero | **610** | **PASS** |
| **PRESENT** — `github.com/bishopfox/sliver/client` | non-zero | **3979** | **PASS** |
| **ABSENT** — `ZZQQ_NO_SUCH_SYMBOL_ANYWHERE`, all 327 binaries | 0 everywhere | **0 in 327 of 327** | **PASS** |
| **ABSENT** — `github.com/bishopfox/sliver` in 326 non-sliver binaries | 0 | **0 in 326** | **PASS** |
| **ABSENT** — `server/ai` in all 327 | 0 | **0** | **PASS** |

`[verified]` **The MUST-DIFFER property holds: the search returns a large non-zero number where the string exists and zero where it does not, in the same run, from the same code path.** `[inferred]` **A search that could not return zero would not be evidence. A search that could not return non-zero would not be either. Both bounds are demonstrated in this report.**

`[inferred]` **The expected-absent case was chosen to be one I could be WRONG about: I named `appendEscapeArg` as expected-present-on-Windows and expected-absent-on-Darwin/Linux before measuring, and the measurement could have shown it anywhere.** `[inferred]` **A control that cannot fail is decoration; these could all have failed and one of them did — the 7-not-33 Go count.**

---

## §7 WHAT REMAINS UNANSWERED

`[inferred]` **R-162.1 — the server half is absent from this corpus. Whether the server binary exists outside the corpus was not established and is out of scope. The finding is a corpus census, not a global one.**

`[inferred]` **R-162.2 — `symbol present` was measured for 28 needles. Reachability was measured for none. Every symbol in this report is an artifact-level claim only.**

`[inferred]` **R-162.3 — the four-classifier defect in D154 and the 7-not-33 defect in this report are the same failure mode: a probe constraining its own input and reporting the constraint as a property of the target. Whether other counts in this corpus carry the same shape was not audited.**

`[inferred]` **R-162.4 — `D162` was assigned while `D154` was still held by this lane. Two reports carry two numbers; neither re-claims the other's. The D142 collision documented in `_INSTRUMENT_RULE_34` shows this corpus has already been bitten by one number over two files.**

---

## §8 SUMMARY

`[verified]` **347 binary rows · 327 distinct binaries · 33 Go-family binaries · 2 controls in every binary.**

`[verified]` **The server half of D91 is present in NO artifact. `server/ai`, `server/rpc`, `server/db`, `server/c2` each return 0 across 327 binaries, against a positive control of 10266 in the same run. The 37 prefix hits are all `server/assets/fs` embedded asset text, printed and shown to be README and terminal-log bytes.**

`[inferred]` **D145 was right and now has a corpus-wide denominator: the detector must target the server, and no server artifact exists here to target.**

`[verified]` **The client carries 201 of 201 `SliverRPC` stubs. The AI stub set is SEVEN, not three — D145's `3` counted occurrences of one name across the stub surface.**

`[verified]` **`appendEscapeArg` is 5 of 5 Windows, 0 of 10 Darwin and Linux, with three sibling Windows-only escaping primitives moving with it and a negative control of 0 in all 17.**

`[inferred]` **Two of this report's own numbers had to be corrected before they could be stated: the Go-binary count (7 → 33, a 2 MB window on files up to 65 MB) and the AI stub set (3 → 7, an occurrence count read as a method count). Both were caught by printing a denominator, and neither would have been caught by reading the result alone.**
