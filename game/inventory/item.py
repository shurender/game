"""Base Item definition."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Item:
    """Immutable definition of an item type."""
    item_id: str
    name: str
    category: str       # "Healing", "Capture", "Stat Boost", "Key Item"
    effect: str         # e.g. "heal_hp", "capture", "cure_status", "boost_spd"
    value: Any          # Effect magnitude or string param (e.g. 20, 1.5, "Poison")
    price: int
    description: str

    def is_usable_in_battle(self) -> bool:
        """Returns True if the item can be used during a battle turn."""
        return self.category in ("Healing", "Capture", "Stat Boost")

    def is_usable_outside_battle(self) -> bool:
        """Returns True if the item can be used on the overworld."""
        return self.category == "Healing"
