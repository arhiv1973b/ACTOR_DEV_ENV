import pydicom
import nibabel as nib
import numpy as np
import os
import sys

# Добавляем путь к библиотекам ml_env
sys.path.append(r"C:\A\LLM - ANSI EROR UT-8\ml_env\Lib\site-packages")

def convert_dicom_to_nifti(dicom_dir, output_file):
    print(f"Загрузка DICOM из: {dicom_dir}")
    # Сбор всех файлов в папке
    files = []
    for root, _, filenames in os.walk(dicom_dir):
        for f in filenames:
            files.append(os.path.join(root, f))
    
    # Сортировка по InstanceNumber
    datasets = []
    for f in files:
        try:
            ds = pydicom.dcmread(f)
            if 'PixelData' in ds:
                datasets.append(ds)
        except:
            continue
            
    datasets.sort(key=lambda x: int(x.InstanceNumber))
    
    # Создание 3D массива
    pixel_array = np.stack([ds.pixel_array for ds in datasets])
    
    # Создание NIfTI (аффин можно улучшить позже, сейчас важно получить объем)
    affine = np.eye(4) 
    nifti_img = nib.Nifti1Image(pixel_array, affine)
    
    nib.save(nifti_img, output_file)
    print(f"Сохранено в: {output_file}")

# Запуск конвертации (используем папку, где мы нашли металл)
convert_dicom_to_nifti(r"C:\A\SABOTAGE_RECOVERY\MEDICAL_2022_ORIGINALS\DICOM\D202204\DD0610", r"H:\ACTOR_DEV_ENV\D202204_analysis.nii.gz")
