from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class BaseResult:
    success: bool
    error: Optional[str] = None


@dataclass
class CountResult(BaseResult):
    count: int = 0


@dataclass
class BatchResult(BaseResult):
    updated_count: int = 0
    deleted_count: int = 0
