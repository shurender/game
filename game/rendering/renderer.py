"""Core rendering utilities and draw helpers."""
from __future__ import annotations

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS


class Renderer:
    """Wraps the display surface and provides commonly-used drawing helpers.

    Higher-level code (states, UI) can also draw directly to the surface;
    this class just centralises reusable primitives.
    """

    def __init__(self, surface: pygame.Surface) -> None:
        self.surface = surface
        self._fade_surface = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )

    def clear(self, color: tuple[int, ...] | None = None) -> None:
        """Fill the screen with a solid color."""
        self.surface.fill(color or COLORS["bg_dark"])

    def draw_gradient_rect(
        self,
        rect: pygame.Rect,
        color_top: tuple[int, ...],
        color_bottom: tuple[int, ...],
    ) -> None:
        """Draw a vertical gradient rectangle."""
        for y in range(rect.height):
            t = y / max(1, rect.height - 1)
            r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t)
            g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t)
            b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t)
            pygame.draw.line(
                self.surface, (r, g, b),
                (rect.x, rect.y + y), (rect.x + rect.width, rect.y + y),
            )

    def draw_panel(
        self,
        rect: pygame.Rect,
        bg_color: tuple[int, ...] | None = None,
        border_color: tuple[int, ...] | None = None,
        border_radius: int = 8,
        alpha: int = 220,
    ) -> None:
        """Draw a semi-transparent panel with optional border."""
        bg = bg_color or COLORS["bg_medium"]
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            panel, (*bg[:3], alpha), panel.get_rect(), border_radius=border_radius
        )
        if border_color:
            pygame.draw.rect(
                panel, border_color, panel.get_rect(),
                width=2, border_radius=border_radius,
            )
        self.surface.blit(panel, rect.topleft)

    def fade(self, alpha: int, color: tuple[int, ...] = (0, 0, 0)) -> None:
        """Draw a translucent overlay for fade effects."""
        self._fade_surface.fill((*color[:3], alpha))
        self.surface.blit(self._fade_surface, (0, 0))
