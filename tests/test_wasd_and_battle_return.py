import pytest
import pygame
from unittest.mock import MagicMock, patch

from game.states.battle_state import BattleState
from game.states.party_state import PartyState
from game.states.inventory_state import InventoryState
from game.states.shop_state import ShopState
from game.creatures.creature import Creature, Species
from game.battle.battle import Battle
from game.player.party import PartyManager
from game.world.shop import Shop


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
    return game


@pytest.fixture
def dummy_creatures():
    sp = Species('sp1', 'Pikamon', ['Normal'], {'hp': 50, 'atk': 20, 'def': 20, 'sp_atk': 20, 'sp_def': 20, 'spd': 20}, 'mouse')
    c1 = Creature(sp, level=5)
    c2 = Creature(sp, level=5)
    return c1, c2


def test_battle_win_enter_pops_state(mock_game, dummy_creatures):
    c1, c2 = dummy_creatures
    pm = PartyManager.get_instance()
    pm.party = [c1]
    
    state = BattleState(mock_game)
    state.enter({"enemy_creature": c2})
    
    # Simulate battle end with player win
    state.phase = 'BATTLE_END'
    state.battle.is_over = True
    state.battle.winner = 'PLAYER'
    state.dialogue_box.skip_typing()
    
    # Press Enter
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    state.handle_event(event)
    
    # Verify state was popped
    mock_game.state_machine.pop.assert_called_once()


def test_battle_wasd_navigation(mock_game, dummy_creatures):
    c1, c2 = dummy_creatures
    pm = PartyManager.get_instance()
    pm.party = [c1]
    
    state = BattleState(mock_game)
    state.enter({"enemy_creature": c2})
    state.phase = 'PLAYER_TURN'
    
    initial_idx = state.main_menu.cursor
    # Move down with 'S'
    state.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s))
    assert state.main_menu.cursor == (initial_idx + 1) % len(state.main_menu.items)
    
    # Move up with 'W'
    state.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))
    assert state.main_menu.cursor == initial_idx


def test_party_state_wasd(mock_game, dummy_creatures):
    c1, c2 = dummy_creatures
    pm = PartyManager.get_instance()
    pm.party = [c1, c2]
    
    state = PartyState(mock_game)
    state.enter()
    
    assert state.cursor_index == 0
    state.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s))
    assert state.cursor_index == 1
    state.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))
    assert state.cursor_index == 0


def test_shop_state_wasd(mock_game):
    state = ShopState(mock_game)
    state.shop = Shop(shop_id="test", name="Shop", greeting="Hi", farewell="Bye", listings=[], buys_items=True, sell_rate=0.5)
    state.phase = 'BUY'
    state.tab = 'BUY'
    
    # Press 'D' to switch tab to SELL
    state.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d))
    assert state.tab == 'SELL'
    
    # Press 'A' to switch tab to BUY
    state.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a))
    assert state.tab == 'BUY'


def test_inventory_state_wasd(mock_game):
    state = InventoryState(mock_game)
    state.enter()
    assert state.tab_index == 0
    
    # Press 'D' to switch to next category tab
    state.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d))
    assert state.tab_index == 1
    
    # Press 'A' to switch back
    state.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a))
    assert state.tab_index == 0


def test_mouse_left_click_confirms(dummy_creatures):
    from game.core.input_handler import Action, InputHandler
    ih = InputHandler()
    ih.begin_frame()
    
    # Send mouse button down (button 1 = left click)
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(100, 100))
    ih.handle_event(click_event)
    
    assert ih.is_pressed(Action.CONFIRM)
    assert ih.is_just_pressed(Action.CONFIRM)
