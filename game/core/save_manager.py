import os
import json
import logging
from typing import Optional
from game.core.save_data import SaveData, migrate_save
from game.player.party import PartyManager
from game.inventory.inventory import Inventory
from game.player.wallet import Wallet
from game.quests.quest_manager import QuestManager
from game.world.progress_manager import WorldProgressManager

logger = logging.getLogger("risu")

class SaveManager:
    """Manages saving and loading game data."""
    
    SAVE_DIR = "saves"
    CURRENT_VERSION = 1
    
    def __init__(self, game):
        self.game = game
        if not os.path.exists(self.SAVE_DIR):
            os.makedirs(self.SAVE_DIR)
            
    def _get_save_path(self, slot: int) -> str:
        return os.path.join(self.SAVE_DIR, f"save_{slot}.json")
        
    def get_world_state(self):
        """Find the WorldState in the state machine stack."""
        from game.states.world_state import WorldState
        for state in reversed(self.game.state_machine._states):
            if isinstance(state, WorldState):
                return state
        return None
        
    def save(self, slot: int = 0) -> bool:
        """Save the current game state to a slot."""
        world_state = self.get_world_state()
        if not world_state:
            logger.error("Cannot save: No active world state found.")
            return False
            
        player_name = getattr(world_state.player, "name", "Player") if world_state.player else "Player"
        data: SaveData = {
            "version": self.CURRENT_VERSION,
            "player_name": player_name,
            "position": {
                "x": world_state.player.x,
                "y": world_state.player.y,
                "facing": world_state.player.facing.name,
                "map_id": world_state.world.current_map.map_id if world_state.world.current_map else "test_town"
            },
            "party": PartyManager.get_instance().to_dict(),
            "inventory": Inventory.get_instance().to_dict(),
            "wallet": Wallet.get_instance().to_dict(),
            "quests": QuestManager.get_instance().to_dict(),
            "progress": WorldProgressManager.get_instance().to_dict(),
            "settings": {} # Placeholder for future settings
        }
        
        path = self._get_save_path(slot)
        temp_path = path + ".tmp"
        
        try:
            with open(temp_path, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(temp_path, path)
            logger.info(f"Game saved to slot {slot}.")
            return True
        except Exception as e:
            logger.error(f"Failed to save game: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False

    def load(self, slot: int = 0) -> bool:
        """Load a saved game from a slot."""
        path = self._get_save_path(slot)
        if not os.path.exists(path):
            logger.error(f"Save slot {slot} does not exist.")
            return False
            
        try:
            with open(path, "r") as f:
                raw_data = json.load(f)
                
            data = migrate_save(raw_data)
            
            # Load Singletons
            PartyManager.get_instance().load_dict(data.get("party", {}))
            Inventory.get_instance().load_dict(data.get("inventory", {}))
            Wallet.get_instance().load_dict(data.get("wallet", {}))
            QuestManager.get_instance().load_dict(data.get("quests", {}))
            WorldProgressManager.get_instance().load_dict(data.get("progress", {}))
            
            # Restart world state with saved position
            pos = data.get("position", {})
            from game.states.world_state import WorldState
            new_world = WorldState(self.game)
            if hasattr(new_world.player, "name"):
                new_world.player.name = data.get("player_name", "Player")
            self.game.state_machine.clear()
            self.game.state_machine.push(new_world, {
                "map_id": pos.get("map_id", "test_town"),
                "x": pos.get("x", 10),
                "y": pos.get("y", 10),
                "facing": pos.get("facing", "DOWN")
            })
            
            logger.info(f"Game loaded from slot {slot}.")
            return True
        except Exception as e:
            logger.error(f"Failed to load game: {e}")
            return False
            
    def get_save_info(self, slot: int) -> Optional[dict]:
        """Read basic info from a save file without fully loading it."""
        path = self._get_save_path(slot)
        if not os.path.exists(path):
            return None
            
        try:
            with open(path, "r") as f:
                raw_data = json.load(f)
            return {
                "player_name": raw_data.get("player_name", "Unknown"),
                "map_id": raw_data.get("position", {}).get("map_id", "Unknown"),
                "party_size": len(raw_data.get("party", {}).get("party", []))
            }
        except Exception:
            return None
