"""Damage and accuracy calculation logic."""
import math
import random
from typing import Tuple

from game.creatures.creature import Creature
from game.creatures.move import Move
from game.creatures.type_system import TypeSystem

def calculate_accuracy(move: Move) -> bool:
    """Determine if a move hits based on its accuracy."""
    if move.accuracy is None or move.accuracy >= 100:
        return True
    return random.randint(1, 100) <= move.accuracy

def calculate_damage(attacker: Creature, defender: Creature, move: Move) -> Tuple[int, float, bool]:
    """Calculate the damage dealt by a move.
    
    Returns:
        A tuple of (damage_amount, type_multiplier, is_critical)
    """
    if move.category == "Status" or move.power <= 0:
        return 0, 1.0, False
        
    # Get relevant attack/defense stats based on category
    if move.category == "Physical":
        atk = attacker.stats.atk
        def_ = defender.stats.def_
    else:  # Special
        atk = attacker.stats.sp_atk
        def_ = defender.stats.sp_def
        
    # Standard RPG damage formula
    level_factor = (2 * attacker.level) / 5 + 2
    base_damage = (level_factor * move.power * (atk / def_)) / 50 + 2
    
    # Critical Hit (approx 1/16 chance = 6.25%)
    is_critical = random.randint(1, 16) == 1
    crit_multiplier = 1.5 if is_critical else 1.0
    
    # Same Type Attack Bonus (STAB)
    stab = 1.5 if move.type in attacker.types else 1.0
    
    # Type Effectiveness
    type_system = TypeSystem.get_instance()
    effectiveness = type_system.get_effectiveness(move.type, defender.types)
    
    # Random variance (85% to 100%)
    variance = random.uniform(0.85, 1.0)
    
    final_damage = math.floor(base_damage * crit_multiplier * stab * effectiveness * variance)
    
    # Ensure at least 1 damage if effectiveness > 0
    if effectiveness > 0 and final_damage == 0:
        final_damage = 1
        
    return final_damage, effectiveness, is_critical
