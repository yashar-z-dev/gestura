# 100/100

from typing import Callable
from dataclasses import dataclass, field
import warnings
import time

from ..models.event import __EVENTS__
from ..models.keyboard import GestureKeyboardCondition
from ..models.mouse import GestureMouseCondition
from ..models.protocols import PolicyEngineProtocol
from ..models.policy import ActionEvent
from ..config.parser import WorkerGestureMap


# ===== Models =====
@dataclass(frozen=True, slots=True)
class KeyboardConfig:
    """
    Configuration container for KeyboardAppMain.

    Attributes:
        gestures (list[GestureKeyboardCondition]): # edit(2026-01-27)
            A list of gesture definitions where each gesture is a dictionary
            containing:
                - 'conditions': a list of keys that define the gesture (e.g., ["ctrl", "space"])
                - 'callback': a callable or any value that will be returned when the gesture triggers.
            Example:
                [{"conditions": ["ctrl", "a"], "callback": some_function}]

        logger (Callable[[str], None]):
            A function to handle logging messages. If None, logging is disabled.

        debug (bool):
            Enables debug mode which outputs additional debug information.

        event_buffer_size (int):
            The maximum number of keyboard events to keep in the event buffer.

        stability_check_threshold (int):
            The threshold to decide when events in the buffer are stable enough to be processed.

        allow_stable_events (bool):
            Whether stable events should be processed or ignored.,

        cooldown_size (int):
            Number of previous trigger sets to remember for cooldown filtering

    ===== Usage Example =====:
        config = KeyboardConfig(
            gestures=[
                {"conditions": ["alt", "space", "space"], 
                 "callback": lambda: print("Alt+Space+Space triggered")}
            ],
            logger=print,
            debug=True
        )

        if not config.validate():
            raise ValueError("Invalid keyboard configuration")

        app = KeyboardAppMain(config=config)
    """

    gestures: list[GestureKeyboardCondition] = field(default_factory=list)
    on_trigger: Callable[[list[str]], None] = lambda _: None
    _buffer_window_seconds: float = 1.5

    def __post_init__(self):
        if not self.gestures:
            warnings.warn(
                "KeyboardConfig initialized with empty 'gestures'. "
                "At least one gesture mapping is recommended.",
                UserWarning
            )

    def validate(self) -> bool:
        """
        Validates the configuration.

        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        for gesture in self.gestures:
            if not isinstance(gesture, dict):
                return False
            if "conditions" not in gesture or "callback" not in gesture:
                return False
            if not isinstance(gesture["conditions"], list):
                return False
        return True


@dataclass(frozen=True, slots=True)
class MouseConfig:
    """
    Configuration container for MouseAppMain.

    Attributes:
        gestures (List[Dict[str, Any]]):
            A list of gesture definitions where each gesture is a dictionary
            containing:
                - 'conditions': a list of directional or segment conditions
                - 'callback': a callable or any value that will be returned when the gesture triggers.
            Example:
                [{"conditions": ["up", "right", "down"], "callback": some_function}]

        logger (Optional[Callable[[str], None]]):
            A function to handle logging messages. If None, logging is disabled.

        debug (bool):
            Enables debug mode which outputs additional debug information.

        event_buffer_size (int):
            The maximum number of mouse events to keep in the event buffer.

        stability_check_threshold (int):
            The threshold to decide when events in the buffer are stable enough to be processed.

        allow_stable_events (bool):
            Whether stable events should be processed or ignored.
        
        cooldown_size (int):
            Number of previous trigger sets to remember for cooldown filtering
        
        min_delta (float):
            minimum delta to keep a segment (final filter)

        rate (int):
            move event rate, filtering for save power.
            for maximum power and fast response, rate = 1

    ===== Usage Example =====:
        config = MouseConfig(
            gestures=[
                {"conditions": [
                    {"axis": "y", "trend": "up", "min_delta": 900}
                    {"axis": "y", "trend": "left", "min_delta": 50}
                    ],
                 "callback": lambda: print("Mouse gesture triggered")}
            ],
            logger=print,
            debug=True
        )

        if not config.validate():
            raise ValueError("Invalid mouse configuration")

        app = MouseAppMain(config=config)
    """

    gestures: list[GestureMouseCondition] = field(default_factory=list)
    on_trigger: Callable[[list[str]], None] = lambda _: None
    _buffer_window_seconds: float = 4.0
    min_delta: float = 10.0
    _min_samples: int = 8
    rate: int = 2

    def __post_init__(self):
        if not self.gestures:
            warnings.warn(
                "MouseConfig initialized with empty 'gestures'. "
                "At least one gesture mapping is recommended.",
                UserWarning
            )

    def validate(self) -> bool:
        """
        Validates the configuration.

        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        for gesture in self.gestures:
            if not isinstance(gesture, dict):
                return False
            if "conditions" not in gesture or "callback" not in gesture:
                return False
            if not isinstance(gesture["conditions"], list):
                return False
        return True


@dataclass(frozen=True, slots=True)
class ShortcutConfig:
    policy_engine: PolicyEngineProtocol
    publish_action: Callable[[ActionEvent], None]
    worker_map: WorkerGestureMap
    combined_window_seconds: float = 5.0
    func_now: Callable[[], float] = time.monotonic


@dataclass(slots=True)
class HandlerConfig:
    """
    TODO: use handler: Protocol_KeyboardListener | Protocol_MouseListener

    NOTE: now is type checker error
    """

    name: str
    handler: Callable[[__EVENTS__], None]
    # handler: Protocol_KeyboardListener | Protocol_MouseListener
    requires_copy: bool = True
    enabled: bool = True