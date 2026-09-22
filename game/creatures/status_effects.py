"""Status effect definitions and logic."""
from enum import Enum, auto

class StatusEffect(Enum):
    NONE = auto()
    BURN = auto()
    POISON = auto()
    PARALYSIS = auto()
    SLEEP = auto()
    FREEZE = auto()

class VolatileStatus(Enum):
    CONFUSION = auto()
    FLINCH = auto()
    LEECH_SEED = auto()
