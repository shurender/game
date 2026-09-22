"""Text rendering helpers — shadow text, outlined text, typewriter effect."""
from __future__ import annotations

import pygame

from config import COLORS


def render_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    x: int,
    y: int,
    color: tuple[int, ...] | None = None,
    shadow: bool = False,
    center: bool = False,
) -> pygame.Rect:
    """Render text with an optional drop shadow.

    Returns the rect of the main (non-shadow) text blit.
    """
    color = color or COLORS["text"]

    if shadow:
        shadow_surf = font.render(text, True, (0, 0, 0))
        if center:
            shadow_rect = shadow_surf.get_rect(center=(x + 2, y + 2))
        else:
            shadow_rect = shadow_surf.get_rect(topleft=(x + 2, y + 2))
        surface.blit(shadow_surf, shadow_rect)

    text_surf = font.render(text, True, color)
    if center:
        text_rect = text_surf.get_rect(center=(x, y))
    else:
        text_rect = text_surf.get_rect(topleft=(x, y))
    surface.blit(text_surf, text_rect)
    return text_rect


def render_text_outlined(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    x: int,
    y: int,
    color: tuple[int, ...] | None = None,
    outline_color: tuple[int, ...] = (0, 0, 0),
    center: bool = False,
) -> pygame.Rect:
    """Render text with an outline (drawn in 8 directions behind the text)."""
    color = color or COLORS["text"]

    for dx in (-2, 0, 2):
        for dy in (-2, 0, 2):
            if dx == 0 and dy == 0:
                continue
            outline_surf = font.render(text, True, outline_color)
            if center:
                rect = outline_surf.get_rect(center=(x + dx, y + dy))
            else:
                rect = outline_surf.get_rect(topleft=(x + dx, y + dy))
            surface.blit(outline_surf, rect)

    text_surf = font.render(text, True, color)
    if center:
        text_rect = text_surf.get_rect(center=(x, y))
    else:
        text_rect = text_surf.get_rect(topleft=(x, y))
    surface.blit(text_surf, text_rect)
    return text_rect


class TypewriterText:
    """Reveals text character-by-character over time."""

    def __init__(self, text: str, chars_per_second: float = 30.0) -> None:
        self.full_text = text
        self.chars_per_second = chars_per_second
        self._elapsed: float = 0.0
        self._visible_chars: int = 0

    def update(self, dt: float) -> None:
        """Advance the typewriter effect."""
        if self.is_complete:
            return
        self._elapsed += dt
        self._visible_chars = min(
            len(self.full_text),
            int(self._elapsed * self.chars_per_second),
        )

    @property
    def visible_text(self) -> str:
        """The portion of text currently visible."""
        return self.full_text[: self._visible_chars]

    @property
    def is_complete(self) -> bool:
        """True when all characters are visible."""
        return self._visible_chars >= len(self.full_text)

    def skip(self) -> None:
        """Instantly reveal all text."""
        self._visible_chars = len(self.full_text)

    def reset(self, text: str | None = None) -> None:
        """Reset the effect, optionally with new text."""
        if text is not None:
            self.full_text = text
        self._elapsed = 0.0
        self._visible_chars = 0
