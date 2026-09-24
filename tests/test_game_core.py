"""Tests for Core Game initialization, main loop controls, and state transitions."""
import os
import pygame
import pytest
from unittest.mock import patch, MagicMock

pygame.init()
pygame.display.set_mode((1, 1), flags=pygame.NOFRAME)

from game.core.game import Game
from game.core.state_machine import StateMachine
from game.states.base_state import State
from game.states.main_menu_state import MainMenuState
from game.core.input_handler import InputHandler
from game.core.asset_manager import AssetManager
from game.rendering.renderer import Renderer
from game.audio.audio_manager import AudioManager
from game.core.settings_manager import SettingsManager


class DummyState(State):
    """Test state recording lifecycle calls."""

    def __init__(self, game, name: str = "dummy") -> None:
        super().__init__(game)
        self.name = name
        self.entered = False
        self.exited = False
        self.paused = False
        self.resumed = False
        self.enter_params = None
        self.events_received = []
        self.updates_received = []
        self.renders_received = []

    def enter(self, params=None):
        self.entered = True
        self.enter_params = params

    def exit(self):
        self.exited = True

    def pause(self):
        self.paused = True

    def resume(self):
        self.resumed = True

    def handle_event(self, event):
        self.events_received.append(event)

    def update(self, dt):
        self.updates_received.append(dt)

    def render(self, surface):
        self.renders_received.append(surface)


# =============================================================================
# Game Initialization Tests
# =============================================================================

def test_game_initialization(tmp_path):
    """Game initializes all subsystems, settings, pre-synthesized tones, and starts at MainMenuState."""
    with patch("pygame.display.set_mode") as mock_set_mode:
        mock_surface = pygame.Surface((960, 640))
        mock_set_mode.return_value = mock_surface

        with patch("game.core.settings_manager.SettingsManager.load") as mock_load_settings:
            game = Game()

            # Verify display and core subsystems
            assert game.running is True
            assert isinstance(game.state_machine, StateMachine)
            assert isinstance(game.input, InputHandler)
            assert isinstance(game.assets, AssetManager)
            assert isinstance(game.renderer, Renderer)
            assert isinstance(game.audio, AudioManager)
            assert isinstance(game.settings, SettingsManager)

            # Settings should have been loaded
            mock_load_settings.assert_called_once()

            # Initial state should be MainMenuState
            assert not game.state_machine.is_empty
            assert isinstance(game.state_machine.current, MainMenuState)


def test_game_quit():
    """game.quit() toggles running to False."""
    with patch("pygame.display.set_mode") as mock_set_mode:
        mock_set_mode.return_value = pygame.Surface((960, 640))
        game = Game()
        assert game.running is True
        game.quit()
        assert game.running is False


# =============================================================================
# State Transitions & Event Dispatch Tests
# =============================================================================

def test_state_machine_event_dispatch():
    """StateMachine dispatches events, updates, and renders to the active state."""
    sm = StateMachine()
    dummy = DummyState(game=None, name="test_state")
    sm.push(dummy)

    # Event dispatch
    test_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
    sm.handle_event(test_event)
    assert len(dummy.events_received) == 1
    assert dummy.events_received[0].key == pygame.K_SPACE

    # Update dispatch
    sm.update(0.016)
    assert len(dummy.updates_received) == 1
    assert dummy.updates_received[0] == 0.016

    # Render dispatch
    dummy_surf = pygame.Surface((10, 10))
    sm.render(dummy_surf)
    assert len(dummy.renders_received) == 1
    assert dummy.renders_received[0] is dummy_surf


def test_state_lifecycle_transitions():
    """Pushing, popping, and replacing states properly invokes pause, resume, enter, and exit."""
    sm = StateMachine()
    state_a = DummyState(game=None, name="A")
    state_b = DummyState(game=None, name="B")
    state_c = DummyState(game=None, name="C")

    # Push state A
    sm.push(state_a, {"mode": "intro"})
    assert state_a.entered is True
    assert state_a.enter_params == {"mode": "intro"}
    assert sm.current is state_a

    # Push state B (pauses A)
    sm.push(state_b)
    assert state_a.paused is True
    assert state_b.entered is True
    assert sm.current is state_b

    # Pop state B (exits B, resumes A)
    popped = sm.pop()
    assert popped is state_b
    assert state_b.exited is True
    assert state_a.resumed is True
    assert sm.current is state_a

    # Replace state A with state C
    sm.replace(state_c, {"source": "A"})
    assert state_a.exited is True
    assert state_c.entered is True
    assert state_c.enter_params == {"source": "A"}
    assert sm.current is state_c

    # Clear states
    sm.clear()
    assert state_c.exited is True
    assert sm.is_empty
    assert sm.current is None
