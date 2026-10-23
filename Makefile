.PHONY: all audit win linux

all: audit

audit:
	@if [ -f /proc/version ] && grep -q Microsoft /proc/version; then \
		echo "WSL detected, running bash audit..."; \
		bash audit.sh; \
	elif [ "$$OS" = "Windows_NT" ] || command -v powershell.exe >/dev/null 2>&1; then \
		echo "Windows detected, running PowerShell audit script..."; \
		powershell.exe -ExecutionPolicy Bypass -File audit_sync_all_repos.ps1 -AutoCommit -AutoPush; \
	else \
		echo "Linux/Unix detected, running bash audit..."; \
		bash audit.sh; \
	fi

win:
	powershell.exe -ExecutionPolicy Bypass -File audit_sync_all_repos.ps1 -AutoCommit -AutoPush

linux:
	bash audit.sh
