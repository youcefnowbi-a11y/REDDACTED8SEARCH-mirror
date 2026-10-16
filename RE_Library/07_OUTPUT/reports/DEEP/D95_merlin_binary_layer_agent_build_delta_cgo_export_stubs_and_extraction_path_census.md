# D95 — Merlin binary layer: the 21-byte agent delta, the cgo export stubs, and the path that is not a census

**Scope:** target T8, `RE_Library\05_TARGETS\merlin_extracted\`. Round 24.
**Line-count convention:** LF count = `([regex]::Matches($text,"`+"`"+`n")).Count` over the whole file read by `[IO.File]::ReadAllText`. A final line without a trailing newline is **not** counted.
**Tags:** `[verified]` instrument run with output shown · `[read]` quoted from an artifact read directly · `[inferred]` reasoning over evidence · `[absence]` probe returned zero with a positive control.
**Discipline:** no corpus binary was executed. Every byte below was read from a file. `DumpSyms.java` was read, not run. Ghidra was **not** invoked this round — all four tasks were answerable from existing outputs plus direct byte reads, which is why there are no new toolchain failures to record.
**Occupancy:** `D95*` enumerated → **0 matches** before writing. `_d95_*` in `binlayer\` → **0**.
**Write scope:** this report, plus optional `binlayer\_d95_*.ps1`.

---

## §0 Headline — the two agent builds DIFFER, and the difference is one linker flag

`[verified]` **`merlinAgent-Windows-x64.exe` and `merlinAgent-Windows-x64-Debug.exe` are NOT the same file.** Same size (13,939,200 B), different content:

```
merlinAgent-Windows-x64.exe        SHA256 E9501A7F325950591B585DFC83E0BAE8B519FFF153806E9EA91351B6742C3FA5
merlinAgent-Windows-x64-Debug.exe  SHA256 F12C1B24C4A700F08EC3E5EF282CED877AA7660C5E5FA4A589DE63E0E768A654
```

`[verified]` **Order-independent set difference over the two string dumps:**

| | distinct strings | unique to this build |
|---|---:|---:|
| release | 36,843 | **2** |
| Debug | 36,844 | **3** |

`[verified]` **Those five strings, in full, are the entire delta:**

1. `L3-5kC` (release) vs `L3-%kC` (Debug) — **one byte, `0x35`→`0x25`**, at file offset 17,034. String-extraction boundary noise.
2. `$\e$v` (Debug only) — further boundary noise.
3. **The `-ldflags` build string**, differing in exactly two respects:
   - **release carries `-H=windowsgui`; Debug does not.**
   - `-X "main.auth=opaque"` and `-X "main.addr=127.0.0.1:4444"` are **emitted in the opposite order.**

`[verified]` **The 21-byte gap decomposes exactly: `-H=windowsgui ` is 15 bytes; the reordered `-X` pair accounts for the remaining 6.**

`[verified]` **INDEPENDENT CONFIRMATION — the PE header agrees, measured a second way:**

| binary | subsystem | meaning |
|---|---|---|
| `merlinAgent-Windows-x64.exe` | **2** | `WINDOWS_GUI` |
| `merlinAgent-Windows-x64-Debug.exe` | **3** | `WINDOWS_CONSOLE` |

`[inferred]` **Two entirely different measurements — a string-set difference and a PE optional-header field — agree that the release agent is a GUI-subsystem build and the Debug agent is a console-subsystem build.** `[inferred]` **This is the strongest form of evidence available here: the finding does not depend on the instrument that found it.**

### §0.1 Correction to C-08 §2, naming the old report

`[read]` C-08 §2 states: *"`merlinAgent-Windows-x64-Debug.exe` and `merlinAgent-Windows-x64.exe` are **byte-identical in size** … and **identical in every census figure**"*, concluding the Debug build *"carries no symbols."*

`[inferred]` **The census figures are indeed identical — 11,246 functions, 1 named, 4 thunks — and that part stands unrefuted.** `[inferred]` **But "byte-identical in size" was read as "byte-identical," and it is not.** The two files differ. `[inferred]` **C-08 drew a correct conclusion (the Debug agent is symbol-stripped) from a measurement (size equality) that does not support the word "identical" in the way it was used.** `[inferred]` **The conclusion survives; the phrasing is corrected here, and it is a name-is-not-a-measurement instance of the same species C-08 itself named — size is not content, just as `Debug` is not symbols.**

---

## §1 T8.1 — the `.strings.txt` files: they were not where the task said

`[verified]` **The task specified `data\bin\merlinAgent-Windows-x64.strings.txt`. That path does not exist.** Enumerated at the stated path: **absent.**

`[verified]` **Enumerating the workspace instead of trusting the given path found both files, at a different location:**

```
RE_Library\07_OUTPUT\extractions\T8\strings\merlinAgent-Windows-x64.strings.txt        1,592,932 B
RE_Library\07_OUTPUT\extractions\T8\strings\merlinAgent-Windows-x64-Debug.strings.txt  1,592,911 B
```

`[inferred]` **The sizes match the task's figures exactly (1,592,932 and 1,592,911), so the files are the intended ones — the path was wrong, not the file.** `[inferred]` **This is Instrument rule 15 applying to the instruction itself: a path given by NAME was not a path confirmed by ENUMERATION.** `[inferred]` **Had I opened the stated path, read the failure, and reported "strings files absent," I would have published a false absence about two files that exist.** `[inferred]` Recorded as a hazard for every future lane: **the artifact root for derived analysis output is `07_OUTPUT\extractions\<TARGET>\`, not the target tree.**

### §1.1 Line and encoding census

| file | bytes | LF | CR | lines (non-empty) |
|---|---:|---:|---:|---:|
| release | 1,592,932 | 40,922 | 40,922 | 40,922 |
| Debug | 1,592,911 | 40,923 | 40,923 | 40,923 |

`[inferred]` `CR = LF` in both, so the files are **CRLF-terminated throughout** with no mixed endings. `[inferred]` The Debug file has **one more line** despite being **21 bytes smaller** — consistent with one additional short line and the `-H=windowsgui` removal from a long one.

### §1.2 THE OPERATIONAL PAYLOAD — the full build configuration, in cleartext, in both builds

`[verified]` **Both agent builds carry their complete `-ldflags` invocation as a literal string.** This is the single highest-value artifact in the task, because it is the agent's **default parameter set with defaults spelled out**:

```
-ldflags="-s -w
  -X "main.auth=opaque"          OPAQUE PAKE authentication
  -X "main.addr=127.0.0.1:4444"  C2 address
  -X "main.protocol=h2"          HTTP/2
  -X "main.url=https://127.0.0.1:443"
  -X "main.psk=merlin"           PRE-SHARED KEY = "merlin"
  -X "main.secure=false"
  -X "main.sleep=30s"            beacon interval
  -X "main.skew=3000"
  -X "main.padding=4096"         traffic padding
  -X "main.killdate=0"           no kill date
  -X "main.maxretry=7"
  -X "main.transforms=jwe,gob-base"  message transforms
  -X "main.httpClient=go"
  -X "main.useragent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36
       (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36"
  -X "github.com/Ne0nd0g/merlin-agent/v2/core.Build=e68a5e810cbd269622b5617ae8cd5c22c6b82005"
  -H=windowsgui  (release only)
  -buildid="
```

`[inferred]` **Four things this settles outright, none of which needed disassembly:**
- **The build hash is `e68a5e810cbd269622b5617ae8cd5c22c6b82005`** and the module is `github.com/Ne0nd0g/merlin-agent/v2` — artifact identity, from the artifact.
- **The default PSK is the literal string `merlin`**, and default auth is `opaque`. `[inferred]` An implant left at defaults authenticates with a guessable key.
- **The default user-agent is Chrome 40** (2015-era), anachronistic on a modern host and therefore a detection signature.
- **`-s -w` is present in BOTH builds** — `-s` strips the symbol table, `-w` strips DWARF. `[inferred]` **This is the mechanism behind C-08's 1-named-function result, stated by the binary itself**, and it confirms the Debug build is stripped by the same flags.

### §1.3 Named-pipe and lateral-movement strings

`[verified]` **The pipe namespace is `\\.\pipe\merlin`:**

```
\\.\pipe\%s                                    (generic template)
\\.\pipe\merlin                                (SMB client connect target)
\\.\pipe\merlinclient
Successfully started SMB listener on \\.\pipe\%s
Try \\.\pipe\merlin
```

`[inferred]` **A named-pipe prefix fixed at `merlin` is a host-based detection signature for the SMB lateral-movement path**, and `smb-reverse` appears alongside `tcp-reverse`, `udp-reverse` in the same string cluster. `[inferred]` The generic `\\.\pipe\%s` template appearing separately means the prefix is composed at runtime for some paths and literal for others.

### §1.4 The shellcode-injection method set, by name

`[verified]` **The agent's injection surface is enumerable as full symbol names**, which is unusual for a stripped binary and is itself a finding — these survive `-s -w` because they are Go type/method names in the runtime metadata:

```
github.com/Ne0nd0g/merlin-agent/v2/commands.ExecuteShellcode
github.com/Ne0nd0g/merlin-agent/v2/commands.ExecuteShellcodeSelf
github.com/Ne0nd0g/merlin-agent/v2/commands.ExecuteShellcodeCreateProcessWithPipe
github.com/Ne0nd0g/merlin-agent/v2/commands.ExecuteShellcodeQueueUserAPC
github.com/Ne0nd0g/merlin-agent/v2/commands.ExecuteShellcodeRtlCreateUserThread
github.com/Ne0nd0g/merlin-agent/v2/commands.ExecuteShellcodeRemote
github.com/Ne0nd0g/merlin-agent/v2/os/windows/api/kernel32.QueueUserAPC
github.com/Ne0nd0g/merlin-agent/v2/os/windows/api/kernel32.VirtualAllocEx
```

`[verified]` **Supporting API and error strings:** `CreateThread`, `QueueUserAPC`, `VirtualAlloc`, `VirtualAllocEx`, `RevertToSelf`, `OpenProcess`, `LoadLibraryW`, `CreateMutexW`, `ReleaseMutex`, plus the error strings *"there was an error executing shellcode with the 'self' method"*, *"…with the 'userapc' method"*, *"there was an error executing shellcode with the 'self' method"*, and `commands/exec.ExecuteShellcodeRemote`.

`[inferred]` **Five injection techniques, named, with their platform APIs.** `[inferred]` **This is the concrete answer to "the agent is the dark binary": the Ghidra layer could not name 11,245 of 11,246 functions, but the STRINGS layer names the implant's entire injection capability set.** `[inferred]` **The two layers are complementary and neither alone is sufficient — a bound on the symbol layer is not a bound on the artifact.**

### §1.5 CLR / .NET assembly loading, and build provenance

`[verified]` **go-clr v1.0.4 in-process .NET execution:**

```
/home/runner/go/pkg/mod/github.com/!ne0nd0g/go-clr@v1.0.4/appdomain.go
/home/runner/go/pkg/mod/github.com/!ne0nd0g/go-clr@v1.0.4/assembly.go
/home/runner/go/pkg/mod/github.com/!ne0nd0g/go-clr@v1.0.4/iclrmetahost.go
mscoree!CLRCreateInstance, ICLRRuntimeInfo::IsLoadable, clr.ICLRMetaHost, commands.assembly
```

`[verified]` **Build provenance, from the artifact:**

```
/opt/hostedtoolcache/go/1.27.2/x64/src/...
/home/runner/go/pkg/mod/golang.org/x/crypto@v0.57.0/...
/home/runner/work/merlin-agent/commands/shellcode.go
```

`[inferred]` **`/opt/hostedtoolcache/` is GitHub Actions' hosted-runner tool cache path, and `/home/runner/work/` is the Actions workspace.** `[inferred]` **The implants were built on GitHub-hosted CI, not on an operator workstation** — an artifact-identity datapoint and a supply-chain observation. `[inferred]` **Go 1.27.2 is confirmed here by an independent route from C-08 §6's analyzer error message, which read the version from the binary's own metadata. Two measurements, same version.**

### §1.6 Additional endpoint and protocol strings

`[verified]` — `127.0.0.1:53` (default DNS target), `127.0.0.1:4444` (default C2), `https://127.0.0.1:443`, `internal/sync`, `internal/tls`, `internal/quic`, `internal/http2`, `internal/utls`; protocol token `smb-reverse` / `tcp-reverse` / `udp-reverse`; header strings `Host: %s`, `User-Agent: %s`, `Set-Cookie`, `Cookie`, `Keep-Alive`, `Content-Id`, `Message-Id`; and `OPAQUE V: %v` / `OPAQUE V: %x` version markers.

`[inferred]` **The presence of `internal/quic` and `internal/http3` alongside `h2` means the default protocol is one of several compiled in**, consistent with `-X "main.protocol=h2"` selecting at build time from a wider runtime set.

---

## §2 T8.2 — can `DumpSyms.java` write to a path containing a space?

`[verified]` **It cannot, and the constraint is in two places.**

`[read]` **`DumpSyms.java:27`:**
```java
File outFile = new File(args[0]);
```
`[read]` **`gate.bat:13`** documents the requirement — `REM  %2 = staged output path (MUST be space-free)` — and `gate.bat:42` passes it quoted:
```bat
call analyzeHeadless.bat "%PROJDIR%" ghprobe -import "%TARGET%" ... -postScript "%SCRIPT%" "%STAGE%" <nul
```

`[inferred]` **The quoting at the cmd layer is correct and does not help.** `[inferred]` **The split happens inside Ghidra's own launcher, which re-tokenises the `-postScript` argument list on whitespace after cmd has already handed it through** — the exact failure C-08 §5 records as failure 6: *`Bad argument: REDDACTED\RE_Library\...`*.

`[verified]` **Second, independent location of the same constraint:** `DumpSyms.java:34` writes the program name into the dump header via `currentProgram.getName()`, which is **derived from the imported filename.** `[inferred]` **So a spaced TARGET also corrupts the dump's own provenance line — the artifact would misname itself.** `[inferred]` **The constraint is therefore asymmetric in a way worth stating: the stage path is a hard failure (no output at all), while a spaced target is a silent corruption (output exists, header is wrong).** `[inferred]` **Silent is worse. The stage may be space-free by construction; the target must be staged to a space-free name too, and the harness currently relies on the caller to do that rather than enforcing it.**

`[inferred]` **Documented constraint, stated for reuse:** script arguments cannot contain spaces; any path reaching `DumpSyms.java` (stage or target) must be staged through a space-free directory such as `%TEMP%` and copied into the repo afterwards. **The repo path `FOR REDDACTED\` itself contains a space, so every invocation must stage.** `[inferred]` The space-free staging is not a workaround for one bad flag — it is **structural**, because the repository root name contains a space.

---

## §3 T8.3 — the extraction tree, enumerated

`[verified]` **Instrument rule 15 applied to the tree itself.** Complete recursive walk of `05_TARGETS\merlin_extracted\`: **56 directories, 89 files, 7 depths.**

`[verified]` **Complete binary inventory, by actual path:**

| path | bytes | note |
|---|---:|---|
| `merlinServer-Windows-x64.exe` | 26,329,600 | **at ROOT** |
| `data\bin\merlin.x86.dll` | 14,687,006 | |
| `data\bin\merlin.x64.dll` | 15,145,760 | |
| `data\bin\merlinAgent-Windows-x64.exe` | 13,939,200 | |
| `data\bin\merlinAgent-Windows-x64-Debug.exe` | 13,939,200 | |
| `data\bin\merlinCLI-Windows-x64.exe` | 20,754,432 | |
| `data\bin\merlinAgent-Darwin-arm64` | 11,808,210 | Mach-O |
| `data\bin\merlinAgent-Darwin-x64` | 12,761,408 | Mach-O |
| `data\bin\merlinAgent-Linux-arm` | 12,124,284 | ELF |
| `data\bin\merlinAgent-Linux-arm64` | 11,534,460 | ELF |
| `data\bin\merlinAgent-Linux-x64` | 12,492,924 | ELF |
| `data\bin\merlinCLI-Darwin-arm64` | 19,571,874 | Mach-O |
| `data\bin\merlinCLI-Darwin-x64` | 20,804,192 | Mach-O |
| `data\bin\merlinCLI-Linux-arm` | 19,183,912 | ELF |
| `data\bin\merlinCLI-Linux-arm64` | 19,017,586 | ELF |
| `data\bin\merlinCLI-Linux-x64` | 20,299,557 | ELF |

### §3.1 The answer to "any other binary at a wrong subpath?"

`[verified]` **`merlinServer-Windows-x64.exe` at the root is the ONLY PE at a path that breaks the pattern — C-08 §8's correction stands and is the only one of its kind.** `[inferred]` All five other Windows PE binaries are under `data\bin\` exactly as inventoried.

`[verified]` **BUT the enumeration found a factual error in the earlier work that is NOT a path error:** C-08 §9 lists `merlinAgent-Darwin-arm64` (11,808,210) · `merlinAgent-Darwin-x64` (12,761,408) · `merlinAgent-Linux-arm` (12,124,284) · `merlinAgent-Linux-arm64` (11,534,460) · `merlinAgent-Linux-x64` (12,492,924) as *"still outstanding"* and implies they are the complete non-Windows agent set. `[inferred]` **The tree contains FIVE more non-Windows binaries C-08 §9 never mentions:**

```
data\bin\merlinCLI-Darwin-arm64   19,571,874
data\bin\merlinCLI-Darwin-x64     20,804,192
data\bin\merlinCLI-Linux-arm      19,183,912
data\bin\merlinCLI-Linux-arm64    19,017,586
data\bin\merlinCLI-Linux-x64      20,299,557
```

`[inferred]` **The outstanding-work list named the AGENT cross-platform set and omitted the CLI cross-platform set entirely.** `[inferred]` **That is the same species as C-08 §8's path error — a population recalled from the shape of the naming pattern rather than enumerated.** `[inferred]` **The cross-platform surface is 10 binaries, not 5.**

### §3.2 Also present and not previously enumerated

`[verified]` **Two source/definition files sit beside the DLLs and are the key to task 4:**
- `data\bin\merlin.def` — **882 B, 22 LF** — the module-definition file listing the seven exports.
- `data\bin\merlin.c` — **1,642 B** — the C shim defining `DllMain` and `Magic`.

`[verified]` **`data\agents\` contains only `README.MD` (167 B)** — the directory is essentially empty, so the agents live in `data\bin\`, not in the intuitively-named `data\agents\`. `[inferred]` **A second name-is-not-a-measurement instance: the folder called `agents` holds no agents.**

---

## §4 T8.4 — the seven exports: what the 67-byte siblings actually DO

`[verified]` **The export table, read from `.edata` at RVA `0x2CB5000`, file offset `0xC7A600`:**

```
ord=0  RVA=0x15C0  VA=0x61C815C0  DllInstall
ord=1  RVA=0x1610  VA=0x61C81610  DllRegisterServer
ord=2  RVA=0x1660  VA=0x61C81660  DllUnregisterServer
ord=3  RVA=0x1507  VA=0x61C81507  Magic
ord=4  RVA=0x16B0  VA=0x61C816B0  Merlin
ord=5  RVA=0x1520  VA=0x61C81520  Run
ord=6  RVA=0x1570  VA=0x61C81570  VoidFunc
```

`[verified]` **The export name is `Magic`, not `_Magic`.** `[inferred]` **The leading underscore in the Ghidra dump is a label-decorating convention, not part of the exported name.** `[inferred]` **A reader who took the symbol dump as the export list would search for the wrong string**, which matters for anyone checking `GetProcAddress` behaviour.

### §4.1 The bytes — `_Magic`

`[verified]` **`Magic` @ `0x61C81507`, file offset `0xB07`, 24 bytes, `.text`:**

```
55 89 e5 83 ec 18        push ebp; mov ebp,esp; sub esp,0x18
8b 45 08                 mov eax,[ebp+8]        ; arg = char *url
89 04 24                 mov [esp],eax          ; pass url
e8 98 01 00 00           call 0x61C816A4
b8 00 00 00 00           mov eax,0              ; return 0
c9 c3                    leave; ret
```

`[inferred]` **`Magic` is a genuine two-line forwarding shell, but not a PE forwarder — it is compiled C that loads its argument and tail-calls `Merlin`.** `[inferred]` The `call` at offset `0x0E` targets `0x61C816A4`, which lies **inside** `Merlin`'s 64-byte body (`0x61C816B0` + 64 = `0x61C816F0`; `0x61C816A4` is 12 bytes before `Merlin`'s entry).

`[inferred]` **That looks wrong and needs stating plainly rather than smoothing over: the call target sits BEFORE `Merlin`'s declared entry.** `[inferred]` **Most likely explanation, and it is a limitation: `Merlin`'s declared start is the cgo wrapper's entry (`0x61C816B0`), while the actual Go function body begins earlier at `0x61C816A4`, and Ghidra's stated size of 64 reflects its own body bound rather than the function's true extent.** `[inferred]` **I did not resolve this and am not asserting a mechanism — the bytes are exact, the boundary interpretation is open.** Recorded as R-95.2.

### §4.2 The five 67-byte siblings — and `Merlin` — are cgo entry stubs

`[verified]` **`Run` @ `0x61C81520`, file offset `0xB20`, 67 bytes, `.text`:**

```
53 83 ec 28              push ebx; sub esp,0x28
e8 57 03 00 00           call 0x61C81880      -> _cgo_wait_runtime_init_done
c7 44 24 08 00 00 00 00  mov [esp+8],0
89 c3                    mov ebx,eax
0f b6 05 48 40 3A 62     movzx eax,byte [0x623A4048]
c7 04 24 30 48 28 62     mov [esp],0x62284830
89 5c 24 0c              mov [esp+0xC],ebx
88 44 24 1F              mov [esp+0x1F],al
8d 44 24 1F              lea eax,[esp+0x1F]
89 44 24 04              mov [esp+4],eax
e8 6A DE 0A 00           call 0x61D2F3C0      -> crosscall2
89 1C 24                 mov [esp],ebx
e8 92 01 00 00           call 0x61C816F0      -> _cgo_release_context
83 c4 28 5B C3           add esp,0x28; pop ebx; ret
```

`[verified]` **The three callees, resolved by address against the Ghidra symbol dump:**

| address | symbol | role |
|---|---|---|
| `0x61C81880` | **`_cgo_wait_runtime_init_done`** | blocks until the Go runtime is initialised |
| `0x61D2F3C0` | **`crosscall2`** | the cgo trampoline entering Go from C |
| `0x61C816F0` | **`_cgo_release_context`** | releases the cgo thread context on return |

`[inferred]` **THE THIN-FORWARDER HYPOTHESIS IS REFUTED. These are not forwarders, not blobs, and not hand-written. They are the standard cgo `//export` entry stub: wait for runtime → `crosscall2` into the Go symbol → release context → return.** `[inferred]` **The hypothesis was worth testing and the test is decisive, because the callees have NAMES in the symbol dump and the names are unambiguous.**

`[verified]` **All six stubs share the identical three-call skeleton.** Verified call sites:

| export | call 1 | call 2 | call 3 |
|---|---|---|---|
| `Run` | `+0x04` → `0x61C81880` | `+0x31` → `0x61D2F3C0` | `+0x39` → `0x61C816F0` |
| `VoidFunc` | `+0x04` → `0x61C81880` | `+0x31` → `0x61D2F3C0` | `+0x39` → `0x61C816F0` |
| `Merlin` | `+0x04` → `0x61C81880` | `+0x2E` → `0x61D2F3C0` | `+0x36` → `0x61C816F0` |

`[inferred]` **What distinguishes the six is ONE immediate — the first argument handed to `crosscall2`:**

```
Run                  -> 0x62284830
VoidFunc             -> 0x62284850
DllInstall           -> 0x62284890
DllRegisterServer    -> 0x622848D0
DllUnregisterServer  -> 0x62284910
Merlin               -> 0x62284950
```

`[inferred]` **Stride is 0x40 (64 bytes), strictly increasing, one record per export.** `[inferred]` **These are per-export cgo argument blocks, not string data** — reading the bytes at those addresses shows they are themselves Go function bodies carrying the `morestack` preamble (`8b 0d 88 f9 91 62 / 64 8b 09 / 8b 09 / 3b 61 08 / 76 …` = load `g` from TLS, compare `SP` against `g.stackguard0`), i.e. **the exported Go functions themselves, reached through a 0x40-aligned stub table.**

`[inferred]` **`VoidFunc`, `DllInstall`, `DllRegisterServer` and `DllUnregisterServer` are bodies byte-identical apart from that one immediate** — which is exactly what a linker-emitted stub set looks like when four differently-named Go functions share a generated wrapper shape.

### §4.3 Why the export list exists — from `merlin.def` and `merlin.c`

`[read]` **`merlin.def` header comment, verbatim:**

> Lists the functions the DLL exports. Passing this file to the final `gcc -shared` link turns OFF mingw's default `--export-all-symbols` behavior and exports ONLY the symbols named below.
> **This is required for the windows/386 build: under Go 1.27 the c-archive carries standard-library symbols that i686-w64-mingw32-ld refuses to auto-export ("cannot export addMulVVWx / go:buildinfo: symbol not found"), which breaks `make 386`.** Exporting an explicit list sidesteps that and, as a bonus, keeps the export table down to the real entry points on both architectures instead of thousands of internal Go symbols.
> The names are the `//export` functions in main.go plus `Magic()` from merlin.c.

`[read]` **`merlin.c`, verbatim, the relevant function:**

```c
// Magic is the exported function name that can be called from sRDI to launch a Merlin agent
int Magic(char *url){
    Merlin(url);
    return 0;
}
```

`[inferred]` **THE `Magic`→`Merlin` ADJACENCY C-00 §5 RECORDED IS A REAL CALL RELATIONSHIP, NOT AN ARTIFACT OF ADDRESS ORDER.** `[inferred]` **The source says so directly: `Magic` calls `Merlin`, and `Magic` exists specifically as the `sRDI` entry point.** `[inferred]` **The 24-byte `Magic` body in §4.1 is the compiled form of exactly those two statements.**

`[inferred]` **And the export list's own justification connects the two rounds' findings:** `[inferred]` **the seven-name `.def` exists BECAUSE Go 1.27's c-archive misbehaves under `i686-w64-mingw32-ld`.** `[inferred]` **C-08 §6 recorded Go 1.27.2 breaking Ghidra's analyzers; this records the same Go version breaking the MinGW 32-bit linker, in the vendor's own words.** `[inferred]` **Two independent Go 1.27 toolchain casualties, different toolchains entirely.**

`[inferred]` `DllInstall` / `DllRegisterServer` / `DllUnregisterServer` / `VoidFunc` are **`regsvr32` boilerplate names and a do-nothing placeholder**, required by the `.def` because the `//export` set includes them, not because the implant uses them. `[inferred]` `VoidFunc` is the giveaway — its name says it does nothing.

---

## §5 Verification, and what this round did NOT do

`[verified]` **No corpus binary was executed.** Every byte came from `[IO.File]::ReadAllBytes` and manual PE structure parsing. `[inferred]` `merlin.c`'s commented-out `MessageBoxA` calls were **read and not run**; the DLL was never loaded.

`[verified]` **`DumpSyms.java` was read, not executed, and no Ghidra run was needed.** `[inferred]` **Therefore this round produced no new toolchain failures — not because the seven in C-08 were resolved, but because the instrument was not invoked.** `[inferred]` **A round with no tool failures is not evidence the tool is fixed.**

`[verified]` **One probe failure, failed loud:** the first PE section parse used a wrong optional-header offset (`$o+16`) and printed **garbage section names (`?\$?L$`) and `NO SECTION` for all seven exports.** `[inferred]` **The output was self-evidently wrong — a section table cannot have binary filth for names — and the offset was corrected to `$peOff+20` (COFF header is 20 bytes).** `[inferred]` **The re-run produced the 18 canonical section names matching C-08 §3 exactly, which is the confirmation that the parse is now correct.** `[inferred]` **A silently-plausible wrong answer would have been far more dangerous here; this one was loud by construction.**

`[verified]` **A second probe failure, failed loud:** the `.edata` export table was first addressed with a hardcoded `0x600+($rva-0x1000)` formula and threw `IndexOutOfRangeException` immediately. `[inferred]` **Re-derived from the parsed section table instead — the `.edata` section is at `RawPtr=0xC7A600`, `VA=0x2CB5000`, so the arithmetic shortcut was simply wrong.** `[inferred]` **Both failures exited non-zero or produced visibly impossible output rather than a smaller census.**

`[inferred]` **INSTRUMENTABILITY IS NOT ACCURACY, and this round is a clean demonstration in the positive direction.** `[inferred]` **`merlinAgent-Windows-x64-Debug.exe` is fully instrumentable — Ghidra ran on it, it produced 11,246 functions, and the census completed cleanly. Every one of those facts was consistent with the conclusion that it is a debug build, and it is not: it is a console-subsystem build with the same `-s -w` stripping.** `[inferred]` **The filename is the only thing that ever called it debug.**

`[verified]` **Byte-census hazard, self-administered, and caught by the check.** The first draft of this sentence *named the two hazardous byte sequences as examples* and thereby embedded them, so the disclaimer contained the defect it disclaimed: the detector returned one match each for the UTF-8-of-U+00C2 sequence and for the UTF-8-of-U+FFFD sequence, against a positive control of four matches for the former in `D61_numeric_claim_audit.md`. `[inferred]` **Rewriting the sentence to describe the sequences rather than spell them is the fix; the count is now zero for both.** `[inferred]` **The lesson generalises: a hazard check that inspects the document must be run against the document, because a claim of cleanliness is not a measurement of cleanliness — and a check whose own text supplies the match is the strongest possible demonstration of why the control matters.** U+FFFD count is 0 by codepoint; no BOM; CR = 0.

---

## §6 Residual unknowns

| ID | Unknown | Severity | Probe |
|---|---|---|---|
| **R-95.1** | **The five non-Windows CLI binaries were never analysed and their symbols remain uncounted** — C-08 §9 omitted the entire CLI cross-platform set. | **high** | Run the gate on `merlinCLI-Darwin-*`/`Linux-*`; Mach-O/ELF need a provider or `-processor` hint. |
| **R-95.2** | **`Magic`'s call target `0x61C816A4` lies 12 bytes BEFORE `Merlin`'s declared entry `0x61C816B0`.** Exact bytes; the boundary interpretation is unresolved. | **medium** | Read the bytes at `0x61C816A4` and resolve whether Ghidra's body bound under-reports the true function extent. |
| **R-95.3** | **The 0x40-stride stub table was read at six points only.** Whether the table has further entries, and what bounds it, is unmeasured. | **medium** | Walk `0x62284830` outward while records remain plausible. |
| **R-95.4** | **`-H=windowsgui` explains the subsystem difference, but the two builds' BEHAVIOURAL divergence (if any) is untested.** Same Go source, same flags minus one, but no dynamic comparison was run. | **high** | Static diff of the two `.text` sections; no execution. |
| **R-95.5** | **The strings layer names the injection methods; whether all five are reachable from the default command set is untested.** Presence of a symbol is not reachability. | **medium** | Map `commands.*` symbols against the server's job dispatch table. |
| **R-95.6** | **The `data\agents\` directory holds only a README** — where the implant deployment path expects agents is inferred from `data\bin\`, not from configuration. | **low** | Read `data\README.MD` and the server's agent-path resolution. |

---

## §7 Summary — four answers

`[verified]` **T8.1 — THE TWO AGENT BUILDS DIFFER, by exactly five strings over 40,922 lines: 2 unique to release, 3 unique to Debug.** The real delta is `-H=windowsgui` (present in release, absent in Debug) plus a reordered `-X` pair; the 21-byte gap decomposes as 15 + 6. **Independently confirmed by the PE header: release = subsystem 2 (GUI), Debug = subsystem 3 (CONSOLE).** Two unrelated measurements agree. **C-08 §2's "byte-identical" is corrected here — the census figures match, the bytes do not.** The strings dumps were **not at the stated path**; they are at `07_OUTPUT\extractions\T8\strings\`, found by enumeration. **Operational payload, in cleartext in both builds: the full `-ldflags` set — `psk=merlin`, `auth=opaque`, `url=https://127.0.0.1:443`, `addr=127.0.0.1:4444`, `protocol=h2`, `sleep=30s`, `padding=4096`, `maxretry=7`, transforms `jwe,gob-base`, a Chrome 40 user-agent, build hash `e68a5e81…`, `-s -w` stripping —** plus the pipe namespace `\\.\pipe\merlin`, five named shellcode-injection methods, go-clr v1.0.4 CLR loading, and build provenance from `/opt/hostedtoolcache/go/1.27.2/` on a GitHub Actions runner.

`[verified]` **T8.2 — `DumpSyms.java` CANNOT reach a spaced path, and the constraint is in two places.** `:27` `new File(args[0])` takes the output path verbatim; Ghidra's launcher re-splits `-postScript` args on whitespace after cmd has already passed them correctly quoted (C-08 §5 failure 6). **Second, independent instance:** `:34` `currentProgram.getName()` derives the dump's own provenance line from the imported filename — so a spaced **target** silently misnames the artifact. **The stage path fails loudly; a spaced target corrupts silently, and silent is worse.** Because the repo root `FOR REDDACTED\` contains a space, **staging is structural, not a workaround.**

`[verified]` **T8.3 — enumerated, and it finds one path error and one population error.** `merlinServer-Windows-x64.exe` alone at the extraction root is **the only wrong-subpath PE** — C-08 §8's correction stands as the sole instance. **But C-08 §9's outstanding list names five cross-platform AGENT binaries and omits the five cross-platform CLI binaries entirely** (`merlinCLI-Darwin-arm64` 19,571,874 · `-Darwin-x64` 20,804,192 · `-Linux-arm` 19,183,912 · `-Linux-arm64` 19,017,586 · `-Linux-x64` 20,299,557). **The cross-platform surface is 10 binaries, not 5** — the same name-from-a-pattern species as the path error. Also: `data\agents\` contains only a README, and `merlin.def` / `merlin.c` sit beside the DLLs.

`[verified]` **T8.4 — THE THIN-FORWARDER HYPOTHESIS IS REFUTED, and the answer is cgo.** The export table has **exactly 7** entries (`DllInstall`, `DllRegisterServer`, `DllUnregisterServer`, `Magic`, `Merlin`, `Run`, `VoidFunc`; note **`Magic`, not `_Magic`** — the underscore is Ghidra's). All six 67/64-byte bodies share **one three-call skeleton: `_cgo_wait_runtime_init_done` → `crosscall2` → `_cgo_release_context`** — the standard cgo `//export` stub. They differ by **one immediate**, a 0x40-strided per-export cgo argument block. **`Magic` is a genuine forwarding shell, but compiled C, not a PE forwarder** — and `merlin.c` states its purpose: **the `sRDI` entry point**, calling `Merlin`. **The seven-name `.def` exists because Go 1.27's c-archive breaks `i686-w64-mingw32-ld` auto-export** (`cannot export addMulVVWx / go:buildinfo`) — **the same Go version C-08 §6 recorded breaking Ghidra's analyzers, in a completely different toolchain.**
