import os, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
COV = os.path.join(WS, r"RE_Library\01_SOURCE_c2\covenant")

print("=" * 100)
print("CONTROL: is my 'deref, no guard' pattern trustworthy?  Test on KNOWN-GUARDED sites.")
print("=" * 100)
P = os.path.join(COV, r"Covenant\Core\CovenantService.cs")
L = open(P, "r", encoding="utf-8", errors="replace").read().split("\n")

def window(lo, hi, note):
    print("   --- %s ---" % note)
    for i in range(lo, min(hi, len(L)) + 1):
        print("      %5d| %s" % (i, L[i - 1].strip()[:104]))

window(525, 534, ":525 savedUser -- my probe said DEREF-no-guard at :530")
window(549, 558, ":549 matching_user -- my probe said DEREF-no-guard at :554")
window(2773, 2776, ":2773 l -- my probe called the guard itself a DEREF")

print()
print("=" * 100)
print("task.Author: every reference, corpus-wide, with a guard test on EACH")
print("=" * 100)
pat = re.compile(r"task\.Author\b|\.Author\.Name|\.Author\.Id")
hits = []
for dp, dn, fn in os.walk(COV):
    for f in fn:
        if not f.endswith(".cs"):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, COV)
        lines = open(p, "r", encoding="utf-8", errors="replace").read().split("\n")
        for i, l in enumerate(lines, 1):
            if pat.search(l):
                hits.append((rel, i, l.strip()))
print("COUNTED: %d task.Author references" % len(hits))
for rel, i, l in hits:
    print("   %-52s :%-5d %s" % (rel, i, l[:82]))
print()

print("=" * 100)
print("IS THERE ANY 'task.Author == null' / 'Author != null' GUARD ANYWHERE?")
print("=" * 100)
g = 0
for dp, dn, fn in os.walk(COV):
    for f in fn:
        if not f.endswith(".cs"):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, COV)
        lines = open(p, "r", encoding="utf-8", errors="replace").read().split("\n")
        for i, l in enumerate(lines, 1):
            if re.search(r"(task|updatingTask|newTask)\.Author\s*(==|!=)\s*null", l):
                g += 1
                print("   %-52s :%-5d %s" % (rel, i, l.strip()[:82]))
print("   COUNTED: %d guards on task.Author  [absence if 0]" % g)
print()

print("=" * 100)
print("CALLERS of CreateGruntTask / EditGruntTask (the two null-Author sites)")
print("=" * 100)
for fn_name in ["CreateGruntTask", "EditGruntTask"]:
    n = 0
    print()
    print("   --- %s ---" % fn_name)
    for dp, dn, fn in os.walk(COV):
        for f in fn:
            if not f.endswith(".cs"):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, COV)
            lines = open(p, "r", encoding="utf-8", errors="replace").read().split("\n")
            for i, l in enumerate(lines, 1):
                if re.search(r"\b%s\s*\(" % fn_name, l) and "public" not in l and "Task<" not in l:
                    n += 1
                    print("      %-50s :%-5d %s" % (rel, i, l.strip()[:80]))
    print("      COUNTED callers: %d" % n)
