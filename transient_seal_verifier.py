import os
import cv2
import json
import math
import shutil
import fitz
import tempfile
import numpy as np


def analyze_seal_geometry_and_color(image_path):
    """
    Классификация печатей по цветовой маске и геометрии контура.
    Возвращает список обнаруженных артефактов без сохранения кадров на диск.
    """
    img = cv2.imread(image_path)
    if img is None:
        return {"detected_count": 0, "seals": []}

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Цветовые маски
    blue_mask = cv2.inRange(hsv, np.array([90, 40, 40]), np.array([140, 255, 255]))
    red_mask1 = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255]))
    red_mask2 = cv2.inRange(hsv, np.array([170, 50, 50]), np.array([180, 255, 255]))
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    combined_mask = cv2.bitwise_or(blue_mask, red_mask)

    # Замыкание микроразрывов чернильных оттисков
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(
        combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    detected_seals = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 1000:
            continue

        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue

        circularity = (4 * math.pi * area) / (perimeter**2)
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w) / h

        cnt_mask = np.zeros(combined_mask.shape, dtype=np.uint8)
        cv2.drawContours(cnt_mask, [cnt], -1, 255, -1)
        blue_pixels = cv2.countNonZero(cv2.bitwise_and(blue_mask, cnt_mask))
        red_pixels = cv2.countNonZero(cv2.bitwise_and(red_mask, cnt_mask))
        color_label = "Синий/Фиолетовый" if blue_pixels >= red_pixels else "Красный"

        approx = cv2.approxPolyDP(cnt, 0.03 * perimeter, True)
        vertices = len(approx)

        seal_class = "Неидентифицированный штамп"
        shape_type = "Произвольная"

        if circularity >= 0.65 and 0.80 <= aspect_ratio <= 1.25:
            shape_type = "Круг"
            seal_class = "Судебная / Гербовая печать"
        elif circularity <= 0.60 and (aspect_ratio > 1.35 or aspect_ratio < 0.70):
            shape_type = "Прямоугольник"
            seal_class = "Министерский / Регистрационный штамп (Апостиль)"
        elif vertices == 3:
            shape_type = "Треугольник"
            seal_class = "Нотариальная / Вспомогательная печать"
        elif circularity >= 0.45 and (1.25 < aspect_ratio <= 1.80):
            shape_type = "Овал"
            seal_class = "Служебный / Заверительный штамп"

        detected_seals.append(
            {
                "class": seal_class,
                "shape": shape_type,
                "color": color_label,
                "metrics": {
                    "circularity": round(circularity, 3),
                    "aspect_ratio": round(aspect_ratio, 3),
                    "area_pixels": int(area),
                    "bounding_box": [x, y, w, h],
                },
            }
        )

    return {"detected_count": len(detected_seals), "seals": detected_seals}


def run_transient_seal_audit(pdf_path, page_number=1):
    temp_dir = tempfile.mkdtemp(prefix="actor_seal_val_")
    result = {}
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_number - 1]

        pix = page.get_pixmap(dpi=300)
        temp_img_path = os.path.join(temp_dir, f"page_{page_number}_transient.png")
        pix.save(temp_img_path)

        seal_analysis = analyze_seal_geometry_and_color(temp_img_path)

        result = {
            "page": page_number,
            "transient_status": "PURGED_AFTER_ANALYSIS",
            "seal_verification": seal_analysis,
        }
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    return result


if __name__ == "__main__":
    target_pdf = "recovered_evidence/Реестр_полный_EVIDENCE.pdf"
    if os.path.exists(target_pdf):
        print(f"[*] Запуск аудита оттисков для: {target_pdf}")
        audit_res = run_transient_seal_audit(target_pdf, page_number=1)
        print(json.dumps(audit_res, ensure_ascii=False, indent=4))
    else:
        print("[-] Целевой PDF не найден.")
