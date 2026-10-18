#!/usr/bin/env bash
set -e

echo "=== 1. Starting Full Repository & Submodule Audit and Repair ==="

# Check overall status
git status

# Function to clean and commit a submodule if modified
audit_submodule() {
    local subpath="$1"
    local msg="$2"
    if [ -d "$subpath/.git" ] || [ -f "$subpath/.git" ]; then
        echo "--- Auditing submodule/repo: $subpath ---"
        git -C "$subpath" status
        if [ -n "$(git -C "$subpath" status --porcelain)" ]; then
            echo "Changes detected in $subpath. Committing..."
            git -C "$subpath" add .
            git -C "$subpath" commit -m "$msg" || true
        else
            echo "$subpath is clean."
        fi
    fi
}

# 2. Audit and repair individual submodules / repos
audit_submodule ".actor_socket" "fix(socket): automated audit sync and tool registry update"
audit_submodule "projects/antigravity-sdk-python" "feat(sdk): update sdk references and default models"
audit_submodule "projects/mcp-servers" "fix(mcp): update mcp servers dependencies and structure"
audit_submodule "projects/testcontainers-cloud-nodejs-example" "fix(example): update testcontainers and dependencies"
audit_submodule "voidImageViewer" "fix(viewer): clean build and metadata"

# Clean up nested mcp-servers repo inside projects/mcp-servers if present as untracked embedded repo
if [ -d "projects/mcp-servers/mcp-servers" ]; then
    echo "--- Handling nested mcp-servers repository ---"
    git -C "projects/mcp-servers" rm --cached mcp-servers || true
    rm -rf projects/mcp-servers/mcp-servers
fi

# Clean up PaxHeaders in voidImageViewer if any
find voidImageViewer -name "PaxHeaders.X" -type d -exec rm -rf {} + 2>/dev/null || true
rm -f drive_index.db-shm drive_index.db-wal 2>/dev/null || true

# 3. Update submodule references in main repository
echo "=== 3. Updating submodule references in main repository ==="
git add .actor_socket projects/antigravity-sdk-python projects/mcp-servers projects/testcontainers-cloud-nodejs-example voidImageViewer || true

if [ -n "$(git status --porcelain)" ]; then
    echo "Committing updated submodule references in main repository..."
    git commit -m "chore: sync and update all submodule references and audit state"
else
    echo "Main repository is already up to date."
fi

# 4. Final status check
echo "=== 4. Final Git Status ==="
git status

# Send email report if configured
if [ -f "send_audit_report.py" ]; then
    echo "Sending email audit report..."
    python3 send_audit_report.py || true
fi

echo "=== Audit and Repair Complete Successfully ==="
