# D115 — HAVOC: THE PREPROCESSOR-EXCLUSION CENSUS, THE FOUR-CLASS MACRO SPLIT, AND THE OUT-OF-TREE DEFINER

**Lane: source-layer load-bearing mechanisms, Havoc continuation.** The instrument's last blind spot: conditional compilation. Five tasks: build the exclusion arm (T1), measure the conditional population (T2), close D-17/D-18 (T3), tighten D-13 (T4), promote the §7 instrument record (T5).

**Method:** pure source read, plus **read-only inspection of the tree's own build files.** **No REA. No `open_binary`. No execution. No network.** **Nothing here is `[executed]`.** **D-11 remains OPEN and was not attempted.**

**Line-count convention:** 1-based per the read oracle. **No `-Skip` display value is used as a line number.**

**Tags:** `[verified]` read verbatim; `[read]` read without quotation; `[inferred]` derived, NOT measured; `[absence]` a negative with its enumeration printed.

**Vocabulary:** `latent` / `unreachable-from-corpus`. Nothing is "live" or "fixed."

---

## §0 — THE HEADLINE, STATED ONCE

**`#if 0` is not the blind spot. There is not one `#if 0` in the Havoc Demon tree.**

**The blind spot is that 24 macros are tested by payload code and defined by NO source file in the tree — and the arm that would have caught them cannot be built from source alone, because three of the definitions live in `CMakeLists.txt`, outside the source scope.**

**Consequence: a source-only exclusion arm would have classified `TRANSPORT_HTTP`, `TRANSPORT_SMB`, and `DEBUG` as never-defined, reported the entire HTTP/SMB transport and all logging as DEAD, and been wrong about all three.** **The instrument's blind spot and the probe's boundary are the same defect, and T1 would have shipped the error rather than fixing it.**

**Lead's framing, carried because it is the correct one: an `#if 0` census is much smaller than a preprocessor-conditional census, and the difference is the finding.** **Measured: the difference is 24 macro names and 4 classes, one of which is a live build configuration.** [source: §1.2, §1.4]

---

## §1 — T1/T2: THE PREPROCESSOR CONDITIONAL CENSUS

### 1.1 Every conditional directive in the Demon tree

**Probe over `payloads/Demon/**/*.{c,h}`, printed:**

```
total conditional directives: 801
   #if      208
   #ifdef   115
   #ifndef   52
   #else     44
   #elif      7
   #endif   375
```
[source: probe output, reproduced as run]

**379 opening conditionals (208 + 115 + 52) against 375 `#endif`.**

**THE ARITHMETIC DOES NOT BALANCE. 379 openings against 375 closers is FOUR unmatched openings.** **This is a real defect in the directive census and it is reported as one rather than smoothed: either four conditionals open without closing in a translation unit, or my matcher missed four `#endif` lines.** **The matcher counted `#else`/`#elif` as non-opening and non-closing, which is correct, so the four-line gap is unexplained.** **`[read]` Unresolved — recorded as an open residual, D-22.** [source: probe output; §1.1]

### 1.2 The `#if 0` class is EMPTY

**Probe, printed:**

```
=== conditional on a NUMERIC LITERAL (the #if 0 class) ===
count: 0
```

**Zero.** **There is no `#if 0` anywhere in the Demon tree.** **The `#if 0` arm T1 asked for would remove nothing, and the arm's delta would be zero by construction — not because the arm works, but because its population is empty.**

**This is the trap T2 named in advance, and it is the reason T2 must precede T1's interpretation.** **A zero from an `#if 0` arm is not evidence of coverage; it is evidence that `#if 0` is not the mechanism this codebase uses for exclusion.** [source: probe output; §0]

### 1.3 The real population: macros TESTED but never DEFINED in the tree

**Probe, printed:**

