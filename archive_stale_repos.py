import subprocess

stale_repos = [
    "arhiv1973b/NewRepo",
    "arhiv1973b/NewRepo2",
    "arhiv1973b/tesr2983",
    "arhiv1973b/Iphone",
    "arhiv1973b/scaling-octo-potato",
    "arhiv1973b/pdf-gui",
    "arhiv1973b/Visual-Studio-2022",
    "arhiv1973b/desktop-tutorial",
    "arhiv1973b/.aws",
    "arhiv1973b/https-github.com-alexeimacheret-alexeimacheret",
    "arhiv1973b/friendly-giggle"
]

def archive_repos():
    print("[⚖ A©t0r] Инициализация массовой санитарной архивации тестовых репозиториев...")
    for repo in stale_repos:
        print(f"-> Архивирование {repo}...")
        cmd = f"gh repo archive {repo} --confirm"
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        if result.returncode == 0:
            print(f"[OK] Репозиторий {repo} успешно архивирован (Read-Only).")
        else:
            print(f"[WARN] Не удалось архивировать {repo}: {result.stderr.strip()}")

if __name__ == "__main__":
    archive_repos()
