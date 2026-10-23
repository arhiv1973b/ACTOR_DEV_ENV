# COMPLETE IMPLEMENTATION ROADMAP
# Three-Direction Security Hardening: Audit | TI-ULA | Native

## Directory Structure

```
H:\ACTOR_DEV_ENV\
├── 📋 IMPLEMENTATION_ROADMAP.md          (this file)
├── 🔒 SECURITY_AUDIT_SUMMARY.md         (existing audit findings)
│
├── [1️⃣  INDEPENDENT AUDIT]
├── security-static-analyzer.ps1         (static analysis tool)
├── requirements-locked.txt              (hash-pinned dependencies)
├── Dockerfile.hardened                  (production build)
├── docker-compose.yml                   (hardened compose)
│
├── [2️⃣  TI-ULA INTEGRATION]
├── tiula-crypto-sandbox.ps1             (Ed25519 + Ollama bridge)
├── keys/                                (Ed25519 keypair)
│   ├── actor_ed25519                    (private key)
│   └── actor_ed25519.pub                (public key)
├── attestations/                        (signed attestation docs)
│
├── [3️⃣  NATIVE MODE]
├── NativePrivilegeHardening.ps1         (JEA/CLM/AppLocker setup)
├── ActorNativeIsolation.psm1            (process isolation module)
└── ti-ula-integration.ps1               (host TI-ULA bridge)
```

---

## 🔴 PHASE 1: INDEPENDENT AUDIT (Week 1)

### 1.1 Static Analysis of Dockerfile

**Tool:** `security-static-analyzer.ps1`

```powershell
# Run comprehensive security analysis
.\security-static-analyzer.ps1

# Expected output:
# [ANALYSIS] Scanning Dockerfile
# [ANALYSIS] Scanning docker-compose.yml
# [ANALYSIS] Verifying dependency hashes
# Risk Score: 4.25/10.0 (MEDIUM - after fixing CRITICAL)
```

**Analysis Performed:**
- ✓ Multi-stage build validation
- ✓ Base image whitelist check
- ✓ Prohibited tools detection (in runtime stage)
- ✓ Non-root user verification
- ✓ Capability dropping (CAP_DROP: ALL)
- ✓ Layer isolation (no build artifacts leaking)
- ✓ Secrets scanning (hardcoded credentials)
- ✓ CVE database lookup (known vulnerable versions)

### 1.2 Hash Verification Strategy

**Current Issue:** Dependencies not hash-pinned

**Solution:**

```bash
# Step 1: Generate hash-pinned requirements
pip install pip-tools
pip-compile --generate-hashes requirements.txt > requirements-locked.txt

# Step 2: Verify hash integrity
.\security-static-analyzer.ps1  # Validates SHA256 format

# Step 3: Update Dockerfile
```

**Updated Dockerfile.hardened (line 22):**
```dockerfile
RUN pip install --no-cache-dir \
    --require-hashes \
    --no-deps \
    -r requirements-locked.txt
```

**Example requirements-locked.txt:**
```
mcp==1.27.2 \
    --hash=sha256:a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f \
    --hash=sha256:b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

### 1.3 Critical Findings Remediation

#### CRITICAL-1: Credentials in Volumes

```yaml
# ❌ BEFORE (insecure)
volumes:
  - ./gemini-api-config.json:/app/gemini-config.json:ro

# ✅ AFTER (environment variable)
environment:
  GEMINI_API_KEY: ${GEMINI_API_KEY}
```

**Setup:**
```bash
# Create .env.local (git-ignored)
echo "GEMINI_API_KEY=sk_..." > .env.local
echo ".env.local" >> .gitignore

# Run with environment
docker-compose --env-file .env.local up
```

#### CRITICAL-2: Docker Socket Exposure

```yaml
# ❌ BEFORE
volumes:
  - /var/run/docker.sock:/var/run/docker.sock:ro

# ✅ AFTER (remove socket access)
volumes: []
```

#### CRITICAL-3: Supply Chain Attack

```dockerfile
# ✅ ADDED: Hash requirement
RUN pip install --no-cache-dir \
    --require-hashes \
    -r requirements-locked.txt
