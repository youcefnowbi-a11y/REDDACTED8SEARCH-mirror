"""
D74 probe 5 -- T1 v2: provenance with METHOD-DEFINITION and PARAMETER-BINDING resolution.

Blindnesses found by _d74_p4_diagnose.py and fixed here:
  B1: a name that is `def name` is a METHOD, not a local. Its provenance is the
      method's body. (puppet_exe: puppet.rb:44, facter_exe likewise)
  B2: a name that is a parameter of the enclosing `def` has provenance = the
      caller's argument. (pvalue in `def nvram_get(pvalue)`)
  B3: an assignment may sit in a DIFFERENT method in the same file than the call
      site. Searching only the enclosing method inflated UNRESOLVABLE.

Resolution order for a name at a site:
  1. parameter of the enclosing def  -> caller's argument (recursively)
  2. local/ivar assignment, nearest preceding inside the enclosing method
  3. any assignment to that name elsewhere in the SAME FILE
  4. `def name` in the same file      -> provenance of the method body
  5. UNRESOLVABLE
"""
import os, re, collections, json

ROOT = r"RE_Library\01_SOURCE_c2\metasploit"
POST = os.path.join(ROOT, "modules", "post")
HERE = os.path.dirname(os.path.abspath(__file__))

CALL = re.compile(r"(?<![A-Za-z0-9_.'\"])(cmd_exec|create_process)\s*\(")
INTERP = re.compile(r"#\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}")
DEFRX = re.compile(r"^(\s*)def\s+([\w?!=\.]+)\s*(?:\(([^)]*)\))?")
MAXDEPTH = 8

DS = re.compile(r"datastore\[|datastore\.")
SESSIONP = re.compile(r"\bsession\.|\bsysinfo\b|\bfs\.|\bcmd_exec\b|\bget_env\b|"
                      r"\bshell_command|\bget_envs\b")
REMOTEP = re.compile(r"Net::HTTP|HTTPClient|Rex::Proto|\.recv\b|\bresponse\b|\.body\b|"
                     r"\.send_request|Rex::Socket|\bSMBSimpleClient|\.read\b|\bRex::Proto::SMB\b")
MIXINP = re.compile(r"\b(writable_dir|temp_dir|writable_directory|rand_text|Rex::Text|"
                    r"File\.join|File\.dirname|File\.basename|expand_path|"
                    r"report_|writable_dir|dir\b|pwd\b)")
HARDP = re.compile(r"^([A-Z][A-Z0-9_]*|['\"].*['\"]|[\d\.\s\-\+\*\/]+)$")


def split_args(s):
    args, depth, cur, i, instr = [], 0, [], 0, None
    while i < len(s):
        c = s[i]
        if instr:
            cur.append(c)
            if c == "\\":
                i += 1
                if i < len(s):
                    cur.append(s[i])
                i += 1
                continue
            if c == instr:
                instr = None
        elif c in "'\"":
            instr = c
            cur.append(c)
        elif c in "([{":
            depth += 1
            cur.append(c)
        elif c in ")]}":
            if depth == 0:
                break
            depth -= 1
            cur.append(c)
        elif c == "," and depth == 0:
            args.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
        i += 1
    if "".join(cur).strip():
        args.append("".join(cur).strip())
    return args


def extract_call(text, start):
    depth, i, out, instr = 0, start, [], None
    while i < len(text):
        c = text[i]
        if instr:
            out.append(c)
            if c == "\\":
                i += 1
                if i < len(text):
                    out.append(text[i])
                i += 1
                continue
            if c == instr:
                instr = None
        elif c in "'\"":
            instr = c
            out.append(c)
        elif c in "([{":
            depth += 1
            out.append(c)
        elif c in ")]}":
            depth -= 1
            if depth == 0:
                return "".join(out)[1:], i
            out.append(c)
        else:
            out.append(c)
        i += 1
    return None, i


def single_literal(arg):
    arg = arg.strip()
    if not arg or arg[0] not in "'\"":
        return None
    q = arg[0]
    i = 1
    while i < len(arg):
        if arg[i] == "\\":
            i += 2
            continue
        if arg[i] == q:
            return (q, arg[1:i]) if arg[i + 1:].strip() == "" else None
        i += 1
    return None


def assign_pattern(name):
    # a name may be a local, an ivar, or a constant; allow the sigil to precede
    return re.compile(r"(?<![\w.])" + re.escape(name) + r"\s*(\|\|=|=)(?!=|>)")


def find_assign_near(lines, name, idx, lower=0):
    pat = assign_pattern(name)
    for j in range(idx, lower - 1, -1):
        m = pat.search(lines[j])
        if m:
            return j, lines[j][m.end():].strip()
    return None, None


def find_assign_file(lines, name):
    pat = assign_pattern(name)
    for j, l in enumerate(lines):
        m = pat.search(l)
        if m:
            return j, l[m.end():].strip()
    return None, None


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


def classify_rhs(r):
    r = (r or "").strip()
    if not r:
        return None
    if DS.search(r):
        return "DATASTORE"
    if REMOTEP.search(r):
        return "REMOTE_RESPONSE"
    if SESSIONP.search(r):
        return "SESSION_TARGET"
    if MIXINP.search(r):
        return "MIXIN_HELPER"
    if HARDP.match(r):
        return "HARDCODED"
    return None


