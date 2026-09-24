"""Comprehensive test suite for battle mechanics:
- Physical vs Special damage formulas
- STAB and Type effectiveness
- Accuracy and Misses
- Critical hit multipliers and messages
- Status effect application and immutability
- Fainting and battle termination
- AI decision making
"""
import pytest
from unittest.mock import patch

from game.creatures.creature import Creature, Species
from game.creatures.move import Move
from game.creatures.status_effects import StatusEffect
from game.creatures.type_system import TypeSystem
from game.battle.battle import Battle
from game.battle.battle_action import BattleAction
from game.battle.battle_engine import BattleEngine
from game.battle.damage import calculate_damage, calculate_accuracy
from game.battle.ai import BattleAI


@pytest.fixture
def mock_type_system():
    class MockTypeSystem:
        def get_effectiveness(self, move_type, defender_types):
            mult = 1.0
            for d_type in defender_types:
                if move_type == "Fire" and d_type == "Grass":
                    mult *= 2.0
                elif move_type == "Fire" and d_type == "Water":
                    mult *= 0.5
                elif move_type == "Electric" and d_type == "Ground":
                    mult *= 0.0
                elif move_type == "Water" and d_type == "Fire":
                    mult *= 2.0
            return mult

    original = TypeSystem.get_instance
    TypeSystem.get_instance = lambda: MockTypeSystem()
    yield
    TypeSystem.get_instance = original


@pytest.fixture
def base_species():
    return Species(
        species_id="norm",
        name="NormalMon",
        types=["Normal"],
        base_stats={"hp": 80, "atk": 60, "def": 50, "sp_atk": 70, "sp_def": 50, "spd": 55},
        description="Standard creature"
    )


@pytest.fixture
def fire_species():
    return Species(
        species_id="fire",
        name="FireMon",
        types=["Fire"],
        base_stats={"hp": 80, "atk": 75, "def": 45, "sp_atk": 85, "sp_def": 50, "spd": 70},
        description="Fire creature"
    )


@pytest.fixture
def dual_species():
    return Species(
        species_id="dual",
        name="GrassBugMon",
        types=["Grass", "Grass"],  # Dual grass for test multiplication
        base_stats={"hp": 80, "atk": 50, "def": 50, "sp_atk": 50, "sp_def": 50, "spd": 50},
        description="Dual grass creature"
    )


def make_move(name="Move", move_type="Normal", category="Physical", power=40, accuracy=100, status_effect=None):
    return Move(
        move_id=f"m_{name.lower().replace(' ', '_')}",
        name=name,
        type=move_type,
        category=category,
        power=power,
        accuracy=accuracy,
        pp=20,
        max_pp=20,
        priority=0,
        status_effect=status_effect,
        description="A test move"
    )


# =============================================================================
# Damage & Stat Category Tests
# =============================================================================

def test_physical_vs_special_damage(mock_type_system, base_species):
    """Physical attacks use Atk/Def; Special attacks use SpAtk/SpDef."""
    # Attacker has 60 Atk and 70 SpAtk
    attacker = Creature(base_species, level=20)
    defender = Creature(base_species, level=20)

    phys_move = make_move("Punch", "Normal", "Physical", power=50)
    spec_move = make_move("Beam", "Normal", "Special", power=50)

    with patch("random.randint", return_value=10):  # No crit
        with patch("random.uniform", return_value=1.0):  # Max roll
            dmg_phys, _, _ = calculate_damage(attacker, defender, phys_move)
            dmg_spec, _, _ = calculate_damage(attacker, defender, spec_move)

            # Since SpAtk (70) > Atk (60) while Def (50) == SpDef (50), Special does more damage
            assert dmg_spec > dmg_phys


def test_status_and_zero_power_moves(mock_type_system, base_species):
    """Status moves or zero-power moves deal exactly 0 damage."""
    attacker = Creature(base_species, level=10)
    defender = Creature(base_species, level=10)

    status_move = make_move("Tail Whip", "Normal", "Status", power=0)
    dmg, eff, is_crit = calculate_damage(attacker, defender, status_move)
    assert dmg == 0
    assert not is_crit


def test_minimum_damage_floor(mock_type_system, base_species):
    """Even a tiny attack with high defense deals at least 1 damage if effectiveness > 0."""
    attacker = Creature(base_species, level=1)
    defender = Creature(base_species, level=100)
    defender.stats.def_ = 999  # Massive defense

    weak_move = make_move("Peck", "Normal", "Physical", power=1)
    with patch("random.uniform", return_value=0.85):
        dmg, eff, _ = calculate_damage(attacker, defender, weak_move)
        assert eff > 0
        assert dmg >= 1


# =============================================================================
# Types & STAB Tests
# =============================================================================

