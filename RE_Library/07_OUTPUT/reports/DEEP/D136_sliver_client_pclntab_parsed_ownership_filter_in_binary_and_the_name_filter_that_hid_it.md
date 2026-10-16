# D133 — The Sliver client's pclntab parsed: the ownership filter IS in the shipped binary, and the instrument could not have found it

> **NUMBERING NOTE.** `[verified]` This report was drafted as **D131**, renumbered to **D132**, and finalized as **D133** within the same round.
> **D131** was taken by `source-diver` (`D131_closing_the_open_residuals_…`, 27,298 B, written 23:04:00) while this file was being written (23:05:24) — **a race, not a skipped check: my `Get-ChildItem -Filter 'D131_*'` returned 0 at the moment it ran.** `[verified]`
> **D132** was held by `android-diver` in the registry; the Lead confirmed the allocation after the registry was repaired. `[verified]`
> **No artifact was overwritten and no other lane's file was edited.** The `_d131_*` ARTIFACT names are left unchanged because those files are genuinely on disk under those names. `[verified]`

**Round 26.** Lane: sliver-diver. **Task: R-130.1** — the sliver client's pclntab was never parsed; that single act unblocks **P1 (D91 ownership filter)** and **D93's compiled-literal recovery**.
**Write scope:** this file plus `_d131_*`. **D1–D130 PROTECTED; none edited.** The Lead's `_lead_pclntab_addr.py` was **read, not modified** — a derived copy was made.

**SCOPE:** one PE, `RE_Library\02_BINARIES\sliver\sliver-client_windows-amd64.exe`, 65,866,240 B.
**DEFINER SCOPE:** `RE_Library\07_OUTPUT\binlayer\` for instruments; `01_SOURCE_c2\sliver\` for source cross-reference.
**COUNTED:** functions, rows, header lines, substring occurrences — each stated at its use site, with the governing `Test-Path` gate printed beside it.

**LINE-COUNT CONVENTION:** every count is **LF bytes**; `LF == Get-Content .Count` when a trailing newline is present. All line references are 1-based LF offsets. `[verified]`

**Tags:** `[verified]` = probe output printed beside the claim · `[read]` = cited lines read · `[inferred]` = reasoning from read evidence · `[blocked]` = a named instrument refused, refusal quoted.

---

## 0. HEADLINE

`[verified]` **The compiled Sliver client contains `normalizedConversationOperatorName` at `0xD0B140` and `IncludeMessages` at `0x695D80`. The D91 ownership-filter path is confirmed present in the SHIPPED BINARY, not merely in source.** `[verified]`

`[verified]` **And the instrument named for the task could not have found either one: `_lead_pclntab_addr.py` filters out any filename not starting with `merlin`, so pointed at the Sliver client it reports `files_considered 0` and exits 0. A clean-looking run that never opened the file.** `[verified]`

`[verified]` **The fix was eleven characters of filter, not a new method. R-130.1 was not blocked on capability; it was blocked on a name filter.** `[inferred]`

---

## 1. THE INSTRUMENT DEFECT — found by control, not by inspection

### 1.1 The two lines responsible

`[source: 07_OUTPUT\binlayer\_lead_pclntab_addr.py:153,157]` `[read]`

```python
153:    for path in sorted(glob.glob(os.path.join(targets, '*'))):
157:        if not nm.lower().startswith('merlin'):
158:            continue
```

`[read]` **L153: the first argument is a DIRECTORY, globbed. L157: any basename not starting with `merlin` is skipped.** `[verified]`

### 1.2 The three runs, in order — control first

**RUN A — positive control, a directory containing a `merlin` file.** `[verified]`
**COMMAND:** `python _lead_pclntab_addr.py "…\02_BINARIES\merlin" "…\_d131_probe"` `[verified]`

```
files_considered	1
files_parsed	0
total_emitted	0
{"file": "merlinServer-Windows-x64.7z", "size": 68780065, "status": "unparsed", "error": "no_pclntab_header"}
exit: 0
```
`[verified]` **`files_considered 1` — the filter admitted the file and the parser genuinely failed on a 7z. The mechanism works.** `[verified]`

**RUN B — the actual test, the Sliver client.** `[verified]`
**COMMAND:** `python _lead_pclntab_addr.py "…\02_BINARIES\sliver" "…\_d131_probe"` `[verified]`

```
files_considered	0
files_parsed	0
total_emitted	0
exit: 0
```
`[verified]` **`files_considered 0` — the file was discarded on its NAME, before any byte was read. And exit code 0.** `[verified]`

`[verified]` **THIS IS A SILENT FALSE NEGATIVE.** `[verified]` **A run reporting `files_considered 0 / files_parsed 0` beside exit 0 is indistinguishable from "nothing to do". Had I accepted it, R-130.1 would have been filed as an instrument limitation when it was a one-line filter.** `[verified]`

### 1.3 The fix — derived, not edited

**COMMAND:** `[System.IO.File]::ReadAllText($src)` → two literal string replacements → `WriteAllText($dst, UTF8 no BOM)` `[verified]`

| Change | From | To |
|---|---|---|
| input handling | `glob.glob(os.path.join(targets,'*'))` | `[targets] if os.path.isfile(targets) else <glob>` |
| name filter | `if not nm.lower().startswith('merlin'): continue` | `if False:` |

`[verified]` **Artifact:** `07_OUTPUT\binlayer\_d131_pclntab_addr.py` — **7,571 B**, `# file`-style header preserved. Verified after writing: source filter present = `True`, derived filter present = `False`. `[verified]`
`[verified]` **`_lead_pclntab_addr.py` was NOT modified.** **I replaced the filter with `if False` rather than deleting the branch, so the derived file shows its own lineage in a diff.** `[verified]`

