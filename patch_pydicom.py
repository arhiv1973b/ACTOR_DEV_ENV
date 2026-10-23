import os

# Путь к библиотеке, где происходит сбой (на основе лога ошибок)
pydicom_path = r"C:\Python314\Lib\site-packages\pydicom"
target_file = os.path.join(pydicom_path, "pixels", "decoders", "pillow.py")

if os.path.exists(target_file):
    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Патч: заменяем вызов, вызывающий NameError
    old_text = 'return bool(features.check_codec("jpg"))'
    new_text = 'return False # Патч A©tor: пропуск проверки кодека для предотвращения NameError'
    
    if old_text in content:
        patched_content = content.replace(old_text, new_text)
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(patched_content)
        print("Патч успешно применен к pillow.py.")
    else:
        print("Целевая строка не найдена. Возможно, файл уже изменен или структура pydicom другая.")
else:
    print(f"Ошибка: Файл не найден по пути {target_file}")
