import os
import pydicom
import matplotlib.pyplot as plt
import numpy as np
from vtk.util import numpy_support
import vtk


# путь к папке с DICOM файлами
folder_patch = "C:/Users/User/Downloads/Stomatology/stomatology/Не в работе/3.Шея/2.01 Расстояние от зубовидного отростка от края до дуги атланта несимметрично. Смещение вправо/К2"

# Список для хранения загруженных DICOM файлов
dicom_files = []

# Перебор файлов в директори
for filename in os.listdir(folder_patch):
    if filename.endswith('.dcm'):
        filepath = os.path.join(folder_patch, filename)
        ds = pydicom.dcmread(filepath)
        dicom_files.append(ds)

# Сортировка файлов по координате среза
dicom_files.sort(key=lambda x: float(x.ImagePositionPatient[2]))

# Создание трехмерного массива пикселей
volume = np.stack([file.pixel_array for file in dicom_files])

# Преобразование в VTK формат
volume_vtk = numpy_support.numpy_to_vtk(num_array=volume.ravel(), deep=True, array_type=vtk.VTK_FLOAT)

# Создание VTK изображения
image = vtk.vtkImageData()
# image.SetDimensions(volume.shape)
image.SetDimensions(volume.shape[2], volume.shape[1], volume.shape[0])
image.GetPointData().SetScalars(volume_vtk)

# Визуализация (упрощеый пример)
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Создаем функцию переноса для определения цвета
colorTransferFunction = vtk.vtkColorTransferFunction()
colorTransferFunction.AddRGBPoint(-700, 0.0, 0.0, 0.0) # Черный при минимальной интенсивности
# colorTransferFunction.AddRGBPoint(20000, 1.0, 0.5, 0.3) # Цвета для интересующего диапазона значений
colorTransferFunction.AddRGBPoint(4000, 1.0, 1.0, 1.0) # Белый при максимальной интенсивности

# Настройка ключевых точек функции переноса прозрачности
opacityTransferFunction = vtk.vtkPiecewiseFunction()
opacityTransferFunction.AddPoint(200, 0.0) # Минимальное значение интенсивности
# opacityTransferFunction.AddPoint(0, 0.15) # Значение, при котором структуры начинают становиться видимыми
opacityTransferFunction.AddPoint(4000, 1.0) # Максимальное значение интенсивности

# Создаем настройки для объемного рендеринга
volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.SetColor(colorTransferFunction)
volumeProperty.SetScalarOpacity(opacityTransferFunction)
volumeProperty.SetInterpolationTypeToLinear() #Интерполяция для плавного перехода цветов

# Добавление объемного рендеринга
volumeMapper = vtk.vtkSmartVolumeMapper()
volumeMapper.SetInputData(image)
volumeRenderer = vtk.vtkVolume()
volumeRenderer.SetMapper(volumeMapper)
volumeRenderer.SetProperty(volumeProperty)
renderer.AddVolume(volumeRenderer)

# Выбор позиции среза
dims = image.GetDimensions() # Получаем размеры изображения. Возвращает кортеж (ширина, высота, глубина)

# Вычисляем центры координат
centerX = dims[0] / 2.0
centerY = dims[1] / 2.0
centerZ = dims[2] / 2.0

# Если у изображения есть информация о расположении и ориентации, вы можете учесть и ее.
spacing = image.GetSpacing()  # Размер вокселя(трехмерного пикселя). Возвращает кортеж (spacingX, spacingY, spacingZ)
origin = image.GetOrigin()  # Начало сетки вокселей. Возвращает кортеж (originX, originY, originZ)

# Учет расстояния между вокселами и начала координат изображения
centerX = origin[0] + spacing[0] * centerX
centerY = origin[1] + spacing[1] * centerY
centerZ = origin[2] + spacing[2] * centerZ

resliceAxes = vtk.vtkMatrix4x4() # 4x4 матрица преобразования, для определения положения и ориентации среза в пространстве
resliceAxes.DeepCopy([1, 0, 0, centerX,
                      0, 1, 0, centerY,
                      0, 0, 1, centerZ + 35,
                      0, 0, 0, 1]) # Позиционирование среза.




# Создание среза изображения
reslice = vtk.vtkImageReslice() # Объект vtkImageReslice используется для извлечения срезов
reslice.SetInputData(image)     # Передаем VTK изображение в vtkImageReslice объект для извлечения среза
reslice.SetOutputDimensionality(2)  # Устанавливаем размерность выходного изображения
reslice.SetResliceAxes(resliceAxes) # Команда устанавливает оси пересечения для операции пересечения (reslicing) изображения.

# Добавление среза в рендер
actor = vtk.vtkImageActor()
actor.GetMapper().SetInputConnection(reslice.GetOutputPort())  # Прямое подключение к reslice
renderer.AddActor(actor) # Добавление актера в рендерер

# Настройка камеры и начало визуализации
renderer.ResetCamera()
renderWindow.Render()
renderWindowInteractor.Start()




