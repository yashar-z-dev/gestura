from typing import Callable

from .pipeline import MouseGesturePipeline
from ...models.event import EventData_click, EventData_move
from ..event_buffer import EventBuffer
from ...config.models import MouseConfig


class MouseApp:
    """
    Event-driven mouse gesture handler.

    Design principles:
    - Time-windowed buffering (via EventBuffer)
    - Lightweight activation guard (min sample count)
    - All gesture recognition delegated to MouseGesturePipeline
    - No motion accumulation state in this layer
    """

    def __init__(self, config: MouseConfig) -> None:

        # External callback to notify when a gesture is triggered
        self._emit_callback: Callable[[list[str]], None] = config.on_trigger

        # Pipeline handles all recognition logic
        self._pipeline = MouseGesturePipeline(
            gesture_definitions=config.gestures, # type "GestureMouseCondition"
            segment_min_delta=config.min_delta
        )

        # Time-sliced event buffer
        self._buffer = EventBuffer(window=config._buffer_window_seconds)

        # Minimum number of samples required before evaluation
        # This is NOT semantic filtering — only to avoid trivial calls.
        self._min_samples: int = config._min_samples # keep small to avoid false negatives

    # ------------------------------------------------------------------ #
    # Event Handling
    # ------------------------------------------------------------------ #

    def _handle_event(self, event: EventData_click | EventData_move) -> None:

        if event.type == "move":
            self._handle_move(event)
        elif event.type == "click":
            self._handle_click(event)

    def _handle_move(self, event: EventData_move) -> None:
        """
        Add move event to buffer and evaluate gestures if sufficient data exists.
        """
        self._buffer.add(event)

        # Lightweight guard — prevents processing extremely small sequences
        if len(self._buffer) >= self._min_samples:
            self._evaluate_gestures()

    def _handle_click(self, event: EventData_click) -> None:
        """
        Click handling is currently not part of gesture recognition.
        Reserved for future extension.
        """

        pass

    # ------------------------------------------------------------------ #
    # Core Processing
    # ------------------------------------------------------------------ #

    def _evaluate_gestures(self):
        """
        Snapshot current buffer and delegate recognition to pipeline.
        """

        snapshot = self._buffer.snapshot()
        callbacks = self._pipeline.process_for_trigger(snapshot)

        self._emit_callback(callbacks)