"""
_d131_r2e_nine.py -- where could '9' and '8-of-9 inert' have come from?

Facts so far:
  OwnershipFilter        : 0 occurrences in 35,742 files  [absence, controlled]
  'ownership' (any case) : 340 files corpus-wide
  cited coordinates      : all resolve to client/core/ copies, all 'ownership' mentions

Hypotheses for D91's 8-of-9:
  H-A  the name is a comment phrase, and the count is over ownership-related SITES
  H-B  the name is a different identifier entirely; sweep every *Ownership* symbol
  H-C  the count is over the SOCKS capability/ownership BIND protocol, i.e. server+client
  H-D  the 9 is over files, not sites

Test all four and REPORT WHICH ONE FITS. Do not pick the one that sounds best.
"""
import os, re, sys
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
ALL = os.path.join(WS, r"RE_Library\01_SOURCE_c2")

files = []
for dp, dn, fn in os.walk(ALL):
    for f in fn:
        files.append(os.path.join(dp, f))
print("SCOPE: %s" % ALL)
print("COUNTED: %d files" % len(files))
print()

# ---- H-B: every identifier that contains Ownership / ownership in a Go identifier position
print("=" * 100)
print("H-B  EVERY *Ownership* IDENTIFIER, corpus-wide")
print("=" * 100)
idents = Counter()
ident_files = defaultdict(set)
for f in files:
    if not f.endswith(".go"):
        continue
    try:
        txt = open(f, "r", encoding="utf-8", errors="replace").read()
    except OSError:
        continue
    for m in re.finditer(r"\b[A-Za-z_][A-Za-z0-9_]*[Oo]wnership[A-Za-z0-9_]*\b", txt):
        idents[m.group(0)] += 1
        ident_files[m.group(0)].add(os.path.relpath(f, ALL))
print("   distinct identifiers containing 'Ownership': %d" % len(idents))
for k, v in idents.most_common():
    print("      %-52s %4d occurrences in %d file(s)" % (k, v, len(ident_files[k])))
print()

# ---- H-A/H-C: the ownership SITE in each copy of socks.go and portfwd.go
print("=" * 100)
print("H-A/H-C  OWNERSHIP-RELATED SITES in the cited files (all copies)")
print("=" * 100)
CITED = {"portfwd.go", "socks.go", "socks_test.go"}
copies = defaultdict(list)
for dp, dn, fn in os.walk(os.path.join(ALL, "sliver")):
    for f in fn:
        if f in CITED:
            copies[f].append(os.path.join(dp, f))

site_total = 0
for name in sorted(copies):
    print()
    print("   --- %s ---" % name)
    for p in sorted(copies[name]):
        txt = open(p, "r", encoding="utf-8", errors="replace").read()
        lines = txt.split("\n")
        hits = [(i, l) for i, l in enumerate(lines, 1) if "ownership" in l.lower()]
        rel = os.path.relpath(p, os.path.join(ALL, "sliver"))
        if hits:
            print("      %-56s %d site(s)" % (rel, len(hits)))
            for i, l in hits:
                site_total += 1
print()
print("   TOTAL ownership SITES across all copies of the 3 cited files: %d" % site_total)
print()

# ---- H-D: the 9 could be a file count somewhere
print("=" * 100)
print("H-D  IS 9 A FILE COUNT?  files containing 'ownership', by project and by area")
print("=" * 100)
byproj = Counter()
sliver_by_area = Counter()
for f in files:
    try:
        b = open(f, "rb").read()
    except OSError:
        continue
    if b"ownership" in b.lower():
        rel = os.path.relpath(f, ALL)
        byproj[rel.split(os.sep)[0]] += 1
        if rel.startswith("sliver"):
            parts = rel.split(os.sep)
            sliver_by_area[os.sep.join(parts[1:3])] += 1
for k, v in byproj.most_common():
    print("      %-22s %4d" % (k, v))
print()
print("   sliver 'ownership' files by area (top 20):")
for k, v in sliver_by_area.most_common(20):
    print("      %-52s %4d" % (k, v))
print()
print("   any project/area exactly 9?: %s" %
      ([k for k, v in list(byproj.items()) + list(sliver_by_area.items()) if v == 9] or "NONE"))
print("   any exactly 8?:              %s" %
      ([k for k, v in list(byproj.items()) + list(sliver_by_area.items()) if v == 8] or "NONE"))
