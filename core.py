import base64
import json
import logging
import os
import re
from typing import List, Dict


class DataProcessor:
    """数据处理核心类"""

    @staticmethod
    def process_file(input_path: str, output_path: str, search: str = "", replace: str = "") -> str:
        """处理文件主方法
        返回: 解码文件的路径
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                original_data = json.load(f)

            decoded_path = DataProcessor.save_decoded_copy(original_data, output_path)
            processed_data = DataProcessor.replace_content(original_data, search, replace)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=2)

            return decoded_path

        except Exception as e:
            logging.error(f"处理失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def save_decoded_copy(data: List[Dict], output_path: str) -> str:
        """保存解码副本
        返回: 解码文件的路径
        """
        base_path, ext = os.path.splitext(output_path)
        decoded_path = f"{base_path}-original-decoded.json"

        decoded_data = []
        for item in data:
            decoded_item = DataProcessor.decode_item(item)
            decoded_data.append(decoded_item)

        with open(decoded_path, 'w', encoding='utf-8') as f:
            json.dump(decoded_data, f, ensure_ascii=False, indent=2)
        logging.info(f"原始解码副本已保存: {decoded_path}")
        return decoded_path

    @staticmethod
    def decode_item(item: Dict) -> Dict:
        """解码单个条目"""
        if "data" not in item:
            return item

        try:
            decoded = base64.b64decode(item["data"]).decode('utf-8')
            return {**item, "data": decoded}
        except Exception as e:
            item_id = item.get("id", "未知")
            logging.warning(f"条目 {item_id} 解码失败 - {str(e)}")
            return item

    @staticmethod
    def replace_content(data: List[Dict], search: str, replace: str) -> List[Dict]:
        """执行内容替换"""
        try:
            pattern = re.compile(search)
        except re.error as e:
            raise ValueError(f"无效的正则表达式: {str(e)}")

        processed = []
        for item in data:
            processed.append(DataProcessor.process_item(item, pattern, replace))
        return processed

    @staticmethod
    def process_item(item: Dict, pattern: re.Pattern, replace: str) -> Dict:
        """处理单个条目"""
        if "data" not in item:
            return item

        try:
            decoded = base64.b64decode(item["data"]).decode('utf-8')
            modified = pattern.sub(replace, decoded)
            return {**item, "data": base64.b64encode(modified.encode()).decode()}
        except Exception as e:
            item_id = item.get("id", "未知")
            logging.warning(f"条目 {item_id} 处理失败 - {str(e)}")
            return item
