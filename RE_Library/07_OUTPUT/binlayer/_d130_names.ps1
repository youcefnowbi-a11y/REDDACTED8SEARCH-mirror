$ErrorActionPreference = 'Continue'
$R  = "C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
$bl = Join-Path $R "RE_Library\07_OUTPUT\binlayer"

function NamesMatching {
  param($file, $regex, $label)
  Write-Output ""
  Write-Output ("=== {0} ===" -f $label)
  if (-not (Test-Path $file)) { Write-Output "  OPERAND MISSING"; return }
  $rows = @(Get-Content $file) | Where-Object { $_ -notmatch '^#' -and $_.Trim().Length -gt 0 }
  Write-Output ("  OPERAND {0}  data rows {1:N0}" -f (Split-Path $file -Leaf), $rows.Count)
  $names = $rows | ForEach-Object { ($_ -split "`t")[1] }
  $hit = @($names | Where-Object { $_ -match $regex })
  Write-Output ("  MATCHING NAMES: {0}  (distinct {1})" -f $hit.Count, @($hit | Sort-Object -Unique).Count)
  $hit | Sort-Object -Unique | ForEach-Object { Write-Output ("      " + $_) }
}

$agent = Join-Path $bl "_lead_pclntab_merlinAgent-Windows-x64.exe.tsv"
$cli   = Join-Path $bl "_lead_pclntab_merlinCLI-Windows-x64.exe.tsv"
$dll   = Join-Path $bl "_lead_pclntab_merlin.x64.dll.tsv"

Write-Output "########################################################"
Write-Output "# P4 -- the ACTUAL names carrying path derivation"
Write-Output "########################################################"
NamesMatching $agent 'Executable|filepath|Path|Dir|Split|GetFilepath|Magic' "AGENT: path/executable/derivation names"
NamesMatching $dll   'os\.Executable|Magic|Magics|main\.'                        "merlin.x64.dll: Executable + Magic surface"

Write-Output ""
Write-Output "########################################################"
Write-Output "# P5b -- main.* surface across the binaries (8 in agent)"
Write-Output "########################################################"
NamesMatching $agent '^main\.' "AGENT main.*"
NamesMatching $cli   '^main\.' "CLI   main.*"

Write-Output ""
Write-Output "########################################################"
Write-Output "# P2 -- what escaping-shaped names EXIST"
Write-Output "########################################################"
NamesMatching $agent 'Escape|Quote|Shell' "AGENT escape/quote/shell"
NamesMatching $cli   'Escape|Quote|Shell' "CLI   escape/quote/shell"

Write-Output ""
Write-Output "########################################################"
Write-Output "# P1 -- ownership / session filter names"
Write-Output "########################################################"
NamesMatching $agent 'Ownership|Filter|Session' "AGENT ownership/filter/session"

Write-Output ""
Write-Output "=== END NAMES ==="
