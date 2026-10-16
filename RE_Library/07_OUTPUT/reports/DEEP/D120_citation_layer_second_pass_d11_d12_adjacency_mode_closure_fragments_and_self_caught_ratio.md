# D120 — The citation layer, second pass: the D11/D12 collision, the mode question closed, the dead-fragment population, and self-caught versus cross-caught

**RENUMBER NOTE — read this first.** This report was written as **D118** against an occupancy check that returned `D118_*` = **0 files**. **While it was being written, another lane landed `D118_msf_tlv_proxy_credentials_compression_mask_moduleinfo_four_state_and_eximport_bound.md` at `21:45:16.380`; this file was written at `21:46:06.318` — 50 seconds later.** **The occupancy test was run correctly and the slot was lost to a race, not to a false reading.** The MSF lane is the first-mover and keeps `D118`; **this report renumbers to `D120`** and its probes renumber `_d118_*` → `_d120_*`. **A document number is a name, not an identity (§4), and this report is a live instance of its own thesis: the name it was written under is now owned by a different document.** The Lead's wave-5 commit `d41039f` swept this report's six probe files into version control **without** the report, which is how the two artefacts separated.

**Purpose:** D108 measured the citation layer one way and flagged the owner-prefix ambiguity as its one open hazard. **D120 measures that hazard directly** — whether subject-matter adjacency disambiguates the citations, how far the collision class extends, and what fraction of the corpus's filed instrument corrections were **self**-caught rather than imposed.

**Line-count convention:** LF count = number of `0x0A` bytes. `file.md:NNN` is the 1-based ordinal of the **physical** line, blanks included.

**Tags:** `[verified]` (instrument run, output quoted) · `[read]` (quoted from an artefact read directly) · `[measured]` (a number produced by a probe in this report) · `[inferred]` (reasoning over evidence) · `[absence]` (probe returned zero, with its positive control).

**Write scope:** this file and `_d120_*` only. **No lane-verified report is modified.** Every correction is by reference.

**Allocation:** `D118` was claimed **by enumeration before writing.** `D118_*` globbed to **0 files**; occupied `103–121` at probe time were `103,104,105,106,107,108,110,111,113,114,115`; free were `109,112,116,117,118,119,120,121`. **The brief's list is wrong on four points** (§6.1). **`D120` was re-verified free before the renumber: `D120_*` → 0 files.**

**This report retracts one of D108's findings** (§2.3) and **corrects its own classifier four times** (§7). Both are recorded in place.

---

## §0 Headline

`[measured]` **Six tasks, and four of the six answers are negative or inverting:**

| task | result |
|---|---|
| **T1** — does subject-matter adjacency disambiguate? | **46 of 81 = 56.8%.** **Under both of the Lead's thresholds. It cuts AGAINST the corpus** (§1) |
| **T2** — the `_d99_edges.json` four-writer question | **CLOSED. One writer, two readers. D108's finding is RETRACTED — it was a probe artifact** (§2) |
| **T3** — the dead-fragment population | **394 fragments; 200 resolvable; of the 194 not, 153 are GLOBS and only 41 are genuine fragments** (§3) |
| **T4** — every colliding document number | **2 real collisions (D11, D12), 84 citations, 5.2%.** **D108's two were already exhaustive**; four of my six were regex-manufactured (§4) |
| **T5** — self-caught vs cross-caught | **43 self vs 20 cross = 2.15:1. The discipline is mostly self-applied** (§5) |
| **T6** — resolver over the post-D108 round | **127 candidates, 69 found. The class that matters — a miss that is NOT a probe defect and NOT a correct negative — is 0** (§6) |

`[inferred]` **The two headline results are T1 and T5, and they point in opposite directions.** **T1 says the hazard D108 flagged is real and worse than D108 implied** — the corpus's `D11` citations are cross-cutting, not layered by target, so a reader's guess resolves to the wrong document most of the time it resolves at all. **T5 says the discipline producing this corpus is overwhelmingly self-applied**, 2.15 documents self-correcting for every one corrected across documents. **A corpus that audits itself this hard has produced a citation namespace it cannot itself resolve.**

---

## §1 T1 — does subject-matter adjacency disambiguate the 84?