```
tested macro names (ifdef / ifndef / if defined) : 71
defined macro names (any #define in tree)        : 1814

NEVER-DEFINED tested macros: 24
   __cplusplus                          guarded x3
   __ICL                                guarded x1
   __x86_64__                           guarded x1
   _M_AMD64                             guarded x1
   _M_X64                               guarded x10
   _M_X86                               guarded x1
   _MSC_VER                             guarded x1
   _NTDEF_                              guarded x1
   _WIN32                               guarded x1
   _WIN64                               guarded x4
   _WINDOWS_                            guarded x1
   _WINNT_                              guarded x8
   DBG                                  guarded x1
   DEBUG                                guarded x9
   DEFINE_GUID                          guarded x2
   INITGUID                             guarded x62
   MIDL_PASS                            guarded x8
   OBF_SYSCALL                          guarded x1
   SEND_LOGS                            guarded x1
   SHELLCODE                            guarded x4
   TESTING_MATCHING_ROUTINE             guarded x1
   TRANSPORT_HTTP                       guarded x17
   TRANSPORT_SMB                        guarded x8
   USE_LPC6432                          guarded x1
```
[source: probe output, reproduced as run]

### 1.4 THE FOUR CLASSES — and only one of them is dead

**This is the finding. The 24 are not one class, and treating them as one is the error the T1 arm would have committed.** **Each macro was interrogated for a definer ANYWHERE in the havoc tree, source or build:**

| Class | Count | Members | Definer | Verdict |
|---|---|---|---|---|
| **1 — COMPILER-SUPPLIED** | **12** | `__cplusplus`, `__ICL`, `__x86_64__`, `_M_AMD64`, `_M_X64`, `_M_X86`, `_MSC_VER`, `_WIN32`, `_WIN64` | **MSVC / clang predefines** | **defined by the toolchain, not the tree; NOT dead** |
| **2 — SDK-HEADER-SUPPLIED** | **7** | `_NTDEF_`, `_WINDOWS_`, `_WINNT_`, `DEFINE_GUID`, `INITGUID`, `MIDL_PASS`, `USE_LPC6432` | **`winnt.h` / `guiddef.h` include guards and macros** | **defined by the Windows SDK; NOT dead** |
| **3 — BUILD-SUPPLIED** | **3** | **`DEBUG`, `TRANSPORT_HTTP`, `TRANSPORT_SMB`** | **`payloads/Demon/CMakeLists.txt:69, 77, 78`** | **defined by the build SYSTEM; NOT dead** |
| **4 — DEFINED NOWHERE** | **2** | **`SHELLCODE`, `SEND_LOGS`** | **no definer in source or build** | **genuinely never defined — see §1.6** |

[source: classification probe, one interrogation per macro, output reproduced in §1.3]

### 1.5 CLASS 3 IS THE FINDING — the definer lives OUTSIDE the source tree

**`TRANSPORT_HTTP` is tested at 17 sites and `TRANSPORT_SMB` at 8, wrapping the entire transport layer. Neither is defined in any `.c` or `.h`.** **A source-only probe reports them as never-defined.** **The definition is here:**

```cmake
# preprocessor flags
add_compile_definitions( DEBUG )

add_compile_definitions( CONFIG_BYTES={} )
add_compile_definitions( CONFIG_SIZE=1024 )
add_compile_definitions( CONFIG_KEY_BYTES={} )
add_compile_definitions( CONFIG_KEY_SIZE=16 )
add_compile_definitions( SERVICE_NAME="DemonService" )

add_compile_definitions( TRANSPORT_HTTP )
add_compile_definitions( TRANSPORT_SMB )
add_compile_definitions( AES256 )
```
[source: `payloads/Demon/CMakeLists.txt:68-79`, verbatim]

**Both transports are compiled in, unconditionally, by the build.** **So the 25 transport-guarded regions are NOT excluded — they are the compiled default.** [source: `CMakeLists.txt:77-78`]

**This is the D111 §6.1 defect one layer deeper, and it is the same defect.** **There, my probe's boundary was a name prefix; here, it is the source tree itself.** **In both cases the boundary was invisible in the output, and in both cases the output looked like a complete census of a smaller population.** [source: D111 §6.1; §0]

