"""
D118 probe 1 -- T4: EVERY DOCUMENT NUMBER THAT MAPS TO MORE THAN ONE FILE.

D108 found D11 (5) and D12 (2) BECAUSE IT LOOKED FOR A CONTROL CASE. The Lead
wants the exhaustive list. Rule 22 applied to document numbers: a document
number is a NAME, not an IDENTITY.

Also enumerates the HOLES: numbers allocated then abandoned (D109), which is a
different species from a collision.

D12 family check per the brief: D6, D29/D38/D50/D46/D44 sub-numbering.
"""
import os, re, sys, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
REPORTS = os.path.join(WS, "RE_Library", "07_OUTPUT", "reports")
DEEP = os.path.join(REPORTS, "DEEP")

# every .md anywhere under reports\, so a collision cannot hide in a subdir
files = []
for dp, ds, fs in os.walk(REPORTS):
    if "\\extractions\\" in dp:
        continue
    for f in fs:
        if f.endswith(".md"):
            files.append(os.path.join(dp, f))

NUM = re.compile(r"^(?:D|C-)(\d+)_")
fam = collections.defaultdict(list)
other = []
for p in files:
    b = os.path.basename(p)
    m = NUM.match(b)
    if m:
        fam[int(m.group(1))].append(b)
    else:
        other.append(b)

print("=" * 78)
print("T4 -- COLLISIONS: document numbers mapping to >1 file")
print("=" * 78)
multi = {k: sorted(v) for k, v in fam.items() if len(v) > 1}
print("   MANDATORY distribution: numbers with >1 file")
for k in sorted(multi):
    print("      D%-5d -> %d files" % (k, len(multi[k])))
    for n in multi[k]:
        print("               %s" % n)
print()
print("   COLLIDING NUMBERS : %d" % len(multi))
print("   FILES INVOLVED    : %d" % sum(len(v) for v in multi.values()))
print("   UNIQUE NUMBERS    : %d" % len(fam))
print("   TOTAL .md FILES   : %d" % len(files))
print("   non-numbered files: %d  -> %s" % (len(other), "; ".join(sorted(other)[:12])))
print()

# ---- the brief's named families, checked explicitly
print("   --- the brief's named families, checked individually ---")
for n in (6, 29, 38, 50, 46, 44, 11, 12):
    v = sorted(fam.get(n, []))
    tag = "COLLISION" if len(v) > 1 else "unique"
    print("      D%-4d [%-9s] %d file(s)" % (n, tag, len(v)))
    for x in v:
        print("                  %s" % x)
print()

# ---- HOLES: a number never used between used numbers
print("   --- HOLES in the D-sequence (numbers skipped between used ones) ---")
used = sorted(fam)
holes = [n for n in range(min(used), max(used) + 1) if n not in fam]
print("      span D%d..D%d" % (min(used), max(used)))
print("      MANDATORY distribution: HOLES = %d" % len(holes))
print("      %s" % ", ".join("D%d" % h for h in holes))
print()

# ---- COUNT the citations per colliding number
print("   --- citation counts for each colliding number ---")
OUT = {"CROSSREF_AUDIT.md", "D59_crossref_remediation.md", "README.md"}
docs = {}
for p in files:
    b = os.path.basename(p)
    if b in OUT or b.startswith("D118_"):
        continue
    docs[b] = open(p, encoding="utf-8", errors="ignore").read()

rows = []
for k in sorted(multi):
    pat = re.compile(r"\bD%d\s*§" % k)
    tot = sum(len(pat.findall(t)) for t in docs.values())
    # also bare mentions
    bare = sum(len(re.findall(r"\bD%d\b" % k, t)) for t in docs.values())
    rows.append(dict(num=k, files=len(multi[k]), sec_cites=tot, all_mentions=bare))
tot_all = sum(sum(len(re.findall(r"\bD\d{1,3}\s*§", t)) for t in docs.values()) for _ in [0])
print("      %-6s %-7s %-10s %s" % ("num", "files", "SS-cites", "all mentions"))
for r in rows:
    print("      D%-5d %-7d %-10d %d" % (r["num"], r["files"], r["sec_cites"], r["all_mentions"]))
amb = sum(r["sec_cites"] for r in rows)
totss = sum(len(re.findall(r"\bD\d{1,3}\s*§", t)) for t in docs.values())
print()
print("      AMBIGUOUS SS-citations : %d" % amb)
print("      TOTAL SS-citations     : %d" % totss)
print("      SHARE                  : %.1f%%" % (100.0 * amb / max(1, totss)))
print("      control (D6, unambiguous check): %d" % sum(len(re.findall(r"\bD6\s*§", t)) for t in docs.values()))
print()

json.dump(dict(multi=multi, holes=holes, rows=rows, totss=totss, amb=amb),
          open(os.path.join(DEEP, "_d120_t4.json"), "w"), indent=1)
print("wrote _d120_t4.json")
