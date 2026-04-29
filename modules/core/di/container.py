from __future__ import annotations

from typing import Any, Callable, TypeVar, Generic, Optional

T = TypeVar('T')


class Provider(Generic[T]):
    def __init__(
        self,
        provide: str,
        use_value: Optional[T] = None,
        use_factory: Optional[Callable[[], T]] = None,
        use_class: Optional[type] = None,
    ):
        self.provide = provide
        self.use_value = use_value
        self.use_factory = use_factory
        self.use_class = use_class


class DIContainer:
    def __init__(self):
        self._providers: dict[str, Provider] = {}
        self._instances: dict[str, Any] = {}

    def register(self, provider: Provider) -> None:
        self._providers[provider.provide] = provider

    def resolve(self, token: str) -> Any:
        if token in self._instances:
            return self._instances[token]

        provider = self._providers.get(token)
        if not provider:
            raise ValueError(f"No provider found for token: {token}")

        instance: Any
        if provider.use_value is not None:
            instance = provider.use_value
        elif provider.use_factory is not None:
            instance = provider.use_factory()
        elif provider.use_class is not None:
            instance = provider.use_class()
        else:
            raise ValueError(f"Invalid provider for token: {token}")

        self._instances[token] = instance
        return instance

    def clear(self) -> None:
        self._instances.clear()


container = DIContainer()
