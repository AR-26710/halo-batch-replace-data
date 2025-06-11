import base64
import json
import logging
import os
import re
from typing import List, Dict


class DataProcessor:
    """数据处理核心类，提供文件处理、解码、编码、内容替换等功能"""

    @staticmethod
    def decode_file(input_path: str) -> List[Dict]:
        """解码文件内容但不保存

        Args:
            input_path (str): 输入文件路径

        Returns:
            List[Dict]: 解码后的数据

        Raises:
            Exception: 如果处理过程中发生错误，记录日志并抛出异常
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                original_data = json.load(f)
            return original_data

        except Exception as e:
            logging.error(f"解码失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def replace_content_in_file(input_path: str, search: str, replace: str) -> tuple:
        """替换文件内容但不保存

        Args:
            input_path (str): 输入文件路径
            search (str): 要搜索的正则表达式
            replace (str): 替换的字符串

        Returns:
            tuple: (原始数据, 处理后的数据)

        Raises:
            Exception: 如果处理过程中发生错误，记录日志并抛出异常
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                original_data = json.load(f)

            processed_data = DataProcessor.replace_content(original_data, search, replace)
            return original_data, processed_data

        except Exception as e:
            logging.error(f"替换失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def process_file(input_path: str, output_path: str, search: str = "", replace: str = "") -> str:
        """处理文件主方法，读取输入文件，解码并替换内容后保存到输出文件

        Args:
            input_path (str): 输入文件路径
            output_path (str): 输出文件路径
            search (str, optional): 要搜索的正则表达式，默认为空字符串
            replace (str, optional): 替换的字符串，默认为空字符串

        Returns:
            str: 解码文件的路径

        Raises:
            Exception: 如果处理过程中发生错误，记录日志并抛出异常
        """
        original_data = DataProcessor.decode_file(input_path)
        processed_data = DataProcessor.replace_content(original_data, search, replace)
        decoded_path = DataProcessor.save_decoded_copy(original_data, output_path)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)

        return decoded_path

    @staticmethod
    def save_decoded_copy(data: List[Dict], output_path: str) -> str:
        """保存解码后的数据副本到文件

        Args:
            data (List[Dict]): 要解码的数据列表
            output_path (str): 输出文件路径

        Returns:
            str: 解码文件的路径
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
        """解码单个条目中的'data'字段

        Args:
            item (Dict): 包含'data'字段的字典

        Returns:
            Dict: 解码后的字典，如果解码失败则返回原字典
        """
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
    def encode_item(item: Dict) -> Dict:
        """编码单个条目中的'data'字段

        Args:
            item (Dict): 包含'data'字段的字典

        Returns:
            Dict: 编码后的字典，如果编码失败则返回原字典
        """
        if "data" not in item:
            return item

        try:
            encoded = base64.b64encode(item["data"].encode('utf-8')).decode()
            return {**item, "data": encoded}
        except Exception as e:
            item_id = item.get("id", "未知")
            logging.warning(f"条目 {item_id} 编码失败 - {str(e)}")
            return item

    @staticmethod
    def reencode_file(input_path: str, output_path: str) -> str:
        """重新加密解码后的文件

        Args:
            input_path (str): 输入文件路径
            output_path (str): 输出文件路径

        Returns:
            str: 输出文件路径

        Raises:
            Exception: 如果重新加密过程中发生错误，记录日志并抛出异常
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                decoded_data = json.load(f)

            encoded_data = []
            for item in decoded_data:
                encoded_data.append(DataProcessor.encode_item(item))

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(encoded_data, f, ensure_ascii=False, indent=2)

            return output_path

        except Exception as e:
            logging.error(f"重新加密失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def reencode_data(input_path: str) -> list:
        """重新加密数据但不保存

        Args:
            input_path (str): 输入文件路径

        Returns:
            list: 加密后的数据列表

        Raises:
            Exception: 如果重新加密过程中发生错误，记录日志并抛出异常
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                decoded_data = json.load(f)

            encoded_data = []
            for item in decoded_data:
                encoded_data.append(DataProcessor.encode_item(item))

            return encoded_data

        except Exception as e:
            logging.error(f"重新加密失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def replace_content(data: List[Dict], search: str, replace: str) -> List[Dict]:
        """在数据列表中执行内容替换

        Args:
            data (List[Dict]): 要处理的数据列表
            search (str): 要搜索的正则表达式
            replace (str): 替换的字符串

        Returns:
            List[Dict]: 替换后的数据列表

        Raises:
            ValueError: 如果正则表达式无效，抛出异常
        """
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
        """处理单个条目，解码并替换'data'字段中的内容

        Args:
            item (Dict): 要处理的字典
            pattern (re.Pattern): 正则表达式模式
            replace (str): 替换的字符串

        Returns:
            Dict: 处理后的字典，如果处理失败则返回原字典
        """
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
