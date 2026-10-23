#!/usr/bin/env python3
r"""
MCP Drive Indexer & Local LLM Orchestrator (Extended with Lazy Hashing, Retry Policy & Multilingual Support)
Components:
1. Database & Queue Manager (SQLite + WAL, file_locks, statuses, mtime, lazy sha256)
2. Disk Scanner (I/O Worker with os.scandir, Lazy Hashing & Retry Policy for Google Drive F:\\)
3. Inference Orchestrator (Ollama API Client with keep_alive: 0 & semaphores)
4. Multi-threaded Worker Pool (ThreadPoolExecutor with get_classification_prompt & expanded critical_keywords)
5. MCP Tools Integration interface
"""

import os
import sys
import sqlite3
import hashlib
import requests
import json
import threading
import logging
import time
import re
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Generator, Optional, Tuple
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
    TimeoutError as FuturesTimeoutError,
)

# Ensure proper UTF-8 handling for standard output/logging on Windows / diacritics
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s"
)
logger = logging.getLogger("DriveIndexer")


def get_classification_prompt(path: str) -> Tuple[str, str, str]:
    r"""
    Эвристический детектор языка и генератор промпта на основе путей с диакритикой (RO, RU, EN).
    Проверяет наличие румынских диакритических знаков (ă, â, î, ș, ț) или специфических юридических маркеров.
    Возвращает кортеж: (language_code, light_prompt, heavy_prompt_template).
    """
    p_lower = str(path).lower()
    tokens = set(re.findall(r"[a-zа-яăâîșț0-9]+", p_lower))

    ro_diacritics = ["ă", "â", "î", "ș", "ț"]
    ro_keywords = {
        "hotărâre",
        "hotarare",
        "judecată",
        "judecata",
        "dosar",
        "cerere",
        "decizie",
        "procură",
        "procura",
        "rechizitoriu",
        "contract",
        "act",
    }
    ru_keywords = {"иск", "завещание", "акт", "справка", "договор", "суд", "дело"}

    is_romanian = any(c in p_lower for c in ro_diacritics) or bool(
        tokens.intersection(ro_keywords)
    )
    is_russian = bool(tokens.intersection(ru_keywords))

    if is_romanian:
        lang = "ro"
        light_prompt = (
            f"Clasificați tipul de fișier și categoria pe baza căii: {path}. "
            f"Returnați JSON cu cheile: category, confidence (float 0.0 la 1.0), summary_ro."
        )
        heavy_prompt_template = (
            f"Efectuați o analiză juridică și medico-legală profundă a artefactului cu calea: {path}. "
            f"Încrederea modelului ușor a fost {{confidence}} (sub pragul 0.6). "
            f"Dimensiune: {{size}} octeți, SHA-256: {{sha256}}. "
            f"Returnați JSON cu cheile: category, forensic_status, summary_ro, risk_level, confidence."
        )
    elif is_russian:
        lang = "ru"
        light_prompt = (
            f"Классифицируйте тип файла и категорию на основе пути: {path}. "
            f"Верните JSON с ключами: category, confidence (float от 0.0 до 1.0), summary_ru."
        )
        heavy_prompt_template = (
            f"Выполните глубокий судебно-правовой анализ артефакта по пути: {path}. "
            f"Уверенность легкой модели составила {{confidence}} (ниже порога 0.6). "
            f"Размер: {{size}} байт, SHA-256: {{sha256}}. "
            f"Верните JSON с ключами: category, forensic_status, summary_ru, risk_level, confidence."
        )
    else:
        lang = "en"
        light_prompt = (
            f"Classify file type and category based on path: {path}. "
            f"Return JSON with keys: category, confidence (float 0.0 to 1.0), summary."
        )
        heavy_prompt_template = (
            f"Perform deep forensic and legal analysis of artifact path: {path}. "
            f"Light model confidence was {{confidence}} (below threshold 0.6). "
            f"Size: {{size}} bytes, SHA-256: {{sha256}}. "
            f"Return JSON with keys: category, forensic_status, summary, risk_level, confidence."
        )

    return lang, light_prompt, heavy_prompt_template


