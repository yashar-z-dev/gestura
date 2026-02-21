# 100/100

from typing import Callable

from ...models.keyboard import GestureKeyboardCondition
from .pipeline import KeyboardGesturePipeline
from ..event_buffer import EventBuffer

from ...models.event import EventData_keyboard
from ...config.models import KeyboardConfig


class KeyboardApp:
    """
    Event-driven keyboard gesture processor.

    Responsibilities:
    - Receive raw keyboard events
    - Maintain a time-windowed buffer of pressed keys
    - Dispatch relevant gestures based on starting key
    - Emit triggered callbacks
    """

    def __init__(self, config: KeyboardConfig) -> None:
        """
        Args:
            config: Keyboard configuration containing gesture definitions and runtime settings.
            on_trigger: Callback executed when a gesture is successfully recognized.
        """

        # External callback to notify when a gesture is triggered
        self._emit_callback: Callable[[list[str]], None] = config.on_trigger

        # Configuration
        self._gesture_definitions: list[GestureKeyboardCondition] = config.gestures
        self._buffer_window_seconds: float = config._buffer_window_seconds  # Time window for gesture detection

        # Time-windowed key buffer
        self._event_buffer = EventBuffer(self._buffer_window_seconds)

        # Gesture pipeline (responsible for matching logic)
        # Internally builds an index by starting key
        self._gesture_pipeline = KeyboardGesturePipeline(
            gestures=self._gesture_definitions
        )

    # ------------------------------------------------------------------
    # Public Event Entry Point
    # ------------------------------------------------------------------

    def _handle_event(self, event: EventData_keyboard) -> None:
        """
        Main entry point for incoming keyboard events.
        Normalizes and routes events to appropriate handlers.
        """

        if event.press:
            self._handle_key_press(event)
        else:
            self._handle_key_release(event)

    # ------------------------------------------------------------------
    # Internal Event Handlers
    # ------------------------------------------------------------------

    def _handle_key_press(self, event: EventData_keyboard) -> None:
        """
        Process key press events.
        Adds key to buffer and evaluates relevant gestures.
        """

        # Store key inside sliding window buffer
        self._event_buffer.add(event)

        # Evaluate only gestures that start with this key
        self._evaluate_gestures(trigger_key=event.key)

    def _handle_key_release(self, event: EventData_keyboard) -> None:
        """
        Process key release events.
        Currently not used in gesture evaluation.
        """

        pass

    # ------------------------------------------------------------------
    # Gesture Evaluation
    # ------------------------------------------------------------------

    def _evaluate_gestures(self, trigger_key: str) -> None:
        """
        Evaluate gestures relevant to the given trigger key.

        NOTE:
        - Snapshot is intentionally preserved to prevent mutation-related
          side effects during evaluation.
        - Pipeline internally uses trigger-key indexing for efficiency.
        """

        # Take snapshot to ensure consistency across multi-stage processing
        current_sequence = self._event_buffer.snapshot()

        # Process only gestures mapped to this starting key
        matched_callbacks = self._gesture_pipeline.process_for_trigger(
            trigger_key=trigger_key,
            event_sequence=current_sequence,
        )

        # Emit callbacks
        self._emit_callback(matched_callbacks)
