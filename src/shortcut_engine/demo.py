def main():
    import logging
    import time
    from shortcut_engine import ShortcutEngine, ActionEvent

    logging.basicConfig(level=logging.INFO)

    # -------------------------------------------------
    # Shared policy (readable & reusable)
    # -------------------------------------------------
    DEFAULT_POLICY = {
        "cooldown_seconds": 1.0,
        "max_triggers": 1,
        "rate_window_seconds": 5.0
    }

    # -------------------------------------------------
    # Demo configuration
    # -------------------------------------------------
    config = [

        # 1. Keyboard only
        {
            "keyboard": {"conditions": ["esc"]},
            "mouse": {"conditions": []},
            "policy": DEFAULT_POLICY,
            "callback": "exit"
        },

        # 2. Mouse only
        {
            "keyboard": {"conditions": []},
            "mouse": {
                "conditions": [
                    {"axis": "y", "trend": "up", "min_delta": 100},
                    {"axis": "x", "trend": "left", "min_delta": 400},
                ]
            },
            "policy": {
                **DEFAULT_POLICY,
                "cooldown_seconds": 2.0
            },
            "callback": "mouse_up_100_then_left_400"
        },

        # 3. Combined mouse + keyboard
        {
            "keyboard": {"conditions": ["ctrl"]},
            "mouse": {
                "conditions": [
                    {"axis": "y", "trend": "down", "min_delta": 20}
                ]
            },
            "policy": {
                **DEFAULT_POLICY,
                "cooldown_seconds": 2.0
            },
            "callback": "ctrl_plus_mouse_down_20"
        },
    ]


    # -------------------------------------------------
    # Event handler
    # -------------------------------------------------
    def handle_event(event: ActionEvent):
        logging.info(f"🔥 Triggered → {event.callback}")

        if event.callback == "exit":
            global running
            running = False

    # -------------------------------------------------
    # Startup Info (Very Important)
    # -------------------------------------------------
    print("\nShortcut Engine Demo")
    print("-" * 30)
    print("1. Press ESC → exit")
    print("2. Move mouse UP 100px then LEFT 400px → trigger #2")
    print("3. Hold CTRL and move mouse DOWN 20px → trigger #3")
    print("-" * 30)
    print("Perform gestures now...\n")


    engine = ShortcutEngine(config, handle_event)

    running = True
    engine.start()

    while running:
        time.sleep(0.01)

    print("\nEngine stopped.")