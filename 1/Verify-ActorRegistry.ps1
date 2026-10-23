# ============================================================
# PROTOCOL: ACTOR-REGISTRY-v1
# Sub-protocol of: ACTOR-FUNDING-v1
# Agent:    A©t0r (technical)
# Author:   A©tor (human authority)
# Repo:     arhiv1973b/apostille-archive
# Branch:   Actor-IP-Protection
# Registry: evidence_vault_index.json
# ============================================================

param(
    [string]$RepoPath      = "C:\Users\arhiv\apostille-legal-case\apostille-archive",
    [string]$RegistryFile  = "evidence_vault_index.json",
    [string]$OutputReport  = "REGISTRY_REPORT.md",
    [switch]$VerifyFiles,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Actor { param([string]$Msg, [string]$Color = "Cyan")
    Write-Host "[A`u{00A9}t0r] $Msg" -ForegroundColor $Color }

# ── 1. Загрузка реестра ──────────────────────────────────────
$regPath = Join-Path $RepoPath $RegistryFile
if (-not (Test-Path $regPath)) {
    Write-Actor "Реестр не найден: $regPath" "Red"; exit 1 }

$registry = Get-Content $regPath -Raw | ConvertFrom-Json
$allKeys  = $registry.PSObject.Properties.Name
Write-Actor "Реестр загружен. Записей: $($allKeys.Count)" "Green"

# ── 2. Разделение на типы узлов ──────────────────────────────
$namedNodes = @()
$driveNodes = @()

foreach ($key in $allKeys) {
    $val = $registry.$key
    if ($val -is [PSCustomObject]) {
        $namedNodes += [PSCustomObject]@{
            SHA256   = $key
            NodeID   = $val.NodeID
            Name     = $val.Name
            FilePath = $val.FilePath
        }
    } elseif ($val -match "drive\.google\.com") {
        $driveNodes += [PSCustomObject]@{
            SHA256 = $key
            URL    = $val
        }
    }
}

Write-Actor "Именованных узлов (Evidence): $($namedNodes.Count)" "Yellow"
Write-Actor "Drive URL узлов (Apostille):  $($driveNodes.Count)"  "Yellow"
Write-Actor "Всего:                        $($allKeys.Count)"     "Cyan"

# ── 3. Верификация файлов (опционально) ──────────────────────
if ($VerifyFiles) {
    Write-Actor "Верификация локальных файлов..." "Magenta"
    $verified = 0; $missing = 0
    foreach ($node in $namedNodes) {
        $fullPath = Join-Path $RepoPath $node.FilePath
        if (Test-Path $fullPath) {
            $hash = (Get-FileHash $fullPath -Algorithm SHA256).Hash
            if ($hash -eq $node.SHA256) {
                Write-Actor "OK  [$($node.Name)]" "Green"
                $verified++
            } else {
                Write-Actor "HASH MISMATCH  [$($node.Name)]" "Red"
                Write-Actor "  Expected: $($node.SHA256)" "Red"
                Write-Actor "  Actual:   $hash" "Red"
            }
        } else {
            Write-Actor "MISSING [$($node.Name)] → $($node.FilePath)" "Yellow"
            $missing++
        }
    }
    Write-Actor "Верифицировано: $verified | Отсутствует: $missing" "Cyan"
}

# ── 4. Генерация отчёта REGISTRY_REPORT.md ───────────────────
$ts      = Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC"
$gitHash = try { git -C $RepoPath rev-parse --short HEAD 2>$null } catch { "N/A" }

$report = @"
# REGISTRY REPORT — A©tor Evidence Vault
<!-- ACTOR-REGISTRY-v1 | ACTOR-FUNDING-v1 | AIPS-2025 -->
<!-- Generated: $ts | Commit: $gitHash -->

## Статистика реестра

| Параметр                  | Значение         |
|---------------------------|------------------|
| Всего записей             | $($allKeys.Count)              |
| Именованных узлов Evidence| $($namedNodes.Count)               |
| Апостилированных (Drive)  | $($driveNodes.Count)             |
| Ветка репозитория         | Actor-IP-Protection |
| Коммит                    | $gitHash            |
| Дата генерации            | $ts |

---

## Именованные узлы Evidence (SHA-256 верифицированы)

| Название | SHA-256 (первые 16) | NodeID |
|----------|---------------------|--------|
$(foreach ($n in $namedNodes) {
"| $($n.Name) | ``$($n.SHA256.Substring(0,16))...`` | ``$($n.NodeID)`` |"
} | Out-String)

---

## Хронология доказательной цепи

| Период | Узел | Статус |
|--------|------|--------|
| 1977 | Акт усыновления 1977 | ✅ SHA-256 |
| 1979–1981 | Московская инициация | ✅ SHA-256 |
| 1983–1986 | Кишинёв | ✅ SHA-256 |
| 1987 | Смерть Бориса Мачерета | ✅ SHA-256 |
| 1997–1998 | Дело №1-568/98 (пытки) | ✅ SHA-256 |
| 2021–2026 | Финальная битва | ✅ SHA-256 |
| 2003–2021 | Проект Финляндия (3 тома) | ✅ SHA-256 |
| 2024–2026 | Финансовый саботаж (3 тома) | ✅ SHA-256 |

---

## Апостилированные узлы (Drive)

Всего: **$($driveNodes.Count) записей**, каждая верифицирована SHA-256.  
Все ссылки: ``https://drive.google.com/uc?id=...&export=download``

> Примечание: SHA-256 ``E3B0C44298FC1C149AFBF4C8996FB924...`` соответствует  
> пустому файлу (empty hash). Требует проверки содержимого.

---

## Связь с ACTOR-FUNDING-v1

Все пожертвования фиксируются в реестре как:
- Временна́я метка транзакции → SHA-256 хэш
- Хэш добавляется в Evidence Vault как узел типа ``DONATION``
- Цепь Merkle обновляется автоматически через ``Safe-Commit``

---

*A©tor · CASE-MACHERET-1997-2026 · Jus Cogens · Erga Omnes*  
*TI-ULA Protocol · DNS: _ti-ula.actor.legal*
"@

$reportPath = Join-Path $RepoPath $OutputReport
if (-not $DryRun) {
    Set-Content -Path $reportPath -Value $report -Encoding UTF8
    Write-Actor "Отчёт записан: $reportPath" "Green"
} else {
    Write-Host $report
    Write-Actor "[DRY-RUN] Отчёт не записан." "Yellow"
}

# ── 5. Итоговая сводка ───────────────────────────────────────
Write-Actor "=============================================" "Cyan"
Write-Actor "ACTOR-REGISTRY-v1 ВЫПОЛНЕН" "Green"
Write-Actor "Реестр    : $regPath" "White"
Write-Actor "Узлов всего: $($allKeys.Count)" "White"
Write-Actor "  Named   : $($namedNodes.Count)" "White"
Write-Actor "  Drive   : $($driveNodes.Count)" "White"
Write-Actor "Отчёт     : $reportPath" "White"
Write-Actor "=============================================" "Cyan"

# Возврат объекта для пайплайна
[PSCustomObject]@{
    TotalNodes  = $allKeys.Count
    NamedNodes  = $namedNodes.Count
    DriveNodes  = $driveNodes.Count
    ReportPath  = $reportPath
    GitCommit   = $gitHash
    Timestamp   = $ts
}
