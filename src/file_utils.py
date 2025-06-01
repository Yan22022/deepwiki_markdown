import os
import re
import time
from pathlib import Path


class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def ensure_directory_exists(filepath):
        """确保文件所在目录存在"""
        dirname = os.path.dirname(filepath)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)

    @staticmethod
    def save_markdown(content, filepath):
        """保存Markdown内容到文件"""
        FileUtils.ensure_directory_exists(filepath)
        
        # 确保文件路径安全
        filepath = FileUtils.sanitize_filepath(filepath)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Saved: {filepath}")

    @staticmethod
    def sanitize_filepath(filepath):
        """清理文件路径中的非法字符"""
        # 替换Windows不支持的字符
        filepath = re.sub(r'[\\/:*?"<>|]', "-", filepath)
        # 移除连续的点
        filepath = filepath.replace("..", ".")
        # 移除开头和结尾的点和空格
        filepath = filepath.strip(". ")
        return filepath

    @staticmethod
    def read_file_if_exists(filepath):
        """如果文件存在则读取内容"""
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        return None

    @staticmethod
    def get_timestamp_filename(prefix="", suffix=".md"):
        """获取带时间戳的文件名"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        return f"{prefix}{timestamp}{suffix}"