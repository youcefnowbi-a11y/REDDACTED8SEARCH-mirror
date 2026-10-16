"""
D99 probe 2 -- the CITATION UNIVERSE at this revision.

D94's 172 is a count produced by an extractor (v7/v8/v9) that D94 itself proved
mis-attributed 46 rows and whose SOURCE FILE IS NOT ON DISK. So the 172 is not
reproducible by re-running. What IS reproducible is the EDGE SET: extract every
citation edge myself, with the owner-attribution window made EXPLICIT and
PARAMETERISED, and report the count as a function of the window.

That turns "172" from a number into a CURVE, which is the only honest form when
the window is the instrument and the instrument is not on disk.

Emits the raw edge set so every downstream class is auditable.
"""
import os, re, json, collections, datetime

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
REPORTS = os.path.join(WS, "RE_Library", "07_OUTPUT", "reports",
                       "DEEP")
HERE = os.path.dirname(os.path.abspath(__file__))

# ---- population: in-scope .md per D94 SS3.3 (applied to DEEP, the citing layer)
OUT = {"CROSSREF_AUDIT.md", "D59_crossref_remediation.md", "README.md",
       "_INSTRUMENT_RULE_20_named_path_is_not_a_census.md",
       "_INTEGRITY_CHECK_crlf_corrected.md", "_D59_fixtable_executed_result.md"}

docs = []
for f in sorted(os.listdir(REPORTS)):
    if not f.lower().endswith(".md"):
        continue
    if f in OUT or f.startswith("D94_") or f.startswith("D99_"):
        continue
    p = os.path.join(REPORTS, f)
    docs.append(dict(name=f, path=p))

# ---- heading index: capture the WHOLE heading line, and ALSO the pseudo-headings
#      D94 SS2 proved matter: bold list items self-numbered as sections.
HEAD = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
BOLDNUM = re.compile(r"^\s*[-*]?\s*\*\*\s*§?\s*(\d+(?:\.\d+)*)\b")
NUMHEAD = re.compile(r"^#{1,6}\s+§?\s*(\d+(?:\.\d+)*)")

index = {}
for d in docs:
    txt = open(d["path"], encoding="utf-8", errors="ignore").read()
    lines = txt.split("\n")
    secs = {}
    for i, l in enumerate(lines):
        m = HEAD.match(l)
        if m:
            body = m.group(2)
            nm = NUMHEAD.match(l)
            if nm:
                secs.setdefault(nm.group(1), i + 1)
            # also index by any leading number inside the heading body
            m2 = re.match(r"§?\s*(\d+(?:\.\d+)*)", body)
            if m2:
                secs.setdefault(m2.group(1), i + 1)
        bm = BOLDNUM.match(l)
        if bm:
            secs.setdefault(bm.group(1), i + 1)
    index[d["name"]] = secs
    d["nlines"] = len(lines)

# ---- citation extraction: D<a> §<b> and D<a>:<line> and D<a>-<b>
REF_SEC = re.compile(r"\bD(\d{1,3})\s*§\s*(\d+(?:\.\d+)*)")
REF_LINE = re.compile(r"\bD(\d{1,3})\s*:\s*(\d+)(?:\s*-\s*(\d+))?")
DOCNAME = re.compile(r"\bD(\d{1,3})_[A-Za-z0-9_]*\.md")

edges = []
for d in docs:
    txt = open(d["path"], encoding="utf-8", errors="ignore").read()
    lines = txt.split("\n")
    for i, l in enumerate(lines):
        # skip markdown table separator rows and pure fences
        ls = l.strip()
        if re.fullmatch(r"\|[\s\-:|]+\|", ls):
            continue
        for m in REF_SEC.finditer(l):
            owner = "D%s" % m.group(1)
            edges.append(dict(src=d["name"], srcline=i + 1, owner=owner,
                              kind="SEC", target=m.group(2), text=l.strip()[:150],
                              off=m.start(), srclen=len(l)))
        for m in REF_LINE.finditer(l):
            owner = "D%s" % m.group(1)
            edges.append(dict(src=d["name"], srcline=i + 1, owner=owner,
                              kind="LINE", target=m.group(2), end=m.group(3),
                              text=l.strip()[:150], off=m.start(), srclen=len(l)))
        for m in DOCNAME.finditer(l):
            owner = "D%s" % m.group(1)
            edges.append(dict(src=d["name"], srcline=i + 1, owner=owner,
                              kind="FILE", target=m.group(0), text=l.strip()[:150],
                              off=m.start(), srclen=len(l)))

