"""Collision detection and spatial queries."""
from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.world.map import TileMap

from game.world.tile import get_tile_info


class CollisionManager:
    """Handles collision queries against a tile map."""

    def __init__(self, tile_map: TileMap) -> None:
        self.map = tile_map

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a coordinate is within bounds and walkable."""
        if x < 0 or y < 0 or x >= self.map.width or y >= self.map.height:
            return False
        
        # Check collision layer first (1 = solid)
        if self.map.collision and self.map.collision[y][x] == 1:
            return False
            
        # Check for NPCs blocking path
        if self.map.get_npc_at(x, y) is not None:
            return False
            
        # Check ground tile info
        if self.map.ground:
            tile_id = self.map.ground[y][x]
            tile_info = get_tile_info(tile_id)
            return tile_info.walkable
            
        return True
