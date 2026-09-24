"""Re-export StatusEffect from the canonical module to avoid duplicate enum classes.

Having two separate StatusEffect enum definitions causes identity comparison failures
(e.g. `creature.status == StatusEffect.POISON` returns False even when both values
look the same, because they belong to different classes).

All code should import StatusEffect from this module OR from game.creatures.status_effects —
both will give the same class.
"""
from game.creatures.status_effects import StatusEffect, VolatileStatus  # noqa: F401

__all__ = ["StatusEffect", "VolatileStatus"]
