# ==============================================================================
# DISTRIBUTED SWARM RUNNER (PowerShell Background Jobs)
# ==============================================================================

Write-Host "=== Launching Distributed Swarm as Background Jobs ===" -ForegroundColor Cyan

$job1 = Start-Job -ScriptBlock { Set-Location $using:PWD; python build_entity_graph.py }
$job2 = Start-Job -ScriptBlock { Set-Location $using:PWD; python generate_legal_draft_bundle.py }

Write-Host "Waiting for Orchestrator and Legal Draftsman jobs to complete..." -ForegroundColor Yellow
$job1 | Wait-Job
$job2 | Wait-Job

Receive-Job $job1
Receive-Job $job2

Write-Host "=== Running Evidence Crosschecker & Archiver ===" -ForegroundColor Cyan
python agent_final_consensus.py

Write-Host "=== Distributed Swarm Execution Complete ===" -ForegroundColor Green
