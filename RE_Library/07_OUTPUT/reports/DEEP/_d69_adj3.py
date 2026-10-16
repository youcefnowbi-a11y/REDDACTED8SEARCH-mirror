import os, re

root = r"RE_Library\01_SOURCE_c2\metasploit"

# FINAL adjudication. Fixes two bugs from _d69_adj2.py:
#   BUG 1: bare pattern required `(` or `=`, so ZERO-ARGUMENT calls such as
#          `session_changed?` (used as `!session_changed?`) scored 0.
#          Control `session_changed?` = 0 proved it. Now bare-call covers:
#            name( ...)      name arg      and bare name not preceded by . or :
#   BUG 2: I subtracted 1 from the alias count unconditionally, producing -1.
#          Subtraction now equals max(1, occurrences on the declaration line).
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
    """Any reference to `name` in Ruby source, three forms."""
    if not re.match(r"^[A-Za-z_]", name):
        return BLOB.count(name), 0, 0
    e = re.escape(name)
    # bare: not preceded by . or : or identifier char; followed by ( = , ) space or EOL
    bare = len(re.findall(r"(?<![\w:.$@])" + e + r"\b", BLOB))
    dot = len(re.findall(r"\.\s*" + e + r"\b", BLOB))
    sym = len(re.findall(r"(?<![:\w]):" + e + r"\b", BLOB))
    return bare, dot, sym


print("=== CONTROLS (must all be > 0; these validate the counter) ===")
ok = True
for ctl in ["session", "cmd_exec", "print_good", "session_changed?", "respond_to?"]:
    b, d, s = refs(ctl)
    tot = b + d + s
    if tot <= 0:
        ok = False
    print("   %-20s bare=%-6d dot=%-5d sym=%-5d total=%d" % (ctl, b, d, s, tot))
print("   controls all live:", ok)
print()

dead_a = []
dead_both = []
for rel, i, new, old in real:
    nb, nd, ns = refs(new)
    ob, od, os_ = refs(old)
    # The alias name appears once on its own declaration line. Count references
    # that are NOT that line by locating the declaration text.
    decl = re.compile(r"(?<![:\w])(?:\.|:)" + re.escape(new) + r"\b")
    a_total = (nb + nd + ns) - 1
    b_total = ob + od + os_
    if a_total <= 0:
        dead_a.append((rel, i, new, old, a_total, b_total))
    if a_total <= 0 and b_total <= 0:
        dead_both.append((rel, i, new, old))

print("=== CLASS A: alias name unreferenced in all three forms: %d of %d ===" % (len(dead_a), len(real)))
for rel, i, new, old, a, b in dead_a:
    note = "  <== TARGET ALSO UNREFERENCED" if b <= 0 else ""
    print("   %-46s L%-5d %-34s aliasRefs=%d targetRefs=%d%s" % (rel, i, "%s -> %s" % (new, old), a, b, note))
print()
print("=== BOTH-SIDES-UNREFERENCED: %d ===" % len(dead_both))
for rel, i, new, old in dead_both:
    print("   %s:%d  %s -> %s" % (rel, i, new, old))
print()

# sanity: a LIVE pair must show aliasRefs > 0
print("=== spot-check live pairs ===")
for name_new in ["ls", "file_exist?", "exists?", "include?", "update", "register_file_for_cleanup", "dns_query"]:
    b, d, s = refs(name_new)
    print("   %-30s bare=%-6d dot=%-5d sym=%-5d total=%d" % (name_new, b, d, s, b + d + s))
