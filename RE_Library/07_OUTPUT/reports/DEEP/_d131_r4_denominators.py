"""
_d131_r4_denominators.py -- D94's unstable denominators.

Two numbers to re-measure:
   (a) 172 citation failures
   (b) 113 in-scope

D94's own IN-SCOPE RULE (§3.3): every *.md under RE_Library\07_OUTPUT\reports\,
recursively, EXCLUDING any path containing \extractions\, EXCLUDING reports\README.md.
OUT OF SCOPE: CROSSREF_AUDIT.md, D59_crossref_remediation.md, D94_*, all non-.md.

The Lead's law: a count that changes with the collation of its comparator is a count
of the comparator. So: run the SAME measurement under SEVERAL defensible collations
and PRINT EVERY NUMBER. If it moves, report it as unstable -- do not smooth it.
"""
import os, re, sys
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
REPORTS = os.path.join(WS, r"RE_Library\07_OUTPUT\reports")
print("SCOPE: %s" % REPORTS)
print()

# ---------- enumerate every .md under reports\ recursively, print the funnel ----------
allmd = []
for dp, dn, fn in os.walk(REPORTS):
    for f in fn:
        if f.lower().endswith(".md"):
            allmd.append(os.path.join(dp, f))
print("A. FUNNEL -- each exclusion counted, so the denominator is visible")
print("   A1  every .md under reports\\ recursively        : %d" % len(allmd))

ex_extr = [p for p in allmd if os.sep + "extractions" + os.sep in p]
print("   A2  ... containing \\extractions\\  (EXCLUDED)    : %d" % len(ex_extr))
step = [p for p in allmd if p not in set(ex_extr)]
print("   A3  = %d" % len(step))

readme = [p for p in step if os.path.basename(p).lower() == "readme.md"]
print("   A4  ... reports\\README.md (EXCLUDED)            : %d" % len(readme))
step2 = [p for p in step if p not in set(readme)]
print("   A5  = %d" % len(step2))

outofscope = [p for p in step2 if os.path.basename(p) in
              ("CROSSREF_AUDIT.md", "D59_crossref_remediation.md")
              or os.path.basename(p).startswith("D94_")]
print("   A6  ... D94's stated OUT-OF-SCOPE names          : %d" % len(outofscope))
for p in outofscope:
    print("          %s" % os.path.relpath(p, REPORTS))
step3 = [p for p in step2 if p not in set(outofscope)]
print("   A7  IN-SCOPE TOTAL                               : %d" % len(step3))
print()
print("   *** the '113 in-scope' claim vs A7 = %d ***" % len(step3))
print()

# ---------- DEEPER: also count DEEP/ alone, which is where citations matter ----------
deep = os.path.join(REPORTS, "DEEP")
deepmd = [p for p in step3 if os.path.dirname(p) == deep]
print("   A8  of which directly in reports\\DEEP\\          : %d" % len(deepmd))
subdirs = Counter(os.path.dirname(os.path.relpath(p, REPORTS)).split(os.sep)[0] for p in step3)
print("   A9  in-scope by top-level subdir:")
for k, v in subdirs.most_common():
    print("          %-40s %4d" % (k, v))
print()
print("=" * 100)
print("B. THE COMPARATOR: a citation is a bracketed/named reference to another report.")
print("=" * 100)
# several defensible definitions of "citation" -- run them ALL, print all
PATTERNS = {
    "P1 backtick-path":  re.compile(r"`[^`\n]*\.md`"),
    "P2 bare D-number":  re.compile(r"\bD\d{1,3}\b"),
    "P3 D-number+ext":   re.compile(r"\bD\d{1,3}[_A-Za-z0-9\-]*\.md\b"),
    "P4 C-number":       re.compile(r"\bC-\d{2}\b"),
    "P5 any C- or D-":   re.compile(r"\b[CD]-?\d{1,3}\b"),
}
docs = {}
for p in step3:
    try:
        docs[p] = open(p, "r", encoding="utf-8", errors="replace").read()
    except OSError:
        pass
print("   COUNTED: %d in-scope documents read" % len(docs))
print()
for label, pat in PATTERNS.items():
    tot = 0
    files_with = 0
    distinct = set()
    for p, t in docs.items():
        ms = pat.findall(t)
        if ms:
            files_with += 1
            tot += len(ms)
            distinct.update(ms)
    print("   %-18s occurrences=%6d  files=%4d  distinct=%5d"
          % (label, tot, files_with, len(distinct)))
print()
print("   ^ IF THESE FIVE DIFFER, THE 172 IS A COUNT OF ITS COMPARATOR.")
