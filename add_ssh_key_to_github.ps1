# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

$PubKeyPath = Join-Path -Path $env:USERPROFILE -ChildPath ".ssh\id_ed25519.pub"
$KeyTitle = "A©tor-TI-ULA-Win11-$(Get-Date -Format 'yyyyMMdd')"

if (Get-Command gh -ErrorAction SilentlyContinue) {
    if (Test-Path $PubKeyPath) {
        Write-Host "Регистрация публичного ключа на GitHub под именем '$KeyTitle'..." -ForegroundColor Cyan
        gh ssh-key add $PubKeyPath --title $KeyTitle
        if ($LASTEXITCODE -eq 0) {
            Write-Host "УСПЕХ: Публичный ключ успешно добавлен в ваш аккаунт GitHub!" -ForegroundColor Green
        } else {
            Write-Host "ОШИБКА: Не удалось зарегистрировать ключ. Проверьте права токена (admin:public_key)." -ForegroundColor Red
        }
    } else {
        Write-Host "ОШИБКА: Публичный ключ не найден по пути: $PubKeyPath" -ForegroundColor Red
    }
} else {
    Write-Host "ОШИБКА: Утилита GitHub CLI (gh) не найдена в системе." -ForegroundColor Red
}
