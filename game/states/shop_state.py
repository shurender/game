"""ShopState — full-screen shop UI backed by ShopTransaction logic."""
import math
import pygame
from typing import Any

from game.states.base_state import State
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS
from game.ui.text import render_text, TypewriterText
from game.world.shop import ShopTransaction
from game.world.shop_factory import ShopFactory
from game.inventory.inventory import Inventory
from game.player.wallet import Wallet


# ── Layout constants ────────────────────────────────────────────────────────
PANEL_W = SCREEN_WIDTH // 2 - 20
LIST_X = 30
DETAIL_X = SCREEN_WIDTH // 2 + 10
HEADER_H = 90
ROW_H = 54


class ShopState(State):
    """Shop browsing UI.

    Phases:
        GREETING  → typewriter greeting from shopkeeper
        BUY       → browse & buy from shop stock
        SELL      → browse & sell from player inventory
        FAREWELL  → typewriter farewell, then pop
    """

    def __init__(self, game) -> None:
        super().__init__(game)
        self.font = game.assets.get_font(22)
        self.small = game.assets.get_font(16)

        self.shop = None
        self.txn: ShopTransaction | None = None

        # UI state
        self.tab = "BUY"          # "BUY" | "SELL"
        self.cursor = 0
        self.phase = "GREETING"

        self._buy_list: list = []   # ShopListing
        self._sell_list: list = []  # (Item, qty)

        self._typewriter: TypewriterText | None = None
        self._feedback = ""
        self._feedback_timer = 0.0
        self._bob = 0.0             # cursor bob animation

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def enter(self, params: dict[str, Any] | None = None) -> None:
        params = params or {}
        shop_id = params.get("shop_id", "")

        factory = ShopFactory.get_instance()
        try:
            self.shop = factory.get(shop_id)
        except ValueError:
            all_shops = factory.all()
            self.shop = all_shops[0] if all_shops else None
            
        if not self.shop:
            self.game.state_machine.pop()
            return

        wallet = Wallet.get_instance()
        inv = Inventory.get_instance()
        self.txn = ShopTransaction(self.shop, inv, wallet.__dict__)

        self._refresh_lists()
        self.cursor = 0
        self.tab = "BUY"
        self.phase = "GREETING"
        self._typewriter = TypewriterText(self.shop.greeting, chars_per_second=40)
        self._feedback = ""

    def _refresh_lists(self) -> None:
        self._buy_list = list(self.shop.listings)
        inv = Inventory.get_instance()
        self._sell_list = [(item, qty) for item, qty in inv.items()
                           if item.category != "Key Item"]

    # ── Input ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        key = event.key

        if self.phase == "GREETING":
            if key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE, pygame.K_e):
                if self._typewriter and not self._typewriter.is_complete:
                    self._typewriter.skip()
                else:
                    self.phase = "BUY"
            return

        if self.phase == "FAREWELL":
            if key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE, pygame.K_e):
                if self._typewriter and not self._typewriter.is_complete:
                    self._typewriter.skip()
                else:
                    self.game.state_machine.pop()
            return

        # BUY / SELL browsing
        rows = self._buy_list if self.tab == "BUY" else self._sell_list
        n = len(rows)

        if key in (pygame.K_LEFT, pygame.K_a):
            self._switch_tab("BUY")
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self._switch_tab("SELL")
        elif key in (pygame.K_UP, pygame.K_w):
            if n:
                self.cursor = (self.cursor - 1) % n
                self.game.audio.play_sound("menu_move")
        elif key in (pygame.K_DOWN, pygame.K_s):
            if n:
                self.cursor = (self.cursor + 1) % n
                self.game.audio.play_sound("menu_move")
        elif key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE, pygame.K_e):
            self._confirm_selection()
        elif key in (pygame.K_ESCAPE, pygame.K_x):
            self._begin_farewell()

    def _switch_tab(self, tab: str) -> None:
        if self.tab == tab:
            return
        self.tab = tab
        self.cursor = 0
        self._refresh_lists()
        self.game.audio.play_sound("menu_move")

    def _confirm_selection(self) -> None:
        self.game.audio.play_sound("menu_select")
        try:
            if self.tab == "BUY":
                if not self._buy_list:
                    return
                listing = self._buy_list[self.cursor]
                msg = self.txn.buy(listing.item, qty=1)
                self._set_feedback(msg)
                self._refresh_lists()
            else:
                if not self._sell_list:
                    return
                item, qty = self._sell_list[self.cursor]
                msg = self.txn.sell(item, qty=1)
                self._set_feedback(msg)
                self._refresh_lists()
                # Clamp cursor after possible list shrink
                rows = self._sell_list
                if rows:
                    self.cursor = min(self.cursor, len(rows) - 1)
                else:
                    self.cursor = 0
        except Exception as e:
            self.game.audio.play_sound("menu_cancel")
            self._set_feedback(str(e))

    def _begin_farewell(self) -> None:
        self.phase = "FAREWELL"
        self._typewriter = TypewriterText(self.shop.farewell, chars_per_second=40)

    def _set_feedback(self, msg: str) -> None:
        self._feedback = msg
        self._feedback_timer = 2.8

    # ── Update ───────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        if self._typewriter:
            self._typewriter.update(dt)
        if self._feedback_timer > 0:
            self._feedback_timer -= dt
            if self._feedback_timer <= 0:
                self._feedback = ""
        self._bob += dt * 3.5

    # ── Render ───────────────────────────────────────────────────────────────

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(COLORS["bg_dark"])

        if self.phase in ("GREETING", "FAREWELL"):
            self._render_dialogue(surface)
            return

        self._render_header(surface)
        self._render_tabs(surface)
        self._render_list(surface)
        self._render_detail(surface)
        self._render_feedback(surface)
        self._render_hints(surface)

    def _render_dialogue(self, surface: pygame.Surface) -> None:
        # Shop keeper portrait placeholder
        portrait_rect = pygame.Rect(60, 140, 200, 200)
        pygame.draw.rect(surface, COLORS["menu_bg"], portrait_rect, border_radius=12)
        pygame.draw.rect(surface, COLORS["accent"], portrait_rect, 3, border_radius=12)
        render_text(surface, "🛒", self.font, portrait_rect.centerx, portrait_rect.centery,
                    color=COLORS["accent"], center=True)
        render_text(surface, self.shop.name, self.font, portrait_rect.x,
                    portrait_rect.bottom + 10, color=COLORS["accent"])

        # Speech bubble
        box_rect = pygame.Rect(280, 140, SCREEN_WIDTH - 320, 200)
        pygame.draw.rect(surface, COLORS["menu_bg"], box_rect, border_radius=12)
        pygame.draw.rect(surface, COLORS["menu_border"], box_rect, 3, border_radius=12)

        text = self._typewriter.visible_text if self._typewriter else ""
        # Simple word-wrap at ~45 chars
        words = text.split()
        lines, line = [], []
        for w in words:
            line.append(w)
            if len(" ".join(line)) > 44:
                lines.append(" ".join(line[:-1]))
                line = [w]
        if line:
            lines.append(" ".join(line))

        for i, ln in enumerate(lines[:5]):
            render_text(surface, ln, self.font, box_rect.x + 20, box_rect.y + 20 + i * 30,
                        color=COLORS["text"])

        # Blinking prompt
        done = not self._typewriter or self._typewriter.is_complete
        if done and (pygame.time.get_ticks() // 500) % 2 == 0:
            render_text(surface, "▼  Press Z", self.small, box_rect.right - 130,
                        box_rect.bottom - 28, color=COLORS["accent"])

    def _render_header(self, surface: pygame.Surface) -> None:
        render_text(surface, self.shop.name, self.font, LIST_X, 18, color=COLORS["accent"])
        wallet = Wallet.get_instance()
        coins_text = f"💰 {wallet.coins} coins"
        render_text(surface, coins_text, self.font,
                    SCREEN_WIDTH - 220, 18, color=COLORS["accent_warm"])
        pygame.draw.line(surface, COLORS["menu_border"],
                         (LIST_X, 50), (SCREEN_WIDTH - LIST_X, 50), 2)

    def _render_tabs(self, surface: pygame.Surface) -> None:
        tabs = [("BUY", LIST_X), ("SELL", LIST_X + 130)]
        for label, tx in tabs:
            active = label == self.tab
            col = COLORS["accent"] if active else COLORS["text_dim"]
            r = pygame.Rect(tx - 10, 56, 110, 30)
            if active:
                pygame.draw.rect(surface, COLORS["menu_bg"], r, border_radius=6)
                pygame.draw.rect(surface, COLORS["accent"], r, 2, border_radius=6)
            render_text(surface, label, self.font, tx, 60, color=col)

    def _render_list(self, surface: pygame.Surface) -> None:
        rows = self._buy_list if self.tab == "BUY" else self._sell_list
        base_y = HEADER_H + 16
        visible_start = max(0, self.cursor - 5)
        visible = rows[visible_start: visible_start + 8]

        if not rows:
            hint = "Nothing to buy." if self.tab == "BUY" else "Nothing to sell."
            render_text(surface, hint, self.small, LIST_X, base_y + 20, color=COLORS["text_dim"])
            return

        for vi, row in enumerate(visible):
            ri = visible_start + vi
            is_sel = ri == self.cursor

            if self.tab == "BUY":
                listing = row
                label = listing.item.name
                price_str = f"{listing.buy_price} ¢"
                affordable = Wallet.get_instance().coins >= listing.buy_price
                name_col = COLORS["text"] if affordable else COLORS["text_dim"]
                price_col = COLORS["accent_warm"] if affordable else COLORS["hp_red"]
            else:
                item, qty = row
                label = item.name
                sell_p = self.shop.sell_price_for(item)
                price_str = f"+{sell_p} ¢  ×{qty}"
                name_col = COLORS["text"]
                price_col = COLORS["accent_green"]

            ry = base_y + vi * ROW_H
            bg = COLORS["menu_highlight"] if is_sel else COLORS["menu_bg"]
            r = pygame.Rect(LIST_X - 8, ry - 4, PANEL_W, ROW_H - 6)
            pygame.draw.rect(surface, bg, r, border_radius=6)
            if is_sel:
                pygame.draw.rect(surface, COLORS["accent"], r, 2, border_radius=6)
                # Animated cursor triangle
                bx = LIST_X - 6 + math.sin(self._bob) * 3
                pts = [(bx, ry + 16), (bx + 8, ry + 22), (bx, ry + 28)]
                pygame.draw.polygon(surface, COLORS["accent"], pts)

            render_text(surface, label, self.font, LIST_X + 16, ry + 4, color=name_col)
            render_text(surface, price_str, self.small,
                        LIST_X + PANEL_W - 130, ry + 10, color=price_col)

    def _render_detail(self, surface: pygame.Surface) -> None:
        rows = self._buy_list if self.tab == "BUY" else self._sell_list
        panel = pygame.Rect(DETAIL_X, HEADER_H, SCREEN_WIDTH - DETAIL_X - 20,
                            SCREEN_HEIGHT - HEADER_H - 60)
        pygame.draw.rect(surface, COLORS["menu_bg"], panel, border_radius=10)
        pygame.draw.rect(surface, COLORS["menu_border"], panel, 2, border_radius=10)

        if not rows or self.cursor >= len(rows):
            return

        row = rows[self.cursor]
        item = row.item if self.tab == "BUY" else row[0]

        render_text(surface, item.name, self.font, panel.x + 18, panel.y + 16,
                    color=COLORS["accent"])
        render_text(surface, f"Category: {item.category}", self.small,
                    panel.x + 18, panel.y + 48, color=COLORS["text_dim"])

        if self.tab == "BUY":
            render_text(surface, f"Price: {row.buy_price} coins", self.small,
                        panel.x + 18, panel.y + 70, color=COLORS["accent_warm"])
        else:
            sp = self.shop.sell_price_for(item)
            render_text(surface, f"You'll receive: {sp} coins", self.small,
                        panel.x + 18, panel.y + 70, color=COLORS["accent_green"])

        # Description with wrapping
        words = item.description.split()
        lines, line = [], []
        for w in words:
            line.append(w)
            if len(" ".join(line)) > 26:
                lines.append(" ".join(line[:-1]))
                line = [w]
        if line:
            lines.append(" ".join(line))
        for i, ln in enumerate(lines[:4]):
            render_text(surface, ln, self.small,
                        panel.x + 18, panel.y + 100 + i * 22, color=COLORS["text"])

        # Owned qty
        inv = Inventory.get_instance()
        owned = inv.quantity(item.item_id)
        render_text(surface, f"In bag: {owned}", self.small,
                    panel.x + 18, panel.y + 180, color=COLORS["text_dim"])

    def _render_feedback(self, surface: pygame.Surface) -> None:
        if not self._feedback:
            return
        fb = pygame.Rect(LIST_X, SCREEN_HEIGHT - 54, SCREEN_WIDTH - LIST_X * 2, 40)
        pygame.draw.rect(surface, COLORS["menu_bg"], fb, border_radius=8)
        pygame.draw.rect(surface, COLORS["accent_green"], fb, 2, border_radius=8)
        render_text(surface, self._feedback, self.small,
                    fb.x + 14, fb.y + 10, color=COLORS["accent_green"])

    def _render_hints(self, surface: pygame.Surface) -> None:
        render_text(surface, "◄► Tab   ▲▼ Browse   Z Confirm   X Leave",
                    self.small, LIST_X, SCREEN_HEIGHT - 24, color=COLORS["text_dim"])
