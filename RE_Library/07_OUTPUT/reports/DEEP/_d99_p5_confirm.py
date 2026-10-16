import re, os, sys, json
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\reports\DEEP"

print("=== CONFIRM: probe 2 used  `is False`  against a THREE-VALUED `resolved` ===")
print("   SEC branch sets  resolved = secs.get(target)  -> an int OR None")
print("   failure filter was  if e['resolved'] is False")
print("   None is not False. Every unresolvable SEC edge was skipped silently.")
print()

j = json.load(open(os.path.join(HERE, "_d99_edges.json")))
E = j["edges"]
c = Counter(repr(e["resolved"]) for e in E)
print("   ACTUAL `resolved` distribution over all %d edges:" % len(E))
for k, v in c.most_common():
    print("      %-8s %5d" % (k, v))
print()

sec = [e for e in E if e["kind"] == "SEC"]
c2 = Counter(repr(e["resolved"]) for e in sec)
print("   SEC-only `resolved` distribution (%d edges):" % len(sec))
for k, v in c2.most_common():
    print("      %-8s %5d" % (k, v))
print()

n_none = sum(1 for e in E if e["resolved"] is None)
print("   TRUE failed count (resolved is None)      :", n_none)
print("   probe 2 reported (resolved is False)      : 0")
print()
print("=== The known case, through the corrected test ===")
for e in E:
    if e["owner"] == "D13" and e.get("target") == "7.2":
        print("   %s:%d  kind=%s target=%s resolved=%r" % (e["src"], e["srcline"], e["kind"], e["target"], e["resolved"]))
