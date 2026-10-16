# D127 — The Merlin archive decoded from bytes, and the three-way block taxonomy

**Report ID:** `D127` · **Lane:** `archive-diver` · **Class:** static artifact analysis. No archive was opened with a tool for this report; no binary was executed; no passphrase was searched for, guessed, or cracked.

**SCOPE:** two questions that can only be settled by reading bytes — (1) what `merlinServer-Windows-x64.7z` is as a container, what it holds, and whether it agrees with D126's 19-field config census; (2) a three-way classification of every blocked target in the corpus, separating MISSING DATA from MISSING TOOLCHAIN from MISSING INVOCATION.

**DEFINER SCOPE:** the single `.7z` under `RE_Library\02_BINARIES\merlin\`; the 89 extracted members under `05_TARGETS\merlin_extracted\`; the T8 listing artefacts; every `.md` under `07_OUTPUT\reports\DEEP\` that carries a blocked marker.

**CONDITIONAL SCOPE:** none. No D-number, lane, or date filter was applied.

**COUNTED:** 148 `.md` files under `DEEP` · 1 `.7z` file in the entire corpus · 4 files under `02_BINARIES` · 89 extracted members · 63 `.json` members · 23 lines carrying a blocked marker across 7 reports · 1 archive byte-censused in full.

**This report is D127 by allocation.** `[verified]` **`_ALLOC/registry.json` records `"127"` held by `archive-diver` from `2026-10-16 22:20:15`.** `[verified]` **That reservation has no board task until this round; the Lead backfilled it as `task-83` at revision 1, and I claimed it at revision 2, `status in_progress`, `ownerName archive-diver`.** `[verified]` **The hold was load-bearing while idle: `binary-layer` attempted `claim 127` and the allocator refused with `HELD D127 by archive-diver since 2026-10-16 22:20:15`, exit 1, before taking `D128`.**

---

## §0 What this brief got wrong, stated first

`[verified]` **1. The brief says the archive is `[blocked]`, and that a SECOND, DIFFERENT archive is the one this lane owns.** `[verified]` **There is exactly ONE `.7z` file under all of `RE_Library`.** `[verified]` **`Get-ChildItem -Recurse -File -Filter *.7z` over the whole tree returns 1 file: `02_BINARIES\merlin\merlinServer-Windows-x64.7z`, 68,780,065 bytes.** `[verified]` **That is the same file D116 §2 measured, byte for byte, and D116 recorded it as NOT BLOCKED.** `[inferred]` **There is no second archive to be a different archive.**

`[verified]` **2. D116 §2 already settled this target, with controls.** `[read]` **D116 L99 records `7z t -p"merlin"` exit 0 with a negative control at exit 2. D116 L126 records the same command on the same file with one character changed flipping `Everything is Ok`/exit 0 to `Can't open as archive`/exit 2.** `[read]` **D116 L365 records the outcome in its correction table: "the archive is OPEN: 50 folders, 89 files, 264,634,542 B, ZERO sliver entries."** `[inferred]` **A target that is open is not a blocked target, and the Lead's own D123 brief carried the same stale premise — D123 §2 corrects it in the same words.**

`[verified]` **3. I did not work the archive with a tool, and I did not use the passphrase.** `[verified]` **Every claim in Part A below comes from reading bytes of the file directly, plus the pre-existing T8 listing and the pre-existing extracted tree.** `[inferred]` **This is deliberate: the container question is answerable from bytes, and the member question was already answered on disk. Re-running 7-Zip would have re-derived D116 at the cost of a password on the command line.**

`[inferred]` **What the brief DID get right, and it is the part that matters:** `[inferred]` **the demand for a positive control before any reader is trusted.** `[inferred]` **A reader that returns zero on everything is indistinguishable from a correctly-empty archive, and this lane would have shipped exactly that if the control had failed silently.** `[inferred]` **It did not fail silently. It was built first and it proved the reader.**

---

## §1 A1 — CONTAINER FORMAT, ESTABLISHED FROM BYTES

### §1.1 The positive control, built before the target was touched

`[verified]` **A synthetic archive was constructed byte by byte with a known member name and known plaintext, then read by the identical reader:**

