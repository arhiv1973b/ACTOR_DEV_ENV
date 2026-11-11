import os
import re
import requests
import pathlib
import urllib.parse

html_content = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Moldcell подписан</title>
</head>
<body>
    <h1>Moldcell подписан</h1>

    <ul>
        <li>
            <a href="https://raw.githubusercontent.com/arhiv1973b/ACTOR_EVIDENCE_MOLDCELL/main/docs/%D0%9C%D0%BE%D0%BB%D0%B4%D1%87%D0%B5%D0%BB%D0%BB.privind%20tehnologia%20informa%C5%A3iei%20Capitalul%20social%20190001000%20Lei.pdf">
                Молдчелл.pdf
            </a>
        </li>

        <li>
            <a href="https://raw.githubusercontent.com/arhiv1973b/ACTOR_EVIDENCE_MOLDCELL/main/docs/Moldcell.pdf">
                Moldcell.pdf
            </a>
        </li>

        <li>
            <a href="https://raw.githubusercontent.com/arhiv1973b/ACTOR_EVIDENCE_MOLDCELL/main/docs/Stimate%20Judecator%20V.%20Dodon%20si%20ai%20Moldcell.%D0%BF%D0%BE%D0%B4%D0%BF%D0%B8%D1%81%D0%B0%D0%BD.pdf">
                Stimate Judecator V. Dodon si ai Moldcell
            </a>
        </li>

        <li>
            <a href="https://raw.githubusercontent.com/arhiv1973b/ACTOR_EVIDENCE_MOLDCELL/main/docs/%D0%A1%D1%83%D0%B4%D1%8C%D0%B5%20%D0%94%D0%BE%D0%B4%D0%BE%D0%BD%20%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D0%BD%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D1%8B%D0%B5%20%D0%BB%D0%B8%D1%81%D1%82%D1%8B.html">
                Судье Додон исполнительные листы
            </a>
        </li>

        <li>
            <a href="https://raw.githubusercontent.com/arhiv1973b/ACTOR_EVIDENCE_MOLDCELL/main/docs/Cita%C8%9Bie%20MACERET%20ALEXEI%20vs.%20CONSILIUL%20PENTRU%20EGALITATE%2C%20SA%20Moldcell%20-%20Ac%C5%A3iuni%20pri.html">
                Citație MACERET ALEXEI
            </a>
        </li>

        <li>
            <a href="https://raw.githubusercontent.com/arhiv1973b/ACTOR_EVIDENCE_MOLDCELL/main/docs/Macheret%20%C3%AEmpotriva%20Consiliului%20pentru%20Egalitate%20%C8%99i%20Protec%C8%9Bie%20Discrimin%C4%83rii%20-%20Moldcell_pdf.html">
                Macheret împotriva Consiliului
            </a>
        </li>

        <li>
            <a href="https://raw.githubusercontent.com/arhiv1973b/ACTOR_EVIDENCE_MOLDCELL/main/docs/Moldcell_%D0%BF%D0%BE%D0%B4%D0%BF%D0%B8%D1%81%D0%B0%D0%BD_pdf.html">
                Moldcell подписан
            </a>
        </li>

        <li>
            <a href="https://raw.githubusercontent.com/arhiv1973b/ACTOR_EVIDENCE_MOLDCELL/main/docs/iCloudPhotos_Photos_Preg%C4%83tirea_declara%C5%A3iei_pentru_instan%C5%A3.pdf_translated.txt">
                Перевод декларации для инстанции
            </a>
        </li>

        <li>
            <a href="https://raw.githubusercontent.com/arhiv1973b/ACTOR_EVIDENCE_MOLDCELL/main/docs/%D0%94%D0%BE%D0%BD%D0%BE%D1%81.pdf_translated.txt">
                Донос (перевод)
            </a>
        </li>
    </ul>
</body>
</html>
"""

def extract_urls(html):
    # Regex to find href attribute values in <a> tags
    urls = re.findall(r'href=["\'](https?://[^"\']+)["\']', html)
    return urls

urls = extract_urls(html_content)
WORKDIR = pathlib.Path("downloads_evidence")
WORKDIR.mkdir(exist_ok=True)

for url in urls:
    filename = pathlib.Path(urllib.parse.unquote(url)).name
    print(f"Downloading {filename}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(WORKDIR / filename, "wb") as f:
            f.write(response.content)
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