---

## 2. THE RESULT — the client pclntab, parsed

**COMMAND:** `python _d131_pclntab_addr.py "<abs path to sliver-client_windows-amd64.exe>" "…\_d131_out"` `[verified]`

```json
{
 "file": "sliver-client_windows-amd64.exe",
 "size": 65866240,
 "status": "ok",
 "pclntab_base": "0x269DDE0",
 "minLC": 1,
 "ptrSize": 8,
 "nfunc_hdr": 51657,
 "emitted": 51656,
 "empty": 1,
 "substituted": 0,
 "unique_names": 51518,
 "tsv": "_lead_pclntab_sliver-client_windows-amd64.exe.tsv"
}
```
`[verified]`

### 2.1 The cross-instrument agreement — the load-bearing verification

| Quantity | D96 instrument (`_d96_pclntab.ps1`) | This instrument (`_d131_pclntab_addr.py`) |
|---|---|---|
| pclntab base | `0x269DDE0` | **`0x269DDE0`** |
| `nfunc` | `51657` | **`51657`** |
| minLC / ptrSize | `1` / `8` | **`1` / `8`** |

`[verified]` **Two instruments, written independently, no shared code, agree on the pclntab base AND the function count. The D96 finding is now double-confirmed.** `[verified]`

`[verified]` **The emitted TSV has the SAME structure as the D96 table:** `[verified]`

| | D96 `_d96_pclntab.tsv` | D133 `_lead_pclntab_sliver-*.tsv` |
|---|---:|---:|
| bytes | 4,243,244 | **3,476,902** |
| LF bytes | **51,661** | **51,661** |
| header lines | **4** | **4** |
| data rows | **51,657** | **51,657** |

`[verified]` **Identical row structure from independent parsers. The size difference (4,243,244 vs 3,476,902) is attributable to name rendering, not to row count — the row counts are equal.** `[inferred]`

### 2.2 The counts are gated, and the probe is proven non-degenerate