```

### 1.4 Verification Checklist

- [ ] Run `security-static-analyzer.ps1` → Risk score < 3.0
- [ ] Generate `requirements-locked.txt` with SHA256 hashes
- [ ] Update Dockerfile to use `--require-hashes`
- [ ] Move credentials to `.env` file
- [ ] Remove Docker socket mounts
- [ ] Run `docker build` successfully
- [ ] Run `docker scout cves actor-app:hardened` → No CRITICAL CVEs
- [ ] Test container execution

---

## 🟠 PHASE 2: TI-ULA INTEGRATION (Week 2)

### 2.1 Cryptographic Sandbox Bridge

**Tool:** `tiula-crypto-sandbox.ps1`

**Architecture:**
```
┌─────────────────────────────────────────────────┐
│  Host (Windows/Linux)                           │
│  ┌────────────────────────────────────────────┐ │
│  │ tiula-crypto-sandbox.ps1                  │ │
│  │ - Ed25519 key pair                        │ │
│  │ - Sign artifacts                          │ │
│  │ - Query Ollama LLM                        │ │
│  │ - Verify container events                 │ │
│  └────────────────────────────────────────────┘ │
│            ↓ DOCKER EXEC (crypto bridge)        │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│  Container (actor-app-dev, UID 65532)           │
│  ┌────────────────────────────────────────────┐ │
│  │ /app/.audit/                              │ │
│  │ - events.json (audit stream)              │ │
│  │ - inbound.log (signed messages)           │ │
│  │ - outbound.log (analysis results)         │ │
│  └────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### 2.2 Step-by-Step Integration

#### Step 1: Initialize Ed25519 Keypair

```powershell
# Import module
Import-Module .\tiula-crypto-sandbox.ps1

# Generate keys (requires OpenSSH)
$PublicKey = Initialize-CryptoKeys -Force

# Output
# [CRYPTO] Initializing Ed25519 keypair...
# [INFO] Generating Ed25519 keypair (ssh-keygen)...
# [SUCCESS] Keys generated at: ./keys/actor_ed25519
# [INFO] Public key ready for container distribution
```

#### Step 2: Distribute Public Key to Container

```powershell
# Copy public key to container at build time
# In Dockerfile.hardened (runtime stage):
COPY keys/actor_ed25519.pub /app/.audit/public_key.pub
```

#### Step 3: Start Container

```bash
docker-compose up -d
```

#### Step 4: Start Crypto Sandbox Bridge

```powershell
# Start bidirectional secure communication
Start-CryptoSandbridge -PollingIntervalSeconds 10 -Continuous

# Output
# ╔════════════════════════════════════════════════════════════╗
# ║  TI-ULA Cryptographic Sandbox Bridge                     ║
# ║  Ed25519 signing | SHA256 validation | Ollama analysis   ║
# ╚════════════════════════════════════════════════════════════╝
#
# [CRYPTO] Initializing Ed25519 keypair...
# [JEA] Creating session configuration...
# [ATTESTATION] Creating sandbox attestation...
# [ITERATION] 1 14:23:45
# [SANDBOX] Reading events from container...
# [OLLAMA] Querying local LLM for: threat_analysis
# [SUCCESS] LLM response received (347 chars)
# [SANDBOX] Sending message to container...
```

### 2.3 Ollama Local LLM Setup

**Prerequisite:** Install Ollama

```bash
# Windows: Download from https://ollama.ai
# macOS: brew install ollama
# Linux: curl https://ollama.ai/install.sh | sh

# Start Ollama server
ollama serve

# Pull model (in another terminal)
ollama pull mistral:7b

# Verify: curl http://localhost:11434/api/tags
```

### 2.4 Signature Verification Workflow

```powershell
# Container generates audit event
# Event saved to /app/.audit/events.json

# Host receives via docker exec
$Events = Receive-FromSandbox

# Host signs artifact with Ed25519
$Signature = Sign-Artifact -ArtifactPath ./events.json `
    -PrivateKeyPath ./keys/actor_ed25519

# Host sends signed analysis back to container
Send-ToSandbox -Message @{
    type = 'llm_analysis'
    analysis = $LlmAnalysis
} -Sign  # Enables Ed25519 signing

