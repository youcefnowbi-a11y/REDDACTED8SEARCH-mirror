import os, re, sys, hashlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
P = os.path.join(WS, r"RE_Library\07_OUTPUT\reports\DEEP",
 "D131_closing_the_open_residuals_D85_D94_ToMap_callers_and_concurrency_OwnershipFilter_census_reconciliation_FromJson_unprotected_path_null_Author_startup_abort_and_unstable_denominators.md")

raw = open(P, "rb").read()
txt = raw.decode("utf-8", errors="strict")
print("SCOPE: %s" % os.path.basename(P))
print()
print("=== BYTE METRICS ===")
print("  bytes      : %d" % len(raw))
print("  LF         : %d" % raw.count(b"\n"))
print("  CR         : %d" % raw.count(b"\r"))
print("  CRLF       : %d" % raw.count(b"\r\n"))
print("  BOM        : %s" % ("PRESENT" if raw.startswith(b"\xef\xbb\xbf") else "none"))
print("  U+FFFD     : %d" % txt.count("\ufffd"))
print("  sha256     : %s" % hashlib.sha256(raw).hexdigest())
print()
print("=== HEADINGS, both bases stated + closure ===")
h16 = re.findall(r"(?m)^#{1,6} ", txt)
h2p = re.findall(r"(?m)^#{2,} ", txt)
h1 = len(re.findall(r"(?m)^# ", txt))
h2 = len(re.findall(r"(?m)^## ", txt))
h3 = len(re.findall(r"(?m)^### ", txt))
h4 = len(re.findall(r"(?m)^#### ", txt))
print("  #{1,6}     : %d" % len(h16))
print("  #{2,}      : %d" % len(h2p))
print("  difference : %d   (must equal H1=%d)  -> %s" % (len(h16)-len(h2p), h1, "OK" if len(h16)-len(h2p)==h1 else "MISMATCH"))
print("  H1=%d H2=%d H3=%d H4=%d  sum=%d  closure=%s" % (h1,h2,h3,h4,h1+h2+h3+h4,"OK" if h1+h2+h3+h4==len(h16) else "MISMATCH"))
print()
print("=== FENCE PAIRING ===")
F = chr(96)*3
opened=None; n=0; unc=0
for i,l in enumerate(txt.split("\n"),1):
    if l.startswith(F):
        n+=1
        if opened is None: opened=i
        else: opened=None
if opened is not None: unc=1; print("  *** UNCLOSED at %d ***"%opened)
print("  fence lines: %d   unclosed blocks: %d   -> %s" % (n,unc,"balanced" if n%2==0 and not unc else "UNBALANCED"))
print()
print("=== WHOLE-LINE DUP (excl blank + table separators) ===")
lines=[l.rstrip() for l in txt.split("\n")]
def ex(l):
    s=l.strip()
    if not s: return True
    if re.match(r"^\|[\s|:\-]+\|$",s): return True
    if s==F: return True
    return False
from collections import Counter
body=[l for l in lines if not ex(l)]
c=Counter(body); d={k:v for k,v in c.items() if v>1}
print("  non-excluded lines: %d   distinct: %d   dups: %d" % (len(body),len(c),len(d)))
for k,v in list(d.items())[:10]:
    print("     x%d  %s" % (v,k[:88]))
print()
print("=== CODEPOINT PROBE over every bracketed token ===")
toks=re.findall(r"\[([^\]\n]{1,80})\]",txt)
bad=[t for t in toks if any(ord(ch)>127 for ch in t)]
print("  bracketed tokens: %d   non-ASCII: %d" % (len(toks),len(bad)))
print("  whole-file non-ASCII: %d" % sum(1 for ch in txt if ord(ch)>127))
nz=sorted(set(ch for ch in txt if ord(ch)>127))
print("  distinct non-ASCII: %s" % " ".join("U+%04X(%s)"%(ord(ch),ch) for ch in nz))
print()
print("=== TAGS ===")
for t in ["[source]","[binary]","[measured]","[inferred]","[absence]","[instrument]","[verified]","[open]"]:
    print("  %-14s %d" % (t, txt.count(t)))
