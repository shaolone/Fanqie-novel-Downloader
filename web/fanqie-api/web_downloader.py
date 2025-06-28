from flask import Flask, render_template, request, jsonify, send_file, make_response
import os
import threading
import time
import json
import requests
import bs4
from datetime import datetime
from download_novel import NovelDownloader
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许所有来源跨域

# 固定下载目录 - 使用绝对路径
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "novel_output")

# 全局变量存储下载状态
download_status = {}
download_history = []

def init_app():
    """初始化应用"""
    # 确保下载目录存在
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    # 检查目录权限
    if not os.access(DOWNLOAD_DIR, os.W_OK):
        print("警告: 下载目录没有写权限")

# 初始化应用
init_app()

class DownloadTask:
    def __init__(self, book_id, save_path):
        self.book_id = book_id
        self.save_path = save_path
        self.status = "pending"
        self.progress = 0
        self.total_chapters = 0
        self.success_count = 0
        self.error_message = ""
        self.start_time = datetime.now()
        self.end_time = None
        self.output_file = ""
        self.pause_event = threading.Event()
        self.cancel_event = threading.Event()
        
    def update_status(self, status, progress=0, total_chapters=None, success_count=0, error_message=""):
        # 状态映射为英文
        status_map = {
            '准备中': 'pending',
            '正在获取书籍信息...': 'pending',
            '获取到书籍': 'pending',
            '找到': 'pending',
            '下载中': 'downloading',
            '第': 'downloading',
            '下载完成': 'completed',
            '完成': 'completed',
            '失败': 'failed',
            '已暂停': 'paused',
            '已取消': 'cancelled',
            '正在保存文件...': 'downloading',
        }
        # 自动映射
        for k, v in status_map.items():
            if status.startswith(k):
                status = v
                break
        self.status = status
        self.progress = progress
        if total_chapters is not None:
            self.total_chapters = total_chapters
        self.success_count = success_count
        self.error_message = error_message
        
    def complete(self, success, output_file=""):
        self.status = "completed" if success else "failed"
        self.end_time = datetime.now()
        self.output_file = output_file

def get_downloaded_novels():
    """获取已下载的小说列表"""
    novels = []
    if os.path.exists(DOWNLOAD_DIR):
        for file in os.listdir(DOWNLOAD_DIR):
            if file.endswith('.txt'):
                file_path = os.path.join(DOWNLOAD_DIR, file)
                file_size = os.path.getsize(file_path)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                # 从文件名提取书名
                book_name = file.replace('.txt', '')
                if book_name.startswith('《') and book_name.endswith('》'):
                    book_name = book_name[1:-1]  # 移除《》
                # 读取作者
                author = "未知"
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.startswith("作者："):
                                author = line.replace("作者：", "").strip()
                                break
                except Exception:
                    pass
                novels.append({
                    'filename': file,
                    'book_name': book_name,
                    'author': author,
                    'file_size': file_size,
                    'file_size_mb': round(file_size / (1024 * 1024), 2),
                    'download_time': file_time.strftime('%Y-%m-%d %H:%M:%S')
                })
    novels.sort(key=lambda x: x['download_time'], reverse=True)
    return novels

def check_novel_exists(book_id):
    """检查小说是否已下载"""
    try:
        # 先获取书籍信息
        downloader = NovelDownloader()
        headers = downloader.get_headers()
        name, author_name, description = downloader.get_book_info(book_id, headers)
        
        if not name:
            return None, None
        
        # 获取章节数
        total_chapters = 0
        try:
            url = f'https://fanqienovel.com/page/{book_id}'
            response = requests.get(url, headers=headers)
            soup = bs4.BeautifulSoup(response.text, 'html.parser')
            item_ids = downloader.extract_chapters(soup)
            total_chapters = len(item_ids)
        except Exception:
            pass
        
        # 检查文件是否存在
        filename = f"{name}.txt"
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            return {
                'exists': True,
                'book_name': name,
                'author': author_name,
                'filename': filename,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'download_time': file_time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_chapters': total_chapters
            }, None
        else:
            return {
                'exists': False,
                'book_name': name,
                'author': author_name,
                'total_chapters': total_chapters
            }, None
            
    except Exception as e:
        return None, str(e)

