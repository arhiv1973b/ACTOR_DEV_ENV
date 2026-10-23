import os
import subprocess
import glob

NODES_DIR = r"F:\Мой диск\ACTOR_DEV_ENV\nodes"
REPO_DIR = r"H:\ACTOR_DEV_ENV\apostille-mirror"
NODES_REPO_DIR = os.path.join(REPO_DIR, "nodes")

def git_deploy():
    os.chdir(REPO_DIR)
    
    branch_name = "feature/evidence-deploy"
    print(f"[GIT] Подготовка ветки {branch_name}...")
    subprocess.run(["git", "checkout", "-b", branch_name], stderr=subprocess.DEVNULL)
    subprocess.run(["git", "checkout", branch_name], check=True)

    # Инициализация LFS
    subprocess.run(["git", "lfs", "install"], check=False)
    subprocess.run(["git", "lfs", "track", "*.zip"], check=False)
    subprocess.run(["git", "add", ".gitattributes"], check=False)
    subprocess.run(["git", "config", "http.postBuffer", "524288000"], check=False)

    # Получаем список файлов
    files = [f for f in os.listdir(NODES_DIR) if os.path.isfile(os.path.join(NODES_DIR, f))]
    
    # Разбиваем на батчи по 1000 файлов
    batch_size = 1000
    for i in range(0, len(files), batch_size):
        batch = files[i:i+batch_size]
        print(f"[GIT] Батч {i//batch_size + 1}: добавление {len(batch)} файлов...")
        
        for file in batch:
            src = os.path.join(NODES_DIR, file)
            dst = os.path.join(NODES_REPO_DIR, file)
            # Копируем файл
            import shutil
            if not os.path.exists(NODES_REPO_DIR):
                os.makedirs(NODES_REPO_DIR)
            shutil.copy2(src, dst)
            subprocess.run(["git", "add", os.path.join("nodes", file)], check=True)
            
        print(f"[GIT] Коммит батча {i//batch_size + 1}...")
        subprocess.run(["git", "commit", "-m", f"feat(evidence): batch {i//batch_size + 1}"], check=True)
        print(f"[GIT] Отправка батча {i//batch_size + 1}...")
        subprocess.run(["git", "push", "origin", branch_name], check=True)

    print("[GIT] Деплой успешно завершен!")

if __name__ == "__main__":
    git_deploy()
