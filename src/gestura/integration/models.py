from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar, Any

# ==========================================================
# Type Variables
# ==========================================================

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)


# ==========================================================
# Logic Result
# ==========================================================

@dataclass(frozen=True, slots=True)
class LogicResult(Generic[T_co]):
    """
    Result produced by a Logic.
    """

    ui_message: str
    payload: T_co


# ==========================================================
# Protocols
# ==========================================================

class LogicProtocol(Protocol[T_co]):
    """
    Pure computation.
    """

    def execute(self) -> LogicResult[T_co]:
        ...


class ActionProtocol(Protocol[T_contra]):
    """
    Performs side-effects.
    """

    def execute(self, payload: T_contra) -> None:
        ...


# ==========================================================
# Manifest
# ==========================================================

@dataclass(frozen=True, slots=True)
class PluginManifest:
    """
    Immutable description of a plugin.

    Instances should be created only through create_manifest().
    """

    logic: type[LogicProtocol[Any]]
    action: type[ActionProtocol[Any]]

    status: bool
    notification: bool


# ==========================================================
# Factory
# ==========================================================

def create_manifest(
    *,
    logic: type[LogicProtocol[T]],
    action: type[ActionProtocol[T]],
    status: bool = True,
    notification: bool = True,
) -> PluginManifest:
    """
    Creates a type-safe PluginManifest.

    The type checker guarantees that Logic and Action
    agree on the payload type.
    """

    return PluginManifest(
        logic=logic,
        action=action,
        status=status,
        notification=notification,
    )
