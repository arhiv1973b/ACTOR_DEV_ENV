<#
.SYNOPSIS
    CLI-style Automated Audit, Cleanup, Commit, and Push Script for ACTOR_DEV_ENV & Submodules with Configurable Log Retention.
.PARAMETER AutoCommit
    Automatically stage and commit changes across all repositories and submodules if changes exist.
.PARAMETER AutoPush
    Automatically push committed changes to remote tracking branches.
.PARAMETER RetentionDays
    Number of days to keep audit log files (default: 30).
.PARAMETER MaxLogs
    Maximum number of log files to retain (default: 0 for unlimited count).
#>

param(
    [switch]$AutoCommit = $false,
    [switch]$AutoPush = $false,
    [int]$RetentionDays = 30,
    [int]$MaxLogs = 0
)

$ErrorActionPreference = "Stop"

# Log Rotation Setup
$LogDir = "logs"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

# Retention Policy: Clean up log files older than RetentionDays
Get-ChildItem -Path $LogDir -Filter "*.log" -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$RetentionDays) } | Remove-Item -Force -ErrorAction SilentlyContinue

# MaxLogs Limit Policy: Keep only the latest N log files if MaxLogs > 0
if ($MaxLogs -gt 0) {
    $allLogs = Get-ChildItem -Path $LogDir -Filter "*.log" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
    if ($allLogs.Count -gt $MaxLogs) {
        $allLogs | Select-Object -Skip $MaxLogs | Remove-Item -Force -ErrorAction SilentlyContinue
    }
}

$sessionTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogDir "audit_$sessionTimestamp.log"
$latestLog = "audit.log"

# Rotate existing audit.log if present
if (Test-Path $latestLog) {
    $archivedName = "audit_archived_$sessionTimestamp.log"
    Move-Item $latestLog (Join-Path $LogDir $archivedName) -Force -ErrorAction SilentlyContinue
}

function Write-Log {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    Write-Host $Message -ForegroundColor $Color
    Add-Content -Path $LogFile -Value $logEntry -ErrorAction SilentlyContinue
    Add-Content -Path $latestLog -Value $logEntry -ErrorAction SilentlyContinue
}

Write-Log "============================================================" "Cyan"
Write-Log " ACTOR_DEV_ENV: AUTOMATED AUDIT, SYNC, COMMIT & PUSH" "Cyan"
Write-Log " Session Log: $LogFile" "Cyan"
Write-Log " Retention Policy: $RetentionDays days | Max Logs: $(if($MaxLogs -eq 0){'Unlimited'}else{$MaxLogs})" "Cyan"
Write-Log "============================================================" "Cyan"
if ($AutoCommit) { Write-Log " [MODE] AutoCommit: ENABLED" "Green" }
if ($AutoPush)   { Write-Log " [MODE] AutoPush: ENABLED" "Green" }

function Invoke-RepoSync {
    param(
        [string]$Path,
        [string]$Name,
        [string]$CommitMessage = "chore: automated audit & sync update"
    )
    
    if (-not (Test-Path $Path)) {
        Write-Log "  -> [$Name] Not found at $Path" "Red"
        return
    }

    Write-Log "`n------------------------------------------------------------" "DarkGray"
    Write-Log " Processing: $Name ($Path)" "Yellow"

    $status = git -C $Path status --porcelain
    if ($status) {
        Write-Log "  -> Changes detected in $Name." "Yellow"
        if ($AutoCommit) {
            git -C $Path add .
            git -C $Path commit -m $CommitMessage
            Write-Log "  -> Committed changes in $Name." "Green"
        }
    } else {
        Write-Log "  -> Working tree clean in $Name." "DarkGreen"
    }

    if ($AutoPush) {
        Write-Log "  -> Pushing $Name..." "Cyan"
        git -C $Path push
        Write-Log "  -> Pushed $Name successfully." "Green"
    }
}

# 1. Nested MCP Servers
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
Write-Log "`n------------------------------------------------------------" "DarkGray"
Write-Log " Processing: submodule-voidImageViewer (voidImageViewer)" "Yellow"
if (Test-Path "voidImageViewer") {
    $items = Get-ChildItem -Path "voidImageViewer" -Recurse -ErrorAction SilentlyContinue
    if ($items) {
        foreach ($item in $items) {
            if ($item -and (-not $item.PSIsContainer) -and ($item.Name -like "PaxHeaders.*")) {
                Remove-Item $item.FullName -Force -ErrorAction SilentlyContinue
            }
        }
        Write-Log "  -> Cleaned PaxHeaders artifacts in voidImageViewer" "Green"
    }
    Invoke-RepoSync -Path "voidImageViewer" -Name "submodule-voidImageViewer" -CommitMessage "chore: clean build artifacts and sync voidImageViewer"
} else {
    Write-Log "  -> voidImageViewer not found" "Red"
}

# 7. Main Repository Cleanup & Sync
Write-Log "`n------------------------------------------------------------" "DarkGray"
Write-Log " Processing: Main Repository (ACTOR_DEV_ENV)" "Yellow"
if (Test-Path "drive_index.db-shm") { Remove-Item "drive_index.db-shm" -Force; Write-Log "  -> Removed drive_index.db-shm" "Green" }
if (Test-Path "drive_index.db-wal") { Remove-Item "drive_index.db-wal" -Force; Write-Log "  -> Removed drive_index.db-wal" "Green" }

Invoke-RepoSync -Path "." -Name "ACTOR_DEV_ENV-Main" -CommitMessage "chore: update submodules references and audit state"

Write-Log "`n============================================================" "Cyan"
Write-Log " AUDIT, SYNC, COMMIT & PUSH COMPLETE SUCCESSFULLY" "Green"
Write-Log "============================================================" "Cyan"
