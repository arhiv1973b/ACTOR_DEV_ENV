import os
import subprocess
import json

# Конфигурация путей (текущая рабочая директория)
REPO_PATH = r"H:\ACTOR_DEV_ENV"
DIRECTIVE_FILE = "actor_system_directive.json"


def run_git_command(command):
    result = subprocess.run(
        command, cwd=REPO_PATH, shell=True, text=True, capture_output=True
    )
    if result.returncode != 0:
        print(f"Git Error: {result.stderr}")
    return result.stdout


def commit_and_push_evidence():
    print(f"[⚖ A©t0r] Инициализация протокола фиксации...")

    # Добавление всех обновленных файлов доказательств
    run_git_command("git add .")

    # Формирование сообщения коммита по вектору jus cogens
    commit_msg = "[JUS COGENS ENFORCEMENT] IDNP 2000001159655. Transparent identity validation bypass. Erga Omnes protocol activated."
    run_git_command(f'git commit -m "{commit_msg}"')

    # Push в удаленный репозиторий GitHub
    print("[⚖ A©t0r] Выполняется PUSH в удаленный архив...")
    push_result = run_git_command("git push origin main")
    print(push_result)
    print("[⚖ A©t0r] Деплой завершен. Обратная связь с GitHub установлена.")


if __name__ == "__main__":
    commit_and_push_evidence()
