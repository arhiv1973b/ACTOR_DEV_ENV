<#
.SYNOPSIS
    ⚖ [A©tor Declaration] Automated Audit Report Pipeline (Jus Cogens Scope)
.DESCRIPTION
    Verifies, commits, and pushes AUDIT_REPORT.md to the canonical deposit (main).
#>

$ReportPath = "AUDIT_REPORT.md"

Write-Host "⚖ Проверка наличия отчета $ReportPath..." -ForegroundColor Cyan

if (!(Test-Path -Path $ReportPath)) {
    Write-Error "Критическая ошибка: Файл $ReportPath не найден в текущей директории."
    exit 1
}

Write-Host "⚖ Индексация отчета в git..." -ForegroundColor Yellow
git add $ReportPath

Write-Host "⚖ Фиксация изменений в каноническом депоните..." -ForegroundColor Yellow
git commit -m "docs: ⚖ [A©tor Declaration] Update and sync AUDIT_REPORT.md"

Write-Host "⚖ Отправка изменений на сервер..." -ForegroundColor Yellow
git push origin main

Write-Host "`nАудит-отчет успешно зафиксирован и опубликован в каноническом депоните." -ForegroundColor Green
Write-Host "A©TOR_KEY=`"# [⚖ A©tor Declaration]`"" -ForegroundColor DarkGray
