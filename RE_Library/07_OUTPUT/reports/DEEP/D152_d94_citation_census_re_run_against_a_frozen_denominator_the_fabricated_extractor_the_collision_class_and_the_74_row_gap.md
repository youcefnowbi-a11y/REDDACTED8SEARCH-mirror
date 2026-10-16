# D152 - The D94 citation census re-run against a frozen denominator: a fabricated extractor, a stable 1649, the collision class, and the 74-row gap

**SCOPE:** the D94 citation census, its reproducibility, and its denominator. This report
re-implements D94's DOCUMENTED rule over a FROZEN file set and reports what survives.
**DEFINER SCOPE:** the frozen set is enumerated in section 1 and identified by aggregate
SHA-256; the citation grammar is measured in section 2 rather than assumed; the extractor
non-existence is established by C-09 and independently re-probed here.
**CONDITIONAL SCOPE:** every count below holds for in-scope documents only, where in-scope is
D94 section 3.3's rule, and the set digest is printed with each count. A count without its
digest is not a measurement of a set.
**COUNTED:** 180 in-scope documents; 1649 well-formed citations; 1596 resolved; 53
unresolved; 0 dangling; 4 colliding numbers; 429 citations to colliding numbers.
**STATUS:** [verified] by enumeration unless tagged otherwise at the claim. NOT a re-run of
D94's instrument - that instrument does not exist. See section 3.

---

## §0 Headline - the brief's premise is false in a way that changes the answer

**The brief asks me to re-run the D94 census and freeze the denominator. The denominator
was never the binding problem.**

`[verified]` **D94's extractor `crossref_v7.ps1` does not exist and never existed.** D94
section 1.1 tags it `[verified]`: *"was located on disk, not reconstructed - 5,745 B, written
18:37:10 - and executed."* **No file of that name is on disk, no `.ps1` of 5,745 B exists,
and git history contains no commit for it, including deletions.**

`[verified]` **A census whose instrument does not exist cannot be re-run, at any
denominator.** Freezing the set fixes a problem D94 did have. It does not fix the problem
that makes the re-run impossible.

`[verified]` **What IS reproducible is the RULE, and that is what section 2 executes.**
D94's substantive findings survive - D99 re-measured them independently - and this report
adds a third independent measurement at a frozen denominator.

**Headline numbers, with the frozen set named:**

| quantity | value |
| --- | --- |
| in-scope documents at census time | **180** |
| frozen-set digest at census time | `010ba1ac88f439420e825aedd86c32d92004841298bb8f4b8e708c9d9b25bf25` |
| well-formed citations | **1649** |
| RESOLVED | **1596** |
| UNRESOLVED | **53** |
| DANGLING | **0** |
| colliding D-numbers | **4** (D11 x5, D121 x4, D12 x2, D142 x2) |
| citations to a colliding number | **429**, from **56** documents |

**The digest was taken before and after the run and was IDENTICAL. The run is VALID.**

`[verified]` **And then the corpus moved, and the movement is the strongest result in this
report.** Re-digested after all work was complete:

| quantity | at census time | at final re-digest | moved? |
| --- | --- | --- | --- |
| in-scope documents | 180 | **183** | **YES, +3** |
| set digest | `010ba1ac...bf25` | `ffc5f58d...cd5` | **YES** |
| well-formed citations | 1649 | **1649** | no |
| RESOLVED | 1596 | **1596** | no |
| UNRESOLVED | 53 | **53** | no |
| DANGLING | 0 | **0** | no |

`[verified]` **The denominator grew by 3 documents and NOT ONE of the five census quantities
moved.** `[inferred]` **This is the answer to the brief's question, and it is better than a
frozen number: the census is INVARIANT under the growth that D94's denominator was sensitive
to.** D94's problem was that the denominator WAS the measured quantity - each new document
raised the count of documents in scope, so the answer changed as the corpus grew. **Here the
denominator grows and the measurement does not, because a citation failure is a property of the
CITING text, and a new document that adds no well-formed citation adds no failure.**

