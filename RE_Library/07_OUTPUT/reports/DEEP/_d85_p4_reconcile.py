"""
D85 probe 4 -- RECONCILE 49 vs 43. Which six sites moved, and are they right?

Probe 1 (resolver A) said DATASTORE 49 / UNRESOLVABLE 45.
Probe 3 (resolver B, paren-less def params) said DATASTORE 43 / UNRESOLVABLE 55.
A 6-site movement in the headline class. I do not write either number until I
have read the six sites by eye and decided which resolver is correct.
"""
import os, re, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"RE_Library\01_SOURCE_c2\metasploit"

p1 = json.load(open(os.path.join(HERE, "_d85_pop.json")))   # resolver A, 131 sites
p3 = json.load(open(os.path.join(HERE, "_d85_sites.json"))) # resolver B, 131 sites

def key(d):
    return (d["file"], d["line"])

a = {key(r): r["cls"] for r in p1}
b = {key(r): r["cls"] for r in p3}
print("sites A:", len(a), " sites B:", len(b))
print("same key set:", set(a) == set(b))
if set(a) != set(b):
    print("  only A:", sorted(set(a) - set(b))[:10])
    print("  only B:", sorted(set(b) - set(a))[:10])
print()
moved = sorted(k for k in a if k in b and a[k] != b[k])
print("=== %d sites whose CLASS changed between resolver A and resolver B ===" % len(moved))
print()
for k in moved:
    print("   %s:%d   A=%-20s -> B=%s" % (k[0], k[1], a[k], b[k]))
print()

# Read each moved site by eye so the report can carry the actual source line.
print("=== SOURCE AT EACH MOVED SITE (read by eye) ===")
byfile = collections.defaultdict(list)
for f, ln in moved:
    byfile[f].append(ln)
for f, lns in sorted(byfile.items()):
    path = os.path.join(r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED", f)
    if not os.path.exists(path):
        print("   MISSING:", path)
        continue
    lines = open(path, encoding="utf-8", errors="ignore").read().split("\n")
    print()
    print("--- %s" % f)
    lo = max(0, min(lns) - 12)
    hi = min(len(lines), max(lns) + 3)
    for i in range(lo, hi):
        mark = "  <<< SITE" if (i + 1) in lns else ""
        print("   %4d| %s%s" % (i + 1, lines[i][:118], mark))
