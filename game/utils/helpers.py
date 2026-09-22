"""Utility functions and classes."""
from __future__ import annotations


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation from a to b by factor t."""
    return a + (b - a) * t


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a value to the range [minimum, maximum]."""
    return max(minimum, min(maximum, value))


def ease_in_out(t: float) -> float:
    """Smooth ease-in-out interpolation (cubic)."""
    if t < 0.5:
        return 4.0 * t * t * t
    else:
        p = 2.0 * t - 2.0
        return 0.5 * p * p * p + 1.0


class Timer:
    """A simple countdown timer."""

    def __init__(self, duration: float, callback=None, repeat: bool = False) -> None:
        self.duration = duration
        self.callback = callback
        self.repeat = repeat
        self._elapsed: float = 0.0
        self.finished: bool = False

    def update(self, dt: float) -> bool:
        """Update the timer. Returns True when it fires."""
        if self.finished and not self.repeat:
            return False
        self._elapsed += dt
        if self._elapsed >= self.duration:
            if self.repeat:
                self._elapsed -= self.duration
            else:
                self.finished = True
            if self.callback:
                self.callback()
            return True
        return False

    def reset(self) -> None:
        """Reset the timer."""
        self._elapsed = 0.0
        self.finished = False

    @property
    def progress(self) -> float:
        """Return progress from 0.0 to 1.0."""
        if self.duration <= 0:
            return 1.0
        return clamp(self._elapsed / self.duration, 0.0, 1.0)


class Cooldown:
    """A reusable cooldown that can be checked and reset."""

    def __init__(self, duration: float) -> None:
        self.duration = duration
        self._elapsed: float = duration  # Start ready

    def update(self, dt: float) -> None:
        """Advance the cooldown."""
        self._elapsed += dt

    @property
    def ready(self) -> bool:
        """Return True if the cooldown is ready."""
        return self._elapsed >= self.duration

    def reset(self) -> None:
        """Reset the cooldown."""
        self._elapsed = 0.0
