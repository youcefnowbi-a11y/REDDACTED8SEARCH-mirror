# The per-path integrity check: how to run it so it does not lie

**Lead, round 21.** The check that caught the D61/D72/D69 integrity gap also produced **one false
positive in 84 files** this round. Both outcomes are recorded here, because a check that is right
once and wrong once is a check nobody can trust until its failure mode is named.

## The check, correctly specified

> **Compare `git cat-file -s HEAD:<path>` against the on-disk byte count — but only after
> normalising the disk side for `core.autocrlf`.**

`core.autocrlf = true` in this repository (verified). Git stores **LF** in the object database and
converts to **CRLF** on checkout. So for any file checked out under that setting:

```
disk_bytes = blob_bytes + (number of CR bytes on disk)
```

**The correct comparison is therefore `diskLength - countOfCR == blobSize`, not `diskLength ==
blobSize`.**

## The false positive, measured

| file | disk | CR count | disk − CR | HEAD | verdict |
|---|---:|---:|---:|---:|---|
| `D11_pupy_transport_crypto.md` | 38,761 | 517 | **38,244** | **38,244** | **IDENTICAL** |

`38,761 − 517 = 38,244` exactly, and a byte-by-byte comparison with CR removed confirms
`BYTE-IDENTICAL modulo CR: True`.

**Why only this one file fired:** it is the only DEEP report whose on-disk copy carries CRLF. The
other 83 are LF-pure, so `CR count = 0` and the naive and corrected comparisons agree. **The probe
was right 83 times by coincidence and wrong once for a real reason — and the one failure is the
only one that carried information.**

**Not an integrity gap:** porcelain is clean for that path, and its mtime is from round 14, so the
file has not been touched since `8671e6d`. The naive check compared a **checkout** against a
**repository object** as though they were the same encoding.

## The instrument failure, logged

**Shape 5 — the probe's shape must match the evidence's shape.** A byte-count comparison is only
valid when both operands are in the same encoding. One operand came from a filesystem with
`autocrlf=true`; the other came from a git object. **They were never comparable as raw lengths.**

**And a second one inside the same probe, which very nearly published a false all-clear:** my first
correction attempt used `$false` and `$real` as counter variables. **`$false` is a read-only
PowerShell automatic variable**, so the increments threw and the probe printed
`REAL mismatches: 0` from a counter that had never run. **A zero from a counter that cannot
increment is not a zero.** Re-run under `$nFalse` / `$nReal` and the answer was the same — but the
first run's agreement was an accident, and it is only because the arithmetic was independently
checkable that the difference was visible at all.

## Where this check is still required

The gap it caught previously was real: `D61` and `D72` were committed at **intermediate** states
and edited afterwards, and `D69` was untracked. `git cat-file -s` distinguished *"the lane
over-reported"* from *"the work was never committed"* — a distinction no other instrument here
makes.

**Corrected results, round 21, all 84 D-numbered reports:**
```
FALSE mismatches (CRLF artifact): 1
REAL mismatches:                  0
```

*Supersedes the naive form used in earlier rounds.*
