from __future__ import annotations

import re
from typing import Any

from modules.domain.entities.extension import Extension
from modules.domain.entities.extension_data import ExtensionData
from modules.infrastructure.types.replace_types import (
    ReplaceRule, ReplaceScope, PreviewChange, ReplaceResult,
    BatchReplaceResult, IReplaceEngine
)


class DefaultReplaceEngine(IReplaceEngine):
    CHUNK_SIZE = 100

    def apply(self, extensions: list[Extension], rules: list[ReplaceRule], scope: ReplaceScope) -> BatchReplaceResult:
        results: list[ReplaceResult] = []
        total_changes = 0

        for ext in extensions:
            ext_kind = ext.data.kind
            if scope.selected_kinds and ext_kind and ext_kind not in scope.selected_kinds:
                continue

            result = self._apply_to_extension(ext, rules, scope)
            if result.has_changes:
                results.append(result)
                total_changes += len(result.changes)

        return BatchReplaceResult(results=results, total_changes=total_changes)

    def preview(self, extensions: list[Extension], rules: list[ReplaceRule], scope: ReplaceScope) -> BatchReplaceResult:
        return self.apply(extensions, rules, scope)

    def _apply_to_extension(self, ext: Extension, rules: list[ReplaceRule], scope: ReplaceScope) -> ReplaceResult:
        changes: list[PreviewChange] = []
        new_data_dict = self._extension_data_to_dict(ext.data)
        new_name = ext.name
        has_changes = False

        for rule in rules:
            if not rule.search.strip():
                continue

            if scope.search_in_name:
                replaced_name = self._apply_replace_to_text(ext.name, rule.search, rule.replace, rule.is_regex)
                if replaced_name != ext.name:
                    changes.append(PreviewChange(field='name', old=ext.name, new=replaced_name))
                    new_name = replaced_name
                    has_changes = True

            current_data = new_data_dict

            if scope.search_in_kind and current_data.get('kind'):
                new_kind = self._apply_replace_to_text(current_data['kind'], rule.search, rule.replace, rule.is_regex)
                if new_kind != current_data['kind']:
                    changes.append(PreviewChange(field='kind', old=current_data['kind'], new=new_kind))
                    new_data_dict = {**current_data, 'kind': new_kind}
                    has_changes = True

            if scope.search_in_metadata_name and current_data.get('metadata', {}).get('name'):
                old_name = current_data['metadata']['name']
                replaced_name = self._apply_replace_to_text(old_name, rule.search, rule.replace, rule.is_regex)
                if replaced_name != old_name:
                    changes.append(PreviewChange(field='metadata.name', old=old_name, new=replaced_name))
                    new_metadata = {**current_data.get('metadata', {}), 'name': replaced_name}
                    new_data_dict = {**current_data, 'metadata': new_metadata}
                    has_changes = True

            if scope.search_in_api_version and current_data.get('apiVersion'):
                new_api_version = self._apply_replace_to_text(current_data['apiVersion'], rule.search, rule.replace, rule.is_regex)
                if new_api_version != current_data['apiVersion']:
                    changes.append(PreviewChange(field='apiVersion', old=current_data['apiVersion'], new=new_api_version))
                    new_data_dict = {**current_data, 'apiVersion': new_api_version}
                    has_changes = True

            if scope.search_in_data and current_data.get('data'):
                data_result = self._replace_in_data(current_data['data'], rule.search, rule.replace, rule.is_regex)
                if data_result['has_changes']:
                    changes.extend(data_result['changes'])
                    new_data_dict = {**current_data, 'data': data_result['new_data']}
                    has_changes = True

            if scope.search_in_spec and current_data.get('spec'):
                spec_result = self._replace_in_object(current_data['spec'], rule.search, rule.replace, rule.is_regex, 'spec')
                if spec_result['has_changes']:
                    changes.extend(spec_result['changes'])
                    new_data_dict = {**current_data, 'spec': spec_result['new_obj']}
                    has_changes = True

        return ReplaceResult(
            extension_name=new_name,
            changes=changes,
            updated_data=new_data_dict,
            has_changes=has_changes
        )

    def _apply_replace_to_text(self, text: str, search: str, replace: str, is_regex: bool) -> str:
        if is_regex:
            try:
                return re.sub(search, replace, text)
            except re.error:
                return text
        return text.replace(search, replace)

    def _replace_in_data(self, data: dict[str, str], search: str, replace: str, is_regex: bool) -> dict:
        changes: list[PreviewChange] = []
        new_data: dict[str, str] = {}
        has_changes = False

        for key, value in data.items():
            new_key = self._apply_replace_to_text(key, search, replace, is_regex)
            new_value = self._apply_replace_to_text(value, search, replace, is_regex)

            if new_key != key or new_value != value:
                changes.append(PreviewChange(field=f'data.{key}', old=f'{key}: {value}', new=f'{new_key}: {new_value}'))
                new_data[new_key] = new_value
                has_changes = True
            else:
                new_data[key] = value

        return {'new_data': new_data, 'changes': changes, 'has_changes': has_changes}

    def _replace_in_object(self, obj: dict, search: str, replace: str, is_regex: bool, path: str) -> dict:
        changes: list[PreviewChange] = []
        has_changes = False
        new_obj: dict[str, Any] = {}

        for key, value in obj.items():
            current_path = f'{path}.{key}'
            new_key = self._apply_replace_to_text(key, search, replace, is_regex)

            if isinstance(value, str):
                new_value = self._apply_replace_to_text(value, search, replace, is_regex)
                if new_key != key or new_value != value:
                    changes.append(PreviewChange(field=current_path, old=f'{key}: {value}', new=f'{new_key}: {new_value}'))
                    new_obj[new_key] = new_value
                    has_changes = True
                else:
                    new_obj[key] = value
            elif isinstance(value, (int, float)):
                str_value = str(value)
                new_str_value = self._apply_replace_to_text(str_value, search, replace, is_regex)
                if new_str_value != str_value:
                    try:
                        new_num = float(new_str_value) if '.' in new_str_value else int(new_str_value)
                        changes.append(PreviewChange(field=current_path, old=f'{key}: {value}', new=f'{new_key}: {new_num}'))
                        new_obj[new_key] = new_num
                        has_changes = True
                    except ValueError:
                        new_obj[key] = value
                elif new_key != key:
                    new_obj[new_key] = value
                    has_changes = True
                else:
                    new_obj[key] = value
            elif isinstance(value, list):
                array_result = self._replace_in_array(value, search, replace, is_regex, current_path)
                if array_result['has_changes'] or new_key != key:
                    changes.extend(array_result['changes'])
                    new_obj[new_key] = array_result['new_array']
                    has_changes = True
                else:
                    new_obj[key] = value
            elif isinstance(value, dict):
                nested_result = self._replace_in_object(value, search, replace, is_regex, current_path)
                if nested_result['has_changes'] or new_key != key:
                    changes.extend(nested_result['changes'])
                    new_obj[new_key] = nested_result['new_obj']
                    has_changes = True
                else:
                    new_obj[key] = value
            else:
                new_obj[new_key] = value
                if new_key != key:
                    has_changes = True

        return {'new_obj': new_obj, 'changes': changes, 'has_changes': has_changes}

    def _replace_in_array(self, arr: list, search: str, replace: str, is_regex: bool, path: str) -> dict:
        changes: list[PreviewChange] = []
        new_array: list = []
        has_changes = False

        for i, item in enumerate(arr):
            current_path = f'{path}[{i}]'

            if isinstance(item, str):
                new_item = self._apply_replace_to_text(item, search, replace, is_regex)
                if new_item != item:
                    changes.append(PreviewChange(field=current_path, old=item, new=new_item))
                    new_array.append(new_item)
                    has_changes = True
                else:
                    new_array.append(item)
            elif isinstance(item, dict):
                nested_result = self._replace_in_object(item, search, replace, is_regex, current_path)
                if nested_result['has_changes']:
                    changes.extend(nested_result['changes'])
                    new_array.append(nested_result['new_obj'])
                    has_changes = True
                else:
                    new_array.append(item)
            else:
                new_array.append(item)

        return {'new_array': new_array, 'changes': changes, 'has_changes': has_changes}

    def _extension_data_to_dict(self, data: ExtensionData) -> dict:
        result = {}
        if data.api_version is not None:
            result['apiVersion'] = data.api_version
        if data.kind is not None:
            result['kind'] = data.kind
        if data.metadata is not None:
            m = data.metadata
            metadata = {}
            if m.name is not None:
                metadata['name'] = m.name
            if m.annotations is not None:
                metadata['annotations'] = m.annotations
            if m.labels is not None:
                metadata['labels'] = m.labels
            if m.resource_version is not None:
                metadata['resourceVersion'] = m.resource_version
            if m.creation_timestamp is not None:
                metadata['creationTimestamp'] = m.creation_timestamp
            if m.version is not None:
                metadata['version'] = m.version
            result['metadata'] = metadata
        if data.spec is not None:
            result['spec'] = data.spec
        if data.data is not None:
            result['data'] = data.data
        return result


default_replace_engine = DefaultReplaceEngine()
