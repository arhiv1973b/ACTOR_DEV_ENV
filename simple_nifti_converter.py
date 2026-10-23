import sys
# Принудительно подключаем здоровые библиотеки из C:\Python314
sys.path.insert(0, r"C:\Python314\Lib\site-packages")

import pydicom
import nibabel as nib
import numpy as np
import os

def convert_dicom_to_nifti(dicom_dir, output_file):
    print(f"Используем рабочие библиотеки из C:\\Python314")
    print(f"Загрузка DICOM из: {dicom_dir}")
    
    # Сбор всех файлов в папке (убрал проверку .dcm, так как у нас raw без расширений)
    files = [os.path.join(dicom_dir, f) for f in os.listdir(dicom_dir) if os.path.isfile(os.path.join(dicom_dir, f))]
    
    # Сортировка по InstanceNumber для корректного стека
    datasets = []
    for f in files:
        try:
            ds = pydicom.dcmread(f)
            if 'PixelData' in ds:
                datasets.append(ds)
        except Exception as e:
            continue
            
    # Сортируем, если есть InstanceNumber
    datasets.sort(key=lambda x: int(getattr(x, 'InstanceNumber', 0)))
    
    # Создание 3D массива
    pixel_array = np.stack([ds.pixel_array for ds in datasets])
    
    # Создание NIfTI
    affine = np.eye(4)
    nifti_img = nib.Nifti1Image(pixel_array, affine)
    
    nib.save(nifti_img, output_file)
    print(f"Конвертация завершена. Файл сохранен: {output_file}")

# Запуск
convert_dicom_to_nifti(r"C:\A\SABOTAGE_RECOVERY\MEDICAL_2022_ORIGINALS\DICOM\D202204\DD0610", 
                       r"H:\ACTOR_DEV_ENV\D202204_analysis.nii.gz")
