"""Input handling — maps raw Pygame key events to game actions."""
from __future__ import annotations

import pygame
from enum import Enum, auto


class Action(Enum):
    """Logical game actions triggered by input."""
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    CONFIRM = auto()
    CANCEL = auto()
    MENU = auto()
    START = auto()
    QUEST = auto()
    SAVE = auto()


# Default keyboard bindings
DEFAULT_BINDINGS: dict[int, Action] = {
    pygame.K_UP: Action.UP,
    pygame.K_w: Action.UP,
    pygame.K_DOWN: Action.DOWN,
    pygame.K_s: Action.DOWN,
    pygame.K_LEFT: Action.LEFT,
    pygame.K_a: Action.LEFT,
    pygame.K_RIGHT: Action.RIGHT,
    pygame.K_d: Action.RIGHT,
    pygame.K_RETURN: Action.CONFIRM,
    pygame.K_z: Action.CONFIRM,
    pygame.K_SPACE: Action.CONFIRM,
    pygame.K_e: Action.CONFIRM,
    pygame.K_ESCAPE: Action.CANCEL,
    pygame.K_x: Action.CANCEL,
    pygame.K_TAB: Action.MENU,
    pygame.K_p: Action.START,
    pygame.K_q: Action.QUEST,
    pygame.K_F5: Action.SAVE,
}


class InputHandler:
    """Translates raw keyboard input into game actions.

    Tracks held, just-pressed, and just-released actions per frame.
    Call ``begin_frame()`` at the start of each frame to reset per-frame state.
    """

    def __init__(self, bindings: dict[int, Action] | None = None) -> None:
        self._bindings = bindings or DEFAULT_BINDINGS.copy()
        self._pressed: set[Action] = set()
        self._just_pressed: set[Action] = set()
        self._just_released: set[Action] = set()

    @property
    def bindings(self) -> dict[int, Action]:
        """Return the current key bindings."""
        return self._bindings

    def begin_frame(self) -> None:
        """Clear per-frame state. Call at the start of each frame."""
        self._just_pressed.clear()
        self._just_released.clear()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Process a single Pygame key or mouse event."""
        if event.type == pygame.KEYDOWN:
            action = self._bindings.get(event.key)
            if action and action not in self._pressed:
                self._pressed.add(action)
                self._just_pressed.add(action)
        elif event.type == pygame.KEYUP:
            action = self._bindings.get(event.key)
            if action and action in self._pressed:
                self._pressed.discard(action)
                self._just_released.add(action)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if Action.CONFIRM not in self._pressed:
                self._pressed.add(Action.CONFIRM)
                self._just_pressed.add(Action.CONFIRM)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if Action.CONFIRM in self._pressed:
                self._pressed.discard(Action.CONFIRM)
                self._just_released.add(Action.CONFIRM)

    def is_pressed(self, action: Action) -> bool:
        """Return True if the action key is currently held down."""
        return action in self._pressed

    def is_just_pressed(self, action: Action) -> bool:
        """Return True if the action key was pressed this frame."""
        return action in self._just_pressed

    def is_just_released(self, action: Action) -> bool:
        """Return True if the action key was released this frame."""
        return action in self._just_released

    def set_binding(self, key: int, action: Action) -> None:
        """Change a key binding."""
        self._bindings[key] = action
