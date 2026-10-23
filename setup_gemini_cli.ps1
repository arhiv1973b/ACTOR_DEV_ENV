# Gemini CLI Setup Script
# Adds gemini command to PowerShell

$GLOBAL_NPM = "H:\npm-global"
$GEMINI_BIN = "$GLOBAL_NPM\bin\gemini"

# Check if gemini exists
if (Test-Path $GEMINI_BIN) {
    Write-Host "✅ Gemini CLI found at: $GEMINI_BIN"
} else {
    Write-Host "❌ Gemini CLI not found. Installing..."
    npm install -g @google/genai
}

# Add to PATH temporarily for this session
$env:PATH = "$GLOBAL_NPM\bin;$env:PATH"

# Create permanent alias in PowerShell profile
$PROFILE_PATH = $PROFILE
if (-not (Test-Path $PROFILE_PATH)) {
    Write-Host "Creating PowerShell profile at: $PROFILE_PATH"
    New-Item -Path $PROFILE_PATH -ItemType File -Force | Out-Null
}

# Add alias to profile if not already there
$profileContent = Get-Content $PROFILE_PATH -Raw -ErrorAction SilentlyContinue
if (-not $profileContent -or $profileContent -notmatch "Set-Alias.*gemini") {
    Write-Host "Adding gemini alias to PowerShell profile..."
    Add-Content -Path $PROFILE_PATH -Value "`nSet-Alias -Name gemini -Value '$GEMINI_BIN' -Force"
} else {
    Write-Host "Gemini alias already in profile"
}

# Test
Write-Host "`nTesting gemini CLI..."
& $GEMINI_BIN --version

Write-Host "`n✅ Gemini CLI is ready!"
Write-Host "Add this to your profile for permanent access:"
Write-Host "  Set-Alias -Name gemini -Value '$GEMINI_BIN' -Force"
Write-Host "  `$env:PATH = '$GLOBAL_NPM\bin;`$env:PATH'"
