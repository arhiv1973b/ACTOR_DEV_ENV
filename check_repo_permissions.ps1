# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

$RepoName = "arhiv1973b/ACTOR_DEV_ENV"

if (Get-Command gh -ErrorAction SilentlyContinue) {
    Write-Host "Проверка прав доступа к репозиторию $RepoName через GitHub CLI..." -ForegroundColor Cyan
    gh repo view $RepoName --json name,owner,viewerPermission,isPrivate,sshUrl
} else {
    Write-Host "ОШИБКА: Утилита GitHub CLI (gh) не найдена в системе." -ForegroundColor Red
}
