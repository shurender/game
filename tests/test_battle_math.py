"""Tests for move parsing and damage calculations."""
import pytest
from unittest.mock import patch

from game.creatures.type_system import TypeSystem
from game.creatures.move import MoveFactory
from game.creatures.damage import calculate_damage
from game.creatures.creature_factory import CreatureFactory


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

MOCK_MOVES = {
    "moves": {
        "M1": {
            "name": "Tackle",
            "type": "Normal",
            "category": "Physical",
            "power": 40,
            "accuracy": 100,
            "pp": 35
        },
        "M2": {
            "name": "Water Splash",
            "type": "Tide",
            "category": "Special",
            "power": 40,
            "accuracy": 100,
            "pp": 25
        },
        "M3": {
            "name": "Growl",
            "type": "Normal",
            "category": "Status",
            "power": 0,
            "accuracy": 100,
            "pp": 40
        }
    }
}

MOCK_CREATURES = {
    "creatures": {
        "C1": {
            "name": "Ignipup",
            "type": ["Ember"],
            "base_stats": {
                "hp": 45, "atk": 60, "def": 40, "sp_atk": 50, "sp_def": 40, "spd": 65
            }
        },
        "C3": {
            "name": "Aquabip",
            "type": ["Tide"],
            "base_stats": {
                "hp": 55, "atk": 45, "def": 55, "sp_atk": 65, "sp_def": 55, "spd": 40
            }
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
        elif filename == "moves.json":
            return MOCK_MOVES
        return {}
        
    with patch("game.creatures.type_system.load_json_file", side_effect=mock_load):
        with patch("game.creatures.move.load_json_file", side_effect=mock_load):
            with patch("game.creatures.creature_factory.load_json_file", side_effect=mock_load):
                yield


def test_type_effectiveness_messages(mock_json_loader):
    TypeSystem._instance = None
    ts = TypeSystem.get_instance()
    
    assert ts.get_effectiveness_message(2.0) == "It's super effective!"
    assert ts.get_effectiveness_message(0.5) == "It's not very effective..."
    assert ts.get_effectiveness_message(1.0) == ""
    assert ts.get_effectiveness_message(0.0) == "It has no effect..."
    
    
def test_move_factory(mock_json_loader):
    MoveFactory._instance = None
    factory = MoveFactory.get_instance()
    
    m1 = factory.get_move("M1")
    assert m1.name == "Tackle"
    assert m1.type == "Normal"
    assert m1.category == "Physical"
    assert m1.pp == 35
    assert m1.max_pp == 35
    
    
@patch("random.uniform", return_value=1.0)
def test_calculate_damage(mock_uniform, mock_json_loader):
    TypeSystem._instance = None
    CreatureFactory._instance = None
    MoveFactory._instance = None
    
    c_factory = CreatureFactory.get_instance()
    m_factory = MoveFactory.get_instance()
    
    attacker = c_factory.create_creature("C3", 5) # Tide
    defender = c_factory.create_creature("C1", 5) # Ember
    
    # Status move
    status_move = m_factory.get_move("M3")
    dmg, eff = calculate_damage(attacker, defender, status_move)
    assert dmg == 0
    assert eff == 1.0
    
    # Special move with STAB and Super Effective
    # Tide vs Ember is 2.0x
    water_move = m_factory.get_move("M2")
    dmg, eff = calculate_damage(attacker, defender, water_move)
    assert eff == 2.0
    assert dmg > 0
    
    # Physical move Neutral, no STAB
    tackle = m_factory.get_move("M1")
    dmg2, eff2 = calculate_damage(attacker, defender, tackle)
    assert eff2 == 1.0
    assert dmg2 > 0