def download_task_worker(task_id, book_id, save_path, settings):
    """后台下载任务"""
    task = download_status[task_id]
    
    try:
        downloader = NovelDownloader()
        
        # 应用前端传递的设置
        if settings:
            print(f"收到前端设置: {settings}")
            # 更新下载器配置
            if 'batch_size' in settings:
                old_batch_size = downloader.config["batch_size"]
                downloader.config["batch_size"] = int(settings['batch_size'])
                print(f"批量大小已更新: {old_batch_size} -> {downloader.config['batch_size']}")
            if 'retry_count' in settings:
                old_retry_count = downloader.config["max_retries"]
                downloader.config["max_retries"] = int(settings['retry_count'])
                print(f"重试次数已更新: {old_retry_count} -> {downloader.config['max_retries']}")
        else:
            print("未收到前端设置，使用默认配置")
        
        print(f"当前下载器配置: {downloader.config}")
        
        # 开始下载
        task.update_status("正在获取书籍信息...")
        
        headers = downloader.get_headers()
        
        # 获取书籍信息
        name, author_name, description = downloader.get_book_info(book_id, headers)
        if not name:
            task.update_status("failed", error_message="无法获取书籍信息，请检查小说ID或网络连接")
            task.complete(False)
            return

        task.update_status(f"获取到书籍：《{name}》", progress=5)
        
        # 获取章节列表
        url = f'https://fanqienovel.com/page/{book_id}'
        response = requests.get(url, headers=headers)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        
        item_ids = downloader.extract_chapters(soup)
        if not item_ids:
            task.update_status("failed", error_message="未找到任何章节")
            task.complete(False)
            return

        task.total_chapters = len(item_ids)
        task.update_status(f"找到 {len(item_ids)} 章，开始下载...", progress=10, total_chapters=len(item_ids))
        
        # 创建保存目录
        os.makedirs(save_path, exist_ok=True)
        
        # 创建文件并写入信息
        output_file = os.path.join(save_path, f"{name}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"书名：《{name}》\n作者：{author_name}\n\n简介：\n{description}\n\n")

        # 分批下载
        batch_size = downloader.config["batch_size"]
        print(f"使用批量大小: {batch_size}")
        total_batches = (len(item_ids) + batch_size - 1) // batch_size
        all_chapters = {}
        success_count = 0

        for batch_num in range(total_batches):
            # 检查取消
            if task.cancel_event.is_set():
                task.update_status("cancelled", progress=task.progress, success_count=success_count)
                task.complete(False)
                return
            # 检查暂停
            while task.pause_event.is_set():
                task.update_status("paused", progress=task.progress, success_count=success_count)
                time.sleep(1)
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(item_ids))
            item_ids_batch = item_ids[start_idx:end_idx]
            
            print(f"第 {batch_num + 1}/{total_batches} 批，章节 {start_idx + 1}-{end_idx}，批量大小: {len(item_ids_batch)}")
            
            task.update_status(f"第 {batch_num + 1}/{total_batches} 批下载中...", 
                             progress=10 + (batch_num + 1) * 80 // total_batches,
                             success_count=success_count)
            
            # 批量下载
            batch_data = downloader.download_batch_content(book_id, item_ids_batch)
            
            if batch_data:
                # 处理下载的内容
                for item_id, chapter_data in batch_data.items():
                    content = chapter_data.get("content", "")
                    title = chapter_data.get("title", f"第{start_idx + item_ids_batch.index(item_id) + 1}章")
                    
                    if content:
                        processed_content = downloader.process_content(content, title)
                        all_chapters[item_id] = {
                            "title": title,
                            "content": processed_content,
                            "index": start_idx + item_ids_batch.index(item_id)
                        }
                        success_count += 1
                
                task.update_status(f"第 {batch_num + 1} 批完成", 
                                 progress=10 + (batch_num + 1) * 80 // total_batches,
                                 success_count=success_count)
            else:
                task.update_status(f"第 {batch_num + 1} 批下载失败", 
                                 progress=10 + (batch_num + 1) * 80 // total_batches,
                                 success_count=success_count)
            
            # 批次间休息，使用前端设置的下载间隔
            if batch_num < total_batches - 1:
                delay = settings.get('download_delay', 3) if settings else 3
                print(f"等待 {delay} 秒后继续下一批...")
                time.sleep(delay)

        # 保存文件
        task.update_status("正在保存文件...", progress=90, success_count=success_count)
        
        # 按索引排序
        sorted_chapters = sorted(all_chapters.values(), key=lambda x: x["index"])
        
        # 检查重复章节内容
        processed_contents = set()
        with open(output_file, 'a', encoding='utf-8') as f:
            for chapter in sorted_chapters:
                # 检查内容是否重复
                content_hash = hash(chapter["content"])
                if content_hash in processed_contents:
                    continue

                processed_contents.add(content_hash)
                f.write(f"\n{chapter['title']}\n\n")
                f.write(chapter["content"] + "\n\n")

        final_success_count = len(processed_contents)
        task.update_status(f"下载完成！成功：{final_success_count}章", 
                         progress=100, success_count=final_success_count)
        task.complete(True, output_file)
        
        # 添加到历史记录
        download_history.append({
            "task_id": task_id,
            "book_id": book_id,
            "book_name": name,
            "status": "completed",
            "success_count": final_success_count,
            "total_chapters": len(item_ids),
            "start_time": task.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": task.end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "output_file": output_file
        })
        
    except Exception as e:
        print(f"下载任务异常: {str(e)}")
        task.update_status("failed", error_message=str(e))
        task.complete(False)
        
        # 添加到历史记录
        download_history.append({
            "task_id": task_id,
            "book_id": book_id,
            "book_name": "未知",
            "status": "failed",
            "error_message": str(e),
            "start_time": task.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": task.end_time.strftime("%Y-%m-%d %H:%M:%S")
        })

