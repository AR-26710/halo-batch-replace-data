from __future__ import annotations

import base64
import json

from modules.domain.entities.extension import Extension, ExtensionItem
from modules.domain.entities.extension_data import ExtensionData, Metadata


class Base64Decoder:
    def decode(self, items: list[ExtensionItem]) -> list[Extension]:
        return [self._decode_item(item) for item in items]

    def _decode_item(self, item: ExtensionItem) -> Extension:
        decoded_data = self._decode_base64(item.data)
        return Extension(
            name=item.name,
            version=item.version,
            data=decoded_data,
            raw_data=item.data
        )

    def _decode_base64(self, base64_string: str) -> ExtensionData:
        decoded_bytes = base64.b64decode(base64_string)
        json_string = decoded_bytes.decode('utf-8')
        parsed = json.loads(json_string)
        return self._dict_to_extension_data(parsed)

    def _dict_to_extension_data(self, data: dict) -> ExtensionData:
        metadata = None
        if 'metadata' in data and data['metadata']:
            m = data['metadata']
            metadata = Metadata(
                name=m.get('name'),
                annotations=m.get('annotations'),
                labels=m.get('labels'),
                resource_version=m.get('resourceVersion'),
                creation_timestamp=m.get('creationTimestamp'),
                version=m.get('version')
            )

        return ExtensionData(
            api_version=data.get('apiVersion'),
            kind=data.get('kind'),
            metadata=metadata,
            spec=data.get('spec'),
            data=data.get('data')
        )


base64_decoder = Base64Decoder()
