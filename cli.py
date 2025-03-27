import argparse
import logging

from core import DataProcessor


def setup_logging():
    """配置日志系统"""
    logging.basicConfig(
        format='[%(levelname)s] %(message)s',
        level=logging.INFO,
        handlers=[logging.StreamHandler()]
    )


def main():
    """命令行入口函数"""
    setup_logging()

    parser = argparse.ArgumentParser(
        description='Base64编码JSON文件处理器 - 命令行版',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '-i', '--input',
        required=True,
        help='输入JSON文件路径'
    )
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='输出JSON文件路径'
    )
    parser.add_argument(
        '-s', '--search',
        default='',
        help='搜索内容(正则表达式)，默认为空字符串'
    )
    parser.add_argument(
        '-r', '--replace',
        default='',
        help='替换内容'
    )

    args = parser.parse_args()

    try:
        logging.info(f"开始处理文件: {args.input}")
        decoded_path = DataProcessor.process_file(
            args.input,
            args.output,
            args.search,
            args.replace
        )
        logging.info(f"处理完成!")
        logging.info(f"输出文件: {args.output}")
        logging.info(f"解码副本: {decoded_path}")
    except Exception as e:
        logging.error(f"处理失败: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