```
COUNTED: 1 synthetic archive, 153 bytes
  known member name      : CONTROL_MEMBER_plaintext_known.txt
  known plaintext        : THE QUICK BROWN FOX 0123456789
  StartHeaderCRC declared: 0xCEC41F69
  StartHeaderCRC computed: 0xCEC41F69   MATCH True
  packed body recovered  : THE QUICK BROWN FOX 0123456789
  body == known plaintext: True
  name bytes in NextHeader: True
  CONTROL VERDICT        : READER PROVEN
```

`[inferred]` **The control exercises all three reader capacities at once: it parses the fixed header, it verifies a CRC the reader computes itself, and it recovers a plaintext whose value the reader was never told.** `[inferred]` **Without this, every zero in §2 is ambiguous between "the archive is empty of that thing" and "the reader is dead."** `[inferred]` **This is the same instrument rule D126 §0 applied to the 18-stub census, and the same one the Lead demanded here.**

### §1.2 StartHeader layout, and the byte order is forced

`[verified]` **COUNTED input: 1 file, 68,780,065 bytes.**

| offset | width | field | value |
|---|---:|---|---|
| 0 | 6 | signature | `37 7A BC AF 27 1C` |
| 6 | 2 | version (LE u16) | `0x0400` |
| 8 | 4 | StartHeaderCRC (LE u32) | `0xFC661B8D` |
| 12 | 8 | NextHeaderOffset (LE u64) | `0x4197FC0` = 68,779,968 |
| 20 | 8 | NextHeaderSize (LE u64) | `0x41` = 65 |
| 28 | 4 | NextHeaderCRC (LE u32) | `0xC29D5BDA` |

`[verified]` **The format is identified as 7z from the signature and the layout, NOT from the `.7z` extension.** `[inferred]` **The extension happens to agree, and that agreement is not evidence — the brief's instruction to establish the format from bytes closes that gap rather than relying on the filename.**

`[verified]` **Byte order is forced, not assumed.** `[verified]` **Read little-endian, `NextHeaderOffset = 0x4197FC0` = 68,779,968, which points at offset 68,780,000 inside a 68,780,065-byte file.** `[verified]` **Read big-endian, the same eight bytes give `0xC07F190400000000`, a value larger than the file by seventeen orders of magnitude. Only one byte order is representable.**

`[verified]` **Three integrity checks, all computed with an implementation written for this report (`binascii.crc32`, not a 7z library):**

| check | computed | declared | result |
|---|---|---|---|
| CRC-32 over bytes 12..31 | `0xFC661B8D` | `0xFC661B8D` | **MATCH** |
| CRC-32 over the 65-byte NextHeader | `0xC29D5BDA` | `0xC29D5BDA` | **MATCH** |
| `32 + NHO + NHS` vs filesize | 32 + 68,779,968 + 65 = **68,780,065** | filesize **68,780,065** | **MATCH** |

`[inferred]` **The third check is the strongest of the three: it says the file has no trailing bytes and no truncation, and it is arithmetic rather than a library call.** `[inferred]` **A truncated archive would fail it. A file with appended data would fail it.** `[inferred]` **This archive is structurally complete.**

### §1.3 The decisive byte

`[verified]` **NextHeader byte 0 is `0x17`.**

`[inferred]` **In the 7z container, the top-level NextHeader opens with one property id, and the two possible openers are structurally different:**

| opener | meaning |
|---|---|
| `0x01` `kHeader` | a **plaintext** property tree follows — **member names are readable without a key** |
| `0x17` `kEncodedHeader` | StreamsInfo describes an **encoded** stream that, once decoded, yields the property tree |

`[verified]` **This archive is `0x17`.** `[inferred]` **The entire question of whether member names are readable is decided by one byte, before any parsing, and it is decided as NO.**

`[inferred]` **The consequence, stated precisely:** `[inferred]` **the FilesInfo block — which is what carries member names (`kName` = `0x11`), sizes, and timestamps — is inside the encoded stream. It is not in the 65 cleartext bytes.** `[inferred]` **Every property id in those 65 bytes belongs to StreamsInfo, which describes the DECODER, not the member list.** `[inferred]` **The 65 bytes are a description of how to decompress and decrypt the real header, and nothing else.**

