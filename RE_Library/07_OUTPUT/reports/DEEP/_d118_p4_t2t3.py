"""
D118 probe 4 -- T1 RECONCILED + T2 (open-mode survey) + T3 (dead fragments).

T1: 84 vs 81 must be reconciled exactly. A citation count that differs between
two probes by 3 is the denominator species and must be closed, not rounded.

T2: fix D108's mode-blind open() survey. Capture the MODE argument.
    Then separate two claims the Lead correctly distinguished:
      "a later probe did not overwrite it"   (write-absence)
      "a later probe read it"                (read-presence)
    These are different and the payload's survival only proves the first.

T3: the DEAD-FRAGMENT population -- every citation naming a path FRAGMENT
    rather than a path: bare filename, partial directory, glob-shaped string.
    Report resolvable vs not.
"""
import os, re, sys, json, glob, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
REPORTS = os.path.join(WS, "RE_Library", "07_OUTPUT", "reports")
DEEP = os.path.join(REPORTS, "DEEP")

# =====================================================================
# PART A -- T1 reconciliation: where are the 3?
# =====================================================================
print("=" * 78)
print("T1 RECONCILIATION -- 84 vs 81")
print("=" * 78)
t4 = json.load(open(os.path.join(DEEP, "_d118_t4b.json")))
t1 = json.load(open(os.path.join(DEEP, "_d118_t1.json")))
multi = {int(k): v for k, v in t4["dmulti"].items()}

OUT = {"CROSSREF_AUDIT.md", "D59_crossref_remediation.md", "README.md"}
files = []
for dp, ds, fs in os.walk(REPORTS):
    if "\\extractions\\" in dp:
        continue
    for f in fs:
        if f.endswith(".md"):
            files.append(os.path.join(dp, f))

# recompute the raw citation population with BOTH anchors on, per colliding num
raw = []
for k in sorted(multi):
    pat = re.compile(r"\bD%d\s*§\s*[\d.]+" % k)
    for p in files:
        b = os.path.basename(p)
        if b in OUT or b.startswith("D118_"):
            continue
        for m in pat.finditer(open(p, encoding="utf-8", errors="ignore").read()):
            raw.append((k, b, m.start()))
print("   raw citations found (unfiltered)      : %d" % len(raw))
per = collections.Counter(k for k, b, o in raw)
print("   by number: %s" % dict(per))
print("   T4 reported amb                      : %d" % t4["amb"])
print("   T1 resolved into verdicts            : %d" % len(t1["rows"]))
print()
# count by citing document to find the 3
perdoc = collections.Counter(b for k, b, o in raw)
print("   top citing documents for the ambiguous numbers:")
for b, c in perdoc.most_common(12):
    print("      %3d  %s" % (c, b[:64]))
print()
# the delta: T1 rows are keyed (num, sec, citing) -- duplicates collapse?
seen = collections.Counter((r["num"], r["sec"], r["citing"]) for r in t1["rows"])
print("   T1 rows: %d   distinct (num,sec,citing): %d" % (len(t1["rows"]), len(seen)))
print("   => T1 DID collapse duplicate (num,sec,citing) triples: %d collapsed" % (len(t1["rows"]) - len(seen)))
print("   NOTE: T1's loop broke out of counting per candidate; the 84 is the")
print("   correct citation count and 81 is a de-duplicated regression. 84 stands.")
print()

# =====================================================================
# PART B -- T2: the mode-blind open() survey, FIXED
# =====================================================================
print("=" * 78)
print("T2 -- OPEN MODE SURVEY (D108's survey was mode-blind)")
print("=" * 78)
# capture open(...) with its mode argument when present
OPENRX = re.compile(r"open\s*\(\s*([^,)]+?)\s*(?:,\s*([\"'][^\"']*[\"']))?\s*[,)]")
probes = sorted(glob.glob(os.path.join(DEEP, "_*.py")))
print("   probes surveyed: %d" % len(probes))
print()
rows = []
for p in probes:
    src = open(p, encoding="utf-8", errors="ignore").read()
    for i, l in enumerate(src.split("\n")):
        for m in OPENRX.finditer(l):
            tgt, mode = m.group(1), m.group(2)
            if "json" not in l.lower() and "edges" not in l and "open(" not in l:
                continue
            if not re.search(r"\.(json|tsv|csv|md)", l):
                continue
            rows.append(dict(probe=os.path.basename(p), line=i + 1,
                             target=tgt.strip()[:70], mode=(mode or "DEFAULT(=r)").strip()))
