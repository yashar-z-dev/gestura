import json
import logging
import time
from pathlib import Path
from typing import Any

# API
from gestura import ActionEvent, GesturaEngine


class main:
    def __init__(self):
        self.running = False

        # _setup_engine
        self._GesturaEngine = GesturaEngine(self._load_config(), self.pump_worker_events)

    def app_state(self, state: bool):
        self.running = state

    def _load_config(self) -> list[dict[str, Any]]:
        BASE_DIR = Path(__file__).resolve().parent
        json_path = BASE_DIR / "sample_config.json"

        with open(json_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config

    def pump_worker_events(self, action_event: ActionEvent):
        logging.info(action_event)  # noqa: LOG015
        if action_event.callback == "exit":
            self.running = False

    def _loop(self):
        # Keep Alive main thread
        while self.running:
            time.sleep(0.01)

    def start(self):
        logging.info("Engine is Started...")  # noqa: LOG015
        self.app_state(True)
        self._GesturaEngine.start()
        self._loop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _main = main()
    _main.start()
