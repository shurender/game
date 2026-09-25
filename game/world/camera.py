"""2D camera with smooth target following."""
from __future__ import annotations

from game.utils.helpers import lerp


class Camera:
    """A 2D camera that follows a target with smooth scrolling.

    Coordinates represent the top-left corner of the viewport in world space.
    """

    def __init__(self, width: int, height: int) -> None:
        self.x: float = 0.0
        self.y: float = 0.0
        self.width = width
        self.height = height
        self.smoothing: float = 5.0  # Higher = snappier

    def follow(self, target_x: float, target_y: float, dt: float) -> None:
        """Smoothly move the camera to center on the target position."""
        goal_x = target_x - self.width / 2
        goal_y = target_y - self.height / 2
        factor = min(1.0, self.smoothing * dt)
        self.x = lerp(self.x, goal_x, factor)
        self.y = lerp(self.y, goal_y, factor)

    def apply(self, world_x: float, world_y: float) -> tuple[float, float]:
        """Convert world coordinates to screen coordinates."""
        return world_x - self.x, world_y - self.y

    def clamp_to_map(self, map_width: int, map_height: int) -> None:
        """Clamp the camera so it doesn't show beyond map boundaries.
        If the map is smaller than the camera viewport, center it.
        """
        if map_width <= self.width:
            self.x = (map_width - self.width) / 2.0
        else:
            self.x = max(0.0, min(self.x, float(map_width - self.width)))

        if map_height <= self.height:
            self.y = (map_height - self.height) / 2.0
        else:
            self.y = max(0.0, min(self.y, float(map_height - self.height)))

    def center_on(self, x: float, y: float) -> None:
        """Immediately center the camera on a world position."""
        self.x = x - self.width / 2
        self.y = y - self.height / 2
