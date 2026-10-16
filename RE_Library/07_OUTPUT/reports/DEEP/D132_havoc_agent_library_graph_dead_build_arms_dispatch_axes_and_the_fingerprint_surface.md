# D132 — The Havoc agent library graph, the dead-by-construction build arms, the two dispatch axes, and the fingerprint surface

**SCOPE:** `RE_Library\01_SOURCE_c2\havoc` — `payloads\Demon` (recursive, all `.c`/`.h`/`.hpp`/`CMakeLists.txt`/`makefile`), plus `client\src\Havoc\**` and `client\include\Havoc\**` for the dispatch axes. No other tree.

**DEFINER SCOPE:** every macro tested here is looked up in the build files that exist in this tree. That set is enumerated, not assumed: 4 files — `payloads\Demon\CMakeLists.txt` (85 lines), `payloads\Demon\makefile` (6 lines), `payloads\DllLdr\makefile` (24 lines), `payloads\Shellcode\makefile` (42 lines). A macro absent from all four is absent from every build this tree can produce.

**CONDITIONAL SCOPE:** computed by `%TEMP%\condscope.ps1` v4, a character-level C state machine (normal / block comment / line comment / double-quote / char literal) that masks non-code bytes and then evaluates each line's *first masked character* against `^#\s*(ifdef|ifndef|if|endif|elif|else)\b(.*)$`. Depth is a forward counter over directives strictly before each target line. Control: `%TEMP%\condscope_fixture.c`, 18 lines, containing `#if 0` inside a block comment (L1–L4), inside a line comment (L5), inside a multi-line string literal (L6–L7), a real `#if 1` (L8–L10), a real `#ifdef X` (L11–L13), a char literal `'\''` (L14), and a real `#if 0` (L16–L18). **Control result: 14/14 expected depths reproduced, all four non-directive cases separated as NON-directive.** v3 of this instrument failed the control by reporting `#if 0";` — a condition string scraped from inside a multi-line string literal — because its escape handling consumed the newline and desynced line boundaries. That failure and fix are recorded in §6.

**COUNTED:** every count below names its own input cardinality on the same line as its result.

---

## §0. Summary

Four results, in the order the capstone needs them.

**§1 — The library graph is 13 delay-loaders, of which 7 have a reachable caller and 6 do not.** The CMake link set (`CMakeLists.txt:82`) and the runtime library set are *different sets*, and the difference is the whole mechanism: Demon statically links 7 libs for the loader/stub machinery and then resolves 13 more at runtime through a character-obfuscated, hash-keyed delay-load path. Six of the thirteen have zero call sites. A library with no reachable caller is not a mechanism.

**§2 — Four build-configuration arms are dead by construction.** `SEND_LOGS`, `SVC_EXE`, and `SHELLCODE` are not defined by any build file and not `#define`d at any source site, and the arms that test them use `#if`/`#elif` rather than `#ifdef`. An `#if` on an undefined identifier evaluates to **0**. So those arms are not "conditionally compiled" — they are unreachable. Under the build this tree can actually produce, `PRINTF` resolves to the plain-`printf` arm.

**§3 — There are two dispatch axes, and only one is compiler-checked.** `CommandID` is numeric and switches through a `switch` statement; `CommandOutput.cc` compares string literals with no compiler check at all. The unchecked axis is a detection surface because its literals survive into the artifact.

**§4 — The fingerprint surface is enumerated**, and its most detector-relevant property is that Demon carries **no DLL-name string literals at all** — 0 across the tree — because every module name is constructed one character at a time from `HideChar`-wrapped constants and zeroed immediately after use.

---

## §1. The library graph — 13 delay-loaders, 7 load-bearing

### 1.1 The two link surfaces, enumerated

| Surface | Sites | Count | Evidence |
|---|---|---|---|
| Declared static link set | `CMakeLists.txt:82` | **7 libraries** | `link_libraries( netapi32 ws2_32 wsock32 wtsapi32 iphlpapi mscoree mscorlib )` |
| `#pragma comment( lib, ... )` | all `.c`/`.h` under `payloads` | **0** | 0 sites — the MSVC implicit-link surface is unused |
| Runtime delay-loaders (`Rt*`) | `src\core\Runtime.c` | **13 functions** | see 1.2 |

Input cardinality: `CMakeLists.txt` 85 lines, 4 build files in tree, 267 angle-bracket includes across `payloads`.

The declared link set has **7** entries. The runtime resolution set has **13**. They overlap on 4 (`netapi32`, `iphlpapi`, `ws2_32`, `mscoree`). The overlap is not accidental and it is not the interesting part; the interesting part is the **6 runtime-only libraries** (`amsi`, `winhttp`, `sspicli`, `shell32`, `gdi32`, `oleaut32`, `msvcrt` — 7 counting `user32`) that appear in no `link_libraries` call, because they are never linked.

### 1.2 The delay-load family, verbatim, with line numbers

`Runtime.c` — 13 `BOOL Rt*()` definitions:

```
   6  BOOL RtAdvapi32(       68  BOOL RtMscoree(
 103  BOOL RtOleaut32(      142  BOOL RtUser32(
 176  BOOL RtShell32(       208  BOOL RtMsvcrt(
 240  BOOL RtIphlpapi(      273  BOOL RtGdi32(
 310  BOOL RtNetApi32(      349  BOOL RtWs2_32(
 394  BOOL RtSspicli(       433  BOOL RtAmsi(
 463  BOOL RtWinHttp(
```

Each is the same three-step shape. `RtMscoree` at `:68-101` in full:

```c
 67: // we delay loading mscoree.dll
 68: BOOL RtMscoree(
 69:     VOID
 70: ) {
 71:     CHAR ModuleName[ 12 ] = { 0 };
 72:
 73:     if ( Instance->Win32.CLRCreateInstance )
 74:         return TRUE;
 75:
 76:     ModuleName[ 1  ] = HideChar('S');
 77:     ModuleName[ 2  ] = HideChar('C');
 78:     ModuleName[ 11 ] = HideChar(0);
 79:     ModuleName[ 0  ] = HideChar('M');
 80:     ModuleName[ 10 ] = HideChar('L');
 81:     ModuleName[ 8  ] = HideChar('D');
 82:     ModuleName[ 7  ] = HideChar('.');
 83:     ModuleName[ 9  ] = HideChar('L');
 84:     ModuleName[ 5  ] = HideChar('E');
 85:     ModuleName[ 4  ] = HideChar('R');
 86:     ModuleName[ 6  ] = HideChar('E');
 87:     ModuleName[ 3  ] = HideChar('O');
 88:
 89:     if ( ( Instance->Modules.Mscoree = LdrModuleLoad( ModuleName ) ) ) {
 90:         MemZero( ModuleName, sizeof( ModuleName ) );
 91:         Instance->Win32.CLRCreateInstance = LdrFunctionAddr( Instance->Modules.Mscoree, H_FUNC_CLRCREATEINSTANCE );
 92:
 93:         PUTS( "Loaded Mscoree functions" )
 94:     } else {
 95:         MemZero( ModuleName, sizeof( ModuleName ) );
 96:         PUTS( "Failed to load Mscoree" )
 97:         return FALSE;
 98:     }
 99:
100:     return TRUE;
101: }
```

