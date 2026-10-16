"""
D118 probe 5 -- T5 (self-caught vs cross-caught corrections) + T6 (resolver re-run
over the D103-D117 round).

T5: the Lead wants the ratio that measures whether the discipline is working:
    how many reports carry a correction they made to THEMSELVES, vs a
    correction-to-a-prior-report. 33 instrument shapes are filed; how many were
    self-caught?

T6: re-run the D108 file-candidate resolver over everything landed since D108:
    D103, D104, D105, D106, D107, D110, D111, D113, D114, D115.
    Report new candidates, new misses, and any miss that is NOT a probe defect
    and NOT the report being correct. That category is the only one that matters.
"""
import os, re, sys, json, glob, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
REPORTS = os.path.join(WS, "RE_Library", "07_OUTPUT", "reports")
DEEP = os.path.join(REPORTS, "DEEP")

# =====================================================================
# T5 -- SELF-CAUGHT vs CROSS-CAUGHT
# =====================================================================
print("=" * 78)
print("T5 -- SELF-CAUGHT vs CROSS-CAUGHT CORRECTIONS")
print("=" * 78)
SELF = [
 ("a first draft",            r"a first draft"),
 ("my first draft",           r"my first draft"),
 ("this report's first",      r"this report'?s first"),
 ("my own error",             r"my own (?:error|mistake|defect)"),
 ("I was wrong",              r"\bI was wrong\b"),
 ("I had it wrong",           r"\bI (?:had|got) it wrong\b"),
 ("I initially",              r"\bI initially\b"),
 ("this report initially",    r"this report initially"),
 ("I accused",                r"\bI accused\b"),
 ("corrected in this report", r"correct(?:ed|ion) (?:in|to) this report"),
 ("self-caught",              r"self-?caught"),
 ("my instrument",            r"my (?:own )?instrument"),
 ("this probe",               r"this probe'?s? (?:was|were|is) (?:wrong|broken)"),
 ("RETRACTED",                r"\bRETRACT"),
]
CROSS = [
 ("correcting D94",           r"correct(?:ion|s)? to D94"),
 ("D99 found",                r"D99 (?:found|caught|caught)"),
 ("as D99",                   r"as D99\b"),
 ("correction to",            r"correction to (?:the )?(?:prior|previous|D\d+)"),
 ("contradicts",              r"contradicts D\d+"),
 ("refutes",                  r"refutes? (?:the )?(?:prior|D\d+)"),
]

docs = {}
for dp, ds, fs in os.walk(REPORTS):
    if "\\extractions\\" in dp:
        continue
    for f in fs:
        if f.endswith(".md") and not f.startswith("D118_"):
            docs[f] = open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read()

print("   population: %d .md documents" % len(docs))
print()
print("   --- SELF-caught signals, by document ---")
selfhit = collections.defaultdict(set)
for name, rx in SELF:
    r = re.compile(rx, re.I)
    for d, t in docs.items():
        n = len(r.findall(t))
        if n:
            selfhit[d].add((name, n))
print("   MANDATORY distribution: documents carrying >=1 SELF-caught signal: %d" % len(selfhit))
for d in sorted(selfhit):
    sigs = ", ".join("%s x%d" % (k, v) for k, v in sorted(selfhit[d]))
    print("      %-58s %s" % (d[:58], sigs))
print()
print("   --- CROSS-caught signals, by document ---")
crosshit = collections.defaultdict(set)
for name, rx in CROSS:
    r = re.compile(rx, re.I)
    for d, t in docs.items():
        n = len(r.findall(t))
        if n:
            crosshit[d].add((name, n))
print("   MANDATORY distribution: documents carrying >=1 CROSS-caught signal: %d" % len(crosshit))
for d in sorted(crosshit):
    sigs = ", ".join("%s x%d" % (k, v) for k, v in sorted(crosshit[d]))
    print("      %-58s %s" % (d[:58], sigs))
print()
both = set(selfhit) & set(crosshit)
onlyself = set(selfhit) - set(crosshit)
onlycross = set(crosshit) - set(selfhit)
print("   SELF only      : %d" % len(onlyself))
print("   CROSS only     : %d" % len(onlycross))
print("   BOTH           : %d" % len(both))
print("   ratio self:cross (documents) = %.2f" % (len(selfhit) / max(1, len(crosshit))))
print()

