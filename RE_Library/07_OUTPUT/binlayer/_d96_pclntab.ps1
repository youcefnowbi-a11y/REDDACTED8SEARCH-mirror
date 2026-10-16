# _d96_pclntab.ps1 -- parse the Go pclntab directly (ghidra-independent symbol census).
# Go 1.20+ format. Verified header: magic 0xFFFFFFF1, pad1=0, pad2=0, minLC=1, ptrSize=8.
# NOTE: on-disk probe uses '#' comments. The earlier run emitted benign stderr because the
# '//' header lines were parsed as commands; the parse itself completed and wrote its TSV.
$ErrorActionPreference='Stop'
$exe='C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\02_BINARIES\sliver\sliver-client_windows-amd64.exe'
$out='C:\Users\PC\OneDrive\Desktop\FOR REDDACTED\RE_Library\07_OUTPUT\binlayer\_d96_pclntab.tsv'
$b=[System.IO.File]::ReadAllBytes($exe)
$P=0x269DDE0

$magic=[BitConverter]::ToUInt32($b,$P)
$nf=[BitConverter]::ToUInt64($b,$P+8)
$nfiles=[BitConverter]::ToUInt64($b,$P+16)
$textStart=[BitConverter]::ToUInt64($b,$P+24)
$funcnameOff=[BitConverter]::ToUInt64($b,$P+32)
$cuOff=[BitConverter]::ToUInt64($b,$P+40)
$filetabOff=[BitConverter]::ToUInt64($b,$P+48)
$pctabOff=[BitConverter]::ToUInt64($b,$P+56)
$pclnOff=[BitConverter]::ToUInt64($b,$P+64)

Write-Host ("magic=0x{0:X8} nfunc={1} nfiles={2}" -f $magic,$nf,$nfiles)
Write-Host ("textStart=0x{0:X} funcnameOff=0x{1:X} pclnOff=0x{2:X}" -f $textStart,$funcnameOff,$pclnOff)

# functab starts at P+pclnOff (relative to pclntab start) -- in Go 1.20+, pclnOff is
# the offset from the pclntab base to the pcHeader-relative function table.
$ftab = $P + $pclnOff
Write-Host ("ftab=0x{0:X}" -f $ftab)

# entry size = 8 bytes (4 entryoff + 4 funcoff)
$nameBase = $P + $funcnameOff

$rows = New-Object System.Collections.Generic.List[string]
$rows.Add("# program`tsliver-client_windows-amd64.exe")
$rows.Add("# source`tpclntab@0x{0:X}" -f $P)
$rows.Add("# kind`tentryoff`tname`tfuncoff")

function Read-GoName([int]$off) {
  $q=$nameBase+$off
  $sb=New-Object System.Text.StringBuilder
  while($q -lt $b.Length -and $b[$q] -ne 0){
    $c=[char]$b[$q]
    if([int]$c -ge 32 -and [int]$c -lt 127){ [void]$sb.Append($c) } else { [void]$sb.Append('.') }
    $q++
    if($sb.Length -gt 512){ break }
  }
  return $sb.ToString()
}

$named=0; $total=0; $seen=@{}
for($i=0;$i -lt $nf;$i++){
  $e = $ftab + $i*8
  if($e+8 -gt $b.Length){ break }
  $entryoff=[BitConverter]::ToUInt32($b,$e)
  $funcoff=[BitConverter]::ToUInt32($b,$e+4)
  $fs = $ftab + [int64]$funcoff
  if($fs+8 -gt $b.Length){ continue }
  $nameoff=[BitConverter]::ToInt32($b,$fs+4)
  $nm = Read-GoName $nameoff
  if($nm.Length -gt 0){
    $total++
    if($seen.ContainsKey($nm)){ $seen[$nm]++ } else { $seen[$nm]=1 }
    if(-not $nm.StartsWith('FUN_')){ $named++ }
    if($rows.Count -lt 300000){ $rows.Add(("FUNC`t0x{0:X}`t{1}`t0x{2:X}" -f $entryoff,$nm,$funcoff)) }
  }
}
$rows.Add("# SUMMARY`ttotal=$total`tunique=$($seen.Count)`tentries=$nf")
[System.IO.File]::WriteAllLines($out,$rows,(New-Object System.Text.UTF8Encoding($false)))
Write-Host "total=$total unique=$($seen.Count) entries=$nf"
Write-Host "wrote $out"
