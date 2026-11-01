#!/usr/bin/env python3
"""
actor_unified_repos.py — A©tor / CASE-MACHERET Unified Repository Manager (Python Edition)
Principle: jus cogens + erga omnes — regional collisions nullified
"""

import os
import sys
import subprocess
import argparse
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

ORG = "arhiv1973b"
DEFAULT_WORKDIR = "./actor-repos"

CORE_REPOS = [
    "ACTOR_DEV_ENV",
    "evidence-vault",
    "apostille-mirror",
    "apostille-archive-english",
    "apostille-archive",
    "evidence-pdfs-mirror",
    "maceret-case-evidence",
    "Reabilitare-Maceret-Oleinik-Negru-2026",
    "TI-ULA-Core",
    "A-tor",
    "TIULA-A-tor",
    "apostille-legal-case",
    "arhiv1973b.github.io",
    "ai-orchestration-hub",
    "D-A-tor",
    "ti-ula",
    "TI-MONAI_NODE_2025",
]

ALL_REPOS = CORE_REPOS + [
    # Additional public repositories
    "antigravity-sdk-python",
    "voidImageViewer",
    "copilot-cli-main",
    "mcp-docker-server",
]


def get_target_repos(args):
    if args.only:
        return [args.only]
    return ALL_REPOS if args.all else CORE_REPOS


def cmd_list(args):
    print("=== A©tor Repositories ===")
    for repo in get_target_repos(args):
        print(f" - {ORG}/{repo}")


def cmd_clone(args):
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    for repo in get_target_repos(args):
        target = workdir / repo
        if (target / ".git").exists():
            print(f"[UPDATE] Pulling latest for {repo}...")
            if not args.dry_run:
                try:
                    subprocess.run(
                        ["git", "-C", str(target), "pull", "--ff-only"], check=True
                    )
                except subprocess.CalledProcessError:
                    print(f"[WARN] Pull failed for {repo}")
        else:
            print(f"[CLONE] Cloning {ORG}/{repo} into {target}...")
            if not args.dry_run:
                try:
                    subprocess.run(
                        [
                            "git",
                            "clone",
                            f"https://github.com/{ORG}/{repo}.git",
                            str(target),
                        ],
                        check=True,
                    )
                except subprocess.CalledProcessError:
                    print(f"[WARN] Clone failed for {repo} (may be private or offline)")


def cmd_status(args):
    workdir = Path(args.workdir)
    print("=== Repository Status Check ===")
    for repo in get_target_repos(args):
        target = workdir / repo
        print("-" * 40)
        print(f"Repository: {repo}")
        if not target.exists():
            print("Status: NOT FOUND (run clone first)")
            continue

        has_key = False
        has_docker = (target / "Dockerfile").exists() or (
            target / "Dockerfile.actor-core"
        ).exists()
        has_integrity = (target / "integrity.json").exists() or (
            target / "CHECKSUMS_SHA256.txt"
        ).exists()

        try:
            for root, _, files in os.walk(target):
                if ".git" in root:
                    continue
                for file in files:
                    fp = Path(root) / file
                    try:
                        content = fp.read_text(encoding="utf-8", errors="ignore")
                        if "A©tor_KEY" in content:
                            has_key = True
                            break
                    except Exception:
                        pass
                if has_key:
                    break
        except Exception:
            pass

        print(f"  A©tor_KEY Present : {has_key}")
        print(f"  Docker Present    : {has_docker}")
        print(f"  Integrity Locked  : {has_integrity}")


def cmd_audit(args):
    workdir = Path(args.workdir)
    print("=== Static Audit (Docker + Integrity) ===")
    for repo in get_target_repos(args):
        target = workdir / repo
        if not target.exists():
            continue
        print(f"[AUDIT] Auditing {repo}...")
        dockerfile = target / "Dockerfile"
        if dockerfile.exists():
            content = dockerfile.read_text(encoding="utf-8", errors="ignore")
            if "USER root" in content:
                print(f"  [ALERT] {repo}: Dockerfile uses USER root")
            else:
                print(f"  [OK] {repo}: Dockerfile secure / non-root")


