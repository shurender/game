"""Abstract base class for game states."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pygame
    from game.core.game import Game


class State(ABC):
    """Base class for all game states.

    Each state represents a distinct mode of the game (menu, world, battle, etc.).
    States are managed by the StateMachine and receive lifecycle callbacks.
    """

    def __init__(self, game: Game) -> None:
        self.game = game

    def enter(self, params: dict[str, Any] | None = None) -> None:
        """Called when the state becomes the active state."""

    def exit(self) -> None:
        """Called when the state is removed from the stack."""

    def pause(self) -> None:
        """Called when another state is pushed on top of this one."""

    def resume(self) -> None:
        """Called when the state above this one is popped."""

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Process a single Pygame event."""
        ...

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update state logic. dt is seconds since last frame."""
        ...

    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """Draw the state to the given surface."""
        ...
