from urllib.parse import urljoin, urlparse
import re


class UrlUtils:
    """URL处理工具类"""
    
    def __init__(self, base_url):
        self.base_url = base_url

    def is_internal_link(self, url):
        """判断是否为内部链接且符合qemu/qemu域"""
        get_path_with_slash = self.get_path_with_slash(url)
        if url.startswith("/"):
            # 检查路径是否以/qemu/qemu开头
            return url.startswith(get_path_with_slash)

        parsed_url = urlparse(url)
        parsed_base = urlparse(self.base_url)

        # 检查域名是否匹配且路径以/qemu/qemu开头
        return parsed_url.netloc == parsed_base.netloc and parsed_url.path.startswith(
            get_path_with_slash
        )

    def normalize_url(self, url):
        """标准化URL"""
        if url.startswith("/"):
            # 确保不以//开头
            if url.startswith("//"):
                url = url[1:]
            return urljoin(self.base_url, url)
        return url
    
    def get_base_url(self, url):
        """获取URL的base url（协议+域名）"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
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
    
    @staticmethod
    def get_path_with_slash(url):
        """获取URL的路径部分，确保以/开头和/结尾"""
        parsed = urlparse(url)
        path = parsed.path
        if not path.startswith("/"):
            path = "/" + path
        if not path.endswith("/"):
            path += "/"
        return path
