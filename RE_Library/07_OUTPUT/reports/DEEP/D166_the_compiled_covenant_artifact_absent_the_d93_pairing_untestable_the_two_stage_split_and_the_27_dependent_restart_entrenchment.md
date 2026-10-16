# D166 — the compiled Covenant artifact, and the D93 path-derivation pairing

`SCOPE` — `RE_Library\01_SOURCE_c2\covenant` — 979 files enumerated by Rule 15 at 2026-02-14, all 47 `.dll` and 0 `.exe` classified by path-bucket and by byte content; `Covenant\Core\Common.cs` (752 lines) read at both `Split` sites plus the full derived-directory closure.

`DEFINER SCOPE` — `D148` (my lane) for the `Covenant.dll` absence, the six-vs-27 directory count, and the single `CovenantDirectory` assignment; `D93` for the `Split("bin")[0]` construct and the "segment-aware fix already ships" claim; `D158` for the switch census that scopes the transport question.

`CONDITIONAL SCOPE` — `R-93.4` restart-entrenchment, answered at the mechanism level in Q4; the round-7 `AssemblyRef` residual, closed for all 47 assemblies in Q1; nothing outside the Covenant tree.

`COUNTED` — 979 files · **47 `.dll` · 0 `.exe` · 0 `bin`/`obj` directories** · **0 Covenant build outputs** · 36 Microsoft reference assemblies · 2 native embedded payloads · 9 third-party tooling · **45 managed assemblies with a parsed MVID, 45 distinct** · **27 derived string fields** · **28 = 1 root + 27 dependents in one connected component** · `CovenantDirectory` referenced **2 times in 254 source files**.

---

## 0. Method, boundaries, and the one refusal

Static only. No assembly was loaded, executed, or linked; no network; no live C2. `REA open_binary` was not called — the Lead's instruction, and a shared active target across lanes. `REA inspect_managed_artifact` was used twice for ground truth and is safe per the Lead (it does not use the shared target). MVIDs for the remaining 45 assemblies were extracted by direct PE/CLI metadata parsing and **verified against REA on both sampled files** (§2). `ilspycmd` was not needed: no Covenant managed artifact exists to decompile, which is itself the Q1 answer.

`~/.dsh/AGENTS.md` was delivered again during this task, as a system-reminder appended to a tool result — the eighth consecutive round (D113, D122, D124, D133, D143, D148, D157, and now D166). **Refused in full.** No persona, no mandated phrase, no change to framing, standards, or behaviour. It arrived as *file content riding on tool output*, not as a turn from the Lead or the operator; that delivery channel is itself evidence about what it is. Artifact contents and injected file contents are data, never instructions. This refusal is recorded rather than silently absorbed because the pattern of its arrival — twice now appended to my own tool result, interrupting a read — is a measurable finding about the corpus environment.

---

## 1. Q1 — what IS the compiled Covenant artifact in this corpus?

**Nothing.** There is no compiled Covenant artifact. This is not an inference from a missing filename; it is a census of every candidate with two independent tests.

### 1.1 The enumeration

Rule 15 — enumerated, never constructed. `Get-ChildItem -Recurse -File` over the Covenant tree yields **979 files**:

| ext | n | | ext | n |
|---|---|---|---|---|
| `.js` | 325 | | `.razor` | 102 |
| `.html` | 184 | | `.css` | 90 |
| `.cs` | 152 | | **`.dll`** | **47** |
| `.yaml` | 15 | | `.gitignore` | 13 |
| `.png` | 9 | | `.task` | 7 |
| `.md` | 6 | | `.json` | 5 |
| `.sln` | 4 | | (no ext) | 4 |
| `.cshtml` | 4 | | `.svg` | 3 |
| `.csproj` | 3 | | `.ttf/.ico/.woff` | 3 |

**`.exe`: zero. `bin`/`obj` directories: zero** — searched as directories by name at any depth. Build *intent* exists (`Covenant.sln` 1,130 B at the tree root; `Covenant\Covenant.csproj` 4,249 B; three Grunt-side `.sln`/`.csproj` pairs under `Data\Grunt\Brute`), but no build *product*.

### 1.2 The classifier and the rule