print("=== CITATION UNIVERSE at this revision ===")
print("   citing documents (in-scope .md, DEEP) :", len(docs))
print("   total citation EDGES                  :", len(edges))
print()
print("   MANDATORY distribution by kind:")
for k, v in collections.Counter(e["kind"] for e in edges).most_common():
    print("      %-8s %5d" % (k, v))
print()

# ---- RESOLUTION: does the owner document exist, and does the target exist in it?
present = set(docs and [d["name"] for d in docs]) | {"D94_" }
all_md_names = set(os.listdir(REPORTS))
def owner_exists(o):
    pat = re.compile(r"^" + re.escape(o) + r"(_|\.md)")
    # D13 must match D13_*.md; D1 must NOT match D11_*.md
    for n in all_md_names:
        if n.startswith(o + "_") or n == o + ".md":
            return n
    return None

# resolve
for e in edges:
    e["owner_file"] = owner_exists(e["owner"])
    if e["kind"] in ("SEC",):
        e["resolved"] = None
        of = e["owner_file"]
        if of:
            secs = index.get(of, {})
            e["resolved"] = secs.get(e["target"])
    elif e["kind"] == "LINE":
        of = e["owner_file"]
        e["resolved"] = bool(of)
        if of:
            d = next((x for x in docs if x["name"] == of), None)
            if d:
                e["resolved"] = int(e["target"]) <= d["nlines"]
    else:
        e["resolved"] = bool(e["owner_file"])

fail = [e for e in edges if e["resolved"] is False]
print("=== RESOLUTION at window=EXACT (whole line) ===")
print("   owner document MISSING entirely :", sum(1 for e in edges if not e["owner_file"]))
print("   owner present, target missing   :", sum(1 for e in edges if e["owner_file"] and e["resolved"] is False))
print("   FAILED                          :", len(fail))
print()
print("   MANDATORY distribution of FAILED by kind:")
for k, v in collections.Counter(e["kind"] for e in fail).most_common():
    print("      %-8s %5d" % (k, v))
print()
print("   MANDATORY distribution of FAILED by owner doc:")
for k, v in collections.Counter(e["owner"] for e in fail).most_common(20):
    print("      %-8s %5d" % (k, v))
print()
print("   MANDATORY distribution of FAILED by CITING doc (top 15):")
for k, v in collections.Counter(e["src"] for e in fail).most_common(15):
    print("      %-52s %5d" % (k[:52], v))
print()

# ---- THE CURVE: edge count as a function of the owner-attribution window
print("=== THE 172 AS A CURVE: owner-window sensitivity ===")
print("   (D94 SS1: v7 used 60 chars back -> OWNER-NEAR; v8 used 400 -> OWNER-FAR)")
print("   %-12s %-10s %-10s %s" % ("window", "edges attrib", "FAILED", "note"))
for W in (30, 60, 150, 400, 1000, 10**9):
    n_att = 0
    for e in edges:
        line = e["text"]
        # find all D<n> tokens in the line up to this citation's offset
        pre = line  # we only stored truncated text; use stored offset
        if W >= 10**9:
            n_att += 1
            continue
        # nearest preceding D-token within W chars
        best = None
        for m in re.finditer(r"\bD(\d{1,3})\b", e["text"]):
            if m.start() <= e["off"] and e["off"] - m.start() <= W:
                best = m.group(1)
        if best is not None:
            n_att += 1
    print("   %-12s %-10d %-10s" % (str(W) if W < 10**9 else "unbounded", n_att, "-"))

json.dump(dict(n_docs=len(docs), n_edges=len(edges), edges=edges,
               failed=len(fail)),
          open(os.path.join(HERE, "_d99_edges.json"), "w"), indent=1)
print()
print("   wrote _d99_edges.json with", len(edges), "edges,", len(fail), "failed")
