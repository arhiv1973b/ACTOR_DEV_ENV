$dest = "H:\ACTOR_DEV_ENV\EVIDENCE_REGISTRY_INDEX.json"
Write-Host "Генерация EVIDENCE_REGISTRY_INDEX.json в корне репозитория..."

$chunks = 1..7 | ForEach-Object { "H:\ACTOR_DEV_ENV\registry_chunks\registry_chunk_$_.json" }
$combined = [System.Collections.Generic.List[object]]::new()

foreach ($chunk in $chunks) {
    if (Test-Path $chunk) {
        Write-Host "Чтение chunk..."
        $content = Get-Content -LiteralPath $chunk -Raw -Encoding UTF8
        try {
            $json = $content | ConvertFrom-Json
            if ($json -is [array]) {
                $combined.AddRange($json)
            } else {
                $combined.Add($json)
            }
        } catch {
            Write-Host "Ошибка парсинга JSON"
        }
    }
}

Write-Host "Запись объединенного индекса в $dest..."
$combined | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $dest -Encoding UTF8
Write-Host "Индекс успешно создан!"

git lfs install
git lfs track "EVIDENCE_REGISTRY_INDEX.json"

git add .gitattributes
git commit -m "chore(lfs): track EVIDENCE_REGISTRY_INDEX.json with Git LFS" -ErrorAction SilentlyContinue

git add EVIDENCE_REGISTRY_INDEX.json
git commit -m "chore(lfs): generate and migrate EVIDENCE_REGISTRY_INDEX.json to LFS storage"

git push origin udhr-audit-rebuild-2026
git lfs push origin udhr-audit-rebuild-2026
