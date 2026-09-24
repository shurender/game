"""Reusable animation system — sprite animations, effects, and screen shake.

Completely decoupled from battle logic. States call into AnimationLayer and
poll ``is_done`` to know when to advance their own phase.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Callable

import pygame


# ---------------------------------------------------------------------------
# Frame-based sprite animation
# ---------------------------------------------------------------------------

class SpriteAnimation:
    """Plays a list of ``pygame.Surface`` frames at a fixed FPS.

    Args:
        frames:    Ordered list of surfaces.
        fps:       Frames per second of playback.
        loop:      If True, wraps back to frame 0 after the last frame.
        on_finish: Optional callback invoked once when the animation ends.
    """

    def __init__(
        self,
        frames: list[pygame.Surface],
        fps: float = 8.0,
        loop: bool = True,
        on_finish: Callable | None = None,
    ) -> None:
        self.frames = frames
        self.fps = fps
        self.loop = loop
        self.on_finish = on_finish

        self._frame_time: float = 1.0 / max(fps, 0.001)
        self._timer: float = 0.0
        self._index: int = 0
        self._finished: bool = False

    @property
    def current_frame(self) -> pygame.Surface:
        return self.frames[self._index]

    @property
    def is_done(self) -> bool:
        return self._finished

    def reset(self) -> None:
        self._timer = 0.0
        self._index = 0
        self._finished = False

    def update(self, dt: float) -> None:
        if self._finished:
            return
        self._timer += dt
        while self._timer >= self._frame_time:
            self._timer -= self._frame_time
            self._index += 1
            if self._index >= len(self.frames):
                if self.loop:
                    self._index = 0
                else:
                    self._index = len(self.frames) - 1
                    if not self._finished:
                        self._finished = True
                        if self.on_finish:
                            self.on_finish()
                    return


# ---------------------------------------------------------------------------
# Individual effect classes
# ---------------------------------------------------------------------------

class FadeEffect:
    """Overlay a solid-colour rectangle that fades in or out.

    Args:
        color:      RGB colour of the overlay (alpha handled separately).
        duration:   Seconds for the full fade.
        fade_in:    True = transparent → opaque, False = opaque → transparent.
        on_finish:  Optional callback.
    """

    def __init__(
        self,
        color: tuple[int, int, int] = (0, 0, 0),
        duration: float = 0.5,
        fade_in: bool = True,
        on_finish: Callable | None = None,
    ) -> None:
        self.color = color
        self.duration = max(duration, 0.001)
        self.fade_in = fade_in
        self.on_finish = on_finish
        self._elapsed: float = 0.0
        self._done: bool = False

    @property
    def is_done(self) -> bool:
        return self._done

    def update(self, dt: float) -> None:
        if self._done:
            return
        self._elapsed += dt
        if self._elapsed >= self.duration:
            self._elapsed = self.duration
            if not self._done:
                self._done = True
                if self.on_finish:
                    self.on_finish()

    def render(self, surface: pygame.Surface) -> None:
        t = min(self._elapsed / self.duration, 1.0)
        alpha = int(255 * (t if self.fade_in else (1.0 - t)))
        if alpha <= 0:
            return
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((*self.color, alpha))
        surface.blit(overlay, (0, 0))


class ScreenShake:
    """Offsets the render position to simulate camera shake.

    Call ``apply(surface)`` to get an offset tuple ``(dx, dy)`` to use
    when blitting the game world.
    """

    def __init__(self, duration: float = 0.4, magnitude: float = 8.0) -> None:
        self.duration = duration
        self.magnitude = magnitude
        self._elapsed: float = 0.0
        self._active: bool = False

    def trigger(self, duration: float | None = None, magnitude: float | None = None) -> None:
        self._elapsed = 0.0
        self._active = True
        if duration is not None:
            self.duration = duration
        if magnitude is not None:
            self.magnitude = magnitude

    @property
    def is_done(self) -> bool:
        return not self._active

    def update(self, dt: float) -> None:
        if not self._active:
            return
        self._elapsed += dt
        if self._elapsed >= self.duration:
            self._active = False

    def get_offset(self) -> tuple[int, int]:
        if not self._active:
            return (0, 0)
        t = self._elapsed / self.duration
        decay = 1.0 - t
        mag = self.magnitude * decay
        return (
            int(random.uniform(-mag, mag)),
            int(random.uniform(-mag, mag)),
        )


# ---------------------------------------------------------------------------
# Hit / flash effect
# ---------------------------------------------------------------------------

class HitFlash:
    """Flashes a surface white to indicate a hit."""

    def __init__(self, duration: float = 0.2, flashes: int = 3) -> None:
        self.duration = duration
        self.flashes = flashes
        self._elapsed: float = 0.0
        self._active: bool = False

    def trigger(self) -> None:
        self._elapsed = 0.0
        self._active = True

    @property
    def is_done(self) -> bool:
        return not self._active

    @property
    def visible(self) -> bool:
        if not self._active:
            return False
        t = self._elapsed / self.duration
        return (int(t * self.flashes * 2) % 2) == 0

    def update(self, dt: float) -> None:
        if not self._active:
            return
        self._elapsed += dt
        if self._elapsed >= self.duration:
            self._active = False

    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        """Return a copy of surface tinted white if flash is visible."""
        if not self.visible:
            return surface
        result = surface.copy()
        white = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        white.fill((255, 255, 255, 160))
        result.blit(white, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return result


# ---------------------------------------------------------------------------
# Floating damage number
# ---------------------------------------------------------------------------

@dataclass
class DamageNumber:
    """A floating number that rises and fades out."""

    x: float
    y: float
    value: int
    color: tuple[int, int, int] = (255, 80, 80)
    duration: float = 1.2
    _elapsed: float = field(default=0.0, init=False)

    @property
    def is_done(self) -> bool:
        return self._elapsed >= self.duration

    def update(self, dt: float) -> None:
        self._elapsed += dt
        self.y -= 40 * dt  # float upward

    def render(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        t = min(self._elapsed / self.duration, 1.0)
        alpha = int(255 * (1.0 - t))
        scale = 1.0 + 0.4 * max(0.0, 1.0 - t * 4)  # brief pop then shrink
        text = font.render(str(abs(self.value)), True, self.color)
        if scale != 1.0:
            w = max(1, int(text.get_width() * scale))
            h = max(1, int(text.get_height() * scale))
            text = pygame.transform.scale(text, (w, h))
        text.set_alpha(alpha)
        surface.blit(text, (int(self.x) - text.get_width() // 2, int(self.y)))


# ---------------------------------------------------------------------------
# Capture animation
# ---------------------------------------------------------------------------

class CaptureAnimation:
    """Procedural pokéball-style capture animation.

    Phases:
        0 → throw (ball grows and flies toward creature)
        1 → creature shrinks into ball
        2 → ball wobbles (N times)
        3 → success flash or burst
    """

    WOBBLE_ANGLES = [20, -18, 14, -10, 6]

    def __init__(
        self,
        start: tuple[int, int],
        target: tuple[int, int],
        shakes: int = 3,
        success: bool = True,
        on_finish: Callable | None = None,
    ) -> None:
        self.start = start
        self.target = target
        self.shakes = min(shakes, len(self.WOBBLE_ANGLES))
        self.success = success
        self.on_finish = on_finish

        self._phase: int = 0   # 0=throw, 1=shrink, 2=wobble, 3=end
        self._elapsed: float = 0.0
        self._wobble_idx: int = 0
        self._done: bool = False

        # Ball visual state
        self.ball_pos: list[float] = list(start)
        self.ball_radius: float = 8.0
        self.ball_angle: float = 0.0
        self.creature_scale: float = 1.0
        self.burst_alpha: int = 0

        # Phase durations
        self._THROW_DUR = 0.5
        self._SHRINK_DUR = 0.4
        self._WOBBLE_DUR = 0.35
        self._END_DUR = 0.6

    @property
    def is_done(self) -> bool:
        return self._done

    def update(self, dt: float) -> None:
        if self._done:
            return
        self._elapsed += dt

        # Process in a loop so large dt values don't get stuck in a phase
        for _ in range(100):  # guard against infinite loops
            if self._phase == 0:  # throw
                if self._elapsed >= self._THROW_DUR:
                    self._elapsed -= self._THROW_DUR
                    self._phase = 1
                else:
                    t = self._elapsed / self._THROW_DUR
                    ease = t * t * (3 - 2 * t)
                    self.ball_pos[0] = self.start[0] + (self.target[0] - self.start[0]) * ease
                    self.ball_pos[1] = (self.start[1] + (self.target[1] - self.start[1]) * ease
                                       - math.sin(t * math.pi) * 80)
                    break

            elif self._phase == 1:  # shrink
                if self._elapsed >= self._SHRINK_DUR:
                    self._elapsed -= self._SHRINK_DUR
                    self.creature_scale = 0.0
                    self._phase = 2
                    self._wobble_idx = 0
                else:
                    t = self._elapsed / self._SHRINK_DUR
                    self.creature_scale = 1.0 - t
                    break

            elif self._phase == 2:  # wobble
                if self._elapsed >= self._WOBBLE_DUR:
                    self._elapsed -= self._WOBBLE_DUR
                    self.ball_angle = 0.0
                    self._wobble_idx += 1
                    if self._wobble_idx >= self.shakes:
                        self._phase = 3
                else:
                    t = self._elapsed / self._WOBBLE_DUR
                    if self._wobble_idx < self.shakes:
                        angle = self.WOBBLE_ANGLES[self._wobble_idx]
                        self.ball_angle = angle * math.sin(t * math.pi)
                    break

            elif self._phase == 3:  # end
                if self._elapsed >= self._END_DUR:
                    self._done = True
                    if self.on_finish:
                        self.on_finish()
                    break
                else:
                    t = self._elapsed / self._END_DUR
                    if self.success:
                        self.burst_alpha = int(255 * math.sin(t * math.pi))
                    break

    def render(self, surface: pygame.Surface) -> None:
        # Draw scaled creature (phases 0-1)
        if self.creature_scale > 0:
            pass  # caller is responsible for drawing the creature sprite scaled

        # Draw ball
        bx, by = int(self.ball_pos[0]), int(self.ball_pos[1])
        col_top = (220, 60, 60)
        col_bot = (240, 240, 240)
        hinge = (30, 30, 30)

        ball_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        cx, cy = 20, 20
        r = 16
        pygame.draw.circle(ball_surf, col_top, (cx, cy - 1), r)
        pygame.draw.circle(ball_surf, col_bot, (cx, cy + 1), r)
        pygame.draw.line(ball_surf, hinge, (cx - r, cy), (cx + r, cy), 3)
        pygame.draw.circle(ball_surf, hinge, (cx, cy), 5)
        pygame.draw.circle(ball_surf, (200, 200, 200), (cx, cy), 3)

        if self.ball_angle:
            ball_surf = pygame.transform.rotate(ball_surf, self.ball_angle)

        surface.blit(ball_surf, (bx - ball_surf.get_width() // 2, by - ball_surf.get_height() // 2))

        # Success burst
        if self._phase == 3 and self.success and self.burst_alpha > 0:
            burst = pygame.Surface((120, 120), pygame.SRCALPHA)
            for i in range(8):
                angle = i * (math.pi / 4)
                ex = 60 + int(math.cos(angle) * 50)
                ey = 60 + int(math.sin(angle) * 50)
                pygame.draw.line(burst, (255, 230, 80, self.burst_alpha), (60, 60), (ex, ey), 3)
            surface.blit(burst, (bx - 60, by - 60))


# ---------------------------------------------------------------------------
# Level-up effect
# ---------------------------------------------------------------------------

class LevelUpEffect:
    """Radiating rings and star particles for level-up celebrations."""

    def __init__(self, x: int, y: int, duration: float = 1.5, on_finish: Callable | None = None) -> None:
        self.x = x
        self.y = y
        self.duration = duration
        self.on_finish = on_finish
        self._elapsed: float = 0.0
        self._done: bool = False
        self._stars: list[dict] = [
            {
                "angle": i * (math.pi * 2 / 8),
                "dist": 0.0,
                "speed": random.uniform(60, 120),
                "size": random.uniform(3, 6),
            }
            for i in range(8)
        ]

    @property
    def is_done(self) -> bool:
        return self._done

    def update(self, dt: float) -> None:
        if self._done:
            return
        self._elapsed += dt
        for s in self._stars:
            s["dist"] += s["speed"] * dt
        if self._elapsed >= self.duration:
            self._done = True
            if self.on_finish:
                self.on_finish()

    def render(self, surface: pygame.Surface) -> None:
        t = min(self._elapsed / self.duration, 1.0)
        alpha = int(255 * (1.0 - t))

        # Expanding rings
        for i in range(3):
            r = int((t + i * 0.25) * 80) % 80
            ring = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            ring_alpha = max(0, int(alpha * (1 - i * 0.3)))
            pygame.draw.circle(ring, (120, 240, 120, ring_alpha), (r + 2, r + 2), r, 3)
            surface.blit(ring, (self.x - r - 2, self.y - r - 2))

        # Stars
        for s in self._stars:
            sx = int(self.x + math.cos(s["angle"]) * s["dist"])
            sy = int(self.y + math.sin(s["angle"]) * s["dist"])
            sz = int(s["size"])
            star_surf = pygame.Surface((sz * 2 + 2, sz * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(star_surf, (255, 255, 100, alpha), (sz + 1, sz + 1), sz)
            surface.blit(star_surf, (sx - sz - 1, sy - sz - 1))


# ---------------------------------------------------------------------------
# Creature entrance / faint animations
# ---------------------------------------------------------------------------

class CreatureEntranceAnim:
    """Slides a creature sprite in from one side."""

    def __init__(
        self,
        start_x: float,
        end_x: float,
        y: float,
        duration: float = 0.4,
        on_finish: Callable | None = None,
    ) -> None:
        self.start_x = start_x
        self.end_x = end_x
        self.y = y
        self.duration = duration
        self.on_finish = on_finish
        self._elapsed: float = 0.0
        self._done: bool = False
        self.current_x: float = start_x

    @property
    def is_done(self) -> bool:
        return self._done

    def update(self, dt: float) -> None:
        if self._done:
            return
        self._elapsed += dt
        t = min(self._elapsed / self.duration, 1.0)
        ease = 1.0 - (1.0 - t) ** 3  # ease-out cubic
        self.current_x = self.start_x + (self.end_x - self.start_x) * ease
        if self._elapsed >= self.duration:
            self.current_x = self.end_x
            self._done = True
            if self.on_finish:
                self.on_finish()


class CreatureFaintAnim:
    """Drops the creature sprite downward and fades it out."""

    def __init__(
        self,
        x: float,
        y: float,
        duration: float = 0.6,
        on_finish: Callable | None = None,
    ) -> None:
        self.x = x
        self.base_y = y
        self.duration = duration
        self.on_finish = on_finish
        self._elapsed: float = 0.0
        self._done: bool = False
        self.current_y: float = y
        self.alpha: int = 255

    @property
    def is_done(self) -> bool:
        return self._done

    def update(self, dt: float) -> None:
        if self._done:
            return
        self._elapsed += dt
        t = min(self._elapsed / self.duration, 1.0)
        self.current_y = self.base_y + t * 40
        self.alpha = int(255 * (1.0 - t))
        if self._elapsed >= self.duration:
            self._done = True
            if self.on_finish:
                self.on_finish()


# ---------------------------------------------------------------------------
# Animation Layer — single object states attach to manage all active effects
# ---------------------------------------------------------------------------

class AnimationLayer:
    """Manages all concurrent active animations for a state.

    Usage::

        # In __init__
        self.anim = AnimationLayer(font)

        # Trigger effects
        self.anim.shake.trigger()
        self.anim.spawn_damage_number(x, y, 42)

        # In update
        self.anim.update(dt)

        # In render (call after drawing the base scene)
        self.anim.render(surface)
    """

    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font
        self.shake = ScreenShake()
        self.fade: FadeEffect | None = None
        self._damage_numbers: list[DamageNumber] = []
        self._capture: CaptureAnimation | None = None
        self._level_up: LevelUpEffect | None = None

    # -- Factory helpers

    def fade_in(self, color=(0, 0, 0), duration=0.4, on_finish: Callable | None = None) -> FadeEffect:
        self.fade = FadeEffect(color, duration, fade_in=True, on_finish=on_finish)
        return self.fade

    def fade_out(self, color=(0, 0, 0), duration=0.4, on_finish: Callable | None = None) -> FadeEffect:
        self.fade = FadeEffect(color, duration, fade_in=False, on_finish=on_finish)
        return self.fade

    def spawn_damage_number(self, x: float, y: float, value: int, color=(255, 80, 80)) -> DamageNumber:
        dn = DamageNumber(x, y, value, color)
        self._damage_numbers.append(dn)
        return dn

    def start_capture(self, start, target, shakes=3, success=True, on_finish=None) -> CaptureAnimation:
        self._capture = CaptureAnimation(start, target, shakes, success, on_finish)
        return self._capture

    def start_level_up(self, x: int, y: int, on_finish=None) -> LevelUpEffect:
        self._level_up = LevelUpEffect(x, y, on_finish=on_finish)
        return self._level_up

    # -- Lifecycle

    def update(self, dt: float) -> None:
        self.shake.update(dt)
        if self.fade:
            self.fade.update(dt)
        for d in self._damage_numbers:
            d.update(dt)
        self._damage_numbers = [d for d in self._damage_numbers if not d.is_done]
        if self._capture:
            self._capture.update(dt)
        if self._level_up:
            self._level_up.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        if self._capture:
            self._capture.render(surface)
        if self._level_up:
            self._level_up.render(surface)
        for d in self._damage_numbers:
            d.render(surface, self.font)
        if self.fade:
            self.fade.render(surface)

    @property
    def capture_done(self) -> bool:
        return self._capture is None or self._capture.is_done

    @property
    def level_up_done(self) -> bool:
        return self._level_up is None or self._level_up.is_done
