import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
import platform
import ctypes
import shutil
import stat

def remove_readonly(file_path):
    try:
        # 獲取當前檔案權限
        current_permissions = os.stat(file_path).st_mode
        # 移除唯讀屬性
        os.chmod(file_path, current_permissions | stat.S_IWRITE)
        return True
    except Exception as e:
        messagebox.showerror("錯誤", f"無法移除唯讀屬性: {e}")
        return False

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_file_writable(file_path):
    if not os.path.exists(file_path):
        return False
    # 檢查檔案是否可寫入
    try:
        with open(file_path, 'r+') as f:
            return True
    except IOError:
        return False

def create_backup(file_path):
    backup_path = file_path + '.bak'
    try:
        # 如果備份檔案存在，先移除其唯讀屬性
        if os.path.exists(backup_path):
            remove_readonly(backup_path)
        shutil.copy2(file_path, backup_path)
        return True
    except Exception as e:
        messagebox.showerror("備份錯誤", f"無法建立備份檔案: {e}")
        return False

def replace_content(file_path):
    try:
        if not check_file_writable(file_path):
            # 嘗試移除唯讀屬性
            if not remove_readonly(file_path):
                if is_admin():
                    messagebox.showerror("錯誤", "無法移除檔案的唯讀屬性，即使具有管理員權限。")
                else:
                    result = messagebox.askquestion("權限不足", 
                        "需要管理員權限才能修改此檔案。\n是否要以管理員身份重新運行程式？")
                    if result == 'yes':
                        # 重新以管理員權限運行程式
                        ctypes.windll.shell32.ShellExecuteW(None, "runas", "python", 
                            f'"{os.path.abspath(__file__)}"', None, 1)
                        root.quit()
                return

        # 建立備份檔案
        if not create_backup(file_path):
            return

        # 使用 UTF-8 編碼讀取檔案
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 定義要搜尋的字串和替換的字串
        search_string = 't.feature_flags.vscode_agent_mode_min_version!==void 0&&(i.vscodeAgentModeMinVersion=t.feature_flags.vscode_agent_mode_min_version)'
        replace_string = 't.feature_flags.vscode_agent_mode_min_version!==void 0&&(i.vscodeAgentModeMinVersion="0.314.0")'
        
        # 替換內容
        new_content = content.replace(search_string, replace_string)

        # 確保目標檔案可寫入
        remove_readonly(file_path)
        
        # 使用 UTF-8 編碼寫入檔案
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        messagebox.showinfo("成功", f"檔案已成功更新！\n備份檔案已建立於：{file_path}.bak")
    
    except IOError as e:
        messagebox.showerror("錯誤", f"檔案無法寫入或讀取: {e}")
    except UnicodeError as e:
        messagebox.showerror("編碼錯誤", f"檔案編碼錯誤: {e}")

def select_file():
    file_path = filedialog.askopenfilename(title="選擇檔案", filetypes=[("所有檔案", "*.*")])
    if file_path:
        replace_content(file_path)

def open_folder():
    # 獲取當前使用者名稱
    user_name = os.getlogin()
    # 指定資料夾路徑
    folder_path = f"C:\\Users\\{user_name}\\.vscode\\extensions\\augment.vscode-augment-0.383.1\\out"
    
    # 根據操作系統打開資料夾
    if platform.system() == "Windows":
        os.startfile(folder_path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.call(["open", folder_path])
    else:  # Linux
        subprocess.call(["xdg-open", folder_path])

# 設定 GUI
root = tk.Tk()
root.title("檔案內容替換工具")
root.geometry("300x150")

# 建立選擇檔案按鈕
select_button = tk.Button(root, text="選擇檔案", command=select_file)
select_button.pack(pady=10)

# 建立打開資料夾按鈕
folder_button = tk.Button(root, text="打開資料夾", command=open_folder)
folder_button.pack(pady=10)

# 開始 GUI 主迴圈
root.mainloop()