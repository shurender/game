"""Quest Log UI State."""
import pygame
from typing import Any, List

from game.states.base_state import State
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS
from game.ui.text import render_text
from game.quests.quest_manager import QuestManager
from game.quests.quest import QuestStatus, Quest

# Layout constants
PANEL_W = SCREEN_WIDTH // 2 - 20
LIST_X = 30
DETAIL_X = SCREEN_WIDTH // 2 + 10
HEADER_H = 90
ROW_H = 54

class QuestLogState(State):
    """UI for viewing active and completed quests."""
    def __init__(self, game) -> None:
        super().__init__(game)
        self.font = game.assets.get_font(22)
        self.small = game.assets.get_font(16)

        self.qm = QuestManager.get_instance()
        
        self.tab = "ACTIVE" # "ACTIVE" | "COMPLETED"
        self.cursor = 0
        
        self._active_list: List[Quest] = []
        self._completed_list: List[Quest] = []

    def enter(self, params: dict[str, Any] | None = None) -> None:
        self._refresh_lists()
        self.cursor = 0
        
    def _refresh_lists(self) -> None:
        self._active_list = self.qm.get_active_quests()
        self._completed_list = self.qm.get_completed_quests()
        
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
            
        key = event.key
        
        rows = self._active_list if self.tab == "ACTIVE" else self._completed_list
        n = len(rows)
        
        if key in (pygame.K_LEFT, pygame.K_a):
            self._switch_tab("ACTIVE")
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self._switch_tab("COMPLETED")
        elif key in (pygame.K_UP, pygame.K_w):
            if n > 0:
                self.cursor = (self.cursor - 1) % n
                self.game.audio.play_sound("menu_move")
        elif key in (pygame.K_DOWN, pygame.K_s):
            if n > 0:
                self.cursor = (self.cursor + 1) % n
                self.game.audio.play_sound("menu_move")
        elif key in (pygame.K_ESCAPE, pygame.K_x, pygame.K_RETURN, pygame.K_SPACE, pygame.K_z, pygame.K_e):
            self.game.state_machine.pop()
            
    def _switch_tab(self, tab: str) -> None:
        if self.tab != tab:
            self.tab = tab
            self.cursor = 0
            self.game.audio.play_sound("menu_move")
            
    def update(self, dt: float) -> None:
        pass
        
    def render(self, surface: pygame.Surface) -> None:
        surface.fill(COLORS["bg_dark"])
        self._render_header(surface)
        self._render_tabs(surface)
        self._render_list(surface)
        self._render_detail(surface)
        self._render_hints(surface)
        
    def _render_header(self, surface: pygame.Surface) -> None:
        render_text(surface, "Quest Log", self.font, LIST_X, 18, color=COLORS["accent"])
        pygame.draw.line(surface, COLORS["menu_border"], (LIST_X, 50), (SCREEN_WIDTH - LIST_X, 50), 2)
        
    def _render_tabs(self, surface: pygame.Surface) -> None:
        tabs = [("ACTIVE", LIST_X), ("COMPLETED", LIST_X + 130)]
        for label, tx in tabs:
            active = label == self.tab
            col = COLORS["accent"] if active else COLORS["text_dim"]
            r = pygame.Rect(tx - 10, 56, 110, 30)
            if active:
                pygame.draw.rect(surface, COLORS["menu_bg"], r, border_radius=6)
                pygame.draw.rect(surface, COLORS["accent"], r, 2, border_radius=6)
            render_text(surface, label.capitalize(), self.font, tx, 60, color=col)
            
    def _render_list(self, surface: pygame.Surface) -> None:
        rows = self._active_list if self.tab == "ACTIVE" else self._completed_list
        base_y = HEADER_H + 16
        visible_start = max(0, self.cursor - 5)
        visible = rows[visible_start: visible_start + 8]

        if not rows:
            hint = "No active quests." if self.tab == "ACTIVE" else "No completed quests."
            render_text(surface, hint, self.small, LIST_X, base_y + 20, color=COLORS["text_dim"])
            return
            
        for vi, row in enumerate(visible):
            ri = visible_start + vi
            is_sel = ri == self.cursor
            
            label = row.name
            type_str = f"[{row.quest_type.upper()}]"
            name_col = COLORS["text"]
            
            ry = base_y + vi * ROW_H
            bg = COLORS["menu_highlight"] if is_sel else COLORS["menu_bg"]
            r = pygame.Rect(LIST_X - 8, ry - 4, PANEL_W, ROW_H - 6)
            pygame.draw.rect(surface, bg, r, border_radius=6)
            if is_sel:
                pygame.draw.rect(surface, COLORS["accent"], r, 2, border_radius=6)
                
            render_text(surface, type_str, self.small, LIST_X, ry + 8, color=COLORS["accent_warm"])
            render_text(surface, label, self.font, LIST_X + 60, ry + 4, color=name_col)

    def _render_detail(self, surface: pygame.Surface) -> None:
        rows = self._active_list if self.tab == "ACTIVE" else self._completed_list
        panel = pygame.Rect(DETAIL_X, HEADER_H, SCREEN_WIDTH - DETAIL_X - 20,
                            SCREEN_HEIGHT - HEADER_H - 60)
        pygame.draw.rect(surface, COLORS["menu_bg"], panel, border_radius=10)
        pygame.draw.rect(surface, COLORS["menu_border"], panel, 2, border_radius=10)
        
        if not rows or self.cursor >= len(rows):
            return
            
        q = rows[self.cursor]
        
        # Quest Name
        render_text(surface, q.name, self.font, panel.x + 18, panel.y + 16, color=COLORS["accent"])
        
        # Wrap description
        words = q.description.split()
        lines, line = [], []
        for w in words:
            line.append(w)
            if len(" ".join(line)) > 35:
                lines.append(" ".join(line[:-1]))
                line = [w]
        if line:
            lines.append(" ".join(line))
        for i, ln in enumerate(lines[:3]):
            render_text(surface, ln, self.small, panel.x + 18, panel.y + 50 + i * 20, color=COLORS["text"])
            
        # Objectives
        obj_y = panel.y + 130
        render_text(surface, "Objectives:", self.small, panel.x + 18, obj_y, color=COLORS["accent_warm"])
        for i, obj in enumerate(q.objectives):
            status = "[X]" if obj.is_complete else "[ ]"
            prog = f"({obj.current_progress}/{obj.required_progress})" if obj.required_progress > 1 else ""
            txt = f"{status} {obj.description} {prog}"
            render_text(surface, txt, self.small, panel.x + 18, obj_y + 25 + i * 20, color=COLORS["text"])
            
        # Rewards
        rew_y = panel.y + 240
        if q.rewards:
            render_text(surface, "Rewards:", self.small, panel.x + 18, rew_y, color=COLORS["accent_warm"])
            for i, rew in enumerate(q.rewards):
                txt = f"- {rew.quantity}x {rew.item_id}" if rew.reward_type == "item" else f"- {rew.amount} coins"
                render_text(surface, txt, self.small, panel.x + 18, rew_y + 25 + i * 20, color=COLORS["text"])

    def _render_hints(self, surface: pygame.Surface) -> None:
        render_text(surface, "◄► Tab   ▲▼ Browse   X Back",
                    self.small, LIST_X, SCREEN_HEIGHT - 24, color=COLORS["text_dim"])
