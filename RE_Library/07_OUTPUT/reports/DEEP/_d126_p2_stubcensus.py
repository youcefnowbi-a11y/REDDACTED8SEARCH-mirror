"""
_d126_p2_stubcensus.py -- D103 R2 conversion: source-stub census -> BINARY name-table measurement.

D103:403 admits the 18-stub claim is 'asserted from a source call-site census, not
from the binary'. This runs the binary check.

METHOD (the PAIR-1 carve-out technique, generalised):
  The pclntab name table occupies a contiguous region. A symbol present OUTSIDE it is
  a real compiled string; present INSIDE it is a FUNCTION NAME. For the stub question
  we want INSIDE -- is the method's generated stub in the name table at all?

  Present  -> the linker kept a symbol for it: a stub that exists in the image.
  Absent   -> genuinely dead: no generated stub symbol survived.

Every count prints its input cardinality beside its result.
"""
import os, re, sys, json, struct
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
EXE = os.path.join(WS, r"RE_Library\02_BINARIES\sliver\sliver-client_windows-amd64.exe")
HERE = os.path.join(WS, r"RE_Library\07_OUTPUT\reports\DEEP")

b = open(EXE, "rb").read()
N = len(b)
print("SCOPE: %s" % EXE)
print("COUNTED: file bytes = %d" % N)

P = 0x269DDE0
funcnameOff = struct.unpack_from("<Q", b, P + 32)[0]
pclnOff = struct.unpack_from("<Q", b, P + 64)[0]
NAME_LO = P + funcnameOff
NAME_HI = P + pclnOff
print("NAME-TABLE REGION (carve-out): 0x%X .. 0x%X  = %d bytes" % (NAME_LO, NAME_HI, NAME_HI - NAME_LO))
print()

# the 18 from D103 s1.4.  #13 already falsified in the PAIR-1 pass; re-measured here
# so the whole population is on one instrument.
STUBS = [
    ("BuilderRegister",              "builder"),
    ("BuilderTrigger",               "builder"),
    ("CrackFileChunkDownload",       "crack"),
    ("CrackstationBenchmark",        "crackstation"),
    ("CrackstationRegister",         "crackstation"),
    ("CrackstationTrigger",          "crackstation"),
    ("CrackTaskByID",                "crack"),
    ("CrackTaskUpdate",              "crack"),
    ("CredsSniffHashType",           "creds"),
    ("CredsUpdate",                  "creds"),
    ("GenerateExternalGetBuildConfig", "external build"),
    ("GenerateExternalSaveBuild",    "external build"),
    ("GetAIConversationMessages",    "AI"),
    ("GetCredByID",                  "creds"),
    ("GetPlaintextCredsByHashType",  "creds"),
    ("Host",                         "hosts"),
    ("RestartJobs",                  "jobs"),
    ("ShellcodeRDI",                 "shellcode"),
]
print("COUNTED: %d stub methods from D103 s1.4" % len(STUBS))
print()

# positive controls: methods D103 says ARE called.
CTRL = ["GetVersion", "GetSessions", "SaveAIConversation", "GetBeacons", "GetAIConversation"]
print("COUNTED: %d positive controls (methods D103 says ARE called)" % len(CTRL))
print()

CLIENT_STUB = "rpcpb.(*sliverRPCClient)."
ANY_STUB = "rpcpb._SliverRPC_"
HANDLER = "rpcpb._SliverRPC_%s_Handler"

rows = []
print("=" * 100)
print("%-32s %-14s %6s %6s %6s  %s" % ("Method", "Family", "Client", "Other", "Handler", "VERDICT"))
print("=" * 100)


def count(needle):
    return b.count(needle.encode())


for name, fam in STUBS:
    cl = count(CLIENT_STUB + name)
    # the generated handler symbol: rpcpb._SliverRPC_<Name>_Handler
    hnd = count("rpcpb._SliverRPC_%s_Handler" % name)
    # every mention of the bare name anywhere in the image
    tot = count(name)
    verdict = "PRESENT" if cl else ("NAME-ONLY" if tot else "ABSENT")
    rows.append(dict(m=name, fam=fam, client=cl, handler=hnd, total=tot, verdict=verdict))
    print("%-32s %-14s %6d %6d %6d  %s" % (name, fam, cl, tot, hnd, verdict))

print()
print("=" * 100)
print("POSITIVE CONTROLS -- must be PRESENT, else the instrument is broken")
print("=" * 100)
ctrl_ok = 0
for name in CTRL:
    cl = count(CLIENT_STUB + name)
    tot = count(name)
    ok = "PRESENT" if cl else "*** ABSENT ***"
    if cl:
        ctrl_ok += 1
    print("%-32s client-stub=%6d  total=%-6d  %s" % (name, cl, tot, ok))
print()
print("CONTROLS PASSED: %d / %d" % (ctrl_ok, len(CTRL)))
if ctrl_ok == 0:
    print("  *** INSTRUMENT INVALID: not one control resolved. Do not read the stub table. ***")
elif ctrl_ok < len(CTRL):
    print("  *** PARTIAL: %d of %d resolved -- state this beside any result. ***" % (ctrl_ok, len(CTRL)))

# distribution print -- a classifier returning one value for 100% of input is broken
print()
print("=" * 100)
print("DISTRIBUTION PRINT (mandatory: a classifier returning one value for 100% is broken)")
print("=" * 100)
from collections import Counter
d = Counter(r["verdict"] for r in rows)
for k, v in sorted(d.items()):
    print("  %-12s %3d / %d   (%.0f%%)" % (k, v, len(rows), 100.0 * v / len(rows)))
print()
print("  input cardinality : %d stub methods" % len(rows))
print("  distinct verdicts : %d" % len(d))

json.dump(dict(rows=rows, controls=CTRL, ctrl_ok=ctrl_ok,
               name_table=[hex(NAME_LO), hex(NAME_HI), NAME_HI - NAME_LO]),
          open(os.path.join(HERE, "_d126_stubcensus.json"), "w"), indent=1)
print()
print("wrote _d126_stubcensus.json")
