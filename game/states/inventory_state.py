"""Placeholder for the inventory state."""
import pygame
from game.states.base_state import State

class InventoryState(State):
    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((50, 100, 50))
