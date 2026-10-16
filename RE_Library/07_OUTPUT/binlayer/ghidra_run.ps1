# ghidra_run.ps1 -- the WORKING, verified Ghidra headless invocation.
#
# Replaces run_ghidra.bat. Five batch-quoting attempts each failed for a
# different reason; this form is proven. Failure modes recorded so nobody
# repeats them:
#
#   1. name=probe location=...  -> InvalidInputException: Bad argument.
#      analyzeHeadless takes <projDir> <projName> POSITIONALLY.
#   2. missing project directory -> Abort, Directory not found.
#      analyzeHeadless does NOT create the project directory.
#   3. -readOnly -> prints 'Analysis succeeded', THEN
#      'Discarded file import due to readOnly option'. Exit 0, analysis gone.
#      It is a do-not-persist flag, NOT a no-prompt flag.
#   4. setlocal in the .bat -> scopes env vars away from the child process.
#   5. spaced script args -> 'Bad argument: REDDACTED\RE_Library\...'
#      Ghidra 12.1.4 splits script args at the space even when quoted, so the
#      output MUST be staged through a space-free temp path and copied back.
#   6. -noanalysis -> function manager is EMPTY, total=0. Correct behaviour,
#      but it silently makes the census report zero.
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File ghidra_run.ps1
#       -Target <binary> -Out <tsv> [-Script DumpSyms.java] [-AnalysisSeconds N]

param(
    [Parameter(Mandatory=$true)][string]$Target,
    [Parameter(Mandatory=$true)][string]$Out,
    [string]$Script = "DumpSyms.java",
    [int]$AnalysisSeconds = 1800,
    [switch]$KeepProject
)

$ErrorActionPreference = "Continue"
$ghidra    = "C:\tools\ghidra_12.1.4_PUBLIC"
$support   = Join-Path $ghidra "support"
$headless  = Join-Path $support "analyzeHeadless.bat"
$scriptDir = $PSScriptRoot

if (-not (Test-Path $Target))    { Write-Error "target not found: $Target"; exit 3 }
if (-not (Test-Path $headless))  { Write-Error "analyzeHeadless not found: $headless"; exit 4 }
if (-not (Test-Path $scriptDir)) { Write-Error "script dir not found: $scriptDir"; exit 5 }

# Failure 2: the project directory must pre-exist.
$tag     = [guid]::NewGuid().ToString("N").Substring(0,12)
$projDir = Join-Path $env:TEMP ("ghproj_" + $tag)
New-Item -ItemType Directory -Force -Path $projDir | Out-Null
if (-not (Test-Path $projDir)) { Write-Error "could not create project dir"; exit 5 }

# Failure 5: stage through a space-free path.
$stage = Join-Path $env:TEMP ("ghout_" + $tag + ".tsv")
if (Test-Path $stage) { Remove-Item $stage -Force }
$log = Join-Path $env:TEMP ("ghrun_" + $tag + ".log")
$err = $log + ".err"

$argv = @(
    "/c", "`"$headless`"",
    "`"$projDir`"", "ghprobe",
    "-import", "`"$Target`"",
    "-analysisTimeoutPerFile", "$AnalysisSeconds",
    "-scriptPath", "`"$scriptDir`"",
    "-postScript", $Script, "`"$stage`""
)

Push-Location $support
$p = Start-Process -FilePath "cmd.exe" -ArgumentList $argv -NoNewWindow -Wait -PassThru `
        -RedirectStandardOutput $log -RedirectStandardError $err
Pop-Location

$rc = if ($p) { $p.ExitCode } else { 1 }

if (Test-Path $stage) {
    $parent = Split-Path $Out -Parent
    if ($parent -and -not (Test-Path $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    Copy-Item $stage $Out -Force
    Remove-Item $stage -Force
} else {
    Write-Warning "script produced no output at $stage"
    if ($rc -eq 0) { $rc = 7 }
}

Get-Content $log -ErrorAction SilentlyContinue |
    Select-String -Pattern 'EXPORTED_FUNCTIONS|NAMED_FUNCTIONS|THUNKS|TOTAL_BODY_BYTES|Analysis succeeded|Untested Go version|bootstrap type' |
    ForEach-Object { $_.Line.Trim() }

if ($KeepProject) { Write-Host "PROJECT_KEPT=$projDir" }
else { Remove-Item $projDir -Recurse -Force -ErrorAction SilentlyContinue }
Write-Host "GHIDRA_EXIT=$rc"
exit $rc
