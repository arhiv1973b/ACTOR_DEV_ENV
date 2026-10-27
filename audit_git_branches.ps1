# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

$RepoDir = "H:\ACTOR_DEV_ENV"

if (Test-Path (Join-Path $RepoDir ".git")) {
    Push-Location $RepoDir
    Write-Host "=== АУДИТ ВЕТОК РЕПОЗИТОРИЯ ACTOR_DEV_ENV ===" -ForegroundColor Cyan
    git fetch --all --prune | Out-Null
    git branch -a -vv
    Pop-Location
} else {
    Write-Host "ОШИБКА: Директория $RepoDir не является Git-репозиторием." -ForegroundColor Red
}
