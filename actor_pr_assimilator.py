import os
import subprocess
import json

REPO_PATH = r"H:\ACTOR_DEV_ENV"
REPOS = ["arhiv1973b/ACTOR_DEV_ENV", "arhiv1973b/apostille-mirror"]

def run_cmd(cmd, cwd=REPO_PATH):
    result = subprocess.run(cmd, cwd=cwd, shell=True, text=True, capture_output=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def assimilate_prs():
    for repo_name in REPOS:
        print(f"[⚖ A©t0r] Инициализация безопасного извлечения PR из {repo_name}...")
        stdout, stderr, code = run_cmd(f"gh pr list --repo {repo_name} --json number,title")
        if code != 0:
            print(f"[WARN] Не удалось получить список PR для {repo_name}: {stderr}")
            continue
        
        try:
            prs = json.loads(stdout)
        except Exception as e:
            print(f"[ERR] Ошибка парсинга JSON списка PR для {repo_name}: {e}")
            continue
        
        if not prs:
            print(f"[OK] Открытых PR для {repo_name} не обнаружено.")
            continue
        
        for pr in prs:
            num = pr["number"]
            title = pr["title"]
            audit_branch = f"audit/{repo_name.split('/')[1]}-pr-{num}"
            print(f"-> Изоляция PR #{num} ('{title}') в карантинную ветку: {audit_branch}")
            
            _, stderr_fetch, code_fetch = run_cmd(f"git fetch origin pull/{num}/head:{audit_branch}")
            if code_fetch != 0:
                print(f"[WARN] Ошибка fetch PR #{num} для {repo_name}: {stderr_fetch}")
            else:
                print(f"[OK] PR #{num} успешно изолирован в ветку {audit_branch}")

if __name__ == "__main__":
    assimilate_prs()
