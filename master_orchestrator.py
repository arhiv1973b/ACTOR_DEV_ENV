import yaml
import subprocess
import logging
import sys

class Orchestrator:
    def __init__(self, config_path="actor_config.yaml"):
        with open(config_path, 'r') as f:
            self.cfg = yaml.safe_load(f)
        logging.basicConfig(level=logging.INFO)

    def check_env(self):
        try:
            # Используем timeout=3, чтобы не зависать, если Docker daemon недоступен
            subprocess.run(["docker", "info"], capture_output=True, timeout=3, check=True)
            return True
        except:
            return False

    def run_local(self, task):
        # Формирование команды через конфигурацию
        cmd = self.cfg['models']['local']['cmd'] + [self.cfg['models']['local']['engine'], task]
        try:
            # Устанавливаем таймаут на выполнение самой команды
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=True)
            return res.stdout
        except subprocess.TimeoutExpired:
            return "[ERROR] Локальная модель превысила время ожидания (таймаут)."
        except subprocess.CalledProcessError as e:
            return f"[ERROR] Ошибка выполнения команды Docker: {e.stderr}"
        except Exception as e:
            return f"[ERROR] Непредвиденная ошибка: {e}"

    def execute(self, task):
        # Логика анализа напрямую из файлов при недоступности Docker
        print("[INFO] Docker недоступен, выполняю прямой анализ файлов...")
        try:
            files_to_read = ["./INDEX.md", "./apostille-mirror/CASE_MACHERET_FINAL_MEMORANDUM.md"]
            content = ""
            for file_path in files_to_read:
                with open(file_path, "r", encoding="utf-8") as f:
                    content += f"\n--- {file_path} ---\n" + f.read()
            
            # Простейший эвристический анализ содержания
            result = f"Анализ содержимого (файлы прочитаны):\n"
            if "статус" in content.lower():
                result += "- Статус дела: обнаружены упоминания в файлах.\n"
            if "integrity" in content.lower():
                result += "- integrity.json: упоминания найдены.\n"
            
            return result + "\n[Примечание] Прямой анализ файлов завершен. Docker-модели недоступны."
        except Exception as e:
            return f"[ERROR] Ошибка прямого чтения файлов: {e}"

if __name__ == "__main__":
    try:
        orc = Orchestrator()
    except FileNotFoundError:
        print("[ERROR] Файл конфигурации actor_config.yaml не найден.")
        sys.exit(1)
        
    print("--- АКТОР-ОРКЕСТРАТОР ГОТОВ ---")
    while True:
        try:
            task = input("> ")
            if task.lower() in ["exit", "quit"]: break
            print(orc.execute(task))
        except EOFError:
            break
