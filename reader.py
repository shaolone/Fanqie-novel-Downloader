import tkinter as tk
from tkinter import colorchooser
import customtkinter as ctk
from config import CONFIG, save_user_config
import os
import json
from PIL import Image
import re # Import re for chapter parsing

class Reader(ctk.CTkToplevel):
    def __init__(self, master, content, title, file_path=None, geometry=None): # <-- 添加 geometry 参数
    # def __init__(self, master, content, title, file_path=None):
        super().__init__(master)
        # Store original title passed
        self.original_title = title
        self.reader_config = CONFIG["reader"]
        # self.geometry(f"{self.reader_config['default_width']}x{self.reader_config['default_height']}") # Removed config-based size
        # 将 geometry 设置移到 __init__ 末尾
        self.content = content
        self.current_file_path = file_path  # 保存当前文件路径，用于书库功能
        self.chapters = [] # To store chapter info: (title, start_index)
         # Changed format: (title, start_char_index)
        self.current_chapter_index = -1 # Track current chapter (Restore this line)
        self.parsed_author = None # To store parsed author
        
        # Try to parse author and potentially update title from content beginning
        self.parse_metadata()
        
        # Set window title using original or parsed title
        self.title(f"阅读器 - {self.original_title}")
        
        # 设置默认外观
        ctk.set_appearance_mode("dark" if self.reader_config.get("dark_mode", True) else "light")
        
        # 加载图标
        self.load_icons()
        
        # 设置UI
        self.parse_chapters() # Parse chapters before setting up UI that uses them
        
        # 解析章节并填充UI
        self.setup_ui()
        self.update_chapter_navigation() # Update UI after setup
        
        
        # 中心化窗口位置 (Removed call)
        # self.center_window()
        
        # 在所有 UI 设置完成后应用 geometry
        if geometry:
            self.geometry(geometry)
            print(f"Reader: 应用 geometry: {geometry}") # 添加调试信息

        # 尝试加载阅读进度
        self.load_reading_progress()
        
        # 如果加载进度失败或没有进度记录，则跳转到第一章
        if self.current_chapter_index == -1 and self.chapters and len(self.chapters) > 0:
            # 使用after避免初始化过程中的视图冲突
            self.after(100, lambda: self.goto_chapter(0, True))
            
        # 定期保存阅读进度（每30秒）
        self.after(30000, self.auto_save_progress)

        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 绑定滚动事件，用于追踪阅读位置
        self.text_widget.bind("<MouseWheel>", self.on_scroll)
        self.text_widget.bind("<Button-4>", self.on_scroll)  # Linux上滚轮上滚
        self.text_widget.bind("<Button-5>", self.on_scroll)  # Linux上滚轮下滚
        
        # 当前阅读位置（yview的分数值）
        self.current_position = 0.0
        
    def on_scroll(self, event=None):
        """滚动时记录当前位置"""
        # 延迟更新以确保滚动完成
        self.after(200, self.update_current_position)
    
    def update_current_position(self):
        """更新当前阅读位置"""
        try:
            # 获取当前可见区域的顶部位置（分数值，0.0-1.0之间）
            self.current_position = self.text_widget.yview()[0]
        except Exception as e:
            print(f"更新阅读位置时出错: {e}")
            
    def auto_save_progress(self):
        """定期自动保存阅读进度"""
        self.save_reading_progress()
        # 继续定时保存
        self.after(30000, self.auto_save_progress)

    def get_progress_file_path(self):
        """获取进度文件路径"""
        if not self.current_file_path:
            return None
            
        # 使用书籍文件路径创建一个唯一的标识符
        book_id = os.path.basename(self.current_file_path)
        # 移除扩展名
        book_id = os.path.splitext(book_id)[0]
        
        # 创建进度文件目录
        progress_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reading_progress")
        os.makedirs(progress_dir, exist_ok=True)
        
        # 进度文件路径
        return os.path.join(progress_dir, f"{book_id}.progress")
    
    def save_reading_progress(self):
        """保存阅读进度到文件"""
        progress_file = self.get_progress_file_path()
        if not progress_file:
            return
            
        # 更新当前位置
        self.update_current_position()
        
        try:
            # 生成章节信息的哈希值作为额外验证
            chapters_hash = 0
            for title, _ in self.chapters:
                chapters_hash += hash(title)
                
            progress_data = {
                "book_title": self.original_title,
                "chapter_index": self.current_chapter_index,
                "chapter_title": self.chapters[self.current_chapter_index][0] if 0 <= self.current_chapter_index < len(self.chapters) else "",
                "chapters_count": len(self.chapters),
                "chapters_hash": str(chapters_hash),  # 转为字符串以便JSON序列化
                "position": self.current_position,
                "file_path": self.current_file_path
            }
            
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
                
            print(f"阅读进度已保存: 章节 {self.current_chapter_index + 1}/{len(self.chapters)}, '{progress_data['chapter_title']}', 位置 {self.current_position:.2f}")
        except Exception as e:
            print(f"保存阅读进度失败: {e}")
    
    def load_reading_progress(self):
        """加载阅读进度"""
        progress_file = self.get_progress_file_path()
        if not progress_file or not os.path.exists(progress_file):
            return False
            
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
                
            # 确认是同一本书
            if progress_data.get("file_path") == self.current_file_path:
                # 验证章节数量是否匹配
                if progress_data.get("chapters_count", 0) != len(self.chapters):
                    print(f"章节数量不匹配: 存储的={progress_data.get('chapters_count')}, 当前的={len(self.chapters)}")
                    return False
                
                # 计算当前章节哈希值并验证
                chapters_hash = 0
                for title, _ in self.chapters:
                    chapters_hash += hash(title)
                if str(chapters_hash) != progress_data.get("chapters_hash", ""):
                    print("章节内容已更改，不恢复进度")
                    return False
                
                chapter_index = progress_data.get("chapter_index", 0)
                position = progress_data.get("position", 0.0)
                chapter_title = progress_data.get("chapter_title", "")
                
                # 额外验证章节标题
                if 0 <= chapter_index < len(self.chapters):
                    current_title = self.chapters[chapter_index][0]
                    if chapter_title != current_title:
                        print(f"章节标题不匹配: 存储的='{chapter_title}', 当前的='{current_title}'")
                        
                        # 尝试通过标题找到正确的章节
                        for i, (title, _) in enumerate(self.chapters):
                            if title == chapter_title:
                                chapter_index = i
                                print(f"通过标题找到正确章节索引: {chapter_index}")
                                break
                
                # 安全检查确保章节索引在有效范围内
                if 0 <= chapter_index < len(self.chapters):
                    print(f"恢复阅读进度: 章节 {chapter_index + 1}/{len(self.chapters)}, 标题: '{self.chapters[chapter_index][0]}', 位置 {position:.2f}")
                    
                    # 使用单独的函数跳转到章节，避免lambda问题
                    self.after(200, lambda idx=chapter_index: self.goto_saved_chapter(idx, position))
                    return True
                else:
                    print(f"章节索引超出范围: {chapter_index}, 范围:[0-{len(self.chapters)-1}]")
                    
        except Exception as e:
            print(f"加载阅读进度失败: {e}")
            
        return False
        
    def goto_saved_chapter(self, chapter_idx, position):
        """跳转到保存的章节和位置"""
        self.goto_chapter(chapter_idx, True)
        self.after(200, lambda pos=position: self.restore_position(pos))
        
    def restore_position(self, position):
        """恢复阅读位置"""
        try:
            if 0.0 <= position <= 1.0:
                self.text_widget.yview_moveto(position)
                self.current_position = position
                print(f"恢复到位置: {position:.2f}")
        except Exception as e:
            print(f"恢复阅读位置失败: {e}")

    def parse_metadata(self):
        """Try to parse Title and Author from the beginning of the content."""
        lines = self.content.split('\n', 5) # Check first few lines
        author_pattern = re.compile(r"^作者[：:](.+)$")
        # Title pattern is optional as it's passed via init
        # title_pattern = re.compile(r"^书名[：:](.+)$")
        
        for line in lines:
            line = line.strip()
            author_match = author_pattern.match(line)
            if author_match:
                self.parsed_author = author_match.group(1).strip()
                print(f"解析到作者: {self.parsed_author}") # Debug
                # Stop searching for author once found
                break
            # Add title parsing here if needed in the future

    def load_icons(self):
        """加载图标"""
        icon_size = (20, 20)
        assets_path = "assets"
        
        # 尝试加载图标
        # 禁用所有图标加载以避免 "pyimage" 错误
        self.font_icon = None
        self.color_icon = None
        # Add icons for navigation if available
        self.prev_icon = None
        self.next_icon = None
        print("阅读器图标已禁用")

    def setup_ui(self):
        # 创建主框架
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Text widget takes most space
        
        # --- Top Control Frame (Chapters & Author) ---
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 5))
        top_frame.grid_columnconfigure(1, weight=1) # Make combobox expand
        
        # 创建导航框架，专门用于放置导航按钮和章节选择器
        nav_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        nav_frame.grid(row=0, column=0, sticky="ew", columnspan=3)
        nav_frame.grid_columnconfigure(1, weight=1)
        
        self.prev_button = ctk.CTkButton(
            nav_frame, 
            text="上一章", 
            # image=self.prev_icon, # Icon disabled
            # compound="left", # Icon disabled
            command=self.prev_chapter,
            width=80
        )
        self.prev_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.chapter_combo = ctk.CTkComboBox(
            nav_frame,
            values=["无章节"], # Placeholder
            command=self.goto_chapter_from_combo,
            state="disabled" # Initially disabled
        )
        self.chapter_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.next_button = ctk.CTkButton(
            nav_frame, 
            text="下一章", 
            # image=self.next_icon, # Icon disabled
            # compound="right", # Icon disabled
            command=self.next_chapter,
            width=80
        )
        self.next_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Add Author Label if parsed (现在总是在行1，即使没有作者信息)
        if self.parsed_author:
            author_label = ctk.CTkLabel(top_frame, text=f"作者: {self.parsed_author}", anchor="w")
            author_label.grid(row=1, column=0, columnspan=3, padx=5, pady=(0,5), sticky="w")
        else:
            # 如果没有作者信息，添加一个空白标签占位，保持布局一致
            spacer_label = ctk.CTkLabel(top_frame, text="", height=5)
            spacer_label.grid(row=1, column=0, columnspan=3, padx=5, pady=(0,5), sticky="w")
        
        # --- Main Frame (Text Content) ---
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=0)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # 创建文本框
        self.text_widget = ctk.CTkTextbox(
            main_frame, 
            wrap="word",
            font=(self.reader_config["default_font"], self.reader_config["default_size"]),
            fg_color=self.reader_config["default_bg"],
            text_color=self.reader_config["default_fg"],
            corner_radius=8,
            border_width=0
        )
        self.text_widget.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # 显示内容，如果有章节，则从第一个章节开始显示，跳过简介等信息
        content_to_display = self.content
        if self.chapters:
            first_chapter_start_index = self.chapters[0][1]
            # 从第一章开始，但在章节标题前后添加空行，使标题更明显
            raw_content = self.content[first_chapter_start_index:]
            # 在每个章节标题前添加空行
            for i in range(1, len(self.chapters)):
                # 计算相对于content_to_display的索引
                relative_index = self.chapters[i][1] - first_chapter_start_index
                if relative_index > 0 and relative_index < len(raw_content):
                    # 在章节标题前插入两个换行符
                    insertion_point = relative_index
                    raw_content = raw_content[:insertion_point] + "\n\n" + raw_content[insertion_point:]
            
            # 在开头添加更多空行以确保第一章标题在顶部可见
            content_to_display = "\n\n\n\n\n" + raw_content
            print(f"检测到章节，仅显示从字符索引 {first_chapter_start_index} 开始的内容。已添加空行突出章节标题。")
        self.text_widget.insert("1.0", content_to_display)
        
        self.text_widget.configure(state="disabled") # Disable editing initially
        
        # --- Bottom Control Frame (Settings) ---
        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(5, 10))
        # Let the settings buttons distribute space
        control_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1) 
        
        # 字体设置
        font_label = ctk.CTkLabel(control_frame, text="字体:")
        font_label.pack(side=tk.LEFT, padx=(0, 5), pady=10)
        
        import tkinter.font as tkfont
        fonts = list(sorted(tkfont.families()))
        
        self.font_var = ctk.StringVar(value=self.reader_config["default_font"])
        font_combo = ctk.CTkOptionMenu(
            control_frame, 
            values=fonts,
            variable=self.font_var,
            command=lambda x: self.update_font(),
            width=120
        )
        font_combo.pack(side=tk.LEFT, padx=5, pady=10)
        
        # 字体大小
        size_label = ctk.CTkLabel(control_frame, text="大小:")
        size_label.pack(side=tk.LEFT, padx=(15, 5), pady=10)
        
        sizes = [str(i) for i in range(8, 25)]
        self.size_var = ctk.StringVar(value=str(self.reader_config["default_size"]))
        size_combo = ctk.CTkOptionMenu(
            control_frame, 
            values=sizes,
            variable=self.size_var,
            command=lambda x: self.update_font(),
            width=60
        )
        size_combo.pack(side=tk.LEFT, padx=5, pady=10)
        
        # 主题模式（亮/暗）
        self.theme_var = ctk.StringVar(value="暗色" if self.reader_config.get("dark_mode", True) else "亮色")
        theme_button = ctk.CTkButton(
            control_frame, 
            textvariable=self.theme_var, # Use textvariable to update text automatically
            command=self.toggle_theme,
            width=70
        )
        theme_button.pack(side=tk.LEFT, padx=(20, 5), pady=10)
        
        # 文字颜色
        text_color_button = ctk.CTkButton(
            control_frame, 
            text="文字颜色", 
            # image=self.color_icon, # Icon disabled
            # compound="left", # Icon disabled
            command=self.choose_text_color,
            width=90
        )
        text_color_button.pack(side=tk.LEFT, padx=5, pady=10)
        
        # 背景颜色
        bg_color_button = ctk.CTkButton(
            control_frame, 
            text="背景颜色", 
            # image=self.color_icon, # Icon disabled
            # compound="left", # Icon disabled
            command=self.choose_bg_color,
            width=90
        )
        bg_color_button.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Initially disable text widget editing (moved from end of setup_ui)
        self.text_widget.configure(state="disabled")

    def parse_chapters(self):
        """解析文本内容以查找章节标题"""
        print("开始解析章节...")
        self.chapters = []
        # Use the refined regex directly on the content string
        # Explicitly match potential 4-space indent or no indent at the beginning of the line
        pattern = re.compile(r"^(?:\s{4}|\s*)(?:第\d+章\s+|第[一二三四五六七八九十百千]+章\s*|Chapter\s*\d+\s*|楔子|序章|引子|番外|特别篇|if线).*", re.MULTILINE)

        last_match_end = 0
        for match in re.finditer(pattern, self.content):
            title = match.group(0).strip()
            start_char_index = match.start()

            # Basic check to avoid adding the same chapter index if regex matches slightly differently
            if title and (not self.chapters or self.chapters[-1][1] != start_char_index):
                 # print(f"找到章节: '{title}' at char index {start_char_index}") # Debug
                 self.chapters.append((title, start_char_index))
            last_match_end = match.end()
            
        print(f"解析到 {len(self.chapters)} 个章节") # Debug output

    def update_chapter_navigation(self):
        """更新章节导航UI"""
        if self.chapters:
            chapter_titles = [ch[0] for ch in self.chapters]
            self.chapter_combo.configure(values=chapter_titles, state="normal")
            
            # If chapters were found, try to set the first chapter
            if self.current_chapter_index == -1:
                 self.goto_chapter(0, update_combo=True)
            else:
                 # Ensure combo reflects the current chapter if it was already set
                 self.chapter_combo.set(self.chapters[self.current_chapter_index][0])
                 
            self.prev_button.configure(state="normal" if self.current_chapter_index > 0 else "disabled")
            self.next_button.configure(state="normal" if self.current_chapter_index < len(self.chapters) - 1 else "disabled")
        else:
            self.chapter_combo.configure(values=["未找到章节"], state="disabled")
            self.prev_button.configure(state="disabled")
            self.next_button.configure(state="disabled")

    def goto_chapter(self, chapter_idx, update_combo=False):
        """跳转到指定索引的章节"""
        # Now uses character index
        if 0 <= chapter_idx < len(self.chapters):
            title, start_char_index = self.chapters[chapter_idx]
            # Convert character index to Tkinter text index ("line.char")
            tk_index = f"1.0+{start_char_index}c"
            print(f"跳转到章节 {chapter_idx + 1}: '{title}' at char {start_char_index} (tk index: {tk_index})") # Debug
            
            # 先跳转到章节开始位置
            self.text_widget.see(tk_index)
            
            # 确保章节标题位于可见区域的顶部
            self.text_widget.update_idletasks()  # 确保几何信息已更新
            
            # 获取章节标题所在的行
            title_line_index = self.text_widget.index(tk_index).split('.')[0]
            print(f"章节标题在第 {title_line_index} 行")
            
            # 优先尝试让标题位于顶部
            self.text_widget.see(f"{title_line_index}.0")
            
            # 确保滚动到标题行的开头，而不是中间或末尾
            # 强制重置滚动位置，让标题行尽可能贴近顶部
            if chapter_idx == 0:  # 对于第一章特殊处理
                self.text_widget.yview_moveto(0.0)  # 直接滚动到最顶部
            else:
                # 先获取当前可见区域的信息
                fraction = self.text_widget.yview()
                # 稍微向上滚动一点，确保章节标题在顶部
                self.text_widget.yview_scroll(-2, "units")
            
            self.current_chapter_index = chapter_idx
            
            if update_combo:
                self.chapter_combo.set(title)
                
            # Update button states
            self.prev_button.configure(state="normal" if self.current_chapter_index > 0 else "disabled")
            self.next_button.configure(state="normal" if self.current_chapter_index < len(self.chapters) - 1 else "disabled")
        else:
            print(f"无效的章节索引: {chapter_idx}")

    def goto_chapter_from_combo(self, selected_title):
        """从下拉菜单选择章节后跳转"""
        for idx, (title, start_index) in enumerate(self.chapters):
            if title == selected_title: # Title is still the first element
                self.goto_chapter(idx)
                break
                
    def prev_chapter(self):
        """跳转到上一章"""
        if self.current_chapter_index > 0:
            self.goto_chapter(self.current_chapter_index - 1, update_combo=True)

    def next_chapter(self):
        """跳转到下一章"""
        if self.current_chapter_index < len(self.chapters) - 1:
            self.goto_chapter(self.current_chapter_index + 1, update_combo=True)

    def update_font(self, event=None):
        """更新字体设置"""
        try:
            font_name = self.font_var.get()
            font_size = int(self.size_var.get())
            
            self.text_widget.configure(state="normal") # Need to enable to change font
            self.text_widget.configure(font=(font_name, font_size))
            self.text_widget.configure(state="disabled") # Disable again
            
            # 保存用户配置
            CONFIG["reader"]["default_font"] = font_name
            CONFIG["reader"]["default_size"] = font_size
            save_user_config(CONFIG)
        except Exception as e:
            print(f"更新字体失败: {e}")

    def choose_text_color(self):
        """选择文字颜色"""
        color = colorchooser.askcolor(title="选择文字颜色", initialcolor=self.reader_config["default_fg"])[1]
        if color:
            self.text_widget.configure(state="normal")
            self.text_widget.configure(text_color=color)
            self.text_widget.configure(state="disabled")
            
            # 保存用户配置
            CONFIG["reader"]["default_fg"] = color
            save_user_config(CONFIG)

    def choose_bg_color(self):
        """选择背景颜色"""
        color = colorchooser.askcolor(title="选择背景颜色", initialcolor=self.reader_config["default_bg"])[1]
        if color:
            self.text_widget.configure(state="normal")
            self.text_widget.configure(fg_color=color) # Use fg_color for CTkTextbox background
            self.text_widget.configure(state="disabled")
            
            # 保存用户配置
            CONFIG["reader"]["default_bg"] = color
            save_user_config(CONFIG)
            
    def toggle_theme(self):
        """切换亮/暗主题"""
        # Correct logic for toggling theme
        is_currently_dark = ctk.get_appearance_mode() == "Dark"
        new_mode = "Light" if is_currently_dark else "Dark"
        new_button_text = "亮色" if is_currently_dark else "暗色"
        
        ctk.set_appearance_mode(new_mode)
        self.theme_var.set(new_button_text) # Update button text
        CONFIG["reader"]["dark_mode"] = not is_currently_dark
            
        save_user_config(CONFIG)

    # def center_window(self): # Removed method
    #     """将窗口居中显示"""
    #     self.update_idletasks()
    #     width = self.winfo_width()
    #     height = self.winfo_height()
    #     # Ensure width/height are reasonable before centering
    #     if width < 100 or height < 100:
    #         width = self.reader_config['default_width']
    #         height = self.reader_config['default_height']
    #
    #     # Check if screen dimensions are available and valid
    #     try:
    #         screen_width = self.winfo_screenwidth()
    #         screen_height = self.winfo_screenheight()
    #         if screen_width > 0 and screen_height > 0:
    #             x = (screen_width // 2) - (width // 2)
    #             y = (screen_height // 2) - (height // 2)
    #             self.geometry(f"{width}x{height}+{x}+{y}")
    #         else:
    #              # Fallback if screen dimensions aren't available
    #              self.geometry(f"{width}x{height}")
    #     except tk.TclError:
    #          # Fallback if screen info fails
    #          self.geometry(f"{width}x{height}")

    def on_closing(self):
        """关闭窗口时的操作"""
        # 确保释放所有资源和引用
        try:
            # 保存阅读进度
            self.save_reading_progress()
            
            # 保存用户配置
            save_user_config(CONFIG)
            
            # 清理图标引用 (Important to avoid potential issues with Image references)
            self.font_icon = None
            self.color_icon = None
            self.prev_icon = None
            self.next_icon = None

            # 释放文本控件资源
            # No explicit destroy needed here, Toplevel destruction handles it

            # 释放自身
            self.destroy()
            self.master.deiconify() # 恢复主窗口显示
        except Exception as e:
            print(f"关闭阅读器窗口时出错: {e}")
            # 强制销毁
            self.destroy()

    def force_scroll_to_top(self):
        """强制滚动到文本顶部"""
        self.text_widget.see("1.0")
        self.text_widget.yview_moveto(0.0)  # 直接设置滚动位置为0
        print("强制滚动到顶部执行")

# 测试代码
if __name__ == "__main__":
    # Use CTk main loop for testing
    root = ctk.CTk() 
    root.withdraw()  # 隐藏主窗口

    # Sample content with chapters
    sample_content = """书名：《测试书》
作者：测试作者

简介：
这是一本测试用的书。

第1章 开始
这是第一章的内容。
有很多行。
非常多行。

第2章 中间
这是第二章的内容。
也有很多行。

番外 故事
这是一个番外篇。

第3章 结尾
这是最后一章的内容。
结束了。
"""
    
    # Need to pass the root explicitly now
    reader = Reader(root, sample_content, "测试书籍") 
    reader.focus() # Bring the reader window to front

    root.mainloop()