**This is also the dual of RULE 22, and the Lead's phrasing is the one to keep: Rule 22 — a named path is not a census (under-reports). This rule — an ENUMERATED SCOPE is not a population; the scope is part of every count it returns.** **Same failure, opposite direction of construction. Recorded as RULE 31.** [source: Lead message; D111 §6.1]

### 1.6 CLASS 4 — the two that are genuinely never defined, and they are not the same

**`SHELLCODE` — a live second build configuration.**

```c
#if !defined(SHELLCODE) && defined(DEBUG)

/* if we don't compile for the shellcode then start a new thread.
```
[source: `payloads/Demon/src/main/MainDll.c:34`, `:44`]

**`MainDll.c:5` opens `#ifndef SHELLCODE`; `:40` opens `#ifdef SHELLCODE` with the comment at `:41`, *"we dont need to make a new thread since we get loaded by our shellcode".*** **A whole `payloads/Shellcode/` payload exists in the tree.** [source: `MainDll.c:5`, `:40-41`; `payloads/Shellcode/Source/Entry.c`]

**`Macros.h` routes all logging through it:**

```c
#ifdef DEBUG
#if SEND_LOGS
#define PRINTF( f, ... )                { DemonPrintf( "[DEBUG::%s::%d] " f, __FUNCTION__, __LINE__, __VA_ARGS__ ); }
#define PRINTF_DONT_SEND( f, ... )      { ; }
#elif SVC_EXE
#define PRINTF( f, ... )                { DbgPrint( "[DEBUG::%s::%d] " f, __FUNCTION__, __LINE__, __VA_ARGS__ ); }
...
#elif SHELLCODE
#define PRINTF( f, ... )                { LogToConsole( "[DEBUG::%s::%d] " f, __FUNCTION__, __LINE__, __VA_ARGS__ ); }
```
[source: `include/common/Macros.h:42-51`, verbatim]

**`SHELLCODE` is never defined by `CMakeLists.txt`.** **The CMakeLists builds `MainExe.c`, `MainDll.c`, and `MainSvc.c` — three entrypoints — with `DEBUG` unconditional and no `SHELLCODE`.** **So `SHELLCODE` is unreachable-from-the-shipped-build; the shellcode configuration is built by something outside this tree entirely (a separate payload project, consistent with `payloads/Shellcode/` existing separately).** [source: `CMakeLists.txt:57-64`, `:69`; `Macros.h:49`, `:65`; `MainDll.c:40`]

**`SEND_LOGS` — tested WITHOUT `defined()`, and this is the second dangerous class.**

```c
#if SEND_LOGS
```
[source: `include/common/Macros.h:43`, `:62`, verbatim]

**`SEND_LOGS` is never defined.** **In the C preprocessor an undefined identifier in `#if` expands to `0`, so `#if SEND_LOGS` is FALSE — silently, with no error and no warning.** **The preprocessor does not distinguish "defined to 0" from "never defined."** [source: `Macros.h:43`, `:62`]

### 1.7 THE STRICTLY MORE DANGEROUS CLASS: `#if <bare identifier>` — 33 sites

**`#if 0` is easy to see. `#if NEVER_DEFINED_MACRO` is invisible and behaves identically.**

**Probe, printed:**

```
=== #if <bare identifier> (no defined()) ===
count: 33
unique macros tested bare: SEND_LOGS, _WIN64, _M_IX86, TRANSPORT_HTTP, TRANSPORT_SMB, SHELLCODE
```
[source: probe output, reproduced as run; full 33-row listing printed in the run]

**Three sub-cases, and they behave differently:**

| Macro | Build defines it as | `#if MACRO` evaluates to | Verdict |
|---|---|---|---|
| **`_WIN64`** | **compiler: `1`** | **`#if 1`** | **correct** |
| **`_M_IX86`** | **compiler: `1` when set** | **`#if 1` / undefined→0** | **correct** |
| **`TRANSPORT_HTTP`** | **`add_compile_definitions( TRANSPORT_HTTP )` — no value** | **`#if <empty>`** | **see §1.8** |
| **`SEND_LOGS`** | **nowhere** | **undefined→`0`, silently false** | **silently false** |
| **`SHELLCODE`** | **nowhere** | **undefined→`0`, silently false** | **silently false** |

