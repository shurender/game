"""Tests for world progression logic."""
import pytest
from unittest.mock import patch

from game.world.progress_manager import WorldProgressManager
from game.quests.quest_manager import QuestManager
from game.quests.quest import QuestStatus

@pytest.fixture(autouse=True)
def reset_singletons():
    WorldProgressManager._instance = None
    QuestManager._instance = None
    
def test_flags():
    pm = WorldProgressManager.get_instance()
    
    assert pm.get_flag("met_prof") is None
    pm.set_flag("met_prof", True)
    assert pm.get_flag("met_prof") is True
    assert pm.has_flag("met_prof")
    
    pm.clear_flag("met_prof")
    assert not pm.has_flag("met_prof")

def test_check_conditions():
    pm = WorldProgressManager.get_instance()
    qm = QuestManager.get_instance()
    
    # Empty conditions pass
    assert pm.check_conditions({}) is True
    
    pm.set_flag("has_badge", True)
    pm.set_flag("defeated_trainer_gary", True)
    
    cond_true = {
        "flags": {"has_badge": True}
    }
    assert pm.check_conditions(cond_true) is True
    
    cond_false = {
        "flags": {"has_badge": False}
    }
    assert pm.check_conditions(cond_false) is False
    
    cond_multi = {
        "flags": {"has_badge": True},
        "trainers_defeated": ["trainer_gary"]
    }
    assert pm.check_conditions(cond_multi) is True
    
    cond_missing = {
        "flags": {"has_badge": True},
        "trainers_defeated": ["trainer_brock"]
    }
    assert pm.check_conditions(cond_missing) is False

def test_quest_conditions():
    pm = WorldProgressManager.get_instance()
    qm = QuestManager.get_instance()
    
    qm._quests = {}  # Mock empty quests
    from game.quests.quest import Quest
    q = Quest("main_01", "Main", "main", "desc")
    q.status = QuestStatus.COMPLETED
    qm._quests["main_01"] = q
    
    cond = {
        "quests": {"main_01": "COMPLETED"}
    }
    
    assert pm.check_conditions(cond) is True
    
    q.status = QuestStatus.IN_PROGRESS
    assert pm.check_conditions(cond) is False

