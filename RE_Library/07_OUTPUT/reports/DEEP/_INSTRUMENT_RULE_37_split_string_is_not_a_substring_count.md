# _INSTRUMENT_RULE_37_split_string_is_not_a_substring_count — `String.Split(String)` binds to `Split(char[])` in .NET Framework, so a substring census silently counts individual letters

**Author:** `lead` · **Class:** instrument defect (Lead, round 8)
**Not a numbered report.**
**SCOPE:** any substring count performed in PowerShell via `String.Split`.
**DEFINER SCOPE:** `[System.String]::Split` under PowerShell 5.1 on .NET Framework 4.x, where **the `Split(String)` overload does not exist.**
**CONDITIONAL SCOPE:** the defect is PowerShell/CLR-specific. An `IndexOf` loop or Python `str.count` is unaffected.
**COUNTED:** the demonstration below uses two operands of known content; no corpus census is claimed.

---

## 0. The defect

```powershell
$raw.Split('runtime.').Count - 1     # <-- intends "occurrences of runtime."
```

**There is no `Split(String)` overload in .NET Framework.** PowerShell therefore binds the argument to the **`Split(char[])`** overload — and a single `string` coerces to `char[]` by **being exploded into its own characters.**

```
'runtime.'  ->  [ 'r', 'u', 'n', 't', 'i', 'm', 'e', '.' ]
```

**The expression then splits the haystack on any of those eight characters and counts the pieces.** The result is not the count of `runtime.`; it is **the count of the letters r, u, n, t, i, m, e and the period, combined.** In any real Go symbol table those characters are everywhere, so the number is **large, plausible, and meaningless.**

---

## 1. The demonstration, with operands of known content

**Haystack:** the three-character-class string `runtime.fmt.gorm`. The literal `runtime.` occurs in it **exactly once.**

| method | result | correct? |
|---|---:|---|
| `'runtime.fmt.gorm'.Split('runtime.').Count - 1` | **13** | ❌ **wrong by 12** |
| ordinal `IndexOf` loop advancing by `$needle.Length` | **1** | ✅ |

**13 is the count of the eight delimiter characters in a 16-character string.** It is not a rounding error and not an edge case — it is a different quantity with no relationship to the intended one.

---

## 2. THE RULE

**RULE 37: IN POWERSHELL, `String.Split` IS NOT A SUBSTRING COUNT. USE AN ORDINAL `IndexOf` LOOP.**

```powershell
function Count-Lit([string]$hay, [string]$needle) {
    $c = 0; $i = 0
    while (($i = $hay.IndexOf($needle, $i, [System.StringComparison]::Ordinal)) -ge 0) {
        $c++; $i += $needle.Length
    }
    return $c
}
```

**Requirements on the replacement, each of which matters:**
- **`Ordinal`** — `CurrentCulture` lets the collation decide what matches. **A count that changes with the collation of its comparator is a count of the comparator** (already a filed law, D128).
- **advance by `$needle.Length`, not by 1** — advancing by 1 counts **overlapping** occurrences, which is a different number. For `aa` in `aaa`, overlap-counting gives 2 and true occurrence-counting gives 1.
- **`-ge 0`, never `-gt 0`** — a match at offset 0 is a match.

**In Python the equivalent is safe:** `txt.count(sym)` is a non-overlapping literal substring count. **PowerShell has no equivalently safe one-liner** — which is precisely why the reflex is dangerous here.

---

## 3. How it was caught, and why the control is the whole story

**I used this expression to re-measure D145's central absence claim — the Lead's independent verification of a lane's number.** Every "absence" probe returned a large count, and a reader skimming would have concluded **D145 was refuted.**

**What caught it was one probe with a string that cannot exist:**

```
ZZQQ_NO_SUCH_SYMBOL_ANYWHERE  ->  182,221
```

**A count of a string that cannot be present is a count that cannot be true.** No reasoning about D145, no reading of its report, and no comparison against its published numbers was needed. **The control failed, and the failure identified the instrument rather than the target.**