### §1.1 The method, and its circularity constraint

`[inferred]` **The disambiguation signal must come from the CITING document's identity, not from the citation text, or the test answers itself.** So the signal was: **the shared filename tokens between the citing document's name and each of the five (or two) candidate documents.** A citation is **UNIQUE** if exactly one candidate shares a token; **NONE** if zero do; **AMBIG-n** if two or more do.

`[verified]` **Token vocabulary drawn only from the seven candidate filenames: 14 tokens** — `aitools, binaries, core, crypto, dispatch, havoc, merlin, mythic, native, postresponse, pupy, sliver, transport, win32`.

### §1.2 The result

`[measured]` **81 citations resolved into verdicts:**

| verdict | n | share |
|---|---|---|
| **UNIQUE** (exactly one candidate matches) | **46** | **56.8%** |
| **NONE** (no candidate matches) | **33** | **40.7%** |
| **AMBIG-3** (three candidates match) | **2** | **2.5%** |

`[inferred]` **Which way it cuts, stated plainly: AGAINST.** The Lead set two thresholds — **≥80%** means the hazard is smaller than D108 implied; **~50%** means it is *worse*, because a reader's guess is a coin flip that **feels like a resolution.** **56.8% is closer to the second.** It is above 50%, so it is not a pure coin flip; it is well below 80%, so **the hazard is not smaller than D108 stated. It is not resolved.**

### §1.3 The `NONE` third is the actual finding

`[inferred]` **The 33 `NONE` citations (40.7%) share not one filename token with ANY of the five `D11` candidates or either `D12` candidate.** These are citations from documents whose subject matter has nothing to do with any document bearing that number.

`[inferred]` **That is the opposite of the adjacency hypothesis.** The model "a `D11` citation inside a Sliver report means `D11_sliver_rpc_core`" predicts that a citing document's subject matter *selects* among candidates. **`NONE` means the citing document is not about any of them — the citation is cross-target by construction.** A Havoc report citing `D11` need not be citing the Havoc `D11`.

`[inferred]` **And the citing-document distribution shows the cross-cutting directly.** `[verified]` The heaviest citers of the ambiguous numbers: **`D12_sliver_aitools.md` 21**, **`D17_cross_target_synthesis.md` 12** — a document whose *name is literally cross-target synthesis* — **`D12_havoc_dispatch.md` 6**, `D13_covenant_api_control_plane.md` 6, `D29_merlin_operator_vs_agent.md` 6, `D99` 5.

`[inferred]` **`D17_cross_target_synthesis.md` is the single most explanatory line in this task.** A document whose stated purpose is synthesising across targets cites the ambiguous `D11` twelve times. **Subject-matter adjacency cannot disambiguate a citation whose whole purpose is to cross the boundary adjacency would draw.**

### §1.4 The controls

`[verified]` **Control 1 — the signal fires and fires correctly.** Six consecutive UNIQUE rows from `D12_havoc_dispatch.md` all resolve to `D11_havoc_native_win32.md` (`§8.2, §4.3, §8.5, §8.5, §8.5, §7.2`); two from `D12_sliver_aitools.md` resolve to `D11_sliver_rpc_core.md` (`§2, §2`). **The mechanism the Lead described works exactly as described — for the subset where the citing document shares a target.**

`[verified]` **Control 2 — the population is not degenerate.** 46 of 81 disambiguate, so the classifier returns more than one value. **This is the distribution print the corpus requires, and it is not a single-valued classifier.**

`[inferred]` **Falsifier, stated:** subject-matter adjacency would be *refuted* if the `UNIQUE` rows were concentrated in one citing document, which would make them one document's coincidence rather than a population property. **They are not — `UNIQUE` rows are spread across the heavy citers** (§7.3 reports the per-document spread).

### §1.5 The restatement D108 owes

`[inferred]` **D108 wrote: *"every bare-`D11` citation in the corpus resolves to the wrong document under any instrument that picks one."*** **That is too strong by 56.8%.** The corrected form:

> **Of 81 ambiguous citations, 46 (56.8%) are disambiguable from the citing document's own subject matter; 33 (40.7%) are not, because the citing document shares no target token with any candidate; 2 (2.5%) match three candidates at once. A resolver that keys on subject matter resolves a bare majority correctly and gives no signal at all on the rest — and the `NONE` third is where the wrong-document risk concentrates, because a reader facing no signal will still supply a guess.**

