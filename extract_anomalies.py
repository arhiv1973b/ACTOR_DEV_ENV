import json
import logging
import re
from pathlib import Path

# Настройка базового логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def extract_critical_nodes(input_file: str, output_file: str):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            nodes = json.load(f)

        anomalies = []
        
        # Шаг 1: Поиск по уже размеченному флагу
        for node in nodes:
            if node.get('is_anomaly') is True:
                anomalies.append(node)

        # Шаг 2: Fallback-механизм
        # Если флаги 'is_anomaly' еще не размечены, фильтруем базу по наличию 13-значных маркеров
        if not anomalies:
            idnp_pattern = re.compile(r'\b\d{13}\b')
            for node in nodes:
                node_name = str(node.get('name', ''))
                node_idnp = str(node.get('idnp', ''))
                if idnp_pattern.search(node_name) or idnp_pattern.search(node_idnp):
                    anomalies.append(node)

        # Сохранение артефакта
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(anomalies, f, ensure_ascii=False, indent=2)

        logging.info(f"✦ Выборка завершена. Извлечено узлов: {len(anomalies)}")
        logging.info(f"✦ Артефакт декомпозиции сохранен: {output_file}")

    except FileNotFoundError:
        logging.error(f"[ОШИБКА] Базовый файл не найден: {input_file}")
    except json.JSONDecodeError:
        logging.error(f"[ОШИБКА] Файл {input_file} содержит некорректный JSON.")
    except Exception as e:
        logging.error(f"[КРИТИЧЕСКАЯ ОШИБКА] Сбой при парсинге графа: {e}")

if __name__ == '__main__':
    TARGET_DIR = Path(r"H:\ACTOR_DEV_ENV\apostille-mirror")
    
    # Используем IDNP_Anomalies_Map.json как подтвержденный источник
    INPUT_MAP = TARGET_DIR / "IDNP_Anomalies_Map.json" 
    OUTPUT_MAP = TARGET_DIR / "Critical_IDNP_Entities.json"
    
    logging.info("Инициализация вектора [build-entity-graph]...")
    extract_critical_nodes(str(INPUT_MAP), str(OUTPUT_MAP))