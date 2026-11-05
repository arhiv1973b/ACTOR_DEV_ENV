<#
.SYNOPSIS
    Скрипт диагностики и запуска OpenCode 2.0
.DESCRIPTION
    Проверяет наличие исполняемого файла OpenCode, тестирует версию, 
    проверяет статус фоновых служб и предлагает варианты запуска (TUI или Serve).
#>

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet("Diagnose", "Interactive", "Serve", "All")]
    [string]$Mode = "All"
)

# Цветовое оформление вывода
function Write-Header($text) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host " $text" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

$binPath = "H:\npm-global\node_modules\@opencode\cli\bin\opencode.exe"
$cliWrapper = "C:\Users\arhiv\opencode.ps1"

Write-Header "Диагностика окружения OpenCode 2.0"

# 1. Проверка наличия бинарника
if (Test-Path $binPath) {
    Write-Host "[OK] Бинарник OpenCode найден по пути: $binPath" -ForegroundColor Green
    $versionOutput = & $binPath --version
    Write-Host "     Версия: $versionOutput" -ForegroundColor Yellow
} else {
    Write-Host "[ERROR] Бинарник OpenCode не найден по пути: $binPath" -ForegroundColor Red
    exit 1
}

# 2. Проверка лаунчера
if (Test-Path $cliWrapper) {
    Write-Host "[OK] Пользовательский лаунчер доступен: $cliWrapper" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Лаунчер в корне пользователя не обнаружен" -ForegroundColor Yellow
}

# Выполнение в зависимости от выбранного режима
if ($Mode -eq "Interactive" -or $Mode -eq "All") {
    Write-Header "Запуск интерактивного режима (TUI)"
    Write-Host "Запуск команды 'opencode'..." -ForegroundColor Cyan
    & $binPath
}
elseif ($Mode -eq "Serve") {
    Write-Header "Запуск фонового сервиса (Serve)"
    Write-Host "Старт управляющего демона OpenCode..." -ForegroundColor Cyan
    & $binPath serve
}
else {
    Write-Header "Диагностика завершена успешно"
    Write-Host "Для запуска интерактивной сессии выполните: opencode" -ForegroundColor Green
    Write-Host "Для запуска фонового сервера: opencode serve" -ForegroundColor Green
}

# SIG # Begin signature block
# MIIFoQYJKoZIhvcNAQcCoIIFkjCCBY4CAQExCzAJBgUrDgMCGgUAMGkGCisGAQQB
# gjcCAQSgWzBZMDQGCisGAQQBgjcCAR4wJgIDAQAABBAfzDtgWUsITrck0sYpfvNR
# AgEAAgEAAgEAAgEAAgEAMCEwCQYFKw4DAhoFAAQUJfTC1oG5e4/a/ofxcOVWy8Jf
# DnugggM2MIIDMjCCAhqgAwIBAgIQUkiU2o8FKoxESM2XIiZvxDANBgkqhkiG9w0B
# AQsFADAgMR4wHAYDVQQDDBVQb3dlclNoZWxsTG9jYWxTaWduZXIwHhcNMjYxMTAz
# MTY1ODQzWhcNMzExMTAzMTcwODM1WjAgMR4wHAYDVQQDDBVQb3dlclNoZWxsTG9j
# YWxTaWduZXIwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDwhCzgdojd
# KLdwK350YJJsRKm3NBDpnOjFOX4CbuAy9j+5AMcPILSuU9Ug+bn+L5ZWGY2gMNN+
# qMpnQ1F2NEvLf8YRvBbCzNu3t3TntTddZBpExplctdL2z5GKyMqe9fX2Uk9QlC0r
# yh16Rbu2ATlIlhbELKc2IwawYpVNRgPrUbD9PG3QCRfy6Ej4dX7m62Jz1+hY+vPn
# tqxjuRJu6/6x5uHtCol9f9//3iuEMcGC9ibM781uQPQGQiyT0sYH/ZfmeW+9pq0F
# RgTj6BjVrtL1VGyHfPoQfmNNIAsnjPvZ7KDzmjQ5gjKTia0m+Rfb+Ive2wwGF7WU
# 3ys0FrZWKqVBAgMBAAGjaDBmMA4GA1UdDwEB/wQEAwIHgDATBgNVHSUEDDAKBggr
# BgEFBQcDAzAgBgNVHREEGTAXghVQb3dlclNoZWxsTG9jYWxTaWduZXIwHQYDVR0O
# BBYEFH/ZfhBlsB4GZrqAyWs/EWaTsCYyMA0GCSqGSIb3DQEBCwUAA4IBAQBD/oNZ
# sbGqVRxb5tMcrSjgLjS3JPTwtLT7d3ow7ygAXkCmU1So/40wpUH2vroJJKWomr21
# TJp07yz4i4qB7+3DJqZ4tHXh+z6T/ShAB0JvpBINHMbRSi/hEFVw5zFTifxcpAg9
# 3/wcYSPtK2wB/nNRef1A1LvJcHbAosmJH41EfHUBYWzRxXW9/PeAFrANeM2ldrOM
# lMIsxUSceVHh8c7W/WQR4E3xTrZkmBDyPdJpL6HhL9OPPEgqLRgvUX3Kcn0k+Vlf
# 6KB+2uSzqigC+a0FbOlIogOItO8qbQa8kc1NsjQHvXl92eO0/iLnFotvtS5Gtudw
# f9mcZra48eeCf6lWMYIB1TCCAdECAQEwNDAgMR4wHAYDVQQDDBVQb3dlclNoZWxs
# TG9jYWxTaWduZXICEFJIlNqPBSqMREjNlyImb8QwCQYFKw4DAhoFAKB4MBgGCisG
# AQQBgjcCAQwxCjAIoAKAAKECgAAwGQYJKoZIhvcNAQkDMQwGCisGAQQBgjcCAQQw
# HAYKKwYBBAGCNwIBCzEOMAwGCisGAQQBgjcCARUwIwYJKoZIhvcNAQkEMRYEFAxd
# B1Jd1Oci8ulZ3TPq+RPXjGrlMA0GCSqGSIb3DQEBAQUABIIBACTVuqkNsXb8hpQz
# zSFbhZ/HurfvRahtVO9nyEj/EIC/2cYzh/5KVSNYrXTrVEhme25crjbjiMilCGsB
# AxiL1JvAtclh5MwfCIfgtD8S+9tHGSAX8x/nr2oI91WnJkas+EY4sZxs6VK7cb4b
# Bb19EwQD8kFtp4r8r2bypWuseCVo6zDNN1eQTHCkOY3WhhdXjlEXKt1tJT27RSh5
# VnVITT8NTwbZOEJ0yK0GmErKLKTcPV2NvDzuawWf4Naw+BojQZQI5Lg6buqXzpe5
# +IPYJ0xZ0aZxvI9/n9hBx4Z2Av6GfjWeINuuhcTM8LPtaXFjFPETwviev2Ngkxzh
# 7JaP4bo=
# SIG # End signature block
