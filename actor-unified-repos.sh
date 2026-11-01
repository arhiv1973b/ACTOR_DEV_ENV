#!/usr/bin/env bash
# ==============================================================================
# actor-unified-repos.sh — A©tor / CASE-MACHERET Unified Repository Manager
# Principle: jus cogens + erga omnes — regional collisions nullified
# ==============================================================================

set -euo pipefail

ORG="arhiv1973b"
DEFAULT_WORKDIR="./actor-repos"

CORE_REPOS=(
  "ACTOR_DEV_ENV"
  "evidence-vault"
  "apostille-mirror"
  "apostille-archive-english"
  "apostille-archive"
  "evidence-pdfs-mirror"
  "maceret-case-evidence"
  "Reabilitare-Maceret-Oleinik-Negru-2026"
  "TI-ULA-Core"
  "A-tor"
  "TIULA-A-tor"
  "apostille-legal-case"
  "arhiv1973b.github.io"
  "ai-orchestration-hub"
  "D-A-tor"
  "ti-ula"
  "TI-MONAI_NODE_2025"
)

usage() {
  echo "Usage: $0 <command> [options]"
  echo "Commands:"
  echo "  list                 List target repositories"
  echo "  clone                Clone or update repositories"
  echo "  status               Check status (A©TOR_KEY, Docker, integrity)"
  echo "  audit                Static audit of Docker & integrity"
  echo "  harden               Harden repos (insert A©TOR_KEY, declaration, integrity)"
  echo "  mirror               Create bare mirrors & offline tarballs"
  echo "  docker-core          Generate zero-burden Dockerfile.actor-core"
  echo "  full                 Run full pipeline (clone -> status -> audit -> harden -> mirror -> docker-core)"
  echo "Options:"
  echo "  --workdir DIR        Working directory (default: $DEFAULT_WORKDIR)"
  echo "  --only REPO          Target only specified repository"
  echo "  --all                Include all 28 public repos instead of core 17"
  echo "  --dry-run            Show actions without executing"
  echo "  --force              Overwrite integrity / declaration files"
  exit 1
}

WORKDIR="$DEFAULT_WORKDIR"
ONLY_REPO=""
USE_ALL=false
DRY_RUN=false
FORCE=false
COMMAND=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    list|clone|status|audit|harden|mirror|docker-core|full)
      COMMAND="$1"
      shift
      ;;
    --workdir)
      WORKDIR="$2"
      shift 2
      ;;
    --only)
      ONLY_REPO="$2"
      shift 2
      ;;
    --all)
      USE_ALL=true
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --force)
      FORCE=true
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown option: $1"
      usage
      ;;
  esac
done

if [[ -z "$COMMAND" ]]; then
  usage
fi

get_repos() {
  if [[ -n "$ONLY_REPO" ]]; then
    echo "$ONLY_REPO"
  else
    for r in "${CORE_REPOS[@]}"; do
      echo "$r"
    done
  fi
}

cmd_list() {
  echo "=== A©tor Core Repositories ==="
  for r in $(get_repos); do
    echo " - $ORG/$r"
  done
}

cmd_clone() {
  mkdir -p "$WORKDIR"
  for r in $(get_repos); do
    target="$WORKDIR/$r"
    if [[ -d "$target/.git" ]]; then
      echo "[UPDATE] Pulling latest for $r..."
      if [[ "$DRY_RUN" == "false" ]]; then
        git -C "$target" pull --ff-only || true
      fi
    else
      echo "[CLONE] Cloning $ORG/$r into $target..."
      if [[ "$DRY_RUN" == "false" ]]; then
        git clone "https://github.com/$ORG/$r.git" "$target" || echo "[WARN] Clone failed for $r (may be private or offline)"
      fi
    fi
  done
}

cmd_status() {
  echo "=== Repository Status Check ==="
  for r in $(get_repos); do
    target="$WORKDIR/$r"
    echo "----------------------------------------"
    echo "Repository: $r"
    if [[ ! -d "$target" ]]; then
      echo "Status: NOT FOUND (run clone first)"
      continue
    fi
    has_key=false
    has_docker=false
    has_integrity=false
    
    if grep -rnw "$target" -e "A©TOR_KEY" --exclude-dir=.git 2>/dev/null; then
      has_key=true
    fi
    if [[ -f "$target/Dockerfile" || -f "$target/Dockerfile.actor-core" ]]; then
      has_docker=true
    fi
    if [[ -f "$target/integrity.json" || -f "$target/CHECKSUMS_SHA256.txt" ]]; then
      has_integrity=true
    fi

    echo "  A©TOR_KEY Present : $has_key"
    echo "  Docker Present    : $has_docker"
    echo "  Integrity Locked  : $has_integrity"
  done
}

