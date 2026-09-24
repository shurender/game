from typing import TypedDict, Any, List, Optional
from dataclasses import dataclass, asdict

class PositionData(TypedDict):
    x: int
    y: int
    facing: str
    map_id: str

class SaveData(TypedDict):
    version: int
    player_name: str
    position: PositionData
    party: dict
    inventory: dict
    wallet: dict
    quests: dict
    progress: dict
    settings: dict

def migrate_save(data: dict) -> SaveData:
    """Migrate an older save format to the current version if necessary."""
    current_version = 1
    
    if "version" not in data:
        data["version"] = 1
        
    version = data["version"]
    
    # Future migrations would go here
    # if version == 1:
    #     ... migrate to v2 ...
    #     version = 2
        
    return data # type: ignore
