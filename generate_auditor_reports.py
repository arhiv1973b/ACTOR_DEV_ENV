import os
import json
import shutil
from datetime import datetime

def generate_auditor_package():
    print("--- [AUDITOR PIPELINE] Генерация регулярного пакета отчетов для внешних аудиторов ---")
    
    output_dir = r"H:\ACTOR_DEV_ENV\auditor_reports_package"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Собираем ключевые файлы артефактов
    artifacts = [
        "CASE_MACHERET_MASTER_SUMMARY_2026.md",
        "financial_anomaly_analysis_25m_mdl.md",
        "compliance_matrix.json",
        "expert_forensic_report.html",
        "apostille-mirror/A©tor_FORENSIC_AUDIT_MANIFEST_V4_4.md"
    ]
    
    package_manifest = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "case_id": "CASE-MACHERET-1997-2026",
        "included_artifacts": []
    }
    
    for art in artifacts:
        src = os.path.join(r"H:\ACTOR_DEV_ENV", art)
        if os.path.exists(src):
            dst = os.path.join(output_dir, os.path.basename(art))
            shutil.copy2(src, dst)
            package_manifest["included_artifacts"].append(art)
            print(f"  [+] Скопирован артефакт: {art}")
        else:
            print(f"  [!] Артефакт не найден: {art}")
            
    # Записываем манифест пакета аудитора
    manifest_path = os.path.join(output_dir, "auditor_package_manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(package_manifest, f, ensure_ascii=False, indent=2)
        
    print(f"Пакет отчетов для внешних аудиторов успешно сформирован в: {output_dir}")

if __name__ == "__main__":
    generate_auditor_package()
