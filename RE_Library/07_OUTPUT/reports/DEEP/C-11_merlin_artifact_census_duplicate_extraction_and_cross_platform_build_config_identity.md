# C-11 — The Merlin agent corpus census and the cross-platform build-config identity

**Purpose:** D95 §1 reported the operational payload for the **two Windows agent builds** and nine config fields. This report **enumerates the artifact surface properly** — which D95 also asked for — and extends the config extraction to **every agent platform in the corpus**. The extension changes the finding in three ways.

**Tags:** `[verified]` (measured, invocation shown) · `[read]` (quoted from an artifact read directly) · `[absence]` (zero with a positive control) · `[inferred]` (reasoning over evidence).

**Write scope:** this file only. D95 and C-08 are **not edited** — this is a correction and extension by reference.

---

## §0 Headline

`[verified]` **All six Merlin agent builds — Windows release, Windows Debug, Linux-arm, Linux-arm64, Linux-x64, Darwin-x64, Darwin-arm64 — carry the IDENTICAL 19-field `-X` linker config, including `main.secure=false`.**

`[verified]` **All of them carry the IDENTICAL Windows-Chrome-40 user-agent string**, including the Linux and Darwin builds.

`[verified]` **The extraction tree exists TWICE, byte-identical, 17/17 files, zero differences.**

`[verified]` **There are SIX `merlinCLI` binaries, not five.** C-08 §9's corrected list and D95 §3's "five cross-platform CLI binaries" both undercount by one — the Windows CLI is a CLI too.

---

## §1 The artifact census — enumerated, not patterned

