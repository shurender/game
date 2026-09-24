"""Tests for quest system logic — no Pygame, no UI."""
import pytest
from unittest.mock import patch

from game.quests.objective import Objective, process_objective
from game.quests.quest import Quest, QuestStatus, Reward
from game.quests.quest_manager import QuestManager
from game.inventory.inventory import Inventory
from game.player.wallet import Wallet

MOCK_QUESTS = {
    "quests": {
        "q1": {
            "name": "Talk to Mom",
            "type": "main",
            "description": "Say hi.",
            "objectives": [
                {
                    "id": "o1",
                    "type": "talk_npc",
                    "npc_id": "npc_mom",
                    "description": "Talk to Mom"
                }
            ],
            "rewards": [
                {"type": "coins", "amount": 100}
            ]
        },
        "q2": {
            "name": "Defeat creature",
            "type": "side",
            "description": "Defeat C1.",
            "objectives": [
                {
                    "id": "o2",
                    "type": "defeat_creature",
                    "species_id": "C1",
                    "description": "Defeat C1",
                    "required": 2
                }
            ]
        }
    }
}

@pytest.fixture(autouse=True)
def reset_singletons():
    QuestManager._instance = None
    Inventory._instance = None
    Wallet._instance = None
    with patch("game.quests.quest_manager.load_json_file", return_value=MOCK_QUESTS):
        yield
    QuestManager._instance = None
    Inventory._instance = None
    Wallet._instance = None
    
def test_quest_loading():
    qm = QuestManager.get_instance()
    q1 = qm.get_quest("q1")
    assert q1 is not None
    assert q1.name == "Talk to Mom"
    assert len(q1.objectives) == 1
    assert q1.status == QuestStatus.NOT_STARTED

def test_quest_progress_and_completion():
    qm = QuestManager.get_instance()
    qm.start_quest("q1")
    
    assert len(qm.get_active_quests()) == 1
    
    # Send incorrect event
    qm.on_event("talk_npc", {"npc_id": "npc_dad"})
    q1 = qm.get_quest("q1")
    assert q1.status == QuestStatus.IN_PROGRESS
    
    # Send correct event
    msgs = qm.on_event("talk_npc", {"npc_id": "npc_mom"})
    assert q1.status == QuestStatus.COMPLETED
    assert len(qm.get_active_quests()) == 0
    assert len(qm.get_completed_quests()) == 1
    
    assert "Completed Quest: Talk to Mom!" in msgs
    assert "Received 100 coins" in msgs
    
    w = Wallet.get_instance()
    assert w.coins == 3100 # base 3000 + 100

def test_multiple_required_progress():
    qm = QuestManager.get_instance()
    qm.start_quest("q2")
    q2 = qm.get_quest("q2")
    
    qm.on_event("defeat_creature", {"species_id": "C1"})
    assert q2.status == QuestStatus.IN_PROGRESS
    assert q2.objectives[0].current_progress == 1
    
    qm.on_event("defeat_creature", {"species_id": "C1"})
    assert q2.status == QuestStatus.COMPLETED
    assert q2.objectives[0].current_progress == 2
