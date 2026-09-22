"""Type system and effectiveness calculations."""
from game.utils.data_loader import load_json_file

class TypeSystem:
    """Manages creature elemental types and matchup calculations."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        data = load_json_file("types.json")
        self.types = data.get("types", [])
        self.matchups = data.get("matchups", {})
        
    def get_effectiveness(self, attack_type: str, defense_types: list[str]) -> float:
        """Calculate damage multiplier for an attack against defending types."""
        if attack_type not in self.matchups:
            return 1.0
            
        multiplier = 1.0
        attack_matchups = self.matchups[attack_type]
        
        for def_type in defense_types:
            if def_type in attack_matchups:
                multiplier *= attack_matchups[def_type]
                
        return multiplier
