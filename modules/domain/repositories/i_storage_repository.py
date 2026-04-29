from __future__ import annotations

from abc import ABC, abstractmethod

from modules.domain.entities.extension import ExtensionItem


class IStorageRepository(ABC):
    @abstractmethod
    def load(self, filepath: str) -> list[ExtensionItem]:
        pass

    @abstractmethod
    def save(self, data: list[ExtensionItem], filepath: str) -> None:
        pass
