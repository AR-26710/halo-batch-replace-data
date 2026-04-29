from __future__ import annotations

from typing import Callable, Optional, TypeVar

from modules.application.base.use_case_decorator import UseCaseDecorator
from modules.core.logging.logger import ILogger, ConsoleLogger

Input = TypeVar('Input')
Output = TypeVar('Output')


class LoggingDecorator(UseCaseDecorator[Input, Output]):
    def __init__(self, source: str, operation: str, get_metadata: Optional[Callable] = None):
        super().__init__()
        self._logger: ILogger = ConsoleLogger(source)
        self._operation = operation
        self._get_metadata = get_metadata

    def _execute_internal(self, input_data: Input) -> Output:
        metadata = self._get_metadata(input_data) if self._get_metadata else None
        return self._logger.log_operation(
            self._operation,
            lambda: self._use_case.execute(input_data) if self._use_case else None,
            metadata
        )