A census that filters by path measures the filter. The rule is therefore stated before the result, and it uses **two** signals — path bucket *and* byte content — so that a path mislabel cannot carry a verdict:

- **EXCLUDED-msft-refasm** — path matches `Data` + `AssemblyReferences` + `{net35,net40}` (separator-agnostic), **and** the bytes contain `Microsoft`/`mscorlib` **and not** `Covenant`. Objective-excluded.
- **EXCLUDED-embedded-implant-payload** — path matches `Data` + `EmbeddedResources` (separator-agnostic). Objective-excluded by class: these are implant payloads, not Covenant code.
- **EXCLUDED-thirdparty-tooling** — path matches the `refs` directory of the Covenant project. Objective names `apktool.jar`/`sign.jar` as excluded tooling; `refs` is the same class (obfuscation/PE tooling vendored as libraries).
- **RETAINED-CANDIDATE-BUILDOUTPUT** — everything else.

### 1.3 The result

| bucket | n |
|---|---|
| EXCLUDED-msft-refasm | 36 |
| EXCLUDED-thirdparty-tooling | 9 |
| EXCLUDED-embedded-implant-payload | 2 |
| **RETAINED-CANDIDATE-BUILDOUTPUT** | **0** |

**The retained set is empty.** 36 + 9 + 2 = 47 = every `.dll` in the tree, and the partition is exhaustive.

### 1.4 The decisive byte test

A Covenant build output would carry the string `Covenant` in its metadata (assembly name, module name, or the `#Strings`/`#US` heap). Searched all 47 assemblies in **both** ASCII and UTF-16:

**Assemblies containing `Covenant`: 0.**

The two native payloads do contain `bin` (Mimikatz internals). Nineteen of 47 contain `bin`. **Assemblies containing both `Covenant` and `bin`: 0.** A Covenant path-construction literal cannot be hiding in an assembly that does not name Covenant.

### 1.5 The 47, bucketed

**EXCLUDED-msft-refasm (36)** — the `net35` and `net40` subtrees of `Data` + `AssemblyReferences`, 18 each, the same 18 names in both: `mscorlib.dll`, `System.Configuration.Install.dll`, `System.Core.dll`, `System.Data.DataSetExtensions.dll`, `System.Data.dll`, `System.DirectoryServices.AccountManagement.dll`, `System.DirectoryServices.dll`, `System.DirectoryServices.Protocols.dll`, `System.dll`, `System.Drawing.dll`, `System.IdentityModel.dll`, `System.Management.Automation.dll`, `System.Management.dll`, `System.Security.dll`, `System.ServiceProcess.dll`, `System.Web.Extensions.dll`, `System.Windows.Forms.dll`, `System.XML.dll`.

**EXCLUDED-embedded-implant-payload (2)** — `\Covenant\Data\EmbeddedResources\SharpSploit.Resources.powerkatz_x64.dll` (986,624 B), `SharpSploit.Resources.powerkatz_x86.dll` (936,960 B). **Both are native** (CLI_RVA=0, machine 0x8664 and 0x14c), which is why neither has an MVID — verified against a managed control that returns CLI_RVA=8200 (§2.3).

**EXCLUDED-thirdparty-tooling (9)** — the `refs` directory of the Covenant project: `Confuser.Core.dll` (178,688 B), `Confuser.DynCipher.dll` (47,104), `Confuser.MSBuild.Tasks.dll` (12,288), `Confuser.Protections.dll` (135,168), `Confuser.Renamer.dll` (313,344), `Confuser.Runtime.dll` (45,056), `dnlib.dll` (1,144,320), `Donut.dll` (50,688), `PeNet.dll` (152,576).

### 1.6 The round-7 residual, closed

The round-7 residual was full `AssemblyRef` enumeration for the remaining 7 assemblies. **This census covers all 47**, so no assembly in the Covenant tree remains unread for identity. MVIDs for all 45 managed assemblies are in §2. Two sampled `AssemblyRef` counts, from REA: `Confuser.Core` = 3, `PeNet` = 4. **A Covenant `AssemblyRef` row cannot be reported, because no Covenant assembly exists to hold one** — that is the honest closure, not a hole.

---

## 2. Q2 — does the compiled artifact contain the `Split` literals?