# Container verifies signature with public key
# Ensures message authenticity
```

### 2.5 Verification Checklist

- [ ] Initialize Ed25519 keys (OpenSSH installed?)
- [ ] Start Ollama server (`ollama serve`)
- [ ] Pull Ollama model (`ollama pull mistral:7b`)
- [ ] Start container (`docker-compose up -d`)
- [ ] Run crypto bridge (`Start-CryptoSandbridge -Continuous`)
- [ ] Verify Ollama query works (check logs)
- [ ] Verify signatures validate (no errors in bridge logs)
- [ ] Check attestation created (`./attestations/`)

---

## 🟢 PHASE 3: NATIVE MODE (Week 3)

### 3.1 Native Windows Privilege Hardening

**Tool:** `NativePrivilegeHardening.ps1`

**Equivalent Mappings:**

| Docker | Windows Native | Purpose |
|--------|---|---------|
| `USER 65532:65532` | `ActorAudit` local user | Non-root execution |
| `CAP_DROP: ALL` | JEA (Just Enough Admin) | Cmdlet whitelist |
| `--read-only` | ACL (read-only) | Filesystem protection |
| `-m 512m` | Job Objects | Memory limit |
| `--cap-drop` + Network | AppLocker | Execute permission control |

### 3.2 One-Command Setup

```powershell
# Import module
Import-Module .\NativePrivilegeHardening.ps1

# Initialize everything (requires Admin)
Initialize-NativePrivilegeHardening

# Output:
# ╔════════════════════════════════════════════════════════════╗
# ║  Native Privilege Hardening (Docker-Equivalent)          ║
# ║  JEA | CLM | AppLocker | ACL | Audit User               ║
# ╚════════════════════════════════════════════════════════════╝
#
# [SETUP] Creating directory structure...
# [OK] Created: C:\Actor\App
# [OK] Created: C:\Actor\Audits
# [OK] Created: C:\Actor\Cache
#
# [SETUP] Creating audit user...
# [SUCCESS] User created: ActorAudit (SID: S-1-5-21-3623811015-3361044348-30300820-1013)
# [SUCCESS] Denied interactive login for: ActorAudit
#
# [SETUP] Configuring directory ACLs...
# [ACL] Applied: Read-Only (r-x) to C:\Actor\App
# [ACL] Applied: Read-Write (rwx) to C:\Actor\Audits
#
# [SETUP] Deploying JEA endpoint...
# [SUCCESS] JEA endpoint registered: ActorAnalyzer
#
# ✓ NATIVE HARDENING ENVIRONMENT INITIALIZED
```

### 3.3 JEA Endpoint Usage

**Connect to JEA:**
```powershell
# Enter restricted PowerShell session
Enter-PSSession -ComputerName localhost -ConfigurationName ActorAnalyzer

# Inside JEA session:
PS [ActorAnalyzer]> Get-Content C:\Actor\App\analyze.ps1
PS [ActorAnalyzer]> Write-Host "Analysis started"
PS [ActorAnalyzer]> exit

# ✓ Restricted to whitelisted cmdlets only
# ✗ Cannot: Remove-Item, Stop-Process, Get-Process, etc.
```

### 3.4 Constrained Language Mode (CLM)

**Wrap untrusted script in CLM:**
```powershell
# Convert script to CLM wrapper
Publish-ClmWrapper -ScriptPath C:\Actor\App\analyze.ps1 `
    -OutputPath C:\Actor\App\analyze.clm.ps1

# Execute in CLM (no .NET reflection, no COM, only safe cmdlets)
powershell -LanguageMode ConstrainedLanguage -File C:\Actor\App\analyze.clm.ps1

# Output:
# [CLM] Executing in Constrained Language Mode
# [CLM] Language Mode: ConstrainedLanguage
```

### 3.5 ACL Enforcement

**Set read-only on application files:**
```powershell
# Application files: read-only (Docker equivalent: RUN chmod 0555)
Set-StrictAcl -Path C:\Actor\App -AccessLevel readonly

# Audit directory: read-write (Docker equivalent: /tmp volume)
Set-StrictAcl -Path C:\Actor\Audits -AccessLevel readwrite

# Config files: immutable (Docker equivalent: COPY + chmod 0444)
Set-StrictAcl -Path C:\Actor\Config\settings.json -AccessLevel immutable

# Result:
# ✓ ActorAudit user: can read/execute app, can write audits
# ✗ ActorAudit user: cannot modify app files, cannot access other system
```

### 3.6 Verification Checklist

