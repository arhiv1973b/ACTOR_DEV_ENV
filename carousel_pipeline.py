import os
import json
import time
import hashlib
from collections import deque
from datetime import datetime
import shutil

# Импортируем наш верификатор
from transient_lifecycle_verifier import verify_single_apostille_pdf


class CarouselPipeline:
    def __init__(
        self,
        registry_records,
        workspace,
        download_delay=10,
        retry_delay=300,
    ):
        self.queue = deque(registry_records)
        self.workspace = workspace
        self.download_delay = download_delay
        self.retry_delay = retry_delay
        self.knowledge_dir = os.path.join(workspace, "knowledge")
        os.makedirs(self.knowledge_dir, exist_ok=True)
        # Инициализация структуры папок
        for folder in ["downloads", "texts", "logs", "reports", "knowledge"]:
            os.makedirs(os.path.join(self.workspace, folder), exist_ok=True)

        self.statistics = {
            "processed": 0,
            "success": 0,
            "failed": 0,
            "ocr_corrections": 0,
        }

    def run_forever(self):
        print(f"[*] Карусельный конвейер запущен. Очередь: {len(self.queue)} записей.")
        while True:
            if not self.queue:
                print("[*] Очередь пуста. Ожидание 60 сек.")
                time.sleep(60)
                continue

            record = self.queue.popleft()
            print(f"[*] Обработка записи: {record.get('apostille')}")

            try:
                self.process_record(record)
                self.statistics["success"] += 1
                print(f"[+] Успешно: {record.get('apostille')}")
            except Exception as exc:
                self.statistics["failed"] += 1
                print(f"[-] Ошибка: {exc}")
                self.log_error(record, str(exc))
                self.queue.append(record)
                time.sleep(self.retry_delay)
            finally:
                self.statistics["processed"] += 1
                time.sleep(self.download_delay)

    def process_record(self, record):
        # В реальной задаче здесь был бы сетевой запрос.
        # Предполагаем, что файл уже скачан в downloads/
        filename = record["apostille"] + ".pdf"
        pdf_path = os.path.join(self.workspace, "downloads", filename)

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Файл не найден: {pdf_path}")

        try:
            # Используем модуль верификации
            report = verify_single_apostille_pdf(pdf_path)
            self.store_report(record, report)
        finally:
            # Cleanup выполняется внутри verify_single_apostille_pdf,
            # но добавим страховку на случай исключений
            pass

    def log_error(self, record, error):
        log_file = os.path.join(self.workspace, "logs", "errors.jsonl")
        row = {
            "timestamp": datetime.utcnow().isoformat(),
            "apostille": record.get("apostille"),
            "error": error,
        }
        with open(log_file, "a", encoding="utf-8") as fp:
            fp.write(json.dumps(row, ensure_ascii=False) + "\n")

    def store_report(self, record, report):
        path = os.path.join(
            self.workspace, "reports", record["apostille"] + "_verification.json"
        )
        with open(path, "w", encoding="utf-8") as fp:
            json.dump(report, fp, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # Тестовая инициализация
    # Предполагаем наличие реестра apostille_registry_25.json
    with open("apostille_registry_25.json", "r", encoding="utf-8") as f:
        registry = json.load(f)

    # Для теста добавим файл в downloads
    # shutil.copy("recovered_evidence/3HWVD912FN7H4_EVIDENCE.pdf", "H:/ACTOR_DEV_ENV/downloads/3HWVD912FN7H4.pdf")

    formatted_registry = [{"apostille": r["apostille"]} for r in registry]

    pipeline = CarouselPipeline(formatted_registry, workspace="H:/ACTOR_DEV_ENV")
    print("[*] Конвейер готов к запуску.")
    # pipeline.run_forever()
