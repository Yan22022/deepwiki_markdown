import argparse
from crawler import DeepWikiCrawler

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="DeepWiki爬虫工具")
    parser.add_argument("url", help="要爬取的起始URL")
    parser.add_argument("-d", "--depth", type=int, default=2,
                        help="爬取深度 (默认: 2)")
    parser.add_argument("-o", "--output", default="output",
                        help="输出目录 (默认: 'output')")
    parser.add_argument("-t", "--timeout", type=int, default=10,
                        help="请求超时时间(秒) (默认: 10)")
    parser.add_argument("-s", "--sleep", type=float, default=1.0,
                        help="请求间隔时间(秒) (默认: 1.0)")
    parser.add_argument("--test-flowchart", action="store_true",
                        help="测试流程图提取功能")
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()
    
    if args.test_flowchart:
        from flowchart import test_flowchart_extraction
        test_flowchart_extraction()
        return
    
    crawler = DeepWikiCrawler(
        base_url=args.url,
        max_depth=args.depth,
        output_dir=args.output,
        timeout=args.timeout,
        delay=args.sleep
    )
    crawler.run()    


if __name__ == "__main__":
    main()