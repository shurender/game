# Main Character Assets (`characters/MC/`)

This directory contains the visual pixel art sprite assets for the game's protagonist / Main Character (MC).

---

## File Manifest & Specifications

| Directory / File | Dimensions | Frame Layout | Description |
| :--- | :--- | :--- | :--- |
| **`Preview.gif`** | 632×500 | Multi-frame GIF | Animated preview showcasing all character movement and attack cycles. |
| **`License.txt`** | Text | N/A | Asset license details. Permitted for commercial and personal game usage. |
| **`Sprites/IDLE/`** | 768×80 | 8 frames (96×80 each) | 4 directional strips (`idle_down.png`, `idle_up.png`, `idle_left.png`, `idle_right.png`). |
| **`Sprites/RUN/`** | 768×80 | 8 frames (96×80 each) | 4 directional strips (`run_down.png`, `run_up.png`, `run_left.png`, `run_right.png`). |
| **`Sprites/ATTACK 1/`**| 768×80 | 8 frames (96×80 each) | Primary weapon swing / action strike frames in 4 directions. |
| **`Sprites/ATTACK 2/`**| 768×80 | 8 frames (96×80 each) | Secondary weapon swing / thrust strike frames in 4 directions. |

---

## Frame Slicing & Anchoring

- **Canvas Size**: 768×80 px per image strip.
- **Individual Frame**: Width = 96 px, Height = 80 px (`768 / 8 = 96`).
- **Character Bounding Box**: The character body occupies an area of ~19×34 pixels centered around $X = 48$ with feet touching at $Y = 58$.
- **Engine Crop**: `SpriteGenerator` extracts a `32×40` sub-surface at `pygame.Rect(i * 96 + 32, 22, 32, 40)`.
- **Anchor Offset**: Rendered in `WorldState` with an anchor offset of `-(surface_height - 32) = -8 px`. This aligns the character's feet with the bottom of the 32×32 ground tile while giving natural 3/4 perspective vertical depth.
