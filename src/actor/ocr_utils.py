from __future__ import annotations
import os
from pathlib import Path
from pypdf import PdfReader

APOSTILLE_MARKERS = [
    "APOSTILLE",
    "APOSTILA",
    "АПОСТИЛЬ",
    "CONVENTION DE LA HAYE",
    "CONVENTIA DE LA HAGA",
    "5 OCTOBER 1961",
    "5 OCTOMBRIE 1961",
    "SECURITY CODE",
    "APOSTILA.GOV.MD",
]


def detect_document_type(first_page_text: str, file_path: str) -> str:
    # Проверка по имени файла
    filename = Path(file_path).name.lower()
    if "apostila" in filename or "apostille" in filename:
        return "apostille"

    # Проверка по содержимому
    text = first_page_text.upper()
    score = sum(1 for marker in APOSTILLE_MARKERS if marker in text)

    return "apostille" if score >= 2 else "other"


def should_force_ocr(page_number: int, document_type: str) -> bool:
    if document_type != "apostille":
        return False
    # Четные страницы начиная со 2-й для апостилей
    return page_number > 1 and page_number % 2 == 0
