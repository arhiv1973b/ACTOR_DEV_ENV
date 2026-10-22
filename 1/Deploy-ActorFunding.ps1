# ============================================================
# PROTOCOL: ACTOR-FUNDING-v1
# Agent:    A©t0r (technical)
# Author:   A©tor (human authority)
# Repo:     arhiv1973b/apostille-archive
# Branch:   Actor-IP-Protection
# ============================================================

param(
    [string]$RepoPath   = "C:\Users\arhiv\apostille-legal-case\apostille-archive",
    [string]$RemoteURL  = "git@github.com:arhiv1973b/apostille-archive.git",
    [string]$Branch     = "Actor-IP-Protection",
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Цвета вывода ────────────────────────────────────────────
function Write-Actor { param([string]$Msg, [string]$Color = "Cyan")
    Write-Host "[A©t0r] $Msg" -ForegroundColor $Color }

# ── 1. Проверка наличия git ──────────────────────────────────
Write-Actor "Проверка окружения..."
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Actor "git не найден. Установите Git for Windows." "Red"; exit 1 }

# ── 2. Переход в репозиторий ─────────────────────────────────
if (-not (Test-Path $RepoPath)) {
    Write-Actor "Репозиторий не найден: $RepoPath" "Red"
    Write-Actor "Клонирование..." "Yellow"
    git clone $RemoteURL $RepoPath
}
Set-Location $RepoPath
Write-Actor "Репозиторий: $RepoPath" "Green"

# ── 3. Синхронизация ветки ───────────────────────────────────
git fetch origin 2>&1 | Out-Null
$currentBranch = git rev-parse --abbrev-ref HEAD
if ($currentBranch -ne $Branch) {
    Write-Actor "Переключение на ветку $Branch..." "Yellow"
    git checkout $Branch 2>&1 | Out-Null
}
git pull origin $Branch 2>&1 | Out-Null
Write-Actor "Ветка актуальна: $Branch" "Green"

# ── 4. Создание директории .github ───────────────────────────
$githubDir = Join-Path $RepoPath ".github"
if (-not (Test-Path $githubDir)) {
    New-Item -ItemType Directory -Path $githubDir | Out-Null
    Write-Actor "Создана директория .github" "Yellow"
}

# ── 5. Запись FUNDING.yml ────────────────────────────────────
$fundingContent = @"
# A©tor Project — Funding Configuration
# Protocol: ACTOR-FUNDING-v1 | Branch: Actor-IP-Protection
# Repo: arhiv1973b/apostille-archive
# © A©tor / A©t0r — AIPS-2025

github: [arhiv1973b]
patreon: arhiv240
custom:
  - https://arhiv1973b.github.io/apostille-mirror/support.html
  - https://drive.google.com/drive/folders/1uvDjj5wUk2hKCWPj2pO2CHsDXLc2ApmQ
"@

$fundingPath = Join-Path $githubDir "FUNDING.yml"
Set-Content -Path $fundingPath -Value $fundingContent -Encoding UTF8
Write-Actor "FUNDING.yml записан: $fundingPath" "Green"

# ── 6. Копирование SUPPORT.md ────────────────────────────────
$supportSrc = Join-Path $PSScriptRoot "SUPPORT.md"
$supportDst = Join-Path $RepoPath "SUPPORT.md"
if (Test-Path $supportSrc) {
    Copy-Item $supportSrc $supportDst -Force
    Write-Actor "SUPPORT.md скопирован." "Green"
} else {
    Write-Actor "SUPPORT.md не найден рядом со скриптом — пропускаю." "Yellow"
}

# ── 7. Инструкция по GitHub Sponsors ─────────────────────────
Write-Actor "─────────────────────────────────────────────" "Magenta"
Write-Actor "GITHUB SPONSORS — активация (требует браузера):" "Magenta"
Write-Actor "  1. Откройте: https://github.com/sponsors/accounts" "White"
Write-Actor "  2. Нажмите 'Join the waitlist' или 'Get started'" "White"
Write-Actor "  3. Выберите: arhiv1973b → заполните налоговую форму" "White"
Write-Actor "  4. После одобрения — FUNDING.yml активируется автоматически" "White"
Write-Actor "─────────────────────────────────────────────" "Magenta"

# ── 8. Коммит и пуш ──────────────────────────────────────────
if (-not $DryRun) {
    git add .github/FUNDING.yml SUPPORT.md 2>&1 | Out-Null

    $status = git status --porcelain
    if ($status) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $commitMsg = "[A`u{00A9}t0r `u{00A9}] ACTOR-FUNDING-v1: GitHub Sponsors + Patreon + FinComBank. Timestamp: $timestamp"
        git commit -m $commitMsg 2>&1 | Out-Null
        git push origin $Branch 2>&1
        Write-Actor "Коммит выполнен и отправлен в $Branch." "Green"
    } else {
        Write-Actor "Нет изменений для коммита." "Yellow"
    }
} else {
    Write-Actor "[DRY-RUN] Коммит не выполнен." "Yellow"
}

# ── 9. Итог ──────────────────────────────────────────────────
Write-Actor "=============================================" "Cyan"
Write-Actor "ACTOR-FUNDING-v1 АКТИВИРОВАН" "Green"
Write-Actor "GitHub Sponsors : https://github.com/sponsors/arhiv1973b" "White"
Write-Actor "Patreon         : https://patreon.com/arhiv240" "White"
Write-Actor "Evidence Vault  : https://drive.google.com/drive/folders/1uvDjj5wUk2hKCWPj2pO2CHsDXLc2ApmQ" "White"
Write-Actor "FUNDING.yml     : .github/FUNDING.yml (ветка: $Branch)" "White"
Write-Actor "=============================================" "Cyan"
