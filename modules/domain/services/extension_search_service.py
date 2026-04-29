from __future__ import annotations

from modules.domain.entities.extension import Extension
from modules.domain.value_objects.search_query import SearchQuery


class ExtensionSearchService:
    MAX_SEARCH_DEPTH = 5

    def matches(self, extension: Extension, query: SearchQuery) -> bool:
        if query.is_empty():
            return True
        if query.has_keywords():
            return all(
                self._matches_keyword(extension, kw.lower().strip())
                for kw in query.keywords
            )
        return True

    def _matches_keyword(self, extension: Extension, keyword: str) -> bool:
        if not keyword:
            return True
        return self._matches_in_extension(extension, keyword)

    def _matches_in_extension(self, extension: Extension, query: str) -> bool:
        if query in extension.name.lower():
            return True

        data = extension.data
        if data.kind and query in data.kind.lower():
            return True
        if data.api_version and query in data.api_version.lower():
            return True
        if data.metadata and data.metadata.name and query in data.metadata.name.lower():
            return True

        if data.metadata and data.metadata.annotations:
            for key, value in data.metadata.annotations.items():
                if query in key.lower() or query in value.lower():
                    return True

        if data.metadata and data.metadata.labels:
            for key, value in data.metadata.labels.items():
                if query in key.lower() or query in value.lower():
                    return True

        if data.data:
            for key, value in data.data.items():
                if query in key.lower() or query in value.lower():
                    return True

        if data.spec:
            return self._search_in_object(data.spec, query)

        return False

    def _search_in_object(self, obj: object, query: str, depth: int = 0) -> bool:
        if depth > self.MAX_SEARCH_DEPTH:
            return False

        if isinstance(obj, str):
            return query in obj.lower()
        if isinstance(obj, (int, float, bool)):
            return query in str(obj).lower()
        if isinstance(obj, list):
            return any(self._search_in_object(item, query, depth + 1) for item in obj)
        if isinstance(obj, dict):
            for key, value in obj.items():
                if query in str(key).lower():
                    return True
                if self._search_in_object(value, query, depth + 1):
                    return True

        return False
