from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from modules.domain.entities.extension import Extension
from modules.domain.value_objects.search_query import SearchQuery
from modules.domain.value_objects.pagination import Pagination


@dataclass
class SearchResult:
    items: list[Extension]
    total: int
    pagination: Pagination


class IExtensionRepository(ABC):
    @abstractmethod
    def find_all(self) -> list[Extension]:
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Extension]:
        pass

    @abstractmethod
    def find_by_query(self, query: SearchQuery, pagination: Pagination) -> SearchResult:
        pass

    @abstractmethod
    def count(self, query: Optional[SearchQuery] = None) -> int:
        pass

    @abstractmethod
    def save(self, extensions: list[Extension]) -> None:
        pass

    @abstractmethod
    def delete(self, name: str) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def has_changes(self) -> bool:
        pass

    @abstractmethod
    def mark_as_saved(self) -> None:
        pass
