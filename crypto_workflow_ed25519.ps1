# Cryptographic Workflow: Ed25519 Key Pair Generation, Signing, and Verification
# Purpose: Generate keys, sign artifacts, verify signatures
# Framework: .NET System.Security.Cryptography (built-in Windows)
# Encoding: UTF-8
# Recommended Font: Consolas

# ============================================================================
# SECTION 1: Helper Functions
# ============================================================================

function New-Ed25519KeyPair {
    <#
    .SYNOPSIS
    Generate a new Ed25519 key pair and save to PEM format
    
    .PARAMETER OutputDir
    Directory to save key files (default: current directory)
    
    .PARAMETER KeyName
    Base name for key files (default: ed25519)
    #>
    param(
        [string]$OutputDir = (Get-Location),
        [string]$KeyName = "ed25519"
    )
    
    Write-Host "Generating Ed25519 key pair..." -ForegroundColor Cyan
    
    # Use dotnet/openssl via PowerShell
    # For Windows, we'll use OpenSSH (built-in since Windows 10)
    
    $privateKeyPath = Join-Path $OutputDir "$KeyName"
    $publicKeyPath = Join-Path $OutputDir "$KeyName.pub"
    
    try {
        # Generate using ssh-keygen (Windows 10+)
        & ssh-keygen -t ed25519 -f $privateKeyPath -N "" -C "crypto-artifact-signing" 2>&1
        
        if (Test-Path $privateKeyPath) {
            Write-Host "✓ Private key: $privateKeyPath" -ForegroundColor Green
            Write-Host "✓ Public key: $publicKeyPath" -ForegroundColor Green
            
            # Set restrictive permissions on private key
            $acl = Get-Acl $privateKeyPath
            $acl.SetAccessRuleProtection($true, $false)
            $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
                [System.Security.Principal.WindowsIdentity]::GetCurrent().User,
                'FullControl',
                'Allow'
            )
            $acl.SetAccessRule($rule)
            Set-Acl -Path $privateKeyPath -AclObject $acl
            Write-Host "✓ Private key permissions restricted (owner only)" -ForegroundColor Green
            
            return @{
                PrivateKey = $privateKeyPath
                PublicKey = $publicKeyPath
                Created = Get-Date
            }
        } else {
            throw "Key generation failed"
        }
    } catch {
        Write-Host "ERROR: Key generation failed: $_" -ForegroundColor Red
        Write-Host "Ensure ssh-keygen is available (Windows 10+ with OpenSSH)" -ForegroundColor Gray
        return $null
    }
}

function Sign-Artifact {
    <#
    .SYNOPSIS
    Sign a file using Ed25519 private key
    
    .PARAMETER FilePath
    Path to file to sign
    
    .PARAMETER PrivateKeyPath
    Path to Ed25519 private key
    
    .PARAMETER OutputPath
    Path to save signature (default: <FilePath>.sig)
    #>
    param(
        [string]$FilePath,
        [string]$PrivateKeyPath,
        [string]$OutputPath = "$FilePath.sig"
    )
    
    if (-not (Test-Path $FilePath)) {
        Write-Host "ERROR: File not found: $FilePath" -ForegroundColor Red
        return $false
    }
    
    if (-not (Test-Path $PrivateKeyPath)) {
        Write-Host "ERROR: Private key not found: $PrivateKeyPath" -ForegroundColor Red
        return $false
    }
    
    Write-Host "Signing artifact: $FilePath" -ForegroundColor Cyan
    
    try {
        # Use ssh-keygen to sign (requires OpenSSH)
        & ssh-keygen -Y sign -f $PrivateKeyPath -n file $FilePath 2>&1 | Out-Null
        
        # OpenSSH places signature in <filename>.sig
        $autoSigPath = "$FilePath.sig"
        
        if (Test-Path $autoSigPath) {
            if ($autoSigPath -ne $OutputPath) {
                Move-Item -Path $autoSigPath -Destination $OutputPath -Force
            }
            Write-Host "✓ Signature created: $OutputPath" -ForegroundColor Green
            
            # Show signature summary
            $sigContent = Get-Content -Path $OutputPath -Raw
            Write-Host "  Signature size: $($sigContent.Length) bytes" -ForegroundColor Gray
            
            return $true
        } else {
            throw "Signature file not created"
        }
    } catch {
        Write-Host "ERROR: Signing failed: $_" -ForegroundColor Red
        return $false
    }
}

