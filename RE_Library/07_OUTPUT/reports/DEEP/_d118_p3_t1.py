"""
D118 probe 3 -- T1: does the CITING DOCUMENT'S SUBJECT MATTER disambiguate
each of the 84 ambiguous citations?

The Lead's framing, verbatim:
  "A D11 citation inside a Sliver report almost certainly means
   D11_sliver_rpc_core; inside Havoc, D11_havoc_native_win32."
  "If subject-matter adjacency disambiguates >=80%, the hazard is smaller."
  "If it disambiguates ~50%, the hazard is WORSE, because a reader's guess is
   a coin flip that FEELS like a resolution."

METHOD -- and its honesty constraint:
The disambiguation signal must come from the CITING DOCUMENT'S IDENTITY, not
from the citation text, or the test is circular. So:
  signal A = the citing document's own filename/family token (sliver, havoc,
             mythic, pupy, merlin) vs the candidate files' tokens.
  signal B = token overlap between the citing doc's TITLE and each candidate's
             title.
A citation is DISAMBIGUATED if exactly ONE candidate's token matches the citing
doc's token. If TWO OR MORE match, or NONE, it is NOT disambiguated.
Report the split and say which way it cuts. No threshold declared in advance.
"""
import os, re, sys, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
REPORTS = os.path.join(WS, "RE_Library", "07_OUTPUT", "reports")
DEEP = os.path.join(REPORTS, "DEEP")

t4 = json.load(open(os.path.join(DEEP, "_d118_t4b.json")))
multi = {int(k): v for k, v in t4["dmulti"].items()}

OUT = {"CROSSREF_AUDIT.md", "D59_crossref_remediation.md", "README.md"}
files = []
for dp, ds, fs in os.walk(REPORTS):
    if "\\extractions\\" in dp:
        continue
    for f in fs:
        if f.endswith(".md"):
            files.append(os.path.join(dp, f))

# token vocabulary drawn ONLY from the candidate filenames + the citing names
TOKENS = set()
for k, v in multi.items():
    for b in v:
        for t in re.split(r"[_\W]+", b):
            if len(t) >= 4 and not t.isdigit():
                TOKENS.add(t.lower())

def toks(s):
    return set(t.lower() for t in re.split(r"[_\W]+", s) if len(t) >= 4 and not t.isdigit())

print("=" * 78)
print("T1 -- SUBJECT-MATTER DISAMBIGUATION OF THE %d AMBIGUOUS CITATIONS" % t4["amb"])
print("=" * 78)
print("   token vocabulary (from candidate filenames): %d" % len(TOKENS))
print("   %s" % ", ".join(sorted(TOKENS)))
print()

rows = []
for k in sorted(multi):
    pat = re.compile(r"\bD%d\s*§\s*([\d.]+)" % k)
    cands = multi[k]
    for p in files:
        b = os.path.basename(p)
        if b in OUT or b.startswith("D118_"):
            continue
        txt = open(p, encoding="utf-8", errors="ignore").read()
        ctoks = toks(b)
        # candidate token scores against the citing doc's name
        for m in pat.finditer(txt):
            sec = m.group(1)
            # which candidates share a token with the citing document?
            matched = [c for c in cands if (ctoks & toks(c))]
            rows.append(dict(num=k, sec=sec, citing=b, ncand=len(cands),
                             matched=matched))

print("   --- per-citation disambiguation ---")
cnt = collections.Counter()
detail = collections.defaultdict(list)
for r in rows:
    if len(r["matched"]) == 1:
        verdict = "UNIQUE"
    elif len(r["matched"]) == 0:
        verdict = "NONE"
    else:
        verdict = "AMBIG-%d" % len(r["matched"])
    cnt[verdict] += 1
    detail[verdict].append(r)

print("   MANDATORY distribution: verdict over %d citations" % len(rows))
for k, v in cnt.most_common():
    print("      %-10s %4d  (%.1f%%)" % (k, v, 100.0 * v / max(1, len(rows))))
print()

uniq = sum(v for k, v in cnt.items() if k == "UNIQUE")
none = cnt.get("NONE", 0)
amb2 = sum(v for k, v in cnt.items() if k.startswith("AMBIG"))
print("   DISAMBIGUATED BY SUBJECT MATTER : %d / %d = %.1f%%" % (uniq, len(rows), 100.0 * uniq / max(1, len(rows))))
print("   NOT disambiguated (NONE)        : %d" % none)
print("   NOT disambiguated (>=2 match)   : %d" % amb2)
print()

print("   --- the AMBIG->1 rows, where the citing doc names TWO candidates ---")
for r in detail.get("AMBIG-2", [])[:10]:
    print("      D%d SS%s  in  %s" % (r["num"], r["sec"], r["citing"][:52]))
    for c in r["matched"]:
        print("            candidate: %s" % c)
print()

print("   --- control: does the signal EVER fire? show 8 UNIQUE rows ---")
for r in detail.get("UNIQUE", [])[:8]:
    print("      D%d SS%s  in  %s  ->  %s" % (r["num"], r["sec"], r["citing"][:44], r["matched"][0][:52]))
print()

json.dump(dict(rows=rows, dist=dict(cnt), uniq=uniq, none=none, amb2=amb2),
          open(os.path.join(DEEP, "_d118_t1.json"), "w"), indent=1)
print("wrote _d118_t1.json")
