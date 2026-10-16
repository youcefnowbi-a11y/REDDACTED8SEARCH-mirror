import os, re
BIN = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\extractions\T8\extracted\data\bin"
OUT = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\binlayer"

def load_tsv(path):
    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        for ln in f:
            if ln.startswith('#') or ln.startswith('entry_off'):
                continue
            p = ln.rstrip('\n').split('\t')
            if len(p) == 2:
                rows.append((int(p[0], 16), p[1]))
    return rows

for b in ('merlin.x64.dll', 'merlin.x86.dll'):
    tsv = os.path.join(OUT, '_lead_pclntab_%s.tsv' % b)
    rows = load_tsv(tsv)
    print('=== %s : %d names ===' % (b, len(rows)))

    # 1. any leaf whose name is exactly one of the 7 def exports
    target = set('Run VoidFunc DllInstall DllRegisterServer DllUnregisterServer Merlin Magic'.split())
    exact = [(a, f) for a, f in rows if f.rsplit('.', 1)[-1] in target]
    print('  exact-leaf matches: %d' % len(exact))
    for a, f in exact:
        print('    0x%-8X %s' % (a, f))

    # 2. substring search - 'Magic' anywhere in any name
    print('  substring "Magic" anywhere in the %d names:' % len(rows))
    m = [(a, f) for a, f in rows if 'Magic' in f]
    for a, f in m[:20]:
        print('    0x%-8X %s' % (a, f))
    print('    count: %d' % len(m))

    # 3. main.* - the package the exports must live in
    print('  all main.* functions (the DLL export surface):')
    mn = [(a, f) for a, f in rows if f.startswith('main.')]
    for a, f in sorted(mn):
        print('    0x%-8X %s' % (a, f))
    print('    main.* count: %d' % len(mn))
    print()

# 4. THE SAME SEARCH ON THE AGENT, as a positive control that the search works
print('=== CONTROL: same substring search on merlinAgent-Windows-x64.exe ===')
rows = load_tsv(os.path.join(OUT, '_lead_pclntab_merlinAgent-Windows-x64.exe.tsv'))
mn = [(a, f) for a, f in rows if f.startswith('main.')]
print('  main.* count: %d' % len(mn))
for a, f in sorted(mn)[:25]:
    print('    0x%-8X %s' % (a, f))
