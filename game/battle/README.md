# Battle Subsystem (`game/battle/`)

The `battle` package implements a turn-based combat system inspired by classic handheld monster battlers. The combat logic is isolated from UI presentation, allowing thorough automated testing and headless simulations.

---

## File Manifest

| File | Purpose |
| :--- | :--- |
| **`battle.py`** | `Battle` domain model holding combatants (`player_creature`, `enemy_creature`), active turn count, battle winner, and escape status. |
| **`battle_action.py`** | `BattleAction` descriptor specifying what an actor intends to do (`MOVE`, `ITEM`, `SWITCH`, `ESCAPE`). |
| **`battle_engine.py`** | Pure functional turn resolver (`BattleEngine.process_turn`). Determines move order via speed/priority, executes actions, applies status effects, and generates an ordered list of animation events. |
| **`battle_math.py`** | Combat formulas. Calculates damage, type effectiveness multipliers, Same-Type Attack Bonus (STAB), critical hit rates, and accuracy checks. |
| **`battle_ai.py`** | Enemy trainer and wild creature AI (`BattleAI`). Implements `BASIC`, `AGGRESSIVE`, `SMART`, and `RANDOM` move selection strategies. |
| **`battle_result.py`** | Output dataclasses (`TurnResult`, `ActionEvent`, `XPResult`) returned by `BattleEngine` to drive UI animations and dialogs. |
| **`capture.py`** | Capture mechanics (`calculate_capture`, `execute_capture`). Uses Gen VI-style capture formulas taking into account species catch rate, remaining HP percentage, status condition, and ball modifiers. |
| **`status_effects.py`** | Volatile and non-volatile conditions (`POISON`, `BURN`, `PARALYSIS`, `SLEEP`, `FREEZE`) and stat modifiers (-6 to +6 stages). |

---

## Turn Resolution Workflow

```
Player Action (Move/Item/Switch/Run) + Enemy AI Action
                       │
                       ▼
           BattleEngine.process_turn()
                       │
  ┌────────────────────┴────────────────────┐
  │ Determine Priority & Speed              │
  │ Execute Fast Action -> Generate Events  │
  │ Check Faint / Status Damage             │
  │ Execute Slow Action -> Generate Events  │
  │ Calculate XP & Level Up (if defeated)   │
  └────────────────────┬────────────────────┘
                       │
                       ▼
      TurnResult (Sequence of ActionEvents)
                       │
                       ▼
       BattleState animates event sequence
```

---

## Capture Formula

Captures evaluate a capture rate threshold `a`:
$$a = \frac{(3 \times \text{max\_hp} - 2 \times \text{current\_hp}) \times \text{catch\_rate} \times \text{status\_mod} \times \text{ball\_mod}}{3 \times \text{max\_hp} \times 255}$$

- If $a \ge 1.0$, capture is an automatic success (3 shakes).
- Otherwise, a shake threshold $b = 65536 \times a^{0.25}$ is evaluated up to 4 times. If 4 checks pass, the capture succeeds; otherwise, the creature breaks free after the corresponding number of shakes.
- When successful, `execute_capture` heals the creature and places it in the active party or sends it to PC storage if full.