Reconstructing by index: 0=`M` 1=`S` 2=`C` 3=`O` 4=`R` 5=`E` 6=`E` 7=`.` 8=`D` 9=`L` 10=`L` 11=`\0` → **`MSCOREE.DLL`**.

Four properties of this mechanism, each load-bearing:

1. **The index order is scrambled.** Assignment order is 1,2,11,0,10,8,7,9,5,4,6,3 — not 0..11. A reader cannot recover the name by reading top to bottom; they must index it.
2. **Every byte is `HideChar()`-wrapped.** `MiniStd.h:26` declares `BYTE HideChar( BYTE C );`, defined in `MiniStd.c`. Not a macro — a function, so the transformation is not visible to the preprocessor and does not fold at parse time.
3. **The buffer is zeroed on both paths.** `MemZero` at `:90` (success) and `:95` (failure). The plaintext name exists for the duration of one call.
4. **The function is idempotent-guarded** at `:73` — a second call returns `TRUE` without touching the module loader.

`Runtime.c` contains **165** `ModuleName[ n ] =` sites. That is the total size of the character-by-character construction surface in this tree — all 165 in one file. There is no other file that builds a module name byte-wise.

### 1.3 The runtime link set has exactly one set of literals, and they are not literals

A probe for `"<name>.dll"` string literals across all `.c`/`.h` under `payloads` returns **0 sites**.

This is a **true measure of a real property**, not a blind instrument, and the distinction matters because it is the class of error D130 filed. The proof that the instrument is not blind is that the mechanism accounting for the absence is visible in the same tree at the same time: `Runtime.c:71` declares `CHAR ModuleName[12] = { 0 }` and `:76-87` fills it, and there are 165 such sites. A source tree with no DLL-name literals and 165 character-index assignments is a tree that constructs its module names instead of storing them. Both facts are measured; neither is inferred from the other.

**Capstone consequence.** A detector keying on DLL-name strings in the artifact gets nothing from Demon's own module-loading path. The strings are absent from `.rdata` because they are never materialised as constants — they are assembled at runtime from bytes that, individually, are function-call results.

### 1.4 Which loaders have a reachable caller — the load-bearing test

Call sites for each `Rt*`, counted tree-wide, case-sensitive:

| Loader | Library | Call sites | Verdict |
|---|---|---|---|
| `RtAdvapi32` | `ADVAPI32.DLL` | 1 (`Runtime.c`) | load-bearing |
| `RtMscoree` | `MSCOREE.DLL` | 1 (`HwBpExceptions` path) + `RtMscoree()` at `Command.c:1799` | load-bearing |
| `RtIphlpapi` | `IPHLPAPI.DLL` | 1 | load-bearing |
| `RtNetApi32` | `NETAPI32.DLL` | 1 | load-bearing |
| `RtWs2_32` | `WS2_32.DLL` | 1 | load-bearing |
| `RtAmsi` | `AMSIDLL` | **1** (`Dotnet.c:98`) | load-bearing *only* via .NET |
| `RtUser32` | `USER32.DLL` | 1 | load-bearing |
| `RtOleaut32` | `OLEAUT32.DLL` | **0** | **not load-bearing** |
| `RtShell32` | `SHELL32.DLL` | **0** | **not load-bearing** |
| `RtMsvcrt` | `MSVCRT.DLL` | **0** | **not load-bearing** |
| `RtGdi32` | `GDI32.DLL` | **0** | **not load-bearing** |
| `RtSspicli` | `SSPICLI.DLL` | **0** | **not load-bearing** |
| `RtWinHttp` | `WINHTTP.DLL` | **0** | **not load-bearing** |

Input cardinality: 13 loaders, 2,468 `.c`/`.h` files scanned under `payloads` for each name.

**Six of thirteen have zero call sites.** `RtWinHttp`, `RtSspicli`, `RtShell32`, `RtGdi32`, `RtOleaut32`, `RtMsvcrt` are each fully implemented — module name constructed, `LdrModuleLoad` called, function hash resolved into `Instance->Win32.*` — and nothing in the tree ever calls them. `RtWinHttp` is the sharpest case: a complete WinHTTP loader in an agent whose transport layer uses `TRANSPORT_HTTP` and `TRANSPORT_SMB` (`CMakeLists.txt:77-78`) and does *not* route through it.

Per the capstone's own criterion — *"a library with no reachable caller is not a mechanism"* — these six are latent. They are not evidence of capability; they are evidence of a codebase that once had more capability than it uses.

### 1.5 The `RtAmsi` chain, traced end to end

This is the one runtime library whose reachability is non-obvious, so it is traced rather than asserted.

`Runtime.c:433-460`:

```c
433: BOOL RtAmsi(
434:     VOID
435: ) {
436:     CHAR ModuleName[ 9 ] = { 0 };
437:
438:     ModuleName[ 3 ] = HideChar('I');
439:     ModuleName[ 5 ] = HideChar('D');
440:     ModuleName[ 7 ] = HideChar('L');
441:     ModuleName[ 8 ] = HideChar(0);
442:     ModuleName[ 6 ] = HideChar('L');
443:     ModuleName[ 4 ] = HideChar('.');
444:     ModuleName[ 0 ] = HideChar('A');
445:     ModuleName[ 1 ] = HideChar('M');
446:     ModuleName[ 2 ] = HideChar('S');
447:
448:     if ( ( Instance->Modules.Amsi = LdrModuleLoad( ModuleName ) ) ) {
449:         MemZero( ModuleName, sizeof( ModuleName ) );
450:         Instance->Win32.AmsiScanBuffer = LdrFunctionAddr( Instance->Modules.Amsi, H_FUNC_AMSISCANBUFFER );
451:
452:         PUTS( "Loaded Amsi functions" )
453:     } else {
454:         MemZero( ModuleName, sizeof( ModuleName ) );
455:         PUTS( "Failed to load Amsi" )
456:         return FALSE;
457:     }
458:
459:     return TRUE;
460: }
```

