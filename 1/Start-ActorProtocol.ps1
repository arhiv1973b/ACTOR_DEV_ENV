# ============================================================
# ПРОТОКОЛ: ACTOR-FUNDING-REGISTRY-v1
# Мастер-запуск: Funding + Registry + Commit
# Agent:  A©t0r | Author: A©tor
# Repo:   arhiv1973b/apostille-archive
# Branch: Actor-IP-Protection
# ============================================================

param(
    [string]$RepoPath = "C:\Users\arhiv\apostille-legal-case\apostille-archive",
    [switch]$SkipFunding,
    [switch]$SkipRegistry,
    [switch]$VerifyFiles,
    [switch]$DryRun
)

$ScriptDir = Split-Path $MyInvocation.MyCommand.Path -Parent

function Write-Actor { param([string]$Msg, [string]$Color = "Cyan")
    Write-Host "[A`u{00A9}t0r] $Msg" -ForegroundColor $Color }

Write-Actor "=========================================" "Magenta"
Write-Actor " ACTOR-FUNDING-REGISTRY-v1 СТАРТ" "Magenta"
Write-Actor "=========================================" "Magenta"

# ── Шаг 1: Развёртывание FUNDING.yml + SUPPORT.md ───────────
if (-not $SkipFunding) {
    Write-Actor "Шаг 1/2: Активация ACTOR-FUNDING-v1..." "Yellow"
    $fundArgs = @{ RepoPath = $RepoPath }
    if ($DryRun) { $fundArgs["DryRun"] = $true }
    & "$ScriptDir\Deploy-ActorFunding.ps1" @fundArgs
    Write-Actor "Шаг 1/2: Funding — DONE" "Green"
} else {
    Write-Actor "Шаг 1/2: Funding — ПРОПУЩЕН" "Gray"
}

# ── Шаг 2: Верификация реестра + генерация отчёта ───────────
if (-not $SkipRegistry) {
    Write-Actor "Шаг 2/2: Верификация ACTOR-REGISTRY-v1..." "Yellow"
    $regArgs = @{ RepoPath = $RepoPath }
    if ($VerifyFiles) { $regArgs["VerifyFiles"] = $true }
    if ($DryRun)      { $regArgs["DryRun"]      = $true }
    $result = & "$ScriptDir\Verify-ActorRegistry.ps1" @regArgs
    Write-Actor "Шаг 2/2: Registry — DONE ($($result.TotalNodes) узлов)" "Green"
} else {
    Write-Actor "Шаг 2/2: Registry — ПРОПУЩЕН" "Gray"
}

Write-Actor "=========================================" "Magenta"
Write-Actor " ACTOR-FUNDING-REGISTRY-v1 ЗАВЕРШЁН" "Magenta"
Write-Actor " GitHub Sponsors: github.com/sponsors/arhiv1973b" "White"
Write-Actor " Patreon:         patreon.com/arhiv240" "White"
Write-Actor " Evidence Vault:  arhiv1973b.github.io/apostille-mirror" "White"
Write-Actor "=========================================" "Magenta"
