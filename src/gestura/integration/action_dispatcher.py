import inspect
import logging

from typing import Any, Optional, TypeVar

from .models import (
    LogicResult,
    PluginManifest,
    LogicProtocol,
    ActionProtocol,
)

_C = TypeVar("_C")


class ActionDispatcher:
    """
    Central registry for callbacks.

    Responsible for:
        - Registering callbacks
        - Instantiating Logic/Action
        - Injecting dependencies
        - Executing callbacks
    """

    def __init__(
        self,
        dependencies: dict[str, object],
    ) -> None:
        self._registry: dict[str, PluginManifest] = {}

        self._dependencies = dependencies

        # Cache constructor parameter names
        self._ctor_cache: dict[type, tuple[str, ...]] = {}

    # ==========================================================
    # Registry
    # ==========================================================

    def register(
        self,
        key: str,
        manifest: PluginManifest,
    ) -> None:
        """
        Register a callback.

        Example:
            dispatcher.register(
                "pause",
                create_manifest(...),
            )
        """
        self._registry[key] = manifest

    def unregister(
        self,
        key: str,
    ) -> None:
        self._registry.pop(key, None)

    def clear(self) -> None:
        self._registry.clear()

    def set_dependencies(
        self,
        dependencies: dict[str, object],
    ) -> None:
        """
        Replace dependency mapping.

        Useful when runtime services are recreated.
        """
        self._dependencies = dependencies

    def get(
        self,
        key: str,
    ) -> Optional[PluginManifest]:
        return self._registry.get(key)

    # ==========================================================
    # Dynamic Instantiation
    # ==========================================================

    def _instantiate(
        self,
        cls: type[_C],
    ) -> _C:

        param_names = self._ctor_cache.get(cls)

        if param_names is None:
            sig = inspect.signature(cls.__init__)
            param_names = tuple(
                p.name
                for p in sig.parameters.values()
                if p.name != "self"
            )
            self._ctor_cache[cls] = param_names

        try:
            args = [
                self._dependencies[name]
                for name in param_names
            ]
        except KeyError as exc:
            raise RuntimeError(
                f"Missing dependency '{exc.args[0]}' "
                f"required by '{cls.__name__}'."
            ) from None

        return cls(*args)

    # ==========================================================
    # Execution
    # ==========================================================

    def execute(
        self,
        key: str,
    ) -> dict[str, str]:
        """
        Execute a callback.
        """

        manifest = self.get(key)

        if manifest is None:
            logging.info("Unknown callback: %s", key)
            return {"warning": "Unknown callback"}

        # Logic
        logic: LogicProtocol[Any] = self._instantiate(manifest.logic)
        result: LogicResult[Any] = logic.execute()

        logging.info(
            "Execute callback '%s' (%s)",
            key,
            result.ui_message,
        )

        # Action
        action: ActionProtocol[Any] = self._instantiate(manifest.action)
        action.execute(result.payload)

        return {
            "ui_message": result.ui_message,
        }
