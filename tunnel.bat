@echo off
chcp 65001 > nul
echo ================================================================================
echo CASE-MACHERET: Secure Tunnel Bridge (Erga Omnes Public Access)
echo ================================================================================
echo [+] Проверка доступности локального порта 5050 (app_dashboard.py)...
python -c "
import urllib.request
try:
    urllib.request.urlopen('http://127.0.0.1:5050/', timeout=2)
    print('[+] Локальный дашборд активен на порту 5050.')
except:
    print('[-] ВНИМАНИЕ: Дашборд не отвечает. Запустите start.bat перед туннелированием.')
"

echo.
echo [+] Инициализация защищенного HTTPS-туннеля...
echo [+] Если у вас установлен cloudflared, вы можете запустить:
echo     cloudflared tunnel --url http://localhost:5050
echo [+] Или использовать встроенный ngrok:
echo     ngrok http 5050
echo ================================================================================
pause