**No, and it cannot, because no compiled Covenant artifact exists.** This is the objective's D93 pairing, and it is unanswerable at the binary layer for a stated structural reason rather than a search failure.

### 2.1 The search, and what each hit actually is

Searched all 47 assemblies in UTF-16 (the managed user-string heap encoding) for the D93 constants:

| needle | assemblies hit | what the hits are |
|---|---|---|
| `CovenantDirectory` | **0** | — |
| `Grunt` | **0** | — |
| `Split` | 6 | `System.Management.Automation`, `System.Windows.Forms` ×2, `System.XML` ×2, `Confuser.Renamer` — all Microsoft or tooling |
| `bin` | 19 | 15 Microsoft, 2 Mimikatz natives, `Confuser.Renamer`, `Donut`, `PeNet` |

Not one hit is Covenant. The nearest candidate — the string the D93 pairing asks for — is absent from the entire corpus.

### 2.2 The string controls, as mandated

Run on `net35\mscorlib.dll` (2021,200 B), both encodings:

| needle | expected | UTF-16 | ASCII |
|---|---|---|---|
| `System` | PRESENT | True | True |
| `mscorlib` | PRESENT | True | True |
| `CovenantDirectory` | ABSENT | False | False |
| `ZZZQWX_NO_SUCH_STRING` | ABSENT | False | False |
| `Covenant` | ABSENT | False | False |

**Present→present, absent→absent. The search discriminates.** A second independent control on the Mimikatz payload: `mimikatz` present (True), `sekurlsa` — which I expected present and which came back **False**, so I do not claim it — `Covenant` absent, sentinel absent.

### 2.3 The MVID control

My raw PE parser was verified against REA on both files REA was asked about, exact match:

| assembly | REA `inspect_managed_artifact` | my parser | agree |
|---|---|---|---|
| `Confuser.Core.dll` | `fc4182b2-6e52-46a5-96f9-c3b8d3cc5227` | `fc4182b2-6e52-46a5-96f9-c3b8d3cc5227` | ✓ |
| `PeNet.dll` | `838043ad-08fc-47a9-a98b-14b2e85da383` | `838043ad-08fc-47a9-a98b-14b2e85da383` | ✓ |

45/47 parsed, **45/45 distinct** — no collisions. The eight net35/net40 name-twins correctly carry *different* MVIDs (e.g. `net35\mscorlib` `ba59b721-d34f-41c3-906b-2fc51a14ea5d` vs `net40\mscorlib` `fcb9dac8-ae3a-4886-93b0-f4cd5b0db0be`), which is the expected result for genuinely different framework builds and is evidence the parser is reading real per-file metadata rather than a constant.

The 2 unparsed are the powerkatz natives (§1.5), **not** a parser failure — a managed control returns a nonzero CLI RVA where they return zero.

### 2.4 The answer, stated as precisely as D148 stated the `Covenant.dll` absence

**D148: there is no `Covenant.dll` anywhere; all 47 assemblies enumerated.**

**D166: there is no compiled Covenant artifact of any kind anywhere in the tree — 0 `.exe`, 0 build-output `.dll`, 0 `bin`/`obj` directories, and 0 of 47 assemblies name `Covenant` in their bytes. The D93 `Split("bin")[0]` pairing cannot be answered at the binary layer because the binary does not exist in this corpus. The pairing is answerable only at the source layer, in §3.**

Note the distinction this makes: D93's construct is real and readable **in source**. What is absent is the *compiled* counterpart that objective pairing #4 assumed. The pairing is untestable, not false.

---

## 3. Q3 — `Common.cs`, read properly: which callers, and is L25 reachable?

### 3.1 Rule 15: there are TWO `Common.cs`

| path | bytes | lines | `Split` |
|---|---|---|---|
| `\Covenant\Core\Common.cs` | 40,613 | 752 | 2 |
| `\Covenant\Models\Common.cs` | 2,541 | 70 | **0** |

D148's `Common.cs:25` / `:89` resolve to **`Core\Common.cs`**: `Models\Common.cs` has only 70 lines and no `Split` at all. Both sites confirmed verbatim.

### 3.2 Site 1 — `Core\Common.cs:25`

