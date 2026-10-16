"""
_d131_r2b_control.py -- the zero must be defended before it is a finding.

Three hypotheses for why OwnershipFilter returns 0 files:
  H1 wrong ROOT   -- the token is not in sliver/ but somewhere else in 01_SOURCE_c2
  H2 wrong TOKEN  -- the real identifier is spelled differently
  H3 probe broken -- the scan cannot find anything at all

H3 is killed by a positive control: a token KNOWN to be present.
H1 is killed by widening the root to all of 01_SOURCE_c2.
H2 is killed by a substring sweep on 'wnership' -- any casing/spelling derivative.
"""
import os, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
ALL = os.path.join(WS, r"RE_Library\01_SOURCE_c2")

files = []
for dp, dn, fn in os.walk(ALL):
    for f in fn:
        files.append(os.path.join(dp, f))
print("SCOPE: %s" % ALL)
print("COUNTED: %d files under ALL of 01_SOURCE_c2" % len(files))
print()

# --- H3: positive control, a token that MUST be present ---
CTRL = b"func "
n = 0
for f in files:
    try:
        if CTRL in open(f, "rb").read():
            n += 1
    except OSError:
        pass
print("H3 POSITIVE CONTROL: files containing 'func ' = %d   (must be > 0)" % n)
print("    -> probe is functional" if n else "    -> *** PROBE BROKEN ***")
print()

# --- H1: widen. which project holds OwnershipFilter? ---
print("H1 WIDEN: which top-level project contains the token?")
tgt = b"OwnershipFilter"
proj = Counter()
where = []
for f in files:
    try:
        b = open(f, "rb").read()
    except OSError:
        continue
    if tgt in b:
        rel = os.path.relpath(f, ALL)
        top = rel.split(os.sep)[0]
        proj[top] += 1
        where.append((rel, b.count(tgt)))
for k, v in proj.most_common():
    print("    %-22s %d file(s)" % (k, v))
if not proj:
    print("    (none)")
print()

# --- H2: is there any 'wnership' substring at all, any casing? ---
print("H2 SPELLING SWEEP: files containing 'wnership' (any case) per project")
sw = Counter()
sample = []
for f in files:
    try:
        b = open(f, "rb").read()
    except OSError:
        continue
    lb = b.lower()
    if b"wnership" in lb:
        rel = os.path.relpath(f, ALL)
        sw[rel.split(os.sep)[0]] += 1
        if len(sample) < 40:
            sample.append(rel)
for k, v in sw.most_common():
    print("    %-22s %d file(s)" % (k, v))
print()

# --- the actual 'ownership' token, all casings, per project ---
print("SWEEP: 'ownership' (case-insensitive) per project")
ow = Counter()
owhere = []
for f in files:
    try:
        b = open(f, "rb").read()
    except OSError:
        continue
    if b"ownership" in b.lower():
        rel = os.path.relpath(f, ALL)
        ow[rel.split(os.sep)[0]] += 1
        owhere.append(rel)
for k, v in ow.most_common():
    print("    %-22s %d file(s)" % (k, v))
print()
print("    all 'ownership' files (up to 50):")
for r in owhere[:50]:
    print("       %s" % r)
