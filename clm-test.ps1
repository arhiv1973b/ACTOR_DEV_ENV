$ExecutionContext.SessionState.LanguageMode = 'ConstrainedLanguage'
try {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    Write-Host "SUCCESS: SHA256 created in CLM"
} catch {
    Write-Host "FAILED: $($_.Exception.Message)"
}
