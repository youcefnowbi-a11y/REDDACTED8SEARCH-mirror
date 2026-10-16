import os, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
COV = os.path.join(WS, r"RE_Library\01_SOURCE_c2\covenant")

print("=" * 100)
print("NULL-AUTHOR: broadened. Any line mentioning Author with null/empty/FirstOrDefault")
print("=" * 100)
pats = [
    (r"Author", "any 'Author'"),
    (r"Author[^\n]{0,40}(null|Empty|Any\(\))", "Author near null/empty"),
    (r"\.Author\b", "dot-Author access"),
]
for pat, label in pats:
    n = 0
    print()
    print("--- %s ---" % label)
    for dp, dn, fn in os.walk(COV):
        for f in fn:
            if not f.endswith(".cs"):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, COV)
            lines = open(p, "r", encoding="utf-8", errors="replace").read().split("\n")
            for i, l in enumerate(lines, 1):
                if re.search(pat, l):
                    n += 1
                    if label != "any 'Author'" or "null" in l.lower() or "First" in l or "Author" in l[:40]:
                        print("   %-54s :%-5d %s" % (rel, i, l.strip()[:82]))
    print("   COUNTED: %d" % n)
    if label == "any 'Author'":
        pass
print()

print("=" * 100)
print("STARTUP: where does Covenant start? Program.cs / Startup.cs -- Author references")
print("=" * 100)
for name in ["Program.cs", "Startup.cs"]:
    for dp, dn, fn in os.walk(COV):
        for f in fn:
            if f == name:
                p = os.path.join(dp, f)
                rel = os.path.relpath(p, COV)
                lines = open(p, "r", encoding="utf-8", errors="replace").read().split("\n")
                print()
                print("FILE: %s (%d lines)" % (rel, len(lines)))
                for i, l in enumerate(lines, 1):
                    if "Author" in l or "User" in l:
                        print("   :%-5d %s" % (i, l.strip()[:100]))