def resolve(text, lines, name, idx, depth=0, chain=None):
    """Return (class, chain). idx is the 0-based line of the site."""
    if chain is None:
        chain = []
    if depth > MAXDEPTH:
        return "UNRESOLVABLE", chain + ["depth limit"]
    didx, dname, params = enclosing_def(lines, idx)

    # 1. parameter binding
    if name in params and dname:
        chain.append("PARAM of %s()" % dname)
        callp = re.compile(r"(?<![\w.])" + re.escape(dname) + r"\s*\(([^)]*)\)")
        pi = params.index(name)
        for cm in callp.finditer(text):
            if text[:cm.start()].count("\n") == idx:
                continue
            cargs = split_args(cm.group(1))
            if pi < len(cargs):
                rhs = cargs[pi]
                chain.append("caller arg: %s" % rhs[:70])
                c = classify_rhs(rhs)
                if c:
                    return c, chain
                nm = re.match(r"^([A-Za-z_@$][\w?!]*)", rhs)
                if nm:
                    return resolve(text, lines, nm.group(1),
                                   text[:cm.start()].count("\n"), depth + 1, chain)
        return "PARAM_UNRESOLVED", chain

    # 2. nearest preceding assignment in the enclosing method
    j, rhs = find_assign_near(lines, name, idx, didx if didx is not None else 0)
    if rhs is None:
        # 3. anywhere in the file
        j, rhs = find_assign_file(lines, name)
        if rhs is not None:
            chain.append("FILE-LEVEL assign L%d: %s" % (j + 1, rhs[:70]))
    else:
        chain.append("assign L%d: %s" % (j + 1, rhs[:70]))
    if rhs is not None:
        c = classify_rhs(rhs)
        if c:
            return c, chain
        nm = re.match(r"^([A-Za-z_@$][\w?!]*)", rhs)
        if nm and nm.group(1) != name:
            return resolve(text, lines, nm.group(1), j, depth + 1, chain)

    # 4. def name
    dpat = re.compile(r"^\s*def\s+" + re.escape(name) + r"\b")
    for k, l in enumerate(lines):
        if dpat.match(l):
            body = "\n".join(lines[k:k + 30])
            chain.append("def %s at L%d" % (name, k + 1))
            c = classify_rhs(body)
            if c:
                chain.append("method body -> %s" % c)
                return c, chain
            return "METHOD_BODY_UNRESOLVED", chain
    return "UNRESOLVABLE", chain


rows = []
for dp, ds_, fs in os.walk(POST):
    for f in fs:
        if not f.endswith(".rb"):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, ROOT)
        text = open(p, encoding="utf-8", errors="ignore").read()
        lines = text.split("\n")
        for m in CALL.finditer(text):
            ls = text.rfind("\n", 0, m.start()) + 1
            nl = text.find("\n", ls)
            if text[ls:nl if nl > 0 else len(text)].lstrip().startswith("#"):
                continue
            ln0 = text[:m.start()].count("\n")
            argstr, _ = extract_call(text, m.end() - 1)
            if argstr is None:
                continue
            args = split_args(argstr)
            if not args:
                continue
            lit = single_literal(args[0])
            if not lit:
                continue
            exprs = [x.group(0) for x in INTERP.finditer(lit[1])]
            if not exprs:
                continue
            if any(e[2:-1].strip().startswith("datastore[") for e in exprs):
                continue
            for e in exprs:
                inner = e[2:-1].strip()
                bm = re.match(r"^([A-Za-z_@$][\w?!]*)", inner)
                if not bm:
                    continue
                cls, chain = resolve(text, lines, bm.group(1), ln0)
                rows.append(dict(file=rel, line=ln0 + 1, expr=e, name=bm.group(1),
                                 cls=cls, chain=chain, cmd=lit[1][:130]))

print("=== T1 v2: PROVENANCE OF NON-DATASTORE INTERPOLATED cmd_exec ARGS ===")
print("expressions:", len(rows), " distinct sites:", len(set((r["file"], r["line"]) for r in rows)))
print()
print("=== BY EXPRESSION ===")
for k, v in collections.Counter(r["cls"] for r in rows).most_common():
    print("   %-24s %4d  %5.1f%%" % (k, v, 100.0 * v / len(rows)))
print()
ORDER = ["REMOTE_RESPONSE", "SESSION_TARGET", "DATASTORE", "MIXIN_HELPER", "HARDCODED",
         "METHOD_BODY_UNRESOLVED", "PARAM_UNRESOLVED", "UNRESOLVABLE"]
sites = collections.defaultdict(list)
for r in rows:
    sites[(r["file"], r["line"])].append(r)
sitecls = {k: min((r["cls"] for r in v), key=lambda c: ORDER.index(c)) for k, v in sites.items()}
print("=== BY SITE (highest-risk expression wins) ===")
for k in ORDER:
    n = sum(1 for v in sitecls.values() if v == k)
    if n:
        print("   %-24s %4d" % (k, n))
print()

json.dump(rows, open(os.path.join(HERE, "_d74_t1v2.json"), "w"), indent=1)
print("written: _d74_t1v2.json")

# print resolution samples for the classes that matter
for want in ["REMOTE_RESPONSE", "SESSION_TARGET", "DATASTORE", "UNRESOLVABLE",
             "PARAM_UNRESOLVED", "METHOD_BODY_UNRESOLVED"]:
    sel = [r for r in rows if r["cls"] == want]
    if not sel:
        continue
    print()
    print("=== %s (%d expressions) ===" % (want, len(sel)))
    for r in sel[:14]:
        print("   %s:%d  %s" % (r["file"], r["line"], r["expr"]))
        for c in r["chain"]:
            print("        %s" % c)
