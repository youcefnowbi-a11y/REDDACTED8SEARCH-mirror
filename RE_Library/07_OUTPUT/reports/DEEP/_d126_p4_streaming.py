"""
_d126_p4_streaming.py -- validate the recovered discriminator on a LARGER population.

Finding so far:  BuilderRegister and CrackstationRegister are the ONLY two of D103's
18 with func1 == 0, and both are grpc.ServerStreamingClient.  n=2 is not a validation.

Test: take EVERY method in the generated client stub set, split by source-side
signature (streaming vs unary), and measure the .func1 closure in the binary.
If streaming => func1==0 holds across the whole set, the discriminator is real.
If it holds for 2 of 40, it was coincidence.

This is the "classifier must be validated" gate applied to a binary probe.
"""
import os, re, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
EXE = os.path.join(WS, r"RE_Library\02_BINARIES\sliver\sliver-client_windows-amd64.exe")
PBG = os.path.join(WS, r"RE_Library\01_SOURCE_c2\sliver\protobuf\rpcpb\services_grpc.pb.go")
HERE = os.path.join(WS, r"RE_Library\07_OUTPUT\reports\DEEP")

b = open(EXE, "rb").read()
print("SCOPE: %s" % EXE)
print("COUNTED: %d bytes" % len(b))
print("SCOPE: %s" % PBG)

src = open(PBG, "r", encoding="utf-8", errors="replace").read()
print("COUNTED: %d source chars" % len(src))
print()

# every generated client method, with its return signature
pat = re.compile(
    r"func \(c \*sliverRPCClient\) (\w+)\(ctx context\.Context[^)]*\) \(([^)]*)\)",
    re.S)
methods = []
for m in pat.finditer(src):
    name, ret = m.group(1), m.group(2).strip()
    methods.append((name, ret))

print("COUNTED: %d client methods recovered from the generated stub" % len(methods))
print()

# classifier: streaming iff the return type is a stream client
def is_stream(ret):
    return "StreamingClient" in ret or "StreamClient" in ret


streaming = [n for n, r in methods if is_stream(r)]
unary = [n for n, r in methods if not is_stream(r)]
print("CLASSIFIED from SOURCE:")
print("   streaming : %d" % len(streaming))
print("   unary     : %d" % len(unary))
print()

# the binary probe
def has_func1(m):
    return b.count(("rpcpb._SliverRPC_%s_Handler.func1" % m).encode()) > 0


def has_handler(m):
    return b.count(("rpcpb._SliverRPC_%s_Handler" % m).encode()) > 0


# cross-tabulate
import collections
tab = collections.Counter()
miss_detail = []
for name, ret in methods:
    key = ("streaming" if is_stream(ret) else "unary", has_func1(name))
    tab[key] += 1
    if not has_func1(name):
        miss_detail.append((name, "streaming" if is_stream(ret) else "unary", ret[:70]))

print("=" * 100)
print("CROSS-TABULATION: source signature  x  binary .func1 presence")
print("=" * 100)
for (kind, f1) in sorted(tab):
    print("   source=%-10s func1=%-5s  n=%d" % (kind, f1, tab[(kind, f1)]))
print()
print("   input cardinality: %d methods" % len(methods))
print()

# the specific claim
st_no_f1 = tab[("streaming", False)]
st_f1 = tab[("streaming", True)]
un_f1 = tab[("unary", True)]
un_no_f1 = tab[("unary", False)]
print("=" * 100)
print("DISCRIMINATOR VALIDATION")
print("=" * 100)
print("   streaming WITHOUT func1 : %d / %d" % (st_no_f1, len(streaming)))
print("   streaming WITH    func1 : %d / %d" % (st_f1, len(streaming)))
print("   unary     WITHOUT func1 : %d / %d" % (un_no_f1, len(unary)))
print("   unary     WITH    func1 : %d / %d" % (un_f1, len(unary)))
print()
if st_no_f1 == len(streaming) and un_no_f1 == 0:
    print("   *** VALIDATED: streaming <=> func1 absent, across all %d methods. ***" % len(methods))
    print("       The probe is a source-free SERVER-STREAMING detector for Go gRPC binaries.")
elif un_no_f1 == len(unary) and st_f1 == 0:
    print("   *** INVERTED: func1 absent <=> UNARY. Same information, opposite polarity. ***")
elif st_no_f1 == 0 and un_no_f1 == 0:
    print("   *** NOT DISCRIMINATING: every method has func1. The 2-of-18 was coincidence. ***")
elif st_no_f1 < len(streaming) or un_no_f1 > 0:
    print("   *** PARTIAL CORRELATION -- report the full table, do not summarise. ***")
print()
print("   ALL methods WITHOUT a .func1 closure (%d):" % len(miss_detail))
for n, k, r in miss_detail:
    print("      %-34s source=%-10s %s" % (n, k, r))

json.dump(dict(n=len(methods), streaming=len(streaming), unary=len(unary),
               missing_func1=[m[0] for m in miss_detail],
               cross_tab={str(k): v for k, v in tab.items()}),
          open(os.path.join(HERE, "_d126_streaming.json"), "w"), indent=1)
print()
print("wrote _d126_streaming.json")