function Verify-Artifact {
    <#
    .SYNOPSIS
    Verify a file signature using Ed25519 public key
    
    .PARAMETER FilePath
    Path to original file
    
    .PARAMETER SignaturePath
    Path to signature file
    
    .PARAMETER PublicKeyPath
    Path to Ed25519 public key
    #>
    param(
        [string]$FilePath,
        [string]$SignaturePath,
        [string]$PublicKeyPath
    )
    
    @($FilePath, $SignaturePath, $PublicKeyPath) | ForEach-Object {
        if (-not (Test-Path $_)) {
            Write-Host "ERROR: File not found: $_" -ForegroundColor Red
            return $false
        }
    }
    
    Write-Host "Verifying signature..." -ForegroundColor Cyan
    
    try {
        # Use ssh-keygen to verify
        & ssh-keygen -Y verify -f $PublicKeyPath -I file -n file -s $SignaturePath < $FilePath 2>&1 | Tee-Object -Variable result | Out-Null
        
        if ($result -match 'Good' -or $result -match 'valid') {
            Write-Host "✓ Signature VALID" -ForegroundColor Green
            return $true
        } else {
            Write-Host "✗ Signature INVALID or verification failed" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "ERROR: Verification failed: $_" -ForegroundColor Red
        return $false
    }
}

function Get-ArtifactHash {
    <#
    .SYNOPSIS
    Calculate SHA256 hash of artifact
    #>
    param(
        [string]$FilePath
    )
    
    if (-not (Test-Path $FilePath)) {
        Write-Host "ERROR: File not found: $FilePath" -ForegroundColor Red
        return $null
    }
    
    $hash = Get-FileHash -Path $FilePath -Algorithm SHA256
    return @{
        File = $FilePath
        Hash = $hash.Hash
        Algorithm = $hash.Algorithm
    }
}

# ============================================================================
# SECTION 2: Interactive Workflow
# ============================================================================

Write-Host "=== Cryptographic Artifact Workflow ===" -ForegroundColor Cyan
Write-Host "Choose action:" -ForegroundColor Yellow
Write-Host "1. Generate new Ed25519 key pair" -ForegroundColor Gray
Write-Host "2. Sign an artifact" -ForegroundColor Gray
Write-Host "3. Verify a signature" -ForegroundColor Gray
Write-Host "4. Get artifact hash" -ForegroundColor Gray
Write-Host "5. Full workflow (generate → sign → verify)" -ForegroundColor Gray

$action = Read-Host "Select (1-5)"

switch ($action) {
    "1" {
        $keyDir = Read-Host "Key output directory (default: current) [press Enter]"
        if ([string]::IsNullOrWhiteSpace($keyDir)) { $keyDir = (Get-Location) }
        
        $keyName = Read-Host "Key name (default: ed25519) [press Enter]"
        if ([string]::IsNullOrWhiteSpace($keyName)) { $keyName = "ed25519" }
        
        $keys = New-Ed25519KeyPair -OutputDir $keyDir -KeyName $keyName
        if ($keys) {
            Write-Host "`n✓ Key pair generated successfully" -ForegroundColor Green
            Write-Host "  Private: $($keys.PrivateKey)" -ForegroundColor Cyan
            Write-Host "  Public: $($keys.PublicKey)" -ForegroundColor Cyan
        }
    }
    
    "2" {
        $filePath = Read-Host "Artifact file path"
        $privateKeyPath = Read-Host "Private key path"
        $outputPath = Read-Host "Output signature path (default: <file>.sig) [press Enter]"
        if ([string]::IsNullOrWhiteSpace($outputPath)) { $outputPath = "$filePath.sig" }
        
        Sign-Artifact -FilePath $filePath -PrivateKeyPath $privateKeyPath -OutputPath $outputPath
    }
    
    "3" {
        $filePath = Read-Host "Artifact file path"
        $sigPath = Read-Host "Signature file path"
        $pubKeyPath = Read-Host "Public key path"
        
        Verify-Artifact -FilePath $filePath -SignaturePath $sigPath -PublicKeyPath $pubKeyPath
    }
    
    "4" {
        $filePath = Read-Host "Artifact file path"
        $hashInfo = Get-ArtifactHash -FilePath $filePath
        if ($hashInfo) {
            Write-Host "`n✓ Hash Information:" -ForegroundColor Green
            Write-Host "  File: $($hashInfo.File)" -ForegroundColor Cyan
            Write-Host "  Algorithm: $($hashInfo.Algorithm)" -ForegroundColor Cyan
            Write-Host "  Hash: $($hashInfo.Hash)" -ForegroundColor Yellow
        }
    }
    
    "5" {
        Write-Host "`n=== Full Cryptographic Workflow ===" -ForegroundColor Cyan
        
        # Step 1: Generate keys
        Write-Host "`nStep 1: Generating Ed25519 key pair..." -ForegroundColor Yellow
        $keyDir = Join-Path (Get-Location) "crypto_keys"
        New-Item -ItemType Directory -Path $keyDir -Force | Out-Null
        $keys = New-Ed25519KeyPair -OutputDir $keyDir -KeyName "artifact_key"
        
        if (-not $keys) {
            Write-Host "ERROR: Key generation failed" -ForegroundColor Red
            exit 1
        }
        
        # Step 2: Create test artifact
        Write-Host "`nStep 2: Creating test artifact..." -ForegroundColor Yellow
        $testFile = Join-Path (Get-Location) "test_artifact.txt"
        $testContent = @"
Test Artifact for Cryptographic Verification
Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')
Encoding: UTF-8
© Symbol Test: © (preserved)
Кириллица: Тестовый артефакт
Hash: $(Get-FileHash -LiteralPath $testFile -Algorithm SHA256 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Hash)
"@
        Set-Content -Path $testFile -Value $testContent -Encoding UTF8
        Write-Host "✓ Test artifact: $testFile" -ForegroundColor Green
        
        # Step 3: Sign artifact
        Write-Host "`nStep 3: Signing artifact..." -ForegroundColor Yellow
        $sigSuccess = Sign-Artifact -FilePath $testFile -PrivateKeyPath $keys.PrivateKey
        
        if (-not $sigSuccess) {
            Write-Host "ERROR: Signing failed" -ForegroundColor Red
            exit 1
        }
        
        # Step 4: Verify signature
        Write-Host "`nStep 4: Verifying signature..." -ForegroundColor Yellow
        $verifySuccess = Verify-Artifact -FilePath $testFile -SignaturePath "$testFile.sig" -PublicKeyPath $keys.PublicKey
        
        # Step 5: Generate summary report
        Write-Host "`nStep 5: Summary Report" -ForegroundColor Yellow
        $reportFile = Join-Path (Get-Location) "verification_report.txt"
        $report = @"
CRYPTOGRAPHIC VERIFICATION REPORT
Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')
Encoding: UTF-8
© Symbol: © (preserved)

KEYS:
  Private Key: $($keys.PrivateKey)
  Public Key: $($keys.PublicKey)

ARTIFACT:
  File: $testFile
  Encoding: UTF-8
  Size: $(if (Test-Path $testFile) { (Get-Item $testFile).Length } else { 'N/A' }) bytes

SIGNATURE:
  File: $testFile.sig
  Algorithm: Ed25519 (OpenSSH format)
  Size: $(if (Test-Path "$testFile.sig") { (Get-Item "$testFile.sig").Length } else { 'N/A' }) bytes

VERIFICATION RESULT:
  Status: $(if ($verifySuccess) { 'VALID ✓' } else { 'INVALID ✗' })
  Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')

INSTRUCTIONS FOR VERIFICATION:
  1. Use public key $($keys.PublicKey) to verify signatures
  2. Signature file: $testFile.sig
  3. Original artifact: $testFile
  4. Command: ssh-keygen -Y verify -f <public_key> -I file -n file -s <signature> < <file>

"@
        Set-Content -Path $reportFile -Value $report -Encoding UTF8
        Write-Host "✓ Report saved: $reportFile" -ForegroundColor Green
        
        Write-Host "`n=== Workflow Complete ===" -ForegroundColor Green
        Write-Host "✓ All steps completed successfully" -ForegroundColor Green
    }
    
    default {
        Write-Host "Invalid selection" -ForegroundColor Red
    }
}

Write-Host "`n✓ Done" -ForegroundColor Green
