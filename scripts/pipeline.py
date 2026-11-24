#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import re
from pathlib import Path

import fitz

LOGGER = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

CODE_RE = re.compile(
    r"apostileCode/([A-Z0-9]+)/securityCode/(\d+)",
    re.IGNORECASE,
)

URL_RE = re.compile(
    r"https://apostila\.gov\.md/[^\s<>\"']+",
    re.IGNORECASE,
)


def build_url(
    apostille_code: str,
    security_code: str,
) -> str:
    return (
        "https://apostila.gov.md/apostila/site/downloadApostila/"
        f"apostileCode/{apostille_code}/"
        f"securityCode/{security_code}"
    )


def save_registry_json(
    registry: list,
    output_dir: Path,
    pretty: bool = False,
) -> Path:
    output_path = output_dir / "registry.json"

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            registry,
            f,
            ensure_ascii=False,
            indent=2 if pretty else None,
        )

    return output_path


def save_manifest(
    registry: list,
    registry_path: Path,
    output_dir: Path,
) -> Path:
    manifest = {
        "entries": len(registry),
        "registry_file": str(registry_path),
    }

    manifest_path = output_dir / "manifest.json"

    with manifest_path.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            manifest,
            f,
            indent=2,
            ensure_ascii=False,
        )

    return manifest_path


def extract_codes(text: str):
    """
    Primary extraction method.
    """

    for match in CODE_RE.finditer(text):
        yield (
            match.group(1).upper(),
            match.group(2),
        )


def extract_codes_from_urls(text: str):
    """
    Fallback extraction via full URLs.
    """

    for url in URL_RE.findall(text):
        m = CODE_RE.search(url)

        if not m:
            continue

        yield (
            m.group(1).upper(),
            m.group(2),
        )


def process_registry_pdf(
    pdf_path: str | Path,
    output_dir: Path,
    pretty: bool = False,
) -> list:
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    registry = []
    seen = set()

    LOGGER.info(
        "Opening PDF: %s",
        pdf_path,
    )

    doc = fitz.open(pdf_path)

    try:
        for page_number, page in enumerate(
            doc,
            start=1,
        ):
            text: str = page.get_text("text") or ""

            # --------------------------------------------------
            # Main extraction
            # --------------------------------------------------

            for apostille_code, security_code in extract_codes(text):
                key = (
                    apostille_code,
                    security_code,
                )

                if key in seen:
                    continue

                seen.add(key)

                registry.append(
                    {
                        "apostille": apostille_code,
                        "security_code": security_code,
                        "url": build_url(
                            apostille_code,
                            security_code,
                        ),
                        "page": page_number,
                    }
                )

            # --------------------------------------------------
            # Fallback extraction from full URLs
            # --------------------------------------------------

            for apostille_code, security_code in extract_codes_from_urls(text):
                key = (
                    apostille_code,
                    security_code,
                )

                if key in seen:
                    continue

                seen.add(key)

                registry.append(
                    {
                        "apostille": apostille_code,
                        "security_code": security_code,
                        "url": build_url(
                            apostille_code,
                            security_code,
                        ),
                        "page": page_number,
                    }
                )

    finally:
        doc.close()

    # Контрольная проверка количества записей
    MIN_EXPECTED_RECORDS = 80
    if len(registry) < MIN_EXPECTED_RECORDS:
        raise RuntimeError(
            f"Unexpected registry size: {len(registry)}. Expected at least {MIN_EXPECTED_RECORDS}."
        )

    LOGGER.info(
        "Extracted %s unique records",
        len(registry),
    )

    registry_path = save_registry_json(
        registry,
        output_dir,
        pretty,
    )

    if not registry_path.exists():
        raise RuntimeError("registry.json was not created")

    manifest_path = save_manifest(
        registry,
        registry_path,
        output_dir,
    )

    if not manifest_path.exists():
        raise RuntimeError("manifest.json was not created")

    return registry


def parse_args():
    parser = argparse.ArgumentParser(description="Extract apostille registry from PDF")

    parser.add_argument(
        "pdf",
        help="Registry PDF file",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="output",
        help="Output directory",
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty JSON formatting",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    pdf_path = Path(args.pdf)

    output_dir = Path(args.output)
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    registry = process_registry_pdf(
        pdf_path=pdf_path,
        output_dir=output_dir,
        pretty=args.pretty,
    )

    print(f"[OK] Extracted {len(registry)} unique records")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        LOGGER.exception("Pipeline failed")
        raise
