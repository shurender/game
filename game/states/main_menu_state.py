"""Main menu state — title screen with animated background and particle effects."""
from __future__ import annotations

import math
import random

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS
from game.states.base_state import State
from game.core.input_handler import Action
from game.ui.menu import Menu
from game.ui.text import render_text_outlined


# ---------------------------------------------------------------------------
# Background particle
# ---------------------------------------------------------------------------

class _Particle:
    """A single floating background particle."""

    __slots__ = ("x", "y", "speed", "size", "alpha", "drift", "shimmer_offset")

    def __init__(self) -> None:
        self.x = 0.0
        self.y = 0.0
        self.speed = 0.0
        self.size = 0.0
        self.alpha = 0
        self.drift = 0.0
        self.shimmer_offset = 0.0
        self.reset()

    def reset(self, start_bottom: bool = False) -> None:
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = (
            random.uniform(0, SCREEN_HEIGHT) if not start_bottom
            else SCREEN_HEIGHT + 10
        )
        self.speed = random.uniform(15, 40)
        self.size = random.uniform(1.5, 4.0)
        self.alpha = random.randint(40, 120)
        self.drift = random.uniform(-8, 8)
        self.shimmer_offset = random.uniform(0, math.pi * 2)

    def update(self, dt: float, time: float) -> None:
        self.y -= self.speed * dt
        self.x += self.drift * dt
        self.alpha = int(60 + 40 * math.sin(time * 2 + self.shimmer_offset))
        if self.y < -10:
            self.reset(start_bottom=True)


# ---------------------------------------------------------------------------
# Main-menu state
# ---------------------------------------------------------------------------

class MainMenuState(State):
    """Title screen with animated background and main menu."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self._time: float = 0.0

        # Fonts
        self._title_font = game.assets.get_font(96)
        self._subtitle_font = game.assets.get_font(22)
        self._menu_font = game.assets.get_font(28)

        # Particles
        self._particles = [_Particle() for _ in range(50)]

        # Menu
        self._menu = Menu(
            items=["New Game", "Load Game", "Settings", "Quit"],
            font=self._menu_font,
            x=SCREEN_WIDTH // 2,
            y=SCREEN_HEIGHT // 2 + 60,
            spacing=45,
            on_select=self._on_menu_select,
        )

        # Pre-rendered surfaces
        self._bg_surface = self._create_bg_gradient()
        self._creature_silhouette = self._create_creature_silhouette()

    # ---- Pre-rendered assets -------------------------------------------

    @staticmethod
    def _create_bg_gradient() -> pygame.Surface:
        """Create a dark-to-deep-blue vertical gradient background."""
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            t = y / SCREEN_HEIGHT
            r = int(8 + 20 * t)
            g = int(5 + 12 * t)
            b = int(18 + 35 * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        return surface

    @staticmethod
    def _create_creature_silhouette() -> pygame.Surface:
        """Procedurally draw a creature silhouette for the title screen."""
        size = 180
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        body_color = (60, 45, 90, 80)

        # Body
        pygame.draw.ellipse(surface, body_color, (30, 70, 120, 80))
        # Head
        pygame.draw.circle(surface, body_color, (90, 60), 40)
        # Ears (pointed)
        pygame.draw.polygon(surface, body_color, [(65, 30), (75, 60), (55, 55)])
        pygame.draw.polygon(surface, body_color, [(115, 30), (105, 60), (125, 55)])
        # Tail
        pygame.draw.ellipse(surface, body_color, (0, 80, 60, 30))
        # Eyes (glowing)
        glow = (120, 200, 255, 160)
        pygame.draw.circle(surface, glow, (78, 55), 4)
        pygame.draw.circle(surface, glow, (102, 55), 4)

        return surface

    # ---- Menu callback --------------------------------------------------

    def _on_menu_select(self, index: int, item: str) -> None:
        if item == "Quit":
            self.game.quit()
        elif item == "New Game":
            from game.states.world_state import WorldState
            self.game.state_machine.push(WorldState(self.game))
            self.game.audio.play_sfx("menu_select")
        elif item == "Load Game":
            self.game.audio.play_sfx("menu_select")
        elif item == "Settings":
            self.game.audio.play_sfx("menu_select")

    # ---- State lifecycle ------------------------------------------------

    def enter(self, params=None) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        action = self.game.input.bindings.get(event.key)
        if action == Action.UP:
            self._menu.move_up()
            self.game.audio.play_sfx("menu_move")
        elif action == Action.DOWN:
            self._menu.move_down()
            self.game.audio.play_sfx("menu_move")
        elif action == Action.CONFIRM:
            self._menu.select()

    def update(self, dt: float) -> None:
        self._time += dt
        self._menu.update(dt)
        for p in self._particles:
            p.update(dt, self._time)

    def render(self, surface: pygame.Surface) -> None:
        # Background gradient
        surface.blit(self._bg_surface, (0, 0))

        # Floating particles
        for p in self._particles:
            color = (120, 180, 255, p.alpha)
            ps = pygame.Surface(
                (int(p.size * 2 + 1), int(p.size * 2 + 1)), pygame.SRCALPHA
            )
            pygame.draw.circle(ps, color, (int(p.size), int(p.size)), int(p.size))
            surface.blit(ps, (int(p.x - p.size), int(p.y - p.size)))

        # Creature silhouette with gentle breathing animation
        breath = math.sin(self._time * 1.5) * 4
        sil_x = SCREEN_WIDTH // 2 - 90
        sil_y = SCREEN_HEIGHT // 2 - 180 + breath
        surface.blit(self._creature_silhouette, (sil_x, sil_y))

        # Title glow
        title_y = SCREEN_HEIGHT // 2 - 80
        glow_alpha = int(100 + 30 * math.sin(self._time * 2))
        glow_surf = pygame.Surface((300, 80), pygame.SRCALPHA)
        pygame.draw.ellipse(
            glow_surf, (80, 150, 255, glow_alpha), glow_surf.get_rect()
        )
        surface.blit(glow_surf, (SCREEN_WIDTH // 2 - 150, title_y - 20))

        # Title text
        render_text_outlined(
            surface, "RISU", self._title_font,
            SCREEN_WIDTH // 2, title_y,
            color=(200, 230, 255),
            outline_color=(30, 20, 60),
            center=True,
        )

        # Subtitle with gentle pulsing
        sub_alpha = int(150 + 60 * math.sin(self._time * 1.2))
        render_text_outlined(
            surface, "A Creature Collecting Adventure", self._subtitle_font,
            SCREEN_WIDTH // 2, title_y + 55,
            color=(sub_alpha, sub_alpha, min(255, sub_alpha + 40)),
            outline_color=(15, 10, 30),
            center=True,
        )

        # Menu
        self._menu.draw(surface, center=True)

        # Version label
        ver_font = self.game.assets.get_font(14)
        ver_surf = ver_font.render("v0.1.0", True, COLORS["text_dim"])
        surface.blit(
            ver_surf,
            (SCREEN_WIDTH - ver_surf.get_width() - 10,
             SCREEN_HEIGHT - ver_surf.get_height() - 10),
        )
