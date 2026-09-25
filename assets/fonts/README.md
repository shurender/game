# Typography Fonts (`assets/fonts/`)

This directory contains TrueType (`.ttf`) and OpenType (`.otf`) pixel and bitmap typography fonts used for in-game UI, dialogues, and menus.

---

## Font Specifications

- **Recommended Style**: Clean monospaced or proportional pixel fonts tailored for 8px, 16px, 24px, and 32px point sizes without subpixel anti-aliasing blur.
- **Engine Lookup**: `AssetManager.get_font(size)` looks for `.ttf` files in this folder.
- **Graceful Fallback**: If no custom `.ttf` font is found, the engine automatically selects the system's clean sans-serif/monospace default using `pygame.font.SysFont(None, size)`.
