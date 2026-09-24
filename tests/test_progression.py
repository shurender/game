"""Tests for XP, levelling, and evolution logic."""
import pytest
from unittest.mock import patch

from game.creatures.progression import (
    xp_for_level, award_xp, evolve, calculate_battle_xp,
    check_condition
)
from game.creatures.creature import Species, Creature
from game.inventory.inventory import Inventory

# ── Mock Data ─────────────────────────────────────────────────────────────────

MOCK_SPECIES = {
    "C1": {
        "name": "Ignipup",
        "xp_curve": "medium_fast",
        "xp_yield": 64,
        "learnset": [
            {"level": 1, "move": "M1"},
            {"level": 5, "move": "M2"}
        ],
        "evolution": {
            "condition": "level",
            "level": 16,
            "target": "C2"
        },
        "base_stats": {"hp": 45, "atk": 60, "def": 40, "sp_atk": 50, "sp_def": 40, "spd": 65}
    },
    "C2": {
        "name": "Blazehound",
        "learnset": [
            {"level": 1, "move": "M1"},
            {"level": 1, "move": "M2"},
            {"level": 20, "move": "M3"}
        ],
        "base_stats": {"hp": 65, "atk": 85, "def": 60, "sp_atk": 70, "sp_def": 60, "spd": 90}
    },
    "C3": {
        "name": "EvoItem",
        "evolution": {
            "condition": "item",
            "item_id": "potion",
            "target": "C4"
        },
        "base_stats": {"hp": 10, "atk": 10, "def": 10, "sp_atk": 10, "sp_def": 10, "spd": 10}
    },
    "C4": {
        "name": "EvolvedItem",
        "base_stats": {"hp": 20, "atk": 20, "def": 20, "sp_atk": 20, "sp_def": 20, "spd": 20}
    }
}

@pytest.fixture
def ignipup_species():
    data = MOCK_SPECIES["C1"]
    s = Species("C1", data["name"], ["Ember"], data["base_stats"], "")
    s.xp_curve = data["xp_curve"]
    s.xp_yield = data["xp_yield"]
    s.learnset = data["learnset"]
    s.evolution_data = data["evolution"]
    return s

@pytest.fixture
def blazehound_species():
    data = MOCK_SPECIES["C2"]
    s = Species("C2", data["name"], ["Ember"], data["base_stats"], "")
    return s

@pytest.fixture
def item_evo_species():
    data = MOCK_SPECIES["C3"]
    s = Species("C3", data["name"], ["Normal"], data["base_stats"], "")
    return s

# ── Tests ─────────────────────────────────────────────────────────────────────

def test_xp_for_level():
    assert xp_for_level(5, "medium_fast") == 125
    assert xp_for_level(10, "medium_fast") == 1000

def test_award_xp_no_level_up(ignipup_species):
    c = Creature(ignipup_species, 5) # 125 XP
    res = award_xp(c, 10, MOCK_SPECIES["C1"])
    assert c.level == 5
    assert c.xp == 135
    assert len(res.level_ups) == 0
    assert not res.pending_evolution

def test_award_xp_with_level_up(ignipup_species):
    c = Creature(ignipup_species, 5) # 125 XP
    next_level_xp = 6**3 # 216
    needed = next_level_xp - 125
    
    res = award_xp(c, needed, MOCK_SPECIES["C1"])
    assert c.level == 6
    assert len(res.level_ups) == 1
    assert res.level_ups[0].new_level == 6

def test_award_xp_multiple_level_ups(ignipup_species):
    c = Creature(ignipup_species, 5)
    needed = (10**3) - 125 # 875
    
    res = award_xp(c, needed, MOCK_SPECIES["C1"])
    assert c.level == 10
    assert len(res.level_ups) == 5

def test_evolution_condition_met(ignipup_species):
    c = Creature(ignipup_species, 15)
    needed = (16**3) - (15**3) # 4096 - 3375 = 721
    
    res = award_xp(c, needed, MOCK_SPECIES["C1"])
    assert c.level == 16
    assert res.pending_evolution is True
    assert res.evolution_target == "C2"

def test_item_evolution_condition(item_evo_species):
    c = Creature(item_evo_species, 5)
    inv = Inventory()
    inv.add("potion", 1)
    
    res = check_condition(c, MOCK_SPECIES["C3"]["evolution"], {"inventory": inv})
    assert res is True
    
    inv.remove("potion", 1)
    res2 = check_condition(c, MOCK_SPECIES["C3"]["evolution"], {"inventory": inv})
    assert res2 is False

def test_evolve(ignipup_species, blazehound_species):
    c = Creature(ignipup_species, 16)
    
    res = evolve(c, MOCK_SPECIES["C1"], "C2", MOCK_SPECIES["C2"], blazehound_species)
    
    assert c.species.species_id == "C2"
    assert c.name == "Blazehound" # Assuming no nickname
    assert res.new_name == "Blazehound"
    assert "M1" in res.moves_learned or "M2" in res.moves_learned # Depending on how it's filtered
    assert "M3" not in res.moves_learned # Level 20 move

def test_battle_xp_calculation():
    defeated = {"xp_yield": 64, "level": 10}
    # winner level 10: base * 1.0 = 64
    assert calculate_battle_xp(defeated, 10) == 64
    # winner level 20: base * 0.5 = 32
    assert calculate_battle_xp(defeated, 20) == 32
    # winner level 5: base * 2.0 = 128
    assert calculate_battle_xp(defeated, 5) == 128
