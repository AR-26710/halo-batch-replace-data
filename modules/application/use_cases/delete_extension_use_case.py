from __future__ import annotations

from dataclasses import dataclass

from modules.application.base.use_case import UseCase
from modules.application.shared.results import BaseResult
from modules.core.events.event_bus import IEventBus
from modules.core.logging.logger import ILogger, ConsoleLogger
from modules.domain.repositories.i_extension_repository import IExtensionRepository
from modules.application.shared.errors import ExtensionNotFoundError


@dataclass
class DeleteExtensionInput:
    name: str


class DeleteExtensionUseCase(UseCase[DeleteExtensionInput, BaseResult]):
    def __init__(
        self,
        extension_repo: IExtensionRepository,
        event_bus: IEventBus
    ):
        self._extension_repo = extension_repo
        self._event_bus = event_bus
        self._logger: ILogger = ConsoleLogger('DeleteExtensionUseCase')

    def execute(self, input_data: DeleteExtensionInput) -> BaseResult:
        return self._logger.log_operation(
            'execute',
            lambda: self._do_execute(input_data),
            {'extension_name': input_data.name}
        )

    def _do_execute(self, input_data: DeleteExtensionInput) -> BaseResult:
        try:
            extension = self._extension_repo.find_by_name(input_data.name)
            if not extension:
                raise ExtensionNotFoundError(input_data.name)

            self._extension_repo.delete(input_data.name)
            self._event_bus.emit('extension:deleted', {'name': input_data.name})
            return BaseResult(success=True)
        except Exception as e:
            error_message = str(e)
            self._event_bus.emit('extension:delete-error', {
                'name': input_data.name,
                'error': error_message
            })
            return BaseResult(success=False, error=error_message)
