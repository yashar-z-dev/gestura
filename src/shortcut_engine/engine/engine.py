from typing import Callable, Any

# Replaceable modules
from ..adapters.__pynput__.manage_listeners import (
    ListenerManagerKeyboard,
    ListenerManagerMouse,
)

from ..input.keyboard.listener import KeyboardListener
from ..input.mouse.listener import MouseListener

from ..adapters.protocols import (
    ListenerKeyboardFactory,
    ListenerMouseFactory,
    ListenerManagerKeyboardFactory,
    ListenerManagerMouseFactory,
)

# Core
from ..config.models import (
    ShortcutConfig,
    MouseConfig,
    KeyboardConfig,
    HandlerKeyboardConfig,
    HandlerMouseConfig,
)

from ..config.parser import parse_shortcut_config
from ..policy.engine import PolicyEngine
from ..engine.worker import ShortcutWorker
from ..models.policy import ActionEvent
from ..input.keyboard.handler import KeyboardApp
from ..input.mouse.handler import MouseApp


class ShortcutEngine:
    """
    High-level orchestration facade.
    Composition root of the engine.
    """

    def __init__(
        self,
        config: list[dict[str, Any]],
        publish_action: Callable[[ActionEvent], None],

        # Listener factories (OS level)
        keyboard_listener_factory: ListenerKeyboardFactory = KeyboardListener,
        mouse_listener_factory: ListenerMouseFactory = MouseListener,

        # Manager factories (threading layer)
        keyboard_manager_factory: ListenerManagerKeyboardFactory = ListenerManagerKeyboard,
        mouse_manager_factory: ListenerManagerMouseFactory = ListenerManagerMouse,
    ) -> None:
        """
        High-level orchestration facade and composition root of the shortcut system.

        This engine:

        - Parses shortcut configuration
        - Builds policy and worker layers
        - Wires keyboard and mouse inputs
        - Dispatches validated actions to the user callback
        - Manages lifecycle of all internal components

        Args:
            config (List[dict]):
                Parsed JSON configuration describing shortcuts, policies,
                and input conditions (keyboard / mouse).

                Typically loaded via:

                    import json
                    config = json.load(open("config.json"))

                The configuration defines:
                    - Gestures Conditions (keyboard & mouse)
                    - Policies
                    - Callback names

            publish_action (Callable[[ActionEvent], None]):
                A user-provided callable that will be invoked when a shortcut
                successfully triggers and passes all policy validation.

                The engine emits:

                    @dataclass(frozen=True, slots=True)
                    class ActionEvent:
                        callback: str
                        triggered_at: float

                `callback` is defined inside the configuration.
                `triggered_at` is a monotonic timestamp of trigger time.

            keyboard_listener_factory (ListenerKeyboardFactory, optional):
                Factory responsible for creating a low-level keyboard listener
                (OS adapter layer).

                Defaults to the built-in implementation.

                Can be replaced to:
                    - Integrate with another backend
                    - Reuse an existing application listener
                    - Provide a mock listener for testing

            mouse_listener_factory (ListenerMouseFactory, optional):
                Same as above, but for mouse input.

            keyboard_manager_factory (ListenerManagerKeyboardFactory, optional):
                Factory responsible for constructing the keyboard listener manager
                (threading / orchestration layer).

                In this version the manager exposes:
                    - start()
                    - stop()
                    - register(...)

                This abstraction is expected to evolve in future versions.

            mouse_manager_factory (ListenerManagerMouseFactory, optional):
                Same as above, but for mouse input.


        Important:
            To avoid running multiple OS listeners simultaneously,
            it is recommended to either:

            - Reuse an existing application-level listener and inject it
            - Or share a single listener instance across systems

            Running multiple independent OS listeners may lead to:
                - Performance overhead
                - Duplicate event streams
                - Platform-specific side effects

        Extensibility:
            All replaceable components follow typed Protocol contracts.
            Custom implementations can be injected without modifying the engine.
        """

        # Parse configuration
        self.bundle = parse_shortcut_config(config)
        self.publish_action = publish_action

        # Build listener managers (DI clean)
        self._keyboard_listener = keyboard_manager_factory(
            keyboard_listener_factory
        )

        self._mouse_listener = mouse_manager_factory(
            mouse_listener_factory
        )

        self._setup_components()
        self._register_handlers()

    # ---------------------------------------------------------
    # Internal Wiring
    # ---------------------------------------------------------

    def _setup_components(self) -> None:

        # Worker
        self._worker = ShortcutWorker(
            ShortcutConfig(
                policy_engine=PolicyEngine(self.bundle.policies),
                publish_action=self.publish_action,
                worker_map=self.bundle.worker_map,
                combined_window_seconds=5,
            )
        )

        # Keyboard
        self.keyboard_app = KeyboardApp(
            KeyboardConfig(
                gestures=self.bundle.keyboard_gestures,
                on_trigger=self._worker.submit_keyboard_triggers,
                BufferWindowSeconds=1.5,
            )
        )

        # Mouse
        self.mouse_app = MouseApp(
            MouseConfig(
                gestures=self.bundle.mouse_gestures,
                on_trigger=self._worker.submit_mouse_triggers,
                BufferWindowSeconds=4.0,
                min_delta=10.0
            )
        )

    def _register_handlers(self):
        # Register handlers
        self._keyboard_listener.register(
            HandlerKeyboardConfig(
                name="keyboard_1",
                handler=self.keyboard_app.HandleEvens,
            )
        )

        self._mouse_listener.register(
            HandlerMouseConfig(
                name="mouse_1",
                handler=self.mouse_app.HandleEvens,
            )
        )

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def start(self) -> None:
        self._worker.start()
        self._keyboard_listener.start()
        self._mouse_listener.start()

    def stop(self) -> None:
        self._keyboard_listener.stop()
        self._mouse_listener.stop()
        self._worker.stop()
