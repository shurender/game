"""Procedurally generates sprites and tiles using Pygame draw calls."""
from __future__ import annotations

import pygame
import math

from config import TILE_SIZE
from game.player.player import Direction


class SpriteGenerator:
    """Generates and caches surface textures procedurally."""

    def __init__(self) -> None:
        self.cache: dict[str, pygame.Surface] = {}

    def get_tile_surface(self, tile_info, seed_x: int, seed_y: int) -> pygame.Surface:
        """Generate a procedural texture for a tile based on its properties."""
        key = f"tile_{tile_info.id}_{seed_x % 3}_{seed_y % 3}"
        if key in self.cache:
            return self.cache[key]

        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill(tile_info.color)
        
        # Add some texture variation based on position
        if tile_info.id == 1:  # Grass
            for i in range(3):
                x = (seed_x * 7 + i * 11) % TILE_SIZE
                y = (seed_y * 13 + i * 5) % TILE_SIZE
                pygame.draw.line(surf, (60, 160, 80), (x, y), (x, y - 4), 2)
        elif tile_info.id == 2:  # Tree
            pygame.draw.circle(surf, (30, 90, 40), (TILE_SIZE // 2, TILE_SIZE // 2 + 4), TILE_SIZE // 2 - 2)
            pygame.draw.circle(surf, (40, 120, 60), (TILE_SIZE // 2, TILE_SIZE // 2 - 4), TILE_SIZE // 2 - 2)
        elif tile_info.id == 6:  # Tall Grass
            for i in range(8):
                x = (seed_x * 3 + i * 7) % TILE_SIZE
                y = (seed_y * 5 + i * 13) % TILE_SIZE
                pygame.draw.line(surf, (40, 120, 60), (x, y), (x + 2, y - 8), 2)
        elif tile_info.id == 10: # Wall
            pygame.draw.rect(surf, (80, 80, 80), (0, 0, TILE_SIZE, TILE_SIZE), 2)
            pygame.draw.line(surf, (80, 80, 80), (0, TILE_SIZE // 2), (TILE_SIZE, TILE_SIZE // 2), 2)
            
        self.cache[key] = surf
        return surf

    def get_player_sprite(self, direction: Direction, is_moving: bool, anim_timer: float) -> pygame.Surface:
        """Generate player sprite for current facing and animation state."""
        frame = 0
        if is_moving:
            frame = int(anim_timer) % 4
            
        key = f"player_{direction.name}_{frame}"
        if key in self.cache:
            return self.cache[key]

        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        # Base colors
        skin = (255, 200, 150)
        shirt = (200, 50, 50)
        pants = (50, 100, 200)
        hair = (100, 50, 20)
        
        # Bobbing effect
        y_offset = -2 if frame in (1, 3) else 0
        
        # Draw character
        # Pants
        pygame.draw.rect(surf, pants, (8, 20 + y_offset, 16, 12), border_radius=2)
        
        # Shirt
        pygame.draw.rect(surf, shirt, (6, 10 + y_offset, 20, 12), border_radius=4)
        
        # Head
        pygame.draw.circle(surf, skin, (TILE_SIZE // 2, 8 + y_offset), 8)
        
        # Hair/Hat
        pygame.draw.arc(surf, hair, (6, y_offset-2, 20, 16), 0, math.pi, 5)
        
        # Details based on direction
        if direction == Direction.DOWN:
            # Eyes
            pygame.draw.rect(surf, (0, 0, 0), (12, 6 + y_offset, 2, 2))
            pygame.draw.rect(surf, (0, 0, 0), (18, 6 + y_offset, 2, 2))
        elif direction == Direction.RIGHT:
            pygame.draw.rect(surf, (0, 0, 0), (18, 6 + y_offset, 2, 2))
        elif direction == Direction.LEFT:
            pygame.draw.rect(surf, (0, 0, 0), (12, 6 + y_offset, 2, 2))
            
        self.cache[key] = surf
        return surf
