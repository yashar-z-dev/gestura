# 100/100

import logging
from typing import Optional
import traceback, copy

from ...models.event import EventData_keyboard, EventData_click, EventData_move, __EVENTS__
from ...config.models import HandlerConfig
from ...models.protocols import ListenerKeyboardFactory, ListenerMouseFactory
from ...models.event import is_valid_button
from ...utils.key_normalizer import KeyUtils
from ...models.event import EventData_keyboard


class BaseListenerManager:
    """
    Shared handler management logic.
    No knowledge about event types.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, HandlerConfig] = {}

    # ------------------------
    # Handler Management
    # ------------------------

    def register(self, config: HandlerConfig) -> None:
        self._handlers[config.name] = config

    def unregister(self, name: str) -> None:
        self._handlers.pop(name, None)

    def enable_handler(self, name: str) -> None:
        if name in self._handlers:
            self._handlers[name].enabled = True

    def disable_handler(self, name: str) -> None:
        if name in self._handlers:
            self._handlers[name].enabled = False

    def list_handlers(self) -> list[str]:
        return list(self._handlers.keys())

    def get_handler_config(self, name: str) -> Optional[HandlerConfig]:
        return self._handlers.get(name)

    # ------------------------
    # Shared dispatch helper
    # ------------------------

    def _dispatch_to_handlers(self, event) -> None:
        for config in self._handlers.values():
            if not config.enabled:
                continue

            try:
                safe_event = (
                    copy.deepcopy(event)
                    if config.requires_copy
                    else event
                )
                config.handler(safe_event)

            except Exception:
                logging.debug(
                    f"[{self.__class__.__name__}] "
                    f"Handler '{config.name}' failed:\n"
                    f"{traceback.format_exc()}"
                )

class ListenerManagerKeyboard(BaseListenerManager):

    def __init__(self, listener_factory: ListenerKeyboardFactory):
        super().__init__()
        self._listener = listener_factory(self._dispatch_event)
        self._event_id: int = 0  # incremental id for move events

    def _dispatch_event(self, key: str, press: bool) -> None:
        key_name = KeyUtils.parse_key(key=key, output_type="str")
        if not key_name:
            logging.debug("Ignored unsupported key name: %s", key)
            return

        event = EventData_keyboard(id=self._event_id, key=key_name, press=press)
        self._event_id += 1

        self._dispatch_to_handlers(event)

    def start(self) -> None:
        self._listener.start()

    def stop(self) -> None:
        self._listener.stop()


class ListenerManagerMouse(BaseListenerManager):
    """
    Mouse Listener Manager.

    Responsibilities:
    - Receive raw mouse events from MouseListener
    - Normalize and filter events
    - Apply sampling (rate) to move events
    - Assign incremental IDs to move events
    - Forward processed events to registered handlers
    """

    def __init__(self, listener_factory: ListenerMouseFactory, rate: int = 2) -> None:
        super().__init__()

        # Sampling rate for move events (e.g., 2 = every second move)
        self._rate: int = max(1, rate)

        # Incremental ID for move events
        self._move_event_id: int = 0

        # Counter for total move events received (telemetry)
        self._move_counter: int = 0

        # Raw listener (OS hook bridge)
        self._listener = listener_factory(on_move=self._handle_move, on_click=self._handle_click)

        logging.debug(
            "ListenerManagerMouse initialized | rate=%s",
            self._rate
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start underlying mouse listener."""
        self._listener.start()

    def stop(self) -> None:
        """Stop underlying mouse listener."""
        self._listener.stop()

    def set_rate(self, rate: int) -> None:
        """
        Dynamically update sampling rate.
        rate=1 means no sampling (process all move events).
        """
        self._rate = max(1, rate)
        logging.debug("Mouse move sampling rate updated | rate=%s", self._rate)

    # ------------------------------------------------------------------
    # Move Handling
    # ------------------------------------------------------------------

    # def _handle_move(self, event: EventData_move) -> None:
    def _handle_move(self, x: int, y: int) -> None:
        """
        Handle move event:
        - Filter invalid coordinates
        - Apply sampling rate
        - Assign incremental ID
        - Forward to handlers
        """

        # Filter negative coordinates
        if x < 0 or y < 0:
            return

        self._move_counter += 1

        # Apply sampling rate
        if self._move_counter % self._rate != 0:
            return

        # Generate EventData_move
        # Assign internal move ID
        event = EventData_move(x=x, y=y, id=self._move_event_id)
        self._move_event_id += 1

        self._dispatch_to_handlers(event)

    # ------------------------------------------------------------------
    # Click Handling
    # ------------------------------------------------------------------
    def _handle_click(self, x: int, y: int, button: str, press: bool) -> None:
        """
        Handle click event.
        Click events are forwarded without sampling.
        """
        if not is_valid_button(button):
            logging.debug("Ignored unsupported mouse button: %s", button)
            return

        event = EventData_click(x=x, y=y, position=button, press=press)

        self._dispatch_to_handlers(event)
