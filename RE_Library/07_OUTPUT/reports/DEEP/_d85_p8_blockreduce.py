"""
D85 probe 8 -- T2: REDUCE the BLOCK_VARIABLE cause (29 sites, the largest).

Method: for a site interpolating a block variable `x`, walk backwards to the
enclosing `... do |x|` or `{ |x| }` header, extract the ITERATED expression,
resolve THAT through the same provenance engine, and inherit its class.

The reduction is only credited where the iterated expression resolves. Where it
does not, the site stays UNRESOLVABLE and is reported as such -- a reducer that
reports 100% success is the classifier-100% failure mode.
"""
import os, re, json, collections

HERE = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\reports\DEEP"
ROOT = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\01_SOURCE_c2\metasploit"

sites = json.load(open(os.path.join(HERE, "_d85_sites.json")))
unres = [s for s in sites if s["cls"] == "UNRESOLVABLE"]
print("UNRESOLVABLE sites:", len(unres))

DEFRX = re.compile(r"^(\s*)def\s+([\w?!=\.]+)\s*(?:\(([^)]*)\))?")
INTERP = re.compile(r"#\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}")
DS = re.compile(r"datastore\[|datastore\.")
MIXINP = re.compile(r"\b(get_env|get_envs|writable_dir|temp_dir|rand_text|Rex::Text|"
                    r"File\.join|File\.dirname|expand_path|report_)\b")
TOOLPATH = re.compile(r"whereis|which\s|command\s+-v|\bfile\?|\bexecutable\?")
REMOTEP = re.compile(r"Net::HTTP|HTTPClient|Rex::Proto|\.recv\b|\.body\b|send_request|Rex::Socket")
TARGETREAD = re.compile(r"cat\s|nvram\s+get|dmesg|ps\s|ls\s|reg\s+query|find\s|grep\s|"
                        r"whoami|hostname|uname|grab_|dump|hashdump|enum_|read_file|"
                        r"readdir|entries|dir\.|sys\.|sess\.|session\.")
HARDP = re.compile(r"^([A-Z][A-Z0-9_]*|['\"].*['\"]|[\d\.\s\-\+\*\/]+)$")


def classify(r):
    r = (r or "").strip()
    if not r:
        return None
    if DS.search(r):
        return "DATASTORE"
    if MIXINP.search(r):
        return "MIXIN_HELPER"
    if TOOLPATH.search(r):
        return "LOCAL_TOOL_PATH"
    if REMOTEP.search(r):
        return "REMOTE_RESPONSE"
    if TARGETREAD.search(r):
        return "SESSION_TARGET"
    if HARDP.match(r):
        return "HARDCODED"
    return None


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


def assign_pattern(name):
    return re.compile(r"(?<![\w.])" + re.escape(name) + r"\s*(\|\|=|=)(?!=|>)")


def resolve(text, lines, name, idx, depth=0, seen=None):
    if seen is None:
        seen = set()
    if depth > 8 or name in seen:
        return "UNRESOLVABLE"
    seen = seen | {name}
    didx, dname, params = enclosing_def(lines, idx)
    if name in params and dname:
        pi = params.index(name)
        callp = re.compile(r"(?<![\w.])" + re.escape(dname) + r"\s*\(([^)]*)\)")
        for cm in callp.finditer(text):
            if text[:cm.start()].count("\n") == idx:
                continue
            cargs = [a.strip() for a in cm.group(1).split(",")]
            if pi < len(cargs):
                c = classify(cargs[pi])
                if c:
                    return c
                nm = re.match(r"^([A-Za-z_@$][\w?!]*)", cargs[pi])
                if nm:
                    return resolve(text, lines, nm.group(1),
                                   text[:cm.start()].count("\n"), depth + 1, seen)
        return "PARAM_UNRESOLVED"
    pat = assign_pattern(name)
    rhs, j = None, None
    for k in range(idx, (didx if didx is not None else 0) - 1, -1):
        m = pat.search(lines[k])
        if m:
            j, rhs = k, lines[k][m.end():].strip()
            break
    if rhs is None:
        for k, l in enumerate(lines):
            m = pat.search(l)
            if m:
                j, rhs = k, l[m.end():].strip()
                break
    if rhs is not None:
        c = classify(rhs)
        if c:
            return c
        nm = re.match(r"^([A-Za-z_@$][\w?!]*)", rhs)
        if nm and nm.group(1) != name:
            return resolve(text, lines, nm.group(1), j, depth + 1, seen)
    dpat = re.compile(r"^\s*def\s+" + re.escape(name) + r"\b")
    for k, l in enumerate(lines):
        if dpat.match(l):
            c = classify("\n".join(lines[k:k + 30]))
            return c if c else "METHOD_BODY_UNRESOLVED"
    return "UNRESOLVABLE"


