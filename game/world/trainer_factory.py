"""Factory for loading trainer data from JSON."""
from game.utils.data_loader import load_json_file
from game.creatures.creature_factory import CreatureFactory

class TrainerFactory:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        data = load_json_file("trainers.json")
        self._trainers = data.get("trainers", {})
        
    def get_trainer_data(self, trainer_id: str) -> dict | None:
        return self._trainers.get(trainer_id)
        
    def create_party(self, trainer_id: str) -> list:
        """Create a list of Creature instances for this trainer's party."""
        data = self.get_trainer_data(trainer_id)
        if not data:
            return []
            
        cf = CreatureFactory.get_instance()
        party = []
        for entry in data.get("party", []):
            species_id = entry.get("id") or entry.get("species_id") or entry.get("creature")
            level = entry.get("level", 5)
            if species_id:
                c = cf.create_creature(species_id, level)
                party.append(c)
        return party
