from PyInstaller.utils.hooks import collect_data_files, collect_all, get_module_file_attribute
import os
import sys

# 收集PaddleX的所有数据文件，包括隐藏的.version文件
datas = collect_data_files('paddlex', include_py_files=False, include_hidden=True)
print(f"Initial datas from collect_data_files: {datas}")

# 手动添加.version文件
try:
    # 使用get_module_file_attribute获取paddlex的路径，更可靠
    paddlex_path = os.path.dirname(get_module_file_attribute('paddlex'))
    version_file = os.path.join(paddlex_path, '.version')
    
    print(f"Looking for version file at: {version_file}")
    
    if os.path.exists(version_file):
        # 将.version文件添加到datas列表，确保它被复制到正确的位置
        datas.append((version_file, 'paddlex'))
        print(f"Successfully added version file: {version_file} -> paddlex/.version")
    else:
        print(f"WARNING: .version file not found at: {version_file}")
        # 尝试在paddlex目录下查找所有文件，看看是否有.version文件
        print(f"Files in paddlex directory:")
        for file in os.listdir(paddlex_path):
            print(f"  - {file}")
except Exception as e:
    print(f"Error while trying to find .version file: {e}")

# 收集PaddleX的所有子模块
try:
    _, _, hiddenimports = collect_all('paddlex')
    print(f"Hidden imports from collect_all: {hiddenimports}")
except Exception as e:
    print(f"Error in collect_all: {e}")
    hiddenimports = []

# 添加其他可能的依赖
hiddenimports.extend([
    'paddlex.version',
    'paddlex.utils',
    'paddlex.cv',
    'paddlex.det',
    'paddlex.cls',
    'paddlex.seg'
])

print(f"Final datas: {datas}")
print(f"Final hiddenimports: {hiddenimports}")
