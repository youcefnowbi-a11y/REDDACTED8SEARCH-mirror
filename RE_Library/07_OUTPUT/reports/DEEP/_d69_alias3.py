import os, re, collections, time

root = r"RE_Library\01_SOURCE_c2\metasploit"
core = os.path.join(root, "lib", "msf", "core")

RX_ALIAS = re.compile(
    r"""^\s*
        (?:alias_method\s*(?:\(\s*)?|alias\s+)
        (?::|['"])?([A-Za-z_$@][\w?!=]*)(?::|['"])?
        \s*(?:,\s*)?
        (?::|['"])?([A-Za-z_$@][\w?!=]*)(?::|['"])?
        \s*\)?\s*(?:\#.*)?$
    """,
    re.X,
)

real = []
for dp, ds, fs in os.walk(core):
    for f in fs:
        if not f.endswith(".rb"):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, core)
        for i, l in enumerate(open(p, encoding="utf-8", errors="ignore").read().split("\n"), 1):
            if not re.match(r"^\s*alias", l):
                continue
            m = RX_ALIAS.match(l)
            if m:
                real.append((rel, i, m.group(1), m.group(2)))

print("real alias statements: %d" % len(real))

# ONE pass over the corpus, tokenising every identifier, so each name is counted
# once. This is O(bytes) instead of O(53 * bytes).
t0 = time.time()
counts = collections.Counter()
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*[?!=]?")
nfiles = 0
for dp, ds, fs in os.walk(root):
    if ".git" in dp:
        continue
    for f in fs:
        if not f.endswith(".rb"):
            continue
        nfiles += 1
        t = open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read()
        counts.update(IDENT.findall(t))
print("corpus: %d .rb files, tokenised in %.1fs" % (nfiles, time.time() - t0))
print()

names_needed = set()
for _, _, new, old in real:
    names_needed.add(new)
    names_needed.add(old)

print("=== per-alias reference counts (raw identifier occurrences corpus-wide) ===")
print("%-50s %-5s %-28s %-8s %-8s" % ("file", "line", "alias -> target", "alias#", "target#"))
dead_new = []
dead_old = []
for rel, i, new, old in real:
    nn = counts.get(new, 0)
    no = counts.get(old, 0)
    # subtract 1 for the alias statement itself declaring the alias name
    nn_eff = nn - 1
    flag = ""
    if nn_eff <= 0:
        flag = "  <== ALIAS NAME NEVER USED"
        dead_new.append((rel, i, new, old))
    if no <= 0:
        flag += "  <== TARGET NAME NEVER USED"
        dead_old.append((rel, i, new, old))
    print("%-50s %-5d %-28s %-8d %-8d%s" % (rel, i, "%s -> %s" % (new, old), nn_eff, no, flag))

print()
print("A) alias name never referenced (dead alias): %d" % len(dead_new))
for r in dead_new:
    print("      %s:%d  %s -> %s" % r)
print()
print("B) target name never referenced (alias to unused impl): %d" % len(dead_old))
for r in dead_old:
    print("      %s:%d  %s -> %s" % r)
print()

# Control: two names we KNOW are used, so the counter is proven live.
for ctl in ["session", "cmd_exec", "print_good", "session_changed?"]:
    print("control %-20s count=%d" % (ctl, counts.get(ctl, 0)))
