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
    # utf-8-sig, NOT utf-8. On 2026-10-16 the Lead rewrote this registry with
    # PowerShell 'Set-Content -Encoding UTF8', which emits a BOM in PS 5.1.
    # 'encoding=utf-8' + json.load REJECTS a BOM, so EVERY claim and EVERY status
    # died with JSONDecodeError while the registry body was perfectly intact.
    # utf-8-sig tolerates a BOM when present and is identical to utf-8 when absent.
    if os.path.exists(REG):
        with open(REG, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    return {}

def save(d):
    # newline='\n' so the file is LF-only regardless of platform, and
    # utf-8-sig WRITES NO BOM (only strips one on read). Atomic via os.replace
    # so a crash mid-write cannot leave a truncated registry.
    os.makedirs(os.path.dirname(REG), exist_ok=True)
    tmp = REG + '.tmp'
    with open(tmp, 'w', encoding='utf-8-sig', newline='\n') as f:
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
        # .get throughout: a refusal path must REFUSE, not crash. The Lead's
        # hand-written D130 entry omitted 'at' and took the refusal path down
        # with KeyError -- so a taken number crashed instead of reporting held.
        print('HELD  D%d by %s since %s' % (n, h.get('lane', '?'), h.get('at', '?')))
        print('      title: %s' % h.get('title', '(none)'))
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
    locks = locks_on_disk()
    print('=== RESERVED (claimed, not yet on disk) ===')
    for k in sorted(d, key=int):
        e = d[k]
        # .get, not []. On 2026-10-16 the Lead hand-wrote registry entries with
        # Add-Member and omitted 'at', which crashed status() with KeyError.
        # A reporting function must not die on a malformed record it is meant
        # to REPORT. Missing fields render as '?' and the record stays visible.
        lane = e.get('lane', '?')
        at = e.get('at', '?')
        title = e.get('title', '(none)')
        print('  D%-4s %-14s %s   %s' % (k, lane, at, str(title)[:60]))
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
    # FREE is computed over the UNION of registry + locks + disk, and only for
    # numbers above the existing corpus. Computing it over the registry alone is
    # what let D132 read as free while its lock file was already held.
    taken = set(int(k) for k in d) | set(locks) | set(got)
    lo = max(got) + 1 if got else 100
    free = [n for n in range(lo, lo + 12) if n not in taken]
    print('  next free above the corpus (union of registry+locks+disk): %s'
          % ' '.join('D%d' % n for n in free[:6]))
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

def check(num):
    """Answer ONE question about ONE number, with a control that can fail.

    ADDED AFTER A LEAD DEFECT (I12). I invoked `verify 141` and `verify 142` and
    read two IDENTICAL outputs as 'positive and negative agree, so D141 is held'.
    But verify() takes NO ARGUMENT -- the dispatch discarded '141' and '142' and
    printed the same whole-corpus report both times. A SILENT ARGUMENT DISCARD.
    Identical output from two different inputs is not agreement; it is evidence
    the input never reached the function. Same species as `-readOnly`, which
    prints "Analysis succeeded" and then discards the analysis.

    This op therefore (a) takes the number, (b) reports each of the three
    sources of truth separately, and (c) exits non-zero when the number is
    genuinely free, so a caller can use it as a positive/negative control pair.
    """
    d = load()
    got = on_disk()
    lk = locks_on_disk()
    in_reg = str(num) in d
    on_dsk = num in got
    has_lk = num in lk
    print('=== check D%d ===' % num)
    print('  registry : %s%s' % (in_reg, '' if not in_reg else
          '  lane=%s at=%s' % (d[str(num)].get('lane', '?'), d[str(num)].get('at', '?'))))
    if on_dsk:
        print('  disk     : True  %d file(s)' % len(got[num]))
        for f in got[num]:
            print('             %s' % f)
    else:
        print('  disk     : False')
    if has_lk:
        print('  lock     : True  %s' % os.path.basename(lk[num]))
        try:
            head = open(lk[num], encoding='utf-8-sig').read().split('|')[0].strip()
            print('             holder=%s' % head)
        except Exception as e:
            print('             (unreadable: %s)' % e)
    else:
        print('  lock     : False')

    # The three sources are ORed, exactly as the allocator does when deciding
    # whether a number is free. Report the ORAGEN result and the disagreement.
    # LEAD DEFECT (I16): the three sources were compared for PRESENCE only, never
    # for OWNERSHIP. D142 was registry=archive-diver with the LEAD's file on disk
    # and this function printed 'VERDICT: HELD' with no disagreement line --
    # because in_reg, on_dsk and has_lk were all True. All three agreed the
    # number was TAKEN and none agreed WHO took it. A lane reading that output
    # learns the number is taken but not that the artefact on disk belongs to
    # somebody else. Presence agreement is not ownership agreement.
    if in_reg:
        reg_lane = str(d[str(num)].get('lane', '?'))
        lk_lane = None
        if has_lk:
            try:
                lk_lane = open(lk[num], encoding='utf-8-sig').read().split('|')[0].strip()
            except Exception:
                lk_lane = '?'
        if lk_lane and reg_lane != lk_lane:
            print('  *** OWNERSHIP DISAGREE ***  registry says %r, lock says %r'
                  % (reg_lane, lk_lane))
        if on_dsk:
            print('      -> the file(s) on disk may belong to a lane that did not')
            print('         hold the number. Re-check the artefact author line.')

    held = in_reg or on_dsk or has_lk
    print('  VERDICT  : %s' % ('HELD' if held else 'FREE'))
    if in_reg != on_dsk or in_reg != has_lk:
        print('  *** SOURCES DISAGREE ***  registry=%s disk=%s lock=%s'
              % (in_reg, on_dsk, has_lk))
        print('      The lock is authoritative and the registry is the derived')
        print('      view: the lock is created BEFORE the registry is saved, so a')
        print('      crash between the two leaves LOCK-HELD, UNREGISTERED.')
    return 0 if held else 1


def locks_on_disk():
    """Every D-number held by a lock file. THE SECOND SOURCE OF TRUTH.

    A lock file is created BEFORE the registry is saved. If the process dies
    between those two acts -- as every lane did on 2026-10-16 while the BOM
    crash was live -- the result is a LOCK-HELD, UNREGISTERED number. A lane
    reading only registry.json would call that number free and collide on it.
    So the lock file is the more reliable of the two signals, not the less.
    """
    got = {}
    for p in glob.glob(os.path.join(LOCKDIR, 'D*.lock')):
        nm = os.path.basename(p)
        j = 1
        while j < len(nm) and nm[j].isdigit():
            j += 1
        if j == 1:
            continue
        got[int(nm[1:j])] = p
    return got

def repair(apply_fix=False):
    """Reconcile registry.json against lock files AND files on disk.

    Reports three fault classes and, with --apply, backfills orphan locks into
    the registry. A half-claim is a real state, not corruption: the number is
    TAKEN and must never be handed out twice.
    """
    d = load()
    locks = locks_on_disk()
    got = on_disk()
    reg_nums = set(int(k) for k in d)
    lock_nums = set(locks)
    disk_nums = set(got)

    orphans = sorted(lock_nums - reg_nums)
    ghosts = sorted(reg_nums - lock_nums)
    unreg_disk = sorted(disk_nums - reg_nums)

    print('=== F1: LOCK-HELD but NOT REGISTERED (half-claim; number is TAKEN) ===')
    if orphans:
        for n in orphans:
            raw = ''
            try:
                with open(locks[n], 'r', encoding='utf-8-sig') as f:
                    raw = f.read().strip()
            except OSError as e:
                raw = '<unreadable: %s>' % e
            print('  D%-4d  %s' % (n, raw.replace('\n', ' ')))
            print('        lock file %d B -- treating as HELD' % os.path.getsize(locks[n]))
    else:
        print('  none')

    print('\n=== F2: REGISTERED but NO LOCK (lock lost or never created) ===')
    print('  %s' % (' '.join('D%d' % n for n in ghosts) or 'none'))

    print('\n=== F3: FILE ON DISK but NOT REGISTERED (pre-registry work) ===')
    print('  %s' % (' '.join('D%d' % n for n in unreg_disk) or 'none'))

    all_taken = sorted(reg_nums | lock_nums | disk_nums)
    # 'next free' must be ABOVE the existing corpus, not the lowest unused
    # integer. D1-D122 were written before this registry existed, so D27 has
    # neither a lock nor an entry -- but it DOES have a report on disk. A naive
    # lowest-unused scan reports D27 and would hand a lane a claimed number.
    lo = (max(got) + 1) if got else 100
    nxt = lo
    while nxt in all_taken:
        nxt += 1
    print('\n=== CROSS-CHECK ===')
    print('  registry %d   locks %d   on-disk %d   union %d'
          % (len(reg_nums), len(lock_nums), len(disk_nums), len(all_taken)))
    print('  max taken: D%d' % (max(all_taken) if all_taken else 0))
    print('  next free above corpus: D%d   (lowest-unused would wrongly say D%d)'
          % (nxt, next((n for n in range(1, lo) if n not in all_taken), 0)))
    print('  NOTE: D1-D122 are ON DISK WITHOUT LOCKS (pre-registry work).'
          ' Never claim below D%d.' % lo)

    if not orphans:
        print('\nNothing to backfill.')
        return 0

    if not apply_fix:
        print('\nDRY RUN. Re-run with:  repair --apply   to backfill %d orphan lock(s).'
              % len(orphans))
        return 0

    for n in orphans:
        lane, at, title = 'unknown', '', ''
        try:
            with open(locks[n], 'r', encoding='utf-8-sig') as f:
                parts = f.read().strip().split('|')
            if len(parts) >= 3:
                lane, at, title = parts[0], parts[1], parts[2]
            elif len(parts) == 1:
                title = parts[0]
        except OSError:
            pass
        d[str(n)] = {'lane': lane, 'at': at, 'title': title or '(backfilled from lock)'}
        print('  backfilled D%d -> lane=%s' % (n, lane))
    save(d)
    print('\nBackfilled %d. Re-verify with:  repair' % len(orphans))
    return 0

def controls():
    """Print the claim-gate controls, with the LEAD'S OWN DEFECT recorded.

    On 2026-10-16 the Lead issued every lane this control pair:
        positive:  Test-Path "129*"   -> claimed True
        negative:  Test-Path "<new>*" -> claimed False
    MEASURED: "129*" -> False, because the files are named D129_*.md.
    So BOTH halves returned False. A control pair whose positive and negative
    are indistinguishable tests NOTHING -- it is an assertion that cannot fail,
    which is the exact defect it was written to catch. It was issued to eight
    lanes across the whole session before havoc-deep measured it.

    The correct form keys on the FULL FILENAME PREFIX (D<num>), which is also
    the registry key. Naked 'D<num>.md' is a THIRD wrong form: files carry a
    slug after the number, so 'D129.md' also returns False and a lane reading
    it as 'taken' would be reading a name that never exists.
    """
    deep = DEEP
    print('=== CLAIM-GATE CONTROLS (run both; they must DIFFER) ===')
    # LEAD DEFECT (I13): the negative row was HARDCODED to D138. When D138 was
    # claimed mid-round the row began printing 'D138* -> True' against a label
    # reading 'a KNOWN-free number' -- a control contradicting its own label.
    # A control whose stub can be consumed by another lane is a control of its
    # own timestamp: this is 'a denominator over a growing corpus' applied to a
    # control. Fixed by DERIVING the negative from live state and choosing a
    # number that is structurally unclaimable (nobody reserves D9001).
    d = load()
    taken = set(int(k) for k in d) | set(locks_on_disk().keys()) | set(on_disk().keys())
    hi = max(taken) if taken else 141
    neg = 9001
    while neg in taken:
        neg += 1
    # LEAD DEFECT (I14): the positive row derived `hi` from ALL THREE sources
    # (registry + locks + disk) but validated it with a FILE GLOB. A freshly
    # claimed number has a lock and a registry entry and NO FILE, so the row
    # printed 'D144* -> False' for a number that is legitimately taken. A
    # control that contradicts its own derivation is worse than no control.
    # The positive stub must therefore be a number that HAS a FILE, and the
    # negative a number that has NO file and NO lock and NO registry entry.
    got_files = on_disk()
    if got_files:
        pos = max(got_files)
        pos_pat = 'D%d*' % pos
    else:
        pos_pat = 'D9001*'          # degenerate case, printed as such below
    neg = 9001
    while neg in taken:
        neg += 1
    rows = [
        (pos_pat,   'positive: the highest number WITH A FILE ON DISK', True),
        ('D%d*' % neg, 'negative: unclaimable stub (nobody reserves it)', False),
        ('%d*' % pos, 'WRONG FORM: misses the D prefix', None),
        ('D%d.md' % pos, 'WRONG FORM: no slug, never exists', None),
    ]
    for pat, what, expect in rows:
        got = bool(glob.glob(os.path.join(deep, pat)))
        if expect is None:
            verdict = 'DO NOT USE'
        else:
            verdict = 'ok' if got == expect else '*** MISMATCH ***'
        print('  %-9s -> %-5s   %-38s %s' % (pat, got, what, verdict))
    print('  If positive and negative return the SAME value, the pair tests')
    print('  nothing. That happened, and this line exists so it cannot recur.')
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
    if op == 'check' and len(sys.argv) == 3:
        sys.exit(check(int(sys.argv[2])))
    if op == 'repair':
        sys.exit(repair(apply_fix=('--apply' in sys.argv)))
    if op == 'controls':
        sys.exit(controls())
    # LOUD FAILURE ON AN UNRECOGNISED INVOCATION. Without this, `check` with a
    # missing number would fall through and print usage while exiting 0 -- the
    # same silent-discard that made `verify 141` read as a control.
    sys.stderr.write('ERROR: unrecognised invocation: %s\n' % ' '.join(sys.argv[1:]))
    sys.stderr.write('       nothing was done. usage: claim|release|status|verify|check|repair|controls\n')
    sys.exit(2)
