from __future__ import annotations

from dataclasses import dataclass

from modules.application.base.use_case import UseCase
from modules.application.shared.results import CountResult
from modules.core.events.event_bus import IEventBus
from modules.core.logging.logger import ILogger, ConsoleLogger
from modules.domain.repositories.i_extension_repository import IExtensionRepository
from modules.domain.repositories.i_storage_repository import IStorageRepository
from modules.infrastructure.services.encoding.base64_decoder import Base64Decoder


@dataclass
class LoadExtensionsInput:
    filepath: str


class LoadExtensionsUseCase(UseCase[LoadExtensionsInput, CountResult]):
    def __init__(
        self,
        storage_repo: IStorageRepository,
        extension_repo: IExtensionRepository,
        decoder: Base64Decoder,
        event_bus: IEventBus
    ):
        self._storage_repo = storage_repo
        self._extension_repo = extension_repo
        self._decoder = decoder
        self._event_bus = event_bus
        self._logger: ILogger = ConsoleLogger('LoadExtensionsUseCase')

    def execute(self, input_data: LoadExtensionsInput) -> CountResult:
        return self._logger.log_operation(
            'execute',
            lambda: self._do_execute(input_data),
            {'filepath': input_data.filepath}
        )

    def _do_execute(self, input_data: LoadExtensionsInput) -> CountResult:
        try:
            raw_data = self._storage_repo.load(input_data.filepath)
            extensions = self._decoder.decode(raw_data)
            self._extension_repo.save(extensions)

            self._event_bus.emit('extensions:loaded', {'count': len(extensions)})

            return CountResult(success=True, count=len(extensions))
        except Exception as e:
            error_message = str(e)
            self._event_bus.emit('extensions:load-error', {'error': error_message})
            return CountResult(success=False, count=0, error=error_message)
