"""Main menu state — title screen with animated background, save-slot detection,
and a polished selection highlight.
"""
from __future__ import annotations

import math
import random
import os

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS
from game.states.base_state import State
from game.core.input_handler import Action
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
# Internal menu item
# ---------------------------------------------------------------------------

class _MenuItem:
    """A single menu entry with optional disabled state."""

    def __init__(self, label: str, action: str, disabled: bool = False, subtitle: str = "") -> None:
        self.label = label
        self.action = action
        self.disabled = disabled
        self.subtitle = subtitle  # e.g. save slot preview text


# ---------------------------------------------------------------------------
# Main-menu state
# ---------------------------------------------------------------------------

SAVE_DIR = "saves"
AUTOSAVE_SLOT = 0
MANUAL_SLOT = 1


def _read_save_info(slot: int) -> dict | None:
    """Read surface-level info from a save slot without loading it fully."""
    path = os.path.join(SAVE_DIR, f"save_{slot}.json")
    if not os.path.exists(path):
        return None
    try:
        import json
        with open(path) as f:
            data = json.load(f)
        pos = data.get("position", {})
        party = data.get("party", {}).get("party", [])
        return {
            "player_name": data.get("player_name", "Unknown"),
            "map_id": pos.get("map_id", "?"),
            "party_size": len(party),
        }
    except Exception:
        return None


