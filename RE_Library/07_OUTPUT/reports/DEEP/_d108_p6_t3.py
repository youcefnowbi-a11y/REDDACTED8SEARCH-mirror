"""
D108 probe 6 -- T3 (the partition rule) + the never_written tail + the D110 anomaly.

T3 is MECHANICAL and the Lead called it high-yield. Rule: a summary that states a
total and then partitions it into named parts must have parts summing to the total.

Approach: find every line that states a bare total AND nearby named parts with
counts, then check the arithmetic. Restrict to PARTITION-SHAPED statements so the
output is adjudicable rather than a wall of numbers.

Also: what is D110?  It has 5 citations and I have no D110 file.
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
            p = os.path.join(dp, f)
            docs[os.path.relpath(p, REPORTS)] = open(p, encoding="utf-8", errors="ignore").read()

# =====================================================================
# THE D110 ANOMALY
# =====================================================================
print("=" * 78)
print("ANOMALY -- what is D110?")
print("=" * 78)
allf = sorted(os.listdir(DEEP))
print("   files matching D110*: %s" % [f for f in allf if f.startswith("D110")])
print("   files matching D11*  : %s" % [f for f in allf if f.startswith("D11")])
d110 = re.compile(r"\bD110\b")
for rel, t in docs.items():
    for i, l in enumerate(t.split("\n")):
        if d110.search(l):
            print("   %s:%d | %s" % (rel, i + 1, l.strip()[:170]))
print()

# =====================================================================
# T3 -- THE PARTITION RULE
# =====================================================================
print("=" * 78)
print("T3 -- THE PARTITION RULE: does every stated total equal its named parts?")
print("=" * 78)

# A partition statement: "N <noun>" followed by >=2 "= M" or "M <part>" fragments
# on the SAME line or the line pair, with plus/decomposition markers.
TOTAL = re.compile(r"\b(\d{1,5})\b")
SPLITMARK = re.compile(r"[\u2192=:]|\+")

# Strategy: find lines containing a total-like phrase AND >=2 named parts
PART_LINE = re.compile(r"(\d{1,5})\s*(?:of|/)\s*(\d{1,5})")     # "31 of 172"
CHAIN = re.compile(r"(\d{1,5})\s*\+\s*(\d{1,5})(?:\s*\+\s*(\d{1,5}))?(?:\s*\+\s*(\d{1,5}))?\s*=\s*(\d{1,5})")

findings = []
# (i) explicit arithmetic chains with '='
for rel, t in docs.items():
    for i, l in enumerate(t.split("\n")):
        for m in CHAIN.finditer(l):
            nums = [int(x) for x in m.groups() if x]
            lhs = sum(nums[:-1]); rhs = nums[-1]
            findings.append(dict(doc=rel, line=i + 1, kind="CHAIN",
                                 lhs=lhs, rhs=rhs, ok=(lhs == rhs),
                                 text=l.strip()[:190]))
print("--- (i) explicit 'a + b + c = d' chains ---")
c = collections.Counter(f["ok"] for f in findings if f["kind"] == "CHAIN")
print("   MANDATORY distribution: chains found=%d  ARITHMETIC OK=%d  WRONG=%d" % (
    c.get(True,0)+c.get(False,0), c.get(True,0), c.get(False,0)))
for f in findings:
    if f["kind"] == "CHAIN" and not f["ok"]:
        print("   ** WRONG ** %s:%d  %d != %d" % (f["doc"][:44], f["line"], f["lhs"], f["rhs"]))
        print("        %s" % f["text"])
    elif f["kind"] == "CHAIN":
        print("   ok          %s:%d  %d == %d" % (f["doc"][:44], f["line"], f["lhs"], f["rhs"]))
print()

# (ii) "X of Y" where a nearby line decomposes Y
print("--- (ii) 'X of Y' statements, with Y checked for a decomposition nearby ---")
ofs = []
for rel, t in docs.items():
    lines = t.split("\n")
    for i, l in enumerate(lines):
        for m in PART_LINE.finditer(l):
            ofs.append(dict(doc=rel, line=i + 1, x=int(m.group(1)), y=int(m.group(2)),
                            text=l.strip()[:190]))
print("   MANDATORY distribution: 'X of Y' statements: %d" % len(ofs))
print("   MANDATORY distribution by whether X<=Y (sanity):")
sane = collections.Counter("X<=Y" if o["x"] <= o["y"] else "X>Y  <== IMPOSSIBLE" for o in ofs)
for k, v in sane.most_common():
    print("      %-24s %4d" % (k, v))
for o in ofs:
    if o["x"] > o["y"]:
        print("      ** %s:%d  %d of %d **" % (o["doc"][:40], o["line"], o["x"], o["y"]))
        print("         %s" % o["text"])
print()

# (iii) the specific shape D94:190 had: "of N, A are X, B are Y, C are Z"
print("--- (iii) 'of N, A are ... B are ... C are ...' three-way summaries ---")
THREE = re.compile(r"of\s+(?:the\s+)?(\d{1,4})[^.]{0,40}?(\d{1,4})\s+(?:are|were)\b")
for rel, t in docs.items():
    for i, l in enumerate(t.split("\n")):
        if THREE.search(l) and l.count(" are ") + l.count(" were ") >= 2:
            print("   %s:%d" % (rel[:50], i + 1))
            print("        %s" % l.strip()[:230])
print()

json.dump(dict(chains=[f for f in findings if f["kind"] == "CHAIN"], ofs=ofs),
          open(os.path.join(DEEP, "_d108_t3.json"), "w"), indent=1)
print("wrote _d108_t3.json")
