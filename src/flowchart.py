import re
from constants import FLOWCHART_PATTERNS


class FlowchartProcessor:
    """流程图处理工具类"""
    
    @staticmethod
    def extract_flowcharts(html_content):
        """从HTML内容中提取所有流程图"""
        flowcharts = []
        for pattern in FLOWCHART_PATTERNS:
            matches = re.findall(pattern, html_content)
            flowcharts.extend(matches)
        return flowcharts

    @staticmethod
    def convert_flowcharts_to_mermaid(flowcharts):
        """将流程图转换为Mermaid格式"""
        mermaid_diagrams = []
        for flowchart in flowcharts:
            # 清理内容
            content = flowchart.strip()
            content = re.sub(r'<[^>]+>', '', content)  # 移除HTML标签
            content = re.sub(r'\s+', ' ', content)  # 合并多余空格
            
            # 转换为Mermaid格式
            mermaid_diagram = f"```mermaid\n{content}\n```"
            mermaid_diagrams.append(mermaid_diagram)
        return mermaid_diagrams

    @staticmethod
    def replace_flowcharts_with_mermaid(html_content):
        """用Mermaid格式替换HTML中的流程图"""
        flowcharts = FlowchartProcessor.extract_flowcharts(html_content)
        mermaid_diagrams = FlowchartProcessor.convert_flowcharts_to_mermaid(flowcharts)
        
        for i, pattern in enumerate(FLOWCHART_PATTERNS):
            html_content = re.sub(
                pattern, 
                lambda m: mermaid_diagrams.pop(0) if mermaid_diagrams else m.group(0), 
                html_content
            )
        return html_content


def test_flowchart_extraction():
    """测试流程图提取功能"""
    test_html = """
    <div class="flowchart">
        graph TD;
            A-->B;
            A-->C;
            B-->D;
            C-->D;
    </div>
    <pre class="mermaid">
        pie
            title 测试图表
            "苹果" : 45
            "香蕉" : 30
            "橙子" : 25
    </pre>
    """
    
    processor = FlowchartProcessor()
    flowcharts = processor.extract_flowcharts(test_html)
    print("提取到的流程图:")
    for i, fc in enumerate(flowcharts, 1):
        print(f"{i}. {fc.strip()}")
    
    mermaid_diagrams = processor.convert_flowcharts_to_mermaid(flowcharts)
    print("\n转换后的Mermaid图表:")
    for i, md in enumerate(mermaid_diagrams, 1):
        print(f"{i}. {md}")
    
    replaced = processor.replace_flowcharts_with_mermaid(test_html)
    print("\n替换后的HTML:")
    print(replaced)


if __name__ == "__main__":
    test_flowchart_extraction()