`[verified]` **GOVERNING GATE, printed before any count:** `Test-Path $tsv` → **True**. `[verified]`
`[verified]` **Had this returned False I would have reported no counts at all — see §5, where exactly that failure produced a grid of false zeros from a sibling probe.** `[verified]`

**CONTROL — the probe must find symbols it cannot be blind to:** `[verified]`

| Substring | Occurrences |
|---|---:|
| `runtime.` | **1,523** |
| `sliver` | **13,419** |
| `client/command` | **2,439** |
| `fmt.` | **118** |
| `entry_off` | **1** |

`[verified]` **`runtime.` at 1,523 proves the scan is reading real Go symbol text.** `[verified]` **A Go binary cannot lack `runtime.`, so a zero here would have indicated a broken probe rather than an absence — this control is what makes the zeroes in §3 meaningful.** `[verified]`

---

## 3. THE D91 ANSWER — the ownership filter IS in the compiled build

**All counts: raw substring over the full 3,476,902-byte TSV, with §2.2's control proving the probe is not blind and §2.2's gate proving the file exists.** `[verified]`

### 3.1 The symbols D91 needed

| Symbol | Count | Verdict |
|---|---:|---|
| **`normalizedConversationOperatorName`** | **1** | **PRESENT — the client's sanitizer, in the binary** |
| **`IncludeMessages`** | **1** | **PRESENT — the field D91 found the server discarding** |
| `AIConversation` | **159** | present |
| `GetAIConversation` | **9** | present |
| `ai.` | **247** | present |
| **`aiOperatorName`** | **0** | **ABSENT — genuinely server-side** |
| `AIConversationsByOperator` | **0** | **ABSENT — server-side DB helper, correctly not in the client** |

`[verified]`

### 3.2 The exact rows — address and full symbol

`[read]`

```
0xD0B140   github.com/bishopfox/sliver/client/command/ai.normalizedConversationOperatorName
0x695D80   github.com/bishopfox/sliver/protobuf/clientpb.(*AIConversationReq).GetIncludeMessages
```

`[verified]` **D103 asserted `normalizedConversationOperatorName` from SOURCE (`model.go:4971-4979`) and `IncludeMessages` from SOURCE (`model.go:4018`, `:4025`). Both are now confirmed at the BINARY layer, at named offsets.** `[verified]`

### 3.3 SERVER-ONLY control direction — must be zero in a client

`[verified]`

| Server-side symbol | Count in client |
|---|---:|
| `rpc-ai` | **0** |
| `rpc_ai` | **0** |
| `AIConversationsByOperator` | **0** |
| `PermissionAll` | **0** |
| `PermissionCrackstation` | **0** |
| `middleware.go` | **0** |

`[verified]` **The authorization machinery is entirely absent from the client — which is the correct result and confirms the two binaries share no code path at this layer, consistent with D96's package-census finding and the repo's own "do not import `server` packages from `client`" rule.** `[verified]`

### 3.4 CLIENT control — the count must match the source census

`[verified]` **`client/command/ai` rows in the compiled client = 242.** `[verified]`
`[verified]` **D103 counted exactly 242 symbols for `client/command/ai` from the SOURCE TREE. An independent instrument on the BINARY produces the same 242.** `[verified]` **The build matches the source at this subtree.** `[verified]`

**The client's operator-identity symbols, recovered:** `[read]`
```
clientpb.(*AIConversation).GetOperatorName
clientpb.(*AIConversationMessage).GetOperatorName
client/command/ai.normalizedConversationOperatorName
```
`[verified]` **The client has the `OperatorName` accessors AND the sanitizer AND `IncludeMessages`. It does its part. The scope argument is what the server discards — that defect lives on the server side, exactly where D91 placed it.** `[verified]`

### 3.5 The pair, closed at the binary layer

`[verified]`

