# D133 — Covenant .NET Library Graph, Detection-Fingerprint Discriminators, and the Grinch Non-Presence Finding

**Report ID:** D133
**Allocation note (TOCTOU — see §0.1a):** drafted and announced as `D132`. At write time `D132` was
taken by `havoc-deep`'s `D132_havoc_agent_library_graph_…` (45,661 B, 23:08:10). It landed as
`D133`. Internal ID corrected to match the filename.
**Claim method:** bare-number registry, control pair both directions (§0.1)
**Subject:** `RE_Library\01_SOURCE_c2\covenant\Covenant\` — 979 files / 243 dirs (source-only lane)
**Round:** R27 capstone leg — Covenant deep surface + .NET library graph
**No execution · no network · no live C2 · no `open_binary`.** All findings from static source and byte-level PE inspection.

---

## §0 — Rule 33 header, allocation, and the toolchain constraint

### §0.1 Allocation: `D133`

### §0.1a THE COLLISION, AND WHY THE BRIEF'S CONTROL COULD NOT CATCH IT

I claimed `D132` after a registry check that independently reproduced the brief's
`129/130/131 taken` statement and returned `132 = False`. **That check was correct when it ran and
wrong when I wrote.**

```
D132_havoc_agent_library_graph_dead_build_arms_dispatch_axes_and_the_fingerprint_surface.md
    45,661 B   23:08:10   <- havoc-deep, the teammate the brief named
D133_<this report>         26,797 B   23:11:35   <- mine
D134_meterpreter_…         20,286 B   23:10:14
D136_sliver_client_…       17,963 B   23:06:50
D137_android_detection_…   20,613 B   23:10:34
```

**Five reports landed within a five-minute window.** This is a **TOCTOU race**, and the brief's
prescribed control — `Test-Path` on the intended filename — **is structurally incapable of catching
it**, because a point-in-time existence assertion cannot observe a concurrent claim. `Test-Path`
returned `False` honestly, and the file was taken 3 minutes later.

**What the control DID catch, and this is the part that worked:** it caught the case where the
number was *already* taken, which is the common failure. It cannot catch the race. **For an
enumerated-scope claim under concurrent writers, the only sound assertion is a reserve-then-write
that is atomic, or a post-write re-check of the registry — which is how this was found.**

**Post-write re-check (the assertion that actually fired):**

```
Get-ChildItem DEEP -Filter 'D132*'  ->  1 file, NOT mine
Get-ChildItem DEEP -Filter 'D133*'  ->  1 file, mine, 26,797 B
```

**No report was overwritten.** `write` did not clobber `havoc-deep`'s file; it landed on the next
free number. The collision cost a re-verification, not anyone's work.

```
SCOPE:          RE_Library\01_SOURCE_c2\covenant\Covenant\  — 979 files, 243 dirs
DEFINER SCOPE:  Covenant\Covenant.csproj (24 PackageReference, netcoreapp3.1)
CONDITIONAL SCOPE: nothing in this report is conditional on the netcoreapp3.1 runtime gap —
                every library claim is a SOURCE-TEXT or PE-HEADER fact, not a runtime behaviour
COUNTED:        152 .cs · 254 .cs/.razor · 60 enum decls · 47 .dll/.exe · 24 PackageReference
                183 REST operation names · 6 fingerprint candidates · 12 string-dispatch enums
