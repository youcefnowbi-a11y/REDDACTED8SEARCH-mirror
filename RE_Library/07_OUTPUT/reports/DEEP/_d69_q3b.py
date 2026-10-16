import os, re, collections

core = r"RE_Library\01_SOURCE_c2\metasploit\lib\msf\core"

# Q3/structural: three dispatch styles touching session type/platform.
#   STYLE A  `case session.type`            (with/without else)
#   STYLE B  `if session.type == '...'`     (independent guards, may fall through)
#   STYLE C  `elsif` chain ending in `else` (catch-all, asserts a default)
rx_case  = re.compile(r"^\s*case\s+session\.(?:type|platform|arch)\b", re.M)
rx_if    = re.compile(r"^\s*if\s+session\.(?:type|platform|arch)\s*==", re.M)
rx_elsif = re.compile(r"^\s*elsif\s+session\.(?:type|platform|arch)\s*==", re.M)

print("%-58s %-6s %-6s %-6s" % ("file", "case", "if==", "elsif"))
tot = collections.Counter()
rows = []
for dp, ds, fs in os.walk(core):
    for f in fs:
        if not f.endswith(".rb"):
            continue
        p = os.path.join(dp, f)
        t = open(p, encoding="utf-8", errors="ignore").read()
        a, b, c = len(rx_case.findall(t)), len(rx_if.findall(t)), len(rx_elsif.findall(t))
        if a or b or c:
            rows.append((os.path.relpath(p, core), a, b, c))
            tot["case"] += a; tot["if"] += b; tot["elsif"] += c
for rel, a, b, c in sorted(rows, key=lambda r: -(r[1] + r[2] + r[3])):
    print("%-58s %-6d %-6d %-6d" % (rel, a, b, c))
print()
print("TOTALS: case=%d  if==%d  elsif=%d" % (tot["case"], tot["if"], tot["elsif"]))
print()
print("=== the `else` catch-alls: does the else assume a shell? ===")
rx_else_cmd = re.compile(r"^\s*else\s*$", re.M)
# find `elsif session...` blocks whose else calls cmd_exec / shell_command_token
for dp, ds, fs in os.walk(core):
    for f in fs:
        if not f.endswith(".rb"):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, core)
        L = open(p, encoding="utf-8", errors="ignore").read().split("\n")
        for i, l in enumerate(L):
            if re.match(r"^\s*else\s*$", l):
                # look ahead 3 lines for an unconditional shell exec
                nxt = "\n".join(L[i + 1:i + 4])
                if re.search(r"(cmd_exec|shell_command_token|shell_command)\b", nxt):
                    print("   %s:%d  else -> %s" % (rel, i + 1, nxt.strip().split("\n")[0][:70]))
