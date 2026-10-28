function Sync-ActorMirror {
    [CmdletBinding()]
    param()

    # Принудительная UTF-8 среда без BOM
    [Console]::InputEncoding  = [System.Text.Encoding]::UTF8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding           = [System.Text.Encoding]::UTF8
    $utf8NoBom                = New-Object System.Text.UTF8Encoding $false

    $manifestsDir = "H:\ACTOR_DEV_ENV\manifests"
    $mirrorDir    = "H:\ACTOR_DEV_ENV\apostille-mirror"
    $signatureKey = "# [⚖ A©tor Declaration]"
    $operator     = "A©t0r"

    # 1. Сбор манифестов
    if (-not (Test-Path -LiteralPath $manifestsDir)) {
        @{ status = "error"; message = "Manifests directory not found"; merkle_root = $null } | ConvertTo-Json -Compress
        return
    }

    $manifestFiles = Get-ChildItem -LiteralPath $manifestsDir -Filter "*.json" -File -Recurse |
                     Sort-Object Name

    $nodes = @()
    foreach ($file in $manifestFiles) {
        try {
            $content = [System.IO.File]::ReadAllText($file.FullName, $utf8NoBom)
            $obj = $content | ConvertFrom-Json
            $nodes += $obj
        }
        catch {
            # Пропускаем битые манифесты, чтобы не ломать весь снимок
            continue
        }
    }

    # Детерминированная сортировка узлов по filename или manifest_id
    $sortedNodes = @($nodes) | Sort-Object { if ($_.filename) { $_.filename } else { $_.manifest_id } }

    # 2. Индексация → детерминированный JSON-массив
    $nodesJson = $sortedNodes | ConvertTo-Json -Compress -Depth 10

    # 3. Root Hash (SHA-256 от сжатого массива)
    $nodesBytes = $utf8NoBom.GetBytes($nodesJson)
    $sha256     = [System.Security.Cryptography.SHA256]::Create()
    $hashBytes  = $sha256.ComputeHash($nodesBytes)
    $merkleRoot = [System.BitConverter]::ToString($hashBytes).Replace("-", "").ToLowerInvariant()

    # 4. Snapshot
    $timestamp  = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $snapshotId = $timestamp
    $registryName = "registry_{0}.json" -f ($timestamp -replace "[:\-]", "" -replace "T", "_" -replace "Z", "")
    $registryPath = Join-Path $mirrorDir $registryName

    $snapshot = [ordered]@{
        snapshot_id  = $snapshotId
        merkle_root  = $merkleRoot
        operator     = $operator
        declaration  = $signatureKey
        nodes_count  = $sortedNodes.Count
        nodes        = $sortedNodes
    }

    $snapshotJson = $snapshot | ConvertTo-Json -Depth 10

    if (-not (Test-Path -LiteralPath $mirrorDir)) {
        New-Item -ItemType Directory -Path $mirrorDir -Force | Out-Null
    }

    [System.IO.File]::WriteAllText($registryPath, $snapshotJson, $utf8NoBom)

    # 5. Git Commit (полностью автономно)
    $gitStatus = "skipped"
    $commitHash = $null

    Push-Location $mirrorDir
    try {
        # Инициализация репозитория при необходимости
        if (-not (Test-Path -LiteralPath (Join-Path $mirrorDir ".git"))) {
            & git init --quiet 2>$null
        }

        & git add --all 2>$null

        $status = & git status --porcelain 2>$null
        if ($status) {
            $commitMsg = @"
STATE: $merkleRoot
AUTHOR: A©t0r
SIGNATURE: $signatureKey
"@
            & git commit -m $commitMsg --quiet 2>$null
            if ($LASTEXITCODE -eq 0) {
                $gitStatus  = "committed"
                $commitHash = (& git rev-parse HEAD 2>$null).Trim()
            }
            else {
                $gitStatus = "commit_failed"
            }
        }
        else {
            $gitStatus = "no_changes"
        }
    }
    catch {
        $gitStatus = "error"
    }
    finally {
        Pop-Location
    }

    # 6. Короткий статусный JSON
    [ordered]@{
        status       = "ok"
        snapshot_id  = $snapshotId
        merkle_root  = $merkleRoot
        nodes_count  = $sortedNodes.Count
        registry     = $registryName
        git          = $gitStatus
        commit       = $commitHash
        operator     = $operator
    } | ConvertTo-Json -Compress
}
