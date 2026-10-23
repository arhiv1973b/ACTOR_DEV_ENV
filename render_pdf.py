import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Preformatted,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

MARKDOWN_FILE = "CASE_MACHERET_1997_2026_DOSSIER.md"
PDF_FILE = "CASE_MACHERET_1997_2026_DOSSIER.pdf"


def main():
    if not os.path.exists(MARKDOWN_FILE):
        print(f"Error: {MARKDOWN_FILE} not found.")
        return

    with open(MARKDOWN_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    doc = SimpleDocTemplate(
        PDF_FILE,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DossierTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#111111"),
        spaceAfter=10,
    )

    h2_style = ParagraphStyle(
        "DossierH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#2c3e50"),
        spaceBefore=15,
        spaceAfter=6,
    )

    h3_style = ParagraphStyle(
        "DossierH3",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#34495e"),
        spaceBefore=10,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "DossierBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#222222"),
        spaceAfter=6,
    )

    code_style = ParagraphStyle(
        "DossierCode",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#2980b9"),
        backColor=colors.HexColor("#f8f9fa"),
        borderColor=colors.HexColor("#e9ecef"),
        borderWidth=1,
        borderPadding=6,
        spaceAfter=8,
    )

    story = []
    lines = content.split("\n")
    in_code_block = False
    code_buffer = []

    for line in lines:
        if line.startswith("```"):
            if in_code_block:
                # End code block
                code_text = "\n".join(code_buffer)
                story.append(Preformatted(code_text, code_style))
                code_buffer = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_buffer.append(line)
            continue

        if line.startswith("# "):
            story.append(Paragraph(line[2:], title_style))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], h2_style))
        elif line.startswith("### "):
            story.append(Paragraph(line[4:], h3_style))
        elif line.startswith("---"):
            story.append(Spacer(1, 6))
            story.append(
                HRFlowable(
                    width="100%",
                    thickness=1,
                    color=colors.HexColor("#cccccc"),
                    spaceAfter=10,
                )
            )
        elif line.strip() == "":
            story.append(Spacer(1, 4))
        else:
            # Handle markdown bold / bullet formatting simply
            formatted_line = line.replace("**", "<b>", 1).replace("**", "</b>", 1)
            formatted_line = formatted_line.replace("`", "<code>", 1).replace(
                "`", "</code>", 1
            )
            story.append(Paragraph(formatted_line, body_style))

    doc.build(story)
    print(f"PDF generated successfully via ReportLab: {PDF_FILE}")


if __name__ == "__main__":
    main()
