# Risu

**A Creature Collecting Adventure** — an original 2D RPG built with Python and Pygame-CE.

## Setup

```bash
# Create a virtual environment (optional but recommended)
python -m venv env
# Windows
env\Scripts\activate
# macOS/Linux
source env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Controls

| Key | Action |
|---|---|
| Arrow keys / WASD | Move / Navigate menus |
| Enter / Z | Confirm |
| Escape / X | Cancel / Back |
| Tab | Open menu |
| P | Pause |

## Project Structure

```
risu/
├── main.py              # Entry point
├── config.py            # Game constants and paths
├── requirements.txt     # Python dependencies
│
├── game/                # Game source code
│   ├── core/            # Engine — Game loop, state machine, input, assets
│   ├── states/          # Game states — menu, world, battle, etc.
│   ├── rendering/       # Drawing helpers and visual effects
│   ├── ui/              # Reusable UI components (text, menus)
│   ├── audio/           # Audio playback and tone synthesis
│   └── utils/           # Shared utilities (lerp, timers, etc.)
│
├── data/                # JSON data files (creatures, maps, items, ...)
├── assets/              # Asset directories (images, sounds, fonts)
└── tests/               # Unit tests (pytest)
```

## Architecture

- **State machine** drives the game flow (main menu → world → battle → …)
- **Data-driven** — creatures, maps, items, and dialogue are defined in JSON
- **Modular** — game logic, rendering, and data are kept separate
- **Procedural art & audio** — all visuals and sounds are generated at runtime

## Tech Stack

- Python 3.10+
- [Pygame-CE](https://pyga.me/) — rendering, input, audio
- NumPy — audio synthesis
- pytest — testing
