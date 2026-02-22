import logging
import traceback

from ...config.models import (HandlerKeyboardConfig, KeyboardEvent,
                              HandlerMouseConfig, MouseEvent)
from ..protocols import ListenerKeyboardFactory, ListenerMouseFactory


class ListenerManagerKeyboard:
    def __init__(self, listener_factory: ListenerKeyboardFactory) -> None:
        self._listener = listener_factory(self._dispatch_event)
        self._handlers: dict[str, HandlerKeyboardConfig] = {}

    def register(self, config: HandlerKeyboardConfig) -> None:
        self._handlers[config.name] = config

    def unregister(self, name: str) -> None:
        self._handlers.pop(name, None)

    def list_handlers(self) -> list[str]:
        return list(self._handlers.keys())

    def _dispatch_event(self, key: str, press: bool) -> None:
        event = KeyboardEvent(key=key, press=press)

        for config in self._handlers.values():
            if not config.enabled:
                continue

            try:
                config.handler(event)
            except Exception:
                logging.exception(
                    "[ListenerManagerKeyboard] "
                    f"Handler '{config.name}' failed:\n"
                    f"{traceback.format_exc()}"
                )

    def start(self) -> None:
        self._listener.start()

    def stop(self) -> None:
        self._listener.stop()


class ListenerManagerMouse:
    def __init__(self, listener_factory: ListenerMouseFactory) -> None:
        self._listener = listener_factory(
            on_move=self._handle_move,
            on_click=self._handle_click,
        )
        self._handlers: dict[str, HandlerMouseConfig] = {}

    def register(self, config: HandlerMouseConfig) -> None:
        self._handlers[config.name] = config

    def unregister(self, name: str) -> None:
        self._handlers.pop(name, None)

    def list_handlers(self) -> list[str]:
        return list(self._handlers.keys())

    def _handle_move(self, x: int, y: int) -> None:
        event = MouseEvent(x=x, y=y)

        for config in self._handlers.values():
            if not config.enabled:
                continue

            try:
                config.handler(event)
            except Exception:
                logging.exception(
                    "[ListenerManagerMouse] "
                    f"Handler '{config.name}' failed:\n"
                    f"{traceback.format_exc()}"
                )

    def _handle_click(self, x: int, y: int, button: str, press: bool) -> None:
        event = MouseEvent(x=x, y=y, position=button, press=press)

        for config in self._handlers.values():
            if not config.enabled:
                continue

            try:
                config.handler(event)
            except Exception:
                logging.exception(
                    "[ListenerManagerMouse] "
                    f"Handler '{config.name}' failed:\n"
                    f"{traceback.format_exc()}"
                )

    def start(self) -> None:
        self._listener.start()

    def stop(self) -> None:
        self._listener.stop()