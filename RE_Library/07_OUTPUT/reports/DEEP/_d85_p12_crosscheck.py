"""
D85 probe 12 -- SECOND METHOD cross-check of every headline number.

Independent reimplementation: blank comments and strings BEFORE counting, walk
with a different scanner, and compare. Any figure that does not reproduce is
labelled unstable and the SERIES is printed (D74 §4.1 discipline).
"""
import os, re, json, collections

HERE = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\reports\DEEP"
ROOT = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\01_SOURCE_c2\metasploit"
POST = os.path.join(ROOT, "modules", "post")


def blank(text):
    """Remove line comments, then blank string literals -- a DIFFERENT preprocessing
    from method 1, which used regex finditer directly on raw text."""
    out = []
    for line in text.split("\n"):
        # strip trailing ' #' comment only when not inside a quote (approximate)
        q = None
        res = []
        i = 0
        while i < len(line):
            c = line[i]
            if q:
                if c == "\\":
                    res.append(" ")
                    i += 2
                    continue
                if c == q:
                    q = None
                res.append(" ")
            elif c in "'\"":
                q = c
                res.append(" ")
            elif c == "#":
                break
            else:
                res.append(c)
            i += 1
        out.append("".join(res))
    return "\n".join(out)


# method 2 scanner: character walk for cmd_exec( ... ) with depth counting
def find_calls(text):
    res = []
    for m in re.finditer(r"\b(cmd_exec|create_process)\s*\(", text):
        start = m.end() - 1
        depth = 0
        i = start
        instr = None
        while i < len(text):
            c = text[i]
            if instr:
                if c == "\\":
                    i += 2
                    continue
                if c == instr:
                    instr = None
            elif c in "'\"":
                instr = c
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        res.append((text[:m.start()].count("\n") + 1, m.group(1), text[start + 1:i]))
    return res


print("=== METHOD 2: comments+strings blanked, independent scanner ===")
raw_n = 0
blank_n = 0
per_file = {}
for dp, ds, fs in os.walk(POST):
    for f in fs:
        if not f.endswith(".rb"):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, ROOT)
        t = open(p, encoding="utf-8", errors="ignore").read()
        raw_n += len(find_calls(t))
        blank_n += len(find_calls(blank(t)))
print("   cmd_exec/create_process sites, RAW text      :", raw_n)
print("   cmd_exec/create_process sites, BLANKED text  :", blank_n)
print()

# interpolated-first-arg population, method 2
INTERP = re.compile(r"#\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}")
DS = re.compile(r"datastore\[|datastore\.")
n_lit = n_interp = n_var = 0
interp_sites = []
for dp, ds, fs in os.walk(POST):
    for f in fs:
        if not f.endswith(".rb"):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, ROOT)
        t = open(p, encoding="utf-8", errors="ignore").read()
        for ln, kind, argstr in find_calls(t):
            a = argstr.strip()
            if not a:
                continue
            # naive split on first top-level comma
            depth = 0
            instr = None
            cut = len(a)
            for i, c in enumerate(a):
                if instr:
                    if c == instr:
                        instr = None
                    continue
                if c in "'\"":
                    instr = c
                elif c in "([{":
                    depth += 1
                elif c in ")]}":
                    depth -= 1
                elif c == "," and depth == 0:
                    cut = i
                    break
            first = a[:cut].strip()
            if first[:1] in ("'", '"'):
                body = first[1:-1] if len(first) > 1 else ""
                if INTERP.search(body):
                    n_interp += 1
                    interp_sites.append((rel, ln, body))
                else:
                    n_lit += 1
            else:
                n_var += 1
print("=== first-argument classes, method 2 ===")
print("   LITERAL      :", n_lit)
print("   INTERPOLATED :", n_interp)
print("   VARIABLE     :", n_var)
print("   (method 1 gave LITERAL 227 / INTERPOLATED 141 / VARIABLE 82 / OTHER 9 from 459)")
print()
print("   interpolation sites, method 2 :", len(interp_sites))
print("   interpolated expressions      :", sum(len(INTERP.findall(b)) for _, _, b in interp_sites))
print()

# class the expressions method-2-style: literal datastore text anywhere in interpolation
ds_only = [s for s in interp_sites if all(DS.search(x.group(0)) for x in INTERP.finditer(s[2]))]
print("   sites where EVERY interpolation is literal datastore[...]:", len(ds_only))
for s in ds_only:
    print("      %s:%d  %s" % (s[0], s[1], s[2][:80]))
print()
print("=== stability table ===")
print("   %-40s %-14s %-14s %s" % ("figure", "method 1", "method 2", "verdict"))
print("   %-40s %-14s %-14s %s" % ("interpolated first-arg sites", "141", str(n_interp),
                                 "STABLE" if abs(n_interp - 141) <= 2 else "UNSTABLE"))
print("   %-40s %-14s %-14s %s" % ("literal first-arg sites", "227", str(n_lit),
                                 "STABLE" if abs(n_lit - 227) <= 3 else "UNSTABLE"))
