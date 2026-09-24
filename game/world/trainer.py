"""Trainers in the overworld that can challenge the player."""
from __future__ import annotations

from game.world.npc import NPC
from game.player.player import Direction

class Trainer(NPC):
    """An NPC that also has a battle configuration."""
    
    def __init__(self, npc_id: str, name: str, x: int, y: int, sprite_name: str, 
                 facing: Direction, dialogue_id: str, trainer_id: str):
        super().__init__(npc_id, name, x, y, sprite_name, facing, dialogue_id)
        
        self.trainer_id = trainer_id
        
        from game.world.trainer_factory import TrainerFactory
        tf = TrainerFactory.get_instance()
        self.trainer_data = tf.get_trainer_data(trainer_id) or {}
        
        self.has_battled = False
        self.sight_range = self.trainer_data.get("sight_range", 4)
