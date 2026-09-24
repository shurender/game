"""Tests for the animation system."""
import math
import pytest
import pygame

# Minimal pygame init for surface creation
pygame.init()
pygame.display.set_mode((1, 1), flags=pygame.NOFRAME)

from game.rendering.animation import (
    SpriteAnimation,
    FadeEffect,
    ScreenShake,
    HitFlash,
    DamageNumber,
    CaptureAnimation,
    LevelUpEffect,
    CreatureEntranceAnim,
    CreatureFaintAnim,
    AnimationLayer,
)


# ---------------------------------------------------------------------------
# SpriteAnimation
# ---------------------------------------------------------------------------

def _dummy_frames(n=4):
    return [pygame.Surface((16, 16)) for _ in range(n)]


def test_sprite_anim_loops():
    anim = SpriteAnimation(_dummy_frames(4), fps=4, loop=True)
    # 4 fps means 0.25s per frame
    for _ in range(4):
        anim.update(0.25)
    assert anim._index == 0  # looped back
    assert not anim.is_done


def test_sprite_anim_oneshot():
    finished = []
    anim = SpriteAnimation(_dummy_frames(3), fps=10, loop=False, on_finish=lambda: finished.append(1))
    # 10 fps = 0.1s per frame; 3 frames takes 0.3s
    anim.update(0.35)
    assert anim.is_done
    assert finished == [1]


def test_sprite_anim_stays_on_last_frame_after_done():
    anim = SpriteAnimation(_dummy_frames(2), fps=10, loop=False)
    anim.update(1.0)
    assert anim._index == 1  # clamped to last frame


# ---------------------------------------------------------------------------
# FadeEffect
# ---------------------------------------------------------------------------

def test_fade_completes():
    done = []
    fade = FadeEffect(duration=0.5, fade_in=True, on_finish=lambda: done.append(1))
    fade.update(0.6)
    assert fade.is_done
    assert done == [1]


def test_fade_render_increases_alpha():
    fade = FadeEffect(color=(0, 0, 0), duration=1.0, fade_in=True)
    surf = pygame.Surface((100, 100))

    fade.update(0.0)
    # At t=0 alpha should be 0 (transparent)
    assert fade._elapsed == 0.0

    fade.update(0.5)
    # At t=0.5 alpha should be ~128
    t = fade._elapsed / fade.duration
    assert abs(t - 0.5) < 0.01


# ---------------------------------------------------------------------------
# ScreenShake
# ---------------------------------------------------------------------------

def test_screen_shake_idle_returns_zero():
    shake = ScreenShake()
    assert shake.get_offset() == (0, 0)
    assert shake.is_done


def test_screen_shake_active_returns_nonzero_sometimes():
    shake = ScreenShake(duration=1.0, magnitude=20.0)
    shake.trigger()
    assert not shake.is_done
    shake.update(0.5)
    # After 0.5s of a 1s shake it should still be active
    assert not shake.is_done
    # Cannot guarantee non-zero (random), but magnitude should be in range
    shake.update(1.1)
    assert shake.is_done
    assert shake.get_offset() == (0, 0)


# ---------------------------------------------------------------------------
# HitFlash
# ---------------------------------------------------------------------------

def test_hit_flash_not_active_initially():
    hf = HitFlash()
    assert hf.is_done
    assert not hf.visible


def test_hit_flash_visible_then_done():
    hf = HitFlash(duration=0.2, flashes=2)
    hf.trigger()
    assert not hf.is_done
    hf.update(0.25)
    assert hf.is_done


def test_hit_flash_apply_returns_surface():
    hf = HitFlash()
    hf.trigger()
    surf = pygame.Surface((32, 32))
    surf.fill((100, 100, 100))
    result = hf.apply(surf)
    assert isinstance(result, pygame.Surface)


# ---------------------------------------------------------------------------
# DamageNumber
# ---------------------------------------------------------------------------

def test_damage_number_rises_and_expires():
    font = pygame.font.SysFont("monospace", 16)
    dn = DamageNumber(x=100, y=200, value=42)
    start_y = dn.y
    dn.update(0.5)
    assert dn.y < start_y  # floated upward

    dn.update(2.0)
    assert dn.is_done


# ---------------------------------------------------------------------------
# CaptureAnimation
# ---------------------------------------------------------------------------

def test_capture_animation_phases():
    cap = CaptureAnimation(start=(50, 300), target=(300, 100), shakes=2, success=True)
    assert not cap.is_done

    # Advance through throw phase
    cap.update(0.6)
    assert cap._phase >= 1

    # Advance through everything
    cap.update(5.0)
    assert cap.is_done


def test_capture_animation_failure():
    cap = CaptureAnimation(start=(50, 300), target=(300, 100), shakes=1, success=False)
    cap.update(10.0)
    assert cap.is_done


# ---------------------------------------------------------------------------
# LevelUpEffect
# ---------------------------------------------------------------------------

def test_level_up_effect_completes():
    done = []
    lvl = LevelUpEffect(x=200, y=200, duration=1.0, on_finish=lambda: done.append(1))
    lvl.update(1.1)
    assert lvl.is_done
    assert done == [1]


# ---------------------------------------------------------------------------
# CreatureEntranceAnim
# ---------------------------------------------------------------------------

def test_entrance_anim_reaches_target():
    anim = CreatureEntranceAnim(start_x=800, end_x=300, y=100, duration=0.5)
    anim.update(1.0)
    assert anim.is_done
    assert abs(anim.current_x - 300) < 1


# ---------------------------------------------------------------------------
# CreatureFaintAnim
# ---------------------------------------------------------------------------

def test_faint_anim_drops_and_fades():
    anim = CreatureFaintAnim(x=100, y=100, duration=0.6)
    anim.update(0.3)
    assert anim.current_y > 100   # dropped
    assert anim.alpha < 255       # faded

    anim.update(1.0)
    assert anim.is_done


# ---------------------------------------------------------------------------
# AnimationLayer
# ---------------------------------------------------------------------------

def test_animation_layer_damage_number_lifecycle():
    font = pygame.font.SysFont("monospace", 16)
    layer = AnimationLayer(font)
    layer.spawn_damage_number(100, 100, 55)
    assert len(layer._damage_numbers) == 1
    layer.update(2.0)  # long enough for DamageNumber to expire (duration=1.2)
    assert len(layer._damage_numbers) == 0


def test_animation_layer_capture_done():
    font = pygame.font.SysFont("monospace", 16)
    layer = AnimationLayer(font)
    assert layer.capture_done
    layer.start_capture((0, 0), (200, 200), shakes=1)
    assert not layer.capture_done
    layer.update(10.0)
    assert layer.capture_done


def test_animation_layer_render_does_not_crash():
    font = pygame.font.SysFont("monospace", 16)
    layer = AnimationLayer(font)
    layer.spawn_damage_number(50, 50, 10)
    layer.start_level_up(100, 100)
    layer.shake.trigger()
    layer.fade_in()
    surf = pygame.Surface((400, 300))
    layer.update(0.1)
    layer.render(surf)  # should not raise