# =====================================================================
# T6 -- resolver re-run over the post-D108 round
# =====================================================================
print("=" * 78)
print("T6 -- FILE-CANDIDATE RESOLVER OVER THE POST-D108 ROUND")
print("=" * 78)
NEW = ["D103_sliver_client_operational_surface_dead_stubs_and_ghidra_census_la.md",
 "D104_android_aab_apk_manifest_three_way_diff_dex_class_census_and_secr.md",
 "D105_havoc_agent_wire_envelope_sleep_surface_and_pivots_synchronisatio.md",
 "D106_android_apk_aab_reentry_census_manifest_attributes_and_screenshot.md",
 "D107_inferred_refutation_sweep_third_party_and_bcl_contracts_by_execut.md",
 "D110_merlin_artifact_census_shared_build_configuration_and_static_boun.md",
 "D111_havoc_service_agent_registry_gate_discriminant_split_and_line_com.md",
 "D113_android_exported_attribute_byte_level_reconciliation_sdk_floor_an.md",
 "D114_android_exported_byte_contradiction_resolved_decoder_acceptance_c.md",
 "D115_havoc_preprocessor_exclusion_census_and_the_out_of_tree_definer.m.md"]
# resolve by prefix, because the truncated names above are illustrative
def find(prefix):
    for f in os.listdir(DEEP):
        if f.startswith(prefix):
            return f
    return None
targets = []
for pre in ["D103_", "D104_", "D105_", "D106_", "D107_", "D110_", "D111_", "D113_", "D114_", "D115_"]:
    f = find(pre)
    if f:
        targets.append(f)
print("   reports resolved on disk: %d" % len(targets))
for t in targets:
    print("      %s" % t[:74])
print()

FILEEXT = {"py","ps1","json","tsv","csv","md","dll","exe","txt","xml","cs","go","rb","java","so","bin","log","yml","yaml","toml","cfg","ini","js","ts","c","h","cpp","sln","csproj"}
NOTFILE = re.compile(r"^(?:[a-z_]+\.[a-z_]+[A-Z]|.*\(|.*\)|.*\[|.*\]|.*\$|.*==|.*!=|.*\.\w+\.\w+$)")

cand = []
for t in targets:
    txt = open(os.path.join(DEEP, t), encoding="utf-8", errors="ignore").read()
    for i, l in enumerate(txt.split("\n")):
        for m in re.finditer(r"`([^`\n]{3,110})`", l):
            tok = m.group(1).strip()
            ext = tok.rsplit(".", 1)[-1].lower() if "." in tok else ""
            if ext not in FILEEXT:
                continue
            if tok.count(".") > 2 and "\\" not in tok and "/" not in tok:
                continue
            if re.match(r"^[a-z_][\w]*\.[\w]+$", tok) and tok.split(".")[0].islower() and "." in tok and tok.split(".")[1][:1].isupper():
                continue   # dotted symbol, e.g. structs.Map
            cand.append(dict(report=t, line=i + 1, token=tok,
                             tag=bool(re.search(r"\[(verified|read|measured|instrument|absence|inferred)\]", l))))

def locate(tok):
    if "\\" in tok or "/" in tok:
        for base in (DEEP, REPORTS, os.path.join(WS, "RE_Library"), WS):
            p = os.path.join(base, tok.replace("/", os.sep))
            if os.path.exists(p):
                return p
        return None
    for base in (DEEP, REPORTS, os.path.join(WS, "RE_Library"), WS):
        for dp, ds, fs in os.walk(base):
            if tok in fs:
                return os.path.join(dp, tok)
    return None

print("   MANDATORY distribution by report:")
rep = collections.Counter(c["report"] for c in cand)
for r, c in rep.most_common():
    print("      %-60s %3d candidates" % (r[:60], c))
print()
print("   candidates total : %d" % len(cand))
found = [c for c in cand if locate(c["token"])]
miss = [c for c in cand if not locate(c["token"])]
print("   FOUND            : %d" % len(found))
print("   NOT FOUND        : %d" % len(miss))
print()
print("   --- EVERY not-found candidate (the T6 hazard list) ---")
for c in miss:
    print("      %s:%d  tags=%s  `%s`" % (c["report"][:34], c["line"],
          "y" if c["tag"] else "-", c["token"][:62]))
print()
json.dump(dict(self=dict((k, list(v)) for k, v in selfhit.items()),
               cross=dict((k, list(v)) for k, v in crosshit.items()),
               cand=len(cand), found=len(found), miss=miss),
          open(os.path.join(DEEP, "_d118_t5t6.json"), "w"), indent=1)
print("wrote _d118_t5t6.json")
