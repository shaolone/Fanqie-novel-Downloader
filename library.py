import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import json
import os
import sys # 需要导入 sys 来检查操作系统类型
from PIL import Image
from config import save_user_config, load_user_config


LIBRARY_FILE = "library.json"

def load_library():
    """加载书库信息"""
    # 检查文件是否存在
    if os.path.exists(LIBRARY_FILE):
        try:
            # 尝试读取文件内容
            with open(LIBRARY_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            # 如果文件为空，创建新的书库
            if not content:
                print(f"书库文件为空，将创建新的书库")
                return {}
                
            # 尝试解析JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"书库文件格式错误: {str(e)}")
                # 创建备份
                backup_file = f"{LIBRARY_FILE}.backup"
                try:
                    import shutil
                    shutil.copy2(LIBRARY_FILE, backup_file)
                    print(f"已创建书库备份: {backup_file}")
                except Exception as be:
                    print(f"创建备份失败: {str(be)}")
                return {}
                
            # 确保数据是字典格式
            if not isinstance(data, dict):
                print(f"警告: 书库数据格式不正确，应为字典格式，当前格式为: {type(data)}")
                return {}
                
            # 验证数据完整性
            valid_books = {}
            for book_id, book_info in data.items():
                if not isinstance(book_info, dict):
                    print(f"警告: 书籍 {book_id} 的数据格式不正确，已跳过")
                    continue
                    
                # 确保必要字段存在
                required_fields = {"name", "author", "description", "file_path"}
                missing_fields = required_fields - set(book_info.keys())
                if missing_fields:
                    print(f"警告: 书籍 {book_id} 缺少必要字段: {missing_fields}，已跳过")
                    continue
                    
                valid_books[book_id] = book_info
                
            print(f"成功加载书库，共有{len(valid_books)}本书")
            return valid_books
            
        except Exception as e:
            print(f"加载书库失败: {str(e)}")
            return {}
    else:
        print(f"书库文件 {LIBRARY_FILE} 不存在，将创建新的书库")
        return {}

def save_library(library_data):
    """保存书库信息"""
    if not isinstance(library_data, dict):
        print(f"错误: 书库数据不是字典格式")
        return False

    # 创建临时文件
    temp_file = f"{LIBRARY_FILE}.temp"
    backup_file = f"{LIBRARY_FILE}.backup"

    try:
        # 先写入临时文件
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(library_data, f, ensure_ascii=False, indent=4)

        # 如果原文件存在，创建备份
        if os.path.exists(LIBRARY_FILE):
            import shutil
            shutil.copy2(LIBRARY_FILE, backup_file)

        # 重命名临时文件为正式文件
        os.replace(temp_file, LIBRARY_FILE)

        print(f"书库保存成功，共{len(library_data)}本书")
        return True

    except Exception as e:
        print(f"保存书库失败: {str(e)}")
        # 如果保存失败，尝试恢复备份
        if os.path.exists(backup_file):
            try:
                os.replace(backup_file, LIBRARY_FILE)
                print("已恢复到上一个可用的书库版本")
            except Exception as be:
                print(f"恢复备份失败: {str(be)}")
        return False

    finally:
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)

