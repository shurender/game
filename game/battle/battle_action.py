from dataclasses import dataclass
from typing import Optional
from game.creatures.creature import Creature
from game.creatures.move import Move

@dataclass
class BattleAction:
    actor: Creature
    action_type: str  # "MOVE", "ESCAPE", "SWITCH", "ITEM"
    target: Optional[Creature] = None
    move: Optional[Move] = None
    
    @property
    def priority(self) -> int:
        if self.action_type in ("SWITCH", "ITEM", "ESCAPE"):
            return 6  # Highest priority
        if self.move:
            return self.move.priority
        return 0

    @property
    def speed(self) -> int:
        return self.actor.stats.spd