```

**Registry method:** regex `^D(\d+)[_\.]` over `DEEP\*.md`, distinct-number set.
**Control pair, both directions — this is an assertion that CAN fail:**

| Key | registry says | brief says | agree |
|---|---|---|---|
| `129` | `True` | taken | **yes** |
| `130` | `True` | taken | **yes** |
| `131` | `True` | taken | **yes** |
| `132` | **`False`** | free | **claimed** |
| `133` | `False` | free | not taken |

**Registry: 129 distinct D-numbers, max `D131`.** My instrument independently reproduces the brief's
`129/130/131 taken` statement. Had it disagreed, the claim would have been refused. `Test-Path` on
my own filename is **not** used as the assertion, because it cannot fail to be absent for a new file.

**One instrument defect caught in the control itself:** the first control-pair run used an inline
`if` inside a string concatenation. PowerShell parsed `if` as a command and threw on 5 of 5 rows —
**the file-list column never printed.** The registry booleans survived; the *check on the check* did
not. Fixed before proceeding. A control that crashes on its own control row is not a control.

### §0.2 THE TOOLCHAIN CONSTRAINT — corrected, and it is NOT a tool defect

The inherited framing said `ilspycmd` *"throws `MetadataFileNotSupportedException` on the two
non-framework Covenant assemblies."* **Measured, the situation is materially different and
better.**

**Enumeration of all 47 `.dll`/`.exe` (excl. `obj/`, `bin/`):**

| Directory | Count | Bytes |
|---|---|---|
| `Data\AssemblyReferences\net40` | 18 | 23,114,648 |
| `Data\AssemblyReferences\net35` | 18 | 20,477,936 |
| `Data\refs` | 9 | 2,079,232 |
| `Data\EmbeddedResources` | 2 | 1,923,584 |

**CLI-header test (PE optional-header data directory index 14), which is the discriminator:**

| File | machine | CLI dir RVA | verdict |
|---|---|---|---|
| `Data\EmbeddedResources\SharpSploit.Resources.powerkatz_x64.dll` | `0x8664` | **0** | **NATIVE — no CLI header** |
| `Data\EmbeddedResources\SharpSploit.Resources.powerkatz_x86.dll` | `0x014C` | **0** | **NATIVE — no CLI header** |
| `Data\refs\Confuser.Core.dll` | `0x014C` | `0x2008` size 72 | managed |
| `Data\refs\Confuser.DynCipher.dll` | `0x014C` | `0x2008` | managed |
| `Data\refs\Confuser.MSBuild.Tasks.dll` | `0x014C` | `0x2008` | managed |
| `Data\refs\Confuser.Protections.dll` | `0x014C` | `0x2008` | managed |
| `Data\refs\Confuser.Renamer.dll` | `0x014C` | `0x2008` | managed |
| `Data\refs\Confuser.Runtime.dll` | `0x014C` | `0x2008` | managed |
| `Data\refs\dnlib.dll` | `0x014C` | `0x2008` | managed |
| `Data\refs\Donut.dll` | `0x014C` | `0x2008` | managed |
| `Data\refs\PeNet.dll` | `0x014C` | `0x2008` | managed |

**THE TWO ARE THE POWERKATZ PAIR — AND THEY ARE NATIVE, NOT MANAGED.** `ilspycmd` does not fail on
them because of a toolchain limit; it fails because **they are not .NET assemblies.** The exception
string in the brief is reproduced exactly, and its own text says so: *"PE file does not contain any
managed metadata."*

**Three-way discrimination proving the instrument:**

| Input | `ilspycmd` result |
|---|---|
| `refs\Confuser.Core.dll` | **20 types listed** (`SevenZip.*`, `Confuser.Core.*`) — readable |
| `powerkatz_x64.dll` | `MetadataFileNotSupportedException: PE file does not contain any managed metadata` |
| `refs\DoesNotExist.dll` | `File '…' does not exist!` — **distinct error** |

**Three inputs, three distinct outcomes.** The tool discriminates correctly. **Fallback reader for
the native pair: PE-header and section parsing at byte level** (no decompiler required, `open_binary`
not used). **Fallback for managed types: `ilspycmd` on the 9 `refs\` assemblies, plus the 152 `.cs`
source files — which are ground truth, stronger than any decompilation.**

**The brief's own law, honoured:** *a blocked tool must not become a blocked finding.* **Here the
"blocked tool" was never blocked; the target was out of its domain.** Stated so the capstone does
not carry a phantom toolchain limitation.

**And the material scoping fact:** there is **no Covenant-authored managed binary in this tree** at
all (no `Covenant.dll`, no `bin/`, no `obj/`) — consistent with D101. **The entire library graph
below is therefore derived from source text and the 24 `PackageReference` entries**, which is the
correct and only available instrument.

---

## §1 — THE COVENANT .NET LIBRARY GRAPH (load-bearing only)

**Rule applied:** a library with no reachable caller is **not** a mechanism and is **excluded from
the graph** — reported instead as a dead dependency (§1.3).

**Denominator: 254 `.cs`/`.razor` source files.**

### §1.1 The live graph — each entry is what it is, its mechanism, and its load-bearing caller

| Library | Ver | Mechanism it provides | Load-bearing caller (`file:line`) | hits |
|---|---|---|---|---|
| **Newtonsoft.Json** | 12.0.3 | JSON (de)serialization — **the wire format for grunt messages and the entire object model** | `Grunt.cs`, `GruntTasking.cs`, `SerializedGruntTask` models; 83 files | **117** |
| **Microsoft.CodeAnalysis.CSharp** (Roslyn) | 3.5.0 | **Compiles C# source to IL in-process** — the core implant-generation mechanism | `Compiler.cs:176` `CSharpSyntaxTree.ParseText`; `CompileCSharpCore` | 23 |
| **Microsoft.Rest.ClientRuntime** | 2.3.21 | Auto-generated **REST/Swagger client** runtime | `CovenantAPI.cs`, `ICovenantAPI.cs`, `CovenantAPIService.cs` | 17 |
| **Microsoft.AspNetCore.Mvc** | 3.1.3 | REST API controllers + attribute routing | 22 `*ApiController.cs` files | 25 |
| **Microsoft.AspNetCore.SignalR** (Client) | 3.1.3 | **WebSocket hub — operator↔server realtime channel** | `CovenantHubService.cs:36` `.WithUrl("…/covenantHub")` | 10 |
| **Microsoft.AspNetCore.Identity.EntityFrameworkCore** | 3.1.3 | user/role store | `CovenantUserApiController.cs`, `CovenantUser.cs` | 26 |
| **Microsoft.AspNetCore.Authentication.JwtBearer** | 3.1.3 | JWT bearer auth on every API call | `Startup.cs` auth registration | 31 |
| **Microsoft.EntityFrameworkCore** | 3.1.4 | SQLite ORM — data model persistence | `CovenantContext.cs` | 11 |
| **Microsoft.EntityFrameworkCore.Sqlite** | 3.1.4 | SQLite provider | **`CovenantContext.cs:59` `.UseSqlite("Data Source=" + Common.CovenantDatabaseFile)`** | 1 |
| **Microsoft.EntityFrameworkCore.InMemory** | 3.1.4 | in-memory provider (transient listener DB) | **`HttpListener.cs:287` `.UseInMemoryDatabase("HttpListenerDatabase")`** | 1 |
| **YamlDotNet** | 8.1.1 | YAML deserialize — task/profile/template definitions | `DbInitializer.cs:404`, `GruntTask.FromSerializedGruntTask` | 7 |
| **NLog.Web.AspNetCore** | 4.9.2 | structured logging | `Startup.cs`, `Program.cs` | 14 |
| **System.IdentityModel.Tokens.Jwt** | 6.5.0 | JWT token construction/validation | `CovenantUserApiController.cs:108` `Login` | 8 |
| **BlazorInputFile** | 0.1.0-preview | file-upload component for task assignment | **`GruntTaskAssignForm.razor:43` `<InputFile @ref="InputFile" OnChange="OnUpload" />`** | 5 |
| **SignalR.Protocols.NewtonsoftJson** | 3.1.3 | hub protocol binding | **`Startup.cs:138` `.AddNewtonsoftJsonProtocol(options => …)`** | 1 |
| **Mvc.NewtonsoftJson** | 3.1.3 | MVC JSON options | **`Startup.cs:142` `services.AddMvc().AddNewtonsoftJson(options => …)`** | 2 |
| **System.Security.Principal.Windows** | 4.7.0 | **Windows identity / impersonation — privilege context for SMB and HTTP listeners** | **`Covenant.cs:251-253`** `WindowsIdentity.GetCurrent()` → `WindowsPrincipal` → `IsInRole("Administrators")`; `GruntBridge.cs:82`, `GruntHTTP.cs:88` `WindowsImpersonationContext` | **23** |
| **Swashbuckle.AspNetCore.\*** | 5.3.3 | OpenAPI/Swagger doc generation | `Startup.cs` | 1 |
| **McMaster.Extensions.CommandLineUtils** | 3.0.0 | CLI argument parsing | `Covenant.cs` | 1 |
| **Microsoft.AspNetCore.Components(.Web)** | 3.1.3 | Blazor component model — the entire operator UI | `_Imports.razor:2`, 40+ `.razor` files | 44 |

### §1.2 The load-bearing core, ranked

**Four libraries are architecturally load-bearing:**
1. **Roslyn** — without it there is no implant; `Compiler.cs` turns C# into the stager bytes.
2. **Newtonsoft.Json** — the wire format, the profile format, and the object model.
3. **EntityFrameworkCore (+Sqlite/InMemory)** — every model is a table.
4. **SignalR** — the operator's realtime channel, and the strongest unique fingerprint (§2.1).

### §1.3 THE DEAD DEPENDENCY — one artifact survived three probes

`Covenant.csproj:49` declares:
```xml
<PackageReference Include="Microsoft.DotNet.PlatformAbstractions" Version="3.1.4" />
```

**Three independent API-surface probes across 254 source files, all zero:**

| Probe | hits |
|---|---|
| token `PlatformAbstractions` | 0 |
| type `RuntimeEnvironment` | 0 |
| type `ApplicationEnvironment` | 0 |

**It is genuinely dead.** Note the near-trap: `Covenant.cs:249` uses `RuntimeInformation.IsOSPlatform(
OSPlatform.Windows)`, but **`RuntimeInformation` comes from `System.Runtime.InteropServices` in the
BCL, not from this package** — so the one plausible caller is not one. **A dead dependency is a
supply-chain surface with zero function**, and the objective's *"no dumb ones"* excludes it from the
graph. That exclusion is the finding.

---

## §2 — DETECTION FINGERPRINTS: UNIQUE vs SHARED, WITH A FALSE-POSITIVE BASELINE

**Baseline method:** each candidate string searched case-sensitively across **all six target trees**
in `01_SOURCE_c2` (covenant, havoc, metasploit, mythic, pupy, sliver), source-like extensions only,
files < 2 MB. **A candidate present in another target is a weak signal and is labelled so.**

### §2.1 The discriminator table

| Candidate | cov | hav | met | myt | pup | sli | Verdict |
|---|---|---|---|---|---|---|---|
| **`covenantHub`** | **7** | 0 | 0 | 0 | 0 | 0 | **STRONG — unique** |
| **`CovenantPort`** | **10** | 0 | 0 | 0 | 0 | 0 | **STRONG — unique** |
| **`SharpSploit`** | **339** | 0 | 0 | 0 | 0 | 0 | **STRONG — unique** |
| **`gruntStager`** / `GruntStager` | **31** | 0 | 0 | 0 | 0 | 0 | **STRONG — unique** |
| **`ConfuserEx`** | **3** | 0 | 0 | 0 | 0 | 0 | **STRONG — unique** |
| **`GruntHTTP`** | 2 | 0 | 0 | 0 | 0 | 0 | strong but low-volume |
| `Grunt` | 2820 | 0 | **4** | 0 | 0 | **1** | **MEDIUM — not unique** |
| `Elite` | 7 | 9 | **23** | 1 | 12 | **214** | **WEAK — reject** |
| `EmbeddedResource` | 447 | 0 | 1 | 0 | 0 | **14** | **WEAK — reject** |

### §2.2 `covenantHub` — the single strongest discriminator, and why

`CovenantHubService.cs:36`:
```csharp
.WithUrl("https://localhost:" + configuration["CovenantPort"] + "/covenantHub", options =>
```

**`/covenantHub` is a hardcoded URI path segment** — a literal string in the compiled assembly,
surviving any optimization, and **present in zero of the other five targets.** It is also on the
wire in every SignalR connection from the operator client, making it **network-observable, not just
file-observable.** The companion `CovenantPort` config key is likewise literal and unique.

### §2.3 THE FALSE-POSITIVE BASELINE, stated per fingerprint

| Fingerprint | What legitimate software also matches it |
|---|---|
| `/covenantHub` | Measured 0 across the other five C2 targets. **Residual risk: any unrelated application that happens to name a hub "covenant".** Low but non-zero — the token is an English word + `Hub`. Mitigate by requiring the **full path with `https://localhost:` prefix and SignalR `negotiate` verb**. |
| `CovenantPort` | A config key string. **Legitimate match: any operator's own infrastructure naming a variable `CovenantPort`** — including a detection engineer's honeypot. Low risk; high specificity. |
| `SharpSploit` (339) | **This is the highest-risk one despite being unique in-corpus.** `SharpSploit` is a **public, well-known .NET post-exploitation library** distributed on GitHub. **Any attacker using SharpSploit independently of Covenant matches this.** It fingerprints the *capability*, not the *framework*. **Recommendation: do NOT use SharpSploit alone; pair with `gruntStager`.** |
| `gruntStager` (31) | Generic word "grunt" is used across tooling (`Grunt` is a JS build tool; `grunt` appears in MITRE ATT&CK as "Grunt"). **`gruntStager` as a compound is unique in-corpus**, but a file named `GruntStager.exe` is Covenant's own output convention. Moderate. |
| `ConfuserEx` (3) | **ConfuserEx is a widely-used public obfuscator.** Presence indicates obfuscation, **not Covenant.** Rejected as a Covenant fingerprint on that basis alone. |
| `Grunt` (2820, but met=4, sli=1) | **Rejected as insufficiently unique** — it appears in Metasploit and Sliver sources. |
| `Elite` (sli=214) | **REJECTED — a generic English word.** Included here specifically as the negative control: it demonstrated that my table can distinguish a real discriminator from vocabulary. |

### §2.4 The transport / framing surface

**GUID formatting — a measured discriminator:**
- `ToString("D")` — **46 occurrences**
- `ToString("N")` — **0 occurrences**

**Covenant emits the 36-character hyphenated GUID form on the wire, never the 32-character compact
form.** A detector keying on command IDs or grunt identity can use this: **8-4-4-4-12 hyphenation
present ⇒ consistent with Covenant's serializer; compact 32-char ⇒ not this path.**

**Default URIs (all `file:line`):**
- `CovenantAPIService.cs:29` — `new Uri("https://localhost:" + configuration["CovenantPort"])`
- `CovenantHubService.cs:36` — `"https://localhost:" + configuration["CovenantPort"] + "/covenantHub"`
- `Covenant.cs:107` — `string CovenantUri = CovenantBindUrl == "0.0.0.0" ? "https://127.0.0.1:" + CovenantPort : "https://" + CovenantEndpoint;`
- `CovenantService.cs:3963` / `:4001` — `listener.CovenantUrl = "https://localhost:" + _configuration["CovenantPort"]`
- `CovenantAPI.cs:283` — `BaseUri = new System.Uri("http://localhost")`

**`Stage`/`Stage0` handoff:** `"Stage0"` **42** occurrences, `"Stage1"` **38**, `"Stager"` **207**.
The `GruntStatus` enum carries `Uninitialized, Stage0, Stage1, Stage2, Active, Lost, Exited,
Disconnected, Hidden` — **the stage progression is an observable lifecycle**, and its member names
are string literals (§3).

**Template boundary:** `REPLACE_` — **137 occurrences.** This is the stager text-substitution
namespace (`{{REPLACE_VALIDATE_CERT}}`, `{{REPLACE_USE_CERT_PINNING}}` measured in D121). **The
`{{REPLACE_…}}` token shape is itself a fingerprint** and is Covenant-specific.

---

## §3 — THE COMPILER-CHECKED vs UNCHECKED DISPATCH QUESTION, APPLIED TO C#

**Answer: BOTH. Covenant uses enum-typed dispatch AND string-keyed dispatch, often for the same
enum — and the string side is the detection surface.**

### §3.1 Compiler-checked (enum-typed) dispatch — safe

```
GruntTaskingType.cs:52-70   case GruntTaskingType.Assembly:  … SetDelay, SetJitter,
                            SetConnectAttempts, SetKillDate, Exit, Connect, Disconnect,
                            Tasks, TaskKill          (all 10 members, exhaustive)
CovenantService.cs:1584     switch (profile.Type)
CovenantService.cs:3179     switch (cred.Type)
CovenantService.cs:3456     switch (indicator.Type)
LauncherForm.razor:298      switch (this.Launcher.Type)
CreateCredential.razor:21   switch (credential.Type)
CreateIndicator.razor:21    switch (indicator.Type)
```

**These are compiler-checked: an unhandled member produces a warning or a fall-through, and the
member names do NOT need to exist as strings.**

### §3.2 String-keyed dispatch — NOT compiler-checked, and therefore detection-usable

**Every enum type in the model layer ALSO carries a `switch` on its own member-name STRING
LITERALS.** Measured, 12+ enums:

```
CommunicationType.cs:52-56   case "HTTP": … case "SMB": … case "Bridge":
CredentialType.cs:52-56      case "Password": … "Hash": … "Ticket":
DotNetVersion.cs:52-56       case "Net35": … "Net40": … "NetCore31":
DownloadProgress.cs:48-50    case "Portion": … "Complete":
EventLevel.cs:60-68          case "Silent": … "Info": … "Warning": … "Highlight": … "Error":
EventType.cs:52-56           case "Normal": … "Download": … "Screenshot":
GruntStatus.cs:76-82         case "Uninitialized": … "Stage0": … "Stage1": … "Stage2": …
CodeMirrorTheme.cs:48-50     case "default": … "night":
```

**This is the string-keyed dispatch the brief asked for, and it is a strong detection surface:**
these literals are **`ldstr` operands in the IL**, they survive compilation, they cannot be
optimized away, and they appear as a **dense, non-English, non-coincidental cluster** —
`"Uninitialized"`, `"Stage0"`, `"Stage1"`, `"Stage2"`, `"Highlight"` in one assembly is a
behavioural signature, not vocabulary.

**Direct consequence for the fingerprint DB:** a YARA-style rule keyed on the *set*
`{"Stage0","Stage1","Stage2","Uninitialized","Disconnected","Highlight"}` is far stronger than any
single token, because the **co-occurrence** is what is unique.

### §3.3 The half-typed half-stringed hazard

**`GruntTaskingForm.razor:112`** (measured D121):
```csharp
await IJSRuntime.InvokeAsync<string>("InitializeSelectPicker", "#Type.selectpicker",
    ((int)Enum.Parse(typeof(GruntTaskingType), this.GruntTasking.Type.ToString())).ToString());
```
An **`Enum.Parse` on a string round-trip with no guard** — the enum-typed model is serialized to a
string and parsed back. **This is the exact seam where the compiler-checked and string-keyed worlds
meet**, and it is unguarded. Same shape as the D121 convergence family.

---

## §4 — THE GRINCH / GRAPHQL FINDING: THE PREMISE IS NOT SUPPORTED

**The brief states: *"Covenant's client is a GraphQL client. Endpoint shape, query names, operation
types — enumerate them."*

**Measured across the whole `covenant` subtree (979 files), seven patterns:**

| Pattern | hits |
|---|---|
| `graphql` (case-insens) | **0** |
| `GraphQL` | **0** |
| `Grinch` | **0** |
| `grinch` | **0** |
| `gql` | **0** |
| `.gql` | **0** |
| `mutation` | **0** |
| `Apollo` | **0** |

**And `Grinch` does not exist anywhere in the repository.** No `grinch` directory under
`01_SOURCE_c2` (which contains exactly: `covenant, havoc, metasploit, mythic, pupy, sliver`). A
repository-wide filename search returns **12 `graphql` matches, ALL in other targets** — Metasploit
scanners (2), Mythic's Hasura metadata (3), Sliver's bundled Monaco editor language files (2), and
supporting assets. **Zero in Covenant.**

**I applied the brief's own law before filing this:** a flat zero across seven patterns is a
distribution returning one verdict for 100% of input, so I suspected my classifier. **I re-probed a
wider namespace surface, checked the directory tree, and searched by filename repository-wide. The
zero is real — the subject genuinely lacks the feature.**

**What Covenant ACTUALLY has is a REST/Swagger client, not GraphQL:**

```
Microsoft.Rest.ClientRuntime 2.3.21   →  CovenantAPI.cs, ICovenantAPI.cs,
                                          CovenantAPIService.cs, CovenantAPIExtensions.cs
L283  BaseUri = new System.Uri("http://localhost");
L29   new Uri("https://localhost:" + configuration["CovenantPort"])
```

**So the detection surface is REST, and it is enumerable. 183 operation names follow.**

### §4.1 The REST operation-name census — string constants, detection-usable

`[Http*(Name = "…")]` attributes across the API controllers. **183 total: 87 `[HttpGet]`, 45
`[HttpPost]`, 33 `[HttpPut]`, 18 `[HttpDelete]`.** These `Name` values are **string literals compiled
into the assembly's attribute metadata and cannot be optimized away.** Representative (from the full
enumeration):

