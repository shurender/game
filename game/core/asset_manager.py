"""Centralized asset loading, caching, path management, and fallback placeholders."""
from __future__ import annotations

import logging
import os
from typing import Any
import pygame

from config import (
    ASSET_DIRS,
    ASSETS_DIR,
    BGM_DIR,
    BGM_TEMPLATE,
    CREATURES_DIR,
    FONTS_DIR,
    ICONS_DIR,
    IMAGES_DIR,
    MUSIC_DIR,
    SFX_DIR,
    SOUNDS_DIR,
    SPRITES_DIR,
    SPRITESHEETS_DIR,
    TILES_DIR,
)
from game.rendering.spritesheet import SpriteSheet

logger = logging.getLogger("risu.assets")


class FallbackSound:
    """Safe no-op replacement for pygame.mixer.Sound when audio assets are missing.

    Ensures that play(), stop(), and volume calls never raise exceptions
    during development.
    """

    def __init__(self, name: str = "fallback_sound") -> None:
        self.name = name
        self._volume: float = 1.0

    def play(self, loops: int = 0, maxtime: int = 0, fade_ms: int = 0) -> None:
        logger.debug(f"FallbackSound '{self.name}'.play() called (no-op).")

    def stop(self) -> None:
        pass

    def fadeout(self, time: int) -> None:
        pass

    def set_volume(self, value: float) -> None:
        self._volume = max(0.0, min(1.0, float(value)))

    def get_volume(self) -> float:
        return self._volume

    def get_length(self) -> float:
        return 0.0

    def get_num_channels(self) -> int:
        return 0


