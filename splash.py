import tkinter as tk
import customtkinter as ctk
import time
import threading
from PIL import Image, ImageTk

class SplashScreen(ctk.CTkToplevel):
    def __init__(self, parent, logo_path=None, duration=2.0):
        super().__init__(parent)
        self.parent = parent
        self.duration = duration  # 持续时间（秒）
        
        # 配置窗口
        self.title("")
        self.overrideredirect(True)  # 移除边框
        self.attributes("-topmost", True)  # 置顶窗口
        
        # 设置窗口大小和位置
        width = 400
        height = 300
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        pos_x = (screen_width // 2) - (width // 2)
        pos_y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
        
        # 设置圆角边框背景
        self.configure(fg_color="#2d2d2d")
        
        # 创建标题和版本标签
        self.create_widgets(logo_path)
        
        # 创建进度条
        self.progress = ctk.CTkProgressBar(self, orientation="horizontal", mode="indeterminate")
        self.progress.grid(row=3, column=0, padx=40, pady=(0, 30), sticky="ew")
        self.progress.start()
        
        # 使窗口居中显示
        self.center_window()
        
        # 启动关闭计时器
        self.start_close_timer()
        # 绑定销毁事件以确保父窗口显示
        self.bind("<Destroy>", self.on_splash_destroy)

    def on_splash_destroy(self, event=None):
        """启动画面销毁时，确保父窗口显示"""
        # 确保事件源是自身，避免意外触发
        if event is None or event.widget == self:
            try:
                # 检查父窗口是否存在且是 Toplevel 或 Tk 类型
                if self.parent and isinstance(self.parent, (tk.Tk, tk.Toplevel, ctk.CTk)):
                    print("启动画面销毁，尝试显示主窗口...")
                    self.parent.deiconify()
                    self.parent.lift() # 尝试将窗口置顶
                    self.parent.focus_force() # 强制获取焦点
                    print("主窗口 deiconify 调用完成。")
                else:
                    print("父窗口无效或不存在，无法显示。")
            except Exception as e:
                print(f"显示主窗口时出错: {e}")

    def create_widgets(self, logo_path):
        # 配置grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        
        # Logo 图像
        if logo_path:
            try:
                logo_img = Image.open(logo_path)
                # 调整大小
                logo_img = logo_img.resize((120, 120), Image.LANCZOS)
                logo_ctk = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(120, 120))
                
                logo_label = ctk.CTkLabel(self, image=logo_ctk, text="")
                logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
            except Exception as e:
                print(f"无法加载logo图像: {e}")
                # 使用文字替代
                title_label = ctk.CTkLabel(self, text="番茄小说下载器", font=("黑体", 24))
                title_label.grid(row=0, column=0, padx=20, pady=(50, 10))
        else:
            # 使用文字替代
            title_label = ctk.CTkLabel(self, text="番茄小说下载器", font=("黑体", 24))
            title_label.grid(row=0, column=0, padx=20, pady=(50, 10))
        
        # 应用名称
        name_label = ctk.CTkLabel(self, text="番茄小说下载器", font=("黑体", 20))
        name_label.grid(row=1, column=0, padx=20, pady=(10, 5))
        
        # 版本号和版权信息
        version_label = ctk.CTkLabel(self, text="专业版 v1.2.0", font=("黑体", 12))
        version_label.grid(row=2, column=0, padx=20, pady=(0, 20))

    def center_window(self):
        """将窗口居中显示"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def start_close_timer(self):
        """启动关闭计时器"""
        # 不使用线程，直接使用after设置定时器
        self.after(int(self.duration * 1000), self.destroy)
        # self.after(int(self.duration * 1000) + 100, self.parent.deiconify) # 移除这行，由 on_splash_destroy 处理

    def close_splash_screen(self):
        """已废弃，使用start_close_timer替代"""
        pass

# 测试代码
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 创建并显示启动画面
    splash = SplashScreen(root, logo_path=None, duration=3.0)
    
    # 主循环
    root.mainloop() 