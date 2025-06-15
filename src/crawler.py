import os
import re
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
        self.url_to_file_mapping = {}

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
        
        # for deepwiki
        out = "_".join(UrlUtils.get_path_with_slash(self.base_url).split("/")).strip("_")
        if "deepwiki.com" in self.base_url:
            self.output_dir = os.path.join("wiki_info", out) 
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        self.visited_urls.add(url)
        print(f"Crawling: {url} (Depth: {current_depth})")
        
        try:
            html_content = self.fetch_url(url)
            if not html_content:
                return
            
            # 处理流程图并转换为Markdown
            markdown_content = self.convert_to_markdown(html_content, url)
            
            filename = self.url_utils.url_to_filename(url)
            output_path = os.path.join(self.output_dir, filename)
            self.url_to_file_mapping[url] = output_path
            #self.file_utils.save_markdown(markdown_content, output_path)
            
            # 爬取内部链接
            if current_depth < self.max_depth:
                internal_links = self.extract_internal_links(html_content)
                for link in internal_links:
                    time.sleep(self.delay)  # 礼貌爬取
                    self.crawl(link, current_depth + 1)
        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")

    def save_url_mapping(self):
        """保存URL到文件的映射关系"""
        mapping_file = os.path.join(self.output_dir, "url_mapping.json")
        import json
        try:
            with open(mapping_file, "w", encoding="utf-8") as f:
                json.dump(self.url_to_file_mapping, f, indent=2)
        except IOError as e:
            print(f"Error saving URL mapping: {e}")

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

        left_panel_class = (
            r"border-r-border hidden max-h-screen border-r border-dashed py-7 pr-4 transition-[border-radius] md:sticky md:left-0 md:top-20 md:block md:h-[calc(100vh-82px)] md:w-64 md:flex-shrink-0 md:overflow-y-auto lg:py-9 xl:w-72"
        )
        left_panel = soup.find("div", class_=left_panel_class)
        for a in left_panel.find_all("a", href=True):
            href = a["href"].strip()

            if not href or href.startswith("#"):
                continue
            name = UrlUtils.get_path_with_slash(self.base_url)
            if not href.startswith(name):
                continue
            
            href= urljoin(self.url_utils.get_base_url(self.base_url), href)
            # 处理相对链接
            normalized_url = self.url_utils.normalize_url(href)
            links.add(normalized_url)

        return links

    def convert_to_markdown(self, html_content, url):
        """将HTML内容转换为Markdown格式"""
        import html2text
        from datetime import datetime
       
        # 处理HTML内容，替换流程图占位符
        # 先转换HTML为Markdown
        h = html2text.HTML2Text()
        h.body_width = 0
        h.ignore_links = False
        h.ignore_images = False
        
        # 表格处理配置
        h.bypass_tables = False
        # h.single_line_break = True
        # h.ignore_emphasis = True  
        # h.protect_links = True
        h.mark_code = True
        # h.table_style = 'full'  # 完整表格样式
        # h.table_cell_separator = '|'  # 单元格分隔符
        # h.table_row_separator = '-'  # 行分隔符
        # h.table_add_trailing_newline = True  # 表格后添加换行
        
        # 转换为Markdown
        markdown_content = h.handle(html_content)

        markdown_content = re.split(r'Menu', markdown_content, maxsplit=1, flags=re.MULTILINE)[1]

        markdown_content = re.split(r'Auto-refresh not enabled yet', markdown_content, maxsplit=1, flags=re.MULTILINE)[0]

        # 添加元数据
        metadata = f"""---
source: {url}
crawled_at: {datetime.now().isoformat()}
---

"""
        content_with_metadata = metadata + markdown_content
        
        # 保存文件
        filename = self.url_utils.url_to_filename(url)
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content_with_metadata)
            print(f"Saved {url} to {filepath}")
            return filename
        except IOError as e:
            print(f"Error saving file {filepath}: {e}")
            return None

    def run(self):
        """开始爬取"""
        self.crawl()
        self.save_url_mapping()
        self.dump_flowcharts(self.base_url)
    
    def dump_flowcharts(self, url):
        html_content = self.fetch_url(url)
        """将所有提取的流程图保存到单独的文件"""
        with open(os.path.join(self.output_dir, "flowchart.md"), "w", encoding="utf-8") as f:
            #r"```mermaid\s*(.*?)\s*```",
            for chart in self.flowchart_processor.extract_flowcharts(html_content):
                f.write(f"```mermaid\n" + chart + "\n```")
                f.write("\n\n")
         # mermaid_code_pattern = f'''<pre class="px-2 py-1.5 has-[code]:rounded-md has-[code]:!bg-[#e5e5e5] has-[div]:bg-transparent has-[div]:!p-0 has-[code]:text-stone-900 dark:has-[code]:!bg-[#242424] has-[code]:dark:text-white [&amp;_code]:block [&amp;_code]:border-none [&amp;_code]:bg-transparent [&amp;_code]:p-0"><!--$!--><template data-dgst="BAILOUT_TO_CLIENT_SIDE_RENDERING"></template><!--/$--></pre>'''
        # with open("flowchart.txt", "w", encoding="utf-8") as f:
        #     f.write(html_content)
        # 提取流程图并记录位置
        # flowcharts = self.flowchart_processor.extract_flowcharts(html_content)
        # flowchart_positions = []
        # processed_html = html_content
        # 记录每个流程图在HTML中的位置
        # for chart in flowcharts:
        #     pos = html_content.find(chart)
        #     if pos >= 0:
        #         flowchart_positions.append((pos, chart))
        # # 使用特殊文本标记替换流程图
        # for i, (pos, chart) in enumerate(flowchart_positions):
        #     # 使用独特的UUID作为占位符
        #     placeholder = f"\"@@@FLOWCHART_{i}_@@@\""
        #     processed_html = processed_html.replace(mermaid_code_pattern, placeholder, 1)
                # with open("flowchart_parsed.txt", "w", encoding="utf-8") as f:
        #     f.write(markdown_content)
        
        # # 将文本占位符替换回Mermaid流程图
        # for i, (pos, chart) in enumerate(flowchart_positions):
        #     placeholder = f"@@@FLOWCHART_{i}_@@@"
        #     mermaid_chart = f"\n```mermaid\n{chart}\n```\n"
        #     markdown_content = markdown_content.replace(placeholder, mermaid_chart, 1)
        