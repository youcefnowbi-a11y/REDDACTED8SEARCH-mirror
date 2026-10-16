"""D74 probe 4 -- diagnose the UNRESOLVABLE inflation. Is find_assign blind?"""
import os, re

ROOT = r"RE_Library\01_SOURCE_c2\metasploit"
POST = os.path.join(ROOT, "modules", "post")

# CONTROL 1: the known assignment `puppet_exe = ...` in linux/gather/puppet.rb
p = os.path.join(POST, "linux", "gather", "puppet.rb")
t = open(p, encoding="utf-8", errors="ignore").read()
print("=== CONTROL: linux/gather/puppet.rb, every 'puppet_exe' line ===")
for i, l in enumerate(t.split("\n"), 1):
    if "puppet_exe" in l:
        print("   L%-4d %s" % (i, l.strip()[:110]))
print()

# CONTROL 2: does the lookbehind (?<![\w.@$]) block '@' assignments?
IV = re.compile(r"(?<![\w.@$])@writeable_folder\s*(\|\|=|=)(?!=|>)")
IV2 = re.compile(r"(?<![\w.@$.])@writeable_folder\s*(\|\|=|=)(?!=|>)")
p2 = os.path.join(POST, "linux", "dos", "xen_420_dos.rb")
t2 = open(p2, encoding="utf-8", errors="ignore").read()
print("=== CONTROL: xen_420_dos.rb '@writeable_folder' lines ===")
for i, l in enumerate(t2.split("\n"), 1):
    if "@writeable_folder" in l:
        print("   L%-4d %s" % (i, l.strip()[:110]))
print("   lookbehind (?<![\\w.@$]) matches:", len(IV.findall(t2)))
print("   lookbehind (?<![\\w.@$.]) matches:", len(IV2.findall(t2)))
print()

# CONTROL 3: how many of the 131 unresolved names are ivars vs locals?
UNRES = ["dbus_session", "url", "interface", "tmp_path", "code", "path", "ip",
         "writable_directory", "pvalue", "ansible_inventory", "hostname",
         "puppet_exe", "facter_exe", "file", "c", "ldapsearch_bin"]
print("=== where is each unresolved name actually assigned, tree-wide? ===")
blob = {}
for dp, ds, fs in os.walk(POST):
    for f in fs:
        if f.endswith(".rb"):
            fp = os.path.join(dp, f)
            blob[os.path.relpath(fp, ROOT)] = open(fp, encoding="utf-8", errors="ignore").read()
for name in ["puppet_exe", "facter_exe", "pvalue", "ansible_inventory", "tmp_path"]:
    pat = re.compile(r"(?<![\w.@$])" + re.escape(name) + r"\s*(\|\|=|=)(?!=|>)")
    hits = []
    for rel, tx in blob.items():
        for m in pat.finditer(tx):
            ln = tx[:m.start()].count("\n") + 1
            eol = tx.find("\n", m.start())
            hits.append("%s:%d  %s" % (rel, ln, tx[m.start():eol][:95]))
    print("--- %s: %d assignments ---" % (name, len(hits)))
    for h in hits[:6]:
        print("      %s" % h)
print()
print("=== are they defined via `attr_accessor` / method def / datastore accessor? ===")
for name in ["puppet_exe", "facter_exe", "pvalue"]:
    for rx, label in [(r"attr_(reader|accessor|writer)\s*:?" + re.escape(name), "attr_"),
                      (r"def\s+" + re.escape(name) + r"\b", "def"),
                      (r"register_advanced_options|OptString|OptPath", "option-decl")]:
        n = sum(len(re.findall(rx, tx)) for tx in blob.values())
        if n:
            print("   %-16s %-12s %d" % (name, label, n))
print()
print("=== 'pvalue' definition hunt (grandstream modules) ===")
for rel, tx in blob.items():
    if "pvalue" in tx and "grandstream" in rel:
        for i, l in enumerate(tx.split("\n"), 1):
            if "pvalue" in l and ("=" in l or "def " in l):
                print("   %s:%d  %s" % (rel, i, l.strip()[:110]))
