import os, sys, re, hashlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
BIN = os.path.join(WS, r"RE_Library\05_TARGETS\merlin_extracted\data\bin")
UA = b"main.useragent="

print("SCOPE: %s" % BIN)
print()

# full key=value extraction from the -ldflags -X blob
KV = re.compile(rb'(-X )?"?(main\.[A-Za-z0-9_]+)=([^\x00"]*?)"?(?= -X | -buildid=|\x00|$)')

sets = {}
fields = {}
for fn in sorted(os.listdir(BIN)):
    p = os.path.join(BIN, fn)
    if not os.path.isfile(p):
        continue
    b = open(p, "rb").read()
    i = b.find(UA)
    if i < 0:
        continue
    s = b.rfind(b"-X ", max(0, i - 900), i)
    if s < 0:
        s = max(0, i - 900)
    e = b.find(b"-buildid=", i)
    blob = b[s:e if e > 0 else i + 700]
    pairs = KV.findall(blob)
    d = {}
    for _pre, k, v in pairs:
        d[k.decode()] = v.decode("latin1")
    sets[fn] = d
    fields[fn] = set(d)

print("COUNTED: %d binaries with a parseable config blob" % len(sets))
print()

# 1. field-set identity
allfields = set()
for f in fields.values():
    allfields |= f
print("=== FIELD SET (C-11 s2 line 90: 'the field SET is IDENTICAL') ===")
print("   union of all fields across %d binaries: %d" % (len(fields), len(allfields)))
print("   fields: %s" % ", ".join(sorted(allfields)))
print()
ident = len(set(frozenset(v) for v in fields.values())) == 1
print("   distinct field-SETS: %d" % len(set(frozenset(v) for v in fields.values())))
print("   field set identical across all: %s" % ident)
print()

# 2. per-field value identity
print("=== PER-FIELD VALUE IDENTITY ===")
print("   %-22s %3s   %s" % ("field", "n", "distinct values"))
for k in sorted(allfields):
    vals = {}
    for fn, d in sets.items():
        if k in d:
            vals.setdefault(d[k], []).append(fn)
    tag = "IDENTICAL" if len(vals) == 1 else ("%d DISTINCT" % len(vals))
    print("   %-22s %3d   %s" % (k, len(vals), tag))
    if len(vals) > 1:
        for v, fns in vals.items():
            print("        %-58s n=%d  %s" % ((v[:56] or "<empty>"), len(fns),
                  ",".join(x[:22] for x in fns[:3])))
print()

# 3. which field drives the three-way blob split
print("=== WHAT DIFFERS BETWEEN THE THREE BLOB GROUPS ===")
g = {}
for fn, d in sets.items():
    h = hashlib.sha256(open(os.path.join(BIN, fn), "rb").read()[
        open(os.path.join(BIN, fn), "rb").read().find(UA):
        open(os.path.join(BIN, fn), "rb").read().find(UA) + 700]).hexdigest()[:12]
    g.setdefault(h, []).append(fn)
for h, fns in g.items():
    print("   group %s : %s" % (h, ", ".join(fns)))
    keys = [sets[f] for f in fns]
    if len(keys) > 1:
        for k in sorted(allfields):
            vs = set(d.get(k) for d in keys)
            if len(vs) > 1:
                print("        DIFFERS %s: %s" % (k, vs))
