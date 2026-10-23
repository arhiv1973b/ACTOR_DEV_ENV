import sys
import os
import csv

# Подключаем локальную библиотеку pydicom
possible_paths = [
    r"C:\A\SABOTAGE_RECOVERY\MEDICAL_2022_ORIGINALS"
]
for p in possible_paths:
    if p not in sys.path:
        sys.path.append(p)

try:
    import pydicom
except ImportError:
    print("Ошибка: pydicom не найден. Проверьте пути.")
    sys.exit(1)

# Директория с DICOM файлами и путь для сохранения отчета
root_dir = r"C:\A\SABOTAGE_RECOVERY\MEDICAL_2022_ORIGINALS\DICOM"
output_csv = r"H:\ACTOR_DEV_ENV\DICOM_Final_Metadata_Registry.csv"

print(f"Сканирование директории: {root_dir}")

results = []

# Проходим по всем файлам
for root, dirs, files in os.walk(root_dir):
    for file in files:
        # Ищем файлы без расширений (типично для сырых DICOM)
        if "." not in file:
            full_path = os.path.join(root, file)
            try:
                # Читаем только заголовки для скорости (stop_before_pixels=True)
                ds = pydicom.dcmread(full_path, stop_before_pixels=True)
                
                # Извлекаем данные, обрабатывая возможные ошибки
                patient_name = str(getattr(ds, 'PatientName', 'ОТСУТСТВУЕТ'))
                study_date = str(getattr(ds, 'StudyDate', 'ОТСУТСТВУЕТ'))
                
                results.append([full_path, file, patient_name, study_date])
            except Exception:
                # Пропускаем файлы, которые не являются DICOM
                pass

# Записываем результаты в CSV
with open(output_csv, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["Полный путь", "Имя файла", "Имя пациента (DICOM)", "Дата исследования (DICOM)"])
    writer.writerows(results)

print(f"Анализ завершен. Обработано корректных DICOM-файлов: {len(results)}.")
print(f"Полный реестр сохранен в {output_csv}")
