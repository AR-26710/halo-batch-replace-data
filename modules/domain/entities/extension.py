from __future__ import annotations

from dataclasses import dataclass

from modules.domain.entities.extension_data import ExtensionData


@dataclass
class ExtensionItem:
    name: str
    data: str
    version: int


@dataclass
class Extension:
    name: str
    version: int
    data: ExtensionData
    raw_data: str

    def update_data(self, new_data: ExtensionData) -> 'Extension':
        return Extension(self.name, self.version, new_data, self.raw_data)

    def update_all(self, name: str, version: int, new_data: ExtensionData) -> 'Extension':
        return Extension(name, version, new_data, self.raw_data)

    def get_kind(self) -> str:
        return self.data.kind or 'Unknown'
