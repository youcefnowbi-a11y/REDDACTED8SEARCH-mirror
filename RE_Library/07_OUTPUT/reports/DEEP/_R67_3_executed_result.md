# R-67.3 EXECUTED — YamlDotNet 8.1.1 unknown-enum behaviour

**Status: CLOSED. Run, not inferred.** Owner: Lead. Date: round 21.

## Why this existed

D67 §3.5 raised a third row it could not adjudicate statically: if an unrecognised
`TaskingType` **coerces to the enum default** rather than throwing, then any malformed task
definition lands on the `TaskExecute` path, and the row was a finding. If it throws, the row is
a non-event. D67 marked it **R-67.3 — the highest-value residual in that lane** and named the
deciding instrument ("a five-line fixture"). It was assumed unrunnable.

**It was runnable.** `.NET SDK 8.0.425` is installed at `C:\Program Files\dotnet`. This is
itself an instrument failure of the *assumption* kind: "we have no .NET runtime" was carried as
fact across several rounds without a probe.

## Instrument

- `dotnet` SDK **8.0.425**, `net8.0` target, TOOL NAMED.
- **`YamlDotNet 8.1.1`** — the version is not assumed. It was read from the corpus:
  `RE_Library\01_SOURCE_c2\covenant\Covenant\Covenant.csproj:46`
  `<PackageReference Include="YamlDotNet" Version="8.1.1" />`
- NuGet cache confirmed to resolve **8.1.1** (`~\.nuget\packages\yamldotnet\8.1.1`).
- Deserializer constructed **exactly as `DbInitializer.cs:404` does**:
  `new DeserializerBuilder().Build()` — bare, no options.
- Model mirrors `SerializedGruntTask` (`TaskingType` enum + `TokenTask` bool).
- Fixture at `%TEMP%\yamltest`, build exit 0, run exit 0.

## Result

| # | input | outcome | note |
|---|---|---|---|
| 1 | `TaskingType: Assembly` | **NO-THROW** → `Assembly` (0) | valid baseline |
| 2 | `TaskingType: Assembaly` | **THREW `YamlException`** | **D67's actual question** |
| 3 | `TaskingType: Script` | NO-THROW → `Script` (1) | valid |
| 4 | `TaskingType: 99` | **NO-THROW → `(TaskingType)99`** | out of range, accepted |
| 5 | `TaskingType: assembly` | **NO-THROW → `Assembly` (0)** | case-folds |
| 6 | `TaskingType: "Nonsense"` | **THREW `YamlException`** | |
| 7 | unknown key `BogusKey: 7` | **THREW `YamlException`** | not ignored |
| 8 | misspelled enum, single object | **THREW `YamlException`** | list-wrapper independent |

## Verdict on D67 §3.5 third row

**NON-EVENT.** An unrecognised enum *name* throws; it does not coerce to the default. Malformed
tasking data does not silently reach the `TaskExecute` path by way of a misspelled type name.
R-67.3 closes **against** the finding.

## Three results D67 did not ask for, and they outrank the answer

1. **An unknown KEY also throws (case 7).** D67 §3 correctly recorded that all 14 deserializer
   sites in the tree are bare — `DeserializerBuilder().Build()`, zero `IgnoreUnmatchedProperties`
   anywhere. The measurement was right; **its consequence was unstated.** A task definition
   carrying any field the C# model lacks is not partially ignored — it **fails the entire
   deserialization**. D67 aimed its probe at the *value*; on this evidence the *key* is the
   stricter surface. **This is the real replacement candidate for R-67.3's slot.**
2. **`99` is accepted and stored as `(TaskingType)99` (case 4).** No range validation. The
   guard that rejects unknown names does **not** reject out-of-range numerics.
3. **`assembly` case-folds to `Assembly` (case 5).** So "unknown input is rejected" is true for
   names and false for case variants and numbers.

**Honest summary: throws on unknown names; silently accepts out-of-range numerics.**
The finding did not vanish — it moved to a narrower and better-specified slot.

## Bounds

- Establishes **YamlDotNet 8.1.1's** behaviour for this model. Not a claim about other versions.
- The fixture is a **minimal reproduction of the call shape**, not Covenant's full loader; the
  real `:399-415` path wraps this call in its own error handling, which was not exercised.
  Whether the thrown `YamlException` is caught and downgraded there is **not measured** — and
  that is the natural next probe, since a caught exception would restore the silent path.
- `%TEMP%\yamltest` is outside the repo; no corpus file was modified by this probe.

*End of R-67.3 result.*