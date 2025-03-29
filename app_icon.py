from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(save_path, size=(128, 128), text="F", bg_color="#3a7ebf", text_color="#ffffff"):
    """
    创建一个简单的应用图标，绘制一个圆形背景和文字
    
    参数:
    save_path: 保存路径
    size: 图标尺寸
    text: 图标中显示的文字
    bg_color: 背景颜色
    text_color: 文字颜色
    """
    # 创建透明背景的图像
    image = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # 绘制圆形背景
    circle_radius = min(size) // 2
    circle_center = (size[0] // 2, size[1] // 2)
    draw.ellipse(
        (
            circle_center[0] - circle_radius, 
            circle_center[1] - circle_radius,
            circle_center[0] + circle_radius, 
            circle_center[1] + circle_radius
        ), 
        fill=bg_color
    )
    
    # 尝试加载字体，如果失败，使用默认字体
    try:
        # 计算合适的字体大小
        font_size = int(circle_radius * 1.2)
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # 如果找不到指定字体，使用默认字体
            font = ImageFont.load_default()
            font_size = circle_radius  # 调整默认字体大小
            
        # 获取文本的大小
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # 计算文本位置使其居中
        text_position = (
            circle_center[0] - text_width // 2,
            circle_center[1] - text_height // 2
        )
        
        # 绘制文本
        draw.text(text_position, text, font=font, fill=text_color)
    except Exception as e:
        print(f"绘制文本失败: {e}")
    
    # 保存图像
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    image.save(save_path)
    print(f"图标已保存到: {save_path}")
    return save_path

def create_app_icons(base_folder="assets"):
    """创建应用程序所需的所有图标"""
    # 确保存在assets文件夹
    os.makedirs(base_folder, exist_ok=True)
    
    # 创建应用图标
    icon_path = os.path.join(base_folder, "app_icon.png")
    create_icon(icon_path, text="F", bg_color="#3a7ebf")
    
    # 创建各个功能图标
    settings_path = os.path.join(base_folder, "settings.png")
    create_icon(settings_path, text="S", bg_color="#4CAF50", size=(64, 64))
    
    library_path = os.path.join(base_folder, "library.png")
    create_icon(library_path, text="L", bg_color="#FF9800", size=(64, 64))
    
    read_path = os.path.join(base_folder, "read.png")
    create_icon(read_path, text="R", bg_color="#9C27B0", size=(64, 64))
    
    browse_path = os.path.join(base_folder, "browse.png")
    create_icon(browse_path, text="B", bg_color="#607D8B", size=(64, 64))
    
    download_path = os.path.join(base_folder, "download.png")
    create_icon(download_path, text="D", bg_color="#F44336", size=(64, 64))
    
    # 新增图标
    folder_path = os.path.join(base_folder, "folder.png")
    create_icon(folder_path, text="F", bg_color="#FFC107", size=(64, 64))
    
    delete_path = os.path.join(base_folder, "delete.png")
    create_icon(delete_path, text="X", bg_color="#f44336", size=(64, 64))
    
    search_path = os.path.join(base_folder, "search.png")
    create_icon(search_path, text="Q", bg_color="#2196F3", size=(64, 64))
    
    font_path = os.path.join(base_folder, "font.png")
    create_icon(font_path, text="A", bg_color="#673AB7", size=(64, 64))
    
    color_path = os.path.join(base_folder, "color.png")
    create_icon(color_path, text="C", bg_color="#009688", size=(64, 64))
    
    reset_path = os.path.join(base_folder, "reset.png")
    create_icon(reset_path, text="R", bg_color="#FF5722", size=(64, 64))
    
    print("所有图标创建完成!")

if __name__ == "__main__":
    create_app_icons() 