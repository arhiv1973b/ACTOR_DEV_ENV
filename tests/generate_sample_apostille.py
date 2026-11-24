from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def generate_sample_apostille(output_path):
    c = canvas.Canvas(output_path, pagesize=letter)

    # Page 1: Text
    c.drawString(100, 750, "APOSTILA")
    c.drawString(100, 735, "Convenția de la Haga")
    c.drawString(100, 720, "5 octombrie 1961")
    c.drawString(100, 700, "Security code: 2013073817848")
    c.showPage()

    # Page 2: Image/Blank (OCR target)
    c.drawString(100, 750, "Acesta este un test OCR. Pagina doi.")
    c.showPage()

    # Page 3: Text
    c.drawString(100, 750, "Document support page.")
    c.showPage()

    # Page 4: Image/Blank (OCR target)
    c.drawString(100, 750, "Pagina patru OCR.")
    c.showPage()

    c.save()


if __name__ == "__main__":
    import os

    os.makedirs("tests/data", exist_ok=True)
    generate_sample_apostille("tests/data/sample_apostille.pdf")
    print("PDF generated successfully.")
