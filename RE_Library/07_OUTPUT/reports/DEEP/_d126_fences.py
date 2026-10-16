import os
WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
P = os.path.join(WS, r"RE_Library\07_OUTPUT\reports\DEEP",
    "D126_layer_pair_source_against_binary_the_other_17_stubs_nil_guard_reachability_and_the_name_table_carve_out_technique.md")
FENCE = chr(96) * 3
t = open(P, encoding="utf-8").read()
lines = t.split("\n")

print("=== FENCE OPEN/CLOSE PAIRING ===")
opened = None
n = 0
unclosed = 0
for i, l in enumerate(lines, 1):
    if l.startswith(FENCE):
        n += 1
        if opened is None:
            opened = (i, l)
            print("  OPEN  :%-5d %s" % (i, l.strip() or "(bare)"))
        else:
            print("  CLOSE :%-5d %-8s <- paired with %d" % (i, l.strip() or "(bare)", opened[0]))
            opened = None
if opened is not None:
    print("  *** UNCLOSED FENCE opened at line %d ***" % opened[0])
    unclosed = 1
print("  total fence lines: %d   unclosed: %d" % (n, unclosed))
print()

print("=== H1 and tail ===")
print("  line 1 : %r" % lines[0][:88])
ne = [l for l in lines if l.strip()]
print("  last 3 : ")
for l in ne[-3:]:
    print("      %r" % l[:96])
print()

print("=== the 4 standalone-tag duplicate lines, with their line numbers ===")
for i, l in enumerate(lines, 1):
    if l.strip() in ("`[verified]`", "`[binary]` `[verified]`"):
        print("  :%-5d %r" % (i, l.strip()))