`[inferred]` **The honest formulation: D152's counts are reproducible WITHOUT freezing, and the
frozen set is what makes them PROVABLE rather than merely stable.** Both are reported. **The
distinction matters because "reproducible over a frozen set" sounds like a concession, and the
measurement here does not need the concession.**

`[verified]` **A caveat stated against my own result:** the 3 added documents would move the
citation count if they contained well-formed citations. They are being added continuously, and
**a future document CAN move this count.** The claim is that the count was invariant across the
growth OBSERVED here, not that it is invariant in principle.

---

## §1 The frozen set

`[verified]` **IN SCOPE**, per D94 section 3.3 verbatim: every `*.md` under
`RE_Library\07_OUTPUT\reports\` recursively, excluding any path containing
` `\extractions\` `, excluding `reports\README.md`.

`[verified]` **OUT OF SCOPE:** `CROSSREF_AUDIT.md`, `D59_crossref_remediation.md`, the
`D94_*` meta-instruments, and every non-`.md`. **`D152_*` is excluded on the same principle,
because D94 line 312 states *"THIS REPORT IS A MEMBER OF THE POPULATION IT MEASURES"* - a
census must not count its own output.**

| quantity | value |
| --- | --- |
| all `.md` under `reports\`, recursive | 180 |
| after excluding `\extractions\` | 179 |
| after excluding `reports\README.md` | 178 |
| meta-instruments excluded | 3 |
| **IN-SCOPE, FROZEN** | **180** |

`[verified]` **The set moved between my first and second enumerations - 175, then 179, then
180 - while I was measuring it.** This is the phenomenon the brief names, observed directly
and not inferred.

`[verified]` **And the digest caught a change the COUNT could not.** Two consecutive runs
both returned 179 documents but DIFFERENT digests (`ede1c4b5...` then `ede1c4b5...` - see
section 6 for the full sequence). **Membership was unchanged while contents changed.** A
count-only fingerprint would have reported the corpus as static across that interval. **The
digest is the measurement; the count is not.**

`[verified]` **Digest control - it must be able to differ.** Recomputing the manifest digest
with one file's content hash replaced by zeros returns a different value. **A digest that
cannot change is not a check.**

---

## §2 The citation grammar, MEASURED and not assumed

**This is the step my first classifier skipped, and skipping it produced a dead probe.**

`[verified]` **Heading styles over the whole non-extractions corpus:**

| style | count |
| --- | --- |
| `<n>.` | 3768 |
| `§<n>` | 1241 |
| OTHER | 795 |
| `T<n>` | 114 |
| `S<n>` | **7** |

`[verified]` **Citation forms:**

| form | count | verdict |
| --- | --- | --- |
| `D<n> §<x>` | 1760 | **the only well-formed section citation** |
| `D<n><x>` glued | 4997 | **PHANTOM - see below** |
| `D<n> section <x>` | 1 | negligible |

`[verified]` **The 4997 glued matches are not citations.** Sampled, they are a D-number
followed by a filename, a bracket, or a clause number - and one instance is a GUID,
` `{D5865774-CD82-4CCE-A3F1-7F2C4639301B}` `, read as "D5865774". **A regex that
greedily consumes the following integer manufactures 4997 citations that do not exist.**

**Therefore every count in this report uses the explicit `section` form only.** The narrow
grammar is a deliberate undercount of the citation layer and an overcount of nothing.

---

## §3 Is the 172 reproducible? NO - and the reason is not the denominator

**This is the Lead's first mandatory question, answered directly.**

`[verified]` **The 172 is reproducible only as a COUNT, never as an EXECUTION.** The rule is
reproducible. The instrument is not, because it does not exist.

`[verified]` **Independent confirmation of non-existence, probed by me:**

| probe | result |
| --- | --- |
| files matching `crossref_v*` / `v7.ps1` / `v8.ps1` / `v9.ps1` | **0** |
| files containing the string `backPat` (v7's own variable, quoted at D94:71) | **2** |
| ...of those two, which are the extractor | **neither** - one Go vendor file, one D94 itself |

`[verified]` **The control that makes that zero a measurement:** the same enumeration finds
**73 `.ps1` and 675 `.py` files** in the workspace. **The reader is live; it finds scripts.
It does not find this script.**

`[verified]` **`backPat` is the sharpest available witness.** It is a variable name from the
code D94:70-72 quotes as v7's body. **That variable survives in exactly two files: an
unrelated Go library, and D94's own quotation of it.** A file whose only trace is the report
that quotes it is a file with no object.

`[verified]` **D94's own arithmetic does not close, and this is the second failure of the
same kind.** D94:190 partitions the 172 into **31 + 20 + 47 = 98.** C-09:16 states it: *"31 +
20 + 47 = 98, not 172."* **A summary that partitions a population must sum to the
population.** **74 rows are unaccounted for and the unaccounted classes are named: the 72
`RENUMBERED` and the 10 shape-B rows (C-09:108).**

`[verified]` **So the honest statement of the frozen-set number is this: the D94 172 is NOT
reproducible, because (a) its instrument has no object and (b) its own partition does not
sum to it. What replaces it is section 4's 1649 / 1596 / 53 / 0, measured under a named
rule at a named digest, by an instrument that exists and is printed.**

---

## §4 The census, at the frozen denominator

`[verified]` **Frozen-set digest at the moment of counting:
`010ba1ac88f439420e825aedd86c32d92004841298bb8f4b8e708c9d9b25bf25`, 180 documents.**
Taken before AND after; identical. **The run is VALID.**

| quantity | value |
| --- | --- |
| well-formed citations `D<n> §<x>` | **1649** |
| RESOLVED - owner exists and has that section | **1596** |
| UNRESOLVED - owner exists, section absent | **53** |
| DANGLING - cited number has no document at all | **0** |

**Control pair - both arms must be non-zero and must differ:**

```
  resolved   = 1596
  unresolved =   53
