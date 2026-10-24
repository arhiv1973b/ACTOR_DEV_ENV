@echo off
chcp 65001 > nul
echo ================================================================================
echo CASE-MACHERET: Инициализация окружения Erga Omnes
echo ================================================================================

:: Шаг 1: Автоматический аудит хэшей перед стартом
echo [+] Выполнение проверки целостности 12 узлов (Zero-Collision)...
.venv_test\Scripts\python -c "
import hashlib, os, sys
manifest = r'H:\ACTOR_DEV_ENV\05_CRYPTO_MANIFESTS\CHECKSUMS_SHA256.txt'
if not os.path.exists(manifest): sys.exit(1)
failed = 0
for line in open(manifest, 'r', encoding='utf-8'):
    parts = line.strip().split()
    if len(parts) < 2 or line.startswith('#'): continue
    expected = parts[0].strip().lower()
    fname = parts[1].lstrip('*').strip()
    fpath = fname if os.path.isabs(fname) else os.path.join(r'H:\ACTOR_DEV_ENV', fname)
    if not os.path.exists(fpath): failed += 1; continue
    h = hashlib.sha256()
    with open(fpath, 'rb') as f: h.update(f.read())
    if h.hexdigest() != expected: failed += 1
if failed > 0:
    echo [-] ВНИМАНИЕ: Обнаружено повреждение или компрометация узлов!
    exit /b 1
else:
    echo [+] АУДИТ ПРОШЕЛ УСПЕШНО: Все узлы верифицированы.
"

if errorlevel 1 (
    echo [-] Ошибка целостности. Запуск портала отменен.
    pause
    exit /b
)

:: Шаг 2: Запуск Flask-портала в фоновом режиме
echo [+] Запуск correlation portal (app_dashboard.py) на порту 5050...
start /b .venv_test\Scripts\python app_dashboard.py > dashboard.log 2>&1

echo ================================================================================
echo [^+] СИСТЕМА АКТИВНА. Портал доступен по адресу: http://127.0.0.1:5050/
echo ================================================================================
pause
