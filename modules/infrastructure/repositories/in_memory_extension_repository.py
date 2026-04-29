from __future__ import annotations

from typing import Optional

from modules.domain.entities.extension import Extension
from modules.domain.repositories.i_extension_repository import IExtensionRepository, SearchResult
from modules.domain.value_objects.search_query import SearchQuery
from modules.domain.value_objects.pagination import Pagination
from modules.domain.services.extension_search_service import ExtensionSearchService


class InMemoryExtensionRepository(IExtensionRepository):
    def __init__(self):
        self._extensions: dict[str, Extension] = {}
        self._has_unsaved_changes = False
        self._search_service = ExtensionSearchService()

    def find_all(self) -> list[Extension]:
        return list(self._extensions.values())

    def find_by_name(self, name: str) -> Optional[Extension]:
        return self._extensions.get(name)

    def find_by_query(self, query: SearchQuery, pagination: Pagination) -> SearchResult:
        all_extensions = self.find_all()
        filtered = self._filter_by_query(all_extensions, query)

        offset = pagination.offset
        limit = pagination.page_size
        paginated = filtered[offset:offset + limit]
        new_pagination = pagination.with_total(len(filtered))

        return SearchResult(
            items=paginated,
            total=len(filtered),
            pagination=new_pagination
        )

    def count(self, query: Optional[SearchQuery] = None) -> int:
        all_extensions = self.find_all()
        if not query or query.is_empty():
            return len(all_extensions)
        return len(self._filter_by_query(all_extensions, query))

    def save(self, extensions: list[Extension]) -> None:
        for ext in extensions:
            existing = None
            for key, val in self._extensions.items():
                if key != ext.name and val.raw_data == ext.raw_data:
                    existing = key
                    break
            if existing:
                del self._extensions[existing]
            self._extensions[ext.name] = ext
        self._has_unsaved_changes = True

    def delete(self, name: str) -> None:
        if name in self._extensions:
            del self._extensions[name]
        self._has_unsaved_changes = True

    def clear(self) -> None:
        self._extensions.clear()
        self._has_unsaved_changes = False

    def has_changes(self) -> bool:
        return self._has_unsaved_changes

    def mark_as_saved(self) -> None:
        self._has_unsaved_changes = False

    def get_kinds(self) -> list[str]:
        kinds = set()
        for ext in self._extensions.values():
            kinds.add(ext.get_kind())
        return sorted(kinds)

    def _filter_by_query(self, extensions: list[Extension], query: SearchQuery) -> list[Extension]:
        filtered = extensions

        if query.has_keywords():
            filtered = [ext for ext in filtered if self._search_service.matches(ext, query)]

        kind_filter = query.get_filter_value('kind')
        if kind_filter:
            filtered = [ext for ext in filtered if ext.get_kind() == kind_filter]

        return filtered
