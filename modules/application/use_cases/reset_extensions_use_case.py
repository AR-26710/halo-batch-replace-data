from __future__ import annotations

from modules.application.base.use_case import UseCase
from modules.application.shared.results import BaseResult
from modules.core.events.event_bus import IEventBus
from modules.core.logging.logger import ILogger, ConsoleLogger
from modules.domain.repositories.i_extension_repository import IExtensionRepository


class ResetExtensionsUseCase(UseCase[None, BaseResult]):
    def __init__(
        self,
        extension_repo: IExtensionRepository,
        event_bus: IEventBus
    ):
        self._extension_repo = extension_repo
        self._event_bus = event_bus
        self._logger: ILogger = ConsoleLogger('ResetExtensionsUseCase')

    def execute(self, input_data: None = None) -> BaseResult:
        return self._logger.log_operation(
            'execute',
            lambda: self._do_execute()
        )

    def _do_execute(self) -> BaseResult:
        try:
            self._extension_repo.clear()
            self._event_bus.emit('extensions:reset', {})
            return BaseResult(success=True)
        except Exception as e:
            return BaseResult(success=False, error=str(e))
