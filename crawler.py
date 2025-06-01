import requests
from bs4 import BeautifulSoup
import html2text
import html
import os
from datetime import datetime
import time
import random
import re
from urllib.parse import urljoin, urlparse
import json


class DeepWikiCrawler:
    def __init__(self, base_url, output_dir="docs"):
        self.base_url = base_url
        self.output_dir = output_dir
        self.visited_urls = set()
        self.internal_links = set()
        self.url_to_file_mapping = {}

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 初始化HTML到Markdown转换器
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.body_width = 0
        self.h2t.inline_links = True
        self.h2t.bypass_tables = True
        self.h2t.ignore_emphasis = True
        self.h2t.protect_links = True

        # 流程图相关的正则表达式
        self.flowchart_patterns = [
            # 基本的流程图容器
            r'(?s)<div[^>]*class="[^"]*flowchart[^"]*"[^>]*>(.*?)</div>',
            r'(?s)<pre[^>]*class="[^"]*mermaid[^"]*"[^>]*>(.*?)</pre>',
            r'(?s)<div[^>]*data-type="flowchart"[^>]*>(.*?)</div>',
            # 常见的Mermaid图表容器
            r'(?s)<div[^>]*class="[^"]*mermaid[^"]*"[^>]*>(.*?)</div>',
            r'(?s)<code[^>]*class="[^"]*mermaid[^"]*"[^>]*>(.*?)</code>',
            # 其他可能的流程图容器
            r'(?s)<div[^>]*class="[^"]*diagram[^"]*"[^>]*>(.*?)</div>',
            r'(?s)<pre[^>]*class="[^"]*diagram[^"]*"[^>]*>(.*?)</pre>',
            # 带有data-属性的容器
            r'(?s)<div[^>]*data-diagram-type="[^"]*"[^>]*>(.*?)</div>',
            r'(?s)<div[^>]*data-mermaid="[^"]*"[^>]*>(.*?)</div>',
            # Markdown风格的代码块
            r"```mermaid\s*(.*?)\s*```",
            r"```flowchart\s*(.*?)\s*```",
        ]

    def get_user_agent(self):
        """返回一个随机的用户代理字符串"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        ]
        return random.choice(user_agents)

    def is_internal_link(self, url):
        """判断是否为内部链接且符合qemu/qemu域"""
        if url.startswith("/"):
            # 检查路径是否以/qemu/qemu开头
            return url.startswith("/qemu/qemu")

        parsed_url = urlparse(url)
        parsed_base = urlparse(self.base_url)

        # 检查域名是否匹配且路径以/qemu/qemu开头
        return parsed_url.netloc == parsed_base.netloc and parsed_url.path.startswith(
            "/qemu/qemu"
        )

    def normalize_url(self, url):
        """标准化URL"""
        if url.startswith("/"):
            # 确保不以//开头
            if url.startswith("//"):
                url = url[1:]
            return urljoin(self.base_url, url)
        return url

    def url_to_filename(self, url):
        """将URL转换为文件名"""
        # 移除域名部分
        parsed = urlparse(url)
        path = parsed.path.strip("/")

        if not path:
            path = "index"
        else:
            # 替换不合法的文件名字符
            path = re.sub(r'[\\/:*?"<>|]', "-", path)

        return f"{path}.md"

    def fetch_page(self, url):
        """获取页面内容"""
        headers = {
            "User-Agent": self.get_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page {url}: {e}")
            return None

    def extract_links(self, html_content, current_url):
        """提取页面中的链接"""
        soup = BeautifulSoup(html_content, "html.parser")
        links = set()

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if self.is_internal_link(href):
                full_url = self.normalize_url(href)
                if full_url not in self.visited_urls:
                    links.add(full_url)
                    self.internal_links.add(full_url)

        return links

    def update_markdown_links(self, content, current_url):
        """更新Markdown文件中的内部链接"""

        def replace_link(match):
            link_url = match.group(2)
            if self.is_internal_link(link_url):
                full_url = self.normalize_url(link_url)
                if full_url in self.url_to_file_mapping:
                    return f"[{match.group(1)}]({self.url_to_file_mapping[full_url]})"
            return match.group(0)

        # 匹配Markdown链接格式 [text](url)
        pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        return re.sub(pattern, replace_link, content)

    def extract_flowcharts(self, html_content):
        """从HTML内容中提取流程图"""
        flowcharts = []

        # 使用正则表达式模式查找流程图
        for pattern in self.flowchart_patterns:
            matches = re.finditer(pattern, html_content)
            for match in matches:
                content = match.group(1).strip()

                # 确定流程图类型
                if "mermaid" in match.group(0).lower():
                    chart_type = "mermaid"
                else:
                    chart_type = "flowchart"

                flowcharts.append({"type": chart_type, "content": content})

        # 使用BeautifulSoup查找更多可能的流程图
        soup = BeautifulSoup(html_content, "html.parser")

        # 查找div元素，class包含flowchart
        for div in soup.find_all("div", class_=re.compile("flowchart")):
            flowcharts.append({"type": "flowchart", "content": div.get_text().strip()})

        # 查找pre元素，class包含mermaid
        for pre in soup.find_all("pre", class_=re.compile("mermaid")):
            flowcharts.append({"type": "mermaid", "content": pre.get_text().strip()})

        # 查找具有data-type="flowchart"属性的元素
        for elem in soup.find_all(attrs={"data-type": "flowchart"}):
            flowcharts.append({"type": "flowchart", "content": elem.get_text().strip()})

        return flowcharts

    def clean_flowchart_content(self, content):
        """清理和标准化流程图内容"""
        # 移除HTML实体
        content = html.unescape(content)

        # 移除多余的空白字符
        content = re.sub(r"\s+", " ", content).strip()

        # 如果内容是JSON格式，尝试提取实际的图表内容
        if content.startswith("{") and content.endswith("}"):
            try:
                data = json.loads(content)
                if "content" in data:
                    content = data["content"]
                elif "diagram" in data:
                    content = data["diagram"]
            except json.JSONDecodeError:
                pass

        return content

    def convert_flowcharts_to_markdown(self, flowcharts):
        """将流程图转换为Markdown格式"""
        result = []
        for fc in flowcharts:
            # 清理内容
            content = self.clean_flowchart_content(fc["content"])

            if not content:  # 跳过空内容
                continue

            # 移除可能的HTML标签
            content = re.sub(r"<[^>]+>", "", content)

            # 处理转义字符
            content = html.unescape(content)
            content = content.replace("\\u003cbr\\u003e", ">")  # 替换HTML转义的换行符
            content = content.replace("\\u003e", ">")  # 替换HTML转义的换行符
            content = content.replace('\\"', '"')  # 移除转义的引号
            content = content.replace("\\n", "\n")
            # 标准化流程图声明
            if fc["type"] == "mermaid":
                # 确保只有一个图表类型声明
                if content.startswith("graph"):
                    content = content.replace("graph", "flowchart", 1)
                elif not any(
                    content.startswith(prefix)
                    for prefix in [
                        "flowchart ",
                        "graph ",
                        "sequenceDiagram",
                        "classDiagram",
                        "stateDiagram",
                    ]
                ):
                    content = f"{content}"
            else:
                # 对于非Mermaid流程图，转换为标准Mermaid语法
                if not content.startswith("flowchart"):
                    content = f"{content}"

            # 修复子图语法
            content = re.sub(r'subgraph\s+"([^"]+)"', r'subgraph \1["\1"]', content)

            # 添加Mermaid标记
            result.append(f"```mermaid\n{content}\n```")

        return "\n\n".join(result) if result else ""

    def save_to_markdown(self, content, url):
        """保存内容到Markdown文件"""
        filename = self.url_to_filename(url)
        filepath = os.path.join(self.output_dir, filename)
        self.url_to_file_mapping[url] = filename

        # 添加元数据
        metadata = f"""---
