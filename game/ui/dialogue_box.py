"""UI component for rendering dialogue boxes with typewriter effects."""
import pygame
from typing import Callable

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, TILE_SIZE

class DialogueBox:
    """Renders a dialogue box, name tag, and typewriter text."""
    
    def __init__(self, font: pygame.font.Font, name_font: pygame.font.Font):
        self.font = font
        self.name_font = name_font
        
        # Dimensions
        self.width = SCREEN_WIDTH - 64
        self.height = 140
        self.x = 32
        self.y = SCREEN_HEIGHT - self.height - 32
        
        # State
        self.speaker = ""
        self.full_text = ""
        self.displayed_text = ""
        self.char_index = 0.0
        self.typewriter_speed = 45.0  # Chars per second
        
        self.is_finished = True
        self.on_complete: Callable | None = None
        
        # Choice UI
        self.choices: list[dict] = []
        self.selected_choice = 0
        
    def start_text(self, speaker: str, text: str, choices: list[dict] = None) -> None:
        """Begin typing new text."""
        self.speaker = speaker
        self.full_text = text
        self.displayed_text = ""
        self.char_index = 0.0
        self.is_finished = False
        self.choices = choices or []
        self.selected_choice = 0
        
    def skip_typing(self) -> None:
        """Instantly finish the typewriter effect."""
        self.char_index = len(self.full_text)
        self.displayed_text = self.full_text
        self.is_finished = True
        
    def update(self, dt: float) -> None:
        if not self.is_finished:
            self.char_index += self.typewriter_speed * dt
            if self.char_index >= len(self.full_text):
                self.skip_typing()
            else:
                self.displayed_text = self.full_text[:int(self.char_index)]
                
    def move_choice(self, direction: int) -> None:
        """Move choice selection (-1 for up, 1 for down)."""
        if not self.choices or not self.is_finished:
            return
        self.selected_choice = (self.selected_choice + direction) % len(self.choices)
        
    def render(self, surface: pygame.Surface) -> None:
        # Draw main box
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, COLORS["menu_bg"], rect, border_radius=8)
        pygame.draw.rect(surface, COLORS["menu_border"], rect, width=4, border_radius=8)
        
        # Draw name tag
        if self.speaker:
            name_surf = self.name_font.render(self.speaker, True, COLORS["text"])
            name_w, name_h = name_surf.get_size()
            name_rect = pygame.Rect(self.x + 16, self.y - name_h - 8, name_w + 32, name_h + 16)
            pygame.draw.rect(surface, COLORS["menu_bg"], name_rect, border_radius=8)
            pygame.draw.rect(surface, COLORS["menu_border"], name_rect, width=4, border_radius=8)
            surface.blit(name_surf, (name_rect.x + 16, name_rect.y + 8))
            
        # Draw text (simple wrapping, in a real game we'd use word wrap)
        # For this implementation we'll assume text fits or we split it across nodes.
        text_surf = self.font.render(self.displayed_text, True, COLORS["text"])
        surface.blit(text_surf, (self.x + 24, self.y + 24))
        
        # Draw blinking arrow if finished and no choices
        if self.is_finished and not self.choices:
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                arrow = self.font.render("▼", True, COLORS["accent"])
                surface.blit(arrow, (self.x + self.width - 32, self.y + self.height - 40))
                
        # Draw choices if finished
        if self.is_finished and self.choices:
            choice_box_w = 200
            choice_box_h = len(self.choices) * 40 + 24
            choice_x = SCREEN_WIDTH - choice_box_w - 32
            choice_y = self.y - choice_box_h - 16
            
            c_rect = pygame.Rect(choice_x, choice_y, choice_box_w, choice_box_h)
            pygame.draw.rect(surface, COLORS["menu_bg"], c_rect, border_radius=8)
            pygame.draw.rect(surface, COLORS["menu_border"], c_rect, width=4, border_radius=8)
            
            for i, c in enumerate(self.choices):
                color = COLORS["accent"] if i == self.selected_choice else COLORS["text"]
                c_surf = self.font.render(c["text"], True, color)
                surface.blit(c_surf, (choice_x + 32, choice_y + 16 + i * 40))
                
                if i == self.selected_choice:
                    cursor = self.font.render("▶", True, COLORS["accent"])
                    surface.blit(cursor, (choice_x + 8, choice_y + 16 + i * 40))
