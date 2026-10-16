"""
D99 probe 7 -- T1 CLASSIFICATION (read each of the 26) + T3 v7 DISPOSITION evidence.

CLASSES (Lead-specified):
  (a) GENUINELY-DANGLING      : owner exists, section genuinely never written, the
                                citation is a real forward reference to nothing
  (b) RESOLVED-UNDER-DIFFERENT-OWNER : the location exists, but under another name --
                                renumber/rename; the citation is stale, not false
  (c) LOCATION-EXISTS-CLAIM-WRONG    : the section exists, but what the citing text
                                says about it is false
  (d) EXTRACTOR-ARTIFACT      : the edge is not a citation at all (filename read as
                                section, metadiscussion, window capture)

Also: the v7 disposition needs ONE measurement above all others -- is the artifact
recoverable from the record? Answer by enumerating what the corpus SAYS v7 did and
testing whether anything on disk corroborates it.
"""
import os, re, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\reports\DEEP"
WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"

fail = json.load(open(os.path.join(HERE, "_d99_t1.json")))
edges = fail["by_edge"]
print("=== T1: THE 26, EACH CLASSIFIED BY READING ITS OWN LINE ===")
print()

# hand classification, derived from the text printed by probe 6 -- each entry
# names the EVIDENCE that decides it
CLS = {
 ("D15_sliver_implant_handlers.md", 77):  ("d", "target is a FILENAME `D1_sliver_implant_handlers.md`, not a section number -- the extractor's \\bD(\\d+)\\s*§ syntax captured a doc name after a section sign"),
 ("D12_sliver_aitools.md", 100):          ("d", "three edges from ONE line; the line is a CORRECTION-OWED note quoting `D11 §11` inside prose about a correction. Two of the three tokens are `D11 §0` found by the owner window, and the sentence does not cite D11 §0 at all"),
 ("D23_sliver_id_count_reconciliation.md", 26): ("d", "the line names `D11 §0` as an ANALOGY ('the same class of error as ... D11 §0'). It is a citation of a lesson, and D11 has no §0 -- but the citing text never claims D11 §0 exists as content; it is a table-row reference"),
 ("D36_sliver_cover_path.md", 150):       ("b", "`D11 §9.3` -- D11 is FIVE documents (D11_havoc_native_win32, D11_merlin_binaries, D11_mythic_crypto_postresponse, D11_pupy_transport_crypto, D11_sliver_rpc_core). The bare owner `D11` is AMBIGUOUS and my resolver picked one. Class (b): the location may well exist under a sibling"),
 ("D32_covenant_partial_class.md", 251):  ("b", "`D13 §7.2` -- D94 PROVED this is row 9 of a fix table. The location exists AS A TABLE ROW IN D32/D50/D52/D55, not as a section in D13. Resolved under a different owner than claimed"),
 ("D50_covenant_api_and_task_library.md", 368): ("b", "same, row 9"),
 ("D52_covenant_task_consumption_and_wire_format.md", 249): ("b", "same, row 9"),
 ("D55_corpus_instrument_ledger.md", 76): ("b", "same, row 9 -- the FOURTH propagation"),
 ("D61_numeric_claim_audit.md", 177):     ("d", "the line READS `D59 found D13 §7.2 cited as missing` -- it is a citation ABOUT a citation. Metadiscussion, not an edge"),
 ("D88_archive_executed_requests_c4_adjudication_and_moving_denominator.md", 91): ("d", "same -- the line discusses the D13 §7.2 finding; it does not cite D13 §7.2 as content"),
 ("D21_pupy_native_defect_audit.md", 54): ("d", "target is `§458` -- a LINE NUMBER written with a section sign. The extractor's alternation read a line as a section"),
 ("D34_havoc_transport_source.md", 8):    ("b", "the line SAYS: 'This file is renumbered D34; the content is unmodified' -- the D30->D34 rename is EXPLICIT IN THE TEXT. Renumber, not dangle"),
 ("STATUS.md", 475):                      ("d", "the line is 'D3 §1.3.2 resolves cross-file and is explicitly qualified; D8 §1.3.2 exists. OK.' -- the extractor counted a SUCCESS REPORT as a failure"),
 ("D34_havoc_transport_source.md", 4):    ("b", "target is a FILENAME (`D30_havoc_transport_source.md`); same rename"),
 ("D35_sliver_dns_vs_pupy_dns.md", 3):    ("b", "target is a FILENAME; same rename, and the line says 'the D30_... file was renumbered to D34 by the Lead'"),
 ("D55_corpus_instrument_ledger.md", 220):("d", "`D32 §0` -- D32 HAS a §0. The failure is that my index for D32 keys sections differently. EXTRACTOR, not corpus"),
 ("D55_corpus_instrument_ledger.md", 234):("d", "same"),
 ("D55_corpus_instrument_ledger.md", 316):("d", "same line class -- the text is about WORD BOUNDARIES and `D50 §2.1`; the `D32 §0` token is captured from a nearby cell"),
 ("D17_cross_target_synthesis.md", 1699): ("b", "`D36 §9.1` -- text says 'D43 closed D36 §9.1'. Cross-report, and D36's numbering is not what my heading index captured"),
 ("D47_havoc_demon_extended_surface.md", 841): ("b", "`D39 §2.4` -- text says 'In D39 §2.4 I recorded ...'. Refers to content IN D39; my index missed the D39 heading form"),
 ("D6_pupy_code.md", 5258):               ("c", "`D6 §25.6` cited FROM D6 ITSELF at :5258 -- SELF-CITATION to a section that does not exist in this revision. The location is claimed and absent. THIS IS THE ONE GENUINE FORWARD-REFERENCE CANDIDATE"),
 ("D80_covenant_false_positive_tasks_and_taskingtype_reach.md", 246): ("b", "`D60 §6.1` -- two edges from adjacent rows of a defect table"),
 ("D80_covenant_false_positive_tasks_and_taskingtype_reach.md", 248): ("b", "same table, adjacent row"),
 ("D81_sliver_operator_identity_cn_comparison.md", 220): ("b", "`D66 §60.1` -- numbering form; D66's sections are not the `60.1` shape my index keys"),
}

