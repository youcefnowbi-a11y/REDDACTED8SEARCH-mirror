"""
D74 probe 1 -- RECONSTRUCT the interpolated-cmd_exec population from scratch.

Purpose: D69 section 2.5 reports 143 INTERPOLATED first arguments, of which only 5
interpolate datastore[...] directly and 138 interpolate a bare local. This probe
rebuilds that population by an INDEPENDENT method so the D74 trace has a validated
starting set rather than a number copied from D69.

Method difference from D69: D69 classified by pattern-matching the leading token of
each #{...} expression. This probe instead extracts EVERY #{...} expression verbatim
and records it, so the expression text itself is auditable.
"""
import os, re, collections

ROOT = r"RE_Library\01_SOURCE_c2\metasploit"
POST = os.path.join(ROOT, "modules", "post")

# --- call-site extractor: find cmd_exec / create_process calls and their arguments
CALL = re.compile(r"(?<![A-Za-z0-9_.'\"])(cmd_exec|create_process)\s*\(")


def split_args(s):
    """Split a Ruby argument list on top-level commas. Returns list of raw args."""
    args, depth, cur, i = [], 0, [], 0
    instr = None
    while i < len(s):
        c = s[i]
        if instr:
            if c == "\\":
                cur.append(c)
                i += 1
                if i < len(s):
                    cur.append(s[i])
                i += 1
                continue
            if c == instr:
                instr = None
            cur.append(c)
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
    """From the '(' at `start`, return the full argument string."""
    depth, i, out = 0, start, []
    instr = None
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


INTERP = re.compile(r"#\{([^{}]|\{[^{}]*\})*\}")


def classify(arg):
    """Return (class, [interpolated expressions])."""
    arg = arg.strip()
    if not arg:
        return "EMPTY", []
    m = re.match(r"^(['\"])", arg)
    # a single literal: starts with a quote and the matching quote closes it at end
    if m:
        q = m.group(1)
        # is the whole arg one literal?
        closed = None
        i = 1
        while i < len(arg):
            if arg[i] == "\\":
                i += 2
                continue
            if arg[i] == q:
                closed = i
                break
            i += 1
        if closed is not None and arg[closed + 1:].strip() == "":
            exprs = INTERP.findall(arg) if False else [x.group(0) for x in INTERP.finditer(arg)]
            if exprs:
                return "INTERPOLATED", exprs
            return "LITERAL", []
    if re.match(r"^[A-Za-z_@$][\w?!=]*$", arg) or re.match(r"^[A-Za-z_@$][\w?!=]*(\.[\w?!=]+|\[[^\]]*\])*$", arg):
        return "VARIABLE", []
    return "OTHER", [x.group(0) for x in INTERP.finditer(arg)]


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
            # skip comments
            ls = text.rfind("\n", 0, m.start()) + 1
            line = text[ls:text.find("\n", ls) if text.find("\n", ls) > 0 else len(text)]
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
            rows.append({
                "file": rel, "line": ln, "fn": m.group(1),
                "nargs": len(args), "cls": cls, "exprs": exprs,
                "first": args[0][:120], "second": args[1][:120] if len(args) > 1 else None,
            })

print("=== POPULATION (all post .rb, both cmd_exec and create_process) ===")
print("total call sites      :", len(rows))
byfn = collections.Counter(r["fn"] for r in rows)
print("by function           :", dict(byfn))
print()
print("=== FIRST-ARGUMENT CLASS DISTRIBUTION ===")
c = collections.Counter(r["cls"] for r in rows)
for k, v in c.most_common():
    print("   %-14s %4d" % (k, v))
print()
interp = [r for r in rows if r["cls"] == "INTERPOLATED"]
print("=== INTERPOLATED FIRST ARGS: %d ===" % len(interp))
print("   (D69 reported 143; this is the independent recomputation)")
print()

# separate cmd_exec from create_process
print("=== INTERPOLATED by function ===")
print("   ", dict(collections.Counter(r["fn"] for r in interp)))
print()

# classify the interpolated expressions
def expr_class(e):
    inner = e[2:-1].strip()
    if inner.startswith("datastore[") or inner.startswith("datastore [") or "@datastore[":
        return "DATASTORE"
    if re.match(r"^[A-Za-z_@$][\w?!=]*$", inner):
        return "BARE_LOCAL"
    if re.match(r"^[A-Za-z_@$][\w?!=]*(\.[\w?!=]+|\([^)]*\)|\[[^\]]*\])+$", inner):
        return "METHOD_CALL"
    if re.match(r"^(session|self|framework)", inner):
        return "FRAMEWORK"
    return "OTHER_EXPR"

exprs_all = []
for r in interp:
    for e in r["exprs"]:
        exprs_all.append((r["file"], r["line"], e, expr_class(e)))
print("=== INTERPOLATED EXPRESSION CLASSES: %d expressions ===" % len(exprs_all))
for k, v in collections.Counter(e[3] for e in exprs_all).most_common():
    print("   %-14s %4d" % (k, v))
print()
print("=== DATASTORE interpolations (the '5' in D69's 5/138 split) ===")
for f, l, e, k in exprs_all:
    if k == "DATASTORE":
        print("   %s:%d   %s" % (f, l, e))
print()
print("=== BARE_LOCAL interpolation names (top 30) ===")
bl = collections.Counter(e[2][2:-1].strip() for e in exprs_all if e[3] == "BARE_LOCAL")
for name, n in bl.most_common(30):
    print("   %-24s %d" % (name, n))
print("   ... total distinct bare locals:", len(bl), " total occurrences:", sum(bl.values()))
