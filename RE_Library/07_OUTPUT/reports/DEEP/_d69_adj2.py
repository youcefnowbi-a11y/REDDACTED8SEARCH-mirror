import os, re

root = r"RE_Library\01_SOURCE_c2\metasploit"

# Method-independent adjudication for the FULL 55-alias population.
# Counts a name as referenced via any of the three Ruby reference forms:
#   bare call   name(  or  name=   (inside-class idiom -- the one the old probe missed)
#   dot call    .name
#   symbol      :name
# A name is DEAD only if all three are zero, minus the alias's own declaration.
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

core = os.path.join(root, "lib", "msf", "core")
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

print("aliases parsed: %d" % len(real))

corpus = []
for dp, ds, fs in os.walk(root):
    if ".git" in dp:
        continue
    for f in fs:
        if f.endswith(".rb"):
            corpus.append(open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read())
BLOB = "\n".join(corpus)
print("corpus files: %d" % len(corpus))
print()

def refs(name):
    if not re.match(r"^[A-Za-z_]", name):
        # operator / setter forms: use literal search
        n = BLOB.count(name)
        return n, 0, 0
    bare = len(re.findall(r"(?<![\w:.$@])" + re.escape(name) + r"\s*[(=]", BLOB))
    dot = len(re.findall(r"\.\s*" + re.escape(name) + r"\b", BLOB))
    sym = len(re.findall(r"(?<![:\w]):" + re.escape(name) + r"\b", BLOB))
    return bare, dot, sym

dead_a = []
dead_both = []
for rel, i, new, old in real:
    nb, nd, ns = refs(new)
    ob, od, os_ = refs(old)
    a_total = nb + nd + ns - 1        # minus its own declaration line
    b_total = ob + od + os_
    if a_total <= 0:
        dead_a.append((rel, i, new, old, a_total, b_total))
    if a_total <= 0 and b_total <= 0:
        dead_both.append((rel, i, new, old))

print("=== CLASS A: alias name unreferenced in all three forms ===")
print("count: %d of %d" % (len(dead_a), len(real)))
for rel, i, new, old, a, b in dead_a:
    note = "  <== TARGET ALSO DEAD" if b <= 0 else ""
    print("   %-46s L%-5d %-30s aliasRefs=%d targetRefs=%d%s" % (rel, i, "%s -> %s" % (new, old), a, b, note))

print()
print("=== BOTH-SIDES-DEAD (alias unused AND target unused): %d ===" % len(dead_both))
for rel, i, new, old in dead_both:
    print("   %s:%d  %s -> %s" % (rel, i, new, old))

print()
print("=== controls (must be > 0) ===")
for ctl in ["session", "cmd_exec", "print_good", "session_changed?"]:
    b, d, s = refs(ctl)
    print("   %-20s bare=%d dot=%d sym=%d" % (ctl, b, d, s))
