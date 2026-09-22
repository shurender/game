"""Tile definitions and properties."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TileInfo:
    """Information about a specific tile type."""
    id: int
    name: str
    walkable: bool
    color: tuple[int, int, int]
    is_encounter: bool = False
    is_water: bool = False


# A minimal tileset for the procedural renderer
TILE_DEFS = {
    0: TileInfo(0, "Empty", False, (0, 0, 0)),
    1: TileInfo(1, "Grass", True, (80, 180, 100)),
    2: TileInfo(2, "Tree", False, (40, 120, 60)),
    3: TileInfo(3, "Path", True, (210, 180, 140)),
    4: TileInfo(4, "Door", True, (139, 69, 19)),
    5: TileInfo(5, "Water", False, (60, 140, 220), is_water=True),
    6: TileInfo(6, "Tall Grass", True, (60, 160, 80), is_encounter=True),
    10: TileInfo(10, "Wall", False, (100, 100, 100)),
    11: TileInfo(11, "Floor", True, (180, 150, 120)),
    12: TileInfo(12, "Carpet", True, (200, 80, 80)),
}


def get_tile_info(tile_id: int) -> TileInfo:
    """Get information for a tile ID, defaulting to Empty."""
    return TILE_DEFS.get(tile_id, TILE_DEFS[0])
