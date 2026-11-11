import fitz
import os

pdf_path = "recovered_evidence/Реестр_полный_EVIDENCE.pdf"
output_dir = "recovered_evidence/registry_split"
os.makedirs(output_dir, exist_ok=True)

doc = fitz.open(pdf_path)
print(f"[*] Всего страниц в документе: {len(doc)}")

manifest = []

for i, page in enumerate(doc):
    page_num = i + 1
    text = page.get_text().strip()

    # Сохраняем первую страницу как текст/информативную базу (Часть А)
    # А остальные страницы как изображения (Часть Б) без OCR

    img_filename = f"page_{page_num:03d}.png"
    img_path = os.path.join(output_dir, img_filename)

    # Рендерим страницу в изображение (300 DPI для верификации)
    pix = page.get_pixmap(dpi=300)
    pix.save(img_path)

    manifest.append(
        {
            "page": page_num,
            "type": "Part_A_Informative" if page_num == 1 else "Part_B_Visual_Evidence",
            "text_preview": text[:200]
            if page_num == 1
            else "[Visual Evidence Stream - No OCR]",
            "image_path": img_path,
        }
    )
    print(f"[+] Обработана страница {page_num}/{len(doc)}")

print(f"[+] Разделение завершено. Результаты в {output_dir}")