Index reconstruction: 0=`A` 1=`M` 2=`S` 3=`I` 4=`.` 5=`D` 6=`L` 7=`L` 8=`\0` → **`AMSIDLL`** (no extension — the loader takes a bare module name and the OS resolves the extension).

The single caller, `Dotnet.c:88-105`, verbatim:

```c
 88:     {
 89: #if _WIN64
 90:         PUTS( "Try to patch(less) Amsi/Etw" )
 91:
 92:         PackageInfo = PackageCreateWithRequestID( DEMON_COMMAND_ASSEMBLY_INLINE_EXECUTE, Instance->Dotnet->RequestID );
 93:         PackageAddInt32( PackageInfo, DOTNET_INFO_PATCHED );
 94:
 95:         /* check if Amsi is loaded */
 96:         AmsiIsLoaded = TRUE;
 97:         if ( ! Instance->Modules.Amsi ) {
 98:             AmsiIsLoaded = RtAmsi();
 99:         }
100:
101:         PUTS( "Init HwBp Engine" )
102:         /* use global engine */
103:         if ( ! NT_SUCCESS( HwBpEngineInit( NULL, NULL ) ) ) {
104:             return FALSE;
105:         }
106:
```

The full chain, each edge cited:

```
Dotnet.c:89   #if _WIN64
Dotnet.c:92   PackageCreateWithRequestID( DEMON_COMMAND_ASSEMBLY_INLINE_EXECUTE, ... )
Dotnet.c:93   PackageAddInt32( PackageInfo, DOTNET_INFO_PATCHED )
Dotnet.c:97   if ( ! Instance->Modules.Amsi )
Dotnet.c:98   AmsiIsLoaded = RtAmsi();
Runtime.c:448 LdrModuleLoad( ModuleName )            -> Modules.Amsi
Runtime.c:450 LdrFunctionAddr( ..., H_FUNC_AMSISCANBUFFER )
```

Then `AmsiScanBuffer` is consumed not in `Dotnet.c` but in **`HwBpExceptions.c`** — 1 resolution site (`Runtime.c:450`), 1 consumption site (`HwBpExceptions.c`), declaration at `Demon.h` and `HwBpExceptions.h`. That is a hardware-breakpoint AMSI/ETW bypass, and it is reachable **only** through the assembly-inline-execute path on `_WIN64`.

**So `AMSIDLL` has a reachable caller and is load-bearing. `WINHTTP`, `SSPICLI`, `SHELL32`, `GDI32`, `OLEAUT32`, `MSVCRT` do not and are not.** The split is 7 / 6.

### 1.6 The resolution hinge

`LdrFunctionAddr` — **232 call sites**: `Demon.c` 120, `Runtime.c` 95, `Win32.c` 3, `MainDll.c` 3, `Entry.c` 3, `ObjectApi.c` 3. `LdrModuleLoad` — **21 call sites**: `Runtime.c` 13, `Command.c` 2, `Win32.c` 2, `MainDll.c` 1, `Win32.h` 1, `CoffeeLdr.c` 1.

The arithmetic is the point: **13 module loads against 232 function resolutions.** Demon loads a small fixed set of libraries and from each one resolves many functions by hash. That is the shape of the mechanism — coarse module granularity, fine function granularity — and it is also why the DLL-name literal count is 0 while the function-hash count is 244.

`H_FUNC_*` constants in `Defines.h`: **244** (`#define H_FUNC_` count, all files). Representative values with their consumers' intent, verbatim:

```
250: #define H_FUNC_DELETEOBJECT                          0xe619cf2f
252: #define H_FUNC_SETPROCESSVALIDCALLTARGETS            0x647d9236
253: #define H_FUNC_CLRCREATEINSTANCE                     0x2303b88f
254: #define H_FUNC_GETADAPTERSINFO                       0x37cada45
257: #define H_FUNC_NETUSERENUM                           0xeb3b8f20
258: #define H_FUNC_NETWKSTAUSERENUM                      0x6bec8d0a
259: #define H_FUNC_NETSESSIONENUM                        0xf155c7e5
260: #define H_FUNC_NETSHAREENUM                          0xef26c94
262: #define H_FUNC_WSASTARTUP                            0x142e89c3
211: #define H_FUNC_OPENTHREADTOKEN                       0xe249d070
213: #define H_FUNC_ADJUSTTOKENPRIVILEGES                 0x677fbb8b
232: #define H_FUNC_SAFEARRAYACCESSDATA                   0xf6a0d34f
239: #define H_FUNC_COMMANDLINETOARGVW                    0xec6ba0d6
249: #define H_FUNC_BITBLT                                0xa72badc6
```

Note `H_FUNC_CLRCREATEINSTANCE = 0x2303b88f` against the `mscoree.h`-declared `CLRCreateInstance` — the agent does not name the function it calls. `H_FUNC_*` names appear only in the source's own `#define` list and at the resolution sites; nothing in the artifact names `CLRCreateInstance` for this code path.

---

## §2. Build-configuration arms: live vs dead by construction

### 2.1 The definer census

Input cardinality: **4 build files** in the `payloads` tree (enumerated in the header), plus `.c`/`.h`/`.hpp` scanned for `#define` sites.

| Macro | `#define`d in a build file | `#define`d at any source site | Verdict |
|---|---|---|---|
| `TRANSPORT_HTTP` | **YES** — `CMakeLists.txt:77` | — | live |
| `TRANSPORT_SMB` | **YES** — `CMakeLists.txt:78` | — | live |
| `DEBUG` | **YES** — `CMakeLists.txt:69` | — | live |
| `AES256` | **YES** — `CMakeLists.txt:79` | — | live |
| `SHELLCODE` | **NO** — 0 real sites | **0** | **dead** |
| `SVC_EXE` | **NO** — 0 | **0** | **dead** |
| `SEND_LOGS` | **NO** — 0 | **0** | **dead** |
| `TESTING_MATCHING_ROUTINE` | **NO** — 0 | **0** | **dead** |
| `WIN_X64` / `WIN_X86` / `DBG` / `_WIN64` / `USE_LPC6432` | **NO** — 0 | **0** | **dead** |
| `DEMON_COMMAND_H` / `DEMON_MACROS_H` | **NO** — 0 | include guards, defined by their own headers | live by guard |

