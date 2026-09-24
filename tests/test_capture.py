import pytest
from unittest.mock import patch
from game.creatures.creature import Creature, Species
from game.player.party import PartyManager
from game.battle.capture import (
    CaptureItem, 
    calculate_capture, 
    execute_capture,
    BASIC_BALL,
    MASTER_BALL
)
from game.battle.status_effects import StatusEffect


@pytest.fixture
def dummy_species():
    species = Species(
        species_id="test",
        name="TestMon",
        types=["Normal"],
        base_stats={"hp": 100, "atk": 50, "def": 50, "sp_atk": 50, "sp_def": 50, "spd": 50},
        description="A test creature"
    )
    species.catch_rate = 100
    return species


@pytest.fixture
def party_manager():
    pm = PartyManager.get_instance()
    pm.clear()
    return pm


def test_capture_probability_hp_modifier(dummy_species):
    creature_full_hp = Creature(dummy_species, level=5)
    creature_low_hp = Creature(dummy_species, level=5)
    creature_low_hp.current_hp = 10
    
    # We patch random to always fail if the threshold isn't met, to reliably test the calculation variables
    # Let's just check the returned shakes
    with patch("random.randint", return_value=30000):
        _, shakes_full = calculate_capture(creature_full_hp, BASIC_BALL)
        _, shakes_low = calculate_capture(creature_low_hp, BASIC_BALL)
        
        # Lower HP should yield higher catch rate, so higher shakes (or success)
        assert shakes_low >= shakes_full


def test_capture_probability_status_modifier(dummy_species):
    creature_normal = Creature(dummy_species, level=5)
    creature_normal.current_hp = 50
    
    creature_sleep = Creature(dummy_species, level=5)
    creature_sleep.current_hp = 50
    creature_sleep.status = StatusEffect.SLEEP
    
    with patch("random.randint", return_value=40000):
        _, shakes_normal = calculate_capture(creature_normal, BASIC_BALL)
        _, shakes_sleep = calculate_capture(creature_sleep, BASIC_BALL)
        
        # Sleep gives a 2.0x modifier, resulting in higher shakes
        assert shakes_sleep >= shakes_normal


def test_master_ball(dummy_species):
    creature = Creature(dummy_species, level=100)
    creature.current_hp = creature.stats.hp # Full HP, hardest to catch
    
    success, shakes = calculate_capture(creature, MASTER_BALL)
    assert success is True
    assert shakes == 3


def test_party_and_storage_behavior(dummy_species, party_manager):
    # Fill the party (max 6)
    for _ in range(6):
        c = Creature(dummy_species, level=5)
        success, shakes, location = execute_capture(c, MASTER_BALL)
        assert success is True
        assert location == "PARTY"
        
    assert len(party_manager.party) == 6
    assert len(party_manager.storage) == 0
    
    # 7th creature should go to storage
    c7 = Creature(dummy_species, level=5)
    success, shakes, location = execute_capture(c7, MASTER_BALL)
    
    assert success is True
    assert location == "STORAGE"
    assert len(party_manager.party) == 6
    assert len(party_manager.storage) == 1
