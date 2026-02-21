# 📘 README.md

---

# Modular Shortcut Engine

A dynamic, event-driven shortcut engine designed for real applications —
not just simple key bindings.

This engine detects complex keyboard and mouse gestures, applies configurable policies (cooldown, rate limit, spam control), and publishes clean callback signals.
You decide what to do with them.

---

# 🚀 Why This Engine Exists

Most shortcut systems are:

- Hardcoded
- UI-coupled
- Not extensible
- Difficult to test
- Limited to simple key combinations

This engine is different.

It separates:

1. **Detection**
2. **Spam filtering & policy**
3. **Execution logic**
4. **Application decision-making**

So your program doesn’t deal with noisy OS input anymore.

It simply receives:

> "This shortcut was detected."

And then you decide what to do.

---

# 🧠 Philosophy

The engine is designed around one principle:

> Input detection should not decide application behavior.

The engine:

- Detects gestures
- Applies anti-spam logic
- Publishes callback keys

Your application:

- Decides how to execute
- Chooses thread model
- Controls priority
- Integrates with UI or backend
- Injects dependencies dynamically

This makes the engine:

- UI-safe
- Backend-safe
- Game-loop-safe
- Async-friendly
- Testable

---

# 🏗 Architecture Overview

```
OS Input
   ↓
Listener (Adapter Layer)
   ↓
Pipeline (Gesture Detection)
   ↓
Worker
   ↓
PolicyEngine (Cooldown / Rate Limit)
   ↓
ActionBus (Publish)
   ↓
Your Application Logic
```

The engine never executes your logic directly.

It publishes callback keys.

---

# ⚙️ What It Can Do

✔ Keyboard sequences
✔ Mouse gesture detection
✔ Combined keyboard + mouse triggers
✔ Cooldown per callback
✔ Rate limit per callback
✔ Dynamic JSON configuration
✔ Dependency injection for actions
✔ Plugin-style logic/action mapping
✔ Event-driven (no polling loops required)

---

# 🧩 Example Use Case

You define in config:

```json
[
  {
    "keyboard": { "conditions": ["esc"] },
    "callback": "exit"
  }
]
```

When ESC is detected:

- Detection layer confirms match
- Policy layer verifies cooldown
- Worker publishes `"exit"`
- Your app decides what to do

Your app might:

- Close UI
- Shutdown engine
- Save state
- Ignore it

Engine doesn’t care.

---

# 🔌 Integration Example

```python
engine = ShortcutEngine(config, action_bus.publish)

while running:
    for cb_key in action_bus.drain():
        orchestrator.execute_callback(cb_key)
```

You control when and how callbacks execute.

Need UI main thread?
Execute there.

Need background thread?
Execute there.

Need prioritization?
Implement it.

Engine stays clean.

---

# 🧠 Why There Is No Forced Main Loop

Some libraries force execution immediately when a shortcut is detected.

This engine does not.

Why?

Because real applications need control:

- UI frameworks require main-thread execution
- Games use custom loops
- Async apps use event loops
- Backend services may batch events

So the engine publishes signals.
You decide scheduling.

---

# 🧪 Testing Friendly

The engine does not depend on real OS time.

You can inject time providers and simulate events.

No global state.
No hidden threads controlling behavior.

Fully testable.

---

# 🔌 Adapter Layer

The core engine is OS-agnostic.

An official `pynput` adapter is provided for convenience.

It:

- Normalizes noisy OS input
- Fixes negative mouse edge values
- Normalizes key combinations
- Prevents duplicate ctrl+key artifacts

You can write your own adapter if needed.

The only requirement:

Produce normalized `EventData`.

---

# 🎯 Designed For

- Desktop apps
- Automation tools
- Overlay systems
- Games
- Background services
- Experimental UI systems
- Modular plugin-based apps

---

# 🧠 Advanced Design Feature

Each callback maps to:

- Logic class
- Action class
- Dependency injection container

Meaning even core behaviors (like exit) are injectable.

The engine itself can be controlled by shortcuts.

---

# ⚡ Performance

- Fully event-driven
- No polling
- Minimal latency (<10ms typical)
- Multi-thread friendly
- No heavy locking

---

# 🧩 Default Behavior Is Simple

Although highly dynamic internally, it can be used in a minimal setup:

```python
engine = ShortcutEngine(config, publish)
engine.start()
```

You don’t need to use advanced features unless you want to.

---

# 💡 What This Engine Solves

It removes:

- OS noise
- Repeated trigger handling
- Cooldown boilerplate
- State tracking for spam prevention
- Shortcut decision entanglement

So your code becomes:

> "When this shortcut happens, do X."

Not:

> "Check time… check state… ignore duplicates… handle spam…"

---

# 📌 Final Thought

This engine is not just a shortcut handler.

It is an input runtime layer.

Invisible when working.
Powerful when needed.
Flexible by design.
