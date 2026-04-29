from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from typing import Callable, Optional, TypeVar

T = TypeVar('T')


class ILogger(ABC):
    @abstractmethod
    def debug(self, message: str, context: Optional[dict] = None) -> None:
        pass

    @abstractmethod
    def info(self, message: str, context: Optional[dict] = None) -> None:
        pass

    @abstractmethod
    def warn(self, message: str, context: Optional[dict] = None) -> None:
        pass

    @abstractmethod
    def error(self, message: str, error: Optional[Exception] = None, context: Optional[dict] = None) -> None:
        pass

    @abstractmethod
    def log_operation(self, operation: str, fn: Callable[[], T], context: Optional[dict] = None) -> T:
        pass

    @abstractmethod
    def with_source(self, source: str) -> 'ILogger':
        pass


class ConsoleLogger(ILogger):
    def __init__(self, source: str = 'App', prefix: str = '[HaloExtensions]'):
        self._source = source
        self._prefix = prefix
        self._logger = logging.getLogger(f'{prefix}.{source}')

    def debug(self, message: str, context: Optional[dict] = None) -> None:
        self._log(logging.DEBUG, message, context)

    def info(self, message: str, context: Optional[dict] = None) -> None:
        self._log(logging.INFO, message, context)

    def warn(self, message: str, context: Optional[dict] = None) -> None:
        self._log(logging.WARNING, message, context)

    def error(self, message: str, error: Optional[Exception] = None, context: Optional[dict] = None) -> None:
        self._log(logging.ERROR, message, context, error)

    def _log(self, level: int, message: str, context: Optional[dict] = None, error: Optional[Exception] = None) -> None:
        context_str = f' {context}' if context else ''
        error_str = f'\nError: {error}' if error else ''
        log_message = f'{self._prefix} [{self._source}] {message}{context_str}{error_str}'
        self._logger.log(level, log_message, exc_info=error is not None and level >= logging.ERROR)

    def log_operation(self, operation: str, fn: Callable[[], T], context: Optional[dict] = None) -> T:
        start_time = time.perf_counter()
        self.info(f'Operation started: {operation}', context)
        try:
            result = fn()
            duration = round((time.perf_counter() - start_time) * 1000)
            self.info(f'Operation completed: {operation}', {**({**context, 'duration': duration} if context else {'duration': duration})})
            return result
        except Exception as e:
            duration = round((time.perf_counter() - start_time) * 1000)
            self.error(f'Operation failed: {operation}', e, {**({**context, 'duration': duration} if context else {'duration': duration})})
            raise

    def with_source(self, source: str) -> 'ConsoleLogger':
        return ConsoleLogger(source, self._prefix)


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        format='[%(levelname)s] %(message)s',
        level=level,
        handlers=[logging.StreamHandler()]
    )
