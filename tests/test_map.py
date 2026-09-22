"""Tests for TileMap loading and querying."""
import os
import json
import pytest
from unittest.mock import patch

from config import DATA_DIR
from game.world.map import TileMap
from game.world.collision import CollisionManager


# Mock maps.json data
MOCK_MAP_DATA = {
    "maps": {
        "test_map": {
            "name": "Test Map",
            "width": 3,
            "height": 3,
            "layers": {
                "ground": [
                    [1, 1, 1],
                    [1, 10, 1],
                    [1, 1, 1]
                ],
                "collision": [
                    [0, 0, 0],
                    [0, 1, 0],
                    [0, 0, 0]
                ],
                "encounter": [
                    [0, 0, 0],
                    [0, 0, 0],
                    [1, 1, 1]
                ]
            },
            "warps": [
                {"x": 1, "y": 0, "target_map": "other_map", "target_x": 5, "target_y": 5}
            ]
        }
    }
}


@pytest.fixture
def mock_json_load():
    with patch("builtins.open"), patch("json.load", return_value=MOCK_MAP_DATA):
        yield


class TestTileMap:
    
    def test_load_map(self, mock_json_load):
        tile_map = TileMap("test_map")
        assert tile_map.name == "Test Map"
        assert tile_map.width == 3
        assert tile_map.height == 3
        
    def test_is_walkable_bounds(self, mock_json_load):
        tile_map = TileMap("test_map")
        cm = CollisionManager(tile_map)
        assert not cm.is_walkable(-1, 0)
        assert not cm.is_walkable(0, -1)
        assert not cm.is_walkable(3, 0)
        assert not cm.is_walkable(0, 3)
        
    def test_is_walkable_collision(self, mock_json_load):
        tile_map = TileMap("test_map")
        cm = CollisionManager(tile_map)
        # Center tile has collision=1
        assert not cm.is_walkable(1, 1)
        # Other tiles have collision=0
        assert cm.is_walkable(0, 0)
        
    def test_is_walkable_tile_type(self, mock_json_load):
        # Even if collision is 0, if the tile type itself is not walkable (e.g. 10=Wall)
        # the TileMap.is_walkable checks ground type as well.
        tile_map = TileMap("test_map")
        cm = CollisionManager(tile_map)
        # 10 is Wall (not walkable). Wait, test mock says collision layer is [0,1,0].
        # Let's say we temporarily modify the mock collision so it's 0, but tile is 10.
        tile_map.collision[1][1] = 0 
        assert not cm.is_walkable(1, 1)

    def test_get_warp(self, mock_json_load):
        tile_map = TileMap("test_map")
        warp = tile_map.get_warp_at(1, 0)
        assert warp is not None
        assert warp.target_map == "other_map"
        
        warp2 = tile_map.get_warp_at(0, 0)
        assert warp2 is None
        
    def test_is_encounter(self, mock_json_load):
        tile_map = TileMap("test_map")
        assert tile_map.is_encounter(0, 2)
        assert tile_map.is_encounter(1, 2)
        assert tile_map.is_encounter(2, 2)
        assert not tile_map.is_encounter(0, 0)
