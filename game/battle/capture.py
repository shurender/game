"""Creature capture system logic."""
import random
import math
from dataclasses import dataclass
from typing import Tuple

from game.creatures.creature import Creature
from game.battle.status_effects import StatusEffect
from game.player.party import PartyManager


@dataclass
class CaptureItem:
    item_id: str
    name: str
    catch_rate_modifier: float

# Predefined standard items
BASIC_BALL = CaptureItem("basic_ball", "Basic Ball", 1.0)
GREAT_BALL = CaptureItem("great_ball", "Great Ball", 1.5)
ULTRA_BALL = CaptureItem("ultra_ball", "Ultra Ball", 2.0)
MASTER_BALL = CaptureItem("master_ball", "Master Ball", 255.0)


def calculate_capture(creature: Creature, item: CaptureItem) -> Tuple[bool, int]:
    """Calculate if a capture is successful independent of UI.
    
    Args:
        creature: The target creature to capture.
        item: The capture item used.
        
    Returns:
        A tuple of (success: bool, shakes: int).
        `shakes` is how many times the ball shakes before failing (0-3). 
        If success is True, `shakes` is 3.
    """
    if item.item_id == "master_ball":
        return True, 3
        
    base_rate = getattr(creature.species, "catch_rate", 100)
    
    # 1. HP modifier
    # (3 * max_hp - 2 * current_hp) / (3 * max_hp)
    hp_mod = (3 * creature.stats.hp - 2 * creature.current_hp) / (3 * creature.stats.hp)
    hp_mod = max(0.1, hp_mod)  # Safety bound
    
    # 2. Status modifier
    status_mod = 1.0
    if hasattr(creature, 'status'):
        if isinstance(creature.status, str):
            status_name = creature.status
        else:
            status_name = creature.status.name
            
        if status_name in ("SLEEP", "FREEZE"):
            status_mod = 2.0
        elif status_name in ("PARALYSIS", "POISON", "BURN"):
            status_mod = 1.5
            
    # Final rate `a`
    a = (base_rate * hp_mod * status_mod * item.catch_rate_modifier) / 255.0
    
    if a >= 1.0:
        return True, 3
        
    # Calculate shakes based on the Gen VI formula
    # b = 65536 * (a / 255)^0.25 (approximation)
    # Actually b = 1048560 / sqrt(sqrt(16711680 / A)) which simplifies to:
    b = 65536 * math.pow(a, 0.25)
    
    shakes = 0
    for _ in range(4):
        if random.randint(0, 65535) >= b:
            break
        shakes += 1
        
    if shakes >= 4:
        return True, 3
        
    return False, shakes


def execute_capture(creature: Creature, item: CaptureItem) -> Tuple[bool, int, str]:
    """Calculate capture and optionally add to party/storage.
    
    Returns:
        A tuple of (success, shakes, location).
        location is "PARTY", "STORAGE", or "NONE" (if failed).
    """
    success, shakes = calculate_capture(creature, item)
    location = "NONE"
    
    if success:
        # Heal creature before inserting
        creature.heal(creature.stats.hp)
        
        party_mgr = PartyManager.get_instance()
        location = party_mgr.add_creature(creature)
        
    return success, shakes, location
