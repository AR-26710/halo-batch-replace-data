from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ReplaceRule:
    search: str
    replace: str
    is_regex: bool = False


@dataclass
class ReplaceScope:
    search_in_name: bool = True
    search_in_kind: bool = True
    search_in_metadata_name: bool = True
    search_in_api_version: bool = True
    search_in_data: bool = True
    search_in_spec: bool = True
    selected_kinds: list[str] = field(default_factory=list)


@dataclass
class PreviewChange:
    field: str
    old: str
    new: str


@dataclass
class ReplaceResult:
    extension_name: str
    changes: list[PreviewChange] = field(default_factory=list)
    updated_data: dict = field(default_factory=dict)
    has_changes: bool = False


@dataclass
class BatchReplaceResult:
    results: list[ReplaceResult] = field(default_factory=list)
    total_changes: int = 0


class IReplaceEngine:
    def apply(self, extensions: list, rules: list[ReplaceRule], scope: ReplaceScope) -> BatchReplaceResult:
        raise NotImplementedError

    def preview(self, extensions: list, rules: list[ReplaceRule], scope: ReplaceScope) -> BatchReplaceResult:
        raise NotImplementedError
