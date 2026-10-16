"""
D85 probe 9 -- T2 HAND-AUDIT of the 29 BLOCK_VARIABLE sites.

Probe 8 delivered 0 automatic reductions and printed every iteration chain. The
chains show WHY: the iterated collections are themselves built by `<<` (shovel)
accumulation from an earlier cmd_exec, or arrive as method parameters. My
resolver follows `=`, `||=` and `def`; it has no rule for `<<`.

So this probe does NOT try to be automatic. It prints, for each of the 29 sites,
the iterated collection's own definition line, so the CLASS can be read by eye.
Two numbers are reported and they are DIFFERENT:
   - automatic reduction (probe 8) : 0
   - hand-auditable reduction      : this probe, per site, read by eye
Reporting only the first would understate; reporting only the second would
pretend a tracer exists that does not.
"""
import os, re, json, collections

HERE = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\reports\DEEP"
ROOT = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\01_SOURCE_c2\metasploit"
t2 = json.load(open(os.path.join(HERE, "_d85_t2.json")))
still = t2["still"]
print("UNRESOLVABLE sites carried into hand-audit:", len(still))
print()

DEFRX = re.compile(r"^(\s*)def\s+([\w?!=\.]+)\s*(?:\(([^)]*)\))?")
BLOCK_HDR = re.compile(r"do\s*\|([^|]*)\||\{\s*\|([^|]*)\|")
SHOVEL = re.compile(r"(?<![\w.@])([A-Za-z_@$][\w?!]*)\s*<<\s*(.+)")
ASSIGN = re.compile(r"(?<![\w.@])([A-Za-z_@$][\w?!]*)\s*(\|\|=|=)(?!=|>)\s*(.+)")

# source fragments that PROVE a target-derived origin
TARGET_SRC = re.compile(
    r"cmd_exec|session\.|sess\.|\.fs\.|dir\.entries|read_file|get_env|"
    r"sys\.config|sys\.process|gather|hashdump|registry|reg\s+query", re.I)
DS_SRC = re.compile(r"datastore\[|datastore\.")


def enclosing_def(lines, idx):
    for i in range(idx, -1, -1):
        m = DEFRX.match(lines[i])
        if m:
            params = []
            if m.group(3):
                params = [p.strip() for p in m.group(3).split(",")]
            else:
                rest = lines[i][m.end(2):].strip()
                if rest and not rest.startswith("#"):
                    params = [p.strip() for p in rest.split(",")]
            params = [re.sub(r"^[*&]", "", p).split("=")[0].strip() for p in params]
            return i, m.group(2), [p for p in params if p]
    return None, None, []


def block_iter(lines, var, idx, didx):
    for k in range(idx, (didx if didx is not None else 0) - 1, -1):
        for m in BLOCK_HDR.finditer(lines[k]):
            names = [n.strip() for n in (m.group(1) or m.group(2) or "").split(",")]
            names = [re.sub(r"^[*&]", "", n).split("=")[0].strip() for n in names]
            if var in names:
                return k, lines[k][:m.start()].strip()
    return None, None


def origin_of(lines, coll, before, didx, depth=0):
    """Find how `coll` got its value: shovel, assignment, or parameter."""
    if depth > 6 or coll is None:
        return None, None
    # shovel accumulation
    for k in range(before, (didx if didx is not None else 0) - 1, -1):
        m = SHOVEL.search(lines[k])
        if m and m.group(1) == coll:
            return k, "SHOVEL: " + lines[k].strip()
    for k in range(before, (didx if didx is not None else 0) - 1, -1):
        m = ASSIGN.search(lines[k])
        if m and m.group(1) == coll:
            return k, "ASSIGN: " + lines[k].strip()
    # whole file
    for k, l in enumerate(lines):
        m = ASSIGN.search(l)
        if m and m.group(1) == coll:
            return k, "ASSIGN(file): " + l.strip()
    # parameter?
    didx2, dname2, params = enclosing_def(lines, before)
    if coll in params:
        return didx2, "PARAMETER of def %s" % dname2
    return None, None


rows = []
for s in still:
    p = os.path.join(ROOT, s["file"])
    text = open(p, encoding="utf-8", errors="ignore").read()
    lines = text.split("\n")
    idx = s["line"] - 1
    didx, dname, params = enclosing_def(lines, idx)
    found = []
    for m in re.finditer(r"#\{([^{}]*)\}", s["cmd"]):
        inner = m.group(1).strip()
        bm = re.match(r"^([A-Za-z_@$][\w?!]*)", inner)
        if not bm:
            continue
        tok = bm.group(1)
        bk, it = block_iter(lines, tok, idx, didx)
        if bk is None:
            continue
        coll = None
        cm = re.search(r"([A-Za-z_@$][\w?!]*)\s*(?:\.each|\.each_line|\.map|\.times)", it or "")
        if cm:
            coll = cm.group(1)
        elif it:
            cm2 = re.search(r"([A-Za-z_@$][\w?!]*)\s*$", it)
            coll = cm2.group(1) if cm2 else None
        ok, how = origin_of(lines, coll, bk, didx)
        found.append((tok, coll, bk, it, ok, how))
    rows.append(dict(s, found=found))

print("=== HAND-AUDIT: iteration origin for each of the", len(rows), "sites ===")
cls_count = collections.Counter()
for r in rows:
    print()
    print("%s:%d" % (r["file"], r["line"]))
    print("    cmd: %s" % r["cmd"][:96])
    if not r["found"]:
        print("    -> NO BLOCK HEADER (not a block-variable site at all)")
        cls_count["NO_BLOCK"] += 1
        continue
    verdict = None
    for tok, coll, bk, it, ok, how in r["found"]:
        print("    block var `%s` <- L%s   iter: %s" % (tok, bk + 1, it))
        if how:
            print("        origin L%s  %s" % (ok + 1, how[:104]))
            if DS_SRC.search(how):
                verdict = verdict or "DATASTORE"
            elif "PARAMETER" in how:
                verdict = verdict or "PARAMETER"
            elif TARGET_SRC.search(how):
                verdict = verdict or "SESSION_TARGET"
        else:
            print("        origin: NOT FOUND")
    if verdict is None:
        # classify by the iterated expression itself
        for tok, coll, bk, it, ok, how in r["found"]:
            if it and TARGET_SRC.search(it):
                verdict = "SESSION_TARGET"
                break
    if verdict is None:
        # the cmd itself is a target read -> its operand is target data
        if TARGET_SRC.search(r["cmd"]):
            verdict = "SESSION_TARGET_OPERAND"
        else:
            verdict = "STILL_UNRESOLVED"
    cls_count[verdict] += 1
    print("    => %s" % verdict)

print()
print("=== HAND-AUDIT VERDICT DISTRIBUTION (mandatory) ===")
for k, v in cls_count.most_common():
    print("   %-24s %4d" % (k, v))
json.dump([{k: v for k, v in r.items() if k != "text"} for r in rows],
          open(os.path.join(HERE, "_d85_t2audit.json"), "w"), indent=1)
