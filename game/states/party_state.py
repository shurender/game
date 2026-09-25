"""State for managing the player's party."""
import pygame
from typing import Any

from game.states.base_state import State
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS
from game.ui.text import render_text
from game.ui.components import draw_hp_bar
from game.player.party import PartyManager
from game.ui.menu import Menu


class PartyState(State):
    """UI for viewing, reordering, and selecting party members."""
    
    def __init__(self, game) -> None:
        super().__init__(game)
        self.font = self.game.assets.get_font(24)
        self.small_font = self.game.assets.get_font(16)
        
        self.party_mgr = PartyManager.get_instance()
        
        self.mode = "VIEW"  # VIEW, BATTLE_SWITCH, SWAP, MENU
        self.on_select = None
        
        self.cursor_index = 0
        self.selected_index = -1
        
        self.action_menu = None
        
    def enter(self, params: dict[str, Any] | None = None) -> None:
        params = params or {}
        self.mode = params.get("mode", "VIEW")
        self.on_select = params.get("on_select")
        
        self.cursor_index = 0
        self.selected_index = -1
        self.action_menu = None
        
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if self.action_menu:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.action_menu.move_up()
                    self.game.audio.play_sound("menu_move")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.action_menu.move_down()
                    self.game.audio.play_sound("menu_move")
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z, pygame.K_e):
                    self.game.audio.play_sound("menu_select")
                    self.action_menu.select()
                elif event.key in (pygame.K_ESCAPE, pygame.K_x):
                    self.game.audio.play_sound("menu_cancel")
                    self.action_menu = None
                    
            else:
                party_len = len(self.party_mgr.party)
                if party_len == 0:
                    if event.key in (pygame.K_ESCAPE, pygame.K_x):
                        self.game.state_machine.pop()
                    return
                    
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.cursor_index = (self.cursor_index - 1) % party_len
                    self.game.audio.play_sound("menu_move")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.cursor_index = (self.cursor_index + 1) % party_len
                    self.game.audio.play_sound("menu_move")
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z, pygame.K_e):
                    self.game.audio.play_sound("menu_select")
                    self._on_creature_click()
                elif event.key in (pygame.K_ESCAPE, pygame.K_x):
                    self.game.audio.play_sound("menu_cancel")
                    if self.mode == "SWAP":
                        self.mode = "VIEW"
                        self.selected_index = -1
                    else:
                        self.game.state_machine.pop()

    def _on_creature_click(self):
        c = self.party_mgr.party[self.cursor_index]
        
        if self.mode == "BATTLE_SWITCH":
            if c.is_fainted:
                # Can't select fainted
                self.game.audio.play_sound("menu_cancel")
            else:
                if self.on_select:
                    self.on_select(c)
                self.game.state_machine.pop()
                
        elif self.mode == "SWAP":
            self.party_mgr.swap_creatures(self.selected_index, self.cursor_index)
            self.mode = "VIEW"
            self.selected_index = -1
            
        elif self.mode == "VIEW":
            self.selected_index = self.cursor_index
            self._open_action_menu()
            
    def _open_action_menu(self):
        options = ["Summary", "Swap", "Cancel"]
        self.action_menu = Menu(
            options,
            self.font,
            SCREEN_WIDTH - 200,
            SCREEN_HEIGHT - 160,
            spacing=30
        )
        self.action_menu.on_select = self._on_action_menu_select
        
    def _on_action_menu_select(self, idx: int, text: str):
        if text == "Summary":
            # Push a summary state if we had one, but for now we'll just ignore
            self.game.audio.play_sound("menu_cancel")
        elif text == "Swap":
            self.mode = "SWAP"
        elif text == "Cancel":
            self.selected_index = -1
            
        self.action_menu = None
        
    def update(self, dt: float) -> None:
        if self.action_menu:
            self.action_menu.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(COLORS["bg_medium"])
        
        render_text(surface, "Creature Party", self.font, 40, 30, color=COLORS["accent"])
        
        y_offset = 80
        for i, creature in enumerate(self.party_mgr.party):
            # Highlight selected or cursor
            is_cursor = (i == self.cursor_index) and not self.action_menu
            is_selected = (i == self.selected_index)
            
            rect_color = COLORS["menu_highlight"] if is_cursor else COLORS["menu_bg"]
            if is_selected:
                rect_color = COLORS["accent_warm"]
                
            rect = pygame.Rect(40, y_offset, 600, 70)
            pygame.draw.rect(surface, rect_color, rect, border_radius=8)
            border_color = COLORS["accent"] if is_cursor or is_selected else COLORS["menu_border"]
            pygame.draw.rect(surface, border_color, rect, width=3, border_radius=8)
            
            # Info
            text_color = COLORS["text_dim"] if creature.is_fainted else COLORS["text"]
            render_text(surface, f"{creature.name} Lv.{creature.level}", self.font, 60, y_offset + 15, color=text_color)
            render_text(surface, f"HP: {int(creature.current_hp)}/{creature.stats.hp}", self.small_font, 420, y_offset + 25, color=text_color)
            
            # HP Bar
            bar_w = 120
            bar_h = 10
            draw_hp_bar(surface, 420, y_offset + 45, bar_w, bar_h, creature.current_hp, creature.stats.hp)

                
            y_offset += 80
            
        if self.action_menu:
            menu_rect = pygame.Rect(SCREEN_WIDTH - 220, SCREEN_HEIGHT - 180, 200, 160)
            pygame.draw.rect(surface, COLORS["menu_bg"], menu_rect, border_radius=8)
            pygame.draw.rect(surface, COLORS["menu_border"], menu_rect, width=4, border_radius=8)
            self.action_menu.draw(surface)
