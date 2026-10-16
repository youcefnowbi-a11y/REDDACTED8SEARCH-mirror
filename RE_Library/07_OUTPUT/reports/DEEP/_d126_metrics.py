import os, re, sys, hashlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
P = os.path.join(WS, r"RE_Library\07_OUTPUT\reports\DEEP",
    "D126_layer_pair_source_against_binary_the_other_17_stubs_nil_guard_reachability_and_the_name_table_carve_out_technique.md")

raw = open(P, "rb").read()
txt = raw.decode("utf-8", errors="strict")
print("SCOPE: %s" % os.path.basename(P))
print()
print("=== BYTE METRICS ===")
print("  bytes          : %d" % len(raw))
print("  LF             : %d" % raw.count(b"\n"))
print("  CR             : %d" % raw.count(b"\r"))
print("  CRLF           : %d" % raw.count(b"\r\n"))
print("  BOM            : %s" % ("PRESENT" if raw.startswith(b"\xef\xbb\xbf") else "none"))
print("  U+FFFD         : %d" % txt.count("\ufffd"))
print("  sha256         : %s" % hashlib.sha256(raw).hexdigest())
print("  lines          : %d" % len(txt.split("\n")))
print()

print("=== HEADING CENSUS (both bases stated) ===")
h16 = re.findall(r"(?m)^#{1,6} ", txt)
h2p = re.findall(r"(?m)^#{2,} ", txt)
print("  regex #{1,6}   : %d" % len(h16))
print("  regex #{2,}    : %d" % len(h2p))
print("  difference     : %d   (must equal H1 count)" % (len(h16) - len(h2p)))
h1 = len(re.findall(r"(?m)^# ", txt))
h2 = len(re.findall(r"(?m)^## ", txt))
h3 = len(re.findall(r"(?m)^### ", txt))
h4 = len(re.findall(r"(?m)^#### ", txt))
print("  H1             : %d" % h1)
print("  H2             : %d" % h2)
print("  H3             : %d" % h3)
print("  H4             : %d" % h4)
print("  sum H1..H4     : %d" % (h1 + h2 + h3 + h4))
print("  closure ok     : %s" % (h1 + h2 + h3 + h4 == len(h16)))
print()

print("=== WHOLE-LINE DUPLICATION (excluding blank + table separators) ===")
lines = [l.rstrip() for l in txt.split("\n")]
def excl(l):
    s = l.strip()
    if not s:
        return True
    if re.match(r"^\|[\s|:\-]+\|$", s):
        return True
    return False
body = [l for l in lines if not excl(l)]
from collections import Counter
c = Counter(body)
dups = {k: v for k, v in c.items() if v > 1}
print("  non-excluded lines     : %d" % len(body))
print("  distinct               : %d" % len(c))
print("  whole-line duplicates  : %d" % len(dups))
for k, v in list(dups.items())[:8]:
    print("     x%d  %s" % (v, k[:96]))
print()

print("=== CODEPOINT PROBE OVER EVERY BRACKETED TOKEN ===")
toks = re.findall(r"\[([^\]\n]{1,80})\]", txt)
bad = [t for t in toks if any(ord(ch) > 127 for ch in t)]
print("  bracketed tokens       : %d" % len(toks))
print("  with non-ASCII         : %d" % len(bad))
for t in bad[:10]:
    print("     %r" % t)
print("  whole-file non-ASCII   : %d" % sum(1 for ch in txt if ord(ch) > 127))
nz = sorted(set(ch for ch in txt if ord(ch) > 127))
print("  distinct non-ASCII cp  : %s" % " ".join("U+%04X(%s)" % (ord(ch), ch) for ch in nz))
print()

print("=== BTICK NET (code-fence parity) ===")
fence = len(re.findall(r"(?m)^```", txt))
inline = len(re.findall(r"`[^`\n]+`", txt))
print("  fence lines (^```)     : %d   odd => %s" % (fence, "UNBALANCED" if fence % 2 else "balanced"))
print("  inline spans           : %d" % inline)
print()

print("=== TAG DISCIPLINE ===")
for tag in ["[source]", "[binary]", "[measured]", "[inferred]", "[absence]", "[instrument]", "[verified]", "[read]"]:
    print("  %-14s %d" % (tag, txt.count(tag)))
