param(
    [string]$SearchRoot = "F:\Мой диск",
    [string]$RepoPath   = "H:\ACTOR_DEV_ENV\apostille-mirror"
)

# 1. Поиск файла по имени
Write-Host "=== Поиск EVIDENCE_REGISTRY_INDEX.json ==="
$file = Get-ChildItem -Path $SearchRoot -Recurse -File -Filter "EVIDENCE_REGISTRY_INDEX.json" -ErrorAction SilentlyContinue | Select-Object -First 1

if (-not $file) {
    Write-Host "Файл EVIDENCE_REGISTRY_INDEX.json не найден." -ForegroundColor Red
    exit 1
}

Write-Host "Найден файл: $($file.FullName)" -ForegroundColor Green

# 2. Перенос в каталог репозитория
if (-not (Test-Path $RepoPath)) {
    New-Item -ItemType Directory -Force -Path $RepoPath | Out-Null
}
$dest = Join-Path $RepoPath "EVIDENCE_REGISTRY_INDEX.json"
Copy-Item -Path $file.FullName -Destination $dest -Force
Write-Host "Файл перенесён в $dest" -ForegroundColor Green

# 3. Добавление под Git LFS
Set-Location $RepoPath
git lfs install
git lfs track "EVIDENCE_REGISTRY_INDEX.json"

# 4. Обновление .gitattributes и фиксация
git add .gitattributes
git commit -m "chore(lfs): track EVIDENCE_REGISTRY_INDEX.json with Git LFS"

# 5. Добавление файла под LFS и фиксация
git add EVIDENCE_REGISTRY_INDEX.json
git commit -m "chore(lfs): migrate EVIDENCE_REGISTRY_INDEX.json to LFS storage"

# 6. Отправка в удалённый репозиторий
git push origin udhr-audit-rebuild-2026
git lfs push origin udhr-audit-rebuild-2026
