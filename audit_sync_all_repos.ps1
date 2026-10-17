<#
.SYNOPSIS
    CLI-style Automated Audit, Cleanup, Commit, and Push Script for ACTOR_DEV_ENV & Submodules.
.PARAMETER AutoCommit
    Automatically stage and commit changes across all repositories and submodules if changes exist.
.PARAMETER AutoPush
    Automatically push committed changes to remote tracking branches.
#>

param(
    [switch]$AutoCommit = $false,
    [switch]$AutoPush = $false
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " ACTOR_DEV_ENV: AUTOMATED AUDIT, SYNC, COMMIT & PUSH" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
if ($AutoCommit) { Write-Host " [MODE] AutoCommit: ENABLED" -ForegroundColor Green }
if ($AutoPush)   { Write-Host " [MODE] AutoPush: ENABLED" -ForegroundColor Green }

function Invoke-RepoSync {
    param(
        [string]$Path,
        [string]$Name,
        [string]$CommitMessage = "chore: automated audit & sync update"
    )
    
    if (-not (Test-Path $Path)) {
        Write-Host "  -> [$Name] Not found at $Path" -ForegroundColor Red
        return
    }

    Write-Host "`n------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host " Processing: $Name ($Path)" -ForegroundColor Yellow

    # Check for changes
    $status = git -C $Path status --porcelain
    if ($status) {
        Write-Host "  -> Changes detected in $Name." -ForegroundColor Yellow
        if ($AutoCommit) {
            git -C $Path add .
            git -C $Path commit -m $CommitMessage
            Write-Host "  -> Committed changes in $Name." -ForegroundColor Green
        }
    } else {
        Write-Host "  -> Working tree clean in $Name." -ForegroundColor DarkGreen
    }

    if ($AutoPush) {
        Write-Host "  -> Pushing $Name..." -ForegroundColor Cyan
        git -C $Path push
        Write-Host "  -> Pushed $Name successfully." -ForegroundColor Green
    }
}

# 1. Submodule / Nested MCP Servers
if (Test-Path "projects/mcp-servers/mcp-servers") {
    Invoke-RepoSync -Path "projects/mcp-servers/mcp-servers" -Name "nested-mcp-servers" -CommitMessage "chore: update nested mcp-servers configs and docs"
}

# 2. Submodule projects/mcp-servers
Invoke-RepoSync -Path "projects/mcp-servers" -Name "submodule-mcp-servers" -CommitMessage "chore: update submodule mcp-servers reference"

# 3. Submodule .actor_socket
Invoke-RepoSync -Path ".actor_socket" -Name "submodule-actor_socket" -CommitMessage "chore: update .actor_socket tool registry and scripts"

# 4. Submodule projects/antigravity-sdk-python
Invoke-RepoSync -Path "projects/antigravity-sdk-python" -Name "submodule-antigravity-sdk-python" -CommitMessage "chore: sync models to gemini-3.5-pro and update protobufs"

# 5. Submodule projects/testcontainers-cloud-nodejs-example
Invoke-RepoSync -Path "projects/testcontainers-cloud-nodejs-example" -Name "submodule-testcontainers-cloud-nodejs-example" -CommitMessage "chore: update testcontainers and node packages"

# 6. Submodule voidImageViewer (with PaxHeaders cleanup)
Write-Host "`n------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host " Processing: submodule-voidImageViewer (voidImageViewer)" -ForegroundColor Yellow
if (Test-Path "voidImageViewer") {
    $items = Get-ChildItem -Path "voidImageViewer" -Recurse -ErrorAction SilentlyContinue
    if ($items) {
        foreach ($item in $items) {
            if ($item -and (-not $item.PSIsContainer) -and ($item.Name -like "PaxHeaders.*")) {
                Remove-Item $item.FullName -Force -ErrorAction SilentlyContinue
            }
        }
        Write-Host "  -> Cleaned PaxHeaders artifacts in voidImageViewer" -ForegroundColor Green
    }
    Invoke-RepoSync -Path "voidImageViewer" -Name "submodule-voidImageViewer" -CommitMessage "chore: clean build artifacts and sync voidImageViewer"
} else {
    Write-Host "  -> voidImageViewer not found" -ForegroundColor Red
}

# 7. Main Repository Cleanup & Sync
Write-Host "`n------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host " Processing: Main Repository (ACTOR_DEV_ENV)" -ForegroundColor Yellow
if (Test-Path "drive_index.db-shm") { Remove-Item "drive_index.db-shm" -Force; Write-Host "  -> Removed drive_index.db-shm" -ForegroundColor Green }
if (Test-Path "drive_index.db-wal") { Remove-Item "drive_index.db-wal" -Force; Write-Host "  -> Removed drive_index.db-wal" -ForegroundColor Green }

Invoke-RepoSync -Path "." -Name "ACTOR_DEV_ENV-Main" -CommitMessage "chore: update submodules references and audit state"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host " AUDIT, SYNC, COMMIT & PUSH COMPLETE SUCCESSFULLY" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