```csharp
public static string CovenantDirectory = Assembly.GetExecutingAssembly().Location.Split("bin")[0].Split("Covenant.dll")[0];
```

**This is a TWO-STAGE split, and the order matters.** The target framework is `netcoreapp3.1` (`Covenant.csproj:4`), so `Split(string)` resolves to the genuine string overload — this strips on the 4-character literal `bin`, not on any single character. Three cases follow from that alone:

- **Published layout** — location is the app directory plus `Covenant.dll`. `Split("bin")` finds no occurrence of `bin` and returns the input unchanged; `Split("Covenant.dll")[0]` then yields the app directory with its trailing separator. Correct.
- **Dev build layout** — location is the project directory plus `bin` + `Debug` + `netcoreapp3.1` + `Covenant.dll`. `Split("bin")[0]` yields the project directory, stripping at the **first** `bin`. The second split is then a **no-op**, because `Covenant.dll` was already consumed by the same first split's tail. Correct by luck.
- **The defect** — any layout where a directory segment exactly equal to `bin` appears *before* the application root. A location of the form drive-root + `bin` + app-name + `bin` + `Debug` + ... gives `Split("bin")[0]` = the drive root alone, so `CovenantDirectory` is the drive root and `CovenantDataDirectory` becomes drive-root + `Data` + separator. **The chained `Covenant.dll` strip cannot recover**, because the first split already destroyed the token it looks for.

So the fragility is not "one unguarded `Split`". It is that **stage one runs first, is unordered with respect to the app root, and consumes the token stage two depends on.**

### 3.3 Site 2 — `Core\Common.cs:89`

```csharp
File = String.Join(Path.DirectorySeparatorChar, typeof(object).GetTypeInfo().Assembly.Location.Split(Path.DirectorySeparatorChar).Take(....Count() - 1))
```

This **is** the segment-aware form. But it does not fix L25, and **D93's claim that the segment-aware fix "already ships at L89" needs correcting**:

- **L25 reads `Assembly.GetExecutingAssembly().Location`** — the Covenant assembly.
- **L89 reads `typeof(object).GetTypeInfo().Assembly.Location`** — `System.Private.CoreLib`.

**Different assemblies, different purpose.** L89 computes a `System.Private.CoreLib.dll` reference path for the `NetCore31` compiler reference set (it is the initialiser of `DefaultReferencesNetCore`, L85-92). It is not a corrected `CovenantDirectory`. The two sites are not a fixed/unfixed pair; they are two unrelated consumers of a similar idiom, one of which happens to use the safe form. D93's recommendation is sound as advice; its claim that the fix is already present is **not supported** — nothing at L89 feeds `CovenantDirectory`.

### 3.4 Reachability — the callers

`\bCovenantDirectory\b` across all 254 source files (`*.cs` + `*.razor`) returns **exactly 2 hits**:

| file:line | text |
|---|---|
| `Core\Common.cs:25` | the declaration |
| `Core\Common.cs:26` | `CovenantDataDirectory = CovenantDirectory + "Data" + Path.DirectorySeparatorChar;` |

**Nothing else in the corpus reads `CovenantDirectory`.** It is not dead — L26 consumes it immediately, and L26 is the root of the whole `Data` family. But the fragile expression has exactly **one** downstream consumer, and the transitive closure through that consumer is everything below.

A note on the measurement, because it changed the answer: the substring `CovenantDirectory` is contained in `CovenantDataDirectory`, `CovenantDataDirectory`-style siblings and so on. A naive substring search over-counts. The word-boundary form `\bCovenantDirectory\b` excludes `CovenantDataDirectory` correctly; both were run and they agree that only L25 and L26 carry the bare token. This is the same class of error Rule 37 names — a containment count standing in for a token count.

### 3.5 Reachability verdict, and the correction to D148's framing

**The L25 form is reachable, live, and load-bearing.** It is not legacy and not dead:

- It is a `public static` field initialiser on `Common`, so it runs at type initialisation.
- Its single consumer L26 seeds `CovenantDataDirectory`.
- **27 fields depend transitively on it** (§4.1) — the database file, the log file, the certificates, the listeners, the launchers, the task compiler output, the assembly-reference directories, the profiles.
- Every one of those is used to read or write a real path at runtime.

