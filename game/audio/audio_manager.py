"""Audio management — SFX playback and master volume control."""
from __future__ import annotations

import pygame
import numpy as np

from game.utils.helpers import clamp
from game.audio.music_manager import MusicManager

class AudioManager:
    """Manages sound effects and delegates BGM to MusicManager.

    Provides on-the-fly tone synthesis via numpy so the game can run
    without any external audio files.
    """

    def __init__(self) -> None:
        self.music = MusicManager()
        
        self._master_volume: float = 1.0
        self._sfx_volume: float = 0.7
        self._sfx_muted: bool = False
        
        self._synth_cache: dict[str, pygame.mixer.Sound] = {}
        self._initialized: bool = pygame.mixer.get_init() is not None

    # ---- Volume Controls ----

    @property
    def master_volume(self) -> float:
        return self._master_volume

    @master_volume.setter
    def master_volume(self, value: float) -> None:
        self._master_volume = clamp(value, 0.0, 1.0)
        self.music.master_volume = self._master_volume

    @property
    def sfx_volume(self) -> float:
        return self._sfx_volume

    @sfx_volume.setter
    def sfx_volume(self, value: float) -> None:
        self._sfx_volume = clamp(value, 0.0, 1.0)

    @property
    def sfx_muted(self) -> bool:
        return self._sfx_muted
        
    @sfx_muted.setter
    def sfx_muted(self, value: bool) -> None:
        self._sfx_muted = value

    # ---- BGM Pass-through (for backward compatibility) ----
    
    @property
    def bgm_volume(self) -> float:
        return self.music.volume
        
    @bgm_volume.setter
    def bgm_volume(self, value: float) -> None:
        self.music.volume = value

    def play_bgm(self, path: str, loops: int = -1, fade_ms: int = 1000) -> None:
        self.music.play_music(path, loops, fade_ms)
        
    def stop_bgm(self, fade_ms: int = 500) -> None:
        self.music.stop_music(fade_ms)

    # ---- Synthesis ----

    def synthesize_tone(
        self,
        name: str,
        frequency: float = 440.0,
        duration: float = 0.15,
        wave: str = "square",
        volume: float = 0.3,
    ) -> pygame.mixer.Sound:
        if name in self._synth_cache:
            return self._synth_cache[name]

        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        if wave == "sine":
            samples = np.sin(2 * np.pi * frequency * t)
        elif wave == "square":
            samples = np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave == "triangle":
            samples = 2 * np.abs(
                2 * (t * frequency - np.floor(t * frequency + 0.5))
            ) - 1
        else:
            samples = np.sin(2 * np.pi * frequency * t)

        # Envelope
        attack = min(n_samples // 10, 200)
        release = min(n_samples // 5, 500)
        envelope = np.ones(n_samples)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)

        samples = (samples * envelope * volume * 32767).astype(np.int16)
        sound = pygame.mixer.Sound(buffer=samples.tobytes())
        self._synth_cache[name] = sound
        return sound

    def play_sfx(self, name: str, **synth_kwargs) -> None:
        """Play a previously-synthesized sound effect by name."""
        if not self._initialized or self._sfx_muted:
            return
            
        sound = self.synthesize_tone(name, **synth_kwargs)
        sound.set_volume(self._sfx_volume * self._master_volume)
        sound.play()

    def play_sound(self, name: str, **synth_kwargs) -> None:
        """Alias for play_sfx."""
        self.play_sfx(name, **synth_kwargs)

    # ---- Hooks ----

    def play_menu_sound(self) -> None:
        """Hook for menu navigation sounds."""
        self.play_sfx("menu_select", frequency=660, duration=0.1, wave="sine")
        
    def play_attack_sound(self) -> None:
        """Hook for physical attacks."""
        self.play_sfx("attack_hit", frequency=150, duration=0.2, wave="square", volume=0.5)
        
    def play_capture_sound(self) -> None:
        """Hook for capture throw/wobble."""
        self.play_sfx("capture_wobble", frequency=300, duration=0.3, wave="triangle")
        
    def play_capture_success_sound(self) -> None:
        """Hook for capture success."""
        self.play_sfx("capture_success", frequency=880, duration=0.5, wave="sine")
        
    def play_level_up_sound(self) -> None:
        """Hook for level up."""
        self.play_sfx("level_up", frequency=1000, duration=0.8, wave="sine")