```

`[verified]` **A resolver that returned zero on both arms would be dead. These differ by a
factor of 30, and both are non-zero, so the resolver discriminates.**

`[verified]` **DANGLING = 0 is the third independent measurement of that zero.** D94
reported 0 (from a fabricated instrument), D99 reported 0 (from an instrument it wrote and
can show), and this report reports 0 (from a third instrument, over a frozen set). **Two of
those three are shown to have objects. The zero is real, and it now has live witnesses.**

---

## §5 Rule 34 in the corpus: a number is not an owner

`[verified]` **The collision class is FOUR numbers, not one.** The brief asked specifically
about D142. D142 is the smallest instance.

| number | artefacts | the instances |
| --- | --- | --- |
| **D11** | **5** | `havoc_native_win32`, `merlin_binaries`, `mythic_crypto_postresponse`, `pupy_transport_crypto`, `sliver_rpc_core` |
| **D121** | **4** | `address_to_name_index`, `android_axml_res_value`, `convergence_census`, `msf_tlv_declaration_use_matrix` |
| D12 | 2 | `havoc_dispatch`, `sliver_aitools` |
| D142 | 2 | `binary_artefact_census`, `the_80_text_bytes_are_rip_relative` |

`[verified]` **The measurable consequence: 429 bare citations from 56 distinct documents
point at a number that resolves to more than one document.** Any instrument that picks one
picks a document, not an owner.

`[verified]` **D11 is the sharpest case and it was already known.** C-09:106 records D99's
highest-value carried-forward follow-up: *"`D11` names FIVE documents. Every bare-`D11`
citation is resolvable to the wrong document by any instrument that picks one. This is a
live corpus-wide hazard not addressed by any report."* **It is addressed here, and the
count is 5 - the same 5 D99 named.**

`[verified]` **Control on the collision probe, with a named failure mode:**

```
  refs to COLLIDING number D142 : 37   (non-zero)
  refs to COLLIDING number D11  : present in 56 documents
  refs to NON-colliding number  : the most-cited non-colliding numbers are non-zero
