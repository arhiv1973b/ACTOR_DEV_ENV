import json
import shutil
from pathlib import Path

REPO_DIR = Path(r"H:\ACTOR_DEV_ENV\apostille-archive-english")
ORIGINALS_DIR = Path(r"H:\ACTOR_DEV_ENV") 
MANIFEST_PATH = Path(r"H:\ACTOR_DEV_ENV\manifest.json")

def restore():
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    
    for rec in data["records"]:
        if rec["status"] != "ok":
            target_path = REPO_DIR / rec["filename"]
            candidates = list(ORIGINALS_DIR.rglob(rec["filename"]))
            
            if candidates:
                original = candidates[0]
                if original.stat().st_size > 1024:
                    shutil.copy2(original, target_path)
                    rec["status"] = "ok"
                    rec["notes"] = "восстановлено из оригинала"
                    print(f"[+] Восстановлен: {rec['filename']} ({original.stat().st_size} bytes)")
                else:
                    print(f"[-] Пропуск: {rec['filename']} (оригинал также пуст)")
            else:
                print(f"[!] Оригинал не найден для: {rec['filename']}")
    
    MANIFEST_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nМанифест обновлен. Файлы подготовлены.")

if __name__ == "__main__":
    restore()
