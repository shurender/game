"""Capture item use logic — delegates to the capture system."""
from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from game.creatures.creature import Creature
    from game.inventory.item import Item

from game.battle.capture import CaptureItem, execute_capture


def use_capture_item(item: "Item", target: "Creature") -> Tuple[bool, int, str]:
    """Attempt to capture a wild creature using a capture item.

    Args:
        item:   The capture item to use.
        target: The wild creature being captured.

    Returns:
        (success, shakes, location) — see execute_capture for semantics.

    Raises:
        ValueError: If the item is not a capture item.
    """
    if item.category != "Capture":
        raise ValueError(f"{item.name} is not a capture item.")

    capture_item = CaptureItem(
        item_id=item.item_id,
        name=item.name,
        catch_rate_modifier=float(item.value),
    )
    return execute_capture(target, capture_item)
