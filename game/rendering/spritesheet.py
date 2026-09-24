"""SpriteSheet class for slicing and managing 2D sprite grids safely."""
from __future__ import annotations

import logging
import pygame
from typing import Any

logger = logging.getLogger("risu.spritesheet")


class SpriteSheet:
    """Represents a sprite sheet image partitioned into regular frames.

    Provides safe sub-surface retrieval by index or grid coordinates.
    Out-of-bounds frame requests return a safe placeholder frame rather
    than crashing the game during development.
    """

    def __init__(
        self,
        surface: pygame.Surface,
        frame_width: int,
        frame_height: int,
        spacing: int = 0,
        margin: int = 0,
        is_placeholder: bool = False,
    ) -> None:
        self.surface = surface
        self.frame_width = max(1, frame_width)
        self.frame_height = max(1, frame_height)
        self.spacing = max(0, spacing)
        self.margin = max(0, margin)
        self.is_placeholder = is_placeholder

        surf_w, surf_h = surface.get_size()
        usable_w = max(0, surf_w - 2 * self.margin + self.spacing)
        usable_h = max(0, surf_h - 2 * self.margin + self.spacing)

        step_w = self.frame_width + self.spacing
        step_h = self.frame_height + self.spacing

        self.cols = max(1, usable_w // step_w) if step_w > 0 else 1
        self.rows = max(1, usable_h // step_h) if step_h > 0 else 1
        self.total_frames = self.cols * self.rows

        self._frame_cache: dict[int, pygame.Surface] = {}
        self._oob_fallback: pygame.Surface | None = None

    def get_frame(self, index: int) -> pygame.Surface:
        """Retrieve a frame by 0-based index in row-major order."""
        if index < 0 or index >= self.total_frames:
            logger.warning(
                f"SpriteSheet index {index} out of bounds (0..{self.total_frames - 1}). "
                "Returning fallback frame."
            )
            return self._get_oob_fallback()

        if index not in self._frame_cache:
            col = index % self.cols
            row = index // self.cols
            self._frame_cache[index] = self.get_image(col, row)
        return self._frame_cache[index]

    def get_image(self, col: int, row: int) -> pygame.Surface:
        """Retrieve a frame by column and row coordinates."""
        if col < 0 or col >= self.cols or row < 0 or row >= self.rows:
            logger.warning(
                f"SpriteSheet coord ({col}, {row}) out of bounds "
                f"(cols={self.cols}, rows={self.rows}). Returning fallback frame."
            )
            return self._get_oob_fallback()

        x = self.margin + col * (self.frame_width + self.spacing)
        y = self.margin + row * (self.frame_height + self.spacing)
        rect = pygame.Rect(x, y, self.frame_width, self.frame_height)
        return self.get_sub_surface(rect)

    def get_sub_surface(self, rect: pygame.Rect | tuple[int, int, int, int]) -> pygame.Surface:
        """Safely extract an arbitrary rectangular sub-surface."""
        if not isinstance(rect, pygame.Rect):
            rect = pygame.Rect(*rect)

        surf_rect = self.surface.get_rect()
        sub = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        # Intersect with available surface to prevent crashes
        clipped = rect.clip(surf_rect)
        if clipped.width > 0 and clipped.height > 0:
            dest_x = clipped.x - rect.x
            dest_y = clipped.y - rect.y
            sub.blit(self.surface, (dest_x, dest_y), clipped)

        return sub

    def get_frames(self, start: int = 0, count: int | None = None) -> list[pygame.Surface]:
        """Return a slice of frames as a list."""
        if start < 0:
            start = 0
        if count is None:
            count = max(0, self.total_frames - start)
        return [self.get_frame(i) for i in range(start, start + count)]

    def get_row(self, row: int, max_frames: int | None = None) -> list[pygame.Surface]:
        """Return all frames in a single row."""
        limit = self.cols if max_frames is None else min(self.cols, max(0, max_frames))
        return [self.get_image(col, row) for col in range(limit)]

    def get_column(self, col: int, max_frames: int | None = None) -> list[pygame.Surface]:
        """Return all frames in a single column."""
        limit = self.rows if max_frames is None else min(self.rows, max(0, max_frames))
        return [self.get_image(col, row) for row in range(limit)]

    def _get_oob_fallback(self) -> pygame.Surface:
        """Generate or return a cached out-of-bounds placeholder frame."""
        if self._oob_fallback is None:
            self._oob_fallback = pygame.Surface(
                (self.frame_width, self.frame_height), pygame.SRCALPHA
            )
            self._oob_fallback.fill((180, 40, 40, 220))  # Warning reddish
            pygame.draw.rect(
                self._oob_fallback,
                (255, 220, 60),  # Yellow warning border
                self._oob_fallback.get_rect(),
                width=max(1, min(self.frame_width, self.frame_height) // 8),
            )
        return self._oob_fallback
