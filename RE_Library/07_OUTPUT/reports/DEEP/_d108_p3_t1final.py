"""
D108 probe 3 -- T1 FINAL: adjudicate the 22 by reading, and test the STRONG claim.

Probe 2's 22 'not found' contain at least six species that are NOT citation
failures. Before any yield is quoted, each must be assigned, because a yield
computed over a population that includes globs, system binaries, package names
and deliberate refutations is not a yield.

THE STRONG CLAIM TEST (Lead's T1): D94's failure was a `[verified]`/`[read]` tag
on a FILE LOCATION that does not exist. So the honest population for T1 is:
   every citation where the report ASSERTS A FILE EXISTS, i.e. a location claim.
   A write-scope glob is not a location claim. A system binary is not a
   corpus artefact. A refutation is the opposite of a location claim.
"""
import os, re, sys, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
DEEP = os.path.join(WS, "RE_Library", "07_OUTPUT", "reports", "DEEP")

cand = json.load(open(os.path.join(DEEP, "_d108_p2_cand.json")))
no = [r for r in cand if not r["exists"]]
ok = [r for r in cand if r["exists"]]

# ---- species assignment for the not-found set, by READING each one
SPEC = {
 ("D95_merlin_binary_layer_agent_build_delta_cgo_export_stubs_and_extraction_path_census.md", 8):
    ("NOT-A-LOCATION", "write-scope GLOB `binlayer\\_d95_*.ps1` -- a declaration of where a probe MAY write, not a claim a file exists"),
 ("D96_sliver_client_server_absence_and_pclntab_census.md", 26):
    ("NEGATIVE-CONTROL-GOOD", "the sentence asserts the file is ABSENT ('no `gsli.tsv` on disk'). Citing a file as missing is a correct use"),
 ("D97_android_wasm_assembler_sqlite_vfs_and_jvm_tooling.md", 25):
    ("NOT-A-CORPUS-ARTEFACT", "`where.exe` is a WINDOWS SYSTEM BINARY, not a corpus file"),
 ("D98_havoc_tomap_serialization_boundary_callers_and_concurrency_surface.md", 20):
    ("NOT-A-LOCATION", "`structs.Map` is a Go SYMBOL, not a file"),
 ("D101_covenant_binary_source_pair_negative_result_and_empirical_closures.md", 15):
    ("NOT-A-CORPUS-ARTEFACT", "`Covenant.dll` named in the BRIEF as a quoted premise; the report is quoting the brief, not citing a path"),
 ("D101_covenant_binary_source_pair_negative_result_and_empirical_closures.md", 97):
    ("FRAGMENT", "`_x86.dll` is the TAIL of `powerkatz_x86.dll`; the full filename appears earlier in the same sentence and DOES exist"),
 ("D101_covenant_binary_source_pair_negative_result_and_empirical_closures.md", 107):
    ("NOT-A-LOCATION", "`Newtonsoft.Json` is a NUGET PACKAGE ID"),
 ("C-09_correction_to_d94_two_fabricated_artifact_locations_and_unclosed_arithmetic.md", 12):
    ("REFUTATION-GOOD", "C-09 asserts `crossref_v7.ps1` does NOT exist. My locate() returning None is the report being CORRECT"),
 ("C-09_correction_to_d94_two_fabricated_artifact_locations_and_unclosed_arithmetic.md", 14):
    ("REFUTATION-GOOD", "C-09 asserts `_INSTRUMENT_RULE_26_line_is_not_a_source.md` does NOT exist. Same -- CORRECT"),
 ("C-10_binary_layer_seven_targets_named_functions_one_signature_and_pclntab_substitution.md", 7):
    ("NOT-A-LOCATION", "write-scope GLOB `binlayer\\C-07_*.tsv`"),
}

print("=== T1: THE 22 NOT-FOUND, ADJUDICATED BY READING ===")
print("   MANDATORY distribution of species:")
sp = collections.Counter()
for r in no:
    key = (r["report"], r["line"])
    s, why = SPEC.get(key, ("UNASSIGNED", "needs a read"))
    sp[s] += 1
for k, v in sp.most_common():
    print("      %-26s %3d" % (k, v))
print()

print("=== every not-found row, with its species ===")
seen = set()
for r in no:
    key = (r["report"], r["line"], r["token"])
    if key in seen:
        continue
    seen.add(key)
    s, why = SPEC.get((r["report"], r["line"]), ("UNASSIGNED", "needs a read"))
    print("   [%s] %s:%d  `%s`" % (s, r["report"][:18], r["line"], r["token"][:60]))
    print("        %s" % why)
print()

# ---- THE STRONG CLAIM: a [verified]/[read] tag on a LOCATION claim
print("=== T1 STRONG CLAIM: tagged citations making a LOCATION ASSERTION ===")
tagged = [r for r in cand if r["tag"]]
print("   candidates carrying a [verified]/[read] tag :", len(tagged))
tagged_no = [r for r in tagged if not r["exists"]]
print("   ... of which NOT FOUND                      :", len(tagged_no))
print()
print("   the tagged-not-found rows (this IS the T1 hazard population):")
for r in tagged_no:
    s, why = SPEC.get((r["report"], r["line"]), ("UNASSIGNED", "needs a read"))
    print("   %s :%d  `%s`  -> %s" % (r["report"][:20], r["line"], r["token"][:44], s))
print()

print("=== T1 VERDICT ===")
bad = [r for r in no if SPEC.get((r["report"], r["line"]), ("UNASSIGNED",))[0] == "UNASSIGNED"]
refut = sum(1 for r in no if SPEC.get((r["report"], r["line"]), ("X",))[0] == "REFUTATION-GOOD")
print("   candidates                       :", len(cand))
print("   found                            :", len(ok))
print("   not found                        :", len(no))
print("     of which REFUTATION-GOOD (C-09 being right) :", refut)
print("     of which NOT-A-LOCATION / GLOB / SYSTEM / PKG:", sum(v for k, v in sp.items() if k in
      ("NOT-A-LOCATION", "NOT-A-CORPUS-ARTEFACT", "FRAGMENT", "NEGATIVE-CONTROL-GOOD")))
print("     of which UNASSIGNED (real hazard)            :", len(bad))
for r in bad:
    print("       %s:%d `%s`" % (r["report"][:24], r["line"], r["token"][:60]))
print()
print("   => THE FALSE-LOCATION COUNT IN THE NEW ROUND IS:", len(bad))
json.dump(dict(cand=len(cand), ok=len(ok), no=len(no),
               species={k: v for k, v in sp.items()}, unassigned=[
                   dict(report=r["report"], line=r["line"], token=r["token"], text=r["text"]) for r in bad]),
          open(os.path.join(DEEP, "_d108_t1.json"), "w"), indent=1)
