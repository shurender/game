# Creature Battle Sprites (`assets/images/creatures/`)

This directory contains battle sprites for collectible creatures.

---

## File Naming Convention

For any creature species with ID `{species_id}` (e.g. `florbit`, `barkbug`):
- **Front Sprite (Enemy View)**: `{species_id}_front.png` or `{species_id}.png`
- **Back Sprite (Player View)**: `{species_id}_back.png`

---

## Technical Specifications

- **Format**: PNG with 32-bit RGBA transparency.
- **Resolution**: 64×64 pixels (native) or 128×128 pixels.
- **Palette**: Clean pixel art with limited color ramps to match retro GBA aesthetics.
- **Engine Fallback**: In the absence of an image file, `CreatureSprite` procedurally renders an animated geometric creature placeholder with species colors.