source: {url}
crawled_at: {datetime.now().isoformat()}
---

"""

        # 合并内容和元数据
        content_with_metadata = metadata + content

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content_with_metadata)
            print(f"Saved {url} to {filepath}")
            return filename
        except IOError as e:
            print(f"Error saving file {filepath}: {e}")
            return None

    def crawl(self, start_url):
        """开始爬取页面"""
        queue = [start_url]
        self.visited_urls.add(start_url)

        while queue:
            current_url = queue.pop(0)
            print(f"Crawling: {current_url}")

            # 获取页面内容
            html_content = self.fetch_page(current_url)
            if not html_content:
                continue

            # 提取新链接
            new_links = self.extract_links(html_content, current_url)

            # 提取流程图并转换为Markdown
            flowcharts = self.extract_flowcharts(html_content)
            flowchart_md = self.convert_flowcharts_to_markdown(flowcharts)

            # 转换为Markdown
            markdown_content = self.h2t.handle(html_content)

            # 如果有流程图，插入到原始位置
            if flowchart_md:
                # 使用BeautifulSoup定位流程图位置
                soup = BeautifulSoup(html_content, "html.parser")
                for fc in flowcharts:
                    # 查找流程图对应的元素
                    for elem in soup.find_all(
                        string=re.compile(re.escape(fc["content"]))
                    ):
                        parent = elem.parent
                        if parent:
                            # 在原始位置插入流程图标记
                            parent.insert_after(
                                f"<!--FLOWCHART_MARKER:{fc['content'][:20]}-->"
                            )

                # 重新生成带标记的HTML
                marked_html = str(soup)
                markdown_content = self.h2t.handle(marked_html)

                # 将流程图插入到标记位置
                for fc in flowcharts:
                    marker = f"<!--FLOWCHART_MARKER:{fc['content'][:20]}-->"
                    if marker in markdown_content:
                        fc_md = f"```mermaid\n{self.convert_flowcharts_to_markdown([fc])}\n```"
                        markdown_content = markdown_content.replace(marker, fc_md)

            # 保存文件
            self.save_to_markdown(markdown_content, current_url)

            # 添加新链接到队列
            for link in new_links:
                if link not in self.visited_urls:
                    queue.append(link)
                    self.visited_urls.add(link)

            # 避免请求过快
            time.sleep(1)

        # 更新所有文件中的内部链接
        self.update_all_files()

        # 保存URL到文件的映射关系
        self.save_url_mapping()

    def update_all_files(self):
        """更新所有文件中的内部链接"""
        for url, filename in self.url_to_file_mapping.items():
            filepath = os.path.join(self.output_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                print(f"Updating links in {filepath}...")
                # 更新Markdown链接
                updated_content = self.update_markdown_links(content, url)

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(updated_content)
            except IOError as e:
                print(f"Error updating links in {filepath}: {e}")

    def save_url_mapping(self):
        """保存URL到文件的映射关系"""
        mapping_file = os.path.join(self.output_dir, "url_mapping.json")
        try:
            with open(mapping_file, "w", encoding="utf-8") as f:
                json.dump(self.url_to_file_mapping, f, indent=2)
        except IOError as e:
            print(f"Error saving URL mapping: {e}")


def test_flowchart_extraction(url):
    """测试流程图提取功能"""
    print(f"测试从 {url} 提取流程图...")

    # 创建临时爬虫实例
    crawler = DeepWikiCrawler("", "test_output")

    # 获取页面内容
    html_content = crawler.fetch_page(url)
    if not html_content:
        print("无法获取页面内容")
        return

    # 提取流程图
    flowcharts = crawler.extract_flowcharts(html_content)
    print(f"找到 {len(flowcharts)} 个流程图")

    # 转换为Markdown
    markdown = crawler.convert_flowcharts_to_markdown(flowcharts)

    # 打印结果
    if flowcharts:
        print("\n提取的流程图:")
        for i, fc in enumerate(flowcharts):
            print(f"\n流程图 {i+1} (类型: {fc['type']}):")
            print(f"内容预览: {fc['content'][:100]}...")

        print("\n转换后的Markdown:")
        print(markdown)
    else:
        print("未找到流程图")


def main():
    """主函数"""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="DeepWiki爬虫工具")
    parser.add_argument(
        "--url",
        default="https://deepwiki.com/qemu/qemu",
        help="起始URL (默认: https://deepwiki.com/qemu/qemu)",
    )
    parser.add_argument("--output", default="docs", help="输出目录 (默认: docs)")
    parser.add_argument(
        "--test", action="store_true", help="测试模式：仅提取流程图而不爬取整个网站"
    )
    parser.add_argument(
        "--single-test",
        action="store_true",
        help="单链接测试模式：仅测试指定URL的流程图，不递归测试其包含的链接",
    )

    args = parser.parse_args()

    # 从URL中提取基础URL
    parsed_url = urlparse(args.url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    if args.test or args.single_test:
        # 测试模式
        test_flowchart_extraction(args.url)
    else:
        # 正常爬取模式
        print(f"开始爬取文档: {args.url}")
        print(f"输出目录: {args.output}")

        crawler = DeepWikiCrawler(base_url, args.output)
        crawler.crawl(args.url)

        print("\n爬取完成！")
        print(f"共爬取了 {len(crawler.visited_urls)} 个页面")
        print(f"文档已保存到 {args.output} 目录")


if __name__ == "__main__":
    main()