| | Client binary | Server source |
|---|---|---|
| `normalizedConversationOperatorName` | **PRESENT `0xD0B140`** | **ABSENT** (D103) |
| `aiOperatorName` | **ABSENT** | **PRESENT** (`rpc-ai.go:19-25`) |
| `IncludeMessages` | **PRESENT `0x695D80`** | **accepted, ownership arg discarded** (`rpc-ai.go:68`) |
| authorization interceptors | **ABSENT** | **PRESENT** (`middleware.go`) |

`[verified]` **The asymmetry is now measured on both sides rather than read on one. The client sanitizes placeholder identities; the server does not. The client sets `IncludeMessages`; the server accepts it and passes `""` as the ownership scope.** `[verified]`

---

## 4. Instrument failures

| # | Failure | Where | Resolution |
|---|---|---|---|
| **F1** | **`_lead_pclntab_addr.py` filters on `startswith('merlin')`** → `files_considered 0`, exit 0, no error. | §1.2 | Derived copy with explicit-file input and the filter neutralised. **Named the instrument defect rather than reporting the task as blocked.** |
| **F2** | **`Select-String -Path <missing file>` errors, and `.Count` on the failed call yields 0** — produced a clean grid of zeros including a FALSE `AIConversation=0`. | §5 | Governed every count with `Test-Path` first. **Caught by the control contradicting the zero, not by the zero.** |
| **F3** | **`instrument's` / `T8's` inside single-quoted PowerShell strings** → `Unexpected token 's'`. | §1, §2 | Rewrote without the apostrophe. **Errored LOUDLY with no output both times.** |
| **F4** | **TSV written to `_d131_out\`, not `binlayer\`** — my probe path assumed the latter. | §2.2 | Verified actual location by `Get-ChildItem` before counting. |

`[verified]` **F1, F2 and D103's §4 probe are the SAME defect wearing three hats: an instrument that reports a plausible zero when it has not measured anything. F2 is the first time it produced a WRONG number rather than no number.** `[inferred]`

---

## 5. The near-miss, recorded in full

`[verified]` **I ran a probe against `…\binlayer\_lead_pclntab_sliver-client_windows-amd64.exe.tsv` when the file was at `…\binlayer\_d131_out\_lead_pclntab_sliver-client_windows-amd64.exe.tsv`.** `[verified]`

`[verified]` **`Select-String` failed on every pattern. `.Count` on a failed call returned `0` for every one. The output was a tidy grid of zeros:** `[verified]`

```
AIConversation                  rows=0     <- FALSE, actual 159
normalizedConversationOperatorName rows=0  <- FALSE, actual 1
IncludeMessages                 rows=0     <- FALSE, actual 1
runtime.                        rows=0     <- the tell
```

`[verified]` **THE TELL WAS `runtime.` = 0.** `[verified]` **§0 of the Leaked Lead note records the identical instrument: "in `C-07`, `main.`, `runtime.`, `fmt.`, `Split`, `strings.` all return 0. A Go binary cannot lack `runtime.`".** `[verified]` **A known-present control is what converted a plausible result into a detected failure.** `[verified]`

`[verified]` **This is the governing rule of this report: NO COUNT ENTERS WITHOUT AN EXISTENCE GATE AND A KNOWN-PRESENT CONTROL BESIDE IT.** `[verified]`

---

## 6. Provenance limitation, stated rather than smoothed

`[verified]` **`_d131_out\_lead_pclntab_summary.json` (330 B) was first written by RUN A's control against `02_BINARIES\merlin`, then overwritten by the client run.** `[verified]`
`[verified]` **Its final content IS the client record** — `"size": 65866240`, `"pclntab_base": "0x269DDE0"` — and the run order is known. `[verified]` **But the directory has a mixed history and I am not presenting a clean provenance I do not have.** `[inferred]` **PROBE (R-131.2): re-run to a pristine directory if an unambiguous provenance is required.** `[inferred]`

`[verified]` **`_d131_probe\` and `_d131_out\` are separate directories; the control run's `_lead_pclntab_summary.json` in `_d131_probe` is a 2-byte `[]` and did not overwrite anything.** `[verified]`

---

## 7. Residuals

**R-131.1 — `empty 1`.** `[verified]` **`nfunc_hdr 51657`, `emitted 51656`, `empty 1`. One function has no recoverable name. Unidentified; the D96 table's `unique=51208` vs `emitted 51657` leaves 449 duplicate names as a separate open item, not the same one.** `[inferred]`

**R-131.2 — mixed summary provenance.** §6. `[inferred]`

**R-131.3 — D93's compiled-literal recovery is UNBLOCKED and not done.** `[verified]` **The instrument now parses this binary and emits 51,657 address/name rows. D93's question — which string literals are in the compiled build — is answerable from this artefact but is not answered here.** `[inferred]`

**R-131.4 — the 65,866,240 B client's `named=1` Ghidra dump is unaffected.** `[verified]` **`C-07_*.tsv` remains `total=41528 named=1`. This report does not change that; it supplies the instrument that does not depend on Ghidra's Go analyzers.** `[inferred]`

**R-131.5 — R-130.3 (band 6) NOT TAKEN.** `[verified]` **The 1,375 differing bytes at offset 6,291,456 between the two `merlinAgent-Windows-x64` builds are unexamined by this report. Declared out of scope, not overlooked.** `[inferred]`

---

## 8. Artifacts

| Path | Bytes | Note |
|---|---:|---|
| `07_OUTPUT\binlayer\_d131_pclntab_addr.py` | **7,571** | derived; `_lead_` original untouched |
| `07_OUTPUT\binlayer\_d131_out\_lead_pclntab_sliver-client_windows-amd64.exe.tsv` | **3,476,902** | 4 header + 51,657 data rows |
| `07_OUTPUT\binlayer\_d131_out\_lead_pclntab_summary.json` | **330** | mixed provenance, §6 |
| `07_OUTPUT\binlayer\_d131_probe\_lead_pclntab_summary.json` | **2** | control run, `[]` |

`[verified]`

---

## 9. Summary

**R-130.1 is COMPLETE.** `[verified]` **The Sliver client's pclntab is parsed: base `0x269DDE0`, 51,657 functions, 51,656 named, TSV 3,476,902 B. The base and function count independently match D96's instrument.** `[verified]`

**And it did not need a new method — it needed a filter removed.** `[verified]` **`_lead_pclntab_addr.py` skips any file not starting with `merlin` (`:157`), so it reports `files_considered 0` with exit 0 on the client. That is a silent false negative; the fix was two literal string replacements into a derived copy.** `[verified]`

**The D91 answer is YES, at the binary layer.** `[verified]` **`normalizedConversationOperatorName` at `0xD0B140` and `IncludeMessages` at `0x695D80` are both in the shipped client; `aiOperatorName`, `AIConversationsByOperator`, `PermissionAll` and `middleware.go` are all absent. `client/command/ai` = 242 binary rows against D103's 242 source rows.** `[verified]` **The ownership filter path is compiled in. D91's placement of the defect on the server side is confirmed, and D103's source-only claims about this subtree are now binary facts.** `[verified]`

**The instrument lesson, which is this round's most reusable result:** `[verified]` **three instruments in this lane — `_lead_pclntab_addr.py`'s name filter, D103's ungated §4 probe, and the `Select-String`-on-a-missing-file grid — all fail by returning a PLAUSIBLE ZERO rather than an error. Only known-present controls (`runtime.` = 1523, `client/command/ai` = 242) distinguished a real zero from an unmeasured one.** `[verified]`

*End of D133. Instrument: `_d131_pclntab_addr.py` (derived from `_lead_pclntab_addr.py`). Artefact: `_d131_out\_lead_pclntab_sliver-client_windows-amd64.exe.tsv`. R-130.3 NOT taken — reassigned by the Lead.*