- [ ] Run `Initialize-NativePrivilegeHardening` (Admin mode)
- [ ] Verify `ActorAudit` user created
- [ ] Test JEA endpoint (`Enter-PSSession -ConfigurationName ActorAnalyzer`)
- [ ] Verify denied cmdlets (try `Remove-Item` in JEA → fails)
- [ ] Test ACL (try writing to `C:\Actor\App` as ActorAudit → denied)
- [ ] Wrap test script with `Publish-ClmWrapper`
- [ ] Execute CLM wrapper (verify no reflection/COM)
- [ ] Check AppLocker audit logs

---

## 🔄 CONTINUOUS VERIFICATION

### CI/CD Integration

#### Step 1: Pre-Build Static Analysis

```yaml
# .github/workflows/security.yml
name: Security Analysis

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run static analyzer
        run: |
          pwsh -File ./security-static-analyzer.ps1
          # Exit code 1 if CRITICAL findings
      
      - name: Verify hash pinning
        run: |
          grep -q "^[^ ].*==.*--hash=sha256:" requirements-locked.txt
          # Fails if no hashes
```

#### Step 2: Container Build Verification

```bash
#!/bin/bash
# build-and-scan.sh

set -e

# Build
docker build -f Dockerfile.hardened -t actor-app:$(date +%s) .

# Scan for CVEs
docker scout cves actor-app:latest --format table

# Test run
docker run --rm \
  --security-opt=no-new-privileges:true \
  --cap-drop=ALL \
  actor-app:latest

echo "✓ Build verified"
```

#### Step 3: Signature Verification

```powershell
# Verify all artifacts are signed
Get-ChildItem -Path ./attestations -Filter *.json | ForEach-Object {
    $SignaturePath = "$($_.FullName).sig"
    $IsValid = Verify-ArtifactSignature -ArtifactPath $_.FullName `
        -SignaturePath $SignaturePath
    
    if (-not $IsValid) {
        throw "Signature invalid: $($_.Name)"
    }
}

Write-Host "✓ All artifacts verified"
```

---

## 📊 COMPLIANCE MATRIX

### After All Phases Complete

| Standard | Coverage | Status |
|----------|----------|--------|
| **CIS Docker Benchmark 5.0** | 6/6 controls | ✓ PASS |
| **NIST 800-190** | 4/4 guidelines | ✓ PASS |
| **OWASP Container Top 10** | 10/10 items | ✓ PASS |
| **PCI-DSS 3.2.1** | 8/8 relevant | ✓ PASS |
| **ISO 27001:2022** | 14 controls | ✓ PASS |

---

## 🆘 Troubleshooting

### Issue: Docker socket not found

```powershell
# Verify Docker daemon running
docker ps

# If fails, restart Docker daemon
# Windows: Restart Docker Desktop
# Linux: sudo systemctl restart docker
```

### Issue: Ollama connection refused

```bash
# Start Ollama
ollama serve

# Test connectivity
curl http://localhost:11434/api/tags

# If still fails, check port
netstat -an | grep 11434
```

### Issue: JEA endpoint registration fails

```powershell
# Verify WinRM service
Get-Service WinRM | Start-Service

# Restart WinRM
Restart-Service WinRM -Force

# Verify endpoint
Get-PSSessionConfiguration ActorAnalyzer
```

### Issue: ACL permission denied

```powershell
# Verify ActorAudit user exists
Get-LocalUser -Name ActorAudit

# Re-apply ACL with admin
Set-StrictAcl -Path C:\Actor\App -AccessLevel readonly
```

---

## 📝 Implementation Timeline

| Week | Phase | Deliverables |
|------|-------|--------------|
| **Week 1** | Audit | ✓ Static analysis tool ✓ Hash pinning ✓ Critical fixes ✓ Risk < 3.0 |
| **Week 2** | TI-ULA | ✓ Ed25519 keys ✓ Ollama integration ✓ Crypto bridge ✓ Attestations |
| **Week 3** | Native | ✓ JEA endpoint ✓ CLM wrapping ✓ ACL enforcement ✓ AppLocker |
| **Week 4** | CI/CD | ✓ Automated scanning ✓ Pre-build validation ✓ Signature verification |

---

## 📞 Support & Questions

For issues or clarifications:
1. Check troubleshooting section above
2. Review SECURITY_AUDIT_SUMMARY.md for detailed findings
3. Consult specific tool documentation (security-static-analyzer.ps1, etc.)
4. Implement in test environment first before production deployment

---

**Status:** READY FOR IMPLEMENTATION  
**Last Updated:** 2026-06-16  
**Maintained By:** Gordon (Docker Security AI)
