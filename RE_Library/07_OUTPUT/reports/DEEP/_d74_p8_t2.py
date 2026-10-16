"""
D74 probe 8 -- T2: SECOND ARGUMENTS.

D69's rule scored the FIRST argument only. `cmd_exec("literal cmd", "interp args")`
is classed LITERAL there but the second arg may be interpolated. This probe
classifies arg[1] for the same population and reports the delta.

Also: create_process signature is (executable, args: [], time_out:, opts:) so its
"second argument" is the KEYWORD args: [...] which is a DIFFERENT semantic position
than cmd_exec's (cmd, args). Handled separately and labelled.
"""
import os, re, collections, json

ROOT = r"RE_Library\01_SOURCE_c2\metasploit"
POST = os.path.join(ROOT, "modules", "post")
HERE = os.path.dirname(os.path.abspath(__file__))

CALL = re.compile(r"(?<![A-Za-z0-9_.'\"])(cmd_exec|create_process)\s*\(")
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


def cls_of(arg):
    if arg is None:
        return "ABSENT", []
    lit = single_literal(arg)
    if lit:
        exprs = [m.group(0) for m in INTERP.finditer(lit[1])]
        return ("INTERPOLATED", exprs) if exprs else ("LITERAL", [])
    a = arg.strip()
    if not a:
        return "EMPTY", []
    if re.match(r"^[A-Za-z_@$][\w?!=]*(\.[\w?!=]+|\[[^\]]*\]|\([^)]*\))*$", a):
        return "VARIABLE", []
    return "OTHER", [m.group(0) for m in INTERP.finditer(a)]


rows = []
for dp, ds_, fs in os.walk(POST):
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
            c1, e1 = cls_of(args[0])
            c2, e2 = cls_of(args[1] if len(args) > 1 else None)
            rows.append(dict(file=rel, line=ln, fn=m.group(1), nargs=len(args),
                             c1=c1, e1=e1, c2=c2, e2=e2,
                             a1=args[0][:110], a2=(args[1][:110] if len(args) > 1 else None),
                             kw=(args[1][:40] if len(args) > 1 else None)))

print("=== T2: SECOND-ARGUMENT CLASSIFICATION, population = %d sites ===" % len(rows))
print()
print("=== SECOND-ARG CLASS DISTRIBUTION ===")
for k, v in collections.Counter(r["c2"] for r in rows).most_common():
    print("   %-14s %4d" % (k, v))
print()
print("=== ARG COUNT ===")
print("   ", dict(collections.Counter(r["nargs"] for r in rows)))
print()
two = [r for r in rows if r["c2"] != "ABSENT"]
print("=== sites WITH a second argument: %d ===" % len(two))
print()
print("=== THE DELTA: first arg LITERAL/VARIABLE but second arg INTERPOLATED ===")
delta = [r for r in two if r["c2"] == "INTERPOLATED" and r["c1"] != "INTERPOLATED"]
print("count:", len(delta))
for r in delta:
    print("   %s:%d  [%s] %s  ||  [%s] %s" % (r["file"], r["line"], r["c1"],
                                              r["a1"], r["c2"], r["a2"]))
print()
print("=== sites where BOTH args interpolate ===")
both = [r for r in rows if r["c1"] == "INTERPOLATED" and r["c2"] == "INTERPOLATED"]
print("count:", len(both))
for r in both[:25]:
    print("   %s:%d  %s || %s" % (r["file"], r["line"], r["a1"][:70], r["a2"][:60]))
print()
print("=== create_process sites (all 8) ===")
for r in rows:
    if r["fn"] == "create_process":
        print("   %s:%d  nargs=%d  arg1=[%s] %s  arg2=[%s] %s" %
              (r["file"], r["line"], r["nargs"], r["c1"], r["a1"], r["c2"], r["a2"]))
print()
# does T2 move the 5/138-style split?
print("=== DOES T2 MOVE THE SPLIT? ===")
interp1 = [r for r in rows if r["c1"] == "INTERPOLATED"]
interp2 = [r for r in rows if r["c2"] == "INTERPOLATED"]
either = [r for r in rows if r["c1"] == "INTERPOLATED" or r["c2"] == "INTERPOLATED"]
print("   first-arg interpolated only : %d" % len(interp1))
print("   second-arg interpolated only: %d" % len(interp2))
print("   EITHER argument interpolated: %d" % len(either))
print("   delta from T2               : %d" % (len(either) - len(interp1)))
json.dump(rows, open(os.path.join(HERE, "_d74_t2.json"), "w"), indent=1)
