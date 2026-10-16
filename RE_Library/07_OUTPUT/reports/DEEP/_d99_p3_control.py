"""
D99 probe 3 -- POSITIVE CONTROL on the citation resolver.

Runs before anything else is concluded from probe 2. Probe 2 returned
FAILED 0 / 1491 and 'owner missing 0 / 1491'. A classifier that returns one
value for 100% of its input is BROKEN, not decisive.

This probe asserts the resolver on cases where the answer is KNOWN, including
cases where it MUST fail. If the control cases resolve, the resolver is not
merely permissive -- it is broken, and probe 2's zero is an artifact.
"""
import os, re, json

REPORTS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\reports\DEEP"
names = set(os.listdir(REPORTS))

print("=== CONTROL A: D-number prefix collisions ===")
print("   Does a naive startswith() attribution collapse D1 and D11?")
for o in ["D1", "D11", "D2", "D22", "D4", "D41"]:
    naive = sorted([n for n in names if n.startswith(o)])
    strict = sorted([n for n in names if n.startswith(o + "_") or n == o + ".md"])
    print("   %-5s naive startswith -> %2d files ; strict '<o>_' -> %2d files %s"
          % (o, len(naive), len(strict), "" if len(naive) == len(strict) else "  <-- DIVERGE"))
print()
print("   D1 files (strict):", [n for n in names if n.startswith("D1_")])
print("   D1 would wrongly absorb:",
      [n for n in names if n.startswith("D1") and not n.startswith("D1_")][:12], "...")
print()

print("=== CONTROL B: is 'D13_...' the only D13? Is D13 present at all? ===")
d13 = [n for n in names if n.startswith("D13_")]
print("   D13 files:", d13)
print()

print("=== CONTROL C: a citation that MUST fail -- synthesize one ===")
# D13 exists. Does D13 contain section 7.2? D94 proved it does NOT.
p = os.path.join(REPORTS, d13[0]) if d13 else None
if p and os.path.exists(p):
    txt = open(p, encoding="utf-8", errors="ignore").read()
    heads = re.findall(r"(?m)^#{1,6}\s+§?\s*(\d+(?:\.\d+)*)", txt)
    print("   D13 heading numbers found:", sorted(set(heads), key=lambda s: [int(x) for x in s.split('.')])[:40])
    print("   contains '7.2' ?", "7" "2" in heads or "7.2" in heads)
    # how does probe 2's index see it?
    print()
    print("   --- reproduce probe 2's index for D13 ---")
    HEAD = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
    BOLDNUM = re.compile(r"^\s*[-*]?\s*\*\*\s*§?\s*(\d+(?:\.\d+)*)\b")
    NUMHEAD = re.compile(r"^#{1,6}\s+§?\s*(\d+(?:\.\d+)*)")
    secs = {}
    for i, l in enumerate(txt.split("\n")):
        m = HEAD.match(l)
        if m:
            m2 = re.match(r"§?\s*(\d+(?:\.\d+)*)", m.group(2))
            if m2:
                secs.setdefault(m2.group(1), i + 1)
            nm = NUMHEAD.match(l)
            if nm:
                secs.setdefault(nm.group(1), i + 1)
        bm = BOLDNUM.match(l)
        if bm:
            secs.setdefault(bm.group(1), i + 1)
    print("   probe-2 index for D13 keys:", sorted(secs.keys(), key=lambda s: [int(x) for x in s.split('.')]))
    print("   probe-2 index sees '7.2'? ", "7.2" in secs, "  <-- D94 PROVED THIS IS FALSE")
print()
print("=== CONTROL D: what does probe-2's index look like for a doc with MANY sections? ===")
# the index is contaminated by any leading number in a heading -- e.g. '1. Foo', '7 Things'
cnt = 0
for n in sorted(names):
    if not n.endswith('.md'):
        continue
    t = open(os.path.join(REPORTS, n), encoding="utf-8", errors="ignore").read()
    HEAD = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
    for i, l in enumerate(t.split("\n")):
        m = HEAD.match(l)
        if m:
            m2 = re.match(r"§?\s*(\d+(?:\.\d+)*)", m.group(2))
            if m2 and not re.match(r"^\d+\.\s", m.group(2)):
                if cnt < 12:
                    print("   NON-NUMERIC heading absorbed as a section number:")
                    print("      %s : %s" % (n, l.strip()[:100]))
                cnt += 1
print("   total headings with a leading number that is NOT a numbered section:", cnt)
