from __future__ import annotations

import json

from modules.domain.entities.extension import ExtensionItem
from modules.domain.repositories.i_storage_repository import IStorageRepository


class FileFormatError(Exception):
    def __init__(self, message: str, code: str = 'UNKNOWN'):
        super().__init__(message)
        self.code = code


class FileStorageRepository(IStorageRepository):
    def load(self, filepath: str) -> list[ExtensionItem]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            raise FileFormatError(f'读取文件失败: {filepath}', 'READ_ERROR') from e

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise FileFormatError('无效的JSON格式', 'INVALID_JSON') from e

        if not isinstance(data, list):
            raise FileFormatError('无效的文件格式: 期望数组', 'NOT_ARRAY')

        if len(data) == 0:
            raise FileFormatError('文件不包含扩展数据', 'EMPTY_ARRAY')

        for i, item in enumerate(data):
            if not self._is_valid_extension_item(item):
                raise FileFormatError(
                    f'索引 {i} 处的扩展项无效: 缺少必需字段 (name, version, data)',
                    'INVALID_ITEM'
                )

        return [ExtensionItem(name=item['name'], data=item['data'], version=item['version']) for item in data]

    def save(self, data: list[ExtensionItem], filepath: str) -> None:
        items = [{'name': item.name, 'data': item.data, 'version': item.version} for item in data]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

    def _is_valid_extension_item(self, item: object) -> bool:
        if not isinstance(item, dict):
            return False
        if not isinstance(item.get('name'), str) or not item['name'].strip():
            return False
        if not isinstance(item.get('version'), int):
            return False
        if not isinstance(item.get('data'), str) or not item['data'].strip():
            return False
        return True
