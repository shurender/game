"""InventoryState — browse, filter, and use items from the bag."""
import pygame
from typing import Any

from game.states.base_state import State
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS
from game.ui.text import render_text
from game.ui.components import draw_hp_bar
from game.ui.menu import Menu
from game.inventory.inventory import Inventory
from game.inventory.item import Item
from game.player.party import PartyManager


# Tab order
CATEGORIES = ["All", "Healing", "Capture", "Stat Boost", "Key Item"]


class InventoryState(State):
    """Full-screen inventory browser.

    Params accepted via enter():
        mode        "VIEW" (default) | "BATTLE_USE" — when opened mid-battle.
        on_use      Callable[[item_id, target_creature], None] — called after
                    a successful use in BATTLE_USE mode (UI should animate).
        battle      Battle instance (needed for mid-battle use).
    """

    def __init__(self, game) -> None:
        super().__init__(game)
        self.font = game.assets.get_font(24)
        self.small_font = game.assets.get_font(16)

        self.mode = "VIEW"
        self.on_use = None
        self.battle = None

        self.tab_index = 0          # index into CATEGORIES
        self.item_cursor = 0        # row in current filtered list
        self.sub_phase = "LIST"     # "LIST" | "TARGET" | "ACTION"

        self._filtered: list[tuple[Item, int]] = []
        self._action_menu: Menu | None = None
        self._target_cursor = 0

        self._feedback: str = ""
        self._feedback_timer: float = 0.0

    # ------------------------------------------------------------------
    def enter(self, params: dict[str, Any] | None = None) -> None:
        params = params or {}
        self.mode = params.get("mode", "VIEW")
        self.on_use = params.get("on_use")
        self.battle = params.get("battle")
        self.tab_index = 0
        self.item_cursor = 0
        self.sub_phase = "LIST"
        self._action_menu = None
        self._refresh_list()

    def _refresh_list(self) -> None:
        inv = Inventory.get_instance()
        cat = CATEGORIES[self.tab_index]
        if cat == "All":
            self._filtered = inv.items()
        else:
            self._filtered = inv.by_category(cat)
        self.item_cursor = min(self.item_cursor, max(0, len(self._filtered) - 1))

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        key = event.key

        if self.sub_phase == "LIST":
            self._handle_list_keys(key)
        elif self.sub_phase == "ACTION" and self._action_menu:
            self._handle_action_menu_keys(key)
        elif self.sub_phase == "TARGET":
            self._handle_target_keys(key)

    def _handle_list_keys(self, key: int) -> None:
        if key in (pygame.K_ESCAPE, pygame.K_x):
            self.game.audio.play_sound("menu_cancel")
            self.game.state_machine.pop()

        elif key in (pygame.K_LEFT, pygame.K_a):
            self.game.audio.play_sound("menu_move")
            self.tab_index = (self.tab_index - 1) % len(CATEGORIES)
            self.item_cursor = 0
            self._refresh_list()

        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.game.audio.play_sound("menu_move")
            self.tab_index = (self.tab_index + 1) % len(CATEGORIES)
            self.item_cursor = 0
            self._refresh_list()

        elif key in (pygame.K_UP, pygame.K_w):
            if self._filtered:
                self.game.audio.play_sound("menu_move")
                self.item_cursor = (self.item_cursor - 1) % len(self._filtered)

        elif key in (pygame.K_DOWN, pygame.K_s):
            if self._filtered:
                self.game.audio.play_sound("menu_move")
                self.item_cursor = (self.item_cursor + 1) % len(self._filtered)

        elif key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE, pygame.K_e):
            if self._filtered:
                self.game.audio.play_sound("menu_select")
                self._open_action_menu()

    def _handle_action_menu_keys(self, key: int) -> None:
        if key in (pygame.K_UP, pygame.K_w):
            self._action_menu.move_up()
            self.game.audio.play_sound("menu_move")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self._action_menu.move_down()
            self.game.audio.play_sound("menu_move")
        elif key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE, pygame.K_e):
            self.game.audio.play_sound("menu_select")
            self._action_menu.select()
        elif key in (pygame.K_ESCAPE, pygame.K_x):
            self.game.audio.play_sound("menu_cancel")
            self.sub_phase = "LIST"
            self._action_menu = None

    def _handle_target_keys(self, key: int) -> None:
        party = PartyManager.get_instance().party
        if key in (pygame.K_UP, pygame.K_w):
            self.game.audio.play_sound("menu_move")
            self._target_cursor = (self._target_cursor - 1) % len(party)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.game.audio.play_sound("menu_move")
            self._target_cursor = (self._target_cursor + 1) % len(party)
        elif key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE, pygame.K_e):
            self.game.audio.play_sound("menu_select")
            self._apply_to_target(party[self._target_cursor])
        elif key in (pygame.K_ESCAPE, pygame.K_x):
            self.game.audio.play_sound("menu_cancel")
            self.sub_phase = "ACTION"

    # ------------------------------------------------------------------
    def _open_action_menu(self) -> None:
        item, _qty = self._filtered[self.item_cursor]
        options = []
        if item.category != "Key Item":
            options.append("Use")
        options.append("Cancel")

        self._action_menu = Menu(
            options, self.font,
            SCREEN_WIDTH - 220, SCREEN_HEIGHT - 140, spacing=32
        )
        self._action_menu.on_select = self._on_action_select
        self.sub_phase = "ACTION"

    def _on_action_select(self, idx: int, text: str) -> None:
        self._action_menu = None
        if text == "Cancel":
            self.sub_phase = "LIST"
            return

        item, _qty = self._filtered[self.item_cursor]

        if item.category in ("Healing", "Stat Boost"):
            # Need to choose a target from the party
            self.sub_phase = "TARGET"
            self._target_cursor = 0

        elif item.category == "Capture":
            # In battle → pass to battle state to handle animation and capture logic
            if self.mode == "BATTLE_USE" and self.battle:
                self.game.state_machine.pop()
                if self.on_use:
                    self.on_use(item.item_id, self.battle.enemy_creature)
            else:
                self._set_feedback("Can only use capture items in battle!")
                self.sub_phase = "LIST"

        else:
            self._set_feedback(f"{item.name} cannot be used right now.")
            self.sub_phase = "LIST"

    def _apply_to_target(self, creature) -> None:
        item, _qty = self._filtered[self.item_cursor]
        self._apply_to_creature(item, creature)
        self.sub_phase = "LIST"

    def _apply_to_creature(self, item: Item, creature) -> None:
        inv = Inventory.get_instance()
        try:
            msg = inv.use(item.item_id, target=creature)
            
            if self.mode == "BATTLE_USE":
                self.game.state_machine.pop()
                if self.on_use:
                    self.on_use(item.item_id, creature)
            else:
                self._set_feedback(msg)
                self._refresh_list()
        except ValueError as e:
            self._set_feedback(str(e))

    def _set_feedback(self, msg: str) -> None:
        self._feedback = msg
        self._feedback_timer = 2.5

    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        if self._action_menu:
            self._action_menu.update(dt)
        if self._feedback_timer > 0:
            self._feedback_timer -= dt
            if self._feedback_timer <= 0:
                self._feedback = ""

    # ------------------------------------------------------------------
    def render(self, surface: pygame.Surface) -> None:
        surface.fill(COLORS["bg_dark"])

        # ── Title ──────────────────────────────────────────────────────
        render_text(surface, "Bag", self.font, 40, 24, color=COLORS["accent"])

        # ── Tab bar ────────────────────────────────────────────────────
        tab_x = 40
        for i, cat in enumerate(CATEGORIES):
            is_active = (i == self.tab_index)
            color = COLORS["accent"] if is_active else COLORS["text_dim"]
            rect = pygame.Rect(tab_x - 8, 58, len(cat) * 14 + 24, 32)
            if is_active:
                pygame.draw.rect(surface, COLORS["menu_bg"], rect, border_radius=6)
                pygame.draw.rect(surface, COLORS["menu_border"], rect, 2, border_radius=6)
            render_text(surface, cat, self.small_font, tab_x, 64, color=color)
            tab_x += len(cat) * 14 + 36

        pygame.draw.line(surface, COLORS["menu_border"], (30, 94), (SCREEN_WIDTH - 30, 94), 2)

        # ── Item list ──────────────────────────────────────────────────
        list_x, list_y = 40, 110
        row_h = 56

        if not self._filtered:
            render_text(surface, "Nothing here.", self.small_font,
                        list_x, list_y + 20, color=COLORS["text_dim"])
        else:
            visible_start = max(0, self.item_cursor - 5)
            visible = self._filtered[visible_start: visible_start + 8]

            for vi, (item, qty) in enumerate(visible):
                real_i = visible_start + vi
                is_selected = (real_i == self.item_cursor)

                row_rect = pygame.Rect(list_x - 8, list_y + vi * row_h - 6,
                                       SCREEN_WIDTH // 2 - 20, row_h - 4)
                bg = COLORS["menu_highlight"] if is_selected else COLORS["menu_bg"]
                pygame.draw.rect(surface, bg, row_rect, border_radius=6)
                if is_selected:
                    pygame.draw.rect(surface, COLORS["accent"], row_rect, 2, border_radius=6)

                render_text(surface, item.name, self.font,
                            list_x, list_y + vi * row_h, color=COLORS["text"])
                render_text(surface, f"×{qty}", self.small_font,
                            row_rect.right - 48, list_y + vi * row_h + 6,
                            color=COLORS["accent"])

        # ── Detail panel ───────────────────────────────────────────────
        panel_x = SCREEN_WIDTH // 2 + 20
        panel_rect = pygame.Rect(panel_x, 110, SCREEN_WIDTH - panel_x - 30,
                                 SCREEN_HEIGHT - 180)
        pygame.draw.rect(surface, COLORS["menu_bg"], panel_rect, border_radius=10)
        pygame.draw.rect(surface, COLORS["menu_border"], panel_rect, 2, border_radius=10)

        if self._filtered:
            item, qty = self._filtered[self.item_cursor]
            render_text(surface, item.name, self.font,
                        panel_x + 20, 128, color=COLORS["accent"])
            render_text(surface, f"Category: {item.category}", self.small_font,
                        panel_x + 20, 164, color=COLORS["text_dim"])
            render_text(surface, f"Qty in bag: {qty}", self.small_font,
                        panel_x + 20, 188, color=COLORS["text_dim"])
            # Word-wrap description (simple 30-char splits)
            desc = item.description
            words = desc.split()
            lines, line = [], []
            for w in words:
                line.append(w)
                if len(" ".join(line)) > 28:
                    lines.append(" ".join(line[:-1]))
                    line = [w]
            if line:
                lines.append(" ".join(line))
            for li, ln in enumerate(lines):
                render_text(surface, ln, self.small_font,
                            panel_x + 20, 220 + li * 22, color=COLORS["text"])

        # ── Target selection overlay ───────────────────────────────────
        if self.sub_phase == "TARGET":
            party = PartyManager.get_instance().party
            ov_rect = pygame.Rect(30, 100, SCREEN_WIDTH - 60, SCREEN_HEIGHT - 200)
            pygame.draw.rect(surface, (10, 10, 20, 220), ov_rect, border_radius=10)
            pygame.draw.rect(surface, COLORS["accent"], ov_rect, 2, border_radius=10)
            render_text(surface, "Choose a creature:", self.font, 60, 120, color=COLORS["accent"])

            for pi, creature in enumerate(party):
                ty = 170 + pi * 60
                is_sel = (pi == self._target_cursor)
                cr = pygame.Rect(50, ty - 4, 500, 52)
                pygame.draw.rect(surface, COLORS["menu_highlight"] if is_sel else COLORS["menu_bg"],
                                 cr, border_radius=6)
                if is_sel:
                    pygame.draw.rect(surface, COLORS["accent"], cr, 2, border_radius=6)
                col = COLORS["text_dim"] if creature.is_fainted else COLORS["text"]
                render_text(surface, f"{creature.name}  Lv.{creature.level}", self.font, 70, ty, color=col)
                render_text(surface, f"HP {int(creature.current_hp)}/{creature.stats.hp}",
                            self.small_font, 380, ty - 6, color=col)
                draw_hp_bar(surface, 380, ty + 18, 140, 10, creature.current_hp, creature.stats.hp)

        # ── Action menu overlay ────────────────────────────────────────
        if self._action_menu and self.sub_phase == "ACTION":
            am_rect = pygame.Rect(SCREEN_WIDTH - 240, SCREEN_HEIGHT - 160, 220, 140)
            pygame.draw.rect(surface, COLORS["menu_bg"], am_rect, border_radius=8)
            pygame.draw.rect(surface, COLORS["menu_border"], am_rect, 3, border_radius=8)
            self._action_menu.draw(surface)

        # ── Feedback message ───────────────────────────────────────────
        if self._feedback:
            fb_rect = pygame.Rect(30, SCREEN_HEIGHT - 68, SCREEN_WIDTH - 60, 50)
            pygame.draw.rect(surface, COLORS["menu_bg"], fb_rect, border_radius=8)
            pygame.draw.rect(surface, COLORS["accent_green"], fb_rect, 2, border_radius=8)
            render_text(surface, self._feedback, self.small_font,
                        fb_rect.x + 16, fb_rect.y + 14, color=COLORS["accent_green"])

        # ── Controls hint ──────────────────────────────────────────────
        render_text(surface, "◄► Tab   ▲▼ Select   Z Use   X Back",
                    self.small_font, 40, SCREEN_HEIGHT - 28, color=COLORS["text_dim"])
