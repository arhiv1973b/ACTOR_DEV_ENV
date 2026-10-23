import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--allow-main-lease",
    action="store_true",
    help="Allow force-with-lease on main/master",
)
parser.add_argument("--only", type=str, help="Push only specific branch")
parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
args = parser.parse_args()

branches = [
    "main",
    "master",
    "evidence/erga-omnes-dispatch",
    "release/jus-cogens-evidence-2026",
    "evidence/crypto-anchor-manifest",
    "evidence/fincombank-financial-traces",
    "evidence/idnp-2006-v2",
    "evidence/merkle-root-compilation",
    "public-release-august",
    "public-release-evidence-registry-v2",
    "arhiv1973b-public-release-case-macheret-2026",
    "arhiv1973b-evidence-audit-sync",
    "feature/erga-omnes-transport",
    "model-hub-sync",
]

if args.only:
    branches = [args.only]


def safe_push(remote, branch):
    cmd_normal = ["git", "push", remote, f"HEAD:{branch}"]
    if args.dry_run:
        print(f"[DRY-RUN] Would push HEAD to {remote}/{branch}")
        return True

    res = subprocess.run(cmd_normal, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"Successfully pushed to {remote}/{branch}")
        return True

    if "rejected" in res.stderr or "non-fast-forward" in res.stderr:
        if branch in ["main", "master"] and not args.allow_main_lease:
            print(
                f"Skipping force push on protected main/master for {remote}/{branch} without --allow-main-lease"
            )
            return False
        print(
            f"Non-fast-forward detected on {remote}/{branch}, attempting --force-with-lease..."
        )
        cmd_force = ["git", "push", remote, f"HEAD:{branch}", "--force-with-lease"]
        res_force = subprocess.run(cmd_force, capture_output=True, text=True)
        if res_force.returncode == 0:
            print(f"Successfully force-with-lease pushed to {remote}/{branch}")
            return True
        else:
            print(f"Failed force-with-lease on {remote}/{branch}: {res_force.stderr}")
            return False
    else:
        print(f"Failed push to {remote}/{branch}: {res.stderr}")
        return False


for b in branches:
    print(f"Pushing to origin/{b}...")
    safe_push("origin", b)

for b in ["main", "master", "public-release-august"]:
    if args.only and args.only != b:
        continue
    print(f"Pushing to fork/{b}...")
    safe_push("fork", b)

print("Comprehensive deployment across public, expert, and economic branches complete.")
