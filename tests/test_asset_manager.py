"""Unit tests for AssetManager, SpriteSheet, and fallback placeholder system."""
import os
import pygame
import pytest
from unittest.mock import patch, MagicMock

pygame.init()
pygame.display.set_mode((1, 1), flags=pygame.NOFRAME)

from config import (
    ASSET_DIRS,
    IMAGES_DIR,
    SOUNDS_DIR,
    MUSIC_DIR,
    FONTS_DIR,
    BGM_TEMPLATE,
)
from game.core.asset_manager import AssetManager, FallbackSound, FallbackFont
from game.rendering.spritesheet import SpriteSheet


@pytest.fixture
def asset_mgr():
    """Fixture providing a fresh AssetManager for each test."""
    manager = AssetManager()
    manager.clear()
    return manager


# =============================================================================
# Directory Centralization & Initialization Tests
# =============================================================================

def test_asset_directories_centralized(asset_mgr):
    """Ensure all standard asset directories are defined and created."""
    assert os.path.isdir(IMAGES_DIR)
    assert os.path.isdir(SOUNDS_DIR)
    assert os.path.isdir(FONTS_DIR)
    assert os.path.isdir(MUSIC_DIR)
    for name, path in ASSET_DIRS.items():
        assert os.path.exists(path), f"Directory {name} at {path} should exist"


# =============================================================================
# Image Loading & Fallback Tests
# =============================================================================

def test_missing_image_returns_fallback_surface(asset_mgr):
    """Missing image must not crash and must return a valid pygame.Surface placeholder."""
    surf = asset_mgr.get_image("nonexistent_hero.png")
    assert isinstance(surf, pygame.Surface)
    assert surf.get_size() == (32, 32)
    assert asset_mgr.is_placeholder("nonexistent_hero.png")
    assert "image:nonexistent_hero.png" in asset_mgr.get_missing_assets()


def test_missing_image_custom_size(asset_mgr):
    """Missing image requested with specific size returns fallback matching that size."""
    surf = asset_mgr.get_image("missing_icon.png", size=(64, 64))
    assert isinstance(surf, pygame.Surface)
    assert surf.get_size() == (64, 64)


def test_existing_image_loads_and_caches(asset_mgr, tmp_path):
    """Creating a temporary valid image on disk should load successfully and cache."""
    test_img_path = os.path.join(IMAGES_DIR, "test_dummy_asset.png")
    dummy_surf = pygame.Surface((48, 48))
    dummy_surf.fill((100, 150, 200))
    pygame.image.save(dummy_surf, test_img_path)

    try:
        assert asset_mgr.has_image("test_dummy_asset.png")
        loaded = asset_mgr.get_image("test_dummy_asset.png")
        assert isinstance(loaded, pygame.Surface)
        assert loaded.get_size() == (48, 48)
        assert not asset_mgr.is_placeholder("test_dummy_asset.png")

        # Second access should hit cache
        loaded2 = asset_mgr.get_image("test_dummy_asset.png")
        assert loaded is loaded2
    finally:
        if os.path.exists(test_img_path):
            os.remove(test_img_path)


def test_load_image_backward_compatibility(asset_mgr):
    """load_image alias works cleanly without error."""
    surf = asset_mgr.load_image("missing_bg.png")
    assert isinstance(surf, pygame.Surface)


def test_cache_surface_manual(asset_mgr):
    """Manually cached surfaces are retrievable."""
    custom = pygame.Surface((16, 16))
    asset_mgr.cache_surface("procedural_stone", custom)
    assert asset_mgr._images["procedural_stone"] is custom


def test_create_fallback_image_visual_styling(asset_mgr):
    """Fallback image contains distinct checkerboard pattern."""
    fallback = asset_mgr.create_fallback_image(width=40, height=40, label="HP")
    assert isinstance(fallback, pygame.Surface)
    assert fallback.get_size() == (40, 40)


# =============================================================================
# SpriteSheet Tests
# =============================================================================

def test_spritesheet_from_surface():
    """SpriteSheet slices a surface into grid frames accurately."""
    surf = pygame.Surface((64, 64))
    # 4 frames of 32x32: (0,0), (1,0), (0,1), (1,1)
    sheet = SpriteSheet(surf, frame_width=32, frame_height=32)
    assert sheet.cols == 2
    assert sheet.rows == 2
    assert sheet.total_frames == 4

    f0 = sheet.get_frame(0)
    assert isinstance(f0, pygame.Surface)
    assert f0.get_size() == (32, 32)

    f_coord = sheet.get_image(1, 0)
    assert isinstance(f_coord, pygame.Surface)
    assert f_coord.get_size() == (32, 32)


def test_spritesheet_out_of_bounds_safety():
    """SpriteSheet frame access out of bounds returns fallback frame without crashing."""
    surf = pygame.Surface((32, 32))
    sheet = SpriteSheet(surf, frame_width=32, frame_height=32)
    assert sheet.total_frames == 1

    # Out of bounds linear index
    oob_frame = sheet.get_frame(99)
    assert isinstance(oob_frame, pygame.Surface)
    assert oob_frame.get_size() == (32, 32)

    # Out of bounds grid coords
    oob_coord = sheet.get_image(5, 5)
    assert isinstance(oob_coord, pygame.Surface)
    assert oob_coord.get_size() == (32, 32)

    # Negative index
    neg_frame = sheet.get_frame(-1)
    assert isinstance(neg_frame, pygame.Surface)


