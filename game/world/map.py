"""Tile map loading, collision checking, and rendering."""
from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pygame

from config import DATA_DIR
from game.world.tile import get_tile_info
from game.world.npc import NPC
from game.world.trainer import Trainer
from game.world.shop_npc import ShopNPC
from game.player.player import Direction


class Warp:
    """Represents a warp point to another map."""
    def __init__(self, x: int, y: int, target_map: str, target_x: int, target_y: int):
        self.x = x
        self.y = y
        self.target_map = target_map
        self.target_x = target_x
        self.target_y = target_y


class TileMap:
    """Manages the current map's grid data."""

    def __init__(self, map_id: str) -> None:
        self.map_id = map_id
        self.name = ""
        self.width = 0
        self.height = 0
        self.ground: list[list[int]] = []
        self.collision: list[list[int]] = []
        self.encounter: list[list[int]] = []
        self.encounter_table: list[dict] = []
        self.warps: list[Warp] = []
        self.npcs: list[NPC] = []
        self._load_map()

    def _load_map(self) -> None:
        """Load map data from maps.json."""
        path = os.path.join(DATA_DIR, "maps.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        map_data = data["maps"].get(self.map_id)
        if not map_data:
            raise ValueError(f"Map {self.map_id} not found in maps.json")

        self.name = map_data["name"]
        self.width = map_data["width"]
        self.height = map_data["height"]
        
        layers = map_data["layers"]
        self.ground = layers.get("ground", [])
        self.collision = layers.get("collision", [])
        self.encounter = layers.get("encounter", [])
        self.encounter_table = map_data.get("encounter_table", [])

        from game.world.progress_manager import WorldProgressManager
        pm = WorldProgressManager.get_instance()
        
        for w in map_data.get("warps", []):
            if "conditions" in w and not pm.check_conditions(w["conditions"]):
                continue
            self.warps.append(
                Warp(
                    w["x"], w["y"], w["target_map"],
                    w["target_x"], w["target_y"]
                )
            )

        for n_data in map_data.get("npcs", []):
            if "conditions" in n_data and not pm.check_conditions(n_data["conditions"]):
                continue
                
            facing_map = {
                "up": Direction.UP, "down": Direction.DOWN,
                "left": Direction.LEFT, "right": Direction.RIGHT
            }
            facing = facing_map.get(n_data.get("facing", "down"), Direction.DOWN)
            
            if "trainer_id" in n_data:
                npc = Trainer(
                    n_data["id"], n_data["name"], n_data["x"], n_data["y"],
                    n_data["sprite"], facing, n_data.get("dialogue_id", ""),
                    n_data["trainer_id"]
                )
            elif "shop_id" in n_data:
                npc = ShopNPC(
                    n_data["id"], n_data["name"], n_data["x"], n_data["y"],
                    n_data["sprite"], facing, n_data.get("dialogue_id", ""),
                    n_data["shop_id"]
                )
            else:
                npc = NPC(
                    n_data["id"], n_data["name"], n_data["x"], n_data["y"],
                    n_data["sprite"], facing, n_data["dialogue_id"]
                )
                
            if "conditional_dialogues" in n_data:
                npc.conditional_dialogues = n_data["conditional_dialogues"]
                
            self.npcs.append(npc)

    def get_warp_at(self, x: int, y: int) -> Warp | None:
        """Return the warp at a location, if any."""
        for warp in self.warps:
            if warp.x == x and warp.y == y:
                return warp
        return None
        
    def get_npc_at(self, x: int, y: int) -> NPC | None:
        """Return the NPC at a location, if any."""
        for npc in self.npcs:
            if npc.x == x and npc.y == y:
                return npc
        return None
        
    def is_encounter(self, x: int, y: int) -> bool:
        """Check if a coordinate has an encounter zone."""
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        if self.encounter and self.encounter[y][x] == 1:
            return True
        # Also check ground tile info as fallback
        if self.ground:
            tile_id = self.ground[y][x]
            return get_tile_info(tile_id).is_encounter
        return False
        
    def generate_wild_encounter(self) -> Any | None:
        """Roll and return a wild creature based on the encounter table."""
        if not self.encounter_table:
            return None
            
        import random
        from game.creatures.creature import Creature
        
        # Calculate total weight
        total_weight = sum(entry.get("weight", 10) for entry in self.encounter_table)
        roll = random.uniform(0, total_weight)
        
        current = 0
        for entry in self.encounter_table:
            current += entry.get("weight", 10)
            if roll <= current:
                level_min = entry.get("level_min", 2)
                level_max = entry.get("level_max", level_min)
                level = random.randint(level_min, level_max)
                return Creature(entry["creature"], level)
                
        return None
