"""Battle item use logic — extensible stat-boost effects."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.creatures.creature import Creature
    from game.inventory.item import Item

# Registry maps effect-id → (stat_attr, description)
_BATTLE_EFFECTS: dict[str, tuple[str, str]] = {
    "boost_spd": ("spd", "Speed"),
    "boost_atk": ("atk", "Attack"),
    "boost_def": ("def_", "Defense"),
    "boost_sp_atk": ("sp_atk", "Sp. Attack"),
    "boost_sp_def": ("sp_def", "Sp. Defense"),
}


def use_battle_item(item: "Item", target: "Creature") -> str:
    """Apply a battle-use item (stat boost) to a creature.

    Args:
        item:   The battle item to use.
        target: The creature to buff.

    Returns:
        A descriptive message of what happened.

    Raises:
        ValueError: If the item or effect is invalid.
    """
    if item.category != "Stat Boost":
        raise ValueError(f"{item.name} is not a battle item.")

    if item.effect not in _BATTLE_EFFECTS:
        raise ValueError(f"Unknown battle effect: {item.effect}")

    stat_attr, stat_name = _BATTLE_EFFECTS[item.effect]
    stages = int(item.value)

    current = getattr(target.stats, stat_attr)
    boost = max(1, int(current * 0.5 * stages))   # 50% per stage
    setattr(target.stats, stat_attr, current + boost)

    return f"{target.name}'s {stat_name} rose!"


def register_battle_effect(effect_id: str, stat_attr: str, description: str) -> None:
    """Register a custom battle effect at runtime (extensibility hook)."""
    _BATTLE_EFFECTS[effect_id] = (stat_attr, description)