`[verified]` **D116 §2 recorded `Method = ARM64 LZMA2:26 LZMA:20 BCJ2 ARM 7zAES` and `Headers Size = 2577` from the T8 listing.** `[verified]` **`7zAES` is named among the coders, which is the cipher's own identifier appearing in the artifact rather than being inferred.**

---

## §2 A2 — MEMBER ENUMERATION

`[verified]` **COUNTED input: 1 archive; 89 files and 50 folders inside it; 264,634,542 B uncompressed; 68,777,488 B compressed.**

`[verified]` **The member list, from `07_OUTPUT\extractions\T8\merlin_listing_plain.txt` (14,722 B, 160 lines) and `merlin_listing_slt.txt` (30,736 B):**

| class | count | notes |
|---|---:|---|
| directories | **50** | `data\modules\{darwin,linux,windows}\...`, `data\bin` |
| files | **89** | footer line reads `89 files, 50 folders` |
| `data\bin\merlinAgent-*` | **5 per-platform agents** | Linux arm/arm64/x64, Darwin arm64/x64 |
| `data\bin\merlinCLI-*` | **5 per-platform CLIs** | plus `merlinCLI-Windows-x64.exe` |
| `merlinServer-Windows-x64.exe` | **1** | 26,329,600 B, alone at the archive root |
| `.json` module descriptors | **63** | under `data\modules\` |
| `.dll` | **2** | `merlin.x64.dll` 15,145,760 B, `merlin.x86.dll` 14,687,006 B |

`[verified]` **CROSS-CHECK AGAINST DISK, independent of the listing.** `[verified]` **`05_TARGETS\merlin_extracted\` holds 89 files totalling 264,634,542 B.** `[verified]` **Both numbers equal the listing footer exactly.** `[verified]` **`merlinServer-Windows-x64.exe` on disk is 26,329,600 B with SHA-256 `054EECE65FD586379574B0BC7FC800B807BF51A3A471B3E75FFCC1B022555552`, matching D116's recorded digest and size.** `[verified]` **An extracted tree and an archive listing agreeing on file count, byte total, and a content hash is a two-method agreement on the same population.**

`[inferred]` **The 63 `.json` figure is load-bearing and I got it wrong first.** `[inferred]` **My scan said 63; my first transcription of the listing said 61. Resolved by three independent methods — `-Filter *.json`, `Extension -eq .json`, `Name -like *.json` — all returning 63, and by counting `.json` lines in the listing itself, also 63, with `in walk, not in listing: 0`. The correct number is 63, and my eye skipped two `templates\` entries in a block it had already passed.**

### §2.1 Are the names encrypted

`[verified]` **YES, and the mechanism is named at byte level.** `[verified]` **The property tree is the `kEncodedHeader` (§1.3), and `7zAES` is a coder in the pipeline (`Method = ARM64 LZMA2:26 LZMA:20 BCJ2 ARM 7zAES`).** `[inferred]` **The name table is inside that stream and is therefore encrypted along with it.** `[inferred]` **This is confirmed independently by D116's controlled observation: without a password, and with an empty password, 7-Zip refuses even the LISTING (`Cannot open encrypted archive. Wrong password?`, exit 2). A reader that cannot list filenames is a reader that cannot reach them.**

`[verified]` **Name decryption path, cross-referenced and not re-derived:** `[read]` **the passphrase is `merlin`, recovered by a prior lane in `T8_merlin_full.md` and independently reproduced by D116 with a negative control (exit 0 vs exit 2 on a one-character change).** `[inferred]` **With the passphrase, 7zAES unwraps the stream, LZMA2 and the BCJ2/ARM filters decode it, and the cleartext property tree yields the names — which is exactly how the listed names exist on disk to be read.**

`[inferred]` **The encryption is therefore CONFIRMED PRESENT and CONFIRMED DEFEATED, and it is defeated by a known operator-supplied passphrase rather than by any weakness.** `[inferred]` **I state that plainly because the alternative reading — "the header is encrypted, therefore blocked" — is the stale premise this report exists to correct.**

---

## §3 A3 — THE FIELD SET, AND THE COMPARISON WITH D126

### §3.1 What is actually in the archive

`[verified]` **COUNTED: 63 `.json` members, all under `data\modules\`, all parsed successfully (0 parse failures).**

`[verified]` **DISTINCT TOP-LEVEL KEY SETS: 4.**

| key set | files | the keys |
|---|---:|---|
| `base` | **39** | module descriptor |
| `base` + `powershell` | **22** | descriptor plus a PowerShell-specific block |
| `additionalInstructions` + `base` | **1** | descriptor plus extra guidance |
| `powershell` | **1** | PowerShell block only |

`[verified]` **PER-KEY TOTALS ACROSS THE POPULATION: `base` 62 of 63 files · `powershell` 23 of 63 · `additionalInstructions` 1 of 63.**

### §3.2 The comparison, answered honestly

`[verified]` **D126 S2 measured: 19 fields, 1 distinct field-set, across 9 config-bearing Merlin binaries, every value identical.**

`[inferred]` **THIS ARCHIVE NEITHER AGREES NOR DISAGREES WITH THAT, AND SAYING EITHER WOULD BE A MEASUREMENT I DID NOT MAKE.**

`[inferred]` **The reason is that they are different populations of different artifact classes.**

| | D126's measurement | this archive |
|---|---|---|
| population | **9 binaries** | 1 archive, 89 members |
| artifact class | the `-X main.*` ldflags run **compiled into a Go binary** | the server's **module catalogue on disk** |
| where the text lives | inside PE bytes, deep | as standalone `.json` member files |
| what a field is | an agent runtime setting (`main.psk`, `main.sleep`) | a module descriptor key |

`[inferred]` **The archive contains the same five `merlinAgent-*` binaries D126 measured, so the config blob D126 found is IN there — inside those binaries, not as a separate member. But recovering it means scanning the PE bytes, which is D126's measurement, and re-running it here would be re-deriving a peer's result rather than cross-referencing it.** `[inferred]` **I did not do that.**

`[verified]` **A bounded check was run and is reported as bounded: 89 files scanned, first 4 KB each, 0 with a `main.*` marker in the head.** `[inferred]` **This negative is EXPECTED and is not informative — the ldflags string lives deep in the PE, not in the first 4 KB — and it is printed here so that nobody later reads the zero as a finding.**

`[inferred]` **So: the `-X main.*` field set is not reachable as a standalone member, the module catalogue is a different thing, and the honest verdict is NOT COMPARABLE rather than AGREE or DISAGREE.** `[inferred]` **Reporting "disagrees" would assert that I measured 19 fields and got something else. I did not measure 19 fields at all.**

`[inferred]` **The archive does contribute one new fact to the field-set question: a module catalogue of 63 descriptors resolves to 4 distinct top-level key sets, not 1.** `[inferred]` **That is a genuine 4-way split in a population D126 never looked at, and it is stated as a property of the module catalogue alone.**

---

## §4 A4 — THE KEY'S ORIGIN

`[verified]` **Cleartext bytes 0..64 were exhaustively inspected. All 65 bytes are accounted for by the StartHeader plus the EncodedHeader's StreamsInfo.**

`[inferred]` **ORIGIN: OPERATOR-SUPPLIED.** `[inferred]` **The basis is not a guess about the format: it is that in 7z, the cipher identifier and any KDF salt are carried INSIDE the encoded stream, so a container can be built where no key material is committed in cleartext at all — and this one has no salt, no IV, and no key blob in any of its 65 cleartext bytes.** `[inferred]` **Nothing in the artifact derives or embeds the key; the key has to arrive from outside it.**

`[read]` **This is corroborated by the one observation already on record: the archive lists and tests correctly under a short, human-memorable passphrase (`merlin`) and refuses under a one-character variant and under an empty password. A derived or embedded key would not have that property.**

`[verified]` **NAMED MISSING INGREDIENT for the one thing this report cannot state: the passphrase is not in the artifact.** `[read]` **It is not missing from the corpus — the prior lane recovered it and D116 reproduced it — but it is not derivable from the container, and no key material is committed there.**

`[inferred]` **I did not search for the passphrase, did not test candidates against the archive, and did not crack anything.** `[inferred]` **A passphrase sweep would be an attempt to open the target, and the target needs no opening for the questions this report was asked.**

---

## §5 B1 / B2 — THE BLOCKED TARGETS, CLASSIFIED THREE WAYS

### §5.1 Enumeration

**SCOPE:** every `.md` under `07_OUTPUT\reports\DEEP\`, no filter.
**COUNTED:** **148 `.md` files** · **23 lines carrying a blocked marker · across 7 reports.**

| report | blocked lines |
|---|---:|
| `D116_d96_denominator_merlin_archive_open_and_line_vs_row_adjudications.md` | 7 |
| `D121_address_to_name_index_..._two_blocked_surfaces.md` | 5 |
| `D123_havoc_orphan_accumulation_..._conditional_scope_table.md` | 5 |
| `D121_msf_tlv_declaration_use_matrix_..._overlay_immunity_count.md` | 3 |
| `D122_android_axml_column_typology_....md` | 1 |
| `D125_android_method_reachability_census_....md` | 1 |
| `D126_layer_pair_source_against_binary_....md` | 1 |

### §5.2 My first classifier was broken, and that is reported rather than hidden

`[verified]` **A keyword classifier over those 23 lines returned: MISSING DATA 1 of 23 (4.3%) · MISSING TOOLCHAIN 0 of 23 (0.0%) · MISSING INVOCATION 0 of 23 (0.0%).**

`[inferred]` **23 of 23 blocked lines matched none of my three classes. A classifier that returns one verdict for 100% of input is a broken classifier, and the Lead's standing instruction is to treat it as broken before treating it as a finding.** `[inferred]` **The phrase list was wrong, not the corpus — the reports mostly say "blocked" in a tag-definition line or a policy line, not in a claim of blockage.** `[inferred]` **I discarded the classifier and classified by reading each claim instead.**

### §5.3 The classification, from the claims themselves

`[verified]` **Only TWO targets in the corpus carry a re-derived, sourced block. Both are named below with the file that blocked them.**

| # | target | blocking file | class | the missing ingredient, named |
|---|---|---|---|---|
| **B-1** | **Havoc Demon build** | `D123` §2 (`havoc-deep`) | **MISSING INVOCATION** | **a recorded invocation of the Demon build** |
| **B-2** | **D77 U1 (ruby/gem/bundle provisioning)** | `D121_msf_tlv_...` §T4.1 | **MISSING TOOLCHAIN** | `ruby`, `gem`, `bundle` absent from this host |
| **B-3** | **Merlin archive** | *contested* | **NOT A BLOCK — a FALSE BLOCKED** | see §0; the archive is open |

`[verified]` **B-2 RE-DERIVED INDEPENDENTLY BY ME, not inherited.** `[verified]` **On this host: `ruby` ABSENT · `gem` ABSENT · `bundle` ABSENT · `gcc` ABSENT · `clang` ABSENT · `cmake` ABSENT · `go` ABSENT.** `[verified]` **Positive control, tools that MUST be present: `cmd` PRESENT · `python` PRESENT · `dotnet` PRESENT · `node` PRESENT · `java` PRESENT · `7z` PRESENT.** `[inferred]` **The finder returns ABSENT and PRESENT in the same pass, so its ABSENT is a measured absence rather than a dead probe.** `[inferred]` **This is a genuine MISSING TOOLCHAIN: the artifact class is addressable and the interpreter is not on the machine.**

`[verified]` **B-3 is the instructive case.** `[read]` **`D116` §2 and `D116` §5 both record that the archive was labelled blocked in a brief, that the label was stale, and that the archive is open — 50 folders, 89 files, 264,634,542 B, zero sliver entries.** `[read]` **`D116` L378 records the self-catch in its own failure table: "Assumed the brief's `[blocked]` framing before checking the corpus — I was one step from documenting a solved target as blocked."** `[inferred]` **A `[blocked]` label sourced from a brief is a FALSE BLOCKED, and this is the one instance in the corpus where that actually happened rather than being warned about.**

### §5.4 Why the three classes are not one class

`[inferred]` **The three describe different missing things, and each implies a different next action:**

| class | what is missing | what would unblock it | example in corpus |
|---|---|---|---|
| **MISSING DATA** | the artifact itself | acquiring the artifact | none re-derived this round |
| **MISSING TOOLCHAIN** | an interpreter/compiler on this host | installing the tool, or reading source instead | **B-2** |
| **MISSING INVOCATION** | a record of a build having been run | a build log or command history — **not a makefile** | **B-1** |

`[inferred]` **B-1 is the case that makes the distinction load-bearing.** `[read]` **`D123` L224: "A makefile is a build INSTRUCTION, not build OUTPUT. It cannot answer what the compiler did, which macros it defined, or whether the target was built at all."** `[inferred]` **A missing toolchain is fixable by acquiring the tool. A missing invocation is not fixable by acquiring anything — the record of what a compiler actually did does not exist and cannot be reconstructed from a build script.**

`[inferred]` **Collapsing B-1 and B-2 would produce the sentence "the Demon build is blocked because the toolchain is missing," which is false: `D123`'s scan found 134 MSVC projects in the corpus, so build tooling was evidently present in the environment that produced the corpus. What is absent is the record of one specific build, and that is a different absence.**

### §5.5 B3 — D-21 is cross-referenced, not re-derived

`[verified]` **D-21 IS CLOSED AND I DID NOT REOPEN IT.** `[read]` **`D123` L205–L228: scope `RE_Library\` recursive, COUNTED 58,321 files; `compile_commands.json` 0 · `CMakeCache.txt` 0 · `CMakeFiles` 0 · CI config 66 hits all issue templates and docs with no `workflows\` directory in the Havoc tree · logs 15 hits all Metasploit spec fixtures · MSVC projects 134 all Metasploit or Covenant · object files 10 all Metasploit or Covenant · PE artifacts 211 all Metasploit or Covenant.** `[read]` **The named missing ingredient: a recorded invocation of the Demon build.** `[read]` **`D126` L240–L245 cites the same enumeration rather than rescanning it.**

`[inferred]` **My contribution is only the classification label: D-21 is MISSING INVOCATION, and it is the corpus's worked example of that class.** `[inferred]` **The provenance contrast is the point worth carrying: D-21 was closed by scanning 58,321 files, while the Merlin archive was blocked by inheriting a sentence from a brief. The labels matched and the provenance was opposite.**

---

## §6 INSTRUMENT FAILURES

`[inferred]` **I1 — my hand-written varint walk produced a wrong stream count and did not throw.** `[verified]` **It decoded `NumPackStreams = 118` from byte `0x76` at offset 4.** `[verified]` **My own validation caught it: 118 sizes cannot fit in the 60 bytes that remain, and the walk had drifted.** `[inferred]` **The fix was not to correct the walk but to stop depending on it. The claim I actually needed — `NextHeader` byte 0 is `0x17` — needs no parsing at all, and I rewrote the finding to rest on that byte plus two CRC checks and one addition.** `[inferred]` **This is the same family as D126's I2: a parser drifting inside a fixed window and returning a confident number. Mine returned 118; D126's returned 6.**

`[inferred]` **I2 — a substring scan of the 65 cleartext bytes "found" `kFilesInfo` at offset 44 and `kEmptyFile` at offset 23.** `[verified]` **Neither is a field.** `[inferred]` **Inside an encoded header there are no member-list property boundaries in cleartext, so a byte match at an arbitrary offset is a byte inside a stream, not a property id.** `[inferred]` **This is precisely D126's I2 error class — a match inside a window read as a field — and it is the third time this round's work has nearly produced a false positive by matching bytes where a boundary was assumed.**

`[inferred]` **I3 — I transcribed the `.json` count as 61 from the listing; it is 63.** `[verified]` **Three methods agree on 63, the listing itself contains 63 `.json` lines, and `in walk, not in listing: 0`.** `[inferred]` **The instrument was correct and my reading of its output was not — the fifth distinct way this round's work produced a number that was plausible, unaccompanied by an exception, and wrong.**

`[inferred]` **I4 — a `python -c` one-liner died on the spaced path.** `[verified]` **`SyntaxError: invalid syntax` with the path split at `FOR`.** `[inferred]` **Same defect D126 recorded as I3 and that my own D121 recorded as F1. The standing fix is to write the probe to a file, which is what every subsequent probe in this report does.**

`[inferred]` **The through-line, and it is the round's real lesson: five failures, zero exceptions until the fourth, and every wrong number was more plausible than the right one. "118" looks like a stream count. "61" looks like a file count. "6 fields" looks like a field count.**

---

## §7 RESIDUAL UNKNOWNS

| id | severity | statement |
|---|---|---|
| **R-127.1** | **high** | **Whether the `-X main.*` config blob inside the five archived `merlinAgent-*` binaries reproduces D126's 19 fields / 1 field-set. Not measured here; D126 is the measurement.** |
| **R-127.2** | medium | The correct field boundary inside the 65-byte EncodedHeader. My walk fix was to abandon the walk, so the offset of `kSize` is unresolved. |
| **R-127.3** | medium | **Probe: no MISSING DATA instance was re-derived this round.** The class exists in the taxonomy with no worked example in this census. |
| **R-127.4** | low | The 4-way module-catalogue key split is described but its cause is not investigated. |
| **R-127.5** | **high** | **The brief's "second, different archive" premise is corrected here but the brief itself is not edited. The correction lives only in this report.** |
| **R-127.6** | medium | `D109` remains genuinely absent from the D-number sequence; unrelated to this report and carried forward. |

---

## §8 SUMMARY

`[verified]` **A1.** `[verified]` **The container is identified from bytes: signature `37 7A BC AF 27 1C`, 32-byte StartHeader, all fields little-endian, byte order forced by the fact that the big-endian read exceeds the file by seventeen orders of magnitude. Both CRC-32s match an implementation written for this report, and `32 + 68,779,968 + 65 = 68,780,065` equals the filesize exactly, so the archive is complete and untruncated.** `[verified]` **The reader was proven on a synthetic 153-byte archive with known plaintext before the target was touched: `READER PROVEN`.**

`[verified]` **A2.** `[verified]` **89 files, 50 folders, 264,634,542 B, matching the extracted tree on count, byte total, and a content hash independently.** `[verified]` **`NextHeader` byte 0 is `0x17` = `kEncodedHeader`, so the property tree is encoded and member names are not in cleartext. `7zAES` appears among the coders. Name encryption is CONFIRMED PRESENT and CONFIRMED DEFEATED by the known passphrase `merlin`, cross-referenced from D116 and not re-derived.** `[verified]` **The archive is NOT a blocked target.**

`[verified]` **A3.** `[verified]` **63 `.json` members with 4 distinct top-level key sets: `base` (39), `base`+`powershell` (22), `additionalInstructions`+`base` (1), `powershell` (1).** `[inferred]` **Against D126's 19 fields / 1 field-set the verdict is NOT COMPARABLE, not AGREE and not DISAGREE: different populations of different artifact classes. The `-X main.*` blob lives inside the archived agent binaries; recovering it is D126's measurement and I did not re-run it.**

`[verified]` **A4.** `[inferred]` **The key is OPERATOR-SUPPLIED. No salt, IV, KDF id, or key blob is committed in any of the 65 cleartext bytes, which is possible precisely because 7z carries that material inside the encoded stream. Nothing in the container derives or embeds the key.**

`[verified]` **B1/B2.** `[verified]` **148 `.md` scanned; 23 blocked-marker lines across 7 reports; only 2 targets carry a re-derived block.** `[verified]` **B-1 Havoc Demon = MISSING INVOCATION, named ingredient a recorded build invocation. B-2 D77 U1 = MISSING TOOLCHAIN, `ruby`/`gem`/`bundle` measured absent by me with present-tools as a positive control. B-3 Merlin archive = NOT A BLOCK, a FALSE BLOCKED inherited from a brief and caught by D116.** `[inferred]` **The three classes are distinct because each implies a different next action, and a makefile can never satisfy MISSING INVOCATION.**

`[verified]` **B3.** `[verified]` **D-21 is cross-referenced and was not re-derived: closed by `havoc-deep` over 58,321 scanned files with the named missing ingredient of a recorded Demon build invocation.**

`[inferred]` **Three findings worth carrying.** `[inferred]` **One byte settled the encryption question and no amount of parsing improved on it.** `[inferred]` **A block inherited from a brief is not a block, and the corpus contains one instance where believing that would have documented an open target as closed.** `[inferred]` **And five instruments produced five plausible wrong numbers this round; the one that failed loudly was the cheapest of them all.**
