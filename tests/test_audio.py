"""Tests for the Audio and Music managers.

Audio tests mock at the instance level (via patch.object on MusicManager._initialized
and direct replacement of pygame.mixer.music) to avoid fighting module-level imports.
"""
import os
import math
import pytest
from unittest.mock import patch, MagicMock, call

import pygame
pygame.init()
pygame.display.set_mode((1, 1), flags=pygame.NOFRAME)

from game.audio.music_manager import MusicManager
from game.audio.audio_manager import AudioManager


# ---------------------------------------------------------------------------
# MusicManager — volume controls
# ---------------------------------------------------------------------------

def _make_mm(initialized=True):
    mm = MusicManager()
    mm._initialized = initialized
    return mm


def test_music_volume_clamped():
    mm = _make_mm()
    mm.volume = 1.5
    assert mm.volume == 1.0
    mm.volume = -0.3
    assert mm.volume == 0.0


def test_music_master_volume():
    mm = _make_mm()
    mm.master_volume = 0.5
    assert mm.master_volume == 0.5


def test_music_mute_calls_set_volume_zero():
    mm = _make_mm()
    mm.volume = 0.8
    mock_music = MagicMock()
    with patch("game.audio.music_manager.pygame.mixer.music", mock_music):
        mm.muted = True
        mock_music.set_volume.assert_called_with(0.0)


def test_music_unmute_restores_volume():
    mm = _make_mm()
    mm.volume = 0.6
    mm.master_volume = 1.0
    mock_music = MagicMock()
    with patch("game.audio.music_manager.pygame.mixer.music", mock_music):
        mm._muted = True
        mm.muted = False
        mock_music.set_volume.assert_called_with(pytest.approx(0.6, abs=0.01))


# ---------------------------------------------------------------------------
# MusicManager — play_music
# ---------------------------------------------------------------------------

def test_play_music_loads_file_if_exists():
    mm = _make_mm()
    mock_music = MagicMock()
    with patch("game.audio.music_manager.pygame.mixer.music", mock_music), \
         patch("game.audio.music_manager.os.path.exists", return_value=True):
        mm.play_music("town_theme")
        mock_music.load.assert_called_once_with("assets/audio/bgm/town_theme.ogg")
        mock_music.play.assert_called_once()


def test_play_music_same_name_is_noop():
    mm = _make_mm()
    mm._current_bgm = "town_theme"
    mock_music = MagicMock()
    with patch("game.audio.music_manager.pygame.mixer.music", mock_music):
        mm.play_music("town_theme")
        mock_music.load.assert_not_called()


def test_play_music_missing_file_calls_stop():
    mm = _make_mm()
    mock_music = MagicMock()
    with patch("game.audio.music_manager.pygame.mixer.music", mock_music), \
         patch("game.audio.music_manager.os.path.exists", return_value=False):
        mm.play_music("nonexistent")
        mock_music.load.assert_not_called()
        mock_music.fadeout.assert_called()


# ---------------------------------------------------------------------------
# MusicManager — named hooks
# ---------------------------------------------------------------------------

def test_play_world_music_town():
    mm = _make_mm()
    mock_music = MagicMock()
    with patch("game.audio.music_manager.pygame.mixer.music", mock_music), \
         patch("game.audio.music_manager.os.path.exists", return_value=True):
        mm.play_world_music("starting_town")
        mock_music.load.assert_called_with("assets/audio/bgm/town_theme.ogg")


def test_play_world_music_route():
    mm = _make_mm()
    mock_music = MagicMock()
    with patch("game.audio.music_manager.pygame.mixer.music", mock_music), \
         patch("game.audio.music_manager.os.path.exists", return_value=True):
        mm.play_world_music("route_7")
        mock_music.load.assert_called_with("assets/audio/bgm/route_theme.ogg")


def test_play_battle_music_wild():
    mm = _make_mm()
    mock_music = MagicMock()
    with patch("game.audio.music_manager.pygame.mixer.music", mock_music), \
         patch("game.audio.music_manager.os.path.exists", return_value=True):
        mm.play_battle_music(is_trainer=False, is_boss=False)
        mock_music.load.assert_called_with("assets/audio/bgm/wild_battle.ogg")


def test_play_battle_music_trainer():
    mm = _make_mm()
    mock_music = MagicMock()
    with patch("game.audio.music_manager.pygame.mixer.music", mock_music), \
         patch("game.audio.music_manager.os.path.exists", return_value=True):
        mm.play_battle_music(is_trainer=True, is_boss=False)
        mock_music.load.assert_called_with("assets/audio/bgm/trainer_battle.ogg")


def test_play_battle_music_boss():
    mm = _make_mm()
    mock_music = MagicMock()
    with patch("game.audio.music_manager.pygame.mixer.music", mock_music), \
         patch("game.audio.music_manager.os.path.exists", return_value=True):
        mm.play_battle_music(is_trainer=True, is_boss=True)
        mock_music.load.assert_called_with("assets/audio/bgm/boss_battle.ogg")


# ---------------------------------------------------------------------------
# AudioManager — hooks and mute
# ---------------------------------------------------------------------------

def test_audio_sfx_volume_clamped():
    am = AudioManager()
    am.sfx_volume = 2.0
    assert am.sfx_volume == 1.0


def test_audio_master_volume_propagates():
    am = AudioManager()
    am.master_volume = 0.5
    assert am.music.master_volume == 0.5


def test_audio_play_menu_sound_calls_synthesize():
    am = AudioManager()
    am.synthesize_tone = MagicMock(return_value=MagicMock())
    am.play_menu_sound()
    am.synthesize_tone.assert_called_with("menu_select", frequency=660, duration=0.1, wave="sine")


def test_audio_play_attack_sound():
    am = AudioManager()
    am.synthesize_tone = MagicMock(return_value=MagicMock())
    am.play_attack_sound()
    am.synthesize_tone.assert_called_with("attack_hit", frequency=150, duration=0.2, wave="square", volume=0.5)


def test_audio_play_level_up_sound():
    am = AudioManager()
    am.synthesize_tone = MagicMock(return_value=MagicMock())
    am.play_level_up_sound()
    am.synthesize_tone.assert_called_with("level_up", frequency=1000, duration=0.8, wave="sine")


def test_audio_sfx_muted_skips_play():
    am = AudioManager()
    am.sfx_muted = True
    am.synthesize_tone = MagicMock()
    am.play_menu_sound()
    am.synthesize_tone.assert_not_called()


def test_audio_play_sound_alias():
    am = AudioManager()
    mock_fn = MagicMock()
    am.play_sfx = mock_fn
    am.play_sound("test_sfx")
    mock_fn.assert_called_once_with("test_sfx")
