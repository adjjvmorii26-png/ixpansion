from __future__ import annotations
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class Registry(Generic[T]):
    def __init__(self) -> None:
        self._items: dict[str, T] = {}

    def register(self, name: str, item: T, *, replace: bool = False) -> None:
        if name in self._items and not replace:
            raise KeyError(f"already registered: {name}")
        self._items[name] = item

    def get(self, name: str) -> T:
        return self._items[name]

    def names(self) -> list[str]:
        return sorted(self._items)

    def create(self, name: str, *args: object, **kwargs: object):
        factory = self.get(name)
        if not isinstance(factory, Callable):
            raise TypeError(f"registered item is not callable: {name}")
        return factory(*args, **kwargs)
