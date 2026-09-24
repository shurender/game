"""Quest objectives and extensible condition checking."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class Objective:
    id: str
    obj_type: str
    description: str
    target: Any
    current_progress: int = 0
    required_progress: int = 1
    
    @property
    def is_complete(self) -> bool:
        return self.current_progress >= self.required_progress

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "current_progress": self.current_progress
        }

    def load_dict(self, data: dict) -> None:
        self.current_progress = data.get("current_progress", 0)

# Extensible registry for objective event handlers
# Signature: check(objective: Objective, event_data: dict) -> bool
ObjectiveHandler = Callable[[Objective, dict], bool]

_OBJECTIVE_HANDLERS: dict[str, ObjectiveHandler] = {}

def register_objective_type(obj_type: str, handler: ObjectiveHandler):
    _OBJECTIVE_HANDLERS[obj_type] = handler

def process_objective(objective: Objective, event_type: str, event_data: dict) -> bool:
    """Returns True if the objective made progress."""
    if objective.is_complete:
        return False
        
    handler = _OBJECTIVE_HANDLERS.get(objective.obj_type)
    if handler:
        if handler(objective, event_data):
            objective.current_progress += 1
            return True
    return False

# ── Built-in Objective Handlers ───────────────────────────────────────────────

def _handle_talk_npc(obj: Objective, event: dict) -> bool:
    if event.get("type") == "talk_npc" and event.get("npc_id") == obj.target:
        return True
    return False

def _handle_defeat_creature(obj: Objective, event: dict) -> bool:
    if event.get("type") == "defeat_creature" and event.get("species_id") == obj.target:
        return True
    return False

def _handle_defeat_trainer(obj: Objective, event: dict) -> bool:
    if event.get("type") == "defeat_trainer" and event.get("trainer_id") == obj.target:
        return True
    return False

def _handle_collect_item(obj: Objective, event: dict) -> bool:
    if event.get("type") == "collect_item" and event.get("item_id") == obj.target:
        return True
    return False

def _handle_reach_location(obj: Objective, event: dict) -> bool:
    if event.get("type") == "reach_location" and event.get("map_id") == obj.target:
        return True
    return False

def _handle_capture_creature(obj: Objective, event: dict) -> bool:
    if event.get("type") == "capture_creature" and event.get("species_id") == obj.target:
        return True
    return False

register_objective_type("talk_npc", _handle_talk_npc)
register_objective_type("defeat_creature", _handle_defeat_creature)
register_objective_type("defeat_trainer", _handle_defeat_trainer)
register_objective_type("collect_item", _handle_collect_item)
register_objective_type("reach_location", _handle_reach_location)
register_objective_type("capture_creature", _handle_capture_creature)

def create_objective_from_data(data: dict) -> Objective:
    obj_type = data["type"]
    target = None
    
    # Extract target based on type
    if obj_type == "talk_npc":
        target = data.get("npc_id")
    elif obj_type == "defeat_creature" or obj_type == "capture_creature":
        target = data.get("species_id")
    elif obj_type == "defeat_trainer":
        target = data.get("trainer_id")
    elif obj_type == "collect_item":
        target = data.get("item_id")
    elif obj_type == "reach_location":
        target = data.get("map_id")
        
    return Objective(
        id=data["id"],
        obj_type=obj_type,
        description=data["description"],
        target=target,
        required_progress=data.get("required", 1)
    )
