# Локальный скрипт пакетной обработки через Gemini CLI PowerShell (без ограничений и сбоев)
$ErrorActionPreference = "Stop"
$pythonPath = "H:\ACTOR_DEV_ENV\.venv\Scripts\python.exe"

Write-Host "[*] Шаг 1: Проверка окружения MCP-сервера..." -ForegroundColor Cyan
& $pythonPath -c "import mcp_server; print('System pre-check passed successfully.')"

Write-Host "[*] Шаг 2: Запуск обработки пакета критических артефактов..." -ForegroundColor Cyan
& $pythonPath -c "
from mcp_drive_indexer import DatabaseManager, InferenceOrchestrator, DriveWorkerPool
db = DatabaseManager('drive_index.db')
orchestrator = InferenceOrchestrator()

query = '''
    SELECT path, size, sha256, mtime, status
    FROM files
    WHERE status = 'PENDING'
      AND LOWER(path) NOT LIKE '%.gdoc'
      AND LOWER(path) NOT LIKE '%.gsheet'
      AND LOWER(path) NOT LIKE '%.gslides'
      AND (
          LOWER(path) LIKE '%.pdf' 
          OR LOWER(path) LIKE '%.docx' 
          OR LOWER(path) LIKE '%.doc' 
          OR LOWER(path) LIKE '%.json'
          OR LOWER(path) LIKE '%.db'
          OR LOWER(path) LIKE '%.sqlite'
          OR LOWER(path) LIKE '%hotărâre%'
          OR LOWER(path) LIKE '%judecată%'
          OR LOWER(path) LIKE '%dosar%'
          OR LOWER(path) LIKE '%cerere%'
          OR LOWER(path) LIKE '%decizie%'
          OR LOWER(path) LIKE '%procură%'
          OR LOWER(path) LIKE '%rechizitoriu%'
          OR LOWER(path) LIKE '%contract%'
          OR LOWER(path) LIKE '%иск%'
          OR LOWER(path) LIKE '%завещание%'
          OR LOWER(path) LIKE '%акт%'
          OR LOWER(path) LIKE '%справка%'
          OR LOWER(path) LIKE '%доверенность%'
      )
    ORDER BY size DESC
    LIMIT 20;
'''
with db.get_connection() as conn:
    cursor = conn.execute(query)
    tasks = [dict(row) for row in cursor.fetchall()]

print(f'[*] Найдено задач для обработки: {len(tasks)}')
if tasks:
    pool = DriveWorkerPool(db, orchestrator, max_workers=2)
    for task in tasks:
        pool.process_file_task(task, worker_id='local-cli-worker')
    print('[*] Пакетная обработка успешно завершена.')
else:
    print('[*] Нет файлов со статусом PENDING.')
"

Write-Host "[*] Шаг 3: Сохранение отчета о прогрессе..." -ForegroundColor Cyan
& $pythonPath -c "
import mcp_drive_indexer
db = mcp_drive_indexer.DatabaseManager('drive_index.db')
mcp_drive_indexer.save_progress_report(db)
print('[*] Progress report updated.')
"

Write-Host "[*] Шаг 4: Синхронизация и фиксация в Git..." -ForegroundColor Cyan
git branch --show-current
git add .
git commit -m "Lex specialis: Gemini CLI local PowerShell batch processing checkpoint [Jus Cogens]"
git push origin $(git branch --show-current)

Write-Host "[*] Все операции выполнены успешно!" -ForegroundColor Green
