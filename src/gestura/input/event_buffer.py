from __future__ import annotations

from time import monotonic
from collections import deque
from typing import Any, Callable


class EventBuffer:
    """
    Thread-friendly sliding window buffer.

    Producer threads only append to the staging queue.
    The runtime thread periodically drains staged events into the
    sliding window buffer, avoiding iteration/mutation conflicts.
    """

    def __init__(
        self,
        window: float,
        max_event_rate_per_sec: int = 3000,
        func_now: Callable[[], float] = monotonic,
    ) -> None:
        self.window = window
        self.func_now = func_now

        # Multiple producers append here.
        # maxlen prevents unbounded memory growth if the runtime stalls.
        self._pre_buffer: deque[Any] = deque(maxlen=int(max_event_rate_per_sec * window))

        # Only the runtime thread mutates this buffer.
        self._buffer: deque[Any] = deque()

    def _drain(self) -> None:
        """Move staged events into the sliding window buffer."""
        pre = self._pre_buffer
        buf = self._buffer

        while pre:
            buf.append(pre.popleft())

    def _prune(self, now: float) -> None:
        """Remove events outside the configured time window."""
        cutoff = now - self.window
        buf = self._buffer

        while buf and buf[0][0] < cutoff:
            buf.popleft()

    def add(self, event: Any) -> None:
        """
        Fast producer path.

        Events are first staged in a bounded queue.
        This keeps producer threads independent from the runtime thread.
        """
        self._pre_buffer.append((self.func_now(), event))

    def snapshot(self) -> list[Any]:
        """Return a snapshot of the current sliding window."""
        self._drain()

        now = self.func_now()
        self._prune(now)

        return [event for _, event in self._buffer]

    def snapshot_with_time(self) -> list[tuple[float, Any]]:
        self._drain()

        now = self.func_now()
        self._prune(now)

        return list(self._buffer)

    def clear(self) -> None:
        """Remove all staged and buffered events."""
        self._pre_buffer.clear()
        self._buffer.clear()

    def __len__(self) -> int:
        self._drain()

        now = self.func_now()
        self._prune(now)

        return len(self._buffer)
