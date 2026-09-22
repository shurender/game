"""Trainers in the overworld that can challenge the player."""
from __future__ import annotations

from game.world.npc import NPC
from game.player.player import Direction

class Trainer(NPC):
    """An NPC that also has a battle configuration."""
    
    def __init__(self, npc_id: str, name: str, x: int, y: int, sprite_name: str, 
                 facing: Direction, dialogue_id: str, trainer_data: dict):
        super().__init__(npc_id, name, x, y, sprite_name, facing, dialogue_id)
        
        self.trainer_data = trainer_data
        self.has_battled = False
        self.sight_range = trainer_data.get("sight_range", 4)
