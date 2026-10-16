"""
_d131_r134_source.py -- gather R1 (ToMap callers), R3 (FromJson), R4 (D94 denominators).

R1: D89 D-1/D-2/D-3. ToMap callers + concurrency. INCLUDE THE DEFINITION and LABEL it.
    D126 precedent: 18/18 stubs present was a true measurement of the WRONG PROPERTY,
    because protoc-gen-go emits one stub per ServiceDesc entry, so presence != a call.
    Same trap here: a ToMap method exists on every type that has one; the DEFINITION
    is not a caller. Label it.
R3: D92 FromJson unprotected path + null-Author startup abort. Print code and callers
    on EACH side with cardinality.
R4: D94 unstable denominators: the 172 and the 113-in-scope.
"""
import os, re, sys
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
H = os.path.join(WS, r"RE_Library\01_SOURCE_c2\havoc")
SL = os.path.join(WS, r"RE_Library\01_SOURCE_c2\sliver")

def gofiles(root):
    out = []
    for dp, dn, fn in os.walk(root):
        if os.sep + "vendor" + os.sep in dp + os.sep:
            continue
        for f in fn:
            if f.endswith(".go"):
                out.append(os.path.join(dp, f))
    return out

print("#" * 100)
print("# R1  ToMap -- DEFINITION vs CALLER, labeled")
print("#" * 100)
hf = gofiles(H)
print("SCOPE: %s" % H)
print("COUNTED: %d non-vendor .go files" % len(hf))
print()

# control
ctl = sum(1 for f in hf if b"__ZZZ_TOMAP_CTL__" in open(f, "rb").read())
print("CONTROL garbage token: %d -- must be 0" % ctl)
pos = sum(1 for f in hf if b"func " in open(f, "rb").read())
print("CONTROL positive 'func ': %d -- must be > 0" % pos)
print()

# definitions: func (recv *T) ToMap(   OR func ToMap(
defre = re.compile(r"^func\s+(?:\([^)]*\)\s*)?(?:ToMap|toMap|ToMapString)\s*\(")
callre = re.compile(r"\bToMap\s*\(")

defs = []
calls = []
for f in hf:
    rel = os.path.relpath(f, H)
    lines = open(f, "r", encoding="utf-8", errors="replace").read().split("\n")
    for i, l in enumerate(lines, 1):
        if defre.search(l):
            defs.append((rel, i, l.strip()))
        elif "ToMap(" in l:
            calls.append((rel, i, l.strip()))

print("--- DEFINITIONS (these are NOT callers) ---")
print("   COUNTED: %d definitions" % len(defs))
for rel, i, l in defs:
    print("   %-46s :%-5d %s" % (rel, i, l[:88]))
print()

print("--- CALL SITES (definition lines removed) ---")
callonly = [(r, i, l) for r, i, l in calls if (r, i) not in {(a, b) for a, b, _ in defs}]
print("   COUNTED: %d call sites (raw ToMap( mentions = %d)" % (len(callonly), len(calls)))
for rel, i, l in callonly:
    print("   %-46s :%-5d %s" % (rel, i, l[:88]))
print()
byrecv = Counter()
for rel, i, l in callonly:
    m = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\.ToMap\(", l)
    byrecv[m.group(1) if m else "<bare/other>"] += 1
print("   by receiver:")
for k, v in byrecv.most_common():
    print("      %-40s %d" % (k, v))
print()
print("   DISTRIBUTION of receiver names: %d distinct" % len(byrecv))
print()

print("#" * 100)
print("# R3  FromJson -- definition and callers")
print("#" * 100)
allf = gofiles(H) + gofiles(os.path.join(WS, r"RE_Library\01_SOURCE_c2\covenant"))
cj = [f for f in allf if f.endswith(".cs")] if False else []
# FromJson is the Covenant (C#) surface
cov = os.path.join(WS, r"RE_Library\01_SOURCE_c2\covenant")
csf = []
for dp, dn, fn in os.walk(cov):
    for f in fn:
        if f.endswith(".cs"):
            csf.append(os.path.join(dp, f))
print("SCOPE: %s" % cov)
print("COUNTED: %d .cs files" % len(csf))
print()
fj_def = []
fj_call = []
for f in csf:
    rel = os.path.relpath(f, cov)
    lines = open(f, "r", encoding="utf-8", errors="replace").read().split("\n")
    for i, l in enumerate(lines, 1):
        if re.search(r"(public|private|protected|internal|static).*\bFromJson\s*\(", l):
            fj_def.append((rel, i, l.strip()))
        elif "FromJson" in l:
            fj_call.append((rel, i, l.strip()))
print("   COUNTED definitions: %d" % len(fj_def))
for rel, i, l in fj_def:
    print("      %-52s :%-5d %s" % (rel, i, l[:80]))
print()
print("   COUNTED mentions (non-def): %d" % len(fj_call))
for rel, i, l in fj_call[:40]:
    print("      %-52s :%-5d %s" % (rel, i, l[:80]))
print()