class MainMenuState(State):
    """Title screen with animated background, particles, and save-aware menu."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self._time: float = 0.0
        self._selected: int = 0
        self._selector_anim: float = 0.0   # wobble timer for selection cursor
        self._transition_out: bool = False
        self._transition_alpha: int = 0

        # Fonts
        self._title_font = game.assets.get_font(96)
        self._subtitle_font = game.assets.get_font(22)
        self._menu_font = game.assets.get_font(30)
        self._hint_font = game.assets.get_font(16)

        # Particles
        self._particles = [_Particle() for _ in range(60)]

        # Pre-rendered surfaces
        self._bg_surface = self._create_bg_gradient()
        self._creature_silhouette = self._create_creature_silhouette()

        # Build menu items with save detection
        self._items = self._build_items()

        # Cached selection highlight surface (rebuilt per frame for glow pulse)
        self._menu_x = SCREEN_WIDTH // 2
        self._menu_start_y = SCREEN_HEIGHT // 2 + 70
        self._item_spacing = 52

        # Pre-build reusable surfaces — avoids per-frame allocations
        self._glow_surf = pygame.Surface((340, 90), pygame.SRCALPHA)
        self._pill_surf = pygame.Surface((300, 42), pygame.SRCALPHA)
        self._fade_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._fade_surf.fill((0, 0, 0))
        # Per-particle surfaces (fixed max size 20×20; reused each frame)
        _MAX_PARTICLE_R = 10  # max p.size
        self._particle_surf = pygame.Surface(
            (_MAX_PARTICLE_R * 2 + 1, _MAX_PARTICLE_R * 2 + 1), pygame.SRCALPHA
        )


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
        size = 200
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        body_color = (60, 45, 90, 80)

        pygame.draw.ellipse(surface, body_color, (30, 80, 140, 90))
        pygame.draw.circle(surface, body_color, (100, 65), 44)
        # Pointed ears
        pygame.draw.polygon(surface, body_color, [(72, 30), (82, 65), (60, 60)])
        pygame.draw.polygon(surface, body_color, [(128, 30), (118, 65), (140, 60)])
        # Tail
        pygame.draw.ellipse(surface, body_color, (0, 90, 65, 32))
        # Glowing eyes
        glow = (120, 200, 255, 180)
        pygame.draw.circle(surface, glow, (86, 60), 5)
        pygame.draw.circle(surface, glow, (114, 60), 5)

        return surface

    # ---- Menu construction ---------------------------------------------

    def _build_items(self) -> list[_MenuItem]:
        items: list[_MenuItem] = []

        # New Game
        items.append(_MenuItem("New Game", "new_game"))

        # Continue — enabled only if a valid save exists
        save_info = _read_save_info(MANUAL_SLOT) or _read_save_info(AUTOSAVE_SLOT)
        if save_info:
            subtitle = f"{save_info['player_name']}  ·  {save_info['map_id']}  ·  {save_info['party_size']} creatures"
            items.append(_MenuItem("Continue", "continue", disabled=False, subtitle=subtitle))
        else:
            items.append(_MenuItem("Continue", "continue", disabled=True, subtitle="No save found"))

        # Settings & Quit
        items.append(_MenuItem("Settings", "settings"))
        items.append(_MenuItem("Quit", "quit"))

        return items

    # ---- Input helpers -------------------------------------------------

    def _move_up(self) -> None:
        start = self._selected
        for _ in range(len(self._items)):
            self._selected = (self._selected - 1) % len(self._items)
            if not self._items[self._selected].disabled:
                break
        if self._items[self._selected].disabled:
            self._selected = start
        self.game.audio.play_sound("menu_move")

    def _move_down(self) -> None:
        start = self._selected
        for _ in range(len(self._items)):
            self._selected = (self._selected + 1) % len(self._items)
            if not self._items[self._selected].disabled:
                break
        if self._items[self._selected].disabled:
            self._selected = start
        self.game.audio.play_sound("menu_move")

    def _confirm(self) -> None:
        item = self._items[self._selected]
        if item.disabled:
            self.game.audio.play_sound("menu_cancel")
            return
        self.game.audio.play_sound("menu_select")
        self._execute_action(item.action)

    def _execute_action(self, action: str) -> None:
        if action == "quit":
            self.game.quit()
        elif action == "new_game":
            self._begin_transition(lambda: self._start_new_game())
        elif action == "continue":
            self._begin_transition(lambda: self._load_game())
        elif action == "settings":
            def _push_settings():
                from game.states.settings_state import SettingsState
                self.game.state_machine.push(SettingsState(self.game))
            self._begin_transition(_push_settings)

    def _begin_transition(self, callback) -> None:
        """Fade to black, then call callback."""
        self._transition_out = True
        self._transition_alpha = 0
        self._transition_callback = callback

    def _start_new_game(self) -> None:
        from game.states.world_state import WorldState
        new_state = WorldState(self.game)
        self.game.state_machine.replace(new_state)

    def _load_game(self) -> None:
        from game.core.save_manager import SaveManager
        sm = SaveManager(self.game)
        # Try manual save first, fall back to autosave
        if not sm.load(MANUAL_SLOT):
            sm.load(AUTOSAVE_SLOT)

    # ---- State lifecycle ------------------------------------------------

    def enter(self, params=None) -> None:
        self._items = self._build_items()  # refresh save detection
        self._transition_out = False
        self._transition_alpha = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._transition_out:
            return
        if event.type != pygame.KEYDOWN:
            return
        action = self.game.input.bindings.get(event.key)
        if action == Action.UP:
            self._move_up()
        elif action == Action.DOWN:
            self._move_down()
        elif action == Action.CONFIRM:
            self._confirm()
        elif action == Action.CANCEL:
            # If Continue is selected, fall back to New Game
            if self._items[self._selected].action != "new_game":
                self._selected = 0

    def update(self, dt: float) -> None:
        self._time += dt
        self._selector_anim += dt
        for p in self._particles:
            p.update(dt, self._time)

        if self._transition_out:
            self._transition_alpha = min(255, self._transition_alpha + int(600 * dt))
            if self._transition_alpha >= 255:
                self._transition_callback()

    def render(self, surface: pygame.Surface) -> None:
        # Background gradient
        surface.blit(self._bg_surface, (0, 0))

        # Floating particles — reuse a single scratch surface per particle
        _ps = self._particle_surf
        for p in self._particles:
            r = int(p.size)
            _ps.fill((0, 0, 0, 0))  # clear
            pygame.draw.circle(_ps, (120, 180, 255, p.alpha), (r, r), r)
            surface.blit(_ps, (int(p.x - r), int(p.y - r)))


        # Creature silhouette — gentle breathing
        breath = math.sin(self._time * 1.5) * 5
        sil_x = SCREEN_WIDTH // 2 - 100
        sil_y = SCREEN_HEIGHT // 2 - 200 + breath
        surface.blit(self._creature_silhouette, (sil_x, sil_y))

        # Title glow ring — reuse cached surface, update alpha
        title_y = SCREEN_HEIGHT // 2 - 80
        glow_alpha = int(80 + 40 * math.sin(self._time * 2))
        self._glow_surf.fill((0, 0, 0, 0))  # clear
        pygame.draw.ellipse(self._glow_surf, (80, 150, 255, glow_alpha), self._glow_surf.get_rect())
        surface.blit(self._glow_surf, (SCREEN_WIDTH // 2 - 170, title_y - 20))


        # Title
        render_text_outlined(
            surface, "RISU", self._title_font,
            SCREEN_WIDTH // 2, title_y,
            color=(200, 230, 255),
            outline_color=(20, 10, 50),
            center=True,
        )

        # Subtitle pulse
        sub_alpha = int(160 + 70 * math.sin(self._time * 1.2))
        render_text_outlined(
            surface, "A Creature Collecting Adventure", self._subtitle_font,
            SCREEN_WIDTH // 2, title_y + 60,
            color=(sub_alpha, sub_alpha, min(255, sub_alpha + 40)),
            outline_color=(10, 5, 25),
            center=True,
        )

        # Divider line
        dy = self._menu_start_y - 24
        pygame.draw.line(surface, (60, 90, 140), (SCREEN_WIDTH // 2 - 160, dy), (SCREEN_WIDTH // 2 + 160, dy), 1)

        # Menu items
        for i, item in enumerate(self._items):
            y = self._menu_start_y + i * self._item_spacing
            is_selected = (i == self._selected)

            if is_selected and not item.disabled:
                # Glowing selection pill — reuse cached surface
                pulse = 0.5 + 0.5 * math.sin(self._selector_anim * 4)
                pill_w, pill_h = 300, 42
                self._pill_surf.fill((0, 0, 0, 0))  # clear
                pill_alpha = int(60 + 30 * pulse)
                pygame.draw.rect(
                    self._pill_surf, (80, 140, 255, pill_alpha),
                    (0, 0, pill_w, pill_h), border_radius=21,
                )
                # Bright border
                border_alpha = int(160 + 60 * pulse)
                pygame.draw.rect(
                    self._pill_surf, (120, 180, 255, border_alpha),
                    (0, 0, pill_w, pill_h), width=2, border_radius=21,
                )
                surface.blit(self._pill_surf, (SCREEN_WIDTH // 2 - pill_w // 2, y - pill_h // 2 + 2))


                # Arrow cursor
                cursor_x = SCREEN_WIDTH // 2 - 160 + int(8 * math.sin(self._selector_anim * 6))
                render_text_outlined(surface, "▶", self._menu_font, cursor_x, y,
                                     color=(160, 220, 255), outline_color=(10, 20, 50), center=True)

            # Label
            if item.disabled:
                label_color = (60, 70, 90)
                outline = (10, 10, 20)
            elif is_selected:
                label_color = (220, 240, 255)
                outline = (10, 20, 60)
            else:
                label_color = (140, 170, 210)
                outline = (10, 15, 40)

            render_text_outlined(
                surface, item.label, self._menu_font,
                SCREEN_WIDTH // 2, y,
                color=label_color, outline_color=outline, center=True,
            )

            # Subtitle (e.g. save preview or "No save found")
            if item.subtitle:
                sub_col = (80, 100, 130) if item.disabled else (100, 140, 180)
                hint_surf = self._hint_font.render(item.subtitle, True, sub_col)
                surface.blit(hint_surf, (SCREEN_WIDTH // 2 - hint_surf.get_width() // 2, y + 18))

        # Navigation hint
        hint = self._hint_font.render("↑↓ Navigate   Enter/Z Confirm", True, (60, 80, 110))
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 36))

        # Version label
        ver_surf = self._hint_font.render("v0.1.0", True, COLORS["text_dim"])
        surface.blit(ver_surf, (SCREEN_WIDTH - ver_surf.get_width() - 10, SCREEN_HEIGHT - ver_surf.get_height() - 10))

        # Transition fade overlay — reuse cached surface
        if self._transition_out and self._transition_alpha > 0:
            self._fade_surf.set_alpha(self._transition_alpha)
            surface.blit(self._fade_surf, (0, 0))

