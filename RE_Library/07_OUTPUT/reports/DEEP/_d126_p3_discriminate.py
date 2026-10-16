"""
_d126_p3_discriminate.py -- what DOES discriminate called from uncalled?

Presence of rpcpb.(*sliverRPCClient).<Name> is worthless: protoc-gen-go emits a
client method for EVERY ServiceDesc entry.  D103 already measured 201/201.

The candidate discriminating signals, tested against known-called controls AND
known-uncalled stubs:

  A. method-path literal  "/rpcpb.SliverRPC/<Name>"   -- built by the client when
     it constructs an outgoing request.  Should appear for CALLED methods.
  B. the generated handler symbol  rpcpb._SliverRPC_<Name>_Handler  -- emitted for
     every method too, so probably non-discriminating; measured to find out.
  C. invocation-site closure names  <Name>.func1  etc.

Ground truth for the test:
  CALLED   : GetVersion, GetSessions, GetBeacons, GetAIConversation, SaveAIConversation
  UNCALLED : the D103 18 (minus GetAIConversationMessages, which D121 falsified)

A test that flags both groups alike is not a test.  Report the split.
"""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
EXE = os.path.join(WS, r"RE_Library\02_BINARIES\sliver\sliver-client_windows-amd64.exe")
HERE = os.path.join(WS, r"RE_Library\07_OUTPUT\reports\DEEP")
b = open(EXE, "rb").read()

CALLED = ["GetVersion", "GetSessions", "GetBeacons", "GetAIConversation", "SaveAIConversation"]
UNCALLED = ["BuilderRegister", "BuilderTrigger", "CrackFileChunkDownload", "CrackstationBenchmark",
            "CrackstationRegister", "CrackstationTrigger", "CrackTaskByID", "CrackTaskUpdate",
            "CredsSniffHashType", "CredsUpdate", "GenerateExternalGetBuildConfig",
            "GenerateExternalSaveBuild", "GetCredByID", "GetPlaintextCredsByHashType",
            "Host", "RestartJobs", "ShellcodeRDI"]
FALSIFIED = ["GetAIConversationMessages"]

print("SCOPE: %s" % EXE)
print("COUNTED: %d bytes" % len(b))
print("COUNTED: %d CALLED controls, %d UNCALLED stubs, %d falsified" %
      (len(CALLED), len(UNCALLED), len(FALSIFIED)))
print()


def probe(m):
    return dict(
        path=b.count(("/rpcpb.SliverRPC/%s\"" % m).encode()),
        path_loose=b.count(("/rpcpb.SliverRPC/%s" % m).encode()),
        handler=b.count(("rpcpb._SliverRPC_%s_Handler" % m).encode()),
        func1=b.count(("rpcpb._SliverRPC_%s_Handler.func1" % m).encode()),
    )


def show(title, names):
    print("=" * 104)
    print(title)
    print("=" * 104)
    print("  %-34s %6s %11s %8s %7s" % ("Method", "path", "path_loose", "handler", "func1"))
    tot = dict(path=0, handler=0, func1=0)
    for m in names:
        r = probe(m)
        for k in tot:
            tot[k] += 1 if r[k] else 0
        print("  %-34s %6d %11d %8d %7d" % (m, r["path"], r["path_loose"], r["handler"], r["func1"]))
    print("  %-34s %6d %11s %8d %7d   <- methods WITH a hit" %
          ("TOTALS (%d)" % len(names), tot["path"], "", tot["handler"], tot["func1"]))
    print()
    return tot


c = show("GROUP A -- CALLED (positive control)", CALLED)
u = show("GROUP B -- UNCALLED per D103", UNCALLED)
f = show("GROUP C -- falsified by D121 PAIR 1", FALSIFIED)

print("=" * 104)
print("DISCRIMINATION VERDICT")
print("=" * 104)
print("  CALLED   with method-path literal : %d / %d" % (c["path"], len(CALLED)))
print("  UNCALLED with method-path literal : %d / %d" % (u["path"], len(UNCALLED)))
print()
if c["path"] and not u["path"]:
    print("  *** DISCRIMINATING: the method-path literal separates the groups. ***")
    print("      A method-path literal is built only when the client constructs an")
    print("      outgoing request, so its ABSENCE is binary evidence of no call site.")
elif c["path"] == len(CALLED) and u["path"] == len(UNCALLED):
    print("  *** NOT DISCRIMINATING: both groups carry the literal. ***")
    print("      It is emitted for every method, so it is a census not a call test.")
else:
    print("  *** PARTIAL: report the split, do not round it. ***")
    print("      CALLED %.0f%%, UNCALLED %.0f%%" %
          (100.0 * c["path"] / len(CALLED), 100.0 * u["path"] / len(UNCALLED)))

from collections import Counter
for lbl, t, n in (("CALLED", c, len(CALLED)), ("UNCALLED", u, len(UNCALLED))):
    d = Counter()
    for m in (CALLED if lbl == "CALLED" else UNCALLED):
        r = probe(m)
        d["path+func1" if (r["path"] and r["func1"]) else
          "path only" if r["path"] else
          "func1 only" if r["func1"] else "neither"] += 1
    print()
    print("  %s distribution (n=%d):" % (lbl, n))
    for k, v in sorted(d.items()):
        print("     %-12s %3d  (%.0f%%)" % (k, v, 100.0 * v / n))

json.dump(dict(called=c, uncalled=u, falsified=f), open(os.path.join(HERE, "_d126_discriminate.json"), "w"), indent=1)
print()
print("wrote _d126_discriminate.json")
