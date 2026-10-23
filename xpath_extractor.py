import lxml.html
import hashlib
import sys

html_path = r'H:\ACTOR_DEV_ENV\source_page.html'
out_path = r'H:\ACTOR_DEV_ENV\apostille-mirror\extracted_script_6.js'

try:
    print(f"[*] Анализ DOM дерева: {html_path}")
    tree = lxml.html.parse(html_path)
    
    # Извлечение по точному XPath
    scripts = tree.xpath('/html/body/script[6]')
    
    if scripts:
        script_content = scripts[0].text or ""
        print(f"[+] Целевой узел найден. Длина полезной нагрузки: {len(script_content)} байт")
        
        # Вычисление хеша
        hash_obj = hashlib.sha256(script_content.encode('utf-8'))
        sha256_hash = hash_obj.hexdigest()
        print(f"[+] SHA-256: {sha256_hash}")
        
        # Сохранение доказательства
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print(f"[+] Данные изолированы в: {out_path}")
        
    else:
        print("[-] ОШИБКА: Узел /html/body/script[6] не найден в документе.")
except Exception as e:
    print(f"[-] КРИТИЧЕСКАЯ ОШИБКА парсинга: {str(e)}")
