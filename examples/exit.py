# 85/100

import logging
from ..adapters.models import LogicResult


class Logic_Exit:
    def __init__(self):
        pass

    def execute(self) -> LogicResult:
        return LogicResult(ui_message="exit with ui toggle.", payload="exit")


class Action_Exit:
    def __init__(
        self,
        _ShortcutEngine,
        app_state):

        self._ShortcutEngine = _ShortcutEngine
        self.app_state = app_state

    def execute(self, payload) -> None:
        logging.info("Engine is EXIT.")

        self._ShortcutEngine.stop()
        self.app_state(False)