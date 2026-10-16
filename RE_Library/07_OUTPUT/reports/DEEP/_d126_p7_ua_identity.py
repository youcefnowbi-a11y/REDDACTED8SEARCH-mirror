import os, sys, hashlib, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
BIN = os.path.join(WS, r"RE_Library\05_TARGETS\merlin_extracted\data\bin")

UA = b"main.useragent="
CFG = b"main.secure"

print("SCOPE: %s" % BIN)
print("COUNTED: all files in the merlin bin tree")
files = sorted(os.listdir(BIN)) if os.path.isdir(BIN) else []
print("   enumeration returns %d files" % len(files))
print()

rows = []
for fn in files:
    p = os.path.join(BIN, fn)
    if not os.path.isfile(p):
        continue
    b = open(p, "rb").read()
    i = b.find(UA)
    j = b.find(CFG)
    blob = None
    if i > 0:
        e = b.find(b"-buildid=", i)
        blob = b[i:e] if e > 0 else b[i:i + 700]
    rows.append((fn, len(b), i, j, blob))

print("%-30s %12s %10s %10s %s" % ("file", "bytes", "cfg-offset", "ua-offset", "ua-sha256"))
print("-" * 100)
for fn, n, i, j, blob in rows:
    h = hashlib.sha256(blob).hexdigest()[:16] if blob else "-"
    io = ("0x%X" % j) if j > 0 else "ABSENT"
    iu = ("0x%X" % i) if i > 0 else "ABSENT"
    print("%-30s %12d %10s %10s %s" % (fn, n, io, iu, h))

print()
print("=" * 100)
print("IDENTITY TEST -- C-11 s1/s3: is the user-agent identical across platforms?")
print("=" * 100)
blobs = [(fn, blob) for fn, n, i, j, blob in rows if blob]
print("   binaries WITH a main.useragent blob : %d / %d" % (len(blobs), len(rows)))
if blobs:
    ua = {}
    for fn, blob in blobs:
        m = re.search(rb"main\.useragent=([^\x00]*?)(?= -X |\x00|$)", blob)
        ua[fn] = m.group(1) if m else b"(unparsed)"
    distinct = set(ua.values())
    print("   DISTINCT user-agent values: %d" % len(distinct))
    for v in distinct:
        print("      %d bytes: %s" % (len(v), v.decode("latin1")[:110]))
    print()
    for fn, v in ua.items():
        print("   %-30s %s" % (fn, v.decode("latin1")[:70]))
    print()
    if len(distinct) == 1:
        print("   *** CONFIRMED: every build with a config blob carries the SAME user-agent. ***")
    else:
        print("   *** %d DISTINCT values -- C-11 s3 claim does NOT hold as stated. ***" % len(distinct))