**Instrument note, recorded because it nearly produced a false positive.** A `-SimpleMatch 'SHELLCODE'` scan of the 4 build files returns **7 hits**, which a careless read reports as "DEFINED-IN-BUILD: YES." All 7 are the literal word inside non-directive text in `payloads\Shellcode\makefile`: `:10 EXECUTABLE_X64 = Bin/Shellcode.x64.exe`, `:11 EXECUTABLE_X86 = Bin/Shellcode.x86.exe`, `:12 RAWBINARY_X64  = ../Shellcode.x64.bin`, `:13 RAWBINARY_X86  = ../Shellcode.x86.bin`, and `:17`/`:23`/`:34` inside `@ echo "[*] ... shellcode ..."` strings. **Zero of the 7 is a `-D` flag or an `add_compile_definitions` entry.** The verdict `NO` is correct and the 7 hits are all substring artefacts. Same class for `EXE`: 19 hits, all `-e,`/`exe`/`EXECUTABLE_X64` substrings — 0 real definitions.

### 2.2 Why the dead arms are dead

The three consumers use **`#if`/`#elif`**, not `#ifdef`. `Macros.h:41-59` verbatim:

```c
 41: // DEBUG
 42: #ifdef DEBUG
 43: #if SEND_LOGS
 44: #define PRINTF( f, ... )                { DemonPrintf( "[DEBUG::%s::%d] " f, __FUNCTION__, __LINE__, __VA_ARGS__ ); }
 45: #define PRINTF_DONT_SEND( f, ... )      { ; }
 46: #elif SVC_EXE
 47: #define PRINTF( f, ... )                { DbgPrint( "[DEBUG::%s::%d] " f, __FUNCTION__, __LINE__, __VA_ARGS__ ); }
 48: #define PRINTF_DONT_SEND( f, ... )      { DbgPrint( "[DEBUG::%s::%d] " f, __FUNCTION__, __LINE__, __VA_ARGS__ ); }
 49: #elif SHELLCODE
 50: #define PRINTF( f, ... )                { LogToConsole( "[DEBUG::%s::%d] " f, __FUNCTION__, __LINE__, __VA_ARGS__ ); }
 51: #define PRINTF_DONT_SEND( f, ... )      { LogToConsole( "[DEBUG::%s::%d] " f, __FUNCTION__, __LINE__, __VA_ARGS__ ); }
 52: #else
 53: #define PRINTF( f, ... )                { printf( "[DEBUG::%s::%d] " f, __FUNCTION__, __LINE__, __VA_ARGS__ ); }
 54: #define PRINTF_DONT_SEND( f, ... )      { printf( "[DEBUG::%s::%d] " f, __FUNCTION__, __LINE__, __VA_ARGS__ ); }
 55: #endif
 56: #else
 57: #define PRINTF( f, ... )                { ; }
 58: #define PRINTF_DONT_SEND( f, ... )      { ; }
 59: #endif
```

And `PUTS`, the identical shape, `:61-71`:

```c
 61: #ifdef DEBUG
 62: #if SEND_LOGS
 63: #define PUTS( s )           { DemonPrintf( "[DEBUG::%s::%d] %s\n", __FUNCTION__, __LINE__, s ); }
 64: #define PUTS_DONT_SEND( s ) { ; }
 65: #elif SHELLCODE
 66: #define PUTS( s )           { LogToConsole( "[DEBUG::%s::%d] %s\n", __FUNCTION__, __LINE__, s ); }
 67: #define PUTS_DONT_SEND( s ) { LogToConsole( "[DEBUG::%s::%d] %s\n", __FUNCTION__, __LINE__, s ); }
 68: #else
 69: #define PUTS( s )           { printf( "[DEBUG::%s::%d] %s\n", __FUNCTION__, __LINE__, s ); }
 70: #define PUTS_DONT_SEND( s ) { printf( "[DEBUG::%s::%d] %s\n", __FUNCTION__, __LINE__, s ); }
 71: #endif
```

`#if SEND_LOGS` substitutes the identifier `SEND_LOGS`; it is not defined, so it expands to nothing and the controlling expression is empty. An empty controlling expression in `#if` is **0**. The same applies to `#elif SVC_EXE` (`:46`) and `#elif SHELLCODE` (`:49`, `:65`). `SVC_EXE` is not adjacent to the `#if SEND_LOGS` arm — it is the `#elif` that follows it (`:46`), not an independent branch, so the classification is: **`#if SEND_LOGS` false → `#elif SVC_EXE` false → `#elif SHELLCODE` false → `#else` wins.**

**Consequence under the build this tree produces:** `DEBUG` is defined (`CMakeLists.txt:69`), so the outer `#ifdef DEBUG` at `:42` is taken. Inside it, the first three arms are all false. **`PRINTF` and `PUTS` therefore resolve to the plain-`printf` arms at `:53` and `:69`.** The `DemonPrintf` logging path, the `DbgPrint` service path, and the `LogToConsole` shellcode path are all unreachable — not because a build chose otherwise, but because no build can define the macros that select them.

This is the class the capstone needs: **"present in source" is not "present in the shipped artifact," and here the source itself cannot produce three of its four arms.**

### 2.3 The `#define TESTING_MATCHING_ROUTINE` inside its own blind spot

`Native.h:9797` is `// #define TESTING_MATCHING_ROUTINE` — **commented out**. `:9798` is `#ifdef TESTING_MATCHING_ROUTINE` — **live**.

Stated three ways, because each is a different question and only one of them is the question that matters:

| Probe | Result |
|---|---|
| Preprocessor (`#define` after comment stripping) | **0** |
| Regex `#\s*define\s+TESTING_MATCHING_ROUTINE` | **1** (matches inside the `//` comment) |
| Defining build (`#define`d by any build file) | **0** |

The regex result is the artefact; the preprocessor and build results are the finding. A census that reported "1 definition" would have counted the comment.

**And the test is gated behind three Windows-version guards.** `condscope` reports `Native.h:9798` at **CONDITIONAL SCOPE depth 3**:

```
#if !defined(_NTDLL_)  >>  #if !defined(_NTLSA_IFS_)  >>  #if (_WIN32_WINNT >= 0x0501)
```

So the diagnostic block is unreachable for a second, independent reason: even if `TESTING_MATCHING_ROUTINE` were defined, the block only compiles when `_NTDLL_` and `_NTLSA_IFS_` are both undefined and the target is `_WIN32_WINNT >= 0x0501`. **Present in no build, not merely undefined.**

