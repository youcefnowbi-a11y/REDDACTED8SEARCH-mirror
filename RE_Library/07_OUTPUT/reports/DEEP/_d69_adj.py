import os, re, collections

root = r"RE_Library\01_SOURCE_c2\metasploit"

# Adjudicate: the OLD probe required `.name` or `:name`. This probe asks the
# distinguishing question directly, for the pairs where the two methods disagree.
#   BARE CALL:    name(            e.g. `rm_rf(x)`, `key?(y)` -- idiomatically bare
#                 inside the owning class
#   DOT CALL:     .name            e.g. `session.client`
#   SYMBOL:       :name
targets = [
    ("post/file.rb", 118, "ls", "dir"),
    ("post/file.rb", 216, "file_exist?", "file?"),
    ("post/file.rb", 328, "exists?", "exist?"),
    ("post/file.rb", 682, "mv_file", "rename_file"),
    ("post/file.rb", 709, "cp_file", "copy_file"),
    ("post/windows/file_system.rb", 250, "delete_junction", "delete_mount_point"),
    ("data_store.rb", 251, "include?", "key?"),
    ("data_store.rb", 364, "update", "merge!"),
    ("rhosts_walker.rb", 268, "parse_https_uri", "parse_http_uri"),
    ("exe/segment_appender.rb", 25, "secname=", "section_name="),
    ("exploit/file_dropper.rb", 63, "register_file_for_cleanup", "register_files_for_cleanup"),
    ("exploit/remote/ftp.rb", 604, "ftp_connect", "connect"),
    ("exploit/remote/dns/enumeration.rb", 27, "dns_query", "query"),
]

corpus = {}
for dp, ds, fs in os.walk(root):
    if ".git" in dp:
        continue
    for f in fs:
        if f.endswith(".rb"):
            p = os.path.join(dp, f)
            corpus[os.path.relpath(p, root)] = open(p, encoding="utf-8", errors="ignore").read()

def counts(name):
    bare = dot = sym = 0
    for rel, t in corpus.items():
        bare += len(re.findall(r"(?<![\w:.$@])" + re.escape(name) + r"\s*[(=]", t))
        dot += len(re.findall(r"\.\s*" + re.escape(name) + r"\b", t))
        sym += len(re.findall(r"(?<![:\w]):" + re.escape(name) + r"\b", t))
    return bare, dot, sym

print("%-46s %-26s %-22s %s" % ("file:line", "alias -> target", "ALIAS bare/dot/sym", "TARGET bare/dot/sym"))
print("-" * 130)
for rel, ln, new, old in targets:
    nb, nd, ns = counts(new)
    ob, od, os_ = counts(old)
    # subtract the alias declaration line itself from the alias bare count where relevant
    print("%-46s %-26s %-22s %s" % (
        "%s:%d" % (rel, ln), "%s -> %s" % (new, old),
        "%d / %d / %d" % (nb, nd, ns), "%d / %d / %d" % (ob, od, os_)))

print()
print("=== TOTAL call sites (bare + dot + symbol), minus 1 for the declaring alias ===")
still_dead = []
for rel, ln, new, old in targets:
    nb, nd, ns = counts(new)
    total = nb + nd + ns - 1
    status = "DEAD" if total <= 0 else "LIVE (%d)" % total
    if total <= 0:
        still_dead.append((rel, ln, new, old))
    print("   %-46s %-30s %s" % ("%s:%d" % (rel, ln), "%s -> %s" % (new, old), status))
print()
print("still dead under BOTH methods:", len(still_dead))
for r in still_dead:
    print("      %s:%d  %s -> %s" % r)
