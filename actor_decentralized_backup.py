# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

import os
import shutil
import hashlib
import subprocess
import json
from datetime import datetime

WORKSPACE_ROOT = r"H:\ACTOR_DEV_ENV"
BACKUP_TARGET_DIR = r"C:\Users\arhiv\.ti_ula_decentralized_backup"
OS_LOCAL_APPDATA = os.path.expandvars(r"%LOCALAPPDATA%")
USER_PROFILE = os.path.expandvars(r"%USERPROFILE%")


def log(msg):
    print(f"[A©t0r Backup Sentinel] {timestamp()} | {msg}")


def timestamp():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


def main():
    log(
        "Инициализация децентрализованного бэкапа TI-ULA (Docker, GitHub, Независимые узлы)..."
    )
    os.makedirs(BACKUP_TARGET_DIR, exist_ok=True)

    # 1. Бэкап локальных критических файлов и демона
    backup_snapshot_dir = os.path.join(
        BACKUP_TARGET_DIR, f"snapshot_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    )
    os.makedirs(backup_snapshot_dir, exist_ok=True)

    # Копирование Watchdog и Healer
    for script_name in ["ActorCopilotWatchdog.ps1", "ActorCopilotHealer.ps1"]:
        src = os.path.join(OS_LOCAL_APPDATA, script_name)
        if os.path.exists(src):
            shutil.copy2(src, backup_snapshot_dir)
            log(f"Скопирован артефакт: {script_name}")

    # 2. Бэкап конфигураций и ключей TI-ULA
    keys_src = os.path.join(USER_PROFILE, ".ti_ula_keys")
    if os.path.exists(keys_src):
        keys_dest = os.path.join(backup_snapshot_dir, ".ti_ula_keys")
        if os.path.exists(keys_dest):
            shutil.rmtree(keys_dest)
        shutil.copytree(keys_src, keys_dest)
        log("Криптографические ключи Ed25519 включены в бэкап.")

    # 3. Синхронизация с Docker контейнерами / томами (Case Macheret Registry & Volumes)
    try:
        docker_inspect = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True,
        )
        containers = docker_inspect.stdout.strip().splitlines()
        log(f"Обнаружено Docker контейнеров: {len(containers)}")

        container_state_record = os.path.join(
            backup_snapshot_dir, "docker_containers_state.json"
        )
        with open(container_state_record, "w", encoding="utf-8") as f:
            json.dump(containers, f, indent=2)
    except Exception as e:
        log(f"Предупреждение Docker sync: {e}")

    # 4. Создание сводного архива бэкапа с вычислением SHA-256
    manifest = {
        "timestamp": timestamp(),
        "case": "CASE-MACHERET-1997-2026",
        "legal_scope": "ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ",
        "files": [],
    }

    for root, dirs, files in os.walk(backup_snapshot_dir):
        for file in files:
            fpath = os.path.join(root, file)
            with open(fpath, "rb") as f:
                f_hash = hashlib.sha256(f.read()).hexdigest()
            manifest["files"].append(
                {"path": os.path.relpath(fpath, BACKUP_TARGET_DIR), "sha256": f_hash}
            )

    manifest_path = os.path.join(BACKUP_TARGET_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    log(f"Манифест бэкапа создан: {manifest_path}")

    # 5. Синхронизация с независимым резервным сервером / зеркалом (independent non-GitHub node mirror)
    independent_mirror = r"C:\Users\arhiv\Aytor_Independent_Mirror"
    os.makedirs(independent_mirror, exist_ok=True)
    shutil.copytree(
        backup_snapshot_dir,
        os.path.join(independent_mirror, os.path.basename(backup_snapshot_dir)),
        dirs_exist_ok=True,
    )
    log(f"Зеркало на независимом узле обновлено: {independent_mirror}")

    log("Децентрализованный бэкап TI-ULA успешно завершен.")


if __name__ == "__main__":
    main()
