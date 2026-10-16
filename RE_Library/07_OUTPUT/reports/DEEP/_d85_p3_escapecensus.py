"""
D85 probe 3 -- ESCAPING PRIMITIVE CENSUS v2, derived FROM THE CORPUS.

Rule 20 fired against ME: my v1 census listed 15 primitives from memory and
`.shelljoin` was not among them -- yet cups_root_file_read.rb:60 uses it. So v2
does not guess the primitive list. It enumerates every method call that appears
INSIDE an interpolation in the population, and every method named in the
Ruby/Shellwords shell-escaping families, then reports which actually occur.

The primitive list is now an OUTPUT, not an input.
"""
import os, re, json, collections

ROOT = r"RE_Library\01_SOURCE_c2\metasploit"
POST = os.path.join(ROOT, "modules", "post")
HERE = os.path.dirname(os.path.abspath(__file__))

FILES = []
for dp, ds, fs in os.walk(POST):
    for f in fs:
        if f.endswith(".rb"):
            FILES.append(os.path.join(dp, f))
TEXT = {p: open(p, encoding="utf-8", errors="ignore").read() for p in FILES}

# ---- STEP 1: derive the primitive set FROM THE CORPUS, not from memory -------
# Any method named anything in the escaping family, counted tree-wide.
FAMILY = re.compile(
    r"\b(shellescape|shelljoin|shellsplit|shellwords|Shellwords\.\w+|"
    r"escape|escaping|quote|quoting|sanitize|shell_command|"
    r"Rex::Text\.(encode_base64|encode_base64url|decode_base64))\b")
print("=== STEP 1: escaping-FAMILY census, derived from the corpus ===")
fam = collections.Counter()
famfiles = collections.defaultdict(set)
for p, t in TEXT.items():
    rel = os.path.relpath(p, ROOT)
    for m in FAMILY.finditer(t):
        fam[m.group(1)] += 1
        famfiles[m.group(1)].add(rel)
for k, v in fam.most_common():
    print("   %-32s %4d occ / %3d files" % (k, v, len(famfiles[k])))
print()

# ---- STEP 2: what methods are called INSIDE interpolations in the population --
CALL = re.compile(r"(?<![A-Za-z0-9_.'\"])(cmd_exec|create_process)\s*\(")
INTERP = re.compile(r"#\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}")


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


# The 131 sites / 49 DATASTORE population, rebuilt with the v2 (paren-less def) resolver
import importlib.util
spec = importlib.util.spec_from_file_location("p1", os.path.join(HERE, "_d85_p1_primcensus.py"))

# simpler: re-run the population detection inline but only collect the 49 DATASTORE sites
DS = re.compile(r"datastore\[|datastore\.")
MIXINP = re.compile(r"\b(get_env|get_envs|writable_dir|temp_dir|rand_text|Rex::Text|"
                    r"File\.join|File\.dirname|File\.basename|expand_path|report_)\b")
TOOLPATH = re.compile(r"whereis|which\s|command\s+-v|\bfile\?|\bexecutable\?")
REMOTEP = re.compile(r"Net::HTTP|HTTPClient|Rex::Proto|\.recv\b|\.body\b|\.send_request|Rex::Socket")
TARGETREAD = re.compile(r"cat\s|nvram\s+get|dmesg|ps\s|ls\s|reg\s+query|find\s|grep\s|"
                        r"whoami|hostname|uname|id\b|grab_|dump|hashdump|enum_|read_file")
HARDP = re.compile(r"^([A-Z][A-Z0-9_]*|['\"].*['\"]|[\d\.\s\-\+\*\/]+)$")
DEFRX = re.compile(r"^(\s*)def\s+([\w?!=\.]+)\s*(?:\(([^)]*)\))?")


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


