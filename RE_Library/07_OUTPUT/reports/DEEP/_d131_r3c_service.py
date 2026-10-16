import os, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
COV = os.path.join(WS, r"RE_Library\01_SOURCE_c2\covenant")
P = os.path.join(COV, r"Covenant\Core\CovenantService.cs")
lines = open(P, "r", encoding="utf-8", errors="replace").read().split("\n")
print("FILE: Covenant\\Core\\CovenantService.cs  (%d lines)" % len(lines))
print()

for lo, hi, mark in [(2044, 2075, {2052, 2062}), (2200, 2240, {2208, 2211, 2212, 2218}), (2320, 2350, {2327, 2330, 2331})]:
    print("=" * 100)
    for i in range(lo, min(hi, len(lines)) + 1):
        f = ">>" if i in mark else "  "
        print("  %s %5d| %s" % (f, i, lines[i - 1][:116]))
    print()

print("=" * 100)
print("EVERY FirstOrDefaultAsync result that is dereferenced with no null check")
print("=" * 100)
# pattern: X = await ...FirstOrDefaultAsync(...)   then later X.Something
import collections
cand = []
for i, l in enumerate(lines, 1):
    m = re.search(r"(\w+)\s*=\s*await\s+.*FirstOrDefaultAsync\(", l)
    if m:
        cand.append((i, m.group(1), l.strip()))
print("COUNTED: %d FirstOrDefaultAsync assignments" % len(cand))
for i, v, l in cand:
    # look ahead 8 lines for a deref of v
    deref = None
    for j in range(i, min(i + 9, len(lines))):
        if re.search(r"\b%s\s*\.\s*\w" % re.escape(v), lines[j]):
            deref = (j + 1, lines[j].strip(), j + 1 - i)
            break
    if deref:
        print("   :%-5d %-14s -> DEREF at :%-5d (line +%d)  %s" % (i, v, deref[0], deref[2], deref[1][:66]))
    else:
        print("   :%-5d %-14s -> no deref found within 8 lines" % (i, v))
