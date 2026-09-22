"""Reusable vertical menu component with cursor navigation."""
from __future__ import annotations

import math
from typing import Callable

import pygame

from config import COLORS
from game.ui.text import render_text


class Menu:
    """A vertical list menu with animated cursor.

    Items are drawn top-to-bottom. The currently selected item is
    highlighted, and a small triangle cursor bobs beside it.
    """

    def __init__(
        self,
        items: list[str],
        font: pygame.font.Font,
        x: int,
        y: int,
        spacing: int = 40,
        color: tuple[int, ...] | None = None,
        highlight_color: tuple[int, ...] | None = None,
        on_select: Callable[[int, str], None] | None = None,
    ) -> None:
        self.items = items
        self.font = font
        self.x = x
        self.y = y
        self.spacing = spacing
        self.color = color or COLORS["text_dim"]
        self.highlight_color = highlight_color or COLORS["accent"]
        self.on_select = on_select
        self.cursor: int = 0
        self._cursor_bob: float = 0.0

    def move_up(self) -> None:
        """Move the cursor up (wraps around)."""
        self.cursor = (self.cursor - 1) % len(self.items)

    def move_down(self) -> None:
        """Move the cursor down (wraps around)."""
        self.cursor = (self.cursor + 1) % len(self.items)

    def select(self) -> int:
        """Trigger the selection callback and return the cursor index."""
        if self.on_select:
            self.on_select(self.cursor, self.items[self.cursor])
        return self.cursor

    def update(self, dt: float) -> None:
        """Animate the cursor bob."""
        self._cursor_bob += dt * 3.0

    def draw(self, surface: pygame.Surface, center: bool = False) -> None:
        """Draw all menu items with the animated cursor indicator."""
        for i, item in enumerate(self.items):
            is_selected = i == self.cursor
            color = self.highlight_color if is_selected else self.color

            item_x = self.x
            item_y = self.y + i * self.spacing

            if is_selected:
                bob_offset = math.sin(self._cursor_bob) * 3
                cursor_x = item_x - 25 + bob_offset
                cursor_y = (
                    item_y + self.font.get_height() // 2 if not center else item_y
                )
                points = [
                    (cursor_x, cursor_y - 6),
                    (cursor_x + 10, cursor_y),
                    (cursor_x, cursor_y + 6),
                ]
                pygame.draw.polygon(surface, self.highlight_color, points)

            render_text(
                surface, item, self.font, item_x, item_y,
                color=color, shadow=True, center=center,
            )
