# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "[⚖ TI-ULA] АУДИТ КОДИРОВКИ И ТИПОГРАФИЧЕСКОЙ МАТРИЦЫ A©tor" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$inputEnc = [System.Console]::InputEncoding.WebName
$outputEnc = [System.Console]::OutputEncoding.WebName
$defaultEncoding = $OutputEncoding.WebName

Write-Host "InputEncoding  : $inputEnc" -ForegroundColor $(if ($inputEnc -eq 'utf-8') { 'Green' } else { 'Red' })
Write-Host "OutputEncoding : $outputEnc" -ForegroundColor $(if ($outputEnc -eq 'utf-8') { 'Green' } else { 'Red' })
Write-Host "`$OutputEncoding: $defaultEncoding" -ForegroundColor $(if ($defaultEncoding -eq 'utf-8') { 'Green' } else { 'Red' })

if ($inputEnc -eq 'utf-8' -and $outputEnc -eq 'utf-8' -and $defaultEncoding -eq 'utf-8') {
    Write-Host "`nСТАТУС: Защита идентификатора A©tor активна. Кодировка UTF-8 подтверждена." -ForegroundColor Green
} else {
    Write-Host "`nВНИМАНИЕ: Обнаружено отклонение кодировки!" -ForegroundColor Red
}
Write-Host "======================================================================" -ForegroundColor Cyan