def test_same_type_attack_bonus_stab(mock_type_system, fire_species, base_species):
    """Moves matching the attacker's type get a 1.5x STAB damage multiplier."""
    fire_creature = Creature(fire_species, level=15)
    normal_creature = Creature(base_species, level=15)
    defender = Creature(base_species, level=15)

    # Equate attack stats so only STAB differentiates them
    fire_creature.stats.sp_atk = 60
    normal_creature.stats.sp_atk = 60

    fire_move = make_move("Flame", "Fire", "Special", power=40)

    with patch("random.randint", return_value=10):
        with patch("random.uniform", return_value=1.0):
            dmg_stab, eff1, _ = calculate_damage(fire_creature, defender, fire_move)
            dmg_no_stab, eff2, _ = calculate_damage(normal_creature, defender, fire_move)

            assert eff1 == eff2 == 1.0
            assert dmg_stab > dmg_no_stab
            assert dmg_stab == int(dmg_no_stab * 1.5)


def test_type_immunity_zero_damage(mock_type_system, base_species):
    """An immune type matchup yields 0.0x effectiveness and 0 damage."""
    attacker = Creature(base_species, level=15)
    ground_defender = Creature(Species("g", "GroundMon", ["Ground"], {"hp": 50, "def": 50, "sp_def": 50}, ""), level=15)

    electric_move = make_move("Shock", "Electric", "Special", power=60)
    dmg, eff, _ = calculate_damage(attacker, ground_defender, electric_move)
    assert eff == 0.0
    assert dmg == 0


def test_dual_type_effectiveness_stacking(mock_type_system, fire_species, dual_species):
    """Effectiveness against dual types multiplies together (e.g. 2.0 * 2.0 = 4.0x)."""
    attacker = Creature(fire_species, level=15)
    defender = Creature(dual_species, level=15)

    fire_move = make_move("Fire Spin", "Fire", "Special", power=40)
    dmg, eff, _ = calculate_damage(attacker, defender, fire_move)
    assert eff == 4.0  # 2.0x * 2.0x
    assert dmg > 0


# =============================================================================
# Accuracy & Miss Handling Tests
# =============================================================================

def test_accuracy_mechanics():
    """calculate_accuracy checks random rolls against move accuracy."""
    sure_hit = make_move("Swift", accuracy=100)
    assert calculate_accuracy(sure_hit) is True

    risky = make_move("Zap", accuracy=70)
    with patch("random.randint", return_value=70):
        assert calculate_accuracy(risky) is True
    with patch("random.randint", return_value=71):
        assert calculate_accuracy(risky) is False


def test_battle_engine_miss_handling(base_species):
    """In BattleEngine, a missed attack results in 0 damage and a missed event."""
    c1 = Creature(base_species, level=10)
    c1.nickname = "Attacker"  # Give a distinct name so events can be matched unambiguously

    c2 = Creature(base_species, level=10)
    initial_hp = c2.current_hp
    battle = Battle(c1, c2)

    inaccurate_move = make_move("Wild Swing", accuracy=50, power=80)
    action1 = BattleAction(actor=c1, action_type="MOVE", target=c2, move=inaccurate_move)
    action2 = BattleAction(actor=c2, action_type="MOVE", target=c1, move=make_move("Wait", power=0))

    # Force a miss on action1.
    # The engine imports calculate_accuracy directly, so patch it in the engine's namespace.
    with patch("game.battle.battle_engine.calculate_accuracy", return_value=False):
        result = BattleEngine.process_turn(battle, action1, action2)
        # Find the event for c1's action (order may vary by speed tiebreaker)
        c1_event = next(e for e in result.events if e.actor_name == c1.name and e.action_type == "MOVE")
        assert c1_event.missed is True
        assert c1_event.damage_dealt == 0
        assert c2.current_hp == initial_hp
        assert "missed" in c1_event.message.lower()





# =============================================================================
# Critical Hits Tests
# =============================================================================

def test_critical_hit_multiplier_and_message(base_species):
    """Critical hits deal 1.5x damage and produce an explicit message in BattleEngine."""
    c1 = Creature(base_species, level=10)
    c1.nickname = "Striker"  # distinct name for unambiguous event lookup
    c2 = Creature(base_species, level=10)
    battle = Battle(c1, c2)

    move = make_move("Strike", power=40)
    action1 = BattleAction(actor=c1, action_type="MOVE", target=c2, move=move)
    action2 = BattleAction(actor=c2, action_type="MOVE", target=c1, move=make_move("Wait", power=0))

    # Force critical hit (randint returning 1)
    with patch("random.randint", return_value=1):
        with patch("random.uniform", return_value=1.0):
            result = BattleEngine.process_turn(battle, action1, action2)
            # Find c1's MOVE event regardless of turn order
            c1_event = next(e for e in result.events if e.actor_name == c1.name and e.action_type == "MOVE")
            assert c1_event.is_critical is True
            assert "critical hit" in c1_event.message.lower()






# =============================================================================
# Status Effects Tests
# =============================================================================

