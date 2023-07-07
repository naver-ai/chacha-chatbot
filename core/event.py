from typing import TypeVar, Generic, Awaitable, Callable

T = TypeVar('T')


class AsyncSubject(Generic[T]):
    def __init__(self):
        self._handlers: list[Callable[[T], Awaitable[None]]] = []

    def dispose(self):
        self._handlers.clear()

    def subscribe(self, on_next: Callable[[T], Awaitable[None]]):
        if on_next not in self._handlers:
            self._handlers.append(on_next)

    async def on_next(self, value: T):
        for handler in self._handlers:
            await handler(value)



class AsyncBehaviorSubject(AsyncSubject[T]):
    def __init__(self, default_value: T):
        super().__init__()
        self._value = default_value

    @property
    def value(self)->T:
        return self._value

    async def subscribe(self, on_next: Callable[[T], Awaitable[None]]):
        super().subscribe(on_next)
        await on_next(self._value)

    async def on_next(self, value: T):
        self._value = value
        await super().on_next(value)