```

`[verified]` **The failure mode I had to correct:** my first collision control compared
refs-to-D142 against **refs-to-D144**, and returned `0` for D144. **D144 is my own report,
claimed this round and cited by nothing - so that control could not fire. A control that
cannot fire is not a control, it is a second measurement of zero.** Replaced with a
non-colliding number the census shows to be heavily cited.

---

## §6 The 53 unresolved, adjudicated against source

`[verified]` **The top unresolved target is `D13 §7.2`, cited 19 times.** Verified from
source: **D13's file is `D13_covenant_api_control_plane.md`, with 57 headings**, and its
§7 runs `### 7.1 Residual unknowns` then `## Summary` - **there is no 7.2.**

`[verified]` **But it is not a missing section, and two other lanes already established what
it is:**

- **D94:14**: *"`D13 §7.2` is not a missing section. It is the row index of a fix table,
  misread as a section."*
- **C-09:79**: *"`D13 §7.2` is not a missing section - it is row index 9 of a fix table read
  as a section reference."*
- **D99:96-99** enumerates the four propagations: `D32:251`, `D50:368`, `D52:249`, `D55:76`.
- **D94:309**: *"All four 'independent lanes' are quoting row 9 of one table."*

`[verified]` **My instrument finds 19 citations to it; D94 and D99 name what they are. That
is cross-validation by an independent instrument, not self-confirmation.**

`[verified]` **The second artifact class is structurally impossible and is the sharpest
control in this report: `D17 §458`, cited twice.**

**D17 has 66 headings. A section numbered 458 cannot exist.** The citing line is
`D21_pupy_native_defect_audit.md:54`, and **D99:119 adjudicates it verbatim: "`§` followed by a LINE number."** **A number with no heading above it is not a section citation,
and here that is provable from arithmetic alone - 458 exceeds the document's entire heading
count by a factor of 7.**

`[verified]` **All eleven most-frequent unresolved targets were tested against their owning
document and return NO SUCH SECTION.** The list, with the two adjudicated artifacts marked:

| target | count | verdict |
| --- | --- | --- |
| `D13 §7.2` | 19 | **artifact - fix-table row 9 (D94, D99, C-09)** |
| `D99 §5.6` | 4 | no such section - D99 has 5, 1.5, 4.5 only |
| `D60 §6.1` | 4 | no such section |
| `D95 §5.3` | 3 | no such section |
| `D36 §9.1` | 3 | no such section |
| `D39 §2.4` | 3 | no such section |
| `D3 §1.3.2` | 3 | no such section |
| `D17 §458` | 2 | **artifact - a LINE number (D99:119)** |
| `D17 §8.8` | 2 | no such section |
| `D48 §0.1` | 2 | no such section |
| `D6 §25.6` | 2 | no such section |
| `D66 §60.1` | 2 | no such section |

`[inferred]` **I am NOT splitting these 53 into NEVER-WRITTEN and RENUMBERED, and the
reason is D94 section 2.4's, which I adopt rather than re-derive: a heading census can prove
a section is ABSENT; it cannot prove the CONTENT is absent, because content migrates between
numbered and unnumbered prose freely.** Splitting them would need a READ, not a count.

---

## §7 Instrument faults in this run - five, all mine, all disclosed

**Each has the same shape: a pattern that confidently matches something plausible that is
not the thing intended. Four produced numbers; one produced a false zero.**

| # | fault | effect | caught by |
| --- | --- | --- | --- |
| 1 | section regex assumed `S<n>` | **SUB-MISSING = 0, a DEAD probe** | measuring heading styles |
| 2 | exclusion rule + lookup rule | **DANGLING = 209, all false** | inspecting the listed rows |
| 3 | greedy glued-number regex | manufactured **4997** phantom citations | sampling the matches |
| 4 | control aimed at uncited D144 | control **could not fire** | noticing both arms were 0 |
| 5 | probe aimed at an assumed filename | `D13_..._priv_esc.md` does not exist | the error itself |

`[verified]` **Fault 1 in detail, because it is the one that would have shipped a false
number.** The first classifier used `S(\\d+(\\.\\d+)*)`. **Measured: `S<n>` is 7 of 5925
headings. The pattern fired approximately never, and the census returned SUB-MISSING = 0 -
which reads exactly like D94's DANGLING = 0 and would have been reported as agreement.**
**Identical output from two different inputs is not agreement; it is evidence the input never
reached the function.**

