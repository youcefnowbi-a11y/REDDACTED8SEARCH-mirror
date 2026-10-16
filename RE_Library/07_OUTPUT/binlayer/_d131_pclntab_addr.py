# Lead-side pclntab address->name extractor. Static only. No execution of targets.
# Go pclntab (Go 1.16+) header:
#   magic u32 = 0xFFFFFFF1 ; pad u8 0 ; pad u8 0 ; minLC u8 ; ptrSize u8
#   nfunc u64, nfiles u64, textStart u64, funcnameOffset u64,
#   cuOffset u64, filetabOffset u64, pctabOffset u64, pclnOffset u64
# Offsets in the header are relative to the START OF PCLNTAB.
# functab: nfunc entries of (entryoff u32, funcoff u32) - entryoff is relative
#   to textStart, funcoff relative to pclntab start.
# _func: entryoff u32, nameoff i32 (relative to funcnameOffset), args u32,
#   deferreturn u32, pcsp u32, pcfile u32, pcln u32, npcdata u32, cuOffset u32,
#   startLine i32, funcID u8, flag u8, _ u8, nfuncdata u8
import os, sys, struct, json, glob

MAGIC = 0xFFFFFFF1

def u32(b, o): return struct.unpack_from('<I', b, o)[0]
def u64(b, o): return struct.unpack_from('<Q', b, o)[0]
def i32(b, o): return struct.unpack_from('<i', b, o)[0]

def find_pclntab(b):
    """Locate pclntab by magic + header self-consistency, ptrSize-aware."""
    cands = []
    n = len(b)
    for i in range(0, n - 64):
        if b[i] != 0xF1 or b[i+1] != 0xFF or b[i+2] != 0xFF or b[i+3] != 0xFF:
            continue
        if b[i+4] != 0 or b[i+5] != 0:
            continue
        minLC = b[i+6]
        ptr = b[i+7]
        if ptr not in (4, 8):
            continue
        if minLC not in (1, 2, 4):
            continue
        # read fields with the right pointer width
        if ptr == 8:
            nfunc = u64(b, i+8); nfiles = u64(b, i+16)
            textStart = u64(b, i+24); funcnameOff = u64(b, i+32)
            cuOff = u64(b, i+40); filetabOff = u64(b, i+48)
            pctabOff = u64(b, i+56); pclnOff = u64(b, i+64)
            hdr = 72
        else:
            nfunc = u32(b, i+8); nfiles = u32(b, i+12)
            textStart = u32(b, i+16); funcnameOff = u32(b, i+20)
            cuOff = u32(b, i+24); filetabOff = u32(b, i+28)
            pctabOff = u32(b, i+32); pclnOff = u32(b, i+36)
            hdr = 40
        # plausibility: nfunc between 100 and 2,000,000; every offset inside file
        if not (100 <= nfunc <= 2_000_000):
            continue
        if not (0 <= funcnameOff < n and 0 <= pclnOff < n and funcnameOff < pclnOff):
            continue
        if not (funcnameOff < filetabOff <= pclnOff):
            continue
        cands.append((i, ptr, minLC, nfunc, nfiles, textStart,
                      funcnameOff, cuOff, filetabOff, pctabOff, pclnOff, hdr))
    return cands

def read_cstr(b, off):
    e = off
    while e < len(b) and b[e] != 0:
        e += 1
    return b[off:e]

def parse(b):
    cands = find_pclntab(b)
    if not cands:
        return None, 'no_pclntab_header'
    # prefer the candidate whose functab is fully in-bounds
    best = None
    for c in cands:
        (base, ptr, minLC, nfunc, nfiles, textStart,
         fnameOff, cuOff, ftOff, pctabOff, pclnOff, hdr) = c
        ft = base + pclnOff          # functab lives at pclnOffset
        if ft + nfunc * 8 > len(b):
            continue
        fnames = base + fnameOff
        if fnames >= len(b):
            continue
        ok = 0
        for k in range(min(nfunc, 64)):
            fo = ft + k * 8
            eoff = u32(b, fo)
            foff = u32(b, fo + 4)
            if foff == 0 or foff == 0xFFFFFFFF:
                continue
            fo2 = ft + foff
            if fo2 + 8 > len(b):
                continue
            nm = i32(b, fo2 + 4)
            p = fnames + nm
            if 0 <= p < len(b) and b[p] != 0:
                ok += 1
        if ok < 8:
            continue
        cand = dict(base=base, ptr=ptr, minLC=minLC, nfunc=nfunc, nfiles=nfiles,
                    textStart=textStart, funcnameOff=fnameOff, cuOff=cuOff,
                    pctabOff=pctabOff, pclnOff=pclnOff, hdr=hdr, ft=ft,
                    fnames=fnames, probe_ok=ok)
        if best is None or ok > best['probe_ok']:
            best = cand
    if best is None:
        return None, 'no_parseable_functab'
    return best, None

