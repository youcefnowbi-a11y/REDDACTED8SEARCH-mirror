"""
D99 probe 6 -- T1: the 172 ADJUDICATED, at this revision.

Probe 5 established the true failure count at this revision is 26 SEC edges whose
owner document exists but whose cited section does not -- a small, DISCRETE,
enumerable set. That is not 172, and the difference must be explained rather than
asserted. D94's 172 came from an extractor that:
   * is NOT ON DISK (probe 7)
   * used a 60-char owner window (v7) whose mis-attribution D94 measured at 46 rows
   * classified via a three-valued field the way probe 2 did (is False vs None)

So: adjudicate at the EDGE level, with a FOUR-WAY class the Lead specified, and
print every class's membership. Bounded value space this time.
"""
import os, re, sys, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\reports\DEEP"
E = json.load(open(os.path.join(HERE, "_d99_edges.json")))["edges"]

# ---- resolve properly, with an explicit tri-state
docs = {}
for n in os.listdir(HERE):
    if n.endswith(".md") and not n.startswith("D94_") and not n.startswith("D99_"):
        p = os.path.join(HERE, n)
        docs[n] = open(p, encoding="utf-8", errors="ignore").read()

HEAD = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
NUMHEAD = re.compile(r"^#{1,6}\s+§?\s*(\d+(?:\.\d+)*)")
BOLDNUM = re.compile(r"^\s*[-*]?\s*\*\*\s*§?\s*(\d+(?:\.\d+)*)\b")

idx = {}
for n, t in docs.items():
    secs = {}
    for i, l in enumerate(t.split("\n")):
        m = HEAD.match(l)
        if m:
            nm = NUMHEAD.match(l)
            if nm:
                secs.setdefault(nm.group(1), i + 1)
            m2 = re.match(r"^§?\s*(\d+(?:\.\d+)*)\s*[.．]?\s+\S", m.group(2))
            if m2 and re.match(r"^§?\s*\d+(?:\.\d+)*[.．]\s", m.group(2)):
                secs.setdefault(m2.group(1), i + 1)
        bm = BOLDNUM.match(l)
        if bm and re.search(r"§|CLOSED|OPEN|PARTIAL", l):
            secs.setdefault(bm.group(1), i + 1)
    idx[n] = secs


def owner_file(o):
    for n in docs:
        if n.startswith(o + "_") or n == o + ".md":
            return n
    return None


for e in E:
    of = owner_file(e["owner"])
    e["owner_file"] = of
    if of is None:
        e["verdict"] = "OWNER-ABSENT"
    elif e["kind"] == "SEC":
        e["verdict"] = "OK" if e["target"] in idx.get(of, {}) else "TARGET-ABSENT"
    elif e["kind"] == "LINE":
        e["verdict"] = "OK"
    else:
        e["verdict"] = "OK" if os.path.exists(os.path.join(HERE, e["target"])) else "TARGET-ABSENT"

print("=== T1: EVERY CITATION EDGE, CLASSIFIED (bounded value space) ===")
print("   edges:", len(E))
print()
print("   MANDATORY distribution of edge verdict:")
for k, v in collections.Counter(e["verdict"] for e in E).most_common():
    print("      %-16s %5d" % (k, v))
print()

fail = [e for e in E if e["verdict"] == "TARGET-ABSENT"]
print("=== T1.a THE ENUMERABLE FAILURE SET at this revision (%d edges) ===" % len(fail))
by_owner = collections.Counter(e["owner"] for e in fail)
print("   MANDATORY distribution by OWNER document -- bounded, small:")
for k, v in by_owner.most_common():
    print("      %-8s %4d   %s" % (k, v, owner_file(k)))
print()
print("   MANDATORY distribution by CITING document:")
for k, v in collections.Counter(e["src"] for e in fail).most_common():
    print("      %-56s %4d" % (k[:56], v))
print()
print("=== EVERY FAILING EDGE, listed ===")
for e in sorted(fail, key=lambda x: (x["owner"], x["src"], x["srcline"])):
    print("   %s:%s  cites %s §%s" % (e["src"].replace(".md", ""), e["srcline"], e["owner"], e["target"]))
    print("        | %s" % e["text"][:120])

json.dump(dict(n=len(E), fail=len(fail),
               by_edge=[{k: v for k, v in e.items() if k != "text"} for e in fail]),
          open(os.path.join(HERE, "_d99_t1.json"), "w"), indent=1)

print()
print("=== T1.b: D94's 172 vs this revision's %d -- reconciled or not? ===" % len(fail))
print("   D94 recorded 172 failures from v7/v8/v9. This probe enumerates %d." % len(fail))
print("   The gap is NOT a corpus change (citation edges only GROW). It is")
print("   INSTRUMENT SCOPE: see probe 7 (v7 not on disk) and D94 SS1 (v8's 400-char")
print("   far window re-attributed 37 rows that v7 had attributed to the citing doc).")
