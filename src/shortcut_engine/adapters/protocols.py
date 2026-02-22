from typing import Protocol, Callable

from ..config.models import HandlerKeyboardConfig, HandlerMouseConfig

# --------------------------------------------------
# Base Listener
# --------------------------------------------------
class ListenerProtocol(Protocol):
    def start(self) -> None: ...
    def stop(self) -> None: ...


# --------------------------------------------------
# Listener Factories (OS adapters)
# --------------------------------------------------
class ListenerKeyboardFactory(Protocol):
    def __call__(
        self,
        on_event_callback: Callable[[str, bool], None]
    ) -> ListenerProtocol: ...


class ListenerMouseFactory(Protocol):
    def __call__(
        self,
        on_move: Callable[[int, int], None],
        on_click: Callable[[int, int, str, bool], None]
    ) -> ListenerProtocol: ...


# --------------------------------------------------
# Manager Protocols
# --------------------------------------------------
class ListenerKeyboardManagerProtocol(Protocol):
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def register(self, config: HandlerKeyboardConfig) -> None: ...


class ListenerMouseManagerProtocol(Protocol):
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def register(self, config: HandlerMouseConfig) -> None: ...


# --------------------------------------------------
# Manager Factories
# --------------------------------------------------
class ListenerManagerKeyboardFactory(Protocol):
    def __call__(
        self,
        listener_factory: ListenerKeyboardFactory
    ) -> ListenerKeyboardManagerProtocol: ...


class ListenerManagerMouseFactory(Protocol):
    def __call__(
        self,
        listener_factory: ListenerMouseFactory
    ) -> ListenerMouseManagerProtocol: ...