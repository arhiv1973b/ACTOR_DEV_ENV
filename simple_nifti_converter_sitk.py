import SimpleITK as sitk
import os

def convert_dicom_to_nifti_sitk(series_directory, output_file):
    print(f'Запуск конвертации через SimpleITK: {series_directory}')
    
    # Инициализация ридера
    reader = sitk.ImageSeriesReader()
    
    # Получение списка файлов DICOM (серии)
    dicom_names = reader.GetGDCMSeriesFileNames(series_directory)
    
    if not dicom_names:
        print('Ошибка: DICOM-серии не найдены в директории.')
        return

    reader.SetFileNames(dicom_names)
    
    # Загрузка и конвертация
    try:
        image = reader.Execute()
        sitk.WriteImage(image, output_file)
        print(f'Успех! Файл NIfTI сохранен: {output_file}')
    except Exception as e:
        print(f'Критическая ошибка SimpleITK: {e}')

# Точка входа
if __name__ == '__main__':
    convert_dicom_to_nifti_sitk(
        r'C:\A\SABOTAGE_RECOVERY\MEDICAL_2022_ORIGINALS\DICOM\D202204\DD0610',
        r'H:\ACTOR_DEV_ENV\D202204_analysis_sitk.nii.gz'
    )