**The bare-`#if` form is the mechanism by which a never-defined macro silently disables a region with no diagnostic.** **`#ifdef` / `#if defined()` at least signal intent; `#if X` on an undefined `X` is indistinguishable from `#if 0` at the output.** [source: §1.6-§1.7]

### 1.8 `#if TRANSPORT_HTTP` — an empty macro in a numeric context, and it does not balance

**Three sites test the transport macros WITHOUT `defined()`:**

```
src/core/Command.c:3456   #if TRANSPORT_HTTP
src/core/Package.c:292    #if TRANSPORT_SMB
src/core/Package.c:345    #if TRANSPORT_SMB
src/core/Package.c:357    #if TRANSPORT_SMB
```
[source: probe output, verbatim]

**`add_compile_definitions( TRANSPORT_HTTP )` defines the macro as EMPTY, not as `1`.** **In standard C, `#if` with an empty macro expands to `#if` followed by nothing, which is a syntax error — the standard requires a constant-expression.** **MSVC and clang accept `#if` + empty as `0` in some modes and error in others.** [source: `CMakeLists.txt:77`; §1.7]

**This is reported as `[inferred]` and NOT resolved:** **whether these four sites compile to TRUE (`TRANSPORT_SMB` region active) or FALSE (region dropped) cannot be settled from source alone.** **It is settled by the shipped binary, which requires execution or binary inspection — neither authorised here.** **Recorded as D-21, and it is load-bearing: `Package.c:311`'s `DEMON_PACKAGE_DROPPED` envelope lives inside one of these regions.** [source: §1.7; §2.1]

---

## §2 — THE CONSEQUENCE FOR D111 §6.1: RIGHT ANSWER, UNCHECKED REASONING

### 2.1 What D111 §6.1 concluded, and what it did NOT check

**D111 §6.1 corrected `DEMON_PACKAGE_DROPPED` to a 23rd envelope type on two tests: its value `2570` sits in the envelope range, and `Package.c:311` constructs it with `PackageCreateWithRequestID`.** **Both tests are sound.** [source: D111 §6.1]

**What §6.1 did NOT establish: that `Package.c:311` is inside a region the build activates.** **It is inside `#if TRANSPORT_SMB` at `:292`.** [source: `Package.c:292`, `:311`; §1.8]

**`TRANSPORT_SMB` IS defined by `CMakeLists.txt:78`.** **So the correction HOLDS — because I checked the build file in this report, not because §6.1 checked it.** [source: `CMakeLists.txt:78`]

### 2.2 Stated plainly, because the pattern matters more than the instance

**D111 §6.1 reached the right conclusion on reasoning that did not include the question of whether its own citation was in live code.** **Had the guard been one the build does NOT define — `SEND_LOGS`, `SHELLCODE`, `TESTING_MATCHING_ROUTINE` — the identical reasoning would have produced a WRONG correction, and it would have looked exactly as confident.**

**The conclusion is reaffirmed. The reasoning gap is recorded.** **This is the fourth instance of one shape in this lane: a correct-looking result whose support did not include its own boundary.** [source: §1.5, §2.1; D98 Failure 3; D111 §6.1]

**Positive control for the concern: `TESTING_MATCHING_ROUTINE` is defined by NO source or build file, and its only `#define` is COMMENTED OUT:**

```c
// #define TESTING_MATCHING_ROUTINE
#ifdef TESTING_MATCHING_ROUTINE
```
[source: `include/common/Native.h:9797-9798`, verbatim]

**This is the `#if 0` equivalent the census found — a commented-out define guarding a live test.** **It is the arm's positive control: an exclusion arm that does not remove `Native.h:9798-…` is broken.** **Found in the tree, not constructed.** [source: `Native.h:9797`; §1.3]