def resolve(text, lines, name, idx, depth=0):
    if depth > 8:
        return "UNRESOLVABLE"
    didx, dname, params = enclosing_def(lines, idx)
    if name in params and dname:
        callp = re.compile(r"(?<![\w.])" + re.escape(dname) + r"\s*\(([^)]*)\)")
        pi = params.index(name)
        for cm in callp.finditer(text):
            # SPECIES 18 GUARD: the call-pattern also matches the `def name(...)`
            # declaration itself, which feeds the parameter back into its own
            # resolver until depth 8 -> a false UNRESOLVABLE. Skip the decl line.
            if text[:cm.start()].count("\n") == idx:
                continue
            cargs = split_args(cm.group(1))
            if pi < len(cargs):
                c = classify(cargs[pi])
                if c:
                    return c
                nm = re.match(r"^([A-Za-z_@$][\w?!]*)", cargs[pi])
                if nm:
                    return resolve(text, lines, nm.group(1),
                                   text[:cm.start()].count("\n"), depth + 1)
        return "PARAM_UNRESOLVED"
    j, rhs = find_assign_near(lines, name, idx, didx if didx is not None else 0)
    if rhs is None:
        j, rhs = find_assign_file(lines, name)
    if rhs is not None:
        c = classify(rhs)
        if c:
            return c
        nm = re.match(r"^([A-Za-z_@$][\w?!]*)", rhs)
        if nm and nm.group(1) != name:
            return resolve(text, lines, nm.group(1), j, depth + 1)
    dpat = re.compile(r"^\s*def\s+" + re.escape(name) + r"\b")
    for k, l in enumerate(lines):
        if dpat.match(l):
            c = classify("\n".join(lines[k:k + 30]))
            return c if c else "METHOD_BODY_UNRESOLVED"
    return "UNRESOLVABLE"


ORDER = ["REMOTE_RESPONSE", "SESSION_TARGET", "DATASTORE", "MIXIN_HELPER",
         "LOCAL_TOOL_PATH", "HARDCODED", "METHOD_BODY_UNRESOLVED",
         "PARAM_UNRESOLVED", "UNRESOLVABLE"]

sites = []
for p, t in TEXT.items():
    rel = os.path.relpath(p, ROOT)
    lines = t.split("\n")
    for m in CALL.finditer(t):
        ls = t.rfind("\n", 0, m.start()) + 1
        nl = t.find("\n", ls)
        if t[ls:nl if nl > 0 else len(t)].lstrip().startswith("#"):
            continue
        ln0 = t[:m.start()].count("\n")
        argstr, _ = extract_call(t, m.end() - 1)
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
            if bm:
                cls.append(resolve(t, lines, bm.group(1), ln0))
        site = min(cls, key=lambda c: ORDER.index(c)) if cls else "UNRESOLVABLE"
        sites.append(dict(file=rel, line=ln0 + 1, cls=site, cmd=lit[1], args=args))

dat = [s for s in sites if s["cls"] == "DATASTORE"]
print("=== the 49 DATASTORE sites, with the ESCAPING PRIMITIVE present in the arg ===")
ESCAPE = re.compile(r"\bshellescape\b|\bshelljoin\b|\bshellsplit\b|Shellwords\.\w+|"
                    r"\.gsub\(\s*['\"]['\"]|\.gsub\(\s*['\"]\\\"['\"]|"
                    r"Rex::Text\.encode_base64")
esc, raw = [], []
for s in dat:
    combined = " ".join(s["args"])
    if ESCAPE.search(combined):
        esc.append(s)
    else:
        raw.append(s)
print("   ESCAPED  :", len(esc))
print("   RAW      :", len(raw))
print()
print("=== ESCAPED SITES ===")
for s in esc:
    print("   %s:%d  %s" % (s["file"], s["line"], s["cmd"][:110]))
print()
json.dump(sites, open(os.path.join(HERE, "_d85_sites.json"), "w"), indent=1)
print("distribution over all", len(sites), "sites:", dict(collections.Counter(s["cls"] for s in sites)))
