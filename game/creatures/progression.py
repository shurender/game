"""Progression engine: XP gain, levelling, move learning, evolution checks.

All functions are pure / side-effect-free with respect to the UI.
They return structured result objects the caller (state/UI) can animate.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from game.creatures.creature import Creature

from game.creatures.evolution import check_condition


# ── XP Curves ─────────────────────────────────────────────────────────────────

def xp_for_level(level: int, curve: str) -> int:
    """Total accumulated XP needed to reach `level` on the given curve."""
    n = max(1, level)
    if curve == "fast":
        return int(4 * n ** 3 / 5)
    elif curve == "medium_fast":
        return n ** 3
    elif curve == "medium_slow":
        return int((6 / 5) * n ** 3 - 15 * n ** 2 + 100 * n - 140)
    elif curve == "slow":
        return int(5 * n ** 3 / 4)
    else:
        return n ** 3   # fallback


# ── Result dataclasses (UI reads these) ───────────────────────────────────────

@dataclass
class LevelUpResult:
    new_level: int
    stat_gains: dict[str, int]         # {"hp": +5, "atk": +3, …}
    moves_learned: list[str]           # move IDs unlocked at this level


@dataclass
class XPGainResult:
    xp_gained: int
    level_ups: list[LevelUpResult]     # one entry per level crossed
    pending_evolution: bool            # True if evolution condition is now met
    evolution_target: str | None       # species_id of the target form


@dataclass
class EvolutionResult:
    old_name: str
    new_species_id: str
    new_name: str
    stat_changes: dict[str, int]       # delta from old to new stats
    moves_learned: list[str]           # level-1 moves of new species not already known


# ── XP / Level-up ─────────────────────────────────────────────────────────────

def award_xp(creature: "Creature", amount: int,
             species_data: dict[str, Any]) -> XPGainResult:
    """Award XP to a creature and resolve all level-ups.

    Args:
        creature:     The creature receiving XP (mutated in place).
        amount:       Raw XP to award.
        species_data: The raw dict for this species from creatures.json
                      (needed for learnset, curve, evolution).

    Returns:
        XPGainResult describing all changes.
    """
    if creature.level >= 100:
        return XPGainResult(0, [], False, None)

    curve = species_data.get("xp_curve", "medium_fast")
    creature.xp += amount

    level_ups: list[LevelUpResult] = []
    while creature._level < 100:
        next_xp = xp_for_level(creature._level + 1, curve)
        if creature.xp < next_xp:
            break
        level_ups.append(_do_level_up(creature, species_data))

    # Check evolution
    evo_data = species_data.get("evolution")
    pending = False
    target = None
    if evo_data and evo_data.get("condition") == "level":
        if check_condition(creature, evo_data):
            pending = True
            target = evo_data.get("target")

    return XPGainResult(amount, level_ups, pending, target)


def _do_level_up(creature: "Creature", species_data: dict) -> LevelUpResult:
    """Advance creature one level and apply stat recalculation."""
    from game.creatures.stats import calculate_max_hp, calculate_stat

    old_stats = creature.stats
    creature._level += 1
    new_stats = creature._recalculate_stats()
    creature.stats = new_stats

    # Heal by HP gained
    hp_diff = new_stats.hp - old_stats.hp
    creature.current_hp = min(new_stats.hp, creature.current_hp + hp_diff)

    # Stat gains for display
    gains = {
        "hp":     new_stats.hp     - old_stats.hp,
        "atk":    new_stats.atk    - old_stats.atk,
        "def_":   new_stats.def_   - old_stats.def_,
        "sp_atk": new_stats.sp_atk - old_stats.sp_atk,
        "sp_def": new_stats.sp_def - old_stats.sp_def,
        "spd":    new_stats.spd    - old_stats.spd,
    }

    # Move learning
    moves_learned = _learn_moves_at_level(creature, species_data, creature._level)

    return LevelUpResult(creature._level, gains, moves_learned)


def _learn_moves_at_level(creature: "Creature", species_data: dict,
                           level: int) -> list[str]:
    """Return move IDs learnable at this level that the creature doesn't have."""
    learnset = species_data.get("learnset", [])
    new_moves = []
    for entry in learnset:
        if entry["level"] == level:
            move_id = entry["move"]
            if move_id not in creature.moves:
                creature.moves.append(move_id)
                new_moves.append(move_id)
    return new_moves


# ── Evolution ─────────────────────────────────────────────────────────────────

def evolve(creature: "Creature",
           old_species_data: dict,
           new_species_id: str,
           new_species_data: dict,
           new_species_obj) -> EvolutionResult:
    """Mutate creature in-place to its evolved form.

    Args:
        creature:          The creature to evolve.
        old_species_data:  Raw JSON dict for the old species.
        new_species_id:    Target species ID.
        new_species_data:  Raw JSON dict for the new species.
        new_species_obj:   The Species instance for the new form.

    Returns:
        EvolutionResult for UI consumption.
    """
    old_name = creature.nickname if creature.nickname != creature.species.name else creature.species.name

    old_max_hp = creature.stats.hp
    old_atk = creature.stats.atk
    old_def = creature.stats.def_
    old_sp_atk = creature.stats.sp_atk
    old_sp_def = creature.stats.sp_def
    old_spd = creature.stats.spd

    # Swap species
    creature.species = new_species_obj
    if creature.nickname == old_species_data.get("name", ""):
        creature.nickname = new_species_obj.name   # auto-rename if not nicknamed

    # Recalculate stats at current level
    creature.stats = creature._recalculate_stats()

    # Heal by HP gained from evolution
    hp_diff = creature.stats.hp - old_max_hp
    creature.current_hp = min(creature.stats.hp, creature.current_hp + max(0, hp_diff))

    # Stat deltas for display
    stat_changes = {
        "hp":     creature.stats.hp     - old_max_hp,
        "atk":    creature.stats.atk    - old_atk,
        "def_":   creature.stats.def_   - old_def,
        "sp_atk": creature.stats.sp_atk - old_sp_atk,
        "sp_def": creature.stats.sp_def - old_sp_def,
        "spd":    creature.stats.spd    - old_spd,
    }

    # Learn level-1 moves of new species not already known
    learnset = new_species_data.get("learnset", [])
    new_moves = []
    for entry in learnset:
        if entry["level"] <= 1:
            move_id = entry["move"]
            if move_id not in creature.moves:
                creature.moves.append(move_id)
                new_moves.append(move_id)

    return EvolutionResult(
        old_name=old_name,
        new_species_id=new_species_id,
        new_name=creature.species.name,
        stat_changes=stat_changes,
        moves_learned=new_moves,
    )


# ── Post-battle XP helper ─────────────────────────────────────────────────────

def calculate_battle_xp(defeated_species_data: dict, winner_level: int) -> int:
    """Standard battle XP formula (scaled by level difference)."""
    base = defeated_species_data.get("xp_yield", 50)
    defeated_level = defeated_species_data.get("level", winner_level)  # fallback
    # Scale: higher-level defeated → more XP; cap at ×2 / floor at ×0.5
    ratio = max(0.5, min(2.0, defeated_level / max(1, winner_level)))
    return max(1, int(base * ratio))
