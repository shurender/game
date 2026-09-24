"""Comprehensive tests for Creature stats, XP curves, leveling, and evolution."""
import math
import pytest
from unittest.mock import patch

from game.creatures.stats import Stats, calculate_max_hp, calculate_stat
from game.creatures.creature import Species, Creature
from game.creatures.status_effects import StatusEffect
from game.creatures.progression import (
    xp_for_level,
    award_xp,
    evolve,
    calculate_battle_xp,
    check_condition,
)
from game.inventory.inventory import Inventory


@pytest.fixture
def mock_species_base():
    return Species(
        species_id="SP1",
        name="FlamePup",
        types=["Ember"],
        base_stats={"hp": 45, "atk": 55, "def": 40, "sp_atk": 50, "sp_def": 40, "spd": 60},
        description="A fiery pup."
    )


@pytest.fixture
def mock_species_evo():
    return Species(
        species_id="SP2",
        name="BlazeHound",
        types=["Ember"],
        base_stats={"hp": 70, "atk": 85, "def": 65, "sp_atk": 75, "sp_def": 65, "spd": 90},
        description="A blazing hound."
    )


# =============================================================================
# Stat Calculation & Scaling Tests
# =============================================================================

def test_stat_formula_exact_values():
    """Verify that calculate_max_hp and calculate_stat match formulas across levels."""
    base_hp = 50
    base_atk = 60

    for lvl in [1, 5, 25, 50, 100]:
        expected_hp = math.floor(0.01 * (2 * base_hp) * lvl) + lvl + 10
        expected_atk = math.floor(0.01 * (2 * base_atk) * lvl) + 5
        assert calculate_max_hp(base_hp, lvl) == expected_hp
        assert calculate_stat(base_atk, lvl) == expected_atk


def test_creature_all_six_stats_initialized(mock_species_base):
    """Creature instance accurately initializes all 6 stats from species base stats."""
    c = Creature(mock_species_base, level=10)
    assert c.stats.hp == calculate_max_hp(45, 10)
    assert c.stats.atk == calculate_stat(55, 10)
    assert c.stats.def_ == calculate_stat(40, 10)
    assert c.stats.sp_atk == calculate_stat(50, 10)
    assert c.stats.sp_def == calculate_stat(40, 10)
    assert c.stats.spd == calculate_stat(60, 10)
    assert c.current_hp == c.stats.hp


def test_nickname_handling(mock_species_base):
    """Creature name defaults to species name, or custom nickname if provided."""
    c_default = Creature(mock_species_base, level=5)
    assert c_default.name == "FlamePup"

    c_nick = Creature(mock_species_base, level=5, nickname="Sparky")
    assert c_nick.name == "Sparky"


# =============================================================================
# XP and Curve Tests
# =============================================================================

def test_xp_curve_calculations():
    """xp_for_level adheres to the cubic curve."""
    assert xp_for_level(1, "medium_fast") == 1
    assert xp_for_level(5, "medium_fast") == 125
    assert xp_for_level(10, "medium_fast") == 1000
    assert xp_for_level(50, "medium_fast") == 125000
    assert xp_for_level(100, "medium_fast") == 1000000


def test_calculate_battle_xp_differential():
    """calculate_battle_xp scales proportionally based on defeated vs winner level."""
    defeated = {"xp_yield": 80, "level": 10}

    # Same level: multiplier is 1.0 -> 80
    assert calculate_battle_xp(defeated, winner_level=10) == 80
    # Winner is double the level: multiplier 0.5 -> 40
    assert calculate_battle_xp(defeated, winner_level=20) == 40
    # Winner is half the level: multiplier 2.0 -> 160
    assert calculate_battle_xp(defeated, winner_level=5) == 160


# =============================================================================
# Leveling Tests
# =============================================================================

def test_single_and_multi_level_up(mock_species_base):
    """Adding XP triggers single or multiple level-ups and recalculates stats."""
    c = Creature(mock_species_base, level=5) # 125 XP
    initial_atk = c.stats.atk

    # Level 6 requires 6^3 = 216 XP (diff = 91)
    leveled = c.add_xp(50)
    assert not leveled
    assert c.level == 5

    leveled = c.add_xp(50) # total added 100 -> 225 XP
    assert leveled
    assert c.level == 6
    assert c.stats.atk > initial_atk

    # Big XP jump: level 10 requires 1000 XP
    leveled = c.add_xp(1000)
    assert leveled
    assert c.level == 10


