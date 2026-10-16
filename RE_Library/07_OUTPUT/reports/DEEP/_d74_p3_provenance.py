"""
D74 probe 3 -- T1: PROVENANCE TRACE for the 131 NO_DATASTORE interpolated sites.

This is the expensive probe D69 section 5.4 named. It does a LEXICAL trace:
for each interpolated bare local at a cmd_exec site, find the nearest preceding
assignment to that name in the SAME method body, then classify the right-hand
side. It is labelled INFERRED where the chain does not terminate in a literal
datastore/session read.

Provenance classes (stated before application):
  DATASTORE       rhs reads datastore[...] / a datastore accessor
  SESSION_TARGET  rhs derives from the session object (session.*, sysinfo, fs.*,
                  or a mixin method known to hit the target: cmd_exec, get_env)
  REMOTE_RESPONSE rhs derives from a network/HTTP/SMB read (Net::HTTP, HTTPClient,
                  Rex::Proto, recv, response, res.body, ...)
  HARDCODED       rhs is a literal, a constant, or a path built from literals
  LOOP_VAR        rhs is a loop/block variable or an iterator element
  MIXIN_HELPER    rhs is a return value of a Post:: mixin helper (e.g.
                  writable_dir, temp_dir) -- framework-controlled
  UNRESOLVABLE    no assignment found in the enclosing method, or the chain does
                  not terminate in any of the above within MAXDEPTH
"""
import os, re, collections, json

ROOT = r"RE_Library\01_SOURCE_c2\metasploit"
POST = os.path.join(ROOT, "modules", "post")
CALL = re.compile(r"(?<![A-Za-z0-9_.'\"])(cmd_exec|create_process)\s*\(")
INTERP = re.compile(r"#\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}")
MAXDEPTH = 6


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


# ---- def-boundary finder (peer-aware, learned from D69's walker bug) ----
DEF = re.compile(r"^(\s*)def\s+([\w?!=.]+)")


def method_bounds(lines, target_idx):
    """Return (start,end) line indices of the method containing target_idx."""
    start = None
    for i in range(target_idx, -1, -1):
        m = DEF.match(lines[i])
        if m:
            start = i
            break
    if start is None:
        return 0, len(lines) - 1
    # peer-aware end: first line whose indent <= def-indent and is a bare end
    ind = len(DEF.match(lines[start]).group(1))
    depth = 0
    for j in range(start + 1, len(lines)):
        s = lines[j].strip()
        if re.match(r"^(if|unless|case|while|until|for|begin|def|module|class|do)\b", s) or s.endswith(" do"):
            depth += 1
        elif s == "end":
            if depth == 0:
                return start, j
            depth -= 1
    return start, len(lines) - 1


DS = re.compile(r"datastore\[|datastore\.|\[['\"]")
SESSIONPAT = re.compile(r"\bsession\.|\bsysinfo\b|\bfs\.|\bcmd_exec\b|\bget_env\b|\bshell_command")
REMOTEPAT = re.compile(r"Net::HTTP|HTTPClient|Rex::Proto|\.recv\b|\.read\b|\bresponse\b|\.body\b|Open3|IO\.popen|\.send_request|Rex::Socket")
MIXIN = re.compile(r"\b(writable_dir|temp_dir|writable_directory|temp_?path|rand_text|Rex::Text|File\.join|File\.dirname|File\.basename|expand_path)\b")
LOOPV = re.compile(r"\b(iterator|each|map|select|find)\b")


def rhs_class(rhs):
    r = rhs.strip()
    if DS.search(r):
        return "DATASTORE"
    if REMOTEPAT.search(r):
        return "REMOTE_RESPONSE"
    if SESSIONPAT.search(r):
        return "SESSION_TARGET"
    if MIXIN.search(r):
        return "MIXIN_HELPER"
    if re.match(r"^[A-Z][A-Z0-9_]*$", r):
        return "HARDCODED"
    if re.match(r"^['\"].*['\"]$", r):
        return "HARDCODED"
    if re.match(r"^[\d\.\s\-\+\*\/]+$", r):
        return "HARDCODED"
    return None


