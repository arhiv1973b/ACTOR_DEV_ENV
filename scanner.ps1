$TargetDir = "H:\ACTOR_DEV_ENV\apostille-mirror"
$ManifestPath = "H:\ACTOR_DEV_ENV\apostille_candidates_manifest.json"

Write-Host "[e-Erga_Omnes] Инициализация оптимизированного сканирования (без глубокого хеширования): $TargetDir" -ForegroundColor Cyan

if (Test-Path $TargetDir) {
    # Сбор кандидатов (ускоренный режим)
    $Candidates = Get-ChildItem -Path $TargetDir -File -Recurse | Select-Object `
        @{Name='Node_ID';Expression={[guid]::NewGuid().ToString()}},
        Name,
        Extension,
        @{Name='Size(KB)';Expression={[math]::Round($_.Length/1KB, 2)}},
        CreationTime,
        LastWriteTime,
        FullName

    $FileCount = $Candidates.Count
    Write-Host "[+] Найдено потенциальных якорных узлов (документов): $FileCount" -ForegroundColor Green

    if ($FileCount -gt 0) {
        # Экспорт структурированного графа
        $Candidates | ConvertTo-Json -Depth 2 | Out-File $ManifestPath -Encoding utf8
        Write-Host "[+] Манифест кандидатов сохранен: $ManifestPath" -ForegroundColor DarkGray
        
        # Вывод превью
        $Candidates | Select-Object Name, 'Size(KB)', CreationTime | Select-Object -First 10 | Format-Table -AutoSize
    }
} else {
    Write-Host "[-] Ошибка: Директория $TargetDir не найдена." -ForegroundColor Red
}