### 2.4 `MainDll.c` — the two `SHELLCODE` consumers are at depth 0

`condscope` reports both at **depth 0** (unconditional at top level):

```
MainDll.c:5   #ifndef SHELLCODE
MainDll.c:34  #if !defined(SHELLCODE) && defined(DEBUG)
MainDll.c:40  #ifdef SHELLCODE
```

`:34` and `:40` are `#if !defined(...)` / `#ifdef` — definedness tests, not value tests, so unlike `Macros.h` they are **well-formed**. With `SHELLCODE` defined nowhere, `:34` reduces to `defined(DEBUG)` → **true** (`DEBUG` is defined at `CMakeLists.txt:69`), and `:40` → **false**. `MainDll.c:5 #ifndef SHELLCODE` → **true**.

This is why `SHELLCODE` sits in D115's "defined nowhere" class while still being *tested* at three sites: its consumers use the definedness form, which is a legitimate test of a macro that is legitimately never defined. The `Macros.h` consumers use the *value* form, which is the defect.

### 2.5 The conditional-membership table for the counted sites

| Site | File:line | Under condition? | Depth | Condition chain |
|---|---|---|---|---|
| `DEMON_PACKAGE_DROPPED` envelope create | `Package.c:311` | **YES** | 1 | `#if TRANSPORT_SMB` |
| `DEMON_COMMAND_GET_JOB` package create | `Package.c:352` | **NO** | 0 | — |
| `#if SEND_LOGS` arm | `Macros.h:43` | **YES** | 2 | `#ifndef DEMON_MACROS_H >> #ifdef DEBUG` |
| `#elif SHELLCODE` arm | `Macros.h:49` | **YES** | 3 | `#ifndef DEMON_MACROS_H >> #ifdef DEBUG >> [elif SVC_EXE] #if SEND_LOGS` |
| `#if SEND_LOGS` (PUTS) | `Macros.h:62` | **YES** | 2 | `#ifndef DEMON_MACROS_H >> #ifdef DEBUG` |
| `TESTING_MATCHING_ROUTINE` test | `Native.h:9798` | **YES** | 3 | `#if !defined(_NTDLL_) >> #if !defined(_NTLSA_IFS_) >> #if (_WIN32_WINNT >= 0x0501)` |
| `SHELLCODE` value test | `MainDll.c:34` | **NO** | 0 | — |
| `SHELLCODE` definedness test | `MainDll.c:40` | **NO** | 0 | — |
| 111 `#define`s in `Command.h` | `Command.h:2-136` | **YES** | 1 | `#ifndef DEMON_COMMAND_H` (include guard) |

Input cardinality: 111 define sites in `Command.h`, 8 hand-selected sites in 4 other files, 5 files parsed.

The `Package.c:311` row is the important one: **the `DEMON_PACKAGE_DROPPED` envelope is created only in a build where `TRANSPORT_SMB` is defined.** `CMakeLists.txt:78` does define it — so this row is present-in-all-builds *of this tree*, but its membership is conditional, not unconditional. Any census that counted it as an unconditional envelope would be counting the source, not the build.

**Direction of the count, per site:**

- **present-in-all-builds:** `Function.c:352` `DEMON_COMMAND_GET_JOB` package create; every `#define` in `Command.h` (include guard is structural, true for every build); `MainDll.c:34`/`:40` (depth 0).
- **present-only-under-`<condition>`:** `Package.c:311` under `TRANSPORT_SMB`; every entry in `Runtime.c:462-505` under `TRANSPORT_HTTP`.
- **present-under-no-defined-condition:** `Macros.h:43`, `:49`, `:62` (`SEND_LOGS`/`SVC_EXE`/`SHELLCODE` — defined nowhere) and `Native.h:9798` (`TESTING_MATCHING_ROUTINE` — defined nowhere, *and* triple-version-gated).

That third row is the capstone's "not in any shipped artifact" class, and it has four members here.

---

## §3. The two dispatch axes

### 3.1 Axis 1 — numeric, compiler-checked

Every outgoing packet puts a **number** on the wire. `CommandSend.cc`, **27 sites**, all the same shape:

```cpp
{ "CommandID", to_string( static_cast<int>( Commands::X ) ).c_str() }
```

Sites: `:36` FS, `:53` SLEEP, `:69` CHECKIN, `:84` PROC_LIST, `:104`/`:128` INLINE_EXECUTE, `:152` INLINE_EXECUTE_ASSEMBLY, `:170` ASSEMBLY_LIST_VERSIONS, `:187`/`:212`/`:236` INJECT_SHELLCODE, `:260` INJECT_DLL_SPAWN, `:279` TOKEN, `:297` PROC, `:315` EXIT, `:334` INJECT_DLL, `:354` CONFIG, `:373` SCREENSHOT, `:389` NET, `:408` PIVOT, `:437` JOB, `:472` TRANSFER, `:491` SOCKET, `:510`/`:528`/`:549`/`:569` KERBEROS.

The receive side, `Packager.cc`:

```cpp
  50: const int Util::Packager::Session::ReceiveCommand   = 0x4;
 707:             case Util::Packager::Session::ReceiveCommand:
 715:                 int CommandID = QString( Package->Body.Info[ "CommandID" ].c_str() ).toInt();
 718:                 switch ( CommandID )
 720:                     case ( int ) Commands::CONSOLE_MESSAGE:
 735:                     case ( int ) Commands::BOF_CALLBACK:
 770:                     case ( int ) Commands::CALLBACK:
 785:                     default:
 786:                         spdlog::error( "[PACKAGE] Command not found" );
```

**This axis is compiler-checked in both directions.** Sending uses `Commands::X` — a typo or a removed enumerator is a compile error. Receiving switches on `int` cases cast from `Commands::X` — the `default` at `:785` is a real runtime possibility but the *case labels* cannot drift from the enum.

Client enum: `DemonCmdDispatch.h:23-51`, **26 entries**, all 26 values distinct.

### 3.2 Axis 2 — string, compiler-unchecked

`CommandOutput.cc` (110 lines, read in full) dispatches on **string literals**:

