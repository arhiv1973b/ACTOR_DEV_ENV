# MCP & Docker Diagnostic and Repair Toolkit
# Purpose: Verify, diagnose, and fix MCP server configuration and Docker infrastructure
# Encoding: UTF-8
# Usage: Execute in PowerShell (no profile)

# ============================================================================
# SECTION 1: MCP Diagnostics
# ============================================================================

# Check ripgrep availability and fallback options
Write-Host "=== MCP RipGrep Status ===" -ForegroundColor Cyan
$ripgrepPath = Get-Command rg -ErrorAction SilentlyContinue
if ($ripgrepPath) {
    Write-Host "✓ ripgrep (rg) found: $($ripgrepPath.Source)" -ForegroundColor Green
} else {
    Write-Host "✗ ripgrep NOT found (MCP will use GrepTool fallback)" -ForegroundColor Yellow
    Write-Host "  To install: choco install ripgrep" -ForegroundColor Gray
    Write-Host "  Or: Download from https://github.com/BurntSushi/ripgrep/releases" -ForegroundColor Gray
}

# Generate file list manually (if ripgrep unavailable)
Write-Host "`n=== Manual File Listing (Fallback) ===" -ForegroundColor Cyan
$workDir = Get-Location
$fileList = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
Write-Host "✓ Found $($fileList.Count) files in current workspace" -ForegroundColor Green
$fileList | Out-File -FilePath "mcp_files_list.txt" -Encoding UTF8
Write-Host "  Saved to: mcp_files_list.txt" -ForegroundColor Cyan

# ============================================================================
# SECTION 2: Docker Container Diagnostics
# ============================================================================

Write-Host "`n=== Docker Containers Status ===" -ForegroundColor Cyan

# List all containers with status
$containers = docker ps -a --format "{{.Names}}\t{{.Status}}\t{{.Ports}}" 2>&1
if ($containers) {
    Write-Host $containers | Format-Table -Separator "`t" -AutoSize
} else {
    Write-Host "✗ Docker not available or no containers found" -ForegroundColor Red
}

# Check specific MCP-related containers
$mcpContainers = @('actor_site', 'actor_robot', 'actor_ollama', 'act0r-ollama', 'aytor-sentinel')
Write-Host "`n=== Key Containers Health Check ===" -ForegroundColor Cyan

foreach ($container in $mcpContainers) {
    $exists = docker ps -a --filter "name=$container" --format "{{.Names}}" 2>&1
    if ($exists) {
        $status = docker ps -a --filter "name=$container" --format "{{.Status}}" 2>&1
        $health = if ($status -match 'unhealthy') { "🔴" } elseif ($status -match 'Up') { "🟢" } else { "🟡" }
        Write-Host "$health $container : $status" -ForegroundColor Cyan
    }
}

# ============================================================================
# SECTION 3: Docker Network Diagnostics
# ============================================================================

Write-Host "`n=== Docker Networks ===" -ForegroundColor Cyan
$networks = docker network ls --format "{{.Name}}\t{{.Driver}}\t{{.Scope}}" 2>&1
if ($networks) {
    Write-Host $networks | Format-Table -Separator "`t" -AutoSize
}

# Inspect actor-network connectivity
Write-Host "`n=== Checking actor-network Connectivity ===" -ForegroundColor Cyan
$networkExists = docker network ls --filter "name=actor-network" --format "{{.Name}}" 2>&1
if ($networkExists -eq 'actor-network') {
    Write-Host "✓ actor-network exists" -ForegroundColor Green
    $connectedContainers = docker network inspect actor-network --format "{{json .Containers}}" 2>&1
    Write-Host "  Connected containers: $connectedContainers" -ForegroundColor Cyan
} else {
    Write-Host "✗ actor-network NOT found" -ForegroundColor Red
}

# ============================================================================
# SECTION 4: Container Logs Analysis
# ============================================================================

Write-Host "`n=== Container Logs (Last 50 lines) ===" -ForegroundColor Cyan

foreach ($container in $mcpContainers) {
    $exists = docker ps -a --filter "name=$container" --format "{{.Names}}" 2>&1
    if ($exists) {
        Write-Host "`n--- $container ---" -ForegroundColor Yellow
        docker logs $container --tail 50 2>&1 | Select-Object -Last 20
    }
}