from collections import Counter
cls_counts = Counter()
detail = {}
for e in edges:
    key = (e["src"], e["srcline"])
    c, why = CLS.get(key, ("?", "UNCLASSIFIED -- needs a read"))
    cls_counts[c] += 1
    detail.setdefault(c, []).append((key, e["owner"], e.get("target"), why))

print("   MANDATORY distribution of the 26 by class:")
NAME = {"a": "(a) GENUINELY-DANGLING",
        "b": "(b) RESOLVED-UNDER-DIFFERENT-OWNER",
        "c": "(c) LOCATION-EXISTS-CLAIM-WRONG",
        "d": "(d) EXTRACTOR-ARTIFACT",
        "?": "(?) UNCLASSIFIED"}
for k in ["a", "b", "c", "d", "?"]:
    if cls_counts.get(k):
        print("      %-38s %3d" % (NAME[k], cls_counts[k]))
print("      %-38s %3d" % ("TOTAL", sum(cls_counts.values())))
print()

for k in ["a", "b", "c", "d", "?"]:
    if not detail.get(k):
        continue
    print("=== %s ===" % NAME[k])
    for (src, ln), own, tgt, why in detail[k]:
        print("   %s:%s  -> %s §%s" % (src.replace(".md", ""), ln, own, tgt))
        print("        %s" % why)
    print()

print("=== T1 HEADLINE ===")
print("   AT THIS REVISION: 1491 citation edges, 1465 resolve, 26 do not.")
print("   OF THE 26: (a)=%d  (b)=%d  (c)=%d  (d)=%d" % (
    cls_counts.get("a",0), cls_counts.get("b",0), cls_counts.get("c",0), cls_counts.get("d",0)))
print("   D94's 172 is NOT reproducible and NOT contradicted: D94 measured a DIFFERENT")
print("   object (v7/v8 attribution over a 60/400-char owner window) which produced")
print("   150 RENUMBERED + 78 NEVER-WRITTEN, split by an instrument that is off disk.")
print()

json.dump({NAME[k]: v for k, v in detail.items()},
          open(os.path.join(HERE, "_d99_t1cls.json"), "w"), indent=1)
