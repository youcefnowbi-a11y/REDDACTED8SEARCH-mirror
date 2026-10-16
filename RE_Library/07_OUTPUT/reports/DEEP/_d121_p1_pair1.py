"""
_d121_p1_pair1.py -- PAIR 1: is the AI-path ownership/normalisation string in the
COMPILED build? Compare source string literals against binary string literals.

Method: extract ASCII + UTF-16LE string runs from the exe, then look for the
five sentinels the source switch tests, plus the query-family strings.

NO EXECUTION. Pure byte read.
"""
import os, re, sys, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
EXE = os.path.join(WS, r"RE_Library\02_BINARIES\sliver\sliver-client_windows-amd64.exe")
HERE = os.path.join(WS, r"RE_Library\07_OUTPUT\reports\DEEP")

b = open(EXE, "rb").read()
print("EXE bytes: %d" % len(b))

# --- ASCII string runs, min length 4 ---
RUN = re.compile(rb"[\x20-\x7e]{4,}")
ascii_runs = [m.group().decode("ascii") for m in RUN.finditer(b)]
print("ASCII runs >=4 chars: %d" % len(ascii_runs))

# --- UTF-16LE runs (Go keeps some string data as UTF-16, and Windows resources do) ---
U16 = re.compile(rb"(?:[\x20-\x7e]\x00){4,}")
u16_runs = [m.group().decode("utf-16-le") for m in U16.finditer(b)]
print("UTF-16LE runs >=4 chars: %d" % len(u16_runs))

allset = set(ascii_runs) | set(u16_runs)
blob = b  # for raw byte-substring search we need bytes


def hunt(token, label=""):
    """Find a literal three ways: exact ASCII run, exact UTF-16 run, raw bytes."""
    hits = 0
    where = []
    tb = token.encode("ascii", "ignore")
    if tb:
        start = 0
        while True:
            i = b.find(tb, start)
            if i < 0:
                break
            hits += 1
            if len(where) < 4:
                where.append(i)
            start = i + 1
    return hits, where


TARGETS = [
    # the five switch sentinels -- these are the FUNCTION'S test values
    ('"" (empty)', "empty-string literal, not searchable by bytes"),
    ("unknown", "sentinel 1"),
    ("<unknown>", "sentinel 2"),
    ("<unknown operator>", "sentinel 3"),
    ("<disconnected>", "sentinel 4"),
    # function/type identities the source names
    ("normalizedConversationOperatorName", "the function itself"),
    ("sameConversationMessage", "neighbouring function, control"),
    ("conversationUsesTarget", "neighbouring function, control"),
    ("sameAITargetSelectionIDs", "neighbouring function, control"),
    ("normalizedAITargetIDs", "neighbouring function, control"),
    ("applyTargetSelectionOption", "neighbouring function, control"),
]

print()
print("=" * 78)
print("PAIR 1 -- SOURCE LITERALS vs COMPILED BINARY")
print("=" * 78)
print("  %-38s %6s   %s" % ("literal", "hits", "first offsets"))
print("  " + "-" * 72)
res = {}
for tok, label in TARGETS:
    h, w = hunt(tok)
    res[tok] = dict(hits=h, offs=w, label=label)
    off = ", ".join("0x%X" % x for x in w)
    print("  %-38s %6d   %s" % (tok[:38], h, off))

print()
print("  --- the SENTINEL SET as a block: are they near each other? ---")
sent = ["unknown", "<unknown>", "<unknown operator>", "<disconnected>"]
offs = []
for s in sent:
    h, w = hunt(s)
    if w:
        offs.append((s, w[0]))
offs.sort(key=lambda x: x[1])
for s, o in offs:
    print("    0x%-10X  %s" % (o, s))
if len(offs) >= 2:
    print("    span: 0x%X .. 0x%X  (%d bytes)" % (offs[0][1], offs[-1][1], offs[-1][1] - offs[0][1]))
    # dump the region between the first and last sentinel
    lo = max(0, offs[0][1] - 64)
    hi = min(len(b), offs[-1][1] + 64)
    chunk = b[lo:hi]
    print("    --- region dump 0x%X..0x%X ---" % (lo, hi))
    printable = "".join(chr(c) if 32 <= c < 127 else ("|" if c == 0 else ".") for c in chunk)
    for i in range(0, len(printable), 96):
        print("      %s" % printable[i:i + 96])

json.dump(res, open(os.path.join(HERE, "_d121_pair1.json"), "w"), indent=1)
print()
print("wrote _d121_pair1.json")
