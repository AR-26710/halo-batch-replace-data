from __future__ import annotations

from typing import Any, Callable


class IEventBus:
    def emit(self, event: str, payload: Any = None) -> None:
        raise NotImplementedError

    def on(self, event: str, handler: Callable) -> Callable:
        raise NotImplementedError

    def off(self, event: str, handler: Callable) -> None:
        raise NotImplementedError

    def once(self, event: str, handler: Callable) -> Callable:
        raise NotImplementedError


class SimpleEventBus(IEventBus):
    def __init__(self):
        self._handlers: dict[str, set[Callable]] = {}

    def emit(self, event: str, payload: Any = None) -> None:
        handlers = self._handlers.get(event)
        if handlers:
            for handler in handlers:
                try:
                    handler(payload)
                except Exception as e:
                    print(f"Error in event handler for {event}: {e}")

    def on(self, event: str, handler: Callable) -> Callable:
        if event not in self._handlers:
            self._handlers[event] = set()
        self._handlers[event].add(handler)

        def unsubscribe():
            self.off(event, handler)

        return unsubscribe

    def off(self, event: str, handler: Callable) -> None:
        handlers = self._handlers.get(event)
        if handlers:
            handlers.discard(handler)
            if not handlers:
                del self._handlers[event]

    def once(self, event: str, handler: Callable) -> Callable:
        def once_handler(payload: Any):
            self.off(event, once_handler)
            handler(payload)

        return self.on(event, once_handler)

    def clear(self) -> None:
        self._handlers.clear()


event_bus = SimpleEventBus()
