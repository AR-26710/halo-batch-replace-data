from __future__ import annotations

from dataclasses import dataclass

from modules.application.base.use_case import UseCase
from modules.application.shared.results import BatchResult
from modules.core.events.event_bus import IEventBus
from modules.core.logging.logger import ILogger, ConsoleLogger
from modules.domain.entities.extension_data import ExtensionData, Metadata
from modules.domain.repositories.i_extension_repository import IExtensionRepository
from modules.infrastructure.services.encoding.base64_decoder import Base64Decoder
from modules.infrastructure.services.encoding.base64_encoder import Base64Encoder
from modules.infrastructure.types.replace_types import ReplaceRule, ReplaceScope, IReplaceEngine


@dataclass
class BatchReplaceInput:
    rules: list[ReplaceRule]
    scope: ReplaceScope


class BatchReplaceUseCase(UseCase[BatchReplaceInput, BatchResult]):
    def __init__(
        self,
        extension_repo: IExtensionRepository,
        replace_engine: IReplaceEngine,
        decoder: Base64Decoder,
        encoder: Base64Encoder,
        event_bus: IEventBus
    ):
        self._extension_repo = extension_repo
        self._replace_engine = replace_engine
        self._decoder = decoder
        self._encoder = encoder
        self._event_bus = event_bus
        self._logger: ILogger = ConsoleLogger('BatchReplaceUseCase')

    def execute(self, input_data: BatchReplaceInput) -> BatchResult:
        return self._logger.log_operation(
            'execute',
            lambda: self._do_execute(input_data),
            {'rule_count': len(input_data.rules)}
        )

    def _do_execute(self, input_data: BatchReplaceInput) -> BatchResult:
        try:
            all_extensions = self._extension_repo.find_all()

            if not all_extensions:
                return BatchResult(success=True, updated_count=0)

            result = self._replace_engine.apply(all_extensions, input_data.rules, input_data.scope)

            if result.results:
                updated_extensions = []
                for replace_result in result.results:
                    original = self._extension_repo.find_by_name(replace_result.extension_name)
                    if original:
                        new_data = self._dict_to_extension_data(replace_result.updated_data)
                        updated_ext = original.update_all(
                            replace_result.extension_name,
                            original.version,
                            new_data
                        )
                        updated_extensions.append(updated_ext)

                if updated_extensions:
                    self._extension_repo.save(updated_extensions)

            self._event_bus.emit('extensions:batch-replaced', {
                'total_changes': result.total_changes,
                'updated_count': len(result.results)
            })

            return BatchResult(success=True, updated_count=len(result.results))
        except Exception as e:
            error_message = str(e)
            self._event_bus.emit('extensions:batch-replace-error', {'error': error_message})
            return BatchResult(success=False, updated_count=0, error=error_message)

    def _dict_to_extension_data(self, data: dict) -> ExtensionData:
        metadata = None
        if 'metadata' in data and data['metadata']:
            m = data['metadata']
            metadata = Metadata(
                name=m.get('name'),
                annotations=m.get('annotations'),
                labels=m.get('labels'),
                resource_version=m.get('resourceVersion'),
                creation_timestamp=m.get('creationTimestamp'),
                version=m.get('version')
            )

        return ExtensionData(
            api_version=data.get('apiVersion'),
            kind=data.get('kind'),
            metadata=metadata,
            spec=data.get('spec'),
            data=data.get('data')
        )
