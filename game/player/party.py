"""Manages the player's active creature party and PC storage."""

from game.creatures.creature import Creature

class PartyManager:
    """Singleton managing the player's active party and storage."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        self.party: list[Creature] = []
        self.storage: list[Creature] = []
        self.max_party_size = 6
        
    def add_creature(self, creature: Creature) -> str:
        """Adds a creature to the party or storage.
        
        Returns:
            "PARTY" if added to the party.
            "STORAGE" if added to PC storage (because party is full).
        """
        if len(self.party) < self.max_party_size:
            self.party.append(creature)
            return "PARTY"
        else:
            self.storage.append(creature)
            return "STORAGE"
            
    def get_first_available(self) -> Creature | None:
        """Returns the first non-fainted creature in the party."""
        for c in self.party:
            if not c.is_fainted:
                return c
        return None

    def remove_creature(self, index: int) -> Creature | None:
        """Removes a creature from the party at the given index."""
        if 0 <= index < len(self.party):
            return self.party.pop(index)
        return None

    def swap_creatures(self, index1: int, index2: int) -> bool:
        """Swaps the positions of two creatures in the party."""
        if 0 <= index1 < len(self.party) and 0 <= index2 < len(self.party):
            self.party[index1], self.party[index2] = self.party[index2], self.party[index1]
            return True
        return False
        
    def has_usable_creatures(self) -> bool:
        """Checks if the party has any non-fainted creatures left."""
        return any(not c.is_fainted for c in self.party)

    def clear(self):
        """Clear party and storage for testing purposes."""
        self.party.clear()
        self.storage.clear()
        
    def to_dict(self) -> dict:
        return {
            "party": [c.to_dict() for c in self.party],
            "storage": [c.to_dict() for c in self.storage]
        }
        
    def load_dict(self, data: dict) -> None:
        self.clear()
        for c_data in data.get("party", []):
            try:
                self.party.append(Creature.from_dict(c_data))
            except Exception as e:
                import logging
                logging.getLogger("risu").error(f"Failed to load party creature: {e}")
                
        for c_data in data.get("storage", []):
            try:
                self.storage.append(Creature.from_dict(c_data))
            except Exception as e:
                import logging
                logging.getLogger("risu").error(f"Failed to load storage creature: {e}")