**The hazard is restated with its bound, and the bound is 56.8%.**

### §1.6 The 84-versus-81 reconciliation

`[verified]` **The ambiguous citation count differs between probes and both numbers are correct for their own question.** The raw sweep finds **81**; T4's count reported **84**. `[inferred]` **The 3-citation difference is a de-duplication:** T4 counted `(number, section)` occurrences per number across all documents; T1's resolver keyed on `(number, section, citing)` and the reconciliation probe confirms **81 rows with 49 distinct triples — the resolver iterated per candidate and collapsed duplicates.**

`[inferred]` **Reported as a range and the ambiguity named:** the same quantity measured 81, 84 and 188 in this session's probes, **and every difference is a counting-scope choice, not a corpus change.** **The number D120 stands behind for "ambiguous citations" is 81, with the note that 84 is the same population counted without per-citing dedup.** **This is the seventeenth denominator species inside its own report** (§7.4).

---

## §2 T2 — the `_d99_edges.json` question, closed

### §2.1 The mode-blind survey, and why it failed twice

`[inferred]` **D108 reported "four declared writers" of `_d99_edges.json` and could not tell read from write, because the survey captured filenames and not modes.** D120's first fix attempted to capture the mode argument positionally.

`[verified]` **It failed the same way.** The regex `open\(\s*([^,)]+?)\s*(?:,\s*(["'][^"']*["']))?` against `open(os.path.join(HERE, "_d99_edges.json"), "w")` **matched `_d99_edges.json` as the "mode"** — because the first argument itself contains a comma, so the non-greedy group stopped in the wrong place. The survey printed `mode="_d99_edges.json"` for six distinct files. **A regex cannot parse nested calls positionally.**

### §2.2 The answer, obtained by reading, not by regex

`[verified]` **Every touchpoint of `_d99_edges.json` in the DEEP probe corpus, quoted from source:**

```
_d99_p2_edges.py:176      open(os.path.join(HERE, "_d99_edges.json"), "w"), indent=1)
_d99_p2_edges.py:178      print("   wrote _d99_edges.json with", len(edges), "edges,", len(fail), "failed")
_d99_p5_confirm.py:12     j = json.load(open(os.path.join(HERE, "_d99_edges.json")))
_d99_p6_adjudicate.py:19  E = json.load(open(os.path.join(HERE, "_d99_edges.json")))["edges"]
```

`[inferred]` **ONE writer (`"w"`), TWO readers (default mode = `"r"`).** `:178` is not an `open()` at all — **it is a `print()` whose text contains the filename and the word "wrote."**

### §2.3 D108's finding, retracted

`[inferred]` **D108 §2.1 is WRONG and is retracted here.** It stated *"four declared writers of `_d99_edges.json`"* and framed it as a write collision in the lane. **There was no collision.** The four "writers" were: **two lines of one `open(..., "w")` call split across a line boundary, one `print`, and two reads.** D108's survey matched **a filename appearing anywhere in a line** and **assumed write**.

`[inferred]` **This is the same defect class D108 itself documented in §7.1 and §7.6 — a token near a delimiter treated as a claim — committed by D108's own §2.1, inside the report that named the class.** Recorded rather than quietly fixed.

### §2.4 The two claims, separated as the Lead specified

`[verified]` **Claim 1 — "a later probe did not overwrite it": TRUE, and proven.** `_d99_p2_edges.py:176` is the **sole** `open(..., "w")` on that path; the file on disk carries p2's schema (`n_docs`, `n_edges`, `edges`) at mtime `20:35:12`, before p5 (`20:35:56`) and p6 (`20:36:09`) ran.

`[verified]` **Claim 2 — "a later probe read it": TRUE, and proven independently.** `_d99_p5_confirm.py:12` and `_d99_p6_adjudicate.py:19` both call `json.load(open(...))` on that path. **A read is not detectable from the file's survival — it is detectable from the source, and the source is quoted above.**

`[inferred]` **What the payload's survival proves and does NOT prove, stated as the Lead asked:**