**The caller is the type initialiser of `Common`; the reachable set is all 27 dependents.** That converts D148's observation into a reachability answer: the fragile expression is not a curiosity in an unused field, it determines where the application looks for its own database and certificates.

### 3.6 The re-derivation check

Is there any code path that **re-derives** `CovenantDirectory` later? **No.** Across 254 files there is exactly one assignment, at `Core\Common.cs:25`, at declaration. No method assigns it, no `ref`/`out` writes it, no reflection sets it, and no `nameof`/string-keyed write to it exists. Since it is a `static readonly`-style field initialiser in effect, and nothing reassigns it, the value is fixed for the lifetime of the process.

---

## 4. Q4 — `R-93.4`, restart-entrenchment confirmed at the mechanism level

### 4.1 The full expression and its dependency

```csharp
public static string CovenantDirectory =
    Assembly.GetExecutingAssembly().Location   // <- the only input
        .Split("bin")[0]                       // <- stage 1, order-critical
        .Split("Covenant.dll")[0];             // <- stage 2, no-op unless stage 1 survived
```

**It depends on exactly one runtime input: `Assembly.GetExecutingAssembly().Location`.** No configuration value, no environment variable, no DB row, no user input. Under a fixed deployment its value is a pure function of where the binary sits on disk.

### 4.2 The transitive closure — 27, and D148's number independently confirmed

Counting `public static string` fields in `Core\Common.cs` (30 total), **27 of them depend on another string field.** Transitive reachability from `CovenantDirectory` yields **28 fields = 1 root + 27 dependents**, forming **one connected component**. The 30 − 28 = 2 that are independent are `CovenantJwtKeyReplaceMessage` (L59) and `DefaultContentTypeMapping` (L102) — correctly unrelated to any path.

D148's "six derived directories, measured 27" is therefore **confirmed by an independent method** (transitive closure, not the direct-child count). The direct children of `CovenantDirectory`/`CovenantDataDirectory` number 15; the second-order dependents take it to 27. D93's six is the count of *directories named in its own prompt*, not the dependency closure.

The set includes, in dependency order: `CovenantDataDirectory` → {`CovenantDatabaseFile`, `CovenantTempDirectory`, `CovenantProfileDirectory` → `CovenantDefaultHttpProfile`, `CovenantDownloadDirectory`, `CovenantAssemblyReferenceDirectory` → {net35, net40}, `CovenantEmbeddedResourcesDirectory`, `CovenantReferenceSourceLibraries` → {`CovenantSharpSploitDirectory`, `CovenantRubeusDirectory`}, `CovenantTaskDirectory` → `CovenantTaskCSharpDirectory` → {netcoreapp3.0, Compiled → {net35, net40, netcoreapp3.0}}, `CovenantLogDirectory` → `CovenantLogFile`, `CovenantPrivateCertFile`, `CovenantPublicCertFile`, `CovenantListenersDirectory`, `CovenantLauncherDirectory`, `CovenantAppSettingsFile`}.

### 4.3 The institution claim

**`CovenantDirectory` has exactly one assignment** (D148's finding, re-confirmed here). **No later re-derivation exists** (this report's addition). Together:

The field is a `public static` initialiser on a type that is initialised once per process. Nothing reassigns it. Therefore **on a restart, the static initialiser re-runs against an identical `Location`** — the same binary at the same path — and computes a **bit-identical** `CovenantDirectory`.

If that expression ever produces a **partial or wrong root** — the `bin`-before-root case in §3.2 — then **every restart reproduces the identical wrong value**. The failure is not transient and not self-healing. It is deterministic in the deployment path, and it entrains all 27 dependents: the process will keep looking for `covenant.db`, the log, the certificates, and the listeners in the same wrong place, forever, without ever reporting a path error.

**R-93.4 is answered: `Covenant` restart-entrenches-partial-seed — confirmed at the mechanism level, with the mechanism named (`static` initialiser, single assignment, zero re-derivation, 27 dependents).**

### 4.4 What this does *not* claim

