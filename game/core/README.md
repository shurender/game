# Core Engine Subsystem (`game/core/`)

The `core` module provides foundational infrastructure for the game engine. It governs the main Pygame loop, delta-time management, input mapping, persistence, display scaling, and the stack-based state machine.

---

## File Manifest

| File | Purpose |
| :--- | :--- |
| **`game.py`** | Main engine controller (`Game` class). Manages game loop, clock, delta time (`dt`), window surfaces, and core subsystems. |
| **`state_machine.py`** | Finite state machine (`StateMachine`). Implements a stack-based architecture where states can be pushed, popped, or replaced. |
| **`input_handler.py`** | Input mapping system (`InputHandler`, `Action` enum). Translates raw `pygame.KEYDOWN` events into semantic game actions (`CONFIRM`, `CANCEL`, `UP`, `DOWN`, etc.). |
| **`save_manager.py`** | Save/load system (`SaveManager`). Serializes player state, world coordinates, party stats, quest progress, and inventory into JSON save files. |
| **`settings_manager.py`** | Configuration manager (`SettingsManager`). Controls window resolution, fullscreen toggles, audio volumes, and saves settings to `saves/settings.json`. |

---

## Key Concepts & Patterns

### 1. The Stack-Based State Machine (`StateMachine`)
The engine uses a stack rather than a single active state:
- **`push(state, params)`**: Pushes a new state (e.g. `PauseMenuState` or `DialogueState`) on top of `WorldState`. The previous state is paused, retaining its visual context.
- **`pop()`**: Removes the top state, resuming the underlying state (`resume()` hook called).
- **`replace(state, params)`**: Replaces the active state cleanly without growing the stack.
- **`render(surface)`**: Renders stacked states from bottom to top, allowing transparent overlays (e.g. dialogue boxes and pause menus over the active overworld).

### 2. High-DPI Scaling & Resizing
- Initialized with `pygame.SCALED | pygame.RESIZABLE`.
- Logical internal resolution is 960×640 (`SCREEN_WIDTH`, `SCREEN_HEIGHT`).
- In `WorldState`, rendering targets an internal `480×320` buffer that is scaled 2× up to `960×640`, ensuring retro pixel art clarity without blurriness.

### 3. Save Game Architecture (`SaveManager`)
Saves are written to `saves/save_{slot}.json`:
- Contains player name, map ID, coordinates `(x, y)`, and facing direction.
- Serializes complete creature party rosters (levels, current HP, moves, stats).
- Serializes `Inventory` quantities and `Wallet` coin balances.
- Stores `QuestManager` states (in-progress, completed objectives) and `WorldProgressManager` story flags.