```
GetCommandOutputs · GetCommandOutput · CreateCommandOutput · EditCommandOutput
AppendCommandOutput · DeleteCommandOutput
GetUsers · GetUser · GetCurrentUser · Login · CreateUser · EditUserPassword · EditUser
DeleteUser · GetUsersRoles · GetUserRoles · GetUserRole · CreateUserRole · DeleteUserRole
GetRoles · GetRole
GetCredentials · GetPasswordCredentials · GetHashCredentials · GetTicketCredentials
GetCredential · CreatePasswordCredential · CreateHashCredential · CreateTicketCredential
EditPasswordCredential · EditHashCredential · EditTicketCredential · DeleteCredential
GetEmbeddedResources · CreateEmbeddedResource · EditEmbeddedResource · DeleteEmbeddedResource
GetGruntTasks · … · GetThemes · CreateTheme · EditTheme · DeleteTheme
GetReferenceSourceLibraries · CreateReferenceSourceLibrary · …
```

**Route templates are also literals:** `users/{id}`, `users/login`, `users/logon`,
`users/{id}/roles/{rid}`, `passwords`, `hashes`, `tickets`, `append/{id}`.

**`GetGruntByOriginalServerGUID` / `GetGruntByGUID`** (`CovenantAPIExtensions.cs:1443,1454,1467`)
are notable: they expose **GUID and *original server* GUID** as first-class API parameters.

