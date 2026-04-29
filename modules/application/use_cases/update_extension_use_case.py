from __future__ import annotations

from dataclasses import dataclass

from modules.application.base.use_case import UseCase
from modules.application.shared.errors import ExtensionNotFoundError
from modules.application.shared.results import BaseResult
from modules.core.events.event_bus import IEventBus
from modules.core.logging.logger import ILogger, ConsoleLogger
from modules.domain.entities.extension_data import ExtensionData
from modules.domain.repositories.i_extension_repository import IExtensionRepository


@dataclass
class UpdateExtensionInput:
    name: str
    payload: ExtensionData


class UpdateExtensionUseCase(UseCase[UpdateExtensionInput, BaseResult]):
    def __init__(
        self,
        extension_repo: IExtensionRepository,
        event_bus: IEventBus
    ):
        self._extension_repo = extension_repo
        self._event_bus = event_bus
        self._logger: ILogger = ConsoleLogger('UpdateExtensionUseCase')

    def execute(self, input_data: UpdateExtensionInput) -> BaseResult:
        return self._logger.log_operation(
            'execute',
            lambda: self._do_execute(input_data),
            {'extension_name': input_data.name}
        )

    def _do_execute(self, input_data: UpdateExtensionInput) -> BaseResult:
        try:
            extension = self._extension_repo.find_by_name(input_data.name)
            if not extension:
                raise ExtensionNotFoundError(input_data.name)

            updated = extension.update_data(input_data.payload)
            self._extension_repo.save([updated])

            self._event_bus.emit('extension:updated', {
                'name': input_data.name,
                'data': updated.data
            })
            return BaseResult(success=True)
        except Exception as e:
            error_message = str(e)
            self._event_bus.emit('extension:update-error', {
                'name': input_data.name,
                'error': error_message
            })
            return BaseResult(success=False, error=error_message)
