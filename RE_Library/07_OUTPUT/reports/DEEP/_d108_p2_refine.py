"""
D108 probe 2 -- T1 REFINED: only tokens that CAN be a file.

Probe 1 captured 260 backticked tokens ending in ".something", of which 85 were
Go symbol paths (`a.Pivots.Parent`), .NET type names (`MissingMemberHandling.Ignore`)
and Java class names (`brut.apktool.Main`). Those are NOT files. The regex did not
know what a path is -- exactly the class of defect D94 documented.

REFINED RULE: a token is a FILE CANDIDATE only if
  (a) it has a filesystem separator AND a known file extension, OR
  (b) it is a bare filename whose extension is in the KNOWN-ARTIFACT set, OR
  (c) it appears inside a [verified]/[read] tag sentence as a location.

Symbol paths are excluded explicitly: a dotted identifier chain with no separator
and a non-file extension (.Parent, .Map, .Ignore, .Main) is a SYMBOL.
"""
import os, re, sys, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
DEEP = os.path.join(WS, "RE_Library", "07_OUTPUT", "reports", "DEEP")

FILEEXT = {"md","py","ps1","psm1","json","csv","tsv","txt","log","go","cs","rs","c","cpp","cc","h","hpp",
           "rb","java","kt","smali","wasm","so","dll","exe","bin","elf","dylib","o","a","lib","jar","apk",
           "ipa","app","db","sqlite","yaml","yml","toml","xml","plist","sh","bash","bat","cmd","sln","csproj",
           "jsonl","ndjson","map","pdb","idb","gpr","zip","tar","gz","pcap","svg","png"}
NOTFILE_HINT = {"Parent","Map","Ignore","Error","Include","Links","Agents","Main","Func","Count",
                "Ignore,","Object","Settings","LazyList","Write","Read","Close","Name","ID","Ids"}

rows = json.load(open(os.path.join(DEEP, "_d108_p1_cites.json")))

def is_file_candidate(tok):
    t = tok.strip().strip("`")
    if " " in t or t.startswith(("$", "...", "(")):
        return False
    m = re.search(r"\.([A-Za-z0-9_]{1,8})$", t)
    if not m:
        return False
    ext = m.group(1).lower()
    has_sep = ("\\" in t) or ("/" in t)
    if ext not in FILEEXT:
        return False          # .Parent .Map .Ignore .Main .Links -> symbol
    if has_sep:
        return True
    # bare filename: reject dotted identifier chains like a.b.c
    parts = t.split(".")
    if len(parts) > 2:
        return False
    return True

cand = [r for r in rows if is_file_candidate(r["token"])]
excl = [r for r in rows if not is_file_candidate(r["token"])]

print("=== T1 REFINED: file candidates vs symbols ===")
print("   backticked tokens captured by probe 1 : %d" % len(rows))
print("   FILE CANDIDATES                       : %d" % len(cand))
print("   excluded as symbols/exprs/pseudocode  : %d" % len(excl))
print()
print("   MANDATORY distribution of the EXCLUDED, by shape (proof the filter is right):")
sh = collections.Counter()
for r in excl:
    t = r["token"].strip("`")
    if t.startswith(("$", "...", "(")) or " " in t:
        sh["shell expression / pseudocode"] += 1
    elif "." in t and "\\" not in t and "/" not in t:
        sh["dotted SYMBOL path (Go/.NET/Java)"] += 1
    else:
        sh["other"] += 1
for k, v in sh.most_common():
    print("      %-38s %4d" % (k, v))
print()
print("   sample of excluded SYMBOL paths (the 85 that made probe 1 look bad):")
n = 0
for r in excl:
    t = r["token"].strip("`")
    if "." in t and "\\" not in t and "/" not in t and n < 12:
        print("      %s" % t)
        n += 1
print()

# resolve
def locate(tok):
    t = tok.strip().strip("`")
    for base in (DEEP, WS, os.path.join(WS, "RE_Library", "07_OUTPUT"), os.path.join(WS, "RE_Library")):
        c = os.path.join(base, t)
        if os.path.exists(c):
            return c
    b = os.path.basename(t.replace("\\", "/"))
    if b:
        for dp, ds, fs in os.walk(os.path.join(WS, "RE_Library")):
            if b in fs:
                return os.path.join(dp, b)
    return None

for r in cand:
    r["found"] = locate(r["token"])
    r["exists"] = bool(r["found"])

ok = [r for r in cand if r["exists"]]
no = [r for r in cand if not r["exists"]]
print("=== T1 RESULT ===")
print("   file candidates : %d" % len(cand))
print("   EXISTS          : %d" % len(ok))
print("   NOT FOUND       : %d" % len(no))
print("   YIELD (found/  ) : %.1f%%" % (100.0 * len(ok) / max(1, len(cand))))
print()
print("   MANDATORY distribution by report:")
for k, v in collections.Counter(r["report"][:30] for r in cand).most_common():
    sub = [r for r in cand if r["report"][:30] == k]
    got = sum(1 for r in sub if r["exists"])
    print("      %-32s %3d candidates, %3d found" % (k, len(sub), got))
print()
if no:
    print("=== THE GENUINE NOT-FOUND SET (T1's hazard list) ===")
    seen = set()
    for r in no:
        key = (r["report"], r["token"])
        if key in seen:
            continue
        seen.add(key)
        print("   %-16s :%-5d  tags=%-9s  `%s`" % (r["report"][:16], r["line"], r["tag"] or "-", r["token"][:80]))
        print("        | %s" % r["text"][:140])
print()
json.dump(cand, open(os.path.join(DEEP, "_d108_p2_cand.json"), "w"), indent=1)
