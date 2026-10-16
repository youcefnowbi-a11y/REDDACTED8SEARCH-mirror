import os, re, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
DEEP = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\reports\DEEP"

# read the ACTUAL lines for every remaining suspect, at full width
SUS = [
 ("D96_sliver_client_server_absence_and_pclntab_census.md", [26, 193, 354, 368]),
 ("D101_covenant_binary_source_pair_negative_result_and_empirical_closures.md", [15, 27, 33, 34, 35, 36, 97, 107, 305]),
 ("D98_havoc_tomap_serialization_boundary_callers_and_concurrency_surface.md", [396]),
 ("C-09_correction_to_d94_two_fabricated_artifact_locations_and_unclosed_arithmetic.md", [12, 14, 26, 39]),
]
for name, lns in SUS:
    p = os.path.join(DEEP, name)
    if not os.path.exists(p):
        print("MISSING:", name); continue
    lines = open(p, encoding="utf-8", errors="ignore").read().split("\n")
    print("=" * 78)
    print(name)
    print("=" * 78)
    for n in lns:
        if n <= len(lines):
            print("  :%d | %s" % (n, lines[n-1].strip()[:230]))
    print()

# does Covenant.dll exist anywhere?  and what are the REAL paths D101 cites?
print("=" * 78)
print("DISK CHECK: the tokens D101 and D96 depend on")
print("=" * 78)
WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
for t in ["Covenant.dll", "gsli.tsv", "powerkatz_x64.dll", "powerkatz_x86.dll"]:
    hits = []
    for dp, ds, fs in os.walk(os.path.join(WS, "RE_Library")):
        if t in fs:
            hits.append(os.path.join(dp, t))
    print("  %-24s -> %d on disk" % (t, len(hits)))
    for h in hits[:3]:
        print("        %s" % h.replace(WS + "\\", ""))
