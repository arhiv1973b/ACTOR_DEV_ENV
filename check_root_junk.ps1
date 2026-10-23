$junk = Get-ChildItem -Path "F:\Мой диск" -File -Include *.exe, *.msi -ErrorAction SilentlyContinue
$count = if ($junk) { @($junk).Count } else { 0 }
$names = if ($junk) { @($junk).Name -join ", " } else { "None" }
[PSCustomObject]@{
    Count = $count
    Files = $names
} | Format-List
