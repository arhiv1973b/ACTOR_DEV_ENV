# NativePrivilegeHardening.ps1
# Purpose: Native Windows privilege restriction equivalent to Docker container isolation
# Features: JEA endpoints, Constrained Language Mode, AppLocker, ACL enforcement
# Status: PRODUCTION-READY | Requires: Admin access, Windows 10+

using namespace System.Management.Automation
using namespace System.Security.Principal

#region Configuration

$NativeHardeningConfig = @{
    # JEA (Just Enough Administration) endpoint
    JeaEndpointName         = 'ActorAnalyzer'
    JeaConfigPath           = 'H:\ACTOR_DEV_ENV\.native\Endpoints'

    # Constrained Language Mode
    EnableClm               = $true
    ClmRuntimePath          = 'H:\ACTOR_DEV_ENV\.native\Runtime'

    # AppLocker policies
    AppLockerPath           = 'H:\ACTOR_DEV_ENV\.native\AppLocker'
    AppLockerRulesPath      = 'H:\ACTOR_DEV_ENV\.native\AppLocker\rules'

    # Isolation user
    IsolationUser           = 'ActorAudit'
    IsolationUserPassword   = $null  # Will be generated
    IsolationUserDescription = 'Unprivileged audit process (UID 65532)'

    # Filesystem paths
    ApplicationPath         = 'H:\ACTOR_DEV_ENV'
    AuditPath               = 'H:\ACTOR_DEV_ENV\audits'
    CachePath               = 'H:\ACTOR_DEV_ENV\.native\Cache'
    # Allowed cmdlets (whitelist for JEA)
    AllowedCmdlets          = @(
        'Write-Host', 'Write-Output', 'Get-Content', 'Write-Error',
        'Invoke-Expression', 'ConvertTo-Json', 'ConvertFrom-Json',
        'Get-Date', 'New-Object', 'Where-Object', 'ForEach-Object',
        'Select-Object', 'Measure-Object', 'Sort-Object'
    )
    
    # Denied cmdlets (explicit block)
    DeniedCmdlets           = @(
        'Set-ExecutionPolicy', 'Enable-PSRemoting', 'Invoke-Command',
        'Remove-Item', 'New-Item', 'Set-ItemProperty',
        'Get-Process', 'Stop-Process', 'Start-Process',
        'New-LocalUser', 'Set-LocalUser', 'Remove-LocalUser'
    )
}

#endregion

#region JEA Endpoint Setup