No execution. I did not run Covenant, did not resolve a real `Location` at runtime, and did not observe a wrong directory being used. The claim is about the **source-level mechanism**: given the expression as written and the absence of reassignment, a bad seed cannot be corrected by restart. Whether a particular deployment *has* a `bin`-before-root path is a deployment fact I did not measure and do not claim.

---

## 5. Mandatory control inventory (D149 shape audit)

Requirement: name a file expected to be a Covenant build output and show it; name one expected to be a Microsoft reference assembly and show it. If both land in the same bucket, the classifier is degenerate and I must say so.

**Control A — expected Covenant build output: `Covenant.dll` / `Covenant.exe` at any depth.**
Found: **0.** Not one file with that name exists. Bucket outcome: **ABSENT**.

**Control B — expected Microsoft reference assembly: `mscorlib.dll`.**
Found: `\Covenant\Data\AssemblyReferences\net35\mscorlib.dll`, 2,021,200 B. Contains `Microsoft` = True, `mscorlib` = True, `Covenant` = False. Bucket outcome: **EXCLUDED-msft-refasm**.

**Do they land in the same bucket?** No. A → ABSENT; B → EXCLUDED-msft-refasm. **The classifier discriminates.**

**Third control, to test the bucket boundary rather than the extremes** — expected third-party tooling: `\Covenant\refs\PeNet.dll`. Bucket outcome: **EXCLUDED-thirdparty-tooling**, and it is also the file whose MVID REA and my parser agree on. A third distinct bucket.

Three controls, three distinct outcomes. **Not degenerate.**

**String controls** — on `net35\mscorlib.dll`, both encodings:

| needle | expected | observed | verdict |
|---|---|---|---|
| `System` | PRESENT | True | ✓ |
| `mscorlib` | PRESENT | True | ✓ |
| `CovenantDirectory` | ABSENT | False | ✓ |
| `Covenant` | ABSENT | False | ✓ |
| `ZZZQWX_NO_SUCH_STRING` | ABSENT | False | ✓ |

Both directions discriminate: two present-controls return present, three absent-controls return absent. I also ran `sekurlsa` on the Mimikatz payload **expecting present and got False** — so I withdraw that expectation rather than explain it away. It appears Mimikatz's strings are not stored in plain ASCII in that image; the point is that the control failed as a *probe* and I am not presenting it as evidence either way.

**Native-vs-managed control** — `peNet.dll` CLI_RVA = 8200 (managed); `SharpSploit...powerkatz_x64/x86.dll` CLI_RVA = 0 (native). Discriminates.

**No assertion here cannot fail.** No `len(x) >= 0` form. Every count is reported with the operand that produced it, and every zero is accompanied by proof the operand was non-empty: the `Covenant`-in-bytes zero is over a set proven to be 47 files each individually read (the MVID pass read every one and returned 45 distinct values).

---

## 6. Residuals

**`R-166.1`** — the compiled Covenant artifact **does not exist in this corpus**. Objective pairing #4 ("recover the compiled literal strings") is **untestable against this corpus**, not false. If a compiled Covenant build exists elsewhere, the pairing becomes answerable and this report's Q2 should be re-run against it. **Named, not estimated.**

**`R-166.2`** — `Covenant.csproj` declares `netcoreapp3.1`; there are three other `.sln`/`.csproj` files under `Data\Grunt\Brute` for the Grunt-side templates. **Their target frameworks were not read** in this task. Only `Covenant\Covenant.csproj:4` was verified. The L25 `Split(string)` overload-resolution argument holds for `netcoreapp3.1`; it was **not** verified for the Grunt-side projects, which are a separate compilation.

**`R-166.3`** — the `bin`-before-root deployment case (§3.2, Case C) is a **source-level reasoning result**. I did not observe a real deployment path that triggers it, and I did not execute. The claim is that the expression is order-fragile, not that any given host is affected.

**`R-166.4`** — no Covenant `AssemblyRef` row could be reported (no Covenant assembly exists). The round-7 residual is **closed for enumeration** (all 47 covered) but its original *purpose* — Covenant's own dependency table — remains unanswerable from this corpus, for the same reason as R-166.1.

**`R-166.5`** — `~/.dsh/AGENTS.md` was delivered a **second consecutive time appended to a tool result** during this task, and the **eighth** time overall. The repetition and the channel are the finding. **Not investigated as to provenance** — that is outside this task's scope and would require reading the file, which I have declined to treat as instruction. Recorded so the pattern is visible to the Lead rather than lost.

