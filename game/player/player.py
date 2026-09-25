"""Player entity with grid-based movement and smooth interpolation."""
from __future__ import annotations

from enum import Enum, auto

from config import TILE_SIZE
from game.utils.helpers import lerp


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class Player:
    """The player character on the overworld map."""

    def __init__(self, x: int, y: int) -> None:
        # Grid coordinates
        self.x = x
        self.y = y
        self.name = "Player"
        
        # Pixel coordinates (for rendering smooth movement)
        self.pixel_x = float(x * TILE_SIZE)
        self.pixel_y = float(y * TILE_SIZE)
        
        self.facing = Direction.DOWN
        self.is_moving = False
        self.move_speed = 4.0  # Tiles per second (natural walking/running pace)

        # Animation state
        self.anim_timer = 0.0

    def start_move(self, dx: int, dy: int) -> None:
        """Initiate movement to an adjacent tile."""
        if dx > 0: self.facing = Direction.RIGHT
        elif dx < 0: self.facing = Direction.LEFT
        elif dy > 0: self.facing = Direction.DOWN
        elif dy < 0: self.facing = Direction.UP

        self.x += dx
        self.y += dy
        self.is_moving = True
        self.anim_timer = 0.0

    def turn(self, direction: Direction) -> None:
        """Change facing direction without moving."""
        self.facing = direction

    def update(self, dt: float) -> None:
        """Update smooth movement interpolation."""
        target_pixel_x = float(self.x * TILE_SIZE)
        target_pixel_y = float(self.y * TILE_SIZE)

        if self.is_moving:
            self.anim_timer += dt * 8.0
            
            # Move towards target
            dx = target_pixel_x - self.pixel_x
            dy = target_pixel_y - self.pixel_y
            dist = (dx**2 + dy**2)**0.5
            
            move_amt = self.move_speed * TILE_SIZE * dt
            
            if dist <= move_amt:
                # Snap to grid
                self.pixel_x = target_pixel_x
                self.pixel_y = target_pixel_y
                self.is_moving = False
            else:
                self.pixel_x += (dx / dist) * move_amt
                self.pixel_y += (dy / dist) * move_amt
        else:
            # Ensure snapped and advance idle breathing animation
            self.pixel_x = target_pixel_x
            self.pixel_y = target_pixel_y
            self.anim_timer += dt * 6.0

    def get_facing_offset(self) -> tuple[int, int]:
        """Return the grid offset of the tile the player is facing."""
        if self.facing == Direction.UP: return 0, -1
        if self.facing == Direction.DOWN: return 0, 1
        if self.facing == Direction.LEFT: return -1, 0
        if self.facing == Direction.RIGHT: return 1, 0
        return 0, 0

    def interact(self) -> tuple[int, int]:
        """Return the coordinates of the tile within interaction range."""
        dx, dy = self.get_facing_offset()
        # Interaction range is exactly 1 tile in front of the player
        return self.x + dx, self.y + dy
