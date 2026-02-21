"""
TriggerEvent  →  Policy  →  ActionEvent
"""

from typing import Protocol, Callable

from ..models.event import EventData_keyboard, EventData_click, EventData_move, __EVENTS__
from .policy import TriggerEvent


from typing import Protocol, Callable


class ListenerProtocol(Protocol):
    def start(self) -> None: ...
    def stop(self) -> None: ...


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


class PolicyEngineProtocol(Protocol):
    """
    Public contract required by ShortcutWorker.
    """

    def evaluate(self, _TriggerEvent: TriggerEvent) -> bool: ...

# ===== Protocol =====
class Protocol_KeyboardListener(Protocol):
    def __call__(self, event: EventData_keyboard) -> None: ...

class Protocol_MouseListener(Protocol):
    def __call__(self, event: EventData_click | EventData_move) -> None: ...
