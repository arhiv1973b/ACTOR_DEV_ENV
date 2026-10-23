$path = "F:\Мой диск\ACTOR_DEV_ENV\EVIDENCE_REGISTRY_INDEX.json"
$dest = "H:\ACTOR_DEV_ENV\EVIDENCE_REGISTRY_INDEX.json"
try {
    $bytes = [System.IO.File]::ReadAllBytes($path)
    [System.IO.File]::WriteAllBytes($dest, $bytes)
    Write-Host "Copied successfully via .NET! Size: $($bytes.Length) bytes"
} catch {
    Write-Host "Error: $_"
}
