# 常量定义

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
]

FLOWCHART_PATTERNS = [
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
    # 新增的通用匹配模式
    r'(?s)<svg[^>]*data-type="flowchart"[^>]*>(.*?)</svg>',
    r'(?s)<img[^>]*alt="[^"]*flowchart[^"]*"[^>]*>',
    r'(?s)<img[^>]*src="[^"]*flowchart[^"]*"[^>]*>',
    r'(?s)<object[^>]*data="[^"]*\.flowchart[^"]*"[^>]*>',
    # 更宽松的匹配模式
    r'(?s)<div[^>]*id="[^"]*flow[^"]*"[^>]*>(.*?)</div>',
    r'(?s)<div[^>]*id="[^"]*chart[^"]*"[^>]*>(.*?)</div>',
    r'(?s)<div[^>]*id="[^"]*diagram[^"]*"[^>]*>(.*?)</div>',
]