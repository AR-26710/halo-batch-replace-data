import base64
import json
import logging
import os
import re
from typing import List, Dict, Any, Pattern, Callable

class DataProcessor:
    """数据处理核心类，提供文件处理、解码、编码、内容替换等功能"""

    @staticmethod
    def _load_json(filepath: str) -> List[Dict[str, Any]]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            DataProcessor._log_and_raise(f"加载JSON失败: {filepath}", e)

    @staticmethod
    def _save_json(data: Any, filepath: str):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            DataProcessor._log_and_raise(f"保存JSON失败: {filepath}", e)

    @staticmethod
    def _log_and_raise(msg: str, error: Exception):
        logging.error(f"{msg}: {str(error)}", exc_info=True)
        raise

    @staticmethod
    def decode_file(input_path: str) -> List[Dict[str, Any]]:
        """解码文件内容但不保存"""
        return DataProcessor._load_json(input_path)

    @staticmethod
    def replace_content_in_file(input_path: str, search: str, replace: str) -> tuple:
        """替换文件内容但不保存"""
        original_data = DataProcessor._load_json(input_path)
        processed_data = DataProcessor.replace_content(original_data, search, replace)
        return original_data, processed_data

    @staticmethod
    def process_file(input_path: str, output_path: str, search: str = "", replace: str = "") -> str:
        """处理文件主方法"""
        original_data = DataProcessor._load_json(input_path)
        processed_data = DataProcessor.replace_content(original_data, search, replace)
        decoded_path = DataProcessor.save_decoded_copy(original_data, output_path)
        DataProcessor._save_json(processed_data, output_path)
        return decoded_path

    @staticmethod
    def save_decoded_copy(data: List[Dict[str, Any]], output_path: str) -> str:
        """保存解码后的数据副本到文件"""
        base_path, _ = os.path.splitext(output_path)
        decoded_path = f"{base_path}-original-decoded.json"
        decoded_data = [DataProcessor.decode_item(item) for item in data]
        DataProcessor._save_json(decoded_data, decoded_path)
        logging.info(f"原始解码副本已保存: {decoded_path}")
        return decoded_path

    @staticmethod
    def decode_item(item: Dict[str, Any]) -> Dict[str, Any]:
        """解码单个条目中的'data'字段"""
        if "data" not in item:
            return item
        try:
            decoded = base64.b64decode(item["data"]).decode('utf-8')
            return {**item, "data": decoded}
        except Exception as e:
            logging.warning(f"条目 {item.get('id', '未知')} 解码失败 - {str(e)}")
            return item

    @staticmethod
    def encode_item(item: Dict[str, Any]) -> Dict[str, Any]:
        """编码单个条目中的'data'字段"""
        if "data" not in item:
            return item
        try:
            encoded = base64.b64encode(item["data"].encode('utf-8')).decode()
            return {**item, "data": encoded}
        except Exception as e:
            logging.warning(f"条目 {item.get('id', '未知')} 编码失败 - {str(e)}")
            return item

    @staticmethod
    def reencode_file(input_path: str, output_path: str) -> str:
        """重新加密解码后的文件"""
        if not input_path.lower().endswith('.json'):
            raise ValueError("编码功能只支持JSON文件")
        decoded_data = DataProcessor._load_json(input_path)
        encoded_data = [DataProcessor.encode_item(item) for item in decoded_data]
        DataProcessor._save_json(encoded_data, output_path)
        return output_path

    @staticmethod
    def reencode_data(input_path: str) -> List[Dict[str, Any]]:
        """重新加密数据但不保存"""
        if not input_path.lower().endswith('.json'):
            raise ValueError("编码功能只支持JSON文件")
        decoded_data = DataProcessor._load_json(input_path)
        return [DataProcessor.encode_item(item) for item in decoded_data]

    @staticmethod
    def replace_content(data: List[Dict[str, Any]], search: str, replace: str) -> List[Dict[str, Any]]:
        """在数据列表中执行内容替换"""
        try:
            pattern = re.compile(search)
        except re.error as e:
            raise ValueError(f"无效的正则表达式: {str(e)}")
        return [DataProcessor.process_item(item, pattern, replace) for item in data]

    @staticmethod
    def process_item(item: Dict[str, Any], pattern: Pattern, replace: str) -> Dict[str, Any]:
        """处理单个条目，解码并替换'data'字段中的内容"""
        if "data" not in item:
            return item
        try:
            decoded = base64.b64decode(item["data"]).decode('utf-8')
            modified = pattern.sub(replace, decoded)
            return {**item, "data": base64.b64encode(modified.encode()).decode()}
        except Exception as e:
            logging.warning(f"条目 {item.get('id', '未知')} 处理失败 - {str(e)}")
            return item
