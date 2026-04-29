from __future__ import annotations

import argparse
import logging

from di.container import configure_container, get_use_cases
from modules.application.use_cases.batch_replace_use_case import BatchReplaceInput
from modules.application.use_cases.export_extensions_use_case import ExportExtensionsInput
from modules.application.use_cases.load_extensions_use_case import LoadExtensionsInput
from modules.core.logging.logger import setup_logging
from modules.infrastructure.types.replace_types import ReplaceRule, ReplaceScope


def run_cli():
    setup_logging()

    parser = argparse.ArgumentParser(
        description='Base64编码JSON文件处理器 - 命令行版',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('-i', '--input', required=True, help='输入JSON文件路径')
    parser.add_argument('-o', '--output', required=True, help='输出JSON文件路径')
    parser.add_argument('-s', '--search', default='', help='搜索内容(正则表达式)，默认为空字符串')
    parser.add_argument('-r', '--replace', default='', help='替换内容')
    parser.add_argument('--reencode', help='重新加密解码副本文件路径')

    args = parser.parse_args()

    container = configure_container()
    use_cases = get_use_cases(container)

    try:
        if args.reencode:
            logging.info(f"开始重新加密文件: {args.reencode}")
            load_result = use_cases['load'].execute(LoadExtensionsInput(filepath=args.reencode))
            if not load_result.success:
                logging.error(f"加载文件失败: {load_result.error}")
                return

            export_result = use_cases['export'].execute(ExportExtensionsInput(filepath=args.output))
            if export_result.success:
                logging.info(f"重新加密完成!")
                logging.info(f"输出文件: {args.output}")
            else:
                logging.error(f"导出失败: {export_result.error}")
        else:
            logging.info(f"开始处理文件: {args.input}")
            load_result = use_cases['load'].execute(LoadExtensionsInput(filepath=args.input))
            if not load_result.success:
                logging.error(f"加载文件失败: {load_result.error}")
                return

            if args.search:
                logging.info(f"执行替换: 搜索 '{args.search}', 替换为 '{args.replace}'")
                replace_result = use_cases['batch_replace'].execute(BatchReplaceInput(
                    rules=[ReplaceRule(search=args.search, replace=args.replace, is_regex=True)],
                    scope=ReplaceScope()
                ))
                if not replace_result.success:
                    logging.error(f"替换失败: {replace_result.error}")
                    return
                logging.info(f"替换完成, 更新了 {replace_result.updated_count} 条记录")

            export_result = use_cases['export'].execute(ExportExtensionsInput(filepath=args.output))
            if export_result.success:
                logging.info(f"处理完成!")
                logging.info(f"输出文件: {args.output}")
            else:
                logging.error(f"导出失败: {export_result.error}")
    except Exception as e:
        logging.error(f"处理失败: {str(e)}", exc_info=True)
        raise
