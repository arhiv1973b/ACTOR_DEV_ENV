#!/usr/bin/env python3
"""
Rebuilds apostille_80UQ636YBZG17_2013073978518.pdf with a clean text layer (Page 1 Apostille, Page 2 Curtea de Apel Chișinău letter mentioning judge Sergiu Furdui).
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.drawString(540, 30, f"{self._pageNumber} / {page_count}")
        self.restoreState()

def build_pdf(filename):
    c = NumberedCanvas(filename, pagesize=letter)
    
    # --- PAGE 1: APOSTILLE ---
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(300, 750, "APOSTILLE")
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(300, 735, "(Convention de La Haye du 5 octobre 1961)")
    
    c.setFont("Helvetica", 10)
    y = 700
    lines_p1 = [
        "1. Statul / Country / Pays: Republica Moldova",
        "Prezentul act oficial / This public document",
        "2. a fost semnat de către / has been signed by: Iordan Iurie",
        "3. în calitatea sa de / acting in the capacity of: Vicepresedinte interimar",
        "4. şi poarta sigiliul/ştampila / bears the seal of: Curtea de Apel Chisinau",
        "Confirmat / Certified / Atteste",
        "5. la Agenția Resurse Informaționale Juridice",
        "6. pe data: 07-07-2021",
        "7. de către: Valeriu Frimu",
        "8. cu nr: 8OUQ636YBZGI7",
        "9. Nu se aplică / Not applicable",
        "10. Semnătura digitală / Digital signature",
        "Codul de siguranță: 2013073978518",
        "www.apostila.gov.md"
    ]
    for line in lines_p1:
        c.drawString(50, y, line)
        y -= 25

    c.showPage()

    # --- PAGE 2: CURTEA DE APEL CHISINAU LETTER ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 750, "CURTEA DE APEL CHIŞINĂU")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(450, 750, "CHISINAU COURT OF APPEAL")
    
    c.setFont("Helvetica", 9)
    c.drawString(150, 730, "2043, mun. Chișinău, str. Teilor 4")
    c.drawString(450, 730, "4 Teilor str., Chișinău 2043")
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 680, "09.04.21 № 4-3576-677")
    
    c.drawString(450, 660, "Maceret Alexei Artur")
    c.drawString(450, 645, "mun. Chișinău, str. A. Doga, 30 ap.38")
    
    c.setFont("Helvetica", 10)
    text_p2 = [
        "Prin prezenta, Curtea de Apel Chișinău la cererea înregistrată cu nr.6559e din",
        "01.04.2021 vă comunică că din conținutul ei nu sunt clar cerințele.",
        "Totodată vă comunicăm că cauza penală cu nr. 1a-24/21 (nr.1-272/2003 din",
        "21.02.2003) în privința lui Maceret A., aflată în procedura judecătorului Sergiu Furdui,",
        "a fost redistribuită spre examinare altui judecător.",
        "Despre locul, data și ora examinării cauzei veți fi înștiințat în conformitate cu",
        "legislația în vigoare."
    ]
    y = 580
    for line in text_p2:
        c.drawString(50, y, line)
        y -= 20

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 420, "Vicepreședintele interimar")
    c.drawString(50, 405, "al Curții de Apel Chișinău")
    c.drawString(450, 420, "Iurie Iordan")

    c.setFont("Helvetica", 9)
    c.drawString(50, 350, "Ex. M.Axenti")
    c.drawString(50, 335, "Тел. 022 635323")

    c.showPage()
    c.save()
    print(f"PDF successfully rebuilt: {filename}")

if __name__ == "__main__":
    target = Path(r"H:\ACTOR_DEV_ENV\apostille_80UQ636YBZG17_2013073978518.pdf")
    build_pdf(str(target))
