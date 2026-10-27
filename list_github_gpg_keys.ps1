# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

if (Get-Command gh -ErrorAction SilentlyContinue) {
    Write-Host "=== ЗАРЕГИСТРИРОВАННЫЕ GPG-КЛЮЧИ В АККАУНТЕ GITHUB ===" -ForegroundColor Cyan
    gh api "user/gpg_keys" --jq ".[] | {ID: .id, KeyID: .key_id, Subkeys: (.subkeys | length), CreatedAt: .created_at}"
} else {
    Write-Host "ОШИБКА: Утилита GitHub CLI (gh) не найдена в системе." -ForegroundColor Red
}
