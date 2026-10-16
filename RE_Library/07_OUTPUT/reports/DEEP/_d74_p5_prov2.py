"""
D74 probe 5 -- T1 v2: provenance with METHOD-DEFINITION and PARAMETER-BINDING resolution.

Fixes three blindnesses found by _d74_p4_diagnose.py:
  B1: a name that is `def name` (or `def name=`) is a METHOD, not a local. Its
      provenance is the method's last expression. (puppet_exe:44)
  B2: a name that is a parameter of the enclosing `def` has provenance = the
      caller's argument. (pvalue in `def nvram_get(pvalue)`)
  B3: an ivar assigned at method/class scope is visible; `@` lookbehind was fine,
      the real miss was that the assignment was in a DIFFERENT method than the
      call site, and my search window was the enclosing method only.

Search order for a name at a site:
  1. parameter of enclosing def  -> PROVENANCE OF THE CALLER'S ARGUMENT
  2. local assignment in enclosing method (any position, nearest preceding)
  3. local assignment anywhere in the SAME FILE
  4. `def name` in the same file -> provenance of that method's body
  5. UNRESOLVABLE
"""
import os, re, collections, json

ROOT = r"RE_Library\01_SOURCE_c2\metasploit"
POST = os.path.join(ROOT, "modules", "post")
CALL = re.compile(r"(?<![A-Za-z0-9_.'\"])(cmd_exec|create_process)\s*\(")
INTERP = re.compile(r"#\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}")
MAXDEPTH = 8

DS = re.compile(r"datastore\[|datastore\.|OptString|OptPath|OptInt|OptBool")
SESSIONP = re.compile(r"\bsession\.|\bsysinfo\b|\bfs\.|\bcmd_exec\b|\bget_env\b|\bshell_command|\bget_envs\b|\bsysinfo\b")
REMOTEP = re.compile(r"Net::HTTP|HTTPClient|Rex::Proto|\.recv\b|\bresponse\b|\.body\b|\.send_request|Rex::Socket|\bSMBSimpleClient|\.read\b")
MIXINP = re.compile(r"\b(writable_dir|temp_dir|writable_directory|rand_text|Rex::Text|File\.join|File\.dirname|File\.basename|expand_path|get_env|report_)\b")
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


DEFRX = re.compile(r"^(\s*)def\s+([\w?!=\.]+)\s*(?:\(([^)]*)\))?")


def enclosing_def(lines, idx):
    """Nearest preceding `def`, with its parameter list."""
    for i in range(idx, -1, -1):
        m = DEFRX.match(lines[i])
        if m:
            params = []
            if m.group(3):
                params = [p.strip() for p in m.group(3).split(",")]
            else:
                # parenless: def foo a, b
                rest = lines[i][m.end(2):].strip()
                if rest and not rest.startswith("#"):
                    params = [p.strip() for p in rest.split(",")]
            params = [re.sub(r"^[*&]", "", p).split("=")[0].strip() for p in params]
            return i, m.group(2), [p for p in params if p]
    return None, None, []


def classify_rhs(r):
    r = r.strip()
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
            didx, dname, params = enclosing_def(lines, ln0)
            for e in exprs:
                inner = e[2:-1].strip()
                bm = re.match(r"^([A-Za-z_@$][\w?!]*)", inner)
                if not bm:
                    continue
                name = bm.group(1)
                chain = ["site %s:%d expr %s" % (rel, ln0 + 1, e)]
                cls = None
                # 1. parameter of enclosing def
                if name in params:
                    chain.append("PARAM of %s (def at line %d)" % (dname, didx + 1))
                    # find a caller in the same file passing an argument
                    callp = re.compile(r"(?<![\w.])" + re.escape(dname) + r"\s*\(([^)]*)\)")
                    found = False
                    for cm in callp.finditer(text):
                        if text[:cm.start()].count("\n") == ln0:
                            continue
                        cargs = split_args(cm.group(1))
                        try:
                            pi = params.index(name)
                        except ValueError:
                            continue
                        if pi < len(cargs):
                            rhs = cargs[pi]
                            chain.append("caller arg: %s" % rhs[:80])
                            c = classify_rhs(rhs)
                            if c:
                                cls = c
                                found = True
                                break
                            nm = re.match(r"^([A-Za-z_@$][\w?!]*)", rhs)
                            if nm:
                                _, rr = find_assign_anywhere(lines, nm.group(1), cm.start())
                                if rr:
                                    c2 = classify_rhs(rr)
                                    chain.append("%s := %s" % (nm.group(1), rr[:70]))
                                    if c2:
                                        cls = c2
                                        found = True
                                        break
                    if not found and cls is None:
                        cls = "PARAM_UNRESOLVED"
                    chain.append("param resolution: %s" % cls)
                # 2/3. assignment in method, then file
                if cls is None:
                    j, rhs = find_assign_in(lines, name, ln0, didx)
                    if j is None:
                        j, rhs = find_assign_anywhere(lines, name, len(text))
                    if rhs is not None:
                        chain.append("assign line %d: %s" % (j + 1, rhs[:80]))
                        cls = classify_rhs(rhs)
                        if cls is None:
                            nm = re.match(r"^([A-Za-z_@$][\w?!]*)", rhs)
                            if nm and nm.group(1) != name:
                                j2, r2 = find_assign_anywhere(lines, nm.group(1), len(text))
                                if r2:
                                    chain.append("  %s := %s" % (nm.group(1), r2[:70]))
                                    cls = classify_rhs(r2)
                # 4. def name
                if cls is None:
                    dpat = re.compile(r"^\s*def\s+" + re.escape(name) + r"\b")
                    for k, l in enumerate(lines):
                        if dpat.match(l):
                            chain.append("METHOD DEF at line %d" % (k + 1))
                            body = "\n".join(lines[k:k + 25])
                            cls = classify_rhs(body) or "MIXIN_HELPER"
                            chain.append("  body class: %s" % cls)
                            break
                rows.append(dict(file=rel, line=ln0 + 1, expr=e, name=name,
                                 cls=cls or "UNRESOLVABLE", chain=chain))
print("note: find_assign_* are defined below (forward refs); see v2b")
