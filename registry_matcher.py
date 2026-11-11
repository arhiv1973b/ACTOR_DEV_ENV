import fitz
import re
import cv2
import numpy as np
import json
import math
import os


def load_registry(path="apostille_registry_25.json"):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def extract_part_a_exact(doc):
    page_1 = doc[0]
    text = page_1.get_text()

    # Безопасный поиск 13-символьного кода апостиля (исключая код безопасности на 2013)
    codes = re.findall(r"\b[A-Z0-9]{13}\b", text)
    apostille_code = None
    for code in codes:
        if not code.startswith("2013"):
            apostille_code = code
            break

    security_match = re.search(
        r"Codul\s*de\s*siguranță:\s*(\d{13})", text, re.IGNORECASE
    ) or re.search(r"\b(2013\d{9})\b", text)

    signer_match = re.search(
        r"Digitally\s*signed\s*by\s*(.+)", text, re.IGNORECASE
    ) or re.search(
        r"2\.\s*a\s*fost\s*semnat\s*de\s*către\s*\n?\s*(.+)", text, re.IGNORECASE
    )

    return {
        "apostille_nr": apostille_code,
        "security_code": security_match.group(1) if security_match else None,
        "signed_by": signer_match.group(1).strip() if signer_match else None,
        "total_pages": len(doc),
    }


def scan_part_b_heraldic_stream(doc):
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


def verify_and_match_apostille(pdf_path, registry):
    doc = fitz.open(pdf_path)
    part_a = extract_part_a_exact(doc)
    part_b = scan_part_b_heraldic_stream(doc)

    total_seals = sum(p["seals_found"] for p in part_b)

    # Многоуровневые статусы
    part_a_status = "VERIFIED" if part_a["apostille_nr"] else "FAILED"
    part_b_status = "SEAL_DETECTED" if total_seals > 0 else "NO_SEAL"
    cross_link_status = "NOT_VERIFIED"  # Базовый уровень геометрии

    # Поиск по реестру
    registry_match_info = {
        "registry_match": False,
        "registry_line": None,
        "case_number": None,
        "registry_signer": None,
        "document_signer": part_a["signed_by"],
        "match_status": "NOT_FOUND_IN_REGISTRY",
    }

    target_code = part_a["apostille_nr"]
    target_sec = part_a["security_code"]

    for idx, entry in enumerate(registry):
        reg_code = entry.get("apostille")
        reg_sec = entry.get("security_code")
        if (target_code and reg_code == target_code) or (
            target_sec and reg_sec == target_sec
        ):
            reg_signer = entry.get("signer")
            doc_signer = part_a["signed_by"]
            signer_match = (
                (reg_signer == doc_signer) if (reg_signer and doc_signer) else False
            )

            registry_match_info = {
                "registry_match": True,
                "registry_line": entry.get("num", idx + 1),
                "case_number": entry.get("case"),
                "registry_signer": reg_signer,
                "document_signer": doc_signer,
                "match_status": "VERIFIED_EXACT" if signer_match else "REQUIRES_REVIEW",
            }
            cross_link_status = "CROSS_LINK_VERIFIED"
            break

    overall_status = (
        "VERIFIED_SUCCESS"
        if part_a_status == "VERIFIED"
        and part_b_status == "SEAL_DETECTED"
        and registry_match_info["registry_match"]
        else "VERIFIED_PARTIAL"
    )

    return {
        "overall_status": overall_status,
        "part_a_status": part_a_status,
        "part_b_status": part_b_status,
        "cross_link_status": cross_link_status,
        "part_a": part_a,
        "registry_verification": registry_match_info,
        "part_b_summary": {
            "scanned_pages": len(part_b),
            "total_seals": total_seals,
            "breakdown": part_b,
        },
    }


if __name__ == "__main__":
    reg = load_registry()
    sample_pdf = "recovered_evidence/3HWVD912FN7H4_EVIDENCE.pdf"
    if os.path.exists(sample_pdf):
        print(f"[*] Запуск аудита и сопоставления с реестром для: {sample_pdf}")
        report = verify_and_match_apostille(sample_pdf, reg)
        print(json.dumps(report, indent=2, ensure_ascii=False))
