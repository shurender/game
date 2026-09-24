"""Tests for the SaveManager."""
import os
import json
import pytest
from unittest.mock import MagicMock

from game.core.save_manager import SaveManager
from game.player.party import PartyManager
from game.inventory.inventory import Inventory
from game.player.wallet import Wallet
from game.quests.quest_manager import QuestManager
from game.world.progress_manager import WorldProgressManager

@pytest.fixture
def mock_game():
    game = MagicMock()
    # Mock a state machine with a WorldState
    world_state = MagicMock()
    world_state.player.name = "TestPlayer"
    world_state.player.x = 5
    world_state.player.y = 7
    world_state.player.facing.name = "DOWN"
    world_state.world.current_map.map_id = "test_map"
    
    game.state_machine.stack = [world_state]
    return game

@pytest.fixture
def save_mgr(mock_game, tmp_path):
    mgr = SaveManager(mock_game)
    # Redirect save directory to a temporary path
    mgr.SAVE_DIR = str(tmp_path)
    # Patch get_world_state to return our mock
    mgr.get_world_state = MagicMock(return_value=mock_game.state_machine.stack[0])
    return mgr
    
@pytest.fixture(autouse=True)
def reset_singletons():
    PartyManager._instance = None
    Inventory._instance = None
    Wallet._instance = None
    QuestManager._instance = None
    WorldProgressManager._instance = None

def test_save_and_load(save_mgr, mock_game):
    # Setup some state
    Wallet.get_instance().coins = 1234
    Inventory.get_instance().add("potion", 5)
    WorldProgressManager.get_instance().set_flag("test_flag", True)
    
    # Save
    assert save_mgr.save(slot=1) is True
    
    # Clear state
    Wallet.get_instance().coins = 0
    Inventory.get_instance().items = {}
    WorldProgressManager.get_instance().clear_flag("test_flag")
    
    # Load
    assert save_mgr.load(slot=1) is True
    
    # Verify State restored
    assert Wallet.get_instance().coins == 1234
    assert Inventory.get_instance().quantity("potion") == 5
    assert WorldProgressManager.get_instance().get_flag("test_flag") is True
    
    # Verify world state pushed with correct pos
    mock_game.state_machine.push.assert_called_once()
    args, kwargs = mock_game.state_machine.push.call_args
    params = args[1]
    assert params["map_id"] == "test_map"
    assert params["x"] == 5
    assert params["y"] == 7
    assert params["facing"] == "DOWN"

def test_save_info(save_mgr):
    Wallet.get_instance().coins = 500
    save_mgr.save(slot=2)
    
    info = save_mgr.get_save_info(slot=2)
    assert info is not None
    assert info["player_name"] == "TestPlayer"
    assert info["map_id"] == "test_map"
    assert info["party_size"] == 0

def test_load_nonexistent_slot(save_mgr):
    assert save_mgr.load(slot=99) is False