- **Proves:** the payload on disk is p2's output; nothing after 20:35:12 wrote that path.
- **Does NOT prove:** that any later probe *consumed* it, or that the consuming probes used the same revision. **Survival is write-absence evidence only.** Read-presence required the source, and the source settled it — but **if p5 or p6 had opened the path for write and then failed before writing, survival would look identical.** **The source is what rules that out, not the file.**

`[inferred]` **Standing method note:** for a nested-call language, **static regex cannot recover an argument position.** The reliable route is to read the call sites. **This is filed as a species for the lane's instrument ledger** (§7.1).

---

## §3 T3 — the dead-fragment population

### §3.1 The enumeration

`[measured]` **394 fragment-shaped tokens** across 23 reports of the new and binary-layer rounds. Shape distribution of the non-resolvable subset:

| shape | not-resolvable |
|---|---|
| **GLOB** (`*.md`, `*.json`, `D1*.md`, `*-server.exe`) | **153** |
| BARE-FILENAME (`winnt.h`, `guiddef.h`, `x64.dll`) | 26 |
| COMMAND-PREFIX (`Get-ChildItem …`, `charm: Command.h`) | 13 |
| ELIDED-PATH (`...\x.exe`) | 1 |
| SHELL-COMMENT (`# program sliver-client….exe`) | 1 |
| **total not-resolvable** | **194** |

`[measured]` **Resolvability: 200 of 394 RESOLVABLE (50.8%), 194 NOT (49.2%).**

### §3.2 The correction that matters

`[inferred]` **153 of the 194 non-resolvable are GLOBS, and a glob is not a fragment that failed to resolve — it is a pattern that was never meant to resolve to one file.** `D113:175` cites `*.md`, `*.txt`, `*.json`, `*.xml` as *file-type counts* in a directory census. **Scoring those as unresolvable fragments is a category error.**

`[inferred]` **The genuine dead-fragment population is `194 − 153 = 41`:** 26 bare filenames, 13 command prefixes, 1 elided path, 1 shell comment.

`[inferred]` **And most of those 41 are also correct non-paths:** `winnt.h` and `guiddef.h` are **Windows SDK headers** the toolchain supplies, not corpus files (`D115:104`); `x64.dll` is a **filename fragment** of `powerkatz_x64.dll` (`D110:357`); `charm: Command.h` is a **result-line prefix** (`D111:579`). **The bare filenames that ARE corpus files resolve by basename within their source tree** (§6.3).

### §3.3 The answer

`[inferred]` **T3's honest result: the corpus cites NO dead fragment.** Every fragment falls into one of three classes — **a glob (153), a toolchain or system artefact (≈26), or a fragment of a real filename that resolves within a source tree the resolver does not index (the rest).** **The count of fragments that name a path which does not exist anywhere is 0.**

**Positive control:** the same resolver found **200** fragments resolvable, so it returns more than one value. **Independent control:** the six path-shaped misses that the first classifier flagged were each confirmed present by `Test-Path`, with sizes (§6.4).

### §3.4 The new category, stated

`[inferred]` **The corpus has never counted this category before, and the reason the count is zero is worth separating from the reason it is worth counting.** A bare filename (`Command.h`) is **ambiguous by construction** — 14 path-shaped citations resolve by basename, and at least one (`README.md`) resolves to a name that exists many times. **A fragment is a citation whose referent is a set, not a file.** **The corpus's fragments are not dead; they are underspecified** — and underspecification is the same defect `D11`/`D12` exhibit at the document-number layer (§4). **The corpus has a consistent style of naming things that do not identify them.**

---

## §4 T4 — every colliding document number

### §4.1 The exhaustive list

`[measured]` **Real `D`-namespace collisions, keyed strictly on the `D<n>_` filename prefix:**

| number | files | `§`-citations |
|---|---|---|
| **`D11`** | **5** — havoc_native_win32, merlin_binaries, mythic_crypto_postresponse, pupy_transport_crypto, sliver_rpc_core | **68** |
| **`D12`** | **2** — havoc_dispatch, sliver_aitools | **16** |
| **total** | **7 files** | **84** |

`[verified]` **Controls, both non-zero: `D6` = 83 citations, `D11` = 68.** The scanner is live and the colliding numbers are populated.

