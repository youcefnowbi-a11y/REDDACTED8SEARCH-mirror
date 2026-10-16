"""
_d131_r2_ownership.py -- RE-RUN the OwnershipFilter census. Do not copy D91's list.

The Lead's probe found 6 occurrences: portfwd.go:110, socks.go:912, socks.go:1008,
socks_test.go:454/459/462 -- i.e. 3 production sites, 3 test sites.

D91 claims 8-of-9 INERT. Either D91 counted a different surface, or it over-counted.

So: enumerate exhaustively, with FULL input cardinality, and split by surface:
  - .go files           (production + test, reported separately)
  - any other file type
  - the vendor tree (excluded? included? MUST be stated either way)

MANDATORY: print the count of files actually scanned, and a garbage-token control.
"""
import os, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
ROOTS = [
    os.path.join(WS, r"RE_Library\01_SOURCE_c2\sliver"),
]

def walk(root):
    n = 0
    for dp, dn, fn in os.walk(root):
        for f in fn:
            n += 1
            yield os.path.join(dp, f)
    # cardinality is emitted by the caller

TOKENS = ["OwnershipFilter", "OwnershipFilterMap", "ownershipFilter"]

for ROOT in ROOTS:
    files = list(walk(ROOT))
    print("=" * 100)
    print("SCOPE: %s" % ROOT)
    print("COUNTED: %d files total under the source root" % len(files))
    print()

    # classify
    ext = Counter(os.path.splitext(f)[1].lower() for f in files)
    print("   by extension (top 12):")
    for e, c in ext.most_common(12):
        print("      %-10s %6d" % (e or "(none)", c))
    print()

    # garbage control
    ctl = 0
    for f in files:
        try:
            b = open(f, "rb").read()
        except OSError:
            continue
        if b"__ZZZ_OWNERSHIP_NOT_A_TOKEN_ZZZ__" in b:
            ctl += 1
    print("   CONTROL garbage token: %d file(s) contain it -- must be 0" % ctl)
    if ctl:
        print("   *** VOID ***")
        continue
    print()

    # the real scan
    hits = {t: [] for t in TOKENS}
    for f in files:
        try:
            b = open(f, "rb").read()
        except OSError:
            continue
        for t in TOKENS:
            if t.encode() in b:
                hits[t].append(f)

    for t in TOKENS:
        hs = hits[t]
        rel = [os.path.relpath(h, ROOT) for h in hs]
        prod = [r for r in rel if not r.endswith("_test.go")]
        test = [r for r in rel if r.endswith("_test.go")]
        vend = [r for r in rel if os.sep + "vendor" + os.sep in r]
        print("   TOKEN %-20s files=%3d  production=%3d  test=%3d  vendor=%3d"
              % (t, len(hs), len(prod), len(test), len(vend)))
    print()

    # line-level for the primary token, split by surface
    T = "OwnershipFilter"
    print("   === LINE-LEVEL OCCURRENCES of %s (whole tree) ===" % T)
    total = 0
    for f in sorted(hits[T]):
        rel = os.path.relpath(f, ROOT)
        txt = open(f, "r", encoding="utf-8", errors="replace").read().split("\n")
        loc = []
        for i, l in enumerate(txt, 1):
            if T in l:
                total += 1
                loc.append((i, l.strip()))
        surface = ("TEST" if rel.endswith("_test.go")
                   else "VENDOR" if "vendor" in rel.split(os.sep)
                   else "PROD")
        print("   [%s] %s" % (surface, rel))
        for i, l in loc:
            print("        :%-5d %s" % (i, l[:118]))
    print()
    print("   TOTAL LINE OCCURRENCES of %s: %d" % (T, total))
    print()

    # also count occurrences of the bare word in ANY file, for the ratio
    print("   === occurrence count by surface (not file count) ===")
    agg = Counter()
    for f in files:
        try:
            b = open(f, "rb").read()
        except OSError:
            continue
        c = b.count(T.encode())
        if not c:
            continue
        rel = os.path.relpath(f, ROOT)
        s = ("TEST" if rel.endswith("_test.go")
             else "VENDOR" if "vendor" in rel.split(os.sep)
             else "PROD")
        agg[s] += c
    for s, c in sorted(agg.items()):
        print("      %-8s %4d" % (s, c))
    print("      %-8s %4d" % ("TOTAL", sum(agg.values())))
    print()
