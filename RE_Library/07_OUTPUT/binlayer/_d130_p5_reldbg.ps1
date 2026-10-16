# Write to a file and run; PowerShell 5.1, no inline if-expressions.
$ErrorActionPreference = 'Continue'
$R  = "C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
$bl = Join-Path $R "RE_Library\07_OUTPUT\binlayer"

Write-Output "=============================================================="
Write-Output "P5 -- RELEASE vs DEBUG row-identity control  (THE UNRUN CONTROL)"
Write-Output "=============================================================="
$rel = Join-Path $bl "_lead_pclntab_merlinAgent-Windows-x64.exe.tsv"
$dbg = Join-Path $bl "_lead_pclntab_merlinAgent-Windows-x64-Debug.exe.tsv"

# --- OPERAND ACQUISITION CHECK FIRST ---
$a = Test-Path $rel; $b = Test-Path $dbg
Write-Output ("  OPERAND CHECK  release exists: {0}   debug exists: {1}" -f $a, $b)
if (-not $a -or -not $b) { Write-Output "  ABORT: operand missing -- any verdict below would be fiction."; exit 1 }
$rl = @(Get-Content $rel); $dl = @(Get-Content $dbg)
Write-Output ("  OPERAND CHECK  release lines: {0}   debug lines: {1}" -f $rl.Count, $dl.Count)
if ($rl.Count -eq 0 -or $dl.Count -eq 0) { Write-Output "  ABORT: empty operand."; exit 1 }
Write-Output ("  release[0]: {0}" -f $rl[0])
Write-Output ("  debug[0]  : {0}" -f $dl[0])

# --- compare FULL FILE ---
$sameAll = ($rl -join "`n") -ceq ($dl -join "`n")
Write-Output ("  FULL-FILE case-sensitive identical : {0}" -f $sameAll)

# --- header lines (start with '#') ---
$rh = @($rl | Where-Object { $_.StartsWith('#') })
$dh = @($dl | Where-Object { $_.StartsWith('#') })
Write-Output ("  header lines   release {0}   debug {1}" -f $rh.Count, $dh.Count)
for ($i = 0; $i -lt [Math]::Max($rh.Count, $dh.Count); $i++) {
  $x = ""; if ($i -lt $rh.Count) { $x = $rh[$i] }
  $y = ""; if ($i -lt $dh.Count) { $y = $dh[$i] }
  $m = "SAME"
  if ($x -cne $y) { $m = "*** DIFFER ***" }
  Write-Output ("    hdr[{0}] {1}" -f $i, $m)
  if ($x -cne $y) { Write-Output ("        rel: {0}" -f $x); Write-Output ("        dbg: {0}" -f $y) }
}

# --- data rows ---
$rd = @($rl | Where-Object { -not $_.StartsWith('#') -and $_.Trim().Length -gt 0 })
$dd = @($dl | Where-Object { -not $_.StartsWith('#') -and $_.Trim().Length -gt 0 })
Write-Output ("  DATA ROWS      release {0}   debug {1}" -f $rd.Count, $dd.Count)

# --- ROW-FOR-ROW, three independent axes ---
$rowIdentical = $false
if ($rd.Count -eq $dd.Count) { $rowIdentical = (($rd -join "`n") -ceq ($dd -join "`n")) }
Write-Output ("  ROW-FOR-ROW case-sensitive identical : {0}" -f $rowIdentical)

# names only (col 2)
$rn = @($rd | ForEach-Object { ($_ -split "`t")[1] })
$dn = @($dd | ForEach-Object { ($_ -split "`t")[1] })
$nameSame = (($rn -join "`n") -ceq ($dn -join "`n"))
Write-Output ("  NAMES-ONLY, order preserved identical: {0}" -f $nameSame)
$nameSortedSame = (((($rn | Sort-Object) -join "`n")) -ceq ((($dn | Sort-Object) -join "`n")))
Write-Output ("  NAMES-ONLY, sorted set identical     : {0}" -f $nameSortedSame)

# offsets only (col 1)
$ro = @($rd | ForEach-Object { ($_ -split "`t")[0] })
$do = @($dd | ForEach-Object { ($_ -split "`t")[0] })
$offSame = (($ro -join "`n") -ceq ($do -join "`n"))
Write-Output ("  OFFSETS-ONLY, order identical        : {0}" -f $offSame)

# --- locate the FIRST divergence ---
$first = -1
$max = [Math]::Min($rd.Count, $dd.Count)
for ($i = 0; $i -lt $max; $i++) {
  if ($rd[$i] -cne $dd[$i]) { $first = $i; break }
}
Write-Output ("  FIRST DIVERGING DATA ROW (0-based): {0}" -f $first)
if ($first -ge 0) {
  Write-Output ("    rel[{0}]: {1}" -f $first, $rd[$first])
  Write-Output ("    dbg[{0}]: {1}" -f $first, $dd[$first])
  # how many rows differ in total
  $diffN = 0
  for ($i = 0; $i -lt $max; $i++) { if ($rd[$i] -cne $dd[$i]) { $diffN++ } }
  Write-Output ("    TOTAL DIVERGING ROWS: {0} of {1}" -f $diffN, $max)
  Write-Output ("    IDENTICAL PREFIX LENGTH: {0} rows" -f $first)
}

# --- byte-level: the two real files ---
Write-Output ""
$rbin = Join-Path $R "RE_Library\02_BINARIES\merlin\merlinAgent-Windows-x64.exe"
$dbin = Join-Path $R "RE_Library\02_BINARIES\merlin\merlinAgent-Windows-x64-Debug.exe"
Write-Output "--- the two REAL BINARIES ---"
foreach ($p in @($rbin, $dbin)) {
  $ok = Test-Path $p
  if (-not $ok) { Write-Output ("  MISSING: {0}" -f $p); continue }
  $h = (Get-FileHash $p -Algorithm SHA256).Hash
  $it = Get-Item $p
  Write-Output ("  {0}" -f $it.Name)
  Write-Output ("     size {0:N0} B   sha256 {1}" -f $it.Length, $h)
}
if ((Test-Path $rbin) -and (Test-Path $dbin)) {
  $rlen = (Get-Item $rbin).Length; $dlen = (Get-Item $dbin).Length
  Write-Output ("  SAME SIZE: {0}" -f ($rlen -eq $dlen))
  # first differing byte offset
  $fsr = [System.IO.File]::OpenRead($rbin); $fsd = [System.IO.File]::OpenRead($dbin)
  $bufA = New-Object byte[] 1048576; $bufB = New-Object byte[] 1048576
  $off = 0; $found = -1; $diffCount = 0
  while ($true) {
    $ca = $fsr.Read($bufA,0,$bufA.Length); $cb = $fsd.Read($bufB,0,$bufB.Length)
    if ($ca -le 0 -or $cb -le 0) { break }
    for ($i = 0; $i -lt $ca; $i++) {
      if ($bufA[$i] -ne $bufB[$i]) { if ($found -lt 0) { $found = $off + $i }; $diffCount++ }
    }
    $off += $ca
  }
  $fsr.Close(); $fsd.Close()
  Write-Output ("  FIRST DIFFERING BYTE OFFSET: {0}" -f $found)
  Write-Output ("  TOTAL DIFFERING BYTES      : {0:N0}" -f $diffCount)
  Write-Output ("  bytes compared             : {0:N0}" -f $off)
}
Write-Output "=== P5 END ==="
