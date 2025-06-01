from urllib.parse import urljoin, urlparse
import re


class UrlUtils:
    """URL处理工具类"""
    
    def __init__(self, base_url):
        self.base_url = base_url

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

    @staticmethod
    def url_to_filename(url):
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