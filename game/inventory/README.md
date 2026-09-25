# Inventory Subsystem (`game/inventory/`)

The `inventory` package handles bag management, item definitions, item application logic (healing, capture orbs, stat boosts), and serialization.

---

## File Manifest

| File | Purpose |
| :--- | :--- |
| **`inventory.py`** | `Inventory` singleton. Manages item quantities (`_quantities`), capacity, category queries (`by_category()`), adding/removing items, and invoking item effects. |
| **`item.py`** | `Item` immutable dataclass. Contains `item_id`, `name`, `category`, `effect`, `value`, `price`, and `description`. Exposes `is_usable_in_battle()` and `is_usable_outside_battle()`. |
| **`item_factory.py`** | `ItemFactory` singleton. Reads `data/items.json` and supplies validated `Item` instances by ID. |
| **`healing_item.py`** | Implements healing effect logic (`heal_hp`, `cure_status`). Checks whether HP is already full and restores up to max HP. |
| **`capture_item.py`** | Implements capture orb execution in battle via `game.battle.capture`. |
| **`stat_boost_item.py`** | In-battle temporary stat stage enhancement items (`boost_atk`, `boost_def`, `boost_spd`). |

---

## Item Categories

| Category | Overworld Usable? | Battle Usable? | Example Items |
| :--- | :---: | :---: | :--- |
| **`Healing`** | Yes | Yes | Potion, Super Potion, Antidote |
| **`Capture`** | No | Yes | Capture Orb, Great Orb, Ultra Orb |
| **`Stat Boost`** | No | Yes | Attack Boost, Speed Boost |
| **`Key Item`** | No | No | Parcel, Town Map |

---

## Usage Workflow

When an item is used via `Inventory.use(item_id, target=creature)`:
1. Validates that the item is present in inventory (`count > 0`).
2. Checks usability constraints depending on whether combat is active.
3. Dispatches to effect handlers (`use_healing_item`, etc.).
4. If the effect succeeds, decrements the item quantity by 1 and returns a confirmation message.
