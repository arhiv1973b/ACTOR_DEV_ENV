import json
import re
from pathlib import Path

def generate_markdown_report(input_json, output_md):
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    idnp_pattern = re.compile(r'\b\d{13}\b')
    
    with open(output_md, 'w', encoding='utf-8') as out:
        out.write("# ✦ Матрица саботажа ИДНП (CASE-MACHERET-1997-2026)\n\n")
        out.write("| # | Выявленный ИДНП | Связанный документ (Контекст) | Идентификатор (Drive ID) |\n")
        out.write("|---|---|---|---|\n")
        
        for idx, item in enumerate(data, 1):
            name = item.get('name', 'UNKNOWN')
            file_id = item.get('id', 'N/A')
            
            # Ищем 13-значный код в имени или других полях
            match = idnp_pattern.search(name)
            idnp = match.group(0) if match else "СКРЫТЫЙ МАРКЕР"
            
            # Очищаем имя для корректного отображения в Markdown (убираем переносы и лишние пробелы)
            clean_name = name.replace('\n', ' ').strip()
            
            out.write(f"| {idx} | **{idnp}** | `{clean_name}` | {file_id} |\n")

    print(f"✦ Матрица успешно сгенерирована: {output_md}")

if __name__ == '__main__':
    BASE_DIR = Path(r"H:\ACTOR_DEV_ENV")
    INPUT_FILE = BASE_DIR / "apostille-mirror" / "Critical_IDNP_Entities.json"
    OUTPUT_FILE = BASE_DIR / "Sabotage_Timeline.md"
    
    generate_markdown_report(INPUT_FILE, OUTPUT_FILE)