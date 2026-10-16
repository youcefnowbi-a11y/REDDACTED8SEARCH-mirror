"""
D99 probe 1 -- the DENOMINATOR at THIS revision (D94 T2), plus the POPULATION of
citation edges at this revision.

D94 SS3.3 defined the boundary and then sampled it four times in 22 minutes. It has
not been sampled since. This probe applies D94's OWN stated rule, verbatim:

  IN SCOPE : every *.md under RE_Library\07_OUTPUT\reports\, recursive,
             EXCLUDING any path containing '\extractions\',
             EXCLUDING reports\README.md
  OUT      : CROSSREF_AUDIT.md, D59_crossref_remediation.md, D94_*, all non-.md

FLOOR LOGIC: a count of FILES ON DISK is a floor on the number of documents the
corpus contains, because a document that was written and later deleted, or that
exists only as an attachment, is invisible to it. The floor carries its interval;
it does NOT carry a rate (D94 SS4: three rates spanned 6x).

CRITICAL CONTROL: re-derive D94's FIVE historical readings from the file mtimes
that produce them, so I can test whether the growth is NEW FILES or RE-SCOPING.
"""
import os, re, json, datetime

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
REPORTS = os.path.join(WS, "RE_Library", "07_OUTPUT", "reports")

OUT_OF_SCOPE_NAMES = {"CROSSREF_AUDIT.md", "D59_crossref_remediation.md", "README.md"}


def in_scope(rel):
    if "\\extractions\\" in rel or "/extractions/" in rel:
        return False
    base = os.path.basename(rel)
    if base in OUT_OF_SCOPE_NAMES:
        return False
    if base.startswith("D94_"):
        return False
    return True


all_md = []          # every .md under reports\, no exclusions
for dp, ds, fs in os.walk(REPORTS):
    for f in fs:
        if f.lower().endswith(".md"):
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, WS)
            st = os.stat(p)
            all_md.append(dict(path=rel, name=f, size=st.st_size,
                               mtime=st.st_mtime,
                               iso=datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")))

scope = [d for d in all_md if in_scope(d["path"])]
print("=== THE DENOMINATOR AT THIS REVISION (D94 SS3.3 rule applied verbatim) ===")
print("   every .md under reports\\ recursively           :", len(all_md))
print("   in scope (D94's rule)                           :", len(scope))
print("   excluded                                        :", len(all_md) - len(scope))
print()
print("   exclusion breakdown:")
from collections import Counter
exc = Counter()
for d in all_md:
    if in_scope(d["path"]):
        continue
    b = d["name"]
    if b in OUT_OF_SCOPE_NAMES:
        exc[b] += 1
    elif b.startswith("D94_"):
        exc["D94_* (this lane's predecessor)"] += 1
    elif "extractions" in d["path"]:
        exc["under \\extractions\\"] += 1
    else:
        exc["OTHER -- needs naming"] += 1
for k, v in exc.most_common():
    print("      %-40s %3d" % (k, v))
print()

# --- layer split
deep = [d for d in scope if d["path"].lower().endswith("reports\\deep\\" + d["name"].lower())
        or "\\reports\\deep\\" in d["path"].lower()]
other = [d for d in scope if d not in deep]
print("   in-scope located under reports\\DEEP\\           :", len(deep))
print("   in-scope located elsewhere under reports\\       :", len(other))
for d in other:
    print("      %s" % d["path"])
print()

# --- THE INTERVAL: what is the timestamp of the newest in-scope document?
scope_sorted = sorted(scope, key=lambda d: d["mtime"])
newest = scope_sorted[-1]
oldest = scope_sorted[0]
print("=== INTERVAL ===")
print("   oldest in-scope .md :", oldest["iso"], " ", oldest["name"])
print("   newest in-scope .md :", newest["iso"], " ", newest["name"])
print()
t = datetime.datetime.now()
print("   probe wall-clock    :", t.strftime("%Y-%m-%d %H:%M:%S"))
print()

# --- D94's five historical readings, RE-DERIVED from mtime
print("=== D94's FIVE readings RE-DERIVED from mtime (the growth-vs-rescope test) ===")
print("   %-22s %-9s %-9s %-9s %s" % ("moment (D94's table)", "all.md", "in scope", "D94 said", "match"))
readings = [("19:13:19", 90), ("19:24:57", 90), ("19:27:18", 105),
            ("19:31:24", 106), ("19:35:49", 113)]
# YEAR CORRECTED: the corpus is dated 2026-10-15/16, not 2025. The first run of this
# probe used 2025 and returned 0 at every mark -- a clean, decisive, entirely fake
# number. See D99 SS5 for the failure record. The year is now taken FROM THE DATA.
_yr = datetime.datetime.fromtimestamp(max(d["mtime"] for d in all_md)).year
print("   [year taken from the newest file's mtime: %d]" % _yr)
for hhmmss, claimed in readings:
    hh, mm, ss = (int(x) for x in hhmmss.split(":"))
    cut = datetime.datetime(_yr, 10, 16, hh, mm, ss).timestamp()
    a = len([d for d in all_md if d["mtime"] <= cut])
    s = len([d for d in scope if d["mtime"] <= cut])
    print("   %-22s %-9d %-9d %-9d %s" % (hhmmss, a, s, claimed,
                                          "YES" if s == claimed else "no (%+d)" % (s - claimed)))
print()
print("   NOTE: mtime is LAST-WRITE time, not CREATION time. A document edited after")
print("   its creation is counted at its EDIT time. So this reconstruction is valid")
print("   only for files never edited after their burst, and the residual is printed.")
print()

# --- GROWTH vs RE-SCOPING: files written inside each D94 interval
print("=== WHAT ACTUALLY CHANGED IN EACH INTERVAL (new files vs scope moves) ===")
marks = [(datetime.datetime(_yr,10,16,19,13,19), "19:13:19"),
         (datetime.datetime(_yr,10,16,19,24,57), "19:24:57"),
         (datetime.datetime(_yr,10,16,19,27,18), "19:27:18"),
         (datetime.datetime(_yr,10,16,19,31,24), "19:31:24"),
         (datetime.datetime(_yr,10,16,19,35,49), "19:35:49")]
for i in range(1, len(marks)):
    lo, lon = marks[i-1]
    hi, hin = marks[i]
    new = [d for d in all_md if lo.timestamp() < d["mtime"] <= hi.timestamp()]
    print("   %s -> %s : %d .md written" % (lon, hin, len(new)))
    for d in sorted(new, key=lambda x: x["mtime"]):
        print("        %s  %8d  %s" % (d["iso"][11:], d["size"], os.path.basename(d["path"])))
print()

json.dump(dict(all_md=all_md, scope=[d["path"] for d in scope],
               n_all=len(all_md), n_scope=len(scope),
               newest=newest, oldest=oldest),
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_d99_denom.json"), "w"), indent=1)
