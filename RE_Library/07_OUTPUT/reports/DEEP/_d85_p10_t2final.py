"""
D85 probe 10 -- T2 FINAL: corrected cause census + reduction, three fixes.

FIX 1: D74's cause label "block/iterator variables" conflated three things.
       Recensus all 45 with disjoint causes.
FIX 2: `origin_of` never inspected the ITERATED EXPRESSION itself for
       datastore/cmd_exec. ping_net.rb:33 iterates
       `Rex::Socket::RangeWalker.new(datastore['RANGE']).each` -- datastore
       visible in the iterated expr, reported UNRESOLVED.
FIX 3: instance variables (@pid) assigned in a DIFFERENT method must be chased
       method-wide, not site-wide.

Reported as TWO numbers that are honestly different:
    automatic reduction (probe 8) = 0
    hand-audited reduction         = this probe
"""
import os, re, json, collections

HERE = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\reports\DEEP"
ROOT = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\01_SOURCE_c2\metasploit"
sites = json.load(open(os.path.join(HERE, "_d85_sites.json")))
unres = [s for s in sites if s["cls"] == "UNRESOLVABLE"]

DEFRX = re.compile(r"^(\s*)def\s+([\w?!=\.]+)\s*(?:\(([^)]*)\))?")
BLOCK_HDR = re.compile(r"do\s*\|([^|]*)\||\{\s*\|([^|]*)\|")
DS_SRC = re.compile(r"datastore\[|datastore\.")
TARGET_SRC = re.compile(
    r"\bcmd_exec\b|session\.|sess\.|\.fs\.|dir\.entries|read_file|get_env|"
    r"sys\.config|sys\.process|readdir|\.entries", re.I)
HELPER_SRC = re.compile(r"\b(get_env|get_envs|writable_dir|temp_dir|rand_text|Rex::Text)\b")


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


def find_assign(lines, name, before, didx, ivar=False):
    pat = re.compile(r"(?<![\w.@])" + re.escape(name) + r"\s*(\|\|=|=)(?!=|>)")
    lo = didx if didx is not None else 0
    for k in range(before, lo - 1, -1):
        m = pat.search(lines[k])
        if m:
            return k, lines[k].strip()
    if ivar:
        for k, l in enumerate(lines):
            if pat.search(l):
                return k, l.strip()
    return None, None


def classify_src(src):
    if DS_SRC.search(src):
        return "DATASTORE"
    if HELPER_SRC.search(src):
        return "MIXIN_HELPER"
    if TARGET_SRC.search(src):
        return "SESSION_TARGET"
    return None


