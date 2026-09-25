"""Tests for the MC character sprite loading and animation integration."""
import os
import pygame
from game.rendering.sprite_generator import SpriteGenerator
from game.player.player import Direction, Player
from game.battle.capture import calculate_capture, execute_capture, CaptureItem
from game.inventory.item import Item
from game.creatures.creature import Creature
from game.creatures.creature_factory import CreatureFactory


def test_mc_sprites_loaded():
    """Verify that all 8 MC spritesheets (IDLE & RUN in 4 directions) are loaded with 8 frames each."""
    sg = SpriteGenerator()
    assert "IDLE" in sg.mc_frames
    assert "RUN" in sg.mc_frames
    
    for d in ("down", "up", "left", "right"):
        assert d in sg.mc_frames["IDLE"], f"Missing IDLE {d}"
        assert len(sg.mc_frames["IDLE"][d]) == 8, f"IDLE {d} should have 8 frames"
        
        assert d in sg.mc_frames["RUN"], f"Missing RUN {d}"
        assert len(sg.mc_frames["RUN"][d]) == 8, f"RUN {d} should have 8 frames"


def test_player_sprite_generation():
    """Verify get_player_sprite returns valid surfaces with 32x40 character size for idle and run."""
    sg = SpriteGenerator()
    for direction in (Direction.DOWN, Direction.UP, Direction.LEFT, Direction.RIGHT):
        idle_surf = sg.get_player_sprite(direction, is_moving=False, anim_timer=0.0)
        assert isinstance(idle_surf, pygame.Surface)
        assert idle_surf.get_size() == (32, 40)
        
        run_surf = sg.get_player_sprite(direction, is_moving=True, anim_timer=2.5)
        assert isinstance(run_surf, pygame.Surface)
        assert run_surf.get_size() == (32, 40)


def test_player_anim_timer_advancement():
    """Verify Player.update advances anim_timer during both idle and move states."""
    player = Player(4, 6)
    initial_timer = player.anim_timer
    
    # Idle update
    player.update(0.1)
    assert player.anim_timer > initial_timer
    
    # Moving update
    player.start_move(1, 0)
    move_timer = player.anim_timer
    player.update(0.05)
    assert player.anim_timer > move_timer


def test_capture_with_inventory_item():
    """Verify calculate_capture and execute_capture work with inventory Item instances."""
    cf = CreatureFactory.get_instance()
    creature = cf.create_creature("florbit", level=5)
    
    # Inventory Item
    item = Item(
        item_id="capture_orb",
        name="Capture Orb",
        category="Capture",
        effect="capture",
        value=1.0,
        price=200,
        description="Used to capture wild creatures."
    )
    
    success, shakes = calculate_capture(creature, item)
    assert isinstance(success, bool)
    assert 0 <= shakes <= 3
    
    success, shakes, location = execute_capture(creature, item)
    assert isinstance(success, bool)
    assert location in ("PARTY", "STORAGE", "NONE")