def add_to_library(book_id, book_info, file_path=None):
    """添加书籍到书库"""
    print(f"正在添加书籍到书库，ID: {book_id}")
    
    # 参数检查
    if not book_id:
        print("错误: 书籍ID为空，无法添加到书库")
        return False
        
    if not isinstance(book_info, dict):
        print(f"错误: 书籍信息不是字典格式: {book_info}")
        return False
        
    # 加载现有书库
    library = load_library()
    # 确保 library 是字典
    if not isinstance(library, dict):
        library = {}

    # 从 book_info 中获取保存路径和书名来构建完整的文件路径
    if not file_path:
        save_dir = book_info.get("save_path", "downloads") # 获取指定的保存目录
        book_name = book_info.get('name', 'unknown')      # 获取书名
        output_file_path = os.path.join(save_dir, f"{book_name}.txt") # 构建完整路径
        output_file_path = os.path.abspath(output_file_path)  # 转换为绝对路径
    else:
        output_file_path = os.path.abspath(file_path)  # 使用传入的文件路径并转换为绝对路径

    # 检查文件是否存在
    if not os.path.exists(output_file_path):
        print(f"警告: 文件不存在: {output_file_path}")
        # 尝试在桌面查找
        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            book_name = book_info.get('name', 'unknown')
            desktop_file = os.path.join(desktop_path, f"{book_name}.txt")
            print(f"尝试在桌面查找: {desktop_file}")
            
            if os.path.exists(desktop_file):
                output_file_path = desktop_file
                print(f"在桌面找到文件: {output_file_path}")
            else:
                print(f"警告: 文件在桌面上也不存在")
        except Exception as e:
            print(f"查找桌面文件时出错: {e}")

    # 将书籍信息添加到书库
    library[book_id] = {
        "name": book_info.get("name", "未知书名"),
        "author": book_info.get("author", "未知作者"),
        "description": book_info.get("description", "无简介"),
        "file_path": output_file_path # 存储文件路径
    }
    
    print(f"添加书籍: 《{book_info.get('name')}》, ID: {book_id}, 文件路径: {output_file_path}")
    
    if save_library(library):
        print(f"《{book_info.get('name')}》已成功添加到书库")
        return True
    else:
        print(f"添加《{book_info.get('name')}》到书库失败")
        return False

def remove_from_library(book_id):
    """从书库移除书籍"""
    library = load_library()
    if book_id in library:
        removed_book = library.pop(book_id)
        if save_library(library):
            print(f"已从书库移除《{removed_book.get('name')}》")
            return True
        else:
            print(f"从书库移除《{removed_book.get('name')}》失败")
    return False

