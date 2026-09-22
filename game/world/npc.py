"""Non-Player Characters (NPCs) placed in the world."""
from __future__ import annotations

from game.player.player import Direction

class NPC:
    """A character in the overworld that can be interacted with."""
    
    def __init__(self, npc_id: str, name: str, x: int, y: int, sprite_name: str, 
                 facing: Direction, dialogue_id: str):
        self.npc_id = npc_id
        self.name = name
        self.x = x
        self.y = y
        self.sprite_name = sprite_name
        self.facing = facing
        self.dialogue_id = dialogue_id
        
        # Interactions
        self.interaction_range = 1
        
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
