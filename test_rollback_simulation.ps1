# [⚖ A©tor Declaration]
# A©t0r Identity: arhiv1973b
# Описание: Изолированный тест механизма отката Git (git reset HEAD~1) при падении push

$WorkspacePath = "H:\ACTOR_DEV_ENV"
Set-Location -Path $WorkspacePath

# 1. Сохранение оригинального URL репозитория
$RealOrigin = git config --get remote.origin.url
if (-not $RealOrigin) {
    Write-Host "Ошибка: Не найден remote origin. Убедитесь, что вы в Git-репозитории." -ForegroundColor Red
    exit
}

Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] Оригинальный URL сохранен: $RealOrigin" -ForegroundColor Cyan

try {
    # 2. Искусственный сбой (подмена URL)
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] Симуляция сбоя: подмена URL на невалидный адрес..." -ForegroundColor Yellow
    git remote set-url origin "https://github.com/invalid-actor/blackhole-repo.git"

    # 3. Искусственный триггер ремонта (создание временного файла)
    $TestFile = "test_rollback_trigger.txt"
    Add-Content -Path $TestFile -Value "Тестовая модификация для проверки отката"
    
    git add $TestFile 2>&1 | Out-Null
    git commit -m "⚖️ Auto-repair: TEST ROLLBACK" 2>&1 | Out-Null
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] Тестовый коммит создан." -ForegroundColor Cyan

    # 4. Попытка синхронизации (которая гарантированно упадет)
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] Выполнение git push..." -ForegroundColor Yellow
    $GitPushOut = git push 2>&1 | Out-String

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] ОШИБКА Git Push перехвачена. Сервер недоступен." -ForegroundColor Red
        
        # 5. Срабатывание защитного механизма отката
        Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] Инициализация git reset HEAD~1..." -ForegroundColor Yellow
        $ResetOut = git reset HEAD~1 2>&1 | Out-String
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] УСПЕХ: Выполнен защитный откат. Коммит отменен, изменения сохранены локально." -ForegroundColor Green
        } else {
            Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] КРИТИЧЕСКАЯ ОШИБКА ОТКАТА: $ResetOut" -ForegroundColor Red
        }
    }
} finally {
    # 6. Восстановление исходного состояния
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] Восстановление оригинального URL origin..." -ForegroundColor Cyan
    git remote set-url origin $RealOrigin
    
    # Удаление тестового файла
    if (Test-Path $TestFile) { 
        Remove-Item $TestFile -Force 
        Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] Временный тестовый файл удален." -ForegroundColor Cyan
    }
    
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] Симуляция успешно завершена. Инфраструктура в исходном состоянии." -ForegroundColor Green
}
