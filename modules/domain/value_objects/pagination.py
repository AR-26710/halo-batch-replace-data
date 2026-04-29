from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Pagination:
    page: int
    page_size: int
    total: int

    def __post_init__(self):
        if self.page < 1:
            raise ValueError('Page must be >= 1')
        if self.page_size < 1:
            raise ValueError('Page size must be >= 1')
        if self.total < 0:
            raise ValueError('Total must be >= 0')

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def total_pages(self) -> int:
        return math.ceil(self.total / self.page_size) if self.page_size > 0 else 0

    @property
    def has_next_page(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous_page(self) -> bool:
        return self.page > 1

    def next_page(self) -> 'Pagination':
        if not self.has_next_page:
            return self
        return Pagination(self.page + 1, self.page_size, self.total)

    def previous_page(self) -> 'Pagination':
        if not self.has_previous_page:
            return self
        return Pagination(self.page - 1, self.page_size, self.total)

    def go_to_page(self, page: int) -> 'Pagination':
        clamped = max(1, min(page, self.total_pages or 1))
        return Pagination(clamped, self.page_size, self.total)

    def with_page_size(self, page_size: int) -> 'Pagination':
        return Pagination(1, page_size, self.total)

    def with_total(self, total: int) -> 'Pagination':
        return Pagination(self.page, self.page_size, total)

    @staticmethod
    def default(page_size: int = 12) -> 'Pagination':
        return Pagination(1, page_size, 0)
