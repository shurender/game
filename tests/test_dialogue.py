"""Tests for the dialogue manager."""
import pytest
from unittest.mock import patch

from game.ui.dialogue_manager import DialogueManager

MOCK_DIALOGUES = {
    "dialogues": {
        "test_intro": {
            "start": {
                "speaker": "Test",
                "text": "Hello world!",
                "next": "end"
            },
            "end": {
                "speaker": "Test",
                "text": "Goodbye!"
            }
        }
    }
}

@pytest.fixture
def mock_load_json():
    with patch("game.ui.dialogue_manager.load_json_file", return_value=MOCK_DIALOGUES):
        yield

def test_dialogue_manager_get_dialogue(mock_load_json):
    manager = DialogueManager()
    dialogue = manager.get_dialogue("test_intro")
    assert dialogue is not None
    assert "start" in dialogue
    
def test_dialogue_manager_get_node(mock_load_json):
    manager = DialogueManager()
    node = manager.get_node("test_intro", "start")
    assert node is not None
    assert node["speaker"] == "Test"
    assert node["text"] == "Hello world!"
    assert node["next"] == "end"
    
def test_dialogue_manager_missing(mock_load_json):
    manager = DialogueManager()
    assert manager.get_dialogue("missing") is None
    assert manager.get_node("test_intro", "missing_node") is None
