"""Non-Player Characters (NPCs) placed in the world."""
from __future__ import annotations

from game.player.player import Direction

class NPC:
    """A character in the overworld that can be interacted with."""
    
    def __init__(self, npc_id: str, name: str, x: int, y: int, sprite_name: str, 
                 facing: Direction, dialogue_id: str):
        self.npc_id = npc_id
        self.id = npc_id
        self.name = name
        self.x = x
        self.y = y
        self.sprite_name = sprite_name
        self.facing = facing
        self.dialogue_id = dialogue_id
        self.conditional_dialogues = []
        
        # Interactions
        self.interaction_range = 1
        
    def get_current_dialogue(self) -> str:
        from game.world.progress_manager import WorldProgressManager
        pm = WorldProgressManager.get_instance()
        
        for cond_dial in self.conditional_dialogues:
            if pm.check_conditions(cond_dial.get("conditions", {})):
                return cond_dial["dialogue_id"]
                
        return self.dialogue_id
        
    def face_player(self, player_x: int, player_y: int) -> None:
        """Turn to face the player when interacted with."""
        if player_x > self.x:
            self.facing = Direction.RIGHT
        elif player_x < self.x:
            self.facing = Direction.LEFT
        elif player_y > self.y:
            self.facing = Direction.DOWN
        elif player_y < self.y:
            self.facing = Direction.UP
