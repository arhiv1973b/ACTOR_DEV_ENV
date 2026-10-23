# Add to PowerShell Profile (~\Documents\PowerShell\profile.ps1)

# Gemini CLI function (Python wrapper)
function gemini {
    param(
        [Parameter(ValueFromRemainingArguments=$true)]
        [string[]]$Arguments
    )
    python (Join-Path $PSScriptRoot "gemini_cli.py") @Arguments
}

Set-Alias -Name gemini -Value gemini -Force

Write-Host "✅ Gemini CLI loaded (Python wrapper)"
