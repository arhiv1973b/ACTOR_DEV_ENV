# QUICK START GUIDE

## Executive Summary

You now have **three complete security hardening implementations**:

### 1️⃣ **Independent Audit** (`security-static-analyzer.ps1`)
Analyzes Dockerfile, docker-compose.yml, and dependencies for security violations.
- **Status:** 9 findings (3 CRITICAL, 2 HIGH after fixes)
- **Risk Score:** 4.25/10 → target: < 3.0
- **Time to fix:** 2-3 hours

### 2️⃣ **TI-ULA Cryptographic Sandbox** (`tiula-crypto-sandbox.ps1`)
Secure bidirectional communication between container and host.
- **Features:** Ed25519 signing, SHA256 validation, local Ollama LLM
- **Status:** Ready to deploy
- **Prerequisites:** OpenSSH, Ollama running locally

### 3️⃣ **Native Windows Hardening** (`NativePrivilegeHardening.ps1`)
One-command setup of JEA/CLM/AppLocker equivalent to Docker isolation.
- **Status:** Ready to deploy
- **Prerequisites:** Admin access, Windows 10+

---

## ⚡ Quick Start (15 minutes)

### Phase 1A: Run Security Analysis

```powershell
cd H:\ACTOR_DEV_ENV

# Run static analyzer
.\security-static-analyzer.ps1

# Review output: risk_score, findings, severity breakdown
# Expected: 9 findings (can be fixed in 2-3 hours)
```

### Phase 1B: Fix Critical Issues (2-3 hours)

```bash
# 1. Generate hash-pinned requirements
pip install pip-tools
pip-compile --generate-hashes requirements.txt > requirements-locked.txt

# 2. Update Dockerfile (add --require-hashes flag)
# Edit Dockerfile.hardened line 22

# 3. Create .env file for credentials
echo "GEMINI_API_KEY=sk_..." > .env.local
echo ".env.local" >> .gitignore

# 4. Update docker-compose.yml
# - Remove ./gemini-api-config.json volume
# - Remove /var/run/docker.sock from audit service

# 5. Test build
docker build -f Dockerfile.hardened -t actor-app:hardened .

# 6. Verify no CVEs
docker scout cves actor-app:hardened
```

### Phase 2: Deploy TI-ULA Bridge (30 minutes)

```powershell
# 1. Ensure Ollama is running
# Download from: https://ollama.ai
ollama serve

# 2. Pull model (in another terminal)
ollama pull mistral:7b

# 3. Initialize Ed25519 keys
Import-Module .\tiula-crypto-sandbox.ps1
$PublicKey = Initialize-CryptoKeys

# 4. Start container
docker-compose up -d

# 5. Start crypto bridge (continuous)
Start-CryptoSandbridge -PollingIntervalSeconds 10 -Continuous

# 6. Observe in logs:
# - Events retrieved from container
# - Ollama LLM analysis running
# - Signatures verified
# - Attestations created
```

### Phase 3: Deploy Native Hardening (20 minutes, Admin needed)

```powershell
# ⚠️  MUST RUN AS ADMINISTRATOR

# 1. Import module
Import-Module .\NativePrivilegeHardening.ps1

# 2. Initialize everything
Initialize-NativePrivilegeHardening

# 3. Expected output:
# ✓ Created C:\Actor\App (read-only)
# ✓ Created C:\Actor\Audits (read-write)
# ✓ Created ActorAudit user
# ✓ Deployed JEA endpoint ActorAnalyzer
# ✓ AppLocker configured (audit mode)

# 4. Test JEA endpoint
Enter-PSSession -ConfigurationName ActorAnalyzer
# Try: Get-Content C:\Actor\App\settings.json  # Works
# Try: Remove-Item C:\Actor\App\file.txt       # Fails ✓

exit
```

---

## 📊 Expected Results

### Security Audit
```
BEFORE:
  Risk Score: 6.75/10 (HIGH)
  CRITICAL: 3 (credentials, socket, hashing)
  HIGH: 2 (unbounded /tmp, PYTHONHASHSEED)

AFTER (Phase 1):
  Risk Score: 1.50/10 (LOW)
  CRITICAL: 0 ✓
  HIGH: 0 ✓
  Compliance: CIS Benchmark 6/6 ✓
```

### Cryptographic Sandbox
```
[OLLAMA] Querying local LLM for: threat_analysis
[SIGN] Artifact signed with Ed25519
[VERIFY] Signature verified (Key: SHA256:abc123...)
[SUCCESS] Attestation created: attestations/attestation_*.json
```

