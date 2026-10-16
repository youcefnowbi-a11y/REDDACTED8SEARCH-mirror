"""
D99 probe 4 -- WHY does probe 2 report FAILED 0? Trace one KNOWN failure.

D94 SS0 established by hand that four documents cite `D13 SS7.2`, that D13 has no
SS7.2, and that this is a PROVIDABLE failure. Probe 2 over the same corpus reports
FAILED 0. One of the two is wrong.

Trace the exact known case through probe 2's pipeline, printing at every stage.
"""
import os, re, json, sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPORTS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\reports\DEEP"
KNOWN = ["D32_covenant_partial_class.md", "D50_covenant_api_and_task_library.md",
         "D52_covenant_task_consumption_and_wire_format.md", "D55_corpus_instrument_ledger.md"]

print("=== STAGE 1: does the raw text contain the literal 'D13 §7.2' style token? ===")
PAT_A = re.compile(r"\bD13\s*§\s*7\.2")
PAT_B = re.compile(r"\bD13\b")
for n in KNOWN:
    p = os.path.join(REPORTS, n)
    if not os.path.exists(p):
        print("   %-52s MISSING" % n)
        continue
    t = open(p, encoding="utf-8", errors="ignore").read()
    a = PAT_A.findall(t)
    b = PAT_B.findall(t)
    lines = t.split("\n")
    hits = [i + 1 for i, l in enumerate(lines) if PAT_A.search(l)]
    print("   %-52s 'D13 SS7.2' x%d  bare 'D13' x%-3d  at lines %s"
          % (n, len(a), len(b), hits[:8]))
print()

print("=== STAGE 2: probe 2's SEC regex against the ACTUAL line ===")
# probe 2 used: \bD(\d{1,3})\s*§\s*(\d+(?:\.\d+)*)
P2 = re.compile(r"\bD(\d{1,3})\s*§\s*(\d+(?:\.\d+)*)")
for n in KNOWN:
    p = os.path.join(REPORTS, n)
    if not os.path.exists(p):
        continue
    for i, l in enumerate(open(p, encoding="utf-8", errors="ignore").read().split("\n")):
        if "D13" in l and "7.2" in l:
            m = P2.search(l)
            print("   %s:%d" % (n, i + 1))
            print("      line: %s" % l.strip()[:160])
            print("      probe-2 SEC match: %s" % (m.groups() if m else "NO MATCH"))
print()

print("=== STAGE 3: THE HYPOTHESIS -- is the SS-7.2 text inside a CODE FENCE or TABLE? ===")
print("   probe 2 skips ONLY table-separator rows. It does NOT skip fences.")
print("   D94:249-252 shows the D13 SS7.2 text lives in a TABLE ROW. Test the row shape.")
for n in KNOWN:
    p = os.path.join(REPORTS, n)
    if not os.path.exists(p):
        continue
    lines = open(p, encoding="utf-8", errors="ignore").read().split("\n")
    for i, l in enumerate(lines):
        if "D13" in l and "7.2" in l:
            ls = l.strip()
            is_table = ls.startswith("|")
            print("   %-52s :%-4d table_row=%s  quote=%s" % (n, i + 1, is_table, '"' in ls))
print()

print("=== STAGE 4: the resolver, isolated on the known case ===")
d13 = os.path.join(REPORTS, "D13_covenant_api_control_plane.md")
t = open(d13, encoding="utf-8", errors="ignore").read()
HEAD = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
NUMHEAD = re.compile(r"^#{1,6}\s+§?\s*(\d+(?:\.\d+)*)")
BOLDNUM = re.compile(r"^\s*[-*]?\s*\*\*\s*§?\s*(\d+(?:\.\d+)*)\b")
secs = {}
for i, l in enumerate(t.split("\n")):
    m = HEAD.match(l)
    if m:
        nm = NUMHEAD.match(l)
        if nm:
            secs.setdefault(nm.group(1), i + 1)
        m2 = re.match(r"§?\s*(\d+(?:\.\d+)*)", m.group(2))
        if m2:
            secs.setdefault(m2.group(1), i + 1)
    bm = BOLDNUM.match(l)
    if bm:
        secs.setdefault(bm.group(1), i + 1)
print("   '7.2' in D13 index:", "7.2" in secs)
print("   => resolution for target '7.2' would be:", secs.get("7.2"), "(None = FAIL, correct)")

print()
print("=== STAGE 5: SO WHY 0? -- check the edge extraction loop itself ===")
# reproduce probe 2's extraction for one known file
p = os.path.join(REPORTS, "D55_corpus_instrument_ledger.md")
t = open(p, encoding="utf-8", errors="ignore").read()
REF_SEC = re.compile(r"\bD(\d{1,3})\s*§\s*(\d+(?:\.\d+)*)")
n = 0
for i, l in enumerate(t.split("\n")):
    ls = l.strip()
    if re.fullmatch(r"\|[\s\-:|]+\|", ls):
        continue
    for m in REF_SEC.finditer(l):
        if n < 10:
            print("   edge: src=%s:%d owner=D%s target=%s" % ("D55...", i + 1, m.group(1), m.group(2)))
        n += 1
print("   total SEC edges extracted from D55 by probe 2's regex:", n)
print()
print("   ^ If D55's 'D13 SS7.2' row is NOT in this list, the regex missed it.")
print("   If it IS in this list, the RESOLVER is at fault.")
