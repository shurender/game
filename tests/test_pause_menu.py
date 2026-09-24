"""Tests for the PauseMenuState."""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

import pygame
pygame.init()
pygame.display.set_mode((1, 1), flags=pygame.NOFRAME)

from game.states.pause_state import PauseMenuState


@pytest.fixture
def mock_game():
    game = MagicMock()
    game.assets.get_font.return_value = pygame.font.SysFont("monospace", 16)
    game.audio.master_volume = 0.8
    game.audio.bgm_volume = 0.5
    game.audio.sfx_volume = 0.7
    game.input.bindings = {}
    return game


@pytest.fixture
def pause(mock_game):
    state = PauseMenuState(mock_game)
    state.enter()
    return state


# ---------------------------------------------------------------------------
# Basic lifecycle
# ---------------------------------------------------------------------------

def test_pause_starts_on_menu_page(pause):
    assert pause._page == "menu"
    assert pause._cursor == 0
    assert not pause._closing


def test_pause_slide_in_animation(pause):
    # Initially the panel is offscreen (x == SCREEN_WIDTH)
    from config import SCREEN_WIDTH
    assert pause._panel_x_current >= SCREEN_WIDTH - 1

    # After updating a bit, it should slide in
    pause.update(0.2)
    assert pause._panel_x_current < SCREEN_WIDTH


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

def test_cursor_moves_down(pause, mock_game):
    from game.core.input_handler import Action
    mock_game.input.bindings = {pygame.K_DOWN: Action.DOWN}

    assert pause._cursor == 0
    pause.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
    assert pause._cursor == 1


def test_cursor_wraps_around_bottom(pause, mock_game):
    from game.core.input_handler import Action
    mock_game.input.bindings = {pygame.K_UP: Action.UP}

    pause._cursor = 0
    pause.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
    assert pause._cursor == len(PauseMenuState._ENTRIES) - 1


def test_cursor_moves_up(pause, mock_game):
    from game.core.input_handler import Action
    mock_game.input.bindings = {pygame.K_UP: Action.UP}

    pause._cursor = 3
    pause.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
    assert pause._cursor == 2


# ---------------------------------------------------------------------------
# Menu actions
# ---------------------------------------------------------------------------

def test_resume_begins_close(pause, mock_game):
    """Selecting 'Return to Game' should start the close animation."""
    from game.core.input_handler import Action
    mock_game.input.bindings = {pygame.K_RETURN: Action.CONFIRM}

    # Move cursor to "Return to Game" (index 6)
    pause._cursor = 6
    pause.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert pause._closing is True


def test_cancel_closes_menu(pause, mock_game):
    """Pressing CANCEL/MENU should close the pause menu."""
    from game.core.input_handler import Action
    mock_game.input.bindings = {pygame.K_ESCAPE: Action.CANCEL}

    pause.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert pause._closing is True


def test_save_action_shows_banner(pause, mock_game):
    """Selecting 'Save' should switch to save_result page."""
    from game.core.input_handler import Action
    mock_game.input.bindings = {pygame.K_RETURN: Action.CONFIRM}

    with patch("game.core.save_manager.SaveManager") as MockSM:
        MockSM.return_value.save.return_value = True
        pause._cursor = 4  # "Save"
        pause.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))

    assert pause._page == "save_result"
    assert "saved" in pause._save_msg.lower()


def test_save_banner_auto_dismisses(pause, mock_game):
    """The save banner should auto-dismiss after the timer."""
    pause._page = "save_result"
    pause._save_msg = "Game saved!"
    pause._save_msg_timer = 0.5

    pause.update(0.6)
    assert pause._page == "menu"


def test_settings_opens_state(pause, mock_game):
    """Selecting 'Settings' pushes the SettingsState."""
    from game.core.input_handler import Action
    mock_game.input.bindings = {
        pygame.K_RETURN: Action.CONFIRM,
    }

    pause._cursor = 5  # "Settings"
    
    # We need to set pause._close_callback by firing CONFIRM,
    # and then drive the animation to completion to trigger the push.
    pause.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    
    assert pause._closing is True
    
    # Fast forward the close animation
    for _ in range(20):
        pause.update(0.05)
        
    # Check that it pushed a SettingsState
    assert mock_game.state_machine.push.called
    args, _ = mock_game.state_machine.push.call_args
    assert type(args[0]).__name__ == "SettingsState"

# ---------------------------------------------------------------------------
# Close animation
# ---------------------------------------------------------------------------

def test_close_animation_calls_callback(pause, mock_game):
    """After the slide-out animation finishes, the close callback fires."""
    pause._slide_t = 1.0  # fully open
    called = []
    pause._closing = True
    pause._close_callback = lambda: called.append(True)

    # Pump enough updates to drive slide_t to 0
    for _ in range(20):
        pause.update(0.05)
        if called:
            break

    assert called == [True]


# ---------------------------------------------------------------------------
# Rendering doesn't crash
# ---------------------------------------------------------------------------

def test_render_does_not_crash(pause):
    """Smoke test: render all pages without raising."""
    surf = pygame.Surface((800, 600))

    pause._page = "menu"
    pause.render(surf)

    pause._page = "save_result"
    pause._save_msg = "Game saved!"
    pause.render(surf)
