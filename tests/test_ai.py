import pytest
from unittest.mock import patch
from game.creatures.creature import Creature, Species
from game.creatures.move import Move
from game.battle.battle import Battle
from game.battle.ai import BattleAI
from game.creatures.type_system import TypeSystem

@pytest.fixture
def mock_type_system():
    class MockTypeSystem:
        def get_effectiveness(self, move_type, defender_types):
            if move_type == "Fire" and "Water" in defender_types:
                return 0.5
            if move_type == "Water" and "Fire" in defender_types:
                return 2.0
            return 1.0
    
    original = TypeSystem.get_instance
    TypeSystem.get_instance = lambda: MockTypeSystem()
    yield
    TypeSystem.get_instance = original


@pytest.fixture
def dummy_species():
    return Species(
        species_id="test",
        name="TestMon",
        types=["Normal"],
        base_stats={"hp": 100, "atk": 50, "def": 50, "sp_atk": 50, "sp_def": 50, "spd": 50},
        description="A test creature"
    )


@pytest.fixture
def fire_species():
    return Species(
        species_id="fire",
        name="FireMon",
        types=["Fire"],
        base_stats={"hp": 100, "atk": 50, "def": 50, "sp_atk": 50, "sp_def": 50, "spd": 50},
        description="A fire creature"
    )

def test_ai_random(dummy_species):
    ai = BattleAI(ai_type="RANDOM")
    actor = Creature(dummy_species, level=5)
    target = Creature(dummy_species, level=5)
    
    # Needs valid move IDs to mock factory or directly patch
    with patch("game.creatures.move.MoveFactory.get_instance") as mock_factory_method:
        mock_factory = mock_factory_method.return_value
        m1 = Move("m1", "Move1", "Normal", "Physical", 40, 100, 10, 10, 0, "")
        m2 = Move("m2", "Move2", "Fire", "Physical", 60, 100, 10, 10, 0, "")
        
        def mock_get_move(m_id):
            return m1 if m_id == "m1" else m2
        mock_factory.get_move.side_effect = mock_get_move
        
        actor.moves = ["m1", "m2"]
        
        # Test random AI doesn't crash and returns a move action
        action = ai.choose_action(None, actor, target)
        assert action.action_type == "MOVE"
        assert action.move.move_id in ["m1", "m2"]


def test_ai_type_aware(mock_type_system, dummy_species, fire_species):
    ai = BattleAI(ai_type="BASIC")
    actor = Creature(dummy_species, level=5)
    target = Creature(fire_species, level=5) # Target is Fire type
    
    with patch("game.creatures.move.MoveFactory.get_instance") as mock_factory_method:
        mock_factory = mock_factory_method.return_value
        
        m_normal = Move("m_normal", "Tackle", "Normal", "Physical", 40, 100, 10, 10, 0, "")
        m_water = Move("m_water", "Water Gun", "Water", "Special", 40, 100, 10, 10, 0, "")
        
        def mock_get_move(m_id):
            return m_normal if m_id == "m_normal" else m_water
            
        mock_factory.get_move.side_effect = mock_get_move
        actor.moves = ["m_normal", "m_water"]
        
        # Patch random to always pick the best move (avoid the 20% random chance)
        with patch("random.random", return_value=0.5):
            action = ai.choose_action(None, actor, target)
            assert action.action_type == "MOVE"
            # Water move should be chosen because it's super effective (2.0) against Fire
            # Water score = 40 * 2.0 = 80
            # Normal score = 40 * 1.0 = 40
            assert action.move.move_id == "m_water"


def test_ai_low_hp(dummy_species):
    ai = BattleAI(ai_type="BASIC")
    actor = Creature(dummy_species, level=5)
    target = Creature(dummy_species, level=5)
    actor.moves = ["m1"]
    
    # Set HP to critical level (10%)
    actor.current_hp = 10 
    actor.stats.hp = 100
    
    with patch("game.creatures.move.MoveFactory.get_instance") as mock_factory_method:
        mock_factory = mock_factory_method.return_value
        mock_factory.get_move.return_value = Move("m1", "Tackle", "Normal", "Physical", 40, 100, 10, 10, 0, "")
        
        # Patch random to trigger the 15% escape chance
        with patch("random.random", return_value=0.1):
            action = ai.choose_action(None, actor, target)
            assert action.action_type == "ESCAPE"