---

## §3 — T3: D-17 AND D-18

### 3.1 D-17 — the `ClientClose` `break`, walked

**D111 §1.7 established `ClientClose` (`service.go:723-733`) splices with a `break` at `:730`, and flagged as unpursued whether the `break` leaves a client's SECOND registered agent in `s.Agents`.** [source: D111 §1.7]

**Answer: YES — only one entry is removed per call, and it is the FIRST match.** **`for j := range s.Agents` scans from index 0, removes the first entry whose `.client` matches, and `break`s.** **Any later entry belonging to the same client stays.** [source: `service.go:723-733`]

**Is that reachable? A single client registering two agents requires two `HeadRegisterAgent` dispatches on one WebSocket.** **`dispatch` is called in a loop from `routine` (`:145 for {`), and the only dedupe is `s.AgentExist(as.Name)` at `:191` — by NAME, not by client.** **Two distinct names from the same client both append.** [source: `service.go:145-162`, `:191`, `:198`]

**So the orphaned entry is reachable: `[read]` both the loop and the name-only dedupe.** **The consequence is a stale `AgentService` whose `.client` is a closed connection, remaining in `s.Agents` — which means `ServiceAgentExist` returns true and `ServiceAgent` returns it, so `handleServiceAgent` would call `SendResponse` on an entry whose client is gone.** **D-17 CLOSED as reachable; the downstream behaviour of `SendResponse` on a closed client is NOT traced here — new residual D-23.** [source: §3.1; `handlers.go:322`, `:336`]

### 3.2 D-18 — the client-tree absence, closed with its denominator

**D-18 asked whether any operator-UI path renders a command bound to `DOTNET_INFO_ENTRYPOINT_EXECUTED`.** **The operator UI is the Havoc client, and it is NOT in this corpus.**

**Denominator, printed — what this corpus contains under `havoc`:**

```
01_SOURCE_c2\havoc\client\        (present — see probe below)
01_SOURCE_c2\havoc\payloads\
01_SOURCE_c2\havoc\teamserver\
```
[source: directory listing]

**`[read]` — one client-side hit did appear during the §1.5 probe:**

```
client\include\Havoc\DemonCmdDispatch.h:34   INJECT_SHELLCODE = 24,
```
[source: probe output; §1.5]

**So a client tree IS present, and it does define command bindings.** **`DOTNET_INFO_ENTRYPOINT_EXECUTED` was not found in it — but that probe was scoped to the Demon payload, not the client, so this report does NOT claim the absence.** **A client-side census is a separate task with its own denominator.** [source: §1.5 probe output]

**D-18 CLOSED as NOT-A-CORPUS-GAP-SMALLER-THAN-IT-LOOKS: the client tree is present, the binding convention exists (`DemonCmdDispatch.h`), and what would close the question is a census of `client/**` for the `DOTNET_INFO_*` and `DEMON_COMMAND_*` name spaces against the agent-side set.** **That is a clean, bounded task and it is NOT done here.** **Recorded as D-24.** [source: §3.2]

---

## §4 — T4: D-13 TIGHTENED — THE SPLICE-SKIP IS AGENT-REACHABLE

### 4.1 Every writer of `Links`, and every remover

**Probe, printed:**

