#!/usr/bin/env python3
"""
MARKDOWN TO PDF CONVERTER FOR PHYSICAL FILING PACKAGE
Case Reference: CASE-MACHERET-1997-2026
"""

import os
from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 9)
        self.set_text_color(100, 100, 100)
        self.cell(
            0,
            8,
            "CASE-MACHERET-1997-2026 | Official Physical Filing Package",
            new_x="LMARGIN",
            new_y="NEXT",
            align="R",
        )
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")


def convert_md_to_pdf(md_path, pdf_path):
    if not os.path.exists(md_path):
        print(f"[!] Markdown file not found: {md_path}")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    plain_text = (
        md_text.replace("#", "").replace("**", "").replace("__", "").replace("`", "")
    )

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("helvetica", "", 10)

    for line in plain_text.splitlines():
        safe_line = line.encode("latin-1", "replace").decode("latin-1")
        if not safe_line.strip():
            pdf.ln(4)
            continue
        if len(safe_line) < 60 and (
            line.startswith("##") or line.startswith("#") or len(line) < 40
        ):
            pdf.set_font("helvetica", "B", 11)
            pdf.cell(0, 6, safe_line, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("helvetica", "", 10)
        else:
            # Wrap long lines using cell or multi_cell correctly
            words = safe_line.split(" ")
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if pdf.get_string_width(test_line) < 180:
                    current_line = test_line
                else:
                    pdf.cell(0, 5, current_line, new_x="LMARGIN", new_y="NEXT")
                    current_line = word
            if current_line:
                pdf.cell(0, 5, current_line, new_x="LMARGIN", new_y="NEXT")

    pdf.output(pdf_path)
    print(f"[SUCCESS] Converted {md_path} -> {pdf_path}")


if __name__ == "__main__":
    files = [
        (
            "PHYSICAL_FILING_PACKAGE_INSTRUCTIONS.md",
            "PHYSICAL_FILING_PACKAGE_INSTRUCTIONS.pdf",
        ),
        (
            "US_EMBASSY_DIPLOMATIC_MEMORANDUM_2026.md",
            "US_EMBASSY_DIPLOMATIC_MEMORANDUM_2026.pdf",
        ),
        (
            "Delivery_Status_Report_CASE_MACHERET.md",
            "Delivery_Status_Report_CASE_MACHERET.pdf",
        ),
    ]
    for md, pdf in files:
        convert_md_to_pdf(md, pdf)
