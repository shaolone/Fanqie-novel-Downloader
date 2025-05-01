# epub_generator.py
from ebooklib import epub
import os
import re
import logging
import requests
from bs4 import BeautifulSoup
import json
from typing import Optional
from config import CONFIG

logger = logging.getLogger(__name__)

class EpubGenerator:
    def __init__(self, book_info, chapters):
        self.book = epub.EpubBook()
        self.book_info = book_info
        self.chapters = chapters
        
        # 初始化书籍元数据
        self._init_metadata()
        # 创建样式表
        self._create_styles()
        # 构建书籍结构
        self._build_structure()

    def _init_metadata(self):
        """初始化元数据"""
        self.book.set_identifier(f"fanqie_{self.book_info['id']}")
        self.book.set_title(self.book_info['name'])
        self.book.set_language('zh-CN')
        self.book.add_author(self.book_info['author'])
        
        # 自动获取封面
        if 'id' in self.book_info:
            cover_url = self._get_cover_url(self.book_info['id'])
            if cover_url:
                self._add_cover_from_url(cover_url)
        
        # 添加出版社信息
        self.book.add_metadata('DC', 'publisher', '番茄小说下载器')

    def _get_cover_url(self, novel_id: str) -> Optional[str]:
        """从小说页面获取封面URL"""
        url = f'https://fanqienovel.com/page/{novel_id}'
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            script_tag = soup.find('script', type="application/ld+json")
            if script_tag:
                data = json.loads(script_tag.string)
                return data.get('image', [None])[0]
        except Exception as e:
            logger.error(f"获取封面URL失败: {str(e)}")
        return None

    def _add_cover_from_url(self, cover_url: str):
        """从URL添加封面"""
        try:
            response = requests.get(cover_url, timeout=10)
            response.raise_for_status()
            
            cover_item = epub.EpubItem(
                uid="cover_image",
                file_name="images/cover.jpg",
                media_type="image/jpeg",
                content=response.content
            )
            self.book.add_item(cover_item)
            
            # 创建封面页面
            cover_html = epub.EpubHtml(
                uid="cover",
                title="封面",
                file_name="cover.xhtml"
            )
            cover_html.content = (
                '<div class="cover">'
                f'<h1>{self.book_info["name"]}</h1>'
                f'<h2>{self.book_info["author"]}</h2>'
                '<img class="cover-img" src="images/cover.jpg" alt="封面"/>'
                '</div>'
            )
            self.book.add_item(cover_html)
            self.cover_page = cover_html
        except Exception as e:
            logger.error(f"封面下载失败: {str(e)}")

    def _create_styles(self):
        """创建CSS样式表"""
        self.style = '''
        @namespace epub "http://www.idpf.org/2007/ops";
        
        /* 基础排版 */
        body {
            font-family: "Microsoft YaHei", "思源宋体", SimSun, serif;
            line-height: 1.8;
            margin: 1em 2em;
            text-align: justify;
            hyphens: auto;
            -epub-hyphens: auto;
        }
        
        /* 段落样式 */
        p {
            text-indent: 2em;
            margin: 0.5em 0;
            word-wrap: break-word;
        }
        
        /* 标题样式 */
        h1 {
            font-size: 2.2rem;
            text-align: center;
            border-bottom: 2px solid #666;
            padding-bottom: 0.5em;
            margin: 2em 0 1em;
        }
        
        h2 {
            font-size: 1.8rem;
            text-align: center;
            margin: 1.5em 0 1em;
            color: #2c3e50;
        }
        
        /* 目录样式 */
        nav#toc ol {
            list-style-type: none;
            padding-left: 1em;
        }
        
        nav#toc a {
            color: #3498db;
            text-decoration: none;
            display: block;
            padding: 0.3em 0;
        }
        
        /* 封面样式 */
        div.cover {
            text-align: center;
            page-break-after: always;
        }
        
        img.cover-img {
            max-width: 60%;
            height: auto;
            margin: 2em auto;
        }
        '''

        # 创建样式表项目
        self.nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="styles/main.css",
            media_type="text/css",
            content=self.style
        )

    def _add_cover(self, image_path):
        """添加封面图片"""
        try:
            with open(image_path, 'rb') as f:
                cover_image = f.read()
            
            cover_item = epub.EpubItem(
                uid="cover_image",
                file_name="images/cover.jpg",
                media_type="image/jpeg",
                content=cover_image
            )
            self.book.add_item(cover_item)
            
            # 创建封面页面
            cover_html = epub.EpubHtml(
                uid="cover",
                title="封面",
                file_name="cover.xhtml"
            )
            cover_html.content = (
                '<div class="cover">'
                f'<h1>{self.book_info["name"]}</h1>'
                f'<h2>{self.book_info["author"]}</h2>'
                '<img class="cover-img" src="images/cover.jpg" alt="封面"/>'
                '</div>'
            )
            self.book.add_item(cover_html)
            self.cover_page = cover_html
        except Exception as e:
            logger.error(f"封面添加失败: {str(e)}")

    def _build_structure(self):
        """构建书籍结构"""
        # 添加简介章节
        self._add_introduction()
        
        # 添加正文章节
        self._add_chapters()
        
        # 定义目录结构
        self.book.toc = self._build_toc()
        
        # 添加导航文件
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())
        
        # 定义书脊顺序
        spine_items = ['nav']
        if hasattr(self, 'cover_page'):
            spine_items.insert(0, self.cover_page)
        spine_items.append(self.intro)
        spine_items.extend(self.epub_chapters)
        self.book.spine = spine_items
        
        # 添加样式表
        self.book.add_item(self.nav_css)

    def _add_introduction(self):
        """添加简介章节"""
        intro_content = f"""
        <h1>{self.book_info['name']}</h1>
        <h2>作者：{self.book_info['author']}</h2>
        <div class="description">
            <h3>作品简介</h3>
            <p>{self.book_info['description']}</p>
        </div>
        """
        self.intro = epub.EpubHtml(title='简介', file_name='intro.xhtml')
        self.intro.content = intro_content
        self.book.add_item(self.intro)

    def _add_chapters(self):
        """添加正文章节"""
        self.epub_chapters = []
        for idx, (chapter, content) in enumerate(self.chapters):
            # 清理内容格式
            cleaned_content = self._clean_content(content)
            
            # 创建章节
            chap = epub.EpubHtml(
                title=chapter['title'],
                file_name=f'chap_{idx+1}.xhtml'
            )
            chap.content = f"""
            <h2>{chapter['title']}</h2>
            {cleaned_content}
            """
            self.book.add_item(chap)
            self.epub_chapters.append(chap)

    def _clean_content(self, content):
        """清理内容格式"""
        # 移除多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        # 转换段落
        content = re.sub(r'\n', '</p><p>', content)
        # 添加缩进
        return f'<p>{content}</p>'

    def _build_toc(self):
        """构建目录结构"""
        toc_items = []
        if hasattr(self, 'cover_page'):
            toc_items.append(epub.Link('cover.xhtml', '封面', 'cover'))
        
        toc_items.append(epub.Link('intro.xhtml', '简介', 'intro'))
        
        # 添加章节
        chapter_links = []
        for chap in self.epub_chapters:
            chapter_links.append(epub.Link(chap.file_name, chap.title, f'chap_{chap.id}'))
        
        toc_items.extend(chapter_links)
        return toc_items

    def save(self, save_path):
        """保存EPUB文件"""
        try:
            safe_name = re.sub(r'[\\/*?:"<>|]', "", self.book_info['name'])
            safe_name = safe_name.strip()[:100]
            
            epub_path = os.path.join(save_path, f"{safe_name}.epub")
            os.makedirs(save_path, exist_ok=True)
            
            epub.write_epub(epub_path, self.book, {})
            
            if os.path.exists(epub_path) and os.path.getsize(epub_path) > 1024:
                return epub_path
            raise RuntimeError("生成的文件无效")
        except Exception as e:
            logger.error(f"EPUB生成失败: {str(e)}")
            raise