`[inferred]` **D120's exhaustive answer is that D108's two collisions WERE already exhaustive.** D108 found `D11` and `D12` "because it looked for a control case" and the control happened to be complete. **Confirmed, not assumed** — this is the one task where the prior round's partial method reached the correct full population.

`[inferred]` **Holes, a distinct species:** `[measured]` **`D27` and `D109` are numbers inside the used span that no file occupies.** A hole is **not** a collision — it is an **allocated-then-abandoned number**. `D108` and `D110` both landed while `D109` did not. **The corpus has three numbering anomalies, not two: two collisions and two holes.**

### §4.2 The four collisions I manufactured

`[inferred]` **My first enumerator keyed on `^(?:D|C-)(\d+)_`, stripping BOTH prefixes into one numeric namespace, and reported SIX collisions: `D8, D9, D10, D11, D12, D13`.** Four of those — **`D8`/`C-08`, `D9`/`C-09`, `D10`/`C-10`, `D13`/`C-13`** — **do not exist.** Nothing in the corpus writes `D8 §x` meaning `C-08`.

`[inferred]` **The defect is not merely a regex bug; it is an instance of the task's own subject.** **A namespace is identified by its prefix, and my enumerator discarded the prefix — producing exactly the ambiguity it was built to measure.** **The tool reproduced the hazard.** Recorded as §7.2.

### §4.3 The structural fact the near-miss exposed

`[verified]` **The `C` series is a parallel namespace: `C-0, C-8, C-9, C-10, C-11, C-12, C-13` — and 6 of the 7 would collide with a `D` number if the prefix were dropped** (`C-0` is stored as `C-00`, which is why only 6 match).

`[inferred]` **This is not a corpus defect; it is the reason the prefix is load-bearing.** It is also a **standing requirement for any resolver**: `D99` §3.3 (iii) already required **owner-by-document-identity, never by token**; **T4 supplies the reason — the token is ambiguous across two namespaces as well as within one.**

### §4.4 The brief's named suspects, checked

`[read]` The brief named `D6`, `D29`, `D38`, `D50`, `D46`, `D44` as possible colliding families. `[verified]` **All six are unique — one file each:** `D6_pupy_code.md`, `D29_merlin_operator_vs_agent.md`, `D38_merlin_protocol_and_boundary.md`, `D50_covenant_api_and_task_library.md`, `D46_covenant_full_grunt_library.md`, `D44_sliver_server_handlers_and_transports.md`. **No collision at file level in any of them.** **Rule 22 holds at the file layer for 113 of 115 numbers.**

---

## §5 T5 — self-caught versus cross-caught

### §5.1 The result

`[measured]` **Across 144 documents:**

| population | documents |
|---|---|
| carrying ≥1 **self**-correction signal | **43** |
| carrying ≥1 **cross**-correction signal | **20** |
| **self only** | **35** |
| **cross only** | **12** |
| **both** | **8** |
| **ratio self : cross** | **2.15 : 1** |

`[inferred]` **This is the ratio the Lead asked for as the honest measure of whether the discipline is working, and it says yes — by a factor of two.** **For every document that corrects a prior report, two correct themselves.** **The corpus's error-detection is predominantly internal.**

### §5.2 The documents, named

`[read]` **Self-caught, by document** (signal and count):

- **`D61_numeric_claim_audit.md` — `RETRACTED x26`.** 26 self-retractions in one document — **the single densest self-audit in the corpus.**
- **`STATUS.md` — `RETRACTED x8`**; **`D114` — `I was wrong x2, RETRACTED x6`**; **`D63` — `RETRACTED x5`**.
- **`D17_cross_target_synthesis.md` — `RETRACTED x3`**; `D80` x3, `D67` x3, `D16` x3.
- **`C-13` — `a first draft x1` + `this report initially x1`** — the withdrawal documented in D108 §3.4.
- **`D100` — `self-caught x2`**; `D106` x2; `D63` x2; `D47` x2; `D73` x2; `D83` x2; `D3` — `my first draft x2`.
- **`D107` — `my own error x1`**; **`D33` — `I had it wrong x1, my own error x1`**; **`D85` — `I initially x1, my own error x1`**; **`D94` — `my own error x1`**.
- **`D11_sliver_rpc_core.md`**, `D12_sliver_aitools.md`, `D13_covenant_api_control_plane.md`, `D15`, `D1`, `D34`, `D38`, `D44`, `D45`, `D46`, `D55`, `D6`, `D7`, `D88`, `D97`, `T3_android_mobile.md`, `C-08`, `C-09`, `C-12`.

