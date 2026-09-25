# Player Subsystem (`game/player/`)

The `player` package encapsulates the player entity, overworld movement dynamics, creature team management, and currency balances.

---

## File Manifest

| File | Purpose |
| :--- | :--- |
| **`player.py`** | `Player` entity and `Direction` enum (`UP`, `DOWN`, `LEFT`, `RIGHT`). Handles grid coordinate movement with smooth sub-pixel interpolation (`move_speed = 4.0` tiles/sec), animation timers, and 1-tile interaction checks. |
| **`party.py`** | `PartyManager` singleton (aliased as `Party`). Manages the player's 6-slot active creature roster and PC creature storage box. Provides party helper utilities (`get_first_available()`, `swap_creatures()`, `has_usable_creatures()`). |
| **`wallet.py`** | `Wallet` singleton. Single source of truth for the player's coin balance, with serialization support for game saves. |

---

## Movement & Tile Alignment

- The player's logical position is discrete integers `(x, y)` in tile space.
- Rendering uses float coordinates `(pixel_x, pixel_y)` that smoothly interpolate towards the target tile:
```python
move_amt = self.move_speed * TILE_SIZE * dt
```
- Movement cannot be interrupted mid-tile, guaranteeing clean grid-based alignment and precise tile-based collision checks.
- When idle, `anim_timer` cycles at 6 FPS for gentle breathing; when moving, it cycles at 8 FPS matching the character run spritesheet for a natural stride.

---

## Party & PC Storage Logic

- Maximum active party size is **6 creatures**.
- Calling `PartyManager.add_creature(creature)`:
  - If `len(party) < 6`: Appends to `self.party` and returns `"PARTY"`.
  - If `len(party) == 6`: Appends to `self.storage` (the PC box) and returns `"STORAGE"`.
- Supports full serialization (`to_dict` / `load_dict`) integrated with `SaveManager`.
