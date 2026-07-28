# Modular Gesture & Shortcut Detection Engine

A time-aware, event-driven gesture detection engine that turns  
keyboard input and mouse movement into structured signals —  
without coupling detection to execution.

---

## 🚀 What Makes It Different

Unlike traditional shortcut libraries, this engine:

- Treats **mouse movement as a first-class signal** (e.g. `"move up 800px"`)
- Uses a **time-aware state machine** for gesture detection
- Filters OS noise and small jitter automatically
- Separates **detection** from **execution**
- Has a fully **OS-agnostic core**
- Uses a deterministic, single-worker event pipeline

It does not execute your logic.

It publishes clean callback signals.

You control what happens next.

---

## 🧠 Mental Model

```
OS Input
   ↓
Adapter (normalization)
   ↓
Gesture State Machine
   ↓
Policy Engine (cooldown / rate limit)
   ↓
Callback Publish
   ↓
Your Application
```

The core engine contains **no OS-specific code**.  
Only the adapter layer interacts with the operating system.

---

## ⚡ Quick Example

### Minimal ESC trigger

```python
config = [
    {
        "keyboard": {"conditions": ["esc"]},
        "mouse": {"conditions": []},
        "policy": {"cooldown_seconds": 1.0},
        "callback": "exit",
    }
]
```

---

### Mouse Gesture Example

Trigger when user moves mouse **up at least 100px within 4 seconds**:

```python
config = [
    {
        "keyboard": {"conditions": []},
        "mouse": {"conditions": [{"axis": "y", "trend": "up", "min_delta": 100}]},
        "policy": {"cooldown_seconds": 2.0},
        "callback": "mouse_up_100",
    }
]
```

---

### Hybrid Trigger Example

CTRL + move mouse DOWN 20px (order doesn't matter):

```python
{
    "keyboard": {"conditions": ["ctrl"]},
    "mouse": {"conditions": [{"axis": "y", "trend": "down", "min_delta": 20}]},
    "policy": {"cooldown_seconds": 2.0},
    "callback": "ctrl_plus_mouse_down_20",
}
```

---

## 🧠 Gesture Detection Model

- Sequential state machine
- Time-window constrained (default: 4 seconds)
- Perceptual delta accumulation
- Direction-aware path segmentation
- Opposite significant movement breaks the path
- Extremely slow movement does not trigger gestures

The engine evaluates **movement over time**, not just raw displacement.

---

## 🎯 Design Principles

- Detection ≠ Execution
- Core ≠ OS
- Policy ≠ Gesture Logic
- Application owns scheduling

No forced main loop.
No automatic execution.
No hidden threads controlling your logic.

---

## 🧪 Testing Friendly

- Injected time source
- No global state
- Deterministic processing order
- Blocking queue worker (no polling)

Fully unit-testable without real OS input.

---

## 🏗 Architecture Characteristics

- Event-driven
- Single worker (ordered processing)
- No polling loops
- Scales to hundreds of shortcuts
- Latency typically imperceptible in real-world usage

---

## 🧵 Concurrency Model

- Adapter listeners run in separate threads (managed by the adapter implementation)
- Events are pushed into a blocking queue
- A single worker thread processes events sequentially
- Processing order is deterministic
- The engine does **not** execute your callbacks inside its worker thread

You remain in full control of execution scheduling.

---

## 🔌 Adapter Layer

The official adapter uses `pynput`, but the core engine is independent.

You may implement your own adapter for any platform.

The only requirement:

Produce normalized `KeyboardEvent` and `MouseEvent` objects.

---

## 🎯 When To Use This

- You need mouse gesture detection
- You need full control over execution timing
- You build modular or plugin-based systems
- You want testable input logic

---

## 🚫 When Not To Use This

- You only need simple hotkeys
- You want automatic callback execution
- You prefer tightly UI-bound shortcuts

---

## 📚 Documentation

Detailed design documentation is available in the `docs/` directory:

- Architecture
- Gesture model
- Policy engine
- Performance notes
- Design decisions

---

## 📌 Final Thought

This is not just a shortcut handler.

It is a lightweight input runtime layer.

Invisible when working.
Precise when needed.
Modular by design.