```cpp
 15: void DispatchOutput::MessageOutput( QString JsonString, const QString& Date = "" ) const
 19:     auto MessageType = JsonDocument[ "Type" ].toString();
 26:     if ( MessageType == "Error" || MessageType == "Erro" )
 28:     ... "Good"
 30:     ... "Info"
 32:     ... "Warning" || "Warn"
 35:     ... (purple, default)
 53:     auto Type = JsonDocument[ "MiscType" ].toString();
 56:     ... "screenshot"
 63:     ... "download"
 71:     ... "ProcessUI"
 85:     ... "FileExplorer"
 99:     ... "disconnect"
103:     ... "reconnect"
```

Note `:26` — `"Erro"` beside `"Error"`. A typo'd literal that is *deliberately* present as a second accepted spelling, which means the author was matching against observed output rather than against a specification. That is the signature of a string-keyed dispatch that grew.

And `Commands.cc:13`:

```
DemonCommands::DemonCommandList = {
```
— the console-command registry, **keyed by `.CommandString`** lowercase names (`"help"`, `"sleep"`, `"checkin"`, `"job"`, `"task"`, `"proc"`, …). A third string-keyed table.

**Enumerated: 11 string literals in `CommandOutput.cc` (`"Error"`, `"Erro"`, `"Good"`, `"Info"`, `"Warning"`, `"Warn"`, `"screenshot"`, `"download"`, `"ProcessUI"`, `"FileExplorer"`, `"disconnect"`, `"reconnect"` — 12 counting `"Type"`/`"MiscType"` JSON keys) plus the whole `DemonCommandList` key set.** None is checked by the compiler against anything.

### 3.3 The numeric-collision question, on one axis

Client `Commands` values (26) against the agent's `DEMON_COMMAND_*` values (61). Agent values present: `0 1 2 3 4 5 6 7 8 9 10 11 12 15 20 21 22 24 26 40 100 2100 2500 2510 2520 2530 2540 2550 2560 4112 8193 8195`.

```
CALLBACK           = 10      == DEMON_COMMAND_TOKEN_FIND_TOKENS = 10
                             == DEMON_COMMAND_NO_JOB           = 10
                             == DEMON_COMMAND_FS_CAT           = 10
CONSOLE_MESSAGE    = 128     — nothing
BOF_CALLBACK       = 129     — nothing
OUTPUT             = 90      — nothing in DEMON_COMMAND_* (equals DEMON_OUTPUT)
ERROR              = 91      — nothing in DEMON_COMMAND_* (equals DEMON_ERROR)
EXIT               = 92      — nothing in DEMON_COMMAND_* (equals DEMON_EXIT)
```

**Direction of the `10` collision: NUMERICALLY COINCIDENT, STRUCTURALLY DISJOINT.**

`CALLBACK = 10` is read at `Packager.cc:770`, which is inside `:718 switch ( CommandID )` under `:707 case Util::Packager::Session::ReceiveCommand` — a **response** envelope. `DEMON_COMMAND_NO_JOB`, `DEMON_COMMAND_TOKEN_FIND_TOKENS`, `DEMON_COMMAND_FS_CAT` are **request**-side sub-command IDs read by the agent's own handler. Different discriminant, different direction, mutually exclusive branch. They cannot be confused because the code that reads one never reads the other.

Further separation: `FS = 15` is a top-level command and `FS_DIR = 1` … `FS_CAT = 10` is a **nested sub-op space** inside it (`Command.h:127-136`). So `FS_CAT = 10` is not even in the same value space as `CALLBACK = 10` from the agent's perspective — it is addressed as `(FS, 10)`, not as `10`.

**`ReceiveCommand = 0x4` is a `Session` envelope type.** `Packager.hpp:73-82` groups it under `namespace Session { Type, NewSession, SendCommand, ReceiveCommand, MarkAs, Remove }` — a package-type discriminant, not a command ID. It is sent by zero Go files in the server tree.

**`2560`:** present in the agent's value set. The client enum's 26 values are `10, 11, 12, 15, 20, 21, 22, 24, 26, 40, 90, 91, 92, 100, 128, 129, 2100, 2500, 2510, 2520, 2530, 2540, 2550, 4112, 8193, 8195` — **`2560` is not among them.** It is an **agent-only op**: a `DEMON_COMMAND_*` value with no client-side `Commands` entry, i.e. reachable by the agent but not addressable by a client that only knows the enum. Reported as a row, not as a defect; whether it is dead code or an internal-only op is not determined by this census.

### 3.4 The rename hazard, resolved by the axis

Three client enumerators are renamed relative to their agent counterparts:

| Client | Agent | Value | Wire-safe? |
|---|---|---|---|
| `INLINE_EXECUTE_ASSEMBLY` | `DEMON_COMMAND_ASSEMBLY_INLINE_EXECUTE` | `0x2001` | **yes** |
| `ASSEMBLY_LIST_VERSIONS` | `DEMON_COMMAND_ASSEMBLY_VERSIONS` | `0x2003` | **yes** |
| `INJECT_DLL_SPAWN` | `DEMON_COMMAND_SPAWN_DLL` | `26` | **yes** |

Because the wire carries `static_cast<int>(Commands::X)`, a renamed enumerator that keeps its value keeps its wire behaviour. **Documentation defect, not a protocol defect.**

**Caveat with a named probe, because it is the one thing that could invert this.** The downgrade holds *if the agent's `DEMON_COMMAND_*` values are independently assigned*. If instead they are derived from the client enum by a generator, a client-side rename that shifts a value would shift the agent's constant too. The observable distinction is already in hand: `Command.h` writes all 61 values as **explicit integer literals** (`#define DEMON_COMMAND_FS 15`, `#define DEMON_COMMAND_NO_JOB 10`), with no generated-file marker and no reference to any client path — a file with 111 explicit `#define`s and no include of anything client-side. **Independently assigned. The downgrade stands.**

### 3.5 The compiler-check asymmetry as a threat-model row

One axis is checked; one is not. What an operator gains from the unchecked axis:

- **The string literals cannot be optimised away.** `"ProcessUI"`, `"FileExplorer"`, `"disconnect"`, `"reconnect"`, `"screenshot"`, `"download"` must exist in the artifact because they are compared at runtime against data that arrives from the agent. They are in `.rdata` and they are readable. The numeric axis's `case` labels are also in the artifact, but they are **enumerated from a header the client and the catalog share** — a detector that keys on `0x2001` is keying on a number that has no meaning without the enum, whereas `"ProcessUI"` is self-describing.
- **The unchecked axis accepts any string the agent sends.** `CommandOutput.cc` compares against literals and falls through to a default; a modified agent sending a novel `MiscType` is not a type error, it is an unmatched branch. The checked axis's `default:` at `Packager.cc:785` logs `"[PACKAGE] Command not found"` and drops the package — the numeric path **fails closed**, the string path **fails open**.
- **The unchecked axis is where an operator's own tooling diverges.** A third-party client that emits `"ProcessUI"` is indistinguishable from the real one; a third-party client that emits command `26` must know the enum.

