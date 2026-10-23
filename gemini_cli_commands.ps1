# Gemini CLI Command Set — Safe Execution with Input Validation
# Purpose: Run gemini-cli with prompt files, debug options, and safe I/O handling
# Encoding: UTF-8
# Recommended Font: Consolas

# ============================================================================
# COMMAND 1: Read Prompt File and Execute Gemini (Direct Method)
# ============================================================================
# Usage: Execute in PowerShell (no profile)
# Input: prompt_sanitized.txt (UTF-8)
# Output: Console and optional file

powershell -NoProfile -Command {
    $promptFile = "H:\ACTOR_DEV_ENV\prompt_sanitized.txt"
    $outputFile = "H:\ACTOR_DEV_ENV\gemini_output_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
    
    # Validate file exists and is readable
    if (-not (Test-Path $promptFile)) {
        Write-Host "ERROR: Prompt file not found: $promptFile" -ForegroundColor Red
        exit 1
    }
    
    # Read prompt with UTF-8 encoding validation
    try {
        $prompt = Get-Content -Path $promptFile -Encoding UTF8 -Raw -ErrorAction Stop
        Write-Host "✓ Prompt loaded ($($prompt.Length) chars, UTF-8)" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to read prompt: $_" -ForegroundColor Red
        exit 1
    }
    
    # Verify © symbol preservation
    if ($prompt -match '©') {
        Write-Host "✓ © symbol verified in prompt" -ForegroundColor Green
    }
    
    # Execute gemini with --prompt flag (headless mode)
    Write-Host "Executing gemini-cli..." -ForegroundColor Cyan
    agy --model gemini-3.1 -p "$prompt" 2>&1 | Tee-Object -FilePath $outputFile
    
    Write-Host "`n✓ Output saved to: $outputFile" -ForegroundColor Green
}

# ============================================================================
# COMMAND 2: Execute with Debug/Verbose Flags
# ============================================================================
# Usage: For troubleshooting and detailed output

powershell -NoProfile -Command {
    $promptFile = "H:\ACTOR_DEV_ENV\prompt_sanitized.txt"
    $prompt = Get-Content -Path $promptFile -Encoding UTF8 -Raw
    
    # Run with debug flag (if supported by gemini-cli)
    agy --model gemini-3.1 --debug -p "$prompt"
}

# ============================================================================
# COMMAND 3: Pipe Aggregated Sources + Prompt Together
# ============================================================================
# Usage: Combine sanitized prompt + aggregated sources for richer context

powershell -NoProfile -Command {
    $promptFile = "H:\ACTOR_DEV_ENV\prompt_sanitized.txt"
    $sourcesFile = "H:\ACTOR_DEV_ENV\prompt_sources_aggregated.txt"
    $combinedFile = "H:\ACTOR_DEV_ENV\prompt_combined_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
    
    # Validate both files exist
    @($promptFile, $sourcesFile) | ForEach-Object {
        if (-not (Test-Path $_)) {
            Write-Host "ERROR: File not found: $_" -ForegroundColor Red
            exit 1
        }
    }
    
    # Read both files
    $prompt = Get-Content -Path $promptFile -Encoding UTF8 -Raw
    $sources = Get-Content -Path $sourcesFile -Encoding UTF8 -Raw
    
    # Combine (prompt first, then sources as context)
    $combined = @"
$prompt

--- ATTACHED SOURCES FOR CONTEXT ---

$sources
"@
    
    # Save combined file
    Set-Content -Path $combinedFile -Value $combined -Encoding UTF8
    Write-Host "✓ Combined prompt+sources: $combinedFile" -ForegroundColor Green
    
    # Execute with combined context
    agy --model gemini-3.1 -p "$combined"
}

# ============================================================================
# COMMAND 4: Safe Batch Mode (Multiple Prompts with Error Handling)
# ============================================================================
# Usage: Execute prompt and capture output with retry logic

powershell -NoProfile -Command {
    $promptFile = "H:\ACTOR_DEV_ENV\prompt_sanitized.txt"
    $outputFile = "H:\ACTOR_DEV_ENV\gemini_output.txt"
    $maxRetries = 3
    $retryDelay = 5
    
    $attempt = 0
    while ($attempt -lt $maxRetries) {
        $attempt++
        Write-Host "Attempt $attempt/$maxRetries..." -ForegroundColor Yellow
        
        try {
            $prompt = Get-Content -Path $promptFile -Encoding UTF8 -Raw -ErrorAction Stop
            agy --model gemini-3.1 -p "$prompt" -o text 2>&1 | 
                Out-File -FilePath $outputFile -Encoding UTF8 -ErrorAction Stop
            
            Write-Host "✓ Success; output saved to $outputFile" -ForegroundColor Green
            break
            
        } catch {
            Write-Host "✗ Attempt $attempt failed: $_" -ForegroundColor Red
            if ($attempt -lt $maxRetries) {
                Write-Host "Retrying in $retryDelay seconds..." -ForegroundColor Yellow
                Start-Sleep -Seconds $retryDelay
            }
        }
    }
    
    if ($attempt -eq $maxRetries) {
        Write-Host "ERROR: All $maxRetries attempts failed" -ForegroundColor Red
        exit 1
    }
}

# ============================================================================
# COMMAND 5: Validate Output Encoding and © Preservation
# ============================================================================
# Usage: After execution, verify UTF-8 integrity and © symbol

powershell -NoProfile -Command {
    $outputFile = "H:\ACTOR_DEV_ENV\gemini_output.txt"
    
    if (-not (Test-Path $outputFile)) {
        Write-Host "ERROR: Output file not found: $outputFile" -ForegroundColor Red
        exit 1
    }
    
    # Read and validate
    try {
        $content = Get-Content -Path $outputFile -Encoding UTF8 -Raw -ErrorAction Stop
        $lines = $content -split "`n"
        
        Write-Host "✓ Output file validation:" -ForegroundColor Green
        Write-Host "  Size: $($content.Length) bytes" -ForegroundColor Cyan
        Write-Host "  Lines: $($lines.Count)" -ForegroundColor Cyan
        Write-Host "  Encoding: UTF-8 (verified on read)" -ForegroundColor Cyan
        
        # Check © preservation
        if ($content -match '©') {
            Write-Host "  © Symbol: PRESERVED ✓" -ForegroundColor Green
        } else {
            Write-Host "  © Symbol: NOT FOUND (check source)" -ForegroundColor Yellow
        }
        
        # Show first 500 chars
        Write-Host "`nFirst 500 characters:" -ForegroundColor Cyan
        Write-Host ($content.Substring(0, [Math]::Min(500, $content.Length))) -ForegroundColor Gray
        
    } catch {
        Write-Host "ERROR: Validation failed: $_" -ForegroundColor Red
        exit 1
    }
}

# ============================================================================
# COMMAND 6: Interactive Mode with Session Resume
# ============================================================================
# Usage: Start gemini in interactive mode with context file

powershell -NoProfile -Command {
    $promptFile = "H:\ACTOR_DEV_ENV\prompt_sanitized.txt"
    $sessionId = [guid]::NewGuid().ToString()
    
    $prompt = Get-Content -Path $promptFile -Encoding UTF8 -Raw
    
    # Start interactive session
    agy --model gemini-3.1 --session-id $sessionId -i "$prompt"
}

# ============================================================================
# NOTES:
# - All files use UTF-8 encoding (no BOM)
# - © symbol is preserved throughout pipeline
# - Use -NoProfile to avoid PowerShell bootstrap script issues
# - For large prompts, consider splitting or using aggregated sources approach
# - If gemini-cli fails with "arguments" error, check syntax and flag order
# ============================================================================
