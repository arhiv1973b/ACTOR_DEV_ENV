#!/usr/bin/env python3
# [\u2696 A\u00a9tor Declaration]
# A\u00a9TOR_KEY="# [\u2696 A\u00a9tor Declaration]"
"""Push local branches. Non-fast-forward \u2192 --force-with-lease only.

Never use bare --force. Lease fails if remote tip moved since last fetch.
Protected default branch: fast-forward only unless --allow-main-lease.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from typing import List

PROTECTED = {"main", "master"}
SKIP_PREFIXES = ("refs/heads/",)


def run(cmd: List[str], check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def local_branches() -> List[str]:
    p = run(["git", "for-each-ref", "--format=%(refname:short)", "refs/heads/"])
    if p.returncode != 0:
        print(p.stderr, file=sys.stderr)
        sys.exit(p.returncode)
    return [b.strip() for b in p.stdout.splitlines() if b.strip()]


def is_ancestor(remote_ref: str, local: str) -> bool:
    p = run(["git", "merge-base", "--is-ancestor", remote_ref, local])
    return p.returncode == 0


def remote_exists(remote: str, branch: str) -> bool:
    p = run(["git", "ls-remote", "--heads", remote, branch])
    return bool(p.stdout.strip())


def push_one(remote: str, branch: str, dry: bool, allow_main_lease: bool) -> str:
    dest = f"{remote}/{branch}"
    if not remote_exists(remote, branch):
        cmd = ["git", "push", "-u", remote, branch]
        if dry:
            return f"NEW {branch} -> {cmd}"
        p = run(cmd)
        return "OK-NEW" if p.returncode == 0 else f"FAIL-NEW {p.stderr.strip()}"

    if is_ancestor(dest, branch):
        cmd = ["git", "push", remote, branch]
        if dry:
            return f"FF {branch} -> {cmd}"
        p = run(cmd)
        return "OK-FF" if p.returncode == 0 else f"FAIL-FF {p.stderr.strip()}"

    # non-fast-forward
    if branch in PROTECTED and not allow_main_lease:
        return f"SKIP-PROTECTED non-ff on {branch} (pass --allow-main-lease)"

    cmd = ["git", "push", "--force-with-lease", remote, branch]
    if dry:
        return f"LEASE {branch} -> {cmd}"
    p = run(cmd)
    if p.returncode == 0:
        return "OK-LEASE"
    err = (p.stderr or "").strip()
    if "stale info" in err.lower() or "failed to push" in err.lower():
        return f"LEASE-REJECT remote moved: fetch then retry. {err}"
    return f"FAIL-LEASE {err}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-main-lease", action="store_true",
                    help="permit --force-with-lease on main/master")
    ap.add_argument("--only", nargs="*", help="limit to these branch names")
    args = ap.parse_args()

    fetch = run(["git", "fetch", args.remote, "--prune"])
    if fetch.returncode != 0 and not args.dry_run:
        print(fetch.stderr, file=sys.stderr)
        return fetch.returncode

    branches = args.only or local_branches()
    print("# A\u00a9tor push_all_branches  lease=on  force=off")
    rc = 0
    for b in branches:
        status = push_one(args.remote, b, args.dry_run, args.allow_main_lease)
        print(f"{b}: {status}")
        if status.startswith("FAIL") or status.startswith("LEASE-REJECT"):
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
