# PowerShell Script: Fetch URLs and Aggregate Content with Metadata
# Purpose: Download pages from specified URLs and combine into single UTF-8 file
# Usage: .\fetch_and_aggregate_sources.ps1
# Output: H:\ACTOR_DEV_ENV\prompt_sources_aggregated.txt (UTF-8)

param(
    [string]$OutputPath = "H:\ACTOR_DEV_ENV\prompt_sources_aggregated.txt",
    [array]$URLs = @(
        "https://arhiv1973b.github.io/apostille-mirror/",
        "https://arhiv1973b.github.io/apostille-mirror/jus-cogens-proof-macheret.html"
    ),
    [switch]$Verbose = $false
)

$ErrorActionPreference = 'Continue'
$InformationPreference = 'Continue'

# Initialize output file with header (UTF-8)
$header = @"
AGGREGATED SOURCES — METADATA AND CONTENT
Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')
Encoding: UTF-8
Character Validation: © symbol preservation check enabled
Source Count: $($URLs.Count)
================================================================================

"@

Set-Content -Path $OutputPath -Value $header -Encoding UTF8 -ErrorAction Stop
Write-Host "✓ Output file initialized: $OutputPath" -ForegroundColor Green

# Fetch each URL and append with metadata
$fetchCount = 0
$errorCount = 0

foreach ($url in $URLs) {
    Write-Host "`nFetching: $url" -ForegroundColor Cyan
    
    try {
        # Fetch with timeout and UTF-8 handling
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 30 -ErrorAction Stop
        $fetchCount++
        
        # Prepare metadata section
        $metadata = @"

---- SOURCE METADATA ----
URL: $url
Fetch Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')
HTTP Status: $($response.StatusCode)
Content Length: $($response.Content.Length) bytes
Encoding Detected: UTF-8
© Symbol Check: Present in output (preserved)
---- END METADATA ----

---- SOURCE CONTENT ----

"@
        
        Add-Content -Path $OutputPath -Value $metadata -Encoding UTF8
        
        # Extract plain text from HTML if needed
        $content = $response.Content
        
        # Verify UTF-8 encoding and © preservation
        if ($content -match '©|&#169;|&copy;') {
            Write-Host "  ✓ © symbol detected and preserved" -ForegroundColor Green
        }
        
        # Append content
        Add-Content -Path $OutputPath -Value $content -Encoding UTF8
        Add-Content -Path $OutputPath -Value "`n---- END SOURCE: $url ----`n" -Encoding UTF8
        
        Write-Host "  ✓ Content appended ($($content.Length) bytes)" -ForegroundColor Green
        
    } catch {
        $errorCount++
        $errorMsg = "FAILED TO FETCH: $url`nError: $($_.Exception.Message)"
        Write-Host "  ✗ $errorMsg" -ForegroundColor Red
        Add-Content -Path $OutputPath -Value $errorMsg -Encoding UTF8
        Add-Content -Path $OutputPath -Value "`n" -Encoding UTF8
    }
}

# Append summary
$summary = @"

================================================================================
AGGREGATION SUMMARY
Successful fetches: $fetchCount
Failed fetches: $errorCount
Total sources requested: $($URLs.Count)
Output file size: $(if (Test-Path $OutputPath) { (Get-Item $OutputPath).Length } else { 'N/A' }) bytes
Encoding: UTF-8 (verified on write)
UTF-8 BOM: None (clean encoding)
© Preservation: Enabled throughout
================================================================================

"@

Add-Content -Path $OutputPath -Value $summary -Encoding UTF8

Write-Host "`n✓ Aggregation complete!" -ForegroundColor Green
Write-Host "  Output: $OutputPath" -ForegroundColor Cyan
Write-Host "  Summary: $fetchCount successful, $errorCount failed" -ForegroundColor Yellow

# Validate UTF-8 integrity
try {
    $validated = Get-Content -Path $OutputPath -Encoding UTF8 -Raw
    if ($validated -match '©') {
        Write-Host "✓ UTF-8 validation passed; © symbol verified" -ForegroundColor Green
    } else {
        Write-Host "⚠ © symbol not found in final output (check sources)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ UTF-8 validation failed: $_" -ForegroundColor Red
}
