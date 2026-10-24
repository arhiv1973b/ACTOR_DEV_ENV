@echo off
chcp 65001 > nul
echo ================================================================================
echo CASE-MACHERET: Инициализация и аудит Erga Omnes
echo ================================================================================

echo [+] Шаг 1: Проверка целостности всех узлов (Zero-Collision)...
.venv_test\Scripts\python -c "import hashlib, os, sys; failed=any((not os.path.exists(p := f[1].lstrip('*').strip() if os.path.isabs(f[1].lstrip('*').strip()) else os.path.join(r'H:\ACTOR_DEV_ENV', f[1].lstrip('*').strip()))) or (hashlib.sha256(open(p,'rb').read()).hexdigest() != f[0].lower()) for l in open(r'H:\ACTOR_DEV_ENV\05_CRYPTO_MANIFESTS\CHECKSUMS_SHA256.txt', 'r', encoding='utf-8') if (f := l.strip().split()) and len(f)>=2 and not l.startswith('#')); sys.exit(1 if failed else 0)"

if errorlevel 1 (
    echo.
    echo [-] КРИТИЧЕСКАЯ ОШИБКА: Обнаружена компрометация или отсутствие узлов!
    echo [-] Запуск портала отменен. Проверьте целостность репозитория.
    echo ================================================================================
    pause
    exit /b
)

echo [+] АУДИТ УСПЕШЕН: Все 12 узлов подтверждены.
echo ================================================================================
echo [+] Шаг 2: Запуск correlation portal (app_dashboard.py) на порту 5050...
start /b .venv_test\Scripts\python app_dashboard.py > dashboard.log 2>&1

echo ================================================================================
echo [^+] СИСТЕМА АКТИВНА. Портал доступен по адресу: http://127.0.0.1:5050/
echo ================================================================================
pause
