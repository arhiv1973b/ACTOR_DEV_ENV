import pytest
import json
import os
import subprocess
from pathlib import Path


def test_ocr_pipeline_e2e(tmp_path):
    # Setup paths
    input_pdf = "tests/data/sample_apostille.pdf"
    output_dir = tmp_path / "ocr_output"

    # Run pipeline
    result = subprocess.run(
        [
            "python",
            "workflows/process_pdf.py",
            "--input",
            input_pdf,
            "--output",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    # Check report
    report_path = output_dir / "ocr" / "ocr_report.json"
    assert report_path.exists()

    with open(report_path) as f:
        report = json.load(f)

    assert report["document_type"] == "apostille"
    assert report["ocr_strategy"] == "force_even_pages"

    methods = {p["page"]: p["method"] for p in report["pages"]}
    assert methods[2] == "forced_ocr"
    assert methods[4] == "forced_ocr"

    # Check artifacts existence
    assert (output_dir / "ocr" / "images" / "page_002.png").exists()
    assert (output_dir / "ocr" / "images" / "page_002.png").stat().st_size > 0
    assert (output_dir / "ocr" / "images" / "page_004.png").exists()
    assert (output_dir / "ocr" / "images" / "page_004.png").stat().st_size > 0

    assert (output_dir / "ocr" / "text" / "page_002.txt").exists()
    assert (output_dir / "ocr" / "text" / "page_004.txt").exists()
