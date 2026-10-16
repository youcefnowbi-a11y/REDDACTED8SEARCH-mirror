# _INSTRUMENT_RULE_29_a_filename_is_not_an_authorship

**Filed:** round 25. **Trigger:** a real Lead coordination error, caught by a lane that refused to act on it.

**Tags:** `[verified]` (measured) · `[inferred]` (reasoning over evidence).
**Write scope:** this file only.

---

## §0 The error

`[verified]` **I addressed the D100 TOC-fix task to `android-diver` twice. D100 was written by `covenant-diver`.**

`[read]` The measured attribution lines:

```
D100_android_binary_layer_manifest_dex_signing_and_native_census.md
  **Author:** `covenant-diver` · **Round:** 24 · **Report:** D100

D97_android_wasm_assembler_sqlite_vfs_and_jvm_tooling.md
  **Lane:** android-diver

D87_android_release_manifest_floor_and_guard.md
  **Scope owner:** android-diver
```

`[verified]` **Both D100 and D97 first appear in the same commit `c15b383`**, so `git log --diff-filter=A` cannot separate them — both return the identical commit line.

`[inferred]` **I resolved the ambiguity from the filename prefix `D100_android_*` rather than from the author line.** Both files carry "android" in the name and share a commit, so the name was the only remaining signal — and it was the wrong one.

## §1 The consequence, and it is not just a mis-route

`[verified]` The lane refused to edit the file, on the correct ground that it does not own it.

`[verified]` **And it refused to accept my attribution of the mid-round size drift** — the 25,076 → 24,722 → 26,324 B sequence I reported as "android-diver still writing." `[verified]` The live writer was `covenant-diver`.

`[inferred]` **This is the part that matters: the LESSON was correct and the ATTRIBUTION was wrong, and a lesson with the wrong attribution is not reusable.** The lane said it exactly — *"the lesson is only reusable if the writer is correctly identified."* A rule that says "watch for a lane editing its own file mid-measurement" is worthless if the named lane is not the writer.

`[inferred]` **The instrument note is corrected and the lesson survives, reattributed.**

## §2 The rule

`[inferred]` **A FILENAME IS A CLAIM, NOT A MEASUREMENT — and this applies to AUTHORSHIP, not just to existence.**

`[inferred]` **The corpus already had this rule for paths and counts** (rule 15, a path constructed from a NAME instead of an ENUMERATION; rule 22, a NAMED PATH IS NOT A CENSUS). **Authorship is the same shape one level up: two artifacts with a shared filename substring, landing in one commit, will be attributed by whoever writes first and asks second.**

`[inferred]` **MANDATORY: attribute a document from its own author line, never from its filename and never from its commit.** The author line is a measurement the document carries; the filename is a label applied by an allocator.

`[inferred]` **Second-order: a batched commit destroys authorship attribution for every file in it.** `c15b383` carries six reports from five lanes. Any later question of the form "which lane wrote this" is unanswerable from git alone. **Where authorship matters, commit per lane — or rely on the author line and say so.**

## §3 Why this one is worth a file

`[inferred]` **The failure occurred in a COORDINATION MESSAGE, where no probe gates it.** Every other defect in this corpus was caught by a measurement somewhere. **This one had no instrument at all — I typed a lane's name into a task brief and nothing in the pipeline tests that.** The lane caught it by knowing its own work.

`[inferred]` **The generalisable form: the workflow itself is an instrument, and it needs controls.** A brief that names an owner is a claim about the filesystem. **It can be checked in one line, and it is now checked.**

`[inferred]` **Sharpest statement: an unverified attribution in a work order is more dangerous than an unverified claim in a report, because the report is read by auditors and the work order is not.**

## §4 The control, adopted

`[inferred]` **Before assigning a fix to any lane, read the target's author line.** One `Select-String` for `Author:|Lane:|Scope owner:` over the first few lines of the file. This would have caught it in the first round.

**End of rule 29.**
