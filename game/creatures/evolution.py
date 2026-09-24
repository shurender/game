"""Extensible evolution condition system.

Each condition is a pure function:
    check(creature, context) -> bool

`context` is an optional dict the caller can populate with:
    - "inventory": Inventory instance (for item conditions)
    - any custom keys for special conditions

New conditions are registered at runtime via `register_condition`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from game.creatures.creature import Creature


# ── Condition checker type ────────────────────────────────────────────────────

ConditionFn = Callable[["Creature", dict[str, Any], dict[str, Any]], bool]
# signature: (creature, evo_data, context) -> bool


_REGISTRY: dict[str, ConditionFn] = {}


def register_condition(name: str, fn: ConditionFn) -> None:
    """Register a new evolution condition handler."""
    _REGISTRY[name] = fn


def check_condition(creature: "Creature", evo_data: dict[str, Any],
                    context: dict[str, Any] | None = None) -> bool:
    """Evaluate an evolution condition dict against a creature.

    Args:
        creature:  The creature being checked.
        evo_data:  Raw evolution dict from JSON (e.g. {"condition": "level", "level": 16, ...}).
        context:   Optional runtime context (inventory, friendship, etc.)

    Returns:
        True if the condition is satisfied.
    """
    if not evo_data:
        return False

    context = context or {}
    cond_name = evo_data.get("condition", "level")

    fn = _REGISTRY.get(cond_name)
    if fn is None:
        raise ValueError(f"Unknown evolution condition: '{cond_name}'")

    return fn(creature, evo_data, context)


# ── Built-in conditions ───────────────────────────────────────────────────────

def _level_condition(creature: "Creature", evo_data: dict, _ctx: dict) -> bool:
    required = evo_data.get("level", 999)
    return creature.level >= required


def _item_condition(creature: "Creature", evo_data: dict, ctx: dict) -> bool:
    """True if the player's inventory contains the required item."""
    item_id = evo_data.get("item_id")
    if not item_id:
        return False
    inventory = ctx.get("inventory")
    if inventory is None:
        return False
    return inventory.has(item_id)


def _friendship_condition(creature: "Creature", evo_data: dict, _ctx: dict) -> bool:
    required = evo_data.get("friendship", 220)
    friendship = getattr(creature, "friendship", 0)
    return friendship >= required


def _special_condition(creature: "Creature", evo_data: dict, ctx: dict) -> bool:
    """Delegate to a named callable registered in context["special_handlers"]."""
    key = evo_data.get("key", "")
    handlers: dict = ctx.get("special_handlers", {})
    handler = handlers.get(key)
    if handler is None:
        return False
    return handler(creature, evo_data, ctx)


register_condition("level",      _level_condition)
register_condition("item",       _item_condition)
register_condition("friendship", _friendship_condition)
register_condition("special",    _special_condition)
