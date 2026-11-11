import fitz  # PyMuPDF
import cv2
import numpy as np
import re
import json
import math
import os


def extract_part_a_exact(doc):
    """
    Точный парсинг векторного слоя Части А (Страница 1)
    без потери 13-значных кодов апостиля и кодов безопасности.
    """
    page_1 = doc[0]
    text = page_1.get_text()

    code_match = (
        re.search(r"8\.\s*cu\s*nr\.\s*([A-Z0-9]{13})", text, re.IGNORECASE)
        or re.search(r"cu\s*nr\.\s*([A-Z0-9]{13})", text, re.IGNORECASE)
        or re.search(r"\b([A-Z0-9]{13})\b", text)
    )

    security_match = re.search(
        r"Codul\s*de\s*siguranță:\s*(\d{13})", text, re.IGNORECASE
    ) or re.search(r"\b(2013\d{9})\b", text)

    signer_match = re.search(
        r"Digitally\s*signed\s*by\s*(.+)", text, re.IGNORECASE
    ) or re.search(
        r"2\.\s*a\s*fost\s*semnat\s*de\s*către\s*\n?\s*(.+)", text, re.IGNORECASE
    )

    authority_match = re.search(
        r"4\.\s*și\s*poartă\s*sigiliul/ștampila\s*\n?\s*(.+)", text, re.IGNORECASE
    )

    return {
        "apostille_nr": code_match.group(1) if code_match else None,
        "security_code": security_match.group(1) if security_match else None,
        "signed_by": signer_match.group(1).strip() if signer_match else None,
        "authority": authority_match.group(1).strip() if authority_match else None,
        "total_pages": len(doc),
    }


def scan_part_b_heraldic_stream(doc):
    """
    Потоковый обход Части Б (Страницы 2..N):
    Фиксация гербовых печатей с учетом сшивки и наложения подписей.
    """
    pages_data = []

    for idx in range(1, len(doc)):
        page = doc[idx]
        pix = page.get_pixmap(dpi=300)

        img_np = np.frombuffer(pix.tobytes("png"), dtype=np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        if img is None:
            continue

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        blue_mask = cv2.inRange(hsv, np.array([80, 25, 25]), np.array([150, 255, 255]))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        closed_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(
            closed_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        seals = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 700:
                continue

            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue

            circularity = (4 * math.pi * area) / (perimeter**2)
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h

            if circularity >= 0.45 and (0.75 <= aspect_ratio <= 1.35):
                seals.append(
                    {
                        "circularity": round(circularity, 3),
                        "area_px": int(area),
                        "bbox": [x, y, w, h],
                    }
                )

        pages_data.append(
            {
                "page_num": idx + 1,
                "is_final": (idx == len(doc) - 1),
                "seals_found": len(seals),
                "details": seals,
            }
        )

    return pages_data


def verify_single_apostille_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    part_a = extract_part_a_exact(doc)
    part_b = scan_part_b_heraldic_stream(doc)

    total_seals = sum(p["seals_found"] for p in part_b)

    if part_a["apostille_nr"] and total_seals > 0:
        status = "VERIFIED_SUCCESS"
    elif part_a["apostille_nr"]:
        status = "PART_A_ONLY"
    elif total_seals > 0:
        status = "PART_B_ONLY"
    else:
        status = "FAILED"

    return {
        "status": status,
        "part_a": part_a,
        "part_b_summary": {
            "scanned_pages": len(part_b),
            "total_seals": total_seals,
            "breakdown": part_b,
        },
    }


if __name__ == "__main__":
    # Проверяем на одном из файлов свидетельств/апостилей
    sample_pdf = "recovered_evidence/3HWVD912FN7H4_EVIDENCE.pdf"
    if os.path.exists(sample_pdf):
        print(f"[*] Запуск точного верификатора для: {sample_pdf}")
        report = verify_single_apostille_pdf(sample_pdf)
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("[-] Тестовый файл не найден.")