# ============================================================================
# SECTION 5: Port and Network Binding Checks
# ============================================================================

Write-Host "`n=== Port Bindings ===" -ForegroundColor Cyan

$portContainers = @('actor_site', 'actor_ollama', 'act0r-ollama', 'aytor-sentinel')
foreach ($container in $portContainers) {
    $ports = docker port $container 2>&1
    if ($ports) {
        Write-Host "$container :" -ForegroundColor Cyan
        Write-Host $ports -ForegroundColor Gray
    }
}

# Check for port conflicts
Write-Host "`n=== Checking for Port Conflicts ===" -ForegroundColor Cyan
$busyPorts = netstat -ano -p tcp 2>&1 | Select-String "11434|8085|8444" -ErrorAction SilentlyContinue
if ($busyPorts) {
    Write-Host "⚠ Active connections on MCP ports:" -ForegroundColor Yellow
    Write-Host $busyPorts -ForegroundColor Gray
} else {
    Write-Host "✓ No conflicts on standard MCP ports" -ForegroundColor Green
}

# ============================================================================
# SECTION 6: Docker System Resources
# ============================================================================

Write-Host "`n=== Docker System Resources ===" -ForegroundColor Cyan
$diskUsage = docker system df 2>&1
if ($diskUsage) {
    Write-Host $diskUsage -ForegroundColor Gray
}

# ============================================================================
# SECTION 7: Repair Actions (Interactive)
# ============================================================================

Write-Host "`n=== Repair Options ===" -ForegroundColor Cyan
Write-Host "1. Restart unhealthy container (actor_ollama)" -ForegroundColor Yellow
Write-Host "2. Reconnect all containers to actor-network" -ForegroundColor Yellow
Write-Host "3. Clear Docker system (prune images/volumes)" -ForegroundColor Yellow
Write-Host "4. Rebuild actor_site container" -ForegroundColor Yellow

$choice = Read-Host "Select action (1-4) or press Enter to skip"

switch ($choice) {
    "1" {
        Write-Host "Restarting actor_ollama..." -ForegroundColor Cyan
        docker restart actor_ollama
        Start-Sleep -Seconds 5
        $status = docker ps -a --filter "name=actor_ollama" --format "{{.Status}}"
        Write-Host "✓ Status: $status" -ForegroundColor Green
    }
    "2" {
        Write-Host "Reconnecting containers to actor-network..." -ForegroundColor Cyan
        @('actor_robot', 'actor_ollama', 'act0r-ollama') | ForEach-Object {
            docker network disconnect actor-network $_ 2>/dev/null
            docker network connect actor-network $_
            Write-Host "✓ $_ reconnected" -ForegroundColor Green
        }
    }
    "3" {
        Write-Host "Running docker system prune (warning: removes unused resources)..." -ForegroundColor Yellow
        $confirm = Read-Host "Continue? (y/n)"
        if ($confirm -eq 'y') {
            docker system prune -f --volumes
            Write-Host "✓ Prune complete" -ForegroundColor Green
        }
    }
    "4" {
        Write-Host "Rebuilding actor_site..." -ForegroundColor Cyan
        docker stop actor_site 2>/dev/null
        docker rm actor_site 2>/dev/null
        docker run -d --name actor_site --network actor-network -p 8085:80 -p 8444:443 nginx:latest
        Write-Host "✓ actor_site rebuilt" -ForegroundColor Green
    }
    default {
        Write-Host "No action selected" -ForegroundColor Gray
    }
}

# ============================================================================
# SECTION 8: Validation Summary
# ============================================================================

Write-Host "`n=== Validation Summary ===" -ForegroundColor Cyan
$checks = @{
    "Docker Daemon" = if (docker ps 2>&1 | Select-String "CONTAINER") { "✓" } else { "✗" }
    "actor-network" = if (docker network ls 2>&1 | Select-String "actor-network") { "✓" } else { "✗" }
    "MCP Containers Running" = (docker ps --filter "status=running" --format "{{.Names}}" 2>&1 | Measure-Object -Line).Lines
    "ripgrep Available" = if (Get-Command rg 2>/dev/null) { "✓" } else { "✗" }
}

foreach ($check in $checks.GetEnumerator()) {
    Write-Host "$($check.Name): $($check.Value)" -ForegroundColor Cyan
}

Write-Host "`n✓ Diagnostics complete" -ForegroundColor Green
