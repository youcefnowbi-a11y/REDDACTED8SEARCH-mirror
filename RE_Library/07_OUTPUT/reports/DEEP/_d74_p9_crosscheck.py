"""
D74 probe 9 -- INDEPENDENT VERIFICATION of every D74 headline number.

Method 2 for each figure (deliberately different instrument from probes 1-8):
  total call sites  -> count via a DIFFERENT tokenizer: strip comments and string
                       literals FIRST, then count in the cleaned text.
  interpolated      -> count via unbalanced-brace stripping: remove all #{...}
                       spans, then ask whether any quote pair still contains the
                       site; instead, here: count sites whose arg contains '#' '{'.
  datastore exprs   -> count raw substring occurrences of "datastore[" inside
                       interpolations via a different regex.
  second args       -> count by paren-depth splitting written independently.

Any figure that differs between methods is reported as UNSTABLE with both values.
"""
import os, re, collections

ROOT = r"RE_Library\01_SOURCE_c2\metasploit"
POST = os.path.join(ROOT, "modules", "post")

FILES = []
for dp, ds, fs in os.walk(POST):
    for f in fs:
        if f.endswith(".rb"):
            FILES.append(os.path.join(dp, f))
print("post .rb files:", len(FILES))


def strip_comments_and_strings(t):
    """Method 2's preprocessing: blank out #-comments and quoted spans."""
    out = list(t)
    i, n = 0, len(t)
    while i < n:
        c = t[i]
        if c == "#":
            # comment to end of line UNLESS it is #{ interpolation inside a string
            j = i
            while j < n and t[j] != "\n":
                out[j] = " "
                j += 1
            i = j
        elif c in "'\"":
            q = c
            j = i + 1
            while j < n:
                if t[j] == "\\":
                    j += 2
                    continue
                if t[j] == q:
                    break
                j += 1
            for k in range(i + 1, min(j, n)):
                if out[k] not in "\n":
                    out[k] = " "
            i = j + 1
        else:
            i += 1
    return "".join(out)


CLEAN_TOTAL = 0
RAW_TOTAL = 0
CALLRX = re.compile(r"(?<![A-Za-z0-9_.'\"])(cmd_exec|create_process)\s*\(")
for p in FILES:
    t = open(p, encoding="utf-8", errors="ignore").read()
    CLEAN_TOTAL += len(CALLRX.findall(strip_comments_and_strings(t)))
    RAW_TOTAL += len(CALLRX.findall(t))
print()
print("=== METHOD 2: call-site counts ===")
print("   raw text                :", RAW_TOTAL)
print("   comments+strings blanked:", CLEAN_TOTAL)
print("   (probes 1-8 reported    : 459 after comment-line filter)")

# --- method 2 for interpolation: does the arg contain #{ ? ---
# count sites where, after removing ALL #{...} spans, the arg body still contains
# a '#' '{' -- should be zero if stripping is complete (structural control).
SPAN = re.compile(r"#\{")
print()
print("=== METHOD 2: interpolation counts (occurrence of '#{' anywhere in a call's arg list) ===")
n_interp_arg_anywhere = 0
n_datastore_in_interp = 0
for p in FILES:
    t = open(p, encoding="utf-8", errors="ignore").read()
    for m in CALLRX.finditer(t):
        ls = t.rfind("\n", 0, m.start()) + 1
        nl = t.find("\n", ls)
        if t[ls:nl if nl > 0 else len(t)].lstrip().startswith("#"):
            continue
        # take the next 300 chars as an approximate argument window
        win = t[m.end():m.end() + 300]
        if SPAN.search(win):
            n_interp_arg_anywhere += 1
        for im in re.finditer(r"#\{[^{}]*\}", win):
            if "datastore[" in im.group(0):
                n_datastore_in_interp += 1
print("   sites with '#{' in the following 300 chars:", n_interp_arg_anywhere)
print("   datastore[ inside an interpolation (300-char window):", n_datastore_in_interp)
print("   (probe 2 reported 141 first-arg interpolated sites; 16 datastore expressions;")
print("    probe 7 reported 62 DATSTORE expressions after def/param resolution)")

# --- method 2 for second args: split on top-level comma using a stack of chars ---
print()
print("=== METHOD 2: second-argument presence ===")
def comma_positions(s):
    pos, depth, instr = [], 0, None
    i = 0
    while i < len(s):
        c = s[i]
        if instr:
            if c == "\\":
                i += 2
                continue
            if c == instr:
                instr = None
        elif c in "'\"":
            instr = c
        elif c in "([{":
            depth += 1
        elif c in ")]}":
            if depth == 0:
                break
            depth -= 1
        elif c == "," and depth == 0:
            pos.append(i)
        i += 1
    return pos

def args_of(t, start):
    depth, i, instr = 0, start, None
    while i < len(t):
        c = t[i]
        if instr:
            if c == "\\":
                i += 2
                continue
            if c == instr:
                instr = None
        elif c in "'\"":
            instr = c
        elif c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
            if depth == 0:
                return t[start + 1:i]
        i += 1
    return None

n_args = collections.Counter()
n_second_interp = 0
for p in FILES:
    t = open(p, encoding="utf-8", errors="ignore").read()
    for m in CALLRX.finditer(t):
        ls = t.rfind("\n", 0, m.start()) + 1
        nl = t.find("\n", ls)
        if t[ls:nl if nl > 0 else len(t)].lstrip().startswith("#"):
            continue
        a = args_of(t, m.end() - 1)
        if a is None:
            continue
        cp = comma_positions(a)
        n = len(cp) + 1 if a.strip() else 0
        n_args[n] += 1
        if n >= 2:
            seg = a[cp[0] + 1:] if len(cp) == 1 else a[cp[0] + 1:cp[1]]
            if "#{" in seg:
                n_second_interp += 1
print("   arg-count distribution:", dict(n_args))
print("   sites with a 2nd arg containing '#{':", n_second_interp)
print("   (probe 8 reported 27 second-arg INTERPOLATED)")
