"""
D118 probe 6 -- T6 adjudication + T3 adjudication, both by READING.

T6: of the 58 misses, which are path-shaped (a real claim) vs bare extensions,
    globs, shell comments, chain-of-command.wrappers and drive-relative paths?
    The Lead's category of interest: a miss that is NOT a probe defect and NOT
    the report being correct.

T3: of the 194 NOT-RESOLVABLE fragments, classify the same way.

Both probes draw the same line, so one classifier serves both.
"""
import os, re, sys, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
REPORTS = os.path.join(WS, "RE_Library", "07_OUTPUT", "reports")
DEEP = os.path.join(REPORTS, "DEEP")

t56 = json.load(open(os.path.join(DEEP, "_d120_t5t6.json")))
t23 = json.load(open(os.path.join(DEEP, "_d120_t2t3.json")))

BARE_EXT  = re.compile(r"^\.[A-Za-z0-9]{1,8}$")           # ".go", ".yaml"
GLOBSHAPE = re.compile(r"[*?]")                            # "C-0*.tsv"
COMMENT   = re.compile(r"^\s*#")                           # "# program foo.exe"
WRAPPER   = re.compile(r"^(?:Get-ChildItem|Get-Content|Select-String|where\.exe|charm:|\.strings)\b")
DOTPATH   = re.compile(r"^\.{2,}[\\/]|^[A-Za-z]:\\\.{3}")  # "...\x.exe", "C:\...\x.exe"
HTMLFRAG  = re.compile(r"^<.*>$")
DRIVE_ABS = re.compile(r"^[A-Za-z]:[\\/]")

def classify(tok):
    t = tok.strip()
    if COMMENT.match(t):   return "SHELL-COMMENT"
    if WRAPPER.match(t):   return "COMMAND-PREFIX"
    if BARE_EXT.match(t):  return "BARE-EXTENSION"
    if HTMLFRAG.match(t):  return "PLACEHOLDER"
    if DOTPATH.match(t):   return "ELIDED-PATH"
    if GLOBSHAPE.search(t):return "GLOB"
    if DRIVE_ABS.match(t): return "DRIVE-ABSOLUTE"
    if (("\\" in t) or ("/" in t)):
        return "RELATIVE-PATH"
    if "." in t:
        return "BARE-FILENAME"
    return "OTHER"

print("=" * 78)
print("T6 -- THE 58 MISSES, ADJUDICATED")
print("=" * 78)
d6 = collections.Counter()
pathish = []
for m in t56["miss"]:
    k = classify(m["token"])
    d6[k] += 1
    if k in ("RELATIVE-PATH", "DRIVE-ABSOLUTE", "BARE-FILENAME"):
        pathish.append((k, m))
print("   MANDATORY distribution of miss shape:")
for k, v in d6.most_common():
    print("      %-18s %4d" % (k, v))
print("      %-18s %4d  <- total misses" % ("TOTAL", len(t56["miss"])))
print()
print("   >>> PATH-SHAPED misses (the only class that can be a real claim): %d" % len(pathish))
for k, m in pathish:
    print("      [%s] %s:%d  tags=%s" % (k, m["report"][:30], m["line"], "y" if m["tag"] else "-"))
    print("            `%s`" % m["token"][:80])
print()

# now the decisive question: do ANY of them exist by basename anywhere?
print("   --- do the path-shaped misses exist by BASENAME anywhere in the workspace? ---")
reach = []
for k, m in pathish:
    base = os.path.basename(m["token"].replace("/", os.sep))
    hit = None
    for dp, ds, fs in os.walk(WS):
        if base in fs:
            hit = os.path.join(dp, base); break
    if hit:
        reach.append((m["token"], hit.replace(WS + "\\", "")))
print("   MANDATORY distribution: path-shaped misses resolvable by basename")
print("      resolvable-by-basename : %d" % len(reach))
print("      NOT resolvable at all  : %d" % (len(pathish) - len(reach)))
for t, h in reach:
    print("         `%s`" % t[:56])
    print("              -> %s" % h[:96])
print()

# the class the Lead cares about
print("   >>> MISSES THAT ARE NOT A PROBE DEFECT AND NOT A CORRECT NEGATIVE:")
hard = [m for k, m in pathish if not any(m["token"] == t for t, _ in reach)]
print("       count: %d" % len(hard))
for m in hard:
    print("         %s:%d  `%s`" % (m["report"][:34], m["line"], m["token"][:70]))
print()

print("=" * 78)
print("T3 -- THE 194 NOT-RESOLVABLE FRAGMENTS, ADJUDICATED")
print("=" * 78)
d3 = collections.Counter()
byrep = collections.defaultdict(collections.Counter)
for b, ln, tok in t23["unresolved"]:
    k = classify(tok)
    d3[k] += 1
    byrep[b][k] += 1
print("   MANDATORY distribution of fragment shape:")
for k, v in d3.most_common():
    print("      %-18s %4d  (%.1f%%)" % (k, v, 100.0 * v / max(1, len(t23["unresolved"]))))
print()
print("   --- by report, the RELATIVE-PATH + BARE-FILENAME residue ---")
for b in sorted(byrep):
    r = byrep[b].get("RELATIVE-PATH", 0) + byrep[b].get("BARE-FILENAME", 0) + byrep[b].get("DRIVE-ABSOLUTE", 0)
    if r:
        print("      %-46s %3d" % (b[:46], r))
print()
print("   >>> REAL UNRESOLVABLE PATH-LIKE FRAGMENTS (aggregate): %d" % (
    d3.get("RELATIVE-PATH", 0) + d3.get("BARE-FILENAME", 0) + d3.get("DRIVE-ABSOLUTE", 0)))
print("   >>> of which GLOBS (resolvable in principle, not by exact name): %d" % d3.get("GLOB", 0))
print()

json.dump(dict(t6_dist=dict(d6), t6_pathish=len(pathish), t6_reach=len(reach),
               t6_hard=hard, t3_dist=dict(d3)), open(os.path.join(DEEP, "_d120_t3t6adj.json"), "w"), indent=1)
print("wrote _d120_t3t6adj.json")