def dump(b, meta):
    ft = meta['ft']; fnames = meta['fnames']; nfunc = meta['nfunc']
    textStart = meta['textStart']; base = meta['base']
    rows = []
    sub = 0; empty = 0; okc = 0
    for k in range(nfunc):
        fo = ft + k * 8
        if fo + 8 > len(b):
            break
        eoff = u32(b, fo)
        foff = u32(b, fo + 4)
        if foff in (0, 0xFFFFFFFF):
            empty += 1
            continue
        fo2 = ft + foff
        if fo2 + 16 > len(b):
            empty += 1
            continue
        nm = i32(b, fo2 + 4)
        if nm == 0:
            empty += 1
            continue
        p = fnames + nm
        if not (0 <= p < len(b)):
            empty += 1
            continue
        name = read_cstr(b, p)
        if not name:
            empty += 1
            continue
        try:
            s = name.decode('utf-8')
        except UnicodeDecodeError:
            s = name.decode('utf-8', 'replace')
            sub += 1
        if '\ufffd' in s:
            sub += 1
        entry = textStart + eoff if textStart else eoff
        rows.append((entry, s))
        okc += 1
    return rows, dict(ok=okc, empty=empty, sub=sub)

def main():
    targets = sys.argv[1]
    outdir = sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    summary = []
    for path in ([targets] if os.path.isfile(targets) else sorted(glob.glob(os.path.join(targets, '*')))):
        if not os.path.isfile(path):
            continue
        nm = os.path.basename(path)
        with open(path, 'rb') as f:
            b = f.read()
        meta, err = parse(b)
        if meta is None:
            # try a relaxed anchor: scan for the magic char pattern only
            summary.append(dict(file=nm, size=len(b), status='unparsed', error=err))
            continue
        rows, stats = dump(b, meta)
        out = os.path.join(outdir, '_lead_pclntab_' + nm + '.tsv')
        with open(out, 'w', encoding='utf-8', newline='\n') as w:
            w.write('# file\t%s\tsize\t%d\n' % (nm, len(b)))
            w.write('# pclntab_base\t0x%X\tminLC\t%d\tptrSize\t%d\n'
                    % (meta['base'], meta['minLC'], meta['ptr']))
            w.write('# nfunc_hdr\t%d\tnfunc_emitted\t%d\tempty_or_nameless\t%d'
                    '\tutf8_substituted\t%d\n'
                    % (meta['nfunc'], stats['ok'], stats['empty'], stats['sub']))
            w.write('# NOTE entry is textStart+entryoff; textStart=0x%X\n'
                    % meta['textStart'])
            w.write('entry_off\tname\n')
            for e, s in rows:
                w.write('0x%X\t%s\n' % (e, s))
        uniq = len(set(s for _, s in rows))
        summary.append(dict(file=nm, size=len(b), status='ok',
                            pclntab_base='0x%X' % meta['base'],
                            minLC=meta['minLC'], ptrSize=meta['ptr'],
                            nfunc_hdr=meta['nfunc'], emitted=stats['ok'],
                            empty=stats['empty'], substituted=stats['sub'],
                            unique_names=uniq, tsv=os.path.basename(out)))
    with open(os.path.join(outdir, '_lead_pclntab_summary.json'), 'w',
              encoding='utf-8') as w:
        json.dump(summary, w, indent=1)
    tot = sum(s.get('emitted', 0) for s in summary)
    print('files_considered\t%d' % len(summary))
    print('files_parsed\t%d' % sum(1 for s in summary if s['status'] == 'ok'))
    print('total_emitted\t%d' % tot)
    for s in summary:
        print(json.dumps(s))

if __name__ == '__main__':
    main()
