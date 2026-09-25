# Test Suite (`tests/`)

The `tests` directory contains the automated test suite for the Risu RPG engine, executed with `pytest`. It covers unit logic, combat math, state transitions, UI menus, save persistence, and asset fallbacks.

---

## Test Manifest

| Test File | Covered Modules & Systems |
| :--- | :--- |
| **`test_ai.py`** | Battle AI decision making (basic, aggressive, smart, random). |
| **`test_animation.py`** | `AnimationLayer`, screen shakes, damage numbers, and capture animations. |
| **`test_asset_manager.py`** | Asset fallback behaviors, font loading, missing audio resilience. |
| **`test_audio.py`** | Procedural tone synthesis (`numpy`), volume clamping, SFX and BGM controls. |
| **`test_battle.py`** | Core battle actions, turn flow, faint checks, and victory conditions. |
| **`test_battle_comprehensive.py`** | End-to-end combat scenarios, multi-turn battles, and party switches. |
| **`test_battle_math.py`** | Damage formulas, type effectiveness matrices, STAB, and critical hits. |
| **`test_capture.py`** | Capture math formulas, shake counts, `CaptureItem`, and `execute_capture`. |
| **`test_creatures.py`** | Creature stats, levels, learnset populations, and serialization. |
| **`test_creatures_comprehensive.py`** | Species learnsets, XP gain curves, and evolution progression. |
| **`test_data_loader.py`** | JSON validation for `creatures.json`, `moves.json`, and `items.json`. |
| **`test_dialogue.py`** | Dialogue state node transitions, choices, and action executions. |
| **`test_game_core.py`** | Engine initialization, game loop hooks, and graceful exit routines. |
| **`test_inventory.py`** | Bag management, category filtering, healing items, and item removal. |
| **`test_map.py`** | Map loading, warp links, NPC placements, and wild encounter rates. |
| **`test_mc_character.py`** | Main character 8-frame IDLE and RUN spritesheet loading and animation timers. |
| **`test_pause_menu.py`** | Pause menu slide animations, drawer options, and sub-state pushes. |
| **`test_player.py`** | Player grid movement, pixel interpolation, and facing interaction range. |
| **`test_progress.py`** | Story flags, conditional dialogues, and world progress triggers. |
| **`test_progression.py`** | XP thresholds, level-up stat increases, and move learning. |
| **`test_quests.py`** | Event routing (`talk_npc`, `defeat_trainer`), objective fulfillment, rewards. |
| **`test_save_system.py`** | Full-game state serialization to JSON, metadata headers, and deserialization. |
| **`test_settings.py`** | Display resolutions, fullscreen mode, and volume persistence in settings. |
| **`test_shop.py`** | Shop listings, coin transactions, buy/sell validations, and wallet sync. |
| **`test_state_machine.py`** | Stack-based state machine push, pop, replace, and pause/resume hooks. |

---

## Running the Tests

To run the complete test suite:
```bash
pytest
```

To run with verbose output:
```bash
pytest -v
```

To run a specific test file:
```bash
pytest tests/test_mc_character.py
```
