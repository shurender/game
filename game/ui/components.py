import pygame
from config import COLORS

def draw_hp_bar(surface: pygame.Surface, x: int, y: int, width: int, height: int, current_hp: float, max_hp: float) -> None:
    """Draw a standard HP bar with dynamic color based on ratio."""
    # Background
    bg_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (50, 50, 50), bg_rect)
    pygame.draw.rect(surface, COLORS["menu_border"], bg_rect, 2)
    
    # Foreground
    hp_ratio = max(0.0, current_hp / max_hp)
    hp_w = int((width - 4) * hp_ratio)
    
    if hp_ratio > 0:
        hp_color = COLORS.get("hp_green", (80, 220, 100))
        if hp_ratio <= 0.2:
            hp_color = COLORS.get("hp_red", (220, 60, 60))
        elif hp_ratio <= 0.5:
            hp_color = COLORS.get("hp_yellow", (220, 200, 60))
            
        fg_rect = pygame.Rect(x + 2, y + 2, hp_w, height - 4)
        pygame.draw.rect(surface, hp_color, fg_rect)
