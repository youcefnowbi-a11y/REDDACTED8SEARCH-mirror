import os, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
REPORTS = os.path.join(WS, r"RE_Library\07_OUTPUT\reports")

allmd = []
for dp, dn, fn in os.walk(REPORTS):
    for f in fn:
        if f.lower().endswith(".md"):
            allmd.append(os.path.join(dp, f))

print("=" * 100)
print("CAN 113 REPRODUCE UNDER ANY DEFENSIBLE SCOPE?")
print("=" * 100)
variants = {
    "all .md recursive":                    allmd,
    "excl extractions":                     [p for p in allmd if os.sep+"extractions"+os.sep not in p],
    "excl extractions+README":              [p for p in allmd if os.sep+"extractions"+os.sep not in p and os.path.basename(p).lower()!="readme.md"],
    "DEEP/ only":                           [p for p in allmd if os.path.dirname(p)==os.path.join(REPORTS,"DEEP")],
    "DEEP/ mind D-named":                   [p for p in allmd if os.path.dirname(p)==os.path.join(REPORTS,"DEEP") and re.match(r"^D\d+",os.path.basename(p))],
    "anywhere, D-named":                    [p for p in allmd if re.match(r"^D\d+",os.path.basename(p))],
    "anywhere, D-named, excl extractions":  [p for p in allmd if re.match(r"^D\d+",os.path.basename(p)) and os.sep+"extractions"+os.sep not in p],
    "D-named excl extractions+README+D94self": [p for p in allmd if re.match(r"^D\d+",os.path.basename(p)) and os.sep+"extractions"+os.sep not in p and not os.path.basename(p).startswith("D94_")],
    "DEEP D-named excl D94":                [p for p in allmd if os.path.dirname(p)==os.path.join(REPORTS,"DEEP") and re.match(r"^D\d+",os.path.basename(p)) and not os.path.basename(p).startswith("D94_")],
    "DEEP only .md excl CROSSREF+D59":      [p for p in allmd if os.path.dirname(p)==os.path.join(REPORTS,"DEEP") and os.path.basename(p) not in ("CROSSREF_AUDIT.md","D59_crossref_remediation.md")],
}
for k, v in variants.items():
    mark = "   <-- MATCHES 113" if len(v) == 113 else ""
    print("   %-44s %4d%s" % (k, len(v), mark))
print()
print("   any variant == 113? %s" % any(len(v)==113 for v in variants.values()))
print("   any variant == 172? (can't be, all are doc counts) -- 172 must be a FAILURE count")
print()

print("=" * 100)
print("CAN 172 REPRODUCE AS A CROSSREF FAILURE COUNT?")
print("=" * 100)
docs = {}
for p in allmd:
    if os.sep+"extractions"+os.sep in p: continue
    docs[p] = open(p,"r",encoding="utf-8",errors="replace").read()

def stem(p): return os.path.splitext(os.path.basename(p))[0]
names = {stem(p) for p in docs}
print("   COUNTED: %d docs, %d distinct stems" % (len(docs), len(names)))
print()

# For each doc, collect D-number refs; count those pointing to a stem that EXISTS
# vs those pointing to a stem that does NOT.  Sweep the ref pattern.
REF = {
    "bare D<n>":        re.compile(r"\bD(\d{1,3})\b"),
    "D<n>_ anytime":    re.compile(r"\bD(\d{1,3})[_A-Za-z0-9\-]*\.md\b"),
    "D-<n> hyphen":     re.compile(r"\bD-(\d{1,3})\b"),
}
by_num = {}
for p in docs:
    m = re.match(r"^D(\d+)", stem(p))
    if m: by_num.setdefault(int(m.group(1)), []).append(p)

print("   implementation files present by number (from DEEP-ish corpus):")
print("      %d distinct D-numbers have at least one file" % len(by_num))
print()

for label, pat in REF.items():
    resolvable = 0
    unresolvable = 0
    uniq_bad = set()
    uniq_good = set()
    for p, t in docs.items():
        for m in pat.finditer(t):
            n = int(m.group(1))
            if n in by_num:
                resolvable += 1
                uniq_good.add(n)
            else:
                unresolvable += 1
                uniq_bad.add(n)
    print("   %-18s resolvable=%6d  UNRESOLVABLE=%6d   distinct-bad=%3d"
          % (label, resolvable, unresolvable, len(uniq_bad)))
    if unresolvable in (172,) or len(uniq_bad) in (172,):
        print("        ^^^ MATCHES 172")
print()
print("   distinct unresolvable D-numbers under 'bare D<n>' (the loosest):")
pat = REF["bare D<n>"]
bad = set()
for p, t in docs.items():
    for m in pat.finditer(t):
        n = int(m.group(1))
        if n not in by_num:
            bad.add(n)
print("      %s" % sorted(bad))
print("      count = %d" % len(bad))
