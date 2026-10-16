"""
D74 probe 7 -- T1 v3: correct the SESSION_TARGET over-inclusion found by eye.

ERROR FOUND (probe 6): `ctl_path -> whereis('cupsctl') -> cmd_exec("whereis #{exe}")`
was classed SESSION_TARGET because SESSIONP matches `cmd_exec`. But the tainted
value there is the ARGUMENT `'cupsctl'` (hardcoded); the cmd_exec RESULT is a path
to a local binary. That is a framework/local-tool lookup, not target data.

RULE REFINEMENT (stated before re-running):
  REMOTE_RESPONSE : value derived from data the TARGET sent back
                    (HTTP/SMB/DNS/raw socket reads, or a command whose result is
                    target filesystem CONTENT, e.g. `cat`, `nvram get`, `dmesg`)
  SESSION_TARGET  : value that is an IDENTITY/ATTRIBUTE of the target session
                    (whoami, hostname, sysinfo, session.*, architecture)
  LOCAL_TOOL_PATH : value is the location of a binary on the target from a
                    whereis/which/command -v lookup, or a framework helper path
  MIXIN_HELPER    : framework Post:: helper return (get_env, writable_dir, rand_text)
  DATASTORE       : operator-set option
  HARDCODED       : literal / constant
  UNRESOLVABLE    : chain does not terminate
The distinction LOCAL_TOOL_PATH vs REMOTE_RESPONSE matters because a tool path is
not attacker-influenced content; a `cat` of a target file is.
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
REMOTEP = re.compile(r"Net::HTTP|HTTPClient|Rex::Proto|\.recv\b|\bresponse\b|\.body\b|"
                     r"\.send_request|Rex::Socket|\bSMBSimpleClient|\.read\b")
MIXINP = re.compile(r"\b(get_env|get_envs|writable_dir|temp_dir|rand_text|Rex::Text|"
                    r"File\.join|File\.dirname|File\.basename|expand_path|report_)\b")
# command RESULT that is target file CONTENT or target stateful read
TARGETREAD = re.compile(r"cat\s|nvram\s+get|dmesg|ps\s|ls\s|reg\s+query|"
                        r"find\s|grep\s|whoami|hostname|uname|sysinfo|id\b|"
                        r"show\s+running|show\s+config|export\b|"
                        r"grab_|dump|hashdump|enum_|read_file|read_reg")
TOOLPATH = re.compile(r"whereis|which\s|command\s+-v|\bfile\?|\bexecutable\?")
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


def resolve(text, lines, name, idx, depth=0, chain=None):
    if chain is None:
        chain = []
    if depth > MAXDEPTH:
        return "UNRESOLVABLE", chain + ["depth limit"]
    didx, dname, params = enclosing_def(lines, idx)
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
                c = classify(rhs)
                if c:
                    return c, chain
                nm = re.match(r"^([A-Za-z_@$][\w?!]*)", rhs)
                if nm:
                    return resolve(text, lines, nm.group(1),
                                   text[:cm.start()].count("\n"), depth + 1, chain)
        return "PARAM_UNRESOLVED", chain
    j, rhs = find_assign_near(lines, name, idx, didx if didx is not None else 0)
    if rhs is None:
        j, rhs = find_assign_file(lines, name)
        if rhs is not None:
            chain.append("FILE-LEVEL assign L%d: %s" % (j + 1, rhs[:70]))
    else:
        chain.append("assign L%d: %s" % (j + 1, rhs[:70]))
    if rhs is not None:
        c = classify(rhs)
        if c:
            return c, chain
        nm = re.match(r"^([A-Za-z_@$][\w?!]*)", rhs)
        if nm and nm.group(1) != name:
            return resolve(text, lines, nm.group(1), j, depth + 1, chain)
    dpat = re.compile(r"^\s*def\s+" + re.escape(name) + r"\b")
    for k, l in enumerate(lines):
        if dpat.match(l):
            body = "\n".join(lines[k:k + 30])
            chain.append("def %s at L%d" % (name, k + 1))
            c = classify(body)
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

ORDER = ["REMOTE_RESPONSE", "SESSION_TARGET", "DATASTORE", "MIXIN_HELPER",
         "LOCAL_TOOL_PATH", "HARDCODED", "METHOD_BODY_UNRESOLVED",
         "PARAM_UNRESOLVED", "UNRESOLVABLE"]
print("=== T1 v3 (SESSION_TARGET corrected) ===")
print("expressions:", len(rows), " sites:", len(set((r["file"], r["line"]) for r in rows)))
print()
print("=== BY EXPRESSION ===")
for k in ORDER:
    n = sum(1 for r in rows if r["cls"] == k)
    if n:
        print("   %-24s %4d  %5.1f%%" % (k, n, 100.0 * n / len(rows)))
print()
sites = collections.defaultdict(list)
for r in rows:
    sites[(r["file"], r["line"])].append(r)
sitecls = {k: min((r["cls"] for r in v), key=lambda c: ORDER.index(c)) for k, v in sites.items()}
print("=== BY SITE ===")
for k in ORDER:
    n = sum(1 for v in sitecls.values() if v == k)
    if n:
        print("   %-24s %4d" % (k, n))
print()
print("=== SESSION_TARGET after correction ===")
for r in rows:
    if r["cls"] == "SESSION_TARGET":
        print("   %s:%d  %s" % (r["file"], r["line"], r["expr"]))
        for c in r["chain"][:3]:
            print("        %s" % c)
json.dump(rows, open(os.path.join(HERE, "_d74_t1v3.json"), "w"), indent=1)
print()
print("written _d74_t1v3.json")
