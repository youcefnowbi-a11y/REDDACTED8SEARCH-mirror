"""
D85 probe 5 -- THE ESCAPING TEST, applied to ALL 131 sites (not just the 49).

Why all 131: cups_root_file_read.rb:60 `cmd_exec("groups #{[user].shelljoin}")`
is ESCAPED, and its class is SESSION_TARGET. So a 49-only census would report
"0 escaped" while an escaped operator-data-adjacent site sits one class over.
Rule 20 again, at the class level: the population I know about is not the
population that matters.

The primitive set is the corpus-derived family from probe 3, minus the ones the
control showed are NOT shell escaping:
  IN  : shellescape, shelljoin, Shellwords.escape, gsub(' -> \\'), gsub(" -> \"),
        Rex::Text.encode_base64 (alphabet excludes metachars)
  OUT : .encode('UTF-16LE'/...), .inspect, .dump, CGI.escape/URI.encode (0 occ),
        decode_base64 (a DECODER, not an escaper)
"""
import os, re, json, collections

HERE = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\reports\DEEP"
ROOT = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\01_SOURCE_c2\metasploit"

sites = json.load(open(os.path.join(HERE, "_d85_sites.json")))
print("population:", len(sites))

# ESCAPING primitives that can actually defeat shell metacharacter interpretation.
ESCAPERS = [
    ("shellescape",       re.compile(r"\.shellescape\b")),
    ("shelljoin",         re.compile(r"\.shelljoin\b")),
    ("Shellwords.escape", re.compile(r"Shellwords\.escape\b")),
    ("Shellwords.split",  re.compile(r"Shellwords\.split\b")),
    ("gsub_squote",       re.compile(r"\.gsub\(\s*['\"]['\"]")),
    ("gsub_dquote",       re.compile(r"\.gsub\(\s*['\"]\\\"['\"]")),
    ("b64_encode",        re.compile(r"Rex::Text\.encode_base64")),
]
# NON-escaping things a naive probe would count. Kept to show the exclusion.
NONESCAPERS = [
    ("char_encode",       re.compile(r"\.encode\(\s*['\"]UTF")),
    ("inspect",           re.compile(r"\.inspect\b")),
    ("b64_decode",        re.compile(r"Rex::Text\.decode_base64")),
]

print()
print("=== distribution over the population (MANDATORY) ===")
for k, v in collections.Counter(s["cls"] for s in sites).most_common():
    print("   %-24s %4d" % (k, v))
print()

rows = []
for s in sites:
    combined = " ".join(s["args"])
    hits = [name for name, rx in ESCAPERS if rx.search(combined)]
    nhits = [name for name, rx in NONESCAPERS if rx.search(combined)]
    verdict = "ESCAPED" if hits else ("RAW" if not nhits else "NONESCAPER_ONLY")
    rows.append(dict(s, esc=hits, nonesc=nhits, verdict=verdict))

print("=== ESCAPING TEST over all %d sites ===" % len(rows))
for k, v in collections.Counter(r["verdict"] for r in rows).most_common():
    print("   %-18s %4d" % (k, v))
print()
print("=== cross-tab: class x verdict ===")
tab = collections.defaultdict(collections.Counter)
for r in rows:
    tab[r["cls"]][r["verdict"]] += 1
for cls in sorted(tab):
    print("   %-24s %s" % (cls, dict(tab[cls])))
print()
print("=== EVERY ESCAPED SITE, with its primitive ===")
esc = [r for r in rows if r["verdict"] == "ESCAPED"]
print("   count:", len(esc))
for r in esc:
    print("   %s:%d  [%s]  prim=%s" % (r["file"], r["line"], r["cls"], ",".join(r["esc"])))
    print("        %s" % r["cmd"][:118])
print()
print("=== NONESCAPER_ONLY sites (naive probe would have called these escaped) ===")
for r in rows:
    if r["verdict"] == "NONESCAPER_ONLY":
        print("   %s:%d  [%s]  nonesc=%s" % (r["file"], r["line"], r["cls"], ",".join(r["nonesc"])))
        print("        %s" % r["cmd"][:118])
print()

# The headline: operator data reaching a shell UNESCAPED
print("=== HEADLINE BASIS ===")
def count(cls, verdict):
    return sum(1 for r in rows if r["cls"] == cls and r["verdict"] == verdict)
for cls in ["DATASTORE", "SESSION_TARGET", "MIXIN_HELPER", "HARDCODED",
            "LOCAL_TOOL_PATH", "METHOD_BODY_UNRESOLVED", "UNRESOLVABLE"]:
    print("   %-24s ESCAPED %2d   RAW %2d   NONESCAPER_ONLY %2d" %
          (cls, count(cls, "ESCAPED"), count(cls, "RAW"), count(cls, "NONESCAPER_ONLY")))
json.dump(rows, open(os.path.join(HERE, "_d85_esc.json"), "w"), indent=1)