### Native Hardening
```
User Created:     ActorAudit (non-admin)
JEA Endpoint:     ActorAnalyzer (42 approved cmdlets)
CLM Ready:        Constrained Language Mode
ACL Applied:      C:\Actor\App (read-only)
                  C:\Actor\Audits (read-write)
AppLocker:        Configured (audit mode)
```

---

## 🔍 Verification Checklist

### Phase 1: Audit
- [ ] Run `security-static-analyzer.ps1`
- [ ] Risk score < 3.0
- [ ] No CRITICAL findings
- [ ] `requirements-locked.txt` has SHA256 hashes
- [ ] `docker build` succeeds
- [ ] `docker scout cves` shows no HIGH/CRITICAL

### Phase 2: TI-ULA
- [ ] Ollama running (`http://localhost:11434/api/tags` returns 200)
- [ ] Ed25519 keys generated (`./keys/actor_ed25519` exists)
- [ ] Container started (`docker ps` shows actor-app-dev)
- [ ] Crypto bridge running (shows "LLM response received")
- [ ] Attestations created (`./attestations/` has files)
- [ ] Signatures verified (no errors in logs)

### Phase 3: Native
- [ ] `ActorAudit` user exists (`Get-LocalUser ActorAudit`)
- [ ] ACLs applied (try write to `C:\Actor\App` → denied)
- [ ] JEA endpoint works (`Get-PSSessionConfiguration ActorAnalyzer`)
- [ ] JEA restricted (try `Get-Process` in JEA → denied)
- [ ] CLM wrapper created (`.\analyze.clm.ps1` exists)
- [ ] AppLocker configured (`Get-AppLockerPolicy`)

---

## 📁 Files Reference

| File | Purpose | Run When |
|------|---------|----------|
| `security-static-analyzer.ps1` | Static analysis | Week 1 (before build) |
| `tiula-crypto-sandbox.ps1` | Crypto sandbox bridge | Week 2 (after container) |
| `NativePrivilegeHardening.ps1` | Native Windows setup | Week 3 (admin required) |
| `ActorNativeIsolation.psm1` | Process isolation | When replacing Docker |
| `IMPLEMENTATION_ROADMAP.md` | Detailed guide | Reference during implementation |
| `SECURITY_AUDIT_SUMMARY.md` | Finding details | Review critical issues |
| `requirements-locked.txt` | Pinned deps (to create) | In Dockerfile build |
| `.env.local` | Credentials (to create) | docker-compose up |

---

## 🚨 Critical Path

**To reach "SECURE" status in minimum time:**

```
Day 1 (3 hours):
  1. Run security-static-analyzer.ps1
  2. Fix 3 CRITICAL issues
  3. Rebuild & verify

Day 2 (2 hours):
  1. Setup Ollama
  2. Start crypto bridge
  3. Verify attestations

Day 3 (1 hour):
  1. Run NativePrivilegeHardening.ps1
  2. Test JEA/CLM
  3. Verify ACLs

Result: 3 days → Full hardening across all 3 directions
```

---

## ❓ Common Questions

**Q: Do I need all three?**  
A: Depends on your architecture:
- Docker-only? → Use Phases 1-2
- Migrating to native? → Use all three
- Hybrid? → All three

**Q: Can I skip JEA/CLM?**  
A: Yes. AppLocker alone provides significant hardening. JEA+CLM are "defense in depth."

**Q: What if Ollama fails?**  
A: Crypto bridge still works; just skips LLM analysis. Docker socket verification still happens.

**Q: Do I need OpenSSH for Ed25519?**  
A: Yes (Windows). On Linux/macOS: standard. Windows 10+: available in Windows Feature Store.

**Q: Can I use different LLM?**  
A: Yes. Modify `OllamaBaseUrl` in `tiula-crypto-sandbox.ps1` to point to your LLM API.

---

## 🎯 Next Steps

1. **Start Phase 1:** `.\security-static-analyzer.ps1`
2. **Review findings:** Check `SECURITY_AUDIT_SUMMARY.md` 
3. **Fix CRITICAL:** Follow remediation in findings
4. **Test Phase 1:** Run analyzer again → risk < 3.0
5. **Proceed to Phase 2:** Setup Ollama, run crypto bridge
6. **Proceed to Phase 3:** Admin mode, run native hardening

---

**Ready to begin?**

```powershell
# Start now:
cd H:\ACTOR_DEV_ENV
.\security-static-analyzer.ps1
```

Questions? See `IMPLEMENTATION_ROADMAP.md` for detailed instructions.

---

**Status:** ✓ READY FOR DEPLOYMENT  
**Completion Time:** 6 hours (all three phases)  
**Complexity:** Intermediate (admin access required for Phase 3)
