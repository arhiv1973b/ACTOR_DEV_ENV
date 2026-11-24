import requests
import urllib3

# Отключаем предупреждения о не верифицированном SSL для диагностического запроса
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://apostila.gov.md/apostila/site/downloadApostila/apostileCode/BOUS9XAQDTFH2/securityCode/2013073851064"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Minimalist-Browser-Emulator/1.0",
    "Accept": "application/pdf,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

try:
    response = requests.get(
        url, headers=headers, allow_redirects=True, verify=False, timeout=30
    )
    if (
        response.status_code == 200
        and "pdf" in response.headers.get("Content-Type", "").lower()
    ):
        with open("BOUS9XAQDTFH2.pdf", "wb") as f:
            f.write(response.content)
        print(
            "[+] Файл успешно скачан напрямую без посещения сайта (с отключенной SSL-верификацией)."
        )
    else:
        print(f"[-] Ошибка загрузки. HTTP Статус: {response.status_code}")
except Exception as e:
    print(f"[-] Исключение: {e}")
