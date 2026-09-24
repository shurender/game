"""Manages loading and querying dialogue data."""
from game.utils.data_loader import load_json_file

class DialogueManager:
    """Loads and caches dialogue data from JSON."""
    
    def __init__(self):
        self._data = load_json_file("dialogues.json").get("dialogues", {})
        
    def get_dialogue(self, dialogue_id: str) -> dict | None:
        """Return the dialogue tree for a given ID."""
        return self._data.get(dialogue_id)
        
    def get_node(self, dialogue_id: str, node_id: str) -> dict | None:
        """Return a specific node within a dialogue."""
        dialogue = self.get_dialogue(dialogue_id)
        if dialogue:
            return dialogue.get(node_id)
        return None
