# 100/100

from typing import Callable
from dataclasses import dataclass, field

from .keyboard import GestureKeyboard
from .mouse import GestureMouse


@dataclass(slots=True)
class GestureCombine_KM:
    mouse: GestureMouse = field(default_factory=GestureMouse)
    keyboard: GestureKeyboard = field(default_factory=GestureKeyboard)
    callback: Callable[[], None] | str = "Unknown"
