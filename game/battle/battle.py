from typing import Optional
from game.creatures.creature import Creature

class Battle:
    """Holds the state of a single battle encounter."""
    def __init__(self, player_creature: Creature, enemy_creature: Creature):
        self.player_creature = player_creature
        self.enemy_creature = enemy_creature
        self.is_over = False
        self.winner: Optional[str] = None  # "PLAYER", "ENEMY", or "ESCAPE"
