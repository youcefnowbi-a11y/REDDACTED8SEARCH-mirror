#!/usr/bin/env python3
"""Lead verification of the release-vs-debug SECTION ATTRIBUTION claim.

D130 measured 64,565 differing bytes between merlinAgent-Windows-x64.exe and
its -Debug twin, and reported a 1 MB band histogram.  sliver-diver (D138)
then claimed the whole diff attributes to PE sections as:

    .reloc 62,896   .rdata 1,375   .data 211   .text 80   outside 3

The .text number is the one that matters for a detection DB: if executable
text differs between release and debug, any fingerprint keyed on those bytes
is build-configuration-specific.  So it is verified here independently of the
lane's instrument, by parsing the PE section table directly.

Rule 33 header is printed BEFORE any number.  Every count is accompanied by
its scope.  The control: total attributed bytes must equal the measured
diff count, and the section table must cover the whole file -- if the
attribution does not close, the numbers are not reported as findings.
"""
import os
import struct
import sys

BASE = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\05_TARGETS\merlin_extracted\data\bin"
REL = os.path.join(BASE, "merlinAgent-Windows-x64.exe")
DBG = os.path.join(BASE, "merlinAgent-Windows-x64-Debug.exe")


def read(path):
    with open(path, "rb") as fh:
        return fh.read()


def sections(buf):
    """Return [(name, virt_size, virt_addr, raw_size, raw_ptr, chars)] in file order."""
    if buf[:2] != b"MZ":
        raise ValueError("not MZ")
    e_lfanew = struct.unpack_from("<I", buf, 0x3C)[0]
    if buf[e_lfanew:e_lfanew + 4] != b"PE\0\0":
        raise ValueError("not PE")
    coff = e_lfanew + 4
    nsec, = struct.unpack_from("<H", buf, coff + 2)
    opt_size, = struct.unpack_from("<H", buf, coff + 16)
    opt = coff + 20
    magic, = struct.unpack_from("<H", buf, opt)
    if magic == 0x20B:      # PE32+
        dd = opt + 112
    elif magic == 0x10B:    # PE32
        dd = opt + 96
    else:
        raise ValueError("bad optional magic 0x%X" % magic)
    # sanity: declared section table must fit
    sec_tab = opt + opt_size
    out = []
    for i in range(nsec):
        off = sec_tab + i * 40
        name = buf[off:off + 8].rstrip(b"\0").decode("latin-1")
        v_size, v_addr, r_size, r_ptr = struct.unpack_from("<IIII", buf, off + 8)
        chars, = struct.unpack_from("<I", buf, off + 36)
        out.append((name, v_size, v_addr, r_size, r_ptr, chars))
    return out, magic, nsec, dd, buf[dd:dd + 8]


def main():
    print("SCOPE:        release vs debug merlinAgent-Windows-x64{,-Debug}.exe, "
          "two artifacts, whole-file byte diff")
    print("DEFINER SCOPE: PE section table parsed directly from the file headers; "
          "attribution by FILE OFFSET")
    print("CONDITIONAL SCOPE: attribution is per-file-offset only. A byte inside a "
          "packed/overlay region is reported as 'outside'")
    print("COUNTED:      all bytes of both files; every differing byte assigned to "
          "exactly one section or to 'outside'\n")

    a, b = read(REL), read(DBG)
    print("=== OPERAND CONTROL (the instrument must have opened them) ===")
    print("  release : %s  %d B  MZ=%s" % (os.path.basename(REL), len(a), a[:2] == b"MZ"))
    print("  debug   : %s  %d B  MZ=%s" % (os.path.basename(DBG), len(b), b[:2] == b"MZ"))
    print("  equal length : %s" % (len(a) == len(b)))
    print("  distinct bytes: %s" % (a != b))
    if len(a) != len(b):
        print("  ABORT: lengths differ, offset-wise attribution invalid")
        return 1

    secs, magic, nsec, dd, ddbytes = sections(a)
    secs_b, magic_b, nsec_b, _, _ = sections(b)
    print("\n=== SECTION TABLE (release) ===")
    print("  optional magic 0x%X   sections %d   data-directory count bytes %s"
          % (magic, nsec, ddbytes[:4].hex()))
    print("  %-10s %>10s %>10s %>12s %>12s %>6s".replace(">", "")
          % ("name", "vsize", "vaddr", "rawsize", "rawptr", "chars"))
    for nm, vs, va, rs, rp, ch in secs:
        print("  %-10s %#10x %#10x %12d %12d  %#06x" % (nm, vs, va, rs, rp, ch))
    print("  section tables identical (name/addr/size): %s"
          % ([s[:5] for s in secs] == [s[:5] for s in secs_b]))

    # Build a file-offset -> section map. Sections are ordered; use raw ranges.
    # Overlaps are impossible in a well-formed PE, but assert it.
    ranges = [(rp, rp + rs, nm) for nm, vs, va, rs, rp, ch in secs]
    ranges.sort()
    for i in range(1, len(ranges)):
        if ranges[i][0] < ranges[i - 1][1]:
            print("  WARNING: raw ranges overlap: %s / %s" % (ranges[i - 1], ranges[i]))

    def owner(off):
        for s, e, nm in ranges:
            if s <= off < e:
                return nm
        return "outside"

    # COVERAGE CONTROL: how much of the file do the sections cover?
    covered = sum(e - s for s, e, nm in ranges)
    print("\n=== COVERAGE CONTROL (attribution must close) ===")
    print("  file size            : %d" % len(a))
    print("  bytes covered by raw sections: %d (%.2f%%)" % (covered, 100.0 * covered / len(a)))
    print("  not covered (headers/overlay/gap): %d" % (len(a) - covered))

    counts = {}
    last = -1
    first = None
    n = 0
    for i in range(len(a)):
        if a[i] != b[i]:
            n += 1
            counts[owner(i)] = counts.get(owner(i), 0) + 1
            if first is None:
                first = i
            if last >= 0 and i - last > 1:
                pass
            last = i

    print("\n=== DIFF TOTALS ===")
    print("  differing bytes: %d  (%.5f%% of %d)" % (n, 100.0 * n / len(a), len(a)))
    print("  first differing offset: %d (0x%X)  section=%s" % (first, first, owner(first)))
    print("  last differing offset : %d (0x%X)  section=%s" % (last, last, owner(last)))

    print("\n=== ATTRIBUTION (independently measured) ===")
    tot = 0
    for nm, c in sorted(counts.items(), key=lambda kv: -kv[1]):
        print("  %-10s %8d  %6.2f%%" % (nm, c, 100.0 * c / n))
        tot += c
    print("  %-10s %8d" % ("SUM", tot))
    print("  CLOSURE (sum == total): %s" % (tot == n))

    print("\n=== LANE CLAIM vs LEAD MEASUREMENT ===")
    claim = {".reloc": 62896, ".rdata": 1375, ".data": 211, ".text": 80, "outside": 3}
    print("  %-10s %>10s %>10s %>8s".replace(">", "")
          % ("section", "claimed", "measured", "match"))
    allmatch = True
    for k in sorted(set(list(claim) + list(counts))):
        c = claim.get(k, 0)
        m = counts.get(k, 0)
        ok = (c == m)
        allmatch = allmatch and ok
        print("  %-10s %10d %10d %8s" % (k, c, m, ok))
    print("  ALL SECTIONS MATCH: %s" % allmatch)
    print("  claimed total %d vs measured total %d" % (sum(claim.values()), n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
