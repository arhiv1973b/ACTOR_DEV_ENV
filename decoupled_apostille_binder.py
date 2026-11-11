import fitz  # PyMuPDF
import cv2
import numpy as np
import re
import json
import math
import os


def extract_part_a_digital_layer(doc):
    """
    Извлечение данных из векторной Части А (Страница 1).
    Электронная подпись контейнера не мешает прямому чтению текста.
    """
    page_1 = doc[0]
    text = page_1.get_text()

    code_match = re.search(r"cu nr\.\s*([A-Z0-9]{13})", text)
    security_match = re.search(r"Codul de siguranță:\s*(\d{13})", text)
    signer_match = re.search(r"a fost semnat de către\s*\n?\s*(.+)", text)
    authority_match = re.search(r"bears the seal / stamp of\s*\n?\s*(.+)", text)

    return {
        "apostille_nr": code_match.group(1) if code_match else None,
        "security_code": security_match.group(1) if security_match else None,
        "signed_by_person": signer_match.group(1).strip() if signer_match else None,
        "seal_authority": authority_match.group(1).strip() if authority_match else None,
        "total_pdf_pages": len(doc),
    }


def scan_part_b_for_heraldic_seals(doc):
    """
    Сканирование Части Б (Страницы 2..N) как независимого растрового потока.
    Полный обход переменного количества страниц с фиксацией круглых гербовых печатей.
    """
    results_b = []

    for page_idx in range(1, len(doc)):
        page = doc[page_idx]
        pix = page.get_pixmap(dpi=300)

        img_np = np.frombuffer(pix.tobytes("png"), dtype=np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

        if img is None:
            continue

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        blue_mask = cv2.inRange(hsv, np.array([90, 40, 40]), np.array([140, 255, 255]))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        closed_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(
            closed_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        found_seals = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 1500:
                continue

            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue

            circularity = (4 * math.pi * area) / (perimeter**2)
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h

            if circularity >= 0.60 and (0.80 <= aspect_ratio <= 1.25):
                found_seals.append(
                    {
                        "circularity": round(circularity, 3),
                        "area_px": int(area),
                        "bounding_box": [x, y, w, h],
                    }
                )

        results_b.append(
            {
                "page_number": page_idx + 1,
                "is_final_page": (page_idx == len(doc) - 1),
                "seals_detected": len(found_seals),
                "seal_details": found_seals,
            }
        )

    return results_b


def process_hybrid_apostille_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    part_a = extract_part_a_digital_layer(doc)
    part_b_pages = scan_part_b_for_heraldic_seals(doc)

    total_seals_in_b = sum(p["seals_detected"] for p in part_b_pages)
    final_page_has_seal = (
        part_b_pages[-1]["seals_detected"] > 0 if part_b_pages else False
    )

    bind_status = (
        "BINDING_SUCCESS"
        if (part_a["apostille_nr"] and total_seals_in_b > 0)
        else "BINDING_WARNING"
    )

    return {
        "bind_status": bind_status,
        "part_a_metadata": part_a,
        "part_b_summary": {
            "total_scanned_pages": len(part_b_pages),
            "total_physical_seals_found": total_seals_in_b,
            "final_page_sealed": final_page_has_seal,
            "pages_breakdown": part_b_pages,
        },
    }


if __name__ == "__main__":
    sample_pdf = "recovered_evidence/Реестр_полный_EVIDENCE.pdf"
    if os.path.exists(sample_pdf):
        report = process_hybrid_apostille_pdf(sample_pdf)
        print(json.dumps(report, indent=2, ensure_ascii=False))
