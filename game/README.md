# Game Package (`game/`)

The `game` package constitutes the core runtime implementation of the Risu engine, built in Python using `pygame-ce`. It implements a complete turn-based creature-collecting RPG architecture based on a stack-based finite state machine, pure domain models, and decoupled presentation systems.

---

## Architecture Overview

```
game/
├── core/         # Engine lifecycle, display setup, input polling, saving & settings
├── states/       # Stack-based game states (World, Battle, Dialogue, Pause, etc.)
├── world/        # Overworld maps, tile layering, collision, camera, NPCs, warps
├── battle/       # Turn-based battle engine, combat formulas, captures, and AI
├── creatures/    # Species definitions, stats, moves, leveling, and evolution
├── player/       # Grid movement, active party management, PC storage, wallet
├── inventory/    # Bag management, item factories, healing/capture item usage
├── quests/       # Event-driven quest tracking, objectives, and progression
├── rendering/    # Procedural sprites, character animations, screen effects
├── audio/        # Procedural tone synthesis, SFX playback, and BGM streaming
├── ui/           # Menus, dialogue boxes, typewriter text, and HUD elements
└── utils/        # Generic math, file loaders, and formatting utilities
```

---

## Subsystem Responsibilities

| Subsystem | Primary Responsibility | Key Classes / Singletons |
| :--- | :--- | :--- |
| **`core/`** | Manages the main Pygame loop, delta timing, display scaling, and persistence. | `Game`, `SaveManager`, `SettingsManager`, `InputHandler` |
| **`states/`** | Dictates active control flow and modal overlays via the state stack. | `StateMachine`, `WorldState`, `BattleState`, `DialogueState` |
| **`world/`** | Handles overworld grid navigation, tile collision, camera centering, and entity interaction. | `World`, `Map`, `CollisionManager`, `Camera`, `NPC`, `Trainer` |
| **`battle/`** | Resolves combat turns, damage calculation, wild creature encounters, and ball captures. | `Battle`, `BattleEngine`, `BattleAI`, `calculate_capture` |
| **`creatures/`** | Manages creature instances, elemental types, stat growth, learnsets, and evolution. | `Creature`, `CreatureFactory`, `Species`, `Move`, `Progression` |
| **`player/`** | Controls player grid positioning, party roster, boxed storage, and coin balances. | `Player`, `PartyManager`, `Wallet` |
| **`inventory/`** | Stores items, handles inventory capacity, item effects, and battle consumable logic. | `Inventory`, `Item`, `ItemFactory` |
| **`quests/`** | Dispatches events (talk NPC, defeat trainer/creature) to update quest states. | `QuestManager`, `Quest`, `Objective` |
| **`rendering/`** | Slices and renders character spritesheets, camera offsets, and battle particle effects. | `SpriteGenerator`, `CaptureAnimation`, `CreatureSprite` |
| **`audio/`** | Synthesizes retro sound effects on the fly and streams background music. | `AudioManager`, `MusicManager` |
| **`ui/`** | Renders dialog boxes, HP meters, selection menus, and text outline styling. | `DialogueBox`, `Menu`, `draw_hp_bar`, `render_text_outlined` |

---

## Execution Flow

1. **Entry Point**: `game/main.py` launches `Game()` from `game/core/game.py`.
2. **Display & Assets**: `Game.__init__` configures display mode (`pygame.SCALED | pygame.RESIZABLE`), loads fonts/assets, and initializes the `StateMachine`.
3. **Initial State**: `MainMenuState` is pushed onto the stack. Selecting "New Game" pushes `WorldState` and initializes quest `main_01`.
4. **Game Loop**:
   - `handle_events`: Dispatched to `state_machine.handle_event()`.
   - `update(dt)`: Topmost state on the stack executes logical updates (`state_machine.update()`).
   - `render()`: States render bottom-to-top onto a double-buffered surface (`state_machine.render()`).
