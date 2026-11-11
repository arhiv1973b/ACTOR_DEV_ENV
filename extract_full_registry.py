import fitz
import json
import os

pdf_path = "recovered_evidence/Реестр_полный_EVIDENCE.pdf"
output_json = "recovered_evidence/full_registry_98_extracted.json"

doc = fitz.open(pdf_path)
full_text = ""

for page in doc:
    full_text += page.get_text() + "\n"

# Сохраняем сырой текст для проверки
with open("recovered_evidence/full_registry_raw_text.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"[+] Извлечен полный текст реестра ({len(full_text)} символов).")
