$EvidenceFile = ".\audits\dual_run_comparative_audit.json"
$VaultPath = ".\evidence_vault"
$ReportsPath = "$VaultPath\reports"
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

if (Test-Path $EvidenceFile) {
    if (!(Test-Path $VaultPath)) { New-Item -Path $VaultPath -ItemType Directory }
    if (!(Test-Path $ReportsPath)) { New-Item -Path $ReportsPath -ItemType Directory }
    
    $Hash = (Get-FileHash $EvidenceFile -Algorithm SHA256).Hash
    $Manifest = [PSCustomObject]@{
        Timestamp = $Timestamp
        OriginalFile = "dual_run_comparative_audit.json"
        SHA256 = $Hash
        Author = "A©tor"
    }
    
    $Manifest | ConvertTo-Json | Out-File "$VaultPath\manifest_$Timestamp.json" -Encoding utf8
    Copy-Item $EvidenceFile "$ReportsPath\audit_$Timestamp.json"
    
    git add .
    git commit -m "TI-ULA Evidence Vault: Audit $Timestamp [SHA256: $Hash]"
    git push origin main
    
    Write-Host "✅ Доказательства зафиксированы в репозитории: $VaultPath" -ForegroundColor Green
} else {
    Write-Host "❌ Файл отчета не найден: $EvidenceFile" -ForegroundColor Red
}
