# -*- coding: utf-8 -*-
# D-number reservation registry. Rule 30, upgraded from census to a LOCK.
#
# The defect this fixes: three lanes each censused D121 free, each ran a positive
# control, each announced -- and all three wrote to D121. A census-then-write
# allocation has NO mutual exclusion across the WORK window. Checking again does
# not close it; only an atomic claim does.
#
# O_CREAT|O_EXCL is atomic on NTFS and on POSIX. The FIRST claimant wins and
# everyone else gets FileExistsError. A reservation that cannot be double-claimed
# is the only form that survives a multi-minute write.
#
# Usage:
#   python _lead_alloc.py claim   <N> <lane> <title>   -> reserves, or reports held-by
#   python _lead_alloc.py status                        -> full table
#   python _lead_alloc.py release <N> <lane>            -> only the holder may release
#   python _lead_alloc.py verify                        -> cross-check registry vs disk
import os, sys, json, glob, datetime

DEEP = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\reports\DEEP"
REG = os.path.join(DEEP, "_ALLOC", "registry.json")
LOCKDIR = os.path.join(DEEP, "_ALLOC", "locks")

def load():
    if os.path.exists(REG):
        with open(REG, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save(d):
    os.makedirs(os.path.dirname(REG), exist_ok=True)
    tmp = REG + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=1, sort_keys=True)
    os.replace(tmp, REG)

def on_disk():
    """Every D-number actually present as a file, with its own count."""
    got = {}
    for p in glob.glob(os.path.join(DEEP, 'D*.md')):
        nm = os.path.basename(p)
        if len(nm) < 2 or nm[0] != 'D':
            continue
        j = 1
        while j < len(nm) and nm[j].isdigit():
            j += 1
        if j == 1:
            continue
        n = int(nm[1:j])
        got.setdefault(n, []).append(nm)
    return got

def claim(n, lane, title):
    os.makedirs(LOCKDIR, exist_ok=True)
    lock = os.path.join(LOCKDIR, 'D%d.lock' % n)
    d = load()
    if str(n) in d:
        h = d[str(n)]
        print('HELD  D%d by %s since %s' % (n, h['lane'], h['at']))
        print('      title: %s' % h['title'])
        return 1
    got = on_disk()
    if n in got:
        print('TAKEN-ON-DISK  D%d already has %d file(s):' % (n, len(got[n])))
        for f in got[n]:
            print('        %s' % f)
        return 2
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        print('LOCK-RACE  D%d lock file already exists (another claimant won)' % n)
        return 3
    at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    os.write(fd, ('%s|%s|%s' % (lane, at, title)).encode('utf-8'))
    os.close(fd)
    d[str(n)] = {'lane': lane, 'at': at, 'title': title}
    save(d)
    print('GRANTED  D%d to %s at %s' % (n, lane, at))
    return 0

def release(n, lane):
    d = load()
    if str(n) not in d:
        print('NOT-HELD  D%d' % n)
        return 1
    if d[str(n)]['lane'] != lane:
        print('REFUSED  D%d is held by %s, not %s' % (n, d[str(n)]['lane'], lane))
        return 2
    del d[str(n)]
    save(d)
    lock = os.path.join(LOCKDIR, 'D%d.lock' % n)
    if os.path.exists(lock):
        os.remove(lock)
    print('RELEASED  D%d' % n)
    return 0

def status():
    d = load()
    got = on_disk()
    print('=== RESERVED (claimed, not yet on disk) ===')
    for k in sorted(d, key=int):
        print('  D%-4s %-14s %s   %s' % (k, d[k]['lane'], d[k]['at'], d[k]['title'][:60]))
    print('\n=== ON DISK, MULTI-FILE (the collision detector) ===')
    bad = 0
    for n in sorted(got):
        if len(got[n]) > 1:
            bad += 1
            print('  D%-4d %d FILES:' % (n, len(got[n])))
            for f in sorted(got[n]):
                print('        %s' % f)
    if not bad:
        print('  none')
    print('\n=== ON DISK ===  %d numbers, %d files' %
          (len(got), sum(len(v) for v in got.values())))
    multi = [n for n in got if len(got[n]) > 1]
    print('  distinct numbers: %d   numbers with >1 file: %d' % (len(got), len(multi)))
    free = [n for n in range(100, 141) if n not in got and str(n) not in d]
    print('  free D100-D140: %s' % ' '.join('D%d' % n for n in free))
    return 0

def verify():
    """Cross-check: reserved-but-on-disk, and on-disk-but-unreserved."""
    d = load()
    got = on_disk()
    print('=== reserved AND on disk (claimed then written - normal) ===')
    a = [int(k) for k in d if int(k) in got]
    print('  %s' % (' '.join('D%d' % n for n in sorted(a)) or 'none'))
    print('=== reserved but NOT yet on disk (in flight) ===')
    b = [int(k) for k in d if int(k) not in got]
    print('  %s' % (' '.join('D%d' % n for n in sorted(b)) or 'none'))
    print('=== on disk but never reserved (pre-registry work) ===')
    c = [n for n in got if str(n) not in d]
    print('  %d numbers, %d files' % (len(c), sum(len(got[n]) for n in c)))
    m = [n for n in c if len(got[n]) > 1]
    if m:
        print('  MULTI-FILE among them: %s' % ' '.join('D%d' % n for n in sorted(m)))
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    op = sys.argv[1]
    if op == 'claim' and len(sys.argv) == 5:
        sys.exit(claim(int(sys.argv[2]), sys.argv[3], sys.argv[4]))
    if op == 'release' and len(sys.argv) == 4:
        sys.exit(release(int(sys.argv[2]), sys.argv[3]))
    if op == 'status':
        sys.exit(status())
    if op == 'verify':
        sys.exit(verify())
    print(__doc__)
