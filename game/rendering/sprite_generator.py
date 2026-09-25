"""Procedurally generates sprites and tiles, and loads character spritesheets."""
from __future__ import annotations

import os
import pygame
import math
import logging

from config import TILE_SIZE, BASE_DIR
from game.player.player import Direction

logger = logging.getLogger("risu")


class SpriteGenerator:
    """Generates and caches surface textures procedurally or from sprite assets."""

    def __init__(self) -> None:
        self.cache: dict[str, pygame.Surface] = {}
        self.mc_frames: dict[str, dict[str, list[pygame.Surface]]] = {"IDLE": {}, "RUN": {}}
        self._load_mc_sprites()

    def _load_mc_sprites(self) -> None:
        """Load the main character spritesheets (IDLE & RUN in 4 directions)."""
        mc_base = os.path.join(BASE_DIR, "characters", "MC", "Sprites")
        if not os.path.exists(mc_base):
            return

        for state in ("IDLE", "RUN"):
            for d in ("down", "up", "left", "right"):
                path = os.path.join(mc_base, state, f"{state.lower()}_{d}.png")
                if os.path.exists(path):
                    try:
                        sheet = pygame.image.load(path)
                        w, h = sheet.get_size()
                        frame_count = 8
                        fw = w // frame_count
                        frame_list: list[pygame.Surface] = []
                        for i in range(frame_count):
                            # Crop centered character box (32x40)
                            frame_surf = pygame.Surface((32, 40), pygame.SRCALPHA)
                            frame_surf.blit(sheet, (0, 0), pygame.Rect(i * fw + 32, 22, 32, 40))
                            frame_list.append(frame_surf)
                        self.mc_frames[state][d] = frame_list
                    except Exception as e:
                        logger.warning(f"Could not load MC sprite {path}: {e}")

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
        """Return player sprite for current facing and animation state."""
        state = "RUN" if is_moving else "IDLE"
        dir_key = direction.name.lower()
        frames = self.mc_frames.get(state, {}).get(dir_key)
        if frames:
            idx = int(anim_timer) % len(frames)
            return frames[idx]

        # Procedural fallback if MC sprites are not found
        frame = int(anim_timer) % 4 if is_moving else 0
        key = f"player_{direction.name}_{frame}"
        if key in self.cache:
            return self.cache[key]

        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        skin = (255, 200, 150)
        shirt = (200, 50, 50)
        pants = (50, 100, 200)
        hair = (100, 50, 20)
        y_offset = -2 if frame in (1, 3) else 0

        pygame.draw.rect(surf, pants, (8, 20 + y_offset, 16, 12), border_radius=2)
        pygame.draw.rect(surf, shirt, (6, 10 + y_offset, 20, 12), border_radius=4)
        pygame.draw.circle(surf, skin, (TILE_SIZE // 2, 8 + y_offset), 8)
        pygame.draw.arc(surf, hair, (6, y_offset - 2, 20, 16), 0, math.pi, 5)

        if direction == Direction.DOWN:
            pygame.draw.rect(surf, (0, 0, 0), (12, 6 + y_offset, 2, 2))
            pygame.draw.rect(surf, (0, 0, 0), (18, 6 + y_offset, 2, 2))
        elif direction == Direction.RIGHT:
            pygame.draw.rect(surf, (0, 0, 0), (18, 6 + y_offset, 2, 2))
        elif direction == Direction.LEFT:
            pygame.draw.rect(surf, (0, 0, 0), (12, 6 + y_offset, 2, 2))

        self.cache[key] = surf
        return surf

    def get_npc_sprite(self, direction: Direction, sprite_name: str = "") -> pygame.Surface:
        """Return distinct procedural NPC sprite based on name and facing direction."""
        key = f"npc_{sprite_name}_{direction.name}"
        if key in self.cache:
            return self.cache[key]

        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        name_lower = sprite_name.lower()
        if "f_" in name_lower or "mom" in name_lower:
            skin = (255, 215, 175)
            shirt = (220, 100, 150)
            pants = (70, 70, 130)
            hair = (110, 60, 30)
        elif "prof" in name_lower or "cedar" in name_lower:
            skin = (250, 205, 160)
            shirt = (240, 240, 245)
            pants = (60, 60, 70)
            hair = (170, 170, 180)
        elif "shop" in name_lower:
            skin = (255, 200, 150)
            shirt = (50, 160, 100)
            pants = (50, 50, 60)
            hair = (80, 50, 20)
        elif "hiker" in name_lower:
            skin = (230, 180, 140)
            shirt = (180, 120, 50)
            pants = (100, 80, 50)
            hair = (50, 30, 10)
        elif "boss" in name_lower or "grunt" in name_lower:
            skin = (240, 195, 150)
            shirt = (40, 40, 50)
            pants = (30, 30, 40)
            hair = (200, 40, 40)
        else:
            skin = (255, 200, 150)
            shirt = (70, 130, 220)
            pants = (50, 60, 70)
            hair = (60, 40, 20)

        pygame.draw.rect(surf, pants, (8, 20, 16, 12), border_radius=2)
        pygame.draw.rect(surf, shirt, (6, 10, 20, 12), border_radius=4)
        pygame.draw.circle(surf, skin, (TILE_SIZE // 2, 8), 8)
        pygame.draw.arc(surf, hair, (6, -2, 20, 16), 0, math.pi, 5)

        if direction == Direction.DOWN:
            pygame.draw.rect(surf, (0, 0, 0), (12, 6, 2, 2))
            pygame.draw.rect(surf, (0, 0, 0), (18, 6, 2, 2))
        elif direction == Direction.RIGHT:
            pygame.draw.rect(surf, (0, 0, 0), (18, 6, 2, 2))
        elif direction == Direction.LEFT:
            pygame.draw.rect(surf, (0, 0, 0), (12, 6, 2, 2))

        self.cache[key] = surf
        return surf
