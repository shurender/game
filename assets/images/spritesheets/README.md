# Spritesheets (`assets/images/spritesheets/`)

This directory is designated for multi-frame spritesheet textures and packed atlas images.

---

## Technical Details

- Sliced at runtime using `SpriteSheet` (`game/rendering/spritesheet.py`).
- Suitable for animated overworld props (fountains, flower sway, ocean waves, doors).
- Supported metadata: Grid dimensions (width, height), margin offsets, and frame counts.
