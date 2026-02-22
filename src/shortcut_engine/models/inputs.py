from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class KeyboardEvent:
    key: str
    press: bool

@dataclass(frozen=True, slots=True, kw_only=True)
class MouseEvent:
    x: int
    y: int
    position: Optional[str] = None
    press: Optional[bool] = None
