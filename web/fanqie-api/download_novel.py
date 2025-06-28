import sys
import os
import time
import requests
import bs4
import re
import json
import random
from collections import OrderedDict

class NovelDownloader:
    def __init__(self, api_url="http://api-test.tutuxka.top/dragon/content"):
        self.api_url = api_url
        self.config = {
            "max_retries": 3,
            "request_timeout": 30,
            "batch_size": 300,  # 每批下载300章
            "user_agents": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            ]
        }

    def get_headers(self, cookie=None):
        """生成随机请求头"""
        return {
            "User-Agent": random.choice(self.config["user_agents"]),
            "Cookie": cookie if cookie else self.get_cookie()
        }

    def get_cookie(self):
        """生成或加载Cookie"""
        cookie_path = "cookie.json"
        if os.path.exists(cookie_path):
            try:
                with open(cookie_path, 'r') as f:
                    return json.load(f)
            except:
                pass

        # 生成新Cookie
        for _ in range(10):
            novel_web_id = random.randint(10**18, 10**19-1)
            cookie = f'novel_web_id={novel_web_id}'
            try:
                resp = requests.get(
                    'https://fanqienovel.com',
                    headers={"User-Agent": random.choice(self.config["user_agents"])},
                    cookies={"novel_web_id": str(novel_web_id)},
                    timeout=10
                )
                if resp.ok:
                    with open(cookie_path, 'w') as f:
                        json.dump(cookie, f)
                    return cookie
            except Exception as e:
                print(f"Cookie生成失败: {str(e)}")
                time.sleep(0.5)
        raise Exception("无法获取有效Cookie")

    def get_book_info(self, book_id, headers):
        """获取书名、作者、简介"""
        url = f'https://fanqienovel.com/page/{book_id}'
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"网络请求失败，状态码: {response.status_code}")
            return None, None, None

        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        # 获取书名
        name_element = soup.find('h1')
        name = name_element.text if name_element else "未知书名"

        # 获取作者
        author_name_element = soup.find('div', class_='author-name')
        author_name = None
        if author_name_element:
            author_name_span = author_name_element.find('span', class_='author-name-text')
            author_name = author_name_span.text if author_name_span else "未知作者"

        # 获取简介
        description_element = soup.find('div', class_='page-abstract-content')
        description = None
        if description_element:
            description_p = description_element.find('p')
            description = description_p.text if description_p else "无简介"

        return name, author_name, description

    def extract_chapters(self, soup):
        """解析章节列表，返回item_ids"""
        item_ids = []
        for item in soup.select('div.chapter-item'):
            a_tag = item.find('a')
            if a_tag:
                item_id = a_tag['href'].split('/')[-1]
                item_ids.append(item_id)
        return item_ids

    def download_batch_content(self, book_id, item_ids_batch):
        """批量下载章节内容"""
        max_retries = self.config.get('max_retries', 3)
        retry_count = 0

        while retry_count < max_retries:
            try:
                # 将item_ids列表转换为逗号分隔的字符串
                item_ids_str = ','.join(item_ids_batch)
                
                params = {
                    "book_id": book_id,
                    "item_ids": item_ids_str
                }
                
                print(f"正在下载 {len(item_ids_batch)} 章...")
                response = requests.get(self.api_url, params=params, timeout=self.config["request_timeout"])
                data = response.json()

                if "data" in data and data["data"]:
                    return data["data"]
                else:
                    print(f"API返回数据格式错误: {data}")
                    retry_count += 1
                    time.sleep(2 * retry_count)
                    
            except Exception as e:
                print(f"批量下载失败: {str(e)}, 重试第{retry_count + 1}次...")
                retry_count += 1
                time.sleep(2 * retry_count)

        return {}

    def process_content(self, content, title):
        """处理章节内容，清理HTML标签"""
        # 移除HTML标签
        content = re.sub(r'<header>.*?</header>', '', content, flags=re.DOTALL)
        content = re.sub(r'<footer>.*?</footer>', '', content, flags=re.DOTALL)
        content = re.sub(r'</?article>', '', content)
        content = re.sub(r'<p idx="\d+">', '\n', content)
        content = re.sub(r'</p>', '\n', content)
        content = re.sub(r'<[^>]+>', '', content)
        content = re.sub(r'\\u003c|\\u003e', '', content)

        # 处理可能的重复章节标题行
        if title and content.startswith(title):
            content = content[len(title):].lstrip()

        content = re.sub(r'\n{2,}', '\n', content).strip()
        content = '\n'.join(['    ' + line if line.strip() else line for line in content.split('\n')])
        return content

    def download_novel(self, book_id, save_path):
        """下载小说的主函数"""
        try:
            headers = self.get_headers()
            print("正在获取书籍信息...")

            # 获取书籍信息
            name, author_name, description = self.get_book_info(book_id, headers)
            if not name:
                raise Exception("无法获取书籍信息，请检查小说ID或网络连接")

            print(f"书名：《{name}》")
            print(f"作者：{author_name}")
            print(f"简介：{description}")

            # 获取章节列表
            url = f'https://fanqienovel.com/page/{book_id}'
            response = requests.get(url, headers=headers)
            soup = bs4.BeautifulSoup(response.text, 'html.parser')

            item_ids = self.extract_chapters(soup)
            if not item_ids:
                raise Exception("未找到任何章节")

            print(f"\n开始下载，共 {len(item_ids)} 章")
            os.makedirs(save_path, exist_ok=True)

            # 创建文件并写入信息
            output_file = os.path.join(save_path, f"{name}.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"书名：《{name}》\n作者：{author_name}\n\n简介：\n{description}\n\n")

            # 分批下载
            batch_size = self.config["batch_size"]
            total_batches = (len(item_ids) + batch_size - 1) // batch_size
            all_chapters = {}

            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, len(item_ids))
                item_ids_batch = item_ids[start_idx:end_idx]
                
                print(f"\n=== 第 {batch_num + 1}/{total_batches} 批 ===")
                print(f"下载章节 {start_idx + 1} - {end_idx}")
                
                # 批量下载
                batch_data = self.download_batch_content(book_id, item_ids_batch)
                
                if batch_data:
                    # 处理下载的内容
                    for item_id, chapter_data in batch_data.items():
                        content = chapter_data.get("content", "")
                        title = chapter_data.get("title", f"第{start_idx + item_ids_batch.index(item_id) + 1}章")
                        
                        if content:
                            processed_content = self.process_content(content, title)
                            all_chapters[item_id] = {
                                "title": title,
                                "content": processed_content,
                                "index": start_idx + item_ids_batch.index(item_id)
                            }
                    
                    print(f"第 {batch_num + 1} 批下载完成，成功：{len(batch_data)} 章")
                else:
                    print(f"第 {batch_num + 1} 批下载失败")
                
                # 批次间休息
                if batch_num < total_batches - 1:
                    print("等待 3 秒后继续下一批...")
                    time.sleep(3)

            # 按顺序写入文件
            print("\n正在保存文件...")
            
            # 按索引排序
            sorted_chapters = sorted(all_chapters.values(), key=lambda x: x["index"])
            
            # 检查重复章节内容
            processed_contents = set()
            with open(output_file, 'a', encoding='utf-8') as f:
                for chapter in sorted_chapters:
                    # 检查内容是否重复
                    content_hash = hash(chapter["content"])
                    if content_hash in processed_contents:
                        print(f"跳过重复章节：{chapter['title']}")
                        continue

                    processed_contents.add(content_hash)
                    f.write(f"\n{chapter['title']}\n\n")
                    f.write(chapter["content"] + "\n\n")

            success_count = len(processed_contents)
            print(f"\n下载完成！成功：{success_count}章，失败：{len(item_ids) - success_count}章")
            print(f"文件保存在：{output_file}")

            return True

        except Exception as e:
            print(f"\n错误：{str(e)}")
            print(f"下载失败: {str(e)}")
            return False

