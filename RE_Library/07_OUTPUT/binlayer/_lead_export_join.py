import os, glob, json
BIN = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\extractions\T8\extracted\data\bin"
OUT = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\binlayer"

def load_tsv(path):
    rows = {}
    with open(path, 'r', encoding='utf-8') as f:
        for ln in f:
            if ln.startswith('#') or ln.startswith('entry_off'):
                continue
            p = ln.rstrip('\n').split('\t')
            if len(p) == 2:
                rows[int(p[0], 16)] = p[1]
    return rows

# --- the merlin.def export list, read from the file rather than typed ---
deflines = []
with open(os.path.join(BIN, 'merlin.def'), 'r', errors='replace') as f:
    for ln in f:
        s = ln.strip()
        if not s or s.startswith(';') or s.startswith('LIBRARY') or s.startswith('EXPORTS'):
            continue
        deflines.append(s)
print('merlin.def EXPORTS read from file: %d' % len(deflines))
for d in deflines:
    print('   %s' % d)

# --- the surviving original binaries (D110 T1) ---
SURVIVORS = [
    'merlin.x64.dll', 'merlin.x86.dll',
    'merlinAgent-Darwin-arm64', 'merlinAgent-Darwin-x64',
    'merlinAgent-Linux-arm', 'merlinAgent-Linux-arm64',
    'merlinAgent-Linux-x64',
    'merlinAgent-Windows-x64.exe', 'merlinAgent-Windows-x64-Debug.exe',
    'merlinCLI-Darwin-arm64', 'merlinCLI-Darwin-x64',
    'merlinCLI-Linux-arm', 'merlinCLI-Linux-arm64', 'merlinCLI-Linux-x64',
    'merlinCLI-Windows-x64.exe',
]
print('\nsurvivor binaries on disk: %d' % len(SURVIVORS))

# --- export names are 'FUNC' or 'FUNC @1' - take the bare name ---
names = []
for d in deflines:
    names.append(d.split()[0])
print('export names: %s' % names)

print('\n=== which exports appear in which binary\'s name table ===')
hdr = 'binary'.ljust(34) + ''.join(n[:11].rjust(13) for n in names)
print(hdr)
totals = {}
for b in SURVIVORS:
    tsv = os.path.join(OUT, '_lead_pclntab_%s.tsv' % b)
    if not os.path.exists(tsv):
        print('%-34s TSV MISSING' % b)
        continue
    rows = load_tsv(tsv)
    # index by bare last component of the Go symbol
    hit = {}
    for addr, full in rows.items():
        leaf = full.rsplit('.', 1)[-1]
        hit.setdefault(leaf, []).append((addr, full))
    line = b.ljust(34)
    for n in names:
        found = hit.get(n)
        if found:
            line += ('%d' % len(found)).rjust(13)
            totals[n] = totals.get(n, 0) + 1
        else:
            line += '-'.rjust(13)
    print(line)

print('\n=== exports found in at least one binary ===')
for n in names:
    print('  %-18s %d of %d survivors' % (n, totals.get(n, 0), len(SURVIVORS)))

print('\n=== the exact rows for each export, with package ===')
for b in ('merlin.x64.dll', 'merlin.x86.dll'):
    tsv = os.path.join(OUT, '_lead_pclntab_%s.tsv' % b)
    if not os.path.exists(tsv):
        continue
    rows = load_tsv(tsv)
    print('\n-- %s (%d names) --' % (b, len(rows)))
    for addr in sorted(rows):
        full = rows[addr]
        leaf = full.rsplit('.', 1)[-1]
        if leaf in names:
            print('   0x%X  %s' % (addr, full))

# --- cross-binary name-table comparison: is the export set in agents/CLIs too? ---
print('\n=== are these export names present in a CLI or agent? (they should NOT be) ===')
for b in ('merlinCLI-Windows-x64.exe', 'merlinAgent-Windows-x64.exe'):
    tsv = os.path.join(OUT, '_lead_pclntab_%s.tsv' % b)
    if not os.path.exists(tsv):
        continue
    rows = load_tsv(tsv)
    leaves = set(f.rsplit('.', 1)[-1] for f in rows.values())
    present = [n for n in names if n in leaves]
    print('  %-32s total names %6d   export-family leaves present: %s'
          % (b, len(rows), present if present else 'NONE'))
