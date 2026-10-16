"""
_d121_p2_pair1b.py -- PAIR 1 part 2: the QUERY STRING question, done right.

Fix the species-35 error: "unknown" matched a pclntab FUNCTION NAME (0x65656F),
not the source's switch literal. The switch literal is tested with strings.EqualFold
against the TRIMSPACE'd name; Go stores short literals in a packed string blob,
not as isolated runs. So:

  1. Locate the pclntab name-table region and EXCLUDE it, so name hits and
     literal hits are never confused.
  2. Search for the sentinels OUTSIDE the name table -> those are real literals.
  3. Search for the query/SQL strings the D91 claim is about.

Every census prints its input cardinality.
"""
import os, re, sys, json, struct
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
EXE = os.path.join(WS, r"RE_Library\02_BINARIES\sliver\sliver-client_windows-amd64.exe")
HERE = os.path.join(WS, r"RE_Library\07_OUTPUT\reports\DEEP")
SRC = os.path.join(WS, r"RE_Library\01_SOURCE_c2\sliver")

b = open(EXE, "rb").read()
N = len(b)
print("SCOPE: %s" % EXE)
print("COUNTED: file bytes = %d" % N)

# --- locate the pclntab, using the verified header offset from _d96_pclntab.ps1 ---
P = 0x269DDE0
magic = struct.unpack_from("<I", b, P)[0]
nf = struct.unpack_from("<Q", b, P + 8)[0]
funcnameOff = struct.unpack_from("<Q", b, P + 32)[0]
pclnOff = struct.unpack_from("<Q", b, P + 64)[0]
print("pclntab base 0x%X magic 0x%X nfunc %d" % (P, magic, nf))
print("funcnameOff 0x%X  pclnOff 0x%X" % (funcnameOff, pclnOff))

# name table runs from P+funcnameOff to the start of the func data (P+pclnOff).
NAME_LO = P + funcnameOff
NAME_HI = P + pclnOff
print("NAME TABLE region: 0x%X .. 0x%X  (%d bytes)" % (NAME_LO, NAME_HI, NAME_HI - NAME_LO))


def find_outside(tok):
    """All byte offsets of tok that are NOT inside the pclntab name table."""
    tb = tok.encode()
    out = []
    s = 0
    while True:
        i = b.find(tb, s)
        if i < 0:
            break
        if not (NAME_LO <= i < NAME_HI):
            out.append(i)
        s = i + 1
    return out


def find_inside(tok):
    tb = tok.encode()
    out = []
    s = 0
    while True:
        i = b.find(tb, s)
        if i < 0:
            break
        if NAME_LO <= i < NAME_HI:
            out.append(i)
        s = i + 1
    return out


SENT = ["<unknown>", "<unknown operator>", "<disconnected>", "unknown"]
print()
print("=" * 78)
print("SENTINELS -- literal storage vs name-table storage, SEPARATED")
print("=" * 78)
print("  %-24s %8s %8s   %s" % ("token", "OUTSIDE", "INSIDE", "outside offsets"))
row = {}
for t in SENT:
    o = find_outside(t)
    i_ = find_inside(t)
    row[t] = dict(out=o[:6], out_n=len(o), in_n=len(i_))
    print("  %-24s %8d %8d   %s" % (t, len(o), len(i_),
          ", ".join("0x%X" % x for x in o[:4])))

print()
print("  >>> a sentinel present OUTSIDE the name table is a REAL COMPILED LITERAL.")
print("  >>> a sentinel present ONLY inside the name table is a FUNCTION NAME.")

# --- now the query/SQL family: what does D91 actually claim? ---
print()
print("=" * 78)
print("THE QUERY-STRING FAMILY (D91: 'ownership filter SQL/query string')")
print("=" * 78)
QUERY = [
    b"SELECT", b"select",
    b"Owner", b"owner",
    b"operator", b"Operator",
    b"conversation", b"Conversation",
    b"WHERE", b"where",
    b"ai_conversation", b"ai_conversations",
    b"GetAIConversationMessages",
]
for q in QUERY:
    o = [x for x in ([m.start() for m in re.finditer(re.escape(q), b)])
         if not (NAME_LO <= x < NAME_HI)]
    print("  %-30s OUTSIDE-name-table hits: %d" % (q.decode(), len(o)))
    if q in (b"ai_conversation", b"ai_conversations", b"GetAIConversationMessages"):
        for x in o[:6]:
            s = max(0, x - 40)
            ctx = b[s:x + 90]
            pr = "".join(chr(c) if 32 <= c < 127 else ("|" if c == 0 else ".") for c in ctx)
            print("       0x%-9X %s" % (x, pr))

json.dump(row, open(os.path.join(HERE, "_d121_pair1b.json"), "w"), indent=1)
print()
print("wrote _d121_pair1b.json")