@app.route('/')
def index():
    return render_template('kawaii.html')

@app.route('/api/check_novel', methods=['POST', 'OPTIONS'])
def check_novel():
    if request.method == 'OPTIONS':
        # 处理预检请求，返回CORS头
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response, 204

    data = request.get_json()
    book_id = data.get('book_id', '').strip()
    
    if not book_id:
        response = jsonify({"success": False, "message": "请输入小说ID"})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    result, error = check_novel_exists(book_id)
    
    if error:
        response = jsonify({"success": False, "message": f"检查失败: {error}"})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    response = jsonify({
        "success": True,
        "data": result
    })
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/api/download', methods=['POST'])
def start_download():
    data = request.get_json()
    book_id = data.get('book_id', '').strip()
    force_download = data.get('force_download', False)  # 是否强制重新下载
    settings = data.get('settings', {})  # 前端传递的下载设置

    if not book_id:
        return jsonify({"success": False, "message": "请输入小说ID"})

    # 检查是否已下载
    if not force_download:
        result, error = check_novel_exists(book_id)
        if result and result.get('exists'):
            return jsonify({
                "success": False,
                "message": "小说已存在",
                "novel_info": result
            })

    # 生成任务ID
    task_id = f"task_{int(time.time())}"

    # 创建下载任务
    task = DownloadTask(book_id, DOWNLOAD_DIR)
    download_status[task_id] = task

    # 启动后台下载线程，传递设置参数
    thread = threading.Thread(target=download_task_worker, args=(task_id, book_id, DOWNLOAD_DIR, settings))
    thread.daemon = True
    thread.start()

    # 获取书籍信息
    downloader = NovelDownloader()
    headers = downloader.get_headers()
    name, author_name, description = downloader.get_book_info(book_id, headers)
    total_chapters = 0
    try:
        url = f'https://fanqienovel.com/page/{book_id}'
        response = requests.get(url, headers=headers)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        item_ids = downloader.extract_chapters(soup)
        total_chapters = len(item_ids)
    except Exception:
        pass

    return jsonify({
        "success": True,
        "data": {
            "task_id": task_id,
            "title": name or "未知小说",
            "author": author_name or "未知作者",
            "total_chapters": total_chapters
        },
        "message": "下载任务已启动"
    })

