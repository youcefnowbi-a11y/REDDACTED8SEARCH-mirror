"""
D118 probe 2 -- T4 CORRECTED: separate REAL collisions from cross-prefix artifacts.

Probe 1's NUM regex was `^(?:D|C-)(\d+)_` -- it stripped BOTH prefixes into one
numeric namespace, so C-08/D8, C-09/D9 ... C-13/D13 all appeared as collisions.
FOUR of the six were MANUFACTURED by that regex. Nothing in the corpus writes
"D8 SSx" meaning C-08.

The real question is narrower and it is the Lead's: which DOCUMENT NUMBERS are
used by more than one file in the D namespace. So this probe keys STRICTLY on
the `D<n>_` prefix, and reports the C-namespace separately as its own finding.
"""
import os, re, sys, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
REPORTS = os.path.join(WS, "RE_Library", "07_OUTPUT", "reports")
DEEP = os.path.join(REPORTS, "DEEP")

files = []
for dp, ds, fs in os.walk(REPORTS):
    if "\\extractions\\" in dp:
        continue
    for f in fs:
        if f.endswith(".md"):
            files.append(os.path.join(dp, f))

DONLY = re.compile(r"^D(\d+)_")
CONLY = re.compile(r"^C-(\d+)_")
dfam, cfam = collections.defaultdict(list), collections.defaultdict(list)
for p in files:
    b = os.path.basename(p)
    m = DONLY.match(b)
    if m:
        dfam[int(m.group(1))].append(b)
    m2 = CONLY.match(b)
    if m2:
        cfam[int(m2.group(1))].append(b)

print("=" * 78)
print("T4 CORRECTED -- D-namespace collisions ONLY (the real question)")
print("=" * 78)
dmulti = {k: sorted(v) for k, v in dfam.items() if len(v) > 1}
print("   MANDATORY distribution: D-numbers used by >1 file")
for k in sorted(dmulti):
    print("      D%-5d -> %d files" % (k, len(dmulti[k])))
    for n in dmulti[k]:
        print("               %s" % n)
print()
print("   REAL D-namespace colliding numbers : %d" % len(dmulti))
print("   files involved                     : %d" % sum(len(v) for v in dmulti.values()))
print("   total D-numbered files             : %d" % sum(len(v) for v in dfam.values()))
print("   distinct D numbers                 : %d" % len(dfam))
print()

print("=" * 78)
print("THE C-NAMESPACE, reported as its OWN finding (not a collision)")
print("=" * 78)
cmulti = {k: v for k, v in cfam.items() if len(v) > 1}
print("   MANDATORY distribution: C numbers")
for k in sorted(cfam):
    flag = "  <== >1 file" if len(cfam[k]) > 1 else ""
    print("      C-%-4d -> %d file(s)%s" % (k, len(cfam[k]), flag))
print()
print("   C files total: %d" % sum(len(v) for v in cfam.values()))
print()
print("   >>> THE STRUCTURAL FACT: C-00..C-13 exist as a PARALLEL series whose")
print("       numbers 0..13 would COLLIDE with D0..D13 if the prefix were ignored.")
print("       Every C number 8..13 collides with a D number.  That is not a")
print("       corpus defect -- it is a reason the prefix is load-bearing.")
overlap = sorted(set(cfam) & set(dfam))
print("       C numbers that also exist as D numbers: %s" % ", ".join(str(o) for o in overlap))
print("       count: %d of %d C files" % (len(overlap), sum(len(v) for v in cfam.values())))
print()

# ---- citation counts, computed per namespace, with the C/D split explicit
OUT = {"CROSSREF_AUDIT.md", "D59_crossref_remediation.md", "README.md"}
docs = {}
for p in files:
    b = os.path.basename(p)
    if b in OUT or b.startswith("D118_"):
        continue
    docs[b] = open(p, encoding="utf-8", errors="ignore").read()
totss = sum(len(re.findall(r"\bD\d{1,3}\s*§", t)) for t in docs.values())

print("   --- citations per REAL colliding D-number ---")
amb = 0
for k in sorted(dmulti):
    c = sum(len(re.findall(r"\bD%d\s*§" % k, t)) for t in docs.values())
    amb += c
    print("      D%-5d  %3d files  %4d SS-citations" % (k, len(dmulti[k]), c))
print()
print("   REAL ambiguous SS-citations : %d" % amb)
print("   TOTAL SS-citations          : %d" % totss)
print("   SHARE                       : %.1f%%" % (100.0 * amb / max(1, totss)))
print("   CONTROLS (must be non-zero) : D6=%d  D11=%d" % (
    sum(len(re.findall(r"\bD6\s*§", t)) for t in docs.values()),
    sum(len(re.findall(r"\bD11\s*§", t)) for t in docs.values())))
print()

# holes recomputed on the D namespace only
used = sorted(dfam)
holes = [n for n in range(min(used), max(used) + 1) if n not in dfam]
print("   HOLES (D-namespace only): %s" % ", ".join("D%d" % h for h in holes))
print("   span D%d..D%d" % (min(used), max(used)))
print()

json.dump(dict(dmulti=dmulti, cfam={k: v for k, v in cfam.items()}, holes=holes,
               amb=amb, totss=totss, overlap=overlap),
          open(os.path.join(DEEP, "_d118_t4b.json"), "w"), indent=1)
print("wrote _d118_t4b.json")
