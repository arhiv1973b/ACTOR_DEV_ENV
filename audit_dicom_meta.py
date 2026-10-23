import sys
import os

# Пути к возможным окружениям, где может быть установлен pydicom
possible_paths = [
    r"C:\A\LLM - ANSI EROR UT-8\chatbot_project\new_chatbot_env\Lib\site-packages",
    r"C:\A\LLM - ANSI EROR UT-8\ml_env\Lib\site-packages",
    r"C:\A\SABOTAGE_RECOVERY\MEDICAL_2022_ORIGINALS"
]

for p in possible_paths:
    if p not in sys.path:
        sys.path.append(p)

try:
    import pydicom
except ImportError:
    print("Ошибка: pydicom не найден в указанных путях. Проверьте окружения.")
    sys.exit(1)

# Файлы для проверки
files_to_check = [
    r"C:\A\SABOTAGE_RECOVERY\MEDICAL_2022_ORIGINALS\DICOM\D202203\DD1412\A2104625",
    r"C:\A\SABOTAGE_RECOVERY\MEDICAL_2022_ORIGINALS\DICOM\D202204\DD0610\A2156682"
]

print("Начинаю анализ метаданных DICOM...")

for f in files_to_check:
    if not os.path.exists(f):
        print(f"Файл не найден: {f}")
        continue
    try:
        ds = pydicom.dcmread(f)
        print("-" * 30)
        print(f"Файл: {os.path.basename(f)}")
        # PatientName может быть объектом PersonName, приводим к строке
        print(f"  Patient Name: {str(ds.PatientName)}")
        # StudyDate обычно строка 'YYYYMMDD'
        print(f"  Study Date: {getattr(ds, 'StudyDate', 'Не указана')}")
    except Exception as e:
        print(f"Ошибка при чтении {os.path.basename(f)}: {e}")
