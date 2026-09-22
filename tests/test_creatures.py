"""Tests for the creature domain model."""
import pytest
from unittest.mock import patch

from game.creatures.stats import calculate_max_hp, calculate_stat, Stats
from game.creatures.status_effects import StatusEffect
from game.creatures.creature import Species, Creature
from game.creatures.creature_factory import CreatureFactory
from game.creatures.type_system import TypeSystem


MOCK_CREATURES = {
    "creatures": {
        "C1": {
            "name": "Ignipup",
            "type": ["Ember"],
            "base_stats": {
                "hp": 45,
                "atk": 60,
                "def": 40,
                "sp_atk": 50,
                "sp_def": 40,
                "spd": 65
            }
        }
    }
}

MOCK_TYPES = {
    "types": ["Normal", "Ember", "Tide"],
    "matchups": {
        "Ember": {
            "Tide": 0.5,
            "Normal": 1.0
        },
        "Tide": {
            "Ember": 2.0
        }
    }
}


@pytest.fixture
def mock_json_loader():
    def mock_load(filename):
        if filename == "creatures.json":
            return MOCK_CREATURES
        elif filename == "types.json":
            return MOCK_TYPES
        return {}
        
    with patch("game.creatures.creature_factory.load_json_file", side_effect=mock_load):
        with patch("game.creatures.type_system.load_json_file", side_effect=mock_load):
            yield


def test_stat_calculations():
    # Base 45 at level 5
    hp = calculate_max_hp(45, 5)
    assert hp > 0
    # Base 60 at level 5
    atk = calculate_stat(60, 5)
    assert atk > 0


def test_type_system_effectiveness(mock_json_loader):
    # Reset singleton for tests
    TypeSystem._instance = None
    ts = TypeSystem.get_instance()
    
    # Ember attacking Tide should be 0.5x
    assert ts.get_effectiveness("Ember", ["Tide"]) == 0.5
    # Tide attacking Ember should be 2.0x
    assert ts.get_effectiveness("Tide", ["Ember"]) == 2.0
    # Unspecified matchup is 1.0x
    assert ts.get_effectiveness("Ember", ["Normal"]) == 1.0
    

def test_creature_creation(mock_json_loader):
    # Reset singleton for tests
    CreatureFactory._instance = None
    factory = CreatureFactory.get_instance()
    
    creature = factory.create_creature("C1", 5)
    assert creature.name == "Ignipup"
    assert creature.level == 5
    assert creature.types == ["Ember"]
    assert creature.status == StatusEffect.NONE
    assert creature.current_hp == creature.stats.hp
    
    
def test_creature_leveling_and_xp(mock_json_loader):
    CreatureFactory._instance = None
    factory = CreatureFactory.get_instance()
    
    creature = factory.create_creature("C1", 5)
    
    # Need 6^3 = 216 total XP for level 6
    # Currently at 5^3 = 125 XP. Difference is 91.
    leveled_up = creature.add_xp(50)
    assert not leveled_up
    assert creature.level == 5
    
    leveled_up = creature.add_xp(50) # +100 total, crosses 91 threshold
    assert leveled_up
    assert creature.level == 6
    
    # Test HP healed on level up
    old_hp = creature.current_hp
    assert old_hp == creature.stats.hp


def test_creature_damage_and_heal(mock_json_loader):
    CreatureFactory._instance = None
    factory = CreatureFactory.get_instance()
    
    creature = factory.create_creature("C1", 5)
    max_hp = creature.stats.hp
    
    creature.take_damage(10)
    assert creature.current_hp == max_hp - 10
    assert not creature.is_fainted
    
    creature.take_damage(999)
    assert creature.current_hp == 0
    assert creature.is_fainted
    
    creature.heal(10)
    assert creature.current_hp == 10
    
    creature.heal(999)
    assert creature.current_hp == max_hp
