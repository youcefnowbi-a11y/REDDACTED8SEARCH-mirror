"""
D74 probe 1b -- FIXED expression classifier.

Bugs in _d74_p1_population.py:
  BUG A: INTERP regex `#\{([^{}]|\{[^{}]*\})*\}` used findall with ONE group, so
         findall returned the GROUP, not the whole match. Then expr_class() sliced
         [2:-1] off a non-match string, producing garbage that fell through to... 
         actually every row printed as DATASTORE because `inner` began with junk.
  BUG B: the population count came out 459 (vs D69's 455) and 141 interpolated
         (vs 143). Those need adjudication, not rounding.

FIX: use finditer and take .group(0); slice with an explicit length, not [2:-1].
"""
import os, re, collections

ROOT = r"RE_Library\01_SOURCE_c2\metasploit"
POST = os.path.join(ROOT, "modules", "post")

CALL = re.compile(r"(?<![A-Za-z0-9_.'\"])(cmd_exec|create_process)\s*\(")
# non-greedy, single-level nesting allowed
INTERP = re.compile(r"#\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}")


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
    """If arg is exactly one quoted literal, return (quote, body) else None."""
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
            if arg[i + 1:].strip() == "":
                return q, arg[1:i]
            return None
        i += 1
    return None


def classify(arg):
    lit = single_literal(arg)
    if lit:
        body = lit[1]
        exprs = [m.group(0) for m in INTERP.finditer(body)]
        return ("INTERPOLATED", exprs) if exprs else ("LITERAL", [])
    a = arg.strip()
    if not a:
        return "EMPTY", []
    if re.match(r"^[A-Za-z_@$][\w?!=]*(\.[\w?!=]+|\[[^\]]*\]|\([^)]*\))*$", a):
        return "VARIABLE", []
    return "OTHER", [m.group(0) for m in INTERP.finditer(a)]


def expr_class(e):
    inner = e[2:-1].strip()          # strip the #{ and }  -- explicit, not [2:-1] guess
    if inner.startswith("datastore[") or inner.startswith("datastore ["):
        return "DATASTORE"
    if re.match(r"^[A-Za-z_@$][\w?!=]*$", inner):
        return "BARE_LOCAL"
    if inner.startswith("@") and re.match(r"^@[\w?!]+$", inner):
        return "IVAR"
    if re.match(r"^[A-Za-z_@$][\w?!=]*(\.[\w?!=]+|\[[^\]]*\]|\([^)]*\))+$", inner):
        return "METHOD_OR_INDEX"
    return "OTHER_EXPR"


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
            line = text[ls:nl if nl > 0 else len(text)]
            if line.lstrip().startswith("#"):
                continue
            ln = text[:m.start()].count("\n") + 1
            argstr, _ = extract_call(text, m.end() - 1)
            if argstr is None:
                continue
            args = split_args(argstr)
            if not args:
                continue
            cls, exprs = classify(args[0])
            rows.append(dict(file=rel, line=ln, fn=m.group(1), nargs=len(args),
                             cls=cls, exprs=exprs, raw=args[0][:200],
                             second=args[1][:200] if len(args) > 1 else None))

raw_sites = len(CALL.findall("".join(
    open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read()
    for dp, ds, fs in os.walk(POST) for f in fs if f.endswith(".rb"))))

print("=== SANITY ===")
print("raw 'cmd_exec|create_process(' occurrences (incl comments/strings):", raw_sites)
print("call sites retained (comment-filtered, parseable)  :", len(rows))
print("by fn:", dict(collections.Counter(r["fn"] for r in rows)))
print()
print("=== FIRST-ARG CLASS ===")
for k, v in collections.Counter(r["cls"] for r in rows).most_common():
    print("   %-14s %4d" % (k, v))
print()
interp = [r for r in rows if r["cls"] == "INTERPOLATED"]
print("INTERPOLATED first args: %d  (D69: 143)" % len(interp))
print("file count:", len(set(r["file"] for r in interp)))
print()

exprs = []
for r in interp:
    for e in r["exprs"]:
        exprs.append((r["file"], r["line"], e, expr_class(e)))
print("=== EXPRESSION CLASSES: %d expressions from %d sites ===" % (len(exprs), len(interp)))
for k, v in collections.Counter(x[3] for x in exprs).most_common():
    print("   %-18s %4d" % (k, v))
print()
print("=== CONTROL: does expr_class see the two known DATASTORE sites? ===")
for f, l, e, k in exprs:
    if "datastore" in e:
        print("   %s:%d  %s  -> %s" % (f, l, e, k))
print()
print("=== BARE_LOCAL names ===")
bl = collections.Counter(x[2][2:-1].strip() for x in exprs if x[3] == "BARE_LOCAL")
for n, c in bl.most_common(40):
    print("   %-26s %d" % (n, c))
print("   distinct:", len(bl), " occurrences:", sum(bl.values()))
print()
iv = collections.Counter(x[2][2:-1].strip() for x in exprs if x[3] == "IVAR")
print("=== IVAR names ===")
for n, c in iv.most_common():
    print("   %-26s %d" % (n, c))
