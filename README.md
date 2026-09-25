# Risu

**A Creature-Collecting Adventure RPG** built in Python with [Pygame-CE](https://pyga.me/).

Explore the region of Oakhaven, capture and train distinct elemental creatures, conquer challenging rival trainers, and unravel the mystery of the Rogue Menace across an expansive tile-based overworld.

---

## Quickstart

### Prerequisites
- Python 3.10+
- Virtual environment recommended

### Installation & Launch
```bash
# Clone or navigate to the repository
cd game

# Create and activate virtual environment
python -m venv venv
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Linux / macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

### Running Tests
```bash
pytest
```
*Current test suite: **219 passing tests** across battle math, captures, state machines, quests, and movement.*

---

## Controls

| Key | Primary Action | Context |
| :--- | :--- | :--- |
| **Arrow Keys / WASD** | Move / Navigate | Overworld movement, menu selection |
| **Enter / Z / Space** | Confirm / Interact | Talk to NPCs, select moves, advance dialogues |
| **Escape / X** | Cancel / Back | Close menus, return to previous state |
| **Tab** | In-game Menu | Opens sliding pause drawer on overworld |
| **F5** | Quick Save | Instantly writes state to save slot 1 |

---

## Project Structure & Subsystem Documentation

Every directory in the codebase includes dedicated technical documentation:

| Directory | Documentation Link | Description |
| :--- | :--- | :--- |
| **`game/`** | [game/README.md](file:///d:/Jk/jkProgramz/game/game/README.md) | High-level package architecture and execution lifecycle. |
| **`game/core/`** | [game/core/README.md](file:///d:/Jk/jkProgramz/game/game/core/README.md) | Engine loop, StateMachine, SaveManager, SettingsManager, InputHandler. |
| **`game/states/`** | [game/states/README.md](file:///d:/Jk/jkProgramz/game/game/states/README.md) | UI and game screens (World, Battle, Dialogue, Pause, Shop, Party, etc.). |
| **`game/battle/`** | [game/battle/README.md](file:///d:/Jk/jkProgramz/game/game/battle/README.md) | Turn-based combat engine, AI, elemental math, status effects, capture. |
| **`game/creatures/`** | [game/creatures/README.md](file:///d:/Jk/jkProgramz/game/game/creatures/README.md) | Creature models, species learnsets, stat growth, evolution formulas. |
| **`game/world/`** | [game/world/README.md](file:///d:/Jk/jkProgramz/game/game/world/README.md) | Tile maps, camera viewport, collision, NPCs, trainers, warps. |
| **`game/player/`** | [game/player/README.md](file:///d:/Jk/jkProgramz/game/game/player/README.md) | Player entity, grid movement, PartyManager (roster & PC box), Wallet. |
| **`game/inventory/`** | [game/inventory/README.md](file:///d:/Jk/jkProgramz/game/game/inventory/README.md) | Bag management, category filtering, healing, and capture items. |
| **`game/quests/`** | [game/quests/README.md](file:///d:/Jk/jkProgramz/game/game/quests/README.md) | Event-driven questline (`main_01`, `main_02`, `main_03`) and rewards. |
| **`game/rendering/`** | [game/rendering/README.md](file:///d:/Jk/jkProgramz/game/game/rendering/README.md) | AnimationLayer, CaptureAnimation, procedural generation, sprite slicing. |
| **`game/audio/`** | [game/audio/README.md](file:///d:/Jk/jkProgramz/game/game/audio/README.md) | Procedural chiptune tone synthesis (`numpy`) and BGM streaming. |
| **`game/ui/`** | [game/ui/README.md](file:///d:/Jk/jkProgramz/game/game/ui/README.md) | Typewriter dialogue boxes, menus, outlined typography, HP meters. |
| **`game/utils/`** | [game/utils/README.md](file:///d:/Jk/jkProgramz/game/game/utils/README.md) | Clamping, linear interpolation, resilient JSON loaders. |
| **`data/`** | [data/README.md](file:///d:/Jk/jkProgramz/game/data/README.md) | JSON database: species, moves, items, maps, dialogues, quests, shops, trainers. |
| **`characters/`** | [characters/README.md](file:///d:/Jk/jkProgramz/game/characters/README.md) | Character asset catalog and protagonist spritesheet specifications. |
| **`characters/MC/`** | [characters/MC/README.md](file:///d:/Jk/jkProgramz/game/characters/MC/README.md) | Main Character 8-frame IDLE and RUN directional animations. |
| **`assets/`** | [assets/README.md](file:///d:/Jk/jkProgramz/game/assets/README.md) | Static audio, fonts, creature sprites, and environmental tiles. |
| **`tests/`** | [tests/README.md](file:///d:/Jk/jkProgramz/game/tests/README.md) | Automated pytest suite catalog and unit testing guidelines. |
| **`saves/`** | [saves/README.md](file:///d:/Jk/jkProgramz/game/saves/README.md) | Persistent save slot format (`save_0.json` - `save_3.json`) and settings. |
| **`story/`** | [story/README.md](file:///d:/Jk/jkProgramz/game/story/README.md) | Story overview, narrative progression, and questline design. |
| **`scratch/`** | [scratch/README.md](file:///d:/Jk/jkProgramz/game/scratch/README.md) | Development scaffold scripts and tooling. |

---

## Packaging

Package as a standalone desktop executable using PyInstaller:
```bash
pyinstaller --noconfirm --onedir --windowed --name "Risu" \
  --add-data "data;data" \
  --add-data "characters;characters" \
  --add-data "assets;assets" \
  main.py
```
The resulting build will be output to `dist/Risu/`.
