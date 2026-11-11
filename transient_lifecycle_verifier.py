import os
import re
import cv2
import json
import math
import hashlib
import fitz  # PyMuPDF
import numpy as np


def compute_sha256(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def extract_part_a_exact(doc):
    page_1 = doc[0]
    text = page_1.get_text()

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


def cleanup_sidecar_files(pdf_path: str):
    abs_pdf_path = os.path.abspath(pdf_path)
    pdf_dir = os.path.dirname(abs_pdf_path)
    pdf_stem = os.path.splitext(os.path.basename(abs_pdf_path))[0]

    removable_extensions = (
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tif",
        ".tiff",
        ".ocr",
        ".hocr",
        ".alto.xml",
        ".txt",
    )

    try:
        for filename in os.listdir(pdf_dir):
            if filename.startswith(pdf_stem) and not filename.endswith(
                "_verification.json"
            ):
                lower = filename.lower()
                if any(lower.endswith(ext) for ext in removable_extensions):
                    try:
                        os.remove(os.path.join(pdf_dir, filename))
                    except Exception:
                        pass
    except Exception:
        pass


def verify_single_apostille_pdf(pdf_path: str) -> dict:
    abs_pdf_path = os.path.abspath(pdf_path)
    if not os.path.exists(abs_pdf_path):
        return {"status": "ERROR", "error": f"Файл не найден: {abs_pdf_path}"}

    try:
        pdf_sha256 = compute_sha256(abs_pdf_path)

        with fitz.open(abs_pdf_path) as doc:
            part_a = extract_part_a_exact(doc)
            part_b = scan_part_b_heraldic_stream(doc)

        total_seals = sum(page["seals_found"] for page in part_b)

        if part_a.get("apostille_nr") and total_seals > 0:
            status = "VERIFIED_SUCCESS"
        elif part_a.get("apostille_nr"):
            status = "PART_A_ONLY"
        elif total_seals > 0:
            status = "PART_B_ONLY"
        else:
            status = "FAILED"

        report = {
            "status": status,
            "evidence_sha256": pdf_sha256,
            "part_a": part_a,
            "part_b_summary": {
                "scanned_pages": len(part_b),
                "total_seals": total_seals,
                "breakdown": part_b,
            },
            "pdf_deleted": False,
            "temporary_files_cleaned": False,
        }

        if status != "FAILED":
            report_path = os.path.splitext(abs_pdf_path)[0] + "_verification.json"
            cleanup_sidecar_files(abs_pdf_path)
            report["temporary_files_cleaned"] = True

            try:
                os.remove(abs_pdf_path)
                report["pdf_deleted"] = True
            except Exception as delete_error:
                report["pdf_deleted"] = False
                report["pdf_delete_error"] = str(delete_error)

            with open(report_path, "w", encoding="utf-8") as fp:
                json.dump(report, fp, ensure_ascii=False, indent=2)

        return report

    except Exception as exc:
        return {
            "status": "ERROR",
            "error": str(exc),
            "pdf_deleted": False,
            "temporary_files_cleaned": False,
        }


if __name__ == "__main__":
    sample_pdf = "recovered_evidence/3HWVD912FN7H4_EVIDENCE.pdf"
    if os.path.exists(sample_pdf):
        print(f"[*] Запуск транзитного жизненного цикла для: {sample_pdf}")
        res = verify_single_apostille_pdf(sample_pdf)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("[-] Файл не найден.")
