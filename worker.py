import re
import requests
from bs4 import BeautifulSoup


def extract_and_process_links():
    print("[*] Запуск воркера: чтение реестра апостилей...")

    try:
        with open("apostille_registry_working.html", "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        print("[!] Файл реестра не найден, проверьте путь.")
        return

    # Извлечение всех ссылок вида https://apostila.gov.md/...
    urls = re.findall(r'https://apostila\.gov\.md[^\s<>"]+', html_content)

    # Уникальные ссылки
    unique_urls = list(set(urls))
    print(f"[*] Найдено уникальных ссылок для обработки: {len(unique_urls)}")

    results = []
    for i, url in enumerate(unique_urls, 1):
        try:
            # Воркер проверяет доступность ссылки
            response = requests.head(url, timeout=10)
            status = response.status_code
            print(f"[{i}/{len(unique_urls)}] [Статус: {status}] {url}")
            results.append({"url": url, "status": status})
        except Exception as e:
            print(f"[{i}/{len(unique_urls)}] [Ошибка] {url} -> {e}")
            results.append({"url": url, "status": "ERROR"})

    print("[*] Воркер успешно завершил обработку всех ссылок.")


if __name__ == "__main__":
    extract_and_process_links()
