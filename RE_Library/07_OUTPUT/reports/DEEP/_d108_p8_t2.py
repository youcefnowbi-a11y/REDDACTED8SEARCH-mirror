"""
D108 probe 8 -- T2: the probe files the new reports leave on disk.

The Lead's test: verify the STATED SIZES of probe artifacts, and confirm the
reported numbers are REPRODUCIBLE FROM THE PROBE BY READING IT -- not by
re-running it. Reading is this lane's job; running is the owning lane's.

So for every _d9x_* artifact named or implied by a new report, capture:
  - actual bytes / LF / CR
  - whether the report STATES a size, and whether it matches
  - what the probe's source SAYS it emits (read, not run)
"""
import os, re, sys, json, glob
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEEP = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\reports\DEEP"

print("=" * 78)
print("T2 -- PROBE ARTIFACTS LEFT ON DISK")
print("=" * 78)
# every probe-ish artifact in DEEP
pats = ["_d9*_*.py", "_d10*_*.py", "_d9*.ps1", "_d10*.ps1", "_d9*.json", "_d9*.tsv",
        "_d10*.json", "_d10*.tsv", "_d9*.csv", "_*.tsv", "_*.json"]
seen = {}
for p in pats:
    for f in glob.glob(os.path.join(DEEP, p)):
        seen[os.path.basename(f)] = f

print("   MANDATORY distribution by kind:")
import collections
kind = collections.Counter()
for b in seen:
    kind[os.path.splitext(b)[1]] += 1
for k, v in kind.most_common():
    print("      %-8s %4d" % (k, v))
print("      %-8s %4d  <- total artifacts" % ("TOTAL", len(seen)))
print()

# sizes
print("   every artifact with byte size (the Lead's T2 population):")
tot = 0
rows = []
for b in sorted(seen):
    p = seen[b]
    n = os.path.getsize(p)
    tot += n
    rows.append((b, n))
    print("      %10s  %s" % ("{:,}".format(n), b))
print("      %10s  <- total bytes" % "{:,}".format(tot))
print()

# --- does any NEW report STATE a size for a probe artifact?
NEWDOCS = ["D95_merlin_binary_layer_agent_build_delta_cgo_export_stubs_and_extraction_path_census.md",
 "D96_sliver_client_server_absence_and_pclntab_census.md",
 "D97_android_wasm_assembler_sqlite_vfs_and_jvm_tooling.md",
 "D98_havoc_tomap_serialization_boundary_callers_and_concurrency_surface.md",
 "D100_android_binary_layer_manifest_dex_signing_and_native_census.md",
 "D101_covenant_binary_source_pair_negative_result_and_empirical_closures.md",
 "D102_meterpreter_tlv_wire_constants_handler_payload_contract_and_d90_u1_closure.md",
 "C-09_correction_to_d94_two_fabricated_artifact_locations_and_unclosed_arithmetic.md",
 "C-10_binary_layer_seven_targets_named_functions_one_signature_and_pclntab_substitution.md",
 "C-11_merlin_artifact_census_duplicate_extraction_and_cross_platform_build_config_identity.md",
 "C-12_havoc_instrument_record_and_the_allocation_collision.md",
 "C-13_merlin_release_vs_debug_the_reloc_table_is_97_percent_of_the_divergence.md",
 "D99_corpus_auditability_citation_adjudication_denominator_floor_and_extractor_disposition.md"]

SIZEPAT = re.compile(r"([\d,]{1,12})\s*(?:B\b|bytes)")
PROBENAM = re.compile(r"_(?:d\d+)_?[A-Za-z0-9_]*\.(?:py|ps1|json|tsv|csv)")
print("   --- does any report STATE a byte size for a probe file? ---")
found_any = False
for d in NEWDOCS:
    p = os.path.join(DEEP, d)
    if not os.path.exists(p):
        continue
    lines = open(p, encoding="utf-8", errors="ignore").read().split("\n")
    for i, l in enumerate(lines):
        if PROBENAM.search(l) and SIZEPAT.search(l):
            found_any = True
            print("      %s:%d" % (d[:44], i + 1))
            print("         %s" % l.strip()[:190])
if not found_any:
    print("      NONE.  No report in the new round states a byte size for a probe file.")
print()

# --- what do the probes SAY they emit?  (read the source, do not run it)
print("   --- READ-ONLY survey: what each probe declares it writes ---")
EMITS = re.compile(r'(?:open\(|json\.dump\(|\.write\()[^)\n]{0,120}?["\']([^"\']*_d9[^"\']*\.(?:json|tsv|csv))["\']')
for b in sorted([x for x in seen if x.endswith(".py")]):
    src = open(seen[b], encoding="utf-8", errors="ignore").read()
    outs = set(EMITS.findall(src))
    hard = [o for o in outs if o]
    print("      %-34s emits: %s" % (b[:34], ", ".join(sorted(hard)) if hard else "(none named)"))
print()
json.dump(rows, open(os.path.join(DEEP, "_d108_t2.json"), "w"), indent=1)
print("wrote _d108_t2.json")
