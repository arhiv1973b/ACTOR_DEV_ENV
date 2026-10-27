# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

$Repo = "arhiv1973b/ACTOR_DEV_ENV"
$ArtifactName = "encoding-audit-log"
$DownloadDir = Join-Path -Path $env:USERPROFILE -ChildPath ".ti_ula_artifacts"

if (!(Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "ОШИБКА: Утилита GitHub CLI (gh) не найдена в системе." -ForegroundColor Red
    exit 1
}

if (!(Test-Path $DownloadDir)) {
    New-Item -ItemType Directory -Path $DownloadDir -Force | Out-Null
}

Write-Host "Проверка последних сборок в репозитории $Repo..." -ForegroundColor Cyan

$RunsJson = gh run list --repo $Repo --limit 1 --json databaseId,status,conclusion,headBranch,createdAt
if (!$RunsJson) {
    Write-Host "Не удалось получить информацию о сборках GitHub Actions." -ForegroundColor Red
    exit 1
}

$LatestRun = ($RunsJson | ConvertFrom-Json)
if ($LatestRun -is [array]) {
    $LatestRun = $LatestRun[0]
}

Write-Host "Последний запуск [ID: $($LatestRun.databaseId)] | Ветка: $($LatestRun.headBranch) | Статус: $($LatestRun.status) / $($LatestRun.conclusion)" -ForegroundColor Yellow

if ($LatestRun.status -ne "completed") {
    Write-Host "Сборка еще выполняется. Дождитесь завершения GitHub Actions." -ForegroundColor Yellow
    exit 0
}

Write-Host "Скачивание артефакта '$ArtifactName'..." -ForegroundColor Cyan
try {
    gh run download $LatestRun.databaseId --repo $Repo --name $ArtifactName --dir $DownloadDir
    
    $DownloadedFile = Join-Path -Path $DownloadDir -ChildPath "encoding_audit.log"
    if (Test-Path $DownloadedFile) {
        Write-Host "УСПЕХ: Артефакт успешно скачан и сохранен: $DownloadedFile" -ForegroundColor Green
        Write-Host "--- СОДЕРЖИМОЕ АРТЕФАКТА ---" -ForegroundColor Gray
        Get-Content -Path $DownloadedFile -Encoding UTF8 | Select-Object -First 10
        Write-Host "----------------------------" -ForegroundColor Gray
    } else {
        Write-Host "ВНИМАНИЕ: Артефакт скачан, но файл 'encoding_audit.log' не найден в архиве." -ForegroundColor Yellow
    }
} catch {
    Write-Host "ОШИБКА скачивания артефакта: $_" -ForegroundColor Red
}
