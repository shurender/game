# Saves Directory (`saves/`)

The `saves` directory stores player configuration and persistent game save states in JSON format.

---

## File Manifest

| File | Purpose |
| :--- | :--- |
| **`settings.json`** | Engine configuration managed by `SettingsManager`. Stores window resolution (`width`, `height`), fullscreen flag, and audio volume sliders (`master_volume`, `sfx_volume`, `bgm_volume`). |
| **`save_0.json`** | Dedicated slot for automatic saves (autosave). |
| **`save_1.json` – `save_3.json`** | Manual player save slots created via the in-game Pause Menu (`Save` option) or `F5`. |

---

## Save File Schema

A standard save file contains:
```json
{
  "player_name": "Player",
  "position": {
    "map_id": "starting_town",
    "x": 4,
    "y": 6,
    "facing": "DOWN"
  },
  "party": {
    "party": [ ... ],
    "storage": [ ... ]
  },
  "inventory": {
    "items": { "potion": 3, "capture_orb": 5 }
  },
  "wallet": {
    "coins": 3000
  },
  "quests": {
    "active_quests": { ... },
    "completed_quests": [ ... ]
  },
  "progress": {
    "flags": { "defeated_trainer_youngster_1": true }
  }
}
```
