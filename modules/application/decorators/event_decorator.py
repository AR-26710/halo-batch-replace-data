from __future__ import annotations

from typing import Callable, Optional, TypeVar

from modules.application.base.use_case_decorator import UseCaseDecorator
from modules.core.events.event_bus import IEventBus

Input = TypeVar('Input')
Output = TypeVar('Output')


class EventDecorator(UseCaseDecorator[Input, Output]):
    def __init__(
        self,
        event_bus: IEventBus,
        success_event: Optional[str] = None,
        error_event: Optional[str] = None,
        get_success_payload: Optional[Callable[[Output, Input], dict]] = None,
        get_error_payload: Optional[Callable[[Exception, Input], dict]] = None,
    ):
        super().__init__()
        self._event_bus = event_bus
        self._success_event = success_event
        self._error_event = error_event
        self._get_success_payload = get_success_payload
        self._get_error_payload = get_error_payload

    def _execute_internal(self, input_data: Input) -> Output:
        try:
            if not self._use_case:
                raise ValueError('UseCase not set')
            result = self._use_case.execute(input_data)

            if self._success_event and self._get_success_payload:
                payload = self._get_success_payload(result, input_data)
                self._event_bus.emit(self._success_event, payload)

            return result
        except Exception as e:
            if self._error_event and self._get_error_payload:
                payload = self._get_error_payload(e, input_data)
                self._event_bus.emit(self._error_event, payload)
            raise
