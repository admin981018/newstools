from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all
import os
import sys

# 收集PaddleOCR的所有数据文件，包括模型文件
datas = collect_all('paddleocr')[0]

# 收集PaddleOCR的所有子模块
hiddenimports = collect_all('paddleocr')[2]

# 收集所有相关的Paddle库依赖
hiddenimports.extend(collect_submodules('paddle'))
hiddenimports.extend(collect_submodules('paddlex'))
hiddenimports.extend(collect_submodules('ppocr'))
hiddenimports.extend(collect_submodules('shapely'))
hiddenimports.extend(collect_submodules('scipy'))
hiddenimports.extend(collect_submodules('scikit_image'))

# 添加其他可能的依赖
hiddenimports.extend([
    'yaml',
    'requests',
    'PIL',
    'cv2',
    'numpy',
    'openpyxl',
    'docx',
    'pdf2image',
    'imgaug',
    'matplotlib',
    'tqdm',
    'onnx',
    'onnxruntime'
])

# 确保所有动态库被正确收集
binaries = []

# 添加系统路径
sys.path.extend(['.'])