class DatabaseManager:
    r"""Менеджер БД и очередей (SQLite + WAL) с поддержкой mtime, ленивого хэша и блокировок."""

    def __init__(self, db_path: str = "drive_index.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.lock, self.get_connection() as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")

            conn.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    size INTEGER,
                    sha256 TEXT,
                    mtime REAL,
                    status TEXT DEFAULT 'PENDING',
                    classification TEXT,
                    metadata TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Migration check for existing dbs
            try:
                conn.execute("ALTER TABLE files ADD COLUMN mtime REAL;")
            except sqlite3.OperationalError:
                pass

            conn.execute("""
                CREATE TABLE IF NOT EXISTS file_locks (
                    path TEXT PRIMARY KEY,
                    worker_id TEXT NOT NULL,
                    locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def add_file(
        self,
        path: str,
        size: int,
        sha256: Optional[str] = None,
        mtime: Optional[float] = None,
    ):
        with self.lock, self.get_connection() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO files (path, size, sha256, mtime, status)
                VALUES (?, ?, ?, ?, 'PENDING')
            """,
                (path, size, sha256, mtime),
            )
            conn.commit()

    def update_sha256(self, path: str, sha256: str):
        with self.lock, self.get_connection() as conn:
            conn.execute(
                """
                UPDATE files SET sha256 = ?, updated_at = CURRENT_TIMESTAMP WHERE path = ?
            """,
                (sha256, path),
            )
            conn.commit()

    def get_pending_files(self, limit: int = 50) -> list:
        with self.lock, self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT path, size, sha256, mtime FROM files WHERE status = 'PENDING' LIMIT ?
            """,
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def acquire_lock(self, path: str, worker_id: str) -> bool:
        with self.lock, self.get_connection() as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO file_locks (path, worker_id) VALUES (?, ?)
                """,
                    (path, worker_id),
                )
                conn.execute(
                    """
                    UPDATE files SET status = 'PROCESSING', updated_at = CURRENT_TIMESTAMP
                    WHERE path = ?
                """,
                    (path,),
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def release_lock(
        self,
        path: str,
        worker_id: str,
        status: str = "COMPLETED",
        classification: str = None,
        metadata: dict = None,
    ):
        with self.lock, self.get_connection() as conn:
            conn.execute(
                "DELETE FROM file_locks WHERE path = ? AND worker_id = ?",
                (path, worker_id),
            )
            meta_json = json.dumps(metadata, ensure_ascii=False) if metadata else None
            conn.execute(
                """
                UPDATE files SET status = ?, classification = ?, metadata = ?, updated_at = CURRENT_TIMESTAMP
                WHERE path = ?
            """,
                (status, classification, meta_json, path),
            )
            conn.commit()

    def get_daily_load_report(self) -> list:
        with self.lock, self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    strftime('%Y-%m-%d', updated_at) AS processing_date,
                    COUNT(*) AS total_processed,
                    SUM(CASE WHEN json_extract(metadata, '$.escalated') IN ('true', 1) THEN 1 ELSE 0 END) AS escalated_count,
                    ROUND(
                        100.0 * SUM(CASE WHEN json_extract(metadata, '$.escalated') IN ('true', 1) THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 
                        2
                    ) AS escalation_percentage,
                    ROUND(AVG(CAST(json_extract(metadata, '$.initial_confidence') AS REAL)), 3) AS avg_initial_confidence,
                    ROUND(
                        AVG(
                            CASE 
                                WHEN json_extract(metadata, '$.escalated') IN ('true', 1) 
                                THEN CAST(json_extract(metadata, '$.initial_confidence') AS REAL) 
                            END
                        ), 3
                    ) AS avg_confidence_on_escalated
                FROM files
                WHERE status = 'COMPLETED'
                GROUP BY processing_date
                ORDER BY processing_date ASC;
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_weekly_load_report(self) -> list:
        """Возвращает агрегированный отчет за неделю (или когорты по неделям) для анализа трендов эскалаций."""
        with self.lock, self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    strftime('%Y-%W', updated_at) AS weekly_cohort,
                    MIN(updated_at) AS cohort_start,
                    MAX(updated_at) AS cohort_end,
                    COUNT(*) AS total_processed,
                    SUM(CASE WHEN json_extract(metadata, '$.escalated') IN ('true', 1) THEN 1 ELSE 0 END) AS escalated_count,
                    ROUND(
                        100.0 * SUM(CASE WHEN json_extract(metadata, '$.escalated') IN ('true', 1) THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 
                        2
                    ) AS escalation_percentage,
                    ROUND(AVG(CAST(json_extract(metadata, '$.initial_confidence') AS REAL)), 3) AS avg_initial_confidence,
                    ROUND(
                        AVG(
                            CASE 
                                WHEN json_extract(metadata, '$.escalated') IN ('true', 1) 
                                THEN CAST(json_extract(metadata, '$.initial_confidence') AS REAL) 
                            END
                        ), 3
                    ) AS avg_confidence_on_escalated
                FROM files
                WHERE status = 'COMPLETED'
                GROUP BY weekly_cohort
                ORDER BY weekly_cohort ASC;
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_monthly_load_report(self) -> list:
        """Возвращает агрегированный отчет за месяц для анализа широкой динамики эскалаций."""
        with self.lock, self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    strftime('%Y-%m', updated_at) AS monthly_cohort,
                    MIN(updated_at) AS cohort_start,
                    MAX(updated_at) AS cohort_end,
                    COUNT(*) AS total_processed,
                    SUM(CASE WHEN json_extract(metadata, '$.escalated') IN ('true', 1) THEN 1 ELSE 0 END) AS escalated_count,
                    ROUND(
                        100.0 * SUM(CASE WHEN json_extract(metadata, '$.escalated') IN ('true', 1) THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 
                        2
                    ) AS escalation_percentage,
                    ROUND(AVG(CAST(json_extract(metadata, '$.initial_confidence') AS REAL)), 3) AS avg_initial_confidence,
                    ROUND(
                        AVG(
                            CASE 
                                WHEN json_extract(metadata, '$.escalated') IN ('true', 1) 
                                THEN CAST(json_extract(metadata, '$.initial_confidence') AS REAL) 
                            END
                        ), 3
                    ) AS avg_confidence_on_escalated
                FROM files
                WHERE status = 'COMPLETED'
                GROUP BY monthly_cohort
                ORDER BY monthly_cohort ASC;
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_category_distribution_report(self) -> list:
        """Возвращает распределение обработанных файлов по категориям (классификации)."""
        with self.lock, self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    COALESCE(classification, 'uncategorized') AS category,
                    COUNT(*) AS count,
                    ROUND(
                        100.0 * COUNT(*) / NULLIF((SELECT COUNT(*) FROM files WHERE status = 'COMPLETED'), 0), 
                        2
                    ) AS percentage
                FROM files
                WHERE status = 'COMPLETED'
                GROUP BY category
                ORDER BY count DESC;
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_queue_stats(self) -> dict:
        """Возвращает текущую статистику очереди по статусам (PENDING, PROCESSING, COMPLETED, FAILED)."""
        with self.lock, self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT status, COUNT(*) as count 
                FROM files 
                GROUP BY status;
            """)
            stats = {row["status"]: row["count"] for row in cursor.fetchall()}
            total_cursor = conn.execute("SELECT COUNT(*) FROM files;")
            total_files = total_cursor.fetchone()[0]
            return {
                "total_files": total_files,
                "pending": stats.get("PENDING", 0),
                "processing": stats.get("PROCESSING", 0),
                "completed": stats.get("COMPLETED", 0),
                "failed": stats.get("FAILED", 0),
                "timestamp": datetime.now().isoformat(),
            }


def save_progress_report(
    db: DatabaseManager, report_path: str = "progress_report.json"
) -> dict:
    stats = db.get_queue_stats()
    path = Path(report_path)
    reports = []
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                reports = json.load(f)
                if not isinstance(reports, list):
                    reports = [reports]
        except:
            reports = []
    reports.append(stats)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=4)
    logger.info(f"Progress report saved to {path}: {stats}")
    return stats


class DiskScanner:
    r"""Сканировщик диска (I/O Worker) с поддержкой Lazy Hashing и Retry Policy для F:\ (Google Drive)."""

    def __init__(self, root_path: str, db_manager: DatabaseManager):
        self.root_path = Path(root_path)
        self.db = db_manager

    def compute_sha256(
        self, file_path: Path, chunk_size: int = 65536, max_retries: int = 5
    ) -> str:
        """Вычисляет SHA-256 с Retry Policy при ошибках доступа, OSError или блокировках Google Drive."""
        for attempt in range(max_retries):
            try:
                sha256 = hashlib.sha256()
                with open(file_path, "rb") as f:
                    while True:
                        data = f.read(chunk_size)
                        if not data:
                            break
                        sha256.update(data)
                return sha256.hexdigest()
            except (PermissionError, OSError) as e:
                wait_time = (
                    2**attempt
                )  # Экспоненциальная задержка: 1s, 2s, 4s, 8s, 16s...
                logger.warning(
                    f"Retry {attempt + 1}/{max_retries} opening {file_path}: {e}. Waiting {wait_time}s..."
                )
                time.sleep(wait_time)
            except Exception as e:
                logger.error(f"Unexpected hash error for {file_path}: {e}")
                return "ERROR_HASH"
        logger.error(
            f"Failed to compute SHA-256 for {file_path} after {max_retries} attempts."
        )
        return "ERROR_HASH"

    def scan(self):
        logger.info(f"Starting lazy disk scan on: {self.root_path}")
        count = 0
        cloud_stubs = {".gdoc", ".gsheet", ".gslides", ".gform"}
        try:
            for entry in self._iter_dir(self.root_path):
                if entry.is_file():
                    path_str = str(entry.path)
                    if Path(path_str).suffix.lower() in cloud_stubs:
                        continue  # Игнорируем облачные ярлыки Google Workspace (.gdoc, .gsheet и др.)
                    try:
                        stat = entry.stat()
                        size = stat.st_size
                        mtime = stat.st_mtime
                    except Exception:
                        size = 0
                        mtime = 0.0

                    # Ленивое хэширование: SHA-256 не вычисляется на этапе первичного os.scandir
                    self.db.add_file(path_str, size, sha256=None, mtime=mtime)
                    count += 1
                    if count % 100 == 0:
                        logger.info(f"Lazily indexed {count} files...")
        except Exception as e:
            logger.error(f"Scan error: {e}")
        logger.info(f"Lazy disk scan completed. Total files registered: {count}")

    def _iter_dir(self, path: Path) -> Generator[os.DirEntry, None, None]:
        cloud_stubs = {".gdoc", ".gsheet", ".gslides", ".gform", ".gshortcut"}
        try:
            with os.scandir(path) as scanner:
                for entry in scanner:
                    if entry.is_dir(follow_symlinks=False):
                        yield from self._iter_dir(Path(entry.path))
                    else:
                        if Path(entry.name).suffix.lower() not in cloud_stubs:
                            yield entry
        except PermissionError:
            logger.warning(f"Permission denied: {path}")
        except Exception as e:
            logger.error(f"Error scanning {path}: {e}")


class InferenceOrchestrator:
    r"""Оркестратор инференса (Ollama API Client) с keep_alive: 0 и семафором."""

    def __init__(self, ollama_url: str = "http://127.0.0.1:11434"):
        self.ollama_url = ollama_url
        self.heavy_semaphore = threading.Semaphore(1)

    def query_model(self, model_name: str, prompt: str, is_heavy: bool = False) -> str:
        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "keep_alive": 0,
        }

        if is_heavy:
            with self.heavy_semaphore:
                return self._send_request(url, payload)
        else:
            return self._send_request(url, payload)

    def _send_request(self, url: str, payload: dict) -> str:
        try:
            response = requests.post(url, json=payload, timeout=120)
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                logger.error(
                    f"Ollama error status {response.status_code}: {response.text}"
                )
                return ""
        except Exception as e:
            logger.error(f"Ollama connection error: {e}")
            return ""


class DriveWorkerPool:
    r"""Пул воркеров с таймаутом задачи (Timeout Guard), многоязычным коммутатором, расширенными критическими ключевыми словами и ленивым хэшированием."""

    def __init__(
        self,
        db_manager: DatabaseManager,
        orchestrator: InferenceOrchestrator,
        max_workers: int = 2,
        task_timeout: int = 60,
    ):
        self.db = db_manager
        self.orchestrator = orchestrator
        self.max_workers = max_workers
        self.task_timeout = task_timeout
        self.scanner = DiskScanner(
            "", db_manager
        )  # Для доступа к репликации хэша/retry
        self.heavy_extensions = {".pdf", ".docx", ".doc", ".json", ".db", ".sqlite"}
        self.cloud_stubs = {".gdoc", ".gsheet", ".gslides", ".gform"}

        # Расширенный словарь критических терминов (включая румынские юридические и административные)
        self.critical_keywords = {
            "legal",
            "court",
            "evidence",
            "contract",
            "иск",
            "завещание",
            "акт",
            "справка",
            "hotărâre",
            "hotarare",
            "judecată",
            "judecata",
            "dosar",
            "cerere",
            "decizie",
            "procură",
            "procura",
            "rechizitoriu",
        }

    def is_critical_artifact(self, path: str) -> bool:
        p = Path(path)
        ext = p.suffix.lower()
        name_lower = p.name.lower()
        tokens = set(re.findall(r"[a-zа-яăâîșț0-9]+", name_lower))

        if ext in self.heavy_extensions:
            return True
        if tokens.intersection(self.critical_keywords):
            return True
        return False

    def process_file_task(self, file_item: dict, worker_id: str = "worker-1"):
        path = file_item["path"]
        if Path(path).suffix.lower() in self.cloud_stubs:
            return  # Пропускаем облачные ярлыки Google Workspace (.gdoc, .gsheet и др.)
        if not self.db.acquire_lock(path, worker_id):
            return  # Уже обрабатывается другим воркером

        print(f"[{worker_id}] START processing: {path}")

        def _execute_pipeline():
            # Отложенное вычисление SHA-256 (Lazy Hashing при переходе в активную обработку)
            file_sha256 = file_item.get("sha256")
            if not file_sha256:
                file_path_obj = Path(path)
                file_sha256 = self.scanner.compute_sha256(file_path_obj)
                self.db.update_sha256(path, file_sha256)

            is_critical_pre = self.is_critical_artifact(path)

            # Многоязычный коммутатор: получение промптов на основе эвристики языка (RO, RU, EN)
            lang_code, light_prompt, heavy_prompt_template = get_classification_prompt(
                path
            )

            # Шаг 1: Первичный анализ легкой моделью (qwen2.5:0.5b)
            light_response = self.orchestrator.query_model(
                "qwen2.5:0.5b", light_prompt, is_heavy=False
            )

            confidence = 1.0
            classification = "standard_document"
            try:
                if "{" in light_response:
                    json_str = light_response[
                        light_response.find("{") : light_response.rfind("}") + 1
                    ]
                    data = json.loads(json_str)
                    classification = data.get("category", classification)
                    confidence = float(data.get("confidence", 0.5))
            except:
                confidence = 0.5

            # Шаг 2: Динамическая эскалация
            needs_escalation = is_critical_pre or (confidence < 0.6)

            model_used = "qwen2.5:0.5b"
            final_response = light_response

            if needs_escalation:
                model_used = "qwen-forensic:latest"
                heavy_prompt = heavy_prompt_template.format(
                    confidence=confidence,
                    size=file_item.get("size"),
                    sha256=file_sha256,
                )
                final_response = self.orchestrator.query_model(
                    model_used, heavy_prompt, is_heavy=True
                )
                try:
                    if "{" in final_response:
                        json_str = final_response[
                            final_response.find("{") : final_response.rfind("}") + 1
                        ]
                        data = json.loads(json_str)
                        classification = data.get("category", classification)
                except:
                    pass

            return {
                "classification": classification,
                "metadata": {
                    "language": lang_code,
                    "model_used": model_used,
                    "initial_confidence": confidence,
                    "escalated": needs_escalation,
                    "raw_response": final_response,
                },
            }

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_execute_pipeline)
            try:
                res = future.result(timeout=self.task_timeout)
                self.db.release_lock(
                    path,
                    worker_id,
                    status="COMPLETED",
                    classification=res["classification"],
                    metadata=res["metadata"],
                )
                print(f"[{worker_id}] COMPLETED: {path}")

            except FuturesTimeoutError:
                err_msg = f"TIMEOUT: Task exceeded {self.task_timeout}s limit"
                print(f"[!] {worker_id} ERROR on {path}: {err_msg}")
                self._mark_as_failed(path, err_msg, worker_id)

            except Exception as e:
                err_msg = f"{type(e).__name__}: {str(e)}"
                print(
                    f"[!] {worker_id} ERROR on {path}: {err_msg}\n{traceback.format_exc()}"
                )
                self._mark_as_failed(path, err_msg, worker_id)

    def _mark_as_failed(self, path, error_reason, worker_id):
        try:
            with self.db.get_connection() as conn:
                conn.execute(
                    "DELETE FROM file_locks WHERE path = ? AND worker_id = ?",
                    (path, worker_id),
                )
                conn.execute(
                    "UPDATE files SET status = 'FAILED', metadata = ?, updated_at = CURRENT_TIMESTAMP WHERE path = ?",
                    (json.dumps({"error": error_reason}, ensure_ascii=False), path),
                )
                conn.commit()
        except Exception as db_err:
            logger.error(
                f"[!] Critical DB error while marking task as FAILED: {db_err}"
            )

    def run_pool(self, batch_limit: int = 200):
        pending = self.db.get_pending_files(batch_limit)
        if not pending:
            logger.info("No pending files in queue.")
            return

        logger.info(
            f"Processing batch of {len(pending)} files with {self.max_workers} workers..."
        )
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for idx, file_item in enumerate(pending):
                worker_id = f"worker_{idx % self.max_workers}"
                futures.append(
                    executor.submit(self.process_file_task, file_item, worker_id)
                )

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Task exception: {e}")
        logger.info("Batch processing completed.")


if __name__ == "__main__":
    print(
        "MCP Drive Indexer & Worker Pool Module (Multilingual / Lazy Hashing) loaded successfully."
    )
