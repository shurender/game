"""Move domain model and data loading."""
from dataclasses import dataclass
from typing import Optional

from game.utils.data_loader import load_json_file


@dataclass
class Move:
    """Immutable data defining a combat move."""
    move_id: str
    name: str
    type: str
    category: str  # "Physical", "Special", or "Status"
    power: int
    accuracy: int
    pp: int
    max_pp: int
    priority: int
    description: str
    status_effect: Optional[str] = None
    
    def __post_init__(self):
        # Ensure max_pp matches initial pp if not explicitly set
        if getattr(self, "max_pp", None) is None:
            self.max_pp = self.pp


class MoveFactory:
    """Manages loading and dispensing Move objects."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        data = load_json_file("moves.json")
        moves_data = data.get("moves", {})
        
        self.moves_db: dict[str, Move] = {}
        
        for m_id, m_data in moves_data.items():
            self.moves_db[m_id] = Move(
                move_id=m_id,
                name=m_data["name"],
                type=m_data["type"],
                category=m_data["category"],
                power=m_data.get("power", 0),
                accuracy=m_data.get("accuracy", 100),
                pp=m_data["pp"],
                max_pp=m_data["pp"],
                priority=m_data.get("priority", 0),
                description=m_data.get("description", ""),
                status_effect=m_data.get("status_effect")
            )
            
    def get_move(self, move_id: str) -> Move:
        """Get a copy of a move (so PP can be modified independently)."""
        base_move = self.moves_db.get(move_id)
        if not base_move:
            # Case-insensitive or normalized lookup
            target_slug = str(move_id).lower().replace(" ", "_")
            for k, m in self.moves_db.items():
                if k.lower() == target_slug or m.name.lower().replace(" ", "_") == target_slug:
                    base_move = m
                    break

        if not base_move:
            # Fallback to Tackle or first move in DB
            base_move = self.moves_db.get("tackle") or self.moves_db.get("M1") or next(iter(self.moves_db.values()), None)
            if not base_move:
                base_move = Move(
                    move_id=move_id,
                    name=str(move_id).replace("_", " ").title(),
                    type="Normal",
                    category="Physical",
                    power=40,
                    accuracy=100,
                    pp=35,
                    max_pp=35,
                    priority=0,
                    description="A basic attack."
                )

        # Return a fresh instance for the creature
        return Move(
            move_id=base_move.move_id,
            name=base_move.name,
            type=base_move.type,
            category=base_move.category,
            power=base_move.power,
            accuracy=base_move.accuracy,
            pp=base_move.pp,
            max_pp=base_move.max_pp,
            priority=base_move.priority,
            description=base_move.description,
            status_effect=base_move.status_effect
        )
