"""
D108 probe 1 -- T1: EVERY HARD ARTIFACT CITATION IN THE NEW ROUND.

D94 fabricated two artifact locations (crossref_v7.ps1, _INSTRUMENT_RULE_26_*).
D99 found both. The new reports were written by lanes that had read D99.

This probe extracts every place a new report HARD-CITES a file on disk, and
records enough context to test three things independently:
   1. does the path exist
   2. is the stated size correct
   3. does the quoted line say what the report says it says  (READ, later)

A citation is "hard" when it names a path with an extension, or names a
path-like token in a tag context. Prose mentions of documents are captured too
but FLAGGED separately, because D94's failure was a PROSE location, not a
quoted path.

Comment-membership discipline: a citation inside a fenced block or a comment
line is recorded with its context kind so it can be judged, not silently kept.
"""
import os, re, sys, json, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
DEEP = os.path.join(WS, "RE_Library", "07_OUTPUT", "reports", "DEEP")

NEW = ["D95_merlin_binary_layer_agent_build_delta_cgo_export_stubs_and_extraction_path_census.md",
       "D96_sliver_client_server_absence_and_pclntab_census.md",
       "D97_android_wasm_assembler_sqlite_vfs_and_jvm_tooling.md",
       "D98_havoc_tomap_serialization_boundary_callers_and_concurrency_surface.md",
       "D100_android_binary_layer_manifest_dex_signing_and_native_census.md",
       "D101_covenant_binary_source_pair_negative_result_and_empirical_closures.md",
       "D102_meterpreter_tlv_wire_constants_handler_payload_contract_and_d90_u1_closure.md",
       "C-09_correction_to_d94_two_fabricated_artifact_locations_and_unclosed_arithmetic.md",
       "C-10_binary_layer_seven_targets_named_functions_one_signature_and_pclntab_substitution.md"]

# a path-like token: has an extension we recognise, or a backslash path
PATHTOK = re.compile(
    r"`([^`\n]{2,200}?(?:\.[A-Za-z0-9]{1,8}))`"          # in backticks, with extension
    r"|(?<![\w`])([A-Za-z]:\\[^\s`\"'|,;)\]]+)"           # absolute windows path
    r"|(?<![\w`])((?:[\w.\-]+\\\\)+[\w.\-]+\.[A-Za-z0-9]{1,8})"  # relative path w/ ext
)
SIZE = re.compile(r"([\d,]{1,12})\s*(?:B|bytes)\b")
TAG  = re.compile(r"\[(verified|read)\]")

rows = []
for name in NEW:
    p = os.path.join(DEEP, name)
    if not os.path.exists(p):
        print("MISSING REPORT:", name)
        continue
    txt = open(p, encoding="utf-8", errors="ignore").read()
    lines = txt.split("\n")
    in_fence = False
    for i, l in enumerate(lines):
        if l.strip().startswith("```"):
            in_fence = not in_fence
            continue
        # strip markdown comments/html comments as context markers
        ctx = "fence" if in_fence else "text"
        for m in PATHTOK.finditer(l):
            tok = next((g for g in m.groups() if g), None)
            if not tok:
                continue
            tok = tok.strip()
            rows.append(dict(report=name, line=i + 1, token=tok, ctx=ctx,
                             text=l.strip()[:200],
                             tag=",".join(x.group(1) for x in TAG.finditer(l))))

print("=== T1: HARD ARTIFACT CITATIONS IN THE NEW ROUND ===")
print("   reports scanned :", len(NEW))
print("   total path-tokens:", len(rows))
print()
print("   MANDATORY distribution by citing report:")
for k, v in collections.Counter(r["report"] for r in rows).most_common():
    print("      %-58s %4d" % (k[:58], v))
print()
print("   MANDATORY distribution by context (fence vs running text):")
for k, v in collections.Counter(r["ctx"] for r in rows).most_common():
    print("      %-10s %4d" % (k, v))
print()

# ---- RESOLUTION: try to locate each token on disk
def locate(tok):
    t = tok.strip().strip("`")
    # 1 exact relative to DEEP
    for base in (DEEP, WS, os.path.join(WS, "RE_Library", "07_OUTPUT")):
        cand = os.path.join(base, t)
        if os.path.exists(cand):
            return cand
    # 2 basename search under RE_Library
    b = os.path.basename(t.replace("\\", "/"))
    if b and "." in b:
        root = os.path.join(WS, "RE_Library")
        for dp, ds, fs in os.walk(root):
            if b in fs:
                return os.path.join(dp, b)
    return None

for r in rows:
    r["found"] = locate(r["token"])
    r["exists"] = bool(r["found"])

resolved = [r for r in rows if r["exists"]]
unres = [r for r in rows if not r["exists"]]
print("=== RESOLUTION ===")
print("   exists  :", len(resolved))
print("   NOT FOUND:", len(unres))
print()
print("   MANDATORY distribution of NOT-FOUND by token SHAPE (is it a real path or prose?):")
shape = collections.Counter()
for r in unres:
    t = r["token"]
    if re.search(r"\.[A-Za-z0-9]{1,8}$", t) and ("\\" in t or "/" in t):
        shape["path-shaped (\\ or /)"] += 1
    elif re.search(r"\.(md|py|ps1|json|csv|tsv|go|cs|rs|c|cpp|h|rb|java|smali|wasm|so|dll|exe|bin)$", t):
        shape["bare filename (no dir)"] += 1
    else:
        shape["other"] += 1
for k, v in shape.most_common():
    print("      %-30s %4d" % (k, v))
print()

print("=== THE UNRESOLVED SET, listed (these are T1's candidates) ===")
for r in unres[:120]:
    print("   %-14s :%-5d  tags=%-11s  `%s`" % (r["report"][:14], r["line"], r["tag"] or "-", r["token"][:90]))
print()
if len(unres) > 120:
    print("   ... %d more" % (len(unres) - 120))

json.dump(rows, open(os.path.join(DEEP, "_d108_p1_cites.json"), "w"), indent=1)
print("   wrote _d108_p1_cites.json (%d rows)" % len(rows))
