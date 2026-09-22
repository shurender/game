"""Tests for the StateMachine."""
import pytest

from game.states.base_state import State
from game.core.state_machine import StateMachine


class MockState(State):
    """A lightweight mock state for unit testing."""

    def __init__(self, name: str = "mock") -> None:
        # Skip State.__init__ — no Game object needed for pure logic tests
        self.game = None  # type: ignore[assignment]
        self.name = name
        self.entered = False
        self.exited = False
        self.paused = False
        self.resumed = False
        self.enter_params = None

    def enter(self, params=None):
        self.entered = True
        self.enter_params = params

    def exit(self):
        self.exited = True

    def pause(self):
        self.paused = True

    def resume(self):
        self.resumed = True

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def render(self, surface):
        pass


class TestStateMachine:
    """Test suite for StateMachine push / pop / replace / clear."""

    def test_starts_empty(self):
        sm = StateMachine()
        assert sm.is_empty
        assert sm.current is None

    def test_push(self):
        sm = StateMachine()
        state = MockState()
        sm.push(state)
        assert sm.current is state
        assert state.entered
        assert not sm.is_empty

    def test_push_with_params(self):
        sm = StateMachine()
        state = MockState()
        sm.push(state, {"key": "value"})
        assert state.enter_params == {"key": "value"}

    def test_push_pauses_previous(self):
        sm = StateMachine()
        first = MockState("first")
        second = MockState("second")
        sm.push(first)
        sm.push(second)
        assert first.paused
        assert sm.current is second

    def test_pop(self):
        sm = StateMachine()
        state = MockState()
        sm.push(state)
        popped = sm.pop()
        assert popped is state
        assert state.exited
        assert sm.is_empty

    def test_pop_resumes_previous(self):
        sm = StateMachine()
        first = MockState("first")
        second = MockState("second")
        sm.push(first)
        sm.push(second)
        sm.pop()
        assert first.resumed
        assert sm.current is first

    def test_pop_empty_returns_none(self):
        sm = StateMachine()
        assert sm.pop() is None

    def test_replace(self):
        sm = StateMachine()
        first = MockState("first")
        second = MockState("second")
        sm.push(first)
        sm.replace(second)
        assert first.exited
        assert second.entered
        assert sm.current is second

    def test_replace_on_empty(self):
        sm = StateMachine()
        state = MockState()
        sm.replace(state)
        assert sm.current is state
        assert state.entered

    def test_clear(self):
        sm = StateMachine()
        states = [MockState(f"s{i}") for i in range(3)]
        for s in states:
            sm.push(s)
        sm.clear()
        assert sm.is_empty
        for s in states:
            assert s.exited

    def test_stack_ordering(self):
        sm = StateMachine()
        s1 = MockState("s1")
        s2 = MockState("s2")
        s3 = MockState("s3")
        sm.push(s1)
        sm.push(s2)
        sm.push(s3)
        assert sm.current is s3
        sm.pop()
        assert sm.current is s2
        sm.pop()
        assert sm.current is s1
