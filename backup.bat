@echo off
chcp 65001 > nul
echo ================================================================================
echo CASE-MACHERET: Создание резервной копии ACTOR_DEV_ENV (Erga Omnes Backup)
echo ================================================================================

set "SOURCE=H:\ACTOR_DEV_ENV"
set "BACKUP_ROOT=F:\Мой диск\ACTOR_DEV_ENV_BACKUPS"

:: Генерация штампа времени для уникальной папки бэкапа
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "YEAR=%datetime:~0,4%"
set "MONTH=%datetime:~4,2%"
set "DAY=%datetime:~6,2%"
set "HOUR=%datetime:~8,2%"
set "MINUTE=%datetime:~10,2%"
set "DESTINATION=%BACKUP_ROOT%\backup_%YEAR%-%MONTH%-%DAY%_%HOUR%%MINUTE%"

echo [+] Источник: %SOURCE%
echo [+] Назначение: %DESTINATION%
echo [+] Синхронизация и копирование файлов...

:: Использование robocopy: /E - копирует поддиректории, /XD и /XF исключают тяжелые виртуалки и логи
robocopy "%SOURCE%" "%DESTINATION%" /E /XD "%SOURCE%\.venv_test" "%SOURCE%\.git" /XF "*.log" "*.pyc" /NFL /NDL /NJH /NJS

echo ================================================================================
echo [+] РЕЗЕРВНОЕ КОПИРОВАНИЕ УСПЕШНО ЗАВЕРШЕНО!
echo [+] Архив сохранен в: %DESTINATION%
echo ================================================================================
pause
