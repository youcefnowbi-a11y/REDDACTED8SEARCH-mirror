"""
D85 probe 2 -- adjudicate two drifts before they reach the report.

DRIFT A: UNRESOLVABLE is 45 here, 44 in D74. One site differs. Find it.
DRIFT B: `encode_x` reported 76 occurrences / 9 files. Is `.encode` a shell
         escaping primitive, or is my pattern matching charset encoding?
         RULE: a primitive counts only if a control shows it can defeat shell
         metacharacter interpretation. Print the actual matches.
"""
import os, re, json, collections

ROOT = r"RE_Library\01_SOURCE_c2\metasploit"
POST = os.path.join(ROOT, "modules", "post")
HERE = os.path.dirname(os.path.abspath(__file__))

# --- DRIFT B first: what IS .encode in this corpus?
print("=== DRIFT B: every `.encode` call site in modules/post ===")
n = 0
for dp, ds, fs in os.walk(POST):
    for f in fs:
        if not f.endswith(".rb"):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, ROOT)
        t = open(p, encoding="utf-8", errors="ignore").read()
        for i, l in enumerate(t.split("\n"), 1):
            for m in re.finditer(r"\.encode\b", l):
                n += 1
                if n <= 30:
                    print("   %s:%d  %s" % (rel, i, l.strip()[:100]))
print("   total .encode hits:", n)
print()
print("   CONTROL: does any .encode call involve a shell metacharacter or a quote?")
susp = 0
for dp, ds, fs in os.walk(POST):
    for f in fs:
        if not f.endswith(".rb"):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, ROOT)
        t = open(p, encoding="utf-8", errors="ignore").read()
        for i, l in enumerate(t.split("\n"), 1):
            if ".encode" in l:
                arg = l[l.find(".encode"):]
                if re.search(r"['\"]\\?['\"]|\$|;|\||`", arg[:60]):
                    susp += 1
                    print("   SUSPECT %s:%d  %s" % (rel, i, l.strip()[:95]))
print("   .encode with a shell-metachar-looking argument:", susp)
print()

# --- DRIFT A: compare this run's classification to D74's stored json
print("=== DRIFT A: UNRESOLVABLE 45 (now) vs 44 (D74) ===")
pop = json.load(open(os.path.join(HERE, "_d85_pop.json")))
now_unres = sorted((r["file"], r["line"]) for r in pop if r["cls"] == "UNRESOLVABLE")
print("   current UNRESOLVABLE sites:", len(now_unres))
try:
    d74 = json.load(open(os.path.join(HERE, "_d74_t1v3.json")))
    # t1v3 is per-EXPRESSION; collapse to sites with the same ORDER rule
    ORDER = ["REMOTE_RESPONSE", "SESSION_TARGET", "DATASTORE", "MIXIN_HELPER",
             "LOCAL_TOOL_PATH", "HARDCODED", "METHOD_BODY_UNRESOLVED",
             "PARAM_UNRESOLVED", "UNRESOLVABLE"]
    sites = collections.defaultdict(list)
    for r in d74:
        sites[(r["file"], r["line"])].append(r["cls"])
    d74_unres = sorted(k for k, v in sites.items()
                       if min(v, key=lambda c: ORDER.index(c)) == "UNRESOLVABLE")
    print("   D74 (_d74_t1v3.json) UNRESOLVABLE sites:", len(d74_unres))
    only_now = sorted(set(now_unres) - set(d74_unres))
    only_d74 = sorted(set(d74_unres) - set(now_unres))
    print("   in NOW not in D74 :", only_now)
    print("   in D74 not in NOW :", only_d74)
except FileNotFoundError as e:
    print("   D74 json not readable:", e)
