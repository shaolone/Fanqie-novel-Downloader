import PyInstaller.__main__
import os
import sys
import io
import customtkinter # 导入以获取路径

# 解决Windows环境下的编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 确保脚本路径正确
script_path = os.path.dirname(os.path.abspath(__file__))
gui_path = os.path.join(script_path, 'gui.py')
icon_path = os.path.join(script_path, 'assets', 'app_icon.ico') # Corrected icon path
assets_path = os.path.join(script_path, 'assets') # 添加 assets 文件夹路径

# 获取 customtkinter 库的路径
try:
    ctk_path = os.path.dirname(customtkinter.__file__)
    # 构建 --add-data 参数，注意 Windows 和非 Windows 路径分隔符
    ctk_data_arg = f"--add-data={ctk_path}{os.pathsep}customtkinter"
except Exception as e:
    print(f"警告: 无法获取 customtkinter 路径: {e}. 打包可能失败。")
    ctk_data_arg = None

# 基本的PyInstaller参数 (保持不变或核心的)
base_args = [
    gui_path,
    '--name=FanqieNovelDownloader',  # 使用英文名称避免编码问题
    '--onefile',
    '--windowed',
    '--clean',
    # '--icon=' + icon_path, # 取消注释以包含图标
    # 核心或总是需要的 hidden imports
    '--hidden-import=requests',
    '--hidden-import=bs4',
    '--hidden-import=lxml',
    '--hidden-import=ebooklib',
    '--hidden-import=ebooklib.epub',
    '--hidden-import=tqdm',
    '--hidden-import=json',
    '--hidden-import=threading',
    '--hidden-import=tkinter',
    '--hidden-import=tkinter.ttk',
    '--hidden-import=tkinter.filedialog',
    '--hidden-import=tkinter.messagebox',
    '--hidden-import=customtkinter',
    '--hidden-import=PIL',
    '--hidden-import=config',
    '--hidden-import=settings',
    '--hidden-import=library',
    '--hidden-import=reader',
    '--hidden-import=splash',
    '--hidden-import=request_handler', # 添加 request_handler
    # '--uac-admin', # 暂时移除UAC，看是否是导致问题的原因之一，后续可加回
    # 添加 assets 文件夹及其内容
    f'--add-data={assets_path}{os.pathsep}assets',
]

# 添加 customtkinter 数据文件
if ctk_data_arg:
    base_args.append(ctk_data_arg)

# 如果是Windows，添加图标参数
if sys.platform == 'win32' and os.path.exists(icon_path):
    base_args.append('--icon=' + icon_path)
    # base_args.append('--uac-admin') # 如果需要UAC，在这里加回

# 从命令行接收额外的参数 (例如 --add-data)
# sys.argv[0] 是脚本名, sys.argv[1:] 是后面的参数
extra_args = sys.argv[1:]

# 合并参数
all_args = base_args + extra_args

# 打印最终参数用于调试
try:
    print(f"Running PyInstaller with args: {all_args}")
except UnicodeEncodeError:
    print("Running PyInstaller with the configured arguments...")

# 运行PyInstaller
PyInstaller.__main__.run(all_args)

# 避免中文输出导致的编码错误
try:
    print("Build completed! The executable file is in the dist folder.")
except UnicodeEncodeError:
    try:
        sys.stdout.buffer.write("Build completed! The executable file is in the dist folder.\n".encode('utf-8'))
    except:
        print("Build completed!")