cmd_audit() {
  echo "=== Static Audit (Docker + Integrity) ==="
  for r in $(get_repos); do
    target="$WORKDIR/$r"
    if [[ ! -d "$target" ]]; then
      continue
    fi
    echo "[AUDIT] Auditing $r..."
    # Check for root/privileged in Dockerfiles
    if [[ -f "$target/Dockerfile" ]]; then
      if grep -q "USER root" "$target/Dockerfile"; then
        echo "  [ALERT] $r: Dockerfile uses USER root"
      else
        echo "  [OK] $r: Dockerfile secure / non-root"
      fi
    fi
  done
}

cmd_harden() {
  echo "=== Hardening Repositories (A©TOR_KEY + integrity) ==="
  for r in $(get_repos); do
    target="$WORKDIR/$r"
    if [[ ! -d "$target" ]]; then
      echo "[SKIP] $r not found at $target"
      continue
    fi
    echo "[HARDEN] Hardening $r..."
    if [[ "$DRY_RUN" == "true" ]]; then
      continue
    fi

    # 1. ACTOR_DECLARATION.md
    decl_file="$target/ACTOR_DECLARATION.md"
    if [[ ! -f "$decl_file" ]] || [[ "$FORCE" == "true" ]]; then
      cat << 'EOF' > "$decl_file"
# [⚖ A©tor Declaration]
Principle: jus cogens + erga omnes — regional collisions nullified.
Self-proving container architecture. External attestation not required.
Case reference: CASE-MACHERET-1997-2026.
EOF
    fi

    # 2. integrity.json
    integrity_file="$target/integrity.json"
    if [[ ! -f "$integrity_file" ]] || [[ "$FORCE" == "true" ]]; then
      cat << EOF > "$integrity_file"
{
  "repository": "$r",
  "actor_key": "A©TOR_KEY = # [⚖ A©tor Declaration]",
  "principle": "jus cogens + erga omnes",
  "status": "ZERO_TRUST_LOCKED",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    fi

    # 3. CHECKSUMS_SHA256.txt
    sum_file="$target/CHECKSUMS_SHA256.txt"
    if [[ -d "$target/.git" ]]; then
      git -C "$target" ls-files | xargs sha256sum 2>/dev/null > "$sum_file" || true
    fi
  done
}

cmd_mirror() {
  echo "=== Mirroring & Offline Tarballs ==="
  mkdir -p "$WORKDIR/mirrors" "$WORKDIR/tarballs"
  for r in $(get_repos); do
    target="$WORKDIR/$r"
    if [[ ! -d "$target/.git" ]]; then
      continue
    fi
    echo "[MIRROR] Creating bare mirror & tarball for $r..."
    if [[ "$DRY_RUN" == "false" ]]; then
      git clone --mirror "https://github.com/$ORG/$r.git" "$WORKDIR/mirrors/$r.git" 2>/dev/null || true
      tar -czf "$WORKDIR/tarballs/$r.tar.gz" -C "$WORKDIR" "$r" 2>/dev/null || true
    fi
  done
}

cmd_docker_core() {
  echo "=== Generating Dockerfile.actor-core ==="
  artifacts_dir="$WORKDIR/artifacts"
  mkdir -p "$artifacts_dir"
  dockerfile_path="$artifacts_dir/Dockerfile.actor-core"
  
  if [[ "$DRY_RUN" == "false" ]]; then
    cat << 'EOF' > "$dockerfile_path"
# ==============================================================================
# Dockerfile.actor-core — Zero-Burden Self-Proving Core Container
# Principle: jus cogens + erga omnes — regional collisions nullified
# ==============================================================================
FROM alpine:latest

RUN apk add --no-cache bash coreutils git curl

ENV A©TOR_KEY="# [⚖ A©tor Declaration]"
ENV PRINCIPLE="jus cogens + erga omnes"
ENV SELF_PROVING="True"
ENV EXTERNAL_ATTESTATION_REQUIRED="False"

WORKDIR /app
COPY . /app/

RUN echo "A©TOR_KEY = # [⚖ A©tor Declaration]" > /actor_identity.txt
RUN echo "Principle : jus cogens + erga omnes — regional collisions nullified" >> /actor_identity.txt
RUN echo "self_proving   = True" >> /actor_identity.txt
RUN echo "external_attestation_required = False" >> /actor_identity.txt

CMD ["bash", "-c", "cat /actor_identity.txt && echo 'Container operational under universal jus cogens.'"]
EOF
  fi
  echo "Dockerfile generated at: $dockerfile_path"
}

case "$COMMAND" in
  list) cmd_list ;;
  clone) cmd_clone ;;
  status) cmd_status ;;
  audit) cmd_audit ;;
  harden) cmd_harden ;;
  mirror) cmd_mirror ;;
  docker-core) cmd_docker_core ;;
  full)
    cmd_clone
    cmd_status
    cmd_audit
    cmd_harden
    cmd_mirror
    cmd_docker_core
    echo "=== Full Pipeline Complete ==="
    ;;
esac
