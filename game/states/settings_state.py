"""Settings state for adjusting game configuration."""
from __future__ import annotations

import pygame
import math

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS
from game.states.base_state import State
from game.core.input_handler import Action
from game.ui.text import render_text, render_text_outlined


class SettingsState(State):
    """A full-screen state for configuring game settings."""

    # Map text speed multiplier to string labels
    TEXT_SPEEDS = [(0.5, "Slow"), (1.0, "Normal"), (2.0, "Fast"), (100.0, "Instant")]

    def __init__(self, game):
        super().__init__(game)
        self._font_title = game.assets.get_font(48)
        self._font_item = game.assets.get_font(24)
        self._font_value = game.assets.get_font(24)
        self._font_hint = game.assets.get_font(16)
        
        self._cursor = 0
        self._anim_time = 0.0
        
        self.options = [
            {"key": "master_volume", "label": "Master Volume", "type": "volume"},
            {"key": "bgm_volume", "label": "Music Volume", "type": "volume"},
            {"key": "sfx_volume", "label": "SFX Volume", "type": "volume"},
            {"key": "fullscreen", "label": "Fullscreen", "type": "toggle"},
            {"key": "resolution_idx", "label": "Resolution", "type": "resolution"},
            {"key": "text_speed", "label": "Text Speed", "type": "text_speed"},
            {"key": "battle_animations", "label": "Battle Animations", "type": "toggle"}
        ]

        # Pre-build the header gradient once (avoids 100 draw.line() calls per frame)
        _header_h = 100
        self._header_surf = pygame.Surface((SCREEN_WIDTH, _header_h), pygame.SRCALPHA)
        for y in range(_header_h):
            alpha = int(255 * (1 - y / _header_h))
            pygame.draw.line(self._header_surf, (*COLORS["accent"], alpha),
                             (0, y), (SCREEN_WIDTH, y))

        
    def enter(self, params=None):
        self._cursor = 0
        self._anim_time = 0.0

    def exit(self):
        # Save settings to disk when leaving
        self.game.settings.save()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        action = self.game.input.bindings.get(event.key)
        if not action:
            return

        if action == Action.UP:
            self._cursor = (self._cursor - 1) % len(self.options)
            self.game.audio.play_sound("menu_move")
        elif action == Action.DOWN:
            self._cursor = (self._cursor + 1) % len(self.options)
            self.game.audio.play_sound("menu_move")
        elif action == Action.LEFT:
            self._adjust_option(-1)
        elif action == Action.RIGHT:
            self._adjust_option(1)
        elif action == Action.CONFIRM:
            # Toggle if it's a toggle
            opt = self.options[self._cursor]
            if opt["type"] == "toggle":
                self._adjust_option(1)
        elif action in (Action.CANCEL, Action.MENU):
            self.game.audio.play_sound("menu_cancel")
            self.game.settings.save()
            self.game.state_machine.pop()

    def _adjust_option(self, direction: int):
        opt = self.options[self._cursor]
        key = opt["key"]
        val = self.game.settings.get(key)
        
        changed = False
        
        if opt["type"] == "volume":
            new_val = max(0.0, min(1.0, val + direction * 0.1))
            if new_val != val:
                self.game.settings.update_volume(key, new_val)
                changed = True
                
        elif opt["type"] == "toggle":
            self.game.settings.set(key, not val)
            changed = True
            if key == "fullscreen":
                self.game.settings.apply_display()
                
        elif opt["type"] == "resolution":
            # Cycle resolution
            res_len = len(self.game.settings.RESOLUTIONS)
            new_idx = (val + direction) % res_len
            self.game.settings.set(key, new_idx)
            self.game.settings.apply_display()
            changed = True
            
        elif opt["type"] == "text_speed":
            # Find current index
            idx = 1 # Default normal
            for i, (mult, _) in enumerate(self.TEXT_SPEEDS):
                if math.isclose(mult, val):
                    idx = i
                    break
            new_idx = (idx + direction) % len(self.TEXT_SPEEDS)
            self.game.settings.set(key, self.TEXT_SPEEDS[new_idx][0])
            changed = True

        if changed:
            self.game.audio.play_sound("menu_select")

    def update(self, dt: float) -> None:
        self._anim_time += dt

    def render(self, surface: pygame.Surface) -> None:
        # Background
        surface.fill(COLORS["bg_dark"])
        
        # Draw gradient header (cached surface, no per-frame allocation)
        surface.blit(self._header_surf, (0, 0))
        

        
        # Title
        render_text_outlined(
            surface, "SETTINGS", self._font_title, 
            SCREEN_WIDTH // 2, 50,
            color=COLORS["white"], outline_color=(20, 10, 40), center=True
        )

        # Options
        start_y = 150
        spacing = 50
        
        for i, opt in enumerate(self.options):
            y = start_y + i * spacing
            selected = (i == self._cursor)
            
            # Label
            label_col = COLORS["white"] if selected else COLORS["text_dim"]
            render_text_outlined(
                surface, opt["label"], self._font_item,
                SCREEN_WIDTH // 2 - 50, y,
                color=label_col, outline_color=COLORS["black"], center=False
            )
            
            # Value renderer
            val = self.game.settings.get(opt["key"])
            val_text = ""
            
            if opt["type"] == "volume":
                val_text = f"{int(val * 100)}%"
                # Draw small volume bar
                bar_w = 100
                bar_h = 10
                bar_x = SCREEN_WIDTH // 2 + 180
                bar_y = y + 8
                pygame.draw.rect(surface, (50, 50, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=5)
                fill_w = int(bar_w * val)
                if fill_w > 0:
                    fill_color = COLORS["accent"] if selected else COLORS["text_dim"]
                    pygame.draw.rect(surface, fill_color, (bar_x, bar_y, fill_w, bar_h), border_radius=5)
                    
            elif opt["type"] == "toggle":
                val_text = "ON" if val else "OFF"
            elif opt["type"] == "resolution":
                res = self.game.settings.RESOLUTIONS[val]
                val_text = f"{res[0]}x{res[1]}"
            elif opt["type"] == "text_speed":
                for mult, label in self.TEXT_SPEEDS:
                    if math.isclose(mult, val):
                        val_text = label
                        break
                        
            # Selection arrows
            if selected:
                bob = int(math.sin(self._anim_time * 6) * 4)
                left_arrow = "< "
                right_arrow = " >"
                render_text_outlined(
                    surface, left_arrow, self._font_value,
                    SCREEN_WIDTH // 2 + 150 - bob, y,
                    color=COLORS["accent"], outline_color=COLORS["black"], center=True
                )
                render_text_outlined(
                    surface, right_arrow, self._font_value,
                    SCREEN_WIDTH // 2 + 300 + bar_w + bob if opt["type"] == "volume" else SCREEN_WIDTH // 2 + 250 + bob, y,
                    color=COLORS["accent"], outline_color=COLORS["black"], center=True
                )
                
            val_col = COLORS["accent"] if selected else COLORS["text_dim"]
            render_text_outlined(
                surface, val_text, self._font_value,
                SCREEN_WIDTH // 2 + 200, y,
                color=val_col, outline_color=COLORS["black"], center=False
            )
            
        # Hint at bottom
        hint = self._font_hint.render("Arrow Keys: Navigate & Adjust  |  Esc: Save & Back", True, COLORS["text_dim"])
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 40))
