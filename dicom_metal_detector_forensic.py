import sys
import os
import csv
import hashlib
import numpy as np

# Подключаем локальные библиотеки
possible_paths = [
    r"C:\A\SABOTAGE_RECOVERY\MEDICAL_2022_ORIGINALS",
    r"C:\A\LLM - ANSI EROR UT-8\ml_env\Lib\site-packages"
]
for p in possible_paths:
    if p not in sys.path:
        sys.path.append(p)

try:
    import pydicom
except ImportError as e:
    print(f"Ошибка импорта pydicom: {e}")
    sys.exit(1)

# --- КОНФИГУРАЦИЯ ---
registry_csv = r"H:\ACTOR_DEV_ENV\DICOM_Final_Metadata_Registry.csv"
audit_log_csv = r"H:\ACTOR_DEV_ENV\audit_detection_log.csv"
METAL_HU_THRESHOLD = 2000
MIN_PIXELS_FOR_BOLT = 50
# Ожидаемый ID пациента для верификации (заменить на реальный после первого запуска)
EXPECTED_PATIENT_ID = "Marcova^Galina" 

# Диапазон Z-координат (нужно определить через предварительный просмотр метаданных)
Z_MIN = -500.0
Z_MAX = 500.0

def get_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def log_detection(ds, file_path, z_pos, hu_image):
    # Находим координаты центра масс металла
    y_coords, x_coords = np.where(hu_image > METAL_HU_THRESHOLD)
    if len(x_coords) == 0: return

    center_x = np.mean(x_coords)
    center_y = np.mean(y_coords)
    max_hu = np.max(hu_image)
    
    log_entry = {
        "File": os.path.basename(file_path),
        "Hash": get_file_hash(file_path),
        "StudyUID": ds.get("StudyInstanceUID", "N/A"),
        "PatientID": str(ds.get("PatientName", "N/A")),
        "Z_Coord": z_pos,
        "X_Pixel": round(center_x, 2),
        "Y_Pixel": round(center_y, 2),
        "Max_HU": round(max_hu, 2)
    }
    
    file_exists = os.path.isfile(audit_log_csv)
    with open(audit_log_csv, "a", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=log_entry.keys())
        if not file_exists: writer.writeheader()
        writer.writerow(log_entry)

def analyze_metal_in_dicom(file_paths):
    print(f"Запуск криминалистического анализа (ROI: {Z_MIN} to {Z_MAX})")
    
    for f in file_paths:
        try:
            ds = pydicom.dcmread(f)
            
            # Верификация пациента
            patient_id = str(ds.get("PatientName", ""))
            if "Marcova" not in patient_id: # Гибкая проверка
                continue
                
            slice_loc = float(getattr(ds, 'SliceLocation', 0))
            if not (Z_MIN <= slice_loc <= Z_MAX): continue
            
            pixels = ds.pixel_array.astype(np.float64)
            intercept = getattr(ds, 'RescaleIntercept', 0)
            slope = getattr(ds, 'RescaleSlope', 1)
            hu_image = pixels * slope + intercept
            
            if np.sum(hu_image > METAL_HU_THRESHOLD) > MIN_PIXELS_FOR_BOLT:
                log_detection(ds, f, slice_loc, hu_image)
                print(f"[!] ЗАФИКСИРОВАН АРТЕФАКТ: {os.path.basename(f)}")
                    
        except Exception:
            pass

# Сбор путей
files_to_process = []
with open(registry_csv, mode='r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        files_to_process.append(row[0])

analyze_metal_in_dicom(files_to_process)
print(f"Анализ завершен. Лог сохранен в {audit_log_csv}")