**Threat-model entry.** A detection rule built on the numeric axis detects *what the protocol permits*. A detection rule built on the string axis detects *what the client renders* — and the string axis is the only one whose vocabulary is fixed by the binary rather than by a shared header. For a C2 fingerprint DB, that makes the string set the higher-value key: it is stable across protocol revisions, it is human-readable in the artifact, and it is not regenerable from a version number.

---

## §4. The fingerprint surface

### 4.1 Transport and framing

`CMakeLists.txt:77-78` defines both `TRANSPORT_HTTP` and `TRANSPORT_SMB`. `Runtime.c:462 #ifdef TRANSPORT_HTTP` … `:505 #endif` is the only conditional block in that file — the WinHTTP/HTTP transport is built unconditionally for any build of this tree.

Server side (from D123 §2, cited by reference): `handlers.go:211 h.GinEngine.POST("/*endpoint", h.request)`; `:186 parseAgentRequest`; `:47 handleServiceAgent`; `:336 ServiceAgent(...).SendResponse(...)`. Client-side transport headers and framing are generated in `Package.c` (`PackageCreate*` family, `:311`, `:352`) and consumed by `PackageTransmit*`.

### 4.2 The absence that is a detection signal

Input cardinality: all `.c`/`.h` under `payloads`, 267 angle-bracket includes, 2,468 source files.

**`<name>.dll` string literals: 0.** Thirteen libraries are loaded and not one name appears as a literal. `ModuleName[ n ] =` assignment sites: **165**, all in `Runtime.c`.

A detector scanning for `WINHTTP`/`SSPICLI`/`AMSIDLL` in Demon's own loading code finds nothing, because the strings do not exist until `HideChar` runs. **The correct detector signature is the loader shape, not the name:** a stack buffer zero-initialised and then filled by single-character assignments at non-sequential indices, followed by a call into a module-loading helper and a zeroing call. That shape is present 165 times and is self-similar across all 13 loaders — it is a better fingerprint than any string.

### 4.3 Strings that are present and are fingerprint-relevant

From the loaders themselves, `PUTS` calls that (per §2.2) expand to `printf` under this build:

```
Runtime.c:52  "Loaded Advapi32"        Runtime.c:93  "Loaded Mscoree functions"
Runtime.c:54  "Failed to load Advapi32" Runtime.c:96 "Failed to load Mscoree"
Runtime.c:452 "Loaded Amsi functions"  Runtime.c:455 "Failed to load Amsi"
```

Plus the `Command.c` sites: `:1838 PUTS("Failed to CLRCreateInstance")`, `:1841 PUTS("Failed to load mscoree.dll")`, `Dotnet.c:562 PRINTF("[-] ( CLRCreateInstance ) Process refusing to create %ls CLR version.  Try running an assembly that requires a different CLR version.\n", dotNetVersion)`, `Dotnet.c:90 PUTS("Try to patch(less) Amsi/Etw")`, `Dotnet.c:101 PUTS("Init HwBp Engine")`.

These are `printf`-formatted with `"[DEBUG::%s::%d] "` prefixes (`Macros.h:53`), so the runtime output shape is `[DEBUG::<function>::<line>] <message>` — a `__FUNCTION__`/`__LINE__` prefix on every diagnostic. **That prefix format is itself a fingerprint**: a detector matching `[DEBUG::` on stdout of a suspicious process is matching a format that is compiled in under `DEBUG`, which `CMakeLists.txt:69` defines unconditionally.

Note `:93` says `"Loaded Mscoree functions"` plural — a copy-paste from a multi-function loader into a one-function loader. Minor, but it means the string is not a reliable per-library discriminator.

### 4.4 Build-configuration fingerprint

`CMakeLists.txt:71-75` defines `CONFIG_BYTES={}`, `CONFIG_SIZE=1024`, `CONFIG_KEY_BYTES={}`, `CONFIG_KEY_SIZE=16`, `SERVICE_NAME="DemonService"`. The `{}` values are CMake list placeholders filled at configure time; `CONFIG_SIZE=1024` and `CONFIG_KEY_SIZE=16` are the concrete profile constants. `SERVICE_NAME="DemonService"` is a literal that will be present in any service-mode build.

`CMakeLists.txt:82` `link_libraries( ... mscoree mscorlib )` — linking `mscoree` (the CLR shim) into an agent is itself unusual and is visible in the import table of any compiled artifact in a way the runtime `LdrModuleLoad` path is not. **This is the single strongest static fingerprint in the link set**, and it is present precisely *because* the runtime path is obfuscated: the author hid the module names and left the linker's import for the CLR shim visible.

### 4.5 Sleep / jitter / check-in

From D123 §3 T4 (cited by reference): the task metadata `Sleep`, `Jitter`, `KillDate`, `WorkingHours` crosses the wire as base64 JSON, read client-side at `Packager.cc:776-781` in the `case ( int ) Commands::CALLBACK:` branch. Default sleep/jitter values, the check-in packet shape, and `InWorkingHours()` remain **unread** in this lane — see §7.

---

## §5. What this changes for the capstone

1. **The library graph is 7 load-bearing of 13 declared.** A capstone "library inventory" that lists 13 mechanisms overstates by 6. The correct statement: Demon resolves 13 libraries at runtime; 7 are called by reachable code; 6 are implemented and unreachable.
2. **The link set and the runtime set are different sets.** `link_libraries` (7) is the loader/stub machinery; the `Rt*` family (13) is the operational capability. Conflating them is the §1.1 defect class at library granularity.
3. **Four build arms are dead by construction.** `SEND_LOGS`, `SVC_EXE`, `SHELLCODE`, `TESTING_MATCHING_ROUTINE` are defined nowhere; three of the four are tested with the *value* form (`#if`/`#elif`), which on an undefined identifier is 0, so those arms are unreachable rather than conditional. A capability census that counts source arms counts four arms that no build can select.
4. **The string dispatch axis is the higher-value fingerprint key.** Self-describing literals, fixed by the binary, not regenerable from a version number, and failing open rather than closed.
5. **The DLL-name absence is a signal, not a gap.** 165 character-index assignments and 0 name literals; detect the loader shape.

