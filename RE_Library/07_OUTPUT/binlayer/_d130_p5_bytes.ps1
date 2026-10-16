$ErrorActionPreference = 'Continue'
$R = "C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
$dir = Join-Path $R "RE_Library\05_TARGETS\merlin_extracted\data\bin"

Write-Output "=== OPERAND ACQUISITION CHECK (enumerate, do not guess) ==="
$rel = Get-ChildItem $dir -File -Filter 'merlinAgent-Windows-x64.exe' -ErrorAction SilentlyContinue
$dbg = Get-ChildItem $dir -File -Filter 'merlinAgent-Windows-x64-Debug.exe' -ErrorAction SilentlyContinue
Write-Output ("  release found: {0}   debug found: {1}" -f @($rel).Count, @($dbg).Count)
if (@($rel).Count -ne 1 -or @($dbg).Count -ne 1) { Write-Output "  ABORT: operands not uniquely acquired."; exit 1 }
$rel = $rel[0]; $dbg = $dbg[0]
Write-Output ("  A: {0}  {1:N0} B" -f $rel.FullName, $rel.Length)
Write-Output ("  B: {0}  {1:N0} B" -f $dbg.FullName, $dbg.Length)

$ha = (Get-FileHash $rel.FullName -Algorithm SHA256).Hash
$hb = (Get-FileHash $dbg.FullName -Algorithm SHA256).Hash
Write-Output ""
Write-Output "=== THE CONTROL ==="
Write-Output ("  release sha256: {0}" -f $ha)
Write-Output ("  debug   sha256: {0}" -f $hb)
Write-Output ("  SAME SHA : {0}   (expected False -> proves they are different artifacts)" -f ($ha -eq $hb))
Write-Output ("  SAME SIZE: {0}" -f ($rel.Length -eq $dbg.Length))

Write-Output ""
Write-Output "=== BYTE DIFF (chunked, real operands) ==="
$fsa = [System.IO.File]::OpenRead($rel.FullName)
$fsb = [System.IO.File]::OpenRead($dbg.FullName)
$bufA = New-Object byte[] 1048576
$bufB = New-Object byte[] 1048576
$off = 0; $firstDiff = -1; $diffBytes = 0
while ($true) {
  $ca = $fsa.Read($bufA,0,$bufA.Length)
  $cb = $fsb.Read($bufB,0,$bufB.Length)
  if ($ca -le 0) { break }
  if ($ca -ne $cb) { Write-Output ("  READ LENGTH MISMATCH at {0}: {1} vs {2}" -f $off,$ca,$cb); break }
  for ($i = 0; $i -lt $ca; $i++) {
    if ($bufA[$i] -ne $bufB[$i]) {
      if ($firstDiff -lt 0) { $firstDiff = $off + $i }
      $diffBytes++
    }
  }
  $off += $ca
}
$fsa.Close(); $fsb.Close()
Write-Output ("  bytes compared        : {0:N0}" -f $off)
Write-Output ("  FIRST DIFFERING OFFSET: {0}" -f $firstDiff)
Write-Output ("  TOTAL DIFFERING BYTES : {0:N0}" -f $diffBytes)
Write-Output ("  pct differing         : {0:N5}%" -f ((100.0 * $diffBytes) / $off))

Write-Output ""
Write-Output "=== are the differing bytes LOCALIZED or SPREAD? (histogram of 1 MB bands) ==="
if ($firstDiff -ge 0) {
  $fsa = [System.IO.File]::OpenRead($rel.FullName)
  $fsb = [System.IO.File]::OpenRead($dbg.FullName)
  $bandBytes = 1048576
  $bands = @{}
  $off = 0
  while ($true) {
    $ca = $fsa.Read($bufA,0,$bufA.Length)
    $cb = $fsb.Read($bufB,0,$bufB.Length)
    if ($ca -le 0) { break }
    $bi = [math]::Floor($off / $bandBytes)
    $n = 0
    for ($i = 0; $i -lt $ca; $i++) { if ($bufA[$i] -ne $bufB[$i]) { $n++ } }
    if ($n -gt 0) { $bands[[string]$bi] = $n }
    $off += $ca
  }
  $fsa.Close(); $fsb.Close()
  Write-Output ("  1MB bands with any difference: {0}" -f $bands.Count)
  $bands.GetEnumerator() | Sort-Object { [int]$_.Key } | ForEach-Object {
    Write-Output ("    band {0,4}  (offset {1,12:N0})  differing bytes {2,8:N0}" -f $_.Key, ([int]$_.Key * $bandBytes), $_.Value)
  }
}
Write-Output "=== END ==="
