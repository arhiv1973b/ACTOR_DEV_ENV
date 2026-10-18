# Deployment View 2026: ActorDevEnv Architecture

## Overview
This document outlines the deployment view, execution flow, and architectural components of the **ActorDevEnv** forensic and audit automation framework (Case: `CASE-MACHERET-1997-2026`).

---

## Architectural Components

1. **EnvDev (Environment & Profiles)**
   - Developer selects the operational profile (`Local`, `Staging`, `Production`).
   - Active `.env.audit` is generated dynamically via template replication.

2. **OS Layer (OSWindows / OSLinux)**
   - Automated triggers via Windows Task Scheduler or Linux Cron.
   - Manual execution options via `audit-all.sh`, Makefile, or PowerShell scripts (`sync_l0_to_google_drive.ps1`, `setup-task-scheduler.ps1`).

3. **CoreEngine (Automation & Audit)**
   - PowerShell / Bash execution engines performing integrity verification, artifact pruning, L0 witness generation, and git synchronization.
   - Air-gapped replication bridge to Google Drive mirror (`F:\Мой диск\ACTOR_DEV_ENV`).

4. **Logging & Retention**
   - Centralized logging into `audit_log.json`, `audit.log`, and archive directories.
   - Strict retention and MaxLogs policies.

5. **Notifier**
   - Python-based notification bridge transmitting audit reports via Gmail SMTP to `arhiv240@gmail.com`.

---

## Verification & Integrity
- **L0 Invariants:** Mathematical witnesses (`INTEGRITY_WITNESS.json`, `evidence_manifest.json`) ensure immutable chain-of-custody.
- **Sync Status:** Dual-contour execution verified across local Git DAG and Google Drive cloud storage.
