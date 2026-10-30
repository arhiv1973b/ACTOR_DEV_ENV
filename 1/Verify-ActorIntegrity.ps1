function Verify-ActorIntegrity {
    [CmdletBinding()]
    param()

    # Принудительная UTF-8 среда
    [Console]::InputEncoding  = [System.Text.Encoding]::UTF8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding           = [System.Text.Encoding]::UTF8
    $utf8NoBom                = New-Object System.Text.UTF8Encoding $false

    $mirrorDir    = "H:\ACTOR_DEV_ENV\apostille-mirror"
    $auditor      = "A©t0r"
    $signatureKey = "# [⚖ A©tor Declaration]"

    Write-Host ""
    Write-Host "=== TI-ULA Integrity Verification ===" -ForegroundColor Cyan
    Write-Host "AUDITOR: $auditor" -ForegroundColor Cyan
    Write-Host "DECLARATION: $signatureKey" -ForegroundColor DarkGray
    Write-Host ""

    # 1. Поиск самого свежего registry_*.json
    if (-not (Test-Path -LiteralPath $mirrorDir)) {
        Write-Host "[COMPROMISED] Mirror directory not found: $mirrorDir" -ForegroundColor Red
        return
    }

    $latestRegistry = Get-ChildItem -LiteralPath $mirrorDir -Filter "registry_*.json" -File |
                      Sort-Object LastWriteTime -Descending |
                      Select-Object -First 1

    if (-not $latestRegistry) {
        Write-Host "[COMPROMISED] No registry_*.json snapshots found" -ForegroundColor Red
        return
    }

    Write-Host "Snapshot : $($latestRegistry.Name)" -ForegroundColor Gray

    # 2. Чтение (UTF-8 без BOM)
    try {
        $raw = [System.IO.File]::ReadAllText($latestRegistry.FullName, $utf8NoBom)
        $snapshot = $raw | ConvertFrom-Json
    }
    catch {
        Write-Host "[COMPROMISED] Failed to parse registry JSON" -ForegroundColor Red
        return
    }

    $expectedRoot = $snapshot.merkle_root
    $nodes        = @($snapshot.nodes)

    if (-not $expectedRoot -or $nodes.Count -eq 0) {
        Write-Host "[COMPROMISED] Registry missing merkle_root or nodes" -ForegroundColor Red
        return
    }

    Write-Host "Nodes    : $($nodes.Count)" -ForegroundColor Gray
    Write-Host "Expected : $expectedRoot" -ForegroundColor Gray

    # 3. Рекалькуляция Root Hash (детерминированная сортировка по filename или manifest_id)
    $sortedNodes = @($nodes) | Sort-Object { if ($_.filename) { $_.filename } else { $_.manifest_id } }
    $nodesJson   = $sortedNodes | ConvertTo-Json -Compress -Depth 10
    $nodesBytes  = $utf8NoBom.GetBytes($nodesJson)
    $sha256      = [System.Security.Cryptography.SHA256]::Create()
    $calcBytes   = $sha256.ComputeHash($nodesBytes)
    $calculatedRoot = [System.BitConverter]::ToString($calcBytes).Replace("-", "").ToLowerInvariant()

    Write-Host "Calculated: $calculatedRoot" -ForegroundColor Gray
    Write-Host ""

    # 4. Сверка Root Hash
    $rootValid = ($calculatedRoot -eq $expectedRoot)

    # 5. Проверка физических файлов (для документов с source_path)
    $filesOk     = $true
    $missing     = 0
    $hashMismatch = 0

    foreach ($node in $nodes) {
        if ($node.source_path) {
            $src = $node.source_path
            $expectedHash = $node.sha256

            if (-not (Test-Path -LiteralPath $src -PathType Leaf)) {
                $missing++
                $filesOk = $false
                continue
            }

            try {
                $fileBytes = [System.IO.File]::ReadAllBytes($src)
                $h = $sha256.ComputeHash($fileBytes)
                $actualHash = [System.BitConverter]::ToString($h).Replace("-", "").ToLowerInvariant()

                if ($actualHash -ne $expectedHash) {
                    $hashMismatch++
                    $filesOk = $false
                }
            }
            catch {
                $hashMismatch++
                $filesOk = $false
            }
        }
    }

    # 6. Итоговый вердикт
    if ($rootValid -and $filesOk) {
        Write-Host "[VALID] Archive integrity confirmed" -ForegroundColor Green
        Write-Host "Root Hash match + all verified source files present and unchanged" -ForegroundColor Green
    }
    else {
        Write-Host "[COMPROMISED] Integrity check failed" -ForegroundColor Red
        if (-not $rootValid) {
            Write-Host "  - Merkle Root mismatch" -ForegroundColor Red
        }
        if ($missing -gt 0) {
            Write-Host "  - Missing files: $missing" -ForegroundColor Red
        }
        if ($hashMismatch -gt 0) {
            Write-Host "  - Hash mismatches: $hashMismatch" -ForegroundColor Red
        }
    }

    Write-Host ""
    Write-Host "AUDITOR: $auditor" -ForegroundColor Cyan
    Write-Host "======================================" -ForegroundColor Cyan
}
