from __future__ import annotations

import base64
import json

from modules.domain.entities.extension import Extension, ExtensionItem
from modules.domain.entities.extension_data import ExtensionData


class Base64Encoder:
    def encode(self, extensions: list[Extension]) -> list[ExtensionItem]:
        return [self._encode_extension(ext) for ext in extensions]

    def _encode_extension(self, extension: Extension) -> ExtensionItem:
        encoded_data = self._encode_base64(extension.data)
        return ExtensionItem(
            name=extension.name,
            version=extension.version,
            data=encoded_data
        )

    def _encode_base64(self, data: ExtensionData) -> str:
        data_dict = self._extension_data_to_dict(data)
        json_string = json.dumps(data_dict, ensure_ascii=False)
        return base64.b64encode(json_string.encode('utf-8')).decode()

    def _extension_data_to_dict(self, data: ExtensionData) -> dict:
        result = {}
        if data.api_version is not None:
            result['apiVersion'] = data.api_version
        if data.kind is not None:
            result['kind'] = data.kind
        if data.metadata is not None:
            m = data.metadata
            metadata = {}
            if m.name is not None:
                metadata['name'] = m.name
            if m.annotations is not None:
                metadata['annotations'] = m.annotations
            if m.labels is not None:
                metadata['labels'] = m.labels
            if m.resource_version is not None:
                metadata['resourceVersion'] = m.resource_version
            if m.creation_timestamp is not None:
                metadata['creationTimestamp'] = m.creation_timestamp
            if m.version is not None:
                metadata['version'] = m.version
            result['metadata'] = metadata
        if data.spec is not None:
            result['spec'] = data.spec
        if data.data is not None:
            result['data'] = data.data
        return result


base64_encoder = Base64Encoder()
