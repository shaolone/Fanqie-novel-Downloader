import tkinter as tk
from tkinter import colorchooser, messagebox
import customtkinter as ctk
from config import CONFIG, save_user_config
import os
from PIL import Image

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, master, geometry=None): # 添加 geometry 参数
        super().__init__(master)
        self.title("设置")
        # self.geometry("550x450") # Removed hardcoded size
        self.resizable(False, False)
        if geometry:
            self.geometry(geometry) # 如果提供了 geometry，则使用它
        else:
            self.geometry(master.geometry()) # 否则，使用主窗口的大小
        self.config = CONFIG.copy()
        
        # 加载图标
        self.load_icons()
        
        # 设置UI
        self.setup_ui()
        
        # 模态对话框
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.master = master
        
        # 居中显示 (Removed call)
        # self.center_window()

    def load_icons(self):
        """加载按钮图标 (Temporarily disabled)"""
        # icon_size = (20, 20)
        # assets_path = "assets"
        
        # # Helper function to load icon safely (copied from library.py fix)
        # def _load_single_icon(filename):
        #     icon_path = os.path.join(assets_path, filename)
        #     if os.path.exists(icon_path):
        #         try:
        #             pil_image = Image.open(icon_path).resize(icon_size)
        #             return ctk.CTkImage(pil_image)
        #         except Exception as e:
        #             print(f"Error loading icon '{filename}': {e}")
        #             return None
        #     else:
        #         return None

        # self.settings_icon = _load_single_icon("settings.png")
        # self.reset_icon = _load_single_icon("reset.png")
        
        # For now, disable all icons to avoid errors
        self.settings_icon = None
        self.reset_icon = None
        
    # def center_window(self): # Removed method
    #     """将窗口居中显示"""
    #     self.update_idletasks()
    #     width = self.winfo_width()
    #     height = self.winfo_height()
    #     x = (self.winfo_screenwidth() // 2) - (width // 2)
    #     y = (self.winfo_screenheight() // 2) - (height // 2)
    #     self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        # 主框架
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 选项卡
        self.tab_view = ctk.CTkTabview(main_frame)
        self.tab_view.pack(fill=tk.BOTH, expand=True)
        
        # 添加选项卡
        download_tab = self.tab_view.add("下载设置")
        reader_tab = self.tab_view.add("阅读器设置")
        appearance_tab = self.tab_view.add("外观设置")
        
        # 下载设置选项卡内容
        self.setup_download_tab(download_tab)
        
        # 阅读器设置选项卡内容
        self.setup_reader_tab(reader_tab)
        
        # 外观设置选项卡内容
        self.setup_appearance_tab(appearance_tab)
        
        # 按钮区域
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # 重置按钮
        reset_button = ctk.CTkButton(
            button_frame, 
            text="恢复默认", 
            # image=self.reset_icon, # Temporarily removed
            # compound="left", # Temporarily removed
            command=self.on_reset,
            fg_color="#FF5722",
            hover_color="#E64A19"
        )
        reset_button.pack(side=tk.LEFT, padx=5)
        
        # 取消和确定按钮
        cancel_button = ctk.CTkButton(
            button_frame, 
            text="取消", 
            command=self.on_cancel,
            fg_color="#607D8B",
            hover_color="#455A64"
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        save_button = ctk.CTkButton(
            button_frame, 
            text="确定", 
            command=self.on_save,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        save_button.pack(side=tk.RIGHT, padx=5)

    def setup_download_tab(self, parent):
        # 使用网格布局
        parent.grid_columnconfigure(1, weight=1)
        
        row = 0
        # 最大线程数
        ctk.CTkLabel(parent, text="最大线程数:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=15)
        self.max_workers_var = ctk.IntVar(value=self.config["request"]["max_workers"])
        workers_slider = ctk.CTkSlider(
            parent,
            from_=1,
            to=20,
            number_of_steps=19,
            variable=self.max_workers_var
        )
        workers_slider.grid(row=row, column=1, sticky=tk.EW, padx=10, pady=15)
        ctk.CTkLabel(parent, textvariable=self.max_workers_var, width=30).grid(row=row, column=2, padx=10, pady=15)
        
        row += 1
        # 请求超时时间
        ctk.CTkLabel(parent, text="请求超时时间(秒):").grid(row=row, column=0, sticky=tk.W, padx=10, pady=15)
        self.timeout_var = ctk.IntVar(value=self.config["request"]["request_timeout"])
        timeout_slider = ctk.CTkSlider(
            parent,
            from_=5,
            to=60,
            number_of_steps=55,
            variable=self.timeout_var
        )
        timeout_slider.grid(row=row, column=1, sticky=tk.EW, padx=10, pady=15)
        ctk.CTkLabel(parent, textvariable=self.timeout_var, width=30).grid(row=row, column=2, padx=10, pady=15)
        
        row += 1
        # 最大重试次数
        ctk.CTkLabel(parent, text="最大重试次数:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=15)
        self.retries_var = ctk.IntVar(value=self.config["request"]["max_retries"])
        retries_slider = ctk.CTkSlider(
            parent,
            from_=1,
            to=10,
            number_of_steps=9,
            variable=self.retries_var
        )
        retries_slider.grid(row=row, column=1, sticky=tk.EW, padx=10, pady=15)
        ctk.CTkLabel(parent, textvariable=self.retries_var, width=30).grid(row=row, column=2, padx=10, pady=15)
        
        # 填充剩余空间
        spacer = ctk.CTkFrame(parent, fg_color="transparent", height=50)
        spacer.grid(row=row+1, column=0, columnspan=3, sticky=tk.EW)

    def setup_reader_tab(self, parent):
        # 使用网格布局
        parent.grid_columnconfigure(1, weight=1)
        
        row = 0
        # 窗口宽度
        ctk.CTkLabel(parent, text="默认窗口宽度:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=15)
        self.width_var = ctk.IntVar(value=self.config["reader"]["default_width"])
        width_slider = ctk.CTkSlider(
            parent,
            from_=400,
            to=1920,
            number_of_steps=152,
            variable=self.width_var
        )
        width_slider.grid(row=row, column=1, sticky=tk.EW, padx=10, pady=15)
        ctk.CTkLabel(parent, textvariable=self.width_var, width=50).grid(row=row, column=2, padx=10, pady=15)
        
        row += 1
        # 窗口高度
        ctk.CTkLabel(parent, text="默认窗口高度:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=15)
        self.height_var = ctk.IntVar(value=self.config["reader"]["default_height"])
        height_slider = ctk.CTkSlider(
            parent,
            from_=300,
            to=1080,
            number_of_steps=78,
            variable=self.height_var
        )
        height_slider.grid(row=row, column=1, sticky=tk.EW, padx=10, pady=15)
        ctk.CTkLabel(parent, textvariable=self.height_var, width=50).grid(row=row, column=2, padx=10, pady=15)
        
        row += 1
        # 内边距
        ctk.CTkLabel(parent, text="默认内边距:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=15)
        self.padding_var = ctk.IntVar(value=self.config["reader"]["padding"])
        padding_slider = ctk.CTkSlider(
            parent,
            from_=0,
            to=50,
            number_of_steps=50,
            variable=self.padding_var
        )
        padding_slider.grid(row=row, column=1, sticky=tk.EW, padx=10, pady=15)
        ctk.CTkLabel(parent, textvariable=self.padding_var, width=30).grid(row=row, column=2, padx=10, pady=15)
        
        row += 1
        # 字体大小
        ctk.CTkLabel(parent, text="默认字体大小:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=15)
        self.font_size_var = ctk.IntVar(value=self.config["reader"]["default_size"])
        font_size_slider = ctk.CTkSlider(
            parent,
            from_=8,
            to=24,
            number_of_steps=16,
            variable=self.font_size_var
        )
        font_size_slider.grid(row=row, column=1, sticky=tk.EW, padx=10, pady=15)
        ctk.CTkLabel(parent, textvariable=self.font_size_var, width=30).grid(row=row, column=2, padx=10, pady=15)
        
        row += 1
        # 颜色设置框架
        color_frame = ctk.CTkFrame(parent)
        color_frame.grid(row=row, column=0, columnspan=3, sticky=tk.EW, padx=10, pady=15)
        
        # 文字颜色
        text_color_label = ctk.CTkLabel(color_frame, text="默认文字颜色:")
        text_color_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        
        self.text_color_preview = ctk.CTkButton(
            color_frame, 
            text="",  
            width=30,
            height=20,
            fg_color=self.config["reader"]["default_fg"],
            hover_color=self.config["reader"]["default_fg"],
            command=lambda: None  # 防止点击反应
        )
        self.text_color_preview.grid(row=0, column=1, padx=10, pady=10)
        
        ctk.CTkButton(
            color_frame, 
            text="选择", 
            width=60,
            command=self.choose_text_color
        ).grid(row=0, column=2, padx=10, pady=10)
        
        # 背景颜色
        bg_color_label = ctk.CTkLabel(color_frame, text="默认背景颜色:")
        bg_color_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        
        self.bg_color_preview = ctk.CTkButton(
            color_frame, 
            text="",  
            width=30,
            height=20,
            fg_color=self.config["reader"]["default_bg"],
            hover_color=self.config["reader"]["default_bg"],
            command=lambda: None  # 防止点击反应
        )
        self.bg_color_preview.grid(row=1, column=1, padx=10, pady=10)
        
        ctk.CTkButton(
            color_frame, 
            text="选择", 
            width=60,
            command=self.choose_bg_color
        ).grid(row=1, column=2, padx=10, pady=10)

    def setup_appearance_tab(self, parent):
        # 使用网格布局
        parent.grid_columnconfigure(1, weight=1)
        
        # 主题选择
        row = 0
        ctk.CTkLabel(parent, text="界面主题:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=15)
        
        theme_frame = ctk.CTkFrame(parent, fg_color="transparent")
        theme_frame.grid(row=row, column=1, sticky=tk.W, padx=10, pady=15)
        
        themes = [("亮色", "light"), ("暗色", "dark"), ("跟随系统", "system")]
        self.theme_var = ctk.StringVar(value="dark")  # 默认暗色
        
        for i, (text, value) in enumerate(themes):
            theme_button = ctk.CTkRadioButton(
                theme_frame,
                text=text,
                variable=self.theme_var,
                value=value
            )
            theme_button.grid(row=0, column=i, padx=10)
        
        # 颜色主题
        row += 1
        ctk.CTkLabel(parent, text="颜色主题:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=15)
        
        color_theme_frame = ctk.CTkFrame(parent, fg_color="transparent")
        color_theme_frame.grid(row=row, column=1, sticky=tk.W, padx=10, pady=15)
        
        color_themes = [("蓝色", "blue"), ("绿色", "green"), ("深蓝", "dark-blue")]
        self.color_theme_var = ctk.StringVar(value="blue")  # 默认蓝色
        
        for i, (text, value) in enumerate(color_themes):
            color_button = ctk.CTkRadioButton(
                color_theme_frame,
                text=text,
                variable=self.color_theme_var,
                value=value
            )
            color_button.grid(row=0, column=i, padx=10)
        
        # 界面缩放
        row += 1
        ctk.CTkLabel(parent, text="界面缩放:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=15)
        
        scaling_frame = ctk.CTkFrame(parent, fg_color="transparent")
        scaling_frame.grid(row=row, column=1, sticky=tk.W, padx=10, pady=15)
        
        scalings = [("80%", "80"), ("90%", "90"), ("100%", "100"), ("110%", "110"), ("120%", "120")]
        self.scaling_var = ctk.StringVar(value="100")  # 默认100%
        
        for i, (text, value) in enumerate(scalings):
            scaling_button = ctk.CTkRadioButton(
                scaling_frame,
                text=text,
                variable=self.scaling_var,
                value=value
            )
            scaling_button.grid(row=0, column=i, padx=5)
            
        # 动画效果
        row += 1
        ctk.CTkLabel(parent, text="动画效果:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=15)
        
        animation_frame = ctk.CTkFrame(parent, fg_color="transparent")
        animation_frame.grid(row=row, column=1, sticky=tk.W, padx=10, pady=15)
        
        self.animation_var = ctk.BooleanVar(value=True)
        animation_switch = ctk.CTkSwitch(
            animation_frame,
            text="启用平滑过渡动画",
            variable=self.animation_var,
            onvalue=True,
            offvalue=False
        )
        animation_switch.grid(row=0, column=0, padx=10)
        
        # 填充剩余空间
        spacer = ctk.CTkFrame(parent, fg_color="transparent", height=50)
        spacer.grid(row=row+1, column=0, columnspan=2, sticky=tk.EW)

    def choose_text_color(self):
        """选择文字颜色"""
        color = colorchooser.askcolor(title="选择文字颜色", initialcolor=self.config["reader"]["default_fg"])
        if color[1]:
            self.text_color_preview.configure(fg_color=color[1], hover_color=color[1])
            self.config["reader"]["default_fg"] = color[1]

    def choose_bg_color(self):
        """选择背景颜色"""
        color = colorchooser.askcolor(title="选择背景颜色", initialcolor=self.config["reader"]["default_bg"])
        if color[1]:
            self.bg_color_preview.configure(fg_color=color[1], hover_color=color[1])
            self.config["reader"]["default_bg"] = color[1]

    def on_save(self):
        """保存设置"""
        # 保存下载设置
        self.config["request"]["max_workers"] = self.max_workers_var.get()
        self.config["request"]["request_timeout"] = self.timeout_var.get()
        self.config["request"]["max_retries"] = self.retries_var.get()
        
        # 保存阅读器设置
        self.config["reader"]["default_width"] = self.width_var.get()
        self.config["reader"]["default_height"] = self.height_var.get()
        self.config["reader"]["padding"] = self.padding_var.get()
        self.config["reader"]["default_size"] = self.font_size_var.get()
        
        # 保存外观设置
        # 这些设置可能需要立即应用，然后才保存
        ctk.set_appearance_mode(self.theme_var.get())
        ctk.set_default_color_theme(self.color_theme_var.get())
        ctk.set_widget_scaling(float(self.scaling_var.get()) / 100.0)
        
        # 保存到全局配置
        for category in self.config:
            if category in CONFIG:
                CONFIG[category].update(self.config[category])
        
        # 特殊处理外观设置
        if "appearance" not in CONFIG:
            CONFIG["appearance"] = {}
        CONFIG["appearance"]["theme"] = self.theme_var.get()
        CONFIG["appearance"]["color_theme"] = self.color_theme_var.get()
        CONFIG["appearance"]["scaling"] = self.scaling_var.get()
        CONFIG["appearance"]["animation"] = self.animation_var.get()
        
        if save_user_config(CONFIG):
            messagebox.showinfo("成功", "设置已保存并应用")
            self.master.deiconify() # 恢复主窗口显示
            self.destroy()
        else:
            messagebox.showerror("错误", "保存设置失败")

    def on_cancel(self):
        """取消并关闭窗口"""
        self.master.deiconify() # 恢复主窗口显示
        self.destroy()

    def on_reset(self):
        """重置为默认设置"""
        if messagebox.askyesno("确认", "确定要恢复默认设置吗？"):
            from config import REQUEST_CONFIG, READER_CONFIG, FILE_CONFIG
            
            # 重置配置
            self.config["request"] = REQUEST_CONFIG.copy()
            self.config["reader"] = READER_CONFIG.copy()
            self.config["file"] = FILE_CONFIG.copy()
            
            # 更新下载设置UI
            self.max_workers_var.set(self.config["request"]["max_workers"])
            self.timeout_var.set(self.config["request"]["request_timeout"])
            self.retries_var.set(self.config["request"]["max_retries"])
            
            # 更新阅读器设置UI
            self.width_var.set(self.config["reader"]["default_width"])
            self.height_var.set(self.config["reader"]["default_height"])
            self.padding_var.set(self.config["reader"]["padding"])
            self.font_size_var.set(self.config["reader"]["default_size"])
            
            # 更新颜色预览
            self.text_color_preview.configure(
                fg_color=self.config["reader"]["default_fg"],
                hover_color=self.config["reader"]["default_fg"]
            )
            self.bg_color_preview.configure(
                fg_color=self.config["reader"]["default_bg"],
                hover_color=self.config["reader"]["default_bg"]
            )
            
            # 重置外观设置
            self.theme_var.set("dark")
            self.color_theme_var.set("blue")
            self.scaling_var.set("100")
            self.animation_var.set(True)