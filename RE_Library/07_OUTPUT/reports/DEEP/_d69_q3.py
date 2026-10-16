import os, re, collections

core = r"RE_Library\01_SOURCE_c2\metasploit\lib\msf\core"

# Q3: what does a module DO when run against an incompatible session?
# The warning comes from session_incompatibility_reasons. Find all providers,
# then read what each check tests.
print("=== providers / overrides of session_incompatibility_reasons ===")
rx = re.compile(r"def\s+session_incompatibility_reasons\b")
for dp, ds, fs in os.walk(core):
    for f in fs:
        if not f.endswith(".rb"):
            continue
        p = os.path.join(dp, f)
        t = open(p, encoding="utf-8", errors="ignore").read()
        for m in rx.finditer(t):
            ln = t[: m.start()].count("\n") + 1
            print("   %s:%d" % (os.path.relpath(p, core), ln))

print()
print("=== session_incompatibility_reasons body (session_compatibility.rb) ===")
p = os.path.join(core, "session_compatibility.rb")
L = open(p, encoding="utf-8", errors="ignore").read().split("\n")
start = None
for i, l in enumerate(L):
    if re.match(r"\s*def\s+session_incompatibility_reasons", l):
        start = i
        break
if start is not None:
    for j in range(start, min(start + 60, len(L))):
        print("  L%-4d %s" % (j + 1, L[j]))
