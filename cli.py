import argparse
import logging

from core import DataProcessor


def setup_logging():
    """配置日志系统

    该函数用于配置Python的日志系统，设置日志格式为`[日志级别] 日志信息`，
    日志级别为INFO，并将日志输出到控制台。
    """
    logging.basicConfig(
        format='[%(levelname)s] %(message)s',
        level=logging.INFO,
        handlers=[logging.StreamHandler()]
    )


def main():
    """命令行入口函数

    该函数是命令行工具的入口函数，负责解析命令行参数并调用相应的处理逻辑。
    主要功能包括：
    - 配置日志系统
    - 解析命令行参数
    - 根据参数调用DataProcessor类中的方法处理文件
    - 捕获并记录处理过程中的异常
    """
    setup_logging()

    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(
        description='Base64编码JSON文件处理器 - 命令行版',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # 添加命令行参数
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
    parser.add_argument(
        '--reencode',
        help='重新加密解码副本文件路径'
    )

    # 解析命令行参数
    args = parser.parse_args()

    try:
        # 根据是否提供了reencode参数，选择不同的处理逻辑
        if args.reencode:
            logging.info(f"开始重新加密文件: {args.reencode}")
            output_path = DataProcessor.reencode_file(
                args.reencode,
                args.output
            )
            logging.info(f"重新加密完成!")
            logging.info(f"输出文件: {output_path}")
        else:
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
        # 捕获并记录处理过程中的异常
        logging.error(f"处理失败: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
