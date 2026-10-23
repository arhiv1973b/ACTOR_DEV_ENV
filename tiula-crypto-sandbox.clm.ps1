#requires -Version 5.1
# Constrained Language Mode Wrapper
# Auto-generated wrapper for sandboxed execution

using namespace System.Management.Automation.Language

[ValidateNotNull()]
param(
    [Parameter(ValueFromPipeline)]
    [PSObject]$InputObject,
    
    [string[]]$ArgumentList
)

# Verify CLM is active
if ([PSLanguageMode]::ConstrainedLanguage -ne $ExecutionContext.SessionState.LanguageMode) {
    throw "ERROR: Constrained Language Mode not active. Actual: $($ExecutionContext.SessionState.LanguageMode)"
}

Write-Host "[CLM] Executing in Constrained Language Mode" -ForegroundColor Green
Write-Host "[CLM] Language Mode: $($ExecutionContext.SessionState.LanguageMode)" -ForegroundColor Cyan

# Audit entry
Add-Content -Path 'H:\ACTOR_DEV_ENV\audits\clm-execution.log' 
    -Value "[$(Get-Date -Format 'u')] Script: H:\ACTOR_DEV_ENV\tiula-crypto-sandbox.ps1 | User: $env:USERNAME | Args: $($ArgumentList -join ' ')"

# Execute original script in CLM
try {
    & 'H:\ACTOR_DEV_ENV\tiula-crypto-sandbox.ps1' @ArgumentList
}
catch {
    Write-Error "CLM Script Error: $_"
    exit 1
}