def main():
    print("=" * 50)
    print("番茄小说下载器")
    print("=" * 50)
    
    # 手动输入 book_id
    while True:
        try:
            book_id = input("\n请输入小说ID (从番茄小说URL中获取): ").strip()
            if book_id:
                break
            else:
                print("❌ 小说ID不能为空，请重新输入")
        except KeyboardInterrupt:
            print("\n\n👋 已取消下载")
            sys.exit(0)
    
    # 手动输入保存路径
    while True:
        try:
            save_path_input = input("请输入保存路径 (默认: novel_output): ").strip()
            if not save_path_input:
                save_path = "novel_output"
                break
            save_path = save_path_input
            break
        except KeyboardInterrupt:
            print("\n\n👋 已取消下载")
            sys.exit(0)

    print(f"\n📚 开始下载小说")
    print(f"🔢 小说ID: {book_id}")
    print(f"💾 保存路径: {save_path}")
    print(f"📦 每批下载: 300章")
    print("-" * 50)

    # 确认开始下载
    while True:
        try:
            confirm = input("\n确认开始下载? (y/n): ").strip().lower()
            if confirm in ['y', 'yes', '是', '确认']:
                break
            elif confirm in ['n', 'no', '否', '取消']:
                print("👋 已取消下载")
                sys.exit(0)
            else:
                print("❌ 请输入 y 或 n")
        except KeyboardInterrupt:
            print("\n\n👋 已取消下载")
            sys.exit(0)

    try:
        downloader = NovelDownloader()
        success = downloader.download_novel(book_id, save_path)

        if success:
            print("\n✅ 下载完成！")
            # 列出下载的文件
            print("\n📁 下载的文件列表:")
            for file in os.listdir(save_path):
                file_path = os.path.join(save_path, file)
                file_size = os.path.getsize(file_path) / 1024  # KB
                print(f"📄 {file} ({file_size:.2f} KB)")
        else:
            print("\n❌ 下载或处理失败，请检查错误信息")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 下载被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
