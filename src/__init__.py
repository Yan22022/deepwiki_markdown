"""
DeepWiki爬虫包

提供从DeepWiki网站爬取内容并转换为Markdown格式的功能

主要接口:
- DeepWikiCrawler: 主爬虫类
- FlowchartProcessor: 流程图处理工具
- run_cli: 运行命令行接口
"""

from .crawler import DeepWikiCrawler
from .flowchart import FlowchartProcessor
from .cli import main as run_cli

__all__ = ['DeepWikiCrawler', 'FlowchartProcessor', 'run_cli']