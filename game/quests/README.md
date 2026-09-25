# Quests Subsystem (`game/quests/`)

The `quests` package provides an event-driven quest tracking framework that manages main storylines and side objectives.

---

## File Manifest

| File | Purpose |
| :--- | :--- |
| **`quest.py`** | `Quest`, `Objective`, and `QuestStatus` (`NOT_STARTED`, `IN_PROGRESS`, `COMPLETED`). Tracks objective progress counters and reward distributions. |
| **`quest_manager.py`** | `QuestManager` singleton. Loads `data/quests.json`, starts quests, routes world/battle events, evaluates completion criteria, and grants item/coin rewards. |

---

## Event-Driven Architecture

Instead of hardcoding quest checks across the codebase, game events are broadcast through `QuestManager.on_event(event_name, data)`:

| Event Name | Data Payload | Example Trigger |
| :--- | :--- | :--- |
| **`talk_npc`** | `{"npc_id": "npc_mom"}` | Talking to Mom completes `main_01`. |
| **`defeat_trainer`** | `{"trainer_id": "trainer_boss_1"}` | Defeating Rogue Leader on Route 2 completes `main_03`. |
| **`defeat_creature`** | `{"species_id": "barkbug"}` | Defeating a wild creature in combat. |
| **`capture_creature`** | `{"species_id": "florbit"}` | Catching a wild creature using a Capture Orb. |

---

## Reward Distribution

When all objectives in a quest are satisfied:
1. Quest status switches to `COMPLETED`.
2. Rewards defined in `data/quests.json` are automatically credited:
   - Items are deposited directly into `Inventory`.
   - Coins are deposited directly into `Wallet`.
3. Completion messages are logged and displayed in the `QuestLogState`.
