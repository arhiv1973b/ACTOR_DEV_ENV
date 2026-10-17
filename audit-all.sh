#!/usr/bin/env bash
set -e

echo "=== Universal Audit & Repair Dispatcher ==="

# Check if running on Windows (Git Bash, MSYS, Cygwin, etc.)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    echo "Windows environment detected. Dispatching PowerShell audit script..."
    powershell.exe -ExecutionPolicy Bypass -File audit_sync_all_repos.ps1 -AutoCommit -AutoPush
else
    echo "Linux/WSL environment detected. Dispatching Bash audit script..."
    bash audit.sh
fi

echo "=== Universal Audit Dispatcher Completed Successfully ==="
