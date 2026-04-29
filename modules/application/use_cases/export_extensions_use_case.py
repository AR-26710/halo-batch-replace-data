from __future__ import annotations

from dataclasses import dataclass

from modules.application.base.use_case import UseCase
from modules.application.shared.results import BaseResult
from modules.core.events.event_bus import IEventBus
from modules.core.logging.logger import ILogger, ConsoleLogger
from modules.domain.repositories.i_extension_repository import IExtensionRepository
from modules.infrastructure.repositories.file_storage_repository import FileStorageRepository
from modules.infrastructure.services.encoding.base64_encoder import Base64Encoder


@dataclass
class ExportExtensionsInput:
    filepath: str


class ExportExtensionsUseCase(UseCase[ExportExtensionsInput, BaseResult]):
    def __init__(
        self,
        extension_repo: IExtensionRepository,
        storage_repo: FileStorageRepository,
        encoder: Base64Encoder,
        event_bus: IEventBus
    ):
        self._extension_repo = extension_repo
        self._storage_repo = storage_repo
        self._encoder = encoder
        self._event_bus = event_bus
        self._logger: ILogger = ConsoleLogger('ExportExtensionsUseCase')

    def execute(self, input_data: ExportExtensionsInput) -> BaseResult:
        return self._logger.log_operation(
            'execute',
            lambda: self._do_execute(input_data),
            {'filepath': input_data.filepath}
        )

    def _do_execute(self, input_data: ExportExtensionsInput) -> BaseResult:
        try:
            extensions = self._extension_repo.find_all()
            if not extensions:
                return BaseResult(success=False, error='没有可导出的扩展数据')

            raw_data = self._encoder.encode(extensions)
            self._storage_repo.save(raw_data, input_data.filepath)

            self._extension_repo.mark_as_saved()
            self._event_bus.emit('extensions:exported', {
                'filename': input_data.filepath,
                'count': len(extensions)
            })

            return BaseResult(success=True)
        except Exception as e:
            error_message = str(e)
            self._event_bus.emit('extensions:export-error', {'error': error_message})
            return BaseResult(success=False, error=error_message)
