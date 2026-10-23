# Настройка окружения
$env:PYTHONIOENCODING = "utf-8"
Set-Location -Path "H:\ACTOR_DEV_ENV"

# Запуск анализатора (логирование встроено в Python)
python batch_analyzer.py --limit 5
