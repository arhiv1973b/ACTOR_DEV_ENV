#!/usr/bin/env python3
"""
QR CODE GENERATOR FOR EVIDENCE PORTALS
Case Reference: CASE-MACHERET-1997-2026
"""

import sys
import argparse


def generate_qr(url, output):
    try:
        import qrcode

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output)
        print(f"[SUCCESS] QR code saved to {output} for URL: {url}")
    except ImportError:
        print(
            "[WARN] 'qrcode' library not installed. Generating dummy placeholder image."
        )
        from PIL import Image, ImageDraw

        img = Image.new("RGB", (300, 300), color="white")
        d = ImageDraw.Draw(img)
        d.text((10, 140), f"QR: {url[:30]}...", fill="black")
        img.save(output)
        print(f"[SUCCESS] Placeholder QR image saved to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate QR code for evidence links.")
    parser.add_argument("--url", required=True, help="URL to encode in QR code")
    parser.add_argument("--output", required=True, help="Output image filename")
    args = parser.parse_args()
    generate_qr(args.url, args.output)
