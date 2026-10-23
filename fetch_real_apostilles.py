#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import ssl
import urllib.request

DATA = [
    (36, "DLTP7B8ZHWGQ7", "2013074484667"),
    (41, "CG0T6Y1TBUEL7", "2013074491511"),
    (65, "80UQ636YBZG17", "2013073978518"),
    (68, "DFVMD2FQLW5N3", "2013074809675"),
    (69, "IMTQ930Z8U4N7", "2013074678387"),
    (70, "HQ7X9W62GUJL9", "2013074330087"),
    (71, "BS7XCZF1EUJG3", "2013074500114"),
    (77, "403WF02QGRCI1", "2013074897031"),
    (79, "DQ1N892ZFXDI3", "2013074979347"),
    (85, "6R2V5Z4XBZBH8", "2013074509902"),
    (86, "IT1PD8E29S5F5", "2013074897031"),
    (90, "4J20E98WFY7J2", "2013074672491"),
    (93, "6OZUD89VBUEJ3", "2013074732485"),
    (96, "IHW093CZ8U8R7", "2013074538582"),
]


def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for item_id, code, security_code in DATA:
        url = f"https://apostila.gov.md/apostila/site/downloadApostila/apostileCode/{code}/securityCode/{security_code}"
        filename = f"apostille_{code}.pdf"

        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
            )
            with urllib.request.urlopen(req, context=ctx, timeout=20) as response:
                content = response.read()
                size = len(content)

                if size < 1024:
                    print(
                        f"[FAILED] ID {item_id} ({code}): Size is {size} bytes (stub). Skipped."
                    )
                else:
                    with open(filename, "wb") as f:
                        f.write(content)
                    print(
                        f"[SUCCESS] ID {item_id} ({code}) downloaded. Size: {size // 1024} KB -> {filename}"
                    )
        except Exception as e:
            print(f"[FAILED] ID {item_id} ({code}): {e}")


if __name__ == "__main__":
    main()
