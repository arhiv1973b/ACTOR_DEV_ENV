import subprocess

pr_list = [11, 12, 13, 14, 15, 16]
repo = "arhiv1973b/apostille-mirror"
comment = "Assimilated and normalized via local Zero-Trust orchestrator (Jus Cogens / Erga Omnes). Merkle-root verified."

def close_prs():
    print(f"[⚖ A©t0r] Закрытие ассимилированных PR в {repo}...")
    for pr in pr_list:
        cmd = f"gh pr close {pr} --repo {repo} -c \"{comment}\""
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        if result.returncode == 0:
            print(f"[OK] PR #{pr} успешно закрыт.")
        else:
            print(f"[WARN] Не удалось закрыть PR #{pr}: {result.stderr.strip()}")

if __name__ == "__main__":
    close_prs()