rows = []
for s in unres:
    p = os.path.join(ROOT, s["file"])
    text = open(p, encoding="utf-8", errors="ignore").read()
    lines = text.split("\n")
    idx = s["line"] - 1
    didx, dname, params = enclosing_def(lines, idx)
    cause = None
    verdict = None
    trail = []

    toks = []
    for m in re.finditer(r"#\{([^{}]*)\}", s["cmd"]):
        inner = m.group(1).strip()
        bm = re.match(r"^([A-Za-z_@$][\w?!]*)", inner)
        toks.append((bm.group(1) if bm else None, inner))

    if didx is None:
        cause = "NO_ENCLOSING_DEF"

    for tok, inner in toks:
        if tok is None:
            cause = cause or "EXPRESSION_NOT_NAME"
            continue
        # instance variable?
        if tok.startswith("@") or tok.startswith("$"):
            cause = cause or "INSTANCE_VAR"
            k, src = find_assign(lines, tok, idx, didx, ivar=True)
            if k is not None:
                trail.append("%s <- L%d %s" % (tok, k + 1, src[:78]))
                c = classify_src(src)
                verdict = verdict or c or "INSTANCE_VAR_UNRESOLVED"
            else:
                trail.append("%s no assignment" % tok)
            continue
        bk, it = block_iter(lines, tok, idx, didx)
        if bk is not None:
            cause = cause or "BLOCK_VARIABLE"
            trail.append("%s <- L%d iter: %s" % (tok, bk + 1, it))
            # FIX 2: classify the ITERATED EXPRESSION itself
            c = classify_src(it or "")
            if c:
                verdict = verdict or c
            coll = None
            cm = re.search(r"([A-Za-z_@$][\w?!]*)\s*(?:\.each|\.each_line|\.map|\.times)", it or "")
            if cm:
                coll = cm.group(1)
            elif it:
                cm2 = re.search(r"([A-Za-z_@$][\w?!]*)\s*$", it)
                coll = cm2.group(1) if cm2 else None
            if coll and verdict is None:
                k, src = find_assign(lines, coll, bk, didx)
                if k is not None:
                    trail.append("   ^ %s <- L%d %s" % (coll, k + 1, src[:78]))
                    verdict = verdict or classify_src(src)
                else:
                    # shovel accumulation?
                    sh = re.compile(r"(?<![\w.@])" + re.escape(coll) + r"\s*<<\s*(.+)")
                    for k2 in range(bk, (didx if didx is not None else 0) - 1, -1):
                        m2 = sh.search(lines[k2])
                        if m2:
                            trail.append("   ^ %s << L%d %s" % (coll, k2 + 1, m2.group(1).strip()[:70]))
                            # chase the RHS's source: usually a prior cmd_exec block var
                            for k3 in range(k2, (didx if didx is not None else 0) - 1, -1):
                                if TARGET_SRC.search(lines[k3]) or DS_SRC.search(lines[k3]):
                                    trail.append("   ^^ source L%d %s" % (k3 + 1, lines[k3].strip()[:74]))
                                    verdict = verdict or classify_src(lines[k3])
                                    break
                            break
            continue
        # plain local
        k, src = find_assign(lines, tok, idx, didx)
        if k is not None:
            cause = cause or "LOCAL_ASSIGN_UNCLASSIFIED"
            trail.append("%s <- L%d %s" % (tok, k + 1, src[:78]))
            verdict = verdict or classify_src(src)
        else:
            cause = cause or "NO_ASSIGNMENT_FOUND"
            nparams = enclosing_def(lines, idx)[2]
            if tok in nparams:
                cause = "PARAMETER_OF_ENCLOSING_DEF"
            trail.append("%s: not found" % tok)

    if verdict is None and TARGET_SRC.search(s["cmd"]):
        verdict = "SESSION_TARGET_OPERAND"
    rows.append(dict(s, cause=cause or "OTHER", verdict=verdict or "STILL_UNRESOLVED",
                     trail="; ".join(trail)))

print("=== CORRECTED CAUSE CENSUS (D74's label split into disjoint causes) ===")
print("   total:", len(rows))
for k, v in collections.Counter(r["cause"] for r in rows).most_common():
    print("   %-32s %4d" % (k, v))
print()
print("=== REDUCTION VERDICT (mandatory distribution) ===")
for k, v in collections.Counter(r["verdict"] for r in rows).most_common():
    print("   %-32s %4d" % (k, v))
red = [r for r in rows if r["verdict"] not in ("STILL_UNRESOLVED", "INSTANCE_VAR_UNRESOLVED")]
print()
print("   REDUCED:", len(red), "of", len(rows))
print()
print("=== REDUCED SITES WITH CHAINS ===")
for r in red:
    print("   %s:%d  => %s" % (r["file"], r["line"], r["verdict"]))
    print("        %s" % r["trail"][:150])
print()
print("=== STILL UNRESOLVED WITH REASON ===")
for r in rows:
    if r["verdict"] in ("STILL_UNRESOLVED", "INSTANCE_VAR_UNRESOLVED"):
        print("   %s:%d  cause=%s" % (r["file"], r["line"], r["cause"]))
        print("        %s" % r["trail"][:130])
json.dump(rows, open(os.path.join(HERE, "_d85_t2final.json"), "w"), indent=1)
