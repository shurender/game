# Creatures Subsystem (`game/creatures/`)

The `creatures` package defines the core entity models, data representations, statistics, moves, and progression systems for all collectible creatures in the game.

---

## File Manifest

| File | Purpose |
| :--- | :--- |
| **`creature.py`** | Runtime `Creature` instance. Encapsulates current level, HP, active moves, status effects, calculated stats, and serialization (`to_dict` / `from_dict`). |
| **`species.py`** | Immutable species metadata (`Species`). Holds species ID, display name, elemental types, base stats, base XP yield, catch rate, and learnsets. |
| **`move.py`** | `Move` definition and `MoveFactory`. Handles move types, damage categories (`physical`, `special`, `status`), base power, accuracy, and PP tracking. |
| **`stats.py`** | `Stats` container class holding the 6 core RPG statistics (`hp`, `atk`, `def_`, `sp_atk`, `sp_def`, `spd`). |
| **`types.py`** | Elemental type system (`ElementType` enum). Defines elemental relationships (Grass, Fire, Water, Electric, Normal, Bug, Rock, Flying, Ghost, etc.) and type interaction multipliers. |
| **`progression.py`** | Leveling and evolution logic. Implements standard RPG cubic/quadratic XP curves, stat calculation formulas, and evolution check functions. |
| **`creature_factory.py`** | Singleton factory (`CreatureFactory`). Loads `data/creatures.json`, instantiates creatures with appropriate starting moves according to level, and executes species evolution. |

---

## Stat Calculation Formula

Creature stats at level $L$ are derived from base stats ($B$) using classic RPG formulas:

$$\text{HP} = \left\lfloor \frac{2 \times B_{\text{HP}} \times L}{100} \right\rfloor + L + 10$$

$$\text{Other Stat} = \left\lfloor \frac{2 \times B_{\text{Stat}} \times L}{100} \right\rfloor + 5$$

---

## Lifecycle: Spawning to Evolution

1. **Instantiation**: `CreatureFactory.get_instance().create_creature(species_id, level)` queries `species_db`.
2. **Move Population**: Assigns starting moves from the species learnset up to the given level. If fewer than 4 moves exist, basic attacks like `tackle` or `scratch` are populated as fallbacks.
3. **Combat Experience**: When an opponent is defeated, `BattleEngine` awards XP. If XP crosses the threshold in `progression.py`, the creature levels up and recalculates its stats.
4. **Evolution**: When a creature reaches its evolution level threshold, an `EvolutionResult` is produced and passed to `EvolutionState`, transforming the species while preserving current HP ratios and nickname.
