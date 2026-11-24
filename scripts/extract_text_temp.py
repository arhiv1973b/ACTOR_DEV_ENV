import fitz
import hashlib
import json
from pathlib import Path

PDF_PATH = Path(r"H:\ACTOR_DEV_ENV\apostille_registry_working_18.signed.pdf")
OUTPUT_JSON = Path(r"H:\ACTOR_DEV_ENV\temp\temp_index.json")

with PDF_PATH.open("rb") as source:
    sha256 = hashlib.file_digest(source, "sha256").hexdigest()

doc = fitz.open(PDF_PATH)
pages = []

for number, page in enumerate(doc, start=1):
    text = page.get_text("text").strip()
    pages.append(
        {
            "page": number,
            "text": text,
            "text_layer_available": bool(text),
        }
    )

doc.close()

index = {
    "declaration_key": "# [⚖ A©tor Declaration]",
    "documents": [
        {
            "document_id": "apostille_registry_working_18",
            "pdf": PDF_PATH.name,
            "pdf_sha256": sha256,
            "pages": pages,
        }
    ],
}

OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT_JSON.open("w", encoding="utf-8") as target:
    json.dump(index, target, ensure_ascii=False, indent=2)

print(f"PDF_SHA256={sha256}")
print(f"PAGES={len(pages)}")
print(f"TEXT_LAYERS={sum(p['text_layer_available'] for p in pages)}")
print(f"OUTPUT={OUTPUT_JSON}")
