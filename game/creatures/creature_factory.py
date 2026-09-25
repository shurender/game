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
        self._raw: dict = data.get("creatures", {})   # raw JSON — progression needs it

        self.species_db: dict[str, Species] = {}

        for sp_id, sp_data in self._raw.items():
            types = sp_data.get("type", sp_data.get("types", ["Normal"]))
            s = Species(
                species_id=sp_id,
                name=sp_data["name"],
                types=types,
                base_stats=sp_data.get("base_stats", {}),
                description=sp_data.get("description", ""),
            )
            # Attach optional data used by progression / capture
            s.catch_rate = sp_data.get("catch_rate", 100)
            s.xp_yield = sp_data.get("xp_yield", 50)
            s.xp_curve = sp_data.get("xp_curve", sp_data.get("growth_rate", "medium_fast"))
            s.learnset = sp_data.get("learnset", sp_data.get("level_moves", []))
            s.evolution_data = sp_data.get("evolution")   # raw dict or None
            self.species_db[sp_id] = s

    def get_species(self, species_id: str) -> Species | None:
        return self.species_db.get(species_id)

    def get_raw(self, species_id: str) -> dict | None:
        """Return the raw JSON dict for a species (used by progression engine)."""
        return self._raw.get(species_id)

    def create_creature(self, species_id: str, level: int,
                        nickname: str = None) -> Creature:
        """Create a new Creature instance and populate starting moves."""
        species = self.get_species(species_id)
        if not species:
            # Fallback to first available species if unknown
            first_id = next(iter(self.species_db.keys()), None)
            if first_id:
                species = self.species_db[first_id]
            else:
                raise ValueError(f"Unknown species ID: {species_id}")

        creature = Creature(species, level, nickname)

        # Populate moves from learnset up to starting level
        raw = self._raw.get(species.species_id, {})
        learnset = raw.get("learnset") or raw.get("level_moves") or []
        for entry in learnset:
            if entry.get("level", 1) <= level:
                move_id = entry.get("move") or entry.get("move_id")
                if move_id and move_id not in creature.moves:
                    creature.moves.append(move_id)

        # Ensure the creature has at least one move
        if not creature.moves:
            creature.moves.append("tackle")

        return creature

    def evolve_creature(self, creature: Creature, target_species_id: str) -> "EvolutionResult":
        """Trigger in-place evolution, returning an EvolutionResult for the UI."""
        from game.creatures.progression import evolve

        old_raw = self.get_raw(creature.species.species_id)
        new_species = self.get_species(target_species_id)
        new_raw = self.get_raw(target_species_id)

        if not new_species or not new_raw:
            raise ValueError(f"Unknown evolution target: {target_species_id}")

        return evolve(creature, old_raw, target_species_id, new_raw, new_species)
