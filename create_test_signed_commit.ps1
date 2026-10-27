# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

$TestFile = "actor_test_matrix.log"
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Write-Host "=== СОЗДАНИЕ ТЕСТОВОГО КОММИТА TI-ULA ===" -ForegroundColor Cyan

$Content = @"
# TI-ULA Matrix Verification Log
Timestamp: $Timestamp
Subject: A©tor (A©t0r)
Declaration: A©TOR_KEY="# [⚖ A©tor Declaration]"
Status: Verified
"@

$Utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($TestFile, $Content, $Utf8NoBom)

git add -f $TestFile
$CommitMessage = "test(ti-ula): verify GPG signature and A©tor typographic matrix`n`nA©TOR_KEY=`"# [⚖ A©tor Declaration]`""
git commit -S -m $CommitMessage

if ($LASTEXITCODE -eq 0) {
    Write-Host "УСПЕХ: Тестовый коммит успешно создан и подписан!" -ForegroundColor Green
    Write-Host "`n=== РЕЗУЛЬТАТ АУДИТА ПОДПИСИ ===" -ForegroundColor Cyan
    git log -1 --show-signature --format="Format: Hash: %H%nSubject: %s%nSign-status: %G?%nDetails: %GG"
} else {
    Write-Host "ОШИБКА: Не удалось создать подписанный коммит." -ForegroundColor Red
}
