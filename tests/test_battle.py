import pytest
from unittest.mock import patch
from game.creatures.creature import Creature, Species
from game.creatures.move import Move
from game.battle.battle import Battle
from game.battle.battle_action import BattleAction
from game.battle.battle_engine import BattleEngine
from game.battle.damage import calculate_damage, calculate_accuracy
from game.creatures.type_system import TypeSystem

@pytest.fixture
def mock_type_system():
    # Mocking a basic TypeSystem instance
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
def test_species():
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

@pytest.fixture
def water_species():
    return Species(
        species_id="water",
        name="WaterMon",
        types=["Water"],
        base_stats={"hp": 100, "atk": 50, "def": 50, "sp_atk": 50, "sp_def": 50, "spd": 50},
        description="A water creature"
    )

def create_move(power=40, accuracy=100, priority=0, type="Normal", category="Physical"):
    return Move(
        move_id="m1",
        name="TestMove",
        type=type,
        category=category,
        power=power,
        accuracy=accuracy,
        pp=10,
        max_pp=10,
        priority=priority,
        description="test"
    )

def test_damage_and_type_multipliers(mock_type_system, fire_species, water_species):
    attacker = Creature(water_species, level=5)
    defender = Creature(fire_species, level=5)
    move = create_move(type="Water") # Super effective

    with patch('random.randint', return_value=10): # No crit
        with patch('random.uniform', return_value=1.0): # Max variance
            damage, effectiveness, is_critical = calculate_damage(attacker, defender, move)
            assert effectiveness == 2.0
            assert damage > 0
            assert is_critical is False

def test_critical_hits(mock_type_system, test_species):
    attacker = Creature(test_species, level=5)
    defender = Creature(test_species, level=5)
    move = create_move()

    with patch('random.randint', return_value=1): # Crit
        with patch('random.uniform', return_value=1.0):
            damage_crit, eff, is_crit = calculate_damage(attacker, defender, move)
            assert is_crit is True

    with patch('random.randint', return_value=10): # No crit
        with patch('random.uniform', return_value=1.0):
            damage_no_crit, eff, is_crit = calculate_damage(attacker, defender, move)
            assert is_crit is False

    assert damage_crit > damage_no_crit

def test_accuracy():
    move_hit = create_move(accuracy=100)
    move_miss = create_move(accuracy=50)

    with patch('random.randint', return_value=50):
        assert calculate_accuracy(move_hit) is True
        assert calculate_accuracy(move_miss) is True
    
    with patch('random.randint', return_value=51):
        assert calculate_accuracy(move_hit) is True
        assert calculate_accuracy(move_miss) is False

def test_fainting(mock_type_system, test_species):
    player = Creature(test_species, level=5)
    enemy = Creature(test_species, level=5)
    
    battle = Battle(player, enemy)
    
    # Give player an overwhelming move
    move = create_move(power=999)
    action1 = BattleAction(actor=player, action_type="MOVE", target=enemy, move=move)
    action2 = BattleAction(actor=enemy, action_type="MOVE", target=player, move=create_move(power=0))
    
    with patch('random.randint', return_value=10): # No crit, no miss
        with patch('random.uniform', return_value=1.0):
            result = BattleEngine.process_turn(battle, action1, action2)
            
            assert enemy.is_fainted
            assert result.battle_ended
            assert result.winner == "PLAYER"
            
            # Find the faint event
            faint_events = [e for e in result.events if e.action_type == "FAINT"]
            assert len(faint_events) == 1
            assert faint_events[0].actor_name == enemy.name

def test_turn_ordering(mock_type_system, test_species):
    fast_creature = Creature(test_species, level=5)
    fast_creature.stats.spd = 100
    
    slow_creature = Creature(test_species, level=5)
    slow_creature.stats.spd = 10
    
    battle = Battle(fast_creature, slow_creature)
    
    move = create_move()
    action_fast = BattleAction(actor=fast_creature, action_type="MOVE", target=slow_creature, move=move)
    action_slow = BattleAction(actor=slow_creature, action_type="MOVE", target=fast_creature, move=move)
    
    result = BattleEngine.process_turn(battle, action_fast, action_slow)
    
    assert len(result.events) == 2
    assert result.events[0].actor_name == fast_creature.name
    
    # Priority override
    move_prio = create_move(priority=1)
    action_prio = BattleAction(actor=slow_creature, action_type="MOVE", target=fast_creature, move=move_prio)
    result = BattleEngine.process_turn(battle, action_fast, action_prio)
    assert result.events[0].actor_name == slow_creature.name
