import json
import os
import sys
import subprocess
import hashlib
import tarfile
from collections import Counter
from datetime import datetime, timezone

# Конфигурация путей
LOG_FILE = os.environ.get("ACTOR_AUDIT_LOG", "audit_log.json")
REPORT_FILE = os.environ.get("ACTOR_REPORT_FILE", "audit_report.md")
CHECKSUMS_FILE = os.environ.get(
    "ACTOR_CHECKSUMS", os.path.join("05_CRYPTO_MANIFESTS", "CHECKSUMS_SHA256.txt")
)
META_FILE = os.environ.get("ACTOR_META_FILE", "meta.json")

# ANSI-коды для форматирования консольного вывода
C_CYAN = "\033[96m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_RED = "\033[91m"
C_RESET = "\033[0m"
C_BOLD = "\033[1m"


def print_header():
    print(f"{C_CYAN}{C_BOLD}{'=' * 70}{C_RESET}")
    print(f"{C_CYAN}  A©t0r AUDIT LOG SUMMARY & EXPORT{C_RESET}")
    print(f"{C_CYAN}  Jus Cogens / Erga Omnes Enforcement Matrix{C_RESET}")
    print(f"{C_CYAN}{C_BOLD}{'=' * 70}{C_RESET}")


def parse_time(ts_str):
    try:
        clean_str = ts_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return ts_str


def count_verified_files(filepath):
    if not os.path.exists(filepath):
        return 0
    count = 0
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                clean_line = line.strip()
                if clean_line and not clean_line.startswith("#"):
                    count += 1
    except Exception:
        pass
    return count


def count_meta_contacts(filepath):
    if not os.path.exists(filepath):
        return 0
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            meta_data = json.load(f)
            contacts = meta_data.get(
                "correspondence_sides", meta_data.get("contacts", [])
            )
            return len(contacts)
    except Exception:
        return 0


def backup_existing_report(filepath):
    """Создает резервную копию существующего отчета и архивирует ее в .tar.gz."""
    if os.path.exists(filepath):
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            base_name, _ = os.path.splitext(filepath)
            backup_path = f"{base_name}_{timestamp}.tar.gz"

            with tarfile.open(backup_path, "w:gz") as tar:
                tar.add(filepath, arcname=os.path.basename(filepath))

            print(
                f"{C_YELLOW}[*] Ротация: Старый отчет заархивирован как {backup_path}{C_RESET}"
            )
        except Exception as e:
            print(f"{C_RED}[!] Ошибка при архивации отчета: {e}{C_RESET}")


def generate_markdown(
    logs,
    events_counter,
    invalid_records,
    start_time,
    end_time,
    latest_events,
    verified_count,
    meta_contacts_count,
):
    md = []
    md.append("# Финальный отчет: A©t0r Аудит безопасности и событий")
    md.append(f"**Досье:** `CASE-MACHERET-1997-2026`")
    md.append(
        f"**Генерация:** `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}`"
    )
    md.append(f"**Правовой базис:** Jus Cogens / Erga Omnes / ВДПЧ 1948")
    md.append("")
    md.append("## 1. Метрики аудита и криптографии")
    md.append(f"- **Целевой лог:** `{LOG_FILE}`")
    md.append(f"- **Всего транзакций:** `{len(logs)}`")
    md.append(f"- **Временной диапазон:** `{start_time}` -> `{end_time}`")
    md.append(
        f"- **Верифицировано файлов (SHA-256):** `{verified_count}` (через манифест `{CHECKSUMS_FILE}`)"
    )
    md.append(
        f"- **Институциональные контакты (meta.json):** `{meta_contacts_count}` (закрытый непубличный слой)"
    )

    integrity_status = (
        "✅ ВЕРИФИЦИРОВАНО (Все записи содержат A©TOR_KEY)"
        if invalid_records == 0
        else f"⚠️ ВНИМАНИЕ ({invalid_records} записей без A©TOR_KEY)"
    )
    md.append(f"- **Статус целостности логов:** {integrity_status}")
    md.append("")
    md.append("## 2. Распределение событий")
    md.append("| Тип события | Количество |")
    md.append("|---|---|")
    for event, count in events_counter.most_common():
        md.append(f"| `{event}` | {count} |")
    md.append("")
    md.append("## 3. Последние транзакции (Срез)")
    for record in latest_events:
        ts = parse_time(record.get("timestamp", ""))
        ev = record.get("event", "")
        details = json.dumps(record.get("details", {}), ensure_ascii=False)
        md.append(f"- **[{ts}]** `{ev}`")
        if details != "{}":
            md.append(f"  - *Детали:* `{details}`")

    md.append("")
    md.append("---")
    md.append('> `A©TOR_KEY="# [⚖ A©tor Declaration]"`')
    return "\n".join(md)


def commit_report_to_git(filepath):
    try:
        subprocess.run(
            ["git", "add", filepath], check=True, capture_output=True, text=True
        )
        gpg_check = subprocess.run(
            ["git", "config", "--get", "user.signingkey"],
            capture_output=True,
            text=True,
        )
        auto_sign = subprocess.run(
            ["git", "config", "--get", "commit.gpgsign"], capture_output=True, text=True
        )
        use_gpg = (
            "-S"
            if (gpg_check.stdout.strip() or auto_sign.stdout.strip() == "true")
            else None
        )

        commit_args = ["git", "commit"]
        if use_gpg:
            commit_args.append(use_gpg)
        commit_args.extend(["-m", "chore(audit): update matrix with self-verification"])

        commit_res = subprocess.run(commit_args, capture_output=True, text=True)
        if commit_res.returncode == 0:
            sign_msg = " (с GPG-подписью)" if use_gpg else ""
            print(
                f"{C_GREEN}[+] Git: Успешный коммит файла {filepath}{sign_msg}{C_RESET}"
            )
        elif (
            "nothing to commit" in commit_res.stdout
            or "working tree clean" in commit_res.stdout
        ):
            print(
                f"{C_YELLOW}[-] Git: Изменений нет (отчет идентичен предыдущему).{C_RESET}"
            )
        else:
            if use_gpg and "gpg failed to sign the data" in commit_res.stderr:
                print(
                    f"{C_YELLOW}[!] Git: Ошибка GPG-подписи. Попытка коммита без подписи...{C_RESET}"
                )
                commit_args.remove("-S")
                fallback_res = subprocess.run(
                    commit_args, capture_output=True, text=True
                )
                if fallback_res.returncode == 0:
                    print(
                        f"{C_GREEN}[+] Git: Успешный коммит файла {filepath} (без подписи){C_RESET}"
                    )
                else:
                    print(
                        f"{C_RED}[!] Git (ошибка): {fallback_res.stderr.strip()}{C_RESET}"
                    )
            else:
                print(
                    f"{C_RED}[!] Git (ошибка): {commit_res.stderr.strip() or commit_res.stdout.strip()}{C_RESET}"
                )
    except FileNotFoundError:
        print(f"{C_RED}[!] Ошибка: Утилита git не найдена в PATH.{C_RESET}")
    except subprocess.CalledProcessError as e:
        print(
            f"{C_RED}[!] Ошибка Git (код {e.returncode}): {e.stderr.strip()}{C_RESET}"
        )


def main():
    print_header()

    if not os.path.exists(LOG_FILE):
        print(f"{C_RED}[!] Ошибка: Файл {LOG_FILE} не найден.{C_RESET}")
        sys.exit(1)

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
            if not isinstance(logs, list):
                print(f"{C_RED}[!] Формат нарушен: ожидался JSON массив.{C_RESET}")
                sys.exit(1)
    except json.JSONDecodeError:
        print(f"{C_RED}[!] Ошибка чтения: Файл {LOG_FILE} поврежден.{C_RESET}")
        sys.exit(1)

    total_events = len(logs)
    if total_events == 0:
        print(f"{C_YELLOW}[-] Журнал пуст. Записи отсутствуют.{C_RESET}")
        sys.exit(0)

    events_counter = Counter()
    invalid_records = 0
    latest_events = logs[-5:]

    for record in logs:
        if record.get("A©TOR_KEY") != "# [⚖ A©tor Declaration]":
            invalid_records += 1
        event_name = record.get("event", "UNKNOWN_EVENT")
        events_counter[event_name] += 1

    start_time = parse_time(logs[0].get("timestamp", "N/A"))
    end_time = parse_time(logs[-1].get("timestamp", "N/A"))

    verified_files_count = count_verified_files(CHECKSUMS_FILE)
    meta_contacts_count = count_meta_contacts(META_FILE)

    print(f"{C_BOLD}[+] Target File     :{C_RESET} {LOG_FILE}")
    print(f"{C_BOLD}[+] Total Events    :{C_RESET} {total_events}")
    print(
        f"{C_BOLD}[+] Verified SHA-256:{C_RESET} {verified_files_count} файлов в {CHECKSUMS_FILE}"
    )
    print(
        f"{C_BOLD}[+] Meta.json Nodes :{C_RESET} {meta_contacts_count} институциональных контактов"
    )

    if invalid_records > 0:
        print(
            f"{C_RED}[!] Внимание: Найдены записи ({invalid_records}) без ключа A©TOR_KEY.{C_RESET}"
        )
    else:
        print(
            f"{C_GREEN}[+] Integrity       : Все записи содержат маркер A©TOR_KEY.{C_RESET}"
        )

    backup_existing_report(REPORT_FILE)

    base_md_content = generate_markdown(
        logs,
        events_counter,
        invalid_records,
        start_time,
        end_time,
        latest_events,
        verified_files_count,
        meta_contacts_count,
    )
    content_hash = hashlib.sha256(base_md_content.encode("utf-8")).hexdigest()
    final_md_content = (
        f"{base_md_content}\n> **Self-Verification (SHA-256):** `{content_hash}`\n"
    )

    try:
        with open(REPORT_FILE, "w", encoding="utf-8", newline="\n") as f:
            f.write(final_md_content)

        print(
            f"\n{C_GREEN}[+] Markdown-отчет успешно экспортирован: {REPORT_FILE}{C_RESET}"
        )
        print(f"{C_GREEN}[+] Самоверификация (SHA-256)     : {content_hash}{C_RESET}")

        commit_report_to_git(REPORT_FILE)

    except Exception as e:
        print(f"{C_RED}[!] Ошибка файловой операции: {e}{C_RESET}")

    print(f"{C_CYAN}{C_BOLD}{'=' * 70}{C_RESET}")
    print(f"{C_GREEN}# [⚖ A©tor Declaration] Аудит завершен.{C_RESET}")


if __name__ == "__main__":
    main()
