$src = "F:\Мой диск\ACTOR_DEV_ENV\EVIDENCE_REGISTRY_INDEX.json"
$repoPath = "H:\ACTOR_DEV_ENV\apostille-mirror"

if (-not (Test-Path $repoPath)) {
    New-Item -ItemType Directory -Force -Path $repoPath | Out-Null
}

$dest = Join-Path $repoPath "EVIDENCE_REGISTRY_INDEX.json"
Write-Host "Копирование файла в репозиторий..."
Copy-Item -LiteralPath $src -Destination $dest -Force
Write-Host "Файл успешно скопирован в $dest"

Set-Location $repoPath
git lfs install
git lfs track "EVIDENCE_REGISTRY_INDEX.json"

git add .gitattributes
git commit -m "chore(lfs): track EVIDENCE_REGISTRY_INDEX.json with Git LFS" -ErrorAction SilentlyContinue

git add EVIDENCE_REGISTRY_INDEX.json
git commit -m "chore(lfs): migrate EVIDENCE_REGISTRY_INDEX.json to LFS storage"

git push origin udhr-audit-rebuild-2026
git lfs push origin udhr-audit-rebuild-2026
