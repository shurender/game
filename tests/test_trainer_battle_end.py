import pytest
import pygame
from unittest.mock import MagicMock, patch

from game.states.battle_state import BattleState
from game.states.dialogue_state import DialogueState
from game.creatures.creature import Creature, Species
from game.player.party import PartyManager
from game.world.trainer import Trainer
from game.world.interaction import InteractionManager
from game.world.progress_manager import WorldProgressManager
from game.player.player import Direction


@pytest.fixture
def mock_game():
    pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    game = MagicMock()
    game.state_machine = MagicMock()
    game.assets = MagicMock()
    game.assets.get_font.return_value = pygame.font.Font(None, 24)
    game.assets.get_image.return_value = pygame.Surface((32, 32))
    game.audio = MagicMock()
    game.settings = MagicMock()
    game.input = MagicMock()
    return game


@pytest.fixture
def dummy_creatures():
    sp = Species('sp1', 'Florbit', ['Flora'], {'hp': 50, 'atk': 20, 'def': 20, 'sp_atk': 20, 'sp_def': 20, 'spd': 20}, 'leaf')
    c1 = Creature(sp, level=5)
    c2 = Creature(sp, level=5)
    return c1, c2


def test_trainer_battle_win_marks_trainer_defeated(mock_game, dummy_creatures):
    c1, c2 = dummy_creatures
    pm = PartyManager.get_instance()
    pm.party = [c1]
    
    wpm = WorldProgressManager.get_instance()
    wpm.clear()

    trainer = Trainer(
        npc_id="trainer_1",
        name="Lass Mia",
        x=5,
        y=5,
        sprite_name="trainer_lass",
        facing=Direction.DOWN,
        dialogue_id="trainer_mia_intro",
        trainer_id="trainer_lass_mia"
    )
    assert not trainer.has_battled
    assert not wpm.has_flag("defeated_trainer_lass_mia")

    state = BattleState(mock_game)
    state.enter({
        "enemy_creature": c2,
        "is_trainer": True,
        "trainer_id": "trainer_lass_mia",
        "trainer_party": [c2],
        "trainer_npc": trainer
    })

    assert state.is_trainer is True
    assert state.trainer_npc is trainer

    # Defeat enemy creature
    c2.current_hp = 0
    state.battle.is_over = True
    state.battle.winner = "PLAYER"
    state.phase = "BATTLE_END"
    state.dialogue_box.skip_typing()

    # Enter key to finish battle
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    state.handle_event(event)

    # Verify trainer is marked defeated in both the object and WorldProgressManager
    assert trainer.has_battled is True
    assert wpm.has_flag("defeated_trainer_lass_mia") is True
    mock_game.state_machine.pop.assert_called_once()


def test_mouse_click_advances_battle_end_for_trainer(mock_game, dummy_creatures):
    c1, c2 = dummy_creatures
    pm = PartyManager.get_instance()
    pm.party = [c1]
    
    wpm = WorldProgressManager.get_instance()
    wpm.clear()

    trainer = Trainer(
        npc_id="trainer_1",
        name="Lass Mia",
        x=5,
        y=5,
        sprite_name="trainer_lass",
        facing=Direction.DOWN,
        dialogue_id="trainer_mia_intro",
        trainer_id="trainer_lass_mia"
    )

    state = BattleState(mock_game)
    state.enter({
        "enemy_creature": c2,
        "is_trainer": True,
        "trainer_id": "trainer_lass_mia",
        "trainer_party": [c2],
        "trainer_npc": trainer
    })

    c2.current_hp = 0
    state.battle.is_over = True
    state.battle.winner = "PLAYER"
    state.phase = "BATTLE_END"
    state.dialogue_box.skip_typing()

    # Left click (button 1) to finish battle
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(200, 200))
    state.handle_event(click_event)

    assert trainer.has_battled is True
    assert wpm.has_flag("defeated_trainer_lass_mia") is True
    mock_game.state_machine.pop.assert_called_once()


def test_interaction_after_trainer_defeated_does_not_loop_battle(mock_game):
    wpm = WorldProgressManager.get_instance()
    wpm.clear()

    trainer = Trainer(
        npc_id="trainer_1",
        name="Lass Mia",
        x=5,
        y=5,
        sprite_name="trainer_lass",
        facing=Direction.DOWN,
        dialogue_id="trainer_mia_intro",
        trainer_id="trainer_lass_mia"
    )
    # Mark trainer as defeated
    trainer.has_battled = True
    assert wpm.has_flag("defeated_trainer_lass_mia") is True

    interaction_mgr = InteractionManager(mock_game)
    interaction_mgr.trigger_interaction(trainer)

    # Should push DialogueState (defeat dialogue), NOT BattleState
    assert mock_game.state_machine.push.called
    pushed_state = mock_game.state_machine.push.call_args[0][0]
    assert isinstance(pushed_state, DialogueState)
    assert not isinstance(pushed_state, BattleState)


def test_interaction_start_battle_passes_params_properly(mock_game):
    wpm = WorldProgressManager.get_instance()
    wpm.clear()

    trainer = Trainer(
        npc_id="trainer_1",
        name="Lass Mia",
        x=5,
        y=5,
        sprite_name="trainer_lass",
        facing=Direction.DOWN,
        dialogue_id="trainer_mia_intro",
        trainer_id="trainer_lass_1"
    )

    interaction_mgr = InteractionManager(mock_game)
    # Trigger interaction on undefeated trainer
    interaction_mgr.trigger_interaction(trainer)

    # DialogueState is pushed with on_complete callback
    dialogue_state = mock_game.state_machine.push.call_args[0][0]
    assert isinstance(dialogue_state, DialogueState)
    assert dialogue_state.on_complete_callback is not None

    # Trigger completion callback which starts battle
    dialogue_state.on_complete_callback()

    # Verify BattleState was pushed with parameters dict
    last_call = mock_game.state_machine.push.call_args
    pushed_battle = last_call[0][0]
    pushed_params = last_call[0][1] if len(last_call[0]) > 1 else None

    assert isinstance(pushed_battle, BattleState)
    assert pushed_params is not None
    assert pushed_params.get("is_trainer") is True
    assert pushed_params.get("trainer_npc") is trainer
    assert pushed_params.get("trainer_id") == "trainer_lass_1"
