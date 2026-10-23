$junk = Get-ChildItem -Path "F:\Мой диск" -Recurse -File -Include *.exe, *.msi -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch "\.git" }
$sum = 0
foreach ($f in $junk) {
    if ($f.Length) { $sum += $f.Length }
}
$junkSize = [math]::Round($sum / 1GB, 2)
[PSCustomObject]@{
    Count = $junk.Count
    SizeGB = $junkSize
} | Format-List
