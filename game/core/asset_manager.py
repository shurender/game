"""Centralized asset loading and caching."""
from __future__ import annotations

import os
import pygame

from config import IMAGES_DIR, SOUNDS_DIR, FONTS_DIR


class AssetManager:
    """Loads and caches images, sounds, and fonts.

    All assets are loaded lazily on first access and cached for reuse.
    Procedurally generated surfaces can also be stored via ``cache_surface``.
    """

    def __init__(self) -> None:
        self._images: dict[str, pygame.Surface] = {}
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._fonts: dict[tuple[str | None, int], pygame.font.Font] = {}

    def load_image(self, name: str, alpha: bool = True) -> pygame.Surface:
        """Load an image from the images directory, with caching."""
        if name not in self._images:
            path = os.path.join(IMAGES_DIR, name)
            if os.path.exists(path):
                image = pygame.image.load(path)
                self._images[name] = image.convert_alpha() if alpha else image.convert()
            else:
                # Return a placeholder magenta square
                surface = pygame.Surface((32, 32))
                surface.fill((255, 0, 255))
                self._images[name] = surface
        return self._images[name]

    def load_sound(self, name: str) -> pygame.mixer.Sound | None:
        """Load a sound from the sounds directory, with caching."""
        if name not in self._sounds:
            path = os.path.join(SOUNDS_DIR, name)
            if os.path.exists(path):
                self._sounds[name] = pygame.mixer.Sound(path)
            else:
                return None
        return self._sounds[name]

    def get_font(self, size: int, name: str | None = None) -> pygame.font.Font:
        """Get a font at the given size.

        If *name* is given it is looked up in the fonts directory.
        Falls back to the Pygame default font.
        """
        key = (name, size)
        if key not in self._fonts:
            if name:
                path = os.path.join(FONTS_DIR, name)
                if os.path.exists(path):
                    self._fonts[key] = pygame.font.Font(path, size)
                else:
                    self._fonts[key] = pygame.font.Font(None, size)
            else:
                self._fonts[key] = pygame.font.Font(None, size)
        return self._fonts[key]

    def cache_surface(self, name: str, surface: pygame.Surface) -> None:
        """Manually cache a surface (useful for procedurally generated assets)."""
        self._images[name] = surface

    def clear(self) -> None:
        """Clear all cached assets."""
        self._images.clear()
        self._sounds.clear()
        self._fonts.clear()
