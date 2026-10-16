import os, sys, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
BIN = os.path.join(WS, r"RE_Library\05_TARGETS\merlin_extracted\data\bin")

# The blob is a contiguous run of: -X "main.k=v"  (with escaped quotes in the raw bytes)
# Find the run by locating the FIRST -X "main. and scanning forward to -buildid=
FIRST = b'-X \\"main.'
PAIR = re.compile(rb'-X \\"(main\.[A-Za-z0-9_]+)=([^\\]*)\\"')

print("SCOPE: %s" % BIN)
print("COUNTED: enumerating the merlin bin tree")
files = [f for f in sorted(os.listdir(BIN)) if os.path.isfile(os.path.join(BIN, f))]
print("   %d files" % len(files))
print()

sets = {}
for fn in files:
    b = open(os.path.join(BIN, fn), "rb").read()
    i = b.find(FIRST)
    if i < 0:
        continue
    e = b.find(b"-buildid=", i)
    blob = b[i:e if e > 0 else i + 2000]
    d = {}
    for m in PAIR.finditer(blob):
        d[m.group(1).decode()] = m.group(2).decode("latin1")
    if d:
        sets[fn] = d

print("COUNTED: %d binaries with a parseable -X run" % len(sets))
print()
allf = set()
for d in sets.values():
    allf |= set(d)
print("=== FIELD INVENTORY ===")
print("   union across %d binaries: %d fields" % (len(sets), len(allf)))
for k in sorted(allf):
    print("      %s" % k)
print()

print("=== PER-BINARY FIELD COUNT AND SET ===")
for fn in sorted(sets):
    print("   %-34s n=%2d" % (fn, len(sets[fn])))
print()
setsig = {}
for fn, d in sets.items():
    setsig.setdefault(frozenset(d), []).append(fn)
print("   distinct field-SETS: %d" % len(setsig))
for s, fns in setsig.items():
    print("      n=%d  %s" % (len(s), ", ".join(fns)))
print()

print("=== PER-FIELD VALUE IDENTITY (across all %d) ===")
print("   %-22s %3s  %s" % ("field", "n", "status"))
for k in sorted(allf):
    vals = {}
    for fn, d in sets.items():
        vals.setdefault(d.get(k, "<ABSENT>"), []).append(fn)
    st = "IDENTICAL" if len(vals) == 1 else "%d DISTINCT" % len(vals)
    print("   %-22s %3d  %s" % (k, len(vals), st))
    if len(vals) > 1:
        for v, fns in vals.items():
            print("        %-56s n=%d  %s" % ((v[:54] or "<EMPTY>"), len(fns), fns[0][:26]))