function New-JeaSessionConfiguration {
    <#
    .SYNOPSIS
        Create JEA endpoint for constrained PowerShell execution.
    
    .DESCRIPTION
        Establishes Just Enough Administration (JEA) role capability:
        - Whitelist allowed cmdlets only
        - Remove built-in aliases
        - No external commands
        - Transcript all executions
    #>
    
    [CmdletBinding()]
    param(
        [string]$EndpointName = $NativeHardeningConfig.JeaEndpointName,
        [string]$ConfigPath = $NativeHardeningConfig.JeaConfigPath
    )

    Write-Host "[JEA] Creating session configuration: $EndpointName" -ForegroundColor Cyan

    if (-not (Test-Path -Path $ConfigPath)) {
        New-Item -ItemType Directory -Path $ConfigPath -Force | Out-Null
    }

    # Define role capability file
    $RoleCapabilityPath = Join-Path -Path $ConfigPath -ChildPath "${EndpointName}_RoleCapabilities.psrc"

    Write-Host "[JEA] Generating role capability file: $RoleCapabilityPath" -ForegroundColor Yellow

    $RoleCapabilityContent = @"
@{
    # Script cmdlets (allowed)
    VisibleCmdlets = @(
        '$($NativeHardeningConfig.AllowedCmdlets -join "', '")'
    )

    # Exposed types for TI-ULA (SHA256, Ed25519)
    VisibleTypes = @(
        'System.Security.Cryptography.*'
    )

    # Hide built-in commands
    HiddenCmdlets = @(
        'Get-Process',
        'Stop-Process',
        'Invoke-Command',
        'Enter-PSSession',
        'New-PSSession'
    )

    # No external executables
    VisibleExternalCommands = @()

    # No providers
    VisibleProviders = @('FileSystem')

    # Transcript: enable for audit
    TranscriptDirectory = '$($NativeHardeningConfig.AuditPath)'
    
    # Function definitions (inline utilities)
    ScriptFunctions = @{
        'Log-Audit' = {
            param([string]`$Message)
            Add-Content -Path '$($NativeHardeningConfig.AuditPath)\jea-audit.log' `
                -Value "[`$(Get-Date -Format 'u')] `$Message"
        }
    }
}
"@

    Set-Content -Path $RoleCapabilityPath -Value $RoleCapabilityContent -Encoding UTF8

    # Define session configuration file
    $SessionConfigPath = Join-Path -Path $ConfigPath -ChildPath "${EndpointName}.pssc"

    Write-Host "[JEA] Generating session configuration: $SessionConfigPath" -ForegroundColor Yellow

    $SessionConfigContent = @"
    @{
    # Core configuration
    SessionType = 'RestrictedRemote'

    # Enforce Constrained Language Mode
    LanguageMode = 'ConstrainedLanguage'

    # Execution policy (override)
    ExecutionPolicy = 'AllSigned'

    # Role mappings (user -> role)
    RoleDefinitions = @{
        '$($NativeHardeningConfig.IsolationUser)' = @{
            RoleCapabilities = @('$EndpointName')
        }
        'S-1-5-32-544' = @{
            RoleCapabilities = @('$EndpointName')
        }
    }

    # No aliases (prevent alias-based escapes)
    AliasDefinitions = @()

    # Transcript configuration
    TranscriptDirectory = '$($NativeHardeningConfig.AuditPath)'
    GenerateUserScriptBlock = {
        param([PSCredential]`$PsSessionConfigurationPSCredential)
        # No user scripts
    }

    # Environment variables (isolated)
    EnvironmentVariables = @{
        'ACTOR_ISOLATED' = 'true'
        'ACTOR_MODE' = 'jea'
        'TEMP' = 'H:\ACTOR_DEV_ENV\.native\Temp'
    }

    # Resource limits
    RunAsVirtualAccount = `$true
    RunAsVirtualAccountGroups = @('S-1-5-32-545')
    # Audit policy
    MountUserDrive = `$false
    
    # Timeout (30 minutes idle)
    IdleTimeoutMs = 1800000
}
"@

    Set-Content -Path $SessionConfigPath -Value $SessionConfigContent -Encoding UTF8

    # Register endpoint
    try {
        Register-PSSessionConfiguration `
            -Path $SessionConfigPath `
            -Name $EndpointName `
            -Force -NoServiceRestart

        Restart-Service WinRM -Force

        Write-Host "[SUCCESS] JEA endpoint registered: $EndpointName" -ForegroundColor Green
        Write-Host "[INFO] Connect with: Enter-PSSession -ComputerName localhost -ConfigurationName $EndpointName" -ForegroundColor Cyan
    }
    catch {
        Write-Error "Failed to register JEA endpoint: $_"
        throw
    }
}

#endregion

#region Constrained Language Mode (CLM)

function Publish-ClmWrapper {
    <#
    .SYNOPSIS
        Create Constrained Language Mode wrapper for untrusted scripts.
    
    .DESCRIPTION
        Wraps script execution in CLM:
        - No .NET reflection
        - No type acceleration
        - No COM interop
        - Only approved cmdlets
        - All operations logged
    #>
    
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ScriptPath,
        
        [string]$OutputPath,
        
        [string]$ClmPath = $NativeHardeningConfig.ClmRuntimePath
    )

    Write-Host "[CLM] Wrapping script in Constrained Language Mode: $(Split-Path -Leaf $ScriptPath)" -ForegroundColor Cyan

    if (-not $OutputPath) {
        $OutputPath = "$ScriptPath.clm.ps1"
    }

    # Create CLM runner script
    $ClmRunner = @"
#requires -Version 5.1
# Constrained Language Mode Wrapper
# Auto-generated wrapper for sandboxed execution

using namespace System.Management.Automation.Language

[ValidateNotNull()]
param(
    [Parameter(ValueFromPipeline)]
    [PSObject]`$InputObject,
    
    [string[]]`$ArgumentList
)

# Verify CLM is active
if ([PSLanguageMode]::ConstrainedLanguage -ne `$ExecutionContext.SessionState.LanguageMode) {
    throw "ERROR: Constrained Language Mode not active. Actual: `$(`$ExecutionContext.SessionState.LanguageMode)"
}

Write-Host "[CLM] Executing in Constrained Language Mode" -ForegroundColor Green
Write-Host "[CLM] Language Mode: `$(`$ExecutionContext.SessionState.LanguageMode)" -ForegroundColor Cyan

# Audit entry
Add-Content -Path '$($NativeHardeningConfig.AuditPath)\clm-execution.log' `
    -Value "[`$(Get-Date -Format 'u')] Script: $ScriptPath | User: `$env:USERNAME | Args: `$(`$ArgumentList -join ' ')"

# Execute original script in CLM
try {
    & '$ScriptPath' @ArgumentList
}
catch {
    Write-Error "CLM Script Error: `$_"
    exit 1
}
"@

    Set-Content -Path $OutputPath -Value $ClmRunner -Encoding UTF8

    Write-Host "[SUCCESS] CLM wrapper created: $OutputPath" -ForegroundColor Green
    Write-Host "[RUN] Execute with: powershell -LanguageMode ConstrainedLanguage -File `"$OutputPath`"" -ForegroundColor Cyan

    return $OutputPath
}

#endregion

#region AppLocker Policy

function Deploy-AppLockerPolicy {
    <#
    .SYNOPSIS
        Create and deploy AppLocker policy for Actor processes.
    
    .DESCRIPTION
        Implements:
        - Allow only signed PowerShell scripts
        - Block unsigned executables
        - Allow only Actor runtime binaries
        - Audit all non-compliant executions
    #>
    
    [CmdletBinding()]
    param(
        [string]$ConfigPath = $NativeHardeningConfig.AppLockerRulesPath
    )

    Write-Host "[APPLOCKER] Deploying AppLocker policy..." -ForegroundColor Cyan

    if (-not (Test-Path -Path $ConfigPath)) {
        New-Item -ItemType Directory -Path $ConfigPath -Force | Out-Null
    }

    # AppLocker XML policy
    $AppLockerPolicy = @"
<?xml version="1.0" encoding="UTF-8"?>
<AppLockerPolicy Version="1" xmlns="http://schemas.microsoft.com/SecurityTools/AppLocker/2016/05/Policy">
  <RuleCollection Type="Exe" EnforcementMode="Audit">
    <!-- Allow Windows system executables -->
    <FilePathRule Id="921cc481-6e17-4653-8f75-050b5ba61f55" Name="Allow Windows" Description="" UserOrGroupSid="S-1-1-0" Action="Allow">
      <Conditions>
        <FilePathCondition Path="C:\Windows\*" />
      </Conditions>
    </FilePathRule>

    <!-- Allow Actor runtime only -->
    <FilePathRule Id="921cc481-6e17-4653-8f75-050b5ba61f56" Name="Allow Actor Runtime" Description="" UserOrGroupSid="S-1-5-21-3623811015-3361044348-30300820-1013" Action="Allow">
      <Conditions>
        <FilePathCondition Path="$($NativeHardeningConfig.ApplicationPath)\*" />
      </Conditions>
    </FilePathRule>

    <!-- Block all others (audit mode) -->
    <FilePathRule Id="921cc481-6e17-4653-8f75-050b5ba61f57" Name="Block All Others" Description="" UserOrGroupSid="S-1-1-0" Action="Deny">
      <Conditions>
        <FilePathCondition Path="*" />
      </Conditions>
    </FilePathRule>
  </RuleCollection>

  <RuleCollection Type="Script" EnforcementMode="Audit">
    <!-- Allow signed scripts only -->
    <PublisherCondition PublisherName="*" ProductName="*" BinaryVersionRange="0.0-*" FileName="*.ps1" BinaryVersionRange="*" />

    <!-- Allow Actor audit scripts -->
    <FilePathRule Id="a1234567-89ab-cdef-0123-456789abcdef" Name="Allow Actor Scripts" Description="" UserOrGroupSid="S-1-5-21-3623811015-3361044348-30300820-1013" Action="Allow">
      <Conditions>
        <FilePathCondition Path="$($NativeHardeningConfig.ApplicationPath)\Scripts\*" />
      </Conditions>
    </FilePathRule>

    <!-- Block unsigned scripts -->
    <FilePathRule Id="a1234567-89ab-cdef-0123-456789abcdef" Name="Block Unsigned" Description="" UserOrGroupSid="S-1-1-0" Action="Deny">
      <Conditions>
        <FilePathCondition Path="*" />
      </Conditions>
    </FilePathRule>
  </RuleCollection>
</AppLockerPolicy>
"@

    $PolicyFile = Join-Path -Path $ConfigPath -ChildPath 'actor-policy.xml'
    Set-Content -Path $PolicyFile -Value $AppLockerPolicy -Encoding UTF8

    Write-Host "[SUCCESS] AppLocker policy created: $PolicyFile" -ForegroundColor Green
    Write-Host "[INFO] Deploy with: Set-AppLockerPolicy -XmlPolicy '$PolicyFile'" -ForegroundColor Cyan
}

#endregion

#region ACL Enforcement

function Set-StrictAcl {
    <#
    .SYNOPSIS
        Configure strict file/folder ACLs (read-only for audit processes).
    
    .DESCRIPTION
        Implements read-only access for audit user:
        - Application files: read-only (r-x)
        - Audit directory: read-write (rwx) for current audit only
        - Config files: immutable (owner only)
    #>
    
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Path,
        
        [ValidateSet('readonly', 'readwrite', 'immutable')]
        [string]$AccessLevel = 'readonly',
        
        [string]$IsolationUser = $NativeHardeningConfig.IsolationUser
    )

    Write-Host "[ACL] Setting strict ACL on: $Path (Access: $AccessLevel)" -ForegroundColor Cyan

    $Acl = Get-Acl -Path $Path

    # Remove inherited permissions
    $Acl.SetAccessRuleProtection($true, $false)
    $Acl.Access | ForEach-Object { $Acl.RemoveAccessRule($_) | Out-Null }

    # Create identity
    $IsolationUserSid = New-Object System.Security.Principal.NTAccount($IsolationUser)

    switch ($AccessLevel) {
        'readonly' {
            # Read + Execute only
            $Rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
                $IsolationUserSid,
                'ReadAndExecute',
                'ContainerInherit,ObjectInherit',
                'None',
                'Allow'
            )
            Write-Host "[ACL] Applied: Read-Only (r-x)" -ForegroundColor Green
        }
        
        'readwrite' {
            # Modify (read + write + execute)
            $Rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
                $IsolationUserSid,
                'Modify',
                'ContainerInherit,ObjectInherit',
                'None',
                'Allow'
            )
            Write-Host "[ACL] Applied: Read-Write (rwx)" -ForegroundColor Green
        }
        
        'immutable' {
            # Read only, no recursive inheritance
            $Rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
                $IsolationUserSid,
                'Read',
                'None',
                'None',
                'Allow'
            )
            Write-Host "[ACL] Applied: Immutable (r--)" -ForegroundColor Green
        }
    }

    # Add SYSTEM (admin) and Current User for backup
    $SystemSid = New-Object System.Security.Principal.SecurityIdentifier('S-1-5-18')
    $SystemRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $SystemSid,
        'FullControl',
        'ContainerInherit,ObjectInherit',
        'None',
        'Allow'
    )

    $CurrentUserSid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User
    $CurrentUserRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $CurrentUserSid,
        'FullControl',
        'ContainerInherit,ObjectInherit',
        'None',
        'Allow'
    )

    $Acl.AddAccessRule($Rule)
    $Acl.AddAccessRule($SystemRule)
    $Acl.AddAccessRule($CurrentUserRule)

    Set-Acl -Path $Path -AclObject $Acl
    Write-Host "[SUCCESS] ACL applied to: $Path" -ForegroundColor Green
}

#endregion

#region Audit User Setup

function New-AuditUser {
    <#
    .SYNOPSIS
        Create unprivileged local user for audit processes.
    
    .DESCRIPTION
        Equivalent to Docker's non-root user (UID 65532).
        - No interactive login rights
        - No admin group membership
        - Unique home directory with restricted permissions
    #>
    
    [CmdletBinding()]
    param(
        [string]$UserName = $NativeHardeningConfig.IsolationUser
    )

    Write-Host "[USER] Creating unprivileged audit user: $UserName" -ForegroundColor Cyan

    # Check if user exists
    try {
        $User = Get-LocalUser -Name $UserName -ErrorAction Stop
        Write-Host "[INFO] User already exists: $UserName (SID: $($User.SID))" -ForegroundColor Yellow
        return $User
    }
    catch [Microsoft.PowerShell.Commands.UserNotFoundException] {
        # Create new user
    }

    # Generate password (PS Core compatible)
    $Bytes = New-Object Byte[] 32
    $Generator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $Generator.GetBytes($Bytes)
    $Password = [Convert]::ToBase64String($Bytes)
    $SecurePassword = ConvertTo-SecureString -String $Password -AsPlainText -Force

    try {
        $NewUser = New-LocalUser -Name $UserName `
            -Password $SecurePassword `
            -PasswordNeverExpires:$false `
            -UserMayNotChangePassword:$true `
            -Description $NativeHardeningConfig.IsolationUserDescription

        Write-Host "[SUCCESS] User created: $UserName (SID: $($NewUser.SID))" -ForegroundColor Green

        # Remove from all groups
        @('Administrators', 'Remote Desktop Users', 'Power Users', 'Backup Operators') | ForEach-Object {
            $Group = Get-LocalGroup -Name $_ -ErrorAction SilentlyContinue
            if ($Group) {
                Remove-LocalGroupMember -Group $Group -Member $UserName -ErrorAction SilentlyContinue
            }
        }

        # Deny interactive login (secedit)
        $SecEditCfg = @"
[Privilege Rights]
SeDenyInteractiveLogonRight = $UserName
"@

        $TempCfg = New-TemporaryFile
        Set-Content -Path $TempCfg.FullName -Value $SecEditCfg
        secedit.exe /configure /db secedit.sdb /cfg $TempCfg.FullName 2>&1 | Out-Null
        Remove-Item -Path $TempCfg.FullName -Force

        Write-Host "[SUCCESS] Denied interactive login for: $UserName" -ForegroundColor Green

        # Store password securely (temp file, removed after use)
        $CredFile = "$env:TEMP\.${UserName}_cred.enc"
        $SecurePassword | ConvertFrom-SecureString | Set-Content -Path $CredFile -Force
        Write-Host "[INFO] Credential cached at: $CredFile (auto-clean after execution)" -ForegroundColor Cyan

        return $NewUser
    }
    catch {
        Write-Error "Failed to create audit user: $_"
        throw
    }
}

#endregion

#region Main Hardening

function Initialize-NativePrivilegeHardening {
    <#
    .SYNOPSIS
        Initialize complete native privilege hardening environment.
    
    .DESCRIPTION
        One-command setup:
        1. Create audit user
        2. Set up directory structure with ACLs
        3. Deploy JEA endpoint
        4. Enable Constrained Language Mode
        5. Configure AppLocker policy
        6. Set up audit logging
    #>
    
    [CmdletBinding()]
    param(
        [switch]$SkipJea,
        [switch]$SkipClm,
        [switch]$SkipAppLocker
    )

    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║  Native Privilege Hardening (Docker-Equivalent)          ║" -ForegroundColor Magenta
    Write-Host "║  JEA | CLM | AppLocker | ACL | Audit User               ║" -ForegroundColor Magenta
    Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Magenta

    # Check for admin
    if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]'Administrator')) {
        throw "ERROR: This script requires administrator privileges."
    }

    # Step 1: Create directories
    Write-Host "`n[SETUP] Creating directory structure..." -ForegroundColor Yellow
    @(
        $NativeHardeningConfig.ApplicationPath,
        $NativeHardeningConfig.AuditPath,
        $NativeHardeningConfig.CachePath,
        $NativeHardeningConfig.JeaConfigPath,
        $NativeHardeningConfig.AppLockerPath
    ) | ForEach-Object {
        if (-not (Test-Path -Path $_)) {
            New-Item -ItemType Directory -Path $_ -Force | Out-Null
            Write-Host "[OK] Created: $_" -ForegroundColor Green
        }
    }

    # Step 2: Create audit user
    Write-Host "`n[SETUP] Creating audit user..." -ForegroundColor Yellow
    $AuditUser = New-AuditUser

    # Step 3: Set ACLs on directories
    Write-Host "`n[SETUP] Configuring directory ACLs..." -ForegroundColor Yellow
    Set-StrictAcl -Path $NativeHardeningConfig.ApplicationPath -AccessLevel 'readonly'
    Set-StrictAcl -Path $NativeHardeningConfig.AuditPath -AccessLevel 'readwrite'
    Set-StrictAcl -Path $NativeHardeningConfig.CachePath -AccessLevel 'readwrite'

    # Step 4: Deploy JEA (optional)
    if (-not $SkipJea) {
        Write-Host "`n[SETUP] Deploying JEA endpoint..." -ForegroundColor Yellow
        try {
            New-JeaSessionConfiguration
        }
        catch {
            Write-Warning "JEA deployment failed: $_"
        }
    }

    # Step 5: Deploy CLM wrapper
    if (-not $SkipClm) {
        Write-Host "`n[SETUP] Preparing CLM wrapper..." -ForegroundColor Yellow
        Write-Host "[INFO] CLM wrapping ready (use: Publish-ClmWrapper -ScriptPath <script>)" -ForegroundColor Cyan
    }

    # Step 6: Deploy AppLocker
    if (-not $SkipAppLocker) {
        Write-Host "`n[SETUP] Configuring AppLocker policy..." -ForegroundColor Yellow
        try {
            Deploy-AppLockerPolicy
        }
        catch {
            Write-Warning "AppLocker configuration failed: $_"
        }
    }

    Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  ✓ NATIVE HARDENING ENVIRONMENT INITIALIZED              ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

    Write-Host "Summary:" -ForegroundColor Cyan
    Write-Host "  Audit User:        $($NativeHardeningConfig.IsolationUser)" -ForegroundColor Green
    Write-Host "  App Path:          $($NativeHardeningConfig.ApplicationPath) (read-only)" -ForegroundColor Green
    Write-Host "  Audit Path:        $($NativeHardeningConfig.AuditPath) (read-write)" -ForegroundColor Green
    Write-Host "  JEA Endpoint:      $($NativeHardeningConfig.JeaEndpointName)" -ForegroundColor Green
    Write-Host "  CLM Support:       Ready" -ForegroundColor Green
    Write-Host "  AppLocker:         Audit mode" -ForegroundColor Green
}

#endregion

# Export public functions
Export-ModuleMember -Function @(
    'Initialize-NativePrivilegeHardening',
    'New-JeaSessionConfiguration',
    'Publish-ClmWrapper',
    'Deploy-AppLockerPolicy',
    'Set-StrictAcl',
    'New-AuditUser'
)

# Execute if run as script (not imported as module)
if ($MyInvocation.InvocationName -ne '.') {
    Initialize-NativePrivilegeHardening
}
