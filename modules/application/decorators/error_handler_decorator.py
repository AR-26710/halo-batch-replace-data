from __future__ import annotations

from modules.application.base.use_case_decorator import UseCaseDecorator
from modules.application.shared.results import BaseResult
from typing import TypeVar, Callable

Input = TypeVar('Input')
Output = TypeVar('Output')


class ErrorHandlerDecorator(UseCaseDecorator[Input, Output]):
    def __init__(self, default_error_message: str, get_error_result: Callable[[Exception], BaseResult]):
        super().__init__()
        self._default_error_message = default_error_message
        self._get_error_result = get_error_result

    def _execute_internal(self, input_data: Input) -> Output:
        try:
            if not self._use_case:
                raise ValueError('UseCase not set')
            return self._use_case.execute(input_data)
        except Exception as e:
            error_message = str(e) if isinstance(e, Exception) else self._default_error_message
            error_result = self._get_error_result(e)
            error_result.error = error_message
            return error_result
