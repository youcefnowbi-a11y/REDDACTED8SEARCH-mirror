import os, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
COV = os.path.join(WS, r"RE_Library\01_SOURCE_c2\covenant")

def show(rel, lo, hi, mark=()):
    p = os.path.join(COV, rel)
    lines = open(p, "r", encoding="utf-8", errors="replace").read().split("\n")
    print("=" * 100)
    print("FILE: %s  (%d lines)" % (rel, len(lines)))
    print("=" * 100)
    lo = max(1, lo); hi = min(len(lines), hi)
    for i in range(lo, hi + 1):
        f = ">>" if i in mark else "  "
        print("  %s %5d| %s" % (f, i, lines[i - 1][:118]))
    print()

# R3: the unprotected GruntEncryptedMessage.FromJson site + the guarded sibling
show(r"Covenant\Data\Grunt\GruntHTTP\GruntHTTP.cs", 420, 505, mark={430, 491, 496})
# R3: the FromJson definition itself -- is it protected?
show(r"Covenant\Data\Grunt\GruntHTTP\GruntHTTP.cs", 1095, 1125, mark={1095})
# R3: null-Author -- find Author nullability
print("#" * 100)
print("# NULL-AUTHOR: every 'Author' null check in Covenant controllers/models")
print("#" * 100)
hits = []
for dp, dn, fn in os.walk(COV):
    for f in fn:
        if not f.endswith(".cs"):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, COV)
        lines = open(p, "r", encoding="utf-8", errors="replace").read().split("\n")
        for i, l in enumerate(lines, 1):
            if re.search(r"Author\s*(==|!=)\s*null|null\s*(==|!=)\s*Author", l):
                hits.append((rel, i, l.strip()))
print("COUNTED: %d Author-null checks" % len(hits))
for rel, i, l in hits:
    print("   %-56s :%-5d %s" % (rel, i, l[:84]))
print()
