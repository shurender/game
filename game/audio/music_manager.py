"""Music management — BGM playback and transitions."""
from __future__ import annotations

import pygame
import os

from game.utils.helpers import clamp
from config import BGM_TEMPLATE, MUSIC_DIR


class MusicManager:
    """Manages background music and transitions."""

    def __init__(self) -> None:
        self._volume: float = 0.5
        self._muted: bool = False
        self._current_bgm: str | None = None
        self._initialized: bool = pygame.mixer.get_init() is not None
        self._master_volume: float = 1.0

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        self._volume = clamp(value, 0.0, 1.0)
        self._update_mixer_volume()

    @property
    def master_volume(self) -> float:
        return self._master_volume
        
    @master_volume.setter
    def master_volume(self, value: float) -> None:
        self._master_volume = clamp(value, 0.0, 1.0)
        self._update_mixer_volume()

    @property
    def muted(self) -> bool:
        return self._muted

    @muted.setter
    def muted(self, value: bool) -> None:
        self._muted = value
        self._update_mixer_volume()

    def _update_mixer_volume(self) -> None:
        if self._initialized:
            if self._muted:
                pygame.mixer.music.set_volume(0.0)
            else:
                pygame.mixer.music.set_volume(self._volume * self._master_volume)

    def play_music(self, name: str, loops: int = -1, fade_ms: int = 1000) -> None:
        """Play background music by logical name or path."""
        if not self._initialized:
            return
        if self._current_bgm == name:
            return
            
        # Try to resolve path from centralized template or music directory
        path = BGM_TEMPLATE.format(name=name)
        if not os.path.exists(path):
            alt_path = os.path.join(MUSIC_DIR, f"{name}.ogg")
            if os.path.exists(alt_path):
                path = alt_path
            elif os.path.exists(name):
                path = name

        try:
            if os.path.exists(path):
                pygame.mixer.music.load(path)
                self._update_mixer_volume()
                pygame.mixer.music.play(loops, fade_ms=fade_ms)
                self._current_bgm = name
            else:
                # If no asset, stop playing
                self.stop_music(fade_ms)
                self._current_bgm = None
        except pygame.error:
            self._current_bgm = None

    def stop_music(self, fade_ms: int = 500) -> None:
        """Stop background music with a fade-out."""
        if self._initialized:
            pygame.mixer.music.fadeout(fade_ms)
            self._current_bgm = None

    # ---- Hooks ----

    def play_world_music(self, map_id: str) -> None:
        """Hook to play world music based on the current map."""
        # E.g. map_id "starting_town" -> "town_theme"
        if "town" in map_id:
            self.play_music("town_theme", fade_ms=2000)
        elif "route" in map_id:
            self.play_music("route_theme", fade_ms=2000)
        else:
            self.play_music("wild_theme", fade_ms=2000)

    def play_battle_music(self, is_trainer: bool = False, is_boss: bool = False) -> None:
        """Hook to play battle music."""
        if is_boss:
            self.play_music("boss_battle", fade_ms=500)
        elif is_trainer:
            self.play_music("trainer_battle", fade_ms=500)
        else:
            self.play_music("wild_battle", fade_ms=500)
            
    def play_victory_music(self, is_trainer: bool = False) -> None:
        """Hook to play victory music."""
        if is_trainer:
            self.play_music("trainer_victory", loops=0, fade_ms=0)
        else:
            self.play_music("wild_victory", loops=0, fade_ms=0)
