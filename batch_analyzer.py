#!/usr/bin/env python3
"""
Batch Document Analyzer - Optimized
Быстрая автоматизированная обработка документов
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
import subprocess
import time
import logging

class BatchDocumentAnalyzer:
    """Оптимизированный пакетный анализатор."""
    
    def __init__(self, source_dir: str, results_dir: str):
        self.source_dir = Path(source_dir)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        
        # Настройка логирования
        self.logs_dir = self.results_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        self.setup_logging()
        
        # Поддерживаемые форматы
        self.supported_formats = {'.txt', '.md', '.html', '.json', '.csv'}
        # PDF обычно требует OCR, пропускаем для скорости
        
        # Файл для отслеживания
        self.processed_file = self.results_dir / "processed_files.json"
        self.load_processed_files()
    
    def setup_logging(self):
        """Настроить логирование."""
        log_file = self.logs_dir / f"batch_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # Настроить логгер
        self.logger = logging.getLogger('BatchAnalyzer')
        self.logger.setLevel(logging.DEBUG)
        
        # Обработчик для файла
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        
        # Обработчик для консоли
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        
        # Форматер
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def load_processed_files(self):
        """Загрузить список обработанных файлов."""
        if self.processed_file.exists():
            with open(self.processed_file, 'r') as f:
                self.processed = json.load(f)
        else:
            self.processed = {}
    
    def save_processed_files(self):
        """Сохранить список обработанных файлов."""
        with open(self.processed_file, 'w') as f:
            json.dump(self.processed, f, indent=2)
    
    def get_file_hash(self, file_path: Path) -> str:
        """Получить хеш файла."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    def is_already_processed(self, file_path: Path) -> bool:
        """Проверить, обработан ли файл."""
        file_str = str(file_path)
        if file_str not in self.processed:
            return False
        
        try:
            current_hash = self.get_file_hash(file_path)
            return self.processed[file_str] == current_hash
        except:
            return False
    
    def scan_documents_fast(self, max_depth: int = 2) -> list:
        """Быстрое сканирование (ограничена глубина)."""
        documents = []
        
        try:
            # Проверить только первый уровень
            for item in self.source_dir.iterdir():
                if item.name == "analysis_results":
                    continue
                
                if item.is_file():
                    if item.suffix.lower() in self.supported_formats:
                        if not self.is_already_processed(item):
                            documents.append(item)
                
                elif item.is_dir() and max_depth > 0:
                    # Рекурсия только на 1 уровень
                    try:
                        for subitem in item.iterdir():
                            if subitem.is_file() and subitem.suffix.lower() in self.supported_formats:
                                if not self.is_already_processed(subitem):
                                    documents.append(subitem)
                    except:
                        pass
        except Exception as e:
            self.logger.error(f"Scan error: {e}")
        
        return sorted(documents)[:50]  # Максимум 50 файлов за раз
    
    def run_analysis(self, file_path: Path, model: str = "gemma:2b", timeout: int = 180) -> dict:
        """Анализировать документ."""
        try:
            self.logger.info(f"Analyzing: {file_path.name}")
            
            cmd = [
                sys.executable,
                "H:\\ACTOR_DEV_ENV\\hybrid_llm_engine_v2.py",
                "analyze",
                str(file_path),
                model
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode == 0:
                try:
                    analysis = json.loads(result.stdout)
                    return analysis
                except:
                    return {"error": "Parse failed"}
            else:
                return {"error": result.stderr[:200]}
        except subprocess.TimeoutExpired:
            raise
        except Exception as e:
            self.logger.error(f"Error analyzing {file_path.name}: {str(e)[:100]}")
            return {"error": str(e)[:100]}

    def analyze_with_retry(self, file_path: Path, model: str = "gemma:2b", retries: int = 3, timeout: int = 180) -> dict:
        """Анализировать документ с повторными попытками при таймауте."""
        for attempt in range(retries):
            try:
                self.logger.info(f"Attempt {attempt+1}/{retries} for {file_path}")
                return self.run_analysis(file_path, model=model, timeout=timeout)
            except subprocess.TimeoutExpired:
                self.logger.warning(f"Timeout analyzing {file_path.name} (attempt {attempt+1}/{retries})")
                if attempt < retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Failed after {retries} retries due to timeout: {file_path.name}")
                    return {"error": "Timeout"}
            except KeyboardInterrupt:
                self.logger.info("KeyboardInterrupt detected. Exiting...")
                raise
            except Exception as e:
                self.logger.error(f"Error during attempt {attempt+1}: {str(e)[:100]}")
                if attempt < retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Failed after {retries} retries: {file_path.name}")
                    return {"error": str(e)[:100]}
        return {"error": "Unknown error during retries"}
    
    def save_result(self, file_path: Path, analysis: dict):
        """Сохранить результат."""
        try:
            # Использовать хеш для обхода ограничений Windows MAX_PATH и кириллицы
            filename_hash = hashlib.md5(str(file_path).encode('utf-8')).hexdigest()
            result_file = self.results_dir / f"{filename_hash}_analysis.json"
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "file": str(file_path),
                    "timestamp": datetime.now().isoformat(),
                    "result": analysis
                }, f, indent=2, ensure_ascii=False)
            
            # Отметить как обработанный
            file_hash = self.get_file_hash(file_path)
            self.processed[str(file_path)] = file_hash
            self.save_processed_files()
            
            self.logger.info(f"Result saved: {result_file}")
            return result_file
        except Exception as e:
            self.logger.error(f"Error saving result: {e}")
            return None
    
    def run(self, model: str = "gemma:2b", max_files: int = None):
        """Запустить анализ."""
        self.logger.info("=" * 70)
        self.logger.info("BATCH ANALYZER (OPTIMIZED) - STARTED")
        self.logger.info("=" * 70)
        
        self.logger.info(f"Scanning: {self.source_dir}")
        self.logger.info(f"Model: {model}")
        self.logger.info(f"Log file: {self.logs_dir}")
        
        documents = self.scan_documents_fast()
        
        if max_files:
            documents = documents[:max_files]
        
        self.logger.info(f"Found {len(documents)} documents to process")
        
        if not documents:
            self.logger.info("No documents to process")
            return
        
        success = 0
        failed = 0
        
        for i, doc in enumerate(documents, 1):
            self.logger.info(f"[{i}/{len(documents)}] Processing: {doc.name}")
            
            analysis = self.analyze_with_retry(doc, model)
            result_file = self.save_result(doc, analysis)
            
            if result_file:
                success += 1
                self.logger.info(f"✅ Success")
            else:
                failed += 1
                self.logger.error(f"❌ Failed")
            
            time.sleep(1)
        
        self.logger.info("=" * 70)
        self.logger.info(f"Session Complete: Success={success}, Failed={failed}")
        self.logger.info(f"Results saved: {self.results_dir}")
        self.logger.info("=" * 70)

if __name__ == "__main__":
    # Redirecting to H:\ based on security policy restrictions
    source = r"H:\ACTOR_DEV_ENV\inbox" 
    results = r"H:\ACTOR_DEV_ENV\analysis_results"
    model = "gemma:2b"
    max_files = None
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--limit" and len(sys.argv) > 2:
            max_files = int(sys.argv[2])
        elif sys.argv[1] == "--model" and len(sys.argv) > 2:
            model = sys.argv[2]
    
    analyzer = BatchDocumentAnalyzer(source, results)
    analyzer.run(model=model, max_files=max_files)
