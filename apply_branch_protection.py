import json
import subprocess

payload = {
    "required_status_checks": None,
    "enforce_admins": True,
    "required_pull_request_reviews": {
        "required_approving_review_count": 0
    },
    "restrictions": None,
    "allow_force_pushes": False,
    "allow_deletions": False
}

repos = ["arhiv1973b/ACTOR_DEV_ENV", "arhiv1973b/apostille-mirror"]

for repo in repos:
    print(f"[⚖ A©t0r] Применение branch protection для {repo}...")
    cmd = f"gh api -X PUT repos/{repo}/branches/main/protection --input - -H \"Accept: application/vnd.github+json\""
    result = subprocess.run(cmd, input=json.dumps(payload), text=True, shell=True, capture_output=True)
    if result.returncode == 0:
        print(f"[OK] Защита ветки main успешно применена для {repo}.")
    else:
        print(f"[WARN] Ошибка применения защиты для {repo}: {result.stderr}")
