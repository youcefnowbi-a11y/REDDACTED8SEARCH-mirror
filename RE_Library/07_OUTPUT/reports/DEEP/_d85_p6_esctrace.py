"""
D85 probe 6 -- ESCAPING VIA A VARIABLE (the puppet_exe pattern, applied to escaping).

Probe 5 found ESCAPED=2/131 because it tested escaping INLINE in the argument.
But screen.rb:45 escapes into `file_type` and uses it LATER. mount_share, vpn,
sonic_pi all do the same. 16 of the 18 shellescape/shelljoin occurrences escape
into a VARIABLE.

So the test must be: for each interpolation, is the interpolated NAME bound to an
expression that carries an escaping primitive? That is D74's resolver, pointed at
a different predicate. Same engine, new question.

This probe reuses the corpus-derived primitive list and re-runs resolution
looking specifically for ESCAPING in the resolved chain, reporting the chain.
"""
import os, re, json, collections

HERE = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\reports\DEEP"
ROOT = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\01_SOURCE_c2\metasploit"
POST = os.path.join(ROOT, "modules", "post")

ESCAPERS = re.compile(
    r"\.shellescape\b|\.shelljoin\b|Shellwords\.escape\b|Shellwords\.split\b|"
    r"\.gsub\(\s*['\"]['\"]|\.gsub\(\s*['\"]\\\"['\"]|Rex::Text\.encode_base64")
DS = re.compile(r"datastore\[|datastore\.")
DEFRX = re.compile(r"^(\s*)def\s+([\w?!=\.]+)\s*(?:\(([^)]*)\))?")


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


# --- ESCAPING CHAIN TRACER -------------------------------------------------
def esc_chain(text, lines, name, idx, depth=0, chain=None):
    """Return (escaped?, chain-string). Walks the same resolution path as the
    provenance tracer but asks 'does an escaping primitive appear en route'."""
    if chain is None:
        chain = []
    if depth > 8:
        return None, " -> ".join(chain + ["DEPTH"])
    didx, dname, params = enclosing_def(lines, idx)
    if name in params and dname:
        pi = params.index(name)
        callp = re.compile(r"(?<![\w.])" + re.escape(dname) + r"\s*\(([^)]*)\)")
        for cm in callp.finditer(text):
            if text[:cm.start()].count("\n") == idx:
                continue          # species-18 guard: never bind to the decl line
            cargs = split_args(cm.group(1))
            if pi < len(cargs):
                arg = cargs[pi]
                if ESCAPERS.search(arg):
                    return True, " -> ".join(chain + ["%s(arg: %s)" % (dname, arg[:44])])
                nm = re.match(r"^([A-Za-z_@$][\w?!]*)", arg)
                if nm:
                    ok, ch = esc_chain(text, lines, nm.group(1),
                                       text[:cm.start()].count("\n"), depth + 1,
                                       chain + ["%s(%s)" % (dname, nm.group(1))])
                    if ok:
                        return True, ch
        return None, " -> ".join(chain + ["PARAM_NO_ESCAPE"])
    pat = assign_pattern(name)
    rhs = None
    j = None
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
        if ESCAPERS.search(rhs):
            return True, " -> ".join(chain + ["assign L%d: %s" % (j + 1, rhs[:56])])
        nm = re.match(r"^([A-Za-z_@$][\w?!]*)", rhs)
        if nm and nm.group(1) != name:
            ok, ch = esc_chain(text, lines, nm.group(1), j, depth + 1,
                               chain + ["assign L%d(%s)" % (j + 1, nm.group(1))])
            if ok:
                return True, ch
        return None, " -> ".join(chain + ["assign L%d NO_ESCAPE: %s" % (j + 1, rhs[:44])])
    dpat = re.compile(r"^\s*def\s+" + re.escape(name) + r"\b")
    for k, l in enumerate(lines):
        if dpat.match(l):
            body = "\n".join(lines[k:k + 30])
            if ESCAPERS.search(body):
                return True, " -> ".join(chain + ["def %s body carries escaper" % name])
            return None, " -> ".join(chain + ["def %s body NO_ESCAPE" % name])
    return None, " -> ".join(chain + ["NO_ASSIGNMENT"])


# --- rebuild population, but WIDEN to accept ordered-array first args too -----
INTERP = re.compile(r"#\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}")
CALL = re.compile(r"(?<![A-Za-z0-9_.'\"])(cmd_exec|create_process)\s*\(")

rows = []
for dp, ds, fs in os.walk(POST):
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
            a0 = args[0].strip()
            # accept: single-quoted literal, OR ordered array whose elements are literals
            lit = single_literal(a0)
            if lit:
                body = lit[1]
                shape = "LITERAL"
            elif a0.startswith("[") and a0.endswith("]"):
                body = a0
                shape = "ARRAY"
            else:
                continue
            exprs = [x.group(0) for x in INTERP.finditer(body)]
            if not exprs:
                continue
            rows.append(dict(file=rel, line=ln0 + 1, cmd=body[:120], shape=shape,
                             args=args, text=text, lines=lines, ln0=ln0, exprs=exprs))

print("population (widened to include ARRAY first args):", len(rows))
print("  by first-arg shape:", dict(collections.Counter(r["shape"] for r in rows)))
print()

# class each interpolated token, and chase escaping
out = []
for r in rows:
    for e in r["exprs"]:
        inner = e[2:-1].strip()
        bm = re.match(r"^([A-Za-z_@$][\w?!]*)", inner)
        tok = bm.group(1) if bm else None
        is_ds = bool(DS.search(inner))
        if tok:
            ok, chain = esc_chain(r["text"], r["lines"], tok, r["ln0"])
        else:
            ok, chain = None, "(no bare token: expression)"
        out.append(dict(file=r["file"], line=r["line"], shape=r["shape"],
                        token=tok, inner=inner[:70], datastore=is_ds,
                        escaped=ok, chain=chain, cmd=r["cmd"][:100]))

print("=== ESCAPING CHAIN RESULT, per interpolated expression ===")
print("  expressions:", len(out))
for k, v in collections.Counter(
        ("ESCAPED" if o["escaped"] else "NOT_ESCAPED") for o in out).most_common():
    print("   %-14s %4d" % (k, v))
print()
print("=== ESCAPED expressions, with the chain ===")
for o in out:
    if o["escaped"]:
        print("   %s:%d  tok=%s" % (o["file"], o["line"], o["token"]))
        print("        %s" % o["chain"])
print()
print("=== DATSTORE expressions that are NOT escaped (the defect set) ===")
dsraw = [o for o in out if o["datastore"] and not o["escaped"]]
print("   count:", len(dsraw))
for o in dsraw[:60]:
    print("   %s:%d  %s" % (o["file"], o["line"], o["inner"]))
json.dump(out, open(os.path.join(HERE, "_d85_esctrace.json"), "w"), indent=1)
