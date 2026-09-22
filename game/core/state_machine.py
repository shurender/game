"""Stack-based state machine for managing game states."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pygame

from game.states.base_state import State


class StateMachine:
    """A stack-based state machine.

    The topmost state receives events, updates, and draw calls.
    Push adds a state on top (pausing the current one).
    Pop removes the topmost state (resuming the one below).
    Replace swaps the topmost state.
    """

    def __init__(self) -> None:
        self._states: list[State] = []

    @property
    def current(self) -> State | None:
        """Return the current (topmost) state, or None if the stack is empty."""
        return self._states[-1] if self._states else None

    @property
    def is_empty(self) -> bool:
        """Return True if there are no states on the stack."""
        return len(self._states) == 0

    def push(self, state: State, params: dict[str, Any] | None = None) -> None:
        """Push a new state onto the stack, pausing the current one."""
        if self._states:
            self._states[-1].pause()
        self._states.append(state)
        state.enter(params)

    def pop(self) -> State | None:
        """Pop the topmost state and resume the one below."""
        if not self._states:
            return None
        state = self._states.pop()
        state.exit()
        if self._states:
            self._states[-1].resume()
        return state

    def replace(self, state: State, params: dict[str, Any] | None = None) -> None:
        """Replace the topmost state with a new one."""
        if self._states:
            self._states[-1].exit()
            self._states.pop()
        self._states.append(state)
        state.enter(params)

    def clear(self) -> None:
        """Remove all states from the stack, calling exit on each."""
        while self._states:
            self._states.pop().exit()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Forward an event to the current state."""
        if self.current:
            self.current.handle_event(event)

    def update(self, dt: float) -> None:
        """Update the current state."""
        if self.current:
            self.current.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        """Draw all states from bottom to top."""
        for state in self._stack:
            state.render(surface)
