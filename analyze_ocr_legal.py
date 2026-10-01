import json
import re
import os

INPUT_FILE = "pdf_manifest.json"
OUTPUT_FILE = "legal_findings_contextual.json"

# Радиус поиска: максимальное количество символов между датой и термином
PROXIMITY_THRESHOLD = 500

LEGAL_TERMS = [
    r"Jus\s*Cogens",
    r"Erga\s*Omnes",
    r"ECHR",
    r"Art\.?\s*3",
    r"Art\.?\s*5",
    r"суд\w*",
    r"иск\w*",
    r"решени\w*",
    r"закон\w*",
    r"обязательств\w*",
    r"договор\w*",
    r"справк\w*",
    r"заявлени\w*",
    r"выплат\w*",
]

NAMES = [r"Macheret", r"Мачерет", r"Alexei", r"Алексей", r"А\.\s*А\.\s*Мачерет"]

DATE_PATTERN = r"\b(?:\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{4}[./-]\d{1,2}[./-]\d{1,2})\b"


def clean_regex_display(pattern):
    return pattern.replace(r"\w*", "").replace(r"\s*", " ").replace(r"\.?", ".").strip()


def analyze_manifest():
    if not os.path.exists(INPUT_FILE):
        print(f"[-] Файл {INPUT_FILE} не найден.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []

    for item in data:
        filename = item.get("filename", "unknown")
        text = item.get("text", "")

        if not text:
            continue

        # Собираем координаты всех юридических терминов в тексте
        term_intervals = []
        found_terms_display = set()

        for term in LEGAL_TERMS:
            for match in re.finditer(term, text, re.IGNORECASE):
                term_intervals.append((match.start(), match.end()))
                found_terms_display.add(clean_regex_display(term))

        # Собираем все даты и проверяем их близость к терминам
        contextual_dates = set()
        for match in re.finditer(DATE_PATTERN, text):
            d_start, d_end = match.start(), match.end()
            date_str = match.group()

            # Проверяем расстояние от даты до каждого найденного термина
            for t_start, t_end in term_intervals:
                # Вычисляем разрыв между концом одного слова и началом другого
                distance = max(0, max(d_start - t_end, t_start - d_end))

                if distance <= PROXIMITY_THRESHOLD:
                    contextual_dates.add(date_str)
                    break  # Дата подтверждена, переходим к следующей

        # Обычный поиск имен (без привязки к дистанции)
        found_names = set()
        for name in NAMES:
            if re.search(name, text, re.IGNORECASE):
                found_names.add(clean_regex_display(name))

        # Сохраняем результат, если есть контекстные даты ИЛИ найдены другие важные маркеры
        if contextual_dates or found_terms_display or found_names:
            results.append(
                {
                    "filename": filename,
                    "matches": {
                        "contextual_dates": list(contextual_dates),
                        "legal_terms": list(found_terms_display),
                        "names": list(found_names),
                    },
                    "preview": text[:200].replace("\n", " ").strip() + "...",
                }
            )

    if results:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        print(f"[+] Анализ завершен. Документов с совпадениями: {len(results)}")
        print(f"[+] Результаты сохранены в {OUTPUT_FILE}\n")

        for res in results[:5]:
            print(f"Файл: {res['filename']}")
            if res["matches"]["contextual_dates"]:
                print(
                    f"  Релевантные даты: {', '.join(res['matches']['contextual_dates'])}"
                )
            print("-" * 40)
    else:
        print("[-] Совпадений по заданным критериям не найдено.")


if __name__ == "__main__":
    analyze_manifest()