# --- BLOCK REDUCER -----------------------------------------------------------
BLOCK_HDR = re.compile(r"do\s*\|([^|]*)\||\{\s*\|([^|]*)\|")


def reduce_block(lines, var, idx, didx):
    """Find the nearest enclosing block header naming `var`, return the iterated expr."""
    for k in range(idx, (didx if didx is not None else 0) - 1, -1):
        for m in BLOCK_HDR.finditer(lines[k]):
            names = [n.strip() for n in (m.group(1) or m.group(2) or "").split(",")]
            names = [re.sub(r"^[*&]", "", n).split("=")[0].strip() for n in names]
            if var in names:
                pre = lines[k][:m.start()].strip()
                return k, pre
    return None, None


ORDER = ["REMOTE_RESPONSE", "SESSION_TARGET", "DATASTORE", "MIXIN_HELPER",
         "LOCAL_TOOL_PATH", "HARDCODED", "METHOD_BODY_UNRESOLVED",
         "PARAM_UNRESOLVED", "UNRESOLVABLE"]

reduced, still = [], []
for s in unres:
    p = os.path.join(ROOT, s["file"])
    text = open(p, encoding="utf-8", errors="ignore").read()
    lines = text.split("\n")
    idx = s["line"] - 1
    didx, dname, params = enclosing_def(lines, idx)
    toks = []
    for e in INTERP.finditer(s["cmd"]):
        inner = e.group(0)[2:-1].strip()
        bm = re.match(r"^([A-Za-z_@$][\w?!]*)", inner)
        toks.append(bm.group(1) if bm else None)
    toks = [t for t in toks if t]
    got = None
    trail = []
    if didx is not None:
        for tok in toks:
            bk, iter_expr = reduce_block(lines, tok, idx, didx)
            if iter_expr is None:
                continue
            trail.append("%s <- L%d iter: %s" % (tok, bk + 1, iter_expr[:60]))
            # the iterated expr's own terminal name
            nm = re.search(r"([A-Za-z_@$][\w?!]*)\s*$", iter_expr)
            if nm:
                c = resolve(text, lines, nm.group(1), bk, 0, {tok})
                if c and c not in ("UNRESOLVABLE", "PARAM_UNRESOLVED"):
                    got = c if got is None else min(got, c, key=lambda x: ORDER.index(x))
    if got:
        reduced.append(dict(s, newcls=got, trail="; ".join(trail)))
    else:
        still.append(dict(s, trail="; ".join(trail) or "(no block header found)"))

print()
print("=== T2 REDUCTION OF THE BLOCK_VARIABLE CAUSE ===")
print("   attempted      :", len(unres))
print("   REDUCED        :", len(reduced))
print("   still unresolved:", len(still))
print()
print("   MANDATORY distribution of reduced classes:")
for k, v in collections.Counter(r["newcls"] for r in reduced).most_common():
    print("      %-22s %4d" % (k, v))
print()
print("=== REDUCED SITES (with the iteration chain) ===")
for r in reduced:
    print("   %s:%d  %s -> %s" % (r["file"], r["line"], r["newcls"], r["cmd"][:62]))
    print("        %s" % r["trail"])
print()
print("=== STILL UNRESOLVABLE (with why) ===")
for r in still:
    print("   %s:%d  %s" % (r["file"], r["line"], r["cmd"][:70]))
    print("        %s" % r["trail"])
json.dump({"reduced": reduced, "still": still},
          open(os.path.join(HERE, "_d85_t2.json"), "w"), indent=1)
