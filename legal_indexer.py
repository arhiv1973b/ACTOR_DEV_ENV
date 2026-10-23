import json, pathlib, re

BASE_DIR = pathlib.Path(__file__).parent.resolve()
HTML_FILE = BASE_DIR / "un_treaties_page.html"
INDEX_FILE = BASE_DIR / "vclt_index.json"

def parse_articles():
    if not HTML_FILE.exists():
        print(f"❌ Файл {HTML_FILE} не найден.")
        return
    
    with HTML_FILE.open("r", encoding="utf-8") as f:
        content = f.read()
    
    # Ищем все, что похоже на "Статья 1", "Статья 2..." 
    # [ \n\r]+.*?\d+\.? - захватывает перенос строки, слово и цифру
    articles = {}
    # Регулярка для поиска заголовков статей в любом регистре
    matches = list(re.finditer(r"(?:Статья|Article)\s+(\d+)", content, re.IGNORECASE))
    
    for i in range(len(matches)):
        start = matches[i].end()
        end = matches[i+1].start() if i+1 < len(matches) else len(content)
        num = matches[i].group(1)
        text = content[start:end].strip()
        articles[num] = {"title": f"Статья {num}", "content": text[:500]}
            
    with INDEX_FILE.open("w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print(f"✅ Индекс создан, добавлено статей: {len(articles)}")

if __name__ == "__main__":
    parse_articles()
