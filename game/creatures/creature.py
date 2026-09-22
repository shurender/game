"""Creature base species data and individual instance state."""
import math
from typing import Optional

from game.creatures.stats import Stats, calculate_max_hp, calculate_stat
from game.creatures.status_effects import StatusEffect
from game.creatures.type_system import TypeSystem


class Species:
    """Immutable base data for a creature species."""
    def __init__(self, species_id: str, name: str, types: list[str], 
                 base_stats: dict, description: str):
        self.species_id = species_id
        self.name = name
        self.types = types
        self.description = description
        
        self.base_stats = Stats(
            hp=base_stats.get("hp", 10),
            atk=base_stats.get("atk", 10),
            def_=base_stats.get("def", 10),
            sp_atk=base_stats.get("sp_atk", 10),
            sp_def=base_stats.get("sp_def", 10),
            spd=base_stats.get("spd", 10)
        )


class Creature:
    """An individual instance of a creature species."""
    
    def __init__(self, species: Species, level: int, nickname: str = None):
        self.species = species
        self.nickname = nickname or species.name
        self._level = level
        self.xp = self._calculate_xp_for_level(level)
        
        # Current state
        self.status = StatusEffect.NONE
        self.moves: list[str] = []  # List of move IDs
        
        # Calculate max stats
        self.stats = self._recalculate_stats()
        self.current_hp = self.stats.hp
        
    @property
    def name(self) -> str:
        return self.nickname
        
    @property
    def level(self) -> int:
        return self._level
        
    @property
    def types(self) -> list[str]:
        return self.species.types
        
    def _calculate_xp_for_level(self, level: int) -> int:
        """Calculate total XP required to reach a level (Medium Fast curve)."""
        return int(level ** 3)
        
    def _recalculate_stats(self) -> Stats:
        """Recalculate max stats based on current level and base stats."""
        base = self.species.base_stats
        lvl = self._level
        return Stats(
            hp=calculate_max_hp(base.hp, lvl),
            atk=calculate_stat(base.atk, lvl),
            def_=calculate_stat(base.def_, lvl),
            sp_atk=calculate_stat(base.sp_atk, lvl),
            sp_def=calculate_stat(base.sp_def, lvl),
            spd=calculate_stat(base.spd, lvl)
        )
        
    def add_xp(self, amount: int) -> bool:
        """Add XP to the creature. Returns True if the creature leveled up."""
        if self._level >= 100:
            return False
            
        self.xp += amount
        leveled_up = False
        
        while self._level < 100 and self.xp >= self._calculate_xp_for_level(self._level + 1):
            self._level += 1
            leveled_up = True
            
        if leveled_up:
            old_max_hp = self.stats.hp
            self.stats = self._recalculate_stats()
            # Heal the HP gained from leveling up
            hp_diff = self.stats.hp - old_max_hp
            self.current_hp = min(self.stats.hp, self.current_hp + hp_diff)
            
        return leveled_up

    def heal(self, amount: int) -> None:
        """Heal the creature by an amount, capped at max HP."""
        self.current_hp = min(self.stats.hp, self.current_hp + amount)
        
    def take_damage(self, amount: int) -> None:
        """Reduce HP by an amount, capped at 0."""
        self.current_hp = max(0, self.current_hp - amount)
        
    @property
    def is_fainted(self) -> bool:
        return self.current_hp <= 0
