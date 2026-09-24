"""Healing item use logic — no UI dependencies."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.creatures.creature import Creature
    from game.inventory.item import Item


def use_healing_item(item: "Item", target: "Creature") -> str:
    """Apply a healing item effect to a creature.

    Args:
        item:   The healing item to use.
        target: The creature to apply the effect to.

    Returns:
        A descriptive message of what happened.

    Raises:
        ValueError: If the item cannot be used (fainted target, wrong category).
    """
    if item.category != "Healing":
        raise ValueError(f"{item.name} is not a healing item.")

    if target.is_fainted and item.effect == "heal_hp":
        raise ValueError(f"{target.name} has fainted and cannot be healed this way.")

    if item.effect == "heal_hp":
        amount = int(item.value)
        before = target.current_hp
        target.heal(amount)
        healed = target.current_hp - before
        return f"{target.name} recovered {healed} HP!"

    elif item.effect == "cure_status":
        status_to_cure = str(item.value).upper()
        current = target.status
        current_name = current.name if hasattr(current, "name") else str(current).upper()

        if current_name == "NONE":
            raise ValueError(f"{target.name} has no status condition to cure.")
        if current_name != status_to_cure:
            raise ValueError(f"{item.name} cannot cure {current_name}.")

        from game.battle.status_effects import StatusEffect
        target.status = StatusEffect.NONE
        return f"{target.name}'s {status_to_cure} was cured!"

    raise ValueError(f"Unknown healing effect: {item.effect}")