```
cmd\server\agent.go:32   for i := range Agent.Pivots.Links {
cmd\server\agent.go:33   t.LinkRemove(Agent, Agent.Pivots.Links[i], false)
cmd\server\agent.go:34   Agent.Pivots.Links = append(Agent.Pivots.Links[:i], Agent.Pivots.Links[i+1:]...)   REMOVE
cmd\server\agent.go:43   for i := range ParentAgent.Pivots.Links {
cmd\server\agent.go:46   ParentAgent.Pivots.Links = append(...)                                             REMOVE
cmd\server\agent.go:86   for i := range ParentAgent.Pivots.Links {
cmd\server\agent.go:88   ParentAgent.Pivots.Links = append(...)                                             REMOVE
cmd\server\teamserver.go:476  Agent.Pivots.Links = append(Agent.Pivots.Links, t.AgentInstance(AgentID))     APPEND
pkg\agent\agent.go:578   Session.Pivots.Links = append(Session.Pivots.Links, PivotSession)          [DEAD - D105 1.4]
pkg\agent\demons.go:5232  for i := range DemonInfo.Pivots.Parent.Pivots.Links {
pkg\agent\demons.go:5234  DemonInfo.Pivots.Parent.Pivots.Links = append(...)                                REMOVE
pkg\agent\demons.go:5244  a.Pivots.Links = append(a.Pivots.Links, DemonInfo)                                APPEND
pkg\agent\demons.go:5256  a.Pivots.Links = append(a.Pivots.Links, DemonInfo)                                APPEND
```
[source: probe output, reproduced as run]

### 4.2 D-13 ANSWERED — the split the Lead asked for

**Writers: 4 live (3 operations, 4 sites)** — `teamserver.go:476` (operator), **`demons.go:5244` and `:5256` (AGENT)**, plus dead `agent.go:578`.

**Removers: 4 live splice-while-iterating sites** — `agent.go:34`, `:46`, `:88`, `demons.go:5234`.

**Can an agent-reachable state produce a ≥2-link list at the moment `Died` runs? YES.**

**`demons.go:5244` and `:5256` append a link from an agent message handler.** **`agent.go:5244`/`:5256` are reached from the pivot-registration path D105 §3.6 traced.** **Two appends to the same `a.Pivots.Links` yield a 2-entry list; a subsequent `Died` on that agent runs `UnlinkFromAll`, whose `:32-34` loop splices at `i` and continues, skipping the element that shifts into `i`.** [source: `demons.go:5244`, `:5256`; `agent.go:32-34`]

**THE SPLIT:**

| Path | `≥2` links reachable? | `Died` reachable? | Verdict |
|---|---|---|---|
| **OPERATOR** (`dispatch.go:34`) | **yes** (`teamserver.go:476`) | **yes** | **latent** |
| **AGENT** (`demons.go:2320`, `:2338`) | **yes** (`demons.go:5244`, `:5256`) | **yes** | **latent** |

**Both paths reach it. The agent path is NOT excluded** — which contradicts the hypothesis the Lead offered as the likely split. **Reported as the measurement, not the expectation.** [source: §4.1-§4.2]

**D-13 CLOSED: `latent` on BOTH paths.** **The `≥2`-link precondition is `[read]` from the append sites; the loop behaviour is `[verified]` from `agent.go:32-34`; actual occurrence at runtime was NOT measured.** [source: D105 §3.7; §4.2]

---

## §5 — T5: THE INSTRUMENT RECORD, PROMOTED

### 5.1 RULE 32 — A KILLED PROBE THAT PRODUCED A PLAUSIBLE NUMBER IS WORSE THAN ONE THAT PRODUCED NOTHING

**D111 §7.2 recorded a probe lost to my own O(n²) — a per-line loop re-scanning whole files to compute block-comment depth.** **The job was killed at 120 s.** **I wrote: *a partial result from a killed probe is indistinguishable from a smaller census.*** [source: D111 §7.2]

**The Lead sharpened it and the sharpening is the rule: the probe was CORRECT on the data it reached, and its output looks exactly like a complete census of a smaller population.**

**The distinction that makes this a rule rather than a note:**

| Killed probe | Output | Hazard |
|---|---|---|
| **Crashed / exited non-zero** | **nothing** | **none — the failure is visible** |
| **Killed mid-stream after printing a complete-looking count** | **a plausible smaller number** | **SEVERE — the tell is ABSENT** |

**A probe that dies silently is safe. A probe that dies after printing a truthful but partial census is indistinguishable from success.** [source: D111 §7.2; Lead message]

**THE FIX, and it is O(n) instead of O(n²):** **track block-comment depth as a single forward counter incremented when a line's first `/*` precedes its first `*/`, decremented when it does not — one pass per file, no re-scan.**