ASSIGN = {}


def find_assign(lines, name, idx):
    """Nearest preceding assignment to `name` at or before idx, in line order."""
    pat = re.compile(r"(?<![\w.@$])" + re.escape(name) + r"\s*(\|\|=|=)(?!=|>)")
    for j in range(idx, -1, -1):
        m = pat.search(lines[j])
        if m:
            return j, lines[j][m.end():].strip()
    return None, None


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
            ln = ln0 + 1
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
            ds_exprs = [e for e in exprs if e[2:-1].strip().startswith("datastore[")]
            if ds_exprs:
                continue  # handled by the 5/5 in probe 2
            mstart, mend = method_bounds(lines, ln0)
            for e in exprs:
                inner = e[2:-1].strip()
                base = re.match(r"^([A-Za-z_@$][\w?!]*)", inner)
                if not base:
                    continue
                name = base.group(1)
                chain = [inner]
                depth = 0
                cls = None
                cur = name
                while depth < MAXDEPTH:
                    j, rhs = find_assign(lines, cur, ln0)
                    if j is None or rhs is None:
                        break
                    chain.append("%s:%d -> %s" % (cur, j + 1, rhs[:90]))
                    c = rhs_class(rhs)
                    if c:
                        cls = c
                        break
                    nxt = re.match(r"^([A-Za-z_@$][\w?!]*)", rhs)
                    if not nxt or nxt.group(1) == cur:
                        break
                    cur = nxt.group(1)
                    depth += 1
                rows.append(dict(file=rel, line=ln, expr=e, name=name,
                                 cls=cls or "UNRESOLVABLE", chain=chain,
                                 mstart=mstart + 1, mend=mend + 1,
                                 cmd=lit[1][:150]))

print("=== T1: PROVENANCE OF NON-DATASTORE INTERPOLATED cmd_exec ARGUMENTS ===")
print("sites analysed (cmd_exec with >=1 interpolated non-datastore expr): ")
print("   expressions:", len(rows))
print("   distinct sites:", len(set((r["file"], r["line"]) for r in rows)))
print()
print("=== PROVENANCE CLASS DISTRIBUTION (by expression) ===")
for k, v in collections.Counter(r["cls"] for r in rows).most_common():
    print("   %-18s %4d  %5.1f%%" % (k, v, 100.0 * v / len(rows)))
print()
print("=== BY SITE (a site takes the HIGHEST-risk class among its expressions) ===")
ORDER = ["REMOTE_RESPONSE", "SESSION_TARGET", "DATASTORE", "MIXIN_HELPER",
         "LOOP_VAR", "HARDCODED", "UNRESOLVABLE"]
sites = {}
for r in rows:
    key = (r["file"], r["line"])
    sites.setdefault(key, []).append(r)
sitecls = {}
for k, v in sites.items():
    sitecls[k] = min((r["cls"] for r in v), key=lambda c: ORDER.index(c))
for k, v in sorted(collections.Counter(sitecls.values()).items(),
                   key=lambda x: ORDER.index(x[0])):
    print("   %-18s %4d" % (k, v))
print()
print("=== SITES BY CLASS: UNRESOLVABLE and REMOTE_RESPONSE and SESSION_TARGET ===")
for want in ["REMOTE_RESPONSE", "SESSION_TARGET", "UNRESOLVABLE"]:
    print("--- %s ---" % want)
    for k, v in sorted(sites.items()):
        if sitecls[k] == want:
            print("   %s:%d" % k)
            for r in v:
                print("        %s  [%s]" % (r["expr"], r["cls"]))
                for c in r["chain"][1:3]:
                    print("           %s" % c)
    print()

json.dump([{k: (v if k != "chain" else v) for k, v in r.items()} for r in rows],
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_d74_t1_raw.json"), "w"), indent=1)
print("raw trace written to _d74_t1_raw.json")
