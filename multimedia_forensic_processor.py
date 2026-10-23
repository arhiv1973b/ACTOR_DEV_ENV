import os
import cv2
import easyocr
import pytesseract
from typing import List, Dict, Any

class MultimediaProcessor:
    """
    Unified processor for OCR and Audio analysis for CASE-MACHERET-1997-2026.
    Supports ru/ro languages and dual-engine OCR.
    """

    def __init__(self, languages: List[str] = ['ru', 'ro', 'en']):
        self.languages = languages
        # EasyOCR: ru and ro both need en for compatibility in some versions
        # Refactoring to handle separate readers if necessary, but starting with unified
        try:
            self.easy_reader = easyocr.Reader(languages, gpu=False)
        except Exception:
            # Fallback if combined ru+ro fails: prioritize ru+en
            self.easy_reader = easyocr.Reader(['ru', 'en'], gpu=False)
        
        # Tesseract configuration for ru/ro
        self.tess_config = f"-l {'+'.join(['rus', 'ron', 'eng'])} --oem 3 --psm 3"

    def perform_ocr_easyocr(self, image_path: str) -> List[Dict[str, Any]]:
        """Extracts text using EasyOCR."""
        results = self.easy_reader.readtext(image_path)
        extracted = []
        for (bbox, text, prob) in results:
            extracted.append({
                "text": text,
                "confidence": float(prob),
                "bbox": [list(map(int, pt)) for pt in bbox]
            })
        return extracted

    def perform_ocr_tesseract(self, image_path: str) -> str:
        """Extracts text using Tesseract."""
        image = cv2.imread(image_path)
        if image is None:
            return ""
        # Convert to grayscale for better OCR
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, config=self.tess_config)
        return text.strip()

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Runs dual-engine OCR on an image."""
        report = {
            "image_path": image_path,
            "easyocr": self.perform_ocr_easyocr(image_path),
            "tesseract": self.perform_ocr_tesseract(image_path)
        }
        return report

    def transcribe_audio(self, audio_path: str, engine: str = 'vosk') -> Dict[str, Any]:
        """Placeholder for Whisper/Vosk transcription."""
        # Implementation depends on model availability
        return {
            "audio_path": audio_path,
            "engine": engine,
            "status": "NOT_IMPLEMENTED",
            "note": "Requires ffmpeg and local model weights"
        }

if __name__ == "__main__":
    # Test script initialization
    print("[*] Initializing MultimediaProcessor with ru/ro support...")
    try:
        processor = MultimediaProcessor()
        print("[+] Processor ready.")
    except Exception as e:
        print(f"[-] Initialization failed: {e}")
