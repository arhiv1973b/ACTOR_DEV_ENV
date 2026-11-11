import os
import json
import yaml
import glob
import fitz  # PyMuPDF
import img2pdf
import subprocess

# Пути к файлам
scans_dir = r"H:\Загрузки\Scanner_X_2026-11-11_085626"
output_dir = (
    r"F:\Мой диск" if os.path.exists(r"F:\Мой диск") else r"H:\ACTOR_DEV_ENV\evidence"
)
pdf_output = os.path.join(output_dir, "cazier_counter_registry_final.pdf")
json_output = os.path.join(output_dir, "cazier_evidence_manifest.json")
yaml_output = os.path.join(output_dir, "cazier_evidence_manifest.yaml")

os.makedirs(output_dir, exist_ok=True)

# 1. Поиск сканов в нужном порядке
scan_files = sorted(
    glob.glob(os.path.join(scans_dir, "Scanner_X_*.png")),
    key=lambda x: int(x.split("_")[-1].split(".")[0]),
)

# 2. Сборка PDF из изображений
if scan_files:
    with open(pdf_output, "wb") as f:
        f.write(img2pdf.convert(scan_files))
    print(f"[SUCCESS] PDF создан: {pdf_output}")

# 3. Пуш в Git
os.chdir(r"H:\ACTOR_DEV_ENV")
subprocess.run(["git", "checkout", "-b", "evidence-mvd-dec-2025"], check=False)
subprocess.run(["git", "add", "."], check=True)
subprocess.run(
    [
        "git",
        "commit",
        "-m",
        "feat(audit): build Cazier counter-registry PDF and manifests [A©tor]",
    ],
    check=False,
)
subprocess.run(
    ["git", "push", "origin", "evidence-mvd-dec-2025", "--force"], check=True
)
print("[SUCCESS] Пуш в Git завершен.")
