"""
_d126_p5_carveout_merlin.py -- the name-table carve-out GENERALISED to C-11.

C-11 makes four string-in-binary claims:
  S1  all six agent builds carry the IDENTICAL Windows-Chrome-40 user-agent   (POSITIVE)
  S2  the main.* config set, 'extracted by regex over direct byte reads'       (POSITIVE)
  S3  three platforms, same 115-byte user-agent                               (POSITIVE)
  S4  the six CLIs carry NO main.* build-config string AT ALL                 (NEGATIVE)

S4 is the one the carve-out protects.  On a GO binary 'main.' is a symbol prefix:
main.main, main.init, main.(*X).Y.  A naive substring probe returns hundreds of
hits that are ALL name-table entries, and the negative becomes unfalsifiable.

METHOD: locate the Go pclntab, derive the name-table region from its own header,
then report INSIDE vs OUTSIDE.  A real compiled config literal is OUTSIDE.
A symbol name is INSIDE.

Everything is measured, nothing is assumed about the layout.
"""
import os, sys, struct, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
HERE = os.path.join(WS, r"RE_Library\07_OUTPUT\reports\DEEP")
TARGETS = [
    os.path.join(WS, r"RE_Library\05_TARGETS\merlin_extracted\data\bin\merlinCLI-Linux-x64"),
    os.path.join(WS, r"RE_Library\05_TARGETS\merlin_extracted\data\bin\merlinAgent-Linux-x64"),
]

MAGICS = [b"\xf1\xff\xff\xff", b"\xfa\xff\xff\xff", b"\xf0\xff\xff\xff"]


def find_pclntab(b):
    """Locate the Go pclntab by magic.  Returns (ptrSize, base) or None."""
    for mag in MAGICS:
        s = 0
        while True:
            i = b.find(mag, s)
            if i < 0:
                break
            # candidate: next bytes must be 0 0 then ptrsize 8 or 4
            if i + 8 < len(b):
                if b[i + 6] in (1, 2, 4, 8) and b[i + 7] in (4, 8):
                    return b[i + 7], i
            s = i + 1
    return None, None


for path in TARGETS:
    if not os.path.exists(path):
        print("ABSENT: %s" % path)
        continue
    b = open(path, "rb").read()
    print("=" * 96)
    print("SCOPE: %s" % os.path.basename(path))
    print("COUNTED: %d bytes" % len(b))
    ps, P = find_pclntab(b)
    if P is None:
        print("   pclntab: NOT FOUND (not a Go binary, or magic unmatched)")
        print()
        continue
    print("   pclntab: ptrSize=%d base=0x%X" % (ps, P))

    def u64(o):
        return struct.unpack_from("<Q", b, o)[0]

    nf = u64(P + 8)
    funcnameOff = u64(P + 32)
    pclnOff = u64(P + 64)
    NAME_LO = P + funcnameOff
    NAME_HI = P + pclnOff
    print("   nfunc=%d  funcnameOff=0x%X  pclnOff=0x%X" % (nf, funcnameOff, pclnOff))
    print("   NAME-TABLE REGION: 0x%X .. 0x%X  = %d bytes" % (NAME_LO, NAME_HI, NAME_HI - NAME_LO))
    print()

    def split(tok):
        tb = tok.encode()
        ins, out = [], []
        s = 0
        while True:
            i = b.find(tb, s)
            if i < 0:
                break
            (ins if NAME_LO <= i < NAME_HI else out).append(i)
            s = i + 1
        return ins, out

    print("   %-34s %8s %8s   %s" % ("probe", "OUTSIDE", "INSIDE", "verdict"))
    probes = [
        ("main.main", "symbol"),
        ("main.init", "symbol"),
        ("main.", "prefix"),
        ("main.secure", "config-key"),
        ("main.useragent", "config-key"),
        ("main.headers", "config-key"),
        ("Windows NT 10.0", "ua-fragment"),
        ("Mozilla/5.0", "ua-fragment"),
        ("parrot", "config-key"),
        ("listener", "config-key"),
    ]
    res = {}
    for tok, kind in probes:
        ins, out = split(tok)
        if out and not ins:
            v = "REAL LITERAL (%s)" % kind
        elif ins and not out:
            v = "SYMBOL NAME ONLY"
        elif ins and out:
            v = "BOTH -- %d literal / %d symbol" % (len(out), len(ins))
        else:
            v = "ABSENT"
        res[tok] = dict(inside=len(ins), outside=len(out), verdict=v)
        print("   %-34s %8d %8d   %s" % (tok, len(out), len(ins), v))
    print()

    # the decisive control: does the config blob exist at all?
    ins, out = split("main.secure")
    print("   S4 TEST -- does a main.* CONFIG BLOB exist outside the name table?")
    if out:
        print("      YES, %d outside hit(s). First at 0x%X." % (len(out), out[0]))
        s = max(0, out[0] - 60)
        seg = b[s:out[0] + 180]
        txt = "".join(chr(c) if 32 <= c < 127 else ("|" if c == 0 else ".") for c in seg)
        print("      0x%-9X %s" % (s, txt))
    else:
        print("      NO outside hits -- the string is not a compiled literal in this image.")
    print()

    json.dump(res, open(os.path.join(HERE, "_d126_carve_%s.json" %
              os.path.basename(path).replace("-", "_")), "w"), indent=1)

print("done")
