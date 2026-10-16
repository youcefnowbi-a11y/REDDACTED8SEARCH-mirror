"""
_d131_r2d_disambiguate.py -- the cited lines must be read against the copy that HAS them.

portfwd.go has 5 copies (93..~700 lines), socks.go has 7. Line 110 / 912 / 1008 only
exist in some. Reading copy[0] silently printed nothing -- my own under-capture.

Method: for EVERY copy of the cited filenames, report line count, whether the cited
line exists, and what is on it. Ground the search in 'ownership' occurrences and
print each with its real identifier. Let the data name the symbol; do not supply it.
"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
SL = os.path.join(WS, r"RE_Library\01_SOURCE_c2\sliver")

CITED = {"portfwd.go": [110], "socks.go": [912, 1008], "socks_test.go": [454, 459, 462]}

copies = {}
for dp, dn, fn in os.walk(SL):
    for f in fn:
        if f in CITED:
            copies.setdefault(f, []).append(os.path.join(dp, f))

for name in sorted(copies):
    print("=" * 100)
    print("%s  -- %d COPIES" % (name, len(copies[name])))
    print("=" * 100)
    for p in sorted(copies[name], key=lambda x: os.path.getsize(x)):
        lines = open(p, "r", encoding="utf-8", errors="replace").read().split("\n")
        rel = os.path.relpath(p, SL)
        flags = []
        for ln in CITED[name]:
            if ln <= len(lines):
                txt = lines[ln - 1].strip()
                flags.append(":%d=%s" % (ln, (txt[:60] + "...") if len(txt) > 60 else txt))
            else:
                flags.append(":%d=<OUT OF RANGE, file has %d lines>" % (ln, len(lines)))
        print("   %-52s %6d B  %5d lines" % (rel, os.path.getsize(p), len(lines)))
        for fl in flags:
            print("         %s" % fl)
    print()

# now: every line containing 'ownership', across ALL copies, with the real identifier
print("=" * 100)
print("THE REAL IDENTIFIER -- every 'ownership' line across every copy")
print("=" * 100)
import re
total = 0
for name in sorted(copies):
    for p in sorted(copies[name]):
        lines = open(p, "r", encoding="utf-8", errors="replace").read().split("\n")
        hits = [(i, l) for i, l in enumerate(lines, 1) if "ownership" in l.lower()]
        if not hits:
            continue
        print("   %s" % os.path.relpath(p, SL))
        for i, l in hits:
            total += 1
            # extract the identifier-ish token on the line
            ids = re.findall(r"[A-Za-z_][A-Za-z0-9_]*[Oo]wnership[A-Za-z0-9_]*", l)
            print("      :%-5d %-70s  %s" % (i, l.strip()[:70], ("IDS=" + ",".join(ids)) if ids else ""))
print()
print("   TOTAL 'ownership' lines across the cited filenames: %d" % total)
