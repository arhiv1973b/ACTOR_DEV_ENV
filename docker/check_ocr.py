import shutil
import pytesseract
import sys

required = {"rus", "ron"}

try:
    installed = set(pytesseract.get_languages(config=""))
except Exception as e:
    print(f"Error checking languages: {e}")
    sys.exit(1)

missing = required - installed

if missing:
    print(f"Missing OCR languages: {', '.join(sorted(missing))}")
    sys.exit(1)

if shutil.which("tesseract") is None:
    print("tesseract executable missing")
    sys.exit(1)

if shutil.which("pdftoppm") is None:
    print("poppler executable missing")
    sys.exit(1)

print("OCR environment OK")
