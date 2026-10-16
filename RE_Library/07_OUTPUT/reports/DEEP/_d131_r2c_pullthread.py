"""
_d131_r2c_pullthread.py -- the cited COORDINATES exist even though the TOKEN does not.

Lead's probe: portfwd.go:110, socks.go:912, socks.go:1008, socks_test.go:454/459/462.
D91: 8-of-9 inert, OwnershipFilter.

So: read those exact lines. Whatever is there IS the thing D91 named OwnershipFilter.
That is the reconciliation -- report the real identifier, not the remembered one.
"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
SL = os.path.join(WS, r"RE_Library\01_SOURCE_c2\sliver")

# locate the cited files anywhere under sliver
targets = ["portfwd.go", "socks.go", "socks_test.go"]
found = {}
for dp, dn, fn in os.walk(SL):
    for f in fn:
        if f in targets:
            found.setdefault(f, []).append(os.path.join(dp, f))

print("SCOPE: %s" % SL)
print("COUNTED: searching for %d filenames" % len(targets))
for t in targets:
    hits = found.get(t, [])
    print("   %-16s %d copy/copies" % (t, len(hits)))
    for h in hits:
        print("        %s  (%d B)" % (os.path.relpath(h, SL), os.path.getsize(h)))
print()

CITED = {
    "portfwd.go": [110],
    "socks.go": [912, 1008],
    "socks_test.go": [454, 459, 462],
}

for name, linenos in CITED.items():
    paths = found.get(name, [])
    if not paths:
        print("   %s: FILE NOT FOUND" % name)
        continue
    p = paths[0]
    lines = open(p, "r", encoding="utf-8", errors="replace").read().split("\n")
    print("=" * 100)
    print("FILE: %s   (%d lines)" % (os.path.relpath(p, SL), len(lines)))
    print("=" * 100)
    if len(linenos) == 1:
        lo, hi = linenos[0] - 8, linenos[0] + 8
    else:
        lo, hi = min(linenos) - 10, max(linenos) + 6
    lo = max(1, lo)
    hi = min(len(lines), hi)
    marks = set(linenos)
    for i in range(lo, hi + 1):
        flag = ">>" if i in marks else "  "
        print("  %s %5d| %s" % (flag, i, lines[i - 1][:120]))
    print()
