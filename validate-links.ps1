# ======================================================================
# validate-links.ps1
# Автоматическая проверка ссылок в HTML/Markdown для CI/CD
# ======================================================================

param(
    [string]$RepoRoot = "."
)

Write-Host "🔍 Запуск проверки ссылок в $RepoRoot"

# 1. Собираем все HTML и MD файлы
$files = Get-ChildItem -Path $RepoRoot -Recurse -Include *.html, *.md

# 2. Регулярка для извлечения ссылок
$regex = '(?<=href=")[^"]+|(?<=src=")[^"]+'

$errors = @()

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $matches = [regex]::Matches($content, $regex)

    foreach ($m in $matches) {
        $link = $m.Value

        # Игнорируем внешние ссылки (http/https)
        if ($link -match '^https?://') { continue }

        # Нормализуем путь
        $path = Join-Path $RepoRoot $link

        if (-not (Test-Path $path)) {
            $errors += "❌ Missing target: $link (referenced in $($file.FullName))"
        }
    }
}

if ($errors.Count -gt 0) {
    Write-Host "⚠️ Обнаружены ошибки ссылок:"
    $errors | ForEach-Object { Write-Host $_ }
    exit 1
} else {
    Write-Host "✅ Все локальные ссылки валидны."
}
