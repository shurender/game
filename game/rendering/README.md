# Rendering & Animation Subsystem (`game/rendering/`)

The `rendering` package contains visual systems, character sprite extraction, procedural textures, battle visual effects, and particle animations.

---

## File Manifest

| File | Purpose |
| :--- | :--- |
| **`sprite_generator.py`** | `SpriteGenerator`. Slices and caches the 8-frame IDLE and RUN spritesheets for the Main Character (`characters/MC/Sprites/`), generates distinct procedural NPC sprites, and builds procedural tile textures. |
| **`animation.py`** | Visual animation controllers: `CaptureAnimation` (pokéball arc, shrink, wobbles, success burst), `HitFlash` (white flash on hit), `CreatureEntranceAnim`, `CreatureFaintAnim`, `DamageNumberAnim`, and `AnimationLayer`. |
| **`creature_sprite.py`** | `CreatureSprite`. Renders combatants in battle with idle breathing offsets, HP meters, status tags, and attack lunges. |
| **`particle.py`** | Particle emitters for weather, battle impacts, capture success bursts, and title screen ambient floating motes. |
| **`spritesheet.py`** | Utility for loading grid-aligned spritesheets and slicing rectangular frames. |

---

## Main Character (MC) Rendering Pipeline

1. **Source Assets**: Loaded from `characters/MC/Sprites/{IDLE,RUN}/{state}_{direction}.png`.
2. **Slicing & Alignment**:
   - Each sheet is 768×80 containing 8 frames (96×80 per frame).
   - The character is centered and cropped to a crisp 32×40 Surface (`pygame.Rect(i * 96 + 32, 22, 32, 40)`).
3. **Overworld Anchor**:
   - In `WorldState.render()`, the sprite is blitted at `(screen_x, screen_y - 8)` so its feet anchor cleanly at `y = 28` of the 32px ground tile.
4. **Animation Rates**:
   - **IDLE**: 8 frames cycling at 6 FPS for smooth idle breathing.
   - **RUN**: 8 frames cycling at 10 FPS matching overworld tile movement.

---

## Battle Animation Layer (`AnimationLayer`)

Combat visuals are decoupled from battle math:
- `BattleEngine` calculates turns and returns pure data (`ActionEvent` list).
- `AnimationLayer` consumes these events to queue screen shakes, damage numbers, health bar slides, and capture ball wobbles without affecting combat logic.
