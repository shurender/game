"""World progression state manager."""
from typing import Dict, Any

class WorldProgressManager:
    """Manages global flags and story progression state."""
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        self._flags: Dict[str, Any] = {}
        
    def set_flag(self, key: str, value: Any) -> None:
        self._flags[key] = value
        
    def get_flag(self, key: str, default: Any = None) -> Any:
        return self._flags.get(key, default)
        
    def has_flag(self, key: str) -> bool:
        return key in self._flags
        
    def clear_flag(self, key: str) -> None:
        if key in self._flags:
            del self._flags[key]
            
    def clear(self) -> None:
        """Clear all progression flags."""
        self._flags.clear()
            
    def check_conditions(self, conditions: dict) -> bool:
        """
        Check if all conditions in the dictionary are met.
        Supports standard flags, quest statuses, and trainer defeats.
        Example conditions dict:
        {
            "flags": {"spoke_to_mom": True, "beat_game": False},
            "quests": {"main_01": "COMPLETED"},
            "trainers_defeated": ["trainer_rival"]
        }
        """
        if not conditions:
            return True
            
        # Check standard flags
        for key, value in conditions.get("flags", {}).items():
            if self.get_flag(key) != value:
                return False
                
        # Check quests
        quests = conditions.get("quests", {})
        if quests:
            from game.quests.quest_manager import QuestManager
            qm = QuestManager.get_instance()
            for q_id, status_str in quests.items():
                q = qm.get_quest(q_id)
                if not q or q.status.name != status_str:
                    return False
                    
        # Check defeated trainers
        trainers = conditions.get("trainers_defeated", [])
        if trainers:
            # We can use a generic flag prefix for trainers
            for t_id in trainers:
                if not self.get_flag(f"defeated_{t_id}", False):
                    return False
                    
        return True

    def to_dict(self) -> dict:
        return {"flags": self._flags.copy()}
        
    def load_dict(self, data: dict) -> None:
        self._flags = data.get("flags", {})