@app.route('/api/status/<task_id>')
def get_status(task_id):
    if task_id not in download_status:
        return jsonify({"success": False, "message": "任务不存在"})
    
    task = download_status[task_id]
    return jsonify({
        "success": True,
        "status": task.status,
        "progress": task.progress,
        "total_chapters": task.total_chapters,
        "success_count": task.success_count,
        "downloaded_chapters": task.success_count,
        "error_message": task.error_message,
        "start_time": task.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": task.end_time.strftime("%Y-%m-%d %H:%M:%S") if task.end_time else None
    })

@app.route('/api/download/<task_id>')
def download_file(task_id):
    if task_id not in download_status:
        return jsonify({"success": False, "message": "任务不存在"})
    
    task = download_status[task_id]
    if not task.output_file:
        return jsonify({"success": False, "message": "任务尚未完成，没有输出文件"})
    
    if not os.path.exists(task.output_file):
        return jsonify({
            "success": False, 
            "message": "文件不存在或已被删除"
        })
    
    try:
        return send_file(task.output_file, as_attachment=True)
    except Exception as e:
        return jsonify({
            "success": False, 
            "message": "文件下载失败，请稍后重试"
        })

@app.route('/api/novels')
def get_novels():
    """获取已下载的小说列表"""
    novels = get_downloaded_novels()
    return jsonify({
        "success": True,
        "novels": novels
    })

@app.route('/api/download_novel/<filename>')
def download_novel_file(filename):
    """下载指定的小说文件"""
    # 确保文件名安全，防止路径遍历攻击
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({"success": False, "message": "无效的文件名"})
    
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({
            "success": False, 
            "message": "文件不存在或已被删除"
        })
    
    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({
            "success": False, 
            "message": "文件下载失败，请稍后重试"
        })

@app.route('/api/history')
def get_history():
    return jsonify({
        "success": True,
        "history": download_history[-10:]  # 返回最近10条记录
    })

@app.route('/api/pause_download/<task_id>', methods=['POST'])
def pause_download(task_id):
    task = download_status.get(task_id)
    if task:
        task.pause_event.set()
        return jsonify({"success": True, "message": "已暂停"})
    return jsonify({"success": False, "message": "任务不存在"})

@app.route('/api/resume_download/<task_id>', methods=['POST'])
def resume_download(task_id):
    task = download_status.get(task_id)
    if task:
        task.pause_event.clear()
        return jsonify({"success": True, "message": "已恢复"})
    return jsonify({"success": False, "message": "任务不存在"})

@app.route('/api/cancel_download/<task_id>', methods=['POST'])
def cancel_download(task_id):
    task = download_status.get(task_id)
    if task:
        task.cancel_event.set()
        return jsonify({"success": True, "message": "已取消"})
    return jsonify({"success": False, "message": "任务不存在"})

@app.route('/api/delete_novel/<filename>', methods=['DELETE'])
def delete_novel(filename):
    """删除指定的小说文件"""
    # 确保文件名安全，防止路径遍历攻击
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({"success": False, "message": "无效的文件名"})
    
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return jsonify({"success": True, "message": "删除成功"})
        except Exception as e:
            return jsonify({"success": False, "message": f"删除失败: {str(e)}"})
    return jsonify({"success": False, "message": "文件不存在"})

@app.route('/api/clear_history', methods=['DELETE'])
def clear_history():
    """清空下载历史记录"""
    global download_history
    try:
        download_history.clear()
        return jsonify({"success": True, "message": "历史记录已清空"})
    except Exception as e:
        return jsonify({"success": False, "message": f"清空失败: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
