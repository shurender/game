"""Battle AI for deciding enemy actions."""
import random

from game.battle.battle import Battle
from game.battle.battle_action import BattleAction
from game.creatures.creature import Creature
from game.creatures.move import MoveFactory
from game.creatures.type_system import TypeSystem


class BattleAI:
    def __init__(self, ai_type: str = "BASIC"):
        """Initialize the AI.
        
        Args:
            ai_type: Strategy to use. "RANDOM" or "BASIC" (Type-aware).
        """
        self.ai_type = ai_type
        
    def choose_action(self, battle: Battle, actor: Creature, target: Creature) -> BattleAction:
        """Determines the action for the enemy creature to take."""
        
        hp_percent = actor.current_hp / actor.stats.hp
        
        # Low HP behavior: slight chance to attempt escape
        # (Could also switch if party support existed)
        if hp_percent < 0.2 and random.random() < 0.15:
            return BattleAction(actor, "ESCAPE")
            
        mf = MoveFactory.get_instance()
        available_moves = []
        for m_id in actor.moves:
            available_moves.append(mf.get_move(m_id))
            
        if not available_moves:
            # Degrade gracefully: no moves available → attempt to flee rather than deadlock
            return BattleAction(actor, "ESCAPE")

            
        if self.ai_type == "RANDOM":
            selected_move = random.choice(available_moves)
            return BattleAction(actor, "MOVE", target=target, move=selected_move)
            
        # Default to BASIC (Type-aware)
        return self._choose_type_aware_move(actor, target, available_moves)
        
    def _choose_type_aware_move(self, actor: Creature, target: Creature, available_moves: list) -> BattleAction:
        type_system = TypeSystem.get_instance()
        
        best_move = None
        best_score = -1.0
        
        for move in available_moves:
            if move.category == "Status":
                # Moderate score for status moves, so they are sometimes used
                score = 40.0
            else:
                effectiveness = type_system.get_effectiveness(move.type, target.types)
                score = move.power * effectiveness
                
                # STAB (Same Type Attack Bonus) anticipation
                if move.type in actor.types:
                    score *= 1.5
                    
            if score > best_score:
                best_score = score
                best_move = move
                
        # 20% chance to pick randomly anyway, to avoid being 100% predictable
        if random.random() < 0.2:
            best_move = random.choice(available_moves)
            
        return BattleAction(actor, "MOVE", target=target, move=best_move)