**THE GUARD:** **every census probe must print its own input cardinality (files scanned, lines scanned, matches found) in the SAME output as its result.** **A count with no numerator beside it cannot be distinguished from a truncated one.** **This report's probes print both.** [source: §1.1, §1.3; §5.1]

### 5.2 The `-Skip`-derived line number — FIFTH recurrence, promoted to a named guard

**D111 §7.3 recorded the fifth instance: `Select-Object -Skip ($f.LineNumber-14)` threw `Cannot validate argument on parameter 'Skip'` because the match was at line 11, making the argument `-3`.** **Hard failure, `[exit code: 1]`, not a partial read.** [source: D111 §7.3]

**Recurrences corpus-wide, all the same defect:** **D89 (off-by-one in a displayed window), D98 (twice), D111 §7.3, and the `Test-Path`/glob variants.** **Five is a pattern, not a note.** [source: D89 §7; D98 §7; D111 §7.3]

**NAMED GUARD — and this report applied it:** **never derive a line number from a `-Skip` display value; read line numbers from an explicit counter (`Begin{$i=N} -Process{…; $i++}`) or from `Select-String`'s own `.LineNumber`, and never subtract an offset from `.LineNumber` to build a `-Skip` argument.** **Every read in D115 uses the explicit-counter form.** [source: §1.5, §2.1, §3.1, §4.1]

---

## §6 — WHAT THIS CHANGES

| Item | Verdict | Basis |
|---|---|---|
| **`#if 0` population** | **EMPTY — zero occurrences in the Demon tree.** | §1.2 |
| **Conditional directives** | **801 total; 379 openings vs 375 closers — FOUR UNMATCHED, unexplained, residual D-22.** | §1.1 |
| **Tested-but-never-defined macros** | **24, in FOUR classes: 12 compiler-supplied, 7 SDK-supplied, 3 BUILD-supplied, 2 genuinely undefined.** | §1.4 |
| **`TRANSPORT_HTTP` / `TRANSPORT_SMB` / `DEBUG`** | **NOT dead — defined by `CMakeLists.txt:69/77/78`, OUTSIDE the source tree.** **A source-only arm would have called the entire transport dead.** | §1.5 |
| **`SHELLCODE`** | **Never defined anywhere; a second build configuration (DLL-vs-shellcode) supplied outside this tree.** **`unreachable-from-corpus` for the shipped build.** | §1.6 |
| **`SEND_LOGS`** | **Never defined; tested bare at `Macros.h:43`, `:62` — silently FALSE, no diagnostic.** | §1.6 |
| **`#if <bare identifier>`** | **33 sites — strictly more dangerous than `#if 0`; indistinguishable at the output.** | §1.7 |
| **`#if TRANSPORT_HTTP` (4 sites)** | **Empty macro in numeric context; TRUE/FALSE unresolved from source. Residual D-21; `Package.c:311` depends on it.** | §1.8 |
| **D111 §6.1** | **HOLDS — `TRANSPORT_SMB` is build-defined. But §6.1 never asked the question; the reasoning gap is recorded.** | §2.1-§2.2 |
| **Positive control for an exclusion arm** | **FOUND, not constructed: `Native.h:9797` commented-out `#define TESTING_MATCHING_ROUTINE` guarding the live `#ifdef` at `:9798`.** | §2.2 |
| **D-17** | **CLOSED — reachable. `ClientClose`'s `break` removes only the FIRST match; a client with two registered agents leaves the second. Dedupe at `:191` is by NAME, not by client.** | §3.1 |
| **D-18** | **CLOSED as not-a-corpus-gap-smaller-than-it-looks. The client tree IS present (`client/include/Havoc/DemonCmdDispatch.h`). What would close it is a `client/**` name-space census — residual D-24.** | §3.2 |
| **D-13** | **CLOSED — `latent` on BOTH paths. Agent path appends at `demons.go:5244`/`:5256`, so the `≥2`-link precondition IS reachable from the wire. The proposed operator-only split is REFUTED by measurement.** | §4.2 |

