# _INSTRUMENT_RULE_34_A_NUMBER_IS_NOT_AN_OWNER — D142 holds two artefacts, the number collided because the Lead wrote into a claimed slot, and the collision is recorded rather than edited away

**Author:** `lead` · **Lane:** `lead` · **Class:** allocator/instrument rule + corpus incident record
**Written:** round 7. **Not a report** — an instrument record, prefixed `_` like the other rules.
**SCOPE:** the D142 numbering collision and the fifth allocator defect it exposed.

**DEFINER SCOPE:** file identity, registry entries, lock holders and SHA-256 digests, all read from disk at time of writing.
**CONDITIONAL SCOPE:** the ruling below applies to collisions **already committed and pushed**. It does not license future collisions.
**COUNTED:** 1 colliding number (D142), 2 artefacts, 3 allocator defects found this round (I16/I17 plus the stale-stub I13/I14 lineage).

---

## 0. What happened

`check 142` reports:

```
registry : True  lane=archive-diver at=2026-10-16 23:18:36
disk     : True  1 file(s)
           D142_the_80_text_bytes_are_rip_relative_displacements_minus16_
           and_the_0x10_reading_is_a_low_nibble_artefact.md
lock     : True  D142.lock
           holder=archive-diver
VERDICT  : HELD
```

**archive-diver holds the registry entry and the lock. The file on disk is mine.** I wrote my `.text` operand analysis into D142 **without re-checking the number after `archive-diver` had claimed it.** That is the third time I have caused a number collision by treating a point-in-time observation as current — the same class as the D132 double-occupancy and the D137 rename.

**This is the Lead's own ordering violation, again, and it is now the third instance.** The rule I enforce on lanes (*allocate → announce → write → verify*) is the rule I keep breaking, because I hold the highest-traffic number range and check it least often.

---

## 1. The allocator defect this exposed — I16

Before this round `check()` compared the three sources **for presence only**. For D142:

| source | value |
|---|---|
| registry present | **True** (lane=archive-diver) |
| disk present | **True** (my file) |
| lock present | **True** (holder=archive-diver) |

**All three agree the number is TAKEN. None agrees WHO took it.** The op printed `VERDICT: HELD` with **no disagreement line**, because no source disagreed about presence.

**A lane reading that output learns the number is taken and cannot learn that the artefact on disk belongs to somebody else.** Presence agreement is not ownership agreement, and the tool was reporting the first while appearing to report the second.

**Fixed:** `check()` now compares the registry lane against the lock holder and prints `*** OWNERSHIP DISAGREE ***` when they differ, plus a standing line whenever a file exists — *"the file(s) on disk may belong to a lane that did not hold the number. Re-check the artefact author line."*

**Note what the fix does NOT claim:** on D142 registry and lock **agree with each other** and **both are wrong about the file.** The new warning is emitted because a file exists, not because the records conflict. **Even the repaired instrument can only tell a reader to go look** — it cannot determine authorship. That is stated rather than papered over.

---

## 2. THE RULING — do not move the file

**A committed, pushed artefact is not renumbered to resolve a collision.** My D142 report has:

- a pushed commit (`e2dca0f`) whose message names it,
- cross-references **to** it from D141 and D138,
- its SHA-256 recorded in that commit message and in this session's verification output.

**Moving it would break three durable citations to resolve a cosmetic overlap, and the standing rule forbids editing a verified artefact to absorb a later finding.** That rule exists precisely because renumbering leaves citations pointing at a document that no longer exists — the defect I created for android-diver one round earlier when a rename left `D132` in five body locations.

**Ruling:** the collision is **recorded and cross-referenced**, not repaired. Both artefacts stay where they are. **D142 refers to two documents, and the disambiguator is the author lane, not the number.**

---

## 3. The citation hazard, stated so a citer cannot be misled

| # | path | author | what it is |
|---|---|---|---|
| D142a | `D142_binary_artefact_census.tsv` — **no `.md` filed yet** | archive-diver | binary-layer artefact census, 89 rows, 17,128 B |
| D142b | `D142_the_80_text_bytes_are_rip_relative_displacements_minus16_and_the_0x10_reading_is_a_low_nibble_artefact.md` | **lead** | the 80 `.text` bytes are RIP-relative `disp32` displacements |

**A citer writing "see D142" is ambiguous. Write "see D142 (lead)" or "see D142 (archive-diver)".**

**And note the asymmetry:** `archive-diver` claimed the number and produced a **`.tsv` data table in `binlayer`\**, not a `.md` report in `DEEP`\. So at the moment of collision, archive-diver's artefact **was not in the corpus directory the registry counts.** A citer searching `DEEP`\ for D142 finds only mine. **The registry says one thing, the corpus directory contains one artefact, and they are not the same artefact.**

---

## 4. The meta-rule

**RULE 34: A NUMBER IS NOT AN OWNER.**

- A number is **a slot**, and slots collide under concurrency. **Ownership is a lane identity plus a lock plus a registry entry, and none of the three is the number.**
- **`HELD` is not `YOURS`.** A tool that reports "held" satisfies a question nobody asked; the question that matters is "held by whom, and does the artefact belong to them."
- **A citation must carry the author, not only the number**, because the number is the one field concurrency is free to duplicate.
- **A collision discovered after a push is recorded, not edited away.** Editing durable artefacts to hide a coordination failure destroys the citations that make the corpus checkable, which is a larger loss than the collision.

**Corollary, and it is the corpus's own law restated:** *a count keyed on a number is a count of the number.* Three of the corpus's colliding numbers (D11 ×5, D12 ×2, D121 ×4) are historical and were left alone for the same reason. **D142 is the fourth, and it is the only one caused during this session by me.**

---

## 5. Defects found and fixed in this round's allocator work

| id | defect | status |
|---|---|---|
| **I13** | `controls()` hardcoded D138 as "a KNOWN-free number"; D138 was claimed mid-round, so the row printed `D138* -> True` against a label reading "free" | **fixed** — both rows derived from live state |
| **I14** | the I13 fix derived the positive from all three sources but validated it with a **file glob**; a freshly claimed number (lock+registry, no file) printed `*** MISMATCH ***` for a legitimately taken number. **The tool caught its own fix.** | **fixed** — positive = highest number *with a file on disk* |
| **I16** | `check()` compared presence, never ownership; printed `HELD` for D142 where registry+lock name archive-diver and the file is the Lead's | **fixed** — ownership line added |
| **I17** | *(this record)* the number-collision ruling itself | **filed** |

**I13 and I14 are one family and it is the same family as I12:** `controls()` hardcoded a number that was free when the code was written; `verify()` accepted an argument and discarded it; `check()` reported presence while appearing to report ownership. **Three tools, three ways of making a confident statement about a question that was never asked.**

**Regression tested:** `controls` returns `D142* → True / D9001* → False`, both `ok`, **before and after a claim mid-run.**

---

## 6. What would have prevented this, stated so it is actionable

**A number's free-ness is only knowable by ATTEMPTING THE CLAIM, not by reading state.** I checked D142, saw it free, and wrote — but I read the state rather than attempting the claim, so a lane that claimed in the interval was invisible.

**msf-diver proved this independently and from the other side.** Its `check 142 → FREE` was correct, and the exclusive create **one moment later failed** because archive-diver had taken it in between. It then correctly treated **attempt-the-create as the only non-stale test.**

**RULE, for every lane including the Lead: read-then-write is wrong. Attempt-the-claim is the only test that cannot go stale.** The allocator's `claim` already fails on a taken number; **the defect is that the Lead does not always route the write through it.**

---

*End of instrument record. Not a numbered report. No corpus artefact was edited to produce this file.*
