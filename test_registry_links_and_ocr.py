import os
import re
import urllib.request
import urllib.error
import pypdf

REGISTRY_URLS = [
    "https://arhiv1973b.github.io/apostille-archive-english/",
    "https://arhiv1973b.github.io/apostille-mirror/",
    "https://github.com/arhiv1973b/apostille-mirror",
    "https://github.com/arhiv1973b/apostille-archive-english"
]

def check_link(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return url, resp.status
    except urllib.error.HTTPError as e:
        return url, e.code
    except Exception:
        return url, "ERR"

def test_pdf_ocr_from_page_2(pdf_path):
    """
    Simulates / tests OCR text extraction starting from page 2 (index 1) of the document,
    supporting both Russian and Romanian language inspection.
    """
    try:
        reader = pypdf.PdfReader(pdf_path)
        num_pages = len(reader.pages)
        extracted_text = ""
        # Start OCR/extraction from page 2 (index 1) onwards
        start_page = 1 if num_pages > 1 else 0
        for i in range(start_page, num_pages):
            txt = reader.pages[i].extract_text() or ""
            extracted_text += txt
        
        has_ru = bool(re.search(r'[А-Яа-яЁё]', extracted_text))
        has_ro = bool(re.search(r'[ăâîșțĂÂÎȘȚ]', extracted_text)) or ('si' in extracted_text.lower() or 'pentru' in extracted_text.lower())
        
        return {
            "file": os.path.basename(pdf_path),
            "total_pages": num_pages,
            "tested_from_page": start_page + 1,
            "status": "SUCCESS",
            "detected_russian": has_ru,
            "detected_romanian": has_ro,
            "char_count": len(extracted_text)
        }
    except Exception as e:
        return {
            "file": os.path.basename(pdf_path),
            "status": "ERROR",
            "error": str(e)
        }

def main():
    print("=== REGISTRY LINK AUDIT (Broken vs Active) ===")
    for url in REGISTRY_URLS:
        u, status = check_link(url)
        print(f"URL: {u} -> Status: {status}")
        
    print("\n=== BILINGUAL OCR TEST (Starting from Page 2) ===")
    pdf_files = []
    for root, _, files in os.walk(r"H:\ACTOR_DEV_ENV"):
        if any(p in root for p in [".git", ".venv", "node_modules"]):
            continue
        for f in files:
            if f.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, f))
                
    # Limit test to sample key PDFs to ensure fast execution
    sample_pdfs = pdf_files[:5]
    for pdf in sample_pdfs:
        res = test_pdf_ocr_from_page_2(pdf)
        print(res)

if __name__ == "__main__":
    main()