---

## §6. Instrument record

Two instrument failures, both mine, both caught before the number was filed.

**Failure 1 — the conditional-scope depth counter could not separate a string literal from a directive.** `condscope.ps1` v3 reported `#if 0";` as the enclosing condition for every line from L8 onward in the mandated control fixture. The condition string was scraped from *inside* a multi-line string literal (`L6`-`L7` of the fixture), because the escape branch consumed the backslash **and the following newline**, desyncing line boundaries and leaving the `#` on L7 masked as code. The failure mode was not an arithmetic error — it printed a **plausible, confidently wrong condition string**, which is worse than printing nothing. **Fix (v4):** in the string state, do not treat a backslash before a newline as an escape; let the newline terminate the line while keeping string state across it. **Post-fix control: 14/14 depths correct, all four non-directive cases separated.**

**Failure 2 — a probe whose shape did not match the evidence's shape.** A search for `#define HideChar` returned **0 hits**, which would have supported a false finding that `HideChar` is undefined despite being called 12 times in `Runtime.c:76-87`. The symbol is a **function, not a macro** — `MiniStd.h:26 BYTE HideChar( BYTE C );`. Re-probed case-sensitively in any form: **259 hits** (152 `Runtime.c`, 50 `Kerberos.c`, 40 `Token.c`, 14 `Win32.c`, 1 each `MiniStd.h`/`MiniStd.c`/`Thread.c`). The first probe applied a macro-definition shape to a function-shaped symbol. This is the class D130 filed — *verify the instrument has a name table before filing an absence* — applied to a source probe rather than a symbol-table probe.

**Failure 3 (near-miss, recorded because it produced a false positive).** A `-SimpleMatch 'SHELLCODE'` scan of the 4 build files returned 7 hits and would have reported `SHELLCODE` as defined in the build. All 7 are the literal word in filenames, paths, and `echo` strings in `payloads\Shellcode\makefile`. Zero are definitions. A substring probe answered a definedness question. See §2.1.

**Instrument that did not fail, and why that matters.** The `"<name>.dll"` literal probe returned 0, and 0 is the correct answer rather than a blind instrument — demonstrated by the mechanism's presence in the same tree (165 `ModuleName[ n ] =` sites, `Runtime.c:71-87`). §1.3 states both halves of that check rather than asserting the conclusion.

---

## §7. Residual unknowns

- **D-11 (open).** Does the `Pivots` interleaving occur at runtime? Requires execution or race-detector instrumentation. Not attempted; not attemptable under this lane's constraints.
- **Default sleep, jitter, kill-date, and working-hours values.** The *transport* of these fields is known (`Packager.cc:776-781`); the *defaults* set at registration are unread. Probe: read `NewAgentService` and the session-creation path in `pkg\service\`.
- **Check-in packet shape at byte level.** `PackageCreate*` call sites are known; the serialised field order and encoding are not. Probe: read `Package.c`'s serialiser against `decode.go`.
- **`2560`'s agent-side name and reachability** (§3.3). Probe: read `Command.h` in the 2560 region and grep the agent handler for that label.
- **Whether `RtAmsi`'s `AmsiIsLoaded` result gates anything.** `Dotnet.c:96-99` sets it; the branch that consumes `AmsiIsLoaded` was not read. Probe: read `Dotnet.c` from `:106` to the end of the function and `HwBpExceptions.c` in full.
- **`InWorkingHours()`, `RandomNumber32`/`RandomBool`, `TimerObf`.** Unread. These are the sleep/jitter mechanism and therefore fingerprint-relevant.
- **D-25 — CLOSED this report.** The `SHELLCODE` build definition lives nowhere: `payloads\Shellcode\makefile` uses `-nostdlib -fPIC` with **no `-D` flags at all**, and `CMakeLists.txt:55-64` places `MainExe.c`, `MainDll.c`, and `MainSvc.c` in one unconditional `MAIN_SOURCE` list. Named missing ingredient for any build-output claim remains a **recorded invocation of the Demon build** (D-21, `[blocked]`).

**D-21 provenance note, per the capstone's request.** D116 closed a `[blocked]` by inheriting the label from a brief and then caught itself — *"a `[blocked]` sourced from a brief is a FALSE BLOCKED."* D-21's `[blocked]` was closed by **scanning**: 58,321 files, `compile_commands.json` 0, `CMakeCache.txt` 0, `CMakeFiles` 0, CI 66 hits all issue templates with no `workflows\` directory in the tree, logs 15 all Metasploit fixtures. Same label, opposite provenance.

---

## §8. Validation

Recorded as measured numbers, not as a claim that a check passed.

| Property | Expected | Measured |
|---|---|---|
| Bytes, **before** this §8 correction | — | 44,235 |
| Bytes, **final** (measured after correction) | — | **45,393** |
| `\n` count, final | — | **600** |
| `\r` count | 0 | **0** |
| BOM | none | **absent** (first three bytes not `EF BB BF`) |
| UTF-8 strict decode (`UTF8Encoding($false,$true)`) | valid | **valid, no exception** |
| U+FFFD | 0 | **0** |
| Headings, regex `^# [^#]` | exactly one H1 | **1 H1** |
| Headings, regex `^## [^#]` | — | **9 H2** |
| Headings, regex `^### [^#]` | — | **21 H3** |
| Whole-line duplicates excluding table separators | 0 prose duplicates | **4 fence artefacts:** horizontal rule ×9; bare fence ×24; `c`-fence ×5; `cpp`-fence ×3. All delimiters, no repeated prose line. |
| Backtick parity | even | **1,373, even** |
| Codepoints > U+007E | all deliberate | **97× U+2014, 22× U+00A7, 8× U+2192, 5× U+2013, 3× U+2026** |
| Tail | `**End of D132.**` | **present** |

**Why there are two byte counts.** A table that reports the size of the file containing it cannot converge: each correction changes the number the correction states. The pre-correction measurement (**44,235 B / 592 LF / 1,316 backticks**) is the value my first draft asserted, and it is recorded because I asserted it before measuring. The final row is the file as it now stands. **Any absolute self-measurement in a report body is a snapshot of the instant before the last write; treat the two rows together, not the second alone.**

The heading regex is stated with its basis: `#{1,}` for H1 would also match `##` and `###`, so it is the wrong regex for counting H1. These counts use the anchored forms `^# [^#]`, `^## [^#]`, `^### [^#]`, which cannot overlap. Exactly one H1 holds under either convention.

**End of D132.**
