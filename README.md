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

## Save Location

Saved games and settings are stored locally in the `saves/` folder inside the project directory:
- `saves/save_0.json` (Autosave)
- `saves/save_1.json` (Manual Save)
- `saves/settings.json` (User Preferences)

## Packaging (Standalone Desktop App)

You can package the game as a standalone executable using PyInstaller. Make sure `pyinstaller` is installed (`pip install pyinstaller`).

```bash
# Generate the standalone executable
pyinstaller --noconfirm --onedir --windowed --name "Risu" --add-data "data;data" --add-data "assets;assets" main.py
```
The executable will be generated inside the `dist/Risu/` folder.

## Troubleshooting

- **Missing fonts or assets**: The game uses procedurally generated assets (images, sounds, and standard fonts) as placeholders if final assets are missing. Missing visual assets shouldn't crash the game.
- **Audio stuttering**: You can disable audio from the Settings menu if you encounter driver issues.
- **Save file corruption**: If the game fails to load a save, check `saves/save_1.json`. The game is resilient to minor data loss, but you can safely delete the file to start a fresh game.

## Credits

- Developed by Risu Development Team.
- Built with [Pygame-CE](https://pyga.me/).

## Tech Stack

- Python 3.10+
- Pygame-CE — rendering, input, audio
- NumPy — audio synthesis
- pytest — testing