class FallbackFont:
    """Safe fallback font if Pygame font initialization fails."""

    def __init__(self, size: int = 16) -> None:
        self.size_val = max(8, size)

    def render(
        self, text: str, antialias: bool, color: Any, background: Any = None
    ) -> pygame.Surface:
        w = max(8, len(str(text)) * (self.size_val // 2))
        h = max(8, self.size_val)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        return surf

    def size(self, text: str) -> tuple[int, int]:
        return (len(str(text)) * (self.size_val // 2), self.size_val)

    def get_height(self) -> int:
        return self.size_val

    def get_linesize(self) -> int:
        return self.size_val

    def get_ascent(self) -> int:
        return int(self.size_val * 0.8)

    def get_descent(self) -> int:
        return int(self.size_val * 0.2)


class AssetManager:
    """Centralized asset loader with caching, safe fallbacks, and directory management.

    Supports:
      * Images (PNG, JPG, WEBP)
      * Sprite sheets (grid frames, rows, subsurfaces)
      * Fonts (TTF, OTF, System, and default)
      * Sounds / SFX (WAV, OGG, MP3 with silent/synthesized fallbacks)
      * Music (BGM path resolution and safe playback)

    Missing assets log a warning and return non-crashing fallback placeholders.
    """

    IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
    SOUND_EXTENSIONS = (".wav", ".ogg", ".mp3")
    FONT_EXTENSIONS = (".ttf", ".otf")
    MUSIC_EXTENSIONS = (".ogg", ".mp3", ".wav")

    def __init__(self) -> None:
        self._images: dict[str, pygame.Surface] = {}
        self._spritesheets: dict[tuple[Any, ...], SpriteSheet] = {}
        self._sounds: dict[str, pygame.mixer.Sound | FallbackSound] = {}
        self._fonts: dict[tuple[str | None, int], pygame.font.Font | FallbackFont] = {}

        # Tracking for development audits
        self._missing_assets: set[str] = set()
        self._placeholder_assets: set[str] = set()

        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create standard asset directories if they do not yet exist."""
        for name, dir_path in ASSET_DIRS.items():
            try:
                os.makedirs(dir_path, exist_ok=True)
            except OSError as e:
                logger.warning(f"Could not create asset directory {dir_path}: {e}")

    # =========================================================================
    # Images
    # =========================================================================

    def _find_image_path(self, name: str) -> str | None:
        """Search configured image directories for a file matching name."""
        candidates = [
            name,
            os.path.join(IMAGES_DIR, name),
            os.path.join(SPRITES_DIR, name),
            os.path.join(SPRITESHEETS_DIR, name),
            os.path.join(TILES_DIR, name),
            os.path.join(CREATURES_DIR, name),
            os.path.join(ICONS_DIR, name),
        ]

        # Also search with extensions if name has none
        _, ext = os.path.splitext(name)
        if not ext:
            expanded = []
            for base in candidates:
                for e in self.IMAGE_EXTENSIONS:
                    expanded.append(f"{base}{e}")
            candidates.extend(expanded)

        for path in candidates:
            if os.path.isfile(path):
                return os.path.abspath(path)

        return None

    def get_image(
        self,
        name: str,
        size: tuple[int, int] | None = None,
        alpha: bool = True,
        fallback_color: tuple[int, int, int] | None = None,
    ) -> pygame.Surface:
        """Load an image by relative path or logical name, with caching.

        If the file is not found or fails to load, returns a fallback placeholder
        surface with a recognizable checkerboard dev pattern without crashing.
        """
        cache_key = f"{name}:{size}:{alpha}"
        if cache_key in self._images:
            return self._images[cache_key]

        resolved_path = self._find_image_path(name)
        surface: pygame.Surface | None = None

        if resolved_path:
            try:
                raw_image = pygame.image.load(resolved_path)
                surface = raw_image.convert_alpha() if alpha else raw_image.convert()
            except (pygame.error, OSError) as e:
                logger.warning(
                    f"Failed to load image at '{resolved_path}': {e}. Using fallback."
                )

        if surface is None:
            self._missing_assets.add(f"image:{name}")
            self._placeholder_assets.add(cache_key)
            w = size[0] if size else 32
            h = size[1] if size else 32
            surface = self.create_fallback_image(
                width=w, height=h, label=name, color=fallback_color
            )
        elif size is not None and surface.get_size() != size:
            surface = pygame.transform.scale(surface, size)

        self._images[cache_key] = surface
        return surface

    def load_image(self, name: str, alpha: bool = True) -> pygame.Surface:
        """Alias for get_image to maintain backward compatibility."""
        return self.get_image(name, alpha=alpha)

    def has_image(self, name: str) -> bool:
        """Return True if an image asset exists on disk."""
        return self._find_image_path(name) is not None

    def create_fallback_image(
        self,
        width: int = 32,
        height: int = 32,
        label: str = "?",
        color: tuple[int, int, int] | None = None,
    ) -> pygame.Surface:
        """Generate a magenta/dark checkerboard placeholder surface."""
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        c1 = color or (255, 0, 220)  # Magenta
        c2 = (35, 10, 45)  # Dark purple

        check_size = max(4, min(width, height) // 4)
        for y in range(0, height, check_size):
            for x in range(0, width, check_size):
                tile_c = (
                    c1
                    if ((x // check_size) + (y // check_size)) % 2 == 0
                    else c2
                )
                rect = pygame.Rect(
                    x, y, min(check_size, width - x), min(check_size, height - y)
                )
                surf.fill(tile_c, rect)

        # Border
        border_w = max(1, min(width, height) // 16)
        pygame.draw.rect(surf, (255, 255, 120), surf.get_rect(), border_w)

        # Label if size allows
        if width >= 24 and height >= 20 and label:
            try:
                font = pygame.font.Font(None, min(18, max(10, height - 4)))
                # Extract basename or short label
                short = os.path.splitext(os.path.basename(label))[0][:3]
                text_surf = font.render(short, True, (255, 255, 255))
                tx = (width - text_surf.get_width()) // 2
                ty = (height - text_surf.get_height()) // 2
                surf.blit(text_surf, (tx, ty))
            except Exception:
                pass

        return surf

    # =========================================================================
    # Sprite Sheets
    # =========================================================================

    def get_spritesheet(
        self,
        name: str,
        frame_width: int = 32,
        frame_height: int = 32,
        spacing: int = 0,
        margin: int = 0,
    ) -> SpriteSheet:
        """Load and cache a SpriteSheet from an image name or path.

        If missing, generates a fallback sprite sheet with distinguishable frames.
        """
        key = (name, frame_width, frame_height, spacing, margin)
        if key in self._spritesheets:
            return self._spritesheets[key]

        is_missing = not self.has_image(name)
        if is_missing:
            self._missing_assets.add(f"spritesheet:{name}")
            sheet = self.create_fallback_spritesheet(
                frame_width=frame_width,
                frame_height=frame_height,
                cols=4,
                rows=4,
            )
            sheet.is_placeholder = True
            self._placeholder_assets.add(f"spritesheet:{name}")
        else:
            base_surf = self.get_image(name)
            sheet = SpriteSheet(
                surface=base_surf,
                frame_width=frame_width,
                frame_height=frame_height,
                spacing=spacing,
                margin=margin,
                is_placeholder=False,
            )

        self._spritesheets[key] = sheet
        return sheet

    def load_spritesheet(
        self,
        name: str,
        frame_width: int = 32,
        frame_height: int = 32,
        spacing: int = 0,
        margin: int = 0,
    ) -> SpriteSheet:
        """Alias for get_spritesheet."""
        return self.get_spritesheet(
            name, frame_width, frame_height, spacing, margin
        )

    def create_fallback_spritesheet(
        self,
        frame_width: int = 32,
        frame_height: int = 32,
        cols: int = 4,
        rows: int = 4,
    ) -> SpriteSheet:
        """Generate a procedural multi-frame sprite sheet as a fallback."""
        total_w = cols * frame_width
        total_h = rows * frame_height
        sheet_surf = pygame.Surface((total_w, total_h), pygame.SRCALPHA)

        colors = [
            (220, 60, 60),
            (60, 180, 80),
            (60, 120, 220),
            (220, 180, 40),
            (180, 60, 220),
            (60, 200, 200),
        ]

        for r in range(rows):
            for c in range(cols):
                idx = r * cols + c
                fx = c * frame_width
                fy = r * frame_height
                color = colors[idx % len(colors)]
                frame_surf = self.create_fallback_image(
                    width=frame_width,
                    height=frame_height,
                    label=str(idx),
                    color=color,
                )
                sheet_surf.blit(frame_surf, (fx, fy))

        return SpriteSheet(
            surface=sheet_surf,
            frame_width=frame_width,
            frame_height=frame_height,
            is_placeholder=True,
        )

    # =========================================================================
    # Fonts
    # =========================================================================

    def _find_font_path(self, name: str) -> str | None:
        """Search font directories for a font file matching name."""
        candidates = [
            name,
            os.path.join(FONTS_DIR, name),
        ]

        _, ext = os.path.splitext(name)
        if not ext:
            for e in self.FONT_EXTENSIONS:
                candidates.append(os.path.join(FONTS_DIR, f"{name}{e}"))
                candidates.append(f"{name}{e}")

        for path in candidates:
            if os.path.isfile(path):
                return os.path.abspath(path)

        return None

    def get_font(
        self, size: int, name: str | None = None
    ) -> pygame.font.Font | FallbackFont:
        """Get a font at the requested size with caching.

        Falls back cleanly to Pygame default font or SysFont if missing.
        """
        key = (name, size)
        if key in self._fonts:
            return self._fonts[key]

        font_obj: pygame.font.Font | FallbackFont | None = None

        if name:
            path = self._find_font_path(name)
            if path:
                try:
                    font_obj = pygame.font.Font(path, size)
                except (pygame.error, OSError) as e:
                    logger.warning(f"Could not load font '{path}': {e}")
            else:
                self._missing_assets.add(f"font:{name}")
                self._placeholder_assets.add(f"font:{name}:{size}")

            if font_obj is None:
                # Try system font as second tier
                try:
                    font_obj = pygame.font.SysFont(name, size)
                except Exception:
                    pass

        if font_obj is None:
            if name:
                self._missing_assets.add(f"font:{name}")
                self._placeholder_assets.add(f"font:{name}:{size}")
            try:
                font_obj = pygame.font.Font(None, size)
            except Exception:
                try:
                    pygame.font.init()
                    font_obj = pygame.font.Font(None, size)
                except Exception:
                    font_obj = FallbackFont(size)

        self._fonts[key] = font_obj
        return font_obj

    def has_font(self, name: str) -> bool:
        """Return True if a font file exists on disk."""
        return self._find_font_path(name) is not None

    # =========================================================================
    # Sounds / SFX
    # =========================================================================

    def _find_sound_path(self, name: str) -> str | None:
        """Search sound directories for an audio file matching name."""
        candidates = [
            name,
            os.path.join(SOUNDS_DIR, name),
            os.path.join(SFX_DIR, name),
        ]

        _, ext = os.path.splitext(name)
        if not ext:
            for e in self.SOUND_EXTENSIONS:
                candidates.append(os.path.join(SOUNDS_DIR, f"{name}{e}"))
                candidates.append(os.path.join(SFX_DIR, f"{name}{e}"))
                candidates.append(f"{name}{e}")

        for path in candidates:
            if os.path.isfile(path):
                return os.path.abspath(path)

        return None

    def get_sound(self, name: str) -> pygame.mixer.Sound | FallbackSound:
        """Load a sound effect with caching.

        If missing, returns a non-crashing fallback sound object.
        """
        if name in self._sounds:
            return self._sounds[name]

        sound: pygame.mixer.Sound | FallbackSound | None = None
        path = self._find_sound_path(name)

        if path and pygame.mixer.get_init():
            try:
                sound = pygame.mixer.Sound(path)
            except (pygame.error, OSError) as e:
                logger.warning(f"Failed to load sound '{path}': {e}")

        if sound is None:
            self._missing_assets.add(f"sound:{name}")
            self._placeholder_assets.add(f"sound:{name}")
            sound = self.create_fallback_sound(name)

        self._sounds[name] = sound
        return sound

    def load_sound(self, name: str) -> pygame.mixer.Sound | FallbackSound | None:
        """Load sound with fallback, maintaining API backward compatibility."""
        return self.get_sound(name)

    def create_fallback_sound(
        self, name: str = "fallback"
    ) -> pygame.mixer.Sound | FallbackSound:
        """Create a silent or mock sound object so playback never crashes."""
        if pygame.mixer.get_init():
            try:
                # 512 bytes of silence (16-bit mono 22050Hz ~ 11ms)
                silent_buffer = bytes(512)
                return pygame.mixer.Sound(buffer=silent_buffer)
            except Exception:
                pass
        return FallbackSound(name)

    def has_sound(self, name: str) -> bool:
        """Return True if a sound file exists on disk."""
        return self._find_sound_path(name) is not None

    # =========================================================================
    # Music (BGM)
    # =========================================================================

    def get_music_path(self, name: str) -> str | None:
        """Resolve a logical music name or relative path to a valid audio file.

        Searches MUSIC_DIR, BGM_DIR, and BGM_TEMPLATE. Returns None if missing.
        """
        candidates = [
            name,
            BGM_TEMPLATE.format(name=name),
            os.path.join(MUSIC_DIR, name),
            os.path.join(BGM_DIR, name),
            os.path.join(SOUNDS_DIR, name),
        ]

        _, ext = os.path.splitext(name)
        if not ext:
            for e in self.MUSIC_EXTENSIONS:
                candidates.append(os.path.join(MUSIC_DIR, f"{name}{e}"))
                candidates.append(os.path.join(BGM_DIR, f"{name}{e}"))
                candidates.append(f"{name}{e}")

        for path in candidates:
            if os.path.isfile(path):
                return os.path.abspath(path)

        self._missing_assets.add(f"music:{name}")
        return None

    def has_music(self, name: str) -> bool:
        """Return True if a music file exists on disk."""
        return self.get_music_path(name) is not None

    def play_music(
        self, name: str, loops: int = -1, fade_ms: int = 1000
    ) -> bool:
        """Safely load and play background music.

        If missing or mixer is uninitialized, logs a warning and returns False
        without crashing the game.
        """
        if not pygame.mixer.get_init():
            return False

        path = self.get_music_path(name)
        if not path:
            logger.debug(f"Music '{name}' not found. Skipping playback safely.")
            return False

        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(loops, fade_ms=fade_ms)
            return True
        except (pygame.error, OSError) as e:
            logger.warning(f"Error playing music '{path}': {e}")
            return False

    def stop_music(self, fade_ms: int = 500) -> None:
        """Safely stop background music."""
        if pygame.mixer.get_init():
            try:
                pygame.mixer.music.fadeout(fade_ms)
            except pygame.error:
                pass

    # =========================================================================
    # Tracking, Caching & Auditing
    # =========================================================================

    def cache_surface(self, name: str, surface: pygame.Surface) -> None:
        """Manually cache a surface (e.g. procedurally generated textures)."""
        self._images[name] = surface

    def cache_sound(
        self, name: str, sound: pygame.mixer.Sound | FallbackSound
    ) -> None:
        """Manually cache a sound effect."""
        self._sounds[name] = sound

    def is_placeholder(self, key_or_name: str) -> bool:
        """Check if an asset is currently represented by a fallback placeholder."""
        return (
            key_or_name in self._placeholder_assets
            or f"image:{key_or_name}" in self._missing_assets
            or f"spritesheet:{key_or_name}" in self._missing_assets
            or f"sound:{key_or_name}" in self._missing_assets
            or f"music:{key_or_name}" in self._missing_assets
            or f"font:{key_or_name}" in self._missing_assets
        )

    def get_missing_assets(self) -> list[str]:
        """Return a sorted list of all assets that fell back to placeholders."""
        return sorted(self._missing_assets)

    def audit_assets(self) -> dict[str, Any]:
        """Scan configured asset directories and report current status."""
        report: dict[str, Any] = {
            "directories": {},
            "cached_images": len(self._images),
            "cached_spritesheets": len(self._spritesheets),
            "cached_sounds": len(self._sounds),
            "cached_fonts": len(self._fonts),
            "missing_assets_requested": sorted(self._missing_assets),
        }

        for cat, path in ASSET_DIRS.items():
            if os.path.exists(path):
                files = [
                    f
                    for f in os.listdir(path)
                    if os.path.isfile(os.path.join(path, f))
                ]
                report["directories"][cat] = {
                    "path": path,
                    "exists": True,
                    "file_count": len(files),
                    "files": files[:20],
                }
            else:
                report["directories"][cat] = {
                    "path": path,
                    "exists": False,
                    "file_count": 0,
                    "files": [],
                }

        return report

    def clear(self) -> None:
        """Clear all cached assets and audit tracking."""
        self._images.clear()
        self._spritesheets.clear()
        self._sounds.clear()
        self._fonts.clear()
        self._missing_assets.clear()
        self._placeholder_assets.clear()
