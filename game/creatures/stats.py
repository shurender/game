"""Stat blocks and stat calculation logic."""
import math
from dataclasses import dataclass

@dataclass
class Stats:
    hp: int
    atk: int
    def_: int  # def is a reserved keyword
    sp_atk: int
    sp_def: int
    spd: int

def calculate_max_hp(base: int, level: int) -> int:
    """Calculate maximum HP at a given level.
    Uses a simplified formula similar to classic RPGs.
    """
    return math.floor(0.01 * (2 * base) * level) + level + 10

def calculate_stat(base: int, level: int) -> int:
    """Calculate a non-HP stat at a given level."""
    return math.floor(0.01 * (2 * base) * level) + 5
