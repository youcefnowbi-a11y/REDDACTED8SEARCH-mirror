"""
D85 probe 1 -- ESCAPING PRIMITIVE CENSUS (Instrument Rule 20).

RULE 20: a named path is not a census. I know two escaping paths from D74
(.shellescape in osx/capture/screen.rb, .gsub in grandstream_gxp1600_sip.rb).
Those are TWO PATHS. I must enumerate the CALL SITES of the escaping primitive
across the whole population, and print the enumeration beside the claim.

So: first census what escaping primitives EXIST in modules/post, then intersect
with the 49 DATASTORE sites. Distribution printed, not just a total
(Lead's promoted rule: a classifier returning one value for 100% of input is
broken, not decisive).
"""
import os, re, collections

ROOT = r"RE_Library\01_SOURCE_c2\metasploit"
POST = os.path.join(ROOT, "modules", "post")

FILES = []
for dp, ds, fs in os.walk(POST):
    for f in fs:
        if f.endswith(".rb"):
            FILES.append(os.path.join(dp, f))
print("post .rb files:", len(FILES))
print()

# --- RULE 20: enumerate the primitive's call sites, tree-wide, BEFORE intersecting
PRIMS = {
    "shellescape":      r"\.shellescape\b",
    "Shellwords.escape": r"Shellwords\.escape\b",
    "shellwords_escape": r"shellwords_escape\b",
    "gsub_quote":       r"\.gsub\(\s*['\"]['\"]",
    "gsub_dq":          r"\.gsub\(\s*['\"]\"['\"]",
    "inspect_quote":    r"\.inspect\b",
    "dump":             r"\.dump\b",
    "encode_x":         r"\.encode\b",
    "CGI.escape":       r"CGI\.escape\b",
    "URI.encode":       r"URI\.(?:encode|escape)\b",
    "Rex::Text.encode": r"Rex::Text\.encode_base64",
    "escape_single":    r"escape_single_quotes",
    "escape_double":    r"escape_double_quotes",
    "sanitize":         r"\bsanitize\b",
    "shell_command":    r"\bshell_command\b",
}

print("=== RULE 20: CENSUS OF ESCAPING PRIMITIVES, tree-wide, modules/post ===")
print("(occurrences / files -- the ENUMERATION, printed beside the claim)")
for label, rx in PRIMS.items():
    tot, fl = 0, set()
    for p in FILES:
        t = open(p, encoding="utf-8", errors="ignore").read()
        n = len(re.findall(rx, t))
        if n:
            tot += n
            fl.add(os.path.relpath(p, ROOT))
    print("   %-22s %5d occurrences / %3d files" % (label, tot, len(fl)))
print()
print("=== positive control: is `.gsub` itself common? (proves the probe can see gsub) ===")
g = 0
for p in FILES:
    g += len(re.findall(r"\.gsub\b", open(p, encoding="utf-8", errors="ignore").read()))
print("   .gsub total:", g)
print()

# --- Now the population: the 49 DATASTORE sites, rebuilt exactly as D74 did
CALL = re.compile(r"(?<![A-Za-z0-9_.'\"])(cmd_exec|create_process)\s*\(")
INTERP = re.compile(r"#\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}")
DEFRX = re.compile(r"^(\s*)def\s+([\w?!=\.]+)\s*(?:\(([^)]*)\))?")
DS = re.compile(r"datastore\[|datastore\.")


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


# provenance resolver (same rule as D74 probe 7)
SESSIONP = re.compile(r"\bfs\.|\bcmd_exec\b|\bget_env\b|\bsysinfo\b|\bshell_command")
REMOTEP = re.compile(r"Net::HTTP|HTTPClient|Rex::Proto|\.recv\b|\.body\b|\.send_request|Rex::Socket")
MIXINP = re.compile(r"\b(get_env|get_envs|writable_dir|temp_dir|rand_text|Rex::Text|"
                    r"File\.join|File\.dirname|File\.basename|expand_path|report_)\b")
TARGETREAD = re.compile(r"cat\s|nvram\s+get|dmesg|ps\s|ls\s|reg\s+query|find\s|grep\s|"
                        r"whoami|hostname|uname|id\b|grab_|dump|hashdump|enum_|read_file")
TOOLPATH = re.compile(r"whereis|which\s|command\s+-v|\bfile\?|\bexecutable\?")
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


def resolve(text, lines, name, idx, depth=0, chain=None):
    if chain is None:
        chain = []
    if depth > 8:
        return "UNRESOLVABLE", chain
    didx, dname, params = enclosing_def(lines, idx)
    if name in params and dname:
        callp = re.compile(r"(?<![\w.])" + re.escape(dname) + r"\s*\(([^)]*)\)")
        pi = params.index(name)
        for cm in callp.finditer(text):
            if text[:cm.start()].count("\n") == idx:
                continue
            cargs = split_args(cm.group(1))
            if pi < len(cargs):
                c = classify(cargs[pi])
                if c:
                    return c, chain
                nm = re.match(r"^([A-Za-z_@$][\w?!]*)", cargs[pi])
                if nm:
                    return resolve(text, lines, nm.group(1),
                                   text[:cm.start()].count("\n"), depth + 1, chain)
        return "PARAM_UNRESOLVED", chain
    j, rhs = find_assign_near(lines, name, idx, didx if didx is not None else 0)
    if rhs is None:
        j, rhs = find_assign_file(lines, name)
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
            c = classify(body)
            return (c, chain) if c else ("METHOD_BODY_UNRESOLVED", chain)
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
            cls = []
            for e in exprs:
                inner = e[2:-1].strip()
                bm = re.match(r"^([A-Za-z_@$][\w?!]*)", inner)
                if not bm:
                    continue
                c, _ = resolve(text, lines, bm.group(1), ln0)
                cls.append(c)
            ORDER = ["REMOTE_RESPONSE", "SESSION_TARGET", "DATASTORE", "MIXIN_HELPER",
                     "LOCAL_TOOL_PATH", "HARDCODED", "METHOD_BODY_UNRESOLVED",
                     "PARAM_UNRESOLVED", "UNRESOLVABLE"]
            site = min(cls, key=lambda c: ORDER.index(c)) if cls else "UNRESOLVABLE"
            rows.append(dict(file=rel, line=ln0 + 1, cls=site,
                             cmd=lit[1], raw=text, nargs=len(args),
                             args=args))

print("=== POPULATION (D74 basis, first-arg non-datastore interpolated) ===")
print("sites:", len(rows))
print("distribution (MANDATORY per Lead's promoted rule):")
for k in ["REMOTE_RESPONSE", "SESSION_TARGET", "DATASTORE", "MIXIN_HELPER",
          "LOCAL_TOOL_PATH", "HARDCODED", "METHOD_BODY_UNRESOLVED",
          "PARAM_UNRESOLVED", "UNRESOLVABLE"]:
    n = sum(1 for r in rows if r["cls"] == k)
    if n:
        print("   %-24s %4d" % (k, n))
import json
json.dump([{k: v for k, v in r.items() if k != "raw"} for r in rows],
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_d85_pop.json"), "w"), indent=1)
print()
print("written _d85_pop.json")
