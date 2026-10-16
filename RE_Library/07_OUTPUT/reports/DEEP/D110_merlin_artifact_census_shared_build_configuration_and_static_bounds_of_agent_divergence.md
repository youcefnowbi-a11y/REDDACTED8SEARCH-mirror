# D110 — Merlin artifact census, the shared build configuration across platforms, and the static bounds of the agent build divergence

**Scope:** target T8, `RE_Library\05_TARGETS\merlin_extracted\` + `RE_Library\02_BINARIES\` + `RE_Library\07_OUTPUT\extractions\`. Round 25.
**Line-count convention:** LF count = `([regex]::Matches($text,"`+"`"+`n")).Count` over `[IO.File]::ReadAllText`. A final line without a trailing newline is **not** counted.
**Tags:** `[verified]` instrument run with output shown · `[read]` quoted from an artifact read directly · `[inferred]` reasoning over evidence · `[absence]` probe returned zero with a positive control.
**Discipline:** **no corpus binary was executed.** No Ghidra run was performed and none was needed — T1 is enumeration, T2/T4 are string-blob reads, T3 is PE structure arithmetic. **No new toolchain failures**, which is not evidence C-08's seven are fixed.
**Write scope:** this report. `_d110_*` in `binlayer\` — **0 created**; staging went to `%TEMP%` and stays there.
**Occupancy:** `D110*` enumerated → **0 matches** before writing.
**Host note:** the running environment is a delegated subagent with `danger-full-access` file policy; no approval escalation was requested or needed.

---

## §0 Headlines

`[verified]` **1. The Merlin binary population is 16 distinct artifacts, not 26 — every one present exactly twice.** A full byte-level census of all three roots found **32 binary-class file entries collapsing to 16 unique SHA-256 values**, because `07_OUTPUT\extractions\T8\extracted\` is a **byte-identical re-extraction** of `05_TARGETS\merlin_extracted\`. **All 16 hashes match pairwise.** The duplicated tree is a copy, not a second population.

`[verified]` **2. ALL SEVEN agent builds carry a byte-identical build configuration — except the Windows release.** Two and only two config strings exist across seven agent binaries:
- **`64E8E9BA653B71B2`, 699 bytes — SIX of seven builds:** all five non-Windows agents **plus the Windows Debug agent.**
- **`B2DFB420DA59BC19`, 713 bytes — the Windows release agent alone.**

`[verified]` **The delta is exactly 14 bytes = ` -H=windowsgui`,** verified by length arithmetic (713 − 699 = 14) and by direct substring diff.

`[verified]` **3. The Linux and Darwin agents ship a WINDOWS user-agent string.** `Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 … Chrome/40.0.2214.85 Safari/537.36` appears literally in `merlinAgent-Linux-x64` and `merlinAgent-Darwin-arm64` (confirmed by direct match, both `True`). `[inferred]` **The user-agent is a build-time constant applied uniformly, not a platform-aware default.**

`[verified]` **4. The two Windows builds differ by 1,666 bytes out of 13,939,200 — 0.0120% — and the difference is NOT code.** `.pdata` and `.xdata` differ by **zero bytes**; the entry-point code region is **byte-identical for its first 512 bytes**; `.text` differs by **80 bytes (0.0013%)**. **The only meaningful divergence is `.rdata` (1,375 bytes), which is where Go string literals live.**

`[verified]` **5. All seven binaries were cross-compiled on GitHub-hosted LINUX runners.** `GOOS=windows` and `GOOS=darwin` artifacts both carry `/opt/hostedtoolcache/go/1.27.2/` and `/home/runner/…` build roots. **No macOS or Windows build machine was involved for any artifact.**

---

## §1 T1 — THE CENSUS OF MERLIN ARTIFACTS

`[verified]` **Method: enumerate by DIRECTORY walk and by MAGIC BYTES, never by name pattern or extension.** Extension-first enumeration was run and is reported in §1.1 precisely because it is misleading.

### §1.1 Why extension-based inventory fails here

`[verified]` Enumeration of the three roots by extension:

| root | total files | notable |
|---|---:|---|
| `05_TARGETS\merlin_extracted` | 89 | `.json` 63 · **`<none>` 11** · `.MD` 7 · `.exe` 4 · `.dll` 2 · `.c` 1 · `.def` 1 |
| `02_BINARIES` | 4 | `.exe` 1 · `.minisig` 1 · `.md` 1 · `.7z` 1 |
| `07_OUTPUT\extractions` | 9,722 | `.java` 4,164 · `.smali` 2,472 · `.xml` 1,221 · … · **`.exe` 4** · `.dll` 2 |

`[inferred]` **Eleven extension-less files in `merlin_extracted` are the Mach-O and ELF agents and CLIs.** `[inferred]` **An `.exe`-based inventory finds 4 Windows binaries and silently misses 10 cross-platform ones — the same class of error as C-08 §9's omitted CLI set, one level deeper.** `[inferred]` **Extension is not a classification; magic bytes are.**

### §1.2 Magic-byte classification

`[verified]` Path-matching `merlin` (case-insensitive) across all three roots returned **115 file rows.** Classified by **first 4 bytes**, not by name:

| magic class | rows |
|---|---:|
| `PE` (`4D 5A`) | **12** |
| `ELF` (`7F 45 4C 46`) | **12** |
| `Mach-O` | **8** |
| text / other | 83 |

`[verified]` **Binary-class rows: 32. DISTINCT BY SHA-256: 16.** Every binary appears exactly twice.

### §1.3 The 16 distinct artifacts

`[verified]` Canonical root `05_TARGETS\merlin_extracted\`; the twin path is `07_OUTPUT\extractions\T8\extracted\` with an **identical SHA-256** in every case.

| # | class | bytes | SHA-256 (first 16) | artifact |
|---:|---|---:|---|---|
| 1 | Mach-O | 11,808,210 | `43E8E7BFD4B464F3` | `merlinAgent-Darwin-arm64` |
| 2 | Mach-O | 12,761,408 | `389E7DDCD92DEFFC` | `merlinAgent-Darwin-x64` |
| 3 | ELF | 12,124,284 | `FA7E842A0FC2D84A` | `merlinAgent-Linux-arm` |
| 4 | ELF | 11,534,460 | `7096E97239F78CB4` | `merlinAgent-Linux-arm64` |
| 5 | ELF | 12,492,924 | `B418F8BABC9E1AED` | `merlinAgent-Linux-x64` |
| 6 | PE | 13,939,200 | `E9501A7F32595059` | `merlinAgent-Windows-x64.exe` |
| 7 | PE | 13,939,200 | `F12C1B24C4A700F0` | `merlinAgent-Windows-x64-Debug.exe` |
| 8 | Mach-O | 19,571,874 | `5CD894F045EFC4D5` | `merlinCLI-Darwin-arm64` |
| 9 | Mach-O | 20,804,192 | `E478582720F2FA60` | `merlinCLI-Darwin-x64` |
| 10 | ELF | 19,183,912 | `377E7ABA5548AF4C` | `merlinCLI-Linux-arm` |
| 11 | ELF | 19,017,586 | `9838978D09D88791` | `merlinCLI-Linux-arm64` |
| 12 | ELF | 20,299,557 | `84D6D42D62DC0114` | `merlinCLI-Linux-x64` |
| 13 | PE | 20,754,432 | `81CE444B01F28960` | `merlinCLI-Windows-x64.exe` |
| 14 | PE | 14,687,006 | `5242B9D5A2777DF5` | `merlin.x86.dll` |
| 15 | PE | 15,145,760 | `131941097BD1402B` | `merlin.x64.dll` |
| 16 | PE | 26,329,600 | `054EECE65FD58637` | `merlinServer-Windows-x64.exe` |

`[verified]` **Composition: 6 agents · 6 CLIs · 2 DLLs · 1 server · 1 additional agent (Windows Debug) = 16.**

### §1.4 THE DEFINITIVE ANSWER — how many exist, how many are unanalysed

`[verified]` **A symbol-table dump exists for exactly 7 artifacts, and one of those is NOT Merlin.**

| dump | program |
|---|---|
| `C-01_merlin.x86.dll.ghidra-symbols.tsv` | `merlin.x86.dll` |
| `C-02_merlinServer-Windows-x64.exe.ghidra-symbols.tsv` | `merlinServer-Windows-x64.exe` |
| `C-03_merlinCLI-Windows-x64.exe.ghidra-symbols.tsv` | `merlinCLI-Windows-x64.exe` |
| `C-04_merlin.x64.dll.ghidra-symbols.tsv` | `merlin.x64.dll` |
| `C-05_merlinAgent-Windows-x64.exe.ghidra-symbols.tsv` | `merlinAgent-Windows-x64.exe` |
| `C-06_merlinAgent-Windows-x64-Debug.exe.ghidra-symbols.tsv` | `merlinAgent-Windows-x64-Debug.exe` |
| **`C-07_sliver-client_windows-amd64.ghidra-symbols.tsv`** | **`sliver-client_windows-amd64.exe` — NOT Merlin** |

`[verified]` **THE CENSUS:**

| | count |
|---|---:|
| Distinct Merlin binary artifacts in corpus | **16** |
| With a Ghidra symbol dump | **6** |
| **UNANALYSED at the symbol layer** | **10** |
| With a `.strings.txt` dump | **5** (all Windows) |
| **Without a `.strings.txt` dump** | **11** |

`[verified]` **UNANALYSED — the ten, by name:**

```
merlinAgent-Darwin-arm64        merlinAgent-Darwin-x64
merlinAgent-Linux-arm           merlinAgent-Linux-arm64
merlinAgent-Linux-x64           merlinCLI-Darwin-arm64
merlinCLI-Darwin-x64            merlinCLI-Linux-arm
merlinCLI-Linux-arm64           merlinCLI-Linux-x64
```

`[inferred]` **The symbol-layer coverage rate is 6/16 = 37.5%.** `[inferred]` **The 10 unanalysed artifacts are every Mach-O and every ELF in the corpus — 100% of the cross-platform surface, 0% of it analysed.** `[inferred]` **This is not an oversight of the agent set alone: it is a total gap for each non-PE format.**

`[inferred]` **C-07's presence in the `C-0x` numbering is itself a census defect worth noting:** the sequence `C-01…C-07` reads as a contiguous Merlin artifact series, but **`C-07` is a Sliver binary.** `[inferred]` **A reader counting `C-0x` dumps would conclude 7 Merlin artifacts are analysed; the true figure is 6 — the same off-by-name population error, now inside the output layer rather than the target layer.**

### §1.5 §1.6 The archive and the non-Merlin neighbor

`[verified]` `02_BINARIES\` contains exactly four files, enumerated directly by `[IO.Directory]::GetFiles`:

| bytes | name |
|---:|---|
| 307 | `README.md` |
| **68,780,065** | **`merlinServer-Windows-x64.7z`** |
| 65,866,240 | `sliver-client_windows-amd64.exe` |
| 326 | `sliver-client_windows-amd64.exe.minisig` |

`[inferred]` **The `.7z` is the distribution archive the extraction came from — the provenance link between `02_BINARIES\` and `05_TARGETS\merlin_extracted\`, which no prior lane had drawn.** `[inferred]` **It is not itself an analysed artifact and must not enter a Merlin binary count.** `[inferred]` **`sliver-client_windows-amd64.exe` at 65,866,240 B matches C-08 §9's figure exactly, confirming C-08's number — and it is a different tool, correctly excluded from a Merlin census.**

`[inferred]` **NOTE — D96 lane boundary.** `binlayer\` contains `_d96_pclntab.ps1` (2,922 B) and `_d96_pclntab.tsv` (4,243,244 B), i.e. **another lane is attacking the pclntab symbol-recovery problem that C-08 §6's dead Go analyzers created.** `[inferred]` **D110 does not enter that lane.** It is recorded here so the Lead can reconcile the two: if pclntab recovery succeeds, §1.4's "unanalysed 10" may be reducible **without** Ghidra.

---

## §2 T2 — THE BUILD CONFIGURATION ACROSS PLATFORMS

`[verified]` **Method: strings recovered by DIRECT BYTE READ from the five non-Windows agents — no Ghidra, no `.strings.txt`.** A `[IO.File]::ReadAllBytes` pass keeping printable runs of length ≥ 8. **No corpus binary executed.**

`[verified]` **Strings recovered:**

| agent | bytes | strings (≥8) |
|---|---:|---:|
| `merlinAgent-Darwin-arm64` | 11,808,210 | 29,103 |
| `merlinAgent-Darwin-x64` | 12,761,408 | 29,941 |
| `merlinAgent-Linux-arm` | 12,124,284 | 28,554 |
| `merlinAgent-Linux-arm64` | 11,534,460 | 28,830 |
| `merlinAgent-Linux-x64` | 12,492,924 | 29,661 |

### §2.1 THE CONFIG IS SHARED — and the exact partition

`[verified]` **SHA-256 of the recovered `-ldflags` string, all seven agent builds:**

| agent | SHA-256(cfg) first 16 | len |
|---|---|---:|
| `merlinAgent-Darwin-arm64` | `64E8E9BA653B71B2` | 699 |
| `merlinAgent-Darwin-x64` | `64E8E9BA653B71B2` | 699 |
| `merlinAgent-Linux-arm` | `64E8E9BA653B71B2` | 699 |
| `merlinAgent-Linux-arm64` | `64E8E9BA653B71B2` | 699 |
| `merlinAgent-Linux-x64` | `64E8E9BA653B71B2` | 699 |
| `merlinAgent-Windows-x64-Debug.exe` | `64E8E9BA653B71B2` | 699 |
| **`merlinAgent-Windows-x64.exe`** | **`B2DFB420DA59BC19`** | **713** |

`[verified]` **Distinct config strings across all 7 builds: 2.**

`[verified]` **The complete 713-byte Windows-release config, verbatim:**

```
-ldflags="-s -w
 -X "main.auth=opaque" -X "main.addr=127.0.0.1:4444" -X "main.transforms=jwe,gob-base"
 -X "main.listener=" -X "github.com/Ne0nd0g/merlin-agent/v2/core.Build=e68a5e810cbd269622b5617ae8cd5c22c6b82005"
 -X "main.protocol=h2" -X "main.url=https://127.0.0.1:443" -X "main.host=" -X "main.httpClient=go"
 -X "main.psk=merlin" -X "main.secure=false" -X "main.sleep=30s" -X "main.proxy="
 -X "main.useragent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36"
 -X "main.headers=" -X "main.skew=3000" -X "main.padding=4096" -X "main.killdate=0"
 -X "main.maxretry=7" -X "main.parrot=" -H=windowsgui -buildid="
```

### §2.2 THE ANSWER TO "same config, or different per-platform defaults?"

`[verified]` **SAME. Identical on every platform. The `.strings.txt` for the five non-Windows agents does not exist and was not needed — the config is in the binary as a literal.**

`[verified]` **`psk=merlin`, `auth=opaque`, `protocol=h2`, `url=https://127.0.0.1:443`, `addr=127.0.0.1:4444`, `transforms=jwe,gob-base`, `sleep=30s`, `skew=3000`, `padding=4096`, `killdate=0`, `maxretry=7`, `secure=false`, `httpClient=go`, and build hash `e68a5e810cbd269622b5617ae8cd5c22c6b82005` — literally the same characters in all seven builds.**

`[inferred]` **CHALLENGE TO THE TASK'S HYPOTHESIS, STATED PLAINLY.** `[inferred]` **The task anticipated that a per-platform divergence would be the finding — "if the Linux agents use a different protocol or a different sleep, that is a finding."** `[inferred]` **They do not. There is no per-platform default divergence in the build configuration at all.** `[inferred]` **The finding is the REFUTATION: the configuration is uniformly applied by a single build matrix, and platform is not a configuration axis.**

`[inferred]` **The single genuine configuration axis is `-H=windowsgui`, and it separates exactly one binary from the other six.** `[inferred]` **It is a PE-specific linker flag; it is meaningless for Mach-O and ELF, which is why the five non-Windows builds share the Debug build's config — the Debug build is simply "the config without the PE-subsystem flag."**

### §2.3 The Windows user-agent on Linux and Darwin builds

`[verified]` **Direct substring match for `Windows NT 6.1` against the recovered strings:**

```
merlinAgent-Linux-x64    contains 'Windows NT 6.1': True
merlinAgent-Darwin-arm64 contains 'Windows NT 6.1': True
```

`[inferred]` **A Linux agent that announces itself as `Windows NT 6.1` is a high-fidelity, platform-independent detection signature.** `[inferred]` **It also means the default user-agent was never intended as camouflage matched to the implant host — it is a build-time constant in `main.useragent`, set once in the build matrix and applied to every target.**

### §2.4 Platform-specific CODE — the divergence the config cannot show

`[verified]` The shared config does **not** mean shared code. Package-level probes:

| probe | Darwin-arm64 | Darwin-x64 | Linux-arm | Linux-arm64 | Linux-x64 |
|---|:--:|:--:|:--:|:--:|:--:|
| `golang.org/x/sys/unix` | ● | ● | ● | ● | ● |
| `internal/syscall/unix` | ● | ● | ● | ● | ● |
| `darwin` | ● | ● | | | |
| `linux` | ● | ● | ● | ● | ● |
| `kqueue` | ● | ● | ● | ● | ● |
| `epoll` | ● | ● | ● | ● | ● |
| `mach_` | ● | ● | | | |
| `/proc/` | | | ● | ● | ● |
| `SECCOMP` | | | ● | ● | ● |
| `ptrace` | ● | ● | ● | ● | ● |

`[inferred]` **Real per-OS compilation is confirmed:** the Darwin builds carry `mach_` and `darwin` symbols absent from Linux; the Linux builds carry `SECCOMP` and `/proc/` absent from Darwin. `[inferred]` **`kqueue`, `epoll`, `golang.org/x/sys/unix` and `ptrace` appear in both — expected, since Go's runtime and `x/sys` carry both code paths in one build's dependency graph.** `[inferred]` **The `linux` token appearing in Darwin builds is a substring artifact of unrelated identifiers, not evidence of Linux code — recorded as a limitation of substring probing.**

### §2.5 The dependency manifest — 20 modules

`[verified]` **Union of `module@version` across all seven builds, with per-build presence:**

| module@version | builds |
|---|---:|
| `github.com/andybalholm/brotli@v1.2.6` | 7 |
| `github.com/armon/go-socks5@v0.0.0-20160902184237-e75332964ef5` | 7 |
| **`github.com/awgh/rawreader@v0.0.0-20200626064944-56820a9c6da4`** | **2** |
| `github.com/cretz/gopaque@v0.1.0` | 7 |
| `github.com/fatih/color@v1.19.0` | 7 |
| `github.com/go-jose/go-jose/v3@v3.0.5` | 7 |
| `github.com/google/shlex@v0.0.0-20191202100458-e7afc7fbc510` | 7 |
| `github.com/google/uuid@v1.6.0` | 7 |
| `github.com/klauspost/compress@v1.20.1` | 7 |
| `github.com/mattn/go-colorable@v0.1.15` | **7** |
| `github.com/mattn/go-isatty@v0.0.24` | 7 |
| `github.com/quic-go/qpack@v0.6.0` | 7 |
| `github.com/quic-go/quic-go@v0.63.0` | 7 |
| `github.com/refraction-networking/utls@v1.8.2` | 7 |
| `go.dedis.ch/fixbuf@v1.0.3` | 7 |
| `go.dedis.ch/kyber/v3@v3.1.0` | 7 |
| `golang.org/x/crypto@v0.57.0` | 7 |
| `golang.org/x/net@v0.60.0` | 7 |
| `golang.org/x/sys@v0.48.0` | 7 |
| `golang.org/x/text@v0.42.0` | 7 |

`[inferred]` **18 of 20 present in all seven builds.** `[inferred]` **ONE module appears in only 2 builds — `awgh/rawreader` (Windows process-memory reading).** `[verified]` **MEASURED, and it corrects an earlier inference in this report's own drafting:** a first pass put `mattn/go-colorable` at 2 builds; a direct substring search against all seven recovered string sets returns **7 of 7**. `[inferred]` **The first pass matched the `module@version` form, which a module referenced without a version suffix in some builds escapes — an extraction-granularity artifact, the same class as the §5 path-flood probe failure.** `[inferred]` **The corrected figure is 18/20 universal, exactly one build-conditional module, and that one is Windows-only.**

`[inferred]` **The cryptographic stack is named and versioned: `go.dedis.ch/kyber/v3 v3.1.0` + `fixbuf v1.0.3` (OPAQUE PAKE), `google/go-jose v3.0.5` (JWE transforms), `golang.org/x/crypto v0.57.0`, and `refraction-networking/utls v1.8.2` (TLS fingerprint impersonation).** `[inferred]` **`utls` is present in all seven — the agent impersonates a browser TLS stack, which pairs with the Chrome 40 user-agent.**

---

## §3 T3 — THE UNTESTED BEHAVIOURAL DIVERGENCE

`[verified]` **Method: PE structure arithmetic only. No execution. No debugger. No dynamic analysis.**

### §3.1 What `-H=windowsgui` actually writes

`[verified]` Optional-header fields of the two Windows agents:

| field | release | Debug | differs |
|---|---|---|---|
| `Magic` | `0x020B` (PE32+) | `0x020B` | no |
| `AddressOfEntryPoint` | `0x0008ACA0` | `0x0008ACA0` | **no** |
| `ImageBase` | `1` | `1` | no |
| **`Subsystem`** | **2 (WINDOWS_GUI)** | **3 (WINDOWS_CONSOLE)** | **YES** |
| `DllCharacteristics` | `0x8160` | `0x8160` | no |
| `SizeOfImage` | `0x2DAD000` | `0x2DAD000` | no |
| `CheckSum` | `0` | `0` | no |
| `NumberOfSections` | 8 | 8 | no |
| entry-point section | `.text` | `.text` | no |

`[verified]` **`Subsystem` is the ONLY differing header field.** `[inferred]` **`-H=windowsgui` writes exactly one field and nothing else. It is a one-field change, and the entry point is not even moved.**

### §3.2 Whole-file divergence

`[verified]` **Section-by-section differing-byte counts:**

| section | size (both) | differing | % | 
|---|---:|---:|---:|
| `.text` | 6,180,864 | **80** | 0.0013% |
| `.rdata` | 6,295,040 | **1,375** | 0.0218% |
| `.data` | 1,206,784 | **211** | 0.0175% |
| **`.pdata`** | 130,560 | **0** | **0.0000%** |
| **`.xdata`** | 512 | **0** | **0.0000%** |
| **TOTAL** | 13,813,760 | **1,666** | **0.0121%** |

`[verified]` **`.pdata` (exception unwind data) and `.xdata` differ by ZERO bytes.** `[inferred]` **Exception unwind tables are generated from code structure. If the code differed, these would differ. They do not.** `[inferred]` **This is strong static evidence that the compiled instruction stream is unchanged.**

### §3.3 The `.text` divergence is a RELOCATION, not code

`[verified]` `.text` has **identical size** in both builds and differs by **80 bytes across 77 runs.** **74 runs are single bytes, and every single one has the SAME delta:**

```
delta histogram: +0xF0 (240) -> 74 occurrences
```

`[verified]` **`+0xF0` unsigned = `-0x10` signed. Exactly one delta value, 74 times.**

`[verified]` **The 3 remaining runs are 2 bytes each, and all three decode as little-endian 16-bit values differing by EXACTLY −16:**

| `.text` offset | release (LE u16) | Debug (LE u16) | delta |
|---|---|---|---|
| `0x215B90` | `0x6E0C` | `0x6DFC` | **−16** |
| `0x215D9C` | `0x6C00` | `0x6BF0` | **−16** |
| `0x5A5491` | `0x750B` | `0x74FB` | **−16** |

`[inferred]` **A borrow-carry pattern: low byte −0x10, high byte −1 where the 16-bit value crosses a 0x10 boundary. This is the signature of a 16-bit address being adjusted by a constant, not of different source code.** `[inferred]` **77 differing runs, one delta value, three of them exactly 16 apart as 16-bit quantities — that is address fixup, not logic.**

`[verified]` **The strongest single check: the entry-point code region is byte-identical for its first 512 bytes** (`0x8ACA0..0x8ACA0+512`, **0 differing bytes**). `[inferred]` **The function the loader executes first is the same code in both binaries.**

`[verified]` **The only meaningful region is `.rdata` (1,375 bytes, 784 short runs). The largest runs are the Go build-info block and the ldflags string:**

```
off=0x0651B9 len=115   .build.-tags=-trimpath.build.CGO_ENABLED=0.build.GOARCH
off=0x064F10 len= 38   opaque\" -X \"main.addr=127.0.0.1:4444
off=0x0651A3 len= 21   H=windowsgui -buildid
```

`[verified]` **`-H=windowsgui` is at `.rdata` offset `0x651A2`; `main.psk=merlin` at `0x65040`.** `[inferred]` **`.rdata` is Go's string-literal and read-only-data region. The 1,375 differing bytes are string-table content and the address fixups that point into it — the *consequence* of removing a 14-byte string, propagated across the build-info references.**

### §3.4 THE ANSWER — what is settleable, and what is not

`[verified]` **SETTLEABLE FROM STATIC BYTES:**

1. **`-H=windowsgui` changes exactly one PE header field: `Subsystem`, 2 → 3.** No entry point, no image base, no characteristics, no section layout.
2. **The compiled code is unchanged.** `.pdata` 0 · `.xdata` 0 · entry-point first 512 bytes 0 · `.text` 80 bytes all at a single constant delta of −16 consistent with address fixup.
3. **The total divergence is 0.0120% of the file, confined to string data and its fixups.**
4. **`-tags=-trimpath` and `CGO_ENABLED=0` are IDENTICAL in both builds** — the build tags are not the difference.
5. **Console API imports are present in BOTH builds identically**: `AllocConsole`, `GetConsoleWindow`, `WriteConsole`, `GetStdHandle`, `SetConsoleCtrlHandler`, `GetConsoleMode`, `MessageBox`, `ShowWindow`, `ShellExecute` all present in each. `[inferred]` **These come from the shared Go runtime and `mattn/go-colorable`; their presence is not evidence of USE.**
6. **`log.Fatal` is present in both.**

`[verified]` **NOT SETTLEABLE FROM STATIC BYTES — requires execution, and therefore was NOT done:**

1. **Whether the GUI subsystem suppresses a console window at runtime for a process that never allocates one.** `[inferred]` **The loader's behaviour — no console allocated for a subsystem-2 process — is an operating-system policy, not a byte in the file.** `[inferred]` **This is the core of the divergence and it is genuinely outside static reach.**
2. **Whether `AllocConsole` is ever CALLED.** `[inferred]` **Import presence is not call presence; resolving the call sites requires disassembly of 6.1 MB of `.text` and the Go analyzer that C-08 §6 records as dead on Go 1.27.2.** `[inferred]` **The bound is inherited, not new.**
3. **Whether injection output (`ExecuteShellcode*` error strings) is surfaced anywhere observable.** `[inferred]` **The strings exist in both builds; whether either writes them to a handle that exists is a runtime question.**
4. **Whether the GUI-subsystem build is more or less detectable in memory.** `[inferred]` **Static bytes cannot answer this.**

`[inferred]` **THE HONEST BOUND, stated as the task asked:** `[inferred]` **The static evidence says the two builds are THE SAME PROGRAM with one PE header field flipped.** `[inferred]` **The observable divergence is therefore entirely at the loader/OS layer: a subsystem-2 process does not get a console, a subsystem-3 process does.** `[inferred]` **For an implant that is not supposed to be seen, that is the operationally meaningful difference — and it is a real one despite the code being identical, because "does a black window appear when this runs" is answered by the loader, not by the code.** `[inferred]` **It also means the `-Debug` name is doubly misleading: it is not a debug-symbol build (§D95) and it is not a differently-compiled build (§here). It is the portable config with the console subsystem left on.**

### §3.5 Build-info block — a bonus discovery from the T3 diff

`[verified]` The `.rdata` divergence exposed the **Go build-info block**, present in both Windows agents:

```
build  -tags=-trimpath      (identical in both)
build  CGO_ENABLED=0
build  GOARCH=amd64
build  GOOS=windows
build  GOAMD64=v1
```

`[inferred]` **`CGO_ENABLED=0` confirms these are pure-Go builds** — notable because `merlin.x86.dll`/`x64.dll` **are** cgo builds (D95 §4.2) while the **agents are not.** `[inferred]` **The two DLLs and the agent binaries are built with different cgo settings, which is a real toolchain distinction between artifacts in the same distribution.**

`[inferred]` **`GOAMD64=v1` is the baseline x86-64 microarchitecture level** — the least-optimised, most-compatible target, consistent with maximising execution surface over performance.

`[verified]` **`mod.addMulVVW*` appears in every non-Windows agent's symbol strings.** `[inferred]` **That is the exact symbol family `merlin.def` (D95 §4.3) quotes i686-mingw-ld refusing to auto-export** (`cannot export addMulVVWx`). `[inferred]` **The same Go 1.27 standard-library symbol set is present across every platform agent — the `.def` workaround existed because of symbols that are demonstrably still in the binaries.**

---

## §4 T4 — PROVENANCE: THE BUILD ENVIRONMENT

`[verified]` **Method: regex extraction of path roots across all seven agent builds' string sets. Distinct ROOTS only — an earlier pass that returned full file paths produced thousands of Go stdlib lines and was discarded as uninformative.**

### §4.1 The five build roots

`[verified]` **Exactly FIVE distinct build-machine path roots, each present in 7 of 7 builds:**

| build root | builds | meaning |
|---|---:|---|
| `/opt/hostedtoolcache/go/1.27.2` | **7/7** | GitHub Actions hosted-runner tool cache |
| `/home/runner/work/merlin-agent` | **7/7** | GitHub Actions workspace directory |
| `/home/runner/go/pkg/mod/github.com` | **7/7** | Go module cache (GitHub-hosted) |
| `/home/runner/go/pkg/mod/golang.org` | **7/7** | Go module cache |
| `/home/runner/go/pkg/mod/go.dedis.ch` | **7/7** | Go module cache |

`[inferred]` **PERFECT UNIFORMITY: not one build root is platform-specific.** `[inferred]` **`/opt/hostedtoolcache/` is the GitHub-hosted-runner tool path and `/home/runner/` is the Actions runner's home.** `[inferred]` **Both are Linux paths, and they appear in the `GOOS=windows` and `GOOS=darwin` builds identically.** `[inferred]` **Therefore all seven binaries — Windows, Darwin and Linux — were CROSS-COMPILED from a single Linux CI runner. No macOS host and no Windows host was involved in producing any artifact in this corpus.**

`[inferred]` **This is the central attribution finding: the build environment is a GitHub Actions ephemeral Linux runner, and it is the same environment for every platform.** `[inferred]` **It also explains the uniform configuration in §2 — a single CI matrix job cross-compiling seven targets from one source tree and one flag set.**

### §4.2 Toolchain and version

`[verified]` **Go version across all seven builds: `go1.27.2` — uniform, no exceptions.** `[verified]` Toolchain arch path: `x64` (all seven).

`[inferred]` **This is the third independent confirmation of Go 1.27.2 in this corpus:** C-08 §6 read it from Ghidra's analyzer error; D95 §1.5 read it from `/opt/hostedtoolcache/go/1.27.2/` in the Windows builds; **D110 confirms it across all five non-Windows agents from recovered strings.** `[inferred]` **Three measurements, one value — and the bound it implies is now known to apply to the entire cross-platform surface, not just the Windows pair.**

### §4.3 Builder identity — the negative result

`[verified]` **Probes for builder-machine USER identity returned ZERO matches in all seven builds:**

| probe | result |
|---|---|
| `/Users/<name>` (macOS home) | **none — all 7 builds** |
| `/root/<name>` (Linux root home) | **none — all 7 builds** |

`[inferred]` **No developer username, no home directory, no workstation path leaks.** `[inferred]` **This is consistent with ephemeral CI runners, which use `/home/runner` (a service account) rather than a personal home.** `[inferred]` **It is a genuine attribution LIMIT: the embedded paths identify the BUILD PLATFORM and its automation, not a person.** `[inferred]` **Stated as an absence with the probe shown, not as a claim that no identity exists anywhere.**

### §4.4 Module provenance

`[verified]` **20 distinct `module@version` pairs (§2.5).** `[inferred]` The module paths resolve through `/home/runner/go/pkg/mod/…`, and `github.com/Ne0nd0g/...` entries carry the module-cache `!`-escaping of a capital letter (`!ne0nd0g`), a Go module-cache convention.

`[verified]` **The main module is `github.com/Ne0nd0g/merlin-agent/v2`; build hash `e68a5e810cbd269622b5617ae8cd5c22c6b82005` — identical in all seven builds.**

`[inferred]` **A single build hash across seven platform builds means the SEVEN ARTIFACTS ARE ONE RELEASE.** `[inferred]` **There is no version skew in this corpus: one commit, one flag set, seven targets, produced by one CI run.** `[inferred]` **The `core.Build` hash is therefore a join key that ties all seven agents to a single source revision — and it is the same value D95 §1.2 read from the Windows pair.**

---

## §5 Verification, and the limits of this round

`[verified]` **No corpus binary was executed. No debugger attached. No network.** Reads only: directory walks, byte reads, `Get-FileHash`, PE header arithmetic, regex over extracted text.

`[verified]` **No Ghidra run was performed and none was needed.** `[inferred]` **The task's own bound held: the non-Windows agents are Mach-O/ELF and would need a provider Ghidra P0 rejects on this host.** `[inferred]` **All four tasks were answerable without it, which is why there are no new toolchain failures to record — not because C-08's seven are resolved.**

`[verified]` **One probe failure, failed loud, and it was mine.** The T4 path extraction initially returned **full file paths** and produced thousands of Go stdlib lines, flooding the result. `[inferred]` **The output was obviously unusable and was discarded rather than summarised.** `[inferred]` **Re-run against ROOTS ONLY (5 distinct values) — which is the finding.** `[inferred]` **Had I reported "hundreds of build paths," the number would have been an artifact of extraction granularity, not a census.**

`[verified]` **A second probe failure, failed loud, also mine.** A format string with a trailing `(0x{4:X})` threw `InvalidCastFromStringToInteger` when the computed delta was negative. `[inferred]` **The exception did not suppress the evidence — the three deltas printed correctly before it — and the re-run used plain signed decimal.** `[inferred]` **A silent coercion to a bogus unsigned value would have been the dangerous outcome; an exception was the safe one.**

`[verified]` **A third, and it is the same species D95 recorded:** a `Get-ChildItem … -File` on `02_BINARIES` returned nothing on one call and the four files on the next. `[inferred]` **Re-read via `[IO.Directory]::GetFiles`, which is not subject to the cmdlet parameter binding issue.** `[inferred]` **Recorded because a single empty enumeration should never be reported as an absent directory.**

### §5.1 A BROKEN BYTE-HAZARD DETECTOR — the fourth probe failure, and the most instructive

`[verified]` **The post-write byte-hazard check ran, returned `0` for both hazardous sequences, and was WRONG — because the detector itself was broken.** The positive control caught it.

`[verified]` **The control is D61, which carries a known, intentional instance of the mojibake sequence.** The first probe reported the control at **0**, against an expected non-zero — **a detector returning 0 on a known positive can never certify a file clean**, and reporting "0 hazards" off it would have been precisely the false-clean claim D95's §5 defect taught.

`[verified]` **Root cause: a DOUBLE-ENCODING BUG IN THE PROBE.** The regex was built by concatenating four *characters* (`0xC3, 0x82, 0xC2, 0xA7`) and then UTF-8-encoding the resulting string, producing the eight-byte sequence `C3 83 C2 82 C3 82 C2 A7`. It could never match a four-byte sequence in any file. **The instrument was measuring nothing, in both files, silently.**

`[verified]` **Corrected character-level probe, with the control live:**

| probe | D61 (control) | D110 |
|---|---:|---:|
| `U+00C2 U+00A7` (mojibake, char-level) | **3** | **0** |
| `U+FFFD` replacement char | 0 | **0** |
| `U+00A7` (correctly-encoded section sign) | 55 | **46** |

`[verified]` **D110 is clean by THREE independent methods:** character-level match **0**; **raw-byte scan for `C3 82` = 0** and for `EF BF BD` = 0, run directly over the byte array with no regex and no encoding layer; and a **strict `UTF8Encoding($false, $true)` decode that throws on invalid input accepted the whole file without exception.** `[inferred]` **Three methods, one answer — and the second method shares no code path with the first, so a bug in either cannot produce a matching false clean.**

`[verified]` **The 46 real section signs in D110 are correctly single-encoded and are counted by the U+00A7 probe, which is non-zero — confirming the probe distinguishes the correct character from the mojibake rather than merely failing to match both.**

`[inferred]` **CORRECTION TO D95 §5, and it cuts against my own prior report.** D95 recorded the D61 control as **4**. The measured value is **3**. `[inferred]` **D95's own hazard probe used the same character-concatenation construction and reported 0 for both of its files; that probe was almost certainly subject to this same double-encoding defect.** `[inferred]` **D95's "0" findings are therefore NOT reliable evidence of cleanliness as measured — D95's §5 remediation claim must be re-run under the corrected probe before it is cited.** `[inferred]` **This is the D95 lesson recurring one level up: D95 caught a defect by naming a hazard in prose; D110 caught a defect in the DETECTOR that was supposed to catch that defect. A claim of cleanliness is still not a measurement of cleanliness — and a measurement from a broken instrument is not a measurement either.**

`[inferred]` **INSTRUMENTABILITY IS NOT ACCURACY, and §1.4 is this round's instance.** `[inferred]` **Six Merlin artifacts have symbol dumps and a seventh `C-0x` file exists — so a reader inspecting the output directory would count seven Merlin analyses.** `[inferred]` **The seventh is Sliver.** `[inferred]` **The instrument (Ghidra) ran perfectly on all seven; the population it was pointed at was not the population implied by its name.**

`[inferred]` **A NUMBER THE CORPUS REFUTES IS THE STRONGEST EVIDENCE.** `[inferred]` **The task proposed a per-platform config divergence as the likely finding in T2. The measurement refutes it: the config is uniform.** `[inferred]` **That refutation is the finding, and it is stronger than a confirmation would have been — it collapses a build matrix to one job and makes the entire cross-platform surface one release.**

---

## §6 Residual unknowns

| ID | Unknown | Severity | Probe |
|---|---|---|---|
| **R-110.1** | **10 of 16 artifacts have no symbol-layer analysis — 100% of the Mach-O and ELF surface.** Whether this is closable depends on the D96 pclntab lane, which is outside D110's scope. | **critical** | Check `_d96_pclntab.tsv` coverage; if pclntab recovery works, apply to the 10. |
| **R-110.2** | **Whether the 10 unanalysed binaries are the SAME RELEASE as the analysed 6** is strongly implied by the shared `core.Build` hash but **verified only for the seven AGENTS, not for the CLIs, DLLs or server.** | **high** | Extract the build hash from the 6 CLIs and 2 DLLs. |
| **R-110.3** | **`AllocConsole` / console-API CALL sites were not resolved** — import presence ≠ call presence. Requires disassembly of `.text`, blocked by the dead Go analyzer. | **high** | pclntab-driven symbol recovery, then xref the imports. |
| **R-110.4** | **The GUI-vs-console runtime behaviour is genuinely untested** — no console allocation is an OS loader policy, unreachable statically. **Not executed, per mandate.** | **high** | Out of static reach by construction; requires a controlled execution environment outside this corpus. |
| **R-110.5** | **The `.text` −16 delta is consistent with address fixup but was not traced to a specific referenced address.** | **medium** | Resolve the 77 sites against the `.rdata` string table. |
| **R-110.6** | **RESOLVED.** `awgh/rawreader` = Windows pair exactly (measured). `mattn/go-colorable` = **7/7** (measured), correcting the drafting-pass figure of 2. | **resolved** | — |
| **R-110.7** | **The `merlinServer-Windows-x64.7z` contents were not enumerated** — that its extraction produced `merlin_extracted` is inferred from name and size relation, not verified by listing the archive. | **medium** | List the archive; compare the 16 hashes. |
| **R-110.8** | **`linux` token in Darwin builds is a substring artifact** and was not separated from genuine identifiers. | **low** | Word-boundary regex against the recovered strings. |
| **R-110.9** | **D95 §5's byte-hazard cleanliness claim was made with a detector now known to be broken** (§5.1). D95's files were not re-scanned under the corrected probe. | **high** | Re-run the character-level probe over every D9x/D11x report; re-verify D95. |
| **R-110.10** | **D61's true mojibake count is 3, not the 4 recorded in D95 §5** — the discrepancy is unexplained and may indicate D61 was edited since that measurement. | **medium** | Re-measure D61; check git history if available. |

---

## §7 Summary — four answers

`[verified]` **T1 — 16 distinct binary artifacts; 6 analysed at the symbol layer (37.5%); 10 unanalysed, which is every Mach-O and ELF in the corpus.** The 32 binary *file entries* collapse to 16 because `07_OUTPUT\extractions\T8\extracted\` is a **byte-identical re-extraction** — all 16 hashes match pairwise. A seventh `C-0x` dump exists but is **Sliver**, not Merlin, so a reader counting dumps overcounts Merlin by one. `02_BINARIES\` holds the **68,780,065-byte `.7z` distribution archive** — the provenance link nobody had drawn — plus `sliver-client_windows-amd64.exe` at 65,866,240, confirming C-08 §9's figure. **Extension-first inventory finds 4 Windows binaries and misses 10 cross-platform ones.**

`[verified]` **T2 — ALL seven agent builds share one build configuration; there is NO per-platform divergence.** Two config strings exist: **`64E8E9BA653B71B2` (699 B) in six builds — all five non-Windows agents AND the Windows Debug agent — and `B2DFB420DA59BC19` (713 B) in the Windows release alone**, differing by exactly **14 bytes = ` -H=windowsgui`**. Same `psk=merlin`, `h2`, `sleep=30s`, `padding=4096`, `transforms=jwe,gob-base`, `build=e68a5e81…` everywhere. **The Linux and Darwin agents literally ship a `Windows NT 6.1` Chrome 40 user-agent.** Real per-OS compilation is confirmed by `mach_`/`darwin` vs `SECCOMP`/`/proc/`. 20 dependency modules, 17 in all seven builds, cryptographic stack named and versioned.

`[verified]` **T3 — the divergence is ONE PE HEADER FIELD and the code is unchanged.** `Subsystem` 2→3 is the only differing header field; entry point `0x8ACA0` identical; `.pdata` and `.xdata` differ by **zero**; the entry-point code region is **byte-identical for 512 bytes**; `.text` differs by **80 bytes, all at a single constant delta of −16**, consistent with address fixup. **Total divergence 1,666 bytes of 13,939,200 = 0.0121%**, concentrated in `.rdata` string data and its fixups. **What settles statically: the two builds are the same program with one loader-visible flag flipped, built with identical `-tags` and `CGO_ENABLED=0`. What does NOT: whether a console appears at runtime — that is OS loader policy, unreachable from bytes, and was not executed.** `[inferred]` **For an implant meant to be unseen, "does a black window appear" is the operationally decisive question, and it is answered by the loader rather than the code — which is why identical code can still mean different operational behaviour.**

`[verified]` **T4 — five build roots, uniform across all seven builds, all GitHub-hosted Linux CI paths.** `/opt/hostedtoolcache/go/1.27.2` · `/home/runner/work/merlin-agent` · `/home/runner/go/pkg/mod/{github.com,golang.org,go.dedis.ch}` — **each 7/7, none platform-specific.** **All seven binaries, Windows and Darwin included, were cross-compiled from one Linux Actions runner; no macOS or Windows build host was involved.** Go **`go1.27.2`** uniform (third independent confirmation). **No builder user identity leaks** — zero `/Users/<name>`, zero `/root/<name>` — consistent with ephemeral runners and a real attribution limit. **The identical `core.Build` hash `e68a5e81…` across all seven means the corpus is ONE RELEASE, one commit, one CI run, seven targets.** Bonus: the Go build-info block shows **`CGO_ENABLED=0` for the agents** — unlike the cgo-built DLLs of D95 — and **`GOAMD64=v1`**, baseline microarchitecture.
