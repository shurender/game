# Assets Directory (`assets/`)

The `assets` directory stores all static multimedia resources utilized by the Risu engine, including audio tracks, sound effects, typography fonts, UI icons, tilesets, and creature sprites.

---

## Directory Hierarchy

```
assets/
├── audio/
│   └── bgm/            # Area background music streams (.ogg / .mp3)
├── fonts/              # TrueType typography font files (.ttf)
├── images/
│   ├── creatures/      # Front and back battle sprites for creatures
│   ├── icons/          # UI badges, elemental type icons, and status markers
│   ├── sprites/        # Overworld character and NPC sprites
│   ├── spritesheets/   # Packed texture sheets for world props and objects
│   └── tiles/          # Map environment tilesets (grass, paths, water, interiors)
├── music/              # Title screen and cinematic audio tracks
└── sounds/
    └── sfx/            # Pre-recorded discrete sound effect audio clips
```

---

## Asset Loading & Fallback System

Assets are managed through `AssetManager` (`game/core/asset_manager.py`):
- **Resilient Fallbacks**: If external fonts or audio clips are not present in this directory, the engine automatically falls back to:
  - Procedural tone synthesis via `numpy` (`AudioManager`).
  - Pygame system fonts (`pygame.font.SysFont`).
  - Procedural tile and sprite generation (`SpriteGenerator`).
- This guarantees the game and automated test suite run reliably in minimal or headless environments without missing asset exceptions.