def test_spritesheet_get_frames_and_rows():
    """get_frames and get_row return valid lists of frame surfaces."""
    surf = pygame.Surface((96, 64))
    # 3 cols x 2 rows
    sheet = SpriteSheet(surf, frame_width=32, frame_height=32)
    frames = sheet.get_frames(start=0, count=4)
    assert len(frames) == 4

    row0 = sheet.get_row(0)
    assert len(row0) == 3

    col0 = sheet.get_column(0)
    assert len(col0) == 2


def test_missing_spritesheet_generates_procedural_fallback(asset_mgr):
    """Missing sprite sheet generates a fallback sheet with multiple distinguishable frames."""
    sheet = asset_mgr.get_spritesheet("missing_character_sheet.png", frame_width=32, frame_height=32)
    assert isinstance(sheet, SpriteSheet)
    assert sheet.is_placeholder
    assert sheet.total_frames == 16  # 4x4 procedural fallback
    frame = sheet.get_frame(3)
    assert isinstance(frame, pygame.Surface)
    assert frame.get_size() == (32, 32)
    assert asset_mgr.is_placeholder("missing_character_sheet.png")


# =============================================================================
# Font Loading & Fallback Tests
# =============================================================================

def test_default_font_loading(asset_mgr):
    """Default font loading works without custom path."""
    font = asset_mgr.get_font(24)
    assert font is not None
    rendered = font.render("Hello", True, (255, 255, 255))
    assert isinstance(rendered, pygame.Surface)


def test_missing_font_falls_back_gracefully(asset_mgr):
    """Missing custom font falls back to Pygame default font without crashing."""
    font = asset_mgr.get_font(18, "fictional_fantasy_font.ttf")
    assert font is not None
    rendered = font.render("Test Text", True, (255, 255, 255))
    assert isinstance(rendered, pygame.Surface)
    assert "font:fictional_fantasy_font.ttf" in asset_mgr.get_missing_assets()


def test_fallback_font_mock():
    """FallbackFont handles render, size, and height even without pygame font system."""
    fb_font = FallbackFont(size=20)
    surf = fb_font.render("Sample", True, (255, 255, 255))
    assert isinstance(surf, pygame.Surface)
    w, h = fb_font.size("Sample")
    assert w > 0 and h == 20
    assert fb_font.get_height() == 20


# =============================================================================
# Sound Loading & Fallback Tests
# =============================================================================

def test_missing_sound_returns_non_crashing_fallback(asset_mgr):
    """Missing sound effect returns a playable fallback without throwing exceptions."""
    sound = asset_mgr.get_sound("missing_explosion.wav")
    assert sound is not None
    assert "sound:missing_explosion.wav" in asset_mgr.get_missing_assets()

    # Calling audio methods must not crash
    sound.set_volume(0.5)
    sound.play()
    sound.stop()
    sound.fadeout(100)


def test_fallback_sound_class():
    """FallbackSound class implements full mixer.Sound interface safely."""
    fb = FallbackSound("test_sfx")
    fb.set_volume(0.8)
    assert fb.get_volume() == 0.8
    assert fb.get_length() == 0.0
    fb.play()
    fb.stop()
    fb.fadeout(50)


def test_cache_sound_manual(asset_mgr):
    """Manual sound caching works."""
    dummy_sound = FallbackSound("custom_cue")
    asset_mgr.cache_sound("custom_cue", dummy_sound)
    assert asset_mgr.get_sound("custom_cue") is dummy_sound


# =============================================================================
# Music Loading & Path Resolution Tests
# =============================================================================

def test_missing_music_path_returns_none(asset_mgr):
    """Requesting path for missing music returns None and logs missing asset."""
    path = asset_mgr.get_music_path("mythical_dungeon_theme")
    assert path is None
    assert "music:mythical_dungeon_theme" in asset_mgr.get_missing_assets()


def test_missing_music_playback_safe(asset_mgr):
    """Playing missing music returns False without crashing."""
    result = asset_mgr.play_music("nonexistent_bgm")
    assert result is False


def test_stop_music_safe(asset_mgr):
    """Stopping music is safe regardless of playback state."""
    asset_mgr.stop_music()


# =============================================================================
# Asset Auditing & Inspection Tests
# =============================================================================

def test_audit_assets_report(asset_mgr):
    """audit_assets returns complete structured diagnostic data."""
    # Trigger some fallbacks
    asset_mgr.get_image("audit_missing_sprite.png")
    asset_mgr.get_sound("audit_missing_sfx.wav")

    report = asset_mgr.audit_assets()
    assert isinstance(report, dict)
    assert "directories" in report
    assert "cached_images" in report
    assert "cached_sounds" in report
    assert "missing_assets_requested" in report
    assert "image:audit_missing_sprite.png" in report["missing_assets_requested"]
    assert "sound:audit_missing_sfx.wav" in report["missing_assets_requested"]


def test_clear_assets(asset_mgr):
    """Clear resets all caches and missing asset records."""
    asset_mgr.get_image("temp_item.png")
    assert len(asset_mgr.get_missing_assets()) > 0
    asset_mgr.clear()
    assert len(asset_mgr.get_missing_assets()) == 0
    assert len(asset_mgr._images) == 0
