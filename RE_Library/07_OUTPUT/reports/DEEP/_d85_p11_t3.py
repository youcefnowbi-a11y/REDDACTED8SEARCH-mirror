"""
D85 probe 11 -- T3: the NETWORK-FETCH bounded class.

D74's REMOTE_RESPONSE cell was 0 and I flagged it as my weakest, because a
target HTTP response read back via cmd_exec("curl ...") lands in
SESSION_TARGET under my rule. Lead's instruction: WRITE THAT AS A BOUNDED CLASS
-- enumerate every site whose cmd_exec argument contains a network-fetching
tool, and classify what it fetches.

I do NOT restrict to the 141/131 interpolated population. Rule 20: enumerate
the primitive's call sites across ALL cmd_exec sites, then report. The bounded
class is defined by the FETCH TOOL, not by whether the arg interpolates.
"""
import os, re, json, collections

ROOT = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\01_SOURCE_c2\metasploit"
POST = os.path.join(ROOT, "modules", "post")

CALL = re.compile(r"(?<![A-Za-z0-9_.'\"])(cmd_exec|create_process)\s*\(")
FETCH = re.compile(
    r"(?<![\w/-])(curl|wget|fetch|nc|ncat|netcat|telnet|ftp|tftp|scp|sftp|"
    r"Invoke-WebRequest|Invoke-RestMethod|iwr|irm|DownloadString|DownloadFile|"
    r"bitsadmin|certutil)\b", re.I)


def split_args(s):
    args, depth, cur, i, instr = [], 0, [], 0, None
    while i < len(s):
        c = s[i]
        if instr:
            cur.append(c)
            if c == "\\":
                i += 1
                if i < len(s):
                    cur.append(s[i])
                i += 1
                continue
            if c == instr:
                instr = None
        elif c in "'\"":
            instr = c
            cur.append(c)
        elif c in "([{":
            depth += 1
            cur.append(c)
        elif c in ")]}":
            if depth == 0:
                break
            depth -= 1
            cur.append(c)
        elif c == "," and depth == 0:
            args.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
        i += 1
    if "".join(cur).strip():
        args.append("".join(cur).strip())
    return args


def extract_call(text, start):
    depth, i, out, instr = 0, start, [], None
    while i < len(text):
        c = text[i]
        if instr:
            out.append(c)
            if c == "\\":
                i += 1
                if i < len(text):
                    out.append(text[i])
                i += 1
                continue
            if c == instr:
                instr = None
        elif c in "'\"":
            instr = c
            out.append(c)
        elif c in "([{":
            depth += 1
            out.append(c)
        elif c in ")]}":
            depth -= 1
            if depth == 0:
                return "".join(out)[1:], i
            out.append(c)
        else:
            out.append(c)
        i += 1
    return None, i


INTERP = re.compile(r"#\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}")
DS = re.compile(r"datastore\[|datastore\.")

rows = []
for dp, ds, fs in os.walk(POST):
    for f in fs:
        if not f.endswith(".rb"):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, ROOT)
        text = open(p, encoding="utf-8", errors="ignore").read()
        for m in CALL.finditer(text):
            ls = text.rfind("\n", 0, m.start()) + 1
            nl = text.find("\n", ls)
            if text[ls:nl if nl > 0 else len(text)].lstrip().startswith("#"):
                continue
            ln0 = text[:m.start()].count("\n")
            argstr, _ = extract_call(text, m.end() - 1)
            if argstr is None:
                continue
            args = split_args(argstr)
            if not args:
                continue
            joined = " ".join(args)
            fm = FETCH.search(joined)
            if not fm:
                continue
            # what does this site fetch? destination URL/host + whether it writes
            urlm = re.search(r"https?://[^\s'\"\\)\]]+", joined)
            hostm = re.search(r"(?:https?://)?([A-Za-z0-9_.\-]+\.[A-Za-z]{2,})", joined)
            exprs = [x.group(0) for x in INTERP.finditer(joined)]
            has_ds = bool(DS.search(joined))
            writes = bool(re.search(r"\s-o\s|\s-O\s|>\s|>>\s|download|write_file|--output", joined))
            rows.append(dict(file=rel, line=ln0 + 1, tool=fm.group(1).lower(),
                             url=urlm.group(0)[:70] if urlm else None,
                             host=hostm.group(1) if hostm else None,
                             nds=len([e for e in exprs if DS.search(e)]),
                             nexpr=len(exprs), writes=writes,
                             cmd=joined[:120], nargs=len(args)))

print("=== T3 BOUNDED CLASS: cmd_exec sites containing a network-fetch tool ===")
print("   total sites:", len(rows))
print()
print("   MANDATORY distribution by tool:")
for k, v in collections.Counter(r["tool"] for r in rows).most_common():
    print("      %-16s %4d" % (k, v))
print()
print("   distribution by whether the argument interpolates datastore:")
c = collections.Counter("HAS_datastore" if r["nds"] else
                       ("HAS_interp" if r["nexpr"] else "NO_interp") for r in rows)
for k, v in c.most_common():
    print("      %-16s %4d" % (k, v))
print()
print("   distribution by destination host:")
for k, v in collections.Counter(r["host"] or "(no host discernible)" for r in rows).most_common():
    print("      %-40s %4d" % (k, v))
print()
print("   writes to disk:", sum(1 for r in rows if r["writes"]))
print()
print("=== EVERY SITE ===")
for r in sorted(rows, key=lambda x: (x["file"], x["line"])):
    print("   %s:%d  [%s]" % (r["file"], r["line"], r["tool"]))
    print("      %s" % r["cmd"])
json.dump(rows, open(os.path.dirname(os.path.abspath(__file__)) + os.sep + "_d85_t3.json", "w"), indent=1)

# --- CONTROL: does the probe see fetches that are NOT in cmd_exec?
print()
print("=== CONTROL: curl/wget occurrences tree-wide vs inside cmd_exec args ===")
tot = 0
for dp, ds, fs in os.walk(POST):
    for f in fs:
        if not f.endswith(".rb"):
            continue
        t = open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read()
        tot += len(re.findall(r"(?<![\w/-])(curl|wget)\b", t, re.I))
print("   curl/wget tree-wide occurrences:", tot)
print("   curl/wget inside cmd_exec args :", sum(1 for r in rows if r["tool"] in ("curl", "wget")))