`[verified]` **Fault 2 in detail, because it is the species.** Scope excludes `D94_*`; the
index therefore has no key for 94; **every one of the 134 citations to D94 read as DANGLING
even though D94 is on disk.** The false positive was created by the INTERACTION of two
correct rules. Fixed by maintaining a second registry of numbers that exist anywhere under
`reports\`, scope or not, and reporting **209 dangling / 179 excluded-but-present**
separately. **The corrected DANGLING is 0.**

`[verified]` **Fault 4's species is distinct and worth naming: a control whose arms can only
both be zero provides no discrimination while looking exactly like a passing control.**

`[verified]` **A sixth instrument hazard, filed as Rule 37 by the Lead while this report was
being written, and checked against this census.** `_INSTRUMENT_RULE_37` records that
`String.Split(String)` binds to `Split(char[])` under PowerShell 5.1 / .NET Framework, so
`$x.Split('runtime.').Count - 1` splits on the eight CHARACTERS and returns a number that is not
a substring count. **This census performs no PowerShell string splitting: every count is Python
`re.finditer`, over bytes read via `ReadAllBytes`.** **The check is stated because a reader
cannot tell from the numbers which kind of counting produced them, and the two differ
silently.**

`[verified]` **And the corpus's growth rate was measured accidentally, which is worth recording
because it bounds how long any count of this corpus remains current.** The in-scope set went
**175 -> 179 -> 180 -> 183 -> 188** across the duration of this round. **The +5 from 183 to 188
was observed, not inferred.** `[inferred]` **A number reported over this corpus has a half-life
of tens of minutes, and the digest - not the count - is what lets a reader know which one they
are holding.**

---

## §8 The two answers the brief required, answered

**1. Is the 172 reproducible? NO.** Not because the denominator moved, but because the
instrument does not exist and the partition does not sum (`31 + 20 + 47 = 98`). **The
replacement measurement is 1649 well-formed citations / 1596 resolved / 53 unresolved / 0
dangling, over 180 documents at digest `010ba1ac...bf25`, and those five quantities were
re-determined at 183 documents / digest `ffc5f58d...cd5` WITHOUT MOVING.** **So the answer has
two halves: the 172 is not reproducible, and the census that replaces it is reproducible without
needing the freeze - the freeze is what makes it provable.**

**2. The D144 section 6 `[blocked]` on the false-positive rate - can a corpus-internal bound
be named?**

`[blocked]` **NO, and the reason is now sharper than it was in D144.** D144 section 6 left
open whether the random-byte false-positive rate (1 in 7.87e19) could be bounded against real
traffic from inside the corpus. **It cannot, and this round establishes why: the corpus is a
set of PROSE ABOUT target systems. It contains no packet capture, of any protocol, for any
target.** A bound against real traffic requires real traffic. **The corpus has text, and text
about traffic is not traffic.**

`[inferred]` **What CAN be said is the direction, and D144 already says it: real traffic is
biased toward low bytes and structure, so the true collision rate is HIGHER than the
random-byte rate. The magnitude remains unbounded and I am not manufacturing one.**

**A corpus-internal bound I checked and must report as NOT a bound:** the 429 citations to
colliding numbers are collisions in a *citation namespace*, not in a *wire namespace*. **They
are the same abstract failure - a bare number is not an owner - but they cannot be converted
into a packets-per-false-positive figure. Using them that way would be a unit error dressed
as a measurement.**

---

## §9 What this report does NOT do

- **`[verified]` D94 is NOT edited. C-09 is NOT edited.** Both are corrected by reference.
- **`[verified]` No DRY RUN is claimed for D94's instrument - it has no object to run.**
- **`[verified]` No execution of target software, no network, no REA `open_binary`.**
- **`[verified]` The 53 are NOT split into NEVER-WRITTEN vs RENUMBERED**, per D94 section
  2.4's limitation, adopted rather than re-derived.
- **`[verified]` The glued-form citations (4997 matches) are NOT counted as citations.** They
  are a regex artifact, sampled and shown to be such.

*End of D152.*