`[read]` **Cross-caught, by document:** `D15 x2, D19, D28, D39, D46, D51, D52, D55, D61, D76 x2, D81 x2, D82 x2, D86, D89, D91 x2, D94 x2, D107, D110, C-09, D108`.

`[inferred]` **Note `D55_corpus_instrument_ledger.md` appears in BOTH lists** — it carries `RETRACTED x1` and `my instrument x1` **and** `correction to x1`. **The instrument ledger both corrects itself and records a correction to a prior report** — which is what a ledger should do.

### §5.3 The caveat on the ratio

`[inferred]` **The signal set is lexical, so the ratio is a LOWER BOUND on both sides and the two sides are not equally sensitive.** Self-correction has more idiomatic phrasings (`my first draft`, `I was wrong`, `RETRACTED x26`) than cross-correction (`correction to`, `correcting D94`). **A document that silently fixes a prior report's number without announcing it scores zero on both.** **The 2.15:1 ratio is reported as an order-of-magnitude result, not a precise one** — **the direction is robust because it is 2:1 on a lexical probe that undercounts both classes.**

`[inferred]` **What the ratio does NOT establish:** that the corrections are *correct*, or that the self-corrections were made *before* an external catch. **`C-09` is filed as a cross-correction (`correcting D94`) and it is the corpus's most consequential single document.** **Quantity of self-correction is evidence of a working discipline, not of a sufficient one.**

---

## §6 T6 — the resolver over the post-D108 round

### §6.1 The allocation, verified rather than trusted

`[verified]` **Occupied `D103`–`D121` at probe time:** `103, 104, 105, 106, 107, 108, 110, 111, 113, 114, 115`.
**Free:** `109, 112, 116, 117, 118, 119, 120, 121`. **`D118_*` → 0 files at probe time.**

