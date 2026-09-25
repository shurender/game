# UI Subsystem (`game/ui/`)

The `ui` package provides reusable visual interface components, typography utilities, dialogue boxes, and menu selectors for menus, shops, battles, and dialogue overlays.

---

## File Manifest

| File | Purpose |
| :--- | :--- |
| **`dialogue_box.py`** | `DialogueBox`. Overworld dialogue container rendering speaker name plates, typewriter animated text, blinking advance arrows, and choice selection menus. |
| **`menu.py`** | `Menu`. General-purpose vertical/horizontal keyboard navigation menu with audio feedback hooks and selection callbacks. |
| **`text.py`** | Text rendering utilities: `render_text`, `render_text_outlined` (draws high-contrast borders around text for readability over any background), and `TypewriterText` character-by-character reveal helper. |
| **`components.py`** | Standardized UI widgets: `draw_hp_bar` (smooth animated HP bar that changes color from green -> yellow -> red), card panels, and rounded borders. |

---

## Key Components

### 1. `render_text_outlined`
Draws text with a 1-pixel or 2-pixel black outline in all 8 cardinal and diagonal directions before drawing the foreground text. This guarantees legibility across overworld maps, battle arenas, and darkened overlays without requiring dark backing boxes.

### 2. `DialogueBox`
- **Typewriter Effect**: Renders characters incrementally according to `chars_per_second` (default 35-40).
- **Fast Forward / Skip**: Pressing `Confirm` (`Z` / `Space` / `Enter`) while text is printing instantly displays the complete text; pressing again advances the dialogue or selects a choice.
- **Choices**: Supports branching dialog options with arrow cursor selection.

### 3. Dynamic Health Bars (`draw_hp_bar`)
Renders creature vitality with dynamic color gradients:
- **Green** (> 50% HP)
- **Yellow** (20% – 50% HP)
- **Red** (< 20% HP)
