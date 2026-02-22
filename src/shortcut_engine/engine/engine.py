from typing import Callable, List

from ..adapters.__pynput__.manage_listeners import ListenerManagerKeyboard, ListenerManagerMouse
from ..input.keyboard.listener import KeyboardListener
from ..input.mouse.listener import MouseListener

from ..config.models import ShortcutConfig, HandlerConfig, MouseConfig, KeyboardConfig
from ..config.parser import parse_shortcut_config
from ..policy.engine import PolicyEngine
from ..engine.worker import ShortcutWorker
from ..models.policy import ActionEvent
from ..input.keyboard.handler import KeyboardApp
from ..input.mouse.handler import MouseApp


class ShortcutEngine:
    """
    High-level orchestration facade.

    Responsibilities:
    - Parse configuration
    - Build all internal components
    - Wire listeners to worker
    - Manage lifecycle (start/stop)
    """

    def __init__(
        self,
        config: List[dict],
        publish_action: Callable[[ActionEvent], None],
    ) -> None:

        # Parse configuration
        self.bundle = parse_shortcut_config(config)

        # Setup params
        self.publish_action = publish_action

        self._setup_components()

    def _setup_components(self) -> None:

        # Create worker
        self._worker = ShortcutWorker(
            ShortcutConfig(
            policy_engine=PolicyEngine(self.bundle.policies),
            publish_action=self.publish_action,
            worker_map=self.bundle.worker_map,
            combined_window_seconds=5
            )
        )

        self.keyboard_app = KeyboardApp(
            KeyboardConfig(
            gestures=self.bundle.keyboard_gestures,
            on_trigger=self._worker.submit_keyboard_triggers,
            _buffer_window_seconds = 1.5
        ))

        # Mouse
        self.mouse_app = MouseApp(
            MouseConfig(
            gestures=self.bundle.mouse_gestures,
            on_trigger=self._worker.submit_mouse_triggers,
            _buffer_window_seconds = 4.0,
            min_delta=10.0,
            _min_samples=8,
            rate=2))

        # Generate Listener Threadings Objects And Setup handlers
        self._keyboard_listener = ListenerManagerKeyboard(KeyboardListener)

        self._keyboard_listener.register(
            HandlerConfig(
                name="keyboard_1",
                handler=self.keyboard_app._handle_event, # type: ignore
                requires_copy=True))

        self._mouse_listener = ListenerManagerMouse(MouseListener)

        self._mouse_listener.register(
            HandlerConfig(
                name="mouse_1",
                handler=self.mouse_app._handle_event, # type: ignore
                requires_copy=True))

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def start(self) -> None:
        """Start engine and all internal threads."""

        self._worker.start()
        self._keyboard_listener.start()
        self._mouse_listener.start()

    def stop(self) -> None:
        """Stop engine safely."""

        self._keyboard_listener.stop()
        self._mouse_listener.stop()
        self._worker.stop()
