"""Inventory — tracks item quantities and dispatches use calls."""
from __future__ import annotations

from collections import defaultdict
from typing import Iterator, TYPE_CHECKING

if TYPE_CHECKING:
    from game.creatures.creature import Creature

from game.inventory.item import Item
from game.inventory.item_factory import ItemFactory
from game.inventory.healing_item import use_healing_item
from game.inventory.capture_item import use_capture_item
from game.inventory.battle_item import use_battle_item


class Inventory:
    """Manages item quantities and dispatches item use to domain functions.

    This class is UI-agnostic; callers receive plain strings as feedback.
    """

    _instance = None

    @classmethod
    def get_instance(cls) -> "Inventory":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        # item_id → quantity
        self._quantities: dict[str, int] = defaultdict(int)

    # ------------------------------------------------------------------
    # Quantity management
    # ------------------------------------------------------------------

    def add(self, item_id: str, qty: int = 1) -> None:
        """Add qty units of item_id to the inventory."""
        if qty <= 0:
            raise ValueError("Quantity must be positive.")
        factory = ItemFactory.get_instance()
        factory.get(item_id)          # validates item_id exists
        self._quantities[item_id] += qty

    def remove(self, item_id: str, qty: int = 1) -> None:
        """Remove qty units. Raises ValueError if insufficient stock."""
        if qty <= 0:
            raise ValueError("Quantity must be positive.")
        if self._quantities[item_id] < qty:
            raise ValueError(f"Not enough {item_id} in inventory.")
        self._quantities[item_id] -= qty
        if self._quantities[item_id] == 0:
            del self._quantities[item_id]

    def quantity(self, item_id: str) -> int:
        return self._quantities.get(item_id, 0)

    def has(self, item_id: str, qty: int = 1) -> bool:
        return self.quantity(item_id) >= qty

    # ------------------------------------------------------------------
    # Iteration / filtering
    # ------------------------------------------------------------------

    def items(self) -> list[tuple[Item, int]]:
        """Return all stocked items as (Item, quantity) pairs."""
        factory = ItemFactory.get_instance()
        return [(factory.get(iid), qty) for iid, qty in self._quantities.items()]

    def by_category(self, category: str) -> list[tuple[Item, int]]:
        """Return stocked items filtered by category."""
        return [(item, qty) for item, qty in self.items() if item.category == category]

    # ------------------------------------------------------------------
    # Use dispatch
    # ------------------------------------------------------------------

    def use(self, item_id: str, target: "Creature | None" = None, **kwargs) -> str:
        """Use one unit of an item.

        Args:
            item_id: The item to use.
            target:  The creature to apply the effect to (required for most items).
            **kwargs: Extra arguments forwarded to capture items.

        Returns:
            A human-readable result message.

        Raises:
            ValueError: If item cannot be used (invalid, out of stock, wrong context).
        """
        if not self.has(item_id):
            factory = ItemFactory.get_instance()
            name = factory.get(item_id).name
            raise ValueError(f"You have no {name} left.")

        factory = ItemFactory.get_instance()
        item = factory.get(item_id)

        if item.category == "Healing":
            if target is None:
                raise ValueError("A target creature must be specified for healing items.")
            msg = use_healing_item(item, target)
            self.remove(item_id)
            return msg

        elif item.category == "Capture":
            if target is None:
                raise ValueError("A target creature must be specified for capture items.")
            success, shakes, location = use_capture_item(item, target)
            self.remove(item_id)
            if success:
                return f"Captured {target.name}! Sent to {location}."
            else:
                return f"{target.name} broke free! ({shakes} shake{'s' if shakes != 1 else ''})"

        elif item.category == "Stat Boost":
            if target is None:
                raise ValueError("A target creature must be specified for battle items.")
            msg = use_battle_item(item, target)
            self.remove(item_id)
            return msg

        elif item.category == "Key Item":
            raise ValueError(f"{item.name} is a key item and cannot be used directly.")

        raise ValueError(f"Unhandled item category: {item.category}")

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, int]:
        return dict(self._quantities)

    def load_dict(self, data: dict[str, int]) -> None:
        self._quantities = defaultdict(int, data)

    def clear(self) -> None:
        """Reset inventory (testing / new game)."""
        self._quantities.clear()
