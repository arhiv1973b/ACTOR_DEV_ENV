# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

$RepoDir = "H:\ACTOR_DEV_ENV"

Write-Host "=== АУДИТ SSH-ПОДКЛЮЧЕНИЯ ДЛЯ РЕПОЗИТОРИЯ ===" -ForegroundColor Cyan

if (Test-Path (Join-Path $RepoDir ".git")) {
    Push-Location $RepoDir
    $RemoteUrl = & git remote get-url origin
    Pop-Location
    Write-Host "Remote URL: $RemoteUrl" -ForegroundColor Yellow
} else {
    Write-Host "Текущая папка не является Git-репозиторием." -ForegroundColor Red
    exit
}

Write-Host "`nПроверка аутентификации на GitHub по SSH (verbose):" -ForegroundColor Cyan
# Run ssh test via bash or python
