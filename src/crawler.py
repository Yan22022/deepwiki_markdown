import os
import random
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from url_utils import UrlUtils
from file_utils import FileUtils
from flowchart import FlowchartProcessor
from constants import USER_AGENTS


class DeepWikiCrawler:
    """DeepWiki网站爬虫"""
    
    def __init__(self, base_url, max_depth=2, output_dir="output", timeout=10, delay=1.0):
        """
        初始化爬虫
        
        :param base_url: 基础URL
        :param max_depth: 最大爬取深度
        :param output_dir: 输出目录
        :param timeout: 请求超时时间(秒)
        :param delay: 请求间隔时间(秒)
        """
        self.base_url = base_url
        self.max_depth = max_depth
        self.output_dir = output_dir
        self.timeout = timeout
        self.delay = delay
        self.visited_urls = set()
        self.url_utils = UrlUtils(base_url)
        self.file_utils = FileUtils()
        self.flowchart_processor = FlowchartProcessor()

    def crawl(self, url=None, current_depth=0):
        """
        开始爬取
        
        :param url: 当前URL (None表示使用base_url)
        :param current_depth: 当前深度
        """
        if url is None:
            url = self.base_url
        
        if current_depth > self.max_depth or url in self.visited_urls:
            return
        
        self.visited_urls.add(url)
        print(f"Crawling: {url} (Depth: {current_depth})")
        
        try:
            html_content = self.fetch_url(url)
            if not html_content:
                return
            
            # 处理流程图并转换为Markdown
            markdown_content = self.convert_to_markdown(html_content, url)
            
            # 保存Markdown文件
            filename = self.url_utils.url_to_filename(url)
            output_path = os.path.join(self.output_dir, filename)
            self.file_utils.save_markdown(markdown_content, output_path)
            
            # 爬取内部链接
            if current_depth < self.max_depth:
                internal_links = self.extract_internal_links(html_content)
                for link in internal_links:
                    time.sleep(self.delay)  # 礼貌爬取
                    self.crawl(link, current_depth + 1)
                    
        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")

    def fetch_url(self, url):
        """获取URL内容"""
        try:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            response = requests.get(
                url, 
                headers=headers, 
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {str(e)}")
            return None

    def extract_internal_links(self, html_content):
        """从HTML内容中提取内部链接"""
        soup = BeautifulSoup(html_content, "html.parser")
        links = set()
        
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith("#"):
                continue
                
            if self.url_utils.is_internal_link(href):
                normalized_url = self.url_utils.normalize_url(href)
                links.add(normalized_url)
                
        return links

    def convert_to_markdown(self, html_content, url):
        """将HTML转换为Markdown"""
        # 处理流程图
        html_content = self.flowchart_processor.replace_flowcharts_with_mermaid(html_content)
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_content, "html.parser")
        
        # 提取标题
        title = soup.title.string if soup.title else urlparse(url).path
        
        # 构建Markdown内容
        markdown = f"# {title}\n\n"
        markdown += f"**URL**: [{url}]({url})\n\n"
        
        # 添加主要内容
        for element in soup.body.find_all(recursive=True):
            if element.name == "h1":
                markdown += f"\n# {element.get_text()}\n\n"
            elif element.name == "h2":
                markdown += f"\n## {element.get_text()}\n\n"
            elif element.name == "p":
                markdown += f"{element.get_text()}\n\n"
            elif element.name == "a":
                href = element.get("href", "")
                if href.startswith("http"):
                    markdown += f"[{element.get_text()}]({href}) "
                else:
                    markdown += f"[{element.get_text()}]({urljoin(url, href)}) "
            elif element.name == "img":
                src = element.get("src", "")
                alt = element.get("alt", "")
                if src.startswith("http"):
                    markdown += f"![{alt}]({src})\n\n"
                else:
                    markdown += f"![{alt}]({urljoin(url, src)})\n\n"
        
        return markdown