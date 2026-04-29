from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from modules.application.base.use_case import UseCase

Input = TypeVar('Input')
Output = TypeVar('Output')


class UseCaseDecorator(UseCase[Input, Output], ABC):
    def __init__(self):
        self._use_case: UseCase[Input, Output] | None = None

    def set_use_case(self, use_case: UseCase[Input, Output]) -> None:
        self._use_case = use_case

    def execute(self, input_data: Input) -> Output:
        if not self._use_case:
            raise ValueError('UseCase not set in decorator')
        return self._execute_internal(input_data)

    @abstractmethod
    def _execute_internal(self, input_data: Input) -> Output:
        pass