def test_level_up_preserves_damage_difference(mock_species_base):
    """When a damaged creature levels up, its current HP increases by the gained max HP."""
    c = Creature(mock_species_base, level=5)
    max_5 = c.stats.hp
    c.take_damage(10)
    assert c.current_hp == max_5 - 10

    # Level up to 6
    c.add_xp(100)
    assert c.level == 6
    max_6 = c.stats.hp
    hp_gain = max_6 - max_5
    assert c.current_hp == (max_5 - 10) + hp_gain


def test_level_cap_100(mock_species_base):
    """Creature cannot level beyond 100."""
    c = Creature(mock_species_base, level=100)
    assert c.add_xp(500000) is False
    assert c.level == 100


def test_award_xp_with_learnset(mock_species_base):
    """award_xp returns level-up result with moves learned according to learnset."""
    c = Creature(mock_species_base, level=4)
    species_data = {
        "xp_curve": "medium_fast",
        "learnset": [
            {"level": 5, "move": "EMBER_BITE"},
            {"level": 8, "move": "FLAME_CHARGE"},
        ],
        "evolution": None,
    }

    # Level up to 5
    res = award_xp(c, (5**3) - (4**3), species_data)
    assert c.level == 5
    assert len(res.level_ups) == 1
    assert "EMBER_BITE" in res.level_ups[0].moves_learned
    assert "FLAME_CHARGE" not in res.level_ups[0].moves_learned


# =============================================================================
# Evolution Tests
# =============================================================================

def test_evolution_conditions(mock_species_base):
    """check_condition detects level and item conditions accurately."""
    c = Creature(mock_species_base, level=15)

    level_evo = {"condition": "level", "level": 16, "target": "SP2"}
    assert check_condition(c, level_evo, {}) is False

    c_16 = Creature(mock_species_base, level=16)
    assert check_condition(c_16, level_evo, {}) is True

    # Item condition
    item_evo = {"condition": "item", "item_id": "potion", "target": "SP2"}
    inv = Inventory()
    assert check_condition(c, item_evo, {"inventory": inv}) is False

    inv.add("potion", 1)
    assert check_condition(c, item_evo, {"inventory": inv}) is True


def test_evolve_execution(mock_species_base, mock_species_evo):
    """evolve() updates species ID, base stats, learnset moves, and names."""
    c = Creature(mock_species_base, level=16)
    old_hp = c.stats.hp
    old_atk = c.stats.atk

    old_data = {
        "name": "FlamePup",
        "learnset": [{"level": 1, "move": "TACKLE"}]
    }
    new_data = {
        "name": "BlazeHound",
        "learnset": [
            {"level": 1, "move": "TACKLE"},
            {"level": 1, "move": "FIRE_BLAST"},
            {"level": 30, "move": "INFERNO"},
        ]
    }

    res = evolve(c, old_data, "SP2", new_data, mock_species_evo)

    assert c.species.species_id == "SP2"
    assert c.name == "BlazeHound"
    assert res.new_name == "BlazeHound"
    # Stats increase because SP2 has higher base stats
    assert c.stats.hp > old_hp
    assert c.stats.atk > old_atk
    # Learned level <= 1 move not already known, but not level 30 move
    assert "FIRE_BLAST" in res.moves_learned
    assert "INFERNO" not in res.moves_learned


def test_evolve_preserves_custom_nickname(mock_species_base, mock_species_evo):
    """If a creature has a custom nickname, evolution preserves it on the creature."""
    c = Creature(mock_species_base, level=16, nickname="Fido")
    old_data = {"name": "FlamePup", "learnset": []}
    new_data = {"name": "BlazeHound", "learnset": []}
    res = evolve(c, old_data, "SP2", new_data, mock_species_evo)
    assert c.name == "Fido"
    assert res.new_name == "BlazeHound"
    assert res.old_name == "Fido"
