# Game Data Database (`data/`)

The `data` directory contains the static JSON game configuration databases. All content is human-readable, easily modifiable, and decoupled from Python game logic.

---

## File Manifest

| File | Contents | Key Schema Elements |
| :--- | :--- | :--- |
| **`creatures.json`** | All collectible creature species. | `species_id`, `name`, `types`, `base_stats` (hp, atk, def, sp_atk, sp_def, spd), `base_xp`, `catch_rate`, `learnset` (level-to-move mappings), `evolutions`. |
| **`moves.json`** | Combat moves and technique catalog. | `id`, `name`, `type`, `category` (`physical`, `special`, `status`), `power`, `accuracy`, `pp`, `priority`, `effect`. |
| **`items.json`** | Inventory items and consumable items. | `item_id`, `name`, `category` (`Healing`, `Capture`, `Stat Boost`, `Key Item`), `effect`, `value`, `price`, `description`. |
| **`maps.json`** | All overworld locations and interior maps. | `width`, `height`, `layers` (`ground`, `decoration`, `collision`), `warps` (source coords -> target map & coords), `npcs` (positions, sprites, dialogues), `encounters`. |
| **`dialogues.json`** | Conversation scripts and decision trees. | Nodes with `speaker`, `text`, `choices` (`text`, `next`), `actions` (`start_quest`, `give_item`, `remove_item`, `give_creature`, `set_flag`), `next`. |
| **`quests.json`** | Main storyline and side quest objectives. | `id`, `name`, `type`, `description`, `objectives` (`id`, `type`, `npc_id`/`trainer_id`/`species_id`, `description`), `rewards` (`type`, `item_id`/`amount`, `quantity`). |
| **`shops.json`** | Pokémart and merchant catalogs. | `shop_id`, `name`, `greeting`, `farewell`, `buys`, `sell_rate`, `sells` (list of item IDs). |
| **`trainers.json`** | NPC trainer battle configurations. | `trainer_id`, `name`, `sprite`, `ai_type` (`BASIC`, `AGGRESSIVE`, `SMART`), `dialogue_intro`, `dialogue_defeat`, `party` (species, level, moves), `rewards`. |

---

## Content Authoring Guidelines

### Adding a New Creature Species
1. Open `data/creatures.json`.
2. Add an entry under `"species"` with a unique slug ID (e.g. `"volthare"`).
3. Specify `base_stats`, elemental types, and learnset moves (must match IDs in `moves.json`).

### Adding a New Quest
1. Open `data/quests.json`.
2. Add a quest block with `"objectives"` referencing valid event types (`talk_npc`, `defeat_trainer`, `defeat_creature`, `capture_creature`).
3. Connect initial quest activation via `_start_new_game` in `main_menu_state.py` or via `"type": "start_quest"` inside `dialogues.json`.