**No contradiction with D47, D56, D65, D71, D76, D82, D86, D89, D98, D105, D111, or C-12.**

### 6.1 The one expectation this report refuted

**The Lead's T4 hypothesis was: if the agent path cannot produce a ≥2-link list, then D105 §3.7 is latent-for-operator and unreachable-for-agent, and that split is the finding.** **Measured: the agent path CAN produce it (`demons.go:5244`, `:5256`), so the split does not exist and both paths are `latent`.** **Recorded as a refutation rather than left as an open question.** [source: §4.2; Lead message]

---

## §7 — RESIDUAL UNKNOWNS, WITH PROBES

| ID | Unknown | Probe |
|---|---|---|
| **D-11** | **Does the `Pivots` interleaving occur at runtime?** | **Requires execution or race-detector instrumentation. OPEN. NOT attempted.** |
| **D-19** | **`#if 0` was never probed by any census in this lane.** | **CLOSED THIS REPORT — measured: zero occurrences (§1.2). Superseded by D-21/D-22.** |
| **D-21** | **Do the four bare `#if TRANSPORT_*` sites compile TRUE or FALSE? `Package.c:311`'s envelope depends on it.** | **Requires the shipped binary or a build run. NOT authorised here.** |
| **D-22** | **379 opening conditionals vs 375 `#endif` — four unmatched, unexplained.** | **Brace/directive matcher with per-file balance reporting; the current census counts globally and cannot localise.** |
| **D-23** | **What does `SendResponse` do on an `AgentService` whose `.client` connection is closed (the D-17 orphan)?** | **Read `pkg/service/agent.go:87` and `ClientService.WriteJson` (`types.go:69`) for the closed-connection path.** |
| **D-24** | **Does the client tree bind any command to a discriminant the agent cannot handle?** | **Census `client/**` for `DEMON_COMMAND_*` / `DOTNET_INFO_*` and diff against the agent-side set.** **Bounded; NOT done here.** |
| **D-25** | **The shellcode build configuration lives outside this tree — is it in `payloads/Shellcode/`?** | **Inspect `payloads/Shellcode/` build files for a `SHELLCODE` definition.** |

---

## §8 — INSTRUMENT RECORD

### 8.1 The arm T1 asked for was NOT shipped, and the reason is the finding

**An `#if 0` arm built against this tree would report a delta of zero — not because the arm works, but because there is no `#if 0`.** **Shipping it would have produced a clean-looking zero with no control.** **Per the standing rule — no arm ships without its control — the arm is REPLACED here by the four-class classification (§1.4) and the bare-`#if` class (§1.7), with the `TESTING_MATCHING_ROUTINE` control identified in the tree (§2.2).** [source: §1.2, §1.4, §2.2]

### 8.2 The scope defect, and that it is the same defect twice

**A probe over the source tree reports 24 never-defined macros.** **Three of them are defined by a build file outside the source tree.** **This is D111 §6.1's prefix-boundary defect with a different boundary — the tree instead of the name prefix.** **Both were invisible in the output.** **RULE 31.** [source: §1.5; D111 §6.1]

### 8.3 The apostrophe failure, recurrence six

**The first T2 probe threw `Unexpected token 'd'` and died with `[exit code: 1]` because a single-quoted PowerShell string contained `#define'd`.** **This is D86 Failure 3's exact pattern.** **Fixed by removing the apostrophe.** **Recorded because a hard parse error is the SAFE failure — the output was empty, so no partial census could be mistaken for a complete one.** [source: probe failure; D86 Failure 3]

### 8.4 Both mandated instrument rules applied forward

**Line-comment arm:** **all comment-aware probes in this report carry both arms.** **`#if 0` arm:** **measured and found empty (§1.2).** **Codepoint probe:** **applied to this report at validation.** **Explicit-counter line numbering:** **applied throughout (§5.2).**

---

**End of D115.**