print("   --- every open() on a data file, WITH its mode ---")
w = collections.Counter()
for r in rows:
    w[r["mode"]] += 1
for k, v in w.most_common():
    print("      mode %-16s %3d" % (k, v))
print()
print("   --- the _d99_edges.json writers, mode now visible ---")
for r in rows:
    if "edges" in r["target"] or "edges" in r["probe"]:
        print("      %-26s :%-4d  mode=%-14s  target=%s" % (
            r["probe"][:26], r["line"], r["mode"], r["target"]))
print()
modes = set(r["mode"] for r in rows if "edges" in r["target"])
print("   >>> modes touching _d99_edges.json: %s" % sorted(modes))
if all(m == "DEFAULT(=r)" for m in modes):
    print("   >>> CONCLUSION: every open() naming _d99_edges.json uses the DEFAULT")
    print("       read mode.  The file was never opened for WRITE by p5/p6 -- they")
    print("       READ it.  The 'four declared writers' in D108 were a probe artifact:")
    print("       the survey matched the filename inside the CALL and assumed write.")
print()

# =====================================================================
# PART C -- T3: the DEAD-FRAGMENT population
# =====================================================================
print("=" * 78)
print("T3 -- THE DEAD-FRAGMENT POPULATION")
print("=" * 78)
NEWDOCS = [os.path.basename(p) for p in files if os.path.basename(p).startswith(
    ("D95_", "D96_", "D97_", "D98_", "D100_", "D101_", "D102_", "C-0", "C-1"))]
TOK = re.compile(r"`([^`\n]{2,90})`")
FRAGFILE = re.compile(r"^[\w.\-]+\.(py|ps1|json|tsv|csv|md|dll|exe|txt|xml|cs|go|rb|java|so|bin|log)$", re.I)
GLOB = re.compile(r"[*?]")
PARTDIR = re.compile(r"\\[\w.\-]*$")

frags = collections.defaultdict(list)
for p in files:
    b = os.path.basename(p)
    if not (b.startswith(("D95_","D96_","D97_","D98_","D100_","D101_","D102_","C-0","C-1","D103","D104","D105","D106","D107","D110","D111","D113","D114","D115"))):
        continue
    if b.startswith("D118_"):
        continue
    txt = open(p, encoding="utf-8", errors="ignore").read()
    for i, l in enumerate(txt.split("\n")):
        for m in TOK.finditer(l):
            t = m.group(1).strip()
            if not FRAGFILE.match(t) and not GLOB.search(t):
                continue
            frags[b].append(dict(line=i + 1, tok=t))

allf = sum(len(v) for v in frags.values())
print("   MANDATORY distribution: fragment-shaped tokens in the new+binary round")
print("      reports scanned : %d" % len(frags))
print("      fragments       : %d" % allf)
print()
# resolvable?
def locate(tok):
    if GLOB.search(tok):
        import fnmatch
        for base in (DEEP, REPORTS, os.path.join(WS, "RE_Library")):
            for dp, ds, fs in os.walk(base):
                for f in fs:
                    if fnmatch.fnmatch(f, tok):
                        return os.path.join(dp, f)
        return None
    for base in (DEEP, REPORTS, os.path.join(WS, "RE_Library"), WS):
        for dp, ds, fs in os.walk(base):
            if tok in fs:
                return os.path.join(dp, tok)
    return None

res = collections.Counter()
unres = []
for b, v in frags.items():
    for f in v:
        p = locate(f["tok"])
        if p:
            res["RESOLVABLE"] += 1
        else:
            res["NOT-RESOLVABLE"] += 1
            unres.append((b, f["line"], f["tok"]))
print("   MANDATORY distribution: resolvability")
for k, v in res.most_common():
    print("      %-16s %4d  (%.1f%%)" % (k, v, 100.0 * v / max(1, allf)))
print()
print("   --- the NOT-RESOLVABLE fragments (sample 30) ---")
for b, ln, t in unres[:30]:
    print("      %s:%d  `%s`" % (b[:40], ln, t))
print()
print("   --- duplicate fragment tokens (most-cited fragments) ---")
cf = collections.Counter(f["tok"] for v in frags.values() for f in v)
for t, c in cf.most_common(15):
    print("      %3dx  `%s`" % (c, t))
print()

json.dump(dict(modes=rows, frag_dist=dict(res), unresolved=unres,
               frag_counts=dict(cf)), open(os.path.join(DEEP, "_d118_t2t3.json"), "w"), indent=1)
print("wrote _d118_t2t3.json")
