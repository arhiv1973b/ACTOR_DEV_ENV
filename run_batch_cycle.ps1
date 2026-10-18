# run_batch_cycle.ps1 - Automated micro-batch processing loop with monitoring & graph indexing
$ErrorActionPreference = "Stop"
$pythonPath = "H:\ACTOR_DEV_ENV\.venv\Scripts\python.exe"
$branch = "feature/cyber-sabotage-audit-10-2026"

Write-Host "[*] Starting automated micro-batch processing cycle (Batch Size: 5, Timeout: 30s)..." -ForegroundColor Cyan

while ($true) {
    # 1. Pre-check environment
    Write-Host "[*] Running environment pre-check..." -ForegroundColor Yellow
    & $pythonPath -c "import mcp_server; print('System pre-check passed successfully.')"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "[!] Pre-check failed."
        break
    }

    # 2. Process micro-batch of 5 critical artifacts with 30s timeout
    Write-Host "[*] Executing micro-batch processing (Limit 5)..." -ForegroundColor Yellow
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
    LIMIT 5;
'''
with db.get_connection() as conn:
    cursor = conn.execute(query)
    tasks = [dict(row) for row in cursor.fetchall()]

if not tasks:
    print('[*] NO_MORE_TASKS')
    exit(0)

print(f'[*] Processing micro-batch of {len(tasks)} critical artifacts...')
pool = DriveWorkerPool(db, orchestrator, max_workers=2, task_timeout=30)
for task in tasks:
    pool.process_file_task(task, worker_id='cli-cycle-worker')
print('[*] Micro-batch completed successfully.')
"

    # 3. Generate progress monitoring report & update progress_report.json
    Write-Host "[*] Generating progress monitoring report & updating progress_report.json..." -ForegroundColor Yellow
    & $pythonPath -c "
import mcp_drive_indexer
db = mcp_drive_indexer.DatabaseManager('drive_index.db')
stats = mcp_drive_indexer.save_progress_report(db, r'H:\ACTOR_DEV_ENV\progress_report.json')
print(f'[+] Progress report updated: Total={stats[\"total_files\"]}, Completed={stats[\"completed\"]}, Pending={stats[\"pending\"]}')
"

    # 4. Generate visual trend chart (progress_trend.png)
    Write-Host "[*] Rendering visual trend chart (progress_trend.png)..." -ForegroundColor Yellow
    & $pythonPath generate_chart.py

    # Check remaining PENDING count
    $pendingCheck = & $pythonPath -c "
from mcp_drive_indexer import DatabaseManager
db = DatabaseManager('drive_index.db')
with db.get_connection() as conn:
    c = conn.execute('SELECT COUNT(*) FROM files WHERE status = \"PENDING\"').fetchone()[0]
    print(c)
"
    Write-Host "[*] Remaining PENDING files in queue: $pendingCheck" -ForegroundColor Cyan

    # 5. Stage and Commit
    Write-Host "[*] Staging and committing changes with monitoring log & trend chart..." -ForegroundColor Yellow
    git add progress_report.json progress_trend.png batch_progress.json drive_index.db mcp_server.py mcp_drive_indexer.py generate_chart.py run_batch_cycle.ps1
    git commit -m "Lex specialis: micro-batch size 5, 30s timeout & progress checkpoint [Jus Cogens]"

    # 6. Push to remote
    Write-Host "[*] Pushing checkpoint to remote branch $branch..." -ForegroundColor Yellow
    git push origin $branch

    if ([int]$pendingCheck -eq 0) {
        Write-Host "[*] All critical artifacts processed successfully! Exiting loop." -ForegroundColor Green
        break
    }

    Write-Host "[*] Pausing 3 seconds before next iteration..." -ForegroundColor DarkGray
    Start-Sleep -Seconds 3
}