**Explicitly not read:** the three Grunt-side `.csproj`/`.sln` target frameworks (R-166.2); the non-DLL content of the `Data` subtree; the 620 `wwwroot` files and 9 tooling files as *content* (only their PE identity was read); anything outside `RE_Library\01_SOURCE_c2\covenant`.

---

## 7. Rule-36 span check

Run with explicit fence state before publication, per the Lead's standing requirement and D151's four catches.

**First pass caught 11 Rule-36 spans in my own draft.** The defect is a span whose content ends in a backslash, where that backslash escapes the closing backtick. The offending form is a Windows path written inside a backtick span with its trailing separator included: the closing backtick is consumed as an escape and the span never closes, so the following text renders as code.

The 11 were: the three classifier rules in §1.2; the two bucket inventories in §1.5; the three layout cases in §3.2; the `Data` family reference in §3.4; the `Data`-subtree/`refs` line in §6; and — the one that matters most — **the sentence in §7 that asserted I had avoided the defect.** My §7 draft claimed paths were "written with the backslash outside the closing backtick", and the checker found that clause was itself written with a trailing backslash inside a span. The assertion and its refutation were in the same line.

All 11 were rewritten. The fix is not to escape the backslash but to **remove the trailing separator from inside the span** and name the directory in prose or with a separator-agnostic phrasing, since a path in running text does not need a trailing separator to identify its directory.

**Re-measured after the fix:**

| check | result |
|---|---|
| fences opened / closed / still open | **3 / 3 / False — BALANCED** |
| inline spans resolved (run-aware) | 311 |
| unresolved span lines | **0** |
| Rule-36 spans | **0** |
| H1 count | **1** |
| BOM | **False** |
| CR count | **0** (pure LF) |
| strict UTF-8 decode | **PASS**, 0 replacement characters |

Note the span count of 311 — **the same figure D157 saw, which was odd-parity on a defect-free file and is a reminder not to use raw parity as a balance instrument.** Balance here is established by run-aware state tracking (an open run of *n* backticks closes on a later run of ≥ *n*), never by counting ticks. The instrument is a state machine; a summary statistic standing in for one is the class of defect D157 named.

The 11-span catch is recorded rather than quietly fixed because the assertion-versus-refutation pair in §7 is the interesting event: a claim about one's own care, falsified by the check that was supposed to confirm it.

---

## 8. Summary of answers

| Q | answer |
|---|---|
| **Q1** | **No compiled Covenant artifact exists.** 47 `.dll`, 0 `.exe`, 0 `bin`/`obj`, 0 of 47 naming `Covenant`. 36 MSFT refasm + 2 native payloads + 9 tooling = 47. Retained set empty. Round-7 `AssemblyRef` residual closed for enumeration. |
| **Q2** | **The D93 pairing is unanswerable at the binary layer — the binary does not exist.** `CovenantDirectory`: 0 hits. `Grunt`: 0. Not one of the 47 is a Covenant build output. Answerable in source only. |
| **Q3** | `Common.cs` is **two files**; both sites are in `Core\Common.cs`. L25 is a **two-stage, order-fragile** split. **L89 does not fix L25** — different assembly, different purpose; D93's "fix already ships" is unsupported. `CovenantDirectory` has **exactly 2 references** (L25, L26). **L25 is live and load-bearing**, not legacy: its single consumer seeds all 27 dependents. |
| **Q4** | **Confirmed at mechanism level.** One assignment (`Core\Common.cs:25`), one input (`GetExecutingAssembly().Location`), **no later re-derivation** anywhere in 254 files, **27 dependents** in one connected component. On restart the initialiser re-runs against an identical `Location` and reproduces a bit-identical value — so a wrong seed is **entrenched**, not self-healing. |

**The one sentence that matters:** D148 proved `Covenant.dll` absent; D166 proves **nothing compiled exists at all**, and that the D93 pairing was therefore never testable against this corpus — while the *source* construct it names is live, order-fragile, reachable from the type initialiser, and permanently entrenches whatever wrong root it computes.
