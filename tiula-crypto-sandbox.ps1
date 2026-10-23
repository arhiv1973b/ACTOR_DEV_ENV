# tiula-crypto-sandbox.ps1 - TI-ULA Cryptographic Sandbox Bridge
# Purpose: Secure audit trail with Ed25519 signing and local LLM analysis
# Requires: OpenSSH (ssh-keygen), Ollama, Docker

[CmdletBinding()]
param(
    [int]$PollingIntervalSeconds = 10,
    [switch]$Continuous = $true,
    [string]$Model = 'qwen2.5:3b'
)

$PSScriptRoot = "H:\ACTOR_DEV_ENV"
Import-Module (Join-Path $PSScriptRoot "tiula-crypto-sandbox.psm1") -Force

function Start-CryptoSandbridge {
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║  TI-ULA Cryptographic Sandbox Bridge                     ║" -ForegroundColor Magenta
    Write-Host "║  Ed25519 signing | SHA256 validation | Ollama analysis   ║" -ForegroundColor Magenta
    Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Magenta

    # Ensure keys are initialized
    $PubPath = Initialize-CryptoKeys
    
    $Iteration = 0
    do {
        $Iteration++
        $Timestamp = Get-Date -Format 'HH:mm:ss'
        Write-Host "`n[ITERATION] $Iteration $Timestamp" -ForegroundColor Gray

        try {
            # 1. Read events from container
            Write-Host "[SANDBOX] Reading events from container..." -ForegroundColor Cyan
            $EventsJson = docker exec actor-app-dev cat /app/.audit/events.json 2>$null
            
            if ($null -eq $EventsJson -or $EventsJson -match "Error") {
                Write-Host "[WARN] No events found or container not ready." -ForegroundColor Yellow
            } else {
                $Events = $EventsJson | ConvertFrom-Json
                Write-Host "[INFO] Processed $($Events.Count) events." -ForegroundColor Green
                
                # 2. Perform threat analysis with Ollama
                Write-Host "[OLLAMA] Querying local LLM ($Model) for threat analysis..." -ForegroundColor Cyan
                $Prompt = "Analyze these container audit events for security threats and anomalies. Report risk score (0-10) and recommendations: $EventsJson"
                
                $OllamaRequest = @{
                    model = $Model
                    prompt = $Prompt
                    stream = $false
                } | ConvertTo-Json
                
                $Response = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method POST -Body $OllamaRequest -ContentType "application/json"
                
                if ($Response.response) {
                    $Analysis = $Response.response
                    Write-Host "[SUCCESS] LLM response received ($($Analysis.Length) chars)" -ForegroundColor Green
                    
                    # 3. Sign the analysis
                    $AnalysisPath = Join-Path $PSScriptRoot "run\analysis_$Iteration.txt"
                    if (-not (Test-Path (Join-Path $PSScriptRoot "run"))) { New-Item -ItemType Directory -Path (Join-Path $PSScriptRoot "run") -Force | Out-Null }
                    
                    $Analysis | Set-Content $AnalysisPath
                    $Signed = Sign-Artifact -ArtifactPath $AnalysisPath -PrivateKeyPath (Join-Path $PSScriptRoot "keys\actor_ed25519")
                    
                    # 4. Create Attestation
                    $AttestationPath = Join-Path $PSScriptRoot "attestations\attestation_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
                    $Attestation = @{
                        iteration = $Iteration
                        timestamp = Get-Date -Format 'u'
                        events_count = $Events.Count
                        risk_score = 1.5 # Example
                        analysis_signature = (Get-Content "$AnalysisPath.sig" -Raw)
                        model = $Model
                    }
                    $Attestation | ConvertTo-Json | Set-Content $AttestationPath
                    Write-Host "[ATTESTATION] Created signed attestation: $($AttestationPath)" -ForegroundColor Green
                }
            }
        } catch {
            Write-Error "Bridge Error: $_"
        }

        if ($Continuous) {
            Start-Sleep -Seconds $PollingIntervalSeconds
        }
    } while ($Continuous)
}

# Execute
Start-CryptoSandbridge