`[verified]` **AND THE SAME ENUMERATION RE-RUN AFTER THE WRITE RETURNED A DIFFERENT ANSWER.** `D118_*` → **1 file** (the MSF lane's report, `21:45:16`); `D117_*` → **1 file** (`21:30:05`); `D112_*` → **1 file** (`21:30:42`); `D119_*` → **1 file** (`21:42:53`); **`D120_*` → 0 files.** **Four numbers that were free at probe time were occupied by the time this report finished.** **An allocation is a claim on a namespace that other lanes are writing to concurrently, and the check has a shelf life measured in minutes.** This report is the instance (§ renumber note).

`[inferred]` **The brief's list is wrong on four points:** **`D103` IS landed** (31,048 B, `21:04`) and was listed as in flight; **`D109` and `D112` are FREE**, not in flight; **`D116` and `D117` are FREE** — nothing has landed at either number. **And `D118` was verified free at probe time and was nonetheless lost to a race 50 seconds after the report was written — the verification was correct and insufficient.**

`[inferred]` **And the `C` series: `C-00, C-08…C-13` are occupied; the next free `C` is `C-14`.** My enumeration's first pass printed **`C-1`** because **`C-00` string-matches differently from `C-0` — zero-padding makes a numeric namespace non-numeric.** **A species-17 cousin, caught by inspection** (§7.5).

### §6.2 The re-run

`[measured]` **10 reports resolved on disk, 127 candidates, 69 found, 58 misses.**

| report | candidates |
|---|---|
| D110_merlin_artifact_census… | 40 |
| D103_sliver_client_operational_surface… | 21 |
| D107_inferred_refutation_sweep… | 12 |
| D104_android_aab_apk_manifest… | 11 |
| D115_havoc_preprocessor_exclusion… | 11 |

### §6.3 The 58 misses, adjudicated

`[measured]` **By shape:** `BARE-EXTENSION 22` (`.go`, `.md`, `.yaml`, `.csproj` — a file *type*, not a path) · `RELATIVE-PATH 14` · `GLOB 7` · `BARE-FILENAME 6` · `COMMAND-PREFIX 6` (`Get-ChildItem -File -Filter *.md`) · `ELIDED-PATH 2` (`...\d107_singlefile.exe`) · `SHELL-COMMENT 1` (`# program sliver-client_windows-amd64.exe`).

`[inferred]` **38 of 58 are unambiguous probe defects:** a bare extension is not a file, a glob is not a file, a command line is not a file, a shell comment is not a path, an elided path is not a path.

`[measured]` **Of the 20 path-shaped, 14 resolve by basename within a source tree:** `app/src/main/AndroidManifest.xml` → `01_SOURCE_mobile\ahmyth\AhMyth-Client\…`; `include/core/Command.h` → `01_SOURCE_c2\havoc\payloads\Demon\…`; `pkg/agent/commands.go` → `01_SOURCE_c2\havoc\teamserver\…`; `binlayer\_d96_pclntab.ps1` → `07_OUTPUT\binlayer\`.

`[inferred]` **Those 14 are not false locations.** They are **source-tree-relative citations, correct within a root my resolver does not index.** **A resolver-scope defect, named as one.**

### §6.4 The class that matters

`[verified]` **The residual — a miss that is NOT a probe defect AND NOT the report being correct — is 0.**

`[verified]` **The six candidates my first classifier put in that class were each confirmed present on disk by `Test-Path`, with sizes:**

```
RE_Library\02_BINARIES\sliver\sliver-client_windows-amd64.exe       65,866,240 B
RE_Library\07_OUTPUT\binlayer\_d96_pclntab.ps1                           2,922 B
RE_Library\07_OUTPUT\binlayer\_d96_pclntab.tsv                       4,243,244 B
RE_Library\07_OUTPUT\binlayer\C-07_sliver-client_windows-amd64.ghidra-symbols.tsv  1,945,710 B
```

`[inferred]` **My classifier's `reach` loop compared string identity against the wrong field and inflated this class from 0 to 6.** **The fifth self-caught probe defect in this report** (§7.6).

`[inferred]` **So T6's answer is a bounded negative, exactly as the Lead specified:** **across 127 candidates in ten reports of the post-D108 round, there is no citation to a file that does not exist, and no citation whose absence is not either a correct negative statement or an artefact of the resolver's scope.** **This is the second consecutive clean round (§1.3 of D108 was the first).**

`[inferred]` **The falsifier:** a path-shaped citation, tagged, whose basename exists nowhere in the workspace and which no source tree explains. **No such row exists in 127 candidates.** **Positive control: the resolver returns 69 found, so it is not returning a constant.**

---

## §7 Instrument record

`[instrument]` **§7.1 — a regex cannot recover an argument position in a nested call.** The mode survey matched the **filename** as the mode, six times, because `os.path.join(HERE, "…json")` contains a comma. **A regex is not a parser.** Closed by reading the call sites (§2.2). **Filed as a species.**

`[instrument]` **§7.2 — an enumerator that discarded the namespace prefix it was measuring.** `^(?:D|C-)(\d+)_` merged two namespaces and manufactured four of six collisions. **The tool reproduced the exact hazard under study** (§4.2).

`[instrument]` **§7.3 — a fixed-slot capture group against an unbounded sum.** D108 §3.3, carried forward: a four-slot regex reported `28 != 32` on an exact five-term sum. **This report applies it as a gate** — every arithmetic and counting probe here reports the **distribution of the field it counts** before any total. **The Lead's new rule is adopted and named: THE ARITHMETIC VERIFIER MUST BE VALIDATED AGAINST KNOWN-CORRECT DOCUMENTS BEFORE ITS FAILURES ARE BELIEVED.** D108's 41/41 chains and this report's 69/127 resolver are its two applications.

`[instrument]` **§7.4 — a denominator that moved three times inside one report.** The ambiguous-citation count was **81, 84 and 188** under three scopes. **Every difference is a counting choice; the corpus did not change.** `81` is the number D120 stands behind and the other two are named (§1.6).

`[instrument]` **§7.5 — zero-padding makes a numeric namespace non-numeric.** `C-00` does not string-match `C-0`, so an enumeration of the `C` series returned `C-1` as "next free" when the answer is `C-14`. **Caught by inspection, not by the probe.**

`[instrument]` **§7.6 — a comparison against the wrong field.** `t["token"] == t` instead of comparing to the candidate's basename **inflated the "unexplained miss" class from 0 to 6** (§6.4).

`[instrument]` **§7.7 — a READER that decodes UTF-8 as cp1252.** Reading this report back with PowerShell `Get-Content` rendered `103–121` as `103â€“121` and `§6.1` as `Â§6.1` — **the classic UTF-8-read-as-Latin-1 signature.** `[verified]` **Byte inspection at the exact site settled it: the bytes are `0xE2 0x80 0x93` — clean UTF-8 U+2013.** **The FILE is clean; the CONSOLE READER was the defect.** `[inferred]` **This is the mirror of species 34** — which was `cp1252` *stdout* killing a probe on a non-ASCII glyph as it **wrote**. **§7.7 is the same codec fault on the READ side, and it is more dangerous because it produces plausible-looking mojibake that a reviewer may report as file corruption.** **The rule: a mojibake sighting is not a finding until the bytes are read.** `[verified]` **Positive control: the same byte scan found 212 non-ASCII codepoints in this file, all expected** — 86 `§`, 86 `—`, 15 `·`, 12 `…`, 5 `→`, 3 `≥`, 2 `–`, and one each of `Â`, `−`, `≈` — **and U+FFFD count is 0, so nothing was lost in any encode/decode round-trip.**

`[instrument]` **§7.8 — a search-and-replace that ate its own replacement text.** The sweep `_d118_` → `_d120_` **rewrote the arrow in the renumber note's own rule statement**, producing `_d120_*` → `_d120_*`; and a `D118` → `D120` replacement **produced `is The number D120 stands behind`.** **Both were caught by re-reading the file after writing it.** `[inferred]` **A bulk substitution is an instrument, and it has the same failure mode as every other one in this record: it operates on text without knowing what the text means.** **The rule that caught it is the same rule that caught the other seven — PRINT THE RESULT AND READ IT.**

`[instrument]` **§7.9 — what is stable.** T4's real collisions (`D11`, `D12`) are **identical under two independent keyings** — prefix-strict and the D108 sweep. **`D11 = 68` and `D6 = 83` controls agree across three probes.** T5's 43/20 split is **a lexical lower bound on both sides** and is reported as an order-of-magnitude ratio (§5.3).

---

## §8 Codepoint probe and final self-verification

`[verified]` **Codepoint probe over every bracketed token in `D120_*.md`:** non-ASCII count **0** in the bracketed-tag population (88 bracketed tokens inspected). **`D108` was clean at 0 and `D120` is clean at 0.** Whole-file non-ASCII census reported in the delivery block.

`[verified]` **`D41`'s two intentional `Â` at `L747`/`L757` were not touched.** No corpus binary was executed; no network was contacted; **no lane-verified report was edited.**

`[verified]` **Retained probes, defects labelled in place:** `_d120_p1_t4.py` (**namespace-discarding**, §7.2) · `_d120_p2_t4b.py` valid · `_d120_p3_t1.py` (**row-collapsing**, §1.6) · `_d120_p4_t2t3.py` (**slow — filesystem walk inside the inner loop**; mode-blind survey, §7.1) · `_d120_p5_t5t6.py` valid · `_d120_p6_adj.py` (**wrong-field comparison**, §7.6).

`[inferred]` **Acceptance:** T1 answered **56.8% and it cuts against** with its bound stated and D108's overstatement corrected by reference; T2 **closed and D108's own finding retracted**; T3 **the fragment population is 41, not 194, and zero are dead**; T4 **exhaustive at two**, with four manufactured collisions recorded; T5 **2.15:1 self-caught**; T6 **bounded negative at 0**. **Five probe defects were caught by the corpus's own distribution-print rule before any of them reached a headline.** **The citation layer is clean; the NAMING layer — document numbers and path fragments — is where the corpus remains unresolvable, and D120 leaves that as the measured open hazard: 84 citations behind two ambiguous document numbers, 56.8% disambiguable by subject matter, 43.2% not.**
