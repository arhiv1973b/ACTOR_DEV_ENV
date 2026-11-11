import os
import re
import cv2
import json
import math
import shutil
import hashlib
import tempfile
import fitz  # PyMuPDF
import numpy as np


def compute_sha256(data_bytes: bytes) -> str:
    return hashlib.sha256(data_bytes).hexdigest()


def extract_part_a_metadata(text_content: str) -> dict:
    clean_text = text_content.strip()
    apostille_code_match = re.search(r"([A-Z0-9]{13})", clean_text)
    security_code_match = re.search(r"(\d{13})", clean_text)
    case_num_match = re.search(
        r"(?:дело|dosar|case|№)\s*[:\.]?\s*([A-Za-z0-9/\-_]+)",
        clean_text,
        re.IGNORECASE,
    )

    seal_keywords = [
        "печать",
        "sigiliu",
        "stamp",
        "гербовая",
        "оттиск",
        "sceau",
        "seal",
    ]
    signature_keywords = ["подпись", "semnătura", "signature", "подписано", "signed"]

    has_seal_declaration = any(kw in clean_text.lower() for kw in seal_keywords)
    has_signature_declaration = any(
        kw in clean_text.lower() for kw in signature_keywords
    )

    return {
        "apostille_code": apostille_code_match.group(1)
        if apostille_code_match
        else None,
        "security_code": security_code_match.group(1) if security_code_match else None,
        "case_number": case_num_match.group(1) if case_num_match else None,
        "declarations": {
            "seal_claimed": has_seal_declaration,
            "signature_claimed": has_signature_declaration,
        },
        "raw_text_length": len(clean_text),
    }


def analyze_part_b_heraldic_seals(image_path: str) -> dict:
    img = cv2.imread(image_path)
    if img is None:
        return {"round_seals_count": 0, "detected_seals": []}

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    blue_mask = cv2.inRange(hsv, np.array([90, 40, 40]), np.array([140, 255, 255]))
    red_mask1 = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255]))
    red_mask2 = cv2.inRange(hsv, np.array([170, 50, 50]), np.array([180, 255, 255]))
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    combined_mask = cv2.bitwise_or(blue_mask, red_mask)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    closed_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(
        closed_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    detected_seals = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 1200:
            continue

        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue

        circularity = (4 * math.pi * area) / (perimeter**2)
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w) / h

        if circularity >= 0.65 and (0.80 <= aspect_ratio <= 1.25):
            cnt_mask = np.zeros(closed_mask.shape, dtype=np.uint8)
            cv2.drawContours(cnt_mask, [cnt], -1, 255, -1)
            blue_px = cv2.countNonZero(cv2.bitwise_and(blue_mask, cnt_mask))
            red_px = cv2.countNonZero(cv2.bitwise_and(red_mask, cnt_mask))
            seal_color = "Фиолетовый/Синий" if blue_px >= red_px else "Красный"

            detected_seals.append(
                {
                    "type": "Круглая гербовая печать",
                    "color": seal_color,
                    "metrics": {
                        "circularity": round(circularity, 3),
                        "aspect_ratio": round(aspect_ratio, 2),
                        "area_px": int(area),
                        "bounding_box": [x, y, w, h],
                    },
                }
            )

    return {"round_seals_count": len(detected_seals), "detected_seals": detected_seals}


def run_transient_verification(pdf_path: str, page_number: int = 1) -> dict:
    temp_dir = tempfile.mkdtemp(prefix="actor_transient_verify_")
    verification_summary = {}

    try:
        doc = fitz.open(pdf_path)
        if page_number > len(doc):
            raise ValueError(
                f"Страница {page_number} отсутствует в документе (всего {len(doc)} стр.)"
            )

        page = doc[page_number - 1]
        raw_text = page.get_text()
        part_a_data = extract_part_a_metadata(raw_text)

        pix = page.get_pixmap(dpi=300)
        temp_img_path = os.path.join(temp_dir, f"page_{page_number}_stream.png")
        pix.save(temp_img_path)

        frame_sha256 = compute_sha256(pix.tobytes())
        part_b_data = analyze_part_b_heraldic_seals(temp_img_path)

        seal_claimed = part_a_data["declarations"]["seal_claimed"]
        seal_found = part_b_data["round_seals_count"] > 0

        if seal_claimed and seal_found:
            integrity_status = "VERIFIED_MATCH"
        elif not seal_claimed and not seal_found:
            integrity_status = "VERIFIED_EMPTY"
        elif seal_claimed and not seal_found:
            integrity_status = "ALERT_MISSING_PHYSICAL_SEAL"
        else:
            integrity_status = "ALERT_UNDECLARED_SEAL_PRESENT"

        verification_summary = {
            "page_analyzed": page_number,
            "transient_frame_hash": frame_sha256,
            "part_a": part_a_data,
            "part_b": part_b_data,
            "cross_verification": {
                "seal_claimed_in_a": seal_claimed,
                "round_seal_found_in_b": seal_found,
                "status": integrity_status,
            },
            "storage_lifecycle": "PURGED_FROM_DISK",
        }

    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    return verification_summary


if __name__ == "__main__":
    sample_pdf = "recovered_evidence/Реестр_полный_EVIDENCE.pdf"
    if os.path.exists(sample_pdf):
        report = run_transient_verification(sample_pdf, page_number=1)
        print(json.dumps(report, indent=2, ensure_ascii=False))