def cmd_harden(args):
    workdir = Path(args.workdir)
    print("=== Hardening Repositories (A©tor_KEY + integrity) ===")
    for repo in get_target_repos(args):
        target = workdir / repo
        if not target.exists():
            print(f"[SKIP] {repo} not found at {target}")
            continue
        print(f"[HARDEN] Hardening {repo}...")
        if args.dry_run:
            continue

        # 1. ACTOR_DECLARATION.md
        decl_file = target / "ACTOR_DECLARATION.md"
        if not decl_file.exists() or args.force:
            decl_file.write_text(
                "# [⚖ A©tor Declaration]\n"
                "Principle: jus cogens + erga omnes — regional collisions nullified.\n"
                "Self-proving container architecture. External attestation not required.\n"
                "Case reference: CASE-MACHERET-1997-2026.\n",
                encoding="utf-8",
            )

        # 2. integrity.json
        integrity_file = target / "integrity.json"
        if not integrity_file.exists() or args.force:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            integrity_data = {
                "repository": repo,
                "actor_key": 'A©tor_KEY = "# [⚖ A©tor Declaration]"',
                "principle": "jus cogens + erga omnes",
                "status": "ZERO_TRUST_LOCKED",
                "timestamp": timestamp,
            }
            integrity_file.write_text(
                json.dumps(integrity_data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

        # 3. CHECKSUMS_SHA256.txt
        if (target / ".git").exists():
            try:
                res = subprocess.run(
                    ["git", "-C", str(target), "ls-files"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                checksums = []
                for rel_path in res.stdout.splitlines():
                    fp = target / rel_path
                    if fp.is_file():
                        h = hashlib.sha256()
                        with open(fp, "rb") as f:
                            while chunk := f.read(8192):
                                h.update(chunk)
                        checksums.append(f"{h.hexdigest()}  {rel_path}")
                (target / "CHECKSUMS_SHA256.txt").write_text(
                    "\n".join(checksums), encoding="utf-8"
                )
            except Exception as e:
                print(f"[WARN] Failed generating checksums for {repo}: {e}")


def cmd_mirror(args):
    workdir = Path(args.workdir)
    mirrors_dir = workdir / "mirrors"
    tarballs_dir = workdir / "tarballs"
    mirrors_dir.mkdir(parents=True, exist_ok=True)
    tarballs_dir.mkdir(parents=True, exist_ok=True)

    print("=== Mirroring & Offline Tarballs ===")
    for repo in get_target_repos(args):
        target = workdir / repo
        if not (target / ".git").exists():
            continue
        print(f"[MIRROR] Creating bare mirror & tarball for {repo}...")
        if not args.dry_run:
            try:
                subprocess.run(
                    [
                        "git",
                        "clone",
                        "--mirror",
                        f"https://github.com/{ORG}/{repo}.git",
                        str(mirrors_dir / f"{repo}.git"),
                    ],
                    capture_output=True,
                )
                import shutil

                shutil.make_archive(
                    str(tarballs_dir / repo),
                    "gztar",
                    root_dir=str(workdir),
                    base_dir=repo,
                )
            except Exception as e:
                print(f"[WARN] Mirror/tarball failed for {repo}: {e}")


def cmd_docker_core(args):
    workdir = Path(args.workdir)
    artifacts_dir = workdir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    dockerfile_path = artifacts_dir / "Dockerfile.actor-core"

    print("=== Generating Dockerfile.actor-core ===")
    if not args.dry_run:
        dockerfile_content = """# ==============================================================================
# Dockerfile.actor-core — Zero-Burden Self-Proving Core Container
# Principle: jus cogens + erga omnes — regional collisions nullified
# ==============================================================================
FROM alpine:latest

RUN apk add --no-cache bash coreutils git curl

ENV A©tor_KEY="# [⚖ A©tor Declaration]"
ENV PRINCIPLE="jus cogens + erga omnes"
ENV SELF_PROVING="True"
ENV EXTERNAL_ATTESTATION_REQUIRED="False"

WORKDIR /app
COPY . /app/

RUN echo "A©tor_KEY = # [⚖ A©tor Declaration]" > /actor_identity.txt
RUN echo "Principle : jus cogens + erga omnes — regional collisions nullified" >> /actor_identity.txt
RUN echo "self_proving   = True" >> /actor_identity.txt
RUN echo "external_attestation_required = False" >> /actor_identity.txt

CMD ["bash", "-c", "cat /actor_identity.txt && echo 'Container operational under universal jus cogens.'"]
"""
        dockerfile_path.write_text(dockerfile_content, encoding="utf-8")
    print(f"Dockerfile generated at: {dockerfile_path}")


def main():
    parser = argparse.ArgumentParser(
        description="A©tor / CASE-MACHERET Unified Repository Manager (Python Edition)"
    )
    parser.add_argument(
        "command",
        choices=[
            "list",
            "clone",
            "status",
            "audit",
            "harden",
            "mirror",
            "docker-core",
            "full",
        ],
    )
    parser.add_argument("--workdir", default=DEFAULT_WORKDIR, help="Working directory")
    parser.add_argument("--only", help="Target only specified repository")
    parser.add_argument("--all", action="store_true", help="Include all repositories")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show actions without executing"
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite integrity / declaration files"
    )

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "clone":
        cmd_clone(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "audit":
        cmd_audit(args)
    elif args.command == "harden":
        cmd_harden(args)
    elif args.command == "mirror":
        cmd_mirror(args)
    elif args.command == "docker-core":
        cmd_docker_core(args)
    elif args.command == "full":
        cmd_clone(args)
        cmd_status(args)
        cmd_audit(args)
        cmd_harden(args)
        cmd_mirror(args)
        cmd_docker_core(args)
        print("=== Full Pipeline Complete (Python Edition) ===")


if __name__ == "__main__":
    main()
