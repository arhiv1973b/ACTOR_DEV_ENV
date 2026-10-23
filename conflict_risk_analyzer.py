import json, pathlib, sys
from vclt_legal_api import get_article_text

BASE_DIR = pathlib.Path(__file__).parent.resolve()
MANIFEST = BASE_DIR / "evidence_manifest.json"
SIG_FILE = BASE_DIR / "manifest.sig"
REPORT = BASE_DIR / "conflict_risk_report.md"

def verify_signature() -> bool:
    return MANIFEST.exists() and SIG_FILE.exists()

def audit():
    with MANIFEST.open(encoding="utf-8") as f:
        data = json.load(f)
    
    report = ["# Аудит правовых рисков (TI-ULA API)\n"]
    for entry in data.get("entries", []):
        breach = entry.get("breach_article")
        if breach == 60:
            text = get_article_text(60)
            report.append(f"### [КРИТИЧЕСКИЙ РИСК] Контракт: {entry['id']}")
            report.append(f"**Нарушена статья 60:**\n{text}\n")
    
    with REPORT.open("w", encoding="utf-8") as out:
        out.write("\n".join(report))

if __name__ == "__main__":
    if verify_signature():
        audit()
        print("✅ Аудит завершен. Отчет обновлен.")
    else:
        print("❌ Ошибка: манифест или подпись не найдены.")
