"""EvolutionState — full-screen evolution animation and presentation."""
import math
import pygame
from typing import Any

from game.states.base_state import State
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS
from game.ui.text import render_text, TypewriterText


class EvolutionState(State):
    """Presents the evolution animation and stat reveal.

    Params (via enter()):
        creature        The Creature being evolved (already mutated).
        evo_result      EvolutionResult dataclass from progression.evolve().
        on_complete     Optional callable() invoked when animation finishes.
    """

    # Animation phases
    _PHASES = ("FLASH", "MORPH", "REVEAL", "STATS", "DONE")

    def __init__(self, game) -> None:
        super().__init__(game)
        self.font = game.assets.get_font(26)
        self.small = game.assets.get_font(18)

        self.creature = None
        self.evo_result = None
        self.on_complete = None

        self._phase = "FLASH"
        self._timer = 0.0
        self._flash_alpha = 0
        self._morph_progress = 0.0
        self._typewriter: TypewriterText | None = None
        self._stat_lines: list[str] = []

    def enter(self, params: dict[str, Any] | None = None) -> None:
        params = params or {}
        self.creature = params.get("creature")
        self.evo_result = params.get("evo_result")
        self.on_complete = params.get("on_complete")

        self._phase = "FLASH"
        self._timer = 0.0
        self._flash_alpha = 0
        self._morph_progress = 0.0

        if self.evo_result:
            msg = (f"What?! {self.evo_result.old_name} is evolving into "
                   f"{self.evo_result.new_name}!")
            self._typewriter = TypewriterText(msg, chars_per_second=35)

        # Build stat line summaries
        if self.evo_result:
            labels = {"hp": "HP", "atk": "Atk", "def_": "Def",
                      "sp_atk": "Sp.Atk", "sp_def": "Sp.Def", "spd": "Speed"}
            self._stat_lines = []
            for key, label in labels.items():
                delta = self.evo_result.stat_changes.get(key, 0)
                sign = "+" if delta >= 0 else ""
                self._stat_lines.append(f"{label}: {sign}{delta}")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE, pygame.K_e):
            if self._phase in ("REVEAL", "STATS"):
                if self._typewriter and not self._typewriter.is_complete:
                    self._typewriter.skip()
                else:
                    self._advance()

    def _advance(self) -> None:
        idx = self._PHASES.index(self._phase)
        if idx + 1 < len(self._PHASES):
            self._phase = self._PHASES[idx + 1]
            self._timer = 0.0
            if self._phase == "STATS":
                summary = f"{self.evo_result.new_name} learned new abilities!"
                self._typewriter = TypewriterText(summary, chars_per_second=35)
            if self._phase == "DONE":
                self._finish()

    def _finish(self) -> None:
        if self.on_complete:
            self.on_complete()
        self.game.state_machine.pop()

    def update(self, dt: float) -> None:
        self._timer += dt
        if self._typewriter:
            self._typewriter.update(dt)

        if self._phase == "FLASH":
            # Fast white flashes for 2 seconds
            self._flash_alpha = int(abs(math.sin(self._timer * 8)) * 255)
            if self._timer >= 2.0:
                self._morph_progress = 0.0
                self._phase = "MORPH"
                self._timer = 0.0

        elif self._phase == "MORPH":
            self._morph_progress = min(1.0, self._timer / 1.5)
            if self._morph_progress >= 1.0:
                self._phase = "REVEAL"
                self._timer = 0.0

        elif self._phase == "REVEAL":
            pass   # Wait for player input

        elif self._phase == "STATS":
            pass   # Wait for player input

    def render(self, surface: pygame.Surface) -> None:
        if self._phase == "FLASH":
            self._render_flash(surface)
        elif self._phase == "MORPH":
            self._render_morph(surface)
        elif self._phase in ("REVEAL", "STATS"):
            self._render_reveal(surface)

    def _render_flash(self, surface: pygame.Surface) -> None:
        surface.fill(COLORS["bg_dark"])

        # Silhouette of old creature (placeholder rectangle)
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60
        size = 120
        sil = pygame.Surface((size, size))
        sil.fill(COLORS["accent_warm"])
        surface.blit(sil, (cx - size // 2, cy - size // 2))

        # Flash overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((255, 255, 255))
        overlay.set_alpha(self._flash_alpha)
        surface.blit(overlay, (0, 0))

        if self.evo_result:
            render_text(surface, f"{self.evo_result.old_name} is evolving!",
                        self.font, SCREEN_WIDTH // 2, cy + 100,
                        color=COLORS["text"], center=True)

    def _render_morph(self, surface: pygame.Surface) -> None:
        surface.fill(COLORS["bg_dark"])

        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60
        p = self._morph_progress

        # Cross-fade between old (warm) and new (accent) placeholder shapes
        size = int(80 + math.sin(p * math.pi) * 60)
        alpha_old = int((1.0 - p) * 255)
        alpha_new = int(p * 255)

        old_surf = pygame.Surface((size, size))
        old_surf.fill(COLORS["accent_warm"])
        old_surf.set_alpha(alpha_old)
        surface.blit(old_surf, (cx - size // 2, cy - size // 2))

        new_surf = pygame.Surface((size, size))
        new_surf.fill(COLORS["accent"])
        new_surf.set_alpha(alpha_new)
        surface.blit(new_surf, (cx - size // 2, cy - size // 2))

        pct_text = f"{int(p * 100)}%"
        render_text(surface, pct_text, self.small, cx, cy + 100,
                    color=COLORS["text_dim"], center=True)

    def _render_reveal(self, surface: pygame.Surface) -> None:
        surface.fill(COLORS["bg_dark"])

        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100
        size = 140
        new_surf = pygame.Surface((size, size))
        new_surf.fill(COLORS["accent"])
        surface.blit(new_surf, (cx - size // 2, cy - size // 2))

        # Typewriter reveal text
        if self._typewriter:
            render_text(surface, self._typewriter.visible_text,
                        self.font, cx, cy + 100, color=COLORS["text"], center=True)

        if self._phase == "STATS":
            # Show stat gains in two columns
            sx, sy = cx - 160, cy + 140
            for i, line in enumerate(self._stat_lines):
                col = i % 2
                row = i // 2
                x = sx + col * 200
                y = sy + row * 28
                render_text(surface, line, self.small, x, y,
                            color=COLORS["accent_green"])

        if not self._typewriter or self._typewriter.is_complete:
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                render_text(surface, "▼ Press Z", self.small,
                            SCREEN_WIDTH - 140, SCREEN_HEIGHT - 40,
                            color=COLORS["accent"])
