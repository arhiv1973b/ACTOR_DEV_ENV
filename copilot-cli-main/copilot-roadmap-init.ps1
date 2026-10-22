# Copilot Roadmap Init — PowerShell version
# Author: A©t0rAgent

# 1. Copilot init (non-interactive)
& copilot -p "init"

# 2. Roadmap sync (non-interactive)
& copilot -p "roadmap sync"

# 3. Debug session
& copilot-debug --no-cache --once --save

# 4. GCP Cloud Logging
$logMsg = "Запуск copilot-debug завершён: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
gcloud logging write copilot-debug $logMsg --severity=INFO

# 5. Backup to GCS
$backupName = "backup_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').tar.gz"
$backupPath = Join-Path $env:TEMP $backupName
# Archive current directory to temp
Compress-Archive -Path .\* -DestinationPath $backupPath
# Copy to GCS
& gsutil cp $backupPath "gs://your-bucket-name/backups/"
