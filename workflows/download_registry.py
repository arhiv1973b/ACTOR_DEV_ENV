from __future__ import annotations
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import requests
from pypdf import PdfReader


REGISTRY_PDF = os.environ.get(
    "REGISTRY_PDF", "/app/registry/apostille_registry_working_18.signed.pdf"
)

OUTPUT_DIR = Path("registry")

DOWNLOAD_DIR = Path("downloaded_apostilles")

BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "10"))

MIN_EXPECTED_RECORDS = 90

USER_AGENT = "ACTOR/2.0 Apostille Downloader"

URL_RE = re.compile(
    r"(https://apostila\.gov\.md/"
    r"apostila/site/downloadApostila/"
    r"apostileCode/[A-Z0-9]+/"
    r"securityCode/\d+)"
)

DETAIL_RE = re.compile(
    r"apostileCode/([A-Z0-9]+)/"
    r"securityCode/(\d+)"
)

TOTAL_RE = re.compile(r"Всего записей:\s*(\d+)")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with open(path, "rb") as fp:
        while chunk := fp.read(65536):
            digest.update(chunk)

    return digest.hexdigest()


def extract_registry() -> tuple[list[dict], int | None]:
    if not Path(REGISTRY_PDF).exists():
        raise FileNotFoundError(f"Registry PDF not found: {REGISTRY_PDF}")

    reader = PdfReader(REGISTRY_PDF)
    urls = set()

    print(f"[*] Сканирование текста и аннотаций в файле: {Path(REGISTRY_PDF).name}")

    # 1. Сканирование текста
    for page in reader.pages:
        text = page.extract_text() or ""
        matches = URL_RE.findall(text)
        urls.update(matches)

    # 2. Сканирование аннотаций (более надежный метод)
    for page in reader.pages:
        if "/Annots" in page:
            annots_obj = page["/Annots"].get_object()
            if isinstance(annots_obj, list):
                for annot in annots_obj:
                    annot_obj = annot.get_object()
                    if "/A" in annot_obj:
                        action = annot_obj["/A"].get_object()
                        if "/URI" in action:
                            uri = action["/URI"]
                            if isinstance(uri, bytes):
                                uri = uri.decode("utf-8", errors="ignore")
                            if uri and "apostila.gov.md" in uri:
                                urls.add(uri)

    # 3. Сканирование сырых данных
    raw_data = Path(REGISTRY_PDF).read_bytes()
    # Ищем все ссылки, которые начинаются с https://apostila.gov.md
    # и содержат apostila/site/downloadApostila
    matches = re.findall(
        b"https://apostila\\.gov\\.md/apostila/site/downloadApostila/[^\\s<>\"']+",
        raw_data,
    )
    for match in matches:
        urls.add(match.decode("utf-8", errors="ignore"))

    # Исправим: сделаем urls списком, а для дедупликации используем set внутри
    unique_urls = list(set(urls))
    print(f"[✓] Успешно извлечено уникальных ссылок: {len(unique_urls)}")

    if not unique_urls:
        raise RuntimeError("No apostille URLs found inside PDF")

    registry = []
    seen = set()

    for url in unique_urls:
        m = DETAIL_RE.search(url)
        if not m:
            continue

        code = m.group(1)
        security = m.group(2)
        key = f"{code}:{security}"

        if key in seen:
            continue

        seen.add(key)

        registry.append(
            {
                "num": len(registry) + 1,
                "apostille_code": code,
                "security_code": security,
                "url": url,
                "downloaded": False,
                "sha256": None,
                "page_count": 0,
                "ocr_required": True,
                "ocr_strategy": "force_even_pages",
                "average_ocr_confidence": None,
                "manual_review_required": False,
                "manual_review_pages": [],
                "ocr_report_path": None,
                "handwriting_report_path": None,
            }
        )

    registry = sorted(registry, key=lambda x: x["num"])

    return registry, None


def validate_downloaded_pdf(pdf_path: Path) -> int:
    reader = PdfReader(pdf_path)

    page_count = len(reader.pages)

    if page_count == 0:
        raise RuntimeError(f"Empty PDF: {pdf_path}")

    return page_count


def create_batches(registry: list[dict]) -> list[str]:
    batches: list[str] = []

    for start in range(0, len(registry), BATCH_SIZE):
        batch_number = (start // BATCH_SIZE) + 1

        batch_name = f"batch_{batch_number:02d}"

        batch_file = OUTPUT_DIR / f"{batch_name}.json"

        with open(batch_file, "w", encoding="utf-8") as fp:
            json.dump(
                registry[start : start + BATCH_SIZE], fp, ensure_ascii=False, indent=2
            )

        batches.append(batch_name)

    return batches


def save_json(path: Path, data) -> None:
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    registry, declared = extract_registry()
    actual = len(registry)

    # Аудит
    save_json(
        OUTPUT_DIR / "url_validation_report.json",
        {
            "declared_records": declared,
            "actual_urls": actual,
            "missing_count": (declared - actual) if declared else 0,
            "unique_urls": actual,
        },
    )

    if declared and actual < declared:
        print(f"[-] Warning: Missing {declared - actual} records")

    success_count = 0
    fail_count = 0

    with requests.Session() as session:
        session.headers.update({"User-Agent": USER_AGENT})

        for item in registry:
            filename = f"{item['num']:03d}_{item['apostille_code']}.pdf"

            pdf_path = DOWNLOAD_DIR / filename

            try:
                response = session.get(item["url"], timeout=30)

                response.raise_for_status()

                content_type = response.headers.get("Content-Type", "").lower()

                if "pdf" not in content_type and len(response.content) < 1000:
                    raise RuntimeError("Downloaded file is suspicious")

                with open(pdf_path, "wb") as fp:
                    fp.write(response.content)

                item["page_count"] = validate_downloaded_pdf(pdf_path)

                if item["page_count"] <= 0:
                    raise RuntimeError("Downloaded PDF has no pages")

                item["downloaded"] = True

                item["sha256"] = sha256_file(pdf_path)

                success_count += 1

            except Exception as exc:
                if pdf_path.exists():
                    pdf_path.unlink()

                item["downloaded"] = False

                item["error"] = str(exc)

                fail_count += 1

                print(f"[-] Failed {item['apostille_code']}: {exc}")

    if success_count == 0:
        raise RuntimeError("No apostilles downloaded")

    save_json(OUTPUT_DIR / "apostilles_manifest.json", registry)

    batches = create_batches(registry)

    save_json(OUTPUT_DIR / "batches.json", batches)

    save_json(
        OUTPUT_DIR / "download_report.json",
        {
            "total_records": len(registry),
            "success": success_count,
            "failed": fail_count,
            "success_rate": round(success_count / len(registry) * 100, 2),
            "records": registry,
        },
    )

    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as fp:
            fp.write(f"batches={json.dumps(batches)}\n")

    print(f"Downloaded: {success_count}")

    print(f"Failed: {fail_count}")


if __name__ == "__main__":
    try:
        main()

    except Exception as exc:
        print(f"Critical Error: {exc}")

        sys.exit(1)
