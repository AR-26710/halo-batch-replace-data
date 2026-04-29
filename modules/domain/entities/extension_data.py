from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Metadata:
    name: Optional[str] = None
    annotations: Optional[dict[str, str]] = None
    labels: Optional[dict[str, str]] = None
    resource_version: Optional[int] = None
    creation_timestamp: Optional[str] = None
    version: Optional[int] = None


@dataclass
class ExtensionData:
    api_version: Optional[str] = None
    kind: Optional[str] = None
    metadata: Optional[Metadata] = None
    spec: Optional[dict[str, Any]] = None
    data: Optional[dict[str, str]] = None

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key, None)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)
