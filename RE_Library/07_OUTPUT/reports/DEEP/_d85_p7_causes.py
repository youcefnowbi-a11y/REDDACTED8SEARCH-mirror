"""
D85 probe 7 -- T2: cause census of the 45 UNRESOLVABLE sites, then reduce the largest.

D74 §1.5 named five causes with ONE instance each. A named instance is not a
census (Rule 20). So first: classify all 45 by cause, print the distribution,
then attack the largest.
"""
import os, re, json, collections

HERE = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\reports\DEEP"
ROOT = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\01_SOURCE_c2\metasploit"
sites = json.load(open(os.path.join(HERE, "_d85_sites.json")))
unres = [s for s in sites if s["cls"] == "UNRESOLVABLE"]
print("UNRESOLVABLE sites:", len(unres))
print()

DEFRX = re.compile(r"^(\s*)def\s+([\w?!=\.]+)\s*(?:\(([^)]*)\))?")
INTERP = re.compile(r"#\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}")


def enclosing_def(lines, idx):
    for i in range(idx, -1, -1):
        m = DEFRX.match(lines[i])
        if m:
            return i, m.group(2)
    return None, None


causes = collections.Counter()
detail = collections.defaultdict(list)
for s in unres:
    p = os.path.join(ROOT, s["file"])
    lines = open(p, encoding="utf-8", errors="ignore").read().split("\n")
    idx = s["line"] - 1
    didx, dname = enclosing_def(lines, idx)
    exprs = [x.group(0) for x in INTERP.finditer(s["cmd"])]
    toks = []
    for e in exprs:
        inner = e[2:-1].strip()
        bm = re.match(r"^([A-Za-z_@$][\w?!]*)", inner)
        toks.append((bm.group(1) if bm else None, inner))
    # cause determination
    if didx is None:
        cause = "NO_ENCLOSING_DEF"
    else:
        cause = None
        for tok, inner in toks:
            if tok is None:
                cause = cause or "EXPRESSION_NOT_NAME"
                continue
            # block variable?
            blk = re.compile(r"\|\s*[\w,\s]*\b" + re.escape(tok) + r"\b[\w,\s]*\|")
            found_block = False
            for k in range(max(0, didx), idx):
                if blk.search(lines[k]):
                    found_block = True
                    break
            if found_block:
                cause = cause or "BLOCK_VARIABLE"
                continue
            if re.search(r"\b" + re.escape(tok) + r"\s*\[", inner):
                cause = cause or "MEMBER_INDEX_ACCESS"
                continue
            if re.search(r"\b" + re.escape(tok) + r"\s*[\+\-]|[\+\-]\s*" + re.escape(tok), inner):
                cause = cause or "CONCATENATION_EXPR"
                continue
        cause = cause or "OTHER"
    causes[cause] += 1
    detail[cause].append((s["file"], s["line"], s["cmd"][:90]))

print("=== CAUSE CENSUS (distribution, mandatory) ===")
for k, v in causes.most_common():
    print("   %-24s %4d" % (k, v))
print()
for k, v in causes.most_common():
    print("=== %s (%d) ===" % (k, v))
    for f, l, c in detail[k][:40]:
        print("   %s:%d  %s" % (f, l, c))
    print()
json.dump({k: v for k, v in detail.items()},
          open(os.path.join(HERE, "_d85_causes.json"), "w"), indent=1)