class LibraryWindow(ctk.CTkToplevel):
    def __init__(self, master, geometry=None): # 添加 geometry 参数
        super().__init__(master)
        self.title("我的书库")
        if geometry:
            self.geometry(geometry) # 如果提供了 geometry，则使用它
        else:
            self.geometry(master.geometry()) # 否则，使用主窗口的大小
        print("初始化书库窗口...")
        
        # 加载书库数据
        self.library_data = load_library()
        print(f"加载到{len(self.library_data)}本书")
        
        # 加载图标
        self.load_icons()
        
        # 设置UI
        self.setup_ui()
        
        # 使窗口在父窗口之上 (Temporarily commented out for debugging blocking issue)
        # self.transient(master)
        
        # 居中显示
        # 恢复窗口状态，而不是直接居中 (Removed call)
        # self.restore_window_state()
        # self.center_window() # 移除居中调用，让 geometry 参数生效
        
        # 确保所有数据正确加载
        self.after(100, self.refresh_library)

        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # 绑定事件以保存窗口状态 (Removed bindings)
        # self.bind("<Configure>", self.save_window_state)
        # self.bind("<Destroy>", self.save_window_state)

        
    def load_icons(self):
        """加载按钮图标"""
        icon_size = (22, 22)
        assets_path = "assets"
        
        # Helper function to load icon safely
        def _load_single_icon(filename):
            icon_path = os.path.join(assets_path, filename)
            if os.path.exists(icon_path):
                try:
                    pil_image = Image.open(icon_path).resize(icon_size)
                    return ctk.CTkImage(pil_image)
                except Exception as e:
                    print(f"Error loading icon '{filename}': {e}")
                    return None
            else:
                # print(f"Icon file not found: {icon_path}") # Optional: uncomment for debugging
                return None

        self.folder_icon = _load_single_icon("folder.png")
        self.read_icon = _load_single_icon("read.png")
        self.delete_icon = _load_single_icon("delete.png")
        self.search_icon = _load_single_icon("search.png")
            
    def center_window(self):
        """将窗口居中显示"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")


    # def restore_window_state(self): # Removed method
    #     """恢复窗口状态"""
    #     print("尝试恢复书库窗口状态...")
    #     config = load_user_config()
    #     geometry = config.get("window_states", {}).get("library_window")
    #     if geometry:
    #         print(f"找到书库窗口几何信息: {geometry}")
    #         try:
    #             self.geometry(geometry)
    #             print("成功应用书库窗口几何信息")
    #         except tk.TclError as e:
    #             print(f"应用书库窗口几何信息时出错: {e}. 可能由于屏幕分辨率更改或多显示器配置变化。")
    #             # 应用默认或计算后的居中位置
    #         self.center_window()
    #     else:
    #         print("未找到书库窗口几何信息，使用默认居中")
    #         self.center_window()

    # def save_window_state(self, event=None): # Removed method
    #     """保存窗口状态"""
    #     # 仅在窗口可见时保存状态
    #     if self.winfo_viewable():
    #         config = load_user_config()
    #         if "window_states" not in config:
    #             config["window_states"] = {}
    #
    #         # 获取当前几何信息
    #         geometry = self.geometry()
    #         print(f"保存书库窗口状态: {geometry}")
    #
    #         config["window_states"]["library_window"] = geometry
    #         save_user_config(config)
    #     else:
    #         print("书库窗口不可见，跳过保存状态")

    def setup_ui(self):
        # 创建主框架
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # --- 顶部搜索框 ---
        search_frame = ctk.CTkFrame(self)
        search_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)
        
        search_container = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_container.pack(fill=tk.X)
        search_container.grid_columnconfigure(0, weight=1)
        
        # 搜索框
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_container, 
            placeholder_text="搜索书籍...",
            textvariable=self.search_var
        )
        search_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        # 搜索按钮 (Temporarily removed image logic for debugging)
        search_button = ctk.CTkButton(
            search_container,
            text="搜索",
            # image=self.search_icon, # Temporarily removed
            # compound="left", # Temporarily removed if icon is removed
            command=self.search_books,
            width=80
        )
        # search_button_params = {
        #     "master": search_container,
        #     "text": "搜索",
        #     "compound": "left",
        #     "command": self.search_books,
        #     "width": 80
        # }
        # if self.search_icon:
        #     search_button_params["image"] = self.search_icon
        # search_button = ctk.CTkButton(**search_button_params)
        search_button.grid(row=0, column=1)
        
        # 绑定回车键
        search_entry.bind("<Return>", lambda event: self.search_books())
        
        # --- 主内容区 ---
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # 创建一个包含行的框架
        self.book_container = ctk.CTkScrollableFrame(main_frame)
        self.book_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.book_container.grid_columnconfigure(0, weight=1)
        
        # --- 底部按钮栏 ---
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # 刷新按钮
        refresh_button = ctk.CTkButton(
            button_frame, 
            text="刷新", 
            command=self.refresh_library,
            width=100
        )
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # 统计信息标签
        self.stats_label = ctk.CTkLabel(
            button_frame, 
            text=f"总计: {len(self.library_data)} 本书",
            anchor="e"
        )
        self.stats_label.pack(side=tk.RIGHT, padx=5)
        
        # 填充书籍数据
        self.populate_books()
        
    def populate_books(self):
        """填充书籍列表"""
        # 清空现有内容
        for widget in self.book_container.winfo_children():
            widget.destroy()
            
        # 确保 self.library_data 是字典
        if not isinstance(self.library_data, dict):
            self.library_data = {}
            
        # 获取搜索关键词
        search_term = self.search_var.get().lower().strip()
        
        # 跟踪行数
        row = 0
        
        # 按书名排序
        sorted_books = sorted(
            self.library_data.items(),
            key=lambda x: x[1].get("name", "").lower()
        )
        
        for book_id, info in sorted_books:
            # 确保 info 是字典
            if not isinstance(info, dict):
                print(f"书库条目格式错误: ID={book_id}, Info={info}")
                continue
                
            # 如果有搜索词，检查是否匹配
            if search_term:
                name = info.get("name", "").lower()
                author = info.get("author", "").lower()
                description = info.get("description", "").lower()
                
                if (search_term not in name and 
                    search_term not in author and 
                    search_term not in description):
                    continue
            
            # 检查文件是否存在
            file_path = info.get("file_path", "")
            file_exists = os.path.exists(file_path) if file_path else False
            
            # 创建书籍条目框架
            book_frame = ctk.CTkFrame(self.book_container)
            book_frame.grid(row=row, column=0, sticky="ew", pady=5)
            book_frame.grid_columnconfigure(1, weight=1)
            
            # 设置交替背景色
            if row % 2 == 0:
                book_frame.configure(fg_color=("gray90", "gray20"))
            
            # 书籍标题和作者
            title_text = info.get("name", "未知书名")
            if not file_exists:
                title_text += " (文件不存在)"
                
            title_label = ctk.CTkLabel(
                book_frame, 
                text=title_text,
                font=("黑体", 14, "bold"),
                text_color="#FF5555" if not file_exists else None
            )
            title_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))
            
            author_label = ctk.CTkLabel(
                book_frame, 
                text=f"作者: {info.get('author', '未知')}",
                font=("黑体", 12)
            )
            author_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 5))
            
            # 文件路径信息
            if file_path:
                path_label = ctk.CTkLabel(
                    book_frame,
                    text=f"路径: {file_path}",
                    font=("黑体", 10),
                    text_color="gray"
                )
                path_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 5))
            
            # 描述内容
            description = info.get("description", "无简介")
            if len(description) > 100:
                description = description[:100] + "..."
                
            desc_label = ctk.CTkLabel(
                book_frame, 
                text=description,
                wraplength=600,
                justify="left",
                anchor="w"
            )
            desc_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 10))
            
            # 按钮区域
            button_frame = ctk.CTkFrame(book_frame, fg_color="transparent")
            button_frame.grid(row=4, column=0, columnspan=2, sticky="e", padx=10, pady=(0, 10))
            
            # 打开文件夹按钮
            folder_button = ctk.CTkButton(
                button_frame,
                text="打开目录",
                # image=self.folder_icon, # Temporarily removed
                # compound="left", # Temporarily removed
                command=lambda bid=book_id: self.open_folder(bid),
                width=100,
                fg_color="#607D8B",
                hover_color="#455A64",
                state="normal" if file_exists else "disabled"
            )
            # folder_button_params = {
            #     "master": button_frame,
            #     "text": "打开目录",
            #     "compound": "left",
            #     "command": lambda bid=book_id: self.open_folder(bid),
            #     "width": 100,
            #     "fg_color": "#607D8B",
            #     "hover_color": "#455A64",
            #     "state": "normal" if file_exists else "disabled"
            # }
            # if self.folder_icon:
            #     folder_button_params["image"] = self.folder_icon
            # folder_button = ctk.CTkButton(**folder_button_params)
            folder_button.grid(row=0, column=0, padx=5)
            
            # 阅读按钮
            read_button = ctk.CTkButton(
                button_frame,
                text="阅读",
                # image=self.read_icon, # Temporarily removed
                # compound="left", # Temporarily removed
                command=lambda bid=book_id: self.read_book(bid),
                width=80,
                fg_color="#4CAF50",
                hover_color="#388E3C",
                state="normal" if file_exists else "disabled"
            )
            # read_button_params = {
            #     "master": button_frame,
            #     "text": "阅读",
            #     "compound": "left",
            #     "command": lambda bid=book_id: self.read_book(bid),
            #     "width": 80,
            #     "fg_color": "#4CAF50",
            #     "hover_color": "#388E3C",
            #     "state": "normal" if file_exists else "disabled"
            # }
            # if self.read_icon:
            #     read_button_params["image"] = self.read_icon
            # read_button = ctk.CTkButton(**read_button_params)
            read_button.grid(row=0, column=1, padx=5)
            
            # 删除按钮
            delete_button = ctk.CTkButton(
                button_frame,
                text="移除",
                # image=self.delete_icon, # Temporarily removed
                # compound="left", # Temporarily removed
                command=lambda bid=book_id: self.remove_book(bid),
                width=80,
                fg_color="#F44336",
                hover_color="#D32F2F"
            )
            # delete_button_params = {
            #     "master": button_frame,
            #     "text": "移除",
            #     "compound": "left",
            #     "command": lambda bid=book_id: self.remove_book(bid),
            #     "width": 80,
            #     "fg_color": "#F44336",
            #     "hover_color": "#D32F2F"
            # }
            # if self.delete_icon:
            #     delete_button_params["image"] = self.delete_icon
            # delete_button = ctk.CTkButton(**delete_button_params)
            delete_button.grid(row=0, column=2, padx=5)
            
            # 绑定双击事件到整个框架
            if file_exists:
                book_frame.bind("<Double-1>", lambda event, bid=book_id: self.read_book(bid))
            
            row += 1
        
        # 没有书籍的情况
        if row == 0:
            no_books_frame = ctk.CTkFrame(self.book_container, fg_color="transparent")
            no_books_frame.grid(row=0, column=0, sticky="ew", pady=20)
            
            message = "没有找到书籍" if search_term else "书库为空"
            no_books_label = ctk.CTkLabel(
                no_books_frame, 
                text=message,
                font=("黑体", 14)
            )
            no_books_label.pack(pady=50)
        
        # 更新统计信息
        self.stats_label.configure(text=f"总计: {row} 本书")
    
    def search_books(self):
        """搜索书籍"""
        self.populate_books()
    
    def refresh_library(self):
        """刷新书库"""
        print("刷新书库...")
        old_count = len(self.library_data)
        self.library_data = load_library()
        new_count = len(self.library_data)
        print(f"刷新前: {old_count}本书，刷新后: {new_count}本书")
        self.populate_books()

    def get_selected_book_id(self):
        """不再需要此方法，直接在按钮命令中使用 lambda 捕获 book_id"""
        pass

    def open_folder(self, book_id):
        """打开书籍所在文件夹"""
        if book_id and book_id in self.library_data:
            file_path = self.library_data[book_id].get("file_path")
            if file_path and os.path.exists(file_path):
                folder_path = os.path.dirname(file_path)
                try:
                    # 尝试用系统默认方式打开文件夹
                    if os.name == 'nt': # Windows
                        os.startfile(folder_path)
                    elif os.name == 'posix': # macOS, Linux
                        import subprocess
                        # 检查 'open' 或 'xdg-open' 是否可用
                        if sys.platform == 'darwin':
                             subprocess.Popen(['open', folder_path])
                        else:
                             subprocess.Popen(['xdg-open', folder_path])
                    else:
                         messagebox.showerror("错误", "不支持的操作系统", parent=self)
                except FileNotFoundError:
                     messagebox.showerror("错误", "无法找到用于打开文件夹的命令 (xdg-open 或 open)", parent=self)
                except Exception as e:
                    messagebox.showerror("错误", f"无法打开文件夹: {e}", parent=self)
            elif file_path:
                 messagebox.showerror("错误", f"文件路径不存在: {file_path}", parent=self)
            else:
                messagebox.showerror("错误", "未找到文件路径信息", parent=self)

    def read_book(self, book_id):
        """阅读选中的书籍"""
        if book_id and book_id in self.library_data:
            file_path = self.library_data[book_id].get("file_path")
            book_name = self.library_data[book_id].get("name", "未知书籍")
            
            print(f"尝试打开书籍: {book_name}, 路径: {file_path}")

            if file_path and os.path.exists(file_path):
                try:
                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 获取当前窗口几何信息
                    current_geometry = self.geometry()
                    current_size = current_geometry.split('+')[0] # 提取 WxH 部分
                    print(f"传递给阅读器窗口的几何信息: {current_size}") # 调试信息

                    # 导入Reader类并显示，传递geometry参数
                    from reader import Reader
                    reader_window = Reader(
                        self,
                        content,
                        book_name,
                        file_path=file_path,
                        geometry=current_size
                    )
                    reader_window.transient(self)

                except UnicodeDecodeError:
                    # 尝试其他编码
                    try:
                        with open(file_path, 'r', encoding='gbk') as f:
                            content = f.read()
                        
                        # 获取当前窗口几何信息
                        current_geometry = self.geometry()
                        current_size = current_geometry.split('+')[0] # 提取 WxH 部分
                        print(f"传递给阅读器窗口的几何信息（GBK编码）: {current_size}") # 调试信息
                        
                        # 导入Reader类并显示，传递geometry参数
                        from reader import Reader
                        reader_window = Reader(
                            self,
                            content,
                            book_name,
                            file_path=file_path,
                            geometry=current_size
                        )
                        reader_window.transient(self)
                    except Exception as e:
                        messagebox.showerror("错误", f"无法读取文件内容 (尝试GBK编码失败): {e}", parent=self)
                except ImportError:
                    messagebox.showerror("错误", "无法导入 Reader 类，请确保 reader.py 文件存在且正确。", parent=self)
                except Exception as e:
                    messagebox.showerror("错误", f"无法阅读文件: {e}", parent=self)
            else:
                # 文件路径无效或文件不存在
                msg = f"找不到书籍文件: {book_name}\n\n"
                if file_path:
                    msg += f"书库记录路径: {file_path}\n\n"
                    msg += f"请确保文件存在于该路径，或者文件已被移动/删除。"
                else:
                    msg += "书库中未记录有效的文件路径。"
                messagebox.showerror("找不到文件", msg, parent=self)
        else:
            messagebox.showerror("错误", "无效的书籍ID或书库数据", parent=self)

    def remove_book(self, book_id):
        """从书库移除选中的书籍"""
        if book_id:
            book_name = self.library_data.get(book_id, {}).get("name", "未知书籍")
            if messagebox.askyesno("确认", f"确定要从书库移除《{book_name}》吗？\n（这不会删除本地文件）", parent=self):
                if remove_from_library(book_id):
                    self.library_data = load_library() # 重新加载数据
                    self.populate_books() # 刷新列表
                    messagebox.showinfo("成功", f"《{book_name}》已从书库移除", parent=self)
                else:
                    messagebox.showerror("错误", "移除书籍失败", parent=self)


    def on_closing(self):
        """关闭窗口时的操作"""
        try:
            self.master.deiconify() # 恢复主窗口显示
            self.destroy()
        except Exception as e:
            print(f"关闭书库窗口时出错: {e}")
            # 强制销毁
            self.destroy()
# 使用示例 (可选, 用于独立测试)
if __name__ == "__main__":
    # 创建一个临时的根窗口用于测试
    root = tk.Tk()
    root.withdraw() # 隐藏主窗口

    # 假设的书籍信息用于测试 add_to_library
    test_book_id = "test12345"
    test_book_info = {
        "name": "测试书籍",
        "author": "测试作者",
        "description": "这是一本测试书籍",
        "save_path": "downloads" # 假设的保存路径
    }

    # 确保 downloads 目录存在
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    # 创建一个假的测试文件
    test_file_path = os.path.join("downloads", f"{test_book_info['name']}.txt")
    if not os.path.exists(test_file_path):
        try:
            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write("这是测试内容。")
        except Exception as e:
            print(f"创建测试文件失败: {e}")

    # 添加测试书籍到书库并打开书库窗口
    add_to_library(test_book_id, test_book_info)
    app = LibraryWindow(root)

    root.mainloop() 