"""Tests for SettingsManager and SettingsState."""
import os
import json
import pytest
from unittest.mock import MagicMock, patch

import pygame
pygame.init()
pygame.display.set_mode((1, 1), flags=pygame.NOFRAME)

from config import SAVE_DIR
from game.core.settings_manager import SettingsManager
from game.states.settings_state import SettingsState


@pytest.fixture
def mock_game():
    game = MagicMock()
    game.audio = MagicMock()
    game.assets.get_font.return_value = pygame.font.SysFont("monospace", 16)
    game.input.bindings = {}
    return game


@pytest.fixture
def settings_manager(mock_game, tmp_path):
    with patch("game.core.settings_manager.SAVE_DIR", str(tmp_path)):
        sm = SettingsManager(mock_game)
        # Point to the mock settings file
        sm.settings_path = os.path.join(str(tmp_path), "settings.json")
        yield sm


def test_settings_manager_initialization(settings_manager):
    assert settings_manager.settings == SettingsManager.DEFAULT_SETTINGS


def test_settings_manager_save_and_load(settings_manager):
    settings_manager.settings["master_volume"] = 0.3
    settings_manager.settings["fullscreen"] = True
    
    settings_manager.save()
    
    assert os.path.exists(settings_manager.settings_path)
    
    # Modify memory values to verify load overrides them
    settings_manager.settings["master_volume"] = 0.9
    settings_manager.settings["fullscreen"] = False
    
    settings_manager.load()
    
    assert settings_manager.settings["master_volume"] == 0.3
    assert settings_manager.settings["fullscreen"] is True


def test_settings_manager_apply_volume(settings_manager, mock_game):
    settings_manager.update_volume("master_volume", 0.7)
    assert mock_game.audio.master_volume == 0.7
    
    settings_manager.update_volume("bgm_volume", 0.4)
    assert mock_game.audio.bgm_volume == 0.4
    
    # Test bounds
    settings_manager.update_volume("sfx_volume", 1.5)
    assert mock_game.audio.sfx_volume == 1.0


def test_settings_state_navigation(mock_game, settings_manager):
    mock_game.settings = settings_manager
    state = SettingsState(mock_game)
    state.enter()
    
    from game.core.input_handler import Action
    mock_game.input.bindings = {
        pygame.K_DOWN: Action.DOWN,
        pygame.K_UP: Action.UP
    }
    
    assert state._cursor == 0
    state.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
    assert state._cursor == 1
    
    state.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
    assert state._cursor == 0


def test_settings_state_adjust_volume(mock_game, settings_manager):
    mock_game.settings = settings_manager
    state = SettingsState(mock_game)
    state.enter()
    
    from game.core.input_handler import Action
    mock_game.input.bindings = {
        pygame.K_RIGHT: Action.RIGHT,
        pygame.K_LEFT: Action.LEFT
    }
    
    # cursor 0 is master_volume (default 0.8)
    state.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
    assert settings_manager.get("master_volume") == pytest.approx(0.9)
    
    state.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
    assert settings_manager.get("master_volume") == pytest.approx(0.8)


def test_settings_state_toggle(mock_game, settings_manager):
    mock_game.settings = settings_manager
    state = SettingsState(mock_game)
    state.enter()
    
    from game.core.input_handler import Action
    mock_game.input.bindings = {
        pygame.K_RETURN: Action.CONFIRM
    }
    
    # cursor 3 is fullscreen (default False)
    state._cursor = 3
    state.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    
    assert settings_manager.get("fullscreen") is True


def test_settings_state_exit_saves(mock_game, settings_manager):
    mock_game.settings = settings_manager
    settings_manager.save = MagicMock()
    
    state = SettingsState(mock_game)
    state.exit()
    
    settings_manager.save.assert_called_once()


def test_settings_state_render(mock_game, settings_manager):
    mock_game.settings = settings_manager
    state = SettingsState(mock_game)
    state.enter()
    
    surf = pygame.Surface((800, 600))
    state.render(surf) # Should not crash
