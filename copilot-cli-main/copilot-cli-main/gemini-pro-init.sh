#!/bin/bash
set -e
# 1. Запуск copilot-debug
copilot-debug --no-cache --once --save
# 2. Логирование в GCP Cloud Logging (пример через gcloud)
gcloud logging write copilot-debug "Запуск copilot-debug завершён: $(date)" --severity=INFO
# 3. Бэкап в GCS
BACKUP_NAME="backup_$(date +%F_%H-%M-%S).tar.gz"
tar -czf "/tmp/$BACKUP_NAME" .
gsutil cp "/tmp/$BACKUP_NAME" gs://your-bucket-name/backups/