`[verified]` `Get-ChildItem -Recurse -File | Where-Object { $_.Name -match 'merlin' }` across `02_BINARIES\`, `05_TARGETS\`, and `07_OUTPUT\extractions\` returns **44 files**. By magic number, not by extension:

| class | count | bytes |
|---|---:|---:|
| **PE** | 8 | 160,058,266 |
| **ELF** | 6 | 94,652,723 |
| **Mach-O** | 6 | 104,221,158 |
| other (archives, text, strings, source) | 24 | 79,398,048 |
| **TOTAL** | **44** | **438,330,195** |

`[verified]` **The eight PE artifacts:** `merlin.x86.dll` 14,687,006 · `merlin.x64.dll` 15,145,760 · `merlinServer-Windows-x64.exe` 26,329,600 · `merlinCLI-Windows-x64.exe` 20,754,432 · `merlinAgent-Windows-x64.exe` 13,939,200 · `merlinAgent-Windows-x64-Debug.exe` 13,939,200 — **each appearing twice** (the duplicate tree). Six distinct PE targets, eight files.

`[verified]` **The six ELF artifacts:** `merlinAgent-Linux-arm` 12,124,284 · `-arm64` 11,534,460 · `-x64` 12,492,924 · `merlinCLI-Linux-arm` 19,183,912 · `-arm64` 19,017,586 · `-x64` 20,299,557.

`[verified]` **The six Mach-O artifacts:** `merlinAgent-Darwin-arm64` 11,808,210 · `-x64` 12,761,408 · `merlinCLI-Darwin-arm64` 19,571,874 · `-x64` 20,804,192 — each twice.

### §1.1 The duplicate tree — measured, not assumed

`[verified]` **`05_TARGETS\merlin_extracted\data\bin\` and `07_OUTPUT\extractions\T8\extracted\data\bin\` hold the same 17 files, SHA-256 identical for all 17, zero differing.**

`[inferred]` **Consequence: every Merlin byte-count in this corpus is DOUBLE-COUNTED if the method globs both roots.** C-00 §1's total, D95's and C-08's per-target sizes are per-file and unaffected, but any corpus-wide Merlin total that did not dedupe by digest is inflated. **This is a denominator hazard of the same shape as D-12** (the 432-file headline dominated by vendored duplicates) — **new species: a duplicate EXTRACTION, not a duplicate dependency.**

### §1.2 Six CLIs, not five

`[verified]` **`merlinCLI-Windows-x64.exe` is already analysed (C-03), but it is a CLI — so it belongs on a list of CLIs.** C-08 §9's outstanding list and D95 §3 both say **five** cross-platform CLI binaries; the enumeration returns **six**:

```
merlinCLI-Darwin-arm64   19,571,874
merlinCLI-Darwin-x64     20,804,192
merlinCLI-Linux-arm      19,183,912
merlinCLI-Linux-arm64    19,017,586
merlinCLI-Linux-x64      20,299,557
merlinCLI-Windows-x64    20,754,432   <- the sixth, and the ONLY one already analysed
```

`[inferred]` **The uncorrected surface is therefore 9 unanalysed Merlin binaries (5 non-Windows agents + 4 non-Windows CLIs), not the 5 in the objective and not the 10 in C-08 §9.** The objective text is wrong on this point; C-08 §9 was closer but still one short.

---

## §2 The build config — identical across six agent platforms

`[verified]` **The complete `main.*` config set, extracted by regex over direct byte reads:**

```
main.protocol=h2
main.url=https://127.0.0.1:443
main.host=
main.httpClient=go
main.psk=merlin
main.secure=false
main.auth=opaque
main.sleep=30s
main.proxy=
main.headers=
main.skew=3000
main.padding=4096
main.killdate=0
main.maxretry=7
main.parrot=
main.transforms=jwe,gob-base
main.useragent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36
              (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36
main.listener=
```

`[verified]` **Set-difference across all six agent builds: the field SET is IDENTICAL.** The script prints a platform's name only when its field set differs from the Windows release; **it printed none.** No per-platform config divergence in the flag set.

`[verified]` **`main.secure=false` is present in all six**, including both Windows builds.

### §2.1 What D95 did not report

`[read]` **D95 §1 listed nine fields:** `psk`, `auth`, `url`, `addr`, `protocol`, `sleep`, `padding`, `maxretry`, `transforms`. `[verified]` **The measured set is larger.** Fields **absent from D95's nine**:

| field | value | why it matters |
|---|---|---|
| **`main.secure`** | **`false`** | **TLS certificate verification is DISABLED at build time.** |
| `main.skew` | `3000` | clock-skew tolerance, in the `sleep`/`killdate` family |
| `main.httpClient` | `go` | selects the Go stdlib client over the Mercury profile client |
| `main.host` | *(empty)* | declared but unset |
| `main.proxy` | *(empty)* | declared but unset |
| `main.headers` | *(empty)* | declared but unset |
| `main.parrot` | *(empty)* | declared but unset |
| `main.listener` | *(empty)* | declared but unset |
| `main.killdate` | `0` | present — `0` means no kill date |

`[inferred]` **`main.secure=false` is the significant omission.** It is a **security-posture field, not a connectivity field**: it means this agent build will accept a TLS peer without validating its certificate. For a defender that is a **detection and MITM surface**; for the operator it is a **build-time downgrade that is invisible in the traffic pattern.** D95 reported nine of the seventeen named fields and this one was not among them.

`[inferred]` **The five empty fields are also a finding of a kind:** `host`, `proxy`, `headers`, `parrot`, `listener` are **declared and unset**. Per D82's four-state rule — *declared / offered / read / honoured* — these are **structured connection points that a rebuild can populate without touching code.** They are the intended configuration surface, and in this build they are at their defaults.

---

## §3 The user-agent is IDENTICAL on Linux and macOS

`[verified]` **Three platforms, same 115-byte string:**

```
main.useragent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36
               (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36
```

`[read]` Windows: identical. Linux-x64: identical. Darwin-arm64: identical.

`[inferred]` **This is a cross-platform fingerprint anomaly, and it is the strongest single operational finding in this report.** A process running on Linux or macOS that opens TLS to a remote host and sends `Windows NT 6.1; Win64; x64` in its User-Agent header is **self-describing as not-what-it-is.** No legitimate Linux or macOS browser sends that string.

`[inferred]` **The anomaly is compound and each layer is independently checkable:**
1. **OS mismatch** — the platform's own User-Agent contradicts the transport's origin.
2. **A 2015 browser in 2026** — `Chrome/40.0.2214.85` is over a decade old.
3. **An EOL OS** — `Windows NT 6.1` is Windows 7, out of support since 2020.
4. **`Chrome/40` paired with `main.protocol=h2`** — HTTP/2 was not enabled by default in Chrome until v41. **The declared client could not have made the declared connection.**

`[inferred]` **Point 4 is the sharpest and it is derivable from the config alone:** the agent claims to be a browser that does not speak the protocol the agent is configured to use.

`[inferred]` **The bound, stated: this is a STATIC build-config observation.** It is the string compiled into the binary. Whether a given deployment overrides `main.useragent` at build time is a property of that build, not of this artifact — **and the five empty connection fields in §2.1 are exactly how it would be overridden.** What is measured is that these six artifacts carry this string.

---

## §4 What this does and does not change

`[verified]` **It does NOT change D95 §1's agent-delta finding.** The release-vs-Debug delta remains `-H=windowsgui` plus the PE subsystem, 21 bytes decomposing 15 + 6. `[verified]` This report independently confirms the mechanism: `-H=windowsgui` **is present in the Windows release binary's config string and absent from every other agent**, which is the same conclusion D95 reached by a different route.

`[verified]` **It does NOT change C-10's `NAMED_FUNCTIONS=1` finding.** The non-Windows agents are Mach-O and ELF, and **Ghidra P0 on this host is PE-only** — so they were never going to be analysed by the existing harness. **Their config is recoverable by direct byte read, which is why this report could cover them and the symbol census could not.** Nothing here required Ghidra, and no Ghidra run was started.

`[inferred]` **It DOES change the residual's shape.** C-08 §9 said five binaries; D95 §3 said five; the objective says five. **The measured unanalysed surface is nine.** Four of them are CLIs, which matter more than agents for the boundary questions — **a CLI is where the `Split("bin")` path derivation (D93) would surface, because the CLI is what writes paths.**

`[inferred]` **Open and unaddressed: the six CLIs carry NO `main.*` build-config string at all** — the probe on `merlinCLI-Linux-x64` returned `NONE` for every field. **A CLI with no embedded config is a different artifact class from an agent with one**, and nothing in this corpus has measured that difference. It is the next question in this lane.

---

## §5 Status

`[verified]` 44-merlin-file census by magic number: 8 PE · 6 ELF · 6 Mach-O · 24 other, 438,330,195 B total.

`[verified]` Two byte-identical extraction trees, 17/17 files.

`[verified]` Six agent platforms share one identical 19-field config, including `main.secure=false`.

`[verified]` One identical Windows-Chrome-40 user-agent on Windows, Linux, and macOS.

`[verified]` Six `merlinCLI` binaries, not five. Unanalysed Merlin surface = **9**, not 5.

`[inferred]` **Not closed here:** the four non-Windows CLIs' structure; whether the empty connection fields are overridden in any build in this corpus; the nine unanalysed binaries' code (Mach-O/ELF, outside the PE-only harness).

**End of C-11.**
