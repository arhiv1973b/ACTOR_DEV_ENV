#!/usr/bin/env bash
# Setup Linux/WSL Cron job to run audit-all.sh daily at 02:00 with .env loading

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Sourcing .env or .env.audit.local if it exists so cron picks up credentials correctly
CRON_JOB="0 2 * * * cd $REPO_DIR && for f in .env.audit.local .env.audit .env; do if [ -f \"\$f\" ]; then set -a; . \"./\$f\"; set +a; break; fi; done; bash audit-all.sh >> $REPO_DIR/audit.log 2>&1"

(crontab -l 2>/dev/null | grep -Fv "audit-all.sh"; echo "$CRON_JOB") | crontab -

echo "Cron job successfully installed for Linux/WSL (target: arhiv240@gmail.com):"
crontab -l | grep "audit-all.sh"
