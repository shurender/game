# Characters Directory (`characters/`)

This directory houses art assets, spritesheets, and animation frames for character entities in the game, including the Main Character (MC) and future party or rival character packs.

---

## Directory Structure

```
characters/
└── MC/                     # Main Character (player avatar) assets
    ├── License.txt         # Asset usage license
    ├── Preview.gif         # Full animated demonstration preview
    └── Sprites/            # Sliced PNG animation strips
        ├── IDLE/           # 8-frame standing / breathing animation strips
        ├── RUN/            # 8-frame walking / running animation strips
        ├── ATTACK 1/       # 8-frame primary action / attack strips
        └── ATTACK 2/       # 8-frame secondary action / attack strips
```

---

## Engine Integration

- The **Main Character (MC)** in `characters/MC/Sprites/` is loaded at game startup by `SpriteGenerator` in `game/rendering/sprite_generator.py`.
- **Active Animations**:
  - `IDLE` (4 directions: `down`, `up`, `left`, `right`): 8 frames cycling at 6 FPS when the player is stationary.
  - `RUN` (4 directions: `down`, `up`, `left`, `right`): 8 frames cycling at 10 FPS when the player is moving across tiles.
- **Unused Frames**: Combat actions (`ATTACK 1`, `ATTACK 2`) are reserved for potential future action modes, cutscenes, or overworld field moves (e.g. chopping trees or breaking boulders).
