"""
carveout.py -- THE NAME-TABLE CARVE-OUT, as a reusable instrument.

THE PROBLEM IT SOLVES
  On a Go binary, every symbol name lives in a contiguous pclntab name table as a
  null-terminated string.  So a substring search for a literal LIKE "main." or
  "unknown" matches FUNCTION NAMES and returns hundreds of hits.  The claim
  "string X is in the binary" becomes unfalsifiable: every symbol counts as a hit.

THE FIX
  Locate the pclntab by magic, derive the name-table region from its own header,
  and report INSIDE vs OUTSIDE separately.
     OUTSIDE  -> a real compiled string literal.
     INSIDE   -> a function/symbol name.  Not evidence of a literal.

THE SIMPLER VARIANT (no pclntab needed)
  On a PE/ELF with a .rdata-like read-only section, the region between the end of
  .text and the end of .rdata holds the string blob.  Less precise, but portable.

SELF-TEST
  Every run MUST include a probe that cannot exist (a garbage token).  If the
  garbage probe returns > 0, the search pattern is not discriminating and the
  whole table is void.
"""
import struct

MAGICS = [b"\xf1\xff\xff\xff", b"\xfa\xff\xff\xff", b"\xf0\xff\xff\xff"]


def locate_pclntab(b):
    """Return (ptrSize, base, NAME_LO, NAME_HI) or None."""
    for mag in MAGICS:
        s = 0
        while True:
            i = b.find(mag, s)
            if i < 0:
                break
            if i + 8 < len(b) and b[i + 6] in (1, 2, 4, 8) and b[i + 7] in (4, 8):
                ps = b[i + 7]
                try:
                    fno = struct.unpack_from("<Q", b, i + 32)[0]
                    pco = struct.unpack_from("<Q", b, i + 64)[0]
                except struct.error:
                    s = i + 1
                    continue
                lo, hi = i + fno, i + pco
                if 0 < lo < hi <= len(b) and (hi - lo) > 1024:
                    return ps, i, lo, hi
            s = i + 1
    return None


def carve(b, tokens, verbose=True):
    """Report INSIDE/OUTSIDE for each token.  Returns a dict.  Fails loud on a bad control."""
    loc = locate_pclntab(b)
    if loc is None:
        if verbose:
            print("   pclntab NOT FOUND -- carve-out unavailable on this image.")
            print("   (not every target is Go; say so rather than guessing a region)")
        return None
    ps, base, lo, hi = loc
    if verbose:
        print("   pclntab base=0x%X ptrSize=%d" % (base, ps))
        print("   NAME-TABLE REGION: 0x%X .. 0x%X  = %d bytes  (%.1f%% of image)"
              % (lo, hi, hi - lo, 100.0 * (hi - lo) / len(b)))

    # mandatory discrimination control
    ctl = b.count(b"__ZZZ_NOT_A_SYMBOL_ZZZ__")
    if verbose:
        print("   CONTROL (garbage token): %d hit(s) -- must be 0" % ctl)
    if ctl:
        if verbose:
            print("   *** INSTRUMENT VOID: pattern not discriminating. ***")
        return None

    out = {}
    for t in tokens:
        tb = t.encode()
        ins, outs = [], []
        s = 0
        while True:
            i = b.find(tb, s)
            if i < 0:
                break
            (ins if lo <= i < hi else outs).append(i)
            s = i + 1
        if outs and not ins:
            v = "LITERAL"
        elif ins and not outs:
            v = "SYMBOL-ONLY"
        elif ins and outs:
            v = "BOTH"
        else:
            v = "ABSENT"
        out[t] = dict(inside=len(ins), outside=len(outs), verdict=v,
                      first_outside=hex(outs[0]) if outs else None)
        if verbose:
            print("   %-34s OUT=%-6d IN=%-6d %s" % (t, len(outs), len(ins), v))
    return out


if __name__ == "__main__":
    import os, sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
    TESTS = [
        os.path.join(WS, r"RE_Library\02_BINARIES\sliver\sliver-client_windows-amd64.exe"),
        os.path.join(WS, r"RE_Library\05_TARGETS\merlin_extracted\data\bin\merlinAgent-Linux-x64"),
        os.path.join(WS, r"RE_Library\05_TARGETS\merlin_extracted\data\bin\merlinCLI-Linux-x64"),
    ]
    for p in TESTS:
        print("=" * 92)
        print("SCOPE: %s" % os.path.basename(p))
        b = open(p, "rb").read()
        print("COUNTED: %d bytes" % len(b))
        carve(b, ["main.main", "main.secure", "main.useragent", "<unknown>",
                  "GetAIConversationMessages"])
        print()
