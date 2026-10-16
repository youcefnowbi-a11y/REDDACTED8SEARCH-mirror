"""
D108 probe 5 -- T3 (the partition rule), T4 (renumbering repair-in-prose),
T5 (the D11 ambiguity).

All three are corpus-text sweeps over prompts from the Lead. They are combined
because they share one tokenising pass, and because each needs the same
MANDATORY distribution print and the same positive control.

T3 -- C-09's rule: a summary that partitions a population must sum to it.
T4 -- the pattern "There is no SSX" / "contains only SSX-SSY": defects repaired in
      PROSE rather than removed.
T5 -- D11 names five documents; quantify ambiguous bare-D11 citations.
"""
import os, re, sys, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
REPORTS = os.path.join(WS, "RE_Library", "07_OUTPUT", "reports")

# ---- population: every .md under reports\, recursive, minus out-of-scope
OUT = {"CROSSREF_AUDIT.md", "D59_crossref_remediation.md", "README.md"}
docs = {}
for dp, ds, fs in os.walk(REPORTS):
    if "\\extractions\\" in dp:
        continue
    for f in fs:
        if f.endswith(".md") and f not in OUT and not f.startswith("D108_"):
            p = os.path.join(dp, f)
            docs[os.path.relpath(p, REPORTS)] = open(p, encoding="utf-8", errors="ignore").read()

print("=== POPULATION ===")
print("   in-scope .md documents:", len(docs))
print()

# =====================================================================
# T5 FIRST -- D11 names five documents
# =====================================================================
print("=" * 78)
print("T5 -- THE D11 AMBIGUITY")
print("=" * 78)
DEEP = os.path.join(REPORTS, "DEEP")
allnames = os.listdir(DEEP)
def famprefix(n):
    m = re.match(r"^(D\d+)_", n)
    return m.group(1) if m else None
from collections import defaultdict
fam = defaultdict(list)
for n in allnames:
    if n.endswith(".md"):
        pre = famprefix(n)
        if pre:
            fam[pre].append(n)

print("   MANDATORY distribution: D-number prefixes naming MORE THAN ONE document")
multi = {k: v for k, v in fam.items() if len(v) > 1}
tot_amb = 0
for k in sorted(multi, key=lambda s: -len(multi[s])):
    print("      %-6s -> %d documents" % (k, len(multi[k])))
    for n in sorted(multi[k]):
        print("             %s" % n)
    tot_amb += len(multi[k])
print()
print("   AMBIGUOUS PREFIXES: %d   documenting %d files" % (len(multi), tot_amb))
print("   UNAMBIGUOUS PREFIXES: %d" % len([k for k, v in fam.items() if len(v) == 1]))
print()

# ---- how many bare-D11 citations exist corpus-wide?
print("   --- how many citations use an AMBIGUOUS prefix? ---")
PAT_SEC = re.compile(r"\bD(\d{1,3})\s*§")
counts = collections.Counter()
for rel, t in docs.items():
    for m in PAT_SEC.finditer(t):
        counts["D" + m.group(1)] += 1
print("   MANDATORY distribution: total SS-citations per owner prefix, ambiguous ones flagged")
amb_rows = []
for k in sorted(counts, key=lambda s: -counts[s]):
    flag = "  <== AMBIGUOUS (%d files)" % len(fam.get(k, [])) if len(fam.get(k, [])) > 1 else ""
    if len(fam.get(k, [])) > 1:
        amb_rows.append((k, counts[k], len(fam[k])))
    if counts[k] >= 5 or flag:
        print("      %-6s %5d citations%s" % (k, counts[k], flag))
print()
tot_amb_cites = sum(c for _, c, _ in amb_rows)
print("   TOTAL citations whose owner prefix is AMBIGUOUS: %d" % tot_amb_cites)
print("   of total SS-citations: %d (%.1f%%)" % (
    sum(counts.values()), 100.0 * tot_amb_cites / max(1, sum(counts.values()))))
print()
print("   >>> D11 -- the one the Lead named:")
for k, c, nf in sorted(amb_rows, key=lambda x: -x[1])[:6]:
    print("      %-6s %5d citations spread over %d candidate documents" % (k, c, nf))
print()

# =====================================================================
# T4 -- defects repaired in PROSE
# =====================================================================
print("=" * 78)
print("T4 -- CITATION DEFECTS REPAIRED IN PROSE")
print("=" * 78)
PATTERNS = {
 "there_is_no":      re.compile(r"[Tt]here is no\s+(?:a\s+)?(?:§|section\s+)?§?\s*\d+(?:\.\d+)*"),
 "does_not_exist":   re.compile(r"§?\s*\d+(?:\.\d+)*\s+does not exist"),
 "contains_only":    re.compile(r"contains only\s+§?[\d.]+(?:[–\-—]§?[\d.]+)?"),
 "no_such_section":  re.compile(r"no such\s+(?:§|section)"),
 "never_written":    re.compile(r"never (?:written|existed)"),
 "only_runs_to":     re.compile(r"(?:only|runs|ends at)\s+§?\d+\.\d+\s*(?:[–\-—]|to)\s*§?\d+\.\d+"),
}
hits = collections.defaultdict(list)
for rel, t in docs.items():
    lines = t.split("\n")
    for i, l in enumerate(lines):
        for k, rx in PATTERNS.items():
            if rx.search(l):
                hits[k].append(dict(doc=rel, line=i + 1, text=l.strip()[:190]))
print("   MANDATORY distribution by pattern:")
for k in PATTERNS:
    print("      %-18s %4d" % (k, len(hits[k])))
print("      %-18s %4d  <- total occurrences" % ("TOTAL", sum(len(v) for v in hits.values())))
uniq = set()
for k, v in hits.items():
    for h in v:
        uniq.add((h["doc"], h["line"]))
print("      %-18s %4d  <- distinct (doc,line) sites" % ("DISTINCT", len(uniq)))
print()
print("   --- every 'there is no' / 'contains only' hit, with its document ---")
for k in ("there_is_no", "contains_only", "does_not_exist", "no_such_section"):
    for h in hits[k][:18]:
        print("      [%s] %s:%d" % (k, h["doc"][:40], h["line"]))
        print("            %s" % h["text"][:170])
print()

json.dump(dict(D11_ambiguous={k: fam[k] for k in multi},
               amb_cites=amb_rows, tot_amb_cites=tot_amb_cites,
               t4={k: v for k, v in hits.items()}),
          open(os.path.join(DEEP, "_d108_t4t5.json"), "w"), indent=1)
print("   wrote _d108_t4t5.json")