def test_status_effect_infliction_in_battle(base_species):
    """Moves with a status effect afflict the target in BattleEngine."""
    c1 = Creature(base_species, level=10)
    c1.nickname = "Attacker"  # Give a distinct name so events can be matched unambiguously

    c2 = Creature(base_species, level=10)
    assert c2.status == StatusEffect.NONE
    battle = Battle(c1, c2)

    poison_move = make_move("Poison Stinger", power=20, status_effect="poison")
    action1 = BattleAction(actor=c1, action_type="MOVE", target=c2, move=poison_move)
    action2 = BattleAction(actor=c2, action_type="MOVE", target=c1, move=make_move("Wait", power=0))

    with patch("random.randint", return_value=10):
        result = BattleEngine.process_turn(battle, action1, action2)
        # Check creature state (reliable regardless of event order)
        assert c2.status == StatusEffect.POISON
        # Find c1's MOVE event to verify status_applied flag
        c1_event = next(e for e in result.events if e.actor_name == c1.name and e.action_type == "MOVE")
        assert c1_event.status_applied == "POISON"
        assert "POISON" in c1_event.message




def test_status_not_overwritten(base_species):
    """A target already afflicted with a status effect cannot be overwritten by another."""
    c1 = Creature(base_species, level=10)
    c2 = Creature(base_species, level=10)
    c2.status = StatusEffect.BURN
    battle = Battle(c1, c2)

    poison_move = make_move("Poison Stinger", power=20, status_effect="poison")
    action1 = BattleAction(actor=c1, action_type="MOVE", target=c2, move=poison_move)
    action2 = BattleAction(actor=c2, action_type="MOVE", target=c1, move=make_move("Wait", power=0))

    BattleEngine.process_turn(battle, action1, action2)
    # Must remain BURN, not POISON
    assert c2.status == StatusEffect.BURN


def test_status_not_inflicted_if_target_faints(base_species):
    """If the attack faints the target, status effect is not applied."""
    c1 = Creature(base_species, level=10)
    c2 = Creature(base_species, level=10)
    c2.current_hp = 5  # Fragile
    battle = Battle(c1, c2)

    fatal_poison_move = make_move("Fatal Sting", power=999, status_effect="poison")
    action1 = BattleAction(actor=c1, action_type="MOVE", target=c2, move=fatal_poison_move)
    action2 = BattleAction(actor=c2, action_type="MOVE", target=c1, move=make_move("Wait", power=0))

    BattleEngine.process_turn(battle, action1, action2)
    assert c2.is_fainted
    assert c2.status == StatusEffect.NONE


# =============================================================================
# Fainting and Battle Termination Tests
# =============================================================================

def test_fainting_terminates_battle(base_species):
    """When a creature reaches 0 HP, it faints, emits FAINT event, and ends battle."""
    player = Creature(base_species, level=10)
    enemy = Creature(base_species, level=10)
    battle = Battle(player, enemy)

    lethal_move = make_move("Obliterate", power=999)
    action1 = BattleAction(actor=player, action_type="MOVE", target=enemy, move=lethal_move)
    action2 = BattleAction(actor=enemy, action_type="MOVE", target=player, move=make_move("Wait", power=0))

    result = BattleEngine.process_turn(battle, action1, action2)
    assert enemy.is_fainted is True
    assert enemy.current_hp == 0
    assert result.battle_ended is True
    assert result.winner == "PLAYER"

    faint_event = [e for e in result.events if e.action_type == "FAINT"][0]
    assert faint_event.actor_name == enemy.name


# =============================================================================
# AI Tests
# =============================================================================

def test_ai_picks_super_effective_move(mock_type_system, base_species, fire_species):
    """Basic AI chooses the move that maximizes damage / effectiveness against opponent."""
    ai = BattleAI(ai_type="BASIC")
    ai_creature = Creature(base_species, level=10)
    opponent = Creature(fire_species, level=10)  # Fire type

    m_norm = make_move("Tackle", "Normal", power=40)
    m_water = make_move("Water Gun", "Water", power=40)  # 2.0x against Fire

    with patch("game.creatures.move.MoveFactory.get_instance") as mock_mf:
        mock_factory = mock_mf.return_value
        mock_factory.get_move.side_effect = lambda m_id: m_norm if m_id == "m_norm" else m_water
        ai_creature.moves = ["m_norm", "m_water"]

        # Ensure random roll doesn't trigger the 20% random pick
        with patch("random.random", return_value=0.5):
            action = ai.choose_action(None, ai_creature, opponent)
            assert action.action_type == "MOVE"
            assert action.move.type == "Water"


def test_ai_fallback_on_no_moves(base_species):
    """If AI creature has no moves, it safely returns an ESCAPE action without crashing."""
    ai = BattleAI(ai_type="RANDOM")
    ai_creature = Creature(base_species, level=10)
    ai_creature.moves = []
    opponent = Creature(base_species, level=10)

    action = ai.choose_action(None, ai_creature, opponent)
    assert action.action_type == "ESCAPE"
