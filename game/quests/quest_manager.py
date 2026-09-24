"""Singleton manager for quest progression."""
from __future__ import annotations
import logging
from typing import Dict, List, Optional
from game.utils.data_loader import load_json_file
from game.quests.quest import Quest, QuestStatus, create_quest_from_data
from game.quests.objective import process_objective
from game.inventory.inventory import Inventory
from game.player.wallet import Wallet

logger = logging.getLogger("risu")

class QuestManager:
    """Singleton tracking all quests and progression."""
    _instance = None
    
    @classmethod
    def get_instance(cls) -> QuestManager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        self._quests: Dict[str, Quest] = {}
        self._load_quest_definitions()
        
    def _load_quest_definitions(self) -> None:
        data = load_json_file("quests.json")
        for q_id, q_data in data.get("quests", {}).items():
            self._quests[q_id] = create_quest_from_data(q_id, q_data)
            
    def get_quest(self, quest_id: str) -> Optional[Quest]:
        return self._quests.get(quest_id)
        
    def start_quest(self, quest_id: str) -> None:
        q = self.get_quest(quest_id)
        if q and q.status == QuestStatus.NOT_STARTED:
            q.status = QuestStatus.IN_PROGRESS
            logger.info(f"Started quest: {q.name}")
            
    def get_active_quests(self) -> List[Quest]:
        return [q for q in self._quests.values() if q.status == QuestStatus.IN_PROGRESS]
        
    def get_completed_quests(self) -> List[Quest]:
        return [q for q in self._quests.values() if q.status == QuestStatus.COMPLETED]
        
    def on_event(self, event_type: str, event_data: dict) -> List[str]:
        """Dispatch an event to all active quests. Returns list of completion messages."""
        messages = []
        event_data = dict(event_data)
        event_data["type"] = event_type
        
        for q in self.get_active_quests():
            made_progress = False
            for obj in q.objectives:
                if process_objective(obj, event_type, event_data):
                    made_progress = True
                    
            if made_progress and q.is_complete:
                q.status = QuestStatus.COMPLETED
                messages.append(f"Completed Quest: {q.name}!")
                
                # Grant rewards
                inv = Inventory.get_instance()
                wallet = Wallet.get_instance()
                for reward in q.rewards:
                    msg = reward.grant(inv, wallet)
                    if msg:
                        messages.append(msg)
                        
        return messages

    def to_dict(self) -> dict:
        return {
            "quests": [q.to_dict() for q in self._quests.values()]
        }

    def load_dict(self, data: dict) -> None:
        saved_quests = data.get("quests", [])
        for saved_q in saved_quests:
            q_id = saved_q.get("id")
            q = self.get_quest(q_id)
            if q:
                q.load_dict(saved_q)
