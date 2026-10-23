\Continue = 'Stop'
Write-Host "[*] Начало самолечения системы..." -ForegroundColor Yellow

# 1. Исправление DNS-связи для робота
# Добавляем алиас для контейнера Ollama в сеть
docker network disconnect actor_dev_env_actor-net actor_ollama
docker network connect --alias ollama actor_dev_env_actor-net actor_ollama
Write-Host "[+] DNS-алиас 'ollama' успешно назначен." -ForegroundColor Green

# 2. Проверка Git защиты
Write-Host "[*] Проверка защиты веток..." -ForegroundColor Cyan
cd H:\ACTOR_DEV_ENV
git fetch origin
git branch -a | Select-String "Actor-IP-Protection"

Write-Host "[+] Аудит завершен. Система переходит в режим мониторинга." -ForegroundColor Green
