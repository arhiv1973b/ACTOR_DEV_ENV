Set-Location H:\ACTOR_DEV_ENV
$ErrorActionPreference = "Stop"
$Repo = "arhiv1973b/evidence-vault"
$Workflow = "recovery-test.yml"
$LogFile = "H:\ACTOR_DEV_ENV\recovery-monitor.log"
$SuccessStreak = 0

while ($true) {
  trap { Add-Content $LogFile "[$(Get-Date)] ERROR: $_" }
  $startedAt = Get-Date
  Add-Content $LogFile "`n[$startedAt] Dispatching recovery probe"
  gh workflow run $Workflow --repo $Repo | Out-Null
  Start-Sleep -Seconds 20

  $runs = gh run list --repo $Repo --workflow $Workflow --limit 10 --json databaseId,status,conclusion,createdAt | ConvertFrom-Json
  
  $run = $runs |
    Where-Object { [datetime]$_.createdAt -ge $startedAt.AddSeconds(-300) } |
    Sort-Object { [datetime]$_.createdAt } -Descending |
    Select-Object -First 1

  if (-not $run -or -not $run.databaseId) {
    Add-Content $LogFile "[$(Get-Date)] No fresh run found after dispatch"
    $SuccessStreak = 0
    Start-Sleep -Seconds 1800
    continue
  }

  $runId = $run.databaseId
  $timeout = 0
  $completed = $false
  
  do {
    Start-Sleep -Seconds 20
    $timeout += 20
    try {
      Add-Content $LogFile "[$(Get-Date)] DEBUG: Checking run $runId"
      $currentRun = gh run view $runId --repo $Repo --json status,conclusion | ConvertFrom-Json
      if ($currentRun.status -eq "completed") {
        $run = [pscustomobject]@{
          databaseId = $runId
          status     = $currentRun.status
          conclusion = $currentRun.conclusion
        }
        $completed = $true
        break
      }
    } catch {
      Add-Content $LogFile "[$(Get-Date)] ERROR checking run ${runId}: $_"
    }
  } while ($timeout -lt 600)

  if (-not $completed) {
    Add-Content $LogFile "[$(Get-Date)] TIMEOUT run ${runId} still queued_or_in_progress"
    $SuccessStreak = 0
  } elseif ($run.conclusion -eq "success") {
    $log = gh run view $runId --repo $Repo --log 2>$null
    if ($log -match "RECOVERY_TEST_OK") {
      $SuccessStreak++
      Add-Content $LogFile "[$(Get-Date)] SUCCESS run=${runId} streak=$SuccessStreak"
    } else {
      $SuccessStreak = 0
      Add-Content $LogFile "[$(Get-Date)] FALSE_SUCCESS run=${runId} marker missing"
    }
  } else {
    $SuccessStreak = 0
    Add-Content $LogFile "[$(Get-Date)] FAILURE run=${runId} conclusion=$($run.conclusion)"
  }

  if ($SuccessStreak -ge 3) {
    Add-Content $LogFile "[$(Get-Date)] RECOVERY_CONFIRMED after 3 consecutive probes"
    break
  }

  Start-Sleep -Seconds 1800
}
