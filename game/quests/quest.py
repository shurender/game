"""Quest domain model and reward definition."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum
from game.quests.objective import Objective, create_objective_from_data

class QuestStatus(Enum):
    NOT_STARTED = 0
    IN_PROGRESS = 1
    COMPLETED = 2

@dataclass
class Reward:
    reward_type: str # "item", "coins", "xp"
    item_id: str = None
    amount: int = 0
    quantity: int = 1

    def grant(self, inventory: Any, wallet: Any) -> str:
        if self.reward_type == "item":
            inventory.add(self.item_id, self.quantity)
            return f"Received {self.quantity}x {self.item_id}"
        elif self.reward_type == "coins":
            wallet.coins += self.amount
            return f"Received {self.amount} coins"
        return ""

@dataclass
class Quest:
    id: str
    name: str
    quest_type: str # "main" or "side"
    description: str
    objectives: List[Objective] = field(default_factory=list)
    rewards: List[Reward] = field(default_factory=list)
    status: QuestStatus = QuestStatus.NOT_STARTED

    @property
    def is_complete(self) -> bool:
        return all(obj.is_complete for obj in self.objectives)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "status": self.status.name,
            "objectives": [obj.to_dict() for obj in self.objectives]
        }

    def load_dict(self, data: dict) -> None:
        if "status" in data:
            self.status = QuestStatus[data["status"]]
            
        obj_data_map = {obj_dict["id"]: obj_dict for obj_dict in data.get("objectives", [])}
        for obj in self.objectives:
            if obj.id in obj_data_map:
                obj.load_dict(obj_data_map[obj.id])

def create_quest_from_data(quest_id: str, data: dict) -> Quest:
    q = Quest(
        id=quest_id,
        name=data["name"],
        quest_type=data.get("type", "side"),
        description=data["description"]
    )
    
    for obj_data in data.get("objectives", []):
        q.objectives.append(create_objective_from_data(obj_data))
        
    for rew_data in data.get("rewards", []):
        r = Reward(
            reward_type=rew_data["type"],
            item_id=rew_data.get("item_id"),
            amount=rew_data.get("amount", 0),
            quantity=rew_data.get("quantity", 1)
        )
        q.rewards.append(r)
        
    return q
