from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class FilterCriteria:
    field: str
    value: str


@dataclass(frozen=True)
class SearchQuery:
    keywords: tuple[str, ...] = field(default_factory=tuple)
    filters: tuple[FilterCriteria, ...] = field(default_factory=tuple)

    def is_empty(self) -> bool:
        return len(self.keywords) == 0 and len(self.filters) == 0

    def has_keywords(self) -> bool:
        return len(self.keywords) > 0

    def has_filters(self) -> bool:
        return len(self.filters) > 0

    def get_filter_value(self, field_name: str) -> Optional[str]:
        for f in self.filters:
            if f.field == field_name:
                return f.value
        return None

    def with_keywords(self, keywords: list[str]) -> 'SearchQuery':
        return SearchQuery(tuple(keywords), self.filters)

    def with_filter(self, field_name: str, value: str) -> 'SearchQuery':
        new_filters = []
        replaced = False
        for f in self.filters:
            if f.field == field_name:
                new_filters.append(FilterCriteria(field_name, value))
                replaced = True
            else:
                new_filters.append(f)
        if not replaced:
            new_filters.append(FilterCriteria(field_name, value))
        return SearchQuery(self.keywords, tuple(new_filters))

    def without_filter(self, field_name: str) -> 'SearchQuery':
        new_filters = tuple(f for f in self.filters if f.field != field_name)
        return SearchQuery(self.keywords, new_filters)

    @staticmethod
    def empty() -> 'SearchQuery':
        return SearchQuery()

    def __str__(self) -> str:
        parts = []
        if self.keywords:
            parts.append(f'keywords:[{",".join(self.keywords)}]')
        if self.filters:
            filter_str = ','.join(f'{f.field}={f.value}' for f in self.filters)
            parts.append(f'filters:{{{filter_str}}}')
        return ','.join(parts) if parts else '(empty)'
