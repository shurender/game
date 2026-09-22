"""Manages the current active map and transitions."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.core.game import Game

from game.world.map import TileMap


class World:
    """Handles loading maps and transitioning between them."""

    def __init__(self, game: Game) -> None:
        self.game = game
        self.current_map: TileMap | None = None
        self.transitioning: bool = False

    def load_map(self, map_id: str) -> None:
        """Load a new map."""
        self.current_map = TileMap(map_id)
        # BGM changes could happen here later based on map name
