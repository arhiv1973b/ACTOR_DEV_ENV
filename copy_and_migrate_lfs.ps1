# copy_and_migrate_lfs.ps1
param(
    [string]$Src = "F:\Мой диск\ACTOR_DEV_ENV\EVIDENCE_REGISTRY_INDEX.json",
    [string]$Dst = "H:\ACTOR_DEV_ENV\apostille-mirror\EVIDENCE_REGISTRY_INDEX.json",
    [string]$RepoPath = "H:\ACTOR_DEV_ENV\apostille-mirror"
)

Write-Host "=== Копирование файла через .NET ==="
try {
    $bytes = [System.IO.File]::ReadAllBytes($Src)
    [System.IO.File]::WriteAllBytes($Dst, $bytes)
    Write-Host "Copied successfully! Size: $($bytes.Length) bytes"
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "=== Миграция под Git LFS ==="
Set-Location $RepoPath
git lfs install
git lfs track "EVIDENCE_REGISTRY_INDEX.json"

git add .gitattributes
git commit -m "chore(lfs): track EVIDENCE_REGISTRY_INDEX.json with Git LFS"

git add EVIDENCE_REGISTRY_INDEX.json
git commit -m "chore(lfs): migrate EVIDENCE_REGISTRY_INDEX.json to LFS storage"

git push origin udhr-audit-rebuild-2026
git lfs push origin udhr-audit-rebuild-2026

Write-Host "=== Завершено: файл перенесён и зафиксирован под LFS ===" -ForegroundColor Green
