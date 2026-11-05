<#
.SYNOPSIS
    Быстрая генерация SHA-256 чек-сум для ключевых файлов контура TI-ULA и обновление архива.
#>

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "[TI-ULA] Быстрая генерация SHA-256 хэшей для ключевых артефактов..." -ForegroundColor Cyan

$checksumFile = "CHECKSUMS_SHA256.txt"
$files = Get-ChildItem -Recurse -File | Where-Object { 
    $_.FullName -notmatch "node_modules|\.git|[\/\\]\.venv|\.zip|grok_output|output" -and
    $_.Extension -match "\.(py|ps1|js|json|md|html)$"
}

$output = foreach ($file in $files) {
    try {
        $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
        $relPath = $file.FullName.Replace((Get-Location).Path + "\", "")
        "$hash  $relPath"
    } catch {
        # Пропуск файлов, к которым нет доступа
    }
}

$output | Set-Content -Path $checksumFile -Encoding utf8
Write-Host "[УСПЕХ] Файл $checksumFile успешно обновлен." -ForegroundColor Green

# Пересоздание архива
$validPaths = @('secure_logs', 'INTEGRITY_WITNESS.json', $checksumFile, 'check_npm_security.ps1', 'generate_checksums.ps1') | Where-Object { Test-Path $_ }
if ($validPaths) {
    Compress-Archive -Path $validPaths -DestinationPath 'TI-ULA_Security_Audit_Archive_20261105.zip' -Force
    Write-Host "[УСПЕХ] Архив TI-ULA_Security_Audit_Archive_20261105.zip пересоздан." -ForegroundColor Green
}
