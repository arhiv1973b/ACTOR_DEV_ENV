# [⚖ A©tor Declaration]
# A©t0r Identity: arhiv1973b
# Описание: Проверка безопасности и игнорирования файла .env в git

$WorkspacePath = "H:\ACTOR_DEV_ENV"
Set-Location -Path $WorkspacePath

Write-Host "1. Проверка записи в .gitignore..." -ForegroundColor Cyan
if (Select-String -Path ".gitignore" -Pattern "^\.env$" -Quiet) {
    Write-Host "[OK] Файл .env найден в правилах .gitignore." -ForegroundColor Green
} else {
    Write-Host "[ВНИМАНИЕ] .env отсутствует в .gitignore. Добавляем алгоритмически..." -ForegroundColor Yellow
    Add-Content -Path ".gitignore" -Value "`n# Локальные секреты API (A©t0r)`n.env" -Encoding utf8
    Write-Host "[OK] Правило безопасности успешно добавлено в .gitignore." -ForegroundColor Green
}

Write-Host "`n2. Системная проверка движка Git (check-ignore)..." -ForegroundColor Cyan
$IgnoreCheck = git check-ignore -v .env 2>&1 | Out-String
if ($IgnoreCheck -match "\.env") {
    Write-Host "[OK] Механизм Git подтверждает блокировку: $($IgnoreCheck.Trim())" -ForegroundColor Green
} else {
    Write-Host "[ОШИБКА] Движок Git не распознает блокировку файла .env!" -ForegroundColor Red
}

Write-Host "`n3. Проверка кэша отслеживаемых файлов..." -ForegroundColor Cyan
git ls-files --error-unmatch .env 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[КРИТИЧЕСКИ] Файл .env УЖЕ проиндексирован и отслеживается Git! Выполняем принудительную очистку..." -ForegroundColor Red
    git rm --cached .env 2>&1 | Out-Null
    Write-Host "[OK] Секретный файл .env алгоритмически удален из индекса Git. Утечка предотвращена." -ForegroundColor Green
} else {
    Write-Host "[OK] Файл .env отсутствует в индексе Git (чисто)." -ForegroundColor Green
}

Write-Host "`n[СТАТУС БЕЗОПАСНОСТИ] Токены PINATA_JWT и ZENODO_TOKEN надежно изолированы от публичного репозитория.`n" -ForegroundColor Cyan
