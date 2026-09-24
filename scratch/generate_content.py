import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def write_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def generate_maps():
    maps = {}
    
    # helper to make empty layers
    def make_layer(w, h, fill=0):
        return [[fill for _ in range(w)] for _ in range(h)]
        
    # --- Starting Town ---
    # A peaceful town with player's house and a lab.
    m_start = {
        "name": "Oakhaven",
        "width": 15,
        "height": 10,
        "layers": {
            "ground": [
                [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
                [2,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
                [2,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
                [2,1,1,3,3,1,1,1,1,1,3,3,1,1,2],
                [2,1,1,4,3,1,1,1,1,1,4,3,1,1,2],
                [2,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
                [2,1,1,1,1,1,1,3,3,3,1,1,1,1,2],
                [2,1,1,1,1,1,1,3,3,3,1,1,1,1,2],
                [2,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
                [2,2,2,2,2,2,2,1,1,2,2,2,2,2,2]
            ],
            "collision": [
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,1,1,0,0,0,0,0,1,1,0,0,1],
                [1,0,0,0,1,0,0,0,0,0,0,1,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,1,1,1,1,1,1,0,0,1,1,1,1,1,1]
            ],
            "encounter": make_layer(15, 10)
        },
        "warps": [
            {"x": 7, "y": 9, "target_map": "route_1", "target_x": 7, "target_y": 1},
            {"x": 8, "y": 9, "target_map": "route_1", "target_x": 8, "target_y": 1},
            {"x": 3, "y": 4, "target_map": "player_house", "target_x": 4, "target_y": 6},
            {"x": 10, "y": 4, "target_map": "prof_lab", "target_x": 4, "target_y": 6}
        ],
        "npcs": [
            {
                "id": "npc_mom", "name": "Mom", "x": 4, "y": 8, "sprite": "npc_f_1", "facing": "up",
                "dialogue_id": "mom_intro"
            }
        ]
    }
    maps["starting_town"] = m_start

    # --- Player House ---
    maps["player_house"] = {
        "name": "Player's House",
        "width": 10, "height": 8,
        "layers": {
            "ground": [
                [10,10,10,10,10,10,10,10,10,10],
                [10,11,11,11,11,11,11,11,11,10],
                [10,11,11,11,11,11,11,11,11,10],
                [10,11,11,11,11,11,11,11,11,10],
                [10,11,11,11,11,11,11,11,11,10],
                [10,11,11,11,11,11,11,11,11,10],
                [10,11,11,11,12,11,11,11,11,10],
                [10,10,10,10,10,10,10,10,10,10]
            ],
            "collision": [
                [1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,1],
                [1,1,1,1,1,1,1,1,1,1]
            ],
            "encounter": make_layer(10, 8)
        },
        "warps": [
            {"x": 4, "y": 7, "target_map": "starting_town", "target_x": 3, "target_y": 5}
        ],
        "npcs": []
    }

    # --- Prof Lab ---
    maps["prof_lab"] = {
        "name": "Professor's Lab",
        "width": 10, "height": 8,
        "layers": {
            "ground": [
                [10,10,10,10,10,10,10,10,10,10],
                [10,11,11,11,11,11,11,11,11,10],
                [10,11,11,11,11,11,11,11,11,10],
                [10,11,11,11,11,11,11,11,11,10],
                [10,11,11,11,11,11,11,11,11,10],
                [10,11,11,11,11,11,11,11,11,10],
                [10,11,11,11,12,11,11,11,11,10],
                [10,10,10,10,10,10,10,10,10,10]
            ],
            "collision": [
                [1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,1],
                [1,1,1,1,1,1,1,1,1,1]
            ],
            "encounter": make_layer(10, 8)
        },
        "warps": [
            {"x": 4, "y": 7, "target_map": "starting_town", "target_x": 10, "target_y": 5}
        ],
        "npcs": [
            {
                "id": "npc_prof", "name": "Prof. Cedar", "x": 4, "y": 3, "sprite": "npc_m_1", "facing": "down",
                "dialogue_id": "prof_intro"
            }
        ]
    }

    # --- Route 1 ---
    route_1_encounter = make_layer(15, 15)
    for x in range(2, 13):
        for y in range(4, 11):
            route_1_encounter[y][x] = 1 # encounters in grass
    
    maps["route_1"] = {
        "name": "Route 1",
        "width": 15, "height": 15,
        "layers": {
            "ground": [
                [2,2,2,2,2,2,2,1,1,2,2,2,2,2,2],
                [2,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
                [2,1,3,3,3,1,1,1,1,1,3,3,3,1,2],
                [2,1,3,1,3,1,1,1,1,1,3,1,3,1,2],
                [2,1,6,6,6,1,1,1,1,1,6,6,6,1,2],
                [2,1,6,6,6,1,1,1,1,1,6,6,6,1,2],
                [2,1,6,6,6,2,2,2,2,2,6,6,6,1,2],
                [2,1,6,6,6,2,1,1,1,2,6,6,6,1,2],
                [2,1,6,6,6,2,1,1,1,2,6,6,6,1,2],
                [2,1,6,6,6,1,1,1,1,1,6,6,6,1,2],
                [2,1,6,6,6,1,1,1,1,1,6,6,6,1,2],
                [2,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
                [2,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
                [2,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
                [2,2,2,2,2,2,2,1,1,2,2,2,2,2,2]
            ],
            "collision": [
                [1,1,1,1,1,1,1,0,0,1,1,1,1,1,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,1,1,1,1,1,0,0,0,0,1],
                [1,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
                [1,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,1,1,1,1,1,1,0,0,1,1,1,1,1,1]
            ],
            "encounter": route_1_encounter
        },
        "warps": [
            {"x": 7, "y": 0, "target_map": "starting_town", "target_x": 7, "target_y": 8},
            {"x": 8, "y": 0, "target_map": "starting_town", "target_x": 8, "target_y": 8},
            {"x": 7, "y": 14, "target_map": "forest_1", "target_x": 7, "target_y": 1},
            {"x": 8, "y": 14, "target_map": "forest_1", "target_x": 8, "target_y": 1}
        ],
        "npcs": [
            {
                "id": "trainer_youngster_1", "name": "Youngster Joey", "x": 10, "y": 11, "sprite": "npc_m_1", "facing": "left",
                "dialogue_id": "", "trainer_id": "trainer_youngster_1"
            },
            {
                "id": "trainer_lass_1", "name": "Lass Mia", "x": 4, "y": 4, "sprite": "npc_f_1", "facing": "right",
                "dialogue_id": "", "trainer_id": "trainer_lass_1"
            }
        ],
        "encounter_table": [
            {"creature": "florbit", "level_min": 2, "level_max": 4, "weight": 50},
            {"creature": "flapjay", "level_min": 2, "level_max": 4, "weight": 50}
        ]
    }

    # --- Forest 1 ---
    # Trees everywhere, winding path
    forest_ground = make_layer(15, 15, 2)
    forest_coll = make_layer(15, 15, 1)
    forest_enc = make_layer(15, 15, 0)
    
    # Path
    for y in range(1, 14):
        forest_ground[y][7] = 6
        forest_ground[y][8] = 6
        forest_coll[y][7] = 0
        forest_coll[y][8] = 0
        forest_enc[y][7] = 1
        forest_enc[y][8] = 1
    
    # Detour
    for x in range(3, 8):
        forest_ground[5][x] = 6
        forest_coll[5][x] = 0
        forest_enc[5][x] = 1
        forest_ground[6][x] = 6
        forest_coll[6][x] = 0
        forest_enc[6][x] = 1

    maps["forest_1"] = {
        "name": "Whispering Woods",
        "width": 15, "height": 15,
        "layers": {
            "ground": forest_ground,
            "collision": forest_coll,
            "encounter": forest_enc
        },
        "warps": [
            {"x": 7, "y": 0, "target_map": "route_1", "target_x": 7, "target_y": 13},
            {"x": 8, "y": 0, "target_map": "route_1", "target_x": 8, "target_y": 13},
            {"x": 7, "y": 14, "target_map": "second_town", "target_x": 7, "target_y": 1},
            {"x": 8, "y": 14, "target_map": "second_town", "target_x": 8, "target_y": 1},
            # Cave entrance to the left
            {"x": 3, "y": 5, "target_map": "cave_1", "target_x": 13, "target_y": 5}
        ],
        "npcs": [
            {
                "id": "trainer_bug_catcher_1", "name": "Bug Catcher Tim", "x": 8, "y": 10, "sprite": "npc_m_1", "facing": "up",
                "dialogue_id": "", "trainer_id": "trainer_bug_catcher_1"
            }
        ],
        "encounter_table": [
            {"creature": "barkbug", "level_min": 3, "level_max": 6, "weight": 70},
            {"creature": "florbit", "level_min": 4, "level_max": 6, "weight": 30}
        ]
    }

    # --- Cave 1 ---
    cave_ground = make_layer(15, 10, 10)
    cave_coll = make_layer(15, 10, 1)
    cave_enc = make_layer(15, 10, 0)
    for x in range(2, 14):
        for y in range(2, 8):
            cave_ground[y][x] = 11 # floor
            cave_coll[y][x] = 0
            cave_enc[y][x] = 1
            
    maps["cave_1"] = {
        "name": "Echo Cave",
        "width": 15, "height": 10,
        "layers": {
            "ground": cave_ground,
            "collision": cave_coll,
            "encounter": cave_enc
        },
        "warps": [
            {"x": 14, "y": 5, "target_map": "forest_1", "target_x": 4, "target_y": 5}
        ],
        "npcs": [
            {
                "id": "trainer_hiker_1", "name": "Hiker Dan", "x": 6, "y": 4, "sprite": "npc_m_1", "facing": "right",
                "dialogue_id": "", "trainer_id": "trainer_hiker_1"
            }
        ],
        "encounter_table": [
            {"creature": "geopup", "level_min": 5, "level_max": 8, "weight": 60},
            {"creature": "gloomfox", "level_min": 6, "level_max": 8, "weight": 40}
        ]
    }

    # --- Second Town ---
    maps["second_town"] = {
        "name": "Riverbend City",
        "width": 15, "height": 15,
        "layers": {
            "ground": [
                [2,2,2,2,2,2,2,1,1,2,2,2,2,2,2],
                [2,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
                [2,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
                [2,1,1,3,3,1,1,1,1,1,3,3,1,1,2],
                [2,1,1,4,3,1,1,1,1,1,4,3,1,1,2],
                [2,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
                [2,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
                [5,5,5,5,5,5,5,5,5,5,5,5,1,1,2],
                [5,5,5,5,5,5,5,5,5,5,5,5,1,1,2],
                [2,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
                [2,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
                [2,1,1,3,3,1,1,1,1,1,1,1,1,1,2],
                [2,1,1,4,3,1,1,1,1,1,1,1,1,1,2],
                [2,1,1,1,1,1,1,1,1,1,1,1,1,1,2],
                [2,2,2,2,2,2,2,1,1,2,2,2,2,2,2]
            ],
            "collision": [
                [1,1,1,1,1,1,1,0,0,1,1,1,1,1,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,1,1,0,0,0,0,0,1,1,0,0,1],
                [1,0,0,0,1,0,0,0,0,0,0,1,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,1,1,1,1,1,1,1,1,1,1,1,0,0,1],
                [1,1,1,1,1,1,1,1,1,1,1,1,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,1,1,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,1,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,1,1,1,1,1,1,0,0,1,1,1,1,1,1]
            ],
            "encounter": make_layer(15, 15)
        },
        "warps": [
            {"x": 7, "y": 0, "target_map": "forest_1", "target_x": 7, "target_y": 13},
            {"x": 8, "y": 0, "target_map": "forest_1", "target_x": 8, "target_y": 13},
            {"x": 7, "y": 14, "target_map": "route_2", "target_x": 7, "target_y": 1},
            {"x": 8, "y": 14, "target_map": "route_2", "target_x": 8, "target_y": 1}
        ],
        "npcs": [
            {
                "id": "npc_mayor", "name": "Mayor", "x": 10, "y": 5, "sprite": "npc_m_1", "facing": "down",
                "dialogue_id": "mayor_intro"
            },
            {
                "id": "npc_shopkeeper2", "name": "Shopkeeper", "x": 3, "y": 4, "sprite": "npc_f_1", "facing": "down",
                "dialogue_id": "", "shop_id": "shop_riverbend"
            }
        ]
    }

    # --- Route 2 & Boss Area ---
    route_2_ground = make_layer(15, 20, 1)
    route_2_coll = make_layer(15, 20, 0)
    route_2_enc = make_layer(15, 20, 0)
    for x in range(0, 15):
        route_2_ground[0][x] = 2; route_2_coll[0][x] = 1
        route_2_ground[19][x] = 2; route_2_coll[19][x] = 1
        route_2_ground[x][0] = 2; route_2_coll[x][0] = 1
        route_2_ground[x][14] = 2; route_2_coll[x][14] = 1
        
    route_2_ground[0][7] = 1; route_2_coll[0][7] = 0
    route_2_ground[0][8] = 1; route_2_coll[0][8] = 0
    
    # Grass patches
    for x in range(3, 12):
        for y in range(4, 10):
            route_2_ground[y][x] = 6
            route_2_enc[y][x] = 1
            
    # Boss arena at the bottom
    for x in range(5, 10):
        for y in range(14, 18):
            route_2_ground[y][x] = 11
            
    maps["route_2"] = {
        "name": "Route 2",
        "width": 15, "height": 20,
        "layers": {
            "ground": route_2_ground,
            "collision": route_2_coll,
            "encounter": route_2_enc
        },
        "warps": [
            {"x": 7, "y": 0, "target_map": "second_town", "target_x": 7, "target_y": 13},
            {"x": 8, "y": 0, "target_map": "second_town", "target_x": 8, "target_y": 13}
        ],
        "npcs": [
            {
                "id": "trainer_boss_1", "name": "Rogue Leader", "x": 7, "y": 15, "sprite": "npc_m_1", "facing": "down",
                "dialogue_id": "", "trainer_id": "trainer_boss_1"
            },
            {
                "id": "trainer_grunt_1", "name": "Rogue Grunt", "x": 7, "y": 11, "sprite": "npc_m_1", "facing": "up",
                "dialogue_id": "", "trainer_id": "trainer_grunt_1"
            }
        ],
        "encounter_table": [
            {"creature": "flapjay", "level_min": 8, "level_max": 12, "weight": 30},
            {"creature": "gloomfox", "level_min": 9, "level_max": 12, "weight": 40},
            {"creature": "sproutlet", "level_min": 8, "level_max": 10, "weight": 30}
        ]
    }
    
    write_json("maps.json", {"maps": maps})

def generate_creatures():
    creatures = {
        "florbit": {
            "name": "Florbit",
            "type": "grass",
            "base_stats": {"hp": 45, "attack": 49, "defense": 49, "speed": 45},
            "growth_rate": "medium_fast",
            "level_moves": [
                {"level": 1, "move": "tackle"},
                {"level": 5, "move": "vine_whip"}
            ],
            "description": "A small rabbit-like creature with leaves for ears."
        },
        "barkbug": {
            "name": "Barkbug",
            "type": "bug",
            "base_stats": {"hp": 40, "attack": 30, "defense": 50, "speed": 35},
            "growth_rate": "medium_fast",
            "level_moves": [
                {"level": 1, "move": "tackle"},
                {"level": 6, "move": "bug_bite"}
            ],
            "description": "It camouflages as tree bark."
        },
        "geopup": {
            "name": "Geopup",
            "type": "rock",
            "base_stats": {"hp": 50, "attack": 60, "defense": 60, "speed": 40},
            "growth_rate": "medium_slow",
            "level_moves": [
                {"level": 1, "move": "tackle"},
                {"level": 8, "move": "rock_throw"}
            ],
            "description": "A sturdy pup made of living stone."
        },
        "gloomfox": {
            "name": "Gloomfox",
            "type": "dark",
            "base_stats": {"hp": 40, "attack": 55, "defense": 40, "speed": 65},
            "growth_rate": "medium_fast",
            "level_moves": [
                {"level": 1, "move": "scratch"},
                {"level": 8, "move": "bite"}
            ],
            "description": "It hides in the shadows and plays pranks."
        },
        "sproutlet": {
            "name": "Sproutlet",
            "type": "grass",
            "base_stats": {"hp": 60, "attack": 40, "defense": 60, "speed": 40},
            "growth_rate": "medium_slow",
            "level_moves": [
                {"level": 1, "move": "tackle"},
                {"level": 7, "move": "vine_whip"}
            ],
            "description": "A small sprout."
        },
        "vinebrute": {
            "name": "Vinebrute",
            "type": "grass",
            "base_stats": {"hp": 90, "attack": 80, "defense": 80, "speed": 50},
            "growth_rate": "medium_slow",
            "level_moves": [
                {"level": 1, "move": "vine_whip"},
                {"level": 1, "move": "tackle"}
            ],
            "description": "A towering beast made of thick vines."
        },
        "flapjay": {
            "name": "Flapjay",
            "type": "normal",
            "base_stats": {"hp": 40, "attack": 55, "defense": 30, "speed": 60},
            "growth_rate": "medium_fast",
            "level_moves": [
                {"level": 1, "move": "peck"},
                {"level": 6, "move": "quick_attack"}
            ],
            "description": "A loud blue bird."
        }
    }
    
    # We need to define some basic moves if they don't exist.
    # The existing moves.json might have them. 
    # tackle, scratch, water_gun, ember, vine_whip, peck
    write_json("creatures.json", {"creatures": creatures})

def generate_trainers():
    trainers = {
        "trainer_lass_1": {
            "name": "Lass Mia",
            "dialogue_intro": "My Flapjay is so cute!",
            "dialogue_defeat": "Oh no!",
            "party": [
                {"id": "flapjay", "level": 4}
            ],
            "reward_money": 60
        },
        "trainer_youngster_1": {
            "name": "Youngster Joey",
            "dialogue_intro": "I like shorts!",
            "dialogue_defeat": "They're comfy and easy to wear...",
            "party": [
                {"id": "barkbug", "level": 4},
                {"id": "barkbug", "level": 4}
            ],
            "reward_money": 80
        },
        "trainer_bug_catcher_1": {
            "name": "Bug Catcher Tim",
            "dialogue_intro": "Bugs are the best!",
            "dialogue_defeat": "My bugs!",
            "party": [
                {"id": "barkbug", "level": 6}
            ],
            "reward_money": 70
        },
        "trainer_hiker_1": {
            "name": "Hiker Dan",
            "dialogue_intro": "Watch your step in here!",
            "dialogue_defeat": "I stumbled!",
            "party": [
                {"id": "geopup", "level": 8}
            ],
            "reward_money": 150
        },
        "trainer_grunt_1": {
            "name": "Rogue Grunt",
            "dialogue_intro": "You can't pass!",
            "dialogue_defeat": "Boss, I failed!",
            "party": [
                {"id": "gloomfox", "level": 10},
                {"id": "barkbug", "level": 10}
            ],
            "reward_money": 200
        },
        "trainer_boss_1": {
            "name": "Rogue Leader",
            "dialogue_intro": "I won't let some kid stop my plans!",
            "dialogue_defeat": "Impossible!",
            "party": [
                {"id": "gloomfox", "level": 12},
                {"id": "geopup", "level": 12},
                {"id": "vinebrute", "level": 14}
            ],
            "reward_money": 1000
        }
    }
    write_json("trainers.json", {"trainers": trainers})

def generate_dialogues():
    dialogues = {
        "mom_intro": {
            "start": {
                "speaker": "Mom",
                "text": "Good morning! Professor Cedar was looking for you. He's at his lab next door.",
                "next": "end"
            }
        },
        "prof_intro": {
            "start": {
                "speaker": "Prof. Cedar",
                "text": "Ah, there you are! Are you ready for your own creature?",
                "choices": [
                    {"text": "Yes!", "next": "give_florbit"},
                    {"text": "Not yet.", "next": "end"}
                ]
            },
            "give_florbit": {
                "speaker": "Prof. Cedar",
                "text": "Here is a Florbit! Take good care of it.",
                "actions": [
                    {"type": "give_creature", "creature": "florbit", "level": 5},
                    {"type": "set_flag", "flag": "has_creature", "value": True}
                ],
                "next": "prof_quest"
            },
            "prof_quest": {
                "speaker": "Prof. Cedar",
                "text": "I need a favor. Could you deliver this parcel to the Mayor in Riverbend City?",
                "actions": [
                    {"type": "give_item", "item": "parcel", "qty": 1}
                ],
                "next": "end"
            }
        },
        "mayor_intro": {
            "start": {
                "speaker": "Mayor",
                "text": "Did you bring the parcel from Professor Cedar?",
                "choices": [
                    {"text": "Yes", "next": "mayor_thanks"}
                ]
            },
            "mayor_thanks": {
                "speaker": "Mayor",
                "text": "Thank you! But we have a bigger problem... Rogues have taken over Route 2!",
                "next": "end"
            }
        }
    }
    write_json("dialogues.json", {"dialogues": dialogues})

def generate_encounters():
    # Write this directly into maps or somewhere else?
    pass

def generate_items():
    items = {
        "potion": {
            "name": "Potion", "category": "Healing", "effect": "heal_hp",
            "value": 20, "price": 100, "description": "Heals a creature by 20 HP."
        },
        "capture_orb": {
            "name": "Capture Orb", "category": "Capture", "effect": "capture",
            "value": 1.0, "price": 200, "description": "Used to capture wild creatures."
        },
        "parcel": {
            "name": "Parcel", "category": "Key Item", "effect": "none",
            "value": 0, "price": 0, "description": "A package for the Mayor of Riverbend."
        }
    }
    write_json("items.json", {"items": items})

def generate_shops():
    shops = {
        "shop_oakhaven": {
            "name": "Oakhaven Mart",
            "inventory": ["potion", "capture_orb"]
        },
        "shop_riverbend": {
            "name": "Riverbend Supply",
            "inventory": ["potion", "capture_orb"]
        }
    }
    write_json("shops.json", {"shops": shops})

def generate_quests():
    quests = {
        "main_01": {
            "name": "The Journey Begins",
            "type": "main",
            "description": "Speak with Mom before you head out to Route 1.",
            "objectives": [
                {"id": "obj_1", "type": "talk_npc", "npc_id": "npc_mom", "description": "Talk to Mom in Oakhaven."}
            ],
            "rewards": [{"type": "item", "item_id": "potion", "quantity": 3}]
        },
        "main_02": {
            "name": "Special Delivery",
            "type": "main",
            "description": "Deliver the Parcel to the Mayor in Riverbend City.",
            "objectives": [
                {"id": "obj_1", "type": "talk_npc", "npc_id": "npc_mayor", "description": "Deliver the parcel to the Mayor."}
            ],
            "rewards": [{"type": "coins", "amount": 500}]
        },
        "main_03": {
            "name": "Rogue Menace",
            "type": "main",
            "description": "Defeat the Rogue Leader on Route 2.",
            "objectives": [
                {"id": "obj_1", "type": "defeat_trainer", "trainer_id": "trainer_boss_1", "description": "Defeat Rogue Leader."}
            ],
            "rewards": [{"type": "item", "item_id": "capture_orb", "quantity": 5}]
        }
    }
    write_json("quests.json", {"quests": quests})

if __name__ == "__main__":
    generate_maps()
    generate_creatures()
    generate_trainers()
    generate_dialogues()
    generate_items()
    generate_shops()
    generate_quests()
    print("Content generated.")
