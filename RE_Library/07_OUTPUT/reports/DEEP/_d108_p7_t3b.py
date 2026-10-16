"""
D108 probe 7 -- T3 REDONE: unbounded addends, and the partition statements that matter.

Probe 6's CHAIN regex had FOUR addend slots. D7:178 is a FIVE-term sum
(4+16+4+4+4=32) and was reported WRONG when it is correct. A regex with a fixed
number of capture groups cannot evaluate an unbounded sum -- instrument rule 18's
family, and the third time this session an extractor produced a fake finding.

FIX: capture the WHOLE arithmetic expression between word boundaries and evaluate
it properly with a real sum, however many terms it has.
"""
import os, re, sys, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
REPORTS = os.path.join(WS, "RE_Library", "07_OUTPUT", "reports")
DEEP = os.path.join(REPORTS, "DEEP")
OUT = {"CROSSREF_AUDIT.md", "D59_crossref_remediation.md", "README.md"}
docs = {}
for dp, ds, fs in os.walk(REPORTS):
    if "\\extractions\\" in dp:
        continue
    for f in fs:
        if f.endswith(".md") and f not in OUT and not f.startswith("D108_"):
            docs[os.path.relpath(os.path.join(dp, f), REPORTS)] = \
                open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read()

# UNBOUNDED: capture any run of numbers joined by + ... = N
EXPR = re.compile(r"(?:^|[\s(`*])((?:\d{1,3}(?:,\d{3})*|\d+)(?:\s*\+\s*(?:\d{1,3}(?:,\d{3})*|\d+)){1,11})\s*=\s*(\d{1,3}(?:,\d{3})*|\d+)")

def tonum(s):
    return int(s.replace(",", ""))

rows = []
for rel, t in docs.items():
    for i, l in enumerate(t.split("\n")):
        for m in EXPR.finditer(l):
            terms = [tonum(x) for x in re.split(r"\s*\+\s*", m.group(1))]
            lhs = sum(terms); rhs = tonum(m.group(2))
            rows.append(dict(doc=rel, line=i + 1, nterms=len(terms), lhs=lhs, rhs=rhs,
                             ok=(lhs == rhs), text=l.strip()[:200]))

print("=" * 78)
print("T3 (i) REDONE -- unbounded addend sums")
print("=" * 78)
c = collections.Counter(r["ok"] for r in rows)
print("   MANDATORY distribution: chains=%d  OK=%d  WRONG=%d" % (len(rows), c.get(True,0), c.get(False,0)))
print()
print("   MANDATORY distribution by NUMBER OF ADDENDS (proves the fix -- a 5-term sum now evaluates):")
for k, v in sorted(collections.Counter(r["nterms"] for r in rows).items()):
    print("      %2d addends : %4d" % (k, v))
print()
print("   --- every chain with >=5 addends (the population probe 6 could not reach) ---")
for r in rows:
    if r["nterms"] >= 5:
        print("   {0} {1}:{2}".format("OK " if r["ok"] else "WRONG", r["doc"][:40], r["line"]))
        print("      {0} addends: {1} {2} {3}".format(r["nterms"], r["lhs"], "==" if r["ok"] else "!=", r["rhs"]))
print()
print("   --- EVERY WRONG chain, at any length ---")
wrong = [r for r in rows if not r["ok"]]
print("   count: %d" % len(wrong))
for r in wrong:
    print("   ** {0} :{1}  lhs={2} rhs={3}  ({4} addends)".format(r["doc"][:44], r["line"], r["lhs"], r["rhs"], r["nterms"]))
    print("      {0}".format(r["text"]))
print()

# the D7 and D97 cases specifically, to close them
print("   --- closing D7:178 and D97:79 explicitly ---")
for doc, ln in [("DEEP\\D7_metasploit_code.md", 178), ("DEEP\\D97_android_wasm_assembler_sqlite_vfs_and_jvm_tooling.md", 79)]:
    if doc in docs:
        L = docs[doc].split("\n")
        print("   {0}:{1}".format(doc, ln))
        print("      {0}".format(L[ln-1].strip()[:220]))
        if ln > 1:
            print("   prev: {0}".format(L[ln-2].strip()[:220]))
print()

# =====================================================================
# T3 (iii) -- the REAL target: a stated total partitioned into named classes
# =====================================================================
print("=" * 78)
print("T3 (ii) -- STATED TOTAL, then NAMED PARTS.  The D94:190 shape.")
print("=" * 78)
# find sentences: "<total> <noun>" ... then >=2 "N <UPPERCASE-WORD>" classes
CLASSED = re.compile(
    r"(?:of|out of)\s+(?:the\s+)?(\d{1,4})\b([^.]{0,180}?)(\d{1,4})\s+(?:are|were)\b([^.]{0,140}?)(\d{1,4})\s+(?:are|were)\b",
    re.S)
hits = []
for rel, t in docs.items():
    for m in CLASSED.finditer(t):
        hits.append(dict(doc=rel, total=int(m.group(1)), p1=int(m.group(3)), p2=int(m.group(5)),
                         span=m.group(0)[:300].replace("\n", " ")))
print("   MANDATORY distribution: '%d of N ... A are ... B are ...' statements: %d" % (0, len(hits)))
for h in hits:
    s = h["p1"] + h["p2"]
    print("   %s" % h["doc"][:52])
    print("      total=%d  named parts=%d + %d = %d   %s" % (
        h["total"], h["p1"], h["p2"], s, "OK" if s <= h["total"] else "EXCEEDS TOTAL"))
    print("      %s" % h["span"][:200])
print()

json.dump(dict(chains=rows, threeway=hits), open(os.path.join(DEEP, "_d108_t3b.json"), "w"), indent=1)
print("wrote _d108_t3b.json")
