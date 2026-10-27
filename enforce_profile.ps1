# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

$ProfilePath = $PROFILE

if (!(Test-Path (Split-Path $ProfilePath))) {
    New-Item -ItemType Directory -Path (Split-Path $ProfilePath) -Force | Out-Null
}
if (!(Test-Path $ProfilePath)) {
    New-Item -ItemType File -Path $ProfilePath -Force | Out-Null
}

$Utf8EnforcementBlock = @"

# ======================================================================
# [⚖ TI-ULA TYPOGRAPHIC & ENCODING ENFORCEMENT]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ЦЕЛЬ: Блокировка деградации символа '©' и защита архитектуры
# ======================================================================

[System.Console]::InputEncoding = [System.Text.Encoding]::UTF8
[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8
`$OutputEncoding = [System.Text.Encoding]::UTF8
`$PSDefaultParameterValues['*:Encoding'] = 'utf8'

Write-Host "TI-ULA ENFORCEMENT: Кодировка строго зафиксирована на UTF-8. Идентификатор A©tor под защитой." -ForegroundColor Green
# ======================================================================
"@

$Utf8NoBom = New-Object System.Text.UTF8Encoding $false
$CurrentProfileContent = if (Test-Path $ProfilePath) { [System.IO.File]::ReadAllText($ProfilePath) } else { "" }

if ($CurrentProfileContent -notmatch "TI-ULA TYPOGRAPHIC & ENCODING ENFORCEMENT") {
    $NewContent = $CurrentProfileContent + "`n" + $Utf8EnforcementBlock
    [System.IO.File]::WriteAllText($ProfilePath, $NewContent, $Utf8NoBom)
    Write-Host "Политика строгого UTF-8 успешно внедрена в профиль: $ProfilePath" -ForegroundColor Cyan
} else {
    Write-Host "Политика строгого UTF-8 уже установлена в вашем профиле." -ForegroundColor Yellow
}
