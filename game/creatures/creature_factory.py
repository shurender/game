"""Factory for loading species data and creating creatures."""
from game.utils.data_loader import load_json_file
from game.creatures.creature import Species, Creature

class CreatureFactory:
    """Manages species data and instantiates creatures."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        data = load_json_file("creatures.json")
        creatures_data = data.get("creatures", {})
        
        self.species_db: dict[str, Species] = {}
        
        for sp_id, sp_data in creatures_data.items():
            self.species_db[sp_id] = Species(
                species_id=sp_id,
                name=sp_data["name"],
                types=sp_data["type"],
                base_stats=sp_data["base_stats"],
                description=sp_data.get("description", "")
            )
            
    def get_species(self, species_id: str) -> Species | None:
        """Return the Species object for a given ID."""
        return self.species_db.get(species_id)
        
    def create_creature(self, species_id: str, level: int, nickname: str = None) -> Creature:
        """Create a new Creature instance of the given species and level."""
        species = self.get_species(species_id)
        if not species:
            raise ValueError(f"Unknown species ID: {species_id}")
            
        return Creature(species, level, nickname)
