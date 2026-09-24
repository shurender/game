from dataclasses import dataclass, field
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from game.creatures.progression import XPGainResult

@dataclass
class ActionEvent:
    actor_name: str
    action_type: str
    message: str
    damage_dealt: int = 0
    is_critical: bool = False
    effectiveness: float = 1.0
    status_applied: Optional[str] = None
    fainted: bool = False
    escaped: bool = False
    missed: bool = False

@dataclass
class TurnResult:
    events: List[ActionEvent] = field(default_factory=list)
    battle_ended: bool = False
    winner: Optional[str] = None  # "PLAYER" or "ENEMY" or "ESCAPE"
    xp_result: Optional["XPGainResult"] = None  # populated on PLAYER victory
