# 100/100
"""
TODO: 
__all__ = (
    __EVENTS__,
    EventData_keyboard,
    MouseButtonName, is_valid_button,
    EventData_click, EventData_move
"""

from typing import Optional, Literal, Union, Annotated, TypeGuard
from dataclasses import dataclass
from pydantic import Field


# ===== EventData Models =====
@dataclass(frozen=True, slots=True)
class EventData_keyboard:
    """
    Args:
        press: True if press else False
        key: All key in keyboard(ENG, another language not support all character)
        modifiers: active modifiers when key use. (e.g. key="h", modifiers=["shift"] => "H")
        id:   Primary key (sortable)
        time: Capture time(Optianl) (sortable)

    NOTE: support another language good, but change language need to restart program.

    TODO: write language convertor for another language.
    """

    key: str
    press: bool
    id:   Optional[int]   = None
    time: Optional[float] = None
    type: Literal["keyboard"] = "keyboard"


MouseButtonName = Literal["left", "right", "middle"]

def is_valid_button(name: str) -> TypeGuard[MouseButtonName]:
    return name in {"left", "right", "middle"}

@dataclass(frozen=True, slots=True)
class EventData_click:
    """
    Args:
        press: True if press else False
        position: click action name position
        x: Mouse position on the X axis on the monitor
        y: Mouse position on the Y axis on the monitor
        screenshots: Screenshot of the current mouse position for use in machine vision
    """

    x: int
    y: int
    position: MouseButtonName
    press: bool
    id:   Optional[int]   = None
    time: Optional[float] = None
    type: Literal["click"] = "click"


@dataclass(frozen=True, slots=True)
class EventData_move:
    """
    Args:
        x: Mouse position on the X axis on the monitor
        y: Mouse position on the Y axis on the monitor
    """

    x: int
    y: int
    id:   Optional[int]   = None
    time: Optional[float] = None
    type: Literal["move"] = "move"


# ===== Support Models =====
__EVENTS__ = Annotated[
    Union[EventData_keyboard, EventData_click, EventData_move],
    Field(discriminator="axis"),
]
