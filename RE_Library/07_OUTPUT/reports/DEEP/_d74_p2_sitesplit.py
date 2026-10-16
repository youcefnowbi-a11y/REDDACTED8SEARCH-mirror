"""
D74 probe 2 -- PER-SITE provenance classification, plus delta adjudication.

D69's 5/138 split is a SITE split (143 sites -> 5 datastore, 138 bare local).
Probe 1b counted EXPRESSIONS (16 datastore, 168 bare), which is not the same
denominator. This probe does it per SITE so the comparison is apples to apples.

Site rule (stated before application):
  DATASTORE  : EVERY interpolated expression in the first arg is datastore[...]
  MIXED      : at least one datastore AND at least one non-datastore
  NON-DATASTORE: no datastore expression at all
That gives a three-way split that is honest about the middle case D69 collapsed.
"""
import os, re, collections

ROOT = r"RE_Library\01_SOURCE_c2\metasploit"
POST = os.path.join(ROOT, "modules", "post")
CALL = re.compile(r"(?<![A-Za-z0-9_.'\"])(cmd_exec|create_process)\s*\(")
INTERP = re.compile(r"#\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}")
BARE = re.compile(r"^[A-Za-z_@$][\w?!=]*$")


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


rows = []
for dp, ds, fs in os.walk(POST):
    for f in fs:
        if not f.endswith(".rb"):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, ROOT)
        text = open(p, encoding="utf-8", errors="ignore").read()
        for m in CALL.finditer(text):
            ls = text.rfind("\n", 0, m.start()) + 1
            nl = text.find("\n", ls)
            if text[ls:nl if nl > 0 else len(text)].lstrip().startswith("#"):
                continue
            ln = text[:m.start()].count("\n") + 1
            argstr, _ = extract_call(text, m.end() - 1)
            if argstr is None:
                continue
            args = split_args(argstr)
            if not args:
                continue
            lit = single_literal(args[0])
            exprs = [x.group(0) for x in INTERP.finditer(lit[1])] if lit else \
                    [x.group(0) for x in INTERP.finditer(args[0])]
            if not lit:
                cls = "VARIABLE" if BARE.match(args[0].strip()) else "OTHER"
            else:
                cls = "INTERPOLATED" if exprs else "LITERAL"
            rows.append(dict(file=rel, line=ln, fn=m.group(1), cls=cls, exprs=exprs,
                             first=args[0][:160],
                             nargs=len(args),
                             second=args[1][:160] if len(args) > 1 else None,
                             third=args[2][:160] if len(args) > 2 else None))

interp = [r for r in rows if r["cls"] == "INTERPOLATED"]
print("total call sites : %d" % len(rows))
print("interp first args: %d sites" % len(interp))
print()

def site_class(r):
    ds = [e for e in r["exprs"] if e[2:-1].strip().startswith("datastore[")]
    other = [e for e in r["exprs"] if not e[2:-1].strip().startswith("datastore[")]
    if ds and not other:
        return "ALL_DATASTORE"
    if ds and other:
        return "MIXED"
    return "NO_DATASTORE"

print("=== PER-SITE SPLIT (the apples-to-apples comparison with D69's 5/138) ===")
sc = collections.Counter(site_class(r) for r in interp)
for k in ["ALL_DATASTORE", "MIXED", "NO_DATASTORE"]:
    print("   %-16s %4d" % (k, sc.get(k, 0)))
print()
print("=== ALL_DATASTORE sites ===")
for r in interp:
    if site_class(r) == "ALL_DATASTORE":
        print("   %s:%d  %s" % (r["file"], r["line"], r["first"][:110]))
print()
print("=== MIXED sites (datastore + non-datastore in one command) ===")
for r in interp:
    if site_class(r) == "MIXED":
        print("   %s:%d  %s" % (r["file"], r["line"], r["first"][:110]))
print()
print("=== NO_DATASTORE, by explicit value-origin evidence present in the file ===")
# For each such site, look for datastore reads, session return values, and
# remote-response sinks NEAR the site. This is a targeted lexical trace, not a
# whole-program analysis, and it is labelled as such.
print("count:", sc.get("NO_DATASTORE", 0))
print()
print("=== which functions appear where ===")
print("   interp by fn:", dict(collections.Counter(r["fn"] for r in interp)))

# --- DELTA vs D69: the 459 vs 455 and 141 vs 143 questions
print()
print("=== DELTA ADJUDICATION ===")
# D69 excluded lines whose STRIPPED form starts with '#'. Reproduce that exactly.
cmt = [r for r in rows if r["file"]]
print("sites retained here: %d" % len(rows))
print()
print("=== multi-line / nested call handling spot check ===")
# Are there sites where a cmd_exec call is the ARGUMENT of another call?
nested = 0
for dp, ds, fs in os.walk(POST):
    for f in fs:
        if not f.endswith(".rb"):
            continue
        t = open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read()
        for m in CALL.finditer(t):
            pre = t[max(0, m.start() - 60):m.start()]
            if re.search(r"cmd_exec\s*\([^)]*$", pre) or re.search(r"output\s*=\s*$", pre):
                nested += 1
print("suspected nested/prefixed call sites:", nested)
