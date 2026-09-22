"""Audio management — BGM and SFX playback with tone synthesis."""
from __future__ import annotations

import pygame
import numpy as np

from game.utils.helpers import clamp


class AudioManager:
    """Manages background music and sound effects.

    Provides on-the-fly tone synthesis via numpy so the game can run
    without any external audio files.
    """

    def __init__(self) -> None:
        self._bgm_volume: float = 0.5
        self._sfx_volume: float = 0.7
        self._current_bgm: str | None = None
        self._synth_cache: dict[str, pygame.mixer.Sound] = {}
        self._initialized: bool = pygame.mixer.get_init() is not None

    # ---- Volume ----

    @property
    def bgm_volume(self) -> float:
        return self._bgm_volume

    @bgm_volume.setter
    def bgm_volume(self, value: float) -> None:
        self._bgm_volume = clamp(value, 0.0, 1.0)
        if self._initialized:
            pygame.mixer.music.set_volume(self._bgm_volume)

    @property
    def sfx_volume(self) -> float:
        return self._sfx_volume

    @sfx_volume.setter
    def sfx_volume(self, value: float) -> None:
        self._sfx_volume = clamp(value, 0.0, 1.0)

    # ---- Synthesis ----

    def synthesize_tone(
        self,
        name: str,
        frequency: float = 440.0,
        duration: float = 0.15,
        wave: str = "square",
        volume: float = 0.3,
    ) -> pygame.mixer.Sound:
        """Generate and cache a simple synthesized tone.

        Args:
            name: Cache key for this tone.
            frequency: Frequency in Hz.
            duration: Duration in seconds.
            wave: Waveform type — ``"sine"``, ``"square"``, or ``"triangle"``.
            volume: Amplitude scale (0.0 – 1.0).
        """
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

        # Envelope — fade in/out to avoid audible clicks
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
        """Play a previously-synthesized sound effect by name.

        Extra keyword arguments are forwarded to ``synthesize_tone`` if the
        sound hasn't been cached yet.
        """
        if not self._initialized:
            return
        sound = self.synthesize_tone(name, **synth_kwargs)
        sound.set_volume(self._sfx_volume)
        sound.play()

    # ---- BGM ----

    def play_bgm(self, path: str, loops: int = -1, fade_ms: int = 1000) -> None:
        """Play background music from a file path."""
        if not self._initialized:
            return
        if self._current_bgm == path:
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self._bgm_volume)
            pygame.mixer.music.play(loops, fade_ms=fade_ms)
            self._current_bgm = path
        except pygame.error:
            self._current_bgm = None

    def stop_bgm(self, fade_ms: int = 500) -> None:
        """Stop background music with a fade-out."""
        if self._initialized:
            pygame.mixer.music.fadeout(fade_ms)
            self._current_bgm = None

    def pause_bgm(self) -> None:
        """Pause background music."""
        if self._initialized:
            pygame.mixer.music.pause()

    def resume_bgm(self) -> None:
        """Resume paused background music."""
        if self._initialized:
            pygame.mixer.music.unpause()
