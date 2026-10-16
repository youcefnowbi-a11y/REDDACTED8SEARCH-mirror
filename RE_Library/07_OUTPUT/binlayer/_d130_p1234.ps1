$ErrorActionPreference = 'Continue'
$R  = "C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
$bl = Join-Path $R "RE_Library\07_OUTPUT\binlayer"
$src = Join-Path $R "RE_Library\01_SOURCE_c2\sliver"

function Probe {
  param($label, $file, $patterns)
  Write-Output ""
  Write-Output ("--- {0} ---" % [char]0) | Out-Null
  Write-Output ("--- {0}" -f $label)
  if (-not (Test-Path $file)) { Write-Output "  OPERAND MISSING: no verdict."; return }
  $lines = @(Get-Content $file)
  Write-Output ("  OPERAND: {0}  lines {1:N0}" -f (Split-Path $file -Leaf), $lines.Count)
  if ($lines.Count -eq 0) { Write-Output "  EMPTY OPERAND: no verdict."; return }
  # CONTROL pair: one token certain to exist, one certain not to.
  $ctlPos = ([regex]::Matches(($lines -join "`n"), 'a')).Count
  $ctlNeg = ([regex]::Matches(($lines -join "`n"), 'ZZQQXX_NO_SUCH_TOKEN_9931')).Count
  Write-Output ("  CONTROL  always-present 'a' = {0:N0}   never-present token = {1}   (need >0 and 0)" -f $ctlPos, $ctlNeg)
  if ($ctlPos -le 0 -or $ctlNeg -ne 0) { Write-Output "  CONTROL FAILED -> reader dead, no verdict."; return }
  foreach ($p in $patterns) {
    $n = ([regex]::Matches(($lines -join "`n"), $p)).Count
    Write-Output ("    '{0,-34}' -> {1:N0}" -f $p, $n)
  }
}

Write-Output "=============================================================="
Write-Output "P1/P2/P3/P4 -- pair probes against the PCLNTAB name tables"
Write-Output "  (C-05/C-06/C-07 Ghidra TSVs are named=1 -> USELESS for names."
Write-Output "   pclntab TSVs carry real Go names; control shown per file.)"
Write-Output "=============================================================="

$agent = Join-Path $bl "_lead_pclntab_merlinAgent-Windows-x64.exe.tsv"
$dbg   = Join-Path $bl "_lead_pclntab_merlinAgent-Windows-x64-Debug.exe.tsv"
$cli   = Join-Path $bl "_lead_pclntab_merlinCLI-Windows-x64.exe.tsv"
$srv   = Join-Path $bl "_lead_pclntab_merlin.x64.dll.tsv"

# ---------- P3 : the D89 nil-deref guard, BOTH builds ----------
Write-Output ""
Write-Output "########## P3 -- D89 nil-deref: is the guard still in the compiled binary? ##########"
Probe "agent RELEASE  main.* and ToMap surface" $agent @('main\.', 'ToMap', 'GetToMap', 'addCommandsFromFile', '5253', 'nil', 'Magics', 'Merlin')
Probe "agent DEBUG    same" $dbg @('main\.', 'ToMap', 'GetToMap', 'addCommandsFromFile', '5253', 'nil', 'Magics', 'Merlin')

# ---------- P4 : os.Executable and path derivation ----------
Write-Output ""
Write-Output "########## P4 -- D93 Split(bin)[0] path derivation ##########"
Probe "agent RELEASE  Executable/path" $agent @('os\.Executable', 'Executable', 'filepath\.', 'path\.Dir', 'path\.Base', 'GetFilepath', 'Dir\b', 'Split', 'bin')
Probe "CLI Windows    Executable/path" $cli   @('os\.Executable', 'Executable', 'filepath\.', 'path\.Dir', 'path\.Base', 'GetFilepath', 'Split', 'bin')
Probe "merlin.x64.dll Executable/path" $srv   @('os\.Executable', 'Executable', 'filepath\.', 'path\.Dir', 'path\.Base', 'GetFilepath', 'Split', 'bin')

# ---------- P2 : escaping helpers ----------
Write-Output ""
Write-Output "########## P2 -- D85 escaping helper: linked in or eliminated? ##########"
Probe "agent RELEASE  escaping" $agent @('ShellQuote', 'shellEscape', 'escapeShell', 'QuoteArg', 'SingleQuote', 'Escape', 'Quote')
Probe "CLI Windows    escaping" $cli   @('ShellQuote', 'shellEscape', 'escapeShell', 'QuoteArg', 'SingleQuote', 'Escape', 'Quote')

# ---------- P1 : ownership filter ----------
Write-Output ""
Write-Output "########## P1 -- D91 ownership filter ##########"
Probe "agent RELEASE  ownership" $agent @('Ownership', 'ownership', 'Filter', 'GetSessions', 'IsSessionOwned')

Write-Output ""
Write-Output "=== END P1-P4 ==="