**Without it, the sequence would have run:** my probe reports `sliver/server = 2,268,606` → D145 appears to be contradicted → D145 is "corrected" → **a correct report is damaged by a broken reader.** That is **Rule 35's species exactly** (*a corruption report must name the bytes, not the rendering*) — the second time in two rounds that a defective reader would have produced a destructive edit to a byte-clean artefact.

---

## 4. Position in the family

**This is the twelfth-plus instance of the standing family:** *an instrument returns a confident wrong answer instead of failing.*

**What makes it a distinct member is the direction of the plausible error.** Prior members failed toward **zero** (`named=1`, the zero-heading counter, the `-SimpleMatch` + `[regex]::Escape` pair in D145 §1) — and a zero reads as an absence, which is at least *conservatively wrong.* **Rule 37 fails toward a LARGE number, and a large number reads as a positive finding.** A false positive that looks like evidence is more expensive than a false zero that looks like an absence, because **an absence invites a second look and a positive does not.**

**And note which guard made it look safer:** the same as D145 §1.2. `-SimpleMatch` was added as a **correctness measure** and is what broke that probe. Here, `.Count - 1` was written as an **arithmetic safety** and the overload binding is what broke this one. **In both cases the author added something that made the code read as more careful while making it wrong.**

---

## 5. The measurable result, since the instrument was rebuilt

**After the fix, D145 reproduces digit for digit:**

| probe | my count | D145's count | agree |
|---|---:|---:|---|
| `github.com/bishopfox/sliver/server` | **0** | **0** | ✅ |
| `github.com/bishopfox/sliver/client` | **3,104** | **3,104** | ✅ |
| `github.com/bishopfox/sliver/protobuf` | **4,739** | **4,739** | ✅ |
| `runtime.` | **1,523** | **1,523** | ✅ |
| `fmt.` | **118** | **118** | ✅ |
| `AIConversationByID` | **0** | **0** | ✅ |
| `AIConversationsByOperator` | **0** | **0** | ✅ |
| `aiOperatorName` | **0** | **0** | ✅ |
| `getClientCommonName` | **0** | **0** | ✅ |
| `operator_name` | **0** | **0** | ✅ |
| `gorm` | **0** | **0** | ✅ |
| `DeleteAIConversation` | **3** | **3** | ✅ |
| `SaveAIConversation` | **6** | **6** | ✅ |

**D145's central absence claim is INDEPENDENTLY CONFIRMED.** The operand was proven non-empty before any zero was reported (3,476,900 B), and the impossible-string control returns **0**.

**One discrepancy, disclosed:** my operand read is **3,476,900 B**; D145 §1.4 reports **3,476,902 B** and its SHA-256 is `06B96ECF…505E`, which **my file's hash matches exactly.** A 2-byte difference in a reported length against an identical digest means **one of the two length figures is a line-ending or reader artefact, and the digest is authoritative.** I did not resolve it; it changes no count, and **the digest agreeing is what makes the disagreement harmless.** Filed as R-37.1.

---

## 6. Status

- **Rule filed.** The fix is in the function above and is what produced §5.
- **No artefact edited.** This report exists because an instrument of mine was wrong, not because a target was.
- **R-37.1** — the 2-byte operand-length discrepancy between my read (3,476,900 B) and D145 §1.4 (3,476,902 B), **with identical SHA-256 `06B96ECF…505E`.** Digest is authoritative; the length is a reader property.
- **NEXT MEASUREMENT, named:** **every prior count in this session produced by a `Split`-based expression is unverified**, and I have not audited them. The safe forms are `IndexOf` loops (PowerShell) and `str.count` (Python); the unsafe form is `Split`. **A sweep of the Lead's own instruments for `.Split(` used as a counter is the obvious next probe and is not done here.**

---

*End of instrument record. No corpus artefact edited to produce this file.*
