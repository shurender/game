"""In-game pause / main menu overlay.

Pushed on top of WorldState via Action.MENU (Tab key).
WorldState.update() is never called while this state is active because
the StateMachine only ticks the topmost state.

Layout
------
A frosted dark panel slides in from the right side of the screen.
The world scene is visible (dimmed) behind it.
"""
from __future__ import annotations

import math
from typing import Callable

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS
from game.states.base_state import State
from game.core.input_handler import Action
from game.ui.text import render_text, render_text_outlined


# ---------------------------------------------------------------------------
# Menu entry descriptor
# ---------------------------------------------------------------------------

class _Entry:
    """One item in the pause menu."""
    __slots__ = ("label", "icon", "action", "disabled")

    def __init__(self, label: str, icon: str, action: str, disabled: bool = False) -> None:
        self.label = label
        self.icon = icon
        self.action = action
        self.disabled = disabled


# ---------------------------------------------------------------------------
# PauseMenuState
# ---------------------------------------------------------------------------

class PauseMenuState(State):
    """Full in-game pause / menu overlay.

    Pushed on top of WorldState — the world is still rendered (dimmed)
    beneath this state but receives NO update() calls.
    """

    # Panel geometry
    _PANEL_W = 300
    _PANEL_MARGIN_RIGHT = 0       # flush to right edge
    _PANEL_SLIDE_DURATION = 0.18  # seconds for slide-in animation

    _ENTRIES: list[_Entry] = [
        _Entry("Party",          "👥", "party"),
        _Entry("Bag",            "🎒", "bag"),
        _Entry("Pokédex",        "📖", "pokedex"),
        _Entry("Quest Log",      "📜", "quest_log"),
        _Entry("Save",           "💾", "save"),
        _Entry("Settings",       "⚙",  "settings"),
        _Entry("Return to Game", "▶",  "resume"),
        _Entry("Main Menu",      "🏠", "main_menu"),
    ]

    def __init__(self, game) -> None:
        super().__init__(game)

        # Fonts
        self._title_font  = game.assets.get_font(28)
        self._item_font   = game.assets.get_font(24)
        self._hint_font   = game.assets.get_font(15)
        self._icon_font   = game.assets.get_font(20)

        # Cursor & animation
        self._cursor = 0
        self._slide_t: float = 0.0        # 0 → closed, 1 → fully open
        self._closing: bool = False
        self._close_callback: Callable | None = None
        self._anim_time: float = 0.0      # general timer for glow / pulse

        # In-line sub-pages
        self._page: str = "menu"          # "menu" | "save_result"
        self._save_msg: str = ""
        self._save_msg_timer: float = 0.0

        # Panel open-width target (resolved after enter())
        self._panel_x_target = SCREEN_WIDTH - self._PANEL_W
        self._panel_x_current = float(SCREEN_WIDTH)   # starts offscreen right

        # Build dim overlay surface once
        self._dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._dim.fill((0, 0, 0, 140))

        # Build static panel gradient surface once — avoids 600 draw.line() calls per frame
        self._panel_surf = pygame.Surface((self._PANEL_W, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(SCREEN_HEIGHT):
            t_y = y / SCREEN_HEIGHT
            r = int(12 + 8 * t_y)
            g = int(14 + 6 * t_y)
            b = int(28 + 14 * t_y)
            pygame.draw.line(self._panel_surf, (r, g, b, 220), (0, y), (self._PANEL_W, y))


    # ------------------------------------------------------------------ #
    #  Lifecycle                                                           #
    # ------------------------------------------------------------------ #

    def enter(self, params=None) -> None:
        self._cursor = 0
        self._page = "menu"
        self._slide_t = 0.0
        self._closing = False
        self._close_callback = None
        self._panel_x_current = float(SCREEN_WIDTH)
        self._anim_time = 0.0
        self.game.audio.play_sound("menu_select")

    def exit(self) -> None:
        pass

    # ------------------------------------------------------------------ #
    #  Input                                                               #
    # ------------------------------------------------------------------ #

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN or self._closing:
            return

        action = self.game.input.bindings.get(event.key)
        if action is None:
            return

        if self._page == "save_result":
            # Any confirm/cancel dismisses the result banner
            if action in (Action.CONFIRM, Action.CANCEL, Action.MENU):
                self._page = "menu"
                self.game.audio.play_sound("menu_cancel")
            return

        # Main menu page
        if action == Action.UP:
            self._cursor = (self._cursor - 1) % len(self._ENTRIES)
            self.game.audio.play_sound("menu_move")
        elif action == Action.DOWN:
            self._cursor = (self._cursor + 1) % len(self._ENTRIES)
            self.game.audio.play_sound("menu_move")
        elif action == Action.CONFIRM:
            self._activate(self._ENTRIES[self._cursor])
        elif action in (Action.CANCEL, Action.MENU):
            # Close without action → resume game
            self._begin_close(lambda: self.game.state_machine.pop())

    def _activate(self, entry: _Entry) -> None:
        if entry.disabled:
            self.game.audio.play_sound("menu_cancel")
            return
        self.game.audio.play_sound("menu_select")

        act = entry.action
        if act == "resume":
            self._begin_close(lambda: self.game.state_machine.pop())

        elif act == "party":
            def _push_party():
                self.game.state_machine.pop()   # pop pause
                from game.states.party_state import PartyState
                ps = PartyState(self.game)
                ps.enter({})
                self.game.state_machine.push(ps)
            self._begin_close(_push_party)

        elif act == "bag":
            def _push_bag():
                self.game.state_machine.pop()
                from game.states.inventory_state import InventoryState
                inv = InventoryState(self.game)
                inv.enter({})
                self.game.state_machine.push(inv)
            self._begin_close(_push_bag)

        elif act == "quest_log":
            def _push_quest():
                self.game.state_machine.pop()
                from game.states.quest_log_state import QuestLogState
                self.game.state_machine.push(QuestLogState(self.game))
            self._begin_close(_push_quest)

        elif act == "settings":
            def _push_settings():
                self.game.state_machine.pop()
                from game.states.settings_state import SettingsState
                self.game.state_machine.push(SettingsState(self.game))
            self._begin_close(_push_settings)

        elif act == "save":
            from game.core.save_manager import SaveManager
            ok = SaveManager(self.game).save(slot=1)
            self._save_msg = "Game saved!" if ok else "Save failed."
            self._save_msg_timer = 2.0
            self._page = "save_result"

        elif act == "main_menu":
            def _go_main():
                self.game.state_machine.pop()   # pop pause
                self.game.state_machine.pop()   # pop world
                # MainMenuState is now exposed
                from game.states.main_menu_state import MainMenuState
                self.game.state_machine.push(MainMenuState(self.game))
            self._begin_close(_go_main)

        elif act == "pokedex":
            self._save_msg = "Pokédex is not yet available!"
            self._save_msg_timer = 2.0
            self._page = "save_result"

    # ------------------------------------------------------------------ #
    #  Slide animation helpers                                             #
    # ------------------------------------------------------------------ #

    def _begin_close(self, callback: Callable) -> None:
        self._closing = True
        self._close_callback = callback

    # ------------------------------------------------------------------ #
    #  Update                                                              #
    # ------------------------------------------------------------------ #

    def update(self, dt: float) -> None:
        self._anim_time += dt

        # Save result banner auto-dismiss
        if self._page == "save_result":
            self._save_msg_timer -= dt
            if self._save_msg_timer <= 0:
                self._page = "menu"

        # Slide panel in / out
        if not self._closing:
            self._slide_t = min(1.0, self._slide_t + dt / self._PANEL_SLIDE_DURATION)
        else:
            self._slide_t = max(0.0, self._slide_t - dt / self._PANEL_SLIDE_DURATION)
            if self._slide_t <= 0.0 and self._close_callback:
                cb = self._close_callback
                self._close_callback = None
                cb()
                return

        # Ease-out cubic
        t = 1.0 - (1.0 - self._slide_t) ** 3
        self._panel_x_current = SCREEN_WIDTH - self._PANEL_W * t

    # ------------------------------------------------------------------ #
    #  Render                                                              #
    # ------------------------------------------------------------------ #

    def render(self, surface: pygame.Surface) -> None:
        # Dim overlay (world is already drawn by StateMachine.render loop)
        alpha = int(140 * self._slide_t)
        if alpha > 0:
            overlay = self._dim.copy()
            overlay.set_alpha(alpha)
            surface.blit(overlay, (0, 0))

        panel_x = int(self._panel_x_current)
        panel_rect = pygame.Rect(panel_x, 0, self._PANEL_W, SCREEN_HEIGHT)

        # Panel background — blit cached gradient, then draw animated glow on top
        surface.blit(self._panel_surf, panel_rect.topleft)
        glow_alpha = int(160 + 60 * math.sin(self._anim_time * 2))
        pygame.draw.line(surface, (60, 120, 220, glow_alpha),
                         (panel_x, 0), (panel_x, SCREEN_HEIGHT), 3)


        # ---- title bar -----------------------------------------------
        title_y = 24
        render_text_outlined(
            surface, "MENU",
            self._title_font,
            panel_x + self._PANEL_W // 2, title_y,
            color=(200, 220, 255),
            outline_color=(10, 15, 40),
            center=True,
        )
        pygame.draw.line(surface, (50, 80, 160),
                         (panel_x + 20, title_y + 22),
                         (panel_x + self._PANEL_W - 20, title_y + 22), 1)

        # ---- page dispatch -------------------------------------------
        if self._page == "menu":
            self._draw_menu_page(surface, panel_x)
        elif self._page == "save_result":
            self._draw_menu_page(surface, panel_x)
            self._draw_save_banner(surface, panel_x)

        # ---- bottom hint ---------------------------------------------
        hint = self._hint_font.render("Tab / Esc  ·  Close", True, (50, 70, 110))
        surface.blit(hint, (panel_x + self._PANEL_W // 2 - hint.get_width() // 2,
                            SCREEN_HEIGHT - 22))

    # ------------------------------------------------------------------ #
    #  Page renderers                                                      #
    # ------------------------------------------------------------------ #

    def _draw_menu_page(self, surface: pygame.Surface, panel_x: int) -> None:
        item_start_y = 60
        item_h = 46
        inner_x = panel_x + 28

        for i, entry in enumerate(self._ENTRIES):
            y = item_start_y + i * item_h
            selected = i == self._cursor

            if selected:
                # Selection highlight pill
                pulse = 0.5 + 0.5 * math.sin(self._anim_time * 5)
                pill = pygame.Surface((self._PANEL_W - 16, item_h - 4), pygame.SRCALPHA)
                pill_alpha = int(55 + 30 * pulse)
                pygame.draw.rect(pill, (70, 130, 255, pill_alpha),
                                 (0, 0, pill.get_width(), pill.get_height()),
                                 border_radius=10)
                border_alpha = int(140 + 60 * pulse)
                pygame.draw.rect(pill, (100, 170, 255, border_alpha),
                                 (0, 0, pill.get_width(), pill.get_height()),
                                 width=2, border_radius=10)
                surface.blit(pill, (panel_x + 8, y - 2))

            # Icon
            if entry.disabled:
                icon_col = (50, 60, 90)
                label_col = (60, 75, 110)
            elif selected:
                icon_col = (180, 220, 255)
                label_col = (230, 245, 255)
            else:
                icon_col = (90, 120, 180)
                label_col = (150, 175, 215)

            icon_surf = self._icon_font.render(entry.icon, True, icon_col)
            surface.blit(icon_surf, (inner_x, y + (item_h - icon_surf.get_height()) // 2 - 2))

            # Label
            lbl_surf = self._item_font.render(entry.label, True, label_col)
            surface.blit(lbl_surf, (inner_x + 28, y + (item_h - lbl_surf.get_height()) // 2))

        # Bottom confirm hint
        hint = self._hint_font.render("Enter/Z  ·  Select", True, (50, 70, 110))
        surface.blit(hint, (panel_x + self._PANEL_W // 2 - hint.get_width() // 2,
                            SCREEN_HEIGHT - 42))

    def _draw_save_banner(self, surface: pygame.Surface, panel_x: int) -> None:
        ok = "saved" in self._save_msg.lower()
        col = (80, 220, 120) if ok else (220, 80, 80)
        bg_col = (20, 60, 30, 200) if ok else (60, 20, 20, 200)

        banner_h = 48
        banner_y = SCREEN_HEIGHT // 2 - 24
        banner_surf = pygame.Surface((self._PANEL_W, banner_h), pygame.SRCALPHA)
        banner_surf.fill(bg_col)
        pygame.draw.rect(banner_surf, (*col, 200), (0, 0, self._PANEL_W, banner_h), width=2)
        surface.blit(banner_surf, (panel_x, banner_y))

        render_text_outlined(
            surface, self._save_msg, self._item_font,
            panel_x + self._PANEL_W // 2, banner_y + banner_h // 2,
            color=col, outline_color=(5, 5, 5), center=True,
        )