### §4.2 Consequence for the capstone

**The premise needs correcting at the capstone level, not just here.** A threat model or fingerprint
DB built expecting a Covenant GraphQL client would look for query documents, persisted-query hashes,
and `POST /graphql` — **none of which Covenant emits.** The real surface is a **Swagger-generated
REST client with 183 named operations and a `covenantHub` SignalR channel.** Getting this wrong
produces a detector that never fires.

---

## §5 — Self-verification and instrument-artifact log

### §5.1 Instrument artifacts caught this round (all before publication)

| # | Artifact | How caught | Resolution |
|---|---|---|---|
| 1 | Control-pair inline `if` parsed as command, threw 5/5 | stderr on run | hoisted; file column now prints |
| 2 | 3 "absences" (`BlazorInputFile`, `Principal.Windows`, `PlatformAbstractions`) | 0-hits distribution triggered suspicion | **globbed `*.cs` only — `.razor` excluded.** Re-probed with `.razor`: 2 of 3 were live |
| 3 | 6 of 7 "DEAD" dependency verdicts | 7-of-21 zero rate triggered suspicion | my token test was a **`using`-directive detector**; DI extension methods (`AddNewtonsoftJson`, `UseSqlite`, `UseInMemoryDatabase`) never appear in a `using`. Re-probed by API surface: **6 of 7 were LIVE** |
| 4 | `ReferencedAssemblies` → 0 hits | implausible for a core concept | **misspelled. Real token is `ReferenceAssemblies` (152 hits).** One letter. Case-insensitivity does not rescue a token that does not exist |
| 5 | `Elite` looked like a fingerprint | cross-target table | **sli=214. Rejected as a generic English word.** Kept in the report as the negative control |

