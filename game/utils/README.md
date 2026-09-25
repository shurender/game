# Utilities Subsystem (`game/utils/`)

The `utils` package contains common helper functions, mathematical interpolation utilities, and resilient file loading routines used throughout the game.

---

## File Manifest

| File | Purpose |
| :--- | :--- |
| **`helpers.py`** | Mathematical helper functions: `clamp(val, min_v, max_v)` to constrain values, `lerp(a, b, t)` for smooth linear interpolation, and formatting helpers. |
| **`data_loader.py`** | JSON loading utility (`load_json_file`). Resolves absolute paths relative to `DATA_DIR`, caches file handles, and returns deserialized Python dictionaries with detailed error messages. |

---

## Usage Examples

### Clamping and Interpolation
```python
from game.utils.helpers import clamp, lerp

# Constrain volume between 0.0 and 1.0
volume = clamp(raw_volume, 0.0, 1.0)

# Smooth camera tracking
current_x = lerp(current_x, target_x, dt * 5.0)
```

### Loading Game Data
```python
from game.utils.data_loader import load_json_file

# Safely loads data/items.json relative to DATA_DIR
data = load_json_file("items.json")
```