**Artifacts #2 and #3 are the brief's catalogued class — a classifier returning one verdict for a
large fraction of input.** Both were caught by applying the stated law, not by luck.

### §5.2 What is NOT claimed

- **No probe printed a verdict off a null operand.** No operand-acquisition check was needed because
  **no probe in this report reads a byte array by index**; the only byte-level work is PE-header
  field reads at fixed offsets from a validated MZ/PE signature (§0.2), each of which printed its
  offset, its raw value, and its interpretation.
- **No `[absence]` is filed without a positive control.** The seven-pattern GraphQL zero was
  re-probed three ways (§4) before filing.
- **`netcoreapp3.1` was not targeted and was not needed** — every claim is source-text or
  PE-header, so **no verdict here is CONDITIONAL on the runtime gap.**

### §5.3 This report's own metrics

| Property | Value |
|---|---|
| Bytes | **30,134** (measured before this line; stale by this line's length — see below) |
| LF | **499** (same caveat) |
| CR | **0** |
| CRLF | **0** |
| BOM | **none** |
| U+FFFD | **0** |
| NUL / TAB | **0 / 0** |
| Headings (`^#{1,6}\s`) | **26** — H1 count **1** |
| Heading regex basis | **`#{1,6}`**; separately asserted: exactly **one** line matches `^#\s`. A `#{2,}` counter would report 25 |
| Duplicate whole-line headings (excl. table separators) | **0** |
| Codepoint probe over bracketed tokens | **0** |

**These metrics were forecast wrong in the draft and then measured.** The draft said
`23,594 / 452`; a first measurement said `28,805 / 479`; **this note itself changed the size**, and
the final measured values at the last write are `29,470 B / 487 LF`. Four successive values for one
table is not carelessness — it is the loop D119 §8.4 named, recurring:

> **A report's own byte count is not a property of its content. It is a property of its content
> plus the sentence that reports it.** The loop terminates only when the reporting sentence's length
> is independent of the number it reports — which is achievable by **fixed-width padding**, and is
> NOT achieved here.
>
> **Honest statement of what this table is:** the value in it is correct **as of the write that
> produced it**, and the act of writing the corrected value invalidates it again. Any reader needing
> a guaranteed-correct number must **measure the file themselves.** That is the only sound
> disposition, and it is stated rather than hidden.

**Recorded rather than quietly fixed, because this is the third round in which the same ordering
error has occurred.** The generalisable rule: *a self-measuring report must use fixed-width
numeric fields, or must decline to state its own byte count.* D121 and D133 both state it and both
carry the defect.

---

## §6 — Headline findings for the capstone

1. **The toolchain "constraint" is not one.** `ilspycmd` reads the 9 managed `refs\` assemblies
   fine. **The two that throw are the SharpSploit powerkatz pair, and they are NATIVE — `CLI data
   dir RVA=0`.** The tool is not broken; the target is out of its domain. Fallback: PE-header
   parsing (native) + `ilspycmd` (managed) + source (ground truth).
2. **`/covenantHub` is the strongest Covenant fingerprint** — hardcoded URI path, literal in the
   binary, network-observable, **0 hits in all five other targets.**
3. **Six unique discriminators measured**, and **three candidates rejected with reasons** —
   `Elite` (generic English word, sli=214), `EmbeddedResource`, and **`SharpSploit`** (unique
   in-corpus but a **public library**, so it fingerprints capability, not framework).
4. **Both dispatch styles coexist.** Every model enum carries a parallel `switch` on its own member
   name **string literals** — `"Stage0"`, `"Stage1"`, `"Uninitialized"`, `"Highlight"` — which are
   `ldstr` operands that survive compilation. **The co-occurrence set, not any single token, is the
   signature.**
5. **THE GRAPHQL PREMISE IS FALSE FOR THIS CORPUS.** Covenant has zero GraphQL and no Grinch;
   the client is **REST/Swagger with 183 named operations.** A detector built for GraphQL would
   never fire.
6. **One genuinely dead dependency:** `Microsoft.DotNet.PlatformAbstractions 3.1.4` at
   `Covenant.csproj:49`, triple-probed to zero. Excluded from the graph as a non-mechanism.
7. **GUID wire format is the 36-char hyphenated form** — `ToString("D")` 46, `ToString("N")` **